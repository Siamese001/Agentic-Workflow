"""Prompt ↔ X1D judge rubric lockstep audit for apps_rg generated resume sections.

Ensures PA template / runtime I0 / product-shape blocks teach the same criteria the
X1D judge enforces — complementary to ``section_prompt_drift_audit`` (SSOT shape only)
and ``section_x2_x1d_contract`` (X2 gate vs rubric bounds).
"""

from __future__ import annotations

import importlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.judges.graph_skills_x1d_rubric_contract import (
    FAMILY_MARKER_GROUPS,
    LANE_RUBRIC_MODULES,
    RUBRIC_TEXT_ATTR,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    SectionProductShape,
    format_product_shape_prompt_block,
    section_product_shape,
)
from apps_rg.runtime.sections.section_prompt_drift_audit import (
    _load_contract,
    _template_paths_for_section,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ALIGNMENT_MATRIX = _REPO_ROOT / "artifacts" / "apps_rg" / "prompt_authority" / "x2_x1d_alignment_matrix.json"
_PA_CORE_LAW = _REPO_ROOT / "apps_rg" / "prompt_assembly" / "pa_core_law_v1.yaml"

# Judge dimension id → prompt corpus patterns (OR). Fallback tokenizes unknown ids.
DIMENSION_PROMPT_PATTERNS: dict[str, tuple[str, ...]] = {
    "factual_support": (
        r"source_fact",
        r"claim_ledger",
        r"proof",
        r"unsupported",
        r"ground truth",
        r"allowed fact",
    ),
    "executive_signal": (r"executive", r"SVP", r"synthesis", r"platform", r"governance"),
    "resume_voice": (r"third.?person", r"first.?person", r"resume voice", r"prose"),
    "ats_alignment_without_stuffing": (
        r"keyword",
        r"stuffing",
        r"targeting",
        r"jd.*proof",
        r"JD.*proof",
    ),
    "ats_alignment_without_keyword_stuffing": (
        r"keyword",
        r"stuffing",
        r"targeting",
        r"jd.*proof",
    ),
    "anti_overfit": (r"overfit", r"target company", r"unsupported", r"JD.*proof"),
    "synthesis_quality": (r"synthesis", r"six.?sentence", r"6 sentence", r"thesis", r"arc"),
    "evidence_utilization": (r"evidence", r"utilization", r"unused", r"allowed_fact"),
    "deterministic_alignment": (r"deterministic", r"gate", r"authoritative", r"X2"),
    "fixed_prefix_compliance": (r"SVP Engineering", r"pipe", r"segment"),
    "base_identity_fidelity": (
        r"base resume",
        r"anchor",
        r"authentic",
        r"fact-supported",
        r"fact-grounded",
        r"fact supported",
    ),
    "anti_keyword_stuffing": (r"keyword", r"stuffing", r"laundry list"),
    "JD targeting discipline": (r"targeting", r"JD", r"briefing"),
    "executive_authenticity": (r"executive", r"senior", r"leader"),
    "no_title_inflation": (r"title inflation", r"SVP Engineering", r"prefix"),
    "natural human resume sound": (r"human", r"concise", r"resume"),
    "executive_platform_signal": (r"platform", r"governance", r"operating model", r"engineering scale"),
    "current_role_attention": (r"current", r"Unify", r"strongest", r"present"),
    "bullet_impact_clarity": (r"impact", r"concise", r"bullet"),
    "bullet_line_discipline": (r"bullet", r"one high-impact", r"no narrative"),
    "claim_ledger_grounding": (r"claim_ledger", r"source_fact", r"bul_"),
    "pool_variant_quality": (r"pool", r"self[- ]consistency", r"variant", r"min_selection_score"),
    "jd_briefing_targeting_discipline": (r"targeting", r"jd", r"briefing", r"not proof"),
    "keyword_discipline_without_stuffing": (r"keyword", r"stuffing", r"ATS"),
    "cross_bullet_outcome_diversity": (r"distinct", r"outcome", r"redundan"),
    "employer_scope_purity": (r"cross-employer", r"leakage", r"bul_unify_", r"bul_ibm_"),
    "current_role_unify_platform_signal": (r"Unify", r"current", r"platform"),
    "protected_metric_anchor": (r"bul_unify_006", r"\$22M", r"protected"),
    "mechanism_inventory_cap": (r"mechanism", r"inventory", r"dense"),
    "foundation_enterprise_credibility": (r"enterprise", r"foundation", r"IBM"),
    "ibm_fact_scope_only": (r"bul_ibm_", r"IBM-only", r"scope"),
    "no_unify_runtime_vocabulary": (r"GraphRAG", r"agentic", r"orchestration"),
    "narrative_slot_reservation": (r"narrative", r"capstone", r"complement"),
    "role_fit_targeting": (r"targeting", r"JD", r"briefing", r"role"),
    "rewrite_quality": (r"bullet", r"rewrite", r"quality", r"pool"),
    "bullet_semantic_distribution": (r"distinct", r"outcome", r"redundan", r"semantic"),
    "narrative_complementarity": (r"narrative", r"complement", r"mechanism inventory"),
    "fact_ledger_grounding": (r"claim_ledger", r"source_fact", r"bul_"),
    "executive_brevity": (r"one sentence", r"word", r"brevity", r"58"),
    "coherence": (r"coherence", r"integrated", r"flow"),
    "usefulness": (r"useful", r"outcome", r"value"),
    "clarity": (r"clarity", r"concise", r"readable"),
    "impact_signal": (r"impact", r"outcome", r"measurable"),
    "redundancy": (r"redundan", r"duplicate", r"distinct"),
    "precision": (r"precise", r"specific", r"concise"),
    "readability": (r"readable", r"clarity", r"compact"),
    "seniority_executive_relevance": (r"executive", r"senior", r"SVP"),
    "complementarity": (r"complement", r"executive summary", r"augments"),
    "no_bullet_restatement": (r"bullet", r"restate", r"paste", r"laundry"),
    "category_clarity": (r"category", r"label", r"compact", r"phrase"),
    "executive_summary_quality": (r"executive", r"synthesis", r"quality"),
    "alignment": (r"align", r"companion", r"bullet"),
    "concision": (r"concise", r"word", r"brevity"),
    "executive_presence": (r"executive", r"SVP", r"presence"),
    "jd_fit_signal": (r"JD", r"targeting", r"fit"),
    "cluster_coherence": (r"cluster", r"coherence", r"category"),
    "seniority_signal": (r"senior", r"executive", r"SVP"),
}

# Product-shape required_all patterns → searchable aliases in prompt and judge corpora.
PRODUCT_SHAPE_ALIGNMENT_ALIASES: dict[str, tuple[str, ...]] = {
    "fit_to_evidence": (r"fit_to_evidence", r"fit to evidence", r"allowed fact", r"proof"),
    "jd_used_as_proof": (r"jd_used_as_proof", r"jd.?as.?proof", r"jd-as-proof", r"JD.*proof"),
    "briefing_used_as_proof": (r"briefing_used_as_proof", r"briefing.?as.?proof", r"briefing-as-proof"),
    "companion_used_as_proof": (r"companion_used_as_proof", r"companion.*proof", r"companion.*not proof"),
    "companion_context_used_as_proof": (
        r"companion_context_used_as_proof",
        r"companion.*not proof",
        r"companion.*targeting",
    ),
    "targeting_only": (r"targeting_only", r"targeting only", r"targeting-only", r"targeting only,"),
    "source_fact_ids": (r"source_fact_ids", r"source_fact_id", r"source fact"),
    "pool_path_count": (r"pool_path", r"sc_paths", r"self[- ]consistency"),
    "bul_unify_": (r"bul_unify_", r"bul_unify"),
    "bul_ibm_": (r"bul_ibm_", r"bul_ibm"),
    "8": (r"\b8\b", r"six to eight", r"6-8", r"6 to 8"),
    r"58\s+words": (r"58", r"word", r"word_budget", r"word budget", r"executive_brevity"),
    r"360": (r"360", r"char", r"character"),
    "targeting only": (r"targeting only", r"targeting-only", r"targeting_only", r"not proof"),
    "min_selection_score": (r"min_selection_score", r"score floor", r"pool selector"),
}

# Prompt contract field names → judge-rubric phrasing (prompt must still carry literal/alias).
CONTRACT_FIELD_JUDGE_ALIASES: dict[str, tuple[str, ...]] = {
    "jd_used_as_proof": (r"jd.?as.?proof", r"jd-as-proof", r"JD.*proof", r"jd only"),
    "briefing_used_as_proof": (r"briefing.?as.?proof", r"briefing-as-proof", r"briefing"),
    "companion_used_as_proof": (r"companion", r"briefing", r"targeting"),
    "companion_context_used_as_proof": (r"companion", r"not proof", r"targeting"),
    "targeting_only": (r"targeting", r"not proof", r"emphasis only"),
    "fit_to_evidence": (r"allowed_fact", r"claim_ledger", r"supported", r"proof"),
    "source_fact_ids": (r"source_fact", r"claim_ledger", r"bul_"),
}

# Extra aliases when scanning generation prompts (rubrics use dimension ids).
_PROMPT_MARKER_EXTRA: dict[str, tuple[str, ...]] = {
    "factual_support": ("claim_ledger", "proof", "ground truth", "NO FABRICATION", "source_fact"),
    "jd-as-proof": ("jd as proof", "jd-as-proof", "targeting only", "not proof", "JD"),
    "keyword": ("keyword", "stuffing", "ATS"),
}

# Marker groups that apply only to judge rubrics (output schema), not generation prompts.
_JUDGE_ONLY_MARKER_PREFIXES = ("decisive_failure",)


@dataclass(frozen=True)
class PromptJudgeViolation:
    section_id: str
    kind: str
    detail: str
    path: str = ""


def _lane_family(section_id: str) -> str:
    for family, lane, _mod in LANE_RUBRIC_MODULES:
        if lane == section_id:
            return family
    return section_id


def _alignment_row(section_id: str) -> dict[str, Any]:
    if not _ALIGNMENT_MATRIX.is_file():
        return {}
    data = json.loads(_ALIGNMENT_MATRIX.read_text(encoding="utf-8"))
    for row in data.get("sections") or []:
        if isinstance(row, dict) and row.get("section_id") == section_id:
            return row
    return {}


def _dimension_patterns(dimension_id: str) -> tuple[str, ...]:
    if dimension_id in DIMENSION_PROMPT_PATTERNS:
        return DIMENSION_PROMPT_PATTERNS[dimension_id]
    tokens = [re.escape(t) for t in dimension_id.split("_") if len(t) >= 4]
    return tuple(tokens) if tokens else (re.escape(dimension_id),)


def extract_rubric_dimensions(rubric: str) -> tuple[str, ...]:
    return tuple(re.findall(r"^\s*\d+\.\s*([\w]+):", rubric, flags=re.MULTILINE))


def _load_judge_rubrics(section_id: str) -> tuple[str, ...]:
    texts: list[str] = []
    for _family, lane, mod_path in LANE_RUBRIC_MODULES:
        if lane != section_id:
            continue
        mod = importlib.import_module(mod_path)
        attr = RUBRIC_TEXT_ATTR.get(mod_path, "RUBRIC")
        primary = str(getattr(mod, attr, "") or "").strip()
        if primary:
            texts.append(primary)
        for name in sorted(dir(mod)):
            if name.endswith("_RUBRIC") and name != attr:
                val = getattr(mod, name, None)
                if isinstance(val, str) and val.strip():
                    texts.append(val.strip())
    if section_id == "executive_summary":
        pkt = importlib.import_module("apps_rg.runtime.judges.executive_summary_judge_packet")
        for attr in ("SRFS_GRADE_ONLY_RUBRIC", "GRAPH_ONLY_GRADE_ONLY_RUBRIC", "GRADE_ONLY_INSTRUCTION"):
            val = getattr(pkt, attr, None)
            if isinstance(val, str) and val.strip():
                texts.append(val.strip())
    return tuple(texts)


def _append_pa_runtime_snippet(section_id: str, parts: list[str]) -> None:
    """Include runtime I0 bodies that are not fully duplicated in YAML specs."""
    if section_id == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_pa import _legacy_i0

        parts.append(
            _legacy_i0(
                {
                    "unify_header": {
                        "employer": "Unify Consulting",
                        "title": "SVP Engineering",
                        "location": "Boca Raton, FL",
                        "start_date": "2023-02",
                        "end_date": "present",
                    },
                    "selected_fact_plan": {"facts": [{"fact_id": "bul_unify_001", "claim_text": "x"}]},
                }
            )
        )
    elif section_id == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_bullets_pa import _legacy_i0

        parts.append(
            _legacy_i0(
                {
                    "ibm_header": {
                        "employer": "IBM",
                        "title": "Lead Client Partner",
                        "location": "Edgewater, NJ",
                        "start_date": "2017-04",
                        "end_date": "2022-10",
                    },
                    "selected_fact_plan": {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "x"}]},
                }
            )
        )
    elif section_id == "unify_narrative":
        from apps_rg.runtime.sections.unify_narrative_pa import _legacy_i0

        parts.append(
            _legacy_i0(
                {
                    "unify_header": {
                        "employer": "Unify Consulting",
                        "title": "SVP Engineering",
                        "location": "Boca Raton, FL",
                        "start_date": "2023-02",
                        "end_date": "present",
                    },
                    "finalized_unify_bullets": [{"bullet_text": "Platform scale outcome."}],
                }
            )
        )


