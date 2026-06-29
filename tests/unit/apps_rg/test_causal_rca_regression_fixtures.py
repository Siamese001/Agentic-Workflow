"""apps-test-model: APP CONTRACT.

Regression fixtures for the apps_rg BCG/RCA causal controls.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation.preflight import (
    AggregationPreflightError,
    REQUIRED_PROOF_FILES,
    assert_preflight_pass,
    run_aggregation_preflight,
)
from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS
from apps_rg.runtime.sections.role_episode_lane import (
    RoleEpisodeLaneConfig,
    _materialize_bullet_generation,
    _normalize_role_episode_bullet_pool_parsed,
    _parse_json_object,
    run_insurtech_bullets_x2_gates,
)
from apps_rg.runtime.validators.companion_bullet_finalization import (
    ACCEPTED_FINALIZED_COMPANION_STATUS,
    PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
    companion_blocks_narrative_llm,
    evaluate_companion_bullet_lane_finalized,
)
from apps_rg.runtime.validators.competencies_x2 import (
    check_canonical_competency_terms,
    term_supports_resume_or_graph,
)
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates


INSURTECH_BULLET_CFG = RoleEpisodeLaneConfig(
    section_id="insurtech_bullets",
    role_key="insurtech",
    employer_label="InsurTech",
    header_key="insurtech_header",
    bullet_prefix="bul_insurtech",
    output_filename="insurtech_bullets_output.txt",
    output_kind="bullets",
    allow_deterministic_graph_render=True,
)


def _gate_pass(gates: list[dict], gate_id: str) -> bool:
    for gate in gates:
        if gate.get("gate_id") == gate_id:
            return bool(gate.get("pass"))
    raise AssertionError(f"missing gate {gate_id}")


def _x2_gate_pass(gates: list, gate_id: str) -> bool:
    for gate in gates:
        if gate.gate_id == gate_id:
            return bool(gate.pass_)
    raise AssertionError(f"missing gate {gate_id}")


def test_competency_graph_lineage_rejects_ungrounded_terms_and_accepts_graph_backed_terms() -> None:
    allowed_fact_ids = {"fact_graph_skills_001"}
    ungrounded = [
        {
            "category_label": "Graph Delivery",
            "terms": [{"text": "demoable AI accelerators"}],
        }
    ]

    ok, reason = check_canonical_competency_terms(ungrounded, allowed_fact_ids)

    assert ok is False
    assert reason is not None and "missing source_fact_ids or source_skill_ids" in reason

    graph_backed_term = {
        "text": "graph-scoped observability accelerators",
        "source_fact_id": "fact_graph_skills_001",
        "source_fact_ids": ["fact_graph_skills_001"],
        "source_skill_ids": ["skill_graph_observability"],
    }
    graph_backed = [{"category_label": "Graph Delivery", "terms": [graph_backed_term]}]

    ok, reason = check_canonical_competency_terms(graph_backed, allowed_fact_ids)

    assert ok is True, reason
    assert term_supports_resume_or_graph(
        graph_backed_term,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids={"skill_graph_observability"},
        resume_support_blob_lower="",
    )


def test_insurtech_bullet_parser_rejects_malformed_provider_output_and_normalizes_ledger() -> None:
    allowed = ["fact_insurtech_001", "fact_insurtech_002", "fact_insurtech_003"]
    parsed, parse_error = _parse_json_object('[{"bullet_text": "not an object root"}]')

    bullets, receipt = _materialize_bullet_generation(
        cfg=INSURTECH_BULLET_CFG,
        parsed=parsed,
        parse_error=parse_error,
        provider_runtime_generation_status="REAL_LLM",
        facts=[],
        allowed=allowed,
        graph_packet_digest="graph-packet-test",
    )

    assert parse_error == "json_root_not_object"
    assert bullets == []
    assert receipt["generation_method"] == "model_output_invalid"
    assert receipt["llm_output_used"] is False

    compliant, parse_error = _parse_json_object(
        json.dumps(
            {
                "bullets": [
                    {
                        "bullet_text": "Owned actuarial pricing telemetry for regulated insurance modernization.",
                        "source_fact_ids": ["fact_insurtech_001"],
                    },
                    {
                        "bullet_text": "Built underwriting pipeline controls for carrier data remediation.",
                        "source_fact_ids": ["fact_insurtech_002"],
                    },
                    {
                        "bullet_text": "Drove claims analytics observability across operational risk workflows.",
                        "source_fact_ids": ["fact_insurtech_003"],
                    },
                ]
            }
        )
    )
    assert parse_error == ""

    normalized = _normalize_role_episode_bullet_pool_parsed(
        compliant or {},
        cfg=INSURTECH_BULLET_CFG,
        allowed=allowed,
    )
    normalized["role_episode_bundle_consumed"] = True
    gates = run_insurtech_bullets_x2_gates(
        l2=normalized,
        allowed=allowed,
        runtime_generation_status="REAL_LLM",
    )

    assert [b["bullet_id"] for b in normalized["bullets"]] == [
        "bul_insurtech_001",
        "bul_insurtech_002",
        "bul_insurtech_003",
    ]
    assert normalized["claim_ledger"] == [
        {"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]}
        for b in normalized["bullets"]
    ]
    assert _gate_pass(gates, "x2_insurtech_bullets_source_fact_ids_supported") is True
    assert _gate_pass(gates, "x2_insurtech_bullets_bullet_count_3") is True


def test_unify_narrative_specificity_rejects_generic_text_and_accepts_mechanism_bound_text() -> None:
    generic = "Led enterprise mandate across regulated operating models."
    specific = "Led enterprise mandate for agentic orchestration across regulated operating models."

    def run(text: str) -> list:
        return run_unify_narrative_x2_gates(
            narrative_sentence=text,
            parsed_output={
                "narrative_sentence": text,
                "claim_ledger": [{"claim_text": text, "source_fact_ids": ["bul_unify_001"]}],
                "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            },
            claim_ledger=[{"claim_text": text, "source_fact_ids": ["bul_unify_001"]}],
            jd_text="",
            runtime_generation_status="REAL_LLM",
            companion_bullet_texts="- bul_unify_001: Built agentic platform controls.",
            companion_bullets_status=ACCEPTED_FINALIZED_COMPANION_STATUS,
            companion_bullets_reason="ok",
            provider_requested="external_claude",
            provider_attempted="external_claude",
            raw_output="{}",
            x1d_judges=[],
            allowed_fact_ids={"bul_unify_001"},
        )

    assert _x2_gate_pass(run(generic), "x2_narrative_technical_specificity_floor") is False
    assert _x2_gate_pass(run(specific), "x2_narrative_technical_specificity_floor") is True


def test_insurtech_narrative_dependency_blocks_until_upstream_authorization_exists() -> None:
    expected_ids = ("bul_insurtech_001", "bul_insurtech_002", "bul_insurtech_003")
    l2 = {
        "section_id": "insurtech_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": [{"bullet_id": bid, "bullet_text": bid} for bid in expected_ids],
    }

    blocked_status, blocked_reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="insurtech_bullets",
        l2_data=l2,
        x3_code=f"X3_BLOCK_{PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}",
        expected_bullet_ids=expected_ids,
    )

    assert blocked_status == "NOT_FINALIZED"
    assert "x3_not_companion_finalized" in blocked_reason
    assert companion_blocks_narrative_llm({"status": blocked_status}) is True

    allowed_status, allowed_reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="insurtech_bullets",
        l2_data=l2,
        x3_code="X3_ALLOW",
        expected_bullet_ids=expected_ids,
    )

    assert allowed_status == ACCEPTED_FINALIZED_COMPANION_STATUS
    assert allowed_reason == "ok"
    assert companion_blocks_narrative_llm({"status": allowed_status}) is False


def _write_minimal_required_proof_tree(
    repo: Path,
    *,
    x3_overrides: dict[str, str] | None = None,
    omitted_lanes: set[str] | None = None,
) -> tuple[dict, dict]:
    lanes: dict[str, dict] = {}
    pointers: list[dict] = []
    omitted = omitted_lanes or set()
    overrides = x3_overrides or {}

    for lane in GENERATED_LANE_IDS:
        if lane in omitted:
            continue
        run_dir = repo / "runs" / lane
        run_dir.mkdir(parents=True, exist_ok=True)
        for filename in REQUIRED_PROOF_FILES:
            (run_dir / filename).write_text("{}\n", encoding="utf-8")
        x3_code = overrides.get(lane, "X3_ALLOW")
        rel_run_dir = f"runs/{lane}"
        lanes[lane] = {
            "latest_successful_real_artifact_path": rel_run_dir,
            "x2_failed": 0,
            "x3_code": x3_code,
        }
        pointers.append(
            {
                "lane": lane,
                "x3_code": x3_code,
                "product_quality_status": "PASS",
                "pool_receipt_status": "PASS",
            }
        )

    return {"lanes": lanes}, {"pointers": pointers}


def test_final_aggregation_blocks_when_required_lane_is_blocked_or_not_run(tmp_path: Path) -> None:
    fingerprint = {
        "same_date_prefix_coherent": True,
        "jd_digest_coherent": "OK",
        "briefing_digest_coherent": "OK",
    }
    blocked_rollup, blocked_sealed = _write_minimal_required_proof_tree(
        tmp_path,
        x3_overrides={"insurtech_narrative": "X3_BLOCK_UPSTREAM_BULLETS_NOT_FINALIZED"},
    )

    blocked_results = run_aggregation_preflight(
        repo=tmp_path,
        rollup_blob=blocked_rollup,
        fingerprint=fingerprint,
        sealed_index=blocked_sealed,
    )

    blocked_gate = next(g for g in blocked_results if g.gate_id == "x2_preflight_no_blocked_x3")
    assert blocked_gate.pass_ is False
    assert blocked_gate.observed == ["insurtech_narrative"]
    with pytest.raises(AggregationPreflightError):
        assert_preflight_pass(blocked_results)

    not_run_rollup, not_run_sealed = _write_minimal_required_proof_tree(
        tmp_path / "not_run_case",
        omitted_lanes={"insurtech_narrative"},
    )
    not_run_results = run_aggregation_preflight(
        repo=tmp_path / "not_run_case",
        rollup_blob=not_run_rollup,
        fingerprint=fingerprint,
        sealed_index=not_run_sealed,
    )

    proof_gate = next(g for g in not_run_results if g.gate_id == "x2_preflight_required_proof_artifacts_present")
    assert proof_gate.pass_ is False
    assert "insurtech_narrative:missing_rollup_lane" in proof_gate.observed
    with pytest.raises(AggregationPreflightError):
        assert_preflight_pass(not_run_results)
