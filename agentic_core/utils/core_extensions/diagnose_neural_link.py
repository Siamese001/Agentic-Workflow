from __future__ import annotations
"""
Diagnostic Script: Neural Link & Fission Verification
Responsible for:
- Testing Gemini API connectivity via SubAtomicEngine.
- Verifying JSON blueprint generation for Key 42 surgery.
"""
import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent
load_dotenv(dotenv_path=project_root / ".env", override=True)

try:
    # Mock context for standalone execution
    class MockContext:

        def __init__(self):
            self.redis_client = None
            self.pinecone_index = None
except ImportError as e:
    print(f"[X] Import Error: {e}")
    exit(1)

async def diagnose_engine():
    '''Brief description of functionality and purpose.'''

    print(f"[*] Starting Neural Link Diagnostic...")
    print(f"    Target Model: {os.getenv('GEMINI_MODEL', 'Not Set')}")

    # Initialize Engine
    try:
        engine = SubAtomicEngine()
        print("[OK] SubAtomicEngine Initialized.")
    except Exception as e:
        print(f"[CRITICAL] Engine Init Failed: {e}")
        return

    # Test Task: Fission Blueprint Generation (Key 42 Simulation)
    # Creating a dummy file content that mimics a large node
    test_code = 'def operation_{i}():\n    return "data_{i}"\n\n' * 50
    Task = "GENERATE_FISSION_BLUEPRINT for test_large_node.py. Split into 3 logical sub-modules."

    print("\n[>] Testing resilient_mutation (Fission Mode: Key 42)...")
    start_time = time.time()

    try:
        response = await engine.resilient_mutation(
            file_path="test_large_node.py",
            code=test_code,
            Task=Task,
            round_num=1,
            fission_active=True
        )

        duration = time.time() - start_time
        print(f"[OK] LLM Response received in {duration:.2f}s")

        # 1. Latency Check
        if duration < 0.1:
            print("[ALERT] ZERO-LATENCY DETECTED! The engine is likely returning cached/empty data.")

        # 2. JSON Validation
        print("\n[>] Parsing Fission Output...")
        blueprint = engine.parse_fission_output(response)

        if blueprint and isinstance(blueprint, dict):
            print("[SUCCESS] Valid JSON Blueprint generated.")
            print(f"          Keys detected: {list(blueprint.keys())}")
            # Check for standard fission structure
            if "blueprint" in blueprint or any("module" in k for k in blueprint.keys()):
                print("   [✓] Blueprint contains logical module map.")
        else:
            print("[X] Failed to generate valid JSON.")
            print(f"    Raw Response Preview: {str(response)[:150]}...")

    except Exception as e:
        print(f"[CRITICAL] Connectivity or Engine Failure: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_engine())
