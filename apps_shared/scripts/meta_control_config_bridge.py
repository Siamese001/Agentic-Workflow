"""Meta-Control Config Bridge — Wave 7.0.18.

Read-only accessor for APPS_* to consume the meta-control config store.
Delegates to agentic_core config_store; provides zero-write, zero-apply
helpers only.

Hard forbiddances (enforced by tests):
  - Must NOT import meta_apply / meta_apply_ops.
  - Must NOT call any apply functions.
  - Must NOT write files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.interfaces.meta_control import (
    canonical_json,
    load_current,
    validate_component_allowed,
)

# Default store root — co-located with meta_control module.
_DEFAULT_STORE_ROOT = (
    Path(__file__).resolve().parents[2] / "agentic_core" / "L0_routing" / "meta_control" / "config_store"
)


def load_app_component_config(
    app_id: str,
    target_component: str,
    *,
    store_root: Path | None = None,
) -> dict[str, Any]:
    """Load the current config payload for (app_id, target_component).

    Validates target_component against MUTABLE_COMPONENTS (L7 SSOT).
    Returns {} if no config exists yet (pass-through behavior).
    Raises ValueError for invalid component or empty app_id.
    """
    validate_component_allowed(target_component)
    root = store_root if store_root is not None else _DEFAULT_STORE_ROOT
    return load_current(root, app_id, target_component)


def render_app_component_config(
    app_id: str,
    target_component: str,
    *,
    store_root: Path | None = None,
) -> str:
    """Render the current config payload as canonical JSON string.

    Returns "{}" if no config exists yet.
    """
    payload = load_app_component_config(
        app_id,
        target_component,
        store_root=store_root,
    )
    return canonical_json(payload)
