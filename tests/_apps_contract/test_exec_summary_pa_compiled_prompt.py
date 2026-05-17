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
    assert "SELECTED_FACT_PLAN" in content
    assert "NOT PROOF" in content
    assert "JD_TEXT (targeting only" in content and "NOT PROOF" in content
    assert "TARGET_TITLE (positioning only" in content
    cl = content.lower()
    assert "sentence role" in cl
    assert "fixed sentence count" in cl or "no fixed sentence" in cl
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


def test_no_hard_sentence_count_phrases_in_exec_summary_prompt_sources():
    """No mandate for exactly two sentences or a fixed 4-to-5 sentence target."""
    yaml_text = _TEMPLATE.read_text(encoding="utf-8")
    import apps_rg.runtime.dispatch.executive_summary_pa as pa
    import apps_rg.runtime.dispatch.executive_summary_dispatch as disp

    pa_src = Path(pa.__file__).read_text(encoding="utf-8")
    disp_src = Path(disp.__file__).read_text(encoding="utf-8")
    for label, raw in (("yaml", yaml_text), ("pa", pa_src), ("dispatch", disp_src)):
        assert "exactly TWO synthesized" not in raw, label
        assert not re.search(r"\b4\s*to\s*5\b", raw, re.IGNORECASE), label
        assert re.search(r"sentence role", raw, re.IGNORECASE), label


def test_template_yaml_excludes_two_sentence_mandate_and_em_dash():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "exactly TWO synthesized" not in raw
    assert "\u2014" not in raw


def test_template_includes_many_shot_examples_and_deliberation_guards():
    raw = _TEMPLATE.read_text(encoding="utf-8")
    assert "<many_shot_examples>" in raw
    assert raw.count("<positive_example ") >= 3
    assert raw.count("<negative_example ") >= 3
    assert raw.count("<transformation_example ") >= 2
    assert "<internal_deliberation_controls>" in raw
    assert "chain-of-thought" in raw.lower() or "chain of thought" in raw.lower()
    assert "Do **not** output chain-of-thought" in raw or "not output chain-of-thought" in raw
    assert "<self_check_requirements>" in raw
    assert "sentence_roles_omitted_with_reason" in raw
    assert "jd_used_as_proof_false" in raw


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


def test_pa_module_strings_exclude_em_dash():
    import apps_rg.runtime.dispatch.executive_summary_pa as pa

    src = Path(pa.__file__).read_text(encoding="utf-8")
    assert "\u2014" not in src


def test_dispatch_repair_prompt_uses_sentence_roles_not_fixed_count():
    import apps_rg.runtime.dispatch.executive_summary_dispatch as disp

    src = Path(disp.__file__).read_text(encoding="utf-8")
    assert "exactly TWO synthesized" not in src
    assert "Internally compare at least two supported repair options" in src
    assert "jd_used_as_proof=false" in src
    assert not re.search(r"\b4\s*to\s*5\b", src, re.IGNORECASE)


def test_dispatch_parser_default_provider_is_real_shaped_qwen():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_parser

    p = build_parser()
    ns = p.parse_args([])
    assert ns.provider == "qwen_vllm"
    """``run_dispatch`` uses sha256(JSON(messages))[:16] as prompt_hash (see executive_summary_dispatch)."""
    payload = _minimal_payload(run_id="hash_run")
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    messages = out.artifact.messages
    compiled = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    h = _sha16(compiled)
    assert len(h) == 16
    assert "<!-- SLOT:" in compiled


def test_template_yaml_exists_under_repo_apps_rg():
    assert _TEMPLATE.is_file(), f"Missing template: {_TEMPLATE}"
