#!/usr/bin/env python3
"""Shared Active Set Helper — Single Import Point.

Provides a canonical function to enumerate the ACTIVE agent set using
the same pipeline as full_agent_discovery's perform_deep_integrity_scan.

All CI gates that need the ACTIVE set MUST use this helper to prevent
definition divergence.

Usage:
    from ops_scripts.ci.active_set_helper import get_active_set

    result = get_active_set(project_root)
    print(result.count, result.fingerprint)
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ActiveSetResult:
    """Immutable result of active set enumeration."""

    agents: tuple[dict[str, Any], ...]
    agent_ids: tuple[str, ...]
    count: int
    fingerprint: str
    stats: dict[str, int] = field(default_factory=dict)


def _compute_fingerprint(sorted_ids: tuple[str, ...]) -> str:
    """SHA-256 of newline-joined sorted agent IDs."""
    payload = "\n".join(sorted_ids).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def get_active_set(project_root: Path) -> ActiveSetResult:
    """Return the canonical ACTIVE agent set.

    Pipeline: load_agent_discovery → perform_deep_integrity_scan.
    Identical to discovery_registry_consistency_check.py.
    """
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from agentic_core.L0_maintenance.scripts.full_agent_discovery import (
        perform_deep_integrity_scan,
    )
    from agentic_core.L0_maintenance.utils.ssot_discovery_util import (
        load_agent_discovery,
    )

    raw = load_agent_discovery(project_root, force_reload=True)
    verified, stats = perform_deep_integrity_scan(raw, project_root)

    agent_ids = tuple(
        sorted(a.get("canonical_class", "") or a.get("class_name", "") for a in verified),
    )
    fingerprint = _compute_fingerprint(agent_ids)

    return ActiveSetResult(
        agents=tuple(verified),
        agent_ids=agent_ids,
        count=len(verified),
        fingerprint=fingerprint,
        stats=stats,
    )
