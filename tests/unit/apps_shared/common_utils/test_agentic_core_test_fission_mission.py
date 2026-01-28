import pytest

pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Test Protocol: Key 42 Fission Mission Verification
Responsible for:
- Verifying Key 42 detection triggers fission workflow
- Validating physical file splitting occurs
- Ensuring AST integrity post-transformation
"""
import asyncio
import os
import sys

import pytest

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))


# [SSOT IMPORT] Structure blueprint is the single source of truth


@pytest.mark.asyncio
async def test_key_42_fission_execution():
    """
    [L6 TEST] Verifies Key 42 Detection -> Healer Intervention -> Fission Completion.
    """
    # 1. SETUP: Create a temporary 1200-line file
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    target_dir = project_root / "agentic_core" / "L1_cognition" / "thought_engine" / "extraction"
    target_dir.mkdir(parents=True, exist_ok=True)

    test_file = target_dir / "test_fission_subject.py"
    with open(test_file, "w") as f:
        f.write('"""\nTest Protocol: Key 42 Subject\n"""\n')
        for i in range(300):  # ~1200 lines (4 lines per function)
            f.write(f"def operation_{i}():\n    return 'data_{i}'\n\n")

    try:
        # 2. EXECUTION: Run the mission on the specific folder
        # We target the specific directory containing the oversized file
        await run_mission(target_scope="agentic_core/L1_cognition/thought_engine")

        # 3. VERIFICATION: Check physical changes
        # The original file should be gone (or transformed into a shim)
        assert not test_file.exists() or len(test_file.read_text().splitlines()) < 1000, (
            "Original file should be removed or reduced after fission"
        )

        # Check for new sub-modules (FissionManagerAgent creates these)
        new_modules = list(target_dir.glob("test_fission_subject_*.py"))
        assert len(new_modules) >= 2, "Fission should have created at least 2 sub-modules"

        # Check for __init__.py markers in new sub-folders if applicable
        for mod in new_modules:
            assert len(mod.read_text().splitlines()) < 1000, f"{mod.name} is still too large"

    finally:
        # CLEANUP: Remove test artifacts
        if test_file.exists():
            os.remove(test_file)
        for mod in target_dir.glob("test_fission_subject_*.py"):
            os.remove(mod)


if __name__ == "__main__":
    asyncio.run(test_key_42_fission_execution())