def collect_section_prompt_corpus(section_id: str) -> str:
    """Prompt corpus for lockstep — prefers W4 executable authority manifest when available."""
    parts: list[str] = [format_product_shape_prompt_block(section_id)]
    if section_id in GENERATED_LANES:
        from apps_rg.runtime.sections.section_prompt_authority_ssot import (
            collect_executable_prompt_corpus,
        )

        try:
            executable = collect_executable_prompt_corpus(section_id)
        except (KeyError, FileNotFoundError, ValueError):  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
            executable = ""
        if len(executable.strip()) >= 200:
            if _PA_CORE_LAW.is_file():
                parts.append(_PA_CORE_LAW.read_text(encoding="utf-8"))
            parts.append(executable)
            return "\n".join(parts)
    shape = section_product_shape(section_id)
    for path in _template_paths_for_section(shape):
        parts.append(path.read_text(encoding="utf-8"))
    if _PA_CORE_LAW.is_file():
        parts.append(_PA_CORE_LAW.read_text(encoding="utf-8"))
    _append_pa_runtime_snippet(section_id, parts)
    if section_id == "executive_summary":
        tmpl = _REPO_ROOT / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
        if tmpl.is_file():
            parts.append(tmpl.read_text(encoding="utf-8"))
    return "\n".join(parts)


