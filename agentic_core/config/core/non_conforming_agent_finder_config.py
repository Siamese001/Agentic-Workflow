"""
[DEPRECATED] ULTRA-SOVEREIGN NON-CONFORMING AGENT AUDITOR

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script performs its own AST scan which may conflict with the SSOT.

Finds all Python classes in agentic_core that:
 • Do NOT end with "Agent" in PascalCase
 • BUT exhibit agent-like behavior (have canonical methods)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

import warnings

warnings.warn(
    "find_non_conforming_agents.py is DEPRECATED. Use full_agent_discovery.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
import ast
from pathlib import Path

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        ARCHIVES_DIR,
    )
except ImportError:
    AGENTIC_CORE_DIR = "agentic_core"
    ARCHIVES_DIR = ".sovereign_healing_backup"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

EXCLUDED_DIRS = {"__pycache__", ".git", ARCHIVES_DIR, "data", ".sovereign_healing_backup"}

# Canonical agent methods — presence strongly indicates "agent" role
AGENT_LIKE_METHODS = {
    "heal_violation",
    "execute",
    "run",
    "validate",
    "monitor",
    "detect",
    "enforce",
    "prune",
    "check",
    "analyze",
    "scan",
}


class NonConformingAgentFinder(ast.NodeVisitor):
    def __init__(self, file_path: Path, source_lines: list[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.suspect_classes: list[dict] = []
        self.excluded_classes: list[dict] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        class_name = node.name

        # Skip if already canon-compliant
        if class_name.endswith("Agent") and class_name[0].isupper():
            self.generic_visit(node)
            return

        # Check for NOT_AN_AGENT exclusion comment on preceding lines (up to 3 lines back for decorators)
        line_idx = node.lineno - 1  # 0-indexed
        for offset in range(1, 4):  # Check up to 3 lines before class definition
            check_idx = line_idx - offset
            if check_idx >= 0:
                prev_line = self.source_lines[check_idx].strip()
                if "NOT_AN_AGENT" in prev_line:
                    self.excluded_classes.append(
                        {
                            "name": class_name,
                            "line": node.lineno,
                            "reason": prev_line,
                        },
                    )
                    self.generic_visit(node)
                    return

        # Scan methods
        suspicious_methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name in AGENT_LIKE_METHODS:
                    suspicious_methods.append(item.name)

        if suspicious_methods:
            self.suspect_classes.append(
                {
                    "name": class_name,
                    "line": node.lineno,
                    "methods": suspicious_methods,
                },
            )

        self.generic_visit(node)


def main():
    print("=" * 80)
    print("ULTRA NON-CONFORMING AGENT AUDIT")
    print("=" * 80)

    suspects = []

    # Phase 6.9: Use ssot_discovery instead of rglob

    py_files = list(get_python_files(AGENTIC_CORE))
    for py_file in py_files:
        if any(ex in str(py_file) for ex in EXCLUDED_DIRS):
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        # guardian: allow-silent-swallow
        except Exception:
            continue  # Skip unparseable files

        source_lines = source.splitlines()
        finder = NonConformingAgentFinder(py_file, source_lines)
        finder.visit(tree)

        for suspect in finder.suspect_classes:
            suspects.append(
                {
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "line": suspect["line"],
                    "class_name": suspect["name"],
                    "suspicious_methods": ", ".join(suspect["methods"]),
                },
            )

    # Output table
    # Count excluded classes
    sum(len(f.get("excluded", [])) for f in [{"excluded": []}])  # placeholder

    if suspects:
        print(f"\nFound {len(suspects)} non-conforming agent-like classes (excluding NOT_AN_AGENT marked):\n")
        print(f"{'File':<60} {'Line':<6} {'Class Name':<30} {'Suspicious Methods'}")
        print("-" * 140)
        for s in suspects:
            print(f"{s['file']:<60} {s['line']:<6} {s['class_name']:<30} {s['suspicious_methods']}")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("For each suspect:")
        print(" • Rename class to PascalCase + 'Agent' suffix (e.g., NamingValidator → NamingValidatorAgent)")
        print(" • Rename file to match: NamingValidator.py → NamingValidatorAgent.py")
        print(" • Use IDE refactor (safe rename) to update all imports and references")
        print(" • After rename: class will be auto-discovered by ComplianceOrchestratorAgent")
        print(" • If intentionally not an agent → add comment: # NOT_AN_AGENT — exclude from future audits")
    else:
        print("\n[OK] No non-conforming agent-like classes found — naming canon perfectly enforced.")

    print("\n" + "=" * 80)
    print("NON-CONFORMING AGENT-LIKE CLASSES IDENTIFIED — CANON NAMING ENFORCEMENT READY")
    print("=" * 80)


if __name__ == "__main__":
    main()
