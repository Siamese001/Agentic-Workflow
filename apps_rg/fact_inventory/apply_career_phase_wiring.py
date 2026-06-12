"""Career-phase (epoch) wiring migration for the master skills arsenal ledger.

Completes the previously-DRAFT epoch/phase layer. ADDITIVE ONLY — adds metadata
fields + edges that no current projection/generation code reads; the runtime
behaviour is unchanged until the new ordinal X2 gate (separate, validated step)
consumes these fields.

What it does:
  1. P6 decision: move the 6 AI-platform-commercialization skills from Phase 5
     (Agentic AI Runtime) to Phase 6 (AI Platform Commercialization).
  2. Assign ``phase_ordinal`` 1..6 to every skill (skill_rows + graph_nodes stubs)
     derived from ``career_epoch``; cross_career stays non-ordinal (None).
  3. Assign ``phase_ordinal`` to the 6 career_epoch nodes; flip DRAFT -> ACTIVE.
  4. Assign ``min_phase``/``max_phase`` to the 5 employment nodes.
  5. Wire ``skill_in_epoch`` and ``employment_spans_epoch`` edges.

Re-runnable (recomputes from career_epoch; edges deduped by (src,tgt,type)).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

LEDGER = Path(__file__).resolve().parent / "master_skills_arsenal_ledger.json"

# Canonical phase ordinals (final ordering).
EPOCH_ORDINAL: dict[str, int] = {
    "epoch_actuarial_financial_engineering": 1,
    "epoch_enterprise_risk_governance": 2,
    "epoch_cloud_data_platform_engineering": 3,
    "epoch_partner_gtm_revenue_leadership": 4,
    "epoch_agentic_ai_runtime_architecture": 5,
    "epoch_ai_platform_commercialization": 6,
}

# P6 decision (user-confirmed): these 6 productization/commercialization skills
# move from Phase 5 (agentic runtime) to Phase 6 (AI platform commercialization).
P6_SKILLS: set[str] = {
    "skill_agentic_platform_productization",
    "skill_reusable_ai_ip_design",
    "skill_app_specific_runtime_overlay_design",
    "skill_enterprise_workflow_adoption",
    "skill_operating_model_for_agentic_ai",
    "skill_ai_platform_commercialization",
}

# Employment node -> (min_phase, max_phase). IBM spans cloud-platform (3) ->
# partner-GTM (4); Unify spans agentic-runtime (5) -> commercialization (6).
EMPLOYMENT_PHASES: dict[str, tuple[int, int]] = {
    "employment_exp_early_career_001": (1, 1),
    "employment_exp_ey_001": (2, 2),
    "employment_exp_insurtech_001": (3, 3),
    "employment_exp_ibm_001": (3, 4),
    "employment_exp_unify_001": (5, 6),
}


def main() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    changes: Counter[str] = Counter()

    # 1 + 2. Move P6 skills, then stamp phase_ordinal on every skill_row.
    for s in data["skill_rows"]:
        sid = s.get("skill_id")
        if sid in P6_SKILLS and s.get("career_epoch") != "epoch_ai_platform_commercialization":
            s["career_epoch"] = "epoch_ai_platform_commercialization"
            changes["p6_moved"] += 1
        s["phase_ordinal"] = EPOCH_ORDINAL.get(s.get("career_epoch"))  # None for cross_career
        changes["skill_rows_tagged"] += 1

    skill_epoch = {
        s["skill_id"]: (s.get("career_epoch"), s.get("phase_ordinal"))
        for s in data["skill_rows"]
        if s.get("skill_id")
    }

    # 3 + 4. Epoch ordinals + activation; employment phase ranges; propagate to stubs.
    for n in data["graph_nodes"]:
        nt = n.get("node_type")
        if nt == "career_epoch":
            n["phase_ordinal"] = EPOCH_ORDINAL.get(n["node_id"])
            if n.get("activation_status") == "DRAFT":
                n["activation_status"] = "ACTIVE"
                changes["epochs_activated"] += 1
            changes["epochs_ordinal"] += 1
        elif nt == "employment":
            phases = EMPLOYMENT_PHASES.get(n["node_id"])
            if phases:
                n["min_phase"], n["max_phase"] = phases
                changes["employments_phased"] += 1
        elif nt == "skill_row":
            epoch, ordinal = skill_epoch.get(n["node_id"], (None, None))
            if epoch is not None:
                n["career_epoch"] = epoch
                n["phase_ordinal"] = ordinal
                changes["graph_stubs_tagged"] += 1

    # 5. Wire edges (dedupe by (src, tgt, type)).
    existing = {
        (e.get("source_node_id"), e.get("target_node_id"), e.get("edge_type"))
        for e in data["graph_edges"]
    }

    def add_edge(src: str, tgt: str, etype: str, rationale: str) -> bool:
        key = (src, tgt, etype)
        if key in existing:
            return False
        data["graph_edges"].append(
            {
                "edge_id": f"edge_{etype}_{src}_to_{tgt}"[:200],
                "edge_type": etype,
                "source_node_id": src,
                "target_node_id": tgt,
                "rationale": rationale,
                "projection_behavior": "epoch_filter",
                "external_claim_policy": "skill_projection_not_proof",
                "validation_status": "DERIVED_SUPPORTED",
            }
        )
        existing.add(key)
        return True

    for sid, (epoch, ordinal) in skill_epoch.items():
        if epoch in EPOCH_ORDINAL:
            if add_edge(sid, epoch, "skill_in_epoch", f"skill assigned to career phase {ordinal}"):
                changes["skill_epoch_edges"] += 1

    for emp, (lo, hi) in EMPLOYMENT_PHASES.items():
        for epoch, ordinal in EPOCH_ORDINAL.items():
            if lo <= ordinal <= hi:
                if add_edge(emp, epoch, "employment_spans_epoch", f"employer spans career phase {ordinal}"):
                    changes["employer_epoch_edges"] += 1

    # Validate + write (preserve indent=2, no trailing newline, unicode).
    phase_counts = Counter(s.get("phase_ordinal") for s in data["skill_rows"])
    LEDGER.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print("CAREER-PHASE WIRING — COMPLETE")
    for key in (
        "p6_moved",
        "skill_rows_tagged",
        "graph_stubs_tagged",
        "epochs_ordinal",
        "epochs_activated",
        "employments_phased",
        "skill_epoch_edges",
        "employer_epoch_edges",
    ):
        print(f"  {key}: {changes[key]}")
    print("  phase distribution (skill_rows):")
    for phase in (1, 2, 3, 4, 5, 6, None):
        label = f"P{phase}" if phase else "cross_career"
        print(f"    {label}: {phase_counts.get(phase, 0)}")


if __name__ == "__main__":
    main()
