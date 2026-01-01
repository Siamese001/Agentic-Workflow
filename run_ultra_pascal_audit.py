"""Run ultra-hardened PascalSovereigntyEnforcerAgent dry audit."""
import asyncio
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent


async def main():
    print("=" * 70)
    print("ULTRA PASCAL SOVEREIGNTY ENFORCER - DRY AUDIT")
    print("=" * 70)
    
    agent = PascalSovereigntyEnforcerAgent(dry_run=True)
    
    # Run AST audit only (scope="all" for full audit)
    result = await agent.execute(scope="all")
    
    print()
    print("=" * 70)
    print("AUDIT RESULTS")
    print("=" * 70)
    
    if "audit" in result:
        audit = result["audit"]
        print(f"Files with snake_case: {len(audit['files'])}")
        print(f"Snake_case classes: {audit['snake_classes']}")
        print(f"Backward-compat aliases: {audit['aliases']}")
        print()
        print("Summary:", audit["summary"])
    
    if "results" in result:
        print()
        print(f"Layer results: {len(result['results'])} files processed")
        
        # Count by status
        by_status = {}
        for r in result["results"]:
            status = r["status"]
            by_status[status] = by_status.get(status, 0) + 1
        
        for status, count in by_status.items():
            print(f"  {status}: {count}")
    
    print()
    print(f"Dry run: {result.get('dry_run', True)}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
