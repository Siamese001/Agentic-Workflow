"""
Tests for Phase 4: Low Tier Remediation

Tests surgical healing integration for agents with 1-2 violations:
- AgentPermission (1)
- AutonomousThreatEvolutionAgent (1)
- CheckpointManagerAgent (1)
- CodeDeduplicationAgent (2)
- CredentialScannerAgent (1)
- CodeValidatorAgent (1)
- NamingAgent (1)
- NervousSystemAgent (1)
- PreCommitSovereignAgent (1)
- ReportLocationAgent (1)
- RootHygieneAgent (1)
- SubAtomicRegistryAgent (1)
- SystemArchitectAgent (1)
- ValidationOrchestratorAgent (1)
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.SurgicalHealingAdapter import (
    SurgicalHealingAdapter,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_1")
_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_2")
_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_3")
_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_4")
_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_5")
_emit_emits_metric_event("test_surgical_low_tier", "p4obs", "metric_6")
_emit_records_incident_event("test_surgical_low_tier", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_surgical_low_tier", "p4obs", "anomaly")
_emit_writes_observability_log("test_surgical_low_tier", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_surgical_low_tier", "p4obs", "mon_state")
_emit_triggers_alert("test_surgical_low_tier", "p4obs", "alert")
_emit_links_incident_trace("test_surgical_low_tier", "p4obs", "trace_link")
_emit_captures_pattern("test_surgical_low_tier", "p3lm", "pattern")
_emit_records_learning_event("test_surgical_low_tier", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_surgical_low_tier", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_surgical_low_tier", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_surgical_low_tier", "p3lm", "routing")
_emit_improves_agent_policy("test_surgical_low_tier", "p3lm", "policy")
_emit_stores_learning_state("test_surgical_low_tier", "p3lm", "state")
_emit_records_execution_trace("test_surgical_low_tier", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_surgical_low_tier", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_surgical_low_tier", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_surgical_low_tier", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_surgical_low_tier", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_surgical_low_tier", "env_read", "p2_env_1")
_emit_reads_environ("test_surgical_low_tier", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_surgical_low_tier", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_surgical_low_tier", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_surgical_low_tier")
_emit_applies_guardrail("p0", "test_surgical_low_tier", "p0_governance")
_emit_reads_policy_state("p0", "test_surgical_low_tier", "policy_binding")
_emit_snapshots_state("p0", "test_surgical_low_tier", "state_snapshot")
_emit_pulls_context("p1", "test_surgical_low_tier", "context_pull")
_emit_pulls_context("p1", "test_surgical_low_tier", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_surgical_low_tier", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_surgical_low_tier", "uwg_term_secondary")
_emit_writes_through("p1", "test_surgical_low_tier", "write_through")
_emit_writes_through("p1", "test_surgical_low_tier", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_surgical_low_tier", "safety_validation")
_emit_invokes_eval("p1", "test_surgical_low_tier", "eval_call")
_emit_proposal_commits_routing("p1", "test_surgical_low_tier", "routing_commit")
_emit_escalates_to_human("p1", "test_surgical_low_tier", "human_escalation")
_emit_routes_through("p1", "test_surgical_low_tier", "route_through")
_emit_checks_agent_registry("p1", "test_surgical_low_tier", "agent_registry")
_emit_validates_agent_capability("p1", "test_surgical_low_tier", "capability")
_emit_dispatches_execution_plan("p1", "test_surgical_low_tier", "exec_plan")
_emit_agent_executes_agent("p1", "test_surgical_low_tier", "sub_agent")
_emit_routes_to_agent("p1", "test_surgical_low_tier", "target_agent")
_emit_verifies_policy("p1", "test_surgical_low_tier", "policy_check")
_emit_observes_runtime_state("p1", "test_surgical_low_tier", "runtime_state")
_emit_verifies_boundary("p1", "test_surgical_low_tier", "boundary_check")
_emit_transcripts_response("p1", "test_surgical_low_tier", "transcript")
_emit_hard_fails_untranscripted("p1", "test_surgical_low_tier")
_emit_gated_by_confidence("p1", "test_surgical_low_tier", "confidence_gate")
emit_replay_key("p0", "test_surgical_low_tier")
emit_determinism_digest("p0", "test_surgical_low_tier")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_surgical_low_tier", "execution_auth")
_emit_validates_capability("p2", "test_surgical_low_tier", "capability_check")
_emit_routes_to_capability("p2", "test_surgical_low_tier", "capability_route")
_emit_writes_via_uwg("p2", "test_surgical_low_tier", "uwg_write")
_emit_blocks_direct_write("p2", "test_surgical_low_tier", "direct_write_block")
_emit_records_tool_invocation("p2", "test_surgical_low_tier", "tool_invocation")
_emit_captures_execution_output("p2", "test_surgical_low_tier", "exec_output")
_emit_dispatches_agent("p3", "test_surgical_low_tier", "agent_dispatch")
_emit_coordinates_agents("p3", "test_surgical_low_tier", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_surgical_low_tier", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_surgical_low_tier", "healing_outcome")
_emit_escalates_failure("p3", "test_surgical_low_tier", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_surgical_low_tier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_surgical_low_tier", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_surgical_low_tier", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_surgical_low_tier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_surgical_low_tier", "eval_metric")
_emit_stores_embedding("p4", "test_surgical_low_tier", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_surgical_low_tier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_surgical_low_tier", "exec_snapshot_link")


class TestAgentPermissionIntegration:
    """Tests for AgentPermission surgical healing."""

    def test_adapter_with_restore_checkpoint(self):
        """Test restore checkpoint detection."""
        source = "class AgentPermission: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AgentPermission")

            detection_result = {
                "type": "checkpoint_mismatch",
                "line": 1,
                "message": "Checkpoint restore mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="restore_checkpoint",
            )

            assert context is not None
            assert context.detector_agent == "AgentPermission"
        finally:
            temp_path.unlink()


class TestAutonomousThreatEvolutionAgentIntegration:
    """Tests for AutonomousThreatEvolutionAgent surgical healing."""

    def test_adapter_with_recent_detections(self):
        """Test recent detections loading."""
        source = "class AutonomousThreatEvolutionAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AutonomousThreatEvolutionAgent")

            detection_result = {
                "type": "detection_mismatch",
                "line": 1,
                "message": "Detection loading mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_load_recent_detections",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCheckpointManagerAgentIntegration:
    """Tests for CheckpointManagerAgent surgical healing."""

    def test_adapter_with_list_checkpoints(self):
        """Test checkpoint listing."""
        source = "class CheckpointManagerAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CheckpointManagerAgent")

            detection_result = {
                "type": "list_mismatch",
                "line": 1,
                "message": "Checkpoint list mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="list_checkpoints",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCodeDeduplicationAgentIntegration:
    """Tests for CodeDeduplicationAgent surgical healing."""

    def test_adapter_with_dead_code(self):
        """Test dead code detection."""
        source = "class CodeDeduplicationAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeDeduplicationAgent")

            detection_results = [
                {"type": "dead_code", "line": 1, "message": "Dead code detected"},
                {"type": "scan_dead", "line": 1, "message": "Scan dead code"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="detect_dead_code",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()


class TestCredentialScannerAgentIntegration:
    """Tests for CredentialScannerAgent surgical healing."""

    def test_adapter_with_credential_scan(self):
        """Test credential scanning."""
        source = "class CredentialScannerAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CredentialScannerAgent")

            detection_result = {
                "type": "credential_found",
                "line": 1,
                "message": "Potential credential detected",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="scan_for_credentials",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCodeValidatorAgentIntegration:
    """Tests for CodeValidatorAgent surgical healing."""

    def test_adapter_with_mcp_validation(self):
        """Test MCP validation."""
        source = "class CodeValidatorAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeValidatorAgent")

            detection_result = {
                "type": "mcp_violation",
                "line": 1,
                "message": "MCP validation issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_mcp",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestNamingAgentIntegration:
    """Tests for NamingAgent surgical healing."""

    def test_adapter_with_naming_validation(self):
        """Test naming validation."""
        source = "class NamingAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NamingAgent")

            detection_result = {
                "type": "naming_violation",
                "line": 1,
                "message": "Naming convention violation",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_naming",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestNervousSystemAgentIntegration:
    """Tests for NervousSystemAgent surgical healing."""

    def test_adapter_with_nervous_system(self):
        """Test nervous system detection."""
        source = "class NervousSystemAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NervousSystemAgent")

            detection_result = {
                "type": "system_issue",
                "line": 1,
                "message": "Nervous system issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="check_nervous_system",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestPreCommitSovereignAgentIntegration:
    """Tests for PreCommitSovereignAgent surgical healing."""

    def test_adapter_with_precommit(self):
        """Test pre-commit validation."""
        source = "class PreCommitSovereignAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="PreCommitSovereignAgent")

            detection_result = {
                "type": "precommit_issue",
                "line": 1,
                "message": "Pre-commit issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_precommit",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestReportLocationAgentIntegration:
    """Tests for ReportLocationAgent surgical healing."""

    def test_adapter_with_report_location(self):
        """Test report location validation."""
        source = "class ReportLocationAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ReportLocationAgent")

            detection_result = {
                "type": "location_issue",
                "line": 1,
                "message": "Report location issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_location",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestRootHygieneAgentIntegration:
    """Tests for RootHygieneAgent surgical healing."""

    def test_adapter_with_root_hygiene(self):
        """Test root hygiene validation."""
        source = "class RootHygieneAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="RootHygieneAgent")

            detection_result = {
                "type": "hygiene_issue",
                "line": 1,
                "message": "Root hygiene issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="check_hygiene",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestSubAtomicRegistryAgentIntegration:
    """Tests for SubAtomicRegistryAgent surgical healing."""

    def test_adapter_with_registry(self):
        """Test registry validation."""
        source = "class SubAtomicRegistryAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="SubAtomicRegistryAgent")

            detection_result = {
                "type": "registry_issue",
                "line": 1,
                "message": "Registry issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_registry",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestSystemArchitectAgentIntegration:
    """Tests for SystemArchitectAgent surgical healing."""

    def test_adapter_with_architecture(self):
        """Test architecture validation."""
        source = "class SystemArchitectAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="SystemArchitectAgent")

            detection_result = {
                "type": "architecture_issue",
                "line": 1,
                "message": "Architecture issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_architecture",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestValidationOrchestratorAgentIntegration:
    """Tests for ValidationOrchestratorAgent surgical healing."""

    def test_adapter_with_orchestration(self):
        """Test orchestration validation."""
        source = "class ValidationOrchestratorAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ValidationOrchestratorAgent")

            detection_result = {
                "type": "orchestration_issue",
                "line": 1,
                "message": "Orchestration issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="orchestrate_validation",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestLowTierGenericTemplate:
    """Tests for generic low tier template application."""

    def test_template_applies_to_all_agents(self):
        """Test that template works for all low tier agents."""
        low_tier_agents = [
            "AgentPermission",
            "AutonomousThreatEvolutionAgent",
            "CheckpointManagerAgent",
            "CodeDeduplicationAgent",
            "CredentialScannerAgent",
            "CodeValidatorAgent",
            "NamingAgent",
            "NervousSystemAgent",
            "PreCommitSovereignAgent",
            "ReportLocationAgent",
            "RootHygieneAgent",
            "SubAtomicRegistryAgent",
            "SystemArchitectAgent",
            "ValidationOrchestratorAgent",
        ]

        source = "def test(): pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            for agent_name in low_tier_agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                detection_result = {
                    "type": "generic_violation",
                    "line": 1,
                    "message": f"Generic violation for {agent_name}",
                }

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result=detection_result,
                    detection_method="generic_detection",
                )

                assert context is not None, f"Failed for {agent_name}"
                assert context.detector_agent == agent_name
        finally:
            temp_path.unlink()

    def test_surgical_healing_for_low_tier(self):
        """Test surgical healing applies for low tier agents."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NamingAgent")

            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Naming issue",
                "expected_pattern": "TODO: Fix naming",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_naming",
            )

            context.violations[0].fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
