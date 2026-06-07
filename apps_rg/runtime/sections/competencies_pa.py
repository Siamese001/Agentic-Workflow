"""Competencies: build PromptAssemblyInput from runtime payload + competency_selector_v2.pa_slots (W5).

Loads slot bodies from ``competency_selector_v2.pa_slots.yaml`` (PA-only extract) and compiles via
``section_prompt_adapter``. Narrative SSOT remains ``competency_selector_v2.yaml`` on disk for humans/registry;

**Proof facts** live in **C0 only** (single canonical employment block). JD/title/company/briefing are
non-proof in ``c0_jd_requirements``. Companion lanes are **U-tier only** via ``companion_u_tier``.

Runtime compile failures propagate (no silent inline fallback).

W11-M4B SSOT: apps_rg.runtime.sections.competencies_pa."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.prompt_assembly.e0_examples import resolve_e0_for_section
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "competency_selector_v2.pa_slots.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError(
        "Cannot resolve repo root from competencies_pa.py (competency_selector_v2.pa_slots.yaml not found)"
    )


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "competency_selector_v2.pa_slots.yaml"
)

COMPETENCIES_OUTPUT_SCHEMA: dict[str, Any] = {
        "type": "object",
        "required": [
            "categories",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "excluded_jd_skills",
            "removed_or_rewritten_terms",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "categories": {
                "type": "array",
                "minItems": 6,
                "maxItems": 6,
                "description": (
                    "Executive capability categories: category_id, category_label, "
                    "terms[{text, source_fact_id, source_fact_ids, optional source_skill_ids, support_class}]"
                ),
            },
            "competencies": {
                "type": "array",
                "description": "Legacy mirror of categories[] for transitional consumers",
            },
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {"type": "array"},
            "jd_alignment": {"type": "object"},
            "excluded_jd_skills": {"type": "array"},
            "removed_or_rewritten_terms": {"type": "array"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
        "definitions": {
            "competency_term": {
                "type": "object",
                "required": ["text", "source_fact_id", "source_fact_ids"],
                "properties": {
                    "text": {"type": "string"},
                    "source_fact_id": {"type": "string"},
                    "source_fact_ids": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"},
                        "description": "Non-empty bul_* ids backing the term (primary must be listed)",
                    },
                    "jd_signal_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional JD phrases used only for ranking; not proof",
                    },
                },
            }
        },
}

_COMPETENCIES_OUTPUT_SCHEMA_JSON = json.dumps(COMPETENCIES_OUTPUT_SCHEMA, sort_keys=True)


def load_competencies_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def build_competencies_assembly_input(
    runtime_payload: dict[str, Any],
    fact_lines: str,
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    from apps_rg.fact_inventory.augmented_skills_graph import build_verified_skill_inventory_projection

    from apps_rg.runtime.spine.c0_fec_compose import resolve_pa_proof_authority_for_compile

    slots = load_competencies_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    pp_meta, _fec = resolve_pa_proof_authority_for_compile(runtime_payload)
    allowed_raw = runtime_payload.get("allowed_fact_ids") or []
    allowed_set = {str(x) for x in allowed_raw} if isinstance(allowed_raw, (list, tuple)) else set()
    skill_projection_block = ""
    if pp_meta.get("augmented_skills_graph_present") or pp_meta.get("skills_authority_status") == "PASS":
        try:
            proj = build_verified_skill_inventory_projection(
                section_id="competencies",  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
                allowed_fact_ids=allowed_set,
            )
            skill_projection_block = (
                "\nVERIFIED_SKILL_INVENTORY_PROJECTION (graph-authoritative; not base-resume facts.skills):\n"
                + json.dumps(proj.get("verified_skill_inventory_projection") or {}, ensure_ascii=False)[:4500]
                + "\nprojection_from_graph=true; source_authority=augmented_skills_graph\n"
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
            skill_projection_block = (
                "\nVERIFIED_SKILL_INVENTORY_PROJECTION: BLOCKED — augmented skills graph unavailable\n"
            )
    stub = json.dumps(
        {
            "section_id": plan.get("section_id") or "competencies",
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

    allowed_list = sorted(allowed_set)
    allowed_block = ""
    if allowed_list:
        allowed_block = (
            "\nALLOWED_SOURCE_FACT_IDS (bul_* only — every emitted competency term MUST map here):\n"
            + ", ".join(sorted(allowed_list))
        )

    competency_bundle_block = ""
    if pp_meta.get("competency_capability_bundle_consumption"):
        try:
            from apps_rg.runtime.sections.competency_capability_evidence import (
                format_competency_capability_evidence_pack,
            )

            competency_bundle_block = (
                "\n\n"
                + format_competency_capability_evidence_pack(
                    runtime_payload, section_id="competencies"
                )
                + "\n"
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):  # guardian: allow-default-fallback -- bundle pack optional boundary
            competency_bundle_block = ""

    c0_facts = (
        "CANONICAL_EMPLOYMENT_BULLETS (claim evidence — candidate_fact_ledger slice; NOT skills authority):\n"
        + fact_lines.strip()
        + allowed_block
        + skill_projection_block
        + competency_bundle_block
        + "\n\nSELECTED_FACT_PLAN_STUB (echo this shape in output only; do not paste facts[] array):\n"
        + stub
    )

    jd_block = (
        f"TARGET_TITLE (NOT PROOF): {t_title}\n"
        f"TARGET_COMPANY (NOT PROOF): {t_company}\n"
        f"JD_TEXT (ranking/targeting only — NOT PROOF): {jd}\n"
        f"BRIEFING (NOT PROOF): {briefing}\n"
        "Use the JD and briefing only to prioritize, label, order, and tune emphasis. "
        "Do not use the JD, briefing, title, company, or companion generated sections as proof "
        "for any emitted competency term."
    )

    u0 = (
        "MODE: Competencies graph_10x6 — target-aware, fact-constrained SELECTION and GROUPING.\n"
        "Do NOT seed from locked base-resume competencies or facts.skills rows. Do NOT generate from JD/briefing alone.\n"
        "Rank up to 10 executive capability category candidates using VERIFIED_SKILL_INVENTORY_PROJECTION "
        "(augmented_skills_graph) plus ALLOWED_SOURCE_FACT_IDS; emit exactly 6 highest-scoring categories that pass "
        "graph/fact reality.\n"
        "Build a professional Competencies section by selecting, grouping, and normalizing ONLY supported terms "
        "from graph projection and C0 employment facts.\n"
        "The professional Competencies section must be a scannable executive capability index, "
        "not a narrative impact section.\n"
        "Every emitted competency term must trace to allowed source_fact_ids from C0 candidate facts "
        "(bul_* / fact_*); optional source_skill_ids must be graph-backed.\n"
        "- Copy source_fact_id strings EXACTLY from ALLOWED_SOURCE_FACT_IDS / C0 (no typos such as fact_g_overnance_003).\n"
        "- Skill taxonomy phrasing may be informed by VERIFIED_SKILL_INVENTORY_PROJECTION; claim ids remain bul_* / fact_* only.\n\n"
        "DISPLAY PATTERN (resume-facing intent): Category Label: compact phrase, compact phrase, compact phrase\n"
        "Do NOT use full sentences, impact narratives, metrics, or accomplishment prose inside terms.\n\n"
        "Return RAW JSON only: first character {, last character }. No ``` fences.\n\n"
        "OUTPUT CONTRACT (top-level object):\n"
        "- categories: array of exactly 6 executive capability category objects (top-scoring of up to 10 candidates), each with:\n"
        "  - category_id: stable taxonomy id when known\n"
        "  - category_label: crisp professional label (no colon, no newlines, not a sentence; not generic "
        '"Skills" / "Competency 1")\n'
        "  - terms: array of 2 to 6 entries; EACH entry MUST be an object with keys "
        "\"text\" (compact phrase), \"source_fact_id\" (single bul_* primary), "
        "\"source_fact_ids\" (non-empty bul_* array including the primary), "
        "optional \"jd_signal_ids\" (ranking only).\n"
        "    Phrasing: prefer 2–5 words; single-token terms ONLY for resume-grounded technical names, "
        "acronyms, platforms, products, or credentials (for example GraphRAG, AWS, vLLM); "
        "never emit bare generic one-word skills without proof overlap.\n"
        "  - source_fact_ids: non-empty array of bul_* ids backing the category\n"
        "  (Legacy read adapters may mirror categories[] to competencies[] after parse — do not emit competencies as the primary top-level key.)\n"
        "- selected_fact_plan: stub only {section_id, selection_method, required_fact_ids}\n"
        "- claim_ledger: one row per emitted term; claim_text non-empty; source_fact_ids [single bul_*]\n"
        "- jd_alignment must include: targeting_only: true, jd_used_as_proof: false, "
        "briefing_used_as_proof: false, companion_context_used_as_proof: false\n"
        "- excluded_jd_skills, removed_or_rewritten_terms, gap_notes, change_log, self_check\n\n"
        "CORE RULES:\n"
        "- Certifications and credentials are RESERVED for the dedicated CERTIFICATIONS & CREDENTIALS section. "
        "Never emit category labels: Certifications, Credentials, Licenses, Accreditations, or Professional Certifications. "
        "Never relist credential titles as competency terms (e.g. AWS Certified Solutions Architect, FSA). "
        "Express AWS/Databricks as platform skills under Cloud and Data Platforms when needed.\n"
        "- Do not invent tools, platforms, certifications, industries, metrics, or employers.\n"
        "- Do not treat U-tier companion context as proof — tone/positioning only.\n"
        "- No em dash (U+2014). No bullet markers in terms. No inline [source:] tags.\n"
        "- When COMPETENCY_CAPABILITY_EVIDENCE_PACK is present: generate categories organically "
        "from competency capability bundles. Each category must bind to a competency_bundle_id and "
        "its graph_skill_node_ids. Base resume and archive competencies are calibration/provenance only "
        "— never copy or paraphrase their prose. Preserve or exceed the base resume's rigor and "
        "senior executive engineering specificity.\n"
        "- REQUIRED FAMILY COVERAGE: across the 6 categories' terms (collectively), you MUST include "
        "fact-supported vocabulary spanning ALL 7 SVP-Engineering capability families. Do not drop any "
        "family. Use graph/fact-backed terms that name each family's mechanisms:\n"
        "    1. Agentic Platform — agentic / multi-agent orchestration, GraphRAG, agent routing\n"
        "    2. Runtime Governance — runtime policy gates, deterministic guardrails, sandboxed execution\n"
        "    3. Retrieval & Context — retrieval quality, vector / embedding search, context assembly\n"
        "    4. LLMOps & Reliability — evaluation gates, telemetry, observability, monitoring, reliability\n"
        "    5. Distributed Infrastructure — distributed cloud, microservices, Databricks Lakehouse, streaming\n"
        "    6. Productization — platform commercialization, productization, roadmap, go-to-market\n"
        "    7. Engineering Leadership — engineering organization, operating model, team scaling\n"
        "  Each such term must still trace to allowed source_fact_ids (no JD-only / invented coverage). "
        "Families 4 (LLMOps) and 5 (Distributed Infra) are frequently under-covered — explicitly include "
        "fact-supported terms for them (e.g. \"audit-grade observability\", \"evaluation gauntlet design\" "
        "for LLMOps; \"Lakehouse modernization\", \"distributed execution\" for Distributed Infra).\n"
    )

    return PromptAssemblyInput(
        template_id="competency_selector_v2",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        s0_system_preamble=slots.get("S0", ""),
        d0_fences=slots.get("D0"),
        i0_instructions=slots.get("I0", ""),
        e0_examples=resolve_e0_for_section("competencies", slots.get("E0")),
        y0_style_preferences=slots.get("Y0"),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content=c0_facts,
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
        r0_response_schema=_COMPETENCIES_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "competencies",
        },
    )


def compile_competencies_prompt(
    runtime_payload: dict[str, Any],
    *,
    companion_context: str,
    fact_lines: str,
    run_id: str,
) -> SectionCompiledPrompt:
    assembly = build_competencies_assembly_input(
        runtime_payload,
        fact_lines,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"competencies:{run_id}",
    )
    tier = companion_context.strip() or None
    compiled = compile_section_prompt(
        assembly,
        section_id="competencies",
        companion_u_tier=tier,
    )
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = [
    "COMPETENCIES_OUTPUT_SCHEMA",
    "build_competencies_assembly_input",
    "compile_competencies_prompt",
    "load_competencies_template_slots",
]
