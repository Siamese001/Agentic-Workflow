"""CLI prerequisite probe — core gate imported only from ``apps_rg/enforcement/``."""

from __future__ import annotations

from typing import Any


def check_apps_rg_cli_prerequisites(**kwargs: Any) -> None:
    """Delegate to ``check_apps_rg_prerequisites`` (authority MV exempt enforcement path)."""
    from agentic_core.L0_routing.gates.apps_rg_prerequisite_gate import (
        check_apps_rg_prerequisites,
    )

    check_apps_rg_prerequisites(**kwargs)
