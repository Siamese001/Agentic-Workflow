"""
Diagnostic Script: Neural Link & Fission Verification
Responsible for:
- Testing Gemini API connectivity via SubAtomicEngine.
- Verifying JSON blueprint generation for Key 42 surgery.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from root
project_root = Path(__file__).resolve().parent
load_dotenv(dotenv_path=project_root / ".env")

try:
    from agentic_core.L5_safety import SubAtomicEngine
    from apps_shared.canon_validation_context import ValidationContext
except ImportError as e:
    print(f"[X] Import Error: {e}")
    exit(1)

async def diagnose_engine():
    print(f"[*] Starting Neural Link Diagnostic...")
    print(f"    Model: {os.getenv('GEMINI_MODEL')}")
    
    # Initialize Engine
    ctx = ValidationContext()
    engine = SubAtomicEngine(gemini_client=None)
    
    # Test Task: Fission Blueprint Generation
    test_code = 'def test_func():\n    return "logic"\n' * 50 # Simulate file content
    task = "GENERATE_FISSION_BLUEPRINT for test_file.py. Split into logical sub-modules."
    
    print("\n[>] Testing resilient_mutation (Fission Mode)...")
    start_time = asyncio.get_event_loop().time()
    
    try:
        response = await engine.resilient_mutation(
            file_path="test_file.py",
            code=test_code,
            task=task,
            round_num=1,
            fission_active=True
        )
        
        duration = asyncio.get_event_loop().time() - start_time
        print(f"[OK] LLM Response received in {duration:.2f}s")
        
        if duration < 0.1:
            print("[ALERT] Zero-latency detected! The engine is bypassing the API.")
        
        # Verify JSON Structure
        print("\n[>] Parsing Fission Output...")
        blueprint = engine.parse_fission_output(response)
        
        if blueprint and blueprint.get("fission_event"):
            print("[SUCCESS] Valid Fission Blueprint generated.")
            print(f"          Modules identified: {list(blueprint['blueprint'].keys())}")
        else:
            print("[X] Failed to generate a valid Fission Blueprint JSON.")
            print(f"    Raw Response Preview: {str(response)[:100]}...")
            
    except Exception as e:
        print(f"[CRITICAL] Connectivity or Engine Failure: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_engine())
