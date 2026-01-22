"""Test script for Phase 31b Horizontal Boundary Detection."""
from pathlib import Path
from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
agent = ArchitectureGovernorAgent(project_root=Path('.'))
result = agent.detect_horizontal_violations(target_layer='L3_orchestration')
if result['violations']:
    for v in result['violations']:
        pass
result5 = agent.detect_horizontal_violations(target_layer='L5_safety')
if result5['violations']:
    for v in result5['violations'][:10]:
        pass
    if len(result5['violations']) > 10:
        pass