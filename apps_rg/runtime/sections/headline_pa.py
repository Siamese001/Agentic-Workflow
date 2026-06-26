"""Headline: PromptAssemblyInput from headline_tailor_v1.yaml + section_prompt_adapter (W6).

C0 carries canonical employment bullets, forbidden employer names, and selected_fact_plan stub.
JD/title/company/briefing are non-proof in ``c0_jd_requirements`` (targeting / prioritization only;
must not keyword-stuff). Companion lanes are U-tier only.
Compile failures propagate (no silent inline fallback).

W11-M4B SSOT: apps_rg.runtime.sections.headline_pa."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import (
    augment_section_compiled_with_input_authority,
    proof_pool_mode_from_metadata,
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "headline_tailor_v1.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError("Cannot resolve repo root from headline_pa.py")


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "headline_tailor_v1.yaml"
)

_HEADLINE_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "headline_line",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "headline_line": {
                "type": "string",
                "description": (
                    "Single line: SVP Engineering | X | Y | Z — exactly three ' | ' separators, "
                    "four segments, 10–13 words, no metrics, no employer or target company names"
                ),
            },
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {
                "type": "array",
                "minItems": 1,
                "description": (
                    "PROOF CRITICAL: array of OBJECT rows only — never a flat list of bul_* strings. "
                    "Each row proves headline_line themes using candidate facts."
                ),
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "additionalProperties": True,
                    "properties": {
                        "claim_text": {"type": "string", "minLength": 1},
                        "source_fact_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "jd_alignment": {
                "type": "object",
                "description": (
                    "Must include targeting_only true, jd_used_as_proof false, briefing_used_as_proof false, "
                    "selected_theme, anti_stuffing_check; JD/briefing are ranking only. "
                    "When U_TIER_COMPANION_CONTEXT in the assembled prompt is non-empty, MUST include "
                    "companion_used_as_proof: false (boolean)."
                ),
                "properties": {
                    "targeting_only": {"type": "boolean"},
                    "jd_used_as_proof": {"type": "boolean"},
                    "briefing_used_as_proof": {"type": "boolean"},
                    "companion_used_as_proof": {"type": "boolean"},
                    "selected_theme": {"type": "string"},
                    "anti_stuffing_check": {"type": "string"},
                },
            },
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {
                "type": "object",
                "description": (
                    "Dispatch-normalized booleans/counts: fixed_prefix, segment_count 4, separator_count 3, "
                    "word_count, word_count_in_range, no_metrics, no_company_names, no_employer_names, "
                    "no_jd_phrase_lift, base_identity_preserved, jd_used_as_targeting_only"
                ),
            },
        },
    },
    sort_keys=True,
)


def load_headline_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def format_narrowing_it_labels_blocklist_block() -> str:
    """Render the narrowing/demoting-label blocklist FROM the X2 SSOT constant.

    W0-E (plan prompt-gate-ssot-consolidation-e7c9a2): ``x2_headline_no_narrowing_it_labels``
    HARD-fails any headline containing a NARROWING_IT_LABELS phrase, but the prompt never
    enumerated them -- the generator could not avoid what it was never shown. Source the block
    directly from ``headline_quality_x2.NARROWING_IT_LABELS`` so prompt and gate cannot drift:
    one constant, rendered into the prompt at compile time.
    """
    from apps_rg.runtime.validators.headline_quality_x2 import NARROWING_IT_LABELS

    labels = ", ".join(f'"{label}"' for label in sorted(NARROWING_IT_LABELS))
    return (
        "\n<narrowing_label_blocklist>\n"
        "FORBIDDEN narrowing/demoting label phrases — the narrowing-label gate HARD-fails any "
        "headline_line that contains one (case-insensitive substring match). They juniorize the SVP "
        "positioning; never use any as (part of) a segment: " + labels + ".\n"
        "</narrowing_label_blocklist>"
    )


def build_headline_assembly_input(
    runtime_payload: dict[str, Any],
    fact_lines: str,
    forbidden_employer_lines: str,
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    companion_context_nonempty: bool = False,
) -> PromptAssemblyInput:
    slots = load_headline_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    stub = json.dumps(
        {
            "section_id": "headline",
            "selection_method": plan.get("selection_method") or "canonical_base_resume_employment_bullets",
            "required_fact_ids": plan.get("required_fact_ids") or [],
        },
        separators=(",", ":"),
        ensure_ascii=False,
    )

    t_title = str(runtime_payload.get("target_title") or "")
    t_company = str(runtime_payload.get("target_company") or "")
    jd = str(runtime_payload.get("jd_text") or "")
    briefing = str(runtime_payload.get("briefing") or "")

    positioning_block = ""
    pp_meta = runtime_payload.get("proof_pool_metadata") if isinstance(runtime_payload.get("proof_pool_metadata"), dict) else {}
    if not pp_meta.get("headline_positioning_bundle_consumption"):
        raise ValueError(
            "headline: proof_pool_metadata missing headline_positioning_bundle_consumption; graph packet is mandatory"
        )
    from apps_rg.runtime.sections.headline_positioning_evidence import (
        format_headline_positioning_evidence_pack,
    )

    positioning_block = (
        "\n\n" + format_headline_positioning_evidence_pack(runtime_payload, section_id="headline") + "\n"
    )

    c0_block = (
        "CANONICAL_EMPLOYMENT_BULLETS (proof only; do not paste verbatim into headline_line):\n"
        + fact_lines.strip()
        + "\n\nFORBIDDEN_EMPLOYER_NAMES (must not appear in headline_line):\n"
        + forbidden_employer_lines.strip()
        + positioning_block
        + "\n\nSELECTED_FACT_PLAN_STUB (output this shape only; do not paste facts[]):\n"
        + stub
    )

    jd_block = (
        f"TARGET_TITLE (NOT PROOF — framing only): {t_title}\n"
        f"TARGET_COMPANY (NOT PROOF): {t_company}\n"
        f"JD_TEXT (ranking/targeting only — NOT PROOF): {jd}\n"
        f"BRIEFING (ranking/targeting only — NOT PROOF): {briefing}\n"
        "Use JD_TEXT and BRIEFING to prioritize which evidenced themes from candidate_facts to foreground. "
        "Do not treat JD_TEXT as a keyword checklist; avoid stuffing JD nouns into segments.\n"
        "These lines may shape emphasis but cannot prove claims."
    )

    u0_parts = [
        "<role>You are writing one executive resume headline for an SVP Engineering candidate: "
        "pick the three strongest fact-supported positioning themes for the target role; express them as SVP Engineering | X | Y | Z.</role>\n",
        "North Star: headline_line MUST be exactly SVP Engineering | X | Y | Z — X/Y/Z are creative executive phrases from the fact ledger, ranked by JD/briefing relevance only (never proof).\n",
        "Headline display policy: X/Y/Z MUST be executive positioning labels backed by grounded proof, not raw vendor/tool architecture. "
        "Prefer abstractions such as Enterprise AI Platforms, Cloud Data Platforms, Runtime Governance Architecture, Partner AI Ecosystems, "
        "Platform Commercialization, and Regulated AI Systems. Vendor/product names such as Databricks, AWS, Snowflake, Anthropic, or OpenAI "
        "belong in source facts/proof; do not use them as standalone headline segments unless the target explicitly requires vendor-specialist positioning "
        "and the segment still contains an executive abstraction.\n",
        "Produce exactly ONE resume headline JSON object per R0 schema.\n",
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n",
        "Anti-copy: do not default-copy examples, identity-reference lines, JD title, JD phrases, briefing phrases, or the base resume headline verbatim — "
        "prefer fresh fact-led wording unless verbatim text is truly best and still compliant.\n",
        "headline_line MUST use exact prefix 'SVP Engineering | ', exactly three ' | ' separators (four non-empty segments), 10–13 words total, ",
        "no metrics, no employer or target company names, no candidate names, no inline source tags, no first person, no em dash.\n",
        "claim_ledger MUST be an array of OBJECT rows with claim_text (non-empty string) and ",
        "source_fact_ids (non-empty string array of bul_* IDs from C0). ",
        "FORBIDDEN: flat arrays of strings such as [\"bul_unify_001\",\"bul_unify_005\"] — invalid for proof.\n",
        "jd_alignment must include jd_used_as_proof: false and briefing_used_as_proof: false (both booleans).\n",
    ]
    if companion_context_nonempty:
        u0_parts.append(
            "Because U_TIER_COMPANION_CONTEXT is included below (non-empty), jd_alignment MUST also include "
            "companion_used_as_proof: false exactly — boolean false, never true; omitting this key is invalid.\n"
        )
    u0_parts.append(
        "self_check counts MUST match deterministic headline_line metrics: strip headline_line; replace every '|' "
        "with one ASCII space; split on whitespace; word_count = token count (pipes are not tokens). "
        "Then fill segment_count=4, separator_count=3, word_count from headline_line, "
        "word_count_in_range, booleans per R0.\n"
    )
    u0 = "".join(u0_parts)

    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        s0_system_preamble=slots.get("S0", ""),
        d0_fences=slots.get("D0"),
        i0_instructions=slots.get("I0", "") + format_narrowing_it_labels_blocklist_block(),
        e0_examples=slots.get("E0"),
        y0_style_preferences=slots.get("Y0"),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content=c0_block,
            confidence=1.0,
            source_tag="candidate_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_block,
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=u0,
        r0_response_schema=_HEADLINE_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "headline",
        },
    )


def compile_headline_prompt(
    runtime_payload: dict[str, Any],
    *,
    companion_context: str,
    fact_lines: str,
    forbidden_employer_lines: str,
    run_id: str,
) -> SectionCompiledPrompt:
    from apps_rg.runtime.spine.c0_fec_compose import resolve_pa_proof_authority_for_compile

    assembly = build_headline_assembly_input(
        runtime_payload,
        fact_lines,
        forbidden_employer_lines,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"headline:{run_id}",
        companion_context_nonempty=bool(companion_context.strip()),
    )
    tier = companion_context.strip() or None
    compiled = compile_section_prompt(
        assembly,
        section_id="headline",
        companion_u_tier=tier,
    )
    ids = sorted(str(x) for x in (runtime_payload.get("allowed_fact_ids") or []))
    pp_meta, _fec = resolve_pa_proof_authority_for_compile(runtime_payload)
    proof_pool_mode_from_metadata(pp_meta)
    return augment_section_compiled_with_input_authority(
        compiled,
        allowed_source_fact_ids=ids,
        skills_authority_metadata=pp_meta,
        runtime_payload=runtime_payload,
    )


__all__ = [
    "build_headline_assembly_input",
    "compile_headline_prompt",
    "load_headline_template_slots",
]
