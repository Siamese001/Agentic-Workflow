"""Capture-time precedent metadata for Author-Gate (W1).

Runs ``lookup_refactor_decisions`` in a subprocess and persists digest + match
ids. Fail-soft: on lookup failure, optionally falls back to sidecar match ids.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOKUP_SCRIPT = REPO_ROOT / ".claude" / "skills" / "refactor-decision-memory" / "lookup_refactor_decisions.py"

PRECEDENT_LOOKUP_POLICY_VERSION = "lookup-rules-v1+w1-metadata-20260517"


def _canonical_query_payload(
    decision_type: str,
    normalized_intent: str,
    repo_area: str,
    *,
    layer: str,
    degraded_scope: bool,
    limit: int,
) -> dict[str, Any]:
    return {
        "decision_type": (decision_type or "").strip(),
        "normalized_intent": (normalized_intent or "").strip(),
        "repo_area": (repo_area or "").strip(),
        "layer": (layer or "").strip(),
        "limit": int(limit),
        "degraded_scope": bool(degraded_scope),
    }


def _digest_for_query(query: dict[str, Any]) -> str:
    canonical = json.dumps(query, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _match_ids_from_sidecar(sidecar: dict[str, Any] | None) -> list[str]:
    if not sidecar or not isinstance(sidecar.get("matches"), list):
        return []
    out: list[str] = []
    for m in sidecar["matches"]:
        if isinstance(m, dict):
            did = m.get("decision_id")
            if did:
                out.append(str(did))
    return out[:10]


def compute_precedent_capture_metadata(
    decision_type: str,
    normalized_intent: str,
    repo_area: str,
    *,
    layer: str = "",
    degraded_scope: bool = False,
    sidecar: dict[str, Any] | None = None,
    lookup_limit: int = 5,
    timeout_s: float = 45.0,
) -> dict[str, Any | None]:
    """Return columns for ``decisions`` W1 precedent metadata (may contain nulls)."""
    query = _canonical_query_payload(
        decision_type,
        normalized_intent,
        repo_area,
        layer=layer,
        degraded_scope=degraded_scope,
        limit=lookup_limit,
    )
    digest = _digest_for_query(query)
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    out: dict[str, Any | None] = {
        "precedent_lookup_query_digest": digest,
        "precedent_lookup_policy_version": PRECEDENT_LOOKUP_POLICY_VERSION,
        "precedent_capture_utc": captured_at,
        "precedent_match_count": None,
        "precedent_top_match_ids_json": None,
        "precedent_verdict_from_lookup": None,
        "precedent_lookup_ok": False,
        "precedent_lookup_reason": None,
    }

    if not query["normalized_intent"]:
        side_ids = _match_ids_from_sidecar(sidecar)
        out["precedent_top_match_ids_json"] = json.dumps(side_ids) if side_ids else json.dumps([])
        out["precedent_match_count"] = len(side_ids) if side_ids else 0
        return out

    if not LOOKUP_SCRIPT.is_file():
        side_ids = _match_ids_from_sidecar(sidecar)
        out["precedent_top_match_ids_json"] = json.dumps(side_ids) if side_ids else json.dumps([])
        out["precedent_match_count"] = len(side_ids) if side_ids else None
        return out

    try:
        proc = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT)],
            input=json.dumps(query),
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_s,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        side_ids = _match_ids_from_sidecar(sidecar)
        out["precedent_top_match_ids_json"] = json.dumps(side_ids) if side_ids else json.dumps([])
        out["precedent_match_count"] = len(side_ids) if side_ids else None
        return out

    raw = (proc.stdout or "").strip()
    if proc.returncode != 0 or not raw:
        side_ids = _match_ids_from_sidecar(sidecar)
        out["precedent_top_match_ids_json"] = json.dumps(side_ids) if side_ids else json.dumps([])
        out["precedent_match_count"] = len(side_ids) if side_ids else None
        return out
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        side_ids = _match_ids_from_sidecar(sidecar)
        out["precedent_top_match_ids_json"] = json.dumps(side_ids) if side_ids else json.dumps([])
        out["precedent_match_count"] = len(side_ids) if side_ids else None
        return out

    if isinstance(parsed, dict) and "verdict" in parsed:
        out["precedent_lookup_ok"] = True

    matches = parsed.get("matches") if isinstance(parsed.get("matches"), list) else []
    ids_from_lookup = [str(m.get("decision_id")) for m in matches if isinstance(m, dict) and m.get("decision_id")]
    verdict = parsed.get("verdict")
    if isinstance(verdict, str):
        out["precedent_verdict_from_lookup"] = verdict.strip().lower()
    reason = parsed.get("reason")
    if isinstance(reason, str) and reason.strip():
        out["precedent_lookup_reason"] = reason.strip()[:500]

    out["precedent_match_count"] = len(matches)
    out["precedent_top_match_ids_json"] = json.dumps(ids_from_lookup[:10])

    if not ids_from_lookup and sidecar:
        side_ids = _match_ids_from_sidecar(sidecar)
        if side_ids:
            out["precedent_top_match_ids_json"] = json.dumps(side_ids)
            out["precedent_match_count"] = max(len(matches), len(side_ids))

    return out
