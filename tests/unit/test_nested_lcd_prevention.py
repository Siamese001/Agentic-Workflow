"""
Test nested LCD prevention policy.

Validates:
- Leaf domains cannot sprout LCD subtrees
- Only L0-L6 layer roots may have LCD subfolders
- validate_no_nested_lcd() correctly detects violations
"""

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_nested_lcd_prevention", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_nested_lcd_prevention", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_nested_lcd_prevention", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_nested_lcd_prevention", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_nested_lcd_prevention", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_nested_lcd_prevention", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_nested_lcd_prevention", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_nested_lcd_prevention", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_nested_lcd_prevention", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_nested_lcd_prevention", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_nested_lcd_prevention", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_nested_lcd_prevention", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_nested_lcd_prevention", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_nested_lcd_prevention", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_nested_lcd_prevention", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_nested_lcd_prevention", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_nested_lcd_prevention", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_nested_lcd_prevention", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_nested_lcd_prevention", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_nested_lcd_prevention", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_nested_lcd_prevention", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_nested_lcd_prevention", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_nested_lcd_prevention", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_nested_lcd_prevention")
# REMOVED: _emit_applies_guardrail("p0", "test_nested_lcd_prevention", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_nested_lcd_prevention", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_nested_lcd_prevention", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_nested_lcd_prevention", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_nested_lcd_prevention", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_nested_lcd_prevention", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_nested_lcd_prevention", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_nested_lcd_prevention", "write_through")
# REMOVED: _emit_writes_through("p1", "test_nested_lcd_prevention", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_nested_lcd_prevention", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_nested_lcd_prevention", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_nested_lcd_prevention", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_nested_lcd_prevention", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_nested_lcd_prevention", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_nested_lcd_prevention", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_nested_lcd_prevention", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_nested_lcd_prevention", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_nested_lcd_prevention", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_nested_lcd_prevention", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_nested_lcd_prevention", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_nested_lcd_prevention", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_nested_lcd_prevention", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_nested_lcd_prevention", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_nested_lcd_prevention")
# REMOVED: _emit_gated_by_confidence("p1", "test_nested_lcd_prevention", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_nested_lcd_prevention")
# REMOVED: emit_determinism_digest("p0", "test_nested_lcd_prevention")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_nested_lcd_prevention", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_nested_lcd_prevention", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_nested_lcd_prevention", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_nested_lcd_prevention", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_nested_lcd_prevention", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_nested_lcd_prevention", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_nested_lcd_prevention", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_nested_lcd_prevention", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_nested_lcd_prevention", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_nested_lcd_prevention", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_nested_lcd_prevention", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_nested_lcd_prevention", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_nested_lcd_prevention", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_nested_lcd_prevention", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_nested_lcd_prevention", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_nested_lcd_prevention", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_nested_lcd_prevention", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_nested_lcd_prevention", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_nested_lcd_prevention", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_nested_lcd_prevention", "exec_snapshot_link")


class TestLeafDomainsNoLCD:
    """Tests for LEAF_DOMAINS_NO_LCD constant."""

    def test_leaf_domains_contains_expected(self):
        """LEAF_DOMAINS_NO_LCD contains known leaf domains."""
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
        from agentic_core.L5_safety.config.structure_blueprint import (
            LEAF_DOMAINS_NO_LCD,
            validate_no_nested_lcd,
        )
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

        expected = {
            "prompt_governance",
            "knowledge",
            "mixins",
            "runtime",
            "interfaces",
            "base_agents",
            "config",
        }
        assert expected.issubset(LEAF_DOMAINS_NO_LCD)

    def test_leaf_domains_is_frozenset(self):
        """LEAF_DOMAINS_NO_LCD must be immutable."""
        assert isinstance(LEAF_DOMAINS_NO_LCD, frozenset)


class TestValidateNoNestedLCD:
    """Tests for validate_no_nested_lcd() function."""

    @pytest.mark.parametrize(
        "leaf_domain,lcd_subfolder",
        [
            ("prompt_governance", "reasoning"),
            ("prompt_governance", "enforcement"),
            ("prompt_governance", "utils"),
            ("knowledge", "types"),
            ("runtime", "validators"),
            ("base_agents", "config"),
        ],
    )
    def test_nested_lcd_under_leaf_domain_flagged(self, leaf_domain: str, lcd_subfolder: str):
        """LCD subfolders under leaf domains must be flagged as violations."""
        path_parts = [AGENTIC_CORE_DIR, leaf_domain, lcd_subfolder]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None, f"Expected violation for {leaf_domain}/{lcd_subfolder}"
        assert result["domain"] == leaf_domain
        assert result["illegal_subfolder"] == lcd_subfolder

    @pytest.mark.parametrize(
        "layer,lcd_subfolder",
        [
            ("L0_routing", "reasoning"),
            ("L1_cognition", "enforcement"),
            ("L2_execution", "types"),
            ("L3_orchestration", "config"),
            ("L4_state", "validators"),
            ("L5_safety", "utils"),
            ("L6_observability", "reasoning"),
        ],
    )
    def test_lcd_under_layer_root_allowed(self, layer: str, lcd_subfolder: str):
        """LCD subfolders under layer roots are allowed."""
        path_parts = [AGENTIC_CORE_DIR, layer, lcd_subfolder]
        result = validate_no_nested_lcd(path_parts)
        assert result is None, f"Unexpected violation for {layer}/{lcd_subfolder}"

    def test_deeply_nested_lcd_allowed_under_layer(self):
        """LCD subfolders nested under layer scripts are allowed."""
        # L0_routing/scripts/prompt_governance is OK because L0 is a layer root
        path_parts = [AGENTIC_CORE_DIR, "L0_routing", "scripts", "prompt_governance"]
        result = validate_no_nested_lcd(path_parts)
        # This should be allowed because L0_routing is a layer root ancestor
        assert result is None

    def test_non_lcd_subfolder_under_leaf_allowed(self):
        """Non-LCD subfolders under leaf domains are allowed."""
        # prompt_governance/templates is not an LCD subfolder
        path_parts = [AGENTIC_CORE_DIR, "prompt_governance", "templates"]
        result = validate_no_nested_lcd(path_parts)
        assert result is None

    def test_empty_path_parts(self):
        """Empty path parts should not cause errors."""
        result = validate_no_nested_lcd([])
        assert result is None

    def test_single_element_path(self):
        """Single element path should not cause errors."""
        result = validate_no_nested_lcd([AGENTIC_CORE_DIR])
        assert result is None


class TestNestedLCDViolationMessage:
    """Tests for violation message content."""

    def test_violation_message_contains_domain(self):
        """Violation message should mention the offending domain."""
        path_parts = [AGENTIC_CORE_DIR, "prompt_governance", "reasoning"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "prompt_governance" in result["message"]

    def test_violation_message_contains_subfolder(self):
        """Violation message should mention the illegal subfolder."""
        path_parts = [AGENTIC_CORE_DIR, "knowledge", "enforcement"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "enforcement" in result["message"]

    def test_violation_message_mentions_layer_roots(self):
        """Violation message should mention that only layer roots may have LCD."""
        path_parts = [AGENTIC_CORE_DIR, "runtime", "validators"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "L0" in result["message"] or "layer roots" in result["message"].lower()
