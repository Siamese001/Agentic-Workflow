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
from pathlib import Path
from typing import Optional

_log = logging.getLogger(__name__)

# Bump this when the cache key composition changes to invalidate all prior entries.
CACHE_SCHEMA_VERSION = "1"


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


def check_r1a_cache(
    key: str,
    runs_dir: Optional[Path] = None,
) -> Optional[str]:
    """Check R1A exact-match cache for a prior run with identical inputs.

    Scans ``runs_dir`` for a subdirectory whose ``r1a_key.txt`` matches
    the given key and whose ``generated_resume.json`` exists.

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
        key_file = run_dir / "r1a_key.txt"
        output_file = run_dir / "generated_resume.json"
        if key_file.exists() and output_file.exists():
            try:
                stored_key = key_file.read_text(encoding="utf-8").strip()
                if stored_key == key:
                    _log.info("[R1A] Exact cache hit: %s", run_dir.name)
                    return str(run_dir)
            except OSError:
                continue

    _log.debug("[R1A] Exact cache miss")
    return None


def stamp_r1a_cache(
    key: str,
    run_dir_path: str,
) -> None:
    """Write the R1A key to the run directory for future cache hits.

    Call this after a successful L2 execution to enable future R1A dedup.
    """
    run_dir = Path(run_dir_path)
    key_file = run_dir / "r1a_key.txt"
    key_file.write_text(key, encoding="utf-8")
    _log.debug("[R1A] Stamped key=%s to %s", key[:16], key_file)


__all__ = [
    "CACHE_SCHEMA_VERSION",
    "check_r1a_cache",
    "compute_r1a_key",
    "stamp_r1a_cache",
]
