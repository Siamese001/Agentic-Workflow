#!/usr/bin/env python3
"""
PowerShell Usage Ban Guardrail

Enforces user preference: NEVER use PowerShell for shell commands or evidence generation.
ALWAYS use Python subprocess or direct Python file operations instead.

PowerShell has parsing issues with heredocs and complex pipelines that cause hangs and errors.

Usage:
    python ops_scripts/ci/check_powershell_ban.py [--fix]

Exit codes:
    0 - No PowerShell usage found
    1 - PowerShell usage detected (build fails)
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()


class PowerShellBanChecker:
    """Enforces PowerShell usage ban across the repository."""

    # PowerShell patterns to detect
    POWERSHELL_PATTERNS = [
        # Direct PowerShell executable calls
        r"powershell\.exe",
        r"pwsh\.exe",
        r"PowerShell\.",

        # PowerShell cmdlets
        r"Start-Process",
        r"Invoke-Expression",
        r"Invoke-Command",
        r"New-Object",
        r"Get-Content",
        r"Set-Content",
        r"Out-File",
        r"Write-Output",
        r"Write-Host",
        r"Write-Error",
        r"Try-Catch",
        r"ForEach-Object",
        r"Where-Object",
        r"Select-Object",
        r"Sort-Object",
        r"Group-Object",

        # PowerShell operators and syntax
        r"\$[a-zA-Z_][a-zA-Z0-9_]*",  # Variables like $var
        r"\$\([^)]+\)",  # Subexpression operator
        r"@\(.*?\)",  # Array operator
        r"%\{.*?\}",  # Hash table
        r"\.ps1",
        r"\.psm1",
        r"\.psd1",

        # PowerShell specific constructs
        r"param\s*\(",
        r"function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{",
        r"if\s*\([^)]+\)\s*\{",
        r"switch\s*\([^)]+\)\s*\{",

        # Pipeline operators
        r"\s*\|\s*[a-zA-Z-]+",
    ]

    # File extensions to check
    CHECK_EXTENSIONS = {'.py', '.yml', '.yaml', '.md', '.txt', '.json', '.cfg', '.ini', '.toml'}

    # Directories to exclude
    EXCLUDE_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'node_modules', '.venv', 'venv', '.vscode', '.idea'
    }

    def __init__(self):
        self.violations: list[dict[str, Any]] = []
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in self.POWERSHELL_PATTERNS]

    def check_repository(self, max_files: int = 1000) -> list[dict[str, Any]]:
        """Check repository for PowerShell usage with file limit."""
        self.violations = []
        files_checked = 0

        for file_path in PROJECT_ROOT.rglob("*"):
            if files_checked >= max_files:
                print(f"Reached file limit ({max_files}), stopping scan")
                break

            if self._should_check_file(file_path):
                try:
                    self._check_file(file_path)
                    files_checked += 1

                    if files_checked % 100 == 0:
                        print(f"Scanned {files_checked} files...", end='\r')
                except OSError as e:
                    print(f"Could not read {file_path}: {e}", file=sys.stderr)

        print(f"Scanned {files_checked} files total")
        return self.violations

    def _should_check_file(self, file_path: Path) -> bool:
        """Determine if file should be checked for PowerShell usage."""
        # Skip directories
        if not file_path.is_file():
            return False

        # Skip excluded directories
        if any(exclude in str(file_path) for exclude in self.EXCLUDE_DIRS):
            return False

        # Skip binary files
        if file_path.suffix.lower() in ['.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.gif', '.pdf']:
            return False

        # Check specific extensions or common config files
        if file_path.suffix.lower() in self.CHECK_EXTENSIONS:
            return True

        # Check common script/automation files by name
        script_patterns = ['script', 'setup', 'install', 'build', 'deploy', 'run', 'execute']
        filename_lower = file_path.name.lower()
        if any(pattern in filename_lower for pattern in script_patterns):
            return True

        return False

    def _check_file(self, file_path: Path) -> None:
        """Check a single file for PowerShell usage."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for i, pattern in enumerate(self.compiled_patterns):
                matches = pattern.finditer(content)

                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = self._get_line_content(content, line_num)

                    # Skip false positives
                    if self._is_false_positive(match.group(), line_content, file_path):
                        continue

                    violation = {
                        "type": "powershell_usage",
                        "file": str(file_path.relative_to(PROJECT_ROOT)),
                        "line": line_num,
                        "column": match.start() - content.rfind('\n', 0, match.start()),
                        "pattern": self.POWERSHELL_PATTERNS[i],
                        "match": match.group(),
                        "line_content": line_content.strip(),
                        "message": f"PowerShell usage detected: {match.group()}",
                        "severity": "error",
                        "suggestion": self._get_suggestion(match.group(), file_path)
                    }

                    self.violations.append(violation)

        except Exception as e:
            raise

    def _get_line_content(self, content: str, line_num: int) -> str:
        """Extract the content of a specific line."""
        lines = content.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def _is_false_positive(self, match: str, line_content: str, file_path: Path) -> bool:
        """Check if this is a false positive."""
        # Skip comments mentioning PowerShell
        if line_content.strip().startswith('#') and 'powershell' in line_content.lower():
            return True

        # Skip documentation about PowerShell
        if file_path.suffix == '.md' and 'powershell' in line_content.lower():
            return True

        # Skip strings that contain PowerShell but aren't actually PowerShell code
        if line_content.strip().startswith('"') or line_content.strip().startswith("'"):
            return True

        # Skip $ in regular expressions (not PowerShell variables)
        if re.search(r'["\'][^"\']*\$[^"\']*["\']', line_content):
            return True

        # Skip $ in environment variable contexts like ${VAR}
        if '${' in line_content and '}' in line_content:
            return True

        return False

    def _get_suggestion(self, match: str, file_path: Path) -> str:
        """Get suggestion for fixing PowerShell usage."""
        suggestions = {
            "powershell.exe": "Use Python subprocess.run() instead",
            "pwsh.exe": "Use Python subprocess.run() instead",
            "Start-Process": "Use Python subprocess.Popen() instead",
            "Invoke-Expression": "Use Python eval() or exec() instead",
            "Get-Content": "Use Python Path.read_text() or open() instead",
            "Set-Content": "Use Python Path.write_text() or open() instead",
            "Out-File": "Use Python Path.write_text() or print() with file redirection instead",
            "Write-Host": "Use Python print() instead",
            "Write-Error": "Use Python logging.error() or sys.stderr.write() instead",
            "Try-Catch": "Use Python try-except instead",
            "ForEach-Object": "Use Python for loop or list comprehension instead",
            "Where-Object": "Use Python list comprehension or filter() instead",
            "Select-Object": "Use Python list comprehension or map() instead",
        }

        for pattern, suggestion in suggestions.items():
            if pattern.lower() in match.lower():
                return suggestion

        if match.startswith('$'):
            return "Use Python variables without $ prefix"
        elif match.endswith('.ps1'):
            return "Convert PowerShell script to Python"
        elif '|' in match and '-' in match:
            return "Use Python pipes and functions instead of PowerShell pipeline"
        else:
            return "Replace with equivalent Python operation"

    def fix_violations(self) -> bool:
        """Attempt to automatically fix simple PowerShell violations."""
        fixed_count = 0

        for violation in self.violations[:]:  # Copy list to allow modification
            file_path = PROJECT_ROOT / violation["file"]

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                line_idx = violation["line"] - 1

                if 0 <= line_idx < len(lines):
                    line = lines[line_idx]

                    # Simple fixes for common patterns
                    new_line = self._fix_line(line, violation["match"])
                    if new_line != line:
                        lines[line_idx] = new_line
                        file_path.write_text('\n'.join(lines), encoding='utf-8')
                        print(f"Fixed PowerShell usage in {violation['file']}:{violation['line']}")
                        fixed_count += 1
                        self.violations.remove(violation)

            except Exception as e:
                print(f"Failed to fix {violation['file']}: {e}", file=sys.stderr)

        return fixed_count > 0

    def _fix_line(self, line: str, match: str) -> str:
        """Attempt to fix a line with PowerShell usage."""
        # Simple substitutions
        fixes = {
            "Write-Host": "print",
            "Write-Error": "logging.error",
            "Write-Warning": "logging.warning",
        }

        for powershell_cmd, python_cmd in fixes.items():
            if powershell_cmd in line:
                return line.replace(powershell_cmd, python_cmd)

        # Variable substitution (simple cases)
        if re.match(r'\$[a-zA-Z_][a-zA-Z0-9_]*', match):
            return line.replace(match, match[1:])  # Remove $ prefix

        return line

    def print_report(self, verbose: bool = False) -> None:
        """Print PowerShell usage report."""
        if not self.violations:
            print("PowerShell usage ban: No violations found")
            print("Preference enforced: Python subprocess or direct file operations only")
            return

        print(f"PowerShell usage violations found: {len(self.violations)}")
        print()

        # Group violations by file
        by_file: dict[str, list[dict[str, Any]]] = {}
        for v in self.violations:
            file_key = v["file"]
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(v)

        for file_path, file_violations in sorted(by_file.items()):
            print(f"{file_path}")

            for v in sorted(file_violations, key=lambda x: x["line"]):
                print(f"Line {v['line']}: {v['message']}")
                if verbose:
                    print(f"Match: '{v['match']}'")
                    print(f"Context: {v['line_content']}")
                print(f"Suggestion: {v['suggestion']}")
            print()

        print("Python alternatives:")
        print("   • subprocess.run() for shell commands")
        print("   • Path.read_text()/write_text() for file operations")
        print("   • print() for output")
        print("   • logging module for structured logging")
        print("   • Built-in Python functions for data processing")
        print()
        print("Reference: User preference - NEVER use PowerShell")

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about PowerShell usage violations."""
        if not self.violations:
            return {"total": 0}

        by_pattern: dict[str, int] = {}
        by_file: dict[str, int] = {}

        for v in self.violations:
            pattern = v["pattern"]
            file_path = v["file"]

            by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
            by_file[file_path] = by_file.get(file_path, 0) + 1

        return {
            "total": len(self.violations),
            "by_pattern": by_pattern,
            "by_file": by_file,
            "most_common_pattern": max(by_pattern.items(), key=lambda x: x[1]) if by_pattern else None,
            "most_affected_file": max(by_file.items(), key=lambda x: x[1]) if by_file else None
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check for PowerShell usage violations")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix simple violations")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    checker = PowerShellBanChecker()
    violations = checker.check_repository()

    if args.fix:
        print("Attempting to fix PowerShell violations...")
        checker.fix_violations()
        violations = checker.check_repository()  # Re-check

    if args.stats:
        stats = checker.get_statistics()
        print("PowerShell Usage Statistics:")
        print(json.dumps(stats, indent=2))
        print()

    if args.json:
        print(json.dumps({
            "status": "failed" if violations else "passed",
            "violations": violations,
            "statistics": checker.get_statistics()
        }, indent=2))
    else:
        checker.print_report(args.verbose)

    # Fail build if any PowerShell usage found
    if violations:
        print(f"\n❌ POWERSHELL BAN GUARDRAIL: {len(violations)} violations found")
        print("Build FAILED - PowerShell usage violates user preference")
        return 1
    else:
        print("\n✅ POWERSHELL BAN GUARDRAIL: No violations found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
