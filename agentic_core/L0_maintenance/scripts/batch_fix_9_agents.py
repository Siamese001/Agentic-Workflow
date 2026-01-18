#!/usr/bin/env python3
"""Batch fix remaining 9 agents by adding SubatomicTestingMixin."""
import re
from pathlib import Path

project_root = Path(__file__).parent.parent

agents = {
    'InterfaceBoundaryAgent': 'agentic_core/L2_execution/ToolRegistry/InterfaceBoundaryAgent.py',
    'MemoryArchitectAgent': 'agentic_core/L2_execution/ToolRegistry/MemoryArchitectAgent.py',
    'ImportLockAgent': 'agentic_core/L5_safety/guardrails/ImportLockAgent.py',
    'MultiProviderRouterAgent': 'agentic_core/L5_safety/guardrails/MultiProviderRouterAgent.py',
    'TestCoverageGuardianAgent': 'agentic_core/L5_safety/guardrails/TestCoverageGuardianAgent.py',
    'AutonomyGuardianAgent': 'agentic_core/L5_safety/validators/AutonomyGuardianAgent.py',
    'HygieneGuardianAgent': 'agentic_core/L5_safety/validators/HygieneGuardianAgent.py',
    'SyntaxValidatorAgent': 'agentic_core/L5_safety/validators/SyntaxValidatorAgent.py',
    'PerformanceAnalystAgent': 'agentic_core/L6_observability/agents/PerformanceAnalystAgent.py'
}

for agent_name, agent_path in agents.items():
    file_path = project_root / agent_path
    content = file_path.read_text(encoding='utf-8')
    
    if 'SubatomicTestingMixin' in content:
        print(f"Skip {agent_name}: Already has SubatomicTestingMixin")
        continue
    
    # Add import
    lines = content.split('\n')
    import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith(('import ', 'from ')) and 'import' in line:
            import_idx = i
    
    if import_idx >= 0:
        lines.insert(import_idx + 1, "from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin")
        content = '\n'.join(lines)
    
    # Add to class definition
    content = re.sub(
        rf'(class {agent_name}\s*\()',
        r'\1SubatomicTestingMixin, ',
        content
    )
    
    file_path.write_text(content, encoding='utf-8')
    print(f"Fixed {agent_name}")

print("\nDone! Now validating syntax...")
import subprocess
import sys

for agent_name, agent_path in agents.items():
    file_path = project_root / agent_path
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file_path)],
        capture_output=True
    )
    if result.returncode == 0:
        print(f"  OK {agent_name}")
    else:
        print(f"  ERROR {agent_name}: {result.stderr.decode()[:100]}")
