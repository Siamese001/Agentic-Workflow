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
# Canonical SSOT schema (plan author-gate-ssot-consolidation-b7c3e1).
# Legacy decision_record.schema.json remains the ledger-row schema; this
# packet schema is the emit-time SSOT shared with all 4 audit hooks.
SCHEMA_PATH = REPO_ROOT / ".windsurf" / "schemas" / "author_gate_packet.schema.json"
RULE_PATH = REPO_ROOT / ".windsurf" / "rules" / "author-gate-enforcement.md"
PRECEDENT_SCRIPT = Path(__file__).resolve().parent / "precedent_injector.py"

# Shared schema loader — single import surface for emit + audits.
sys.path.insert(0, str(REPO_ROOT))
try:
    from tools.author_gate.schema_loader import validate as _schema_validate  # noqa: E402
except ImportError:  # guardian: allow-broad -- schema loader optional at boot
    _schema_validate = None  # type: ignore

SURFACE_THRESHOLD = 0.72
DOMINANCE_SCORE = 0.85
DOMINANCE_DELTA = 0.12
MAX_SURFACE_OPTIONS = 4

# plan author-gate-hardening-a3b8f2 W1.P1.3 — reason-code enum surfaced to approver
REASON_CODE_PALETTE = [
    "override_recommendation",
    "insufficient_precedent",
    "blast_radius_too_high",
    "principle_shift",
    "test_strategy_change",
    "dependency_risk",
    "deletion_risk",
    "other",
]

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
    """Schema-first validation against the canonical SSOT schema.

    Plan author-gate-ssot-consolidation-b7c3e1 W2.P2.1: prefer jsonschema lib
    against ``.windsurf/schemas/author_gate_packet.schema.json`` and fall back
    to the legacy hand-rolled checks when the lib is unavailable.
    """
    errors: list[str] = []
    if _schema_validate is not None:
        for finding in _schema_validate(packet):
            if finding.get("invariant") == "schema_lib_missing":
                break  # fall through to legacy hand-validation
            errors.append(
                f"schema[{finding.get('path')}]: {finding.get('message', '')}"
            )
        else:
            # Append AG-10 didactic checks not expressible in JSON Schema.
            for opt in packet.get("candidates") or []:
                errors.extend(_validate_option_didactic(opt))
            return errors
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

    # Pre-routing ranking for packet-level metadata only.
    ranked = sorted(candidates_in, key=lambda c: float(c.get("confidence_score", 0)), reverse=True)

    annotated, routing = apply_routing([dict(c) for c in candidates_in])

    # recommended_option_id is set ONLY when dominance fires; otherwise no recommendation exists.
    recommended_id = (
        ranked[0].get("id") if ranked and routing.get("rule_applied") == "dominance_fires" else None
    )

    # Gold-star ONLY when dominance fires (author-gate-enforcement.md Pipeline step 7).
    # In any other routing verdict (surface_top_N, low_confidence_ambiguity, empty)
    # no option is starred — the gate verdict is "user-decision-required" and there
    # is no recommendation. Every surfaced option still carries a [confidence=0.NN]
    # prefix so the UI always shows the score.
    dominance_fired = routing.get("rule_applied") == "dominance_fires"
    surfaced_sorted = sorted(
        (c for c in annotated if c.get("surfaced")),
        key=lambda c: float(c.get("confidence_score", 0)),
        reverse=True,
    )
    for idx, opt in enumerate(surfaced_sorted):
        score = float(opt.get("confidence_score", 0))
        title = opt.get("thesis", opt.get("id", ""))[:80]
        if dominance_fired and idx == 0:
            opt["is_recommended"] = True
            opt["surface_label"] = f"⭐ Recommended — {title}"
            prefix = f"[RECOMMENDED ⭐ confidence={score:.2f}]"
        else:
            opt["is_recommended"] = False
            opt["surface_label"] = title
            prefix = f"[confidence={score:.2f}]"
        opt["surface_description_prefix"] = prefix
        # Plan author-gate-four-req-enforcement-c4d2a8 W1.P1.
        # Floor = prefix + ` · trade-off: <first key_tradeoff truncated>`. This is
        # the deterministic minimum every surfaced option ships with so the
        # approver always sees one tradeoff. UI-audit invariant 4 enforces this
        # segment is present.
        # surface_description = the canonical wire description the renderer feeds
        # into ask_user_question. Defaults to floor; callers may set it on the
        # input spec to extend (e.g., append a second tradeoff sentence).
        tradeoffs = opt.get("key_tradeoffs") or []
        first_tradeoff = ""
        if isinstance(tradeoffs, list) and tradeoffs:
            t0 = tradeoffs[0]
            if isinstance(t0, str):
                first_tradeoff = t0.strip()[:80]
        # Fallback if the option somehow lacks a tradeoff (didactic validator
        # would already have warned at emit time): use what_youd_miss as a
        # last-ditch tradeoff sentence so the floor stays well-formed.
        if not first_tradeoff:
            wym = str(opt.get("what_youd_miss") or "").strip()
            first_tradeoff = wym[:80] if wym else "see candidate.key_tradeoffs"
        floor = f"{prefix} · trade-off: {first_tradeoff}"
        opt["surface_description_floor"] = floor
        existing = opt.get("surface_description")
        if isinstance(existing, str) and existing.strip():
            # Caller supplied an extension; prepend the floor if not already there.
            if not existing.startswith(prefix):
                opt["surface_description"] = f"{floor} · {existing.strip()}"
            else:
                opt["surface_description"] = existing.strip()
        else:
            opt["surface_description"] = floor

    precedent = _fetch_precedent(decision_type, intent, spec.get("repo_area"))
    fingerprint = _context_fingerprint(files_in_scope)

    # W2.P2.1 — attach signal vector per surfaced candidate when signal_collector
    # is available. Fail-soft: skill still emits valid packets without it.
    _attach_signal_vectors(annotated, decision_type, spec)

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
        # plan author-gate-hardening-a3b8f2 W1.P1.3 — reason-code palette surfaced to approver
        "reason_code_palette": REASON_CODE_PALETTE,
        # W3.P3.1 — calibrator stamps (populated by weekly calibrator; NULL during cold-start)
        "calibrator_version": _latest_calibrator_version(decision_type),
    }
    return packet


