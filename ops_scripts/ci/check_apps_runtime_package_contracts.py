#!/usr/bin/env python3
"""
GOV-3: Apps runtime package contracts (advisory)

Wrapper for tests/governance/test_apps_runtime_package_contracts.py

Exit codes:
  0 - PASS (no violations or advisory mode with warnings)
  1 - WARN (advisory mode, violations found)
  2 - FAIL (strict mode, violations found or test error)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
ADVISORY_SUNSET = "2026-06-15"
BYPASS_VAR = "GOV_PACKAGE_BYPASS"


def get_repo_root() -> Path:
    """Get repository root directory."""
    return Path(__file__).resolve().parents[2]


def get_enforcement_mode(cli_strict: bool) -> tuple[bool, str]:
    """Returns (is_strict, reason_message)."""
    today = datetime.now().isoformat()[:10]
    
    # Check bypass env var first
    if os.environ.get(BYPASS_VAR):
        return False, f"BYPASS ACTIVE ({BYPASS_VAR}=1)"
    
    # After sunset, strict is default
    if today > ADVISORY_SUNSET:
        if cli_strict:
            return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} passed, --strict flag)"
        return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} enforced)"
    
    # Before sunset, advisory default unless --strict passed
    if cli_strict:
        return True, "Strict mode (CLI flag)"
    
    return False, f"Advisory mode (sunset {ADVISORY_SUNSET})"


def run_governance_test() -> tuple[int, str, str]:
    """Run the actual governance test."""
    repo_root = get_repo_root()
    test_path = repo_root / "tests" / "governance" / "test_apps_runtime_package_contracts.py"
    
    if not test_path.exists():
        return 2, "", f"Test file not found: {test_path}"
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=120,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Test timed out after 120s"
    except Exception as e:
        return 2, "", f"Test execution error: {e}"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GOV-3: Check apps runtime package contracts"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail-closed mode (post-sunset, this is default)",
    )
    args = parser.parse_args()
    
    is_strict, mode_reason = get_enforcement_mode(args.strict)
    
    print(f"[GOV-3] Apps runtime package contracts")
    print(f"[GOV-3] Mode: {mode_reason}")
    
    # Run the test
    test_rc, stdout, stderr = run_governance_test()
    
    # Determine outcome
    if test_rc == 0:
        print(f"[GOV-3] ✅ PASS: Apps runtime package contracts valid")
        return 0
    
    # Test found violations or had errors
    if test_rc == 2 or "AssertionError" in stderr or "Error" in stderr:
        if is_strict:
            print(f"[GOV-3] ❌ FAIL: Violations or errors found in strict mode")
            if stdout:
                print(f"[GOV-3] STDOUT:\n{stdout}")
            if stderr:
                print(f"[GOV-3] STDERR:\n{stderr}", file=sys.stderr)
            return 2
        else:
            print(f"[GOV-3] ⚠️  WARN: Violations or errors found ({mode_reason})")
            print(f"[GOV-3] Reason: Package contract violations or test execution failed")
            if stdout:
                print(f"[GOV-3] Details:\n{stdout}")
            return 0  # Advisory = non-blocking
    
    # Test failures
    if is_strict:
        print(f"[GOV-3] ❌ FAIL: Test failures in strict mode")
        if stdout:
            print(f"[GOV-3] STDOUT:\n{stdout}")
        if stderr:
            print(f"[GOV-3] STDERR:\n{stderr}", file=sys.stderr)
        return 2
    else:
        print(f"[GOV-3] ⚠️  WARN: Test failures ({mode_reason})")
        if stdout:
            print(f"[GOV-3] Details:\n{stdout}")
        return 0  # Advisory = non-blocking


if __name__ == "__main__":
    sys.exit(main())
