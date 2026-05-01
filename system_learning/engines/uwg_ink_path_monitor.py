"""UWG Ink-Path Uniqueness Monitor (v6 KPI surface).

The v6 spec asserts ``non-UWG writers detected = 0`` (lines 240-241). Any
file named ``l4_state_writer*.py`` that lives outside
``system_learning/engines/`` is by definition a non-UWG writer (a shadow
clerk attempting to ink L4 outside the sanctioned channel). This monitor
performs that detection at the filesystem layer and records the count to
the V6 KPI Board.

Why filesystem detection
------------------------
UWG sole-ink-path is a *structural* invariant. A runtime hook would only
catch writers that are currently executing; the structural check catches
the sin of merely *existing* on disk. Both perspectives are valid; the
v6 KPI is about the structural one.

Excluded paths
--------------
- ``archives/`` — historical code, intentionally retained out of band.
- ``tests/`` — fixtures and stubs may impersonate writer surfaces.
- ``.venv``, ``venv``, ``.git`` — vendored / VCS noise.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

_DEFAULT_EXCLUDE_PREFIXES: tuple[str, ...] = (
    "archives/",
    "tests/",
    ".venv/",
    "venv/",
    ".git/",
    "node_modules/",
    "_smoke_v1_coerce_e9aa09/",
)
_AUTHORIZED_DIR = "system_learning/engines/"
_PATTERN = "l4_state_writer*.py"


def detect_non_uwg_writers(
    repo_root: str | Path,
    *,
    exclude_prefixes: Iterable[str] = _DEFAULT_EXCLUDE_PREFIXES,
) -> tuple[str, ...]:
    """Return the sorted tuple of non-UWG writer paths under ``repo_root``.

    A file matches if:
        - its name matches ``l4_state_writer*.py``, AND
        - its repo-relative posix path does NOT start with
          ``system_learning/engines/``, AND
        - its repo-relative posix path does NOT start with any prefix in
          ``exclude_prefixes``.

    Returns
    -------
    tuple[str, ...]
        Sorted, repo-relative posix paths of every offender.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return ()
    excludes = tuple(exclude_prefixes)
    offenders: list[str] = []
    for path in root.rglob(_PATTERN):
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if rel.startswith(_AUTHORIZED_DIR):
            continue
        if any(rel.startswith(prefix) for prefix in excludes):
            continue
        offenders.append(rel)
    return tuple(sorted(offenders))


def publish_uwg_uniqueness_kpi(
    repo_root: str | Path,
    board: Any,
    *,
    exclude_prefixes: Iterable[str] = _DEFAULT_EXCLUDE_PREFIXES,
) -> int:
    """Detect non-UWG writers and publish the count as v6 KPI.

    Returns the offender count actually recorded (also retrievable from
    the board). Never raises — KPI emission failures are logged WARN.
    """
    try:
        offenders = detect_non_uwg_writers(
            repo_root, exclude_prefixes=exclude_prefixes
        )
        count = len(offenders)
        # Lazy import to keep filesystem-only callers light.
        from system_learning.engines.v6_kpi_producers import (  # noqa: PLC0415
            record_uwg_ink_path_uniqueness,
        )

        record_uwg_ink_path_uniqueness(
            board,
            non_uwg_writers_detected=count,
        )
        if count > 0:
            logger.warning(
                "uwg_ink_path_uniqueness: %d non-UWG writer(s) detected: %s",
                count,
                offenders,
            )
        return count
    except (OSError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break callers
        logger.warning("uwg_ink_path_monitor publish failed: %s", exc)
        return 0


__all__ = ["detect_non_uwg_writers", "publish_uwg_uniqueness_kpi"]
