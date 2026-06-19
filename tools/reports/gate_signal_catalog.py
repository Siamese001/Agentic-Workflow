"""Per-gate high-signal copy for ADG burndown reports.

``GATE_WHAT`` explains what the gate **Rows** number measures.
``_verdict_rule()`` in ``adg_burndown_report`` explains why the **Verdict** is PASS/FAIL/REGR
from enforcement, classification, baseline_count, and exit_code.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# What the Rows column counts (not necessarily CI failures).
GATE_WHAT: dict[str, str] = {
    # --- Canonical ADGGateBase (12) -----------------------------------------
    "1_critical_path_integrity": (
        "Broken or missing links on declared critical execution paths (L0→sink)."
    ),
    "2_authority_boundary": (
        "Calls that cross layer authority without UWG/spine sanction."
    ),
    "3_write_sovereignty": (
        "Non-UWG durable write paths in mv_write_sovereignty_paths (inventory)."
    ),
    "4_capability_egress": (
        "Outbound provider/SDK calls not leaving through sanctioned adapters."
    ),
    "5_text_to_action": (
        "User text reaching action-class tools without prompt-governance gating."
    ),
    "6_determinism_provenance": (
        "Trace roots missing determinism digest or replay key emission."
    ),
    "7_lifecycle_coverage": (
        "Lifecycle gaps: resources opened without matching close/cleanup."
    ),
    "8_trace_replay_eval": (
        "Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path)."
    ),
    "9_executor_theater": (
        "Executor-theater signals: import-only or stub execution patterns."
    ),
    "10_infra_wiring": (
        "Infra wiring defects (canonical pipeline / spine reachability)."
    ),
    "11_architecture_witness": (
        "Architecture witness Class A/B absence or live-plane write violations."
    ),
    "12_prompt_assembly_wiring": (
        "Prompt-assembly subgraph disconnected from runtime spine."
    ),
    # --- Wiring / graph / W3–W6 (36) ----------------------------------------
    "J1_canonical_pipeline_wiring": (
        "Declared canonical_pipelines.yaml steps missing required call wiring."
    ),
    "G2_seam_test_export_coherence": (
        "Production seam symbols exported in tests but not in package __all__/exports."
    ),
    "E1_trace_stub_module": (
        "Modules with high test:production import ratio (trace-theater stub pattern)."
    ),
    "A3_dead_public_symbol_ratchet": (
        "Public symbols with zero importers (dead surface)."
    ),
    "L2_lpg_drift_ratchet": (
        "Illegal or drifted imports touching L_PG boundary."
    ),
    "M1_module_loc_ratchet": (
        "Production modules exceeding LOC ceiling (disk scan)."
    ),
    "D1_layer_doc_binding": (
        "Layer folders missing or mismatched LAYER.md binding (advisory)."
    ),
    "S2_uwg_bypass_ratchet": (
        "Write paths that bypass UWG (overlay on write_sovereignty edges)."
    ),
    "S4_unused_imports_ratchet": (
        "Unused import edges in production modules."
    ),
    "W5_waiver_expiry": (
        "Expired wiring-CI waiver entries in config."
    ),
    "B2_layer_skip_ratchet": (
        "Import edges that skip more than one layer ordinal (layer-hop)."
    ),
    "D2_role_duplication_warn": (
        "Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory)."
    ),
    "Q2_cyclomatic_complexity_ratchet": (
        "Functions with McCabe cyclomatic complexity above ceiling."
    ),
    "C1_uwg_bypass_pview": (
        "Any row in UWG-bypass materialized view (zero tolerance block)."
    ),
    "C2_l5_bypass_pview": (
        "Provider/tool calls skipping L5 gateway (materialized view)."
    ),
    "C3_silent_writes_ratchet": (
        "writes_to edges without sibling emits_side_effect on same source."
    ),
    "C4_policy_without_audit_ratchet": (
        "controls_flow edges without paired audit/telemetry emission."
    ),
    "C5_unresolved_callsites_ratchet": (
        "resolves_callsite edges with NULL destination (unresolved callee)."
    ),
    "I1_exit_disposition_ratchet": (
        "Terminal exit paths not covered in mv_exit_disposition_coverage."
    ),
    "I2_replay_surface_gaps_ratchet": (
        "State mutations not consumed by replay surface (gap_flag=1)."
    ),
    "O_tool_call_parity_ratchet": (
        "Tool invocations missing observability receipt (Anthropic parity pattern)."
    ),
    "N_guardrail_separation_ratchet": (
        "L5 guardrail and L3 core-response sharing same write target."
    ),
    "M_taint_actionable_ratchet": (
        "Actionable taint surfaces without output schema binding."
    ),
    "P_structured_output_ratchet": (
        "generates_prompt at scale without structured output schema."
    ),
    "F1_untyped_seam_ratchet": (
        "Cross-layer imports where target has empty type_surface."
    ),
    "F2_broken_contract_ratchet": (
        "Import targets publishing zero exports edges (contract drift)."
    ),
    "F3_missing_adapter_warn": (
        "Protocol/ABC/Interface with zero implements edges (advisory)."
    ),
    "H1_new_orphans_delta_ratchet": (
        "Modules newly fan_in=0 vs prior snapshot (new orphans)."
    ),
    "H2_fanin_collapse_ratchet": (
        "Hotspot modules with >30% fan_in drop vs prior snapshot."
    ),
    "H4_mv_staleness_ratchet": (
        "Total edge count delta >5% vs prior snapshot (graph drift)."
    ),
    "K1_churn_complexity_kpi": (
        "High churn×complexity files (KPI advisory, jsonl sink)."
    ),
    "E3_trace_theater_kpi": (
        "Emit-symbol density per layer vs imports (KPI advisory)."
    ),
    "H3_ap_velocity_kpi": (
        "Antipattern edge density per 1k LOC (KPI advisory)."
    ),
    "G_REACH_l0_reachability": (
        "Production-layer modules with no import path from any L0 node (orphans)."
    ),
    "G_ISLAND_connected_components": (
        "Non-giant connected components on undirected import graph."
    ),
    "G_WATCHLIST_DELTA_hotspot_regressions": (
        "Graph watchlist items newly FAIL/WARN vs prior run."
    ),
}


@dataclass(frozen=True)
class ExecutiveGateCopy:
    move: str
    finding_name: str
    why_it_matters: str
    affected_system: str = ""
    affected_layers: list[str] = field(default_factory=list)
    diagram: dict[str, str] | None = None


@dataclass(frozen=True)
class DecisionOption:
    label: str
    description: str
    required_proof: str = ""


EXECUTIVE_GATE_COPY: dict[str, dict[str, object]] = {
    "B2_layer_skip_ratchet": {
        "move": "Clear layer-jump regression",
        "finding_name": "direct dependency links",
        "why_it_matters": "Direct layer jumps increase coupling and make future changes harder to contain.",
        "affected_system": "tools",
    },
    "LayerSkipGate": {
        "move": "Clear layer-jump regression",
        "finding_name": "direct dependency links",
        "why_it_matters": "Direct layer jumps increase coupling and make future changes harder to contain.",
        "affected_system": "tools",
    },
    "C2_l5_bypass_pview": {
        "move": "Stop L5 gateway bypass",
        "finding_name": "provider/tool calls bypassing the L5 gateway",
        "why_it_matters": "Gateway bypass weakens control assurances and makes provider routing harder to defend.",
        "affected_system": "agentic_core",
    },
    "L5BypassGate": {
        "move": "Stop L5 gateway bypass",
        "finding_name": "provider/tool calls bypassing the L5 gateway",
        "why_it_matters": "Gateway bypass weakens control assurances and makes provider routing harder to defend.",
        "affected_system": "agentic_core",
    },
    "F1_untyped_seam_ratchet": {
        "move": "Close untyped cross-layer seams",
        "finding_name": "cross-layer imports with empty type surfaces",
        "why_it_matters": "Untyped seams slow safe change and increase integration risk across callers.",
        "affected_system": "tools",
    },
    "UntypedSeamGate": {
        "move": "Close untyped cross-layer seams",
        "finding_name": "cross-layer imports with empty type surfaces",
        "why_it_matters": "Untyped seams slow safe change and increase integration risk across callers.",
        "affected_system": "tools",
    },
    "L2_lpg_drift_ratchet": {
        "move": "Restore L_PG boundary discipline",
        "finding_name": "imports touching the L_PG boundary",
        "why_it_matters": "Boundary drift weakens separation and can spread if left alone.",
        "affected_system": "agentic_core",
    },
    "LpgDriftRatchetGate": {
        "move": "Restore L_PG boundary discipline",
        "finding_name": "imports touching the L_PG boundary",
        "why_it_matters": "Boundary drift weakens separation and can spread if left alone.",
        "affected_system": "agentic_core",
    },
    "S4_unused_imports_ratchet": {
        "move": "Remove unused imports",
        "finding_name": "unused import edges",
        "why_it_matters": "Unused imports add clutter and obscure the live dependency graph.",
        "affected_system": "tools",
    },
    "UnusedImportsRatchetGate": {
        "move": "Remove unused imports",
        "finding_name": "unused import edges",
        "why_it_matters": "Unused imports add clutter and obscure the live dependency graph.",
        "affected_system": "tools",
    },
}


def executive_gate_copy(gate: dict) -> ExecutiveGateCopy:
    gate_id = str(gate.get("gate_id") or "").strip()
    gate_class = str(gate.get("gate_class") or "").strip()
    payload = EXECUTIVE_GATE_COPY.get(gate_id) or EXECUTIVE_GATE_COPY.get(gate_class)
    if payload:
        return ExecutiveGateCopy(
            move=str(payload.get("move") or ""),
            finding_name=str(payload.get("finding_name") or ""),
            why_it_matters=str(payload.get("why_it_matters") or ""),
            affected_system=str(payload.get("affected_system") or ""),
            affected_layers=list(payload.get("affected_layers") or []),
            diagram=payload.get("diagram") if isinstance(payload.get("diagram"), dict) else None,
        )
    return ExecutiveGateCopy(
        move=f"Address {gate_id or gate_class or 'gate'}",
        finding_name=str(what_counts(gate_id, gate_class) or "gate findings"),
        why_it_matters="This gate still carries decision-grade risk and should be reviewed on its own terms.",
    )


def executive_next_step_options(gate: dict, breakout: dict | None) -> list[DecisionOption]:
    breakout_status = str((breakout or {}).get("status") or "").strip()
    options = [
        DecisionOption(
            label="Fix",
            description="Use when the dependency is convenience coupling or accidental reach-through.",
            required_proof="Code diff removes the direct dependency and ADG rerun clears the delta.",
        ),
        DecisionOption(
            label="Adapter/interface",
            description="Use when cross-layer collaboration is valid but the dependency path is wrong.",
            required_proof="New approved interface or adapter in the owning layer, plus tests that cover the mediated path.",
        ),
        DecisionOption(
            label="Guardian exemption",
            description="Use when the dependency is intentional but temporary or tightly constrained.",
            required_proof="Owner, rationale, expiry or retirement condition, and the scoped path list.",
        ),
        DecisionOption(
            label="Re-baseline",
            description="Use when the architecture policy intentionally changed.",
            required_proof="Approval, new baseline artifact, reason, reviewer, and migration plan.",
        ),
        DecisionOption(
            label="Investigate evidence",
            description="Use when the breakout is too thin to distinguish the options yet.",
            required_proof="More detailed samples, counts, or path concentration from ADG.",
        ),
    ]
    if breakout_status != "present":
        return [options[-1], *options[:4]]
    return options


# Top-level Verdict (3-way MECE). Sub = detail (see VERDICT_SUB_DEFINITIONS).
#
#   FIX   — address for a green ADG run (was FAIL / REGR / SEED)
#   TRACK — CI OK this run; hygiene backlog (was DEBT / OPEN / ADVIS)
#   CLEAR — zero rows (was PASS)
VERDICT_CLUSTER_DEFINITIONS: dict[str, str] = {
    "FIX": "Address before treating ADG as green (gate blocked or ratchet regressed).",
    "TRACK": "CI passed this gate; rows are backlog — plan hygiene, not a halt.",
    "CLEAR": "Zero rows; nothing to do on this gate.",
}

VERDICT_SUB_DEFINITIONS: dict[str, str] = {
    "block": "Block policy halted the run (exit 1).",
    "regr": "Ratchet count rose above baseline (+N new).",
    "seed": "Ratchet baseline file missing.",
    "floor": "Ratchet at absorbed floor (≤ baseline); large count OK if no +N.",
    "inventory": "Block warn-tier inventory (e.g. write paths); not baseline math.",
    "advis": "Warn enforcement only; never blocks.",
}

_DETAIL_TO_SUB: dict[str, str] = {
    "FAIL": "block",
    "REGR": "regr",
    "SEED": "seed",
    "DEBT": "floor",
    "OPEN": "inventory",
    "ADVIS": "advis",
    "PASS": "—",
}

_DETAIL_TO_CLUSTER: dict[str, str] = {
    "FAIL": "FIX",
    "REGR": "FIX",
    "SEED": "FIX",
    "DEBT": "TRACK",
    "OPEN": "TRACK",
    "ADVIS": "TRACK",
    "PASS": "CLEAR",
}

CLUSTER_SORT: dict[str, int] = {"FIX": 0, "TRACK": 1, "CLEAR": 2}
SUB_SORT: dict[str, int] = {
    "block": 0,
    "regr": 1,
    "seed": 2,
    "floor": 3,
    "inventory": 4,
    "advis": 5,
    "—": 9,
}


def _verdict_detail(gate: dict) -> str:
    """Internal 7-way label (drives Sub); use ``display_verdict`` for the 3-way cluster."""
    cls = str(gate.get("classification", "pass"))
    n = int(gate.get("violation_count") or 0)
    enf = str(gate.get("enforcement", ""))
    raw_status = str(gate.get("status", ""))

    if cls == "blocked":
        return "FAIL"
    if cls == "regressed":
        return "REGR"
    if cls == "seed_missing":
        return "SEED"
    if n == 0:
        return "PASS"
    if enf == "warn":
        return "ADVIS"
    if enf == "ratchet" and cls == "pass":
        return "DEBT"
    if cls == "pass" and raw_status == "warn":
        return "OPEN"
    if cls == "warn":
        return "OPEN"
    if cls == "pass" and n > 0:
        return "OPEN"
    return "PASS"


def display_verdict(gate: dict) -> str:
    """Top-level verdict: FIX | TRACK | CLEAR."""
    return _DETAIL_TO_CLUSTER[_verdict_detail(gate)]


def display_verdict_sub(gate: dict) -> str:
    """Subcategory under the cluster (block, regr, floor, inventory, …)."""
    return _DETAIL_TO_SUB[_verdict_detail(gate)]


def verdict_sort_key(gate: dict) -> int:
    cluster = display_verdict(gate)
    sub = display_verdict_sub(gate)
    return CLUSTER_SORT.get(cluster, 9) * 10 + SUB_SORT.get(sub, 9)


def has_backlog_findings(gate: dict) -> bool:
    """CI OK but findings remain (TRACK cluster)."""
    return display_verdict(gate) == "TRACK"


def needs_fix(gate: dict) -> bool:
    """Gate blocked or regressed (FIX cluster)."""
    return display_verdict(gate) == "FIX"


def render_verdict_legend_markdown() -> str:
    """Compact 3-way glossary + subcategory reference for burndown reports."""
    lines = [
        "## Verdict glossary",
        "",
        "Scan **Verdict** first (3 values). Use **Sub** only when you need detail.",
        "",
        "| Verdict | You need to… | Sub (detail) |",
        "|---------|--------------|--------------|",
        f"| **FIX** | Fix for green ADG | block, regr, seed |",
        f"| **TRACK** | Plan hygiene; CI OK | floor, inventory, advis |",
        f"| **CLEAR** | Nothing | — |",
        "",
        "| Sub | Parent | Meaning |",
        "|-----|--------|---------|",
    ]
    for sub, parent, meaning in (
        ("block", "FIX", VERDICT_SUB_DEFINITIONS["block"]),
        ("regr", "FIX", VERDICT_SUB_DEFINITIONS["regr"]),
        ("seed", "FIX", VERDICT_SUB_DEFINITIONS["seed"]),
        ("floor", "TRACK", VERDICT_SUB_DEFINITIONS["floor"]),
        ("inventory", "TRACK", VERDICT_SUB_DEFINITIONS["inventory"]),
        ("advis", "TRACK", VERDICT_SUB_DEFINITIONS["advis"]),
    ):
        lines.append(f"| {sub} | {parent} | {meaning} |")
    lines += [
        "",
        "**floor vs inventory (both TRACK):** floor = ratchet ≤ baseline (e.g. G_REACH 2792). "
        "inventory = block warn backlog (e.g. write sovereignty 848). Check **Enf**: "
        "ratchet → floor; block → inventory.",
        "",
    ]
    return "\n".join(lines)


def what_counts(gate_id: str, gate_class: str = "") -> str:
    """Human text for what the Rows column measures."""
    if gate_id in GATE_WHAT:
        return GATE_WHAT[gate_id]
    if gate_class:
        out: list[str] = []
        for ch in gate_class:
            if out and ch.isupper() and out[-1].islower():
                out.append(" ")
            out.append(ch)
        pretty = "".join(out).replace(" Gate", "")
        if pretty:
            return f"{pretty} (auto-derived from gate_class)"
    return "Gate-specific rows (see handler)."


def verdict_rule(gate: dict) -> str:
    """One-line why for Sub (internal detail label)."""
    detail = _verdict_detail(gate)
    cls = str(gate.get("classification", "pass"))
    n = int(gate.get("violation_count") or 0)
    base = gate.get("baseline_count")
    owner = str(gate.get("owner", ""))
    exit_code = int(gate.get("exit_code") or 0)

    if detail == "FAIL":
        return "Run blocked (exit 1)."
    if detail == "REGR":
        if base is not None:
            return f"+{n - int(base)} vs baseline {base}."
        return "Above ratchet baseline."
    if detail == "SEED":
        return "Ratchet baseline missing."
    if detail == "PASS":
        return "No rows."
    if detail == "ADVIS":
        return f"{n} advisory; never blocks."
    if detail == "DEBT":
        if base is not None:
            return f"{n} at floor (baseline {base}); no new debt."
        return f"{n} within ratchet; backlog remains."
    if detail == "OPEN":
        if owner == "adg_gates" and exit_code == 0:
            return f"{n} warn inventory; not halt-tier."
        if cls == "warn":
            return f"{n} subprocess warn."
        return f"{n} open rows; run not blocked."
    return "See gate handler."


def format_gate_signal(gate: dict) -> str:
    """What Rows count + short Sub rationale."""
    gid = str(gate.get("gate_id", ""))
    cls = str(gate.get("gate_class") or "")
    return f"Counts: {what_counts(gid, cls)} Sub: {verdict_rule(gate)}"


def recommended_next_step(gate: dict) -> str:
    """Concrete, per-gate recommended action for the burndown 'Recommended Next Step' column.

    Derived deterministically from the internal 7-way detail label (FAIL / REGR / SEED /
    DEBT / OPEN / ADVIS / PASS), the severity band, and the baseline delta. The intent is
    that an operator can act on each row without re-deriving the fix path.
    """
    detail = _verdict_detail(gate)
    band = str(gate.get("band", "P?"))
    n = int(gate.get("violation_count") or 0)
    base = gate.get("baseline_count")

    if detail == "PASS":
        return "None — gate clean (zero rows)."
    if detail == "FAIL":
        if band == "P0":
            return (
                "BLOCKER (P0): clear the zero-tolerance condition before merge. "
                "Do NOT re-baseline a P0 block."
            )
        return "Blocking: resolve the failing condition before the run can pass."
    if detail == "REGR":
        delta = f"+{n - int(base)}" if base is not None else "+N"
        if band == "P0":
            return (
                f"Regression {delta} over baseline {base} (P0): investigate each NEW path; "
                "fix the regression — re-baseline only with explicit sign-off."
            )
        return (
            f"Regression {delta} over baseline {base}: fix the new findings, or "
            "re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt."
        )
    if detail == "SEED":
        return "First run / missing baseline: seed it via the gate's `--regenerate-baseline`."
    if detail == "DEBT":
        return (
            "Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. "
            "No action needed to pass CI."
        )
    if detail == "OPEN":
        return "Advisory inventory: monitor; reduce opportunistically. Does not block CI."
    if detail == "ADVIS":
        return "Advisory KPI: watch the trend; no action required to pass CI."
    return "Review the gate handler for the appropriate remediation."
