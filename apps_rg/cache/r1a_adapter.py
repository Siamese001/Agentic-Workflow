"""R1A exact-match cache adapter for apps_rg.

R1A deduplicates identical requests by computing a SHA-256 over the full
deterministic input surface: jd_text + master_resume_hash + company_brief_hash
+ policy_hash + blueprint_hash + schema_hash + cache_schema_version.

If an identical request was previously executed and the output artifact exists
on disk, R1A returns the cached path for an immediate terminal return.

R1A runs BEFORE R1B (semantic cache) in the route chain:
  R1A exact → R1B semantic → R5 prerequisite → L2 execute

Plan: apps-rg-spine-deferred-followup-d4e7b2 W1.P1.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional

_log = logging.getLogger(__name__)

# Bump this when the cache key composition changes to invalidate all prior entries.
CACHE_SCHEMA_VERSION = "1"

# Stamp file name — written as JSON envelope so per-entry metadata survives schema bumps.
_STAMP_FILENAME = "r1a_stamp.json"
# Legacy plain-text stamp (pre-W2). Still read for backward compat; never written.
_LEGACY_STAMP_FILENAME = "r1a_key.txt"


def compute_r1a_key(
    source_resume_hash: str,
    target_company: str,
    target_role: str,
    jd_hash: str = "none",
    briefing_hash: str = "none",
    policy_hash: str = "unknown",
    blueprint_hash: str = "unknown",
    cache_schema_version: str = CACHE_SCHEMA_VERSION,
) -> str:
    """Compute the R1A exact-match cache key.

    All inputs are hashed together into a single SHA-256 digest. Any change
    to any field produces a different key — this is intentional exact-match.
    """
    payload = json.dumps(
        {
            "source_resume_hash": source_resume_hash,
            "target_company": target_company.strip().lower(),
            "target_role": target_role.strip().lower(),
            "jd_hash": jd_hash,
            "briefing_hash": briefing_hash,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "v": cache_schema_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _read_stamp(run_dir: Path) -> Optional[dict]:
    """Read the R1A stamp for run_dir.  Supports both JSON (v2) and legacy text (v1)."""
    stamp_file = run_dir / _STAMP_FILENAME
    if stamp_file.exists():
        try:
            return json.loads(stamp_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
    legacy = run_dir / _LEGACY_STAMP_FILENAME
    if legacy.exists():
        try:
            raw = legacy.read_text(encoding="utf-8").strip()
            return {"key": raw, "schema_version": "1"}  # legacy has no policy/blueprint fields
        except OSError:
            return None
    return None


def check_r1a_cache(
    key: str,
    runs_dir: Optional[Path] = None,
    policy_hash: Optional[str] = None,
    blueprint_hash: Optional[str] = None,
) -> Optional[str]:
    """Check R1A exact-match cache for a prior run with identical inputs.

    Scans ``runs_dir`` for a subdirectory whose stamp matches the given key
    and whose ``generated_resume.json`` exists.  When ``policy_hash`` or
    ``blueprint_hash`` are supplied the per-entry metadata is also checked
    so that a global ``CACHE_SCHEMA_VERSION`` bump is not required for
    policy/blueprint rotations.

    Returns:
        String path to the matching run directory on hit, None on miss.
    """
    if runs_dir is None:
        runs_dir = Path("artifacts/apps_rg/runs")

    _log.debug("[R1A] Checking exact cache for key=%s", key[:16])

    if not runs_dir.is_dir():
        return None

    for run_dir in sorted(runs_dir.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        output_file = run_dir / "generated_resume.json"
        if not output_file.exists():
            continue
        stamp = _read_stamp(run_dir)
        if stamp is None:
            continue
        if stamp.get("key") != key:
            continue
        # Per-entry policy/blueprint check (finer-grained than global schema bump)
        if policy_hash is not None and stamp.get("policy_hash") not in (None, policy_hash):
            _log.info(
                "[R1A] Skipping stale entry (policy mismatch): %s", run_dir.name
            )
            continue
        if blueprint_hash is not None and stamp.get("blueprint_hash") not in (None, blueprint_hash):
            _log.info(
                "[R1A] Skipping stale entry (blueprint mismatch): %s", run_dir.name
            )
            continue
        _log.info("[R1A] Exact cache hit: %s", run_dir.name)
        return str(run_dir)

    _log.debug("[R1A] Exact cache miss")
    return None


def stamp_r1a_cache(
    key: str,
    run_dir_path: str,
    policy_hash: Optional[str] = None,
    blueprint_hash: Optional[str] = None,
) -> None:
    """Write the R1A stamp to the run directory for future cache hits.

    Writes a JSON envelope (``r1a_stamp.json``) that records the key plus
    optional per-entry ``policy_hash`` and ``blueprint_hash``.  The legacy
    ``r1a_key.txt`` is no longer written (read-compat still present in
    ``_read_stamp``).

    Call this after a successful L2 execution to enable future R1A dedup.
    """
    run_dir = Path(run_dir_path)
    stamp = {
        "key": key,
        "schema_version": CACHE_SCHEMA_VERSION,
        "stamped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if policy_hash is not None:
        stamp["policy_hash"] = policy_hash
    if blueprint_hash is not None:
        stamp["blueprint_hash"] = blueprint_hash
    stamp_file = run_dir / _STAMP_FILENAME
    stamp_file.write_text(json.dumps(stamp, indent=2), encoding="utf-8")
    _log.debug("[R1A] Stamped key=%s to %s", key[:16], stamp_file)


def prune_stale_r1a_entries(
    runs_dir: Optional[Path] = None,
    policy_hash: Optional[str] = None,
    blueprint_hash: Optional[str] = None,
    dry_run: bool = False,
) -> list[str]:
    """Remove run directories whose R1A stamp is stale.

    A directory is considered stale when:
    - It has a stamp whose ``schema_version`` < ``CACHE_SCHEMA_VERSION``, OR
    - The stamp records a ``policy_hash`` that differs from the current one, OR
    - The stamp records a ``blueprint_hash`` that differs from the current one.

    Returns list of removed (or would-be removed if dry_run) directory names.
    Fail-soft: individual removal errors are logged and skipped.
    """
    if runs_dir is None:
        runs_dir = Path("artifacts/apps_rg/runs")
    if not runs_dir.is_dir():
        return []

    pruned: list[str] = []
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        stamp = _read_stamp(run_dir)
        if stamp is None:
            continue
        stale = False
        if stamp.get("schema_version", "0") < CACHE_SCHEMA_VERSION:
            stale = True
        if policy_hash and stamp.get("policy_hash") not in (None, policy_hash):
            stale = True
        if blueprint_hash and stamp.get("blueprint_hash") not in (None, blueprint_hash):
            stale = True
        if not stale:
            continue
        _log.info("[R1A] %sPruning stale entry: %s", "(dry-run) " if dry_run else "", run_dir.name)
        pruned.append(run_dir.name)
        if not dry_run:
            try:
                import shutil
                shutil.rmtree(run_dir)
            except OSError as exc:  # guardian: allow-broad-exception -- pruning is fail-soft
                _log.warning("[R1A] Failed to prune %s: %s", run_dir.name, exc)
    return pruned


__all__ = [
    "CACHE_SCHEMA_VERSION",
    "check_r1a_cache",
    "compute_r1a_key",
    "stamp_r1a_cache",
    "prune_stale_r1a_entries",
]
