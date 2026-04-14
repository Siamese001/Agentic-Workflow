"""
Regression guard that blocks reintroduction of agentic logic into apps_shared/common_utils.
"""

from __future__ import annotations

import argparse
import ast
import logging
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)
TARGET_SUBPATH = Path("apps_shared") / "common_utils"
BANNED_SUFFIXES = ("Executor", "Agent", "Orchestrator", "Strategist")
BANNED_IMPORTS = ("langchain", "crewai", "autogen", "semantic_kernel")
BANNED_BASES = ("BaseAgent", "Agent", "LLMChain")


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


def scan_for_violations(target_dir: Path) -> list[str]:
    violations: list[str] = []
    if not target_dir.exists():
        print(f"Target directory {target_dir} does not exist. Skipping.")
        return violations

    for root, dirs, files in tqdm(os.walk(target_dir), desc="Processing", unit="dir"):
        dirs[:] = sorted(d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS)
        for file_name in sorted(files):
            if not file_name.endswith(".py"):
                continue

            for suffix in BANNED_SUFFIXES:
                if file_name.lower().endswith(suffix.lower() + ".py"):
                    violations.append(f"[Filename Violation] {file_name} contains banned suffix '{suffix}'")

            full_path = Path(root) / file_name
            try:
                source = full_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(full_path))
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as exc:
                LOGGER.warning("Could not parse %s: %s", full_path, exc)
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if any(banned in name.name for banned in BANNED_IMPORTS):
                            violations.append(
                                f"[Import Violation] {file_name} imports banned module '{name.name}'"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(banned in node.module for banned in BANNED_IMPORTS):
                        violations.append(
                            f"[Import Violation] {file_name} imports from banned module '{node.module}'"
                        )
                elif isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in BANNED_BASES:
                            violations.append(
                                f"[Inheritance Violation] {file_name} defines class "
                                f"'{node.name}' inheriting from '{base.id}'"
                            )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan apps_shared/common_utils for reintroduced agentic logic.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--target-dir",
        help="Optional explicit directory to scan. Defaults to apps_shared/common_utils under the repo root.",
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    target_dir = (
        Path(args.target_dir).expanduser().resolve() if args.target_dir else repo_root / TARGET_SUBPATH
    )

    print(f"🛡️  Architectural Guard Active: Scanning {target_dir}...")
    violations = scan_for_violations(target_dir)
    if violations:
        print("\n❌ ARCHITECTURAL INTEGRITY FAILURE")
        print("The following files violate the 'No Agents in Utils' policy:")
        print("-" * 60)
        for violation in violations:
            print(f" - {violation}")
        print("-" * 60)
        print("ACTION REQUIRED: Move these files to an appropriate engine or orchestration territory.")
        return 1

    print("\n✅ Architectural Integrity Verified: No Agents detected in common_utils.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
