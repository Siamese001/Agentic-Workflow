#!/usr/bin/env python3
"""Show unified diffs for modified files"""
import subprocess

result = subprocess.run(
    ['git', 'diff', 'agentic_core/L2_execution/engines/tool_intent_executor.py'],
    capture_output=True,
    text=True,
    cwd=r'c:\Git\Agentic-Workflow'
)

print("=== DIFF: tool_intent_executor.py ===")
print(result.stdout if result.stdout else "(no changes)")
print()

result2 = subprocess.run(
    ['git', 'diff', 'agentic_core/L2_execution/wrappers/l2_agent_wrappers.py'],
    capture_output=True,
    text=True,
    cwd=r'c:\Git\Agentic-Workflow'
)

print("=== DIFF: l2_agent_wrappers.py (first 200 lines) ===")
lines = result2.stdout.split('\n')[:200]
print('\n'.join(lines))
if len(result2.stdout.split('\n')) > 200:
    print(f"\n... ({len(result2.stdout.split('\n')) - 200} more lines)")
