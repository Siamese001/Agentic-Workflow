"""QnA L2 Step Adapters — typed adapters for each L2 execution stage.

W1.2: Registry scaffold. Provides adapter functions that wrap the
L2 stage modules for capability registry dispatch.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.2
"""

from __future__ import annotations

from typing import Any, Callable

from apps_qna.l2.e1_prep import prep_workspace
from apps_qna.l2.e2_valid import validate_build_inputs
from apps_qna.l2.e3_exec import execute_build

L2StepAdapter = Callable[..., Any]

_L2_STEP_ADAPTERS: dict[str, L2StepAdapter] = {
    "e1_prep": prep_workspace,
    "e2_valid": validate_build_inputs,
    "e3_exec": execute_build,
}


def get_step_adapter(step_name: str) -> L2StepAdapter | None:
    """Return the adapter function for a named L2 step."""
    return _L2_STEP_ADAPTERS.get(step_name)


def list_step_adapters() -> tuple[str, ...]:
    """Return the names of all registered L2 step adapters."""
    return tuple(_L2_STEP_ADAPTERS.keys())


__all__ = ["L2StepAdapter", "get_step_adapter", "list_step_adapters"]
