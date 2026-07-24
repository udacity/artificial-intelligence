from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from contextlib import suppress
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_DATABASE = ROOT / "var" / "startup_check.db"


def main() -> int:
    cleanup_database()
    env = {
        **os.environ,
        "AGENT_ARENA_DATABASE_URL": f"sqlite:///{CHECK_DATABASE.as_posix()}",
        "PYTHONPATH": os.pathsep.join(
            str(ROOT / path)
            for path in (
                "apps/api",
                "packages/isolation_engine",
                "packages/agent_runner",
            )
        ),
    }
    migration = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    if migration.returncode != 0:
        print("The startup-check migration failed", flush=True)
        cleanup_database()
        return migration.returncode
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "agent_arena_api.main:app", "--port", "8011"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    npm = "npm.cmd" if os.name == "nt" else "npm"
    web = subprocess.Popen(
        [npm, "run", "dev", "--", "--port", "5181"],
        cwd=ROOT / "apps" / "web",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    processes = (api, web)
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:8011/api/health", timeout=1
                ) as response:
                    payload = json.load(response)
                with urllib.request.urlopen(
                    "http://127.0.0.1:8011/api/leaderboard", timeout=1
                ) as response:
                    leaderboard = json.load(response)
                with urllib.request.urlopen("http://127.0.0.1:5181", timeout=1) as response:
                    web_page = response.read().decode("utf-8")
                if (
                    payload.get("status") == "ok"
                    and isinstance(leaderboard, list)
                    and "Agent Arena" in web_page
                ):
                    print(json.dumps(payload, indent=2), flush=True)
                    print("web: ready", flush=True)
                    return 0
            except Exception:
                time.sleep(0.1)
        print("API and web did not both become ready", flush=True)
        return 1
    finally:
        for process in processes:
            stop_process(process)
        cleanup_database()


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with suppress(subprocess.TimeoutExpired):
            process.wait(timeout=5)
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def cleanup_database() -> None:
    paths = (
        CHECK_DATABASE,
        CHECK_DATABASE.with_name(f"{CHECK_DATABASE.name}-wal"),
        CHECK_DATABASE.with_name(f"{CHECK_DATABASE.name}-shm"),
    )
    for _ in range(20):
        try:
            for path in paths:
                path.unlink(missing_ok=True)
            return
        except PermissionError:
            time.sleep(0.1)


if __name__ == "__main__":
    raise SystemExit(main())
