"""Data Authority Loader + Sweep — L5 v4 Wave-J wire-in.

Process-local singleton for the active Data Authority ledger — the set of
`DataAuthorityRecord` entries pinned by the current policy version. Pre-L5
Data Authority Resolution (ADR-049, G-13) calls into this loader to:

- Fetch the ledger (memoized per-process for stable digests within a run)
- Run `resolve_data_authority` across all records
- Cache the resolution so audit binding can bind against the same outcome

Parallels `registry_loader.py` (Wave-I) for registries, applying the same
bootstrap-empty / swap-in-production / clear-for-tests pattern.

Adoption path:

    from agentic_core.L5_safety.identity.data_authority_loader import (
        get_active_data_authority_resolution,
        set_active_data_authority_ledger,
    )

    # In production boot: set_active_data_authority_ledger(records, policy_version=...)
    # Pre-L5 sweep (per-request):
    resolution = get_active_data_authority_resolution()
    if not resolution.all_match:
        # Drift detected — audit binding gets drifted source_ids
        ...

Reference:
  - agentic_core/L5_safety/identity/registries.py (`DataAuthorityRecord`, `resolve_data_authority`)
  - agentic_core/L5_safety/identity/registry_loader.py (parallel loader)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

import threading
from collections.abc import Iterable

from agentic_core.L5_safety.identity.registries import (
    DataAuthorityRecord,
    DataAuthorityResolution,
    DataSourceKind,
    resolve_data_authority,
)

_BOOTSTRAP_POLICY_VERSION = "v4.0.0-bootstrap"

_lock = threading.Lock()
_active_ledger: tuple[DataAuthorityRecord, ...] | None = None
_active_resolution: DataAuthorityResolution | None = None
_active_policy_version: str = _BOOTSTRAP_POLICY_VERSION


def _build_bootstrap_resolution() -> DataAuthorityResolution:
    """Empty ledger → trivially-matching resolution.

    Production boot replaces this with a populated ledger before any write
    or egress path that depends on supply-chain attestation.
    """
    return resolve_data_authority(())


def get_active_data_authority_resolution() -> DataAuthorityResolution:
    """Return the process-local active DataAuthorityResolution.

    Thread-safe, memoized. Lazily produces the empty-ledger bootstrap
    resolution on first call.
    """
    global _active_resolution  # noqa: PLW0603
    if _active_resolution is not None:
        return _active_resolution
    with _lock:
        if _active_resolution is None:
            _active_resolution = _build_bootstrap_resolution()
    return _active_resolution


def get_active_data_authority_ledger() -> tuple[DataAuthorityRecord, ...]:
    """Return the current ledger tuple (empty if bootstrap)."""
    return _active_ledger or ()


def get_active_policy_version() -> str:
    """Return the policy version pinned to the active ledger."""
    return _active_policy_version


def set_active_data_authority_ledger(
    records: Iterable[DataAuthorityRecord],
    *,
    policy_version: str,
) -> DataAuthorityResolution:
    """Replace the active ledger + recompute resolution atomically.

    Returns the new resolution so callers can immediately inspect drift.
    Only the policy-promotion path should call this in production, and
    only after `decide_policy_promotion` green-lights the new version.
    """
    global _active_ledger, _active_resolution, _active_policy_version  # noqa: PLW0603
    if not policy_version:
        raise ValueError("set_active_data_authority_ledger: policy_version required")
    records_t = tuple(records)
    resolution = resolve_data_authority(records_t)
    with _lock:
        _active_ledger = records_t
        _active_resolution = resolution
        _active_policy_version = policy_version
    return resolution


def clear_active_data_authority() -> None:
    """Reset the cache (tests only)."""
    global _active_ledger, _active_resolution, _active_policy_version  # noqa: PLW0603
    with _lock:
        _active_ledger = None
        _active_resolution = None
        _active_policy_version = _BOOTSTRAP_POLICY_VERSION


__all__ = [
    "DataAuthorityRecord",
    "DataAuthorityResolution",
    "DataSourceKind",
    "clear_active_data_authority",
    "get_active_data_authority_ledger",
    "get_active_data_authority_resolution",
    "get_active_policy_version",
    "set_active_data_authority_ledger",
]
