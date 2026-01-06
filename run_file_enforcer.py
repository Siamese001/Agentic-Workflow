"""Execute PythonFileSovereigntyEnforcerAgent with dry_run=False."""
import sys
sys.path.insert(0, '.')

from agentic_core.L5_safety.validators.PythonFileSovereigntyEnforcerAgent import PythonFileSovereigntyEnforcerAgent
from pathlib import Path

print("Executing PythonFileSovereigntyEnforcerAgent with dry_run=False...")
agent = PythonFileSovereigntyEnforcerAgent(Path('.'), dry_run=False)
results = agent.run()

print('\n=== EXECUTION COMPLETE ===')
print(f"Total actions: {len(results)}")

proposed = sum(1 for r in results if r.get('status') == 'PROPOSED')
applied = sum(1 for r in results if r.get('status') == 'APPLIED')
failed = sum(1 for r in results if r.get('status') == 'FAILED')

print(f"\nResults:")
print(f"  Applied: {applied}")
print(f"  Failed: {failed}")
print(f"  Proposed (dry-run): {proposed}")

if failed > 0:
    print(f"\nFailed renames:")
    for r in results:
        if r.get('status') == 'FAILED':
            print(f"  {r['current_path']} → {r['expected_path']}")
