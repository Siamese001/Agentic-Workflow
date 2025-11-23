from __future__ import annotations

"""ReAct (reason + act) helpers.

These helpers define a small interface for step-wise reasoning with
interleaved actions. The default implementation is deterministic and
side-effect free.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ReActStep:
    thought: str
    action: str
    observation: str


def run_react_loop(task: str, max_steps: int = 3) -> List[ReActStep]:
    """Run a deterministic ReAct-style loop for a given task description."""

    task = (task or "").strip()
    if not task:
        return []

    steps: List[ReActStep] = []
    for i in range(max_steps):
        thought = f"analyzing task segment {i+1}: {task[:50]}"  # truncated
        action = "noop"
        observation = "no external tools invoked (placeholder)"
        steps.append(ReActStep(thought=thought, action=action, observation=observation))
    return steps
