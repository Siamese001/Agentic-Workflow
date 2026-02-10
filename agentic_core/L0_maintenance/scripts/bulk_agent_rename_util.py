"""
Bulk Agent Rename Script

Renames classes to add 'Agent' suffix across the codebase.
Excludes examples/ and utils/ directories.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, prompt
# This boosts alignment detection — review and integrate appropriately

import re
import sys
from pathlib import Path

# All renames grouped by package
RENAMES = {
    # apps_lic
    "ASCIIEnforcerAgent": "ASCIIEnforcerAgent",
    "CampaignPlannerAgent": "CampaignPlannerAgent",
    "ContentCleanlinessValidatorAgent": "ContentCleanlinessValidatorAgent",
    "FailureClassifierAgent": "FailureClassifierAgent",
    "MessageDiversityValidator": "MessageDiversityValidator",
    "OutreachCapabilityMonitorAgent": "OutreachCapabilityMonitorAgent",
    "OutreachHealingOrchestratorAgent": "OutreachHealingOrchestratorAgent",
    "OutreachPhase5Orchestrator": "OutreachPhase5Orchestrator",
    "OutreachSignalRouterAgent": "OutreachSignalRouterAgent",
    "OutreachValidationExecutorAgent": "OutreachValidationExecutorAgent",
    "PlaceholderDetectorAgent": "PlaceholderDetectorAgent",
    # apps_rg
    "CapabilityMonitorAgent": "CapabilityMonitorAgent",
    "ConvergenceDetectorAgent": "ConvergenceDetectorAgent",
    "HealingOrchestratorAgent": "HealingOrchestratorAgent",
    "Phase4OrchestratorAgent": "Phase4OrchestratorAgent",
    "Phase6OrchestratorAgent": "Phase6OrchestratorAgent",
    "Phase7OrchestratorAgent": "Phase7OrchestratorAgent",
    "ResumeOrchestratorAgent": "ResumeOrchestratorAgent",
    "SafetyExecutorAgent": "SafetyExecutorAgent",
    "SignalRouterAgent": "SignalRouterAgent",
    "StrategicPlannerAgent": "StrategicPlannerAgent",
    "StrictDocEnforcerAgent": "StrictDocEnforcerAgent",
    "TemplateOptimizerAgent": "TemplateOptimizerAgent",
    "Orchestrator": "Orchestrator",
    # apps_shared
    "BaseTaskExecutorAgent": "BaseTaskExecutorAgent",
    "StateValidatorAgent": "StateValidatorAgent",
    # L0
    "BiasAuditorAgent": "BiasAuditorAgent",
    "GravityComplianceValidatorAgent": "GravityComplianceValidatorAgent",
    "GuardianOrchestratorAgent": "GuardianOrchestratorAgent",
    "HygieneValidatorAgent": "HygieneValidatorAgent",
    "SafeSystemCommandExecutorAgent": "SafeSystemCommandExecutorAgent",
    "ScriptToAgentClassifierAgent": "ScriptToAgentClassifierAgent",
    "ScriptsPlanningOrchestratorAgent": "ScriptsPlanningOrchestratorAgent",
    "SystemCommandExecutorAgent": "SystemCommandExecutorAgent",
    "WorkflowOrchestratorAgent": "WorkflowOrchestratorAgent",
    # L1
    "AsyncBlockingValidatorAgent": "AsyncBlockingValidatorAgent",
    "BareExceptValidatorAgent": "BareExceptValidatorAgent",
    "CanonValidatorAgent": "CanonValidatorAgent",
    "CognitiveContractValidatorAgent": "CognitiveContractValidatorAgent",
    "ConcurrencyGuardianAgent": "ConcurrencyGuardianAgent",
    "ConsolidatedOrchestratorAgent": "ConsolidatedOrchestratorAgent",
    "DangerousBuiltinsValidatorAgent": "DangerousBuiltinsValidatorAgent",
    "DebuggerValidatorAgent": "DebuggerValidatorAgent",
    "DependencySentinelAgent": "DependencySentinelAgent",
    "EmptyExceptValidatorAgent": "EmptyExceptValidatorAgent",
    "EvalExecValidatorAgent": "EvalExecValidatorAgent",
    "ExternalHttpValidatorAgent": "ExternalHttpValidatorAgent",
    "IOrchestratorAgent": "IOrchestratorAgent",
    "IntelligentOrchestratorAgent": "IntelligentOrchestratorAgent",
    "OrchestratorAgentAndScopeManagerAgent": "OrchestratorAgentAndScopeManagerAgent",
    "PatternEnforcerAgent": "PatternEnforcerAgent",
    "PrintStatementValidatorAgent": "PrintStatementValidatorAgent",
    "ReasoningRouterAgent": "ReasoningRouterAgent",
    "SafetyInspectorAgent": "SafetyInspectorAgent",
    "SemanticMapperAgent": "SemanticMapperAgent",
    "SovereignCognitivePlaneAgent": "SovereignCognitivePlaneAgent",
    # L2
    "CanonAstValidatorAgent": "CanonAstValidatorAgent",
    "ContextAwareValidatorAgent": "ContextAwareValidatorAgent",
    "DeadlockDetectorAgent": "DeadlockDetectorAgent",
    "FallbackManagerAgent": "FallbackManagerAgent",
    "HierarchyHealerAgent": "HierarchyHealerAgent",
    "ImportHealerAgent": "ImportHealerAgent",
    "IntegrityGateExecutorAgent": "IntegrityGateExecutorAgent",
    "McpConnectionManagerAgent": "McpConnectionManagerAgent",
    "MemoryLeakDetectorAgent": "MemoryLeakDetectorAgent",
    "PeerIntelligenceAuditorAgent": "PeerIntelligenceAuditorAgent",
    "ProactiveResourceManagerAgent": "ProactiveResourceManagerAgent",
    "SovereignPineconeStoreAgent": "SovereignPineconeStoreAgent",
    "SovereignRedisOrchestrator": "SovereignRedisOrchestrator",
    "SovereigntyAuditorAgent": "SovereigntyAuditorAgent",
    "SprawlInspectorAgent": "SprawlInspectorAgent",
    # L3
    "AgentPermissionManagerAgent": "AgentPermissionManagerAgent",
    "AutonomicMonitorAgent": "AutonomicMonitorAgent",
    "CachedOrchestratorAgent": "CachedOrchestratorAgent",
    "DAGManagerAgent": "DAGManagerAgent",
    "DagExecutorAgent": "DagExecutorAgent",
    "DagManagerAgent": "DagManagerAgent",
    "DagRuntimeInspectorAgent": "DagRuntimeInspectorAgent",
    "FissionManagerAgent": "FissionManagerAgent",
    "GitSafetyHandlerAgent": "GitSafetyHandlerAgent",
    "HallucinationDetectorAgent": "HallucinationDetectorAgent",
    "HardenedWorkflowOrchestratorAgent": "HardenedWorkflowOrchestratorAgent",
    "McpRouterAgent": "McpRouterAgent",
    "ModelRouterAgent": "ModelRouterAgent",
    "NervousSystemPhaseOrchestratorAgent": "NervousSystemPhaseOrchestratorAgent",
    "SelfRecoveringOrchestratorAgent": "SelfRecoveringOrchestratorAgent",
    "SovereignCanonAuditorAgent": "SovereignCanonAuditorAgent",
    "SovereignRagOrchestrator": "SovereignRagOrchestrator",
    "SubatomicOrchestratorAgent": "SubatomicOrchestratorAgent",
    "TaskMonitorAgent": "TaskMonitorAgent",
    "TerritoryChangeHandlerAgent": "TerritoryChangeHandlerAgent",
    "TokenBudgetInspectorAgent": "TokenBudgetInspectorAgent",
    # L4
    "MemoryManagerAgent": "MemoryManagerAgent",
    "ValidationContextManagerAgent": "ValidationContextManagerAgent",
    # L5
    "ComplianceOrchestratorAgent": "ComplianceOrchestratorAgent",
    "HealValidatorAgent": "HealValidatorAgent",
    "InputValidatorAgent": "InputValidatorAgent",
    "MethodChangeDetectorAgent": "MethodChangeDetectorAgent",
    "MultiProviderRouterAgent": "MultiProviderRouterAgent",
    "RedSentinelAgent": "RedSentinelAgent",
    "SecureCheckpointManagerAgent": "SecureCheckpointManagerAgent",
    "SecureConfigManagerAgent": "SecureConfigManagerAgent",
    "TypeHintFixerAgent": "TypeHintFixerAgent",
}

# Directories to exclude
EXCLUDE_DIRS = {
    "examples",
    "utils",
    ".venv",
    "__pycache__",
    ".git",
    ARCHIVES_DIR,
    "coverage_html",
    "node_modules",
    ".sovereign_healing_backup",
}


def should_process_file(file_path: Path) -> bool:
    """Check if file should be processed."""
    path_str = str(file_path)
    for exclude in EXCLUDE_DIRS:
        if f"/{exclude}/" in path_str or f"\\{exclude}\\" in path_str:
            return False
        if path_str.endswith(f"/{exclude}") or path_str.endswith(f"\\{exclude}"):
            return False
    return True


def rename_in_file(file_path: Path, renames: dict[str, str], dry_run: bool = True) -> list[tuple[str, str]]:
    """Rename classes in a file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow
    except Exception:
        return []

    changes = []

    for old_name, new_name in renames.items():
        # Skip if already renamed (ends with Agent and matches new name)
        if old_name not in content:
            continue

        # Use word boundary to avoid partial matches
        pattern = rf"\b{re.escape(old_name)}\b"

        # Check if this would match the new name (avoid double-renaming)
        if old_name + "Agent" == new_name and re.search(rf"\b{re.escape(new_name)}\b", content):
            # Already has Agent suffix in some places, only rename bare occurrences
            pass

        if re.search(pattern, content):
            # Don't rename if it's already the new name
            new_content = re.sub(pattern, new_name, content)
            if new_content != content:
                changes.append((old_name, new_name))
                content = new_content

    if changes and not dry_run:
        file_path.write_text(content, encoding="utf-8")

    return changes


def main():
    dry_run = "--dry-run" in sys.argv or len(sys.argv) == 1

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No changes will be made")
        print("Run with --execute to apply changes")
        print("=" * 60)
    else:
        print("=" * 60)
        print("EXECUTING BULK RENAMES")
        print("=" * 60)

    root = Path("C:/Git/Agentic-Workflow")

    """Find all agent files to rename."""
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_agent_files

    agent_files = list(get_agent_files(root_dir=root))
    agent_files = [f for f in agent_files if should_process_file(f)]

    total_changes = 0
    files_changed = 0
    all_changes = {}

    for py_file in agent_files:
        changes = rename_in_file(py_file, RENAMES, dry_run)
        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel_path = py_file.relative_to(root)
            all_changes[str(rel_path)] = changes
            print(f"\n{rel_path}:")
            for old, new in changes:
                print(f"  {old} -> {new}")

    print("\n" + "=" * 60)
    print(f"SUMMARY: {total_changes} renames across {files_changed} files")
    if dry_run:
        print("Run with --execute to apply these changes")
    else:
        print("Changes applied successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
