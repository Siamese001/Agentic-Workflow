"""W4: executive_summary prompt is PA-compiled via section_prompt_adapter (indirect: executive_summary_pa)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt

REPO_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (
    REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "executive_summary.generate_scratch_v1.yaml"
)


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _minimal_payload(*, run_id: str = "pa_test_run") -> dict:
    return {
        "product_visible": False,
        "run_id": run_id,
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform leadership",
        "briefing": "regulated enterprise environment",
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "es_pa_test_fact_001",
                    "claim_text": "Delivered governed agentic AI platforms at scale.",
                },
                {
                    "fact_id": "es_pa_test_fact_002",
                    "claim_text": "Reduced cycle time through standardized delivery patterns.",
                },
            ],
            "required_fact_ids": ["es_pa_test_fact_001", "es_pa_test_fact_002"],
        },
    }


def test_compile_executive_summary_returns_section_adapter_shape():
    payload = _minimal_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    assert isinstance(out, SectionCompiledPrompt)
    assert out.section_id == "executive_summary"
    assert "executive_summary.generate_scratch_v1.yaml" in out.apps_rg_prompt_template_ref
    assert out.artifact.template_id == "strategic_tailor_v1"
    assert len(out.artifact.messages) == 1
    assert out.artifact.messages[0]["role"] == "system"
    assert out.artifact.prompt_hash


def test_compiled_messages_include_only_payload_facts_and_jd_as_non_proof():
    payload = _minimal_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "es_pa_test_fact_001" in content
    assert "es_pa_test_fact_002" in content
    assert "<selected_facts" in content
    assert "SELECTED_FACT_PLAN" in content
    assert "NOT PROOF" in content
    assert "JD_TEXT (targeting only" in content and "NOT PROOF" in content
    assert "TARGET_TITLE (positioning only" in content
    cl = content.lower()
    assert "composition" in cl
    assert "5 or 6" in cl or "5–6" in content or "5-6" in cl
    assert "2 or 3 sentences" not in cl
    assert "2–3 sentences" not in content
    assert "jd_used_as_proof" in content
    assert "source_fact_ids" in content
    assert "ALLOWED_SOURCE_FACT_IDS (authoritative list" in content
    assert "Copy each ID character-for-character" in content
    assert "bul_unify_ 003" in content
    assert "bul_unify_003" in content
    assert "x2_claim_ledger_orphan_zero" in content
    assert "x2_claim_ledger_claim_text_non_empty" in content
    assert '"minLength": 1' in content
    assert "es_pa_test_fact_001" in content and "  - es_pa_test_fact_001" in content
    assert "resume_display_text must be clean prose" in content or "NO [source:" in content
    assert "Do not emit" in content or "must not emit" in content.lower()


def test_no_hard_sentence_count_phrases_in_exec_summary_prompt_sources():
    """No mandate for exactly two sentences in template; SRFS density may reference 4-or-5 in apps_rg PA only."""
    yaml_text = _TEMPLATE.read_text(encoding="utf-8")
    pa_src = (
        REPO_ROOT / "apps_rg" / "runtime" / "sections" / "executive_summary_pa.py"
    ).read_text(encoding="utf-8")
    for label, raw in (("yaml", yaml_text),):
        assert "exactly TWO synthesized" not in raw, label
        assert not re.search(r"\b4\s*to\s*5\b", raw, re.IGNORECASE), label
        assert re.search(r"composition_heuristics", raw, re.IGNORECASE), label
    assert "exactly TWO synthesized" not in pa_src
    assert "SRFS_COMPOSITION_ONESHOT_V1" in pa_src
    assert re.search(r"composition", pa_src, re.IGNORECASE)


def test_template_yaml_excludes_two_sentence_mandate_and_em_dash():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "exactly TWO synthesized" not in raw
    assert "\u2014" not in raw


def test_template_includes_many_shot_examples_and_deliberation_guards():
    from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0

    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "hydrated at compile" in raw
    assert raw.count("<transformation_example ") >= 2
    e0 = build_executive_summary_e0()
    assert "<many_shot_examples>" in e0
    assert e0.count("<positive_example ") >= 4
    assert "exec_summary_gold_base_resume_001" in e0
    assert "E0_STYLE_EXAMPLE_NOT_PROOF" in e0
    assert e0.count("<negative_example ") >= 3
    assert "<internal_deliberation_controls>" in raw
    assert "chain-of-thought" in raw.lower() or "chain of thought" in raw.lower()
    assert "Do **not** output chain-of-thought" in raw or "not output chain-of-thought" in raw
    assert "<self_check_requirements>" in raw
    assert "composition_themes_omitted_with_reason" in raw
    assert "jd_used_as_proof_false" in raw


def test_template_yaml_includes_north_star_synthesis_contract():
    from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0

    raw = _TEMPLATE.read_text(encoding="utf-8")
    e0 = build_executive_summary_e0()
    assert "<north_star_synthesis_contract>" in raw
    assert "SelectedRoleFactSet (SRFS)" in raw
    assert "<composition_heuristics>" in raw
    assert "exec_summary_pos_outcomes_led_001" in e0
    assert "exec_summary_neg_credential_dump_001" in e0
    assert "exec_summary_neg_mechanism_inventory_001" in e0


def test_template_yaml_includes_source_fact_id_spacing_examples():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "bul_unify_003" in raw
    assert "bul_unify_ 003" in raw
    assert "ALLOWED_SOURCE_FACT_IDS" in raw


def test_template_yaml_includes_claim_ledger_non_empty_claim_text_contract():
    payload = _minimal_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "x2_claim_ledger_claim_text_non_empty" in content
    assert content.index("PRODUCT_SHAPE") < content.index("x2_claim_ledger_claim_text_non_empty")


def test_self_check_fields_list_in_r0_matches_contract():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "<self_check_requirements>" in raw
    for field in (
        "no_first_person",
        "jd_used_as_proof_false",
        "no_keyword_stuffing",
        "composition_themes_used",
    ):
        assert field in raw


def test_compiled_srfs_appendix_contains_pool_and_blocking_rules():
    """When runtime_payload carries SelectedRoleFactSet integration, appendix + INPUT_AUTHORITY switch."""
    pool_ids = ["fact_exec_srfs_aa", "fact_exec_srfs_bb"]
    payload = _minimal_payload()
    payload["allowed_fact_ids"] = pool_ids
    facts = [{"fact_id": pool_ids[i], "claim_text": f"claim{i}"} for i in range(len(pool_ids))]
    payload["selected_fact_plan"] = {
        "section_id": "executive_summary",
        "facts": facts,
        "required_fact_ids": pool_ids,
    }
    payload["proof_pool_metadata"] = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_skills_proof_pool": True,
        "blocked_facts_count": 2,
        "facts_requiring_human_confirmation_count": 3,
        "unsupported_jd_needs_count": 1,
        "selection_scope": {"selection_id": "sel_fixture"},
        "evidence_authority": {
            "authority": "augmented_skills_graph",
            "skills_authority_status": "PASS",
        },
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "GRAPH_PROOF_POOL_APPENDIX" in content
    assert "fact_exec_srfs_aa" in content and "fact_exec_srfs_bb" in content
    assert "MEDIUM, LOW, and NEEDS_VERIFICATION" in content
    assert "JD_TEXT (targeting only" in content
    assert "NOT PROOF" in content
    assert "unsupported jd themes" in content.lower()
    import apps_rg.runtime.sections.executive_summary_pa as pa

    assert pa.SRFS_STYLE_ONESHOT_MARKER in content
    assert "STYLE_ONLY_NOT_PROOF" in content
    assert "causal arc" in content.lower() or "metric-dump" in content.lower()
    assert pa.SRFS_COMPOSITION_ONESHOT_MARKER in content
    assert "PRODUCT_SHAPE" in content
    assert "x2_exec_summary_paragraph_max_words" in content
    assert "72–220" not in content and "72-220" not in content
    assert "x2_exec_summary_sentence_count_5_6" in content
    assert "x2_exec_summary_no_credential_dump" in content
    assert "x2_exec_summary_no_mechanism_inventory" in content
    assert "srfs_governance_omission_explained" in content
    assert "credential dump" in content.lower() or "credential_policy_v1" in content
    assert "integrated credibility" in content.lower()
    assert "srfs_product_shape" not in content
    assert "<exemplar_platform_led>" not in content
    assert "srfs_five_part_exec_architecture" not in content
    assert "srfs_suggested_target_shape" not in content


def test_non_srfs_compiled_prompt_includes_north_star_synthesis_contract():
    payload = _minimal_payload()
    payload["evidence_capsule_active"] = True
    payload["evidence_capsule"] = {
        "c0_block": "SELECTED_FACT_PLAN (capsule):\n- es_pa_test_fact_001: fact\n",
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "<north_star_synthesis_contract>" in content
    assert "causal arc" in content.lower()
    assert "metric-dump" in content.lower()
    import apps_rg.runtime.dispatch.executive_summary_pa as pa

    assert pa.SRFS_STYLE_ONESHOT_MARKER not in content
    assert "<srfs_style_only_oneshot" not in content


def test_srfs_lane_retry_is_x2_aligned_not_five_part_slots():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    src = Path(lane.__file__).read_text(encoding="utf-8")
    assert "5 or 6" in src.lower()
    assert "claim_ledger" in src and "source_fact_id" in src
    assert "repair_messages2" not in src
    assert "result2 = call_qwen" not in src
    assert "SRFS SURGICAL DENSITY REPAIR" not in src
    assert "do not expand Sentence 4" not in src


def test_offline_qwen_stub_classifies_as_plumbing_not_product_proof(monkeypatch: pytest.MonkeyPatch):
    from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
    from apps_rg.runtime.section_proof.mock_runtime_proof_policy import infer_product_quality_blocked_or_mock

    monkeypatch.setattr(
        "apps_rg.runtime.product_output_policy.product_fail_closed_runtime",
        lambda: False,
    )
    status, reason = infer_product_quality_blocked_or_mock(
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        x2_failed_gate_ids=[],
        pass_reason="ok",
    )
    assert status == "PARTIAL"
    assert "plumbing-only" in reason.lower() or "not live" in reason.lower()


def test_lane_repair_prompt_uses_sentence_roles_not_fixed_count():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    src = Path(lane.__file__).read_text(encoding="utf-8")
    assert "exactly TWO synthesized" not in src
    assert "jd_used_as_proof=false" in src
    assert "5 or 6" in src.lower()
    assert "north_star_style_example_echo_unsupported" in src
    import apps_rg.runtime.sections.executive_summary_pa as pa

    examples = (
        REPO_ROOT / "apps_rg" / "prompt_assembly" / "examples" / "executive_summary_examples.yaml"
    ).read_text(encoding="utf-8").lower()
    assert "ip-led revenue" in examples or "productized ai revenue" in examples


def test_compile_prompt_hash_is_stable_sha16():
    payload = _minimal_payload(run_id="hash_run")
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    messages = out.artifact.messages
    compiled = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    h = _sha16(compiled)
    assert len(h) == 16
    assert "<!-- SLOT:" in compiled


def test_examples_yaml_contains_gold_style_example_not_proof():
    import yaml

    p = REPO_ROOT / "apps_rg" / "prompt_assembly" / "examples" / "executive_summary_examples.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    ids = [e["id"] for e in data.get("examples", [])]
    assert "exec_summary_gold_base_resume_001" in ids
    assert "exec_summary_pos_outcomes_led_001" in ids
    assert "exec_summary_neg_credential_dump_001" in ids
    assert "exec_summary_neg_mechanism_inventory_001" in ids
    assert "exec_summary_pos_credibility_implied_001" in ids
    gold = next(e for e in data["examples"] if e["id"] == "exec_summary_gold_base_resume_001")
    assert gold["category"] == "positive_gold"
    assert gold["authority"] == "E0_STYLE_EXAMPLE_NOT_PROOF"
    assert "weak" not in gold["annotation"].lower()
    assert "exec_summary_pos_001" not in ids


def test_executive_summary_judge_packet_grade_only_shape():
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        GRADE_ONLY_INSTRUCTION,
        build_executive_summary_judge_packet,
        judge_packet_hash,
        render_judge_prompt_from_packet,
    )

    packet = build_executive_summary_judge_packet(
        resume_display_text="Short.",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["fact_exec_001"]}],
        allowed_fact_packet=[{"fact_id": "fact_exec_001", "claim_text": "supported"}],
        allowed_fact_ids={"fact_exec_001"},
        target_title="SVP",
        target_company="Corp",
        jd_text="jd targeting",
        briefing_text="brief targeting",
        parsed_output={"self_check": {}},
    )
    assert packet["judge_task"] == "GRADE_ONLY"
    assert packet["section"] == "executive_summary"
    assert packet["candidate_output"]["resume_display_text"] == "Short."
    assert packet["allowed_fact_packet"]
    assert packet["proof_boundary"]["jd_is_targeting_context_only"] is True
    assert packet["proof_boundary"]["judges_must_not_rewrite"] is True
    assert packet["deterministic_gate_summary"]["x2_exec_summary_paragraph_max_words"]["pass"] is True
    assert "x2_exec_summary_srfs_density_word_count" not in packet["deterministic_gate_summary"]
    prompt = render_judge_prompt_from_packet(packet)
    assert "GRADE_ONLY" in prompt
    assert "Do NOT write a new executive summary" in prompt
    assert "ALLOWED_FACT_PACKET" in prompt
    assert "CANDIDATE_OUTPUT" in prompt
    assert "TARGETING_CONTEXT (NOT PROOF)" in prompt
    assert GRADE_ONLY_INSTRUCTION.splitlines()[0] in prompt
    assert judge_packet_hash(packet)


def test_run_llm_judges_uses_judge_packet_not_legacy_rubric_prompt():
    from apps_rg.runtime.judges.executive_summary_x1d import RUBRIC, run_llm_judges
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        build_executive_summary_judge_packet,
        render_judge_prompt_from_packet,
    )

    packet = build_executive_summary_judge_packet(
        resume_display_text="Candidate summary for grading.",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["fact_a"]}],
        allowed_fact_packet=[{"fact_id": "fact_a"}],
        allowed_fact_ids={"fact_a"},
        target_title="T",
        target_company="C",
        jd_text="jd",
        briefing_text="brief",
        parsed_output={},
    )
    rendered = render_judge_prompt_from_packet(packet)
    assert "GRADE_ONLY" in rendered
    assert RUBRIC[:40] not in rendered
    judges = run_llm_judges(
        resume_display_text="Candidate summary for grading.",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["fact_a"]}],
        judge_keys=[],
        mode="blocked_if_unavailable",
        judge_packet=packet,
        compiled_prompt="GENERATOR_PROMPT_SHOULD_NOT_APPEAR_IN_JUDGE_PACKET_PATH",
    )
    assert judges == []


def test_proof_judge_model_blocks_flash_and_mini_tiers():
    from apps_rg.runtime.judges.executive_summary_judge_profile import (
        is_forbidden_proof_judge_model,
        resolve_executive_summary_proof_judge_model,
    )

    assert is_forbidden_proof_judge_model("gemini-2.0-flash")
    assert is_forbidden_proof_judge_model("gpt-4o-mini")
    assert not is_forbidden_proof_judge_model("gemini-3.1-pro-preview")
    assert not is_forbidden_proof_judge_model("claude-sonnet-4-6")

    res = resolve_executive_summary_proof_judge_model(
        "gemini_pro", {"APPS_RG_GOOGLE_JUDGE_MODEL": "gemini-2.0-flash"}
    )
    assert not res.blocked
    assert res.model_requested == "gemini-3.1-pro-preview"
    assert res.model_source == "profile_default"


def test_openai_gpt51_omits_reasoning_effort_param():
    from apps_rg.runtime.judges.executive_summary_x1d import _openai_reasoning_effort_supported

    assert not _openai_reasoning_effort_supported("gpt-5.1")
    assert not _openai_reasoning_effort_supported("gpt-5.4")
    assert not _openai_reasoning_effort_supported("gpt-5.5")
    assert not _openai_reasoning_effort_supported("gpt-5.5-pro")
    assert _openai_reasoning_effort_supported("o3-mini")


def test_parsed_to_raw_model_output_json_omits_selected_fact_plan():
    from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
        parsed_to_raw_model_output_json,
    )

    raw = parsed_to_raw_model_output_json(
        {"resume_display_text": "x", "claim_ledger": [], "selected_fact_plan": {"facts": []}}
    )
    assert "selected_fact_plan" not in raw


def test_run_llm_judges_judge_packet_records_model_requested(monkeypatch):
    from apps_rg.runtime.judges import executive_summary_x1d as x1d
    from apps_rg.runtime.judges.executive_summary_judge_packet import build_executive_summary_judge_packet

    packet = build_executive_summary_judge_packet(
        resume_display_text="Grade me.",
        claim_ledger=[],
        allowed_fact_packet=[],
        allowed_fact_ids=set(),
        target_title="T",
        target_company="C",
        jd_text="jd",
        briefing_text="b",
        parsed_output={},
    )

    def _fake_openai(*_a, **kwargs):
        out = x1d._make_model_backed_output(
            "openai_chatgpt",
            "abc",
            "gpt-5.5-pro",
            {
                "score_scale": "0_to_5",
                "score": 4.5,
                "threshold": 4.0,
                "pass": True,
                "decisive_failure": False,
                "findings": ["ok"],
                "cited_sentence_indexes": [1],
                "remediation_suggestions": [],
                "rationale": "supported",
            },
        )
        return x1d._attach_judge_receipt_fields(
            out,
            kwargs.get("judge_receipt"),
            model_requested=kwargs.get("model_requested") or "gpt-5.5-pro",
        )

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("APPS_RG_OPENAI_JUDGE_MODEL", "gpt-5.5-pro")
    monkeypatch.setattr(x1d, "_call_openai", _fake_openai)
    rows = x1d.run_llm_judges(
        resume_display_text="Grade me.",
        claim_ledger=[],
        judge_keys=["openai_chatgpt"],
        judge_packet=packet,
    )
    assert rows[0].model_name in ("gpt-5.5", "gpt-5.5-pro")
    assert rows[0].to_dict()["model_requested"] in (None, "gpt-5.5", "gpt-5.5-pro")
    assert rows[0].judge_packet_hash
    assert rows[0].evaluator_mode == "MODEL_BACKED"
    assert rows[0].mocked is False
