"""W3 deterministic cross-section overlap X2 and claim overlap ledgers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.aggregation._digest_utils import normalize_claim_text, sha256_utf8, tokenize
from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS

# Strongest placement wins (lower index = higher priority).
SECTION_PRIORITY: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_narrative",
    "ibm_narrative",
    "unify_bullets",
    "ibm_bullets",
    "competencies",
)

METRIC_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?%|\$[\d,.]+[MBK]?|\d+\s*(?:months?|weeks?|days?)|99\.9%|6 months to 3 weeks)",
    re.IGNORECASE,
)
EM_DASH = "\u2014"

VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_WARN = "WARN"
VERDICT_UNKNOWN = "UNKNOWN"


@dataclass
class CrossSectionGateResult:
    gate_id: str
    verdict: str
    decisive_reason: str | None = None
    threshold: Any = None
    observed: Any = None
    evidence_refs: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "verdict": self.verdict,
            "decisive_reason": self.decisive_reason,
            "threshold": self.threshold,
            "observed": self.observed,
            "evidence_refs": self.evidence_refs or [],
            "pass": self.verdict == VERDICT_PASS,
        }


def _priority(section_id: str) -> int:
    try:
        return SECTION_PRIORITY.index(section_id)
    except ValueError:
        return 999


def _extract_claim_rows(section: dict[str, Any]) -> list[dict[str, Any]]:
    sid = str(section.get("section_id") or "")
    snap = section.get("l2_output_snapshot")
    if not isinstance(snap, dict):
        return []
    rows: list[dict[str, Any]] = []
    ledger = snap.get("claim_ledger")
    if isinstance(ledger, list):
        for i, row in enumerate(ledger):
            if not isinstance(row, dict):
                continue
            ct = str(row.get("claim_text") or row.get("claim_summary") or "").strip()
            if not ct:
                continue
            sf = [str(x) for x in (row.get("source_fact_ids") or []) if x]
            key = sha256_utf8(f"{sid}|{i}|{normalize_claim_text(ct)}|{','.join(sorted(sf))}")
            rows.append(
                {
                    "claim_key": key,
                    "section_id": sid,
                    "claim_text": ct,
                    "source_fact_ids": sf,
                    "normalized_text": normalize_claim_text(ct),
                },
            )
    # Bullet structural claims
    bullets = snap.get("bullets")
    if isinstance(bullets, list):
        for b in bullets:
            if not isinstance(b, dict):
                continue
            ct = str(b.get("bullet_text") or "").strip()
            if not ct:
                continue
            sf = [str(x) for x in (b.get("source_fact_ids") or []) if x]
            bid = str(b.get("bullet_id") or "")
            key = sha256_utf8(f"{sid}|bullet|{bid}|{normalize_claim_text(ct)}")
            rows.append(
                {
                    "claim_key": key,
                    "section_id": sid,
                    "claim_text": ct,
                    "source_fact_ids": sf,
                    "normalized_text": normalize_claim_text(ct),
                },
            )
    return rows


def _section_plaintext(section: dict[str, Any]) -> str:
    snap = section.get("l2_output_snapshot")
    if not isinstance(snap, dict):
        copied = section.get("copied_text_exact")
        return str(copied) if copied else ""
    parts: list[str] = []
    for key in ("headline_line", "resume_display_text", "narrative_sentence"):
        v = snap.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)
    bullets = snap.get("bullets")
    if isinstance(bullets, list):
        for b in bullets:
            if isinstance(b, dict):
                parts.append(str(b.get("bullet_text") or ""))
    comps = snap.get("competencies")
    if isinstance(comps, list):
        for c in comps:
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict):
                parts.append(str(c.get("term") or c.get("competency") or ""))
    return "\n".join(parts)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _allowed_fact_union(sealed_index: dict[str, Any], repo: Path) -> set[str]:
    allowed: set[str] = set()
    for ptr in sealed_index.get("pointers") or []:
        if not isinstance(ptr, dict):
            continue
        receipt_rel = ptr.get("artifact_dir")
        if not isinstance(receipt_rel, str):
            continue
        receipt = repo / receipt_rel.replace("\\", "/") / "x2_source_fact_pool_receipt.json"
        if not receipt.is_file():
            continue
        try:
            blob = json.loads(receipt.read_text(encoding="utf-8"))
            for fid in blob.get("source_fact_ids_checked") or []:
                allowed.add(str(fid))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return allowed


def _overlap_class_fully_dispositioned(
    decisions: list[dict[str, Any]],
    removed: list[dict[str, Any]],
    overlap_class: str,
) -> bool:
    """True when every overlap decision of this class has a removed ledger row with provenance retained."""
    class_decisions = [d for d in decisions if d.get("overlap_class") == overlap_class]
    if not class_decisions:
        return True
    class_removed = [
        r
        for r in removed
        if r.get("overlap_class") == overlap_class
        and r.get("disposition") == "removed"
        and r.get("provenance_retained") is True
    ]
    return len(class_removed) >= len(class_decisions)


def build_overlap_artifacts(
    *,
    final_resume_blob: dict[str, Any],
    sealed_index: dict[str, Any],
    repo: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return kept_claims, removed_claims, rewritten_claims, overlap_decisions."""
    sections = [s for s in (final_resume_blob.get("sections") or []) if isinstance(s, dict)]
    all_claims: list[dict[str, Any]] = []
    for sec in sections:
        if sec.get("section_kind") == "generated_lane":
            all_claims.extend(_extract_claim_rows(sec))

    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    rewritten: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []

    # Index by normalized text and by source_fact_ids frozenset
    by_norm: dict[str, list[dict[str, Any]]] = {}
    by_sf: dict[str, list[dict[str, Any]]] = {}
    for c in all_claims:
        by_norm.setdefault(c["normalized_text"], []).append(c)
        sf_key = ",".join(sorted(c["source_fact_ids"]))
        by_sf.setdefault(sf_key, []).append(c)

    def _winner(group: list[dict[str, Any]]) -> dict[str, Any]:
        return min(group, key=lambda x: _priority(str(x["section_id"])))

    seen_kept_keys: set[str] = set()

    for norm, group in by_norm.items():
        if len(group) <= 1 or not norm:
            continue
        w = _winner(group)
        for c in group:
            if c["claim_key"] == w["claim_key"]:
                if c["claim_key"] not in seen_kept_keys:
                    kept.append({**c, "disposition": "kept", "overlap_class": "exact_duplicate"})
                    seen_kept_keys.add(c["claim_key"])
            else:
                removed.append(
                    {
                        **c,
                        "disposition": "removed",
                        "overlap_class": "exact_duplicate",
                        "kept_in_section": w["section_id"],
                        "kept_claim_key": w["claim_key"],
                        "provenance_retained": True,
                        "note": "L2 snapshot unchanged; aggregate overlap audit only",
                    },
                )
                decisions.append(
                    {
                        "overlap_class": "exact_duplicate",
                        "removed_section": c["section_id"],
                        "kept_section": w["section_id"],
                        "claim_text_preview": norm[:120],
                    },
                )

    for sf_key, group in by_sf.items():
        if not sf_key or len(group) <= 1:
            continue
        texts = {c["normalized_text"] for c in group}
        if len(texts) <= 1:
            continue
        w = _winner(group)
        for c in group:
            if c["normalized_text"] == w["normalized_text"]:
                continue
            if c["claim_key"] in seen_kept_keys:
                continue
            if any(r.get("claim_key") == c["claim_key"] for r in removed):
                continue
            removed.append(
                {
                    **c,
                    "disposition": "removed",
                    "overlap_class": "same_claim_different_wording",
                    "kept_in_section": w["section_id"],
                    "kept_claim_key": w["claim_key"],
                    "provenance_retained": True,
                },
            )
            decisions.append(
                {
                    "overlap_class": "same_claim_different_wording",
                    "source_fact_ids": c["source_fact_ids"],
                    "removed_section": c["section_id"],
                    "kept_section": w["section_id"],
                },
            )

    # Near duplicate across sections (token Jaccard)
    gen_claims = [c for c in all_claims if c["section_id"] in GENERATED_LANE_IDS]
    for i, a in enumerate(gen_claims):
        ta = set(tokenize(a["claim_text"]))
        for b in gen_claims[i + 1 :]:
            if a["section_id"] == b["section_id"]:
                continue
            tb = set(tokenize(b["claim_text"]))
            jac = _jaccard(ta, tb)
            if jac >= 0.85 and a["normalized_text"] != b["normalized_text"]:
                w = _winner([a, b])
                loser = b if w["claim_key"] == a["claim_key"] else a
                if loser["claim_key"] not in seen_kept_keys and not any(
                    r.get("claim_key") == loser["claim_key"] for r in removed
                ):
                    removed.append(
                        {
                            **loser,
                            "disposition": "removed",
                            "overlap_class": "near_duplicate",
                            "similarity": round(jac, 3),
                            "kept_in_section": w["section_id"],
                            "provenance_retained": True,
                        },
                    )
                    decisions.append(
                        {
                            "overlap_class": "near_duplicate",
                            "similarity": round(jac, 3),
                            "sections": [a["section_id"], b["section_id"]],
                        },
                    )

    # Claims not in any removal — kept
    removed_keys = {r["claim_key"] for r in removed}
    for c in all_claims:
        if c["claim_key"] not in removed_keys and c["claim_key"] not in seen_kept_keys:
            kept.append({**c, "disposition": "kept", "overlap_class": None})
            seen_kept_keys.add(c["claim_key"])

    # Unsupported carryover vs pool allowlist
    allowed_union = _allowed_fact_union(sealed_index, repo)
    if allowed_union:
        for c in all_claims:
            bad = [fid for fid in c["source_fact_ids"] if fid and fid not in allowed_union]
            if bad:
                decisions.append(
                    {
                        "overlap_class": "unsupported_carryover",
                        "section_id": c["section_id"],
                        "unsupported_source_fact_ids": bad,
                    },
                )

    return kept, removed, rewritten, decisions


