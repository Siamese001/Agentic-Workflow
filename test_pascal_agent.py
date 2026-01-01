"""Quick validation script for PascalSovereigntyEnforcerAgent."""
from unittest.mock import MagicMock
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent

# Test instantiation
mock_ctx = MagicMock()
agent = PascalSovereigntyEnforcerAgent(ctx=mock_ctx, dry_run=True)
print('✓ Agent instantiated successfully')
print(f'  Name: {agent.name}')
print(f'  Dry run: {agent.dry_run}')
print(f'  Validation keys: {agent.get_validation_keys()}')

# Test integrated tests
print()
print('Running integrated test suite...')
test_results = agent._run_integrated_tests()
print(f'  All passed: {test_results["all_passed"]}')
for test in test_results['tests']:
    status = '✓' if test['passed'] else '✗'
    print(f'  {status} {test["name"]}')

print()
print('=== AGENT VALIDATION COMPLETE ===')
