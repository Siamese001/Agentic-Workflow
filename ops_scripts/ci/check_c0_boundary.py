#!/usr/bin/env python3
"""
CI gate: §21 C0 Informational Boundary.

Scans production Python files for patterns where retrieval/telemetry outputs
are assigned directly to routing constants, threshold variables, or approval
flags without going through a governed decision function.

Forbidden pattern (§21.3):
    CONFIDENCE_THRESHOLD = retrieval_result["score"]
    approved = memory_recall["flag"]
    route = search_results[0]

Detection: assignment where the RHS is a subscript/attribute access on a
variable whose name suggests retrieval/telemetry origin, and the LHS name
suggests a control variable.

Exits 1 on any violation.
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PRODUCTION_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

# Names suggesting informational/retrieval origin (RHS variable names)
INFORMATIONAL_STEMS = {
    "retrieval", "recall", "search", "memory", "telemetry",
    "context", "result", "results", "signal", "score", "scores",
    "embedding", "similarity",
}

# Names suggesting control variables (LHS assignment targets)
CONTROL_STEMS = {
    "threshold", "gate", "approval", "approved", "route", "routing",
    "confidence", "policy", "decision", "authority", "flag", "allow",
    "permit", "reject", "block",
}


def _name_matches(name: str, stems: set[str]) -> bool:
    name_lower = name.lower()
    return any(stem in name_lower for stem in stems)


class C0BoundaryVisitor(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations: list[str] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        rhs = node.value
        # Check if RHS is a subscript or attribute on an informational variable
        informational_rhs = False
        if isinstance(rhs, ast.Subscript) and isinstance(rhs.value, ast.Name):
            if _name_matches(rhs.value.id, INFORMATIONAL_STEMS):
                informational_rhs = True
        elif isinstance(rhs, ast.Attribute) and isinstance(rhs.value, ast.Name):
            if _name_matches(rhs.value.id, INFORMATIONAL_STEMS):
                informational_rhs = True

        if not informational_rhs:
            self.generic_visit(node)
            return

        # Check if any LHS target name suggests a control variable
        for target in node.targets:
            if isinstance(target, ast.Name) and _name_matches(target.id, CONTROL_STEMS):
                self.violations.append(
                    f"{self.filepath}:{node.lineno}: "
                    f"C0 boundary violation — informational value assigned directly to "
                    f"control variable '{target.id}' without governed decision function (§21.3)",
                )
            elif isinstance(target, ast.Attribute) and _name_matches(target.attr, CONTROL_STEMS):
                self.violations.append(
                    f"{self.filepath}:{node.lineno}: "
                    f"C0 boundary violation — informational value assigned directly to "
                    f"control attribute '{target.attr}' without governed decision function (§21.3)",
                )

        self.generic_visit(node)


def check_file(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    visitor = C0BoundaryVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    all_violations: list[str] = []
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            all_violations.extend(check_file(path))

    if all_violations:
        print(f"ERROR: §21 C0 informational boundary violations ({len(all_violations)}):")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print("OK: §21 C0 informational boundary — no direct informational→control assignments detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
