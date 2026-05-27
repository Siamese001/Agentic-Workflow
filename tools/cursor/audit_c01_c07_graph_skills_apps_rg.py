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
from apps_rg.runtime.spine.c0_graph_lane_receipt import C0_GRAPH_LANE_RECEIPT_ARTIFACT

LANE_FILES: dict[str, str] = {
    "headline": "apps_rg/runtime/sections/headline_lane.py",
    "executive_summary": "apps_rg/runtime/sections/executive_summary_lane.py",
    "unify_bullets": "apps_rg/runtime/sections/unify_bullets_lane.py",
    "unify_narrative": "apps_rg/runtime/sections/unify_narrative_lane.py",
    "ibm_bullets": "apps_rg/runtime/sections/ibm_bullets_lane.py",
    "ibm_narrative": "apps_rg/runtime/sections/ibm_narrative_lane_execution.py",
    "competencies": "apps_rg/runtime/sections/competencies_lane_execution.py",
}

C0_PHASE_FILES: dict[str, tuple[str, ...]] = {
    "c0_binding": ("apps_rg/runtime/bindings/c0_binding.py",),
    "section_c0_retrieve": ("apps_rg/runtime/spine/section_c0_retrieve.py",),
    "c0_fec_compose": ("apps_rg/runtime/spine/c0_fec_compose.py",),
    "c03_graphrag_bound": ("apps_rg/runtime/c03_graphrag_bound.py",),
    "c03_promotion": ("apps_rg/runtime/c0/c03_promotion_candidates.py",),
    "c03_graph_expansion": ("apps_rg/runtime/c0/c03_graph_expansion.py",),
    "evidence_room": ("apps_rg/runtime/c0/evidence_room.py",),
    "l0_binding": ("apps_rg/runtime/bindings/l0_binding.py",),
    "l1_binding": ("apps_rg/runtime/bindings/l1_binding.py",),
}

C0_PHASES: dict[str, tuple[str, ...]] = {
    "C0.1": ("l0_binding", "l1_binding", "L1PlanContract", "grounding_required"),
    "C0.2": ("_perform_bounded_section_retrieval", "dense_search_refs", "G_C02_DENSE"),
    "C0.3": (
        "_resolve_spine_graph_expansion_refs",
        "maybe_run_graph_rag",
        "expand_c03_graph_bindings",
        "_collect_graph_expansion_refs",
    ),
    "C0.4": (
        "merge_dense_sparse_rrf",
        "_merge_section_dense_sparse",
        "perform_product_hybrid_retrieval",
        "stratify_c04_evidence",
    ),
    "C0.5": ("FinalEvidenceContract", "canonical_c0_5"),
    "C0.6": ("_compute_support_status", "STOP_AS_EVIDENCE_GAP"),
    "C0.7": ("_emit_retrieval_quality_span", "emit_spine_span_event"),
}

CONCENTRATION_PHASES = frozenset({"C0.3", "C0.4"})
MIN_HITS_CONCENTRATION = 2


