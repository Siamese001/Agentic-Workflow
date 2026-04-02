#!/usr/bin/env python3
"""Simple debug to identify hang location"""

import subprocess
import time


def run_with_timeout(cmd, timeout=30):
    """Run command with timeout and capture output"""
    print(f"Running: {cmd}")
    print(f"Timeout: {timeout}s")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="C:\\Git\\Agentic-Workflow"
        )
        print("✅ Command completed")
        print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
        print("STDERR:", result.stderr[-500:] if result.stderr else "None")
        return result.returncode == 0
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Command timed out after {timeout}s")
        return False
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Command failed: {e}")
        return False

def test_adg_components():
    """Test ADG components individually"""
    print("=== ADG Component Debug ===")

    # Test 1: Import only
    print("\n1. Testing imports...")
    try:
        import agentic_core.adg.extraction.static_scanner
        print("✅ Static scanner import OK")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Static scanner import failed: {e}")
        return

    # Test 2: Scanner creation
    print("\n2. Testing scanner creation...")
    try:
        from pathlib import Path
        scanner = agentic_core.adg.extraction.static_scanner.ADGStaticScanner(
            repo_root=Path("C:/Git/Agentic-Workflow"),
            cache_path=Path("artifacts/adg/scan_result_cache.json")
        )
        print("✅ Scanner creation OK")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Scanner creation failed: {e}")
        return

    # Test 3: File iteration (first 10 files)
    print("\n3. Testing file iteration (first 10 files)...")
    try:
        from agentic_core.adg.extraction.static_scanner import _iter_python_files
        files = list(_iter_python_files(scanner.repo_root))
        print(f"✅ Found {len(files)} Python files")
        print(f"First few files: {[str(f.relative_to(scanner.repo_root)) for f in files[:5]]}")

        # Test scanning one file
        test_file = files[0]
        print(f"Testing scan of: {test_file.relative_to(scanner.repo_root)}")
        from agentic_core.adg.extraction.static_scanner import _scan_file
        edges, had_error = _scan_file(test_file, scanner.repo_root, True)
        print(f"✅ Single file scan: {len(edges)} edges, error={had_error}")

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ File iteration failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 4: Limited scan (first 100 files)
    print("\n4. Testing limited scan (first 100 files)...")
    try:
        # Create a limited version by temporarily modifying the module function
        import agentic_core.adg.extraction.static_scanner as scanner_module
        original_iter = scanner_module._iter_python_files

        def limited_iter(root):
            for i, f in enumerate(original_iter(root)):
                if i >= 100:
                    break
                yield f

        scanner_module._iter_python_files = limited_iter

        start_time = time.time()
        result = scanner.scan()
        duration = time.time() - start_time

        # Restore original function
        scanner_module._iter_python_files = original_iter

        print(f"✅ Limited scan completed in {duration:.2f}s")
        print(f"   Modules: {len(result.modules)}")
        print(f"   Edges: {len(result.edges)}")
        print(f"   Cache hits: {result.manifest.cache_hits}")
        print(f"   Cache misses: {result.manifest.cache_misses}")

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Limited scan failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ All component tests passed!")

if __name__ == "__main__":
    test_adg_components()
