#!/usr/bin/env python3
"""
emit_packet.py — Construct + validate + emit an AUTHOR_GATE_PACKET JSON block (with HITL_PACKET legacy alias).

Pipeline:
    1. Read input packet spec from stdin (decision_type, intent, candidates, ...)
    2. Enrich with:
         - context_fingerprint (git sha, branch, files_in_scope, fp hash)
         - policy_snapshot (hash of author-gate-enforcement rule)
         - precedent (via precedent_injector.py)
         - routing rules (dominance / low-conf / surface-top-N)
         - decision_id (ulid-like)
    3. Validate against .windsurf/schemas/decision_record.schema.json
    4. Emit AUTHOR_GATE_PACKET: {<json>} to stdout (with HITL_PACKET: legacy alias)
    5. Exit 0 on success, 1 on validation failure, 2 on fatal error

STDIN JSON shape:
    {
        "decision_type": "refactor_scope",
        "user_goal": "Extract L2 adapter",
        "normalized_intent": "Split agentic_core/L2_execution/adapters.py into 3 files",
        "files_in_scope": ["agentic_core/L2_execution/adapters.py"],
        "repo_area": "agentic_core/L2_execution",
        "candidates": [
            {"id": "minimal", "thesis": "...", "confidence_score": 0.88, ...},
            ...
        ]
    }

CONSTITUTIONAL
    - subprocess.run with argv + shell=False + timeout
    - UTF-8 stdio
    - Specific exceptions only
    - No PowerShell; pure Python
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / ".windsurf" / "schemas" / "decision_record.schema.json"
RULE_PATH = REPO_ROOT / ".windsurf" / "rules" / "author-gate-enforcement.md"
PRECEDENT_SCRIPT = Path(__file__).resolve().parent / "precedent_injector.py"

SURFACE_THRESHOLD = 0.72
DOMINANCE_SCORE = 0.85
DOMINANCE_DELTA = 0.12
MAX_SURFACE_OPTIONS = 4

GIT_TIMEOUT_S = 10
PRECEDENT_TIMEOUT_S = 25

_REQUIRED_OPTION_FIELDS = [
    "id",
    "thesis",
    "confidence_score",
    "principle_at_stake",
    "what_youd_miss",
    "what_would_flip",
]


# ===================================================================== #
# Helpers                                                               #
# ===================================================================== #


def _run(argv: list[str], timeout: int, cwd: Path | None = None, stdin: str | None = None) -> str:
    try:
        result = subprocess.run(
            argv,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout,
            check=False,
            input=stdin,
        )
    except (subprocess.TimeoutExpired, OSError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def _make_decision_id() -> str:
    ts = int(time.time() * 1000)
    rand = secrets.token_hex(3)
    # dec_ + 6+ lowercase hex per schema pattern
    return f"dec_{ts:x}{rand}"


def _policy_snapshot() -> str:
    if not RULE_PATH.exists():
        return "unknown"
    content = RULE_PATH.read_bytes()
    sha = hashlib.sha256(content).hexdigest()[:10]
    return f"author-gate@{sha}"


def _context_fingerprint(files_in_scope: list[str]) -> dict[str, Any]:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], GIT_TIMEOUT_S).strip() or "unknown"
    git_sha = _run(["git", "rev-parse", "HEAD"], GIT_TIMEOUT_S).strip() or "unknown"
    # fp matches pre_author_gate.py fingerprint algorithm
    canon = "|".join(sorted(set(files_in_scope)))
    fp = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
    return {
        "adg_snapshot": _find_latest_adg_snapshot(),
        "git_sha": git_sha,
        "branch": branch,
        "files_in_scope": files_in_scope,
        "fp": fp,
    }


def _find_latest_adg_snapshot() -> str:
    adg_dir = REPO_ROOT / "artifacts" / "adg"
    if not adg_dir.exists():
        return "none"
    candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].name if candidates else "none"


def _fetch_precedent(decision_type: str, intent: str, repo_area: str | None) -> dict[str, Any]:
    query = {
        "decision_type": decision_type,
        "normalized_intent": intent or "",
        "repo_area": repo_area or "",
        "limit": 3,
    }
    raw = _run(
        [sys.executable, str(PRECEDENT_SCRIPT)],
        PRECEDENT_TIMEOUT_S,
        stdin=json.dumps(query),
    )
    if not raw.strip():
        return {"verdict": "none", "matched_ids": [], "summary": "precedent lookup returned empty"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"verdict": "none", "matched_ids": [], "summary": "precedent lookup invalid JSON"}


# ===================================================================== #
# Routing                                                               #
# ===================================================================== #


def apply_routing(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply thresholds + dominance. Returns (annotated_candidates, routing_info)."""
    # Sort by confidence DESC; fallback to stable order
    sorted_c = sorted(candidates, key=lambda c: float(c.get("confidence_score", 0)), reverse=True)

    if not sorted_c:
        return [], {"rule_applied": "empty", "surface_threshold": SURFACE_THRESHOLD}

    top_score = float(sorted_c[0].get("confidence_score", 0))
    second_score = float(sorted_c[1].get("confidence_score", 0)) if len(sorted_c) > 1 else 0.0
    dominance_gap = top_score - second_score

    # Low-confidence ambiguity
    if top_score < SURFACE_THRESHOLD:
        for c in sorted_c:
            c["surfaced"] = False
            c["suppression_reason"] = "below_surface_threshold"
        return sorted_c, {
            "rule_applied": "low_confidence_ambiguity",
            "surface_threshold": SURFACE_THRESHOLD,
            "dominance_delta_observed": round(dominance_gap, 3),
            "top_score": top_score,
        }

    # Dominance
    if top_score >= DOMINANCE_SCORE and dominance_gap >= DOMINANCE_DELTA:
        for idx, c in enumerate(sorted_c):
            if idx == 0:
                c["surfaced"] = True
                c["suppression_reason"] = None
            else:
                c["surfaced"] = False
                c["suppression_reason"] = "dominance_fired"
        return sorted_c, {
            "rule_applied": "dominance_fires",
            "surface_threshold": SURFACE_THRESHOLD,
            "dominance_delta_observed": round(dominance_gap, 3),
            "top_score": top_score,
        }

    # Surface top N
    surfaced = 0
    for c in sorted_c:
        if float(c.get("confidence_score", 0)) >= SURFACE_THRESHOLD and surfaced < MAX_SURFACE_OPTIONS:
            c["surfaced"] = True
            c["suppression_reason"] = None
            surfaced += 1
        else:
            c["surfaced"] = False
            c["suppression_reason"] = "below_surface_threshold"
    return sorted_c, {
        "rule_applied": f"surface_top_{surfaced}",
        "surface_threshold": SURFACE_THRESHOLD,
        "dominance_delta_observed": round(dominance_gap, 3),
        "top_score": top_score,
    }


