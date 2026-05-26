"""Static audit: C0.1–C0.7 + graph-skills spine wiring for all apps_rg sections."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.section_graph_skills_proof_pool import GRAPH_SKILLS_AUTHORITY_SECTIONS
from apps_rg.runtime.spine import apps_rg_spine_run

LANE_FILES: dict[str, str] = {
    "headline": "apps_rg/runtime/sections/headline_lane.py",
    "executive_summary": "apps_rg/runtime/sections/executive_summary_lane.py",
    "unify_bullets": "apps_rg/runtime/sections/unify_bullets_lane.py",
    "unify_narrative": "apps_rg/runtime/sections/unify_narrative_lane.py",
    "ibm_bullets": "apps_rg/runtime/sections/ibm_bullets_lane.py",
    "ibm_narrative": "apps_rg/runtime/sections/ibm_narrative_lane_execution.py",
    "competencies": "apps_rg/runtime/sections/competencies_lane_execution.py",
}

C0_PHASES: dict[str, tuple[str, ...]] = {
    "C0.1": ("l0_binding", "l1_binding", "L1PlanContract", "grounding_required"),
    "C0.2": ("_perform_bounded_section_retrieval", "dense_search_refs", "G_C02_DENSE"),
    "C0.3": ("_resolve_spine_graph_expansion_refs", "maybe_run_graph_rag"),
    "C0.4": ("merge_dense_sparse_rrf", "_merge_section_dense_sparse"),
    "C0.5": ("FinalEvidenceContract", "canonical_c0_5"),
    "C0.6": ("_compute_support_status", "STOP_AS_EVIDENCE_GAP"),
    "C0.7": ("_emit_retrieval_quality_span", "emit_spine_span_event"),
}


def main() -> int:
    c0_binding = (REPO / "apps_rg/runtime/bindings/c0_binding.py").read_text(encoding="utf-8")
    section_c0 = (REPO / "apps_rg/runtime/spine/section_c0_retrieve.py").read_text(encoding="utf-8")
    c0_compose = (REPO / "apps_rg/runtime/spine/c0_fec_compose.py").read_text(encoding="utf-8")
    canonical = (REPO / "apps_rg/runtime/orchestration/canonical_dispatch.py").read_text(encoding="utf-8")
    modular_steps = (REPO / "apps_rg/l2_recipe/steps.py").read_text(encoding="utf-8")
    spine_run = (REPO / "apps_rg/runtime/spine/apps_rg_spine_run.py").read_text(encoding="utf-8")

    phase_hits: dict[str, list[str]] = {}
    for phase, needles in C0_PHASES.items():
        hits: list[str] = []
        for name, text in (
            ("c0_binding", c0_binding),
            ("section_c0_retrieve", section_c0),
            ("c0_fec_compose", c0_compose),
        ):
            if any(n in text for n in needles):
                hits.append(name)
        phase_hits[phase] = hits

    lane_wire: dict[str, dict[str, object]] = {}
    for lane, rel in LANE_FILES.items():
        txt = (REPO / rel).read_text(encoding="utf-8")
        lane_wire[lane] = {
            "file": rel,
            "wire_spine_c0_fec": "wire_spine_c0_fec_for_section" in txt,
        }

    runners = set(apps_rg_spine_run._SECTION_RUNNERS.keys())
    generated = set(GENERATED_LANES)
    graph_sections = set(GRAPH_SKILLS_AUTHORITY_SECTIONS)
    section_keys = set(SECTION_KEYS)
    sets_equal = runners == generated == graph_sections == section_keys
    all_wire = all(bool(lane_wire[l]["wire_spine_c0_fec"]) for l in GENERATED_LANES)
    phases_ok = all(phase_hits[p] for p in C0_PHASES)

    from apps_rg.runtime.spine.graph_skills_fec_set_equality import audit_all_d7_lanes

    d7 = audit_all_d7_lanes(repo_root=REPO)

    full_resume = {
        "canonical_dispatch_integrated_spine": "run_integrated_single_action_spine"
        in canonical,
        "modular_section_lanes": "modular_section_lanes" in modular_steps,
        "spine_scope_full": 'scope == "full"' in spine_run,
    }

    status = (
        "PASS"
        if all_wire and sets_equal and phases_ok and d7.get("d7_all_pass")
        else "FAIL"
    )
    out = {
        "status": status,
        "lane_registry_equal": sets_equal,
        "all_lanes_wire_spine_c0": all_wire,
        "lane_wire": lane_wire,
        "c0_phase_code_hits": phase_hits,
        "full_resume_path": full_resume,
        "d7_graph_skills_fec_equality": {
            "status": d7.get("status"),
            "pass_count": d7.get("d7_pass_count"),
            "target": d7.get("d7_target_count"),
        },
    }
    report = REPO / "docs/reports/apps_rg/c01_c07_graph_skills_apps_rg_audit.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
