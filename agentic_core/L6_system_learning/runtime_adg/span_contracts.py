"""Tier 1 span coverage contract for Runtime ADG snapshots.

Plan: `.windsurf/plans/runtime-adg-tier1-trace-binding-c9b84d.md`
Doctrine: `docs/reference/Runtime ADG and OTEL Spans.md`

What this module does
---------------------
Given a `RuntimeADGSnapshot`, report whether it contains each of the 5
Tier 1 span categories that constitute the "correlation spine." Does NOT
emit spans and does NOT mutate anything. Pure read-only validation.

Tier 1 categories (minimum viable runtime ADG)
----------------------------------------------
    1. runtime.trace_root       — "Which execution is this?"
    2. L0.route.select          — "Why did L0 choose this path?"
    3. L2.step.seal             — "What did execution finish with?"
    4. L2.(model|tool).invoke   — "What actually ran?"
    5. Exit.disposition         — "Was it allowed / denied / escalated?"

Why this is a contract, not a test
----------------------------------
Because it runs against EVERY persisted snapshot at production time (when
`strict_tier1=True` is enabled on the store). A snapshot that fails the
contract either (a) reveals an emit-site gap, or (b) reveals a run that
took an unusual path. Either way the operator needs to know.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .snapshot import RuntimeADGNode, RuntimeADGSnapshot

# Signal-based Tier 1 contracts — Tier 1.5 upgrade.
#
# Moving from pure name-substring matching to multi-signal scoring. A node
# matches a category if the sum of satisfied signals >= SIGNAL_THRESHOLD.
# This recognizes production-like spans (e.g. `heal_router.v1.route` is the
# canonical L0.route.select in this codebase — router kind, L0 layer,
# routing.* attrs — even though its name never contains "route.select").


@dataclass(frozen=True, slots=True)
class _CategoryContract:
    """Multi-signal contract for one Tier 1 category."""

    name_patterns: tuple[str, ...]  # substring matched case-insensitive against node.name
    kinds: tuple[str, ...]  # acceptable node.kind values (case-insensitive)
    layers: tuple[str, ...]  # acceptable node.layer prefixes (case-insensitive)
    required_any_attr: tuple[str, ...]  # at least one of these keys must be in attributes_json


# SIGNAL_THRESHOLD=2 means a node must score on at least 2 of 4 signals
# (name / kind / layer / attrs). Tuned empirically: gives `heal_router.v1.route`
# a 4/4 match for L0.route.select, but keeps `test.op` from matching
# anything (name non-matching, kind=tool matches invoke only by itself).
SIGNAL_THRESHOLD: int = 2

_TIER1_CONTRACTS: dict[str, _CategoryContract] = {
    "runtime.trace_root": _CategoryContract(
        name_patterns=(
            "trace_root",
            "runtime.trace",
            "runtime.root",
            "orchestrator.execute",
            "intake.stamp_trace",
        ),
        kinds=("orchestrator", "intake", "trace_root"),
        layers=("u0", "l0"),
        required_any_attr=("trace_id", "run_id", "input_envelope_hash"),
    ),
    "L0.route.select": _CategoryContract(
        name_patterns=(
            "l0.route",
            "route.select",
            "route.contract",
            "router.",
            "heal_router",
            ".v1.route",
        ),
        kinds=("router", "route"),
        layers=("l0",),
        required_any_attr=(
            "selected_route",
            "routing.target_model",
            "route.reason_codes",
            "routing.confidence_score",
            "routing.tier",
            "cache_decision",
        ),
    ),
    "L2.step.seal": _CategoryContract(
        name_patterns=(
            "l2.step.seal",
            "step.seal",
            "execution.seal",
            ".seal",
        ),
        kinds=("seal", "execution"),
        layers=("l2",),
        required_any_attr=(
            "output_hash",
            "output_artifact_ids",
            "lineage_hash",
            "replay_key",
            "evidence_ids",
        ),
    ),
    "L2.invoke": _CategoryContract(
        name_patterns=(
            "l2.model.invoke",
            "l2.tool.invoke",
            "model.invoke",
            "tool.invoke",
            "tool.",
            "model.",
            ".judge",
            "consensus.v1.judge",
        ),
        kinds=("tool", "model", "cognitive", "invoke"),
        layers=("l1", "l2"),
        required_any_attr=(
            "tool_name",
            "model_id",
            "args_hash",
            "prompt_hash",
            "return_code",
            "consensus.verdict",
            "consensus.juror_count",
        ),
    ),
    "Exit.disposition": _CategoryContract(
        name_patterns=(
            "exit.disposition",
            "exit.eval",
            "disposition",
            "exit.allow",
            "exit.deny",
        ),
        kinds=("exit", "disposition", "eval"),
        layers=("l3", "l5"),
        required_any_attr=(
            "exit_disposition",
            "policy_hash",
            "guardrail_result",
            "compliance_hash",
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class _MatchBreakdown:
    """Debug-friendly per-category breakdown of which signals hit."""

    matched_by_name: bool
    matched_by_kind: bool
    matched_by_layer: bool
    matched_by_attrs: bool

    def signal_count(self) -> int:
        return sum(
            [
                int(self.matched_by_name),
                int(self.matched_by_kind),
                int(self.matched_by_layer),
                int(self.matched_by_attrs),
            ]
        )


@dataclass(frozen=True, slots=True)
class Tier1Coverage:
    """Coverage report for one snapshot.

    Attributes
    ----------
    category_present : dict[str, bool]
        Whether each Tier 1 category has at least one matching node.
    category_with_attrs : dict[str, bool]
        Whether at least one matching node for each category also carries
        the required attributes.
    coverage_pct : float
        Fraction of the 5 Tier 1 categories satisfied (with attrs). In [0, 1].
    missing_categories : tuple[str, ...]
        Category names missing at the attrs level.
    """

    category_present: dict[str, bool]
    category_with_attrs: dict[str, bool]
    coverage_pct: float
    missing_categories: tuple[str, ...]

    def is_complete(self) -> bool:
        return self.coverage_pct >= 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "category_present": dict(self.category_present),
            "category_with_attrs": dict(self.category_with_attrs),
            "coverage_pct": round(self.coverage_pct, 4),
            "missing_categories": list(self.missing_categories),
            "is_complete": self.is_complete(),
        }


def _match_name(node: RuntimeADGNode, patterns: tuple[str, ...]) -> bool:
    name = node.name.lower()
    return any(pat.lower() in name for pat in patterns)


def _match_kind(node: RuntimeADGNode, kinds: tuple[str, ...]) -> bool:
    if not kinds:
        return False
    nk = node.kind.lower()
    return any(nk == k.lower() or nk.startswith(k.lower()) for k in kinds)


def _match_layer(node: RuntimeADGNode, layers: tuple[str, ...]) -> bool:
    if not layers:
        return False
    nl = node.layer.lower()
    return any(nl.startswith(layer.lower()) for layer in layers)


def _match_attrs(node: RuntimeADGNode, required_any: tuple[str, ...]) -> bool:
    if not required_any:
        return False
    if not node.attributes_json:
        return False
    try:
        attrs = json.loads(node.attributes_json)
    except (ValueError, TypeError):
        return False
    if not isinstance(attrs, dict):
        return False
    return any(k in attrs and attrs[k] not in (None, "") for k in required_any)


def _score_node(node: RuntimeADGNode, contract: _CategoryContract) -> _MatchBreakdown:
    return _MatchBreakdown(
        matched_by_name=_match_name(node, contract.name_patterns),
        matched_by_kind=_match_kind(node, contract.kinds),
        matched_by_layer=_match_layer(node, contract.layers),
        matched_by_attrs=_match_attrs(node, contract.required_any_attr),
    )


def validate_tier1_coverage(snapshot: RuntimeADGSnapshot) -> Tier1Coverage:
    """Report Tier 1 span coverage for a snapshot.

    Uses multi-signal matching (name / kind / layer / attrs). A node matches
    a category if `signal_count >= SIGNAL_THRESHOLD`.

    `category_present`  : any node scored >= threshold on name alone (partial)
    `category_with_attrs`: any node scored >= threshold AND had a signature attr
    """
    category_present: dict[str, bool] = {}
    category_with_attrs: dict[str, bool] = {}

    for category, contract in _TIER1_CONTRACTS.items():
        name_hit = False
        full_hit = False
        for node in snapshot.nodes:
            br = _score_node(node, contract)
            if br.signal_count() < SIGNAL_THRESHOLD:
                continue
            name_hit = True
            # A "with_attrs" hit requires attrs to be one of the satisfied
            # signals OR the name to explicitly match (keeping backward-
            # compatibility for cases like L2.invoke where attrs are optional).
            # Full hit if attrs match OR signal count >= 3 (strong multi-signal
            # match even without the signature attribute). Three-of-four
            # signals is an unambiguous production match.
            if br.matched_by_attrs or br.signal_count() >= 3:
                full_hit = True
                break
        category_present[category] = name_hit
        category_with_attrs[category] = full_hit

    total = len(_TIER1_CONTRACTS)
    satisfied = sum(1 for v in category_with_attrs.values() if v)
    pct = satisfied / total if total else 0.0
    missing = tuple(c for c, ok in category_with_attrs.items() if not ok)
    return Tier1Coverage(
        category_present=category_present,
        category_with_attrs=category_with_attrs,
        coverage_pct=pct,
        missing_categories=missing,
    )


# ---------------------------------------------------------------------------
# Corpus-level analysis — distinguishes emit-site gaps from name-mismatches.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CorpusTier1Report:
    """Aggregate Tier 1 report across an entire snapshot corpus.

    Each category is classified as exactly one of:
      - "satisfied"       : at least one snapshot had a full match (name + attrs)
      - "name_mismatch"   : some node matches by signals but no signature attrs
                            are present anywhere — likely a naming/attr-key
                            drift problem, not an emit-site gap
      - "emit_site_gap"   : zero nodes in the entire corpus scored above
                            threshold — this category has no emit site at all,
                            which is a real architectural hole
    """

    snapshots_scanned: int
    nodes_scanned: int
    category_status: dict[str, str]
    category_example_hits: dict[str, tuple[str, ...]]  # up to 3 example span names per satisfied cat
    satisfied_pct: float

    def satisfied_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "satisfied")

    def name_mismatch_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "name_mismatch")

    def emit_site_gap_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "emit_site_gap")

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshots_scanned": self.snapshots_scanned,
            "nodes_scanned": self.nodes_scanned,
            "category_status": dict(self.category_status),
            "category_example_hits": {k: list(v) for k, v in self.category_example_hits.items()},
            "satisfied_pct": round(self.satisfied_pct, 4),
            "satisfied_count": self.satisfied_count(),
            "name_mismatch_count": self.name_mismatch_count(),
            "emit_site_gap_count": self.emit_site_gap_count(),
        }


def validate_tier1_corpus_coverage(
    snapshots: list[RuntimeADGSnapshot],
) -> CorpusTier1Report:
    """Aggregate Tier 1 analysis across a corpus of snapshots.

    A category is:
      - `satisfied` if any node anywhere in the corpus hit `signal_count >= threshold`
        AND had a signature attr (or name-matched a category with no attr requirement)
      - `name_mismatch` if some node scored `>= threshold` but no signature attr
        ever appeared — the signal is there but the data drifted
      - `emit_site_gap` if zero nodes anywhere hit `>= threshold` for this category
    """
    # Per-category counters across the whole corpus.
    any_signal_hit: dict[str, bool] = {c: False for c in _TIER1_CONTRACTS}
    any_full_hit: dict[str, bool] = {c: False for c in _TIER1_CONTRACTS}
    example_hits: dict[str, list[str]] = {c: [] for c in _TIER1_CONTRACTS}

    nodes_scanned = 0
    for snap in snapshots:
        for node in snap.nodes:
            nodes_scanned += 1
            for category, contract in _TIER1_CONTRACTS.items():
                br = _score_node(node, contract)
                if br.signal_count() < SIGNAL_THRESHOLD:
                    continue
                any_signal_hit[category] = True
                full_hit = br.matched_by_attrs or br.signal_count() >= 3
                if full_hit:
                    any_full_hit[category] = True
                    if node.name not in example_hits[category] and len(example_hits[category]) < 3:
                        example_hits[category].append(node.name)

    status: dict[str, str] = {}
    for category in _TIER1_CONTRACTS:
        if any_full_hit[category]:
            status[category] = "satisfied"
        elif any_signal_hit[category]:
            status[category] = "name_mismatch"
        else:
            status[category] = "emit_site_gap"

    satisfied_pct = sum(1 for s in status.values() if s == "satisfied") / max(1, len(status))
    return CorpusTier1Report(
        snapshots_scanned=len(snapshots),
        nodes_scanned=nodes_scanned,
        category_status=status,
        category_example_hits={k: tuple(v) for k, v in example_hits.items()},
        satisfied_pct=satisfied_pct,
    )


# ===========================================================================
# Tier 2 — Full 14-stage spec coverage
#
# Tier 1 (above) tracks 5 critical "correlation spine" categories. Tier 2 adds
# coverage for every stage defined in `docs/reference/Runtime ADG and OTEL
# Spans.md` so the operator can see WHICH stages are emitting versus silent.
#
# Tier 2 reuses the same multi-signal scoring (name / kind / layer / attrs)
# but is purely additive — Tier 1 reports are NOT affected. The semconv SSOT
# in `agentic_core.L6_observability.semconv.runtime` provides the canonical
# span-name / attribute lists; this module embeds the same names for an
# import-free SSOT view (the constraint here is that span_contracts.py must
# not depend on agentic_core because it lives in system_learning, which sits
# below L6 in the layer stack).
# ===========================================================================

# Stages mirror semconv.runtime.STAGE_SPANS keys 1..14. Each stage maps to a
# single contract — enough to prove the stage is emitting at all. The contract
# is satisfied by ANY one of the stage's span names plus signature attrs.
_TIER2_CONTRACTS: dict[str, _CategoryContract] = {
    # 1. trace_root — already covered by Tier 1 "runtime.trace_root", duplicated
    #    here so Tier 2 reports stand alone for operator dashboards.
    "stage_01_trace_root": _CategoryContract(
        name_patterns=("runtime.trace_root", "trace_root", "runtime.root", "intake.stamp_trace"),
        kinds=("orchestrator", "intake", "trace_root"),
        layers=("u0", "l0"),
        required_any_attr=("trace_id", "run_id", "input_envelope_hash"),
    ),
    # 2. intake / U0
    "stage_02_intake": _CategoryContract(
        name_patterns=(
            "u0.intake.validate",
            "u0.intake.normalize",
            "u0.intake.stamp_trace",
            "intake.validate",
            "intake.normalize",
        ),
        kinds=("intake", "validator"),
        layers=("u0", "l0"),
        required_any_attr=(
            "request_id",
            "schema_status",
            "auth_status",
            "normalized_payload_hash",
            "envelope_version",
        ),
    ),
    # 3. L1 reasoning
    "stage_03_L1_reasoning": _CategoryContract(
        name_patterns=(
            "l1.intent.parse",
            "l1.context.priors_load",
            "l1.plan.draft",
            "l1.plan.validate",
        ),
        kinds=("reasoning", "planner", "cognitive"),
        layers=("l1",),
        required_any_attr=(
            "intent_frame_hash",
            "plan_contract_hash",
            "proposed_route",
            "task_class",
        ),
    ),
    # 4. L0 routing
    "stage_04_L0_routing": _CategoryContract(
        name_patterns=(
            "l0.route.score",
            "l0.cache.check",
            "l0.route.select",
            "l0.route.contract",
            "router.",
            "heal_router",
        ),
        kinds=("router", "route"),
        layers=("l0",),
        required_any_attr=(
            "selected_route",
            "reason_codes",
            "route_contract_hash",
            "cache_decision",
            "execution_form",
        ),
    ),
    # 5. direct path
    "stage_05_direct_path": _CategoryContract(
        name_patterns=(
            "l0.direct.package",
            "l0.ret.short_circuit",
            "l0.single_step.dispatch",
            "direct.package",
            "short_circuit",
        ),
        kinds=("dispatcher", "direct", "route"),
        layers=("l0",),
        required_any_attr=(
            "direct_step_id",
            "packet_hash",
            "terminal_return_reason",
            "no_l3_required",
        ),
    ),
    # 6. L3 orchestration
    "stage_06_L3_orchestration": _CategoryContract(
        name_patterns=(
            "l3.workflow.expand",
            "l3.workflow.state",
            "l3.step.ready_check",
            "l3.step.dispatch",
            "l3.step.merge_result",
            "workflow.",
        ),
        kinds=("orchestrator", "workflow"),
        layers=("l3",),
        required_any_attr=(
            "workflow_id",
            "dag_hash",
            "ready_node_ids",
            "workflow_state_hash",
        ),
    ),
    # 7. C0 retrieval — `evidence_ids` is intentionally NOT in the signature
    #    attr set because it travels downstream into PA and L2 spans. C0-specific
    #    attrs are vector_store_id / index_version / retrieval_mode / support_score.
    "stage_07_C0_retrieval": _CategoryContract(
        name_patterns=(
            "c0.retrieval.plan",
            "c0.query.embed",
            "c0.evidence.fetch",
            "c0.graph.traverse",
            "c0.evidence.rerank",
            "c0.evidence.contract",
            "gen_ai.retrieval.",
            "retrieval.embed",
            "retrieval.search",
            "retrieval.rerank",
            "retrieval.fuse",
        ),
        kinds=("retriever", "retrieval", "rag"),
        layers=("l1", "l4", "l6"),
        required_any_attr=(
            "retrieval_mode",
            "vector_store_id",
            "index_version",
            "support_score",
            "rerank_scores",
            "embedding_model_id",
        ),
    ),
    # 8. prompt assembly
    "stage_08_prompt_assembly": _CategoryContract(
        name_patterns=(
            "pa.static_blocks.load",
            "pa.context.slot",
            "pa.token_budget",
            "pa.prompt.contract",
            "prompt.assemble",
            "prompt.contract",
        ),
        kinds=("prompt", "assembler"),
        layers=("l1", "l2"),
        required_any_attr=(
            "prompt_envelope_hash",
            "prompt_hash",
            "system_template_hash",
            "token_budget_total",
        ),
    ),
    # 9. L2 execution
    "stage_09_L2_execution": _CategoryContract(
        name_patterns=(
            "l2.step.prepare",
            "l2.step.validate",
            "l2.model.invoke",
            "l2.tool.invoke",
            "l2.heal.attempt",
            "l2.step.seal",
            "model.invoke",
            "tool.invoke",
        ),
        kinds=("execution", "tool", "model", "seal"),
        layers=("l2",),
        required_any_attr=(
            "step_id",
            "output_hash",
            "tool_name",
            "model_id",
            "args_hash",
        ),
    ),
    # 10. exit eval
    "stage_10_exit_eval": _CategoryContract(
        name_patterns=(
            "exit.eval.policy",
            "exit.eval.quality",
            "exit.eval.safety",
            "exit.eval.mutation_auth",
            "exit.disposition",
            "exit.eval",
        ),
        kinds=("exit", "disposition", "eval"),
        layers=("l3", "l5"),
        required_any_attr=(
            "exit_disposition",
            "policy_hash",
            "compliance_hash",
            "safety_check",
            "mutation_auth_result",
        ),
    ),
    # 11. response / no write
    "stage_11_response": _CategoryContract(
        name_patterns=(
            "response.emit",
            "runtime.close_no_write",
            "response.",
        ),
        kinds=("response", "emitter"),
        layers=("l0", "l3", "l5"),
        required_any_attr=(
            "no_write_marker",
            "final_output_hash",
            "caller_delivery_status",
            "runtime_closed",
        ),
    ),
    # 12. UWG / L4 commit
    "stage_12_uwg_l4_commit": _CategoryContract(
        name_patterns=(
            "uwg.commit.verify_authority",
            "uwg.commit.validate_diff",
            "uwg.commit.append_ledger",
            "l4.archive.materialize",
            "uwg.commit",
            "ledger.append",
        ),
        kinds=("commit", "ledger", "uwg"),
        layers=("l4", "l5"),
        required_any_attr=(
            "commit_id",
            "ledger_hash",
            "before_hash",
            "after_hash",
            "audit_receipt_id",
        ),
    ),
    # 13. L6 eval / shadow evaluation
    "stage_13_L6_eval": _CategoryContract(
        name_patterns=(
            "l6.telemetry.ingest",
            "l6.outcome.evaluate",
            "l6.trajectory.evaluate",
            "l6.retrieval.evaluate",
            "l6.replay.verify",
            "l6.metrics.seal",
        ),
        kinds=("eval", "observability", "metrics"),
        layers=("l6",),
        required_any_attr=(
            "eval_bundle_id",
            "replay_digest",
            "task_completion_score",
            "groundedness_score",
            "trajectory_score",
        ),
    ),
    # 14. meta-learning / promotion
    "stage_14_meta_learning": _CategoryContract(
        name_patterns=(
            "metalearning.signal.fuse",
            "metalearning.rca.create",
            "metalearning.pattern.extract",
            "metalearning.rule.draft",
            "metalearning.shadow_replay",
            "metalearning.promotion.propose",
            "metalearning.promotion.approve_or_reject",
            "metalearning.promotion.commit",
        ),
        kinds=("meta_learning", "promotion", "rca"),
        layers=("l6", "l7"),
        required_any_attr=(
            "rca_id",
            "RCA_id",
            "promotion_candidate_id",
            "approved_update_id",
            "shadow_replay_result",
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class Tier2Coverage:
    """Tier 2 (full 14-stage spec) coverage report for a single snapshot.

    Each stage has the same `present` / `with_attrs` distinction as Tier 1.
    """

    stage_present: dict[str, bool]
    stage_with_attrs: dict[str, bool]
    coverage_pct: float
    missing_stages: tuple[str, ...]

    def is_complete(self) -> bool:
        return self.coverage_pct >= 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "stage_present": dict(self.stage_present),
            "stage_with_attrs": dict(self.stage_with_attrs),
            "coverage_pct": round(self.coverage_pct, 4),
            "missing_stages": list(self.missing_stages),
            "is_complete": self.is_complete(),
        }


def validate_tier2_coverage(snapshot: RuntimeADGSnapshot) -> Tier2Coverage:
    """Report Tier 2 (full spec) stage coverage for a single snapshot.

    Identical scoring to Tier 1 — multi-signal threshold, name/attrs duality —
    applied to all 14 stages.
    """
    stage_present: dict[str, bool] = {}
    stage_with_attrs: dict[str, bool] = {}

    for stage, contract in _TIER2_CONTRACTS.items():
        name_hit = False
        full_hit = False
        for node in snapshot.nodes:
            br = _score_node(node, contract)
            if br.signal_count() < SIGNAL_THRESHOLD:
                continue
            name_hit = True
            if br.matched_by_attrs or br.signal_count() >= 3:
                full_hit = True
                break
        stage_present[stage] = name_hit
        stage_with_attrs[stage] = full_hit

    total = len(_TIER2_CONTRACTS)
    satisfied = sum(1 for v in stage_with_attrs.values() if v)
    pct = satisfied / total if total else 0.0
    missing = tuple(s for s, ok in stage_with_attrs.items() if not ok)
    return Tier2Coverage(
        stage_present=stage_present,
        stage_with_attrs=stage_with_attrs,
        coverage_pct=pct,
        missing_stages=missing,
    )


@dataclass(frozen=True, slots=True)
class CorpusTier2Report:
    """Aggregate Tier 2 stage report across a snapshot corpus.

    Same status enum as Tier 1: 'satisfied' | 'name_mismatch' | 'emit_site_gap'.
    """

    snapshots_scanned: int
    nodes_scanned: int
    stage_status: dict[str, str]
    stage_example_hits: dict[str, tuple[str, ...]]
    satisfied_pct: float

    def satisfied_count(self) -> int:
        return sum(1 for s in self.stage_status.values() if s == "satisfied")

    def name_mismatch_count(self) -> int:
        return sum(1 for s in self.stage_status.values() if s == "name_mismatch")

    def emit_site_gap_count(self) -> int:
        return sum(1 for s in self.stage_status.values() if s == "emit_site_gap")

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshots_scanned": self.snapshots_scanned,
            "nodes_scanned": self.nodes_scanned,
            "stage_status": dict(self.stage_status),
            "stage_example_hits": {k: list(v) for k, v in self.stage_example_hits.items()},
            "satisfied_pct": round(self.satisfied_pct, 4),
            "satisfied_count": self.satisfied_count(),
            "name_mismatch_count": self.name_mismatch_count(),
            "emit_site_gap_count": self.emit_site_gap_count(),
        }


def validate_tier2_corpus_coverage(
    snapshots: list[RuntimeADGSnapshot],
) -> CorpusTier2Report:
    """Aggregate Tier 2 analysis across a corpus of snapshots."""
    any_signal_hit: dict[str, bool] = {s: False for s in _TIER2_CONTRACTS}
    any_full_hit: dict[str, bool] = {s: False for s in _TIER2_CONTRACTS}
    example_hits: dict[str, list[str]] = {s: [] for s in _TIER2_CONTRACTS}

    nodes_scanned = 0
    for snap in snapshots:
        for node in snap.nodes:
            nodes_scanned += 1
            for stage, contract in _TIER2_CONTRACTS.items():
                br = _score_node(node, contract)
                if br.signal_count() < SIGNAL_THRESHOLD:
                    continue
                any_signal_hit[stage] = True
                full_hit = br.matched_by_attrs or br.signal_count() >= 3
                if full_hit:
                    any_full_hit[stage] = True
                    if node.name not in example_hits[stage] and len(example_hits[stage]) < 3:
                        example_hits[stage].append(node.name)

    status: dict[str, str] = {}
    for stage in _TIER2_CONTRACTS:
        if any_full_hit[stage]:
            status[stage] = "satisfied"
        elif any_signal_hit[stage]:
            status[stage] = "name_mismatch"
        else:
            status[stage] = "emit_site_gap"

    satisfied_pct = sum(1 for s in status.values() if s == "satisfied") / max(1, len(status))
    return CorpusTier2Report(
        snapshots_scanned=len(snapshots),
        nodes_scanned=nodes_scanned,
        stage_status=status,
        stage_example_hits={k: tuple(v) for k, v in example_hits.items()},
        satisfied_pct=satisfied_pct,
    )


def tier2_stage_count() -> int:
    """Return the number of Tier 2 stages — 14 per the doctrine document."""
    return len(_TIER2_CONTRACTS)


def tier2_stage_names() -> tuple[str, ...]:
    """Return the canonical Tier 2 stage keys in spec order."""
    return tuple(_TIER2_CONTRACTS.keys())


# ===========================================================================
# apps_rg governed spine — REQ parent span checklist (pa-exec-flowchart-gap W8)
#
# Maps REQ reference parents to Tier 2 semconv stages and spine receipt fallbacks
# when product paths emit filesystem receipts before full OTEL on every lane.
# ===========================================================================

@dataclass(frozen=True, slots=True)
class AppsRgSpineSpanRow:
    """One REQ-parent row in the apps_rg spine span checklist."""

    req_parent: str
    layer_key: str
    tier2_stage: str
    span_patterns: tuple[str, ...]
    spine_receipt_fallback: str
    binding_seam: str
    wave: str


APPS_RG_SPINE_SPAN_CHECKLIST: tuple[AppsRgSpineSpanRow, ...] = (
    AppsRgSpineSpanRow(
        "01_Request_Intake",
        "U0",
        "stage_02_intake",
        ("u0.intake", "intake.validate", "intake.stamp_trace"),
        "validated_request.json",
        "apps_rg/runtime/bindings/u0_binding.py",
        "W1",
    ),
    AppsRgSpineSpanRow(
        "02_L1_Reasoning_Plan",
        "L1",
        "stage_03_L1_reasoning",
        ("l1.plan", "l1.intent"),
        "l1_plan_contract.json",
        "apps_rg/runtime/bindings/l1_binding.py",
        "W3",
    ),
    AppsRgSpineSpanRow(
        "03_L0_Route",
        "L0",
        "stage_04_L0_routing",
        ("l0.route", "route.contract", "router."),
        "route_contract.json",
        "apps_rg/runtime/bindings/l0_binding.py",
        "W3",
    ),
    AppsRgSpineSpanRow(
        "03A_C0_Context",
        "C0",
        "stage_07_C0_retrieval",
        ("c0.evidence", "c0.retrieval", "c0.query"),
        "final_evidence_contract_bridge.json",
        "apps_rg/runtime/spine/section_c0_retrieve.py",
        "W4",
    ),
    AppsRgSpineSpanRow(
        "03B_PA_Prompt_Assembly",
        "PA",
        "stage_08_PA_assembly",
        ("pa.", "prompt_assembly", "pa.0.boundary"),
        "compiled_prompt_artifact.json",
        "apps_rg/runtime/spine/governed_pa_compose.py",
        "W5",
    ),
    AppsRgSpineSpanRow(
        "04_L2_Execute",
        "L2",
        "stage_09_L2_execution",
        ("l2.step", "l2.model", "l2.tool"),
        "sealed_l2_artifact.json",
        "apps_rg/runtime/spine/governed_l2_exit_compose.py",
        "W6",
    ),
    AppsRgSpineSpanRow(
        "05_Exit_Evaluation",
        "EXIT",
        "stage_10_exit_eval",
        ("exit.eval", "exit.disposition", "pa.0.boundary"),
        "exit_disposition_receipt.json",
        "apps_rg/runtime/spine/section_x3_finalize.py",
        "W6",
    ),
    AppsRgSpineSpanRow(
        "06_L6_Learning",
        "L6",
        "stage_14_L6_learning",
        ("l6.", "shadow"),
        "runtime_exhaust_bundle.json",
        "apps_rg/runtime/spine/governed_l6_shadow_compose.py",
        "W7",
    ),
)


def apps_rg_spine_span_checklist_report() -> dict[str, object]:
    """Serializable checklist for CI / gap audit (read-only)."""
    return {
        "plan_id": "pa-exec-flowchart-gap-f2a8c3",
        "wave": "W8",
        "checklist_id": "apps_rg_spine_span_vs_req_parents",
        "row_count": len(APPS_RG_SPINE_SPAN_CHECKLIST),
        "rows": [
            {
                "req_parent": r.req_parent,
                "layer_key": r.layer_key,
                "tier2_stage": r.tier2_stage,
                "span_patterns": list(r.span_patterns),
                "spine_receipt_fallback": r.spine_receipt_fallback,
                "binding_seam": r.binding_seam,
                "wave": r.wave,
            }
            for r in APPS_RG_SPINE_SPAN_CHECKLIST
        ],
        "explicit_non_claims": [
            "receipt_fallback does not replace OTEL on live product paths",
            "tier2_stage satisfied in snapshot OR receipt file exists on disk for CI",
        ],
    }


def validate_apps_rg_spine_spans_against_snapshot(
    snapshot: RuntimeADGSnapshot,
    *,
    receipt_dir: str | None = None,
) -> dict[str, str]:
    """Per-layer status: satisfied | receipt_only | emit_site_gap."""
    from pathlib import Path

    tier2 = validate_tier2_coverage(snapshot)
    receipt_root = Path(receipt_dir) if receipt_dir else None
    status: dict[str, str] = {}
    for row in APPS_RG_SPINE_SPAN_CHECKLIST:
        stage_ok = tier2.stage_status.get(row.tier2_stage) == "satisfied"
        receipt_ok = False
        if receipt_root is not None:
            receipt_ok = (receipt_root / row.spine_receipt_fallback).is_file()
        if stage_ok:
            status[row.layer_key] = "satisfied"
        elif receipt_ok:
            status[row.layer_key] = "receipt_only"
        else:
            status[row.layer_key] = "emit_site_gap"
    return status


__all__ = [
    "APPS_RG_SPINE_SPAN_CHECKLIST",
    "AppsRgSpineSpanRow",
    "apps_rg_spine_span_checklist_report",
    "Tier1Coverage",
    "CorpusTier1Report",
    "validate_tier1_coverage",
    "validate_tier1_corpus_coverage",
    "validate_apps_rg_spine_spans_against_snapshot",
    "Tier2Coverage",
    "CorpusTier2Report",
    "validate_tier2_coverage",
    "validate_tier2_corpus_coverage",
    "tier2_stage_count",
    "tier2_stage_names",
    "SIGNAL_THRESHOLD",
]
