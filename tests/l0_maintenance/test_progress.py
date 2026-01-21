#!/usr/bin/env python3
"""
Test Progress Monitor with Color-Coded Progress Bars
Provides real-time feedback for long-running test operations.
"""
from __future__ import annotations

from pathlib import Path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install tqdm for better progress bars: pip install tqdm")


class ColoredProgress:
    """Color-coded progress indicator for test operations."""

    # ANSI color codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def scan_skipped_tests() -> tuple[int, int]:
        """Scan for skipped tests and return (total_files, total_skips)."""
        import re

        total_files = 0
        total_skips = 0
        skip_pattern = re.compile(r'@pytest\.mark\.skip')

        test_dir = Path(TESTS_UNIT_DIR)
        if not test_dir.exists():
            return 0, 0

        # Phase 6.7: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        test_files = list(get_python_files(test_dir))

        if HAS_TQDM:
            iterator = tqdm(test_files, desc=f"{ColoredProgress.CYAN}Scanning tests{ColoredProgress.RESET}",
                          bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
        else:
            iterator = test_files
            print(f"{ColoredProgress.CYAN}Scanning {len(test_files)} test files...{ColoredProgress.RESET}")

        for py_file in iterator:
            if '__pycache__' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                skip_count = len(skip_pattern.findall(content))
                if skip_count > 0:
                    total_files += 1
                    total_skips += skip_count
            except Exception:
                pass

        return total_files, total_skips

    @staticmethod
    def remove_skips_with_progress(dry_run: bool = False) -> tuple[int, int]:
        """Remove @pytest.mark.skip decorators with progress bar."""
        import re

        files_modified = 0
        skips_removed = 0
        skip_pattern = re.compile(r'@pytest\.mark\.skip\([^)]*\)\s*\n')

        test_dir = Path(TESTS_UNIT_DIR)
        # Phase 6.7: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        test_files = list(get_python_files(test_dir))

        if HAS_TQDM:
            color = ColoredProgress.YELLOW if dry_run else ColoredProgress.GREEN
            desc = f"{color}{'[DRY RUN] ' if dry_run else ''}Removing skips{ColoredProgress.RESET}"
            iterator = tqdm(test_files, desc=desc,
                          bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
        else:
            iterator = test_files
            print(f"{ColoredProgress.GREEN}Processing {len(test_files)} files...{ColoredProgress.RESET}")

        for py_file in iterator:
            try:
                content = py_file.read_text(encoding='utf-8')
                matches = skip_pattern.findall(content)

                if matches:
                    new_content = skip_pattern.sub('', content)
                    if not dry_run:
                        py_file.write_text(new_content, encoding='utf-8')
                    files_modified += 1
                    skips_removed += len(matches)
            except Exception as e:
                if HAS_TQDM:
                    tqdm.write(f"{ColoredProgress.RED}Error in {py_file.name}: {e}{ColoredProgress.RESET}")

        return files_modified, skips_removed

    @staticmethod
    def print_summary(files: int, skips: int, action: str = "found"):
        """Print colored summary."""
        color = ColoredProgress.GREEN if skips < 200 else ColoredProgress.YELLOW if skips < 400 else ColoredProgress.RED

        print(f"\n{ColoredProgress.BOLD}{'='*60}{ColoredProgress.RESET}")
        print(f"{ColoredProgress.BOLD}Test Skip Summary{ColoredProgress.RESET}")
        print(f"{ColoredProgress.BOLD}{'='*60}{ColoredProgress.RESET}")
        print(f"  Files {action}: {ColoredProgress.CYAN}{files}{ColoredProgress.RESET}")
        print(f"  Skips {action}: {color}{skips}{ColoredProgress.RESET}")

        if skips < 200:
            status = f"{ColoredProgress.GREEN}✓ EXCELLENT{ColoredProgress.RESET}"
        elif skips < 400:
            status = f"{ColoredProgress.YELLOW}⚠ NEEDS WORK{ColoredProgress.RESET}"
        else:
            status = f"{ColoredProgress.RED}✗ CRITICAL{ColoredProgress.RESET}"

        print(f"  Status: {status}")
        print(f"{ColoredProgress.BOLD}{'='*60}{ColoredProgress.RESET}\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Test Progress Monitor')
    parser.add_argument('--scan', action='store_true', help='Scan for skipped tests')
    parser.add_argument('--remove', action='store_true', help='Remove skip decorators')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')

    args = parser.parse_args()

    if args.scan or (not args.scan and not args.remove):
        print(f"{ColoredProgress.BLUE}Starting test scan...{ColoredProgress.RESET}\n")
        files, skips = ColoredProgress.scan_skipped_tests()
        ColoredProgress.print_summary(files, skips, "found")

    if args.remove:
        print(f"{ColoredProgress.BLUE}Starting skip removal...{ColoredProgress.RESET}\n")
        files, skips = ColoredProgress.remove_skips_with_progress(dry_run=args.dry_run)
        action = "would remove" if args.dry_run else "removed"
        ColoredProgress.print_summary(files, skips, action)


if __name__ == '__main__':
    main()
