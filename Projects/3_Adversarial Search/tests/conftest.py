from __future__ import annotations

from pathlib import Path

import pytest
from agent_arena_api.config import Settings
from isolation_engine import Isolation, MoveResponse


class FirstLegalController:
    def reset(self, player_id: int) -> None:
        self.player_id = player_id

    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        del timeout_ms
        actions = state.actions()
        return MoveResponse(actions[0] if actions else None)

    def close(self) -> None:
        return None


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        source_root=tmp_path / "sources",
        temp_root=tmp_path / "tmp",
        runner_image="test-runner",
    )
