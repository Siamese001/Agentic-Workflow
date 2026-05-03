"""W6.P2 — DOCX re-seal helper for post-run patches.

Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
Phase: W6.P2 (AG-RG-011 decision B: re-seal-helper ACTIVATED)

When a run produces `generated_resume.docx` and a downstream tool (e.g.
manual DOCX edit, ATS optimizer) modifies it, the `artifact_sha256_map`
in `runtime_exhaust_bundle.json` goes stale. Without re-sealing, the
cert bundle's sha256 binding invariant breaks.

This helper recomputes the sha256 for a patched artifact and rewrites
the `artifact_sha256_map` entry, emitting an audit trail event.

AG-RG-011 decision B (2026-05-03): Re-seal helper with audit trail is the
active policy. Forbid all patches (option A) or per-tool allowlist (option C)
may be implemented via CI gates later if operational discipline requires.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_exhaust_bundle(run_dir: Path) -> dict[str, Any] | None:
    """Read runtime_exhaust_bundle.json (fail-soft)."""
    bundle_path = run_dir / "runtime_exhaust_bundle.json"
    if not bundle_path.exists():
        return None
    try:
        return json.loads(bundle_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- re-seal must be fail-soft
        _log.warning("[reseal] Failed to parse exhaust bundle at %s", bundle_path)
        return None


def reseal_artifact(
    run_dir: Path,
    artifact_path: Path,
    *,
    reason: str = "post_run_patch",
    patcher: str = "unknown",
) -> dict[str, Any]:
    """Re-seal a patched artifact by recomputing sha256 + updating bundle.

    Args:
        run_dir: Path to artifacts/apps_rg/runs/<timestamp>/.
        artifact_path: Path to the patched artifact (MUST be within run_dir).
        reason: Why the patch happened (e.g. "docx_fixup", "manual_edit").
        patcher: Name of the tool/user that patched it.

    Returns:
        Dict with reseal result:
            {
                "success": bool,
                "artifact_relpath": str,
                "old_sha256": str | None,
                "new_sha256": str,
                "resealed_at_utc": str,
                "reason": str,
                "patcher": str,
            }

    Raises:
        ValueError: if artifact_path is not within run_dir.
    """
    # Enforce scope: artifact must be within run_dir
    try:
        artifact_relpath = str(artifact_path.relative_to(run_dir))
    except ValueError as e:
        raise ValueError(
            f"reseal_artifact: {artifact_path} is not within run_dir {run_dir}"
        ) from e

    if not artifact_path.exists():
        return {
            "success": False,
            "reason_failed": f"artifact_missing: {artifact_relpath}",
            "artifact_relpath": artifact_relpath,
        }

    new_sha256 = compute_sha256(artifact_path)
    now_utc = datetime.now(timezone.utc).isoformat()

    bundle = read_exhaust_bundle(run_dir)
    old_sha256: str | None = None

    if bundle is not None:
        sha_map = bundle.setdefault("artifact_sha256_map", {})
        old_sha256 = sha_map.get(artifact_relpath)
        sha_map[artifact_relpath] = new_sha256

        # Append audit trail
        reseal_log = bundle.setdefault("reseal_events", [])
        reseal_log.append({
            "artifact_relpath": artifact_relpath,
            "old_sha256": old_sha256,
            "new_sha256": new_sha256,
            "resealed_at_utc": now_utc,
            "reason": reason,
            "patcher": patcher,
        })

        # Write back
        bundle_path = run_dir / "runtime_exhaust_bundle.json"
        bundle_path.write_text(
            json.dumps(bundle, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        _log.info(
            "[reseal] Resealed %s: old=%s new=%s reason=%s",
            artifact_relpath, old_sha256, new_sha256, reason,
        )

    return {
        "success": True,
        "artifact_relpath": artifact_relpath,
        "old_sha256": old_sha256,
        "new_sha256": new_sha256,
        "resealed_at_utc": now_utc,
        "reason": reason,
        "patcher": patcher,
        "bundle_updated": bundle is not None,
    }


__all__ = [
    "compute_sha256",
    "read_exhaust_bundle",
    "reseal_artifact",
]
