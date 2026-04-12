#!/usr/bin/env python3
"""Safe ADG scanner profiling with timeout and hang detection."""

import cProfile
import io
import pstats
import signal
import sys
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timeout_context(seconds):
    """Timeout context manager to prevent hangs."""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def profile_scanner_safe():
    """Safe profiler with timeout and progress reporting."""
    print("🔍 Profiling ADG Scanner (with timeout protection)...")

    # Create profiler
    profiler = cProfile.Profile()

    try:
        with timeout_context(300):  # 5 minute timeout
            print("  Starting scanner scan...")
            start_time = time.time()

            # Enable profiling
            profiler.enable()

            # Import and run scanner
            from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

            scanner = ADGStaticScanner(repo_root=Path.cwd())

            # Add progress reporting
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
            stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")

            print("\n🔥 Top 15 Performance Bottlenecks:")
            stats.print_stats(15)

            # Save detailed profile
            profile_file = Path("scanner_profile_safe.stats")
            profiler.dump_stats(str(profile_file))
            print(
                f"\n💾 Detailed profile saved to: {profile_file}"
            )  # guardian: TimeoutError should be handled with specific context

            return result

    # guardian: allow-silent-swallow - optional timeout handling
    except TimeoutError as e:
        print(f"⏰ TIMEOUT: {e}")
        print("  Scanner appears to be hanging. Let's investigate...")

        # Try to get partial stats
        profiler.disable()
        partial_file = Path("scanner_profile_partial.stats")
        profiler.dump_stats(str(partial_file))
        print(f"📝 Partial profile saved to: {partial_file}")

        # Investigate potential hang causes
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

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"   ERROR: {e}")

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

    # Check 4: Memory usage
    try:
        import psutil

        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        print(f"\n4. Memory usage: {memory_mb:.1f} MB")
    # guardian: allow-silent-swallow - optional dependency
    except ImportError:
        # psutil is optional for memory monitoring - this is acceptable
        print("\n4. psutil not available for memory monitoring")


if __name__ == "__main__":
    result = profile_scanner_safe()
    if result is None:
        print("\n Profiling failed due to hang/error")
        sys.exit(1)
    else:
        print("\n✅ Profiling completed successfully")
