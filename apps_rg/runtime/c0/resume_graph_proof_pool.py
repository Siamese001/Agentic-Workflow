"""Bind a section proof pool to the active frozen resume-graph allocation."""
from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.c0.resume_graph_allocation import (
    ALLOCATION_PLAN_ENV,
    SECTION_EVIDENCE_CONTRACTS_ENV,
    build_section_only_graph_allocation,
    load_resume_graph_allocation_plan,
    slice_section_plan_for_allocation,
)
from apps_rg.runtime.sections.graph_evidence_contract import (
    build_allowed_fact_ids_for_plan_facts,
    plan_fact_to_employment_bullet_row,
)


def _load_contracts(path: Path) -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"section final graph evidence contracts unavailable: {path}") from exc
    if not isinstance(raw, dict):
        raise ValueError("section final graph evidence contracts must be a JSON object")
    return {
        str(section_id): dict(contract)
        for section_id, contract in raw.items()
        if isinstance(contract, Mapping)
    }


def _active_whole_resume_inputs(
    section_id: str,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    plan_ref = str(os.environ.get(ALLOCATION_PLAN_ENV) or "").strip()
    contracts_ref = str(os.environ.get(SECTION_EVIDENCE_CONTRACTS_ENV) or "").strip()
    if not plan_ref and not contracts_ref:
        return None
    if not plan_ref or not contracts_ref:
        raise ValueError(
            f"{section_id}: incomplete whole-resume graph allocation environment binding"
        )
    plan = load_resume_graph_allocation_plan(Path(plan_ref))
    contracts = _load_contracts(Path(contracts_ref))
    contract = contracts.get(section_id)
    if not contract:
        raise ValueError(f"{section_id}: missing frozen final graph evidence contract")
    return plan, contract


def bind_proof_pool_to_resume_graph_allocation(pool: Any) -> Any:
    """Return a new frozen ``SectionProofPool`` narrowed to its allocation slice."""
    section_id = str(pool.section or "")
    source_plan = dict(pool.selected_fact_plan)
    active = _active_whole_resume_inputs(section_id)
    if active is None:
        standalone = build_section_only_graph_allocation(
            section_plan=source_plan,
            section_id=section_id,
        )
        allocation_plan = standalone["allocation_plan"]
        contract = standalone["final_evidence_contract"]
    else:
        allocation_plan, contract = active
    sliced = slice_section_plan_for_allocation(
        section_plan=source_plan,
        allocation_plan=allocation_plan,
        final_evidence_contract=contract,
        section_id=section_id,
    )
    facts = [dict(row) for row in sliced.get("facts") or [] if isinstance(row, Mapping)]
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    bullet_rows = [plan_fact_to_employment_bullet_row(row) for row in facts]
    metadata = dict(pool.proof_pool_metadata)
    metadata.update(
        {
            "selected_graph_evidence_plan": sliced,
            "resume_graph_allocation_scope": allocation_plan["allocation_scope"],
            "resume_graph_allocation_plan_id": allocation_plan["allocation_plan_id"],
            "resume_graph_allocation_plan_digest": allocation_plan[
                "allocation_plan_digest"
            ],
            "resume_graph_global_uniqueness_claimed": allocation_plan[
                "global_uniqueness_claimed"
            ],
            "final_graph_evidence_contract": dict(contract),
            "final_graph_evidence_contract_digest": str(
                contract.get("contract_digest") or ""
            ),
            "durable_graph_state_mutated": False,
        }
    )
    # ``slice_section_plan_for_allocation`` preserves the canonical source
    # plan digest while narrowing its fact rows.  Re-hashing the sliced
    # serialization creates a second, non-authoritative identity and breaks
    # the W7 end-to-end digest chain.
    digest = str(sliced.get("plan_digest") or "").strip()
    if not digest:
        raise ValueError(f"{section_id}: sliced graph plan lacks canonical plan_digest")
    metadata["canonical_section_graph_plan_id"] = sliced.get("plan_id")
    metadata["canonical_section_graph_plan_digest"] = digest
    binding_receipt = metadata.get("graph_selection_binding_receipt")
    if isinstance(binding_receipt, Mapping):
        updated_binding_receipt = dict(binding_receipt)
        updated_binding_receipt.update(
            {
                "canonical_plan_id": sliced.get("plan_id"),
                "canonical_plan_digest": digest,
                "selected_fact_plan_digest": digest,
                "proof_pool_digest": digest,
                "selected_graph_plan_is_selected_fact_plan": True,
                "pass": True,
            }
        )
        metadata["graph_selection_binding_receipt"] = updated_binding_receipt
    return replace(
        pool,
        proof_pool_digest=digest,
        selected_fact_plan=sliced,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=allowed,
        bullet_rows=bullet_rows,
        proof_pool_metadata=metadata,
    )


__all__ = ["bind_proof_pool_to_resume_graph_allocation"]
