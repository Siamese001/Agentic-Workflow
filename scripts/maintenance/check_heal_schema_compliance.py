#!/usr/bin/env python3
"""
Static Analysis: Canonical Schema Compliance Checker for @standard_heal Methods

This script scans all Python files for methods decorated with @standard_heal
and validates that their return statements use canonical keys.

CANONICAL KEYS (from decorators.py):
    - violations_found (NOT: total_violations, count, violations, issues)
    - violations_fixed (NOT: fixed_count, fixed, healed, repaired)
    - errors
    - skipped
    - status (optional - auto-computed by decorator)

USAGE:
    python scripts/maintenance/check_heal_schema_compliance.py

    # As pre-commit hook:
    python scripts/maintenance/check_heal_schema_compliance.py --strict

EXIT CODES:
    0 - All compliant
    1 - Non-canonical keys found (warnings only in non-strict mode)
    2 - Non-canonical keys found (strict mode - blocks commit)
"""

import ast
import sys
from pathlib import Path

# Canonical keys that @standard_heal recognizes directly
CANONICAL_KEYS = {
    'violations_found',
    'violations_fixed',
    'errors',
    'skipped',
    'status',
    'error_message',
}

# Non-canonical keys that should be replaced
NON_CANONICAL_MAPPINGS = {
    # violations_found alternatives
    'total_violations': 'violations_found',
    'violations': 'violations_found',
    'count': 'violations_found',
    'issues': 'violations_found',
    'problems': 'violations_found',
    'findings': 'violations_found',

    # violations_fixed alternatives
    'fixed_count': 'violations_fixed',
    'fixed': 'violations_fixed',
    'healed': 'violations_fixed',
    'repaired': 'violations_fixed',
    'resolved': 'violations_fixed',
    'renamed': 'violations_fixed',
    'moved': 'violations_fixed',
    'deleted': 'violations_fixed',
    'created': 'violations_fixed',

    # errors alternatives
    'error_count': 'errors',
    'failures': 'errors',

    # skipped alternatives
    'skip_count': 'skipped',
    'ignored': 'skipped',
}


class HealSchemaVisitor(ast.NodeVisitor):
    """AST visitor to find @standard_heal decorated methods and check return keys."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: list[dict] = []
        self.in_standard_heal_method = False
        self.current_method_name = ""
        self.current_method_lineno = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Check if decorated with @standard_heal
        for decorator in node.decorator_list:
            decorator_name = ""
            if isinstance(decorator, ast.Name):
                decorator_name = decorator.id
            elif isinstance(decorator, ast.Attribute):
                decorator_name = decorator.attr

            if decorator_name == 'standard_heal':
                self.in_standard_heal_method = True
                self.current_method_name = node.name
                self.current_method_lineno = node.lineno
                break

        # Visit children
        self.generic_visit(node)

        # Reset state
        self.in_standard_heal_method = False
        self.current_method_name = ""

    def visit_Return(self, node: ast.Return):
        if not self.in_standard_heal_method:
            return

        if node.value is None:
            return

        # Check if returning a dict literal
        if isinstance(node.value, ast.Dict):
            self._check_dict_keys(node.value, node.lineno)

    def _check_dict_keys(self, dict_node: ast.Dict, lineno: int):
        """Check dict keys for non-canonical names."""
        for key in dict_node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                key_name = key.value

                if key_name in NON_CANONICAL_MAPPINGS:
                    canonical = NON_CANONICAL_MAPPINGS[key_name]
                    self.violations.append({
                        'file': self.filepath,
                        'line': lineno,
                        'method': self.current_method_name,
                        'key': key_name,
                        'canonical': canonical,
                        'message': f"Use '{canonical}' instead of '{key_name}'"
                    })


def check_file(filepath: Path) -> list[dict]:
    """Check a single file for schema compliance."""
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)

        visitor = HealSchemaVisitor(str(filepath))
        visitor.visit(tree)

        return visitor.violations
    except SyntaxError:
        return []  # Skip files with syntax errors
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return []


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check @standard_heal schema compliance')
    parser.add_argument('--strict', action='store_true', help='Exit with error code on violations')
    parser.add_argument('--path', default='agentic_core', help='Path to scan (default: agentic_core)')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent / args.path
    if not root.exists():
        print(f"Error: Path not found: {root}", file=sys.stderr)
        sys.exit(1)

    all_violations = []
    files_checked = 0

    for py_file in root.rglob('*.py'):
        # Skip __pycache__ and other ignored dirs
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue

        violations = check_file(py_file)
        all_violations.extend(violations)
        files_checked += 1

    print(f"\n{'='*60}")
    print("@standard_heal Schema Compliance Check")
    print(f"{'='*60}")
    print(f"Files scanned: {files_checked}")
    print(f"Violations found: {len(all_violations)}")

    if all_violations:
        print(f"\n{'='*60}")
        print("NON-CANONICAL KEYS DETECTED:")
        print(f"{'='*60}")

        for v in all_violations:
            rel_path = Path(v['file']).relative_to(root.parent) if root.parent in Path(v['file']).parents else v['file']
            print(f"\n  {rel_path}:{v['line']}")
            print(f"    Method: {v['method']}()")
            print(f"    Issue: '{v['key']}' → should be '{v['canonical']}'")

        print(f"\n{'='*60}")
        print("RECOMMENDED FIX:")
        print("  Replace non-canonical keys with canonical equivalents.")
        print("  See: agentic_core/L5_safety/validators/decorators.py")
        print(f"{'='*60}\n")

        if args.strict:
            print("❌ STRICT MODE: Blocking due to schema violations")
            sys.exit(2)
        else:
            print("⚠️  Warnings only (use --strict to block)")
            sys.exit(1)
    else:
        print("\n✅ All @standard_heal methods use canonical keys!")
        sys.exit(0)


if __name__ == '__main__':
    main()
