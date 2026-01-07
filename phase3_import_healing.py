"""
Phase 3 Step 2: Import Healing
Fixes broken imports in relocated agents and their dependents.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L2_execution.ToolRegistry.ImportHealerAgent import ImportHealerAgent

async def main():
    print("\n" + "=" * 80)
    print("  PHASE 3 STEP 2: IMPORT HEALING")
    print("=" * 80 + "\n")
    
    print("Initializing ImportHealerAgent...")
    agent = ImportHealerAgent()
    
    print("Scanning for broken imports after Phase 2 relocation...")
    print("Target: 27 changed files from gravity relocation\n")
    
    try:
        result = await agent.heal_repository(execute=True)
        
        print("\n" + "=" * 80)
        print("  IMPORT HEALING COMPLETE")
        print("=" * 80 + "\n")
        
        print(f"Files healed: {result.get('files_healed', 0)}")
        print(f"Imports fixed: {result.get('imports_fixed', 0)}")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        
        if result.get('errors'):
            print(f"\nErrors encountered: {len(result['errors'])}")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Import healing failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "FAILED", "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result.get("status") == "SUCCESS" else 1)
