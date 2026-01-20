"""
Rename Classes to Add 'Agent' Suffix

This script renames classes that are agents but don't have the 'Agent' suffix.
Uses AST to safely rename class definitions and updates references.

Run with --dry-run first to preview changes.
"""
import ast
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from agentic_core.utils.sovereign_index import SovereignIndex

# Classes to rename: old_name -> new_name
RENAMES = {
    # L0 Maintenance
    "SafeSystemCommandExecutorAgent": "SafeSystemCommandExecutorAgent",
    "ScriptToAgentClassifierAgent": "ScriptToAgentClassifierAgent",
    "ScriptsPlanningOrchestratorAgent": "ScriptsPlanningOrchestratorAgent",
    "SystemCommandExecutorAgent": "SystemCommandExecutorAgent",
    "WorkflowOrchestratorAgent": "WorkflowOrchestratorAgent",
    
    # L1 Cognition
    "AssertionInspector": "AssertionInspectorAgent",
    "BranchTracker": "BranchTrackerAgent",
    "CriticalPathAnalyzer": "CriticalPathAnalyzerAgent",
    "DecisionAnalyzer": "DecisionAnalyzerAgent",
    "DuplicateDetector": "DuplicateDetectorAgent",
    "DuplicateFunctionDetector": "DuplicateFunctionDetectorAgent",
    "ExceptionFlowAnalyzer": "ExceptionFlowAnalyzerAgent",
    "IntelligentOrchestratorAgent": "IntelligentOrchestratorAgent",
    "OrchestratorAgentAndScopeManagerAgent": "OrchestratorAgentAndScopeManagerAgent",
    "PatternEnforcerAgent": "PatternEnforcerAgent",
    "PrintStatementValidatorAgent": "PrintStatementValidatorAgent",
    "ReasoningRouterAgent": "ReasoningRouterAgent",
    "SafetyInspectorAgent": "SafetyInspectorAgent",
    "SemanticMapperAgent": "SemanticMapperAgent",
    "SovereignCognitivePlaneAgent": "SovereignCognitivePlaneAgent",
    
    # L2 Execution
    "AuditTrailManager": "AuditTrailManagerAgent",
    "CircuitBreaker": "CircuitBreakerAgent",
    "CodeBlockValidator": "CodeBlockValidatorAgent",
    "DocumentHealer": "DocumentHealerAgent",
    "ImportHealerAgent": "ImportHealerAgent",
    "IntegrityGateExecutorAgent": "IntegrityGateExecutorAgent",
    "McpConnectionManagerAgent": "McpConnectionManagerAgent",
    "MemoryLeakDetectorAgent": "MemoryLeakDetectorAgent",
    "PeerIntelligenceAuditorAgent": "PeerIntelligenceAuditorAgent",
    "ProactiveResourceManagerAgent": "ProactiveResourceManagerAgent",
    "SovereignPineconeStoreAgent": "SovereignPineconeStoreAgent",
    "SovereignRedisOrchestratorAgent": "SovereignRedisOrchestratorAgent",
    "SovereigntyAuditorAgent": "SovereigntyAuditorAgent",
    "SprawlInspectorAgent": "SprawlInspectorAgent",
    
    # L3 Orchestration
    "DeadlockDetectorAgent": "DeadlockDetectorAgent",
    "McpRouterAgent": "McpRouterAgent",
    "ModelRouterAgent": "ModelRouterAgent",
    "NervousSystemPhaseOrchestratorAgent": "NervousSystemPhaseOrchestratorAgent",
    "ResumeOrchestratorAgent": "ResumeOrchestratorAgent",
    "SelfRecoveringOrchestratorAgent": "SelfRecoveringOrchestratorAgent",
    "SovereignCanonAuditorAgent": "SovereignCanonAuditorAgent",
    "SovereignRagOrchestratorAgent": "SovereignRagOrchestratorAgent",
    "SubatomicOrchestratorAgent": "SubatomicOrchestratorAgent",
    "TaskMonitorAgent": "TaskMonitorAgent",
    "TerritoryChangeHandlerAgent": "TerritoryChangeHandlerAgent",
    "TokenBudgetInspectorAgent": "TokenBudgetInspectorAgent",
    
    # L4 State
    "MemoryManagerAgent": "MemoryManagerAgent",
    "ValidationContextManagerAgent": "ValidationContextManagerAgent",
    
    # L5 Safety
    "InputValidatorAgent": "InputValidatorAgent",
    "MethodChangeDetectorAgent": "MethodChangeDetectorAgent",
    "MultiProviderRouterAgent": "MultiProviderRouterAgent",
    "RedSentinelAgent": "RedSentinelAgent",
    "SecureCheckpointManagerAgent": "SecureCheckpointManagerAgent",
    "SecureConfigManagerAgent": "SecureConfigManagerAgent",
    "TypeHintFixerAgent": "TypeHintFixerAgent",
    
    # Apps
    "CapabilityMonitorAgent": "CapabilityMonitorAgent",
    "ConversationalRepairOrchestrator": "ConversationalRepairOrchestratorAgent",
    "MessageDiversityValidatorAgent": "MessageDiversityValidatorAgent",
    "OutreachCapabilityMonitorAgent": "OutreachCapabilityMonitorAgent",
    "OutreachHealingOrchestratorAgent": "OutreachHealingOrchestratorAgent",
    "OutreachPhase5OrchestratorAgent": "OutreachPhase5OrchestratorAgent",
    "OutreachSignalRouterAgent": "OutreachSignalRouterAgent",
    "OutreachValidationExecutorAgent": "OutreachValidationExecutorAgent",
    "Phase4OrchestratorAgent": "Phase4OrchestratorAgent",
    "Phase6OrchestratorAgent": "Phase6OrchestratorAgent",
    "Phase7OrchestratorAgent": "Phase7OrchestratorAgent",
    "PlaceholderDetectorAgent": "PlaceholderDetectorAgent",
    "SafetyExecutorAgent": "SafetyExecutorAgent",
    "SignalRouterAgent": "SignalRouterAgent",
    "StateValidatorAgent": "StateValidatorAgent",
    "StrategicPlannerAgent": "StrategicPlannerAgent",
    "StrictDocEnforcerAgent": "StrictDocEnforcerAgent",
    "TemplateOptimizerAgent": "TemplateOptimizerAgent",
    "UnifiedOrchestratorAgent": "UnifiedOrchestratorAgent",
    
    # Utils
    "Phase5Validator": "Phase5ValidatorAgent",
    "SystemValidator": "SystemValidatorAgent",
    "ValidationGateExecutor": "ValidationGateExecutorAgent",
}