def collect_section_judge_corpus(section_id: str) -> str:
    return "\n\n".join(_load_judge_rubrics(section_id))


def _prompt_marker_groups(lane_family: str) -> tuple[tuple[str, ...], ...]:
    groups = FAMILY_MARKER_GROUPS.get(lane_family, FAMILY_MARKER_GROUPS["executive_summary"])
    return tuple(
        aliases
        for aliases in groups
        if not any(aliases[0].startswith(prefix) for prefix in _JUDGE_ONLY_MARKER_PREFIXES)
    )


def _markers_missing(text: str, *, lane_family: str, for_prompt: bool) -> list[str]:
    lower = text.lower()
    groups = (
        _prompt_marker_groups(lane_family)
        if for_prompt
        else FAMILY_MARKER_GROUPS.get(lane_family, FAMILY_MARKER_GROUPS["executive_summary"])
    )
    missing: list[str] = []
    for idx, aliases in enumerate(groups):
        expanded = list(aliases)
        if for_prompt:
            for alias in aliases:
                expanded.extend(_PROMPT_MARKER_EXTRA.get(alias, ()))
        if not any(alias.lower() in lower for alias in expanded):
            missing.append(f"group_{idx}:{aliases[0]}")
    return missing


def _patterns_missing(text: str, patterns: tuple[str, ...]) -> bool:
    return not any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _product_shape_patterns(pattern: str) -> tuple[str, ...]:
    if pattern in PRODUCT_SHAPE_ALIGNMENT_ALIASES:
        return PRODUCT_SHAPE_ALIGNMENT_ALIASES[pattern]
    # Regex patterns from SSOT (e.g. HEAVY:\s*2) pass through as-is.
    return (pattern,)