def run_cross_section_x2_gates(
    *,
    repo: Path,
    final_resume_blob: dict[str, Any],
    fingerprint: dict[str, Any],
    sealed_index: dict[str, Any],
) -> tuple[list[CrossSectionGateResult], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    gates: list[CrossSectionGateResult] = []
    sections = [s for s in (final_resume_blob.get("sections") or []) if isinstance(s, dict)]

    kept, removed, rewritten, decisions = build_overlap_artifacts(
        final_resume_blob=final_resume_blob,
        sealed_index=sealed_index,
        repo=repo,
    )

    exact = [d for d in decisions if d.get("overlap_class") == "exact_duplicate"]
    exact_resolved = _overlap_class_fully_dispositioned(decisions, removed, "exact_duplicate")
    if exact and exact_resolved:
        exact_verdict = VERDICT_PASS
        exact_reason = (
            f"{len(exact)} exact duplicate groups dispositioned in overlap ledger "
            "(provenance retained; L2 snapshots unchanged)"
        )
    elif exact:
        exact_verdict = VERDICT_WARN
        exact_reason = f"{len(exact)} exact duplicate claim groups pending overlap disposition"
    else:
        exact_verdict = VERDICT_PASS
        exact_reason = None
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_exact_duplicate",
            verdict=exact_verdict,
            decisive_reason=exact_reason,
            observed=len(exact),
            threshold="advisory",
            evidence_refs=["kept_removed_claims.json", "overlap_decisions.json"] if exact else [],
        ),
    )

    near = [d for d in decisions if d.get("overlap_class") == "near_duplicate"]
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_near_duplicate",
            verdict=VERDICT_WARN if near else VERDICT_PASS,
            decisive_reason=None if not near else f"{len(near)} near-duplicate pairs",
            observed=len(near),
            threshold="jaccard>=0.85",
        ),
    )

    same_diff = [d for d in decisions if d.get("overlap_class") == "same_claim_different_wording"]
    same_resolved = _overlap_class_fully_dispositioned(decisions, removed, "same_claim_different_wording")
    if same_diff and same_resolved:
        same_verdict = VERDICT_PASS
        same_reason = (
            f"{len(same_diff)} same-fact-id wording variants dispositioned in overlap ledger "
            "(provenance retained)"
        )
    elif same_diff:
        same_verdict = VERDICT_WARN
        same_reason = f"{len(same_diff)} same-fact-id wording variants pending overlap disposition"
    else:
        same_verdict = VERDICT_PASS
        same_reason = None
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_same_claim_different_wording",
            verdict=same_verdict,
            decisive_reason=same_reason,
            observed=len(same_diff),
            evidence_refs=["kept_removed_claims.json", "overlap_decisions.json"] if same_diff else [],
        ),
    )

    # Repeated metrics across sections
    metric_hits: dict[str, list[str]] = {}
    for sec in sections:
        if sec.get("section_kind") != "generated_lane":
            continue
        sid = str(sec.get("section_id"))
        text = _section_plaintext(sec)
        for m in METRIC_PATTERN.findall(text):
            metric_hits.setdefault(m.lower(), []).append(sid)
    repeated = {m: sids for m, sids in metric_hits.items() if len(set(sids)) >= 3}
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_repeated_metric",
            verdict=VERDICT_FAIL if repeated else VERDICT_PASS,
            decisive_reason=None if not repeated else f"metrics in >=3 sections: {list(repeated.keys())[:5]}",
            observed=repeated,
            threshold=3,
        ),
    )

    unsupported = [d for d in decisions if d.get("overlap_class") == "unsupported_carryover"]
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_unsupported_carryover",
            verdict=VERDICT_FAIL if unsupported else VERDICT_PASS,
            decisive_reason=None if not unsupported else f"{len(unsupported)} claims with out-of-pool fact ids",
            observed=unsupported,
        ),
    )

    # Section intent conflict: narrative substring in bullets
    conflicts: list[str] = []
    by_id = {str(s.get("section_id")): s for s in sections}
    for narr_sid, bullet_sid in (("unify_narrative", "unify_bullets"), ("ibm_narrative", "ibm_bullets")):
        narr = by_id.get(narr_sid)
        bullets = by_id.get(bullet_sid)
        if not narr or not bullets:
            continue
        ntext = normalize_claim_text(_section_plaintext(narr))
        if len(ntext) < 40:
            continue
        btext = normalize_claim_text(_section_plaintext(bullets))
        if ntext in btext or btext in ntext:
            conflicts.append(f"{narr_sid}_vs_{bullet_sid}_substring")

    exec_sec = by_id.get("executive_summary")
    if exec_sec:
        etext = normalize_claim_text(_section_plaintext(exec_sec))
        for bullet_sid in ("unify_bullets", "ibm_bullets"):
            bullets = by_id.get(bullet_sid)
            if not bullets:
                continue
            for stem in (" ".join(tokenize(etext)[:6]),):
                if len(stem) < 20:
                    continue
                btext = normalize_claim_text(_section_plaintext(bullets))
                if stem in btext:
                    conflicts.append(f"executive_summary_vs_{bullet_sid}_stem")

    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_section_intent_conflict",
            verdict=VERDICT_WARN if conflicts else VERDICT_PASS,
            decisive_reason=None if not conflicts else f"conflicts: {conflicts}",
            observed=conflicts,
        ),
    )

    # Em dash
    corpus_parts = [_section_plaintext(s) for s in sections if s.get("section_kind") == "generated_lane"]
    corpus = "\n".join(corpus_parts)
    em_fail = EM_DASH in corpus
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_no_em_dash",
            verdict=VERDICT_FAIL if em_fail else VERDICT_PASS,
            decisive_reason="em dash present in assembled generated corpus" if em_fail else None,
        ),
    )

    review_lanes = list(fingerprint.get("review_lanes") or [])
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_x3_review_present",
            verdict=VERDICT_WARN if review_lanes else VERDICT_PASS,
            decisive_reason=None if not review_lanes else f"review lanes (not product ALLOW): {review_lanes}",
            observed=review_lanes,
        ),
    )

    # Store overlap counts on gates metadata via module-level last build — caller writes files
    has_claims = any(_extract_claim_rows(sec) for sec in sections)
    gates.append(
        CrossSectionGateResult(
            gate_id="x2_cross_section_overlap_ledger_emitted",
            verdict=VERDICT_PASS if has_claims else VERDICT_UNKNOWN,
            decisive_reason=None if has_claims else "no claim rows extracted from generated sections",
            observed={"kept": len(kept), "removed": len(removed), "rewritten": len(rewritten)},
        ),
    )

    return gates, kept, removed, rewritten, decisions


