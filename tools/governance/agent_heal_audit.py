#!/usr/bin/env python3
"""
Agent Healing Audit - Deterministic AST Enumeration

Phase 1, Wave 1.1: Core audit functionality
- AST-only scanning (no runtime imports)
- Detect heal() and heal_repository() methods
- Produce byte-stable JSON output
"""

import argparse
import ast
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


class AgentHealAuditScanner:
    """AST-based scanner for agent healing capabilities."""

    def __init__(self, repo_root: Path):
        """Initialize scanner with repository root."""
        self.repo_root = repo_root

    def scan_agent_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single Python file for Agent classes and their healing methods."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            agents = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    # Detect healing methods
                    has_heal = False
                    has_heal_repository = False

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name == "heal":
                                has_heal = True
                            elif item.name == "heal_repository":
                                has_heal_repository = True

                    # Get base class names (AST only, no resolution)
                    base_class_names = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_class_names.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            # Handle cases like module.ClassName
                            base_class_names.append(ast.unparse(base))

                    # Get repo-relative path with forward slashes (OS-independent)
                    repo_relative = str(PurePosixPath(file_path.relative_to(self.repo_root)))

                    agents.append(
                        {
                            "repo_relative_path": repo_relative,
                            "class_name": node.name,
                            "has_heal": has_heal,
                            "has_heal_repository": has_heal_repository,
                            "base_class_names": sorted(base_class_names),  # Ensure deterministic ordering
                        }
                    )

            return sorted(agents, key=lambda x: (x["repo_relative_path"], x["class_name"]))

        except (SyntaxError, UnicodeDecodeError, OSError):
            # Skip files that can't be parsed
            return []

    def scan_repository(self) -> dict[str, Any]:
        """Scan entire repository for Agent classes."""
        scan_paths = [
            self.repo_root / "agentic_core",
            self.repo_root / "apps_lic",
            self.repo_root / "apps_rg",
            self.repo_root / "apps_shared",
        ]

        all_agents = []

        for scan_path in scan_paths:
            if scan_path.exists():
                for py_file in scan_path.rglob("*.py"):
                    # Skip __pycache__ and test files for cleaner results
                    if "__pycache__" not in str(py_file) and not py_file.name.startswith("test_"):
                        agents = self.scan_agent_file(py_file)
                        all_agents.extend(agents)

        # Sort deterministically
        all_agents.sort(key=lambda x: (x["repo_relative_path"], x["class_name"]))

        # Compute summary
        total_agents = len(all_agents)
        missing_heal = sum(1 for agent in all_agents if not agent["has_heal"])
        missing_heal_repository = sum(1 for agent in all_agents if not agent["has_heal_repository"])
        missing_both = sum(
            1 for agent in all_agents if not agent["has_heal"] and not agent["has_heal_repository"]
        )

        return {
            "audit_results": all_agents,
            "summary": {
                "total_agents": total_agents,
                "missing_heal": missing_heal,
                "missing_heal_repository": missing_heal_repository,
                "missing_both": missing_both,
            },
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Agent Healing Audit - AST Enumeration")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format")
    parser.add_argument("--out", type=Path, help="Output file path (for markdown format)")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path")

    args = parser.parse_args()

    scanner = AgentHealAuditScanner(args.repo_root)
    result = scanner.scan_repository()

    if args.format == "json":
        # Use sorted keys for deterministic output
        json_output = json.dumps(result, indent=2, sort_keys=True)
        print(json_output)
    elif args.format == "md":
        if not args.out:
            print("Error: --out required for markdown format", file=sys.stderr)
            sys.exit(1)
        markdown = generate_markdown_report(result)
        args.out.write_text(markdown, encoding="utf-8")
        print(f"Markdown report generated: {args.out}")


def generate_markdown_report(audit_data: dict[str, Any]) -> str:
    """Generate deterministic markdown report from audit data."""
    results = audit_data["audit_results"]
    summary = audit_data["summary"]

    lines = [
        "# Agent Healing Audit Report",
        "",
        "## Summary",
        "",
        f"- **Total Agents**: {summary['total_agents']}",
        f"- **Missing heal()**: {summary['missing_heal']}",
        f"- **Missing heal_repository()**: {summary['missing_heal_repository']}",
        f"- **Missing Both**: {summary['missing_both']}",
        "",
        "## Detailed Results",
        "",
        "| Path | Class | heal | heal_repository |",
        "|------|-------|------|-----------------|",
    ]

    # Add table rows (already sorted deterministically)
    for agent in results:
        path = agent["repo_relative_path"].replace("\\", "/")  # Normalize path separators
        class_name = agent["class_name"]
        heal_check = "✓" if agent["has_heal"] else "✗"
        heal_repo_check = "✓" if agent["has_heal_repository"] else "✗"

        lines.append(f"| {path} | {class_name} | {heal_check} | {heal_repo_check} |")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