def audit_contract_judge_refs(shape: SectionProductShape) -> list[PromptJudgeViolation]:
    out: list[PromptJudgeViolation] = []
    contract = _load_contract(shape.section_id)
    contract_ref = str(contract.get("x1d_judge_profile_ref") or "").strip()
    row = _alignment_row(shape.section_id)
    matrix_ref = str(row.get("x1d_judge_profile_ref") or "").strip()
    if matrix_ref and contract_ref and contract_ref != matrix_ref:
        out.append(
            PromptJudgeViolation(
                shape.section_id,
                "contract_matrix_judge_ref_mismatch",
                f"contract={contract_ref!r} matrix={matrix_ref!r}",
                "section_prompt_contracts",
            )
        )
    expected_mod = None
    for _fam, lane, mod_path in LANE_RUBRIC_MODULES:
        if lane == shape.section_id:
            expected_mod = mod_path.replace(".", "/") + ".py"
            break
    if expected_mod and matrix_ref and matrix_ref != expected_mod:
        out.append(
            PromptJudgeViolation(
                shape.section_id,
                "matrix_lane_rubric_module_mismatch",
                f"matrix={matrix_ref!r} lane_registry={expected_mod!r}",
                str(_ALIGNMENT_MATRIX),
            )
        )
    return out


