"""IBM narrative: PA compile via section_prompt_adapter (W7 mechanical).

Section-specific instructions are sourced from ``ibm_position_narrative_v1.yaml`` (design SSOT).
Generic shell slots remain ``strategic_tailor_v1`` via ``w7_strategic_tailor_shell_slots.yaml``.

W11-M4B SSOT: apps_rg.runtime.sections.ibm_narrative_pa."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    NARRATIVE_R0,
    jd_non_proof_block,
    load_w7_shell_slot_bodies,
)

_SPEC_PATH = (
    Path(__file__).resolve().parent.parent.parent / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
)
_SPEC_DOC: dict[str, Any] | None = None
_SPEC_PATH_MTIME: float | None = None


def _ibm_position_narrative_spec() -> dict[str, Any]:
    """Load spec from disk (reload when template file changes — pytest / dev iteration)."""
    global _SPEC_DOC, _SPEC_PATH_MTIME
    mtime = _SPEC_PATH.stat().st_mtime
    if _SPEC_DOC is None or _SPEC_PATH_MTIME != mtime:
        with _SPEC_PATH.open(encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
        _SPEC_DOC = loaded if isinstance(loaded, dict) else {}
        _SPEC_PATH_MTIME = mtime
    return _SPEC_DOC


def _fact_lines(runtime_payload: dict[str, Any]) -> str:
    facts = runtime_payload["selected_fact_plan"]["facts"]
    return "\n".join(
        f"- {fact['fact_id']}: {fact['claim_text']}"
        + (f" | metric: {fact['metric_raw']}" if fact.get("metric_raw") else "")
        for fact in facts
    )


def _format_allowed_fact_ids(runtime_payload: dict[str, Any]) -> str:
    ids = list(runtime_payload.get("allowed_fact_ids") or [])
    lines = "\n".join(f"- {fid}" for fid in ids)
    return (
        "ALLOWED_SOURCE_FACT_IDS (deterministic gate surface; every token in claim_ledger[].source_fact_ids "
        "MUST be copied exactly from this list — no invented IDs):\n"
        f"{lines}\n"
    )


def _yaml_instruction_layers(spec: dict[str, Any]) -> str:
    chunks: list[str] = []
    purpose = str(spec.get("purpose") or "").strip()
    if purpose:
        chunks.append(purpose)
    oath = str(spec.get("sovereign_oath") or "").strip()
    if oath:
        chunks.append(oath)

    ns = spec.get("north_star_semantic_contract")
    if isinstance(ns, str) and ns.strip():
        chunks.append("IBM NARRATIVE NORTH STAR (STYLE TARGET — PARAPHRASE ALLOWED):\n" + ns.strip())

    cc = spec.get("claim_ledger_coverage_contract")
    if isinstance(cc, str) and cc.strip():
        chunks.append("CLAIM_LEDGER THEME COVERAGE (DETERMINISTIC X2 GATE):\n" + cc.strip())

    sah = spec.get("source_authority_hierarchy")
    if isinstance(sah, dict):
        lines = ["SOURCE AUTHORITY (proof vs targeting):"]
        ps = sah.get("proof_sources")
        if isinstance(ps, list):
            lines.append("Proof sources: " + "; ".join(str(x) for x in ps))
        tc = sah.get("targeting_context_only")
        if isinstance(tc, list):
            lines.append("Targeting context only: " + ", ".join(str(x) for x in tc))
        ar = sah.get("authority_rules")
        if isinstance(ar, list):
            lines.append("Rules: " + " | ".join(str(x) for x in ar))
        chunks.append("\n".join(lines))

    ng = spec.get("narrative_complement_guidance")
    if isinstance(ng, dict):
        np = str(ng.get("purpose") or "").strip()
        if np:
            chunks.append(np)
        angles = ng.get("angle_options") or []
        if isinstance(angles, list) and angles:
            chunks.append("ANGLE OPTIONS:\n" + "\n".join(f"- {a}" for a in angles))
        avoid = ng.get("avoid") or []
        if isinstance(avoid, list) and avoid:
            chunks.append("AVOID:\n" + "\n".join(f"- {a}" for a in avoid))
        examples = ng.get("example_anti_patterns") or []
        if isinstance(examples, list) and examples:
            chunks.append(
                "EXAMPLE ANTI-PATTERNS:\n"
                + "\n".join(str(x) for x in examples if str(x).strip())
            )

    pe = spec.get("prompt_engineering_hardening")
    if isinstance(pe, dict):
        proc = pe.get("private_process")
        if isinstance(proc, list) and proc:
            chunks.append(
                "GENERATION DISCIPLINE (private; do not echo as instructions in JSON fields):\n"
                + "\n".join(f"- {str(p).strip()}" for p in proc if str(p).strip())
            )

    mh = spec.get("metric_handling_rules")
    if isinstance(mh, dict):
        lines: list[str] = ["METRIC HANDLING (from IBM narrative spec):"]
        dp = mh.get("default_policy")
        if isinstance(dp, str) and dp.strip():
            lines.append(f"DEFAULT POLICY: {dp.strip()}")
        fb = mh.get("from_bullets")
        if isinstance(fb, list):
            for row in fb:
                if isinstance(row, dict):
                    lines.append(f"- {row}")
        cra = mh.get("conceptual_references_allowed")
        if isinstance(cra, list):
            lines.append("CONCEPTUAL REFERENCES ALLOWED:")
            for item in cra:
                lines.append(f"  - {item}")
        chunks.append("\n".join(lines))

    ft = spec.get("forbidden_terms_in_narrative")
    if isinstance(ft, list) and ft:
        chunks.append(
            "FORBIDDEN TERMS (narrative):\n"
            + "\n".join(
                f"- {item.get('term', item)}" if isinstance(item, dict) else f"- {item}"
                for item in ft
            )
        )

    fp = spec.get("forbidden_patterns")
    if isinstance(fp, list) and fp:
        chunks.append(
            "FORBIDDEN PATTERNS:\n"
            + "\n".join(
                (
                    f"- {entry.get('pattern')}: {entry.get('action')}"
                    if isinstance(entry, dict)
                    else f"- {entry}"
                )
                for entry in fp
            )
        )

    return "\n\n".join(c for c in chunks if c.strip())


def _i0_from_spec(runtime_payload: dict[str, Any]) -> str:
    spec = _ibm_position_narrative_spec()
    header = runtime_payload["ibm_header"]
    layers = _yaml_instruction_layers(spec)
    mechanical = (
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "OUTPUT MECHANICS:\n"
        "- Return RAW JSON only: first character {, last character }. No markdown fences.\n"
        "- Required JSON keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, "
        "gap_notes, change_log, self_check.\n"
        "- narrative_sentence: exactly one sentence; third person or implied subject; include the employer anchor "
        "\"IBM\" once; no em dash; no inline source tags; preferred 34–48 words, hard max 58 words.\n"
        "- claim_ledger: rows {claim_text, source_fact_ids}; claim_text non-empty after trim; "
        "source_fact_ids non-empty, ALLOWED_SOURCE_FACT_IDS only; each material theme needs matching bul_ibm_* "
        "(see claim_ledger_coverage_contract in spec).\n"
        "- Proof/targeting: pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml).\n"
        "- JD and briefing are targeting context only — never treated as résumé proof.\n"
        "- When ACCEPTED_IBM_BULLETS companion context exists (U-tier): write narrative_sentence as the capstone "
        "after that tailoring — align strategically, never contradict, never paste companion lines.\n"
        "- gap_notes, change_log, self_check, claim_ledger text fields MUST avoid plumbing/test scaffolding "
        "phrases such as mocked_runtime_slice, 'provider not requested', mock_fallback, mocked_judge, "
        "\"plumbing only\", plumbing_only, or test-only (deterministic gates reject).\n\n"
        "IDENTITY (mandatory):\n"
        "- Do not include the candidate's given name, surname, initials, or full name — the résumé header "
        "already identifies them.\n"
        "- Use implied subject or role-first framing without naming the person.\n\n"
        "SCOPE:\n"
        "- Proof binds strictly to IBM employment facts corresponding to bul_ibm_* IDs from ALLOWED_SOURCE_FACT_IDS.\n"
        "- No Unify / InsurTech / EY / education / certification / early-career facts.\n\n"
        f"READ-ONLY EMPLOYMENT CONTEXT (not copy-paste openers): employer={header['employer']}, "
        f"title={header['title']}, location={header['location']}, dates={header['start_date']} to "
        f"{header['end_date']}.\n\n"
        f"{_format_allowed_fact_ids(runtime_payload)}\n"
        f"{layers}"
    )
    return mechanical.strip()


def _u0(companion_nonempty: bool) -> str:
    closing = (
        "Write exactly one narrative_sentence: polished SVP-level executive prose, third person or implied subject, "
        "IBM as employer anchor once, one period, preferred 34–48 words and hard max 58 words. "
        "When ACCEPTED_IBM_BULLETS companion lines include the standard IBM KPI set ($15M, 99.9%, 30%, 25%, 50%), "
        "do not restate those digits or percentages in narrative_sentence — use conceptual language only."
    )
    if companion_nonempty:
        return closing
    return "(No companion ibm_bullets artifact; still avoid repeating every metric in one list.)\n\n" + closing


def compile_ibm_narrative_prompt(
    runtime_payload: dict[str, Any],
    companion_text: str,
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    fact_lines = _fact_lines(runtime_payload)
    companion_nonempty = bool(companion_text.strip())
    tier = (
        f"ACCEPTED_IBM_BULLETS (read-only; do not recap each line):\n{companion_text.strip()}"
        if companion_nonempty
        else None
    )
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"ibm_narrative:{run_id}",
        s0_system_preamble=slots["S0"],
        d0_fences=slots["D0"],
        e0_examples=slots["E0"],
        y0_style_preferences=slots["Y0"],
        i0_instructions=_i0_from_spec(runtime_payload),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content="CANONICAL IBM FACTS:\n" + fact_lines,
            confidence=1.0,
            source_tag="candidate_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_non_proof_block(runtime_payload),
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=_u0(companion_nonempty),
        r0_response_schema=NARRATIVE_R0,
        render_context={
            "section_id": "ibm_narrative",
            "target_title": str(runtime_payload.get("target_title") or ""),
            "target_company": str(runtime_payload.get("target_company") or ""),
            "apps_rg_prompt_spec_ref": "apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml",
        },
    )
    compiled = compile_section_prompt(assembly, section_id="ibm_narrative", companion_u_tier=tier)
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_ibm_narrative_prompt"]
