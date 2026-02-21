#!/usr/bin/env python3
"""Manual test runner for guardian tests."""

import sys
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    enforce_protected_root,
    SourceMutationBlocked,
)

def test_enforce_protected_root_blocks_agentic_core():
    """Test that writes to agentic_core are blocked."""
    target_path = Path("agentic_core/test_file.py")
    try:
        enforce_protected_root(target_path, allow_override=False)
        print("✗ FAIL: Should have blocked")
        return False
    except SourceMutationBlocked as e:
        print(f"✓ PASS: Blocked protected root: {e}")
        return True

def test_enforce_protected_root_allows_outside():
    """Test that writes outside protected roots are allowed."""
    target_path = Path("docs/evidence/test.md")
    try:
        enforce_protected_root(target_path, allow_override=False)
        print("✓ PASS: Allowed outside protected root")
        return True
    except SourceMutationBlocked:
        print("✗ FAIL: Should have allowed")
        return False

def test_enforce_protected_root_override_allows():
    """Test that override allows writes to protected roots."""
    target_path = Path("agentic_core/test_file.py")
    try:
        enforce_protected_root(target_path, allow_override=True)
        print("✓ PASS: Override allowed protected root")
        return True
    except SourceMutationBlocked:
        print("✗ FAIL: Override should have allowed")
        return False

def test_enforce_protected_root_blocks_tests():
    """Test that writes to tests directory are blocked."""
    target_path = Path("tests/test_file.py")
    try:
        enforce_protected_root(target_path, allow_override=False)
        print("✗ FAIL: Should have blocked tests directory")
        return False
    except SourceMutationBlocked as e:
        print(f"✓ PASS: Blocked tests directory: {e}")
        return True

def test_enforce_protected_root_blocks_github():
    """Test that writes to .github directory are blocked."""
    target_path = Path(".github/workflows/test.yml")
    try:
        enforce_protected_root(target_path, allow_override=False)
        print("✗ FAIL: Should have blocked .github directory")
        return False
    except SourceMutationBlocked as e:
        print(f"✓ PASS: Blocked .github directory: {e}")
        return True

def test_write_gateway_blocks():
    """Test write gateway integration."""
    from agentic_core.L2_execution.tools import write_gateway
    from unittest.mock import patch
    
    with patch("pathlib.Path.write_text") as mock_write:
        target_path = Path("agentic_core/test_file.py")
        try:
            write_gateway.write_text(target_path, "test content")
            print("✗ FAIL: Should have blocked")
            return False
        except SourceMutationBlocked as e:
            print(f"✓ PASS: Write gateway blocked: {e}")
            mock_write.assert_not_called()
            return True

def main():
    """Run all tests."""
    print("Running SSOT Mutation Fence Tests manually...")
    print("=" * 50)
    
    tests = [
        test_enforce_protected_root_blocks_agentic_core,
        test_enforce_protected_root_allows_outside,
        test_enforce_protected_root_override_allows,
        test_enforce_protected_root_blocks_tests,
        test_enforce_protected_root_blocks_github,
        test_write_gateway_blocks,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ ERROR in {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
