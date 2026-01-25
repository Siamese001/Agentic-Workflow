import pytest
import subprocess
import sys


def test_run_e2e_verification():
    """
    Executes the End-to-End integration test.
    """
    test_path = "tests/e2e/test_rg_production_flow.py"

    # Run the specific test file
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v"], capture_output=True, text=True
    )

    # Check for "Broken Link" failure (Signature propagation)
    if result.returncode != 0:
        if "KeyError" in result.stderr or "Signature" in result.stderr:
            pytest.fail(
                f"E2E FAIL: Architectural Disconnect detected. Signature not propagating?\n{result.stderr}"
            )
        else:
            pytest.fail(f"E2E FAIL: System Integration Error.\n{result.stderr}\n{result.stdout}")

    print("\n[PASSED] apps_rg Modernization Complete.")
