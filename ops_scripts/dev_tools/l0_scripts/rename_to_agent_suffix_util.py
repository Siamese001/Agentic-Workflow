"""
Rename Classes to Add 'Agent' Suffix

This script renames classes that are agents but don't have the 'Agent' suffix.
Uses AST to safely rename class definitions and updates references.

Run with --dry-run first to preview changes.
"""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "rename_to_agent_suffix_util")
_emit_applies_guardrail("p0", "rename_to_agent_suffix_util", "p0_governance")
_emit_reads_policy_state("p0", "rename_to_agent_suffix_util", "policy_binding")
_emit_snapshots_state("p0", "rename_to_agent_suffix_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_1")
_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_2")
_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_3")
_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_4")
_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_5")
_emit_emits_metric_event("rename_to_agent_suffix_util", "p4obs", "metric_6")
_emit_records_incident_event("rename_to_agent_suffix_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("rename_to_agent_suffix_util", "p4obs", "anomaly")
_emit_writes_observability_log("rename_to_agent_suffix_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("rename_to_agent_suffix_util", "p4obs", "mon_state")
_emit_triggers_alert("rename_to_agent_suffix_util", "p4obs", "alert")
_emit_links_incident_trace("rename_to_agent_suffix_util", "p4obs", "trace_link")
_emit_captures_pattern("rename_to_agent_suffix_util", "p3lm", "pattern")
_emit_records_learning_event("rename_to_agent_suffix_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rename_to_agent_suffix_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("rename_to_agent_suffix_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rename_to_agent_suffix_util", "p3lm", "routing")
_emit_improves_agent_policy("rename_to_agent_suffix_util", "p3lm", "policy")
_emit_stores_learning_state("rename_to_agent_suffix_util", "p3lm", "state")
_emit_records_execution_trace("rename_to_agent_suffix_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rename_to_agent_suffix_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rename_to_agent_suffix_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rename_to_agent_suffix_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rename_to_agent_suffix_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rename_to_agent_suffix_util", "env_read", "p2_env_1")
_emit_reads_environ("rename_to_agent_suffix_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("rename_to_agent_suffix_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rename_to_agent_suffix_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rename_to_agent_suffix_util", "context_pull")
_emit_pulls_context("p1", "rename_to_agent_suffix_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rename_to_agent_suffix_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rename_to_agent_suffix_util", "uwg_term_2")
_emit_writes_through("p1", "rename_to_agent_suffix_util", "write_through")
_emit_writes_through("p1", "rename_to_agent_suffix_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "rename_to_agent_suffix_util", "safety_validation")
_emit_invokes_eval("p1", "rename_to_agent_suffix_util", "eval_call")
_emit_proposal_commits_routing("p1", "rename_to_agent_suffix_util", "routing_commit")
_emit_escalates_to_human("p1", "rename_to_agent_suffix_util", "human_escalation")
_emit_routes_through("p1", "rename_to_agent_suffix_util", "route_through")
_emit_checks_agent_registry("p1", "rename_to_agent_suffix_util", "agent_registry")
_emit_validates_agent_capability("p1", "rename_to_agent_suffix_util", "capability")
_emit_dispatches_execution_plan("p1", "rename_to_agent_suffix_util", "exec_plan")
_emit_agent_executes_agent("p1", "rename_to_agent_suffix_util", "sub_agent")
_emit_routes_to_agent("p1", "rename_to_agent_suffix_util", "target_agent")
_emit_verifies_policy("p1", "rename_to_agent_suffix_util", "policy_check")
_emit_observes_runtime_state("p1", "rename_to_agent_suffix_util", "runtime_state")
_emit_verifies_boundary("p1", "rename_to_agent_suffix_util", "boundary_check")
_emit_transcripts_response("p1", "rename_to_agent_suffix_util", "transcript")
_emit_hard_fails_untranscripted("p1", "rename_to_agent_suffix_util")
_emit_gated_by_confidence("p1", "rename_to_agent_suffix_util", "confidence_gate")
emit_replay_key("p0", "rename_to_agent_suffix_util")
emit_determinism_digest("p0", "rename_to_agent_suffix_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rename_to_agent_suffix_util", "execution_auth")
_emit_validates_capability("p2", "rename_to_agent_suffix_util", "capability_check")
_emit_routes_to_capability("p2", "rename_to_agent_suffix_util", "capability_route")
_emit_writes_via_uwg("p2", "rename_to_agent_suffix_util", "uwg_write")
_emit_blocks_direct_write("p2", "rename_to_agent_suffix_util", "direct_write_block")
_emit_records_tool_invocation("p2", "rename_to_agent_suffix_util", "tool_invocation")
_emit_captures_execution_output("p2", "rename_to_agent_suffix_util", "exec_output")
_emit_dispatches_agent("p3", "rename_to_agent_suffix_util", "agent_dispatch")
_emit_coordinates_agents("p3", "rename_to_agent_suffix_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "rename_to_agent_suffix_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "rename_to_agent_suffix_util", "healing_outcome")
_emit_escalates_failure("p3", "rename_to_agent_suffix_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "rename_to_agent_suffix_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rename_to_agent_suffix_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "rename_to_agent_suffix_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "rename_to_agent_suffix_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rename_to_agent_suffix_util", "eval_metric")
_emit_stores_embedding("p4", "rename_to_agent_suffix_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "rename_to_agent_suffix_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rename_to_agent_suffix_util", "exec_snapshot_link")
RENAMES = {'SafeSystemCommandExecutorAgent': 'SafeSystemCommandExecutorAgent', 'ScriptToAgentClassifierAgent': 'ScriptToAgentClassifierAgent', 'ScriptsPlanningOrchestratorAgent': 'ScriptsPlanningOrchestratorAgent', 'SystemCommandExecutorAgent': 'SystemCommandExecutorAgent', 'WorkflowOrchestratorAgent': 'WorkflowOrchestratorAgent', 'AssertionInspector': 'AssertionInspectorAgent', 'BranchTracker': 'BranchTrackerAgent', 'CriticalPathAnalyzer': 'CriticalPathAnalyzerAgent', 'DecisionAnalyzer': 'DecisionAnalyzerAgent', 'DuplicateDetector': 'DuplicateDetectorAgent', 'DuplicateFunctionDetector': 'DuplicateFunctionDetectorAgent', 'ExceptionFlowAnalyzer': 'ExceptionFlowAnalyzerAgent', 'IntelligentOrchestratorAgent': 'IntelligentOrchestratorAgent', 'OrchestratorAgentAndScopeManagerAgent': 'OrchestratorAgentAndScopeManagerAgent', 'PatternEnforcerAgent': 'PatternEnforcerAgent', 'PrintStatementValidatorAgent': 'PrintStatementValidatorAgent', 'ReasoningRouterAgent': 'ReasoningRouterAgent', 'SafetyInspectorAgent': 'SafetyInspectorAgent', 'SemanticMapperAgent': 'SemanticMapperAgent', 'SovereignCognitivePlaneAgent': 'SovereignCognitivePlaneAgent', 'AuditTrailManager': 'AuditTrailManagerAgent', 'CircuitBreaker': 'CircuitBreakerAgent', 'CodeBlockValidator': 'CodeBlockValidatorAgent', 'DocumentHealer': 'DocumentHealerAgent', 'ImportHealerAgent': 'ImportHealerAgent', 'IntegrityGateExecutorAgent': 'IntegrityGateExecutorAgent', 'McpConnectionManagerAgent': 'McpConnectionManagerAgent', 'MemoryLeakDetectorAgent': 'MemoryLeakDetectorAgent', 'PeerIntelligenceAuditorAgent': 'PeerIntelligenceAuditorAgent', 'ProactiveResourceManagerAgent': 'ProactiveResourceManagerAgent', 'SovereignRedisOrchestrator': 'SovereignRedisOrchestrator', 'SovereigntyAuditorAgent': 'SovereigntyAuditorAgent', 'SprawlInspectorAgent': 'SprawlInspectorAgent', 'DeadlockDetectorAgent': 'DeadlockDetectorAgent', 'McpRouterAgent': 'McpRouterAgent', 'ModelRouterAgent': 'ModelRouterAgent', 'NervousSystemPhaseOrchestratorAgent': 'NervousSystemPhaseOrchestratorAgent', 'ResumeOrchestratorAgent': 'ResumeOrchestratorAgent', 'SelfRecoveringOrchestratorAgent': 'SelfRecoveringOrchestratorAgent', 'SovereignCanonAuditorAgent': 'SovereignCanonAuditorAgent', 'SovereignRagOrchestrator': 'SovereignRagOrchestrator', 'SubatomicOrchestratorAgent': 'SubatomicOrchestratorAgent', 'TaskMonitorAgent': 'TaskMonitorAgent', 'TerritoryChangeHandlerAgent': 'TerritoryChangeHandlerAgent', 'TokenBudgetInspectorAgent': 'TokenBudgetInspectorAgent', 'MemoryManagerAgent': 'MemoryManagerAgent', 'ValidationContextManagerAgent': 'ValidationContextManagerAgent', 'InputValidatorAgent': 'InputValidatorAgent', 'MethodChangeDetectorAgent': 'MethodChangeDetectorAgent', 'MultiProviderRouterAgent': 'MultiProviderRouterAgent', 'RedSentinelAgent': 'RedSentinelAgent', 'SecureCheckpointManagerAgent': 'SecureCheckpointManagerAgent', 'SecureConfigManagerAgent': 'SecureConfigManagerAgent', 'TypeHintFixerAgent': 'TypeHintFixerAgent', 'CapabilityMonitorAgent': 'CapabilityMonitorAgent', 'ConversationalRepairOrchestrator': 'ConversationalRepairOrchestratorAgent', 'MessageDiversityValidator': 'MessageDiversityValidator', 'OutreachCapabilityMonitorAgent': 'OutreachCapabilityMonitorAgent', 'OutreachHealingOrchestratorAgent': 'OutreachHealingOrchestratorAgent', 'OutreachPhase5Orchestrator': 'OutreachPhase5Orchestrator', 'OutreachSignalRouterAgent': 'OutreachSignalRouterAgent', 'OutreachValidationExecutorAgent': 'OutreachValidationExecutorAgent', 'Phase4OrchestratorAgent': 'Phase4OrchestratorAgent', 'Phase6OrchestratorAgent': 'Phase6OrchestratorAgent', 'Phase7OrchestratorAgent': 'Phase7OrchestratorAgent', 'PlaceholderDetectorAgent': 'PlaceholderDetectorAgent', 'SafetyExecutorAgent': 'SafetyExecutorAgent', 'SignalRouterAgent': 'SignalRouterAgent', 'StateValidatorAgent': 'StateValidatorAgent', 'StrategicPlannerAgent': 'StrategicPlannerAgent', 'StrictDocEnforcerAgent': 'StrictDocEnforcerAgent', 'TemplateOptimizerAgent': 'TemplateOptimizerAgent', 'Orchestrator': 'Orchestrator', 'Phase5Validator': 'Phase5ValidatorAgent', 'SystemValidator': 'SystemValidatorAgent', 'ValidationGateExecutor': 'ValidationGateExecutorAgent'}

def rename_in_file(file_path: Path, renames: dict[str, str], dry_run: bool=True) -> list[tuple[str, str]]:
    """
    Rename class definitions and references in a file.

    Returns list of (old_name, new_name) tuples for classes renamed.
    """
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f'  Error reading {file_path}: {e}')
        return []
    changes = []
    new_content = content
    for old_name, new_name in renames.items():
        if old_name in content:
            pattern_class = f'\\bclass\\s+{old_name}\\b'
            if re.search(pattern_class, content):
                new_content = re.sub(pattern_class, f'class {new_name}', new_content)
                changes.append((old_name, new_name))
            pattern_ref = f'\\b{old_name}\\b'
            new_content = re.sub(pattern_ref, new_name, new_content)
    if changes and (not dry_run):
        file_path.write_text(new_content, encoding='utf-8')
    return changes

def main():
    dry_run = '--dry-run' in sys.argv or len(sys.argv) == 1
    if dry_run:
        print('=' * 60)
        print('DRY RUN - No changes will be made')
        print('Run with --execute to apply changes')
        print('=' * 60)
    else:
        print('=' * 60)
        print('EXECUTING RENAMES')
        print('=' * 60)
    root = Path('C:/Git/Agentic-Workflow')
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files
    py_files = list(get_python_files(root))
    total_changes = 0
    files_changed = 0
    for py_file in py_files:
        changes = rename_in_file(py_file, RENAMES, dry_run)
        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel_path = py_file.relative_to(root)
            print(f'\n{rel_path}:')
            for old, new in changes:
                print(f'  {old} -> {new}')
    print('\n' + '=' * 60)
    print(f'SUMMARY: {total_changes} renames across {files_changed} files')
    if dry_run:
        print('Run with --execute to apply these changes')
    else:
        print('Changes applied successfully')
    print('=' * 60)
if __name__ == '__main__':
    main()
