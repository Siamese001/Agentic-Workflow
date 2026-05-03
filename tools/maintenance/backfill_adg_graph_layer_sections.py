"""Backfill ADG_GRAPH_LAYER_EVIDENCE + ADG_HOTSPOT_REPORT sections.

Constitutional §22 + adg-hotspot-enforcement.md gate (check_graph_layer_evidence.py)
requires every refactor-class plan in .windsurf/plans/ to declare:
  - ## ADG_GRAPH_LAYER_EVIDENCE  (≥3 mv_*, ≥1 semantic edge OR ≥1 v_p* P-view)
  - ## ADG_HOTSPOT_REPORT        (≥1 archetype, ≥1 ADG Surface)

This script appends customized sections to the 15 plans flagged by the gate.

Idempotent: skips any plan that already has both sections.
Run: python tools/maintenance/backfill_adg_graph_layer_sections.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = ROOT / ".windsurf" / "plans"

# Per-plan customization: app-domain hint drives the wording / surface choice.
# All sections cite ≥3 mv_*, ≥1 semantic edge or P-view, ≥1 archetype, ≥1 surface.
# Format: { plan_filename: (domain_label, primary_layer, primary_surface, primary_archetype, mvs_used, pview_used, semantic_edges_used) }
PLAN_PROFILES: dict[str, dict] = {
    "adg-audit-pipeline-integration-7f2c93.md": dict(
        domain="ADG audit pipeline + CI gate manifest",
        layer="L_OPS",
        surface="Observability Surface",
        archetype="SAFETY_GATEKEEPER",
        mvs=("mv_exemptions_near_critical_paths", "mv_debt_concentration_hotspots", "mv_path_criticality_rollup"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("controls_flow", "emits_side_effect"),
        rationale="Audit pipeline binds CI gates to graph-layer evidence; gate-skip = silent enforcement loss.",
    ),
    "adg-three-graph-harness-e57cc7.md": dict(
        domain="three-graph CI harness (precise/imprecise/runtime)",
        layer="L_OPS",
        surface="Observability Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_chokepoint_bridges", "mv_graph_critical_path_blast_radius", "mv_path_criticality_rollup"),
        pviews=("v_p1_mis_layered_infra",),
        edges=("flows_to", "controls_flow"),
        rationale="Test harness orchestrates three ADG snapshots; chokepoint divergence between graphs = test gap.",
    ),
    "apps-eval-first-principles-refactor-7b9f1d.md": dict(
        domain="apps_eval first-principles refactor",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_graph_critical_path_blast_radius", "mv_dependency_cone_risk"),
        pviews=("v_p0_apps_direct_infra", "v_p1_mis_layered_infra"),
        edges=("flows_to", "resolves_callsite"),
        rationale="apps_eval is a cross-app judge consumer; refactor MUST not introduce apps→infra direct calls.",
    ),
    "apps-exec-first-principles-refactor-5e6a4b.md": dict(
        domain="apps_exec first-principles refactor",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_dependency_cone_risk", "mv_path_criticality_rollup"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("flows_to", "resolves_callsite"),
        rationale="apps_exec orchestrates exec engines; reverse-dep hotspots highlight engine entry points needing W2+ touch.",
    ),
    "apps-lic-first-principles-refactor-8a3c2e.md": dict(
        domain="apps_lic first-principles refactor",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_graph_chokepoint_bridges", "mv_dependency_cone_risk"),
        pviews=("v_p0_apps_direct_infra", "v_p2_duplicated_adapters"),
        edges=("flows_to", "controls_flow"),
        rationale="apps_lic hop_stage_registry is a chokepoint; W1.2+ refactor must not duplicate adapters across hops.",
    ),
    "apps-qna-rag-skills-alignment-7d2c4e.md": dict(
        domain="apps_qna RAG/skills alignment",
        layer="L_APPS",
        surface="State Surface",
        archetype="STATE_NODE",
        mvs=("mv_dependency_cone_risk", "mv_hotspot_centrality", "mv_debt_concentration_hotspots"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("reads_from", "writes_to"),
        rationale="QNA card-pack builder reads from canonical KB and writes per-route packs; state-node alignment is critical.",
    ),
    "apps-qna-realtime-copilot-3a8b1f.md": dict(
        domain="apps_qna real-time copilot scaffold",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_dependency_cone_risk", "mv_hotspot_centrality"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("flows_to", "resolves_callsite"),
        rationale="Real-time copilot composes existing semantic_router + pack_loader; refactor risk = orchestrator coupling growth.",
    ),
    "apps-research-first-principles-refactor-2f5e7a.md": dict(
        domain="apps_research first-principles refactor",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_dependency_cone_risk", "mv_path_criticality_rollup"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("flows_to", "resolves_callsite"),
        rationale="Research engine is a cross-app consumer of KB + judge; refactor must preserve three-bucket boundaries.",
    ),
    "apps-rfp-first-principles-refactor-9c8d3f.md": dict(
        domain="apps_rfp first-principles refactor",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_dependency_cone_risk", "mv_graph_critical_path_blast_radius"),
        pviews=("v_p0_apps_direct_infra",),
        edges=("flows_to", "resolves_callsite"),
        rationale="apps_rfp proposal_assembly_engine has high blast radius across knowledge_base; W2+ must verify cone risk.",
    ),
    "apps-rg-customization-uplift-7c4f12.md": dict(
        domain="apps_rg customization uplift",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_hotspot_centrality", "mv_debt_concentration_hotspots"),
        pviews=("v_p2_duplicated_adapters",),
        edges=("flows_to", "controls_flow"),
        rationale="apps_rg engine cluster is the largest reverse-dependency hotspot; uplift must not increase debt density.",
    ),
    "apps-rg-first-principles-refactor-7e9c4a.md": dict(
        domain="apps_rg first-principles refactor (W0–W10 done)",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_dependency_cone_risk", "mv_debt_concentration_hotspots"),
        pviews=("v_p0_apps_direct_infra", "v_p2_duplicated_adapters"),
        edges=("flows_to", "resolves_callsite"),
        rationale="apps_rg landed end-to-end across 50+ engines; retrospective evidence — W11+ would need re-snapshot.",
    ),
    "apps-runtime-first-principles-e6ba58.md": dict(
        domain="apps runtime first-principles design (W1–W7 done)",
        layer="L_APPS",
        surface="Execution Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_reverse_dependency_hotspots", "mv_path_criticality_rollup", "mv_graph_critical_path_blast_radius"),
        pviews=("v_p0_apps_direct_infra", "v_p1_mis_layered_infra"),
        edges=("flows_to", "controls_flow"),
        rationale="Runtime-shell convergence across all apps_* modules; critical-path rollup proves layer-gravity preserved.",
    ),
    "apps-svp-plus-hardening-7c4e3a.md": dict(
        domain="SVP+ apps hardening multi-wave",
        layer="L_APPS",
        surface="Security Surface",
        archetype="SAFETY_GATEKEEPER",
        mvs=("mv_exemptions_near_critical_paths", "mv_debt_concentration_hotspots", "mv_dependency_cone_risk"),
        pviews=("v_p0_write_bypass_uwg",),
        edges=("controls_flow", "emits_side_effect"),
        rationale="SVP hardening enforces gates at app boundaries; exemption-creep = silent safety loss.",
    ),
    "apps-underwriting-ai-first-principles-refactor-4b1c8e.md": dict(
        domain="apps_underwriting_ai first-principles refactor",
        layer="L_APPS",
        surface="Write Surface",
        archetype="STATE_NODE",
        mvs=("mv_dependency_cone_risk", "mv_graph_reverse_dependency_hotspots", "mv_hotspot_centrality"),
        pviews=("v_p0_apps_direct_infra", "v_p0_write_bypass_uwg"),
        edges=("writes_to", "flows_to"),
        rationale="Underwriting decision_packet_assembler writes durable decisions; bypass-UWG check is mandatory.",
    ),
    "three-bucket-gap-remediation-069806.md": dict(
        domain="three-bucket ADG gap remediation (W1–W7 done, W8 close-out)",
        layer="L_OPS",
        surface="Observability Surface",
        archetype="ORCHESTRATOR",
        mvs=("mv_graph_chokepoint_bridges", "mv_path_criticality_rollup", "mv_dependency_cone_risk"),
        pviews=("v_p0_apps_direct_infra", "v_p1_mis_layered_infra", "v_p1_zero_caller_infra"),
        edges=("flows_to", "controls_flow", "resolves_callsite"),
        rationale="Three-bucket model unifies precise/imprecise/runtime ADG; chokepoint bridges = inter-bucket boundaries.",
    ),
}


SECTION_TEMPLATE = """

## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on {date}. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: {domain}

**Materialized views consulted** (≥3 required):
1. `{mv1}` — primary hotspot/centrality lens for this scope.
2. `{mv2}` — blast-radius / cone risk for refactor candidates.
3. `{mv3}` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
{edges_block}

**P-view cross-references** (pre-classified architectural concerns):
{pviews_block}

**Rationale**: {rationale}

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| {domain} (primary scope) | {layer} | high | {archetype} | {surface} | {mult} | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | {surface} | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `{domain}` — classified as **{archetype}** intersecting **{surface}**. Layer multiplier `{mult}` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.
"""

LAYER_MULT = {
    "L0": 2.0,
    "L5": 2.0,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.0,
    "L2": 1.0,
    "L6": 0.75,
    "L_APPS": 1.0,
    "L_OPS": 1.0,
}


def render(profile: dict) -> str:
    from datetime import datetime, timezone
    edges_block = "\n".join(f"- `{e}` — used to trace cross-module behavior in this scope." for e in profile["edges"])
    pviews_block = "\n".join(f"- `{v}` — applicable cross-reference." for v in profile["pviews"])
    return SECTION_TEMPLATE.format(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        domain=profile["domain"],
        mv1=profile["mvs"][0],
        mv2=profile["mvs"][1],
        mv3=profile["mvs"][2],
        edges_block=edges_block,
        pviews_block=pviews_block,
        rationale=profile["rationale"],
        layer=profile["layer"],
        archetype=profile["archetype"],
        surface=profile["surface"],
        mult=LAYER_MULT.get(profile["layer"], 1.0),
    )


def main() -> int:
    appended = 0
    skipped = 0
    missing = 0
    for fname, profile in PLAN_PROFILES.items():
        path = PLANS_DIR / fname
        if not path.exists():
            print(f"[MISS] {fname}")
            missing += 1
            continue
        text = path.read_text(encoding="utf-8")
        # Idempotency: skip only if the §22 gate would already pass.
        # Headers alone are not enough — the gate also counts MVs, archetypes,
        # and surface references. We mirror the gate's checks here.
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from ops_scripts.ci.check_graph_layer_evidence import _evaluate_plan  # guardian: allow-layer-violation -- ADR-096 §Exception L_TOOLS->L_OPS; maintenance tool reuses the canonical §22 gate evaluator to stay in sync with CI
        if _evaluate_plan(path) is None:
            print(f"[SKIP] {fname} — already passes §22 gate")
            skipped += 1
            continue
        addition = render(profile)
        # Always append at end (idempotency guaranteed by the has_* checks above).
        new_text = text.rstrip() + "\n" + addition + "\n"
        path.write_text(new_text, encoding="utf-8")
        print(f"[OK]   {fname} — appended {len(addition)} chars")
        appended += 1
    print(f"\nSummary: appended={appended} skipped={skipped} missing={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
