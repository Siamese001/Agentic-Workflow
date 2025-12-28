"""
Master Mission Orchestrator - L6 Sovereignty Execution
Responsible for:
- Orchestrating 50-key canon validation sweeps.
- Enforcing Zero-Latency Neural Link integrity.
- Managing Atomic Fission (Key 42) for large files.
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
load_dotenv(dotenv_path=project_root / ".env", override=True)

# L6 Component Imports
from canon_validator_agentic_v2 import run_mission


async def execute_sovereign_sweep(target_scope: str = "agentic_core"):
    print(f"\n{'='*70}\n[L6] STARTING MASTER MISSION: {target_scope}\n{'='*70}")
    
    # 1. Initialize Hardened Neural Link
    try:
        engine = SubAtomicEngine()
        guardrail = SafetyGuardrail(deletion_limit=110)
        print(f"[OK] Neural Link Active: {os.getenv('GEMINI_MODEL')}")
        print(f"[OK] Safety Guardrail Active (AST Gate Enabled)")
    except Exception as e:
        print(f"[CRITICAL] Initialization Failure: {e}")
        return

    # 2. Configure Context with Fission Awareness
    ctx = ValidationContext()
    ctx.engine = engine
    ctx.safety = guardrail
    
    # 3. Execute Mission Sweep
    # This will trigger the Key 42 Fission for files > 1000 lines
    try:
        await run_mission(target_scope=target_scope)
    except Exception as e:
        print(f"\n[X] Mission Aborted: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*70}\n[L6] MASTER MISSION COMPLETE\n{'='*70}")

if __name__ == "__main__":
    # Ensure standard env vars are set for the mission
    os.environ['MAX_FILE_LINES'] = '1000'
    os.environ['RUN_GRAVITY_REFACTOR'] = 'True'
    
    asyncio.run(execute_sovereign_sweep())
