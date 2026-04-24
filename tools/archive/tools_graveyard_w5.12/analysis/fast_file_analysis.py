#!/usr/bin/env python3
"""
Fast diagnostic script for broken file analysis with bounded operations and progress display.
Enforces constitutional requirements for progress reporting and PowerShell compatibility.
"""

import argparse
import ast
import collections
import pathlib
import sys
import time


class ProgressTracker:
    """Simple progress tracker with ANSI colors for terminal compatibility."""

    # ANSI color codes
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def start(self):
        """Initialize progress tracking."""
        self.start_time = time.time()
        print(f"{self.BLUE}🚀 {self.description}: Starting ({self.total} items){self.RESET}")

    def update(self, increment: int = 1, item_desc: str = ""):
        """Update progress with colored display."""
        self.current += increment
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time

        # ETA calculation
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f" ETA: {eta:.1f}s" if eta > 1 else ""
        else:
            eta_str = ""

        # Progress bar (40 characters)
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        # Color based on percentage
        if percentage >= 90:
            color = self.GREEN
        elif percentage >= 50:
            color = self.BLUE
        elif percentage >= 25:
            color = self.YELLOW
        else:
            color = self.RED

        status = f"{color}[{bar}] {percentage:.1f}%{self.RESET} ({self.current}/{self.total}){eta_str}"
        if item_desc:
            status += f" - {item_desc}"

        # Print on same line
        print(f"\r{self.description}: {status}", end="", flush=True)

    def complete(self, message: str = "Complete"):
        """Mark completion with success color."""
        print(f"\r{self.GREEN}✅ {self.description}: {message} ({self.total} items){self.RESET}")


def analyze_files_fast(
    tests_dir: pathlib.Path,
    max_files: int = 1000,
    pattern: str = "test_*.py",
) -> tuple[int, int, dict[str, int]]:
    """
    Fast bounded analysis of test files with progress display.

    Args:
        tests_dir: Directory to scan
        max_files: Maximum files to process (bounded operation)
        pattern: File pattern to match

    Returns:
        Tuple of (valid_count, broken_count, error_categories)
    """
    print(f"🔍 Starting fast file analysis (max {max_files} files)")

    # Collect files with progress
    all_files = list(tests_dir.rglob(pattern))
    # Filter out archives
    all_files = [f for f in all_files if "archive" not in str(f).lower()]

    # Apply file limit
    files_to_process = all_files[:max_files]
    total_files = len(files_to_process)

    print(f"📊 Found {len(all_files)} total files, processing {total_files} (limited)")

    # Initialize counters
    error_cats = collections.Counter()
    total_broken = 0
    total_valid = 0

    # Progress tracker
    tracker = ProgressTracker(total_files, "Analyzing files")
    tracker.start()

    # Process files with progress
    for i, f in enumerate(files_to_process):
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            ast.parse(content)
            total_valid += 1
            tracker.update(1, f"✅ {f.name}")
        except SyntaxError as e:
            total_broken += 1
            error_cats[e.msg] += 1
            tracker.update(1, f"❌ {f.name}: {e.msg}")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            total_broken += 1
            error_cats[f"Other: {type(e).__name__}"] += 1
            tracker.update(1, f"⚠️ {f.name}: {type(e).__name__}")

        # Early termination if we've seen enough patterns
        if len(error_cats) >= 10 and i > 100:
            print(f"\n🔄 Early termination: patterns converged after {i} files")
            break

    tracker.complete(f"Valid: {total_valid}, Broken: {total_broken}")
    print()  # Add newline for better formatting
    return total_valid, total_broken, error_cats


def print_summary(valid: int, broken: int, error_cats: dict[str, int], top_n: int = 10):
    """Print formatted summary with colors."""
    total = valid + broken
    if total == 0:
        print("📝 No files found to analyze")
        return

    print("\n📈 Analysis Summary:")
    print(f"   Total files: {total}")
    print(f"   {'🟢 Valid:':<12} {valid} ({valid / total * 100:.1f}%)")
    print(f"   {'🔴 Broken:':<12} {broken} ({broken / total * 100:.1f}%)")

    if error_cats:
        print(f"\n🔍 Top {top_n} error categories:")
        for i, (msg, cnt) in enumerate(error_cats.most_common(top_n)):
            percentage = cnt / broken * 100 if broken > 0 else 0
            print(f"   {i + 1:2d}. {cnt:5d} ({percentage:5.1f}%) - {msg}")


def main():
    """Main entry point with PowerShell-compatible argument parsing."""
    parser = argparse.ArgumentParser(
        description="Fast bounded file analysis with progress display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/fast_file_analysis.py
  python tools/fast_file_analysis.py --max-files 500
  python tools/fast_file_analysis.py --directory tests/unit
        """,
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default="tests",
        help="Directory to analyze (default: tests)",
    )

    parser.add_argument(
        "--max-files",
        "-m",
        type=int,
        default=1000,
        help="Maximum files to process (default: 1000)",
    )

    parser.add_argument(
        "--pattern",
        "-p",
        type=str,
        default="test_*.py",
        help="File pattern to match (default: test_*.py)",
    )

    args = parser.parse_args()

    # Validate directory
    tests_dir = pathlib.Path(args.directory)
    if not tests_dir.exists():
        print(f"❌ Directory not found: {tests_dir}")
        sys.exit(1)

    if not tests_dir.is_dir():
        print(f"❌ Not a directory: {tests_dir}")
        sys.exit(1)

    try:
        # Run analysis
        valid, broken, error_cats = analyze_files_fast(tests_dir, args.max_files, args.pattern)

        # Print summary
        print_summary(valid, broken, error_cats)

        # Exit code based on findings
        if broken > 0:
            print(f"\n⚠️ Found {broken} broken files")
            sys.exit(1)
        else:
            print(f"\n✅ All {valid} files are valid")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