# ===================================================================== #
# Validation                                                            #
# ===================================================================== #


def _validate_option_didactic(opt: dict[str, Any]) -> list[str]:
    """AG-10 enforcement: surfaced options must have all 10 fields populated."""
    errors: list[str] = []
    if not opt.get("surfaced"):
        return errors  # suppressed options get a pass
    for field in _REQUIRED_OPTION_FIELDS:
        if not opt.get(field):
            errors.append(f"option[{opt.get('id')}]: missing or empty field '{field}'")
    tradeoffs = opt.get("key_tradeoffs") or []
    if isinstance(tradeoffs, list) and len(tradeoffs) < 2:
        errors.append(f"option[{opt.get('id')}]: key_tradeoffs requires ≥2 entries")
    # Didactic discipline: reject non-specific "what_would_flip"
    wwf = str(opt.get("what_would_flip") or "")
    if wwf and re.search(r"(user prefers|user wants|different|other)", wwf, re.I):
        errors.append(f"option[{opt.get('id')}]: what_would_flip appears non-falsifiable: '{wwf[:80]}'")
    return errors


def _validate_schema(packet: dict[str, Any]) -> list[str]:
    """Minimal jsonschema check (no jsonschema lib dep — hand-validate required fields)."""
    errors: list[str] = []
    for required in ("decision_id", "created_at", "decision_type", "status"):
        if not packet.get(required):
            errors.append(f"missing required field: {required}")

    if packet.get("decision_type") not in {
        "architecture_choice",
        "refactor_scope",
        "anti_pattern",
        "dependency_addition",
        "test_strategy",
        "deletion_strategy",
        "error_handling",
        "unknown",
    }:
        errors.append(f"invalid decision_type: {packet.get('decision_type')}")

    if packet.get("status") not in {"surfaced", "executed", "rolled_back", "failed"}:
        errors.append(f"invalid status: {packet.get('status')}")

    did = packet.get("decision_id") or ""
    if not re.match(r"^dec_[a-z0-9]{6,}$", did):
        errors.append(f"decision_id pattern mismatch: {did}")

    for opt in packet.get("candidates") or []:
        errors.extend(_validate_option_didactic(opt))

    return errors


