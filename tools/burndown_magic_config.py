#!/usr/bin/env python3
"""
ADG-Guided Magic Configuration Burndown

Uses AST dependency graph to systematically eliminate magic configuration
anti-patterns by replacing hardcoded values with SSOT imports.

Strategy:
1. Identify all files with threshold=0.95 violations
2. Check if they already import from path_constants
3. Replace hardcoded values with THRESHOLD constant
4. Add import if missing
5. Verify no new violations introduced
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


class MagicConfigReplacer(ast.NodeTransformer):
    """AST transformer to replace magic config values with SSOT constants."""

    def __init__(self):
        self.replacements = []
        self.needs_import = False

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Replace threshold=0.95 assignments with THRESHOLD constant."""
        if isinstance(node.value, ast.Constant):
            if node.value.value == 0.95:
                # Check if this is a threshold-related variable
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if 'threshold' in var_name:
                            # Replace with Name node referencing THRESHOLD
                            node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                            self.needs_import = True
                            self.replacements.append((node.lineno, var_name))
        return self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> Any:
        """Replace threshold=0.95 in function calls."""
        if node.arg and 'threshold' in node.arg.lower():
            if isinstance(node.value, ast.Constant) and node.value.value == 0.95:
                node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                self.needs_import = True
                self.replacements.append((node.lineno, node.arg))
        return self.generic_visit(node)


def analyze_file(file_path: Path) -> dict:
    """Analyze a file for magic config violations."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))

        # Check if already imports THRESHOLD
        has_threshold_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'path_constants' in node.module:
                    if any(alias.name == 'THRESHOLD' for alias in node.names):
                        has_threshold_import = True
                        break

        # Count threshold=0.95 occurrences
        threshold_count = source.count('threshold=0.95') + source.count('THRESHOLD = 0.95')

        return {
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'has_import': has_threshold_import,
            'violations': threshold_count,
            'can_fix': threshold_count > 0,
        }
    except Exception as e:
        return {
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
            'can_fix': False,
        }


def main():
    """Main burndown execution."""
    project_root = get_validated_project_root()

    # Load landmine baseline
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    if not baseline_file.exists():
        print("[ERROR] Landmine baseline not found")
        return 1

    # Parse baseline for threshold=0.95 violations
    violations = []
    with open(baseline_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    # Deduplicate files
    unique_files = sorted(set(violations))
    print(f"[INFO] Found {len(unique_files)} files with threshold=0.95 violations")

    # Analyze each file
    fixable_files = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        analysis = analyze_file(file_path)
        if analysis.get('can_fix'):
            fixable_files.append(analysis)

    print(f"[INFO] {len(fixable_files)} files can be automatically fixed")

    # Group by whether they already have the import
    has_import = [f for f in fixable_files if f['has_import']]
    needs_import = [f for f in fixable_files if not f['has_import']]

    print(f"\n[ANALYSIS]")
    print(f"  Already imports THRESHOLD: {len(has_import)} files")
    print(f"  Needs import added: {len(needs_import)} files")

    # Show top 10 files by violation count
    print(f"\n[TOP VIOLATORS]")
    sorted_files = sorted(fixable_files, key=lambda x: x['violations'], reverse=True)[:10]
    for f in sorted_files:
        status = "✓ has import" if f['has_import'] else "✗ needs import"
        print(f"  {f['violations']:3d} violations - {f['file']} ({status})")

    return 0


if __name__ == '__main__':
    sys.exit(main())
