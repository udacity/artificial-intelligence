"""Docker boundary for submitted Python in the local beta."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from contextlib import suppress
from pathlib import Path
from typing import Any

from isolation_engine import (
    ControllerTimeoutError,
    Isolation,
    MoveResponse,
)

RUNNER_IMAGE = "agent-arena-runner:py312-v1"
MAX_PROTOCOL_LINE = 32_768
STARTUP_TIMEOUT_SECONDS = 10


class RunnerUnavailableError(RuntimeError):
    pass


class DockerAgent:
    """Start one fresh container for one submitted agent in one game."""

    def __init__(self, source_path: Path, image: str = RUNNER_IMAGE) -> None:
        self.source_path = source_path.resolve()
        self.image = image
        self.process: subprocess.Popen[str] | None = None
        # A reader thread makes a blocking stdout pipe compatible with a wall-clock timeout.
        self.reader = ThreadPoolExecutor(max_workers=1, thread_name_prefix="docker-agent-line")

    @classmethod
    def diagnostic(cls, image: str = RUNNER_IMAGE) -> dict[str, Any]:
        executable = shutil.which("docker")
        if executable is None:
            return {
                "available": False,
                "code": "docker_not_installed",
                "message": "Docker CLI is unavailable; submitted-code execution is disabled.",
            }
        try:
            image_reference = _canonical_image_reference(image)
            inspection = subprocess.run(
                [executable, "image", "inspect", image_reference, "--format", "{{.Id}}"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            return {
                "available": False,
                "code": "docker_daemon_unavailable",
                "message": "Docker did not respond to image inspection within 10 seconds.",
            }
        except OSError as error:
            return {
                "available": False,
                "code": "docker_cli_error",
                "message": f"Docker CLI could not be started: {error}",
            }
        if inspection.returncode != 0:
            detail = _docker_error_excerpt(inspection.stderr, inspection.stdout)
            if _image_is_missing(detail):
                return {
                    "available": False,
                    "code": "runner_image_missing",
                    "message": f"Runner image {image} is not built.",
                }
            return {
                "available": False,
                "code": "docker_daemon_unavailable",
                "message": (
                    "The API process could not inspect the Docker daemon or active context: "
                    f"{detail}"
                ),
            }
        return {"available": True, "code": "ready", "message": "Runner is ready."}

    def reset(self, player_id: int) -> None:
        diagnostic = self.diagnostic(self.image)
        if not diagnostic["available"]:
            raise RunnerUnavailableError(diagnostic["message"])
        mount = f"type=bind,src={self.source_path},dst=/workspace/agent.py,readonly"
        executable = shutil.which("docker")
        if executable is None:
            raise RunnerUnavailableError("Docker CLI is unavailable")
        command = [
            executable,
            "run",
            "--rm",
            "-i",
            "--network=none",
            "--read-only",
            "--tmpfs=/tmp:rw,noexec,nosuid,size=16m",
            "--cpus=1",
            "--memory=256m",
            "--pids-limit=64",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges:true",
            "--mount",
            mount,
            _canonical_image_reference(self.image),
            "python",
            "-m",
            "agent_runner.worker",
            "--player-id",
            str(player_id),
        ]
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.process.stdout is not None
        startup = self.reader.submit(self.process.stdout.readline)
        try:
            line = startup.result(timeout=STARTUP_TIMEOUT_SECONDS)
        except FutureTimeout as error:
            self.close()
            raise RunnerUnavailableError("runner startup exceeded 10 seconds") from error
        if not line:
            detail = self._stderr_excerpt()
            self.close()
            raise RunnerUnavailableError(f"runner stopped during startup: {detail}")
        if len(line) > MAX_PROTOCOL_LINE:
            self.close()
            raise RunnerUnavailableError("runner startup protocol output limit exceeded")
        try:
            response = json.loads(line)
        except json.JSONDecodeError as error:
            self.close()
            raise RunnerUnavailableError("runner emitted invalid startup JSON") from error
        if response.get("status") != "ready":
            self.close()
            raise RunnerUnavailableError(response.get("error", "runner failed during startup"))

    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        if self.process is None or self.process.stdin is None or self.process.stdout is None:
            raise RunnerUnavailableError("runner process was not started")
        self.process.stdin.write(
            json.dumps(
                {
                    "type": "choose_action",
                    "state": state.to_dict(),
                    "timeout_ms": timeout_ms,
                }
            )
            + "\n"
        )
        self.process.stdin.flush()
        future = self.reader.submit(self.process.stdout.readline)
        try:
            line = future.result(timeout=timeout_ms / 1000)
        except FutureTimeout as error:
            self.close()
            raise ControllerTimeoutError(f"agent exceeded {timeout_ms} ms") from error
        if not line:
            raise RuntimeError(f"runner stopped without a response: {self._stderr_excerpt()}")
        if len(line) > MAX_PROTOCOL_LINE:
            self.close()
            raise RuntimeError("runner protocol output limit exceeded")
        response = json.loads(line)
        if response.get("status") == "error":
            raise RuntimeError(response.get("error", "runner error"))
        return MoveResponse(
            action=response.get("action"),
            stdout=response.get("stdout", "")[-8192:],
            stderr=response.get("stderr", "")[-8192:],
        )

    def close(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.kill()
            with suppress(subprocess.TimeoutExpired):
                self.process.wait(timeout=2)
        self.process = None
        self.reader.shutdown(wait=False, cancel_futures=True)

    def _stderr_excerpt(self) -> str:
        if self.process is None or self.process.stderr is None:
            return ""
        return self.process.stderr.read(8192)


def _docker_error_excerpt(stderr: str, stdout: str) -> str:
    lines = [line.strip() for line in f"{stderr}\n{stdout}".splitlines() if line.strip()]
    if not lines:
        return "docker image inspect failed without an error message"
    return " | ".join(lines[-3:])[-2_000:]


def _image_is_missing(detail: str) -> bool:
    normalized = detail.lower()
    return "no such image" in normalized or "image does not exist" in normalized


def _canonical_image_reference(image: str) -> str:
    """Normalize Docker Hub short names for Docker Desktop's containerd store."""

    reference = image.strip()
    if reference.startswith("sha256:") or re.fullmatch(r"[0-9a-fA-F]{12,64}", reference):
        return reference
    first_component, separator, _remainder = reference.partition("/")
    if not separator:
        return f"docker.io/library/{reference}"
    if first_component == "localhost" or "." in first_component or ":" in first_component:
        return reference
    return f"docker.io/{reference}"
