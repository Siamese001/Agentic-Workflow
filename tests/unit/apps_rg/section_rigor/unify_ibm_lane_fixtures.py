"""Shared in-process fixtures for Unify/IBM bullets+narrative E2E rigor (no live vLLM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]


def _fake_judges(*, pass_all: bool = True) -> list[dict[str, Any]]:
    return [
        {
            "provider_key": key,
            "evaluator_mode": "MOCKED",
            "provider_blocked": False,
            "pass": pass_all,
        }
        for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude")
    ]


def _unify_role_episode_meta() -> dict[str, Any]:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority
    from apps_rg.runtime.sections.unify_role_episode_evidence import (
        attach_role_episode_bundles_to_proof_pool_metadata,
    )

    graph_ref = "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
    ledger_ref = "apps_rg/fact_inventory/candidate_fact_ledger.json"
    return attach_role_episode_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "graph_ref": graph_ref,
            "skills_authority_status": "PASS",
            "evidence_authority": build_evidence_authority(
                graph_ref=graph_ref,
                ledger_ref=ledger_ref,
                skills_authority_status="PASS",
            ),
            "selected_graph_evidence_plan": {
                "role_family_key": "SVP_AGENTIC_ENGINEERING",
                "target_role_profile": "SVP_AGENTIC_ENGINEERING",
            },
        },
        section_id="unify_bullets",
        repo_root=REPO,
    )


def _enrich_unify_mock_with_role_episode_contract(parsed: dict[str, Any]) -> dict[str, Any]:
    from apps_rg.runtime.sections.role_episode_metric_registry import metric_outcome_nodes_from_path
    from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
        BUNDLES_PATH as UNIFY_BUNDLES_PATH,
    )

    out = dict(parsed)
    meta = _unify_role_episode_meta()
    slot_map = meta["unify_bullet_slot_bundle_map_resolved"]
    bundle_by_id = {b["role_episode_bundle_id"]: b for b in meta["role_episode_bundles"]}
    metric_nodes = metric_outcome_nodes_from_path(UNIFY_BUNDLES_PATH)
    bullets: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    change_log: list[dict[str, Any]] = []
    for bid in (
        "bul_unify_001",
        "bul_unify_002",
        "bul_unify_003",
        "bul_unify_004",
        "bul_unify_005",
        "bul_unify_006",
    ):
        bundle = bundle_by_id[slot_map[bid]]
        mid = str(bundle["linked_metric_outcome_ids"][0])
        node = metric_nodes[mid]
        token = str((node.get("surface_tokens") or [node.get("metric")])[0])
        text = (
            f"Owned {token} across governed enterprise AI platform delivery, tying architecture "
            "mechanisms to measurable operating outcomes."
        )
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "has_metric": True,
                "metric_raw": mid,
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
        change_log.append(
            {
                "bullet_id": bid,
                "role_episode_bundle_id": bundle["role_episode_bundle_id"],
                "graph_skill_node_ids": list(bundle["graph_skill_node_ids"])[:3],
                "fact_ids_used": [bid, *list(bundle["linked_source_fact_ids"])[:1]],
                "metric_outcome_ids": [mid],
            }
        )
    out["bullets"] = bullets
    out["claim_ledger"] = ledger
    out["change_log"] = change_log
    out["proof_pool_metadata"] = meta
    return out


def unify_bullets_parsed_from_mock() -> tuple[dict[str, Any], set[str]]:
    from apps_rg.runtime.sections.unify_bullets_lane import (
        build_mock_output,
        build_runtime_payload,
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
    )
    from apps_rg.runtime.sections.unify_bullets_graph_evidence import TRACK_RANKED_SELECTION_METHOD

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    plan["selection_method"] = TRACK_RANKED_SELECTION_METHOD
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP IT Strategy & Innovation",
        target_company="Brown & Brown",
        jd_text="Enterprise AI platform leadership.",
        briefing="regulated insurance distribution",
    )
    parsed = build_mock_output(rp)
    plan = dict(parsed.get("selected_fact_plan") or plan)
    plan["selection_method"] = TRACK_RANKED_SELECTION_METHOD
    for row in plan.get("facts") or []:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or "")
        row["claim_text"] = f"Graph-bound evidence anchor for {fid} (compose target; not bullet prose)."
    parsed["selected_fact_plan"] = plan
    parsed = _enrich_unify_mock_with_role_episode_contract(parsed)
    parsed["selected_fact_plan"] = plan
    return parsed, allowed


def ibm_bullets_parsed_from_mock() -> tuple[dict[str, Any], set[str]]:
    from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
    from apps_rg.runtime.sections.ibm_bullets_lane import (
        build_mock_output,
        extract_ibm_employment,
    )
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    base, _path, _digest = load_lane_base_resume_json(repo_root=REPO)
    _hdr, facts, allowed = extract_ibm_employment(base)
    rp = {
        "selected_fact_plan": {"facts": facts},
        "jd_alignment": {"targeting_only": True},
    }
    parsed = build_mock_output(rp)
    return parsed, set(IBM_BULLET_IDS) & allowed


def unify_narrative_parsed_from_mock(*, companion_text: str = "- bul_unify_001: sample") -> dict[str, Any]:
    from apps_rg.runtime.sections.unify_narrative_lane import build_mock_output

    rp = {
        "selected_fact_plan": {"facts": []},
        "companion_bullets_text": companion_text,
        "companion_bullets_status": "ACCEPTED_FINALIZED",
        "companion_bullets_reason": "ok",
        "target_title": "SVP",
        "target_company": "Corp",
        "jd_text": "AI",
        "briefing": "brief",
    }
    out = build_mock_output(rp)
    out["companion_bullets_text"] = companion_text
    out["companion_bullets_status"] = rp["companion_bullets_status"]
    out["companion_bullets_reason"] = rp["companion_bullets_reason"]
    return out


def ibm_narrative_parsed_from_mock(*, companion_text: str = "- bul_ibm_001: sample") -> dict[str, Any]:
    from apps_rg.runtime.sections.ibm_narrative_lane_runtime import build_mock_output

    rp = {
        "selected_fact_plan": {"facts": []},
        "companion_bullets_text": companion_text,
        "companion_bullets_status": "ACCEPTED_FINALIZED",
        "companion_bullets_reason": "ok",
        "target_title": "SVP",
        "target_company": "Corp",
        "jd_text": "AI",
        "briefing": "brief",
    }
    out = build_mock_output(rp)
    out["companion_bullets_text"] = companion_text
    out["companion_bullets_status"] = rp["companion_bullets_status"]
    out["companion_bullets_reason"] = rp["companion_bullets_reason"]
    return out


def run_unify_bullets_x2(parsed: dict[str, Any], allowed: set[str]) -> list:
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        build_unify_bullets_text_claim_coverage,
        run_unify_bullets_x2_gates,
    )

    bullets = parsed["bullets"]
    ledger = parsed["claim_ledger"]
    if "text_claim_coverage" not in parsed:
        parsed = dict(parsed)
        parsed["text_claim_coverage"] = build_unify_bullets_text_claim_coverage(
            bullets, ledger, allowed
        )
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=allowed,
        jd_text="enterprise",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        proof_pool_metadata=parsed.get("proof_pool_metadata") if isinstance(parsed, dict) else None,
    )


def run_ibm_bullets_x2(parsed: dict[str, Any], allowed: set[str]) -> list:
    from apps_rg.runtime.validators.ibm_bullets_x2 import (
        build_ibm_bullets_text_claim_coverage,
        run_ibm_bullets_x2_gates,
    )

    bullets = parsed["bullets"]
    ledger = parsed["claim_ledger"]
    if "text_claim_coverage" not in parsed:
        parsed = dict(parsed)
        parsed["text_claim_coverage"] = build_ibm_bullets_text_claim_coverage(
            bullets, ledger, allowed
        )
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=allowed,
        jd_text="enterprise",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def run_unify_narrative_x2(
    parsed: dict[str, Any],
    *,
    runtime_generation_status: str = "MOCKED",
    companion_text: str = "",
    companion_status: str = "ACCEPTED_FINALIZED",
    companion_reason: str = "ok",
) -> list:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    narrative = str(parsed.get("narrative_sentence") or "")
    ledger = parsed.get("claim_ledger") or []
    resolved_companion = str(companion_text or parsed.get("companion_bullets_text") or "")
    resolved_status = str(companion_status or parsed.get("companion_bullets_status") or companion_status)
    resolved_reason = str(companion_reason or parsed.get("companion_bullets_reason") or companion_reason)
    return run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="enterprise",
        runtime_generation_status=runtime_generation_status,
        companion_bullet_texts=resolved_companion,
        companion_bullets_status=resolved_status,
        companion_bullets_reason=resolved_reason,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
    )


def run_ibm_narrative_x2(
    parsed: dict[str, Any],
    *,
    runtime_generation_status: str = "MOCKED",
    companion_text: str = "",
    companion_status: str = "ACCEPTED_FINALIZED",
    companion_reason: str = "ok",
    companion_aware: bool = True,
) -> list:
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = str(parsed.get("narrative_sentence") or "")
    ledger = parsed.get("claim_ledger") or []
    resolved_companion = str(companion_text or parsed.get("companion_bullets_text") or "")
    resolved_status = str(companion_status or parsed.get("companion_bullets_status") or companion_status)
    resolved_reason = str(companion_reason or parsed.get("companion_bullets_reason") or companion_reason)
    return run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="enterprise",
        runtime_generation_status=runtime_generation_status,
        companion_bullet_texts=resolved_companion,
        companion_bullets_status=resolved_status,
        companion_bullets_reason=resolved_reason,
        companion_aware=companion_aware,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        allowed_fact_ids=["bul_ibm_001", "bul_ibm_002"],
    )


def gate_results_map(gates: list) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for g in gates:
        gid = getattr(g, "gate_id", None) or (g.get("gate_id") if isinstance(g, dict) else None)
        if gid:
            out[str(gid)] = bool(getattr(g, "pass_", g.get("pass") if isinstance(g, dict) else False))
    return out


def assert_critical_gates_pass(lane: str, gates: list) -> None:
    from tests.unit.apps_rg.section_rigor.lane_registry import LANE_CRITICAL_GATES

    critical = LANE_CRITICAL_GATES[lane]
    results = gate_results_map(gates)
    missing = sorted(critical - set(results))
    assert not missing, f"{lane} missing gates: {missing}"
    failed = sorted(gid for gid in critical if not results.get(gid))
    assert not failed, f"{lane} critical failures: {[(g, results.get(g)) for g in failed]}"


def companion_bullets_l2_fixture(
    lane: str,
    *,
    product_quality: str = "PASS",
    runtime_status: str = "REAL_LLM",
    x3_code: str = "X3_ALLOW",
) -> dict[str, Any]:
    """Minimal accepted upstream bullets bundle for companion resolution tests."""
    if lane == "unify_bullets":
        parsed, _allowed = unify_bullets_parsed_from_mock()
        section_id = "unify_bullets"
    else:
        parsed, _allowed = ibm_bullets_parsed_from_mock()
        section_id = "ibm_bullets"
    return {
        "section_id": section_id,
        "product_quality_status": product_quality,
        "runtime_generation_status": runtime_status,
        "bullets": parsed["bullets"],
    }


__all__ = [
    "REPO",
    "assert_critical_gates_pass",
    "companion_bullets_l2_fixture",
    "gate_results_map",
    "ibm_bullets_parsed_from_mock",
    "ibm_narrative_parsed_from_mock",
    "run_ibm_bullets_x2",
    "run_ibm_narrative_x2",
    "run_unify_bullets_x2",
    "run_unify_narrative_x2",
    "unify_bullets_parsed_from_mock",
    "unify_narrative_parsed_from_mock",
]
