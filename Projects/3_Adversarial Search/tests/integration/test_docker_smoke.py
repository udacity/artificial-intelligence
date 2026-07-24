from __future__ import annotations

import pytest
from agent_arena_api.config import Settings
from agent_arena_api.submissions import prepare_submission
from agent_runner import DockerAgent

SOURCE = """class CustomPlayer:
    def get_action(self, state):
        actions = state.actions()
        return actions[0] if actions else None
"""


@pytest.mark.docker
def test_real_docker_submission_when_runner_is_available(tmp_path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'docker.db').as_posix()}",
        source_root=tmp_path / "sources",
        temp_root=tmp_path / "tmp",
    )
    diagnostic = DockerAgent.diagnostic(settings.runner_image)
    if not diagnostic["available"]:
        pytest.skip(diagnostic["message"])
    prepared = prepare_submission(SOURCE, settings)
    assert prepared.accepted, prepared.validation