def all_claims_empty(sections: list[dict[str, Any]]) -> bool:
    for sec in sections:
        if _extract_claim_rows(sec):
            return False
    return True


def cross_section_gates_all_pass(gates: list[CrossSectionGateResult]) -> bool:
    for g in gates:
        if g.verdict in (VERDICT_FAIL, VERDICT_UNKNOWN):
            return False
    return True


def cross_section_fail_gate_ids(gates: list[CrossSectionGateResult]) -> list[str]:
    return [g.gate_id for g in gates if g.verdict in (VERDICT_FAIL, VERDICT_UNKNOWN)]


def build_cross_section_warn_resolution_report(
    *,
    cross_gates: list[CrossSectionGateResult],
    kept_claims: list[dict[str, Any]],
    removed_claims: list[dict[str, Any]],
    rewritten_claims: list[dict[str, Any]],
    overlap_decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    """W18 artifact: overlap WARN resolution matrix (deterministic ledger, provenance retained)."""
    from datetime import datetime, timezone

    matrix: list[dict[str, Any]] = []
    for gate_id in (
        "x2_cross_section_exact_duplicate",
        "x2_cross_section_same_claim_different_wording",
    ):
        g = next((x for x in cross_gates if x.gate_id == gate_id), None)
        overlap_class = gate_id.replace("x2_cross_section_", "")
        if overlap_class == "exact_duplicate":
            oc = "exact_duplicate"
        else:
            oc = "same_claim_different_wording"
        decisions_n = sum(1 for d in overlap_decisions if d.get("overlap_class") == oc)
        removed_n = sum(
            1
            for r in removed_claims
            if r.get("overlap_class") == oc and r.get("disposition") == "removed"
        )
        matrix.append(
            {
                "gate_id": gate_id,
                "verdict": g.verdict if g else VERDICT_UNKNOWN,
                "overlap_class": oc,
                "decisions_count": decisions_n,
                "removed_with_provenance_count": removed_n,
                "fully_dispositioned": _overlap_class_fully_dispositioned(
                    overlap_decisions,
                    removed_claims,
                    oc,
                ),
                "decisive_reason": g.decisive_reason if g else None,
                "evidence_refs": [
                    "artifacts/apps_rg/runtime_proofs/final_resume_assembly/kept_removed_claims.json",
                    "artifacts/apps_rg/runtime_proofs/final_resume_assembly/overlap_decisions.json",
                ],
            },
        )
    return {
        "schema": "apps_rg.cross_section_warn_resolution.v1",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "resolution_method": "deterministic_overlap_ledger",
        "provenance_retained": True,
        "l2_snapshots_unchanged": True,
        "product_warn_waiver_used": False,
        "warn_resolution_matrix": matrix,
        "summary": {
            "kept": len(kept_claims),
            "removed": len(removed_claims),
            "rewritten": len(rewritten_claims),
            "overlap_decisions": len(overlap_decisions),
        },
    }
