#!/usr/bin/env python3
"""
ADG-Driven Intelligent Anti-Pattern Burndown

Uses AST dependency graph to understand code structure and relationships,
then applies surgical fixes based on graph topology.

Strategy:
1. Load ADG to understand import relationships
2. Identify which files import from path_constants
3. Find files that could import but don't
4. Use AST parsing (not regex) to make precise edits
5. Follow dependency order to avoid breaking imports
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "adg_intelligent_burndown")
_emit_applies_guardrail("p0", "adg_intelligent_burndown", "p0_governance")
_emit_reads_policy_state("p0", "adg_intelligent_burndown", "policy_binding")
_emit_snapshots_state("p0", "adg_intelligent_burndown", "state_snapshot")
emit_replay_key("p0", "adg_intelligent_burndown")
emit_determinism_digest("p0", "adg_intelligent_burndown")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


class IntelligentThresholdFixer:
    """AST-based threshold fixer using ADG dependency information."""

    def __init__(self, adg_path: Path, baseline_path: Path):
        self.project_root = get_validated_project_root()
        self.adg_path = adg_path
        self.baseline_path = baseline_path

        # Load ADG
        print("[INFO] Loading ADG dependency graph...")
        with open(adg_path, encoding='utf-8') as f:
            self.adg = json.load(f)

        # Build import graph
        self.import_graph = self._build_import_graph()

        # Load violations
        self.violations = self._load_violations()

        print(f"[INFO] Loaded {len(self.adg.get('nodes', []))} nodes from ADG")
        print(f"[INFO] Found {len(self.violations)} files with violations")

    def _build_import_graph(self) -> dict[str, set[str]]:
        """Build import relationships from ADG edges."""
        graph = defaultdict(set)

        for edge in self.adg.get('edges', []):
            source = edge.get('f', '')
            target_sym = edge.get('sym', '')

            if not source or not target_sym:
                continue

            # Extract module from symbol
            if '.' in target_sym:
                parts = target_sym.split('.')
                # Reconstruct module path
                target_module = '/'.join(parts[:-1]) + '.py'
                graph[source].add(target_module)

        return graph

    def _load_violations(self) -> dict[str, list[int]]:
        """Load violations from baseline, grouped by file."""
        violations = defaultdict(list)

        with open(self.baseline_path, encoding='utf-8') as f:
            for line in f:
                if 'threshold=0.95' not in line:
                    continue

                parts = line.split(':')
                if len(parts) < 2:
                    continue

                file_path = parts[0]
                try:
                    line_num = int(parts[1])
                    violations[file_path].append(line_num)
                except (ValueError, IndexError):
                    continue

        return violations

    def analyze_file_dependencies(self, file_path: str) -> dict[str, Any]:
        """Analyze a file's dependencies using ADG."""
        imports_path_constants = False
        imports_threshold = False

        # Check if file imports from path_constants
        if file_path in self.import_graph:
            for imported in self.import_graph[file_path]:
                if 'path_constants' in imported:
                    imports_path_constants = True
                    # Would need to check AST to see if THRESHOLD specifically imported
                    break

        return {
            'file': file_path,
            'imports_path_constants': imports_path_constants,
            'imports_threshold': imports_threshold,
            'violation_lines': self.violations.get(file_path, []),
        }

    def fix_file_ast(self, file_path: Path) -> dict[str, Any]:
        """Fix a file using AST parsing and manipulation."""
        try:
            source = file_path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=str(file_path))

            # Analyze what needs fixing
            needs_import = False
            modifications = []

            # Walk AST to find threshold=0.95 patterns
            for node in ast.walk(tree):
                # Look for keyword arguments with threshold=0.95
                if isinstance(node, ast.keyword):
                    if node.arg == 'threshold':
                        if isinstance(node.value, ast.Constant):
                            if node.value.value == 0.95:
                                needs_import = True
                                modifications.append({
                                    'type': 'keyword_arg',
                                    'line': node.lineno,
                                    'arg': node.arg,
                                })

            # Check if already imports THRESHOLD
            has_threshold_import = False
            import_node = None

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'path_constants' in node.module:
                        for alias in node.names:
                            if alias.name == 'THRESHOLD':
                                has_threshold_import = True
                                break
                        if not has_threshold_import:
                            # Found path_constants import but no THRESHOLD
                            import_node = node

            return {
                'status': 'analyzed',
                'needs_import': needs_import and not has_threshold_import,
                'has_threshold_import': has_threshold_import,
                'modifications': modifications,
                'import_node': import_node,
            }

        except SyntaxError as e:
            return {
                'status': 'error',
                'error': f'SyntaxError: {e}',
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
            }

    def generate_report(self) -> None:
        """Generate analysis report of violations."""
        print("\n" + "="*80)
        print("ADG-DRIVEN ANTI-PATTERN ANALYSIS")
        print("="*80)

        # Analyze top violators
        sorted_files = sorted(
            self.violations.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:20]

        print("\nTop 20 files by violation count:")
        for file_path, lines in sorted_files:
            analysis = self.analyze_file_dependencies(file_path)
            status = "✓ imports path_constants" if analysis['imports_path_constants'] else "✗ no import"
            print(f"  {len(lines):3d} violations - {file_path} ({status})")

        # Categorize files
        has_import = []
        needs_import = []

        for file_path in self.violations.keys():
            analysis = self.analyze_file_dependencies(file_path)
            if analysis['imports_path_constants']:
                has_import.append(file_path)
            else:
                needs_import.append(file_path)

        print("\n[SUMMARY]")
        print(f"  Files already importing from path_constants: {len(has_import)}")
        print(f"  Files needing new import: {len(needs_import)}")
        print(f"  Total files with violations: {len(self.violations)}")

        # Show dependency clusters
        print("\n[DEPENDENCY CLUSTERS]")
        layer_counts = defaultdict(int)
        for file_path in self.violations.keys():
            if '/' in file_path:
                layer = file_path.split('/')[0]
                layer_counts[layer] += 1

        for layer, count in sorted(layer_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {layer}: {count} files")


def main():
    """Main execution."""
    project_root = get_validated_project_root()

    adg_path = project_root / "artifacts" / "adg" / "adg_file_graph_03122026.json"
    baseline_path = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    if not adg_path.exists():
        print(f"[ERROR] ADG file not found: {adg_path}")
        return 1

    if not baseline_path.exists():
        print(f"[ERROR] Baseline file not found: {baseline_path}")
        return 1

    fixer = IntelligentThresholdFixer(adg_path, baseline_path)
    fixer.generate_report()

    return 0


if __name__ == '__main__':
    sys.exit(main())
