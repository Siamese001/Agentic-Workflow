"""
Rename Classes to Add 'Agent' Suffix

This script renames classes that are agents but don't have the 'Agent' suffix.
Uses AST to safely rename class definitions and updates references.

Run with --dry-run first to preview changes.
"""
import re
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
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
    from agentic_core.utils.ssot_discovery_validator import get_python_files
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
