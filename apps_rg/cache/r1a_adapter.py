"""R1A exact-hash cache helpers (deterministic filesystem index under runs_dir).

Contract:
- Stamp JSON envelope ``r1a_stamp.json`` (primary) alongside ``generated_resume.json``.
- Preserve read-compat for legacy ``r1a_key.txt`` stamps.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any

CACHE_SCHEMA_VERSION = "2026-05-02-r1a-v2"


def compute_r1a_key(
    *,
    source_resume_hash: str,
    target_company: str,
    target_role: str,
) -> str:
    """Return a deterministic 64-hex fingerprint for (resume_snapshot, tenant shape)."""
    corp = target_company.strip().lower()
    role = target_role.strip().lower()
    resume = source_resume_hash.strip()
    envelope = f"r1a|v1|{resume}|{corp}|{role}"
    return hashlib.sha256(envelope.encode("utf-8")).hexdigest()


def stamp_r1a_cache(
    key: str,
    run_dir: str | Path,
    *,
    policy_hash: str | None = None,
    blueprint_hash: str | None = None,
) -> None:
    """Write ``r1a_stamp.json`` into an existing artifact directory."""
    rd = Path(run_dir)
    rd.mkdir(parents=True, exist_ok=True)
    blob: dict[str, Any] = {
        "key": key,
        "schema_version": CACHE_SCHEMA_VERSION,
        "stamped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if policy_hash is not None:
        blob["policy_hash"] = policy_hash
    if blueprint_hash is not None:
        blob["blueprint_hash"] = blueprint_hash
    stamp_path = rd / "r1a_stamp.json"
    stamp_path.write_text(json.dumps(blob, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stamp_matches_requested(
    stamp: dict[str, Any],
    key: str,
    *,
    policy_hash: str | None,
    blueprint_hash: str | None,
) -> bool:
    if str(stamp.get("key", "")).strip() != str(key).strip():
        return False
    if policy_hash is not None:
        stamped = stamp.get("policy_hash")
        if stamped is not None and str(stamped) != str(policy_hash):
            return False
    if blueprint_hash is not None:
        stamped = stamp.get("blueprint_hash")
        if stamped is not None and str(stamped) != str(blueprint_hash):
            return False
    return True


def check_r1a_cache(
    key: str,
    *,
    runs_dir: Path | str,
    policy_hash: str | None = None,
    blueprint_hash: str | None = None,
) -> str | None:
    """Return artifact directory containing a stamped hit, or ``None``."""
    root = Path(runs_dir)
    if not root.is_dir():
        return None

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        resume = child / "generated_resume.json"
        if not resume.is_file():
            continue

        stamp_file = child / "r1a_stamp.json"
        if stamp_file.is_file():
            try:
                stamp = json.loads(stamp_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError):
                continue
            if isinstance(stamp, dict) and _stamp_matches_requested(
                stamp, key, policy_hash=policy_hash, blueprint_hash=blueprint_hash
            ):
                return str(child.resolve())
            continue

        txt = child / "r1a_key.txt"
        if txt.is_file():
            legacy = txt.read_text(encoding="utf-8").strip()
            if legacy == key.strip():
                if policy_hash is not None or blueprint_hash is not None:
                    continue
                return str(child.resolve())

    return None


def prune_stale_r1a_entries(
    *,
    runs_dir: Path | str,
    policy_hash: str | None = None,
    blueprint_hash: str | None = None,
    dry_run: bool = False,
) -> list[str]:
    """Remove run directories stamped with mismatched hashes (destructive helper)."""
    root = Path(runs_dir)
    if not root.is_dir():
        return []

    pruned: list[str] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        stamp_file = child / "r1a_stamp.json"
        if not stamp_file.is_file():
            continue
        try:
            stamp = json.loads(stamp_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, TypeError):
            continue
        if not isinstance(stamp, dict):
            continue

        stale = False
        if policy_hash is not None and "policy_hash" in stamp:
            if str(stamp.get("policy_hash")) != str(policy_hash):
                stale = True
        if blueprint_hash is not None and "blueprint_hash" in stamp:
            if str(stamp.get("blueprint_hash")) != str(blueprint_hash):
                stale = True

        if stale:
            pruned.append(child.name)
            if not dry_run:
                shutil.rmtree(child, ignore_errors=True)  # guardian: allow-missing-hitl-on-irreversible -- stale cache-dir prune; ephemeral blueprint artifacts only

    return pruned
