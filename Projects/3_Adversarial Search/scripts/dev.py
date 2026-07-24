from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELOAD_DIRECTORIES = (
    ROOT / "apps" / "api" / "agent_arena_api",
    ROOT / "packages" / "isolation_engine" / "isolation_engine",
    ROOT / "packages" / "agent_runner" / "agent_runner",
)


def api_command() -> list[str]:
    command = [sys.executable, "-m", "uvicorn", "agent_arena_api.main:app", "--reload"]
    for directory in RELOAD_DIRECTORIES:
        command.extend(("--reload-dir", str(directory)))
    return command


def development_environment(overrides: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            str(ROOT / path)
            for path in (
                "apps/api",
                "packages/isolation_engine",
                "packages/agent_runner",
            )
        ),
    }
    env.update(overrides or {})
    return env


def run_development(env: dict[str, str] | None = None) -> int:
    active_env = env or development_environment()
    api = subprocess.Popen(api_command(), cwd=ROOT, env=active_env)
    npm = "npm.cmd" if os.name == "nt" else "npm"
    web = subprocess.Popen([npm, "run", "dev"], cwd=ROOT / "apps" / "web", env=active_env)
    processes = (api, web)

    def stop(*_: object) -> None:
        for process in processes:
            stop_process(process)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(0.25)
        return next((process.returncode for process in processes if process.returncode), 0)
    finally:
        stop()


def main() -> int:
    return run_development()


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
    else:
        process.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
