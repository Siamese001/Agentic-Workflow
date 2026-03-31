#!/usr/bin/env python3
"""Windows-compatible ADG scanner profiling."""
import cProfile
import io
import pstats
import sys
import threading
import time
from pathlib import Path


class TimeoutException(Exception):
    pass

def timeout_thread(seconds):
    """Timeout thread for Windows compatibility."""
    time.sleep(seconds)
    raise TimeoutException(f"Operation timed out after {seconds} seconds")

def profile_scanner_windows():
    """Windows-compatible profiler with timeout."""
    print("🔍 Profiling ADG Scanner (Windows-compatible)...")

    # Create profiler
    profiler = cProfile.Profile()

    # Start timeout thread
    timeout_seconds = 300  # 5 minutes
    timer_thread = threading.Thread(target=timeout_thread, args=(timeout_seconds,))
    timer_thread.daemon = True
    timer_thread.start()

    try:
        print("  Starting scanner scan...")
        start_time = time.time()

        # Enable profiling
        profiler.enable()

        # Import and run scanner
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
        scanner = ADGStaticScanner(repo_root=Path.cwd())

        print("  Scanner initialized, starting scan...")
        result = scanner.scan()

        # Disable profiling
        profiler.disable()

        end_time = time.time()
        scan_time = end_time - start_time

        print(f"✅ Scan completed in {scan_time:.2f}s")
        print(f"  Modules scanned: {len(result.module_graph)}")
        print(f"  Edges found: {len(result.edges)}")

        # Get and analyze stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')

        print("\n🔥 Top 15 Performance Bottlenecks:")
        stats.print_stats(15)

        # Save detailed profile
        profile_file = Path("scanner_profile_windows.stats")
        profiler.dump_stats(str(profile_file))
        print(f"\n💾 Detailed profile saved to: {profile_file}")

        return result

    # guardian: allow-silent-swallow - acceptable exception handling    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context    # guardian: TimeoutException should be handled with specific context
    except TimeoutException as e:
        print(f"⏰ TIMEOUT: {e}")
        print("  Scanner appears to be hanging. Investigating...")

        profiler.disable()
        partial_file = Path("scanner_profile_partial.stats")
        profiler.dump_stats(str(partial_file))
        print(f"📝 Partial profile saved to: {partial_file}")

        investigate_hang()
        return None

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def investigate_hang():
    """Investigate potential causes of scanner hangs."""
    print("\n🔍 Investigating potential hang causes...")

    # Check 1: IdentityNormalizer performance
    print("\n1. Testing IdentityNormalizer...")
    try:
        start = time.time()
        from agentic_core.adg.identity.normalizer import IdentityNormalizer
        normalizer = IdentityNormalizer(repo_root=Path.cwd())
        # This should trigger the rglob if not pre-warmed
        end = time.time()
        print(f"   IdentityNormalizer init: {end - start:.2f}s")

        # Test normalization
        start = time.time()
        result = normalizer.normalize("os.path")
        end = time.time()
        print(f"   Test normalization: {end - start:.4f}s")
        print(f"   Result: {result}")

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Check 2: File count
    print("\n2. Counting Python files...")
    try:
        start = time.time()
        py_files = list(Path.cwd().rglob("*.py"))
        end = time.time()
        print(f"   Python files found: {len(py_files)}")
        print(f"   File enumeration time: {end - start:.2f}s")

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"   ERROR: {e}")

    # Check 3: Cache status
    print("\n3. Checking cache status...")
    cache_file = Path("artifacts/adg/scan_result_cache.json")
    if cache_file.exists():
        size = cache_file.stat().st_size / (1024 * 1024)
        print(f"   Cache file: {cache_file}")
        print(f"   Cache size: {size:.1f} MB")
    else:
        print("   No cache file found")

    # Check 4: Test a single file scan
    print("\n4. Testing single file scan...")
    try:
        from agentic_core.adg.extraction.static_scanner import _scan_file
        test_file = Path.cwd() / "agentic_core" / "__init__.py"
        if test_file.exists():
            start = time.time()
            edges, error = _scan_file(test_file, Path.cwd())
            end = time.time()
            print(f"   Single file scan: {end - start:.4f}s")
            print(f"   Edges found: {len(edges)}")
            print(f"   Syntax error: {error}")
        else:
            print("   Test file not found")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = profile_scanner_windows()
    if result is None:
        print("\n❌ Profiling failed due to hang/error")
        sys.exit(1)
    else:
        print("\n✅ Profiling completed successfully")
