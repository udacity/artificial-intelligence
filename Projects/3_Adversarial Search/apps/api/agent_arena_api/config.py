from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_prefix="AGENT_ARENA_", extra="ignore"
    )

    database_url: str = f"sqlite:///{(ROOT / 'var' / 'agent_arena.db').as_posix()}"
    source_root: Path = ROOT / "var" / "sources"
    temp_root: Path = ROOT / "var" / "tmp"
    runner_image: str = "agent-arena-runner:py312-v1"
    move_budget_ms: int = 150
    minimum_ranked_fixtures: int = 10
    demo_owner_name: str = "oualid"
    max_source_bytes: int = 131_072


settings = Settings()
