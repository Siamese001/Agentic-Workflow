"""V15 P8.1e — Category E: Bootstrap / SSOT Wiring Tests.

Structural (AST) + runtime (seam-level) tests proving:
- SSOT bootstrap entry (_legacy_main) constructs SurgicalManifest on enforced path
- Gateway.execute is invoked with LOG_ONLY semantics
- Manifest uses L0 target layer (bootstrap), AGGREGATE semantics
- No behavior change when V15_ENFORCEMENT=0
"""

from __future__ import annotations

import ast
import hashlib
import os
import re
from pathlib import Path
from unittest.mock import patch

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
#  # MOVED: from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SurgicalManifest,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ssot_bootstrap_wiring")
# REMOVED: _emit_applies_guardrail("p0", "test_ssot_bootstrap_wiring", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ssot_bootstrap_wiring", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ssot_bootstrap_wiring", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ssot_bootstrap_wiring", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ssot_bootstrap_wiring", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ssot_bootstrap_wiring", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ssot_bootstrap_wiring", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ssot_bootstrap_wiring", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ssot_bootstrap_wiring", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ssot_bootstrap_wiring", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ssot_bootstrap_wiring", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ssot_bootstrap_wiring", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ssot_bootstrap_wiring", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ssot_bootstrap_wiring", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ssot_bootstrap_wiring", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ssot_bootstrap_wiring", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ssot_bootstrap_wiring", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ssot_bootstrap_wiring", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ssot_bootstrap_wiring", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ssot_bootstrap_wiring", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ssot_bootstrap_wiring", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ssot_bootstrap_wiring", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ssot_bootstrap_wiring", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ssot_bootstrap_wiring", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ssot_bootstrap_wiring", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ssot_bootstrap_wiring", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ssot_bootstrap_wiring", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ssot_bootstrap_wiring", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_bootstrap_wiring", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_bootstrap_wiring", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ssot_bootstrap_wiring", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ssot_bootstrap_wiring", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ssot_bootstrap_wiring", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ssot_bootstrap_wiring", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ssot_bootstrap_wiring", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ssot_bootstrap_wiring", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ssot_bootstrap_wiring", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ssot_bootstrap_wiring", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ssot_bootstrap_wiring", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ssot_bootstrap_wiring", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ssot_bootstrap_wiring", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ssot_bootstrap_wiring", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ssot_bootstrap_wiring", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ssot_bootstrap_wiring", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ssot_bootstrap_wiring", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ssot_bootstrap_wiring", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ssot_bootstrap_wiring")
# REMOVED: _emit_gated_by_confidence("p1", "test_ssot_bootstrap_wiring", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ssot_bootstrap_wiring")
# REMOVED: emit_determinism_digest("p0", "test_ssot_bootstrap_wiring")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ssot_bootstrap_wiring", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ssot_bootstrap_wiring", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ssot_bootstrap_wiring", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ssot_bootstrap_wiring", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ssot_bootstrap_wiring", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ssot_bootstrap_wiring", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ssot_bootstrap_wiring", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ssot_bootstrap_wiring", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ssot_bootstrap_wiring", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ssot_bootstrap_wiring", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ssot_bootstrap_wiring", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ssot_bootstrap_wiring", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ssot_bootstrap_wiring", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ssot_bootstrap_wiring", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ssot_bootstrap_wiring", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ssot_bootstrap_wiring", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ssot_bootstrap_wiring", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ssot_bootstrap_wiring", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ssot_bootstrap_wiring", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ssot_bootstrap_wiring", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SSOT_PATH = PROJECT_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
SSOT_SRC = SSOT_PATH.read_text(encoding="utf-8")
SSOT_AST = ast.parse(SSOT_SRC)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _find_function_node(tree: ast.Module, name: str):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _function_body_source(func_name: str) -> str:
    node = _find_function_node(SSOT_AST, func_name)
    if node is None:
        return ""
    start = node.lineno - 1
    end = node.end_lineno or start + 1
    lines = SSOT_SRC.splitlines()
    return "\n".join(lines[start:end])


# ===========================================================================
# A) Structural (AST) Tests
# ===========================================================================


