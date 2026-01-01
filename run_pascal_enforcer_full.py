"""Run PascalSovereigntyEnforcerAgent across entire repo."""
import asyncio
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent


async def main():
    print("=" * 80)
    print("PASCAL SOVEREIGNTY ENFORCER — FULL REPO EXECUTION")
    print("=" * 80)
    
    # Create agent with mock ctx and dry_run=False for actual changes
    agent = PascalSovereigntyEnforcerAgent(ctx=None, dry_run=False, _allow_mock=True)
    
    print(f"\nTarget prefixes: {agent.target_prefixes}")
    print(f"Purge order: {agent.purge_order}")
    print()
    
    # Execute across all layers
    result = await agent.execute(scope="all")
    
    print("\n" + "=" * 80)
    print("EXECUTION RESULTS")
    print("=" * 80)
    
    # Print audit summary
    audit = result.get("audit", {})
    print(f"\nAudit Summary: {audit.get('summary', 'N/A')}")
    print(f"Files with snake_case: {len(audit.get('files', []))}")
    print(f"Snake_case classes: {audit.get('snake_classes', 0)}")
    print(f"Backward-compat aliases: {audit.get('aliases', 0)}")
    
    # Print purge results
    results = result.get("results", [])
    if results:
        print(f"\nPurge Results ({len(results)} files):")
        for r in results[:20]:  # First 20
            status = r.get("status", "unknown")
            file = r.get("file", "unknown")
            print(f"  [{status}] {file}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more files")
    
    print(f"\nDry run: {result.get('dry_run', False)}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
