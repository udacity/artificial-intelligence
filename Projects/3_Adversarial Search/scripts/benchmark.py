"""Launch Agent Arena with an isolated strategy benchmark database."""

from __future__ import annotations

import subprocess
import sys

from dev import ROOT, development_environment, run_development

BENCHMARK_ROOT = ROOT / "var" / "benchmark"


def benchmark_environment() -> dict[str, str]:
    database_path = (BENCHMARK_ROOT / "agent_arena.db").as_posix()
    return development_environment(
        {
            "AGENT_ARENA_DATABASE_URL": f"sqlite:///{database_path}",
            "AGENT_ARENA_SOURCE_ROOT": str(BENCHMARK_ROOT / "sources"),
            "AGENT_ARENA_TEMP_ROOT": str(BENCHMARK_ROOT / "tmp"),
            "AGENT_ARENA_DEMO_OWNER_NAME": "benchmark-lab",
        }
    )


def prepare_benchmark(environment: dict[str, str]) -> None:
    BENCHMARK_ROOT.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "agent_arena_api.benchmark_seed"],
        cwd=ROOT,
        env=environment,
        check=True,
    )


def main() -> int:
    environment = benchmark_environment()
    prepare_benchmark(environment)
    return run_development(environment)


if __name__ == "__main__":
    raise SystemExit(main())
