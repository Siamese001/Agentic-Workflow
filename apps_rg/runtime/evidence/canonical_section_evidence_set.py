"""Canonical section evidence set — pool is authority; FEC materializes (narrow-only)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import SectionFecBridge

PROOF_CLASS_INCOMPLETE = "INCOMPLETE_PROOF"
X2_BLOCK_ID_NAMESPACE_SPLIT = "X2_BLOCK_ID_NAMESPACE_SPLIT"

_BULLET_SURFACE_PREFIXES = ("bul_unify_", "bul_ibm_")
_LEDGER_PREFIX = "fact_"


def canonical_evidence_set_digest(ids: Iterable[str]) -> str:
    """Stable SHA-256 digest for an ordered canonical allowlist."""
    ordered = sorted({str(x).strip() for x in ids if str(x).strip()})
    payload = json.dumps(ordered, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_id_alias_map_from_plan(plan: dict[str, Any] | None) -> dict[str, str]:
    """Map surface proof ids (``bul_*``) to ledger ``fact_*`` ids when explicitly stamped."""
    out: dict[str, str] = {}
    if not isinstance(plan, dict):
        return out
    for row in plan.get("facts") or []:
        if not isinstance(row, dict):
            continue
        surface = str(row.get("fact_id") or "").strip()
        ledger = str(row.get("ledger_candidate_fact_id") or row.get("candidate_fact_id") or "").strip()
        if surface and ledger and surface != ledger:
            out[surface] = ledger
    return out


def detect_id_namespace_split_without_alias(
    *,
    pool_ids: set[str],
    fec_ids: set[str],
    alias_map: dict[str, str] | None = None,
) -> tuple[bool, list[str]]:
    """True when disjoint ``bul_*`` vs ``fact_*`` surfaces lack an explicit alias map entry."""
    amap = alias_map or {}
    if not pool_ids and not fec_ids:
        return False, []
    pool_bul = {x for x in pool_ids if x.startswith(_BULLET_SURFACE_PREFIXES)}
    pool_fact = {x for x in pool_ids if x.startswith(_LEDGER_PREFIX)}
    fec_bul = {x for x in fec_ids if x.startswith(_BULLET_SURFACE_PREFIXES)}
    fec_fact = {x for x in fec_ids if x.startswith(_LEDGER_PREFIX)}
    if not pool_bul or not fec_fact:
        if not fec_bul or not pool_fact:
            return False, []
    if pool_bul and fec_fact:
        for b in pool_bul:
            if b in fec_ids:
                continue
            if amap.get(b) in fec_ids:
                continue
            if not amap:
                return True, sorted(pool_bul | fec_fact)
    if fec_bul and pool_fact:
        for b in fec_bul:
            if b in pool_ids:
                continue
            rev = {v: k for k, v in amap.items()}
            if rev.get(b) in pool_ids:
                continue
            if not amap:
                return True, sorted(fec_bul | pool_fact)
    return False, []


@dataclass(frozen=True, slots=True)
class CanonicalSectionEvidenceSet:
    """Resolver pool is canonical authority; FEC is its materialized contract form."""

    section_id: str
    pool_ids_ordered: tuple[str, ...]
    pool_ids: frozenset[str]
    pool_digest: str
    alias_map: dict[str, str] = field(default_factory=dict)

    @property
    def membership_ids(self) -> frozenset[str]:
        """IDs valid for downstream membership (pool + explicit alias keys)."""
        extra = set(self.alias_map.keys())
        return frozenset(set(self.pool_ids) | extra)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "canonical_section_evidence_set_v1",
            "section_id": self.section_id,
            "canonical_evidence_set_digest": self.pool_digest,
            "pool_ids_ordered": list(self.pool_ids_ordered),
            "pool_id_count": len(self.pool_ids),
            "id_alias_map": dict(self.alias_map),
        }


def build_canonical_section_evidence_set(pool: SectionProofPool) -> CanonicalSectionEvidenceSet:
    ordered = tuple(str(x) for x in (pool.allowed_fact_ids_ordered or []) if str(x).strip())
    if not ordered:
        ordered = tuple(sorted(pool.allowed_fact_ids))
    alias = build_id_alias_map_from_plan(pool.selected_fact_plan)
    digest = canonical_evidence_set_digest(ordered)
    return CanonicalSectionEvidenceSet(
        section_id=str(pool.section or ""),
        pool_ids_ordered=ordered,
        pool_ids=frozenset(ordered),
        pool_digest=digest,
        alias_map=alias,
    )


def materialize_fec_allowed_from_c04(
    *,
    c04_allowed: list[str],
    canonical: CanonicalSectionEvidenceSet,
) -> tuple[list[str], dict[str, Any]]:
    """Intersect C04 allowlist with canonical pool (never widen). Preserve pool order."""
    c04_set = {str(x).strip() for x in c04_allowed if str(x).strip()}
    pool_set = set(canonical.pool_ids)
    widening_blocked = sorted(c04_set - pool_set)
    fec_allowed = [fid for fid in canonical.pool_ids_ordered if fid in c04_set]
    narrowing_dropped = sorted(pool_set - set(fec_allowed))
    fec_digest = canonical_evidence_set_digest(fec_allowed)
    narrowed = bool(narrowing_dropped)
    receipt: dict[str, Any] = {
        "schema_version": "fec_materialization_receipt_v1",
        "section_id": canonical.section_id,
        "canonical_evidence_set_digest": canonical.pool_digest,
        "fec_allowed_fact_ids_digest": fec_digest,
        "fec_narrowed_from_pool": narrowed,
        "narrowing_dropped_pool_ids": narrowing_dropped,
        "widening_blocked_ids": widening_blocked,
        "fec_allowed_count": len(fec_allowed),
        "pool_allowed_count": len(pool_set),
    }
    if narrowed:
        receipt["explicit_narrowing"] = True
    return fec_allowed, receipt


def apply_canonical_section_evidence_materialization(
    *,
    pool: SectionProofPool,
    runtime_payload: dict[str, Any],
    bridge: SectionFecBridge | None,
    fec_allowed: list[str] | None = None,
    fec_materialization_receipt: dict[str, Any] | None = None,
) -> CanonicalSectionEvidenceSet:
    """Sync runtime_payload + FEC bridge to materialized canonical/FEC allowlist."""
    canonical = build_canonical_section_evidence_set(pool)
    if fec_allowed is None:
        fec_allowed = list(canonical.pool_ids_ordered)
    fec_digest = canonical_evidence_set_digest(fec_allowed)
    widening = sorted(set(fec_allowed) - set(canonical.pool_ids))
    if widening:
        raise ValueError(
            f"FEC allowlist widens canonical pool for {canonical.section_id!r}: {widening[:8]}"
        )

    runtime_payload["canonical_section_evidence_set"] = canonical.as_dict()
    runtime_payload["canonical_evidence_set_digest"] = canonical.pool_digest
    runtime_payload["fec_allowed_fact_ids_digest"] = fec_digest
    runtime_payload["allowed_fact_ids"] = list(fec_allowed)
    if fec_materialization_receipt is not None:
        runtime_payload["fec_materialization_receipt"] = fec_materialization_receipt

    meta = dict(runtime_payload.get("proof_pool_metadata") or pool.proof_pool_metadata or {})
    meta["canonical_evidence_set_digest"] = canonical.pool_digest
    meta["fec_allowed_fact_ids_digest"] = fec_digest
    meta["proof_pool_digest"] = canonical.pool_digest
    runtime_payload["proof_pool_metadata"] = meta

    plan = dict(pool.selected_fact_plan or {})
    plan["required_fact_ids"] = [x for x in fec_allowed if x in canonical.pool_ids]
    runtime_payload["selected_fact_plan"] = plan

    if bridge is not None and isinstance(bridge.bridge_doc, dict):
        doc = bridge.bridge_doc
        doc["allowed_fact_ids"] = list(fec_allowed)
        doc["source_fact_ids"] = list(fec_allowed)
        doc["canonical_evidence_set_digest"] = canonical.pool_digest
        doc["fec_allowed_fact_ids_digest"] = fec_digest
        doc["proof_pool_digest"] = canonical.pool_digest
        doc["id_alias_map"] = dict(canonical.alias_map)
        # R1 (plan apps-rg-fec-grounding-blocker-d9a4b7): align evidence_items to the canonical FEC
        # allow-set too. allowed_fact_ids/source_fact_ids are synced above, but a stray evidence item
        # whose source_fact_id was NOT promoted into fec_allowed (a sibling the canonical narrowing
        # dropped — e.g. fact_quant_hpc_002 vs the selected _003) still leaks into
        # collect_prompt_c0_fact_ids and trips x2_prompt_c0_ids_subset_of_fec. Drop those items
        # (alias-aware, mirroring validate_downstream_subset) so the bridge's prompt surface is a
        # strict subset of the FEC. Items without a source_fact_id are non-claim context — kept.
        _fec_set = set(fec_allowed)
        _amap = dict(canonical.alias_map)

        def _fec_admits(source_fact_id: Any) -> bool:
            s = str(source_fact_id or "").strip()
            if not s:
                return True
            base = s.split("_metric_", 1)[0]
            if s in _fec_set or base in _fec_set:
                return True
            ledger = _amap.get(base) or _amap.get(s)
            return bool(ledger and (ledger in _fec_set or ledger.split("_metric_", 1)[0] in _fec_set))

        _items = doc.get("evidence_items")
        if isinstance(_items, list):
            doc["evidence_items"] = [
                it
                for it in _items
                if not isinstance(it, dict) or _fec_admits(it.get("source_fact_id"))
            ]
        if fec_materialization_receipt is not None:
            doc["fec_materialization_receipt"] = fec_materialization_receipt
        snap = doc.get("final_evidence_contract")
        if isinstance(snap, dict):
            snap["allowed_fact_ids"] = list(fec_allowed)
            snap["canonical_evidence_set_digest"] = canonical.pool_digest
    return canonical


def classify_lane_proof_bundle_completeness(run_dir: Path) -> str:
    """Classify proof bundle completeness without treating missing artifacts as PASS/FAIL."""
    required = (
        "runtime_payload.json",
        "selected_fact_plan.json",
        "x2_gate_outputs.json",
    )
    missing = [name for name in required if not (run_dir / name).is_file()]
    if missing:
        return PROOF_CLASS_INCOMPLETE
    return "COMPLETE"


def collect_prompt_c0_fact_ids(runtime_payload: dict[str, Any]) -> set[str]:
    """Extract fact ids referenced by compiled prompt / FEC consumption surfaces."""
    ids: set[str] = set()
    bridge = runtime_payload.get("section_fec_bridge")
    if isinstance(bridge, dict):
        for it in bridge.get("evidence_items") or []:
            if isinstance(it, dict):
                sid = str(it.get("source_fact_id") or "").strip()
                if sid:
                    ids.add(sid)
        for fid in bridge.get("allowed_fact_ids") or []:
            if str(fid).strip():
                ids.add(str(fid).strip())
    for fid in runtime_payload.get("allowed_fact_ids") or []:
        if str(fid).strip():
            ids.add(str(fid).strip())
    return ids


def collect_claim_ledger_source_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for raw in row.get("source_fact_ids") or []:
            s = str(raw).strip()
            if s:
                out.add(s)
    return out


def validate_downstream_subset(
    child_ids: Iterable[str],
    fec_ids: set[str],
    *,
    label: str,
    alias_map: dict[str, str] | None = None,
) -> tuple[bool, list[str]]:
    """Return (ok, violations) for child ⊆ FEC (alias-aware)."""
    amap = alias_map or {}
    violations: list[str] = []
    for raw in child_ids:
        s = str(raw).strip()
        if not s:
            continue
        base = s.split("_metric_", 1)[0]
        if s in fec_ids or base in fec_ids:
            continue
        ledger = amap.get(base) or amap.get(s)
        if ledger and (ledger in fec_ids or ledger.split("_metric_", 1)[0] in fec_ids):
            continue
        violations.append(s)
    ok = not violations
    return ok, violations


__all__ = [
    "CanonicalSectionEvidenceSet",
    "PROOF_CLASS_INCOMPLETE",
    "X2_BLOCK_ID_NAMESPACE_SPLIT",
    "apply_canonical_section_evidence_materialization",
    "build_canonical_section_evidence_set",
    "build_id_alias_map_from_plan",
    "canonical_evidence_set_digest",
    "classify_lane_proof_bundle_completeness",
    "collect_claim_ledger_source_fact_ids",
    "collect_prompt_c0_fact_ids",
    "detect_id_namespace_split_without_alias",
    "materialize_fec_allowed_from_c04",
    "validate_downstream_subset",
]
