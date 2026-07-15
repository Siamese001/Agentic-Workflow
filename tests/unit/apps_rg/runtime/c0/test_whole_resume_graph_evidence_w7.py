from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest
from apps_rg.runtime.c0.resume_graph_allocation import (
    ALL_CLAIM_BEARING_SECTIONS,
    finalize_resume_graph_allocation_plan,
)
from apps_rg.runtime.c0.whole_resume_graph_evidence import (
    build_whole_resume_graph_evidence_contract,
)


def _write(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return path.name


def _fixture(repo: Path) -> tuple[dict, dict]:
    assignments = []
    for index, section_id in enumerate(ALL_CLAIM_BEARING_SECTIONS):
        assignments.append(
            {
                "section_id": section_id,
                "claim_unit_id": f"{section_id}:claim-1",
                "candidate_id": f"candidate-{index}",
                "skill_id": f"skill-{index}",
                "metric_outcome_id": f"metric-{index}",
                "normalized_metric_signature": f"signature-{index}",
                "counts_toward_global_uniqueness": True,
            }
        )
    plan = finalize_resume_graph_allocation_plan(
        {
            "schema_version": "resume_graph_allocation_plan_v1",
            "allocation_scope": "WHOLE_RESUME",
            "global_uniqueness_claimed": True,
            "assignments": assignments,
            "candidate_decisions": [],
            "candidate_conservation_receipt": {"pass": True},
            "durable_graph_state_mutated": False,
        }
    )
    digest = plan["allocation_plan_digest"]
    ledger = {
        "allocation_plan_digest": digest,
        "current_run_only": True,
        "durable_graph_state_mutated": False,
    }
    contracts = {}
    sections = []
    for section_id in ALL_CLAIM_BEARING_SECTIONS:
        contract = {
            "section_id": section_id,
            "allocation_plan_digest": digest,
            "traversal_conservation_pass": True,
            "pass": True,
        }
        contract["contract_digest"] = stable_digest(contract)
        contracts[section_id] = contract
        text = f"Visible claim for {section_id}."
        claim_hash = stable_digest({"text": text})
        sections.append(
            {
                "section_id": section_id,
                "section_kind": "generated_lane",
                "section_digest": stable_digest({"section_id": section_id}),
                "l2_output_snapshot": {
                    "resume_graph_allocation_plan_digest": digest,
                    "claim_ledger": [{"claim_text": text}],
                    "graph_claim_bindings": [
                        {
                            "visible_claim_hash": claim_hash,
                            "allocation_plan_digest": digest,
                        }
                    ],
                    "resume_graph_claim_binding_pass": True,
                },
            }
        )
    _write(repo / "allocation.json", plan)
    _write(repo / "ledger.json", ledger)
    _write(repo / "contracts.json", contracts)
    rollup = {
        "resume_graph_allocation_plan_digest": digest,
        "resume_graph_allocation_refs": {
            "allocation_plan": "allocation.json",
            "usage_ledger": "ledger.json",
            "section_final_evidence_contracts": "contracts.json",
        },
    }
    return {"sections": sections}, rollup


def test_engineering_contract_passes_but_unknown_human_release_blocks(tmp_path: Path) -> None:
    final_resume, rollup = _fixture(tmp_path)
    result = build_whole_resume_graph_evidence_contract(
        repo=tmp_path,
        final_resume_blob=final_resume,
        rollup_blob=rollup,
    )
    assert result["engineering_pass"] is True
    assert result["official_w6_status"] == "UNKNOWN"
    assert result["release_pass"] is False
    assert result["promotion_eligible"] is False
    assert result["unknown_is_pass"] is False


def test_unbound_materialized_claim_fails_engineering(tmp_path: Path) -> None:
    final_resume, rollup = _fixture(tmp_path)
    final_resume["sections"][0]["l2_output_snapshot"]["claim_ledger"][0][
        "claim_text"
    ] = "A claim that was added after binding."
    result = build_whole_resume_graph_evidence_contract(
        repo=tmp_path,
        final_resume_blob=final_resume,
        rollup_blob=rollup,
    )
    assert result["engineering_pass"] is False
    assert any("unbound_visible_claim" in code for code in result["failure_codes"])


def test_section_traversal_nonpass_fails_closed(tmp_path: Path) -> None:
    final_resume, rollup = _fixture(tmp_path)
    contracts = json.loads((tmp_path / "contracts.json").read_text(encoding="utf-8"))
    section_id = next(iter(contracts))
    contract = contracts[section_id]
    contract["traversal_conservation_pass"] = False
    contract["contract_digest"] = stable_digest(
        {key: value for key, value in contract.items() if key != "contract_digest"}
    )
    _write(tmp_path / "contracts.json", contracts)
    result = build_whole_resume_graph_evidence_contract(
        repo=tmp_path,
        final_resume_blob=final_resume,
        rollup_blob=rollup,
    )
    assert result["engineering_pass"] is False
    assert any("traversal_conservation_nonpass" in code for code in result["failure_codes"])


def test_allocation_ref_cannot_escape_repo(tmp_path: Path) -> None:
    final_resume, rollup = _fixture(tmp_path)
    rollup["resume_graph_allocation_refs"]["allocation_plan"] = "../allocation.json"
    result = build_whole_resume_graph_evidence_contract(
        repo=tmp_path,
        final_resume_blob=final_resume,
        rollup_blob=rollup,
    )
    assert result["engineering_pass"] is False
    assert "allocation_plan_missing_or_invalid" in result["failure_codes"]
