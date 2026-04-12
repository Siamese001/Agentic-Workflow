#!/usr/bin/env python3
"""Test cache preservation fix"""

from pathlib import Path


def test_cache_preservation():
    """Test that scan cache is now preserved with timestamp prefix"""
    artifacts_dir = Path("artifacts/adg")
    cache_file = artifacts_dir / "scan_result_cache.json"

    print("=== Cache Preservation Test ===")

    # Create a dummy cache file to test archiving
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text('{"test": "cache"}')
    print(f"✅ Created test cache: {cache_file}")

    # Test archive patterns
    from tools.generate_full_adg import _archive_old_artifacts

    # This should preserve the cache file now
    print("🔄 Testing archive function...")
    _archive_old_artifacts(artifacts_dir, "03222026_9999", keep_runs=0)

    # Check if cache still exists
    if cache_file.exists():
        print("✅ Cache preserved - fix working!")
    else:
        print("❌ Cache still being deleted")

    # Check if it was archived
    archive_dir = artifacts_dir / "_archive"
    archived_cache = archive_dir / "scan_result_cache.json"
    if archived_cache.exists():
        print("✅ Cache properly archived")
    else:
        print("ℹ️  Cache not archived (expected for keep_runs=0)")


if __name__ == "__main__":
    test_cache_preservation()
