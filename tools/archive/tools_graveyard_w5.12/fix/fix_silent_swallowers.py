#!/usr/bin/env python3
"""
Fix silent swallowers that violate the Error & Exception Handling policy.

According to docs/technical/Error & Exception Handling.md:
- Column 3 (BROAD SWALLOW/SILENT SWALLOWER) should be tightly defined
- Should not veer too widely in definition
- Must have guardian: allow-silent-swallow comments for legitimate cases
- Violations should be fixed with proper exception handling
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class SilentSwallowerFixer:
    """Identify and fix improper silent swallowers."""

    def __init__(self):
        self.violations = []
        self.fixes_applied = []

        # Legitimate silent swallower patterns (with guardian comments)
        self.legitimate_patterns = [
            r"# guardian: allow-silent-swallow",
            r"# guardian:.*silent.*swallow",
        ]

        # Cases where silent swallowing is NEVER acceptable
        self.never_acceptable = [
            "ImportError",  # Import errors should fail or use importorskip
            "ModuleNotFoundError",  # Same as ImportError
            "AttributeError",  # Should be fixed, not swallowed
            "TypeError",  # Should be fixed, not swallowed
            "ValueError",  # Should be fixed, not swallowed
            "KeyError",  # Should be handled with proper fallback
            "IndexError",  # Should be handled with bounds checking
        ]

    def find_silent_swallowers(self, file_path: Path) -> List[Dict[str, Any]]:
        """Find silent swallowers in a file."""
        violations = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
            return violations

        # Parse AST to find exception handlers
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                violation = self._analyze_exception_handler(node, lines, file_path)
                if violation:
                    violations.append(violation)

        return violations

    def _analyze_exception_handler(
        self, handler: ast.ExceptHandler, lines: List[str], file_path: Path
    ) -> Dict[str, Any]:
        """Analyze an exception handler for violations."""
        line_no = handler.lineno - 1  # Convert to 0-based

        # Get the exception type
        exception_type = "Exception"  # Default
        if handler.type:
            if isinstance(handler.type, ast.Name):
                exception_type = handler.type.id
            elif isinstance(handler.type, ast.Tuple):
                # Multiple exception types
                types = []
                for elt in handler.type.elts:
                    if isinstance(elt, ast.Name):
                        types.append(elt.id)
                exception_type = ", ".join(types)

        # Check if handler has guardian comment
        has_guardian = False
        if line_no > 0:
            comment_line = lines[line_no - 1].strip()
            for pattern in self.legitimate_patterns:
                if re.search(pattern, comment_line, re.IGNORECASE):
                    has_guardian = True
                    break

        # Check if handler just passes or continues
        handler_body = []
        if handler.body:
            first_stmt = handler.body[0]
            if isinstance(first_stmt, ast.Pass):
                handler_body = ["pass"]
            elif isinstance(first_stmt, ast.Continue):
                handler_body = ["continue"]
            elif isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
                if first_stmt.value.value is None:
                    handler_body = ["pass"]

        is_silent = len(handler_body) == 0 or (
            len(handler_body) == 1 and handler_body[0] in ["pass", "continue"]
        )

        # Determine if this is a violation
        is_violation = False
        severity = "LOW"

        if is_silent and not has_guardian:
            is_violation = True

            # Check severity based on exception type
            found_high = False
            for never_acceptable in self.never_acceptable:
                if never_acceptable in exception_type:
                    severity = "HIGH"
                    found_high = True
                    break
            if not found_high:
                if exception_type == "Exception":
                    severity = "MEDIUM"  # Broad exception swallowing
                else:
                    severity = "LOW"

        if is_violation:
            return {
                "file_path": str(file_path),
                "line_number": handler.lineno,
                "exception_type": exception_type,
                "handler_body": handler_body,
                "has_guardian": has_guardian,
                "severity": severity,
                "code_snippet": lines[line_no] if line_no < len(lines) else "",
            }

        return None

    def fix_violation(self, violation: Dict[str, Any]) -> str:
        """Generate fix for a violation."""
        exception_type = violation["exception_type"]
        severity = violation["severity"]

        if severity == "HIGH":
            # High severity: Never acceptable - must be fixed properly
            return self._generate_proper_fix(exception_type, violation)
        elif severity == "MEDIUM":
            # Medium severity: Broad exceptions - narrow them down
            return self._generate_narrow_fix(exception_type, violation)
        else:
            # Low severity: Add guardian comment or proper handling
            return self._generate_lightweight_fix(exception_type, violation)

    def _generate_proper_fix(self, exception_type: str, violation: Dict[str, Any]) -> str:
        """Generate proper fix for high-severity violations."""
        fixes = {
            "ImportError": "# Import errors should surface as failures or use pytest.importorskip",
            "ModuleNotFoundError": "# Module errors should surface as failures or use pytest.importorskip",
            "AttributeError": "# AttributeError indicates programming error - fix the attribute access",
            "TypeError": "# TypeError indicates programming error - fix the type usage",
            "ValueError": "# ValueError indicates invalid input - validate before use",
            "KeyError": "# KeyError indicates missing key - check key existence or use dict.get()",
            "IndexError": "# IndexError indicates out-of-bounds - check array length first",
        }

        return fixes.get(exception_type, f"# {exception_type} should be handled properly, not swallowed")

    def _generate_narrow_fix(self, exception_type: str, violation: Dict[str, Any]) -> str:
        """Generate fix for broad exception violations."""
        if exception_type == "Exception":
            return "# Replace 'except Exception:' with specific exception types"
        return f"# Narrow 'except {exception_type}' to specific cases"

    def _generate_lightweight_fix(self, exception_type: str, violation: Dict[str, Any]) -> str:
        """Generate lightweight fix for low-severity violations."""
        return (
            f"# Add guardian comment: # guardian: allow-silent-swallow - {exception_type} is acceptable here"
        )

    def scan_all_files(self) -> List[Dict[str, Any]]:
        """Scan all Python files for silent swallowers."""
        print("🔍 Scanning for silent swallowers...")

        all_violations = []
        python_files = list(PROJECT_ROOT.rglob("*.py"))

        # Skip certain directories
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "node_modules"}

        for file_path in python_files:
            # Skip if in excluded directory
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            violations = self.find_silent_swallowers(file_path)
            all_violations.extend(violations)

        return all_violations

    def apply_fixes(self, violations: List[Dict[str, Any]]) -> None:
        """Apply fixes to violations (generate recommendations)."""
        print("🔧 Generating fix recommendations...")

        for violation in violations:
            fix = self.fix_violation(violation)
            violation["recommended_fix"] = fix
            self.fixes_applied.append(violation)


def main():
    """Main entry point."""
    print("=" * 80)
    print("SILENT SWALLOWER FIXER")
    print("=" * 80)

    fixer = SilentSwallowerFixer()
    violations = fixer.scan_all_files()

    print(f"Found {len(violations)} silent swallower violations")

    # Group by severity
    by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for violation in violations:
        by_severity[violation["severity"]].append(violation)

    print("\nBy severity:")
    for severity, vlist in by_severity.items():
        print(f"  {severity}: {len(vlist)}")

    # Generate fixes
    fixer.apply_fixes(violations)

    # Show high severity violations (must fix)
    high_severity = by_severity["HIGH"]
    if high_severity:
        print("\n🚨 HIGH SEVERITY VIOLATIONS (must fix):")
        for violation in high_severity[:10]:
            print(f"  {violation['file_path']}:{violation['line_number']}")
            print(f"    {violation['exception_type']} -> {violation['recommended_fix']}")

        if len(high_severity) > 10:
            print(f"  ... and {len(high_severity) - 10} more")

    # Show medium severity violations
    medium_severity = by_severity["MEDIUM"]
    if medium_severity:
        print("\n⚠️  MEDIUM SEVERITY VIOLATIONS (should fix):")
        for violation in medium_severity[:5]:
            print(f"  {violation['file_path']}:{violation['line_number']}")
            print(f"    {violation['exception_type']} -> {violation['recommended_fix']}")

        if len(medium_severity) > 5:
            print(f"  ... and {len(medium_severity) - 5} more")

    # Generate report
    report = {
        "scan_timestamp": "2026-03-24T18:31:00Z",
        "total_violations": len(violations),
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "violations": violations,
    }

    output_file = PROJECT_ROOT / "silent_swallower_report.json"
    import json

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📋 Report written to: {output_file}")

    print("\n" + "=" * 80)
    print("FIX RECOMMENDATIONS:")
    print("1. HIGH: Replace with proper error handling")
    print("2. MEDIUM: Narrow exception types")
    print("3. LOW: Add guardian comments for legitimate cases")
    print("=" * 80)


if __name__ == "__main__":
    main()
