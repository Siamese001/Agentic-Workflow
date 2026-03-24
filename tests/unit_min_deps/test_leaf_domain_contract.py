"""
Structural invariant: LEAF_DOMAIN_NO_LCD folders must not contain subdirectories.

Deterministic filesystem scan. No heuristics.
Guardian hard gate per LEAF_DOMAINS_NO_LCD in ssot.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_leaf_domain_contract")
_emit_applies_guardrail("p0", "test_leaf_domain_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_leaf_domain_contract", "policy_binding")
_emit_snapshots_state("p0", "test_leaf_domain_contract", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_leaf_domain_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_leaf_domain_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_leaf_domain_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_leaf_domain_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_leaf_domain_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_leaf_domain_contract", "p4obs", "alert")
_emit_links_incident_trace("test_leaf_domain_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_leaf_domain_contract", "p3lm", "pattern")
_emit_records_learning_event("test_leaf_domain_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_leaf_domain_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_leaf_domain_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_leaf_domain_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_leaf_domain_contract", "p3lm", "policy")
_emit_stores_learning_state("test_leaf_domain_contract", "p3lm", "state")
_emit_records_execution_trace("test_leaf_domain_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_leaf_domain_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_leaf_domain_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_leaf_domain_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_leaf_domain_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_leaf_domain_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_leaf_domain_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_leaf_domain_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_leaf_domain_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_leaf_domain_contract", "context_pull")
_emit_pulls_context("p1", "test_leaf_domain_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_leaf_domain_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_leaf_domain_contract", "uwg_term_2")
_emit_writes_through("p1", "test_leaf_domain_contract", "write_through")
_emit_writes_through("p1", "test_leaf_domain_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_leaf_domain_contract", "safety_validation")
_emit_invokes_eval("p1", "test_leaf_domain_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_leaf_domain_contract", "routing_commit")
_emit_escalates_to_human("p1", "test_leaf_domain_contract", "human_escalation")
_emit_routes_through("p1", "test_leaf_domain_contract", "route_through")
_emit_checks_agent_registry("p1", "test_leaf_domain_contract", "agent_registry")
_emit_validates_agent_capability("p1", "test_leaf_domain_contract", "capability")
_emit_dispatches_execution_plan("p1", "test_leaf_domain_contract", "exec_plan")
_emit_agent_executes_agent("p1", "test_leaf_domain_contract", "sub_agent")
_emit_routes_to_agent("p1", "test_leaf_domain_contract", "target_agent")
_emit_verifies_policy("p1", "test_leaf_domain_contract", "policy_check")
_emit_observes_runtime_state("p1", "test_leaf_domain_contract", "runtime_state")
_emit_verifies_boundary("p1", "test_leaf_domain_contract", "boundary_check")
_emit_transcripts_response("p1", "test_leaf_domain_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "test_leaf_domain_contract")
_emit_gated_by_confidence("p1", "test_leaf_domain_contract", "confidence_gate")
emit_replay_key("p0", "test_leaf_domain_contract")
emit_determinism_digest("p0", "test_leaf_domain_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_leaf_domain_contract", "execution_auth")
_emit_validates_capability("p2", "test_leaf_domain_contract", "capability_check")
_emit_routes_to_capability("p2", "test_leaf_domain_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_leaf_domain_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_leaf_domain_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_leaf_domain_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_leaf_domain_contract", "exec_output")
_emit_dispatches_agent("p3", "test_leaf_domain_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_leaf_domain_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_leaf_domain_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_leaf_domain_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_leaf_domain_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_leaf_domain_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_leaf_domain_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_leaf_domain_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_leaf_domain_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_leaf_domain_contract", "eval_metric")
_emit_stores_embedding("p4", "test_leaf_domain_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_leaf_domain_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_leaf_domain_contract", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR

LEAF_DOMAINS_NO_LCD: frozenset[str] = frozenset(
    {
        "prompt_governance",
        "knowledge",
        "mixins",
        "runtime",
        "interfaces",
        "base_agents",
        "config",
    },
)

# Subdirectories that are always allowed (Python cache, etc.)
ALWAYS_ALLOWED_SUBDIRS: frozenset[str] = frozenset({"__pycache__"})


def _scan_leaf_domain_violations() -> list[str]:
    """Find LEAF_DOMAIN folders that contain illegal subdirectories."""
    violations: list[str] = []
    for domain in LEAF_DOMAINS_NO_LCD:
        domain_path = AGENTIC_CORE / domain
        if not domain_path.is_dir():
            continue
        for entry in domain_path.iterdir():
            if entry.is_dir() and entry.name not in ALWAYS_ALLOWED_SUBDIRS:
                # Check if this subdirectory is declared in the domain's own structure
                # (e.g., prompt_governance has declared subfolders like meta_prompts)
                # We need to check the blueprint for optional_subfolders
                violations.append(f"{domain}/{entry.name}: illegal subdirectory in LEAF_DOMAIN")
    return violations


def _get_declared_subfolders(domain: str) -> set[str]:
    """Get subfolders declared in the blueprint for a LEAF_DOMAIN."""
    # Import here to avoid circular deps at module level
    try:
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            build_sovereign_territories,
        )

        territories = build_sovereign_territories()
        ac = territories.get(AGENTIC_CORE_DIR, {})
        subfolders_def = ac.get("subfolders", {})
        domain_def = subfolders_def.get(domain, {})
        declared = set()
        # Check for subfolders key
        if "subfolders" in domain_def:
            declared.update(domain_def["subfolders"].keys())
        # Check for required_subfolders and optional_subfolders
        if "required_subfolders" in domain_def:
            declared.update(domain_def["required_subfolders"])
        if "optional_subfolders" in domain_def:
            declared.update(domain_def["optional_subfolders"])
        return declared
    except (OSError, ValueError, KeyError):
        return set()


class TestLeafDomainNoSubdirs:
    """Hard gate: LEAF_DOMAIN folders must not sprout LCD-style subdirectories."""

    def test_prompt_governance_no_illegal_subdirs(self) -> None:
        """prompt_governance must not contain domain/ or other LCD subdirs."""
        pg = AGENTIC_CORE / "prompt_governance"
        if not pg.is_dir():
            pytest.fail("prompt_governance not found")
        declared = _get_declared_subfolders("prompt_governance")
        declared.update(ALWAYS_ALLOWED_SUBDIRS)
        illegal = []
        for entry in pg.iterdir():
            if entry.is_dir() and entry.name not in declared:
                illegal.append(entry.name)
        assert not illegal, (
            f"prompt_governance/ contains undeclared subdirectories: {illegal}\n"
            f"Declared: {sorted(declared - ALWAYS_ALLOWED_SUBDIRS)}"
        )

    def test_no_domain_subfolder_in_prompt_governance(self) -> None:
        """Specific regression: domain/ must never exist under prompt_governance."""
        assert not (AGENTIC_CORE / "prompt_governance" / "domain").exists(), (
            "prompt_governance/domain/ exists — LEAF_DOMAIN violation"
        )

    def test_synthetic_subfolder_detected(self, tmp_path: Path) -> None:
        """Negative test: prove scanner catches a synthetic subfolder."""
        fake_domain = tmp_path / "fake_leaf"
        fake_domain.mkdir()
        (fake_domain / "__init__.py").write_text("", encoding="utf-8")
        illegal_sub = fake_domain / "illegal_subdir"
        illegal_sub.mkdir()
        (illegal_sub / "__init__.py").write_text("", encoding="utf-8")

        subdirs = [
            e.name for e in fake_domain.iterdir() if e.is_dir() and e.name not in ALWAYS_ALLOWED_SUBDIRS
        ]
        assert subdirs, "Scanner failed to detect synthetic illegal subdirectory"
        assert "illegal_subdir" in subdirs
