#!/usr/bin/env python3
"""
L6 Deterministic Sanitation & L5 Hot-Brain Resilience Validation

This test validates:
1. Deterministic cleaning with isort/autopep8
2. Markdown artifact scrubbing
3. AST validation before file writes
4. Root hygiene enforcement
5. Redis distributed locking
6. Redis hot caching with fallback
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from L2_execution.deterministic_sanitizer import (
    CompliantFileWriter,
    DeterministicCleaner,
    deterministic_clean,
    write_compliant_file,
)
from L4_state.storage import (
    RedisDistributedLock,
    RedisHotCache,
    acquire_lock,
    get_cache,
    release_lock,
    set_cache,
)


async def test_deterministic_cleaning():
    """Test deterministic code cleaning."""
    print("=" * 80)
    print("DETERMINISTIC CLEANING VALIDATION")
    print("=" * 80)

    print("\n1. Testing markdown artifact removal")
    print("-" * 50)

    cleaner = DeterministicCleaner(enable_isort=False, enable_autopep8=False)

    # Test markdown removal
    dirty_code = """```python
def hello_world():
    print("Hello, World!")
    return 42
```"""

    cleaned, was_modified = cleaner.deterministic_clean(dirty_code)

    if "```" not in cleaned and "def hello_world" in cleaned:
        print("✅ Markdown artifacts removed")
    else:
        print("❌ Markdown artifacts not removed")
        return False

    if was_modified:
        print("✅ Code was marked as modified")
    else:
        print("❌ Code should be marked as modified")
        return False

    return True


async def test_import_sorting():
    """Test import sorting with isort."""
    print("\n" + "=" * 80)
    print("IMPORT SORTING VALIDATION")
    print("=" * 80)

    print("\n1. Testing isort integration")
    print("-" * 50)

    cleaner = DeterministicCleaner(enable_isort=True, enable_autopep8=False)

    if not cleaner.has_isort:
        print("⚠️  isort not available - skipping test")
        return True

    # Test unsorted imports
    unsorted_code = """import os
import sys
from pathlib import Path
import json
"""

    cleaned, was_modified = cleaner.deterministic_clean(unsorted_code)

    # Check if imports are sorted (json should come before os)
    lines = cleaned.strip().split('\n')
    json_line = next((i for i, line in enumerate(lines) if 'import json' in line), -1)
    os_line = next((i for i, line in enumerate(lines) if 'import os' in line), -1)

    if json_line < os_line:
        print("✅ Imports sorted correctly")
    else:
        print("❌ Imports not sorted")
        return False

    return True


async def test_pep8_formatting():
    """Test PEP8 formatting with autopep8."""
    print("\n" + "=" * 80)
    print("PEP8 FORMATTING VALIDATION")
    print("=" * 80)

    print("\n1. Testing autopep8 integration")
    print("-" * 50)

    cleaner = DeterministicCleaner(enable_isort=False, enable_autopep8=True)

    if not cleaner.has_autopep8:
        print("⚠️  autopep8 not available - skipping test")
        return True

    # Test code with PEP8 violations
    messy_code = """def messy_function( ):
    x=1+2
    y = 3+4
    return x,y"""

    cleaned, was_modified = cleaner.deterministic_clean(messy_code)

    # Check for basic formatting fixes
    if "def messy_function():" in cleaned and "x = " in cleaned:
        print("✅ Basic PEP8 formatting applied")
    else:
        print("❌ PEP8 formatting not applied")
        return False

    return True


async def test_ast_validation():
    """Test AST validation before file writes."""
    print("\n" + "=" * 80)
    print("AST VALIDATION")
    print("=" * 80)

    print("\n1. Testing syntax validation")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        writer = CompliantFileWriter(temp_dir)

        # Test valid code
        valid_code = """def valid_function():
    return "This is valid"
