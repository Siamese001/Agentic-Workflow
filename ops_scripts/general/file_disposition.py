"""
AST-based diagnostic tool to identify hidden agentic files in apps_shared/common_utils.
"""

from __future__ import annotations

import argparse
import ast
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)
TARGET_SUBPATH = Path("apps_shared") / "common_utils"


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / "apps_shared").exists():
            return candidate
    return Path.cwd().resolve()


@dataclass
class FileDisposition:
    filepath: str
    is_agent: bool
    confidence: str
    signals: list[str]


class AgentVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.is_agent = False
        self.signals: list[str] = []
        self.agent_imports = {"langchain", "openai", "anthropic", "crewai", "autogen"}
        self.agent_bases = {"BaseAgent", "Agent", "Chain", "LLMChain"}
        self.agent_decorators = {"tool", "action"}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if any(imp in alias.name for imp in self.agent_imports):
                self.is_agent = True
                self.signals.append(f"Import detected: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and any(imp in node.module for imp in self.agent_imports):
            self.is_agent = True
            self.signals.append(f"From-Import detected: {node.module}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self.agent_bases:
                self.is_agent = True
                self.signals.append(f"Inheritance detected: {base.id}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in self.agent_decorators:
                self.is_agent = True
                self.signals.append(f"Decorator detected: @{decorator.id}")
            elif (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id in self.agent_decorators
            ):
                self.is_agent = True
                self.signals.append(f"Decorator call detected: @{decorator.func.id}")
        self.generic_visit(node)


def analyze_directory(directory: Path) -> list[FileDisposition]:
    results: list[FileDisposition] = []
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return results

    for root, dirs, files in tqdm(os.walk(directory), desc="Processing", unit="dir"):
        dirs[:] = sorted(d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS)
        for file_name in sorted(files):
            if not file_name.endswith(".py"):
                continue

            full_path = Path(root) / file_name
            try:
                source = full_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(full_path))
                visitor = AgentVisitor()
                visitor.visit(tree)
                results.append(
                    FileDisposition(
                        filepath=str(full_path),
                        is_agent=visitor.is_agent,
                        confidence="HIGH" if visitor.signals else "LOW",
                        signals=visitor.signals,
                    )
                )
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as exc:
                LOGGER.warning("Failed to analyze %s: %s", full_path, exc)
                results.append(
                    FileDisposition(
                        filepath=str(full_path),
                        is_agent=False,
                        confidence="ERROR",
                        signals=[f"Parse Error: {exc}"],
                    )
                )
    return results


def generate_report(results: list[FileDisposition], repo_root: Path) -> None:
    print(f"{'DISPOSITION':<12} | {'FILE PATH':<60} | {'SIGNALS'}")
    print("-" * 100)
    for result in results:
        disposition = "MOVE" if result.is_agent else "STAY"
        file_path = Path(result.filepath)
        try:
            rel_path = file_path.relative_to(repo_root)
        except ValueError:
            rel_path = file_path
        signals = ", ".join(result.signals[:2]) if result.signals else "-"
        prefix = "!!" if result.is_agent else "  "
        print(f"{prefix} {disposition:<9} | {str(rel_path):<60} | {signals}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze apps_shared/common_utils for hidden agentic code.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--target-dir", help="Optional explicit directory to analyze.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    target_dir = (
        Path(args.target_dir).expanduser().resolve() if args.target_dir else repo_root / TARGET_SUBPATH
    )

    print(f"Scanning {target_dir} for agent contamination...")
    results = analyze_directory(target_dir)
    generate_report(results, repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
