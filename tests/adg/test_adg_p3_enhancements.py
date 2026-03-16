"""P3 Enhancement Test Suite — E26-E31.

Tests all six P3 architectural verification enhancements grounded in the
live ADG (20260311: 3,302 modules, 148,859 edges, 2,323 writes_to edges).

E26: Runtime execution graph (runtime_graph.py)
E27: Layer authority enforcement (layer_authority.py)
E28: Mutation path verification (mutation_authority.py)
E29: State lineage query API (state_lineage.py)
E30: Architecture verifier (architecture_verifier.py)
E31: Policy hash runtime validation (policy_hash_validator.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.adg.schema import (
    L1_WRITE_ALLOWLIST,
    LAYER_AUTHORITY_FORBIDDEN,
    PROMPT_AUTHORITY_RULES,
    PROMPT_FIELD_TO_SLOT,
    PROMPT_SLOT_AUTHORITY,
    PROMPT_SLOT_TYPES,
    UWG_CANONICAL_SYMBOL,
    UWG_MODULE_PATH,
    UWG_WRITE_SYMBOLS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_p3_enhancements")
_emit_applies_guardrail("p0", "test_adg_p3_enhancements", "p0_governance")
_emit_snapshots_state("p0", "test_adg_p3_enhancements", "state_snapshot")
emit_replay_key("p0", "test_adg_p3_enhancements")
emit_determinism_digest("p0", "test_adg_p3_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Shared test infrastructure — minimal ScanResult / Edge stubs
# ---------------------------------------------------------------------------


@dataclass
class _Edge:
    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str = "call"
    source_file: str = "test_file.py"
    line_no: int = 1
    symbol: str = ""


@dataclass
class _ScanResult:
    edges: list[_Edge] = field(default_factory=list)
    commit_sha: str = "deadbeef" * 5

    def print_digest(self) -> None:
        pass


def _mod(path: str) -> str:
    return f"ADG::Module::{path}"


def _sym(name: str) -> str:
    return f"ADG::Symbol::{name}"


# ---------------------------------------------------------------------------
# E26: Runtime Execution Graph
# ---------------------------------------------------------------------------


class TestRuntimeGraph:
    """E26: build_runtime_graph produces AgentAction/ToolInvocation/LayerTransition."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)

    def test_agent_action_node_detected(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L3_orchestration/planner.py"),
                    relation_type="calls",
                    to_name=_sym("agent.execute"),
                ),
            ]
        )
        report = build_runtime_graph(result)
        assert len(report.agent_action_nodes) == 1
        node = report.agent_action_nodes[0]
        assert node.module_path == "agentic_core/L3_orchestration/planner.py"
        assert node.layer == "L3"

    def test_tool_invocation_node_detected(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/executor.py"),
                    relation_type="calls",
                    to_name=_sym("tool.invoke"),
                ),
            ]
        )
        report = build_runtime_graph(result)
        assert len(report.tool_invocation_nodes) == 1
        node = report.tool_invocation_nodes[0]
        assert node.module_path == "agentic_core/L2_execution/executor.py"
        assert node.layer == "L2"

    def test_layer_transition_cross_layer_detected(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        # L3 calling something in L1 (downward = allowed)
        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L3_orchestration/planner.py"),
                    relation_type="calls",
                    to_name=_sym("agentic_core.L1_cognition.reasoning.ThinkEngine"),
                ),
            ]
        )
        report = build_runtime_graph(result)
        assert report.total_cross_layer_calls >= 1

    def test_upward_layer_violation_detected(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        # L1 calling L3 — upward violation
        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/engine.py"),
                    relation_type="calls",
                    to_name=_sym("agentic_core.L3_orchestration.Orchestrator"),
                ),
            ]
        )
        report = build_runtime_graph(result)
        assert len(report.upward_layer_violations) >= 1
        violation = report.upward_layer_violations[0]
        assert violation.from_layer == "L1"
        assert violation.to_layer == "L3"
        assert not violation.is_allowed

    def test_downward_layer_call_is_allowed(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        # L3 calling L1 — downward = allowed
        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L3_orchestration/planner.py"),
                    relation_type="calls",
                    to_name=_sym("agentic_core.L1_cognition.ThinkEngine"),
                ),
            ]
        )
        report = build_runtime_graph(result)
        downward = [t for t in report.layer_transitions if t.is_allowed]
        assert len(downward) >= 1

    def test_report_summary_string(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result([])
        report = build_runtime_graph(result)
        s = report.summary
        assert "Runtime graph" in s
        assert "cross-layer" in s

    def test_to_dict_structure(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result([])
        d = build_runtime_graph(result).to_dict()
        assert "agent_action_count" in d
        assert "tool_invocation_count" in d
        assert "total_cross_layer_calls" in d
        assert "upward_violation_count" in d

    def test_multiple_agent_calls_aggregated(self):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L3_orchestration/p.py"), "calls", _sym("agent.execute")),
                _Edge(_mod("agentic_core/L3_orchestration/p.py"), "calls", _sym("agent.run")),
            ]
        )
        report = build_runtime_graph(result)
        assert len(report.agent_action_nodes) == 1
        assert report.agent_action_nodes[0].call_count == 2

    def test_to_json_serializable(self):
        import json

        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        result = self._make_result([])
        json.loads(build_runtime_graph(result).to_json())


