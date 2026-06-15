"""X2 deterministic gates for canonical section evidence set invariants (W1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    X2_BLOCK_ID_NAMESPACE_SPLIT,
    build_id_alias_map_from_plan,
    collect_claim_ledger_source_fact_ids,
    collect_prompt_c0_fact_ids,
    detect_id_namespace_split_without_alias,
    validate_downstream_subset,
)
from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult


def append_canonical_evidence_invariant_x2_gates(
    gates: list[X2GateResult],
    *,
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    claim_ledger: list[dict[str, Any]],
    artifacts_dir: Path | None = None,
) -> None:
    """Append cross-lane canonical/FEC invariant gates (mutates ``gates``)."""
    _ = artifacts_dir
    fec_ids = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or allowed_fact_ids)}
    canon_doc = runtime_payload.get("canonical_section_evidence_set") or {}
    pool_digest = str(
        runtime_payload.get("canonical_evidence_set_digest")
        or canon_doc.get("canonical_evidence_set_digest")
        or ""
    )
    fec_digest = str(runtime_payload.get("fec_allowed_fact_ids_digest") or "")
    alias_map = dict(canon_doc.get("id_alias_map") or {})
    if not alias_map:
        plan = runtime_payload.get("selected_fact_plan")
        if isinstance(plan, dict):
            alias_map = build_id_alias_map_from_plan(plan)

    # ibm_narrative: prompt SSOT (ibm_position_narrative_v1.yaml) explicitly authorizes
    # bul_ibm_001..005 as the proof tokens for claim_ledger.source_fact_ids, but the FEC is
    # built from underlying graph ids. Auto-alias the IBM bullet surface to the FEC id it
    # stands for so the namespace-subset gates accept what the prompt requires.
    #
    # Typed-edge migration (W2.3): the FEC is now composed of graph-era role-episode BUNDLE ids
    # (reb_ibm_*), not legacy fact_* ids — so the prior "first fact_* anchor" yielded None and the
    # alias never built, failing x2_claim_ledger_source_fact_ids_subset_of_fec on every bul_ibm_*.
    # Alias each bullet slot to ITS canonical bundle (IBM_BULLET_SLOT_BUNDLE_MAP) when that bundle
    # is in the FEC — a precise per-slot resolution, not a single shared anchor. Keep the legacy
    # fact_* fallback for any FEC still composed of fact_* ids.
    section_id = str(canon_doc.get("section_id") or runtime_payload.get("section_id") or "")
    if section_id == "ibm_narrative":
        from apps_rg.runtime.sections.ibm_role_episode_evidence import (
            IBM_BULLET_SLOT_BUNDLE_MAP,
        )
        from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

        for bid, bundle_id in IBM_BULLET_SLOT_BUNDLE_MAP.items():
            if bundle_id in fec_ids:
                alias_map.setdefault(bid, bundle_id)
        fact_anchor = next(
            (fid for fid in sorted(fec_ids) if fid.startswith("fact_") and "_metric_" not in fid),
            None,
        )
        if fact_anchor:
            for bid in IBM_BULLET_IDS:
                alias_map.setdefault(bid, fact_anchor)

    pool_ids = set(canon_doc.get("pool_ids_ordered") or []) or set(allowed_fact_ids)

    def add(
        gate_id: str,
        passed: bool,
        observed: Any,
        threshold: Any,
        reason: str | None = None,
    ) -> None:
        gates.append(
            X2GateResult(
                gate_id=gate_id,
                gate_type="deterministic",
                pass_=passed,
                observed_value=observed,
                threshold=threshold,
                failure_reason=None if passed else reason,
                evidence_ref=gate_id,
            )
        )

    widening, widen_ids = validate_downstream_subset(
        fec_ids,
        pool_ids,
        label="fec",
        alias_map=alias_map,
    )
    add(
        "x2_fec_subset_of_canonical_evidence_pool",
        widening,
        {"fec_count": len(fec_ids), "violations": widen_ids},
        "fec_ids_subset_of_pool",
        None if widening else f"fec_widens_canonical_pool:{','.join(widen_ids[:12])}",
    )

    prompt_ids = collect_prompt_c0_fact_ids(runtime_payload)
    c0_ok, c0_bad = validate_downstream_subset(
        prompt_ids,
        fec_ids,
        label="prompt_c0",
        alias_map=alias_map,
    )
    add(
        "x2_prompt_c0_ids_subset_of_fec",
        c0_ok,
        {"prompt_c0_count": len(prompt_ids), "violations": c0_bad},
        "prompt_c0_subset_of_fec",
        None if c0_ok else f"prompt_c0_widens_fec:{','.join(c0_bad[:12])}",
    )

    ledger_ids = collect_claim_ledger_source_fact_ids(claim_ledger)
    led_ok, led_bad = validate_downstream_subset(
        ledger_ids,
        fec_ids,
        label="claim_ledger",
        alias_map=alias_map,
    )
    add(
        "x2_claim_ledger_source_fact_ids_subset_of_fec",
        led_ok,
        {"ledger_id_count": len(ledger_ids), "violations": led_bad},
        "claim_ledger_subset_of_fec",
        None if led_ok else f"claim_ledger_widens_fec:{','.join(led_bad[:12])}",
    )

    split, split_ids = detect_id_namespace_split_without_alias(
        pool_ids=pool_ids,
        fec_ids=fec_ids,
        alias_map=alias_map,
    )
    add(
        X2_BLOCK_ID_NAMESPACE_SPLIT,
        not split,
        {"disjoint_without_alias": split_ids, "alias_map_size": len(alias_map)},
        "explicit_alias_map_or_unified_namespace",
        None if not split else f"disjoint_namespace:{','.join(split_ids[:12])}",
    )

    mat = runtime_payload.get("fec_materialization_receipt") or {}
    narrowed = bool(mat.get("fec_narrowed_from_pool"))
    digest_match = bool(pool_digest and fec_digest and pool_digest == fec_digest)
    digest_ok = digest_match or (narrowed and bool(mat.get("explicit_narrowing")))
    add(
        "x2_active_pool_digest_matches_fec_digest",
        digest_ok,
        {
            "canonical_evidence_set_digest": pool_digest,
            "fec_allowed_fact_ids_digest": fec_digest,
            "fec_narrowed_from_pool": narrowed,
        },
        "digest_equal_or_explicit_narrowing_receipt",
        None
        if digest_ok
        else "x2_active_pool_digest_mismatch_without_narrowing_receipt",
    )


__all__ = ["append_canonical_evidence_invariant_x2_gates", "X2_BLOCK_ID_NAMESPACE_SPLIT"]
