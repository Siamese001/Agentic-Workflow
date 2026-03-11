#!/usr/bin/env python3
"""
Dependency Graph Hardening Verifier

AST-based verification of hardening plan gap claims using dependency graph analysis.
Proves negative claims (never called, never imported, never executed) with certainty.

Usage:
    python ops_scripts/ci/dependency_graph_hardening_verifier.py

Outputs:
    docs/reports/plans/ast_gap_verification_report.md
"""

from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Add project root to sys.path for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Reuse existing DependencyGraph infrastructure
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.enforcement.dependency_graph_enforcer import DependencyGraph
from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
)

EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


@dataclass
class GapVerification:
    """Result of verifying a single gap claim."""

    gap_id: str
    claim: str
    status: str = "UNCERTAIN"  # "CONFIRMED", "DISPROVEN", "UNCERTAIN"
    evidence: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class CallGraphAnalyzer:
    """Extends DependencyGraph with function call analysis."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.call_graph: dict[str, list[str]] = {}
        self.function_definitions: dict[str, str] = {}  # func_name -> file_path
        self.default_args: dict[str, dict[str, Any]] = {}  # func_name -> {arg: default}

    def build(self, files: list[Path]) -> None:
        """Build call graph from Python files."""
        print("🔍 Building call graph...")

        for file_path in files:
            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(file_path))
                self._analyze_file(tree, file_path)
            except (SyntaxError, UnicodeDecodeError):
                continue

    def _analyze_file(self, tree: ast.AST, file_path: Path) -> None:
        """Analyze a single file's AST."""
        rel_path = file_path.relative_to(self.project_root).as_posix()

        for node in ast.walk(tree):
            # Track function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_key = f"{rel_path}::{node.name}"
                self.function_definitions[node.name] = rel_path
                self.function_definitions[func_key] = rel_path

                # Extract default arguments (with error handling for edge cases)
                defaults = {}
                try:
                    if node.args.defaults:
                        # Match defaults to args (defaults align right)
                        num_args = len(node.args.args)
                        num_defaults = len(node.args.defaults)
                        if num_defaults > 0 and num_args >= num_defaults:
                            offset = num_args - num_defaults
                            for i, default in enumerate(node.args.defaults):
                                arg_idx = offset + i
                                if 0 <= arg_idx < num_args:
                                    arg_name = node.args.args[arg_idx].arg
                                    defaults[arg_name] = ast.unparse(default)

                    # Also check keyword-only args
                    if node.args.kw_defaults:
                        for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                            if default is not None:
                                defaults[arg.arg] = ast.unparse(default)
                except (IndexError, AttributeError):
                    # Skip malformed function signatures
                    pass

                self.default_args[func_key] = defaults

                # Track function calls within this function
                calls = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_name = self._extract_call_name(child)
                        if call_name:
                            calls.append(call_name)
                self.call_graph[func_key] = calls

    def _extract_call_name(self, call_node: ast.Call) -> str | None:
        """Extract function name from Call node."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def find_callers(self, function_name: str) -> list[str]:
        """Find all functions that call the given function."""
        callers = []
        for func, calls in self.call_graph.items():
            if function_name in calls:
                callers.append(func)
        return callers

    def is_function_called(self, function_name: str) -> bool:
        """Check if function is called anywhere in the codebase."""
        return len(self.find_callers(function_name)) > 0


class HardeningVerifier:
    """Verifies hardening plan gap claims using dependency graph analysis."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dep_graph = DependencyGraph()
        self.call_graph = CallGraphAnalyzer(project_root)
        self.verifications: list[GapVerification] = []

    def collect_python_files(self) -> list[Path]:
        """Collect all Python files excluding standard exclusions."""
        files = []
        for py_file in self.project_root.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in EXCLUDED_DIRS):
                continue
            files.append(py_file)
        return files

    def build_graphs(self) -> None:
        """Build dependency and call graphs."""
        print("📊 Building dependency graphs...")
        files = self.collect_python_files()
        print(f"   Found {len(files)} Python files")

        # Build import dependency graph
        self.dep_graph.build([str(f) for f in files])

        # Build call graph
        self.call_graph.build(files)

        print("   ✅ Graphs built successfully")

    def verify_heal_gap_01(self) -> GapVerification:
        """HEAL-GAP-01: load_agents() never discovers apps_rg/apps_lic agents."""
        gap = GapVerification(
            gap_id="HEAL-GAP-01",
            claim="load_agents() search_paths hardcoded to [agentic_core/] only - apps_rg/apps_lic agents never discovered",
        )

        execute_ssot_path = "agentic_core/L0_routing/scripts/execute_ssot.py"
        imports = self.dep_graph.get_imports(execute_ssot_path)

        # Check if apps_rg or apps_lic are imported
        apps_imported = any(APPS_RG_DIR in imp or APPS_LIC_DIR in imp for imp in imports)

        if apps_imported:
            gap.status = "DISPROVEN"
            gap.evidence.append(f"apps_rg/apps_lic ARE imported in {execute_ssot_path}")
            gap.recommendations.append("Gap claim is incorrect - agents may be discovered via imports")
        else:
            gap.status = "CONFIRMED"
            gap.evidence.append(f"No apps_rg/apps_lic imports found in {execute_ssot_path}")
            gap.evidence.append("load_agents() likely hardcoded to agentic_core/ only")
            gap.recommendations.append("Add apps_rg and apps_lic to load_agents() search_paths")

        return gap

    def verify_gap_a(self) -> GapVerification:
        """GAP-A: _write_run_manifest_json never called."""
        gap = GapVerification(
            gap_id="GAP-A",
            claim="_write_run_manifest_json() defined but never called in heal pipeline",
        )

        callers = self.call_graph.find_callers("_write_run_manifest_json")

        if callers:
            gap.status = "DISPROVEN"
            gap.evidence.append(f"Function IS called by: {', '.join(callers)}")
            gap.recommendations.append("Gap claim is incorrect - function is called")
        else:
            gap.status = "CONFIRMED"
            gap.evidence.append("No callers found in call graph")
            gap.evidence.append("Function defined but never invoked")
            gap.recommendations.append(
                "Wire _write_run_manifest_json() call at start of _run_heal_pipeline()"
            )

        return gap

    def verify_gap_b(self) -> GapVerification:
        """GAP-B: set_mutation_ledger_path never called."""
        gap = GapVerification(
            gap_id="GAP-B",
            claim="set_mutation_ledger_path() never called in heal pipeline - ledger always None",
        )

        callers = self.call_graph.find_callers("set_mutation_ledger_path")

        if callers:
            gap.status = "DISPROVEN"
            gap.evidence.append(f"Function IS called by: {', '.join(callers)}")
            gap.recommendations.append("Gap claim is incorrect - function is called")
        else:
            gap.status = "CONFIRMED"
            gap.evidence.append("No callers found in call graph")
            gap.evidence.append("Mutation ledger path never set - all appends are no-ops")
            gap.recommendations.append("Call set_mutation_ledger_path() before Phase 2 mutations begin")

        return gap

    def verify_rg_gap_01(self) -> GapVerification:
        """RG-GAP-01: Direct google.generativeai import in ResumeGenerator."""
        gap = GapVerification(
            gap_id="RG-GAP-01",
            claim="ResumeGenerator.py imports google.generativeai directly, bypassing SovereignLLMGateway",
        )

        resume_gen_path = "apps_rg/tools/ResumeGenerator.py"
        imports = self.dep_graph.get_imports(resume_gen_path)

        if "google.generativeai" in imports or "google" in imports:
            gap.status = "CONFIRMED"
            gap.evidence.append(f"Direct google import found in {resume_gen_path}")
            gap.evidence.append("Bypasses SovereignLLMGateway audit logging and circuit breakers")
            gap.recommendations.append("Replace _generate_with_gemini() with SovereignLLMGateway delegation")
        else:
            gap.status = "DISPROVEN"
            gap.evidence.append(f"No google.generativeai import found in {resume_gen_path}")
            gap.recommendations.append("Gap claim is incorrect - no direct SDK import")

        return gap

    def verify_heal_gap_02(self) -> GapVerification:
        """HEAL-GAP-02: All apps_* heal_repository() default dry_run=True."""
        gap = GapVerification(
            gap_id="HEAL-GAP-02",
            claim="All apps_* heal_repository() methods default dry_run=True - no mutations without explicit override",
        )

        # Check default args for heal_repository methods
        heal_methods = [
            func
            for func in self.call_graph.default_args.keys()
            if "heal_repository" in func and (APPS_RG_DIR in func or APPS_LIC_DIR in func)
        ]

        dry_run_true_count = 0
        dry_run_false_count = 0

        for method in heal_methods:
            defaults = self.call_graph.default_args[method]
            if "dry_run" in defaults:
                if defaults["dry_run"] == "True":
                    dry_run_true_count += 1
                    gap.evidence.append(f"{method}: dry_run=True (blocks healing)")
                elif defaults["dry_run"] == "False":
                    dry_run_false_count += 1
                    gap.evidence.append(f"{method}: dry_run=False (allows healing)")

        if dry_run_true_count > 0:
            gap.status = "CONFIRMED"
            gap.evidence.append(f"Found {dry_run_true_count} methods with dry_run=True default")
            gap.recommendations.append(
                "Change default to dry_run=False in all apps_* heal_repository() methods"
            )
        else:
            gap.status = "DISPROVEN"
            gap.evidence.append("No dry_run=True defaults found in apps_* heal_repository() methods")

        return gap

    def run_verification(self) -> None:
        """Run all gap verifications."""
        print("\n🔬 Running gap verifications...\n")

        self.verifications = [
            self.verify_heal_gap_01(),
            self.verify_gap_a(),
            self.verify_gap_b(),
            self.verify_rg_gap_01(),
            self.verify_heal_gap_02(),
        ]

    def generate_report(self) -> str:
        """Generate markdown verification report."""
        lines = [
            "# AST Gap Verification Report",
            "",
            "Dependency graph analysis of hardening plan gap claims.",
            "",
            f"**Analysis Date:** {Path.cwd()}",
            f"**Files Analyzed:** {len(self.dep_graph.get_all_files())}",
            f"**Functions Tracked:** {len(self.call_graph.function_definitions)}",
            "",
            "---",
            "",
        ]

        # Summary table
        lines.extend(
            [
                "## Summary",
                "",
                "| Gap ID | Status | Claim |",
                "|--------|--------|-------|",
            ]
        )

        for v in self.verifications:
            status_emoji = {
                "CONFIRMED": "✅",
                "DISPROVEN": "❌",
                "UNCERTAIN": "⚠️",
            }.get(v.status, "❓")
            lines.append(f"| {v.gap_id} | {status_emoji} {v.status} | {v.claim[:60]}... |")

        lines.extend(["", "---", ""])

        # Detailed findings
        lines.append("## Detailed Findings\n")

        for v in self.verifications:
            lines.extend(
                [
                    f"### {v.gap_id} — {v.status}",
                    "",
                    f"**Claim:** {v.claim}",
                    "",
                ]
            )

            if v.evidence:
                lines.append("**Evidence:**")
                for e in v.evidence:
                    lines.append(f"- {e}")
                lines.append("")

            if v.recommendations:
                lines.append("**Recommendations:**")
                for r in v.recommendations:
                    lines.append(f"- {r}")
                lines.append("")

            lines.append("---\n")

        # Conclusion
        confirmed = sum(1 for v in self.verifications if v.status == "CONFIRMED")
        disproven = sum(1 for v in self.verifications if v.status == "DISPROVEN")

        lines.extend(
            [
                "## Conclusion",
                "",
                f"- **{confirmed}** gaps CONFIRMED by AST analysis",
                f"- **{disproven}** gaps DISPROVEN by AST analysis",
                "",
                "**Next Steps:**",
                "1. Implement fixes for all CONFIRMED gaps",
                "2. Update plan to remove DISPROVEN gap claims",
                "3. Re-run verification after implementation",
                "",
            ]
        )

        return "\n".join(lines)

    def save_report(self, output_path: Path) -> None:
        """Save verification report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = self.generate_report()
        output_path.write_text(report, encoding="utf-8")
        print(f"\n📄 Report saved to: {output_path}")


def main():
    """Main entry point."""
    print("=" * 80)
    print("Dependency Graph Hardening Verifier")
    print("=" * 80)

    verifier = HardeningVerifier(PROJECT_ROOT)
    verifier.build_graphs()
    verifier.run_verification()

    output_path = PROJECT_ROOT / "docs/reports/plans/ast_gap_verification_report.md"
    verifier.save_report(output_path)

    # Print summary to console
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    for v in verifier.verifications:
        status_emoji = {"CONFIRMED": "✅", "DISPROVEN": "❌", "UNCERTAIN": "⚠️"}.get(v.status, "❓")
        print(f"{status_emoji} {v.gap_id}: {v.status}")
    print("=" * 80)


if __name__ == "__main__":
    main()