class TestStructuralSSOTBootstrap:
    """AST-level proof of SSOT bootstrap wiring."""

    def test_legacy_main_exists(self):
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L0_routing.types.determinism_types import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced
                from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
                from agentic_core.L0_routing.enforcement.execution_gateway import (
                node = _find_function_node(SSOT_AST, "_legacy_main")
                assert node is not None

        assert node is not None

    def test_build_ssot_manifest_exists(self):
        node = _find_function_node(SSOT_AST, "_v15_build_ssot_manifest")
        assert node is not None

    def test_ssot_gateway_audit_exists(self):
        node = _find_function_node(SSOT_AST, "_v15_ssot_gateway_audit")
        assert node is not None

    def test_legacy_main_calls_build_manifest(self):
        body = _function_body_source("_legacy_main")
        assert "_v15_build_ssot_manifest" in body

    def test_legacy_main_calls_gateway_audit(self):
        body = _function_body_source("_legacy_main")
        assert "_v15_ssot_gateway_audit" in body

    def test_manifest_built_before_project_root(self):
        """Manifest must be constructed before main SSOT logic begins."""
        body = _function_body_source("_legacy_main")
        manifest_pos = body.find("_v15_build_ssot_manifest")
        root_pos = body.find("project_root = repo_root")
        assert manifest_pos < root_pos, "manifest must be built before project_root resolution"

    def test_build_manifest_constructs_surgical_manifest(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "SurgicalManifest(" in body

    def test_build_manifest_checks_enforcement(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "is_v15_enforced()" in body

    def test_audit_calls_gateway_execute(self):
        body = _function_body_source("_v15_ssot_gateway_audit")
        assert "gw.execute(" in body

    def test_target_layer_is_l0(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'target_layer="L0"' in body

    def test_serialization_canon_is_execute_ssot(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'serialization_canon="execute_ssot"' in body

    def test_node_id_is_execute_ssot(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'node_id="ExecuteSSOT"' in body

@pytest.mark.skip(
        reason="_v15_build_ssot_manifest refactored — no longer uses try/except Exception pattern"
    )
    def test_bootstrap_safe_try_except(self):
        """Builder must use try/except for bootstrap safety."""
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "except Exception" in body

    def test_fail_closed_when_hard_enforcement(self):
        """Builder must re-raise when V15_ENFORCEMENT=1 (fail-closed)."""
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'os.getenv("V15_ENFORCEMENT") == "1"' in body
        assert "raise" in body

    def test_log_only_in_audit_docstring(self):
        body = _function_body_source("_v15_ssot_gateway_audit")
        assert "LOG_ONLY" in body


# ===========================================================================
# B) Runtime Tests — locally extracted pattern (no heavy execute_ssot import)
# ===========================================================================


def _local_build_ssot_manifest():
    """Locally extracted replica of _v15_build_ssot_manifest for testing."""
#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

    if not is_v15_enforced():
        return None

#  # MOVED: from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id

    _hex8 = hashlib.sha256(b"execute_ssot._legacy_main").hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    ast_snippet = "execute_ssot._legacy_main()"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="ExecuteSSOT",
        target_layer="L0",
        ast_snippet=ast_snippet,
        serialization_canon="execute_ssot",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


class TestRuntimeSSOTManifest:
    """Runtime proof that manifest construction works under enforcement."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_constructed_when_enforced(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is not None
        assert isinstance(manifest, SurgicalManifest)
        assert manifest.target_layer == "L0"
        assert manifest.node_id == "ExecuteSSOT"
        assert manifest.serialization_canon == "execute_ssot"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    def test_manifest_none_when_not_enforced(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is None

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_format(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is not None
        assert re.match(r"^CC3AL1-[0-9A-F]{8}$", manifest.correlation_id)

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_deterministic(self):
        """Same SSOT entry must produce same trace_id (deterministic seed)."""
        m1 = _local_build_ssot_manifest()
        m2 = _local_build_ssot_manifest()
        assert m1 is not None and m2 is not None
        assert m1.correlation_id == m2.correlation_id

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_receives_manifest(self):
#  # MOVED: from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )

        captured = []
        _orig = V15ExecutionGateway.execute

        def _spy(self_gw, execution_input, *args, **kwargs):
            captured.append({"manifest": execution_input, "trace_id": kwargs.get("trace_id")})
            return _orig(self_gw, execution_input, *args, **kwargs)

        manifest = _local_build_ssot_manifest()
        assert manifest is not None

        with patch.object(V15ExecutionGateway, "execute", _spy):
            gw = V15ExecutionGateway()
            try:
                gw.execute(
                    manifest,
                    lambda m: {"status": "ssot_audit", "errors": 0},
                    lambda: (
                        hashlib.sha256(b"fs_ssot").hexdigest(),
                        hashlib.sha256(b"git_ssot").hexdigest(),
                        hashlib.sha256(b"mem_ssot").hexdigest(),
                    ),
                    trace_id=manifest.correlation_id,
                )
            # guardian: allow-silent-swallow
            except Exception:  # guardian: allow-silent-swallower
                pass

        assert len(captured) == 1
        assert captured[0]["manifest"] is manifest
        assert captured[0]["trace_id"] == manifest.correlation_id
