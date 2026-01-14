#!/usr/bin/env python3
"""
Fix agents with missing super().heal_repository() calls.
Adds proper invocation chain to reach 100% invocation rate.
"""
import re
from pathlib import Path

# Agents that need super().heal_repository() added
agents_to_fix = [
    # Already fixed: FilesystemSSOTReconcilerAgent, SovereignCognitivePlaneAgent, DynamicModelRouterAgent
    ("agentic_core/L5_safety/guardrails/MultiProviderRouterAgent.py", "MultiProviderRouterAgent"),
    ("agentic_core/L5_safety/agents/SemanticDebuggerAgent.py", "SemanticDebuggerAgent"),
    ("agentic_core/L6_observability/agents/PerformanceAnalystAgent.py", "PerformanceAnalystAgent"),
    ("agentic_core/L6_observability/agents/StrategicObservationAgent.py", "StrategicObservationAgent"),
    ("apps_lic/domain/validators/ContentCleanlinessValidatorAgent.py", "ContentCleanlinessValidatorAgent"),
    ("agentic_core/L1_cognition/learning/MetaLearningAgent.py", "MetaLearningAgent"),
]

fixed_count = 0

for file_path, agent_name in agents_to_fix:
    path = Path(file_path)
    if not path.exists():
        print(f"⚠️ File not found: {file_path}")
        continue
    
    content = path.read_text(encoding='utf-8')
    
    # Check if already has super().heal_repository() in heal_repository method
    if 'super().heal_repository(' in content:
        print(f"✅ Already fixed: {agent_name}")
        continue
    
    # Pattern to find heal_repository method that returns without super() call
    # Look for pattern: return {"skipped": 1} or return {"violations": 0, ...}
    # and add super().heal_repository() before the return
    
    # Pattern 1: return {"skipped": 1} in try block
    pattern1 = r'(print\(f"\[{agent_name}\][^"]*"\)\s*\n)(\s*)(return \{"skipped": 1\})'
    replacement1 = r'\1\2super().heal_repository(dry_run=dry_run, execute=execute, depth=depth+1, max_depth=max_depth, _call_path=_call_path)\n\2\3'
    
    new_content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: return {"violations": 0, "fixed": 0, "errors": 0} without super
    if new_content == content:
        pattern2 = r'(def heal_repository\([^)]+\)[^:]*:\s*"""[^"]*"""\s*\n)(\s*)(return \{"violations": 0)'
        replacement2 = r'\1\2super().heal_repository(dry_run=dry_run, execute=execute)\n\2\3'
        new_content = re.sub(pattern2, replacement2, content)
    
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        print(f"✅ Fixed: {agent_name}")
        fixed_count += 1
    else:
        print(f"⚠️ Could not auto-fix: {agent_name} - needs manual review")

print(f"\n{'='*70}")
print(f"Fixed {fixed_count} agents")
