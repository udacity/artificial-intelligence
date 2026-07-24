from __future__ import annotations

import subprocess
from time import sleep

import pytest
from agent_runner import DecisionDeadlineExceeded, DockerAgent, invoke_agent
from agent_runner.docker import _canonical_image_reference
from isolation_engine import Isolation


class QueuePlayer:
    def get_action(self, state: Isolation) -> None:
        self.queue.put(state.actions()[0])


class ReturnPlayer:
    def get_action(self, state: Isolation) -> int:
        return state.actions()[-1]


class SlowPlayer:
    def get_action(self, state: Isolation) -> int:
        sleep(0.004)
        return state.actions()[0]


def test_queue_and_return_agents_are_compatible() -> None:
    state = Isolation()
    assert invoke_agent(QueuePlayer(), state, 150) in state.actions()
    assert invoke_agent(ReturnPlayer(), state, 150) in state.actions()


def test_runner_adapter_enforces_internal_deadline() -> None:
    with pytest.raises(DecisionDeadlineExceeded):
        invoke_agent(SlowPlayer(), Isolation(), 1)


def test_docker_diagnostic_uses_resolved_windows_executable(monkeypatch) -> None:
    executable = r"C:\Program Files\Docker\Docker\resources\bin\docker.EXE"
    commands: list[list[str]] = []

    monkeypatch.setattr("agent_runner.docker.shutil.which", lambda _name: executable)

    def inspect(command: list[str], **_kwargs) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="sha256:runner\n", stderr="")

    monkeypatch.setattr("agent_runner.docker.subprocess.run", inspect)

    assert DockerAgent.diagnostic()["code"] == "ready"
    assert commands == [
        [
            executable,
            "image",
            "inspect",
            "docker.io/library/agent-arena-runner:py312-v1",
            "--format",
            "{{.Id}}",
        ]
    ]


@pytest.mark.parametrize(
    ("stderr", "expected_code"),
    [
        ("Error response from daemon: No such image: missing:latest", "runner_image_missing"),
        (
            "permission denied while trying to connect to the docker API at "
            "npipe:////./pipe/dockerDesktopLinuxEngine",
            "docker_daemon_unavailable",
        ),
    ],
)
def test_docker_diagnostic_distinguishes_missing_image_from_daemon_failure(
    monkeypatch,
    stderr: str,
    expected_code: str,
) -> None:
    monkeypatch.setattr("agent_runner.docker.shutil.which", lambda _name: "docker.EXE")
    monkeypatch.setattr(
        "agent_runner.docker.subprocess.run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command,
            1,
            stdout="[]\n",
            stderr=stderr,
        ),
    )

    result = DockerAgent.diagnostic("missing:latest")

    assert result["available"] is False
    assert result["code"] == expected_code
    if expected_code == "docker_daemon_unavailable":
        assert "permission denied" in result["message"]


@pytest.mark.parametrize(
    ("image", "expected"),
    [
        ("agent-arena-runner:py312-v1", "docker.io/library/agent-arena-runner:py312-v1"),
        ("example/team-agent:v1", "docker.io/example/team-agent:v1"),
        ("localhost:5000/team-agent:v1", "localhost:5000/team-agent:v1"),
        ("registry.example.com/team-agent:v1", "registry.example.com/team-agent:v1"),
        ("e5354ca0ee27", "e5354ca0ee27"),
    ],
)
def test_docker_image_reference_normalization(image: str, expected: str) -> None:
    assert _canonical_image_reference(image) == expected
