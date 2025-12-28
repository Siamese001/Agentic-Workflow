#!/usr/bin/env python3
"""
Simple wrapper to run canon validator on tests folder only.
Bypasses the recursive import issues in the main validator.
"""
import sys
import os
from pathlib import Path

# Set environment to prevent recursive loops
os.environ["SKIP_PREFLIGHT"] = "1"

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run
if __name__ == "__main__":
    import asyncio
    
    # Import the run_mission function directly
    from canon_validator_agentic_v2 import run_mission
    
    print("\n" + "="*70)
    print("RUNNING CANON VALIDATOR ON TESTS FOLDER ONLY")
    print("="*70)
    
    # Run with no-llm to avoid API quota issues
    asyncio.run(run_mission(
        target_scope="tests",
        structural_only=False,
        no_llm=True,
        batch_size=50
    ))
