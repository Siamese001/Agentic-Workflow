"""Thin BaseRGEngine anchor for RG engine stacks.

Historically exercised by ``tests/unit/apps_rg/engines/test_base_rg_engine.py``.
Runtime résumé work now lives primarily under ``apps_rg/runtime``, but downstream
OPS scripts occasionally import orchestrator primitives from this namespace.
"""


class BaseRGEngine:
    """Placeholder base retained for backward-compatible imports."""

    AGENT_ID = "apps_rg.base_rg_engine"