def _read_repo_text(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _phase_hits() -> dict[str, list[str]]:
    corpus: dict[str, str] = {}
    for label, paths in C0_PHASE_FILES.items():
        corpus[label] = "\n".join(_read_repo_text(p) for p in paths)

    phase_hits: dict[str, list[str]] = {}
    for phase, needles in C0_PHASES.items():
        hits: list[str] = []
        for label, text in corpus.items():
            if any(n in text for n in needles):
                hits.append(label)
        phase_hits[phase] = hits
    return phase_hits


def _latest_runtime_proof_per_lane() -> dict[str, dict[str, object]]:
    proofs_root = REPO / "artifacts/apps_rg/runtime_proofs"
    out: dict[str, dict[str, object]] = {}
    for lane in GENERATED_LANES:
        lane_dir = proofs_root / lane / "real"
        if not lane_dir.is_dir():
            out[lane] = {"runtime_proof": "missing", "run_dir": None}
            continue
        run_dirs = sorted(
            (p for p in lane_dir.iterdir() if p.is_dir()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not run_dirs:
            out[lane] = {"runtime_proof": "missing", "run_dir": None}
            continue
        latest = run_dirs[0]
        receipt_path = latest / C0_GRAPH_LANE_RECEIPT_ARTIFACT
        if not receipt_path.is_file():
            out[lane] = {
                "runtime_proof": "missing_receipt",
                "run_dir": str(latest.relative_to(REPO)).replace("\\", "/"),
            }
            continue
        doc = json.loads(receipt_path.read_text(encoding="utf-8"))
        out[lane] = {
            "runtime_proof": "present",
            "run_dir": str(latest.relative_to(REPO)).replace("\\", "/"),
            "canonical_c0_3_graph_claimed": bool(doc.get("canonical_c0_3_graph_claimed")),
            "graph_lane_deferred": bool(doc.get("graph_lane_deferred")),
        }
    return out


def main() -> int:
    phase_hits = _phase_hits()

    lane_wire: dict[str, dict[str, object]] = {}
    for lane, rel in LANE_FILES.items():
        txt = _read_repo_text(rel)
        lane_wire[lane] = {
            "file": rel,
            "wire_spine_c0_fec": "wire_spine_c0_fec_for_section" in txt,
            "graph_lane_receipt_emit": (
                "ensure_section_c0_graph_lane_receipt" in txt
                or "c0_graph_lane_receipt" in txt
            ),
        }

    exec_lane = lane_wire.get("executive_summary") or {}
    exec_graph_emit = bool(exec_lane.get("graph_lane_receipt_emit"))

    concentration: dict[str, object] = {}
    subphase_concentration_ok = True
    for phase in CONCENTRATION_PHASES:
        count = len(phase_hits.get(phase, []))
        ok = count >= MIN_HITS_CONCENTRATION
        concentration[phase] = {"hit_count": count, "min_required": MIN_HITS_CONCENTRATION, "ok": ok}
        if not ok:
            subphase_concentration_ok = False

    runners = set(apps_rg_spine_run._SECTION_RUNNERS.keys())
    generated = set(GENERATED_LANES)
    graph_sections = set(GRAPH_SKILLS_AUTHORITY_SECTIONS)
    section_keys = set(SECTION_KEYS)
    sets_equal = runners == generated == graph_sections == section_keys
    all_wire = all(bool(lane_wire[l]["wire_spine_c0_fec"]) for l in GENERATED_LANES)
    phases_ok = all(phase_hits[p] for p in C0_PHASES)

    from apps_rg.runtime.spine.graph_skills_fec_set_equality import audit_all_d7_lanes

    d7 = audit_all_d7_lanes(repo_root=REPO)

    canonical = _read_repo_text("apps_rg/runtime/orchestration/canonical_dispatch.py")
    modular_steps = _read_repo_text("apps_rg/l2_recipe/steps.py")
    spine_run = _read_repo_text("apps_rg/runtime/spine/apps_rg_spine_run.py")

    full_resume = {
        "canonical_dispatch_integrated_spine": "run_integrated_single_action_spine"
        in canonical,
        "modular_section_lanes": "modular_section_lanes" in modular_steps,
        "spine_scope_full": 'scope == "full"' in spine_run,
    }

    runtime_proof_per_lane = _latest_runtime_proof_per_lane()

    status = (
        "PASS"
        if all_wire
        and sets_equal
        and phases_ok
        and subphase_concentration_ok
        and exec_graph_emit
        and d7.get("d7_all_pass")
        else "FAIL"
    )
    out = {
        "status": status,
        "lane_registry_equal": sets_equal,
        "all_lanes_wire_spine_c0": all_wire,
        "executive_summary_graph_lane_emit": exec_graph_emit,
        "subphase_concentration_ok": subphase_concentration_ok,
        "subphase_concentration": concentration,
        "lane_wire": lane_wire,
        "c0_phase_code_hits": phase_hits,
        "runtime_proof_per_lane": runtime_proof_per_lane,
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
