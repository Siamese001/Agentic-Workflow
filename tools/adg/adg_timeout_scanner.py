#!/usr/bin/env python3
"""
ADG Timeout Scanner — Find subprocess calls without timeout via ADG edges

Replaces grep/regex patterns with ADG-powered queries for better performance
and accuracy in detecting subprocess calls that lack timeout parameters.

Usage:
    python tools/adg/adg_timeout_scanner.py
    python tools/adg/adg_timeout_scanner.py --directory agentic_core
    python tools/adg/adg_timeout_scanner.py --symbol subprocess.run
"""

import argparse
import warnings
from pathlib import Path

# Try to import ADG Query Bridge
try:
    from adg_query_bridge import ADGQueryBridge, FileMatch

    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable: {e}", stacklevel=2)
    ADG_AVAILABLE = False

    # Define fallback FileMatch class
    class FileMatch:
        def __init__(self, file_path: str, line_number: int = None, symbol: str = None, context: str = None):
            self.file_path = file_path
            self.line_number = line_number
            self.symbol = symbol
            self.context = context


class TimeoutViolation:
    """Represents a timeout violation found by the scanner."""

    def __init__(self, file_path: str, line_number: int, symbol: str, violation_type: str, context: str = ""):
        self.file_path = file_path
        self.line_number = line_number
        self.symbol = symbol
        self.violation_type = violation_type
        self.context = context

    def __repr__(self):
        return (
            f"TimeoutViolation({self.file_path}:{self.line_number} - {self.symbol} [{self.violation_type}])"
        )


