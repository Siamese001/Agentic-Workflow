"""W4: executive_summary prompt is PA-compiled via section_prompt_adapter (indirect: executive_summary_pa)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt

REPO_ROOT = Path(__file__).resolve().parents[2]


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
            ]
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
    assert "TARGET_ROLE_CONTEXT (NOT PROOF):" in content
    assert "resume_display_text must be clean prose" in content or "NO [source:" in content


def test_dispatch_canonical_json_hash_is_stable_for_messages():
    """``run_dispatch`` uses sha256(JSON(messages))[:16] as prompt_hash (see executive_summary_dispatch)."""
    payload = _minimal_payload(run_id="hash_run")
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    messages = out.artifact.messages
    compiled = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    h = _sha16(compiled)
    assert len(h) == 16
    assert "<!-- SLOT:" in compiled


def test_template_yaml_exists_under_repo_apps_rg():
    path = (
        REPO_ROOT
        / "apps_rg"
        / "prompt_assembly"
        / "templates"
        / "executive_summary.generate_scratch_v1.yaml"
    )
    assert path.is_file(), f"Missing template: {path}"