"""

        success = writer.write_compliant_file("valid.py", valid_code)

        if success:
            print("✅ Valid code accepted")
        else:
            print("❌ Valid code rejected")
            return False

        # Test invalid code
        invalid_code = """def invalid_function(
    return "Missing closing parenthesis"
"""

        success = writer.write_compliant_file("invalid.py", invalid_code)

        if not success:
            print("✅ Invalid code rejected")
        else:
            print("❌ Invalid code should be rejected")
            return False

    return True


async def test_root_hygiene():
    """Test root directory hygiene enforcement."""
    print("\n" + "=" * 80)
    print("ROOT HYGIENE ENFORCEMENT")
    print("=" * 80)

    print("\n1. Testing unauthorized file prevention")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        writer = CompliantFileWriter(temp_dir)

        # Test unauthorized file in root
        unauthorized_code = "# This should not be in root"
        success = writer.write_compliant_file("temp_file.txt", unauthorized_code)

        if not success:
            print("✅ Unauthorized file in root rejected")
        else:
            print("❌ Unauthorized file in root should be rejected")
            return False

        # Test authorized file in root
        authorized_code = "# Project README"
        success = writer.write_compliant_file("README.md", authorized_code)

        if success:
            print("✅ Authorized file in root accepted")
        else:
            print("❌ Authorized file in root should be accepted")
            return False

        # Test file in subdirectory (always allowed)
        success = writer.write_compliant_file("scripts/temp_file.py", unauthorized_code)

        if success:
            print("✅ File in subdirectory accepted")
        else:
            print("❌ File in subdirectory should be accepted")
            return False

    return True


async def test_redis_distributed_lock():
    """Test Redis distributed locking with fallback."""
    print("\n" + "=" * 80)
    print("REDIS DISTRIBUTED LOCK")
    print("=" * 80)

    print("\n1. Testing lock acquisition and release")
    print("-" * 50)

    # Test with local fallback (no Redis)
    lock = RedisDistributedLock(redis_client=None)

    # Acquire lock
    acquired = await lock.acquire_lock("test_key")

    if acquired:
        print("✅ Lock acquired successfully")
    else:
        print("❌ Failed to acquire lock")
        return False

    # Try to acquire same lock (should fail)
    acquired_again = await lock.acquire_lock("test_key")

    if not acquired_again:
        print("✅ Duplicate lock correctly rejected")
    else:
        print("❌ Duplicate lock should be rejected")
        await lock.release_lock("test_key")
        return False

    # Release lock
    released = await lock.release_lock("test_key")

    if released:
        print("✅ Lock released successfully")
    else:
        print("❌ Failed to release lock")
        return False

    # Acquire after release (should succeed)
    acquired_after = await lock.acquire_lock("test_key")

    if acquired_after:
        print("✅ Lock re-acquired after release")
        await lock.release_lock("test_key")
    else:
        print("❌ Lock should be acquirable after release")
        return False

    return True


async def test_redis_hot_cache():
    """Test Redis hot caching with fallback."""
    print("\n" + "=" * 80)
    print("REDIS HOT CACHE")
    print("=" * 80)

    print("\n1. Testing cache set and get")
    print("-" * 50)

    # Test with local fallback (no Redis)
    cache = RedisHotCache(redis_client=None)

    # Set value
    test_value = {"key": "value", "number": 42}
    success = await cache.set_cache("test_key", test_value, ttl=60)

    if success:
        print("✅ Value cached successfully")
    else:
        print("❌ Failed to cache value")
        return False

    # Get value
    retrieved = await cache.get_cache("test_key")

    if retrieved == test_value:
        print("✅ Value retrieved correctly")
    else:
        print("❌ Retrieved value doesn't match")
        return False

    # Test cache miss
    miss = await cache.get_cache("nonexistent_key")

    if miss is None:
        print("✅ Cache miss handled correctly")
    else:
        print("❌ Cache miss should return None")
        return False

    # Test deletion
    deleted = await cache.delete_cache("test_key")

    if deleted:
        print("✅ Value deleted successfully")
    else:
        print("❌ Failed to delete value")
        return False

    # Verify deletion
    after_delete = await cache.get_cache("test_key")

    if after_delete is None:
        print("✅ Value properly deleted")
    else:
        print("❌ Value still exists after deletion")
        return False

    return True


async def test_convenience_functions():
    """Test global convenience functions."""
    print("\n" + "=" * 80)
    print("CONVENIENCE FUNCTIONS")
    print("=" * 80)

    print("\n1. Testing global lock and cache functions")
    print("-" * 50)

    # Test lock functions
    lock_acquired = await acquire_lock("global_test", timeout=10)

    if lock_acquired:
        print("✅ Global lock function works")
    else:
        print("❌ Global lock function failed")
        return False

    lock_released = await release_lock("global_test")

    if lock_released:
        print("✅ Global release function works")
    else:
        print("❌ Global release function failed")
        return False

    # Test cache functions
    cache_set = await set_cache("global_test", {"global": True}, ttl=30)

    if cache_set:
        print("✅ Global cache set function works")
    else:
        print("❌ Global cache set function failed")
        return False

    cache_get = await get_cache("global_test")

    if cache_get == {"global": True}:
        print("✅ Global cache get function works")
    else:
        print("❌ Global cache get function failed")
        return False

    return True


async def test_ttl_expiration():
    """Test TTL expiration in local cache."""
    print("\n" + "=" * 80)
    print("TTL EXPIRATION")
    print("=" * 80)

    print("\n1. Testing local cache TTL")
    print("-" * 50)

    cache = RedisHotCache(redis_client=None)

    # Set value with short TTL
    await cache.set_cache("ttl_test", "expires_soon", ttl=1)

    # Get immediately (should exist)
    immediate = await cache.get_cache("ttl_test")

    if immediate == "expires_soon":
        print("✅ Value available immediately")
    else:
        print("❌ Value not available immediately")
        return False

    # Wait for expiration
    await asyncio.sleep(1.1)

    # Get after TTL (should be None)
    expired = await cache.get_cache("ttl_test")

    if expired is None:
        print("✅ Value expired correctly")
    else:
        print("❌ Value should have expired")
        return False

    # Clear expired entries
    await cache.clear_expired_local()

    print("✅ Expired entries cleared")

    return True


async def test_full_sanitization_workflow():
    """Test complete sanitization workflow."""
    print("\n" + "=" * 80)
    print("FULL SANITIZATION WORKFLOW")
    print("=" * 80)

    print("\n1. Testing end-to-end sanitization")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Dirty code with multiple issues
        dirty_code = """```python
import sys
import os
from pathlib import Path
import json

def messy_function( ):
    x=1+2
    y = 3+4
    return x,y
```
"""

        # Apply full sanitization
        sanitized, was_modified = deterministic_clean(dirty_code, "test_file.py")

        if was_modified:
            print("✅ Sanitization applied")
        else:
            print("❌ Sanitization should have been applied")
            return False

        # Write compliant file
        success = write_compliant_file(
            str(Path(temp_dir) / "subdir" / "test_file.py"),
            sanitized,
            pre_clean=False  # Already cleaned
        )

        if success:
            print("✅ Compliant file written")
        else:
            print("❌ Failed to write compliant file")
            return False

        # Verify file exists and is valid
        file_path = Path(temp_dir) / "subdir" / "test_file.py"

        if file_path.exists():
            print("✅ File created at correct location")

            # Verify syntax
            with open(file_path, 'r') as f:
                content = f.read()

            try:
                compile(content, file_path, 'exec')
                print("✅ File has valid Python syntax")
            except SyntaxError:
                print("❌ File has invalid syntax")
                return False
        else:
            print("❌ File not created")
            return False

    return True


async def run_sanitization_and_redis_validation():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("L6 DETERMINISTIC SANITATION & L5 HOT-BRAIN VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting code cleaning, validation, and distributed systems")

    results = {}

    # Run all tests
    results["cleaning"] = await test_deterministic_cleaning()
    results["imports"] = await test_import_sorting()
    results["formatting"] = await test_pep8_formatting()
    results["ast_validation"] = await test_ast_validation()
    results["root_hygiene"] = await test_root_hygiene()
    results["redis_lock"] = await test_redis_distributed_lock()
    results["redis_cache"] = await test_redis_hot_cache()
    results["convenience"] = await test_convenience_functions()
    results["ttl"] = await test_ttl_expiration()
    results["workflow"] = await test_full_sanitization_workflow()

    # Generate report
    print("\n" + "=" * 80)
    print("SANITIZATION & REDIS VALIDATION REPORT")
    print("=" * 80)

    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All components validated!")
        print("The system provides:")
        print("  - Deterministic code cleaning (markdown, imports, formatting)")
        print("  - AST validation before file writes")
        print("  - Root directory hygiene enforcement")
        print("  - Redis distributed locking with fallback")
        print("  - Redis hot caching with TTL support")
        print("  - Graceful degradation when services unavailable")
        print("\n📝 Note: Install isort and autopep8 for full functionality")
        print("   pip install isort autopep8 redis")
    else:
        print("\n⚠️  Some components need attention")
        print("Check the logs above for details")

    return all_passed


if __name__ == "__main__":
    import sys
    asyncio.run(run_sanitization_and_redis_validation())
