#!/usr/bin/env python3
"""Analyze agent classes under agentic_core and emit a technical status report."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root


PROJECT_ROOT = get_validated_project_root()
AGENTS_ROOT = PROJECT_ROOT / AGENTIC_CORE_DIR


@dataclass(slots=True)
class AgentTechnicalStatus:
    file: str
    class_name: str
    line: int
    inherits_base_agent: bool
    has_heal_method: bool
    syntax_ok: bool
    issues: list[str]


def iter_python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def analyze_file(path: Path) -> list[AgentTechnicalStatus]:
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [
            AgentTechnicalStatus(
                file=str(path.relative_to(PROJECT_ROOT)),
                class_name="<syntax-error>",
                line=getattr(exc, "lineno", 0) or 0,
                inherits_base_agent=False,
                has_heal_method=False,
                syntax_ok=False,
                issues=[str(exc)],
            )
        ]

    results: list[AgentTechnicalStatus] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not node.name.endswith("Agent"):
            continue
        base_names = {ast.unparse(base) for base in node.bases}
        method_names = {
            child.name for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        issues: list[str] = []
        inherits_base = any(
            "BaseAgent" in base_name or "SovereignBaseAgent" in base_name for base_name in base_names
        )
        if not inherits_base:
            issues.append("Does not inherit a recognized base agent type")
        has_heal = "heal" in method_names
        if not has_heal:
            issues.append("Missing heal() method")
        results.append(
            AgentTechnicalStatus(
                file=str(path.relative_to(PROJECT_ROOT)),
                class_name=node.name,
                line=node.lineno,
                inherits_base_agent=inherits_base,
                has_heal_method=has_heal,
                syntax_ok=True,
                issues=issues,
            )
        )
    return results


def resolve_report_path(path_arg: str | None) -> Path | None:
    if not path_arg:
        return None
    candidate = Path(path_arg)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    candidate = candidate.resolve()
    if PROJECT_ROOT not in candidate.parents and candidate != PROJECT_ROOT:
        raise ValueError("Report path must remain under the project root")
    return candidate


def main(report_path: str | None = None) -> int:
    all_results: list[AgentTechnicalStatus] = []
    for path in iter_python_files(AGENTS_ROOT):
        all_results.extend(analyze_file(path))

    print(f"Agent classes analyzed: {len(all_results)}")
    unhealthy = [item for item in all_results if item.issues or not item.syntax_ok]
    print(f"Unhealthy findings: {len(unhealthy)}")
    for item in unhealthy[:50]:
        print(f"- {item.file}:{item.line} {item.class_name} -> {'; '.join(item.issues)}")

    target = resolve_report_path(report_path)
    if target is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps([asdict(item) for item in all_results], indent=2), encoding="utf-8")
        print(f"Report saved to: {target}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze agent technical status.")
    parser.add_argument("--report-path", help="Optional JSON report path under the project root.")
    raise SystemExit(main(report_path=parser.parse_args().report_path))
