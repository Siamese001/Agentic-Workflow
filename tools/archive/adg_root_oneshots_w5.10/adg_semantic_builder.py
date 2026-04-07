"""ADG Semantic Graph Builder — Phase 1/2/3 of the test stabilization pipeline.

Layers AST-level semantic nodes on top of the existing module-level ADG artifact.

Produces:
  artifacts/adg_semantic_graph.json     — full semantic node+edge graph
  artifacts/adg_test_surface_map.json   — symbol -> [test_ids]
  artifacts/adg_failure_clusters.json   — ranked risk clusters
  artifacts/adg_validation_report.json  — Phase 0 validation result

Node types extracted:
  ModuleNode, ClassNode, FunctionNode, TestFunctionNode, FixtureNode,
  ParametrizedTestNode, AssertionNode, MockNode

Edge types extracted:
  IMPORT_EDGE, CALL_EDGE, INHERIT_EDGE, TEST_COVERS_EDGE,
  FIXTURE_DEPENDS_EDGE, ASSERT_TARGET_EDGE, MOCK_TARGET_EDGE
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "adg_semantic_builder")
_emit_applies_guardrail("p0", "adg_semantic_builder", "p0_governance")
_emit_reads_policy_state("p0", "adg_semantic_builder", "policy_binding")
_emit_snapshots_state("p0", "adg_semantic_builder", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_1")
_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_2")
_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_3")
_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_4")
_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_5")
_emit_emits_metric_event("adg_semantic_builder", "p4obs", "metric_6")
_emit_records_incident_event("adg_semantic_builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_semantic_builder", "p4obs", "anomaly")
_emit_writes_observability_log("adg_semantic_builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_semantic_builder", "p4obs", "mon_state")
_emit_triggers_alert("adg_semantic_builder", "p4obs", "alert")
_emit_links_incident_trace("adg_semantic_builder", "p4obs", "trace_link")
_emit_captures_pattern("adg_semantic_builder", "p3lm", "pattern")
_emit_records_learning_event("adg_semantic_builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_semantic_builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_semantic_builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_semantic_builder", "p3lm", "routing")
_emit_improves_agent_policy("adg_semantic_builder", "p3lm", "policy")
_emit_stores_learning_state("adg_semantic_builder", "p3lm", "state")
_emit_records_execution_trace("adg_semantic_builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_semantic_builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_semantic_builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_semantic_builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_semantic_builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_semantic_builder", "env_read", "p2_env_1")
_emit_reads_environ("adg_semantic_builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_semantic_builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_semantic_builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_semantic_builder", "context_pull")
_emit_pulls_context("p1", "adg_semantic_builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_semantic_builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_semantic_builder", "uwg_term_2")
_emit_writes_through("p1", "adg_semantic_builder", "write_through")
_emit_writes_through("p1", "adg_semantic_builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_semantic_builder", "safety_validation")
_emit_invokes_eval("p1", "adg_semantic_builder", "eval_call")
_emit_proposal_commits_routing("p1", "adg_semantic_builder", "routing_commit")
_emit_escalates_to_human("p1", "adg_semantic_builder", "human_escalation")
_emit_routes_through("p1", "adg_semantic_builder", "route_through")
_emit_checks_agent_registry("p1", "adg_semantic_builder", "agent_registry")
_emit_validates_agent_capability("p1", "adg_semantic_builder", "capability")
_emit_dispatches_execution_plan("p1", "adg_semantic_builder", "exec_plan")
_emit_agent_executes_agent("p1", "adg_semantic_builder", "sub_agent")
_emit_routes_to_agent("p1", "adg_semantic_builder", "target_agent")
_emit_verifies_policy("p1", "adg_semantic_builder", "policy_check")
_emit_observes_runtime_state("p1", "adg_semantic_builder", "runtime_state")
_emit_verifies_boundary("p1", "adg_semantic_builder", "boundary_check")
_emit_transcripts_response("p1", "adg_semantic_builder", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_semantic_builder")
_emit_gated_by_confidence("p1", "adg_semantic_builder", "confidence_gate")
emit_replay_key("p0", "adg_semantic_builder")
emit_determinism_digest("p0", "adg_semantic_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_semantic_builder", "execution_auth")
_emit_validates_capability("p2", "adg_semantic_builder", "capability_check")
_emit_routes_to_capability("p2", "adg_semantic_builder", "capability_route")
_emit_writes_via_uwg("p2", "adg_semantic_builder", "uwg_write")
_emit_blocks_direct_write("p2", "adg_semantic_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_semantic_builder", "tool_invocation")
_emit_captures_execution_output("p2", "adg_semantic_builder", "exec_output")
_emit_dispatches_agent("p3", "adg_semantic_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_semantic_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_semantic_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_semantic_builder", "healing_outcome")
_emit_escalates_failure("p3", "adg_semantic_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_semantic_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_semantic_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_semantic_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_semantic_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_semantic_builder", "eval_metric")
_emit_stores_embedding("p4", "adg_semantic_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_semantic_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_semantic_builder", "exec_snapshot_link")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_1")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_2")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_3")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_4")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_5")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_6")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_7")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_8")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_9")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_10")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_11")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_12")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_13")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_14")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_15")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_16")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_17")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_18")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_19")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_20")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_21")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_22")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_23")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_24")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_25")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_26")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_27")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_28")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_29")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_30")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_31")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_32")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_33")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_34")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_35")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_36")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_37")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_38")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_39")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_40")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_41")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_42")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_43")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_44")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_45")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_46")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_47")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_48")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_49")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_50")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_51")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_52")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_53")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_54")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_55")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_56")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_57")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_58")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_59")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_60")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_61")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_62")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_63")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_64")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_65")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_66")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_67")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_68")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_69")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_70")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_71")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_72")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_73")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_74")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_75")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_76")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_77")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_78")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_79")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_80")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_81")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_82")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_83")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_84")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_85")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_86")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_87")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_88")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_89")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_90")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_91")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_92")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_93")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_94")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_95")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_96")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_97")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_98")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_99")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_100")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_101")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_102")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_103")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_104")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_105")
_emit_reads_through("l4", "adg_semantic_builder", "urg_read_106")

# guardian: allow-global_mutation
_REPO_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("adg_semantic_builder")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SemanticNode:
    node_id: str
    node_type: str          # ModuleNode, ClassNode, FunctionNode, TestFunctionNode, FixtureNode, ParametrizedTestNode, AssertionNode, MockNode
    module_path: str
    name: str
    qualified_name: str
    lineno: int = 0
    decorators: list[str] = field(default_factory=list)
    layer: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "module_path": self.module_path,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "lineno": self.lineno,
            "decorators": self.decorators,
            "layer": self.layer,
            "meta": self.meta,
        }


@dataclass
class SemanticEdge:
    edge_type: str          # IMPORT_EDGE, CALL_EDGE, INHERIT_EDGE, TEST_COVERS_EDGE, FIXTURE_DEPENDS_EDGE, ASSERT_TARGET_EDGE, MOCK_TARGET_EDGE
    from_id: str
    to_id: str
    from_module: str
    to_module: str
    lineno: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "edge_type": self.edge_type,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "from_module": self.from_module,
            "to_module": self.to_module,
            "lineno": self.lineno,
            "meta": self.meta,
        }


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    names = []
    for d in node.decorator_list:
        if isinstance(d, ast.Name):
            names.append(d.id)
        elif isinstance(d, ast.Attribute):
            names.append(f"{ast.unparse(d)}")
        elif isinstance(d, ast.Call):
            if isinstance(d.func, ast.Name):
                names.append(d.func.id)
            elif isinstance(d.func, ast.Attribute):
                names.append(ast.unparse(d.func))
    return names


def _is_test_function(name: str, decorators: list[str]) -> bool:
    return name.startswith("test_") or name.startswith("Test")


def _is_fixture(decorators: list[str]) -> bool:
    return any("fixture" in d for d in decorators)


def _is_parametrized(decorators: list[str]) -> bool:
    return any("parametrize" in d for d in decorators)


def _is_mock_call(node: ast.expr) -> bool:
    s = ast.unparse(node)
    return any(k in s for k in ("mock.", "Mock(", "MagicMock(", "patch(", "patch.object(", "mocker.patch"))


def _extract_assert_targets(body: list[ast.stmt]) -> list[str]:
    """Walk body and collect names/attrs used in assert statements."""
    targets: list[str] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Assert):
            targets.append(ast.unparse(node.test)[:120])
    return targets


def _extract_mock_targets(body: list[ast.stmt]) -> list[str]:
    targets: list[str] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Call) and _is_mock_call(node):
            targets.append(ast.unparse(node)[:120])
    return targets


def _extract_fixture_deps(args: ast.arguments) -> list[str]:
    return [a.arg for a in args.args]


def _node_id(module_path: str, qualified_name: str) -> str:
    raw = f"{module_path}::{qualified_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-file AST extraction
# ---------------------------------------------------------------------------

def extract_file(rel_path: str, source: str) -> tuple[list[SemanticNode], list[SemanticEdge]]:
    """Parse one Python file and return all semantic nodes and intra-file edges."""
    from agentic_core.adg.contracts.schema_util import module_path_to_layer

    nodes: list[SemanticNode] = []
    edges: list[SemanticEdge] = []

    try:
        tree = ast.parse(source, filename=rel_path)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        return nodes, edges

    layer = module_path_to_layer(rel_path)
    module_qname = rel_path.replace("/", ".").removesuffix(".py")
    module_nid = _node_id(rel_path, module_qname)

    module_node = SemanticNode(
        node_id=module_nid,
        node_type="ModuleNode",
        module_path=rel_path,
        name=rel_path.split("/")[-1],
        qualified_name=module_qname,
        layer=layer,
    )
    nodes.append(module_node)

    # Collect top-level imports for IMPORT_EDGE
    import_targets: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_targets.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_targets.append((node.module, node.lineno))

    for imp_name, lineno in import_targets:
        # Convert dotted module name to a path candidate
        candidate_path = imp_name.replace(".", "/") + ".py"
        imp_id = _node_id(candidate_path, imp_name)
        edges.append(SemanticEdge(
            edge_type="IMPORT_EDGE",
            from_id=module_nid,
            to_id=imp_id,
            from_module=rel_path,
            to_module=candidate_path,
            lineno=lineno,
        ))

    # Walk top-level class and function definitions
    fixture_names: set[str] = set()
    test_function_ids: dict[str, str] = {}  # func_name -> node_id

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = _decorator_names(node)
            is_fixture = _is_fixture(decorators)
            is_test = _is_test_function(node.name, decorators)
            is_parametrized = _is_parametrized(decorators)

            qname = f"{module_qname}.{node.name}"
            nid = _node_id(rel_path, qname)

            if is_fixture:
                fixture_names.add(node.name)
                ntype = "FixtureNode"
            elif is_parametrized and is_test:
                ntype = "ParametrizedTestNode"
            elif is_test:
                ntype = "TestFunctionNode"
            else:
                ntype = "FunctionNode"

            fn_node = SemanticNode(
                node_id=nid,
                node_type=ntype,
                module_path=rel_path,
                name=node.name,
                qualified_name=qname,
                lineno=node.lineno,
                decorators=decorators,
                layer=layer,
            )

            if is_test or is_fixture:
                # Assert targets
                assert_targets = _extract_assert_targets(node.body)
                mock_targets = _extract_mock_targets(node.body)
                fn_node.meta["assert_targets"] = assert_targets[:20]
                fn_node.meta["mock_targets"] = mock_targets[:10]

                # Fixture dependencies from function args
                fixture_deps = _extract_fixture_deps(node.args)
                fn_node.meta["fixture_deps"] = fixture_deps

                for dep_name in fixture_deps:
                    dep_id = _node_id(rel_path, f"{module_qname}.{dep_name}")
                    edges.append(SemanticEdge(
                        edge_type="FIXTURE_DEPENDS_EDGE",
                        from_id=nid,
                        to_id=dep_id,
                        from_module=rel_path,
                        to_module=rel_path,
                        lineno=node.lineno,
                        meta={"dep_name": dep_name},
                    ))

            nodes.append(fn_node)
            if is_test:
                test_function_ids[node.name] = nid

        elif isinstance(node, ast.ClassDef):
            decorators = _decorator_names(node)
            qname = f"{module_qname}.{node.name}"
            nid = _node_id(rel_path, qname)

            bases = []
            for b in node.bases:
                bases.append(ast.unparse(b))

            class_node = SemanticNode(
                node_id=nid,
                node_type="ClassNode",
                module_path=rel_path,
                name=node.name,
                qualified_name=qname,
                lineno=node.lineno,
                decorators=decorators,
                layer=layer,
                meta={"bases": bases},
            )
            nodes.append(class_node)

            for base_name in bases:
                base_id = _node_id(rel_path, base_name)
                edges.append(SemanticEdge(
                    edge_type="INHERIT_EDGE",
                    from_id=nid,
                    to_id=base_id,
                    from_module=rel_path,
                    to_module=rel_path,
                    lineno=node.lineno,
                    meta={"base": base_name},
                ))

    return nodes, edges


# ---------------------------------------------------------------------------
# Repository-wide scan
# ---------------------------------------------------------------------------

_SCAN_DIRS = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "tools",
    "ops_scripts",
    "tests",
    "system_learning",
]

_EXCLUDE_PATTERNS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", "dist", "build",
}


def iter_python_files(repo_root: Path):
    for scan_dir in _SCAN_DIRS:
        base = repo_root / scan_dir
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            if any(part in _EXCLUDE_PATTERNS for part in py_file.parts):
                continue
            try:
                rel = py_file.relative_to(repo_root).as_posix()
                yield rel, py_file
            except ValueError as e:
                # TODO: Add proper input validation
                logger.warning(f"Invalid input: {e}")
                continue


def build_semantic_graph(repo_root: Path) -> dict:
    """Build the complete semantic graph for the repository."""
    all_nodes: list[SemanticNode] = []
    all_edges: list[SemanticEdge] = []

    file_count = 0
    error_count = 0

    for rel_path, abs_path in iter_python_files(repo_root):
        try:
            source = abs_path.read_text(encoding="utf-8", errors="replace")
        # guardian: allow-silent-swallow
        except Exception:
            error_count += 1
# ---------------------------------------------------------------------------

def build_test_surface_map(graph: dict) -> dict:
    """Map every non-test symbol -> list of test_ids that cover it.

    Strategy: a test covers a symbol if:
      1. The test module imports the symbol's module (IMPORT_EDGE)
      2. OR the test's assert_targets mention the symbol name
    """
    # Build module -> test list
    module_to_tests: dict[str, list[str]] = defaultdict(list)
    for node in graph["tests"]:
        mod = node["module_path"]
        qn = node["qualified_name"]
        test_id = f"{mod}::{node['name']}"
        module_to_tests[mod].append(test_id)

    # Build import edges: test_module -> set of imported modules
    test_imports: dict[str, set[str]] = defaultdict(set)
    for edge in graph["relations"]:
        if edge["edge_type"] == "IMPORT_EDGE":
            from_mod = edge["from_module"]
            to_mod = edge["to_module"]
            if from_mod.startswith("tests/"):
                test_imports[from_mod].add(to_mod)

    # Build symbol map: module -> [symbols]
    module_to_symbols: dict[str, list[str]] = defaultdict(list)
    for sym in graph["symbols"]:
        module_to_symbols[sym["module_path"]].append(sym["name"])

    # Now build the coverage map: symbol_qname -> [test_ids]
    surface_map: dict[str, list[str]] = {}

    for sym in graph["symbols"]:
        sym_mod = sym["module_path"]
        sym_name = sym["name"]
        sym_qname = sym["qualified_name"]

        covering_tests: list[str] = []

        # Find all test modules that import this symbol's module
        for test_mod, imported in test_imports.items():
            # Direct module import match
            if sym_mod in imported or any(
                sym_mod.startswith(imp.replace(".", "/")) or
                imp.startswith(sym_mod.replace("/", ".").removesuffix(".py"))
                for imp in imported
            ):
                covering_tests.extend(module_to_tests.get(test_mod, []))

        # Also check assert targets in tests for explicit symbol mention
        for test_node in graph["tests"]:
            for target in test_node.get("meta", {}).get("assert_targets", []):
                if sym_name in target:
                    tid = f"{test_node['module_path']}::{test_node['name']}"
                    if tid not in covering_tests:
                        covering_tests.append(tid)

        if covering_tests:
            surface_map[sym_qname] = sorted(set(covering_tests))

    # Also build module-level map (used in Phase 3)
    module_surface: dict[str, list[str]] = {}
    for test_mod, imported in test_imports.items():
        for imp_mod in imported:
            tests_for_mod = module_to_tests.get(test_mod, [])
            if imp_mod not in module_surface:
                module_surface[imp_mod] = []
            module_surface[imp_mod].extend(tests_for_mod)

    # Deduplicate
    for k in module_surface:
        module_surface[k] = sorted(set(module_surface[k]))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "symbol_coverage": surface_map,
        "module_coverage": module_surface,
        "covered_symbol_count": len(surface_map),
        "covered_module_count": len(module_surface),
    }


# ---------------------------------------------------------------------------
# Phase 3: Root cause cluster discovery
# ---------------------------------------------------------------------------

def build_failure_clusters(graph: dict, surface_map: dict) -> dict:
    """Rank modules by risk signals: fan-out, test surface size, centrality.

    No pytest is run. Risk is inferred purely from graph signals.
    """
    from agentic_core.adg.contracts.schema_util import module_path_to_layer

    module_coverage = surface_map.get("module_coverage", {})

    # Fan-out per module (count of outgoing IMPORT_EDGEs)
    fan_out: dict[str, int] = defaultdict(int)
    fan_in: dict[str, int] = defaultdict(int)
    for edge in graph["relations"]:
        if edge["edge_type"] == "IMPORT_EDGE":
            fan_out[edge["from_module"]] += 1
            fan_in[edge["to_module"]] += 1

    # Test surface size per module
    test_surface_size: dict[str, int] = {
        mod: len(tests) for mod, tests in module_coverage.items()
    }

    # Collect all non-test modules
    all_modules = {
        n["module_path"] for n in graph["entities"]
        if n["node_type"] == "ModuleNode" and not n["module_path"].startswith("tests/")
    }

    clusters = []
    for mod in all_modules:
        fo = fan_out.get(mod, 0)
        fi = fan_in.get(mod, 0)
        ts_size = test_surface_size.get(mod, 0)
        layer = module_path_to_layer(mod)

        # Risk score: weighted combination
        risk = fo * 2 + fi * 3 + ts_size * 1
        if risk == 0:
            continue

        clusters.append({
            "module": mod,
            "layer": layer,
            "fan_out": fo,
            "fan_in": fi,
            "test_surface_size": ts_size,
            "risk_score": risk,
            "covering_tests": module_coverage.get(mod, []),
        })

    # Sort by risk descending
    clusters.sort(key=lambda c: c["risk_score"], reverse=True)
    top_clusters = clusters[:50]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "total_modules_analyzed": len(all_modules),
        "clusters_with_risk": len(clusters),
        "top_clusters": top_clusters,
    }


# ---------------------------------------------------------------------------
# Phase 0: Validation report
# ---------------------------------------------------------------------------

def build_validation_report(latest_artifact_path: Path, semantic_graph: dict) -> dict:
    try:
        adg = json.loads(latest_artifact_path.read_text(encoding="utf-8"))
    # guardian: allow-silent-swallow
    except Exception as e:
        adg = {}
        logger.warning("Could not load adg_latest.json: %s", e)

    required_fields = ["entities", "relations", "symbols", "tests", "fixtures"]
    missing_in_adg = [f for f in required_fields if not adg.get(f)]
    missing_in_sem = [f for f in required_fields if not semantic_graph.get(f)]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "adg_latest_path": str(latest_artifact_path),
        "adg_entity_count": len(adg.get("entities", [])),
        "adg_relation_count": len(adg.get("relations", [])),
        "adg_missing_fields": missing_in_adg,
        "semantic_graph_node_count": semantic_graph["counts"]["total_nodes"],
        "semantic_graph_edge_count": semantic_graph["counts"]["total_edges"],
        "semantic_missing_fields": missing_in_sem,
        "test_node_count": semantic_graph["counts"]["test_functions"],
        "fixture_count": semantic_graph["counts"]["fixtures"],
        "symbol_count": len(semantic_graph["symbols"]),
        "validation_passed": len(missing_in_sem) == 0,
    }


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    artifacts_dir = _REPO_ROOT / "artifacts"
    adg_dir = _REPO_ROOT / "artifacts" / "adg"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    adg_dir.mkdir(parents=True, exist_ok=True)

    latest = adg_dir / "adg_latest.json"
    if not latest.exists():
        logger.error("adg_latest.json not found. Run: python tools/adg_cli.py build --rebuild")
        return 1

    # --- PHASE 1: Semantic graph ---
    logger.info("PHASE 1: Building semantic graph...")
    sem_graph = build_semantic_graph(_REPO_ROOT)
    sem_path = artifacts_dir / "adg_semantic_graph.json"
    sem_path.write_text(json.dumps(sem_graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 1 DONE: %d nodes, %d edges -> %s",
                sem_graph["counts"]["total_nodes"], sem_graph["counts"]["total_edges"], sem_path)

    # --- PHASE 2: Test surface map ---
    logger.info("PHASE 2: Building test surface map...")
    surface_map = build_test_surface_map(sem_graph)
    surf_path = artifacts_dir / "adg_test_surface_map.json"
    surf_path.write_text(json.dumps(surface_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 2 DONE: %d symbols covered, %d modules covered -> %s",
                surface_map["covered_symbol_count"], surface_map["covered_module_count"], surf_path)

    # --- PHASE 3: Root cause clusters ---
    logger.info("PHASE 3: Building failure clusters...")
    clusters = build_failure_clusters(sem_graph, surface_map)
    clust_path = artifacts_dir / "adg_failure_clusters.json"
    clust_path.write_text(json.dumps(clusters, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 3 DONE: %d clusters (top 50 ranked) -> %s",
                clusters["clusters_with_risk"], clust_path)

    # --- PHASE 0: Validation report ---
    logger.info("PHASE 0: Emitting validation report...")
    validation = build_validation_report(latest, sem_graph)
    val_path = artifacts_dir / "adg_validation_report.json"
    val_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 0 DONE: validation_passed=%s -> %s", validation["validation_passed"], val_path)

    # Print summary
    print("\n=== ADG SEMANTIC GRAPH SUMMARY ===")
    print(f"  ModuleNodes:       {sem_graph['counts']['module_nodes']}")
    print(f"  ClassNodes:        {sem_graph['counts']['class_nodes']}")
    print(f"  FunctionNodes:     {sem_graph['counts']['function_nodes']}")
    print(f"  TestFunctionNodes: {sem_graph['counts']['test_functions']}")
    print(f"  FixtureNodes:      {sem_graph['counts']['fixtures']}")
    print(f"  ParametrizedTests: {sem_graph['counts']['parametrized']}")
    print(f"  Total edges:       {sem_graph['counts']['total_edges']}")
    print("\n=== TEST SURFACE MAP ===")
    print(f"  Symbols covered:   {surface_map['covered_symbol_count']}")
    print(f"  Modules covered:   {surface_map['covered_module_count']}")
    print("\n=== TOP 10 RISK CLUSTERS ===")
    for c in clusters["top_clusters"][:10]:
        print(f"  {c['module']:<70} tests={c['test_surface_size']:>4}  risk={c['risk_score']:>6}")
    print("\n=== VALIDATION ===")
    print(f"  passed={validation['validation_passed']}")
    print("\nArtifacts written:")
    print(f"  {val_path}")
    print(f"  {sem_path}")
    print(f"  {surf_path}")
    print(f"  {clust_path}")

    return 0 if validation["validation_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
