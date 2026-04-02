#!/usr/bin/env python3
"""Profile ADG scanner to identify bottlenecks."""
import cProfile
import io
import pstats
import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def profile_scanner():
    """Profile the ADG scanner with detailed metrics."""
    print("🔍 Profiling ADG Scanner...")

    # Create profiler
    profiler = cProfile.Profile()

    # Start profiling
    profiler.enable()

    # Run scanner
    start_time = time.time()
    scanner = ADGStaticScanner(repo_root=Path.cwd())
    result = scanner.scan()
    end_time = time.time()

    # Stop profiling
    profiler.disable()

    # Get stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(50)  # Top 50 functions

    # Print summary
    print("\n📊 Scanner Profile Summary:")
    print(f"  Total scan time: {end_time - start_time:.2f}s")
    print(f"  Modules scanned: {len(result.module_graph)}")
    print(f"  Edges found: {len(result.edges)}")

    print("\n🔥 Top 20 Bottlenecks (by cumulative time):")
    lines = s.getvalue().split('\n')

    # Skip header and find actual function data
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('ncalls'):
            start_idx = i + 2
            break

    # Print top 20
    for i, line in enumerate(lines[start_idx:start_idx+20]):
        if line.strip() and not line.startswith('---'):
            parts = line.split()
            if len(parts) >= 6:
                ncalls, tottime, percall, cumtime, percall2, filename = parts[:6]
                # Clean up filename
                filename = filename.split('/')[-1] if '/' in filename else filename
                filename = filename.split('\\')[-1] if '\\' in filename else filename
                print(f"  {cumtime:>8}s {percall2:>8}s {ncalls:>8} {filename:<30}")

    # Save detailed profile
    profile_file = Path("scanner_profile.stats")
    profiler.dump_stats(str(profile_file))
    print(f"\n💾 Detailed profile saved to: {profile_file}")

    return result

if __name__ == "__main__":
    profile_scanner()
