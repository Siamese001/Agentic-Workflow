#!/usr/bin/env python3
"""Gate Q2 — cyclomatic complexity ratchet (plan W3.6).

AST-counts decision points per function (if / for / while / except /
and / or / ternary / comprehension-if) and flags functions whose
McCabe-style cyclomatic complexity exceeds ``CEILING``.

Tier: R (ratchet). Lock current over-ceiling count; new offenders
regress the build.

Rationale: Thoughtworks architecture fitness functions and CodeScene
research both converge on ~10-15 as the inflection point where
defect density and cognitive load climb sharply. We use 15 as the
ceiling — strict enough to surface real complexity pits, loose
enough to avoid flagging well-structured dispatchers.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import ast
import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

_REPO_ROOT = REPO_ROOT

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PREFIXES = (
    "tests/",
    "tools/archive/",
    "archives/",
)
CEILING = 15


class _ComplexityVisitor(ast.NodeVisitor):
    """Accumulate McCabe complexity for the enclosing function."""

    def __init__(self) -> None:
        self.score = 1  # every function starts at 1 for the entry edge

    def _bump(self, node: ast.AST) -> None:
        self.score += 1
        self.generic_visit(node)

    # Control flow
    visit_If = _bump
    visit_For = _bump
    visit_AsyncFor = _bump
    visit_While = _bump
    visit_Try = _bump
    visit_With = _bump
    visit_AsyncWith = _bump
    visit_Assert = _bump

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.score += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each ``and``/``or`` operator introduces one additional branch
        # beyond the first operand.
        if isinstance(node.op, (ast.And, ast.Or)):
            self.score += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.score += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        # Each ``if`` clause inside a comprehension adds a branch.
        self.score += len(node.ifs)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        # Each ``case`` clause is a branch (excluding the implicit fallthrough).
        self.score += max(0, len(node.cases))
        self.generic_visit(node)


def _complexity_of(func: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    visitor = _ComplexityVisitor()
    # Visit the body directly so we don't count nested FunctionDef bodies
    # against the outer function.
    for stmt in func.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        visitor.visit(stmt)
    return visitor.score


def _iter_functions(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


class CyclomaticCeilingGate(WiringGate):
    gate_id = "Q2_cyclomatic_complexity_ratchet"
    tier = "R"
    baseline_filename = "wiring_cyclomatic_complexity_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        layer_by_path: dict[str, str] = {
            row[0]: row[1]
            for row in conn.execute(
                """
                SELECT resolved_path, layer
                FROM nodes
                WHERE entity_type='module'
                  AND resolved_path IS NOT NULL
                """
            )
        }

        violations: list[Violation] = []
        files = list(_REPO_ROOT.rglob("*.py"))
        for py in tqdm(files, desc="Q2_cyclo_files", unit="file"):
            rel = py.relative_to(_REPO_ROOT).as_posix()
            if not rel.startswith(PRODUCTION_ROOTS):
                continue
            if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            try:
                source = py.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=rel)
            except (OSError, SyntaxError):
                continue

            for func in tqdm(list(_iter_functions(tree)), desc="Q2_cyclo_funcs", unit="func", leave=False):
                score = _complexity_of(func)
                if score <= CEILING:
                    continue
                layer = layer_by_path.get(rel, "UNKNOWN")
                subject = f"{rel}:{func.name}"
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=subject,
                        rule="function_exceeds_cyclomatic_ceiling",
                        detail=(f"layer={layer}; complexity={score} > {CEILING}; line={func.lineno}"),
                        extra={
                            "file": rel,
                            "function": func.name,
                            "line": func.lineno,
                            "complexity": score,
                            "ceiling": CEILING,
                            "layer": layer,
                        },
                    )
                )
        return violations


def main() -> int:
    gate = CyclomaticCeilingGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
