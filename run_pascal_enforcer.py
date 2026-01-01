"""
Run PascalSovereigntyEnforcerAgent over agentic_core and apps_* folders.
"""
import asyncio
from unittest.mock import MagicMock
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent


async def main():
    ctx = MagicMock()
    agent = PascalSovereigntyEnforcerAgent(ctx=ctx, dry_run=True)
    
    scopes = ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]
    
    all_results = {}
    for scope in scopes:
        print(f"\n{'='*60}")
        print(f"SCANNING: {scope}")
        print('='*60)
        
        targets = agent._audit_snake_case(scope)
        print(f"Found {len(targets)} files with snake_case patterns")
        
        if targets:
            for t in targets[:20]:  # Show first 20
                print(f"  - {t}")
            if len(targets) > 20:
                print(f"  ... and {len(targets) - 20} more")
        
        all_results[scope] = targets
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    total = 0
    for scope, targets in all_results.items():
        print(f"{scope}: {len(targets)} files")
        total += len(targets)
    print(f"\nTOTAL: {total} files with snake_case patterns")
    
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