class ADGTimeoutScanner:
    """Scanner for finding subprocess calls without timeout using ADG."""

    def __init__(self, repo_root: str | None = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.bridge = ADGQueryBridge(str(self.repo_root)) if ADG_AVAILABLE else None

    def scan_subprocess_calls(self, directories: list[str] | None = None) -> list[TimeoutViolation]:
        """Scan for subprocess calls without timeout parameters."""
        violations = []

        if not ADG_AVAILABLE:
            print("ADG not available, falling back to regex scanning")
            return self._fallback_regex_scan(directories)

        try:
            # Get all subprocess calls from ADG
            subprocess_calls = self.bridge.subprocess_calls_without_timeout()

            # Filter by directories if specified
            if directories:
                subprocess_calls = self._filter_by_directories(subprocess_calls, directories)

            # Analyze each call for timeout presence
            for call in subprocess_calls:
                violation = self._analyze_subprocess_call(call)
                if violation:
                    violations.append(violation)

        except Exception as e:
            warnings.warn(f"ADG scan failed, falling back to regex: {e}", stacklevel=2)
            violations = self._fallback_regex_scan(directories)

        return violations

    def _filter_by_directories(self, calls: list[FileMatch], directories: list[str]) -> list[FileMatch]:
        """Filter calls to only those in specified directories."""
        filtered = []
        for call in calls:
            call_path = Path(call.file_path)
            for directory in directories:
                dir_path = self.repo_root / directory
                if dir_path in call_path.parents or call_path.is_relative_to(dir_path):
                    filtered.append(call)
                    break
        return filtered

    def _analyze_subprocess_call(self, call: FileMatch) -> TimeoutViolation | None:
        """Analyze a subprocess call to determine if it has timeout."""
        try:
            # Read the specific line to check for timeout parameter
            file_path = self.repo_root / call.file_path
            if not file_path.exists():
                return None

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if call.line_number and call.line_number <= len(lines):
                line_content = lines[call.line_number - 1]

                # Check if timeout is present in the call
                if "timeout=" not in line_content:
                    # Determine violation type based on symbol
                    if "subprocess.run" in call.symbol:
                        violation_type = "subprocess.run_no_timeout"
                    elif "subprocess.Popen" in call.symbol:
                        violation_type = "subprocess.Popen_no_timeout"
                    else:
                        violation_type = "subprocess_call_no_timeout"

                    return TimeoutViolation(
                        file_path=call.file_path,
                        line_number=call.line_number,
                        symbol=call.symbol,
                        violation_type=violation_type,
                        context=line_content.strip(),
                    )
        except Exception as e:
            warnings.warn(f"Failed to analyze call {call.file_path}:{call.line_number}: {e}", stacklevel=2)

        return None

    def _fallback_regex_scan(self, directories: list[str] | None = None) -> list[TimeoutViolation]:
        """Fallback regex-based scanning when ADG is unavailable."""
        import re

        violations = []
        search_dirs = [self.repo_root / d for d in directories] if directories else [self.repo_root]

        # Regex patterns for subprocess calls
        subprocess_patterns = [
            r"subprocess\.run\s*\([^)]*\)",
            r"subprocess\.Popen\s*\([^)]*\)",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        for pattern in subprocess_patterns:
                            matches = re.finditer(pattern, line)
                            for match in matches:
                                call_text = match.group(0)
                                if "timeout=" not in call_text:
                                    # Determine violation type
                                    if "subprocess.run" in call_text:
                                        violation_type = "subprocess.run_no_timeout"
                                    elif "subprocess.Popen" in call_text:
                                        violation_type = "subprocess.Popen_no_timeout"
                                    else:
                                        violation_type = "subprocess_call_no_timeout"

                                    violations.append(
                                        TimeoutViolation(
                                            file_path=str(py_file.relative_to(self.repo_root)),
                                            line_number=line_num,
                                            symbol=call_text,
                                            violation_type=violation_type,
                                            context=line.strip(),
                                        ),
                                    )
                except Exception as e:
                    warnings.warn(f"Failed to scan {py_file}: {e}", stacklevel=2)

        return violations

    def scan_while_true_loops(self, directories: list[str] | None = None) -> list[TimeoutViolation]:
        """Scan for while True loops without timeout guards."""
        violations = []

        if not ADG_AVAILABLE:
            print("ADG not available, falling back to regex scanning for loops")
            return self._fallback_loop_scan(directories)

        try:
            # Use ADG to find loops without progress reporting
            loops = self.bridge.loops_without_progress()

            # Filter by directories if specified
            if directories:
                loops = self._filter_by_directories(loops, directories)

            # Analyze each loop for timeout guards
            for loop in loops:
                violation = self._analyze_loop_for_timeout(loop)
                if violation:
                    violations.append(violation)

        except Exception as e:
            warnings.warn(f"ADG loop scan failed, falling back to regex: {e}", stacklevel=2)
            violations = self._fallback_loop_scan(directories)

        return violations

    def _analyze_loop_for_timeout(self, loop: FileMatch, window: int = 100) -> TimeoutViolation | None:
        """Analyze a loop to determine if it has timeout guards."""
        try:
            file_path = self.repo_root / loop.file_path
            if not file_path.exists():
                return None

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            if loop.line_number and loop.line_number <= len(lines):
                # Look for timeout guards in surrounding context
                context_start = max(0, loop.line_number - window)
                context_end = min(len(lines), loop.line_number + (window // 5))
                context_lines = lines[context_start:context_end]
                context = "\n".join(context_lines)

                if "timeout_guard" not in context and "with timeout" not in context.lower():
                    return TimeoutViolation(
                        file_path=loop.file_path,
                        line_number=loop.line_number,
                        symbol="while True",
                        violation_type="while_true_no_timeout_guard",
                        context=lines[loop.line_number - 1].strip(),
                    )
        except Exception as e:
            warnings.warn(f"Failed to analyze loop {loop.file_path}:{loop.line_number}: {e}", stacklevel=2)

        return None

    def _fallback_loop_scan(self, directories: list[str] | None = None) -> list[TimeoutViolation]:
        """Fallback regex-based loop scanning when ADG is unavailable."""
        import re

        violations = []
        search_dirs = [self.repo_root / d for d in directories] if directories else [self.repo_root]

        # Pattern for while True loops
        while_true_pattern = r"while\s+True\s*:"

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(while_true_pattern, line)
                        for match in matches:
                            # Look for timeout guards in surrounding context
                            context_start = max(0, line_num - 50)
                            context_end = min(len(lines), line_num + 10)
                            context_lines = lines[context_start:context_end]
                            context = "\n".join(context_lines)

                            if "timeout_guard" not in context and "with timeout" not in context.lower():
                                violations.append(
                                    TimeoutViolation(
                                        file_path=str(py_file) if not py_file.is_relative_to(self.repo_root) else str(py_file.relative_to(self.repo_root)),
                                        line_number=line_num,
                                        symbol="while True",
                                        violation_type="while_true_no_timeout_guard",
                                        context=line.strip(),
                                    ),
                                )
                except Exception as e:
                    warnings.warn(f"Failed to scan {py_file}: {e}", stacklevel=2)

        return violations


def main():
    """Main entry point for the ADG timeout scanner."""
    parser = argparse.ArgumentParser(description="ADG Timeout Scanner")
    parser.add_argument(
        "--directory", action="append", help="Directories to scan (can be used multiple times)",
    )
    parser.add_argument("--symbol", help="Specific symbol to scan for")
    parser.add_argument("--loops", action="store_true", help="Scan for while True loops without timeout")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    scanner = ADGTimeoutScanner()

    if args.loops:
        violations = scanner.scan_while_true_loops(args.directory)
    else:
        violations = scanner.scan_subprocess_calls(args.directory)

    if args.format == "json":
        import json

        output = [
            {
                "file_path": v.file_path,
                "line_number": v.line_number,
                "symbol": v.symbol,
                "violation_type": v.violation_type,
                "context": v.context,
            }
            for v in violations
        ]
        print(json.dumps(output, indent=2))
    else:
        print("ADG Timeout Scanner Results")
        print("=========================")
        print(f"Found {len(violations)} timeout violations")
        print()

        # Group violations by type
        by_type = {}
        for v in violations:
            if v.violation_type not in by_type:
                by_type[v.violation_type] = []
            by_type[v.violation_type].append(v)

        for violation_type, type_violations in sorted(by_type.items()):
            print(f"{violation_type}:")
            for v in sorted(type_violations, key=lambda x: (x.file_path, x.line_number)):
                print(f"  {v.file_path}:{v.line_number} - {v.symbol}")
                if v.context:
                    print(f"    Context: {v.context}")
            print()

        if violations:
            print("Recommendations:")
            print("1. Add timeout parameters to all subprocess.run() calls")
            print("2. Add timeout context managers to while True loops")
            print("3. Use timeout_guard() wrapper for long-running operations")
        else:
            print("✅ No timeout violations found")


if __name__ == "__main__":
    main()
