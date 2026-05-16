"""W8 ledger-only citation standard — contracts, examples, production templates, X2 surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
_CONTRACTS_DIR = REPO / "apps_rg" / "prompt_assembly" / "section_prompt_contracts"
_TEMPLATES = REPO / "apps_rg" / "prompt_assembly" / "templates"
_EXAMPLES = REPO / "apps_rg" / "prompt_assembly" / "examples"
_RUBRICS = REPO / "apps_rg" / "prompt_assembly" / "rubrics" / "section_quality_rubrics.yaml"
_SCHEMA_PATH = _CONTRACTS_DIR / "section_prompt_contract.schema.json"


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _contract_paths() -> list[Path]:
    return sorted(_CONTRACTS_DIR.glob("*.contract.yaml"))


def test_section_prompt_contract_schema_requires_ledger_flags() -> None:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert "claim_ledger_required" in required
    assert "display_text_source_tags_allowed" in required
    assert "jd_as_proof_allowed" in required


@pytest.mark.parametrize("contract_path", _contract_paths(), ids=lambda p: p.name)
def test_each_section_contract_ledger_only_flags(contract_path: Path) -> None:
    data = _load_yaml(contract_path)
    sid = data.get("section_id", contract_path.stem)
    assert data.get("claim_ledger_required") is True, sid
    assert data.get("display_text_source_tags_allowed") is False, sid
    assert data.get("jd_as_proof_allowed") is False, sid
    notes = (data.get("notes") or "").lower()
    assert "ledger-only" in notes or "w8" in notes, f"{sid} missing W8 citation notes"


def test_examples_positive_repair_slices_have_no_inline_source_tags() -> None:
    for name in ("competencies_examples.yaml", "unify_examples.yaml"):
        doc = _load_yaml(_EXAMPLES / name)
        for ex in doc.get("examples", []):
            cat = (ex.get("category") or "").lower()
            if cat == "negative":
                continue
            for key in ("after", "before"):
                blob = ex.get(key)
                if not blob or not isinstance(blob, str):
                    continue
                assert "[source:" not in blob.lower(), (name, ex.get("id"), key)


def test_section_quality_rubric_prefers_ledger_over_inline_tags() -> None:
    text = _RUBRICS.read_text(encoding="utf-8").lower()
    assert "claim_ledger" in text
    assert "no requirement that prose repeats inline" in text or "omits inline" in text


# Instruction substrings that historically pushed inline [source: …] into resume display.
_BAD_INLINE_SOURCE_MANDATES = (
    "end each bullet with [source:",
    "every proof point must carry [source:",
    "at least 1 [source:",
    "preserve all [source:",
    "max 2 proof points with [source:",
)


def _production_template_paths() -> list[Path]:
    paths: set[Path] = set()
    for p in _contract_paths():
        data = _load_yaml(p)
        ref = data.get("apps_rg_prompt_template_ref") or ""
        if "LOCKED" in ref:
            continue
        paths.add((REPO / ref).resolve())
    paths.add((_TEMPLATES / "strategic_tailor_v1.yaml").resolve())
    paths.add((_TEMPLATES / "competency_selector_v2.pa_slots.yaml").resolve())
    missing = [p for p in paths if not p.is_file()]
    assert not missing, f"missing templates: {missing}"
    return sorted(paths)


@pytest.mark.parametrize("template_path", _production_template_paths(), ids=lambda p: str(p.relative_to(REPO)))
def test_production_templates_do_not_mandate_inline_source_tags(template_path: Path) -> None:
    body = template_path.read_text(encoding="utf-8").lower()
    for phrase in _BAD_INLINE_SOURCE_MANDATES:
        assert phrase not in body, (template_path.name, phrase)


def test_generated_section_x2_modules_define_inline_source_blocking() -> None:
    x2_paths = {
        "headline": REPO / "apps_rg/runtime/validators/headline_x2.py",
        "executive_summary": REPO / "apps_rg/runtime/validators/executive_summary_x2.py",
        "competencies": REPO / "apps_rg/runtime/validators/competencies_x2.py",
        "unify_narrative": REPO / "apps_rg/runtime/validators/unify_narrative_x2.py",
        "unify_bullets": REPO / "apps_rg/runtime/validators/unify_bullets_x2.py",
        "ibm_narrative": REPO / "apps_rg/runtime/validators/ibm_narrative_x2.py",
        "ibm_bullets": REPO / "apps_rg/runtime/validators/ibm_bullets_x2.py",
    }
    for label, path in x2_paths.items():
        text = path.read_text(encoding="utf-8")
        assert "INLINE_SOURCE_PATTERN" in text, label
        assert "inline_source" in text.lower(), label


def test_locked_section_x2_manifest_has_no_display_inline_source_gate_by_design() -> None:
    """DOCX manifest validates packaging — not recruiter-facing LLM display prose."""
    path = REPO / "apps_rg/runtime/render/docx_manifest_x2.py"
    text = path.read_text(encoding="utf-8")
    assert "INLINE_SOURCE_PATTERN" not in text
    assert "x2_docx_manifest" in text