def rename_in_file(file_path: Path, renames: Dict[str, str], dry_run: bool = True) -> List[Tuple[str, str]]:
    """
    Rename class definitions and references in a file.
    
    Returns list of (old_name, new_name) tuples for classes renamed.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return []
    
    changes = []
    new_content = content
    
    for old_name, new_name in renames.items():
        if old_name in content:
            # Replace class definition
            pattern_class = rf'\bclass\s+{old_name}\b'
            if re.search(pattern_class, content):
                new_content = re.sub(pattern_class, f'class {new_name}', new_content)
                changes.append((old_name, new_name))
            
            # Replace references (imports, inheritance, instantiation)
            # Be careful not to replace partial matches
            pattern_ref = rf'\b{old_name}\b'
            new_content = re.sub(pattern_ref, new_name, new_content)
    
    if changes and not dry_run:
        file_path.write_text(new_content, encoding="utf-8")
    
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
        print("EXECUTING RENAMES")
        print("=" * 60)
    
    root = Path("C:/Git/Agentic-Workflow")
    
    # Find all Python files
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    py_files = list(get_python_files(root))
    
    total_changes = 0
    files_changed = 0
    
    for py_file in py_files:
        changes = rename_in_file(py_file, RENAMES, dry_run)
        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel_path = py_file.relative_to(root)
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
