"""apps_shared.config.legacy_yaml_deprecation — legacy YAML deprecation shim.

Plan: ``.codex/plans/apps-eval-harness-closeout-b7c9d2.md`` W4.P1.

Problem: several apps still ship ``*_policies.yaml`` / ``*_thresholds.yaml``
alongside the canonical ``config/domain_contract/`` bundle. The canonical
bundle is the SSOT (via L4 ``AppEvalRubricRecord`` + ``AppThresholdProfileRecord``),
so legacy files exist only for migration compatibility and should stop
being loaded once producers finish the cutover.

This helper emits a ``DeprecationWarning`` + a structured ledger event on
load. Non-breaking: warnings are filterable and default-filtered in most
test suites. Callers opt in to the warning by calling ``emit_deprecation``
in their loader's top-level module.

Usage:

    from apps_shared.config.legacy_yaml_deprecation import emit_deprecation

    def load_legacy_thresholds(path):
        emit_deprecation(
            path=path,
            since="2026-05-03",
            removal_target="2026-09-01",
            canonical_path="<app>/config/domain_contract/threshold_profiles.yaml",
        )
        # ... actual load logic ...
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Registry so each (path) combination only warns once per process run.
_WARNED_PATHS: set[str] = set()


def emit_deprecation(
    *,
    path: str | Path,
    since: str,
    removal_target: str,
    canonical_path: str,
    extra: dict[str, Any] | None = None,
) -> None:
    """Emit a DeprecationWarning + log + optional ledger event.

    Idempotent per process run: the same ``path`` only warns once.

    Args:
        path: The legacy file being loaded (absolute or repo-relative string or Path).
        since: ISO date the deprecation took effect (e.g. "2026-05-03").
        removal_target: ISO date the file will be removed (e.g. "2026-09-01").
        canonical_path: Repo-relative path of the canonical replacement.
        extra: Optional extra metadata logged alongside the warning.
    """
    key = str(path)
    if key in _WARNED_PATHS:
        return
    _WARNED_PATHS.add(key)
    msg = (
        f"[apps_shared] legacy YAML {key} is DEPRECATED since {since} and will be "
        f"removed on {removal_target}. Use the canonical SSOT at {canonical_path}."
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=3)
    _LOGGER.warning(msg)
    # Best-effort ledger event — tool_routing ledger captures the call so
    # we can audit which callers still load the legacy path. Fail-soft.
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event  # noqa: PLC0415

        emit_ledger_event(
            ledger="tool_routing",
            event_kind="legacy_yaml_load",
            prediction={
                "legacy_path": key,
                "canonical_path": canonical_path,
                "since": since,
                "removal_target": removal_target,
            },
            metadata=extra or {},
            repo_area=key,
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- deprecation telemetry is fail-soft;
        # ledger unavailability must not break the caller
        _LOGGER.info("[apps_shared] legacy_yaml_load ledger emit skipped: %s", exc)


def reset_warning_registry() -> None:
    """Test hook: clear the once-per-path memoization."""
    _WARNED_PATHS.clear()


__all__ = ["emit_deprecation", "reset_warning_registry"]
