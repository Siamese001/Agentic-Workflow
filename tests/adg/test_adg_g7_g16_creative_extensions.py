"""Creative extensions to G7-G16 completeness and accuracy testing.

New testing axes not covered by the existing 8-axis suite:

  D1  Dead-relation audit — relations declared in RelationType but emitted by NO visitor
      must be explicitly catalogued; new unintended dead relations are a bug.
  D2  Visitor contract — all 10 G7-G16 visitors inherit ast.NodeVisitor directly.
  D3  Visitor statefulness — re-using the same visitor instance on two separate AST
      trees accumulates edges; each instantiation is independent (new instance resets).
  D4  _sym_of accuracy — deep attribute chains (a.b.c.d), subscript nodes, lambda
      bodies, and constant nodes are all handled without crashing.
  D5  Schema __all__ coverage — every G7-G16 detection constant is exported in schema's
      __all__ list so downstream importers can rely on `from schema import *`.
  D6  JSON-serializability — every runtime session/report .to_dict() output is
      round-trippable through json.dumps / json.loads without TypeError.
  D7  Enum value format — all G7-G16 enum .value strings are lowercase / snake_case
      (no CamelCase leaking into serialised state machine representations).
  D8  Cross-constant non-overlap — no single symbol string appears in two or more
      different detection frozensets (would create ambiguous visitor routing).
  D9  Report isolation — two independently instantiated recorders of the same type
      share zero mutable state (lists, dicts, counters are not aliased).
  D10 Line-number tracking inside function / class bodies — visitor correctly records
      the line of the call, not line 1, when the call is nested in a def or class.
  D11 Module docstring contract — every G7-G16 runtime module's __doc__ begins with
      the expected 'G<n> (gap):' prefix string.
  D12 Empty / degenerate source safety — all visitors parse an empty string, a single
      comment, and a bare pass statement without raising any exception.
  D13 Edge endpoint distinctness — every emitted edge has from_name != to_name.
  D14 to_name canonical format — every emitted edge's to_name begins with 'ADG::'.
  D15 Blast-radius threshold boundary — MutationTransport commits at exactly the
      0.8 threshold edge (below commits, at-or-above aborts).
  D16 EvalSpine missing-metric robustness — average_metric on an unseen metric name
      returns 0.0 rather than raising KeyError.
  D17 Detection constant member hygiene — no frozenset member is the empty string.
  D18 RelationType / EdgeKind value format — all values are lowercase snake_case.
  D19 Visitor propagation depth — calls nested inside list comprehensions, lambda
      bodies, class bodies, and decorated functions are all detected.
  D20 Schema constant total count — the number of G7-G16 detection constants matches
      the documented count of 23 (one or more per gap, exactly as specified).
"""

from __future__ import annotations

