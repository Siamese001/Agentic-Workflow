"""
Run PascalSovereigntyEnforcerAgent over entire repo — full execution.
"""
import asyncio
import sys
import signal
from unittest.mock import MagicMock
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent


async def main():
    dry_run = "--live" not in sys.argv  # Default safe dry-run
    strict_mode = "--strict" in sys.argv  # Optional deep validation
    scope = sys.argv[sys.argv.index("--scope") + 1] if "--scope" in sys.argv else "all"
    
    mode_str = "DRY RUN (SAFE)" if dry_run else "LIVE EXECUTION"
    if strict_mode:
        mode_str += " | STRICT MODE (Deep Validation)"
    
    print(f"\n{'='*80}")
    print(f"PASCAL SOVEREIGNTY ENFORCER — {mode_str} | Scope: {scope}")
    print('='*80)
    
    # ctx mock only in dry-run — live requires full runtime ctx
    ctx = MagicMock() if dry_run else None  # Pass real ctx in live orchestrator
    agent = PascalSovereigntyEnforcerAgent(ctx=ctx, dry_run=dry_run, strict_mode=strict_mode, _allow_mock=True)
    
    # Run full AST audit first
    print("\n[PHASE 1] AST Audit...")
    audit = agent._ast_audit()
    print(f"Audit: {audit['summary']}")
    
    if audit["files"]:
        print(f"\nTarget files ({len(audit['files'])}):") 
        for f in audit["files"][:50]:
            print(f"  - {f}")
        if len(audit["files"]) > 50:
            print(f"  ... and {len(audit['files']) - 50} more")
    
    # Run execution
    print(f"\n[PHASE 2] {'Simulating' if dry_run else 'Executing'} purge...")
    result = await agent.execute(scope=scope)
    
    # Ultra Summary
    print(f"\n{'='*80}")
    print("SOVEREIGNTY EXECUTION SUMMARY")
    print('='*80)
    purged = sum(1 for r in result.get("results", []) if r["status"] == "purged")
    failed = sum(1 for r in result.get("results", []) if r["status"] == "failed_critique")
    no_change = sum(1 for r in result.get("results", []) if r["status"] == "no_change")
    print(f"Purged: {purged} | No Change: {no_change} | Failed Critique: {failed}")
    print(f"Dry Run: {dry_run} | Scope: {scope}")
    
    if failed > 0:
        print("\nFailed critique files (rollback applied):")
        for r in result.get("results", []):
            if r["status"] == "failed_critique":
                print(f"  - {r['file']} | Tests: {r['tests']}")
    
    return result


def signal_handler(sig, frame):
    print("\n[INTERRUPT] Execution aborted by user")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted")
    except Exception as e:
        print(f"\n[ERROR] {e}")