def audit_section_prompt_judge_alignment(shape: SectionProductShape) -> list[PromptJudgeViolation]:
    violations: list[PromptJudgeViolation] = []
    violations.extend(audit_contract_judge_refs(shape))

    prompt_text = collect_section_prompt_corpus(shape.section_id)
    judge_text = collect_section_judge_corpus(shape.section_id)
    if not judge_text.strip():
        violations.append(
            PromptJudgeViolation(
                shape.section_id,
                "judge_rubric_missing",
                "no X1D rubric text loaded for section",
                "apps_rg/runtime/judges",
            )
        )
        return violations

    family = _lane_family(shape.section_id)
    missing_prompt_markers = _markers_missing(prompt_text, lane_family=family, for_prompt=True)
    if missing_prompt_markers:
        violations.append(
            PromptJudgeViolation(
                shape.section_id,
                "family_marker_missing_prompt",
                f"{family} markers absent in prompt: {missing_prompt_markers}",
                "FAMILY_MARKER_GROUPS",
            )
        )
    missing_judge_markers = _markers_missing(judge_text, lane_family=family, for_prompt=False)
    if missing_judge_markers:
        violations.append(
            PromptJudgeViolation(
                shape.section_id,
                "family_marker_missing_judge",
                f"{family} markers absent in judge: {missing_judge_markers}",
                "FAMILY_MARKER_GROUPS",
            )
        )

    for dim in extract_rubric_dimensions(judge_text):
        patterns = _dimension_patterns(dim)
        if _patterns_missing(prompt_text, patterns):
            violations.append(
                PromptJudgeViolation(
                    shape.section_id,
                    "judge_dimension_missing_in_prompt",
                    f"dimension {dim!r} — no prompt alias match among {patterns}",
                    shape.template_ref,
                )
            )

    for pattern in shape.required_all_text_patterns:
        prompt_aliases = _product_shape_patterns(pattern)
        if _patterns_missing(prompt_text, prompt_aliases):
            violations.append(
                PromptJudgeViolation(
                    shape.section_id,
                    "product_shape_required_missing_in_prompt",
                    f"required_all /{pattern}/ not in prompt corpus (aliases={prompt_aliases})",
                    shape.template_ref,
                )
            )
        judge_aliases = CONTRACT_FIELD_JUDGE_ALIASES.get(pattern, prompt_aliases)
        if _patterns_missing(judge_text, judge_aliases):
            violations.append(
                PromptJudgeViolation(
                    shape.section_id,
                    "product_shape_required_missing_in_judge",
                    f"required_all /{pattern}/ not in judge rubric (aliases={judge_aliases})",
                    "x1d_judge",
                )
            )

    return violations


def audit_all_generated_sections_prompt_judge() -> list[PromptJudgeViolation]:
    out: list[PromptJudgeViolation] = []
    for section_id in GENERATED_LANES:
        out.extend(audit_section_prompt_judge_alignment(section_product_shape(section_id)))
    return out


def assert_all_sections_prompt_judge_lockstep() -> None:
    violations = audit_all_generated_sections_prompt_judge()
    if violations:
        lines = "\n".join(f"  [{v.section_id}:{v.kind}] {v.detail} ({v.path})" for v in violations)
        raise AssertionError(f"prompt/judge alignment drift:\n{lines}")


__all__ = [
    "PromptJudgeViolation",
    "assert_all_sections_prompt_judge_lockstep",
    "audit_all_generated_sections_prompt_judge",
    "audit_section_prompt_judge_alignment",
    "collect_section_judge_corpus",
    "collect_section_prompt_corpus",
    "extract_rubric_dimensions",
]