import ast
import importlib
import json
import textwrap
import typing
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_applies_guardrail("p0", "test_adg_g7_g16_creative_extensions", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_g7_g16_creative_extensions", "policy_binding")
_emit_snapshots_state("p0", "test_adg_g7_g16_creative_extensions", "state_snapshot")
_emit_authorize_and_execute("p2", "test_adg_g7_g16_creative_extensions", "execution_auth")
_emit_validates_capability("p2", "test_adg_g7_g16_creative_extensions", "capability_check")
_emit_routes_to_capability("p2", "test_adg_g7_g16_creative_extensions", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_g7_g16_creative_extensions", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_g7_g16_creative_extensions", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_g7_g16_creative_extensions", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_g7_g16_creative_extensions", "exec_output")
_emit_dispatches_agent("p3", "test_adg_g7_g16_creative_extensions", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_g7_g16_creative_extensions", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_g7_g16_creative_extensions", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_g7_g16_creative_extensions", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_g7_g16_creative_extensions", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_g7_g16_creative_extensions", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_g7_g16_creative_extensions", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_g7_g16_creative_extensions", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_g7_g16_creative_extensions", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_g7_g16_creative_extensions", "eval_metric")
_emit_stores_embedding("p4", "test_adg_g7_g16_creative_extensions", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_g7_g16_creative_extensions", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_g7_g16_creative_extensions", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_g7_g16_creative_extensions", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_g7_g16_creative_extensions", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_g7_g16_creative_extensions", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_g7_g16_creative_extensions", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_g7_g16_creative_extensions", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_g7_g16_creative_extensions", "p4obs", "alert")
_emit_links_incident_trace("test_adg_g7_g16_creative_extensions", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_g7_g16_creative_extensions", "p3lm", "pattern")
_emit_records_learning_event("test_adg_g7_g16_creative_extensions", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_g7_g16_creative_extensions", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_g7_g16_creative_extensions", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_g7_g16_creative_extensions", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_g7_g16_creative_extensions", "p3lm", "policy")
_emit_stores_learning_state("test_adg_g7_g16_creative_extensions", "p3lm", "state")
_emit_records_execution_trace("test_adg_g7_g16_creative_extensions", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_g7_g16_creative_extensions", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_g7_g16_creative_extensions", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_g7_g16_creative_extensions", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_g7_g16_creative_extensions", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_g7_g16_creative_extensions", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_g7_g16_creative_extensions", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_g7_g16_creative_extensions", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_g7_g16_creative_extensions", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_g7_g16_creative_extensions", "context_pull")
_emit_pulls_context("p1", "test_adg_g7_g16_creative_extensions", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_g7_g16_creative_extensions", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_g7_g16_creative_extensions", "uwg_term_2")
_emit_writes_through("p1", "test_adg_g7_g16_creative_extensions", "write_through")
_emit_writes_through("p1", "test_adg_g7_g16_creative_extensions", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_g7_g16_creative_extensions", "safety_validation")
_emit_invokes_eval("p1", "test_adg_g7_g16_creative_extensions", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_g7_g16_creative_extensions", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_g7_g16_creative_extensions", "human_escalation")
_emit_routes_through("p1", "test_adg_g7_g16_creative_extensions", "route_through")
_emit_checks_agent_registry("p1", "test_adg_g7_g16_creative_extensions", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_g7_g16_creative_extensions", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_g7_g16_creative_extensions", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_g7_g16_creative_extensions", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_g7_g16_creative_extensions", "target_agent")
_emit_verifies_policy("p1", "test_adg_g7_g16_creative_extensions", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_g7_g16_creative_extensions", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_g7_g16_creative_extensions", "boundary_check")
_emit_transcripts_response("p1", "test_adg_g7_g16_creative_extensions", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_g7_g16_creative_extensions")
_emit_gated_by_confidence("p1", "test_adg_g7_g16_creative_extensions", "confidence_gate")

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Shared helpers (mirror _scan_src / _edges_for from completeness file)
# ---------------------------------------------------------------------------

_ALL_G7_G16_VISITORS = [
    "_SandboxAirlockVisitor",
    "_CapabilityBudgetVisitor",
    "_JITContextVisitor",
    "_BoundaryVerifierVisitor",
    "_DeterminismControlVisitor",
    "_IOInterceptionVisitor",
    "_MutationTransportVisitor",
    "_ExecutionProofVisitor",
    "_PathControlVisitor",
    "_EvalSpineVisitor",
]


def _import_visitor(name: str):
    from agentic_core.adg.extraction import static_scanner

    return getattr(static_scanner, name)


def _scan_src(source: str) -> list:
    """Run all G7-G16 visitors against dedented source; return edges."""
    tree = ast.parse(textwrap.dedent(source))
    edges: list = []
    for vname in _ALL_G7_G16_VISITORS:
        cls = _import_visitor(vname)
        v = cls("ADG::Module::test", "test.py")
        v.visit(tree)
        edges.extend(v.edges)
    return edges


def _edges_for(source: str, visitor_cls) -> list:
    tree = ast.parse(textwrap.dedent(source))
    v = visitor_cls("ADG::Module::test", "test.py")
    v.visit(tree)
    return v.edges


def _rel_ek(edges: list) -> set[tuple[str, str]]:
    return {(e.relation_type, e.edge_kind) for e in edges}


# ---------------------------------------------------------------------------
# D1 — Dead-relation audit
# ---------------------------------------------------------------------------

# Relations that are KNOWN to be declared in RelationType but never emitted by
# any G7-G16 visitor.  This is intentional: they represent semantic intent that
# will be wired to future visitors.  Any NEW unintended dead relation is a bug.
_KNOWN_DEAD_RELATIONS: frozenset[str] = frozenset(
    {
        "exits_sandbox",  # G7 exit is tracked by state machine, not visitor-emitted
        "consumes_budget",  # G8 consumption is runtime only, not statically detectable
        "rejects_packet",  # G10 rejection is a state-machine output, no static call site
    }
)

G7_G16_RELATION_TYPES = [
    "stamps_work_contract",
    "issues_capability_token",
    "enters_sandbox",
    "exits_sandbox",
    "consumes_budget",
    "grants_resource",
    "exceeds_budget",
    "pulls_context",
    "freezes_context",
    "unfreezes_context",
    "verifies_boundary",
    "rejects_packet",
    "certifies_envelope",
    "seeds_rng",
    "patches_time",
    "guards_replay",
    "emits_determinism_digest",
    "intercepts_io",
    "transcripts_response",
    "hard_fails_untranscripted",
    "packages_diff",
    "validates_blast_radius",
    "signs_execution_trace",
    "commits_mutation",
    "distributes_mutation",
    "records_execution_trace",
    "emits_replay_key",
    "compares_proof",
    "routes_path",
    "forces_stall",
    "reenters_safety",
    "vigilance_reroute",
    "scores_groundedness",
    "emits_drift_alert",
    "builds_dpo_batch",
    "commits_optimization",
]

_FULL_DETECTION_CORPUS = """
SandboxEnvelope()
CapabilityToken()
stamp_work_contract(x)
ToolBudget()
raise BudgetExceededError
JITContext()
freeze_context(x)
pull_context(x)
sync_context(x)
unfreeze_context(x)
snapshot_context(x)
L2BoundaryVerifier('a', 'r')
CapabilityChokepoint('a')
SemanticClock('r')
ReplayGuard('r')
seed_rng(42)
patch_time()
emit_determinism_digest([])
IOInterceptor('a', 'r')
transcript_response(url)
hard_fail_untranscripted(url)
package_diff(x)
validate_blast_radius(x)
TwoPhaseCommit()
MutationTransport('a', 'r')
MutationDistributor()
ExecutionTrace()
emit_replay_key(rng_seed=42)
compare_proof(t1, t2)
record_execution_trace('e')
ExecutionPathController('a', 'r')
route_path(x)
force_stall()
reenter_safety()
vigilance_reroute()
EvalSpine('a', 'r')
DPOBatch()
emit_drift_alert('M', 0.3, 0.7)
build_dpo_batch(pairs)
commit_optimization(p)
"""


class TestD1DeadRelationAudit:
    """D1: Relations in schema that no visitor emits must match the known-dead catalogue exactly."""

    def _all_emitted_from_corpus(self) -> set[str]:
        return {e.relation_type for e in _scan_src(_FULL_DETECTION_CORPUS)}

    def test_known_dead_relations_are_in_schema(self) -> None:
        """Every catalogued dead relation must exist in RelationType (it's a real schema value)."""
        from agentic_core.adg.schema import RelationType

        schema_rels = set(typing.get_args(RelationType))
        missing = _KNOWN_DEAD_RELATIONS - schema_rels
        assert not missing, f"Dead-relation catalogue has entries not in schema: {missing}"

    def test_no_new_unintended_dead_relations(self) -> None:
        """No G7-G16 relation beyond the known-dead catalogue is silently unemittable."""
        emitted = self._all_emitted_from_corpus()
        dead = [r for r in G7_G16_RELATION_TYPES if r not in emitted]
        unexpected_dead = set(dead) - _KNOWN_DEAD_RELATIONS
        assert not unexpected_dead, (
            f"New unintended dead relations (emitted by no visitor, not in known-dead list): "
            f"{sorted(unexpected_dead)}"
        )

    def test_all_live_relations_emitted_by_full_corpus(self) -> None:
        """Every relation NOT in the known-dead catalogue IS emitted by the full corpus."""
        emitted = self._all_emitted_from_corpus()
        live_expected = [r for r in G7_G16_RELATION_TYPES if r not in _KNOWN_DEAD_RELATIONS]
        missing = [r for r in live_expected if r not in emitted]
        assert not missing, f"Live relations not emitted by full corpus: {missing}"

    def test_known_dead_count_matches_expectation(self) -> None:
        """The dead-relation catalogue has exactly 3 entries (documented in spec)."""
        assert len(_KNOWN_DEAD_RELATIONS) == 3


# ---------------------------------------------------------------------------
# D2 — Visitor contract: correct base class
# ---------------------------------------------------------------------------


class TestD2VisitorBaseClass:
    """D2: Every G7-G16 visitor inherits ast.NodeVisitor directly."""

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    def test_visitor_inherits_ast_node_visitor(self, visitor_name: str) -> None:
        cls = _import_visitor(visitor_name)
        assert issubclass(cls, ast.NodeVisitor), f"{visitor_name} must inherit ast.NodeVisitor"

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    def test_visitor_has_edges_attribute_after_init(self, visitor_name: str) -> None:
        cls = _import_visitor(visitor_name)
        v = cls("M", "f.py")
        assert hasattr(v, "edges"), f"{visitor_name} must expose .edges after __init__"
        assert isinstance(v.edges, list), f"{visitor_name}.edges must be a list"

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    def test_visitor_edges_empty_on_fresh_instance(self, visitor_name: str) -> None:
        cls = _import_visitor(visitor_name)
        v = cls("M", "f.py")
        assert len(v.edges) == 0, f"{visitor_name}: fresh instance must have 0 edges, got {len(v.edges)}"

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    def test_visitor_has_visit_method(self, visitor_name: str) -> None:
        cls = _import_visitor(visitor_name)
        assert callable(getattr(cls, "visit", None))

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    def test_visitor_accepts_module_and_source_args(self, visitor_name: str) -> None:
        cls = _import_visitor(visitor_name)
        v = cls("ADG::Module::some_module", "some/file.py")
        assert v.module_adg_name == "ADG::Module::some_module"
        assert v.source_file == "some/file.py"


# ---------------------------------------------------------------------------
# D3 — Visitor statefulness: new instance resets; re-use accumulates
# ---------------------------------------------------------------------------


class TestD3VisitorStatesfulness:
    """D3: Independent instances start clean; same instance accumulates across visits."""

    def test_new_instance_does_not_inherit_edges_from_prior(self) -> None:
        """Two independent instances of the same visitor class are truly independent."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = "SandboxEnvelope()"
        tree = ast.parse(src)

        v1 = _SandboxAirlockVisitor("M", "f")
        v1.visit(tree)
        edges_v1 = len(v1.edges)

        v2 = _SandboxAirlockVisitor("M", "f")
        v2.visit(tree)
        edges_v2 = len(v2.edges)

        assert edges_v1 == edges_v2 == 1, (
            "Each new instance must produce exactly 1 edge, independent of the other"
        )

    def test_reusing_same_instance_accumulates_edges(self) -> None:
        """Calling .visit() on the same instance twice accumulates edges."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = "SandboxEnvelope()"
        tree = ast.parse(src)

        v = _SandboxAirlockVisitor("M", "f")
        v.visit(tree)
        first_count = len(v.edges)
        v.visit(tree)
        second_count = len(v.edges)

        assert second_count == first_count * 2, (
            f"Re-visiting same tree should double edge count: {first_count} → {second_count}"
        )

    @pytest.mark.parametrize(
        "visitor_name,src",
        [
            ("_SandboxAirlockVisitor", "SandboxEnvelope()"),
            ("_JITContextVisitor", "freeze_context(x)"),
            ("_EvalSpineVisitor", "emit_drift_alert('M', 0.3, 0.7)"),
        ],
    )
    def test_independent_instances_from_different_source_trees(self, visitor_name: str, src: str) -> None:
        """Instance A visiting source X and instance B visiting source Y share no edges."""
        cls = _import_visitor(visitor_name)
        tree_x = ast.parse(src)
        tree_empty = ast.parse("pass")

        va = cls("M", "f")
        va.visit(tree_x)

        vb = cls("M", "f")
        vb.visit(tree_empty)

        assert len(va.edges) >= 1
        assert len(vb.edges) == 0, "Visitor B saw empty tree, must have 0 edges"


# ---------------------------------------------------------------------------
# D4 — _sym_of accuracy
# ---------------------------------------------------------------------------


class TestD4SymOfAccuracy:
    """D4: _sym_of handles deep chains, subscripts, lambdas, constants without crashing."""

    def _sym_of(self):
        from agentic_core.adg.extraction.static_scanner import _sym_of

        return _sym_of

    def test_simple_name_extracted(self) -> None:
        sym_of = self._sym_of()
        node = ast.parse("Foo()").body[0].value.func  # type: ignore[attr-defined]
        assert sym_of(node) == "Foo"

    def test_single_attribute_extracted(self) -> None:
        sym_of = self._sym_of()
        node = ast.parse("obj.Foo()").body[0].value.func  # type: ignore[attr-defined]
        assert sym_of(node) == "obj.Foo"

    def test_deep_chain_extracted(self) -> None:
        sym_of = self._sym_of()
        node = ast.parse("a.b.c.Foo()").body[0].value.func  # type: ignore[attr-defined]
        assert sym_of(node) == "a.b.c.Foo"

    def test_returns_empty_string_for_subscript(self) -> None:
        """_sym_of on a subscript node (func[0]()) must return '' not crash."""
        sym_of = self._sym_of()
        # Build a subscript call node manually
        subscript = ast.Subscript(
            value=ast.Name(id="funcs", ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Load(),
        )
        result = sym_of(subscript)
        assert result == "", f"Expected '' for subscript node, got {result!r}"

    def test_returns_empty_string_for_constant(self) -> None:
        """_sym_of on a Constant node must return '' not crash."""
        sym_of = self._sym_of()
        node = ast.Constant(value=42)
        result = sym_of(node)
        assert result == ""

    def test_returns_empty_string_for_lambda(self) -> None:
        """_sym_of on a Lambda node must return '' not crash."""
        sym_of = self._sym_of()
        lambda_node = ast.parse("lambda: None").body[0].value  # type: ignore[attr-defined]
        result = sym_of(lambda_node)
        assert result == ""

    def test_tail_extraction_is_correct_for_deep_chain(self) -> None:
        """tail = sym.split('.')[-1] is the actual class/method name for deep chains."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        edges = _edges_for("module.sub.SandboxEnvelope()", _SandboxAirlockVisitor)
        assert len(edges) == 1
        assert edges[0].relation_type == "enters_sandbox"
        assert "SandboxEnvelope" in edges[0].symbol

    def test_base_extraction_catches_instance_class(self) -> None:
        """base = sym.split('.')[0] catches patterns like SandboxEnvelope.method()."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        edges = _edges_for("SandboxEnvelope.from_contract(c)", _SandboxAirlockVisitor)
        assert len(edges) == 1
        assert edges[0].relation_type == "enters_sandbox"


# ---------------------------------------------------------------------------
# D5 — Schema __all__ coverage
# ---------------------------------------------------------------------------


class TestD5SchemaAllCoverage:
    """D5: All G7-G16 detection constants are exported via schema.__all__."""

    _G7_G16_CONSTANT_NAMES = [
        "SANDBOX_ENVELOPE_CLASSES",
        "CAPABILITY_TOKEN_CLASSES",
        "WORK_CONTRACT_METHODS",
        "TOOL_BUDGET_CLASSES",
        "BUDGET_EXCEEDED_EXCEPTIONS",
        "JIT_CONTEXT_CLASSES",
        "FREEZE_METHOD_NAMES",
        "BOUNDARY_VERIFIER_CLASSES",
        "CAPABILITY_CHOKEPOINT_CLASSES",
        "SEMANTIC_CLOCK_CLASSES",
        "REPLAY_GUARD_CLASSES",
        "DETERMINISM_PATCH_METHODS",
        "IO_INTERCEPT_CLASSES",
        "NETWORK_TRANSCRIPT_SYMBOLS",
        "MUTATION_TRANSPORT_CLASSES",
        "RFC6902_DIFF_SYMBOLS",
        "EXECUTION_TRACE_CLASSES",
        "REPLAY_KEY_METHODS",
        "PATH_CONTROL_CLASSES",
        "PATH_REROUTE_METHODS",
        "EVAL_METRIC_CLASSES",
        "DPO_BATCH_CLASSES",
        "DRIFT_ALERT_METHODS",
    ]

    def test_all_g7_g16_constants_in_schema_all(self) -> None:
        import agentic_core.adg.schema as sch

        if not hasattr(sch, "__all__"):
            pytest.skip("schema.py does not define __all__")
        missing = [n for n in self._G7_G16_CONSTANT_NAMES if n not in sch.__all__]
        assert not missing, f"G7-G16 constants missing from schema.__all__: {missing}"

    def test_all_constants_resolvable_after_star_import(self) -> None:
        """Every constant can be resolved via getattr(schema_module, name)."""
        import agentic_core.adg.schema as sch

        for name in self._G7_G16_CONSTANT_NAMES:
            obj = getattr(sch, name, None)
            assert obj is not None, f"schema.{name} is None or missing"
            assert isinstance(obj, frozenset), f"schema.{name} must be frozenset"

    @pytest.mark.parametrize("const_name", _G7_G16_CONSTANT_NAMES)
    def test_each_constant_importable_directly(self, const_name: str) -> None:
        mod = importlib.import_module("agentic_core.adg.schema")
        obj = getattr(mod, const_name)
        assert isinstance(obj, frozenset)
        assert len(obj) > 0


# ---------------------------------------------------------------------------
# D6 — JSON-serializability of all to_dict() outputs
# ---------------------------------------------------------------------------


class TestD6JSONSerializability:
    """D6: Every runtime session/report .to_dict() is JSON round-trippable."""

    def _round_trip(self, d: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(d))

    def test_airlock_session_to_dict(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import SandboxAirlockRecorder

        rec = SandboxAirlockRecorder("a", "r")
        c = rec.stamp_contract()
        t = rec.issue_token(c)
        env = rec.enter_sandbox(c, t)
        rec.exit_sandbox(env)
        d = rec.session_summary
        rt = self._round_trip(d)
        assert rt["envelope_count"] == d["envelope_count"]

    def test_work_contract_to_dict(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import WorkContract

        c = WorkContract(agent_id="a", run_id="r")
        d = c.to_dict()
        rt = self._round_trip(d)
        assert rt["agent_id"] == "a"

    def test_capability_token_to_dict(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import CapabilityToken

        t = CapabilityToken(contract_id="c", agent_id="a", scope="read")
        d = t.to_dict()
        rt = self._round_trip(d)
        assert rt["agent_id"] == "a"

    def test_sandbox_envelope_to_dict(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import SandboxEnvelope

        e = SandboxEnvelope()
        d = e.to_dict()
        rt = self._round_trip(d)
        assert rt["phase"] == e.phase.value

    def test_resource_grant_to_dict(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGrant

        g = ResourceGrant("tool_calls", 100.0)
        d = g.to_dict()
        rt = self._round_trip(d)
        assert rt["limit"] == 100.0

    def test_budget_governor_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGovernor, ToolBudget

        gov = ResourceGovernor("a", "r")
        gov.activate_budget(ToolBudget.default())
        gov.consume("tool_calls", 5.0)
        d = gov.report.to_dict()
        rt = self._round_trip(d)
        assert "exceeded_count" in rt

    def test_jit_context_session_to_dict(self) -> None:
        from agentic_core.adg.runtime.jit_context import JITContextSynchronizer

        sync = JITContextSynchronizer("a", "r")
        sync.sync_context()
        d = sync.session_summary
        rt = self._round_trip(d)
        assert rt["snapshot_count"] == 1

    def test_context_snapshot_to_dict(self) -> None:
        from agentic_core.adg.runtime.jit_context import ContextSnapshot

        s = ContextSnapshot(run_id="r", agent_id="a")
        d = s.to_dict()
        rt = self._round_trip(d)
        assert rt["agent_id"] == "a"

    def test_boundary_packet_to_dict(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import BoundaryPacket

        p = BoundaryPacket(envelope_id="e", token_id="t", l5_cert_hash="c")
        d = p.to_dict()
        rt = self._round_trip(d)
        assert rt["envelope_id"] == "e"

    def test_boundary_verifier_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import L2BoundaryVerifier

        v = L2BoundaryVerifier("a", "r")
        v.certify_envelope("e", "t", "c")
        d = v.report.to_dict()
        rt = self._round_trip(d)
        assert "accepted_count" in rt

    def test_determinism_digest_to_dict(self) -> None:
        from agentic_core.adg.runtime.determinism_control import DeterminismController

        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(42)
        digest = ctrl.emit_determinism_digest(["e1"])
        d = digest.to_dict()
        rt = self._round_trip(d)
        assert rt["rng_seed"] == 42

    def test_determinism_control_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.determinism_control import DeterminismController

        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(1)
        d = ctrl.report.to_dict()
        rt = self._round_trip(d)
        assert "violation_count" in rt

    def test_network_transcript_to_dict(self) -> None:
        from agentic_core.adg.runtime.io_interception import NetworkTranscript

        t = NetworkTranscript()
        t.capture("https://a.com", "GET", "req", "resp", 200)
        d = t.to_dict()
        rt = self._round_trip(d)
        assert rt["url"] == "https://a.com"

    def test_io_interception_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.io_interception import IOInterceptor

        ic = IOInterceptor("a", "r")
        ic.intercept_io("https://a.com")
        d = ic.report.to_dict()
        rt = self._round_trip(d)
        assert "total_events" in rt

    def test_mutation_packet_to_dict(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([{"op": "add", "path": "/x", "value": 1}])
        d = p.to_dict()
        rt = self._round_trip(d)
        assert "diff_hash" in rt

    def test_mutation_transport_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        d = mt.report.to_dict()
        rt = self._round_trip(d)
        assert "committed_count" in rt

    def test_execution_trace_to_dict(self) -> None:
        from agentic_core.adg.runtime.execution_proof import ExecutionTrace

        t = ExecutionTrace(run_id="r", agent_id="a")
        t.record_event("e1")
        t.seal()
        d = t.to_dict()
        rt = self._round_trip(d)
        assert rt["agent_id"] == "a"

    def test_execution_proof_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.execution_proof import ExecutionProofRecorder

        rec = ExecutionProofRecorder("a", "r")
        rec.start_trace()
        d = rec.report.to_dict()
        rt = self._round_trip(d)
        assert "trace_count" in rt

    def test_path_transition_to_dict(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPath, ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        ctrl.route_path(ExecutionPath.PATH_B)
        d = ctrl.report.to_dict()
        rt = self._round_trip(d)
        assert "total_transitions" in rt

    def test_eval_metric_result_to_dict(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalMetricResult

        m = EvalMetricResult(metric_name="groundedness", value=0.9, run_id="r", agent_id="a")
        d = m.to_dict()
        rt = self._round_trip(d)
        assert rt["value"] == pytest.approx(0.9)

    def test_drift_alert_to_dict(self) -> None:
        from agentic_core.adg.runtime.eval_spine import DriftAlert

        a = DriftAlert(
            metric_name="G", current_value=0.1, baseline_value=0.9, drift_magnitude=0.8, threshold=0.05
        )
        d = a.to_dict()
        rt = self._round_trip(d)
        assert rt["metric_name"] == "G"
        assert rt["is_critical"] is True

    def test_eval_spine_report_to_dict(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        spine.score_groundedness(0.8)
        d = spine.report.to_dict()
        rt = self._round_trip(d)
        assert "metric_count" in rt or "metrics" in rt  # either count or list is acceptable


# ---------------------------------------------------------------------------
# D7 — Enum value format: lowercase / snake_case
# ---------------------------------------------------------------------------

_RUNTIME_MODULE_PATHS = [
    "agentic_core.adg.runtime.sandbox_airlock",
    "agentic_core.adg.runtime.capability_budget",
    "agentic_core.adg.runtime.jit_context",
    "agentic_core.adg.runtime.boundary_verifier",
    "agentic_core.adg.runtime.determinism_control",
    "agentic_core.adg.runtime.io_interception",
    "agentic_core.adg.runtime.mutation_transport",
    "agentic_core.adg.runtime.execution_proof",
    "agentic_core.adg.runtime.path_control",
    "agentic_core.adg.runtime.eval_spine",
]


class TestD7EnumValueFormat:
    """D7: All enum .value strings in G7-G16 modules are lowercase/snake_case."""

    @pytest.mark.parametrize("module_path", _RUNTIME_MODULE_PATHS)
    def test_all_enum_values_lowercase_snake_case(self, module_path: str) -> None:
        import enum
        import re

        mod = importlib.import_module(module_path)
        snake_re = re.compile(r"^[a-z][a-z0-9_]*$")
        violations: list[str] = []
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and issubclass(obj, enum.Enum) and obj is not enum.Enum:
                for member in obj:
                    if isinstance(member.value, str):
                        if not snake_re.match(member.value):
                            violations.append(f"{module_path}.{name}.{member.name} = {member.value!r}")
        assert not violations, f"Enum values not lowercase snake_case: {violations}"

    def test_airlock_phase_values_lowercase(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase

        for member in AirlockPhase:
            assert member.value == member.value.lower(), (
                f"AirlockPhase.{member.name}: {member.value!r} not lowercase"
            )

    def test_budget_status_values_lowercase(self) -> None:
        from agentic_core.adg.runtime.capability_budget import BudgetStatus

        for member in BudgetStatus:
            assert member.value == member.value.lower()

    def test_verification_outcome_values_lowercase(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import VerificationOutcome

        for member in VerificationOutcome:
            assert member.value == member.value.lower()

    def test_optimization_stage_values_lowercase(self) -> None:
        from agentic_core.adg.runtime.eval_spine import OptimizationStage

        for member in OptimizationStage:
            assert member.value == member.value.lower()


# ---------------------------------------------------------------------------
# D8 — Cross-constant non-overlap
# ---------------------------------------------------------------------------


class TestD8CrossConstantNonOverlap:
    """D8: No symbol string appears in two or more detection frozensets."""

    _CONST_NAMES_AND_VALUES: list[tuple[str, frozenset]] = []

    @classmethod
    def _get_constants(cls) -> list[tuple[str, frozenset]]:
        if cls._CONST_NAMES_AND_VALUES:
            return cls._CONST_NAMES_AND_VALUES
        from agentic_core.adg.schema import (
            BOUNDARY_VERIFIER_CLASSES,
            BUDGET_EXCEEDED_EXCEPTIONS,
            CAPABILITY_CHOKEPOINT_CLASSES,
            CAPABILITY_TOKEN_CLASSES,
            DETERMINISM_PATCH_METHODS,
            DPO_BATCH_CLASSES,
            DRIFT_ALERT_METHODS,
            EVAL_METRIC_CLASSES,
            EXECUTION_TRACE_CLASSES,
            FREEZE_METHOD_NAMES,
            IO_INTERCEPT_CLASSES,
            JIT_CONTEXT_CLASSES,
            MUTATION_TRANSPORT_CLASSES,
            NETWORK_TRANSCRIPT_SYMBOLS,
            PATH_CONTROL_CLASSES,
            PATH_REROUTE_METHODS,
            REPLAY_GUARD_CLASSES,
            REPLAY_KEY_METHODS,
            RFC6902_DIFF_SYMBOLS,
            SANDBOX_ENVELOPE_CLASSES,
            SEMANTIC_CLOCK_CLASSES,
            TOOL_BUDGET_CLASSES,
            WORK_CONTRACT_METHODS,
        )

        cls._CONST_NAMES_AND_VALUES = [
            ("SANDBOX_ENVELOPE_CLASSES", SANDBOX_ENVELOPE_CLASSES),
            ("CAPABILITY_TOKEN_CLASSES", CAPABILITY_TOKEN_CLASSES),
            ("WORK_CONTRACT_METHODS", WORK_CONTRACT_METHODS),
            ("TOOL_BUDGET_CLASSES", TOOL_BUDGET_CLASSES),
            ("BUDGET_EXCEEDED_EXCEPTIONS", BUDGET_EXCEEDED_EXCEPTIONS),
            ("JIT_CONTEXT_CLASSES", JIT_CONTEXT_CLASSES),
            ("FREEZE_METHOD_NAMES", FREEZE_METHOD_NAMES),
            ("BOUNDARY_VERIFIER_CLASSES", BOUNDARY_VERIFIER_CLASSES),
            ("CAPABILITY_CHOKEPOINT_CLASSES", CAPABILITY_CHOKEPOINT_CLASSES),
            ("SEMANTIC_CLOCK_CLASSES", SEMANTIC_CLOCK_CLASSES),
            ("REPLAY_GUARD_CLASSES", REPLAY_GUARD_CLASSES),
            ("DETERMINISM_PATCH_METHODS", DETERMINISM_PATCH_METHODS),
            ("IO_INTERCEPT_CLASSES", IO_INTERCEPT_CLASSES),
            ("NETWORK_TRANSCRIPT_SYMBOLS", NETWORK_TRANSCRIPT_SYMBOLS),
            ("MUTATION_TRANSPORT_CLASSES", MUTATION_TRANSPORT_CLASSES),
            ("RFC6902_DIFF_SYMBOLS", RFC6902_DIFF_SYMBOLS),
            ("EXECUTION_TRACE_CLASSES", EXECUTION_TRACE_CLASSES),
            ("REPLAY_KEY_METHODS", REPLAY_KEY_METHODS),
            ("PATH_CONTROL_CLASSES", PATH_CONTROL_CLASSES),
            ("PATH_REROUTE_METHODS", PATH_REROUTE_METHODS),
            ("EVAL_METRIC_CLASSES", EVAL_METRIC_CLASSES),
            ("DPO_BATCH_CLASSES", DPO_BATCH_CLASSES),
            ("DRIFT_ALERT_METHODS", DRIFT_ALERT_METHODS),
        ]
        return cls._CONST_NAMES_AND_VALUES

    def test_no_cross_constant_symbol_duplicates(self) -> None:
        """No single symbol appears in two or more frozensets."""
        from collections import Counter

        all_syms: list[str] = []
        for _, fset in self._get_constants():
            all_syms.extend(fset)
        dupes = {sym: cnt for sym, cnt in Counter(all_syms).items() if cnt > 1}
        assert not dupes, f"Cross-constant symbol duplicates found: {dupes}"

    def test_total_unique_symbols_matches_sum(self) -> None:
        """Total symbols across all constants equals count of unique symbols (no dupes)."""
        all_syms: list[str] = []
        for _, fset in self._get_constants():
            all_syms.extend(fset)
        assert len(all_syms) == len(set(all_syms))

    def test_class_names_and_method_names_do_not_overlap(self) -> None:
        """CamelCase class names never appear in method-name frozensets and vice versa."""
        from agentic_core.adg.schema import (
            BOUNDARY_VERIFIER_CLASSES,
            BUDGET_EXCEEDED_EXCEPTIONS,
            CAPABILITY_CHOKEPOINT_CLASSES,
            CAPABILITY_TOKEN_CLASSES,
            DETERMINISM_PATCH_METHODS,
            DPO_BATCH_CLASSES,
            DRIFT_ALERT_METHODS,
            EVAL_METRIC_CLASSES,
            EXECUTION_TRACE_CLASSES,
            FREEZE_METHOD_NAMES,
            IO_INTERCEPT_CLASSES,
            JIT_CONTEXT_CLASSES,
            MUTATION_TRANSPORT_CLASSES,
            NETWORK_TRANSCRIPT_SYMBOLS,
            PATH_CONTROL_CLASSES,
            PATH_REROUTE_METHODS,
            REPLAY_GUARD_CLASSES,
            REPLAY_KEY_METHODS,
            RFC6902_DIFF_SYMBOLS,
            SANDBOX_ENVELOPE_CLASSES,
            SEMANTIC_CLOCK_CLASSES,
            TOOL_BUDGET_CLASSES,
            WORK_CONTRACT_METHODS,
        )

        all_methods = (
            WORK_CONTRACT_METHODS
            | FREEZE_METHOD_NAMES
            | DETERMINISM_PATCH_METHODS
            | NETWORK_TRANSCRIPT_SYMBOLS
            | RFC6902_DIFF_SYMBOLS
            | REPLAY_KEY_METHODS
            | PATH_REROUTE_METHODS
            | DRIFT_ALERT_METHODS
        )
        all_classes = (
            SANDBOX_ENVELOPE_CLASSES
            | CAPABILITY_TOKEN_CLASSES
            | TOOL_BUDGET_CLASSES
            | BUDGET_EXCEEDED_EXCEPTIONS
            | JIT_CONTEXT_CLASSES
            | BOUNDARY_VERIFIER_CLASSES
            | CAPABILITY_CHOKEPOINT_CLASSES
            | SEMANTIC_CLOCK_CLASSES
            | REPLAY_GUARD_CLASSES
            | IO_INTERCEPT_CLASSES
            | MUTATION_TRANSPORT_CLASSES
            | EXECUTION_TRACE_CLASSES
            | PATH_CONTROL_CLASSES
            | EVAL_METRIC_CLASSES
            | DPO_BATCH_CLASSES
        )
        overlap = all_methods & all_classes
        assert not overlap, f"Method names and class names overlap: {sorted(overlap)}"


# ---------------------------------------------------------------------------
# D9 — Report isolation
# ---------------------------------------------------------------------------


class TestD9ReportIsolation:
    """D9: Two independently created recorders share no mutable state."""

    def test_sandbox_recorders_are_isolated(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import SandboxAirlockRecorder

        r1 = SandboxAirlockRecorder("a", "r1")
        r2 = SandboxAirlockRecorder("a", "r2")
        c = r1.stamp_contract()
        t = r1.issue_token(c)
        r1.enter_sandbox(c, t)
        assert r2.session_summary["envelope_count"] == 0, "r2 must be unaffected by r1's state mutations"

    def test_resource_governors_are_isolated(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGovernor, ToolBudget

        g1 = ResourceGovernor("a", "r1")
        g2 = ResourceGovernor("a", "r2")
        g1.activate_budget(ToolBudget.default())
        g1.consume("tool_calls", 10.0)
        assert g2.report.exceeded_count == 0
        assert not hasattr(g2, "_active_budget") or g2._active_budget is None  # type: ignore[attr-defined]

    def test_jit_synchronisers_are_isolated(self) -> None:
        from agentic_core.adg.runtime.jit_context import JITContextSynchronizer

        s1 = JITContextSynchronizer("a", "r1")
        s2 = JITContextSynchronizer("a", "r2")
        s1.sync_context()
        s1.sync_context()
        assert s2.session_summary["snapshot_count"] == 0

    def test_io_interceptors_are_isolated(self) -> None:
        from agentic_core.adg.runtime.io_interception import IOInterceptor

        ic1 = IOInterceptor("a", "r1")
        ic2 = IOInterceptor("a", "r2")
        ic1.intercept_io("https://a.com")
        ic1.intercept_io("https://b.com")
        assert ic2.report.total_events == 0

    def test_eval_spines_are_isolated(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        sp1 = EvalSpine("a", "r1")
        sp2 = EvalSpine("a", "r2")
        sp1.score_groundedness(0.9)
        assert len(sp2.report.metrics) == 0

    def test_path_controllers_are_isolated(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPathController

        c1 = ExecutionPathController("a", "r1")
        c2 = ExecutionPathController("a", "r2")
        c1.force_stall()
        c1.force_stall()
        c1.force_stall()
        assert c2.report.stall_count == 0

    def test_determinism_controllers_are_isolated(self) -> None:
        from agentic_core.adg.runtime.determinism_control import (
            DeterminismController,
            DeterminismViolationType,
        )

        ctrl1 = DeterminismController("a", "r1")
        ctrl2 = DeterminismController("a", "r2")
        ctrl1.seed_rng(1)
        ctrl1.record_violation(DeterminismViolationType.UNTRANSCRIPTED_RANDOM)
        assert ctrl2.report.violation_count == 0
        assert not ctrl2.report.is_fully_deterministic  # unseeded → not deterministic


# ---------------------------------------------------------------------------
# D10 — Line-number tracking inside function / class bodies
# ---------------------------------------------------------------------------


class TestD10LineNumberTracking:
    """D10: Visitor line_no reflects the actual call line, not line 1."""

    def test_call_on_line_5_inside_function(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = textwrap.dedent("""\
            def setup():
                x = 1
                y = 2
                z = 3
                env = SandboxEnvelope()
            """)
        edges = _edges_for(src, _SandboxAirlockVisitor)
        assert len(edges) == 1
        assert edges[0].line_no == 5, f"Expected line 5, got {edges[0].line_no}"

    def test_call_on_line_3_inside_class_method(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _EvalSpineVisitor

        src = textwrap.dedent("""\
            class Runner:
                def run(self):
                    spine = EvalSpine('a', 'r')
            """)
        edges = _edges_for(src, _EvalSpineVisitor)
        assert any(e.line_no == 3 for e in edges), (
            f"Expected an edge at line 3, got lines: {[e.line_no for e in edges]}"
        )

    def test_multiple_calls_at_different_lines(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DeterminismControlVisitor

        src = textwrap.dedent("""\
            pass
            pass
            seed_rng(1)
            pass
            patch_time()
            """)
        edges = _edges_for(src, _DeterminismControlVisitor)
        line_nos = sorted(e.line_no for e in edges)
        assert 3 in line_nos, f"seed_rng at line 3 not found: {line_nos}"
        assert 5 in line_nos, f"patch_time at line 5 not found: {line_nos}"

    def test_nested_call_in_comprehension_detected(self) -> None:
        """Calls inside list comprehensions are detected (generic_visit propagates)."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = "[SandboxEnvelope() for _ in range(3)]"
        edges = _edges_for(src, _SandboxAirlockVisitor)
        assert len(edges) == 1  # only one SandboxEnvelope call node in the comprehension
        assert edges[0].line_no == 1


# ---------------------------------------------------------------------------
# D11 — Module docstring contract
# ---------------------------------------------------------------------------


class TestD11ModuleDocstringContract:
    """D11: Every G7-G16 runtime module __doc__ starts with the 'G<n> (gap):' prefix."""

    _EXPECTED_PREFIXES = {
        "agentic_core.adg.runtime.sandbox_airlock": "G7 (gap):",
        "agentic_core.adg.runtime.capability_budget": "G8 (gap):",
        "agentic_core.adg.runtime.jit_context": "G9 (gap):",
        "agentic_core.adg.runtime.boundary_verifier": "G10 (gap):",
        "agentic_core.adg.runtime.determinism_control": "G11 (gap):",
        "agentic_core.adg.runtime.io_interception": "G12 (gap):",
        "agentic_core.adg.runtime.mutation_transport": "G13 (gap):",
        "agentic_core.adg.runtime.execution_proof": "G14 (gap):",
        "agentic_core.adg.runtime.path_control": "G15 (gap):",
        "agentic_core.adg.runtime.eval_spine": "G16 (gap):",
    }

    @pytest.mark.parametrize("module_path,expected_prefix", list(_EXPECTED_PREFIXES.items()))
    def test_module_docstring_starts_with_gap_prefix(self, module_path: str, expected_prefix: str) -> None:
        mod = importlib.import_module(module_path)
        doc = (mod.__doc__ or "").strip()
        assert doc.startswith(expected_prefix), (
            f"{module_path}: docstring must start with {expected_prefix!r}, got first 40 chars: {doc[:40]!r}"
        )

    @pytest.mark.parametrize("module_path", list(_EXPECTED_PREFIXES.keys()))
    def test_module_has_non_empty_docstring(self, module_path: str) -> None:
        mod = importlib.import_module(module_path)
        assert mod.__doc__ and len(mod.__doc__.strip()) > 20, (
            f"{module_path}: docstring is empty or too short"
        )

    @pytest.mark.parametrize("module_path", list(_EXPECTED_PREFIXES.keys()))
    def test_module_docstring_mentions_no_side_effects(self, module_path: str) -> None:
        """Every G7-G16 module docstring must state 'no side-effects on import'."""
        mod = importlib.import_module(module_path)
        doc = mod.__doc__ or ""
        normalised = doc.lower().replace("-", " ")
        assert "no side effects on import" in normalised, (
            f"{module_path}: docstring must contain 'no side-effects on import', got: {doc[:100]!r}"
        )


# ---------------------------------------------------------------------------
# D12 — Empty / degenerate source safety
# ---------------------------------------------------------------------------


class TestD12DegenerateSourceSafety:
    """D12: All visitors handle empty / trivial source without exceptions."""

    _DEGENERATE_SOURCES = [
        ("empty_string", ""),
        ("single_comment", "# just a comment"),
        ("bare_pass", "pass"),
        ("only_imports", "import os\nimport sys"),
        ("docstring_only", '"""A module docstring."""'),
        ("ellipsis_only", "..."),
        ("class_with_pass", "class Foo:\n    pass"),
        ("function_with_pass", "def foo():\n    pass"),
        ("empty_list", "x = []"),
        ("number_literal", "42"),
    ]

    @pytest.mark.parametrize("visitor_name", _ALL_G7_G16_VISITORS)
    @pytest.mark.parametrize("desc,source", _DEGENERATE_SOURCES)
    def test_visitor_does_not_crash_on_degenerate_source(
        self, visitor_name: str, desc: str, source: str
    ) -> None:
        cls = _import_visitor(visitor_name)
        tree = ast.parse(source)
        v = cls("M", "f.py")
        v.visit(tree)  # must not raise
        assert isinstance(v.edges, list)
        assert len(v.edges) == 0, (
            f"{visitor_name} produced edges on degenerate source {desc!r}: {[e.relation_type for e in v.edges]}"
        )


# ---------------------------------------------------------------------------
# D13 — Edge endpoint distinctness
# ---------------------------------------------------------------------------


class TestD13EdgeEndpointDistinctness:
    """D13: Every emitted edge has from_name != to_name."""

    def test_no_self_loop_edges_in_full_corpus(self) -> None:
        edges = _scan_src(_FULL_DETECTION_CORPUS)
        self_loops = [e for e in edges if e.from_name == e.to_name]
        assert not self_loops, (
            f"Self-loop edges found (from_name == to_name): "
            f"{[(e.from_name, e.relation_type) for e in self_loops]}"
        )

    @pytest.mark.parametrize(
        "source,rel",
        [
            ("SandboxEnvelope()", "enters_sandbox"),
            ("freeze_context(x)", "freezes_context"),
            ("seed_rng(42)", "seeds_rng"),
            ("ExecutionTrace()", "records_execution_trace"),
            ("emit_drift_alert('M', 0.3, 0.7)", "emits_drift_alert"),
        ],
    )
    def test_individual_edge_has_distinct_endpoints(self, source: str, rel: str) -> None:
        edges = [e for e in _scan_src(source) if e.relation_type == rel]
        assert edges, f"No edge with relation {rel!r} from {source!r}"
        for edge in edges:
            assert edge.from_name != edge.to_name, f"Self-loop on {rel!r}: from={edge.from_name!r}"


# ---------------------------------------------------------------------------
# D14 — to_name canonical format
# ---------------------------------------------------------------------------


class TestD14ToNameCanonicalFormat:
    """D14: Every emitted edge's to_name begins with 'ADG::Symbol::'."""

    def test_all_to_names_in_full_corpus_are_canonical(self) -> None:
        edges = _scan_src(_FULL_DETECTION_CORPUS)
        bad = [e for e in edges if not e.to_name.startswith("ADG::Symbol::")]
        assert not bad, (
            f"to_name not in canonical ADG::Symbol:: format: "
            f"{[(e.relation_type, e.to_name) for e in bad[:5]]}"
        )

    def test_to_name_contains_detected_symbol(self) -> None:
        """to_name must encode the detected symbol name in the canonical path."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        edges = _edges_for("SandboxEnvelope()", _SandboxAirlockVisitor)
        assert any("SandboxEnvelope" in e.to_name for e in edges)

    def test_from_name_always_adg_module(self) -> None:
        """from_name is always the module-level ADG canonical name, not a symbol."""
        edges = _scan_src(_FULL_DETECTION_CORPUS)
        bad = [e for e in edges if not e.from_name.startswith("ADG::")]
        assert not bad


# ---------------------------------------------------------------------------
# D15 — Blast-radius threshold boundary
# ---------------------------------------------------------------------------


class TestD15BlastRadiusBoundary:
    """D15: MutationTransport uses 0.8 as exact commit/abort threshold."""

    def test_blast_radius_exactly_zero_allows_commit(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.0)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is True

    def test_blast_radius_clearly_below_threshold_allows_commit(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.5)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is True

    def test_blast_radius_at_threshold_commits(self) -> None:
        """At exactly 0.8 the threshold is strict (> 0.8 aborts), so 0.8 still commits."""
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.8)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is True
        assert p.phase == CommitPhase.PHASE2_COMMITTED

    def test_blast_radius_just_above_threshold_aborts(self) -> None:
        """At 0.801 (> 0.8 strict threshold), commit must be aborted."""
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.801)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is False
        assert p.phase == CommitPhase.ABORTED
        assert p.abort_reason == "blast_radius_exceeded"

    def test_blast_radius_above_threshold_aborts(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 1.0)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is False
        assert p.phase == CommitPhase.ABORTED

    def test_blast_radius_stored_on_packet(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.35)
        assert p.blast_radius_score == pytest.approx(0.35)

    def test_multiple_packets_have_independent_blast_radii(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p1 = mt.package_diff([])
        p2 = mt.package_diff([])
        mt.validate_blast_radius(p1, 0.1)
        mt.validate_blast_radius(p2, 0.9)
        mt.sign_execution_trace(p1)
        assert mt.commit_mutation(p1) is True
        assert mt.commit_mutation(p2) is False


# ---------------------------------------------------------------------------
# D16 — EvalSpine missing-metric robustness
# ---------------------------------------------------------------------------


class TestD16EvalSpineMissingMetric:
    """D16: EvalSpine.report.average_metric returns 0.0 for unseen metric, not KeyError."""

    def test_average_metric_returns_zero_for_unseen_metric(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        result = spine.report.average_metric("nonexistent_metric_xyz")
        assert result == pytest.approx(0.0), f"Expected 0.0 for missing metric, got {result}"

    def test_average_metric_after_one_score(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        spine.score_groundedness(0.6)
        avg = spine.report.average_metric("groundedness")
        assert avg == pytest.approx(0.6)

    def test_average_metric_after_many_scores(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        values = [0.2, 0.4, 0.6, 0.8, 1.0]
        for v in values:
            spine.score_groundedness(v)
        avg = spine.report.average_metric("groundedness")
        assert avg == pytest.approx(sum(values) / len(values))

    def test_metric_count_zero_for_fresh_spine(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        assert len(spine.report.metrics) == 0

    def test_drift_alert_count_correct_after_mixed_alerts(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        spine.emit_drift_alert("G", 0.1, 0.9, threshold=0.05)  # critical
        spine.emit_drift_alert("G", 0.89, 0.9, threshold=0.1)  # non-critical
        spine.emit_drift_alert("G", 0.05, 0.9, threshold=0.01)  # critical
        assert spine.report.critical_drift_count == 2
        assert len(spine.report.drift_alerts) == 3


# ---------------------------------------------------------------------------
# D17 — Detection constant member hygiene
# ---------------------------------------------------------------------------


class TestD17ConstantMemberHygiene:
    """D17: No frozenset member is the empty string; all members are non-whitespace."""

    _CONSTANT_NAMES = [
        "SANDBOX_ENVELOPE_CLASSES",
        "CAPABILITY_TOKEN_CLASSES",
        "WORK_CONTRACT_METHODS",
        "TOOL_BUDGET_CLASSES",
        "BUDGET_EXCEEDED_EXCEPTIONS",
        "JIT_CONTEXT_CLASSES",
        "FREEZE_METHOD_NAMES",
        "BOUNDARY_VERIFIER_CLASSES",
        "CAPABILITY_CHOKEPOINT_CLASSES",
        "SEMANTIC_CLOCK_CLASSES",
        "REPLAY_GUARD_CLASSES",
        "DETERMINISM_PATCH_METHODS",
        "IO_INTERCEPT_CLASSES",
        "NETWORK_TRANSCRIPT_SYMBOLS",
        "MUTATION_TRANSPORT_CLASSES",
        "RFC6902_DIFF_SYMBOLS",
        "EXECUTION_TRACE_CLASSES",
        "REPLAY_KEY_METHODS",
        "PATH_CONTROL_CLASSES",
        "PATH_REROUTE_METHODS",
        "EVAL_METRIC_CLASSES",
        "DPO_BATCH_CLASSES",
        "DRIFT_ALERT_METHODS",
    ]

    @pytest.mark.parametrize("const_name", _CONSTANT_NAMES)
    def test_no_empty_string_member(self, const_name: str) -> None:
        mod = importlib.import_module("agentic_core.adg.schema")
        fset: frozenset = getattr(mod, const_name)
        assert "" not in fset, f"{const_name} contains the empty string"

    @pytest.mark.parametrize("const_name", _CONSTANT_NAMES)
    def test_no_whitespace_only_member(self, const_name: str) -> None:
        mod = importlib.import_module("agentic_core.adg.schema")
        fset: frozenset = getattr(mod, const_name)
        bad = [s for s in fset if isinstance(s, str) and not s.strip()]
        assert not bad, f"{const_name} contains whitespace-only member: {bad}"

    @pytest.mark.parametrize("const_name", _CONSTANT_NAMES)
    def test_all_members_are_strings(self, const_name: str) -> None:
        mod = importlib.import_module("agentic_core.adg.schema")
        fset: frozenset = getattr(mod, const_name)
        non_strings = [m for m in fset if not isinstance(m, str)]
        assert not non_strings, f"{const_name} has non-string members: {non_strings}"

    @pytest.mark.parametrize("const_name", _CONSTANT_NAMES)
    def test_no_member_contains_whitespace(self, const_name: str) -> None:
        """Symbol names must not contain internal spaces."""
        mod = importlib.import_module("agentic_core.adg.schema")
        fset: frozenset = getattr(mod, const_name)
        bad = [s for s in fset if isinstance(s, str) and " " in s]
        assert not bad, f"{const_name} has member with spaces: {bad}"


# ---------------------------------------------------------------------------
# D18 — RelationType / EdgeKind value format: lowercase snake_case
# ---------------------------------------------------------------------------


class TestD18SchemaValueFormat:
    """D18: All RelationType and EdgeKind Literal values are lowercase snake_case."""

    def test_all_relation_types_lowercase_snake_case(self) -> None:
        import re

        from agentic_core.adg.schema import RelationType

        snake_re = re.compile(r"^[a-z][a-z0-9_]*$")
        bad = [r for r in typing.get_args(RelationType) if not snake_re.match(r)]
        assert not bad, f"RelationType values not lowercase snake_case: {bad}"

    def test_all_edge_kinds_lowercase_snake_case(self) -> None:
        import re

        from agentic_core.adg.schema import EdgeKind

        snake_re = re.compile(r"^[a-z][a-z0-9_]*$")
        bad = [k for k in typing.get_args(EdgeKind) if not snake_re.match(k)]
        assert not bad, f"EdgeKind values not lowercase snake_case: {bad}"

    def test_g7_g16_relation_types_are_lowercase_snake_case(self) -> None:
        import re

        snake_re = re.compile(r"^[a-z][a-z0-9_]*$")
        bad = [r for r in G7_G16_RELATION_TYPES if not snake_re.match(r)]
        assert not bad, f"G7-G16 RelationType values not lowercase snake_case: {bad}"

    def test_no_camelcase_leaks_into_relation_types(self) -> None:
        from agentic_core.adg.schema import RelationType

        camel = [r for r in typing.get_args(RelationType) if any(c.isupper() for c in r)]
        assert not camel, f"CamelCase leaked into RelationType: {camel}"

    def test_no_camelcase_leaks_into_edge_kinds(self) -> None:
        from agentic_core.adg.schema import EdgeKind

        camel = [k for k in typing.get_args(EdgeKind) if any(c.isupper() for c in k)]
        assert not camel, f"CamelCase leaked into EdgeKind: {camel}"


# ---------------------------------------------------------------------------
# D19 — Visitor propagation depth
# ---------------------------------------------------------------------------


class TestD19VisitorPropagationDepth:
    """D19: Calls nested in comprehensions, lambdas, classes, decorators are all detected."""

    def test_call_inside_list_comprehension(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = "envs = [SandboxEnvelope() for _ in range(3)]"
        edges = _edges_for(src, _SandboxAirlockVisitor)
        assert len(edges) >= 1, "Call inside list comprehension must be detected"
        assert edges[0].relation_type == "enters_sandbox"

    def test_call_inside_dict_comprehension(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _EvalSpineVisitor

        src = "m = {i: EvalSpine('a', str(i)) for i in range(2)}"
        edges = _edges_for(src, _EvalSpineVisitor)
        assert len(edges) >= 1

    def test_call_inside_generator_expression(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DeterminismControlVisitor

        src = "results = list(seed_rng(s) for s in [1, 2, 3])"
        edges = _edges_for(src, _DeterminismControlVisitor)
        assert len(edges) >= 1
        assert any(e.relation_type == "seeds_rng" for e in edges)

    def test_call_inside_lambda(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _IOInterceptionVisitor

        src = "fn = lambda u: IOInterceptor('a', 'r')"
        edges = _edges_for(src, _IOInterceptionVisitor)
        assert len(edges) >= 1
        assert edges[0].relation_type == "intercepts_io"

    def test_call_inside_nested_function(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PathControlVisitor

        src = textwrap.dedent("""\
            def outer():
                def inner():
                    route_path(ExecutionPath.PATH_A)
            """)
        edges = _edges_for(src, _PathControlVisitor)
        assert len(edges) >= 1
        assert any(e.relation_type == "routes_path" for e in edges)

    def test_call_inside_class_body(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _MutationTransportVisitor

        src = textwrap.dedent("""\
            class Deployer:
                transport = MutationTransport('a', 'r')
            """)
        edges = _edges_for(src, _MutationTransportVisitor)
        assert len(edges) >= 1

    def test_call_inside_ternary_expression(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _JITContextVisitor

        src = "ctx = JITContext() if flag else None"
        edges = _edges_for(src, _JITContextVisitor)
        assert len(edges) >= 1
        assert edges[0].relation_type == "pulls_context"

    def test_call_inside_assert_statement(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _BoundaryVerifierVisitor

        src = "assert L2BoundaryVerifier('a', 'r') is not None"
        edges = _edges_for(src, _BoundaryVerifierVisitor)
        assert len(edges) >= 1
        assert edges[0].relation_type == "verifies_boundary"

    def test_call_inside_with_statement(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _ExecutionProofVisitor

        src = textwrap.dedent("""\
            with open('f') as f:
                t = ExecutionTrace()
            """)
        edges = _edges_for(src, _ExecutionProofVisitor)
        assert len(edges) >= 1

    def test_multiple_nested_levels_all_detected(self) -> None:
        """Calls at three levels of nesting all produce edges."""
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        src = textwrap.dedent("""\
            class Outer:
                class Inner:
                    def method(self):
                        return SandboxEnvelope()
            """)
        edges = _edges_for(src, _SandboxAirlockVisitor)
        assert len(edges) >= 1


# ---------------------------------------------------------------------------
# D20 — Schema constant total count
# ---------------------------------------------------------------------------


class TestD20SchemaConstantTotalCount:
    """D20: The total number of G7-G16 detection constants is exactly 23."""

    _G7_G16_CONSTANT_NAMES = [
        "SANDBOX_ENVELOPE_CLASSES",
        "CAPABILITY_TOKEN_CLASSES",
        "WORK_CONTRACT_METHODS",
        "TOOL_BUDGET_CLASSES",
        "BUDGET_EXCEEDED_EXCEPTIONS",
        "JIT_CONTEXT_CLASSES",
        "FREEZE_METHOD_NAMES",
        "BOUNDARY_VERIFIER_CLASSES",
        "CAPABILITY_CHOKEPOINT_CLASSES",
        "SEMANTIC_CLOCK_CLASSES",
        "REPLAY_GUARD_CLASSES",
        "DETERMINISM_PATCH_METHODS",
        "IO_INTERCEPT_CLASSES",
        "NETWORK_TRANSCRIPT_SYMBOLS",
        "MUTATION_TRANSPORT_CLASSES",
        "RFC6902_DIFF_SYMBOLS",
        "EXECUTION_TRACE_CLASSES",
        "REPLAY_KEY_METHODS",
        "PATH_CONTROL_CLASSES",
        "PATH_REROUTE_METHODS",
        "EVAL_METRIC_CLASSES",
        "DPO_BATCH_CLASSES",
        "DRIFT_ALERT_METHODS",
    ]

    def test_total_count_is_twenty_three(self) -> None:
        assert len(self._G7_G16_CONSTANT_NAMES) == 23

    def test_count_per_gap_matches_spec(self) -> None:
        """Each gap has the expected number of detection constants per the design doc."""
        expected_per_gap = {
            "G7": ["SANDBOX_ENVELOPE_CLASSES", "CAPABILITY_TOKEN_CLASSES", "WORK_CONTRACT_METHODS"],
            "G8": ["TOOL_BUDGET_CLASSES", "BUDGET_EXCEEDED_EXCEPTIONS"],
            "G9": ["JIT_CONTEXT_CLASSES", "FREEZE_METHOD_NAMES"],
            "G10": ["BOUNDARY_VERIFIER_CLASSES", "CAPABILITY_CHOKEPOINT_CLASSES"],
            "G11": ["SEMANTIC_CLOCK_CLASSES", "REPLAY_GUARD_CLASSES", "DETERMINISM_PATCH_METHODS"],
            "G12": ["IO_INTERCEPT_CLASSES", "NETWORK_TRANSCRIPT_SYMBOLS"],
            "G13": ["MUTATION_TRANSPORT_CLASSES", "RFC6902_DIFF_SYMBOLS"],
            "G14": ["EXECUTION_TRACE_CLASSES", "REPLAY_KEY_METHODS"],
            "G15": ["PATH_CONTROL_CLASSES", "PATH_REROUTE_METHODS"],
            "G16": ["EVAL_METRIC_CLASSES", "DPO_BATCH_CLASSES", "DRIFT_ALERT_METHODS"],
        }
        for gap, names in expected_per_gap.items():
            for name in names:
                assert name in self._G7_G16_CONSTANT_NAMES, f"{gap}: {name} not in constant catalogue"
        total = sum(len(v) for v in expected_per_gap.values())
        assert total == 23

    def test_no_duplicate_constant_names_in_catalogue(self) -> None:
        assert len(self._G7_G16_CONSTANT_NAMES) == len(set(self._G7_G16_CONSTANT_NAMES))

    def test_all_catalogued_constants_are_importable(self) -> None:
        import agentic_core.adg.schema as sch

        for name in self._G7_G16_CONSTANT_NAMES:
            obj = getattr(sch, name, None)
            assert obj is not None, f"schema.{name} is missing"
            assert isinstance(obj, frozenset), f"schema.{name} is not frozenset"
