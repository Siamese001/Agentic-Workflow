"""W4: executive_summary prompt is PA-compiled via section_prompt_adapter (indirect: executive_summary_pa)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

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
    assert "sentence role" in cl
    assert (
        "fixed sentence count" in cl
        or "no fixed sentence" in cl
        or "2 or 3 sentences" in cl
        or "2–3 sentences" in content
        or "2-3 sentences" in cl
    )
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
    import apps_rg.runtime.dispatch.executive_summary_pa as pa

    pa_src = Path(pa.__file__).read_text(encoding="utf-8")
    for label, raw in (("yaml", yaml_text),):
        assert "exactly TWO synthesized" not in raw, label
        assert not re.search(r"\b4\s*to\s*5\b", raw, re.IGNORECASE), label
        assert re.search(r"sentence role", raw, re.IGNORECASE), label
    assert "exactly TWO synthesized" not in pa_src
    assert "SRFS_FIVE_PART_EXEC_ARCH_V1" in pa_src or "4 or 5" in pa_src
    assert re.search(r"sentence role", pa_src, re.IGNORECASE)


def test_template_yaml_excludes_two_sentence_mandate_and_em_dash():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "exactly TWO synthesized" not in raw
    assert "\u2014" not in raw


def test_template_includes_many_shot_examples_and_deliberation_guards():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "<many_shot_examples>" in raw
    assert raw.count("<positive_example ") >= 1
    assert "exec_summary_gold_base_resume_001" in raw
    assert "E0_STYLE_EXAMPLE_NOT_PROOF" in raw
    assert raw.count("<negative_example ") >= 3
    assert raw.count("<transformation_example ") >= 2
    assert "<internal_deliberation_controls>" in raw
    assert "chain-of-thought" in raw.lower() or "chain of thought" in raw.lower()
    assert "Do **not** output chain-of-thought" in raw or "not output chain-of-thought" in raw
    assert "<self_check_requirements>" in raw
    assert "sentence_roles_omitted_with_reason" in raw
    assert "jd_used_as_proof_false" in raw


def test_template_yaml_includes_north_star_synthesis_contract():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "<north_star_synthesis_contract>" in raw
    assert "style-only one-shot" in raw
    assert "SelectedRoleFactSet (SRFS)" in raw
    assert "SRFS_THREE_SENTENCE_EXEC_ARCH_V1" in raw
    assert "SRFS_FIVE_PART_EXEC_ARCH_V1" in raw
    assert "SRFS_SENTENCE_RESP_SEP_V1" in raw


def test_template_yaml_includes_source_fact_id_spacing_examples():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "bul_unify_003" in raw
    assert "bul_unify_ 003" in raw
    assert "ALLOWED_SOURCE_FACT_IDS" in raw


def test_template_yaml_includes_claim_ledger_non_empty_claim_text_contract():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "x2_claim_ledger_claim_text_non_empty" in raw


def test_self_check_fields_list_in_r0_matches_contract():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "SELF_CHECK_FIELDS:" in raw
    for field in (
        "no_first_person:",
        "jd_used_as_proof_false:",
        "no_keyword_stuffing:",
        "sentence_roles_used:",
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
    payload["srfs_integration"] = {
        "artifact_path_resolved": "/tmp/selected_role_fact_set_test.json",
        "selection_id": "sel_fixture",
        "executive_summary_selected_fact_ids": pool_ids,
        "blocked_facts_count": 2,
        "facts_requiring_human_confirmation_count": 3,
        "unsupported_jd_needs_count": 1,
        "blocked_candidate_fact_ids": [],
        "confirmation_required_candidate_fact_ids": [],
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "SELECTED_ROLE_FACT_SET_APPENDIX" in content
    assert "fact_exec_srfs_aa" in content and "fact_exec_srfs_bb" in content
    assert "MEDIUM, LOW, and NEEDS_VERIFICATION" in content
    assert "JD_TEXT (targeting only" in content
    assert "NOT PROOF" in content
    assert "unsupported jd themes" in content.lower()
    assert "SELECTED_ROLE_FACT_SET_EXECUTIVE_SLICE" in content

    import apps_rg.runtime.dispatch.executive_summary_pa as pa

    src = Path(pa.__file__).read_text(encoding="utf-8")
    assert "\u2014" not in src
    assert pa.SRFS_STYLE_ONESHOT_MARKER in content
    assert "STYLE_ONLY_NOT_PROOF" in content
    assert "selected_facts_by_section" in content
    assert "Engineering executive with expertise in" in content
    assert "causal arc" in content.lower()
    assert "metric-dump" in content.lower() or "Do **not** stack metrics" in content
    assert "standalone credential" in content.lower() or "credential sentence" in content.lower()
    assert pa.SRFS_FIVE_PART_EXEC_ARCH_MARKER in content
    assert "srfs_five_part_exec_architecture" in content
    assert pa.SRFS_SENTENCE_RESP_SEP_MARKER in content
    assert "105–145" in content or "105-145" in content
    assert "95" in content and "160" in content
    assert "x2_exec_summary_srfs_density_word_count" in content
    assert "x2_exec_summary_srfs_sentence_count_4_5" in content
    assert "selected_fact_pool_too_small" in content
    assert "srfs_anti_thinness" in content
    assert "Must not include:" in content and "revenue" in content.lower()
    assert "while scaling" in content.lower() and "forbidden" in content.lower()
    assert "srfs_hard_anti_chain" in content
    assert "Technical performance" in content or "technical performance" in content.lower()
    assert "srfs_style_contrast_chain_vs_split" in content
    assert "Designed and operationalized architectures combining deterministic routing" in content
    assert "Designed governed runtime architectures that combine deterministic routing" in content
    assert "fact_governance_003" in content
    assert "srfs_governance_omission_explained" in content
    assert "Holds certifications" in content and "forbidden" in content.lower()
    assert "srfs_anti_metric_chain" in content
    assert "Led X that reduced A" in content
    assert "srfs_credential_integration" in content
    assert "srfs_suggested_target_shape" in content
    assert "x2_exec_summary_srfs_sentence_responsibility_shape" in content
    assert "$14M" in content or "14M" in content
    assert "x2_north_star_style_echo_unsupported_zero" in content
    assert "IP-led revenue" in content
    assert "productized ai revenue" in content.lower()
    assert pa.SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR.split()[0] in content
    assert "Do **not** copy facts" in content or "unless the **same substance**" in content
    assert "integrated credibility" in content.lower()
    assert "pairs aws" in content.lower()
    assert "must not start" in content.lower() and "**`Holds`**" in content


def test_non_srfs_compiled_prompt_includes_north_star_synthesis_contract():
    payload = _minimal_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "<north_star_synthesis_contract>" in content
    assert "causal arc" in content.lower()
    assert "metric-dump" in content.lower()
    import apps_rg.runtime.dispatch.executive_summary_pa as pa

    assert pa.SRFS_STYLE_ONESHOT_MARKER not in content
    assert "<srfs_style_only_oneshot" not in content


def test_srfs_lane_surgical_density_repair_single_pass_only():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    src = Path(lane.__file__).read_text(encoding="utf-8")
    assert "SRFS SURGICAL DENSITY REPAIR" in src
    assert "8-18 words" in src
    assert "93-94" in src
    assert "22 words" in src
    assert "sixth sentence" in src.lower()
    assert "five-part" in src.lower()
    assert "Sentences 2, 3, or 5" in src
    assert "do not expand Sentence 4" in src
    assert "claim_ledger" in src and "source_fact_id" in src
    assert "repair_messages2" not in src
    assert "result2 = call_qwen" not in src
    assert "do not shorten" in src.lower()
    assert "verbatim" in src.lower()
    assert "double underscore" in src.lower()


def test_offline_qwen_stub_classifies_as_plumbing_not_product_proof():
    from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
    from apps_rg.runtime.section_proof.mock_runtime_proof_policy import infer_product_quality_blocked_or_mock

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
    assert "Internally compare at least two supported repair options" in src
    assert "jd_used_as_proof=false" in src
    assert "4 or 5" in src.lower()
    assert "north_star_style_example_echo_unsupported" in src
    assert "ip-led revenue" in src.lower() and "productized ai revenue" in src.lower()


def test_dispatch_parser_default_provider_is_mock_with_qwen_opt_in():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_parser

    p = build_parser()
    ns = p.parse_args([])
    assert ns.provider == "mock"
    assert p.parse_args(["--provider", "qwen_vllm"]).provider == "qwen_vllm"
    # run_dispatch uses sha256(JSON(messages))[:16] as prompt_hash (see executive_summary_dispatch).
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
    gold = next(e for e in data["examples"] if e["id"] == "exec_summary_gold_base_resume_001")
    assert gold["category"] == "positive_gold"
    assert gold["authority"] == "E0_STYLE_EXAMPLE_NOT_PROOF"
    assert "weak" not in gold["annotation"].lower()
    assert "exec_summary_pos_001" not in ids