# ===================================================================== #
# Main                                                                  #
# ===================================================================== #


def build_packet(spec: dict[str, Any]) -> dict[str, Any]:
    decision_type = spec.get("decision_type") or "unknown"
    intent = spec.get("normalized_intent") or ""
    files_in_scope = spec.get("files_in_scope") or []
    candidates_in = spec.get("candidates") or []

    # Recommendation winner (before routing applies suppression)
    ranked = sorted(candidates_in, key=lambda c: float(c.get("confidence_score", 0)), reverse=True)
    recommended_id = ranked[0].get("id") if ranked else None

    annotated, routing = apply_routing([dict(c) for c in candidates_in])

    # Gold-star the recommended option in-place (highest confidence among surfaced)
    surfaced_sorted = sorted(
        (c for c in annotated if c.get("surfaced")),
        key=lambda c: float(c.get("confidence_score", 0)),
        reverse=True,
    )
    if surfaced_sorted:
        top = surfaced_sorted[0]
        top["is_recommended"] = True
        top["surface_label"] = f"⭐ Recommended — {top.get('thesis', top.get('id', ''))[:80]}"
        top["surface_description_prefix"] = (
            f"[RECOMMENDED ⭐ confidence={float(top.get('confidence_score', 0)):.2f}]"
        )
        for other in surfaced_sorted[1:]:
            other["is_recommended"] = False
            other["surface_label"] = other.get("thesis", other.get("id", ""))[:80]
            other["surface_description_prefix"] = (
                f"[confidence={float(other.get('confidence_score', 0)):.2f}]"
            )

    precedent = _fetch_precedent(decision_type, intent, spec.get("repo_area"))
    fingerprint = _context_fingerprint(files_in_scope)

    packet = {
        "decision_id": _make_decision_id(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "branch": fingerprint.get("branch"),
        "commit_sha": (
            (fingerprint.get("git_sha") or "")[:12]
            if fingerprint.get("git_sha") and fingerprint.get("git_sha") != "unknown"
            else None
        ),
        "decision_type": decision_type,
        "request_summary": spec.get("request_summary"),
        "normalized_intent": intent,
        "user_goal": spec.get("user_goal"),
        "principle_at_stake": spec.get("principle_at_stake"),
        "recommended_option_id": recommended_id,
        "selected_option_id": None,
        "selection_rationale": None,
        "candidates": annotated,
        "confidence_top": float(ranked[0].get("confidence_score", 0)) if ranked else None,
        "confidence_dominance_gap": routing.get("dominance_delta_observed"),
        "override_vs_recommendation": None,  # set at selection time
        "selection_latency_ms": None,  # set at selection time
        "policy_snapshot": _policy_snapshot(),
        "context_fingerprint": fingerprint,
        "routing": routing,
        "precedent": precedent,
        "status": "surfaced",
    }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit schema-valid Author-Gate packet.")
    parser.add_argument("--strict", action="store_true", help="Fail on didactic-field warnings (AG-10)")
    parser.add_argument("--no-precedent", action="store_true", help="Skip precedent lookup (for testing)")
    args = parser.parse_args()

    try:
        spec_raw = sys.stdin.read()
        if not spec_raw.strip():
            print("[emit_packet] stdin empty", file=sys.stderr)
            return 2
        spec = json.loads(spec_raw)
    except json.JSONDecodeError as exc:
        print(f"[emit_packet] bad stdin JSON: {exc}", file=sys.stderr)
        return 2

    if args.no_precedent:
        # Monkey-patch the fetch so we don't invoke the lookup
        global _fetch_precedent
        _fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": "skipped"}  # type: ignore

    packet = build_packet(spec)
    errors = _validate_schema(packet)

    if errors and args.strict:
        for err in errors:
            print(f"[emit_packet] SCHEMA: {err}", file=sys.stderr)
        return 1
    elif errors:
        for err in errors:
            print(f"[emit_packet] WARN: {err}", file=sys.stderr)

    # Emit the packet. Two markers for compatibility:
    #   AUTHOR_GATE_PACKET: — canonical (per W4 didactic template)
    #   HITL_PACKET:        — legacy alias for post_cascade_author_gate_capture.py scanner
    body = json.dumps(packet, indent=2)
    sys.stdout.write("AUTHOR_GATE_PACKET: " + body + "\n")
    sys.stdout.write("HITL_PACKET: " + body + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