def _attach_signal_vectors(
    annotated: list[dict[str, Any]], decision_type: str, spec: dict[str, Any]
) -> None:
    """W2.P2.1 — compute a 5-signal confidence vector per surfaced candidate.

    Signals + weights (sum=1.0):
        verbalized              0.15  (candidate.confidence_score)
        precedent_agreement     0.30  (spec['precedent_agreement_by_option'][id], default 0.5)
        blast_radius_penalty    0.20  (1 - min(spec['blast_radius_hops']/5, 1), default 1.0)
        hotspot_penalty         0.15  (1 - spec['adg_hotspot_rank']/top_N, default 1.0)
        rule_violation_penalty  0.20  (1 if id not in spec['rule_flagged_options'], else 0)

    Each signal is recorded on the option under ``signals`` as a dict; the
    weighted raw sum is stored as ``raw_score``. ``confidence_calibrated``
    is left unset here — the calibrator persists it separately.
    """
    weights = {
        "verbalized": 0.15,
        "precedent_agreement": 0.30,
        "blast_radius_penalty": 0.20,
        "hotspot_penalty": 0.15,
        "rule_violation_penalty": 0.20,
    }
    precedent_by_opt = spec.get("precedent_agreement_by_option") or {}
    hops = spec.get("blast_radius_hops")
    hotspot = spec.get("adg_hotspot_rank")
    hotspot_top_n = spec.get("adg_hotspot_top_n") or 100
    rule_flagged = set(spec.get("rule_flagged_options") or [])

    for opt in annotated:
        if not opt.get("surfaced"):
            continue
        oid = opt.get("id", "")
        verbalized = float(opt.get("confidence_score", 0))
        precedent = float(precedent_by_opt.get(oid, 0.5))
        if hops is None:
            blast = 1.0
        else:
            try:
                blast = 1.0 - min(float(hops) / 5.0, 1.0)
            except (TypeError, ValueError):
                blast = 1.0
        if hotspot is None:
            hspot = 1.0
        else:
            try:
                hspot = max(0.0, 1.0 - (float(hotspot) / float(hotspot_top_n)))
            except (TypeError, ValueError):
                hspot = 1.0
        rule = 0.0 if oid in rule_flagged else 1.0
        signals = {
            "verbalized": verbalized,
            "precedent_agreement": precedent,
            "blast_radius_penalty": blast,
            "hotspot_penalty": hspot,
            "rule_violation_penalty": rule,
        }
        raw_score = sum(signals[k] * weights[k] for k in weights)
        opt["signals"] = signals
        opt["signal_weights"] = weights
        opt["raw_score"] = round(raw_score, 4)


def _latest_calibrator_version(decision_type: str) -> str | None:
    """Read the most recent calibrator version for this decision_type, if any.

    Fail-soft: returns None when the ledger / snapshot is not yet populated.
    """
    try:
        import sqlite3 as _sqlite3  # pylint: disable=import-outside-toplevel

        db = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
        if not db.exists():
            return None
        with _sqlite3.connect(str(db), timeout=3) as conn:
            row = conn.execute(
                "SELECT calibrator_version FROM decision_calibration_snapshots "
                "WHERE decision_type = ? ORDER BY created_at DESC LIMIT 1",
                (decision_type,),
            ).fetchone()
            return row[0] if row else None
    except Exception:  # guardian: allow-broad -- fail-soft version probe, non-fatal
        return None


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

    # Emit the packet. Canonical marker only — HITL_PACKET alias retired
    # per DS-4 of plan author-gate-pipeline-hardening-deferred-b3e1d7.
    # Scanners still detect HITL_PACKET for backward compat with older logs.
    body = json.dumps(packet, indent=2)
    sys.stdout.write("AUTHOR_GATE_PACKET: " + body + "\n")

    # W3.P3.1 — emit a ROUTER_DECISION marker so the Author-Gate participates
    # in the closed-loop router family (constitutional §29). `layer=author_gate`
    # is the 11th synthetic router at the harness plane.
    rd_fields = [
        "layer=author_gate",
        f"decision_id={packet['decision_id']}",
        f"decision_type={packet['decision_type']}",
        f"rule_applied={packet['routing'].get('rule_applied', 'unknown')}",
        f"top_score={packet.get('confidence_top') or 0:.2f}",
        f"dominance_gap={packet['routing'].get('dominance_delta_observed') or 0:.2f}",
        f"surfaced={sum(1 for c in packet.get('candidates', []) if c.get('surfaced'))}",
        f"precedent={packet.get('precedent', {}).get('verdict', 'none')}",
        "outcome=pending",
    ]
    sys.stdout.write("ROUTER_DECISION: " + ", ".join(rd_fields) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
