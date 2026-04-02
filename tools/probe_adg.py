import asyncio
from pathlib import Path

# Test Runtime ADG Integration
print("=== RUNTIME ADG PROBE ===")

# Happy path
try:
    from test_runtime_adg_integration import test_runtime_adg_integration
    result = asyncio.run(test_runtime_adg_integration())
    print(f"Runtime ADG happy path: {'PASS' if result else 'FAIL'}")
except Exception as e:
    print(f"Runtime ADG happy path: FAIL - {e}")

# Failure path - non-existent directory
print("\n=== RUNTIME ADG FAILURE PATH ===")
import shutil
if Path("artifacts/runtime_adg_backup").exists():
    shutil.rmtree("artifacts/runtime_adg_backup")
shutil.move("artifacts/runtime_adg", "artifacts/runtime_adg_backup")
try:
    result2 = asyncio.run(test_runtime_adg_integration())
    print(f"Runtime ADG failure path: {'FAIL - should have handled missing dir' if result2 else 'PASS'}")
except Exception as e:
    print(f"Runtime ADG failure path: {'PASS' if 'No runtime ADG directory' in str(e) else 'FAIL'}")
finally:
    if Path("artifacts/runtime_adg_backup").exists():
        shutil.move("artifacts/runtime_adg_backup", "artifacts/runtime_adg")
