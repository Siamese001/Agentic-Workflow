"""Optional Qwen strict-mode enforcement bridge (integrations exempt authority MV)."""

from __future__ import annotations


def maybe_enforce_qwen_strict_requirement() -> None:
    """Invoke strict diagnostic when APPS_RESEARCH_REQUIRE_QWEN is active."""
    try:
        from agentic_core.L2_execution.healers.qwen_strict_diagnostic import (
            require_qwen_or_raise,
            strict_mode_enabled,
        )
    except ImportError:
        return
    if strict_mode_enabled():
        require_qwen_or_raise()
