"""Packet Builders — 8 builder functions, one per packet family.

Every builder:
    1. Gets its template from the PacketRegistry
    2. Calls retrieval adapters to fetch evidence
    3. Runs evidence through the shaper
    4. Applies token budgeting
    5. Assembles and returns a PromptEnvelope

Builders NEVER call SQLite/JSON/graph DB directly — only through adapters.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from tools.adg.prompt_assembly.budgeting.token_budgeter import (
    BudgetResult,
    apply_budget,
    estimate_tokens,
)
from tools.adg.prompt_assembly.contracts import (
    EvidenceItem,
    PromptAssemblyStatus,
    PromptEnvelope,
)
from tools.adg.prompt_assembly.packets.registry import (
    PacketTemplate,
    get_template,
)
from tools.adg.prompt_assembly.retrieval.adapters import (
    GraphDBAdapter,
    RatchetAdapter,
    ReportAdapter,
    SQLiteAdapter,
    StructuralAdapter,
)
from tools.adg.prompt_assembly.shaping.evidence_shaper import shape_evidence


# ---------------------------------------------------------------------------
# Shared assembly helper
# ---------------------------------------------------------------------------


def _assemble(
    template: PacketTemplate,
    must_items: list[EvidenceItem],
    opt_items: list[EvidenceItem],
    task_block: str,
    replay_extras: dict[str, Any] | None = None,
) -> PromptEnvelope:
    """Shared assembly: shape → budget → build envelope."""
    # Shape evidence
    all_items = must_items + opt_items
    bundle = shape_evidence(all_items, must_use_sources=template.must_use_sources)

    # Separate must-use (canonical) from optional (derived)
    must_dicts = [item.to_dict() for item in must_items if not item.data.get("error")]
    opt_dicts = [item.to_dict() for item in opt_items if not item.data.get("error")]

    # Token budget for fixed blocks
    fixed_tokens = (
        estimate_tokens(template.system_block, "text")
        + estimate_tokens(template.policy_block, "text")
        + estimate_tokens(task_block, "text")
    )

    # Apply budget
    budget_result: BudgetResult = apply_budget(
        must_use_evidence=must_dicts,
        optional_evidence=opt_dicts,
        fixed_tokens=fixed_tokens,
        budget=template.token_budget,
    )

    # Build replay metadata
    replay = {
        "snapshot_ids": list({item.snapshot_id for item in all_items if item.snapshot_id}),
        "commit_shas": list({item.commit_sha for item in all_items if item.commit_sha}),
        "artifact_digests": list({item.artifact_digest for item in all_items if item.artifact_digest}),
        "source_artifacts": [item.source_artifact for item in all_items],
    }
    if replay_extras:
        replay.update(replay_extras)

    # Build assembly status
    evidence_status: str
    if bundle.coverage_score >= 0.8:
        evidence_status = "complete"
    elif bundle.coverage_score > 0.0:
        evidence_status = "partial"
    else:
        evidence_status = "empty"

    assembly_result: str
    if evidence_status == "empty" or budget_result.overflow_action == "abstained":
        assembly_result = "fail"
    elif evidence_status == "partial" or budget_result.overflow_action != "none":
        assembly_result = "partial"
    else:
        assembly_result = "pass"

    status = PromptAssemblyStatus(
        packet_type=template.packet_type,
        input_artifacts=[item.source_artifact for item in all_items],
        evidence_contract_status=evidence_status,  # type: ignore[arg-type]
        contradiction_status=bundle.contradiction_status,  # type: ignore[arg-type]
        token_budget_status=budget_result.budget_status,
        overflow_action=budget_result.overflow_action,
        assembly_result=assembly_result,  # type: ignore[arg-type]
        replay_metadata=replay,
    )

    # Abstain / refine instructions
    abstain = template.abstain_instructions
    refine = template.refine_instructions
    if bundle.coverage_score < 0.3:
        abstain = (
            f"Evidence coverage is critically low ({bundle.coverage_score:.0%}). "
            f"Gaps: {', '.join(bundle.gaps)}. {abstain}"
        )
    if budget_result.summary_note:
        refine = f"{budget_result.summary_note}\n{refine}"

    return PromptEnvelope(
        packet_type=template.packet_type,
        schema_version="1.0.0",
        system_block=template.system_block,
        policy_block=template.policy_block,
        task_block=task_block,
        must_use_evidence=budget_result.must_use_evidence,
        optional_evidence=budget_result.optional_evidence,
        contradiction_flags=[c.to_dict() for c in bundle.contradictions],
        abstain_instructions=abstain,
        refine_instructions=refine,
        output_schema=template.output_schema,
        replay_metadata=replay,
        assembly_status=status,
    )


# ---------------------------------------------------------------------------
# A. Determinism / Provenance RCA
# ---------------------------------------------------------------------------


def build_determinism_rca(
    sqlite_path: Path | None = None,
    graph: Any | None = None,
) -> PromptEnvelope:
    """Build a Determinism/Provenance RCA packet."""
    template = get_template("determinism_rca")
    sq = SQLiteAdapter(sqlite_path)
    rp = ReportAdapter()

    must_items = [
        rp.fetch_provenance(),
        rp.fetch_closure(),
        sq.fetch_node_edge_counts(),
    ]
    opt_items: list[EvidenceItem] = []
    if graph is not None:
        gdb = GraphDBAdapter(graph)
        opt_items.append(gdb.fetch_neighborhood("__root__", radius=1))

    task = (
        "Analyze the provenance and closure reports for this ADG run. "
        "Identify digest mismatches, node/edge reconciliation failures, "
        "probe errors, and weak closure rows. Produce root-cause hypotheses "
        "and recommended next diagnostic steps."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# B. P0 Failure
# ---------------------------------------------------------------------------


def build_p0_failure(
    sqlite_path: Path | None = None,
    graph: Any | None = None,
) -> PromptEnvelope:
    """Build a P0 Failure analysis packet."""
    template = get_template("p0_failure")
    sq = SQLiteAdapter(sqlite_path)
    rp = ReportAdapter()

    must_items = [
        sq.fetch_violations(limit=30),
        rp.fetch_closure(),
        rp.fetch_sc_ap_config(),
    ]
    opt_items: list[EvidenceItem] = []
    if graph is not None:
        gdb = GraphDBAdapter(graph)
        opt_items.append(gdb.fetch_neighborhood("__root__", radius=1))

    task = (
        "Analyze the P0 violations from this ADG run. For each violation, "
        "identify the offending file, the rule violated (layer violation, "
        "circular import, or dynamic_exec), the first illegal hop, and "
        "the candidate repair mode. Prioritize by structural risk."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# C. Ratchet Review (P1/P2)
# ---------------------------------------------------------------------------


def build_ratchet_review(
    sqlite_path: Path | None = None,
) -> PromptEnvelope:
    """Build a P1/P2 Ratchet Review packet."""
    template = get_template("ratchet_review")
    sq = SQLiteAdapter(sqlite_path)
    ra = RatchetAdapter()

    must_items = [
        ra.fetch_p1_ratchet(),
        ra.fetch_p2_ratchet(),
        ra.fetch_burndown(),
        sq.fetch_antipatterns_by_severity(),
    ]
    opt_items: list[EvidenceItem] = []

    task = (
        "Compare current P1/P2 anti-pattern counts against ratchet ceilings. "
        "Identify the net delta (new vs resolved violations), affected layers, "
        "exemption counts, and recommend a fix ordering prioritized by "
        "structural risk and layer gravity."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# D. Unknown / Unresolved Triage
# ---------------------------------------------------------------------------


def build_unknown_unresolved_triage(
    sqlite_path: Path | None = None,
    graph: Any | None = None,
) -> PromptEnvelope:
    """Build an Unknown/Unresolved Triage packet."""
    template = get_template("unknown_unresolved_triage")
    sq = SQLiteAdapter(sqlite_path)
    rp = ReportAdapter()

    must_items = [
        rp.fetch_layer_coverage(),
        sq.fetch_unresolved_imports(limit=30),
    ]
    opt_items: list[EvidenceItem] = []
    if graph is not None:
        gdb = GraphDBAdapter(graph)
        opt_items.append(gdb.fetch_neighborhood("__unknown__", radius=1))

    task = (
        "Triage the unknown modules and unresolved imports from this ADG run. "
        "Classify each as taxonomy lag (module exists but layer mapping is "
        "missing) vs real structural gap (module does not exist or was deleted). "
        "Identify package concentration patterns and recommend remediation."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# E. Hotspot Investigation
# ---------------------------------------------------------------------------


def build_hotspot_investigation(
    sqlite_path: Path | None = None,
    graph: Any | None = None,
    top_n: int = 15,
) -> PromptEnvelope:
    """Build a Hotspot Investigation packet."""
    template = get_template("hotspot_investigation")
    sq = SQLiteAdapter(sqlite_path)
    st = StructuralAdapter(sqlite_path)

    must_items = [
        sq.fetch_fan_in_hotspots(top_n=top_n),
        sq.fetch_fan_out_hotspots(top_n=top_n),
        st.fetch_centrality(top_n=top_n),
    ]
    opt_items: list[EvidenceItem] = []
    if graph is not None:
        gdb = GraphDBAdapter(graph)
        # Get blast radius for top hotspot if available
        fan_in = sq.fetch_fan_in_hotspots(top_n=1)
        hotspots = fan_in.data.get("fan_in_hotspots", [])
        if hotspots:
            opt_items.append(gdb.fetch_blast_radius(hotspots[0]["node_id"], max_depth=3))

    task = (
        "Analyze the hotspot landscape of this ADG run. Identify the highest "
        "fan-in/fan-out nodes, their connected risk surfaces (violations, "
        "anti-patterns, infra wiring issues in their neighborhood), and "
        "root-cause neighborhoods. Recommend prioritized remediation targets."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# F. Infrastructure Boundary
# ---------------------------------------------------------------------------


def build_infrastructure_boundary(
    sqlite_path: Path | None = None,
    graph: Any | None = None,
) -> PromptEnvelope:
    """Build an Infrastructure Boundary packet."""
    template = get_template("infrastructure_boundary")
    sq = SQLiteAdapter(sqlite_path)

    must_items = [
        sq.fetch_infra_wiring_views(limit=30),
        sq.fetch_violations(limit=20),
    ]
    opt_items: list[EvidenceItem] = []
    if graph is not None:
        gdb = GraphDBAdapter(graph)
        opt_items.append(gdb.fetch_neighborhood("__infra__", radius=2))

    task = (
        "Analyze infrastructure wiring violations from the ADG SQL views. "
        "Identify raw infra spread (direct imports outside sanctioned adapters), "
        "write-path bypass risks, and provider/tool choke-point failures. "
        "List approved vs miswired surfaces and recommend wiring fixes."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# G. Graph Path Explanation
# ---------------------------------------------------------------------------


def build_graph_path_explanation(
    from_node: str,
    to_node: str,
    sqlite_path: Path | None = None,
    graph: Any | None = None,
) -> PromptEnvelope:
    """Build a Graph Path Explanation packet."""
    template = get_template("graph_path_explanation")
    sq = SQLiteAdapter(sqlite_path)

    must_items: list[EvidenceItem] = [
        sq.fetch_violations(limit=10),
    ]
    opt_items: list[EvidenceItem] = []

    if graph is not None:
        gdb = GraphDBAdapter(graph)
        must_items.append(gdb.fetch_violating_path(from_node, to_node))
        opt_items.append(gdb.fetch_blast_radius(to_node, max_depth=3))
    else:
        must_items.append(
            EvidenceItem(
                source_artifact="graph_db_projection",
                source_type="graph_db",
                snapshot_id="",
                is_derived=True,
                data={"error": "graph_not_loaded", "from_node": from_node, "to_node": to_node},
            )
        )

    task = (
        f"Explain the violating path from `{from_node}` to `{to_node}`. "
        "Identify the first illegal hop, what rule it violates, what "
        "choke point is missing, and the blast-radius neighbors that "
        "would be affected by a fix. Include cross-snapshot context if available."
    )
    return _assemble(
        template,
        must_items,
        opt_items,
        task,
        replay_extras={
            "from_node": from_node,
            "to_node": to_node,
        },
    )


# ---------------------------------------------------------------------------
# H. Executive Summary
# ---------------------------------------------------------------------------


def build_executive_summary(
    sqlite_path: Path | None = None,
) -> PromptEnvelope:
    """Build an Executive Summary packet."""
    template = get_template("executive_summary")
    rp = ReportAdapter()
    ra = RatchetAdapter()

    must_items = [
        rp.fetch_snapshot(),
        ra.fetch_burndown(),
        rp.fetch_closure(),
        ra.fetch_p1_ratchet(),
        ra.fetch_p2_ratchet(),
    ]
    opt_items: list[EvidenceItem] = []
    st = StructuralAdapter(sqlite_path)
    opt_items.append(st.fetch_centrality(top_n=5))

    task = (
        "Produce a concise executive summary of this ADG run. Cover: "
        "(1) top blockers (P0 violations, ratchet breaches), "
        "(2) likely false positives (known taxonomy gaps), "
        "(3) taxonomy mismatches (unknown modules that may be mis-classified), "
        "(4) recommended next wave of work. "
        "Disclose any uncertainty or weak evidence explicitly."
    )
    return _assemble(template, must_items, opt_items, task)


# ---------------------------------------------------------------------------
# Builder dispatch
# ---------------------------------------------------------------------------

_BUILDER_NAMES: list[str] = [
    "determinism_rca",
    "p0_failure",
    "ratchet_review",
    "unknown_unresolved_triage",
    "hotspot_investigation",
    "infrastructure_boundary",
    "graph_path_explanation",
    "executive_summary",
]


def build_packet(
    packet_type: str,
    sqlite_path: Path | None = None,
    graph: Any | None = None,
    **kwargs: Any,
) -> PromptEnvelope:
    """Build a packet by type name. Dispatches to the appropriate builder.

    Args:
        packet_type: One of the 8 registered packet types.
        sqlite_path: Optional explicit path to ADG SQLite.
        graph: Optional NetworkX graph for derived evidence.
        **kwargs: Additional builder-specific arguments.

    Returns:
        Assembled PromptEnvelope.

    Raises:
        ValueError: If packet_type is unknown.
    """
    dispatch: dict[str, Callable[..., PromptEnvelope]] = {
        "determinism_rca": build_determinism_rca,
        "p0_failure": build_p0_failure,
        "ratchet_review": build_ratchet_review,
        "unknown_unresolved_triage": build_unknown_unresolved_triage,
        "hotspot_investigation": build_hotspot_investigation,
        "infrastructure_boundary": build_infrastructure_boundary,
        "graph_path_explanation": build_graph_path_explanation,
        "executive_summary": build_executive_summary,
    }
    if packet_type not in dispatch:
        raise ValueError(f"Unknown packet type: {packet_type!r}. Valid types: {sorted(dispatch.keys())}")
    builder = dispatch[packet_type]

    # Graph path requires from_node/to_node
    if packet_type == "graph_path_explanation":
        from_node = kwargs.get("from_node", "")
        to_node = kwargs.get("to_node", "")
        return builder(from_node=from_node, to_node=to_node, sqlite_path=sqlite_path, graph=graph)

    # Hotspot accepts top_n
    if packet_type == "hotspot_investigation":
        top_n = kwargs.get("top_n", 15)
        return builder(sqlite_path=sqlite_path, graph=graph, top_n=top_n)

    # Ratchet and executive don't use graph
    if packet_type in ("ratchet_review", "executive_summary"):
        return builder(sqlite_path=sqlite_path)

    return builder(sqlite_path=sqlite_path, graph=graph)
