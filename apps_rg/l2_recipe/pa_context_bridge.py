"""Bridge L2 recipe context dict → PromptAssemblyInput for PA compilation.

``GenerateResumeStep`` historically passed the raw context mapping into
``compile_prompt``, which expects a ``PromptAssemblyInput`` dataclass.
This module constructs that input from resolver-provided fields plus
template slot bodies from ``prompt_registry.yaml`` / ``templates/*.yaml``.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from apps_rg.prompt_assembly.compiler import PromptCompiler
from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput

_FLOW_ROUTE_TO_TEMPLATE_ID: dict[str, str] = {
    "tailor_existing": "tailor_existing_v1",
    "strategic_tailor": "strategic_tailor_v1",
    "generate_scratch": "generate_scratch_v1",
    "keyword_match": "tailor_existing_v1",
    "enhance_current": "enhance_current_v1",
}


def _render_slot_bodies(raw: str, vars_: dict[str, str]) -> str:
    """Minimal substitution for Jinja-style placeholders used in slot YAML."""
    if not raw:
        return raw
    out = raw.replace("{{ target_role }}", vars_.get("target_role", ""))
    out = out.replace("{{ target_company }}", vars_.get("target_company", ""))
    out = out.replace("{{ seniority_band }}", vars_.get("seniority_band", ""))
    out = out.replace(
        '{{ length_preference | default("match_existing") }}',
        vars_.get("length_preference", "match_existing"),
    )
    return out


def build_prompt_assembly_input_from_l2_context(context: dict[str, Any]) -> PromptAssemblyInput:
    """Materialize ``PromptAssemblyInput`` for ``compile_prompt`` from recipe context."""
    flow_route = str(context.get("flow_route") or "tailor_existing").strip()
    template_id = _FLOW_ROUTE_TO_TEMPLATE_ID.get(flow_route, "tailor_existing_v1")

    tc = str(context.get("target_company") or "")
    tr = str(context.get("target_role") or "")
    sb = str(context.get("seniority_band") or "")
    lp = str(context.get("length_preference") or "match_existing")
    render_vars = {
        "target_company": tc,
        "target_role": tr,
        "seniority_band": sb,
        "length_preference": lp,
    }

    compiler = PromptCompiler()
    template_def = compiler.resolve_template(template_id)
    template_path = str(template_def.get("path") or "")
    template_yaml = compiler.load_template_file(template_path)
    bodies = template_yaml.get("slot_bodies") or {}

    s0 = _render_slot_bodies(str(bodies.get("S0") or ""), render_vars)
    d0 = _render_slot_bodies(str(bodies.get("D0") or ""), render_vars)
    i0 = _render_slot_bodies(str(bodies.get("I0") or ""), render_vars)
    u0 = _render_slot_bodies(str(bodies.get("U0") or ""), render_vars)
    y0 = _render_slot_bodies(str(bodies.get("Y0") or ""), render_vars)
    e0_raw = bodies.get("E0")
    e0 = _render_slot_bodies(str(e0_raw), render_vars) if e0_raw else None

    schema = compiler.load_schema()
    r0_json = json.dumps(schema, sort_keys=True, separators=(",", ":"))

    resume_blob = str(context.get("master_resume_data") or "").strip()
    if not resume_blob:
        resume_blob = (
            "(empty master_resume_data — expected apps_shared/data/master_resume.json "
            "or injected resume payload)"
        )
    jd_blob = str(context.get("jd_data") or "").strip()
    if not jd_blob:
        jd_blob = "(empty jd_data — expected jd_payload / body_text in raw request)"

    cf = EvidenceSource(
        source_type="candidate_facts",
        content=resume_blob,
        confidence=1.0,
        source_tag="candidate_facts",
    )
    jd_ev = EvidenceSource(
        source_type="jd_requirements",
        content=jd_blob,
        confidence=1.0,
        source_tag="jd_requirements",
    )

    company_brief_ev: EvidenceSource | None = None
    mb_path = str(context.get("manual_brief") or "").strip()
    if mb_path:
        p = Path(mb_path)
        if p.is_file():
            try:
                bt = p.read_text(encoding="utf-8")
                if bt.strip():
                    company_brief_ev = EvidenceSource(
                        source_type="company_brief",
                        content=bt,
                        confidence=1.0,
                        source_tag="company_brief",
                    )
            except OSError:
                pass

    rid = str(context.get("request_id") or "").strip() or f"req-{uuid.uuid4().hex[:24]}"
    run_id = str(context.get("run_id") or "").strip() or f"run-{uuid.uuid4().hex[:24]}"
    trace = str(context.get("trace_root") or "").strip() or f"trace-{uuid.uuid4().hex[:24]}"

    return PromptAssemblyInput(
        template_id=template_id,
        request_id=rid,
        run_id=run_id,
        trace_root=trace,
        s0_system_preamble=s0,
        d0_fences=d0,
        i0_instructions=i0,
        e0_examples=e0,
        y0_style_preferences=y0,
        c0_candidate_facts=cf,
        c0_jd_requirements=jd_ev,
        c0_company_brief=company_brief_ev,
        u0_user_task=u0,
        r0_response_schema=r0_json,
        render_context={"target_company": tc, "target_role": tr},
        target_company=tc,
        target_role=tr,
        seniority_band=sb,
    )


__all__ = ["build_prompt_assembly_input_from_l2_context"]
