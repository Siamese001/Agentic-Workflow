"""Execute PascalSovereigntyEnforcerAgent with dry_run=False."""
import sys
sys.path.insert(0, '.')

from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
import asyncio

print("Executing PascalSovereigntyEnforcerAgent with dry_run=False...")
agent = PascalSovereigntyEnforcerAgent(ctx=None, dry_run=False, strict_mode=False, _allow_mock=True)
result = asyncio.run(agent.execute(scope='all'))

print('\n=== EXECUTION COMPLETE ===')
print(f"Status: {result.get('status', 'unknown')}")
print(f"Dry run: {result.get('dry_run', 'unknown')}")

if 'audit' in result:
    audit = result['audit']
    print(f"\nAudit Summary: {audit.get('summary', 'N/A')}")

if 'results' in result:
    results = result['results']
    purged = sum(1 for r in results if r.get('status') == 'purged')
    failed = sum(1 for r in results if 'failed' in r.get('status', ''))
    no_change = sum(1 for r in results if r.get('status') == 'no_change')
    
    print(f"\nResults:")
    print(f"  Purged: {purged}")
    print(f"  Failed: {failed}")
    print(f"  No change: {no_change}")
    print(f"  Total processed: {len(results)}")
