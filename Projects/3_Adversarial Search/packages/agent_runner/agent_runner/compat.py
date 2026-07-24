"""Compatibility helpers used only inside the isolated runner process."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from isolation_engine import Isolation


class DecisionDeadlineExceeded(TimeoutError):
    pass


@dataclass
class ActionQueue:
    """Collect the last action sent through the original Udacity queue API."""

    deadline: float
    action: int | None = None
    has_action: bool = False

    def put(self, item: Any, block: bool = True, timeout: float | None = None) -> None:
        del block, timeout
        if perf_counter() > self.deadline:
            raise DecisionDeadlineExceeded("decision deadline exceeded")
        self.action = int(item)
        self.has_action = True

    def put_nowait(self, item: Any) -> None:
        self.put(item, block=False)


def invoke_agent(agent: Any, state: Isolation, timeout_ms: int) -> int | None:
    """Normalize ``return action`` and ``self.queue.put(action)`` styles."""

    queue = ActionQueue(perf_counter() + timeout_ms / 1000)
    agent.queue = queue
    if not hasattr(agent, "context"):
        agent.context = None
    returned = agent.get_action(state)
    if perf_counter() > queue.deadline:
        raise DecisionDeadlineExceeded("decision deadline exceeded")
    if returned is not None:
        return int(returned)
    return queue.action if queue.has_action else None
