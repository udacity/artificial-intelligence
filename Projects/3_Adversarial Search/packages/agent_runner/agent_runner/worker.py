"""JSON-lines worker executed only inside the pinned runner container."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from isolation_engine import Isolation

from .compat import invoke_agent

MAX_CAPTURE = 8_192


def load_player(player_id: int) -> Any:
    source_path = Path("/workspace/agent.py")
    spec = importlib.util.spec_from_file_location("submitted_agent", source_path)
    if spec is None or spec.loader is None:
        raise ImportError("unable to load agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    player_class = getattr(module, "CustomPlayer", None)
    if player_class is None:
        raise TypeError("CustomPlayer is missing")
    try:
        player = player_class(player_id=player_id)
    except TypeError:
        try:
            player = player_class(player_id)
        except TypeError:
            player = player_class()
    player.player_id = player_id
    player.context = None
    return player


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--player-id", type=int, required=True)
    args = parser.parse_args()
    startup_output, startup_errors = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(startup_output), redirect_stderr(startup_errors):
            player = load_player(args.player_id)
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": f"import: {type(error).__name__}: {error}",
                    "stdout": startup_output.getvalue()[-MAX_CAPTURE:],
                    "stderr": startup_errors.getvalue()[-MAX_CAPTURE:],
                }
            ),
            flush=True,
        )
        return 1
    print(
        json.dumps(
            {
                "status": "ready",
                "stdout": startup_output.getvalue()[-MAX_CAPTURE:],
                "stderr": startup_errors.getvalue()[-MAX_CAPTURE:],
            }
        ),
        flush=True,
    )

    for line in sys.stdin:
        output, errors = io.StringIO(), io.StringIO()
        try:
            message = json.loads(line)
            if message.get("type") != "choose_action":
                raise ValueError("unsupported protocol message")
            state = Isolation.from_dict(message["state"])
            with redirect_stdout(output), redirect_stderr(errors):
                action = invoke_agent(player, state, int(message["timeout_ms"]))
            payload = {
                "status": "ok" if action is not None else "empty",
                "action": action,
                "stdout": output.getvalue()[-MAX_CAPTURE:],
                "stderr": errors.getvalue()[-MAX_CAPTURE:],
            }
        except Exception as error:
            payload = {
                "status": "error",
                "error": f"{type(error).__name__}: {error}",
                "stderr": traceback.format_exc(limit=4)[-MAX_CAPTURE:],
            }
        print(json.dumps(payload), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