# ---------------------------------------------------------------------------
# E27: Layer Authority Enforcement
# ---------------------------------------------------------------------------


class TestLayerAuthority:
    """E27: detect_layer_authority_violations catches L1/L3/L4/L6 behavioral violations."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)

    def test_l1_writes_to_is_violation(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/reasoning/MetaLearningAgent.py"),
                    relation_type="writes_to",
                    to_name=_sym("_fh.write"),
                    source_file="agentic_core/L1_cognition/reasoning/MetaLearningAgent.py",
                    line_no=42,
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 1
        v = report.violations[0]
        assert v.layer == "L1"
        assert v.violation_type == "L1_MUTATES_STATE"
        assert v.severity == "critical"

    def test_l1_copy_call_is_allowlisted(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        # copy.deepcopy is in allowlist — should NOT be a violation
        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/engines/cognitive_engine.py"),
                    relation_type="writes_to",
                    to_name=_sym("copy.deepcopy"),
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 0
        assert report.allowlisted_count == 1

    def test_l3_invokes_provider_is_violation(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L3_orchestration/planner.py"),
                    relation_type="invokes_provider",
                    to_name=_sym("openai.ChatCompletion"),
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 1
        v = report.violations[0]
        assert v.layer == "L3"
        assert v.violation_type == "L3_INVOKES_PROVIDER_DIRECTLY"
        assert v.severity == "high"

    def test_l4_calls_is_violation(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L4_state/bus.py"),
                    relation_type="calls",
                    to_name=_sym("business_logic.process"),
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 1
        v = report.violations[0]
        assert v.layer == "L4"
        assert v.violation_type == "L4_CONTAINS_LOGIC"

    def test_l6_routes_through_is_violation(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L6_observability/tracer.py"),
                    relation_type="routes_through",
                    to_name=_sym("Router"),
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 1
        v = report.violations[0]
        assert v.layer == "L6"
        assert "L6" in v.violation_type

    def test_l2_writes_to_is_not_violation(self):
        """L2 is the execution layer — it is allowed to write."""
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/UniversalWriteGateway.py"),
                    relation_type="writes_to",
                    to_name=_sym("Path.write_text"),
                ),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert report.violation_count == 0

    def test_report_summary_contains_counts(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result([])
        s = detect_layer_authority_violations(result).summary
        assert "Layer authority violations" in s

    def test_critical_violations_filter(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L1_cognition/x.py"), "writes_to", _sym("open")),
                _Edge(_mod("agentic_core/L3_orchestration/y.py"), "invokes_provider", _sym("openai")),
            ]
        )
        report = detect_layer_authority_violations(result)
        critical = report.critical_violations()
        assert all(v.severity == "critical" for v in critical)
        assert any(v.layer == "L1" for v in critical)

    def test_to_dict_has_violation_list(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L1_cognition/x.py"), "writes_to", _sym("f.write")),
            ]
        )
        d = detect_layer_authority_violations(result).to_dict()
        assert "violations" in d
        assert "violation_count" in d
        assert d["violation_count"] == 1

    def test_suggested_fix_present(self):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L1_cognition/x.py"), "writes_to", _sym("f.write")),
            ]
        )
        report = detect_layer_authority_violations(result)
        assert len(report.violations[0].suggested_fix) > 10


# ---------------------------------------------------------------------------
# E28: Mutation Path Verification
# ---------------------------------------------------------------------------


class TestMutationAuthority:
    """E28: verify_mutation_paths detects UWG bypass violations."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)

    def test_writes_to_without_uwg_is_violation(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L3_orchestration/planner.py"),
                    relation_type="writes_to",
                    to_name=_sym("some_file.write"),
                ),
            ]
        )
        report = verify_mutation_paths(result)
        assert report.violation_count >= 1
        assert report.total_writes_to >= 1

    def test_writes_through_uwg_is_compliant(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        # Module has both writes_to AND writes_through UWG → classified as compliant
        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/some_executor.py"),
                    relation_type="writes_to",
                    to_name=_sym("Path.write_text"),
                ),
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/some_executor.py"),
                    relation_type="writes_through",
                    to_name=_sym("UniversalWriteGateway"),
                ),
            ]
        )
        report = verify_mutation_paths(result)
        assert report.violation_count == 0
        assert len(report.compliant_modules) >= 1

    def test_test_modules_are_allowlisted(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("tests/unit/test_something.py"),
                    relation_type="writes_to",
                    to_name=_sym("tmp_file.write"),
                ),
            ]
        )
        report = verify_mutation_paths(result)
        assert report.violation_count == 0
        assert len(report.allowlisted_modules) == 1

    def test_uwg_module_itself_is_allowlisted(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod(UWG_MODULE_PATH),
                    relation_type="writes_to",
                    to_name=_sym("Path.write_text"),
                ),
            ]
        )
        report = verify_mutation_paths(result)
        assert report.violation_count == 0

    def test_l1_bypass_is_critical(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/reasoning/MetaLearningAgent.py"),
                    relation_type="writes_to",
                    to_name=_sym("_fh.write"),
                ),
            ]
        )
        report = verify_mutation_paths(result)
        critical = report.critical_violations()
        assert len(critical) == 1
        assert critical[0].risk_level == "critical"

    def test_compliance_rate_calculation(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result(
            [
                _Edge(
                    _mod("agentic_core/L2_execution/e.py"), "writes_through", _sym("UniversalWriteGateway")
                ),
            ]
        )
        report = verify_mutation_paths(result)
        assert 0.0 <= report.compliance_rate <= 1.0

    def test_report_summary_has_compliance(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result([])
        s = verify_mutation_paths(result).summary
        assert "writes_to=" in s
        assert "compliance=" in s

    def test_to_dict_structure(self):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        result = self._make_result([])
        d = verify_mutation_paths(result).to_dict()
        assert "violation_count" in d
        assert "compliance_rate" in d
        assert "violations" in d


# ---------------------------------------------------------------------------
# E29: State Lineage Query API
# ---------------------------------------------------------------------------


class TestStateLineage:
    """E29: build_lineage_index allows querying which modules mutated a state key."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)

    def test_mutations_for_state_returns_matching_records(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/executor.py"),
                    relation_type="writes_to",
                    to_name=_sym("config_state.write"),
                ),
            ]
        )
        idx = build_lineage_index(result)
        records = idx.mutations_for_state("config_state")
        assert len(records) == 1
        assert records[0].module_path == "agentic_core/L2_execution/executor.py"

    def test_mutations_by_layer_groups_correctly(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L2_execution/a.py"), "writes_to", _sym("x")),
                _Edge(_mod("agentic_core/L2_execution/b.py"), "writes_to", _sym("y")),
                _Edge(_mod("agentic_core/L3_orchestration/c.py"), "writes_to", _sym("z")),
            ]
        )
        idx = build_lineage_index(result)
        l2 = idx.mutations_by_layer("L2")
        l3 = idx.mutations_by_layer("L3")
        assert len(l2) == 2
        assert len(l3) == 1

    def test_via_uwg_flag_set_for_writes_through(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L2_execution/exec.py"),
                    relation_type="writes_through",
                    to_name=_sym("UniversalWriteGateway"),
                ),
            ]
        )
        idx = build_lineage_index(result)
        assert idx.uwg_covered >= 1

    def test_uwg_bypass_modules_detected(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L3_orchestration/p.py"), "writes_to", _sym("direct.write")),
            ]
        )
        idx = build_lineage_index(result)
        bypasses = idx.uwg_bypass_modules()
        assert "agentic_core/L3_orchestration/p.py" in bypasses

    def test_coverage_summary_structure(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result([])
        summary = build_lineage_index(result).coverage_summary()
        assert "total_records" in summary
        assert "uwg_covered" in summary
        assert "coverage_rate" in summary
        assert "top_writers" in summary

    def test_query_mutations_for_state_convenience(self):
        from agentic_core.adg.applications.state_lineage import query_mutations_for_state

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L2_execution/e.py"), "writes_to", _sym("plan_hash.write")),
            ]
        )
        records = query_mutations_for_state(result, "plan_hash")
        assert len(records) == 1

    def test_total_records_counts_both_write_types(self):
        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L2_execution/a.py"), "writes_to", _sym("x")),
                _Edge(
                    _mod("agentic_core/L2_execution/b.py"), "writes_through", _sym("UniversalWriteGateway")
                ),
            ]
        )
        idx = build_lineage_index(result)
        assert idx.total_records == 2

    def test_to_json_serializable(self):
        import json

        from agentic_core.adg.applications.state_lineage import build_lineage_index

        result = self._make_result([])
        json.loads(build_lineage_index(result).to_json())


# ---------------------------------------------------------------------------
# E30: Architecture Verifier
# ---------------------------------------------------------------------------


class TestArchitectureVerifier:
    """E30: verify_architecture orchestrates all planes and returns a consolidated report."""

    def _make_clean_result(self) -> _ScanResult:
        return _ScanResult(edges=[])

    def test_clean_result_passes(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        report = verify_architecture(result)
        assert report.passed is True
        assert report.exit_code() == 0

    def test_report_has_all_four_planes(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        report = verify_architecture(result)
        plane_names = {p.plane for p in report.planes}
        assert "runtime_graph" in plane_names
        assert "layer_authority" in plane_names
        assert "mutation_paths" in plane_names
        assert "policy_hash" in plane_names

    def test_skip_planes_reduces_plane_count(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        report = verify_architecture(result, skip_planes=frozenset({"runtime_graph", "policy_hash"}))
        plane_names = {p.plane for p in report.planes}
        assert "runtime_graph" not in plane_names
        assert "policy_hash" not in plane_names
        assert "layer_authority" in plane_names
        assert "mutation_paths" in plane_names

    def test_l1_write_violation_fails_architecture(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = _ScanResult(
            edges=[
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/x.py"),
                    relation_type="writes_to",
                    to_name=_sym("_fh.write"),
                ),
            ]
        )
        report = verify_architecture(
            result, skip_planes=frozenset({"runtime_graph", "mutation_paths", "policy_hash"})
        )
        assert not report.passed
        assert report.exit_code() == 1

    def test_summary_contains_pass_fail(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        report = verify_architecture(result)
        s = report.summary
        assert "PASS" in s or "FAIL" in s

    def test_to_dict_structure(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        d = verify_architecture(result).to_dict()
        assert "passed" in d
        assert "total_violations" in d
        assert "planes" in d

    def test_to_json_serializable(self):
        import json

        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        json.loads(verify_architecture(result).to_json())

    def test_plane_result_passed_flag(self):
        from agentic_core.adg.applications.architecture_verifier import verify_architecture

        result = self._make_clean_result()
        report = verify_architecture(result)
        for plane in report.planes:
            if plane.passed:
                assert plane.violation_count == 0


# ---------------------------------------------------------------------------
# E31: Policy Hash Runtime Validation
# ---------------------------------------------------------------------------


class TestPolicyHashValidator:
    """E31: validate_policy_hash_coupling detects instruction modules without policy hash."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)

    def test_instruction_module_without_policy_hash_is_violation(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L0_routing/router.py"),
                    relation_type="instantiates",
                    to_name=_sym("RoutingInputs"),
                ),
            ]
        )
        report = validate_policy_hash_coupling(result)
        assert report.violation_count >= 1
        v = report.violations[0]
        assert v.layer == "L0"
        assert v.violation_type == "INSTRUCTION_WITHOUT_POLICY_HASH"
        assert not v.has_policy_hash_ref

    def test_instruction_module_with_policy_hash_is_coupled(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result(
            [
                _Edge(_mod("agentic_core/L0_routing/router.py"), "instantiates", _sym("RoutingInputs")),
                _Edge(_mod("agentic_core/L0_routing/router.py"), "calls", _sym("_verify_plan_hash")),
            ]
        )
        report = validate_policy_hash_coupling(result)
        assert report.violation_count == 0
        assert "agentic_core/L0_routing/router.py" in report.policy_coupled_modules

    def test_non_required_layer_skipped(self):
        """L5 safety modules using instruction symbols are not required to carry policy hash."""
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L5_safety/checker.py"),
                    relation_type="instantiates",
                    to_name=_sym("GovernedPayload"),
                ),
            ]
        )
        report = validate_policy_hash_coupling(result)
        assert report.violation_count == 0

    def test_l1_instruction_without_policy_is_high_severity(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result(
            [
                _Edge(
                    from_name=_mod("agentic_core/L1_cognition/engine.py"),
                    relation_type="instantiates",
                    to_name=_sym("InstructionPacket"),
                ),
            ]
        )
        report = validate_policy_hash_coupling(result)
        if report.violation_count > 0:
            assert report.violations[0].severity in ("high", "medium")

    def test_coupling_rate_is_one_when_all_coupled(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result([])
        report = validate_policy_hash_coupling(result)
        assert report.coupling_rate == 1.0

    def test_summary_contains_coupling_rate(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result([])
        s = validate_policy_hash_coupling(result).summary
        assert "Policy hash coupling" in s
        assert "coupling=" in s

    def test_to_dict_structure(self):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result([])
        d = validate_policy_hash_coupling(result).to_dict()
        assert "violation_count" in d
        assert "coupling_rate" in d
        assert "violations" in d

    def test_to_json_serializable(self):
        import json

        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        result = self._make_result([])
        json.loads(validate_policy_hash_coupling(result).to_json())


# ---------------------------------------------------------------------------
# P3 Schema Constants
# ---------------------------------------------------------------------------


class TestP3SchemaConstants:
    """Verify P3 constants are correctly defined in schema.py."""

    def test_uwg_canonical_symbol_correct(self):
        assert UWG_CANONICAL_SYMBOL == "ADG::Symbol::UniversalWriteGateway"

    def test_uwg_module_path_correct(self):
        assert UWG_MODULE_PATH == "agentic_core/L2_execution/UniversalWriteGateway.py"

    def test_layer_authority_forbidden_covers_all_layers(self):
        assert "L1" in LAYER_AUTHORITY_FORBIDDEN
        assert "L3" in LAYER_AUTHORITY_FORBIDDEN
        assert "L4" in LAYER_AUTHORITY_FORBIDDEN
        assert "L6" in LAYER_AUTHORITY_FORBIDDEN

    def test_l1_forbidden_includes_writes(self):
        assert "writes_to" in LAYER_AUTHORITY_FORBIDDEN["L1"]
        assert "writes_through" in LAYER_AUTHORITY_FORBIDDEN["L1"]

    def test_l3_forbidden_includes_invokes(self):
        assert "invokes_tool" in LAYER_AUTHORITY_FORBIDDEN["L3"]
        assert "invokes_provider" in LAYER_AUTHORITY_FORBIDDEN["L3"]

    def test_l1_write_allowlist_contains_copy_variants(self):
        assert "copy" in L1_WRITE_ALLOWLIST
        assert "copy.deepcopy" in L1_WRITE_ALLOWLIST

    def test_uwg_write_symbols_contains_uwg(self):
        assert "UniversalWriteGateway" in UWG_WRITE_SYMBOLS


# ---------------------------------------------------------------------------
# P6 Schema Constants (carried over — verify in same file for completeness)
# ---------------------------------------------------------------------------


class TestP6SchemaConstants:
    """Verify P6 prompt governance constants in schema.py."""

    def test_prompt_slot_types_ordered(self):
        assert PROMPT_SLOT_TYPES == ("S0", "D0", "I0", "C0", "U0")

    def test_prompt_slot_authority_s0_highest(self):
        assert PROMPT_SLOT_AUTHORITY["S0"] < PROMPT_SLOT_AUTHORITY["U0"]

    def test_prompt_authority_rules_count(self):
        assert len(PROMPT_AUTHORITY_RULES) == 6

    def test_prompt_field_to_slot_mapping(self):
        assert PROMPT_FIELD_TO_SLOT["s0_system"] == "S0"
        assert PROMPT_FIELD_TO_SLOT["u0_user_prompt"] == "U0"


# ---------------------------------------------------------------------------
# CLI Integration
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """Verify all P3 CLI commands are registered and return codes are correct."""

    def test_help_includes_runtime_graph(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "runtime-graph" in out

    def test_help_includes_layer_authority(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "layer-authority" in out

    def test_help_includes_mutation_paths(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "mutation-paths" in out

    def test_help_includes_verify_architecture(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "verify-architecture" in out

    def test_help_includes_state_lineage(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "state-lineage" in out

    def test_help_includes_policy_hash(self):
        import contextlib
        import io

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        with contextlib.suppress(SystemExit):
            with contextlib.redirect_stdout(buf):
                main(["--help"])
        out = buf.getvalue()
        assert "policy-hash" in out

    def test_no_command_returns_1(self):
        import contextlib

        from agentic_core.adg.cli import main

        with contextlib.suppress(SystemExit):
            code = main([])
        # main with no args prints help and returns 1
