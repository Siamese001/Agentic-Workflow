"""W4: deterministic X2 gates — every proof id must stay inside the section SRFS slice."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections import selected_role_fact_set as srfs
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates
from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates
from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

from tests._apps_contract.contract_harness_paths import harness_run

REPO = Path(__file__).resolve().parents[2]


def _high_row(candidate_fact_id: str, *, claim_text: str = "Fixture claim.") -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": claim_text,
        "metric_values": [],
    }


def _srfs(selection_id: str, sections: dict[str, list[dict]]) -> dict:
    out = {
        "selection_id": selection_id,
        "selected_facts_by_section": dict(sections),
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
        "confidence_policy": "HIGH-only test fixture",
        "candidate_not_canonical_assertion": True,
        "no_jd_fact_minting_assertion": True,
    }
    for k in SECTION_KEYS:
        out["selected_facts_by_section"].setdefault(k, [])
    return out


def test_validate_rejects_disallowed_and_unknown_ids() -> None:
    allow = {"fact_a"}
    ok, bad = srfs.validate_source_fact_ids_within_srfs_slice(
        collected_ids=["fact_a", "jd", "fact_z", "JD_ONLY"],
        allowed_fact_ids=allow,
    )
    assert ok is False
    assert set(bad) >= {"jd", "fact_z", "JD_ONLY"}


def test_headline_srfs_gate_skipped_when_not_active() -> None:
    gates = run_headline_x2_gates(
        headline_line="SVP Engineering | A B | C D | E F",
        parsed_output={
            "headline_line": "x",
            "selected_fact_plan": {"facts": [], "required_fact_ids": []},
            "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}],
            "jd_alignment": {"jd_used_as_proof": False, "briefing_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}],
        jd_text="",
        target_company="",
        target_title="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=False,
    )
    gids = [g.gate_id for g in gates]
    assert "x2_headline_source_fact_ids_within_srfs_slice" not in gids
    assert "x2_headline_active_proof_pool_source_fact_ids" not in gids


def test_headline_srfs_gate_fails_exec_only_fact(tmp_path: Path) -> None:
    p = tmp_path / "srfs.json"
    p.write_text(
        json.dumps(
            _srfs(
                "w4_head",
                {
                    "headline": [_high_row("bul_headline_only_001")],
                    "executive_summary": [_high_row("bul_exec_only_001")],
                },
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "headline")
    gates = run_headline_x2_gates(
        headline_line="SVP Engineering | A B | C D | E F",
        parsed_output={
            "headline_line": "x",
            "selected_fact_plan": {"facts": [], "required_fact_ids": ["bul_exec_only_001"]},
            "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["bul_exec_only_001"]}],
            "jd_alignment": {"jd_used_as_proof": False, "briefing_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_exec_only_001"]}],
        jd_text="",
        target_company="",
        target_title="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=allowed,
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_headline_active_proof_pool_source_fact_ids"]
    assert g.pass_ is False
    assert "bul_exec_only_001" in (g.observed_value.get("out_of_slice_fact_ids") or [])


def _minimal_bullets_stub(prefix: str = "bul_unify_") -> tuple[list[dict], list[dict], dict]:
    bullets = []
    ledger = []
    for i, bid in enumerate(UNIFY_BULLET_IDS, start=1):
        fid = f"{prefix}{i:03d}"
        txt = f"Bullet text for {bid} aligned fixture."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": txt,
                "rewrite_intensity": "HEAVY" if i <= 2 else ("MODERATE" if i <= 5 else "LIGHT_PROTECTED"),
                "source_fact_ids": [fid],
            }
        )
        ledger.append({"claim_text": txt, "source_fact_ids": [fid]})
    dist = {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6}
    po = {
        "bullets": bullets,
        "selected_fact_plan": {"facts": [], "required_fact_ids": []},
        "claim_ledger": ledger,
        "jd_alignment": {"jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [],
        "rewrite_distribution": dist,
        "self_check": {},
    }
    return bullets, ledger, po


@pytest.mark.parametrize("section", GENERATED_LANES)
def test_offline_stub_includes_srfs_slice_gate_pass(structure_w4_srfs: Path, section: str, monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse
    import uuid

    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    u = uuid.uuid4().hex[:10]
    run_dir = harness_run(f"_w4_contract_{u}", section)
    run_dir.mkdir(parents=True, exist_ok=True)
    srfs_path = str(structure_w4_srfs)

    if section == "headline":
        from apps_rg.runtime.sections.headline_lane import build_headline_lane_args, run_headline_execution

        args = build_headline_lane_args(
            provider="qwen_vllm",
            temperature=0.55,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_headline_execution(args, artifact_dir_override=run_dir, print_output=False)
    elif section == "executive_summary":
        from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution
        from apps_rg.runtime.sections.executive_summary_lane import build_parser
        from tests._apps_contract.test_exec_summary_section_pipeline import _tag_exec_summary_provider_resolution

        args = build_parser().parse_args(["--provider", "mock", "--mock-judges", "--allow-non-allow-exit-zero"])
        _tag_exec_summary_provider_resolution(args)
        args.allow_test_mock_judges = True
        args.selected_role_fact_set = srfs_path
        run_executive_summary_execution(args, artifact_dir_override=run_dir)
    elif section == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_lane import run_unify_bullets_execution

        args = argparse.Namespace(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_unify_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "unify_narrative":
        from apps_rg.runtime.sections.unify_narrative_lane import run_unify_narrative_execution

        args = argparse.Namespace(
            provider="mock",
            temperature=0.32,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_unify_narrative_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_bullets_lane import run_ibm_bullets_execution

        args = argparse.Namespace(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_ibm_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_narrative":
        from apps_rg.runtime.sections.ibm_narrative_lane import run_ibm_narrative_lane_execution

        args = argparse.Namespace(
            provider="mock",
            temperature=0.35,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_ibm_narrative_lane_execution(args, artifact_dir_override=run_dir)
    elif section == "competencies":
        from apps_rg.runtime.sections.competencies_lane import build_competencies_lane_args, run_competencies_lane_execution

        args = build_competencies_lane_args(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs_path,
        )
        run_competencies_lane_execution(args, artifact_dir_override=run_dir)
    else:
        raise AssertionError(section)

    x2_path = run_dir / "x2_gate_outputs.json"
    assert x2_path.is_file(), section
    blob = json.loads(x2_path.read_text(encoding="utf-8"))
    gates = blob.get("gates") or []
    # Map section -> gate id
    gate_pattern = f"x2_{section}_active_proof_pool_source_fact_ids"
    by_id = {g["gate_id"]: g for g in gates}
    assert gate_pattern in by_id, (section, [g["gate_id"] for g in gates][:20])
    assert by_id[gate_pattern]["pass"] is True, by_id[gate_pattern]
    obs = by_id[gate_pattern].get("observed_value") or {}
    assert obs.get("x2_srfs_gate_status") in (True, "NOT_APPLICABLE")
    assert "within_srfs_slice" not in gate_pattern
    if obs.get("x2_srfs_gate_status") == "NOT_APPLICABLE":
        assert obs.get("selected_role_fact_set_used") is False
    else:
        assert obs.get("selected_role_fact_set_used") is True
    assert obs.get("srfs_section_id") == section
    assert obs.get("out_of_slice_fact_ids") == []


@pytest.fixture
def structure_w4_srfs(tmp_path: Path) -> Path:
    # IDs aligned with canonical unify / IBM ordinals where lanes require fixed bullet_id slots.
    doc = _srfs(
        "w4_structure",
        {
            "headline": [_high_row("bul_unify_001")],
            "executive_summary": [_high_row("bul_exec_w4_001")],
            "unify_bullets": [_high_row(f"bul_unify_{i:03d}") for i in range(1, 7)],
            "unify_narrative": [_high_row("bul_unify_001"), _high_row("unify_narrative_base_001")],
            "ibm_bullets": [_high_row(f"bul_ibm_{i:03d}") for i in range(1, 6)],
            "ibm_narrative": [_high_row("bul_ibm_001")],
            "competencies": [_high_row("bul_unify_001"), _high_row("bul_ibm_001")],
        },
    )
    p = tmp_path / "w4_srfs.json"
    p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return p


def test_unify_narrative_srfs_gate_fails_synthetic_not_in_slice(tmp_path: Path) -> None:
    p = tmp_path / "srfs_un.json"
    p.write_text(json.dumps(_srfs("w4_un", {"unify_narrative": [_high_row("bul_unify_001")]})), encoding="utf-8")
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "unify_narrative")
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Single sentence about Unify Consulting platforms for enterprise.",
        parsed_output={
            "narrative_sentence": "x",
            "claim_ledger": [],
            "jd_alignment": {
                "selected_jd_themes": ["t"],
                "targeting_rationale": "r",
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
                "selected_briefing_themes": [],
            },
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "Led platform work.", "source_fact_ids": ["unify_narrative_base_001"]}],
        jd_text="enterprise",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts=None,
        x1d_judges=[],
        allowed_fact_ids=allowed,
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_unify_narrative_active_proof_pool_source_fact_ids"]
    assert g.pass_ is False
    assert "unify_narrative_base_001" in (g.observed_value.get("out_of_slice_fact_ids") or [])


def test_unify_bullets_srfs_gate_detects_cross_slice_id(tmp_path: Path) -> None:
    p = tmp_path / "srfs_ub.json"
    p.write_text(json.dumps(_srfs("w4_ub", {"unify_bullets": [_high_row("bul_unify_001")]})), encoding="utf-8")
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "unify_bullets")
    bullets, ledger, po = _minimal_bullets_stub("bul_unify_")
    ledger[0] = {
        "claim_text": ledger[0]["claim_text"],
        "source_fact_ids": ["bul_exec_cross_001"],
    }
    bullets[0]["source_fact_ids"] = ["bul_exec_cross_001"]
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=allowed,
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_bullets_active_proof_pool_source_fact_ids"].pass_ is False


def test_competencies_term_bad_id_fails_srfs_gate(tmp_path: Path) -> None:
    p = tmp_path / "srfs_co.json"
    p.write_text(json.dumps(_srfs("w4_co", {"competencies": [_high_row("bul_comp_001")]})), encoding="utf-8")
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "competencies")
    competencies = []
    for i in range(8):
        competencies.append(
            {
                "category_label": f"Category {i}",
                "terms": [
                    {
                        "text": f"skill {i}a",
                        "source_fact_id": "bul_comp_001",
                        "source_fact_ids": ["bul_comp_001"],
                    },
                    {
                        "text": f"skill {i}b",
                        "source_fact_id": "bul_comp_001",
                        "source_fact_ids": ["bul_comp_001"],
                    },
                ],
                "source_fact_ids": ["bul_comp_001"],
            }
        )
    competencies[0]["terms"][0]["source_fact_ids"] = ["bul_bad_outside"]
    competencies[0]["terms"][0]["source_fact_id"] = "bul_bad_outside"
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output={
            "competencies": competencies,
            "claim_ledger": [{"claim_text": "c", "source_fact_ids": ["bul_comp_001"]} for _ in range(3)],
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_comp_001"]} for _ in range(3)],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=[],
        resume_support_blob="bul_comp_001 skill",
        allowed_fact_ids=allowed,
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_competencies_active_proof_pool_source_fact_ids"].pass_ is False


def test_ibm_narrative_srfs_gate_fails_non_slice_bullet(tmp_path: Path) -> None:
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    p = tmp_path / "srfs_in.json"
    p.write_text(json.dumps(_srfs("w4_in", {"ibm_narrative": [_high_row("bul_ibm_001")]})), encoding="utf-8")
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "ibm_narrative")
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence="Led regulated financial platforms and modernization programs for enterprise scale.",
        parsed_output={
            "narrative_sentence": "x",
            "jd_alignment": {},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "x", "source_fact_ids": [IBM_BULLET_IDS[1]]}],
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts=None,
        x1d_judges=[],
        allowed_fact_ids=list(allowed),
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_ibm_narrative_active_proof_pool_source_fact_ids"].pass_ is False


def test_ibm_bullets_srfs_gate_fails_out_of_slice(tmp_path: Path) -> None:
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    p = tmp_path / "srfs_ibb.json"
    p.write_text(json.dumps(_srfs("w4_ibb", {"ibm_bullets": [_high_row("bul_ibm_001")]})), encoding="utf-8")
    _, _, allowed, _ = srfs.resolve_srfs_section_proof_bundle(p, "ibm_bullets")
    bullets = []
    ledger = []
    for bid in IBM_BULLET_IDS:
        txt = f"IBM bullet {bid} text with metrics $15M 99.9% 30% 25% 50%."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": txt,
                "rewrite_intensity": "MODERATE",
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": txt, "source_fact_ids": [bid]})
    po = {
        "bullets": bullets,
        "selected_fact_plan": {"facts": []},
        "claim_ledger": ledger,
        "jd_alignment": {"jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [],
        "rewrite_distribution": {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5},
        "self_check": {},
    }
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=allowed,
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_ibm_bullets_active_proof_pool_source_fact_ids"].pass_ is False
