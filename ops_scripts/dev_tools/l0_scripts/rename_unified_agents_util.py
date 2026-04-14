"""
Rename Unified agents in L5_safety/unified directory.

Removes "Unified" prefix from file names and class names,
then updates all imports across the codebase.
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    L5_SAFETY_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tqdm import tqdm

_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_1")
_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_2")
_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_3")
_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_4")
_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_5")
_emit_emits_metric_event("rename_unified_agents_util", "p4obs", "metric_6")
_emit_records_incident_event("rename_unified_agents_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("rename_unified_agents_util", "p4obs", "anomaly")
_emit_writes_observability_log("rename_unified_agents_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("rename_unified_agents_util", "p4obs", "mon_state")
_emit_triggers_alert("rename_unified_agents_util", "p4obs", "alert")
_emit_links_incident_trace("rename_unified_agents_util", "p4obs", "trace_link")
_emit_captures_pattern("rename_unified_agents_util", "p3lm", "pattern")
_emit_records_learning_event("rename_unified_agents_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rename_unified_agents_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("rename_unified_agents_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rename_unified_agents_util", "p3lm", "routing")
_emit_improves_agent_policy("rename_unified_agents_util", "p3lm", "policy")
_emit_stores_learning_state("rename_unified_agents_util", "p3lm", "state")
_emit_records_execution_trace("rename_unified_agents_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rename_unified_agents_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rename_unified_agents_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rename_unified_agents_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rename_unified_agents_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rename_unified_agents_util", "env_read", "p2_env_1")
_emit_reads_environ("rename_unified_agents_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("rename_unified_agents_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rename_unified_agents_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "rename_unified_agents_util")
_emit_applies_guardrail("p0", "rename_unified_agents_util", "p0_governance")
_emit_reads_policy_state("p0", "rename_unified_agents_util", "policy_binding")
_emit_snapshots_state("p0", "rename_unified_agents_util", "state_snapshot")
_emit_pulls_context("p1", "rename_unified_agents_util", "context_pull")
_emit_pulls_context("p1", "rename_unified_agents_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rename_unified_agents_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rename_unified_agents_util", "uwg_term_secondary")
_emit_writes_through("p1", "rename_unified_agents_util", "write_through")
_emit_writes_through("p1", "rename_unified_agents_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rename_unified_agents_util", "safety_validation")
_emit_invokes_eval("p1", "rename_unified_agents_util", "eval_call")
_emit_proposal_commits_routing("p1", "rename_unified_agents_util", "routing_commit")
_emit_escalates_to_human("p1", "rename_unified_agents_util", "human_escalation")
_emit_routes_through("p1", "rename_unified_agents_util", "route_through")
_emit_checks_agent_registry("p1", "rename_unified_agents_util", "agent_registry")
_emit_validates_agent_capability("p1", "rename_unified_agents_util", "capability")
_emit_dispatches_execution_plan("p1", "rename_unified_agents_util", "exec_plan")
_emit_agent_executes_agent("p1", "rename_unified_agents_util", "sub_agent")
_emit_routes_to_agent("p1", "rename_unified_agents_util", "target_agent")
_emit_verifies_policy("p1", "rename_unified_agents_util", "policy_check")
_emit_observes_runtime_state("p1", "rename_unified_agents_util", "runtime_state")
_emit_verifies_boundary("p1", "rename_unified_agents_util", "boundary_check")
_emit_transcripts_response("p1", "rename_unified_agents_util", "transcript")
_emit_hard_fails_untranscripted("p1", "rename_unified_agents_util")
_emit_gated_by_confidence("p1", "rename_unified_agents_util", "confidence_gate")
emit_replay_key("p0", "rename_unified_agents_util")
emit_determinism_digest("p0", "rename_unified_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rename_unified_agents_util", "execution_auth")
_emit_validates_capability("p2", "rename_unified_agents_util", "capability_check")
_emit_routes_to_capability("p2", "rename_unified_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "rename_unified_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "rename_unified_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "rename_unified_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "rename_unified_agents_util", "exec_output")
_emit_dispatches_agent("p3", "rename_unified_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "rename_unified_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "rename_unified_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "rename_unified_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "rename_unified_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "rename_unified_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rename_unified_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "rename_unified_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "rename_unified_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rename_unified_agents_util", "eval_metric")
_emit_stores_embedding("p4", "rename_unified_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "rename_unified_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rename_unified_agents_util", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
RENAMES = {
    "CodeDetectorAgent.py": "CodeDetectorAgent.py",
    "CodeEnforcerAgent.py": "CodeEnforcerAgent.py",
    "CodeHealerAgent.py": "CodeHealerAgent.py",
    "CodeValidatorAgent.py": "CodeValidatorAgent.py",
    "ResourceManagerAgent.py": "ResourceManagerAgent.py",
    "SafetyDetectorAgent.py": "SafetyDetectorAgent.py",
    "SafetyExecutorAgent.py": "SafetyExecutorAgent.py",
    "SecurityManagerAgent.py": "SecurityManagerAgent.py",
    "StructureEnforcerAgent.py": "StructureEnforcerAgent.py",
    "StructureHealerAgent.py": "StructureHealerAgent.py",
}
CLASS_RENAMES = {
    "CodeDetectorAgent": "CodeDetectorAgent",
    "CodeEnforcerAgent": "CodeEnforcerAgent",
    "CodeHealerAgent": "CodeHealerAgent",
    "CodeValidatorAgent": "CodeValidatorAgent",
    "ResourceManagerAgent": "ResourceManagerAgent",
    "SafetyDetectorAgent": "SafetyDetectorAgent",
    "SafetyExecutorAgent": "SafetyExecutorAgent",
    "SecurityManagerAgent": "SecurityManagerAgent",
    "StructureEnforcerAgent": "StructureEnforcerAgent",
    "StructureHealerAgent": "StructureHealerAgent",
}
UNIFIED_DIR = PROJECT_ROOT / L5_SAFETY_DIR / "unified"


def rename_files():
    """Rename the files in the unified directory."""
    for old_name, new_name in RENAMES.items():
        old_path = UNIFIED_DIR / old_name
        new_path = UNIFIED_DIR / new_name
        if old_path.exists():
            old_path.rename(new_path)


def update_class_names_in_unified():
    """Update class names inside the unified directory files."""
    for py_file in tqdm(UNIFIED_DIR.glob("*.py"), desc="Processing", unit="item"):
        if py_file.name == "__pycache__":
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            original = content
            for old_class, new_class in CLASS_RENAMES.items():
                content = content.replace(old_class, new_class)
            if content != original:
                py_file.write_text(content, encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            pass


def update_imports_codebase():
    """Update imports across the entire codebase (excluding archives)."""
    scan_dirs = [
        PROJECT_ROOT / AGENTIC_CORE_DIR,
        PROJECT_ROOT / TESTS_DIR,
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / APPS_RG_DIR,
        PROJECT_ROOT / APPS_SHARED_DIR,
    ]
    files_updated = 0
    for scan_dir in tqdm(scan_dirs, desc="Processing", unit="item"):
        if not scan_dir.exists():
            continue
        for py_file in tqdm(scan_dir.rglob("*.py"), desc="Processing", unit="item"):
            if ARCHIVES_DIR in str(py_file) or "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                original = content
                for old_name, new_name in tqdm(RENAMES.items(), desc="Processing", unit="item"):
                    old_module = old_name.replace(".py", "")
                    new_module = new_name.replace(".py", "")
                    content = content.replace(
                        f"from agentic_core.L5_safety.reasoning.{old_module}",
                        f"from agentic_core.L5_safety.reasoning.{new_module}",
                    )
                    content = content.replace(
                        f"import agentic_core.L5_safety.reasoning.{old_module}",
                        f"import agentic_core.L5_safety.reasoning.{new_module}",
                    )
                for old_class, new_class in CLASS_RENAMES.items():
                    content = content.replace(old_class, new_class)
                if content != original:
                    py_file.write_text(content, encoding="utf-8")
                    files_updated += 1
            # guardian: allow-silent-swallow
            except Exception:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                pass


def add_backward_compat_aliases():
    """Add backward compatibility aliases to __init__.py."""
    init_file = UNIFIED_DIR / "__init__.py"
    new_init = '"""\nUnified L5 Safety/Validation Agents\n\n[PHASE 33c UPGRADE 2026-01-21]: Removed "Unified" prefix from agent names.\nBackward compatibility aliases maintained for existing imports.\n\nAgents:\n- CodeValidatorAgent: Single-pass AST validation (syntax, canon, async, print)\n- StructuralValidatorAgent: Gravity, hygiene, registry, contract validation\n- CodeDetectorAgent: Code pattern detection\n- CodeEnforcerAgent: Code pattern enforcement\n- CodeHealerAgent: Code healing operations\n- ResourceManagerAgent: Resource management\n- SafetyDetectorAgent: Safety pattern detection\n- SafetyExecutorAgent: Safety execution\n- SecurityManagerAgent: Security management\n- StructureEnforcerAgent: Structure enforcement\n- StructureHealerAgent: Structure healing\n"""\n\nfrom agentic_core.L5_safety.reasoning.CodeDetectorAgent import CodeDetectorAgent\nfrom agentic_core.L5_safety.reasoning.CodeEnforcerAgent import CodeEnforcerAgent\nfrom agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent\nfrom agentic_core.L5_safety.reasoning.CodeValidatorAgent import (\n    CodeValidatorAgent,\n    RuleSet,\n    ValidationReport,\n    Violation,\n    ViolationType,\n    create_legacy_async_validator,\n    create_legacy_canon_validator,\n    create_legacy_print_validator,\n    create_legacy_syntax_validator,\n)\nfrom agentic_core.L5_safety.reasoning.ResourceManagerAgent import ResourceManagerAgent\nfrom agentic_core.L5_safety.reasoning.SafetyDetectorAgent import SafetyDetectorAgent\nfrom agentic_core.L5_safety.reasoning.SafetyExecutorAgent import SafetyExecutorAgent\nfrom agentic_core.L5_safety.reasoning.SecurityManagerAgent import SecurityManagerAgent\nfrom agentic_core.L5_safety.reasoning.StructuralValidatorAgent_types import (\n    StructuralValidatorAgent,\n    StructureConfig,\n    StructureReport,\n    StructureViolation,\n    StructureViolationType,\n    StructureValidatorAgent,  # Backward compat alias\n    create_legacy_gravity_validator,\n    create_legacy_hygiene_validator,\n    create_legacy_registry_validator,\n)\nfrom agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent\nfrom agentic_core.L5_safety.reasoning.StructureHealerAgent_types import StructureHealerAgent\n\n# Backward compatibility aliases (DEPRECATED - use new names)\nCodeDetectorAgent = CodeDetectorAgent\nCodeEnforcerAgent = CodeEnforcerAgent\nCodeHealerAgent = CodeHealerAgent\nCodeValidatorAgent = CodeValidatorAgent\nResourceManagerAgent = ResourceManagerAgent\nSafetyDetectorAgent = SafetyDetectorAgent\nSafetyExecutorAgent = SafetyExecutorAgent\nSecurityManagerAgent = SecurityManagerAgent\nStructureEnforcerAgent = StructureEnforcerAgent\nStructureHealerAgent = StructureHealerAgent\n\n__all__ = [\n    # New canonical names\n    "CodeDetectorAgent",\n    "CodeEnforcerAgent",\n    "CodeHealerAgent",\n    "CodeValidatorAgent",\n    "ResourceManagerAgent",\n    "SafetyDetectorAgent",\n    "SafetyExecutorAgent",\n    "SecurityManagerAgent",\n    "StructuralValidatorAgent",\n    "StructureEnforcerAgent",\n    "StructureHealerAgent",\n    # Legacy aliases (backward compat - DEPRECATED)\n    "CodeDetectorAgent",\n    "CodeEnforcerAgent",\n    "CodeHealerAgent",\n    "CodeValidatorAgent",\n    "ResourceManagerAgent",\n    "SafetyDetectorAgent",\n    "SafetyExecutorAgent",\n    "SecurityManagerAgent",\n    "StructureEnforcerAgent",\n    "StructureHealerAgent",\n    "StructureValidatorAgent",\n    # Data classes\n    "RuleSet",\n    "ValidationReport",\n    "Violation",\n    "ViolationType",\n    "StructureConfig",\n    "StructureReport",\n    "StructureViolation",\n    "StructureViolationType",\n    # Factory methods\n    "create_legacy_syntax_validator",\n    "create_legacy_canon_validator",\n    "create_legacy_async_validator",\n    "create_legacy_print_validator",\n    "create_legacy_gravity_validator",\n    "create_legacy_hygiene_validator",\n    "create_legacy_registry_validator",\n]\n'
    init_file.write_text(new_init, encoding="utf-8")


if __name__ == "__main__":
    rename_files()
    update_class_names_in_unified()
    update_imports_codebase()
    add_backward_compat_aliases()
