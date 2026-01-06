import sys
sys.path.insert(0, '.')
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
import asyncio

agent = PascalSovereigntyEnforcerAgent(ctx=None, dry_run=True, strict_mode=False, _allow_mock=True)
result = asyncio.run(agent._run_critique_tests())

print('\n=== TEST RESULTS ===')
for t in result['tests']:
    status = 'PASS' if t['passed'] else 'FAIL'
    print(f"{t['name']}: {status}")

print(f"\nOverall: {'PASS' if result['basic_passed'] else 'FAIL'}")

# Debug failing tests
if not result['basic_passed']:
    print('\n=== DEBUGGING FAILURES ===')
    for t in result['tests']:
        if not t['passed']:
            print(f"\n{t['name']} FAILED")
