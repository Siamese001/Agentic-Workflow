"""Executable prompt authority SSOT — which sources the model actually receives per lane.

Complements ``section_prompt_drift_audit`` (YAML shape patterns) and
``section_prompt_judge_alignment`` (prompt ↔ judge lockstep). W0 minimal manifest;
W4 extends coverage and CI wiring.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape

_APPS_RG_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = _APPS_RG_ROOT.parent

P0_ALIGNMENT_LANES: frozenset[str] = frozenset(
    {
        "executive_summary",
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "unify_narrative",
        "ibm_narrative",
    }
)

PromptSourceKind = str  # yaml_template | yaml_section_spec | legacy_i0 | pa_u0_snippet | w7_shell_slots


def resolve_repo_template_path(ref: str) -> Path:
    """Resolve a repo-relative template ref; reject absolute paths and traversal."""
    normalized = str(ref or "").strip().replace("\\", "/")
    if not normalized:
        raise ValueError("empty template ref")
    if normalized.startswith("/"):
        raise ValueError(f"absolute template ref forbidden: {ref!r}")
    if len(normalized) > 1 and normalized[1] == ":":
        raise ValueError(f"absolute template ref forbidden: {ref!r}")
    parts = [p for p in normalized.split("/") if p not in ("", ".")]
    if ".." in parts:
        raise ValueError(f"path traversal forbidden: {ref!r}")
    resolved = (_REPO_ROOT.joinpath(*parts)).resolve()
    repo_root = _REPO_ROOT.resolve()
    if repo_root not in resolved.parents and resolved != repo_root:
        raise ValueError(f"template ref escapes repo: {ref!r} -> {resolved}")
    return resolved


def _read_repo_ref(ref: str) -> str:
    return resolve_repo_template_path(ref).read_text(encoding="utf-8")


# Minimal stub payloads for runtime I0 snippets (lockstep / authority corpus only).
_LEGACY_I0_STUBS: dict[str, dict[str, Any]] = {
    "unify_bullets": {
        "unify_header": {
            "employer": "Unify Consulting",
            "title": "SVP Engineering",
            "location": "Boca Raton, FL",
            "start_date": "2023-02",
            "end_date": "present",
        },
        "selected_fact_plan": {"facts": [{"fact_id": "bul_unify_001", "claim_text": "x"}]},
    },
    "ibm_bullets": {
        "ibm_header": {
            "employer": "IBM",
            "title": "Lead Client Partner",
            "location": "Edgewater, NJ",
            "start_date": "2017-04",
            "end_date": "2022-10",
        },
        "selected_fact_plan": {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "x"}]},
    },
    "unify_narrative": {
        "unify_header": {
            "employer": "Unify Consulting",
            "title": "SVP Engineering",
            "location": "Boca Raton, FL",
            "start_date": "2023-02",
            "end_date": "present",
        },
        "finalized_unify_bullets": [{"bullet_text": "Platform scale outcome."}],
    },
}

_HEADLINE_STUB: dict[str, Any] = {
    "target_title": "SVP Engineering",
    "target_company": "Example Co",
    "jd_text": "",
    "briefing": "",
    "selected_fact_plan": {
        "section_id": "headline",
        "selection_method": "canonical_base_resume_employment_bullets",
        "required_fact_ids": ["bul_unify_001"],
    },
}

_COMPETENCIES_STUB: dict[str, Any] = {
    "target_title": "SVP Engineering",
    "target_company": "Example Co",
    "jd_text": "",
    "briefing": "",
    "product_visible": False,
    "allowed_fact_ids": ["bul_unify_001"],
    "canonical_final_evidence_contract": {"allowed_fact_ids": ["bul_unify_001"]},
    "proof_pool_metadata": {},
    "selected_fact_plan": {
        "section_id": "competencies",
        "selection_method": "canonical_base_resume_employment_bullets",
        "required_fact_ids": ["bul_unify_001"],
    },
}


def _executable_sources_for_section(section_id: str) -> list[dict[str, str]]:
    shape = section_product_shape(section_id)
    sources: list[dict[str, str]] = [
        {"kind": "yaml_template", "ref": shape.template_ref},
    ]
    if section_id in ("unify_bullets", "ibm_bullets", "unify_narrative"):
        sources.append(
            {
                "kind": "legacy_i0",
                "ref": f"apps_rg.runtime.sections.{section_id}_pa._legacy_i0",
            }
        )
    if section_id in ("unify_bullets", "ibm_bullets", "unify_narrative", "ibm_narrative"):
        sources.append({"kind": "w7_shell_slots", "ref": "apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml"})
    if section_id == "ibm_narrative":
        sources.append(
            {
                "kind": "yaml_section_spec",
                "ref": "apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml",
            }
        )
    if section_id == "executive_summary":
        sources.append(
            {
                "kind": "pa_u0_snippet",
                "ref": "apps_rg.runtime.sections.executive_summary_pa.format_graph_only_quality_guardrails_block",
            }
        )
    if section_id == "competencies":
        sources.append(
            {
                "kind": "pa_u0_snippet",
                "ref": "apps_rg.runtime.sections.competencies_pa.build_competencies_assembly_input",
            }
        )
    if section_id == "headline":
        sources.append(
            {
                "kind": "pa_u0_snippet",
                "ref": "apps_rg.runtime.sections.headline_pa.build_headline_assembly_input",
            }
        )
    return sources


EXECUTABLE_PROMPT_SOURCES: dict[str, list[dict[str, str]]] = {
    section_id: _executable_sources_for_section(section_id) for section_id in GENERATED_LANES
}


def _legacy_i0_corpus(section_id: str) -> str:
    mod = importlib.import_module(f"apps_rg.runtime.sections.{section_id}_pa")
    fn: Callable[[dict[str, Any]], str] = getattr(mod, "_legacy_i0")
    return fn(_LEGACY_I0_STUBS[section_id])


def _executive_summary_extra_corpus() -> str:
    from apps_rg.runtime.sections.executive_summary_pa import format_graph_only_quality_guardrails_block

    parts = [format_graph_only_quality_guardrails_block()]
    scratch = resolve_repo_template_path(
        "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
    )
    if scratch.is_file():
        parts.append(scratch.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _headline_u0_corpus() -> str:
    from apps_rg.runtime.sections.headline_pa import build_headline_assembly_input

    assembly = build_headline_assembly_input(
        _HEADLINE_STUB,
        "- bul_unify_001: platform delivery\n",
        "- ExampleCo\n",
        request_id="authority-corpus",
        run_id="authority-corpus",
        trace_root="headline:authority-corpus",
    )
    return str(assembly.u0_user_task or "")


def _competencies_u0_corpus() -> str:
    from apps_rg.runtime.sections.competencies_pa import build_competencies_assembly_input

    assembly = build_competencies_assembly_input(
        _COMPETENCIES_STUB,
        "- bul_unify_001: platform delivery\n",
        request_id="authority-corpus",
        run_id="authority-corpus",
        trace_root="competencies:authority-corpus",
    )
    return str(assembly.u0_user_task or "")


def collect_executable_prompt_corpus(section_id: str) -> str:
    """Concatenate all sources the runtime actually sends to the model for ``section_id``."""
    if section_id not in GENERATED_LANES:
        raise KeyError(f"unknown generated lane: {section_id}")
    parts: list[str] = []
    for source in EXECUTABLE_PROMPT_SOURCES.get(section_id, ()):
        kind = source.get("kind", "")
        ref = str(source.get("ref", "")).strip()
        if not ref:
            continue
        if kind == "yaml_template" or kind == "yaml_section_spec" or kind == "w7_shell_slots":
            path = resolve_repo_template_path(ref)
            if path.is_file():
                parts.append(path.read_text(encoding="utf-8"))
        elif kind == "legacy_i0":
            parts.append(_legacy_i0_corpus(section_id))
        elif kind == "pa_u0_snippet":
            if section_id == "executive_summary":
                parts.append(_executive_summary_extra_corpus())
            elif section_id == "competencies":
                parts.append(_competencies_u0_corpus())
            elif section_id == "headline":
                parts.append(_headline_u0_corpus())
    return "\n".join(parts)


def assert_p0_lanes_executable_corpus_non_empty() -> None:
    """Smoke: P0 lanes must yield executable prompt text for lockstep alignment."""
    failures: list[str] = []
    for section_id in sorted(P0_ALIGNMENT_LANES):
        corpus = collect_executable_prompt_corpus(section_id)
        if len(corpus.strip()) < 200:
            failures.append(f"{section_id}: executable corpus too short ({len(corpus)} chars)")
    if failures:
        raise AssertionError("; ".join(failures))


def assert_all_generated_lanes_executable_corpus_non_empty(
    *,
    min_chars: int = 200,
) -> None:
    """W4.1 — every ``GENERATED_LANES`` entry must have non-empty executable prompt corpus."""
    failures: list[str] = []
    for section_id in GENERATED_LANES:
        corpus = collect_executable_prompt_corpus(section_id)
        if len(corpus.strip()) < min_chars:
            failures.append(f"{section_id}: executable corpus too short ({len(corpus)} chars)")
        sources = EXECUTABLE_PROMPT_SOURCES.get(section_id) or []
        if not sources:
            failures.append(f"{section_id}: no EXECUTABLE_PROMPT_SOURCES entries")
    if failures:
        raise AssertionError("; ".join(failures))


__all__ = [
    "EXECUTABLE_PROMPT_SOURCES",
    "P0_ALIGNMENT_LANES",
    "assert_all_generated_lanes_executable_corpus_non_empty",
    "assert_p0_lanes_executable_corpus_non_empty",
    "collect_executable_prompt_corpus",
    "resolve_repo_template_path",
]
