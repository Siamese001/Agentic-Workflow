"""Scan Python files for repo-local imports that no longer resolve."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


PROJECT_ROOT = get_validated_project_root()
LOCAL_PREFIXES = ("agentic_core", "apps_lic", "apps_rg", "apps_shared")


@dataclass(slots=True)
class GhostImport:
    file: str
    line: int
    module: str


def module_exists(module_name: str) -> bool:
    path = PROJECT_ROOT / module_name.replace(".", "/")
    return path.with_suffix(".py").exists() or path.is_dir()


def scan_file(path: Path) -> list[GhostImport]:
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    findings: list[GhostImport] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(LOCAL_PREFIXES) and not module_exists(alias.name):
                    findings.append(GhostImport(str(path.relative_to(PROJECT_ROOT)), node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith(LOCAL_PREFIXES) and not module_exists(node.module):
                findings.append(GhostImport(str(path.relative_to(PROJECT_ROOT)), node.lineno, node.module))
    return findings


def main(limit: int = 200) -> int:
    findings: list[GhostImport] = []
    for path in sorted(PROJECT_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        findings.extend(scan_file(path))

    print(f"Ghost imports found: {len(findings)}")
    for finding in findings[:limit]:
        print(f"- {finding.file}:{finding.line} -> {finding.module}")
    if len(findings) > limit:
        print(f"... truncated {len(findings) - limit} additional findings")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for unresolved repo-local imports.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum findings to print.")
    raise SystemExit(main(limit=parser.parse_args().limit))
