"""
Analyze apps_shared/legacy for prompt and regex value that may need preservation.
"""

from __future__ import annotations

import argparse
import ast
import logging
import os
import re
from pathlib import Path

from tqdm import tqdm

LOGGER = logging.getLogger(__name__)
DEFAULT_LEGACY_ROOT = Path("apps_shared") / "legacy"
DEFAULT_OUTPUT = "LEGACY_VALUE_REPORT.md"


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def extract_strings(node: ast.AST) -> list[str]:
    """Find prompt templates: long strings with formatting markers."""
    strings: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            if len(child.value) > 50 and ("{" in child.value or "%" in child.value):
                strings.append(child.value[:100] + "...")
    return strings


def extract_regex(content: str) -> list[str]:
    """Find regex patterns."""
    return re.findall(r'r"([^"]{5,})"', content)


def analyze_file(file_path: Path) -> dict[str, object]:
    content = file_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(content, filename=str(file_path))
    return {
        "file": file_path.name,
        "classes": [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
        "prompts": extract_strings(tree),
        "regex_patterns": extract_regex(content),
        "methods": [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)],
    }


def generate_report(legacy_root: Path, output_path: Path) -> int:
    if not legacy_root.exists():
        print(f"Legacy directory not found: {legacy_root}")
        return 1

    report = ["# LEGACY VALUE EXTRACTION REPORT", "", "## Organic Value Findings"]
    for file_path in tqdm(sorted(legacy_root.glob("*.py")), desc="Processing", unit="file"):
        try:
            data = analyze_file(file_path)
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as exc:
            LOGGER.warning("Error analyzing %s: %s", file_path.name, exc)
            continue

        if data["prompts"] or data["regex_patterns"]:
            report.append(f"### File: {data['file']}")
            if data["prompts"]:
                report.append(f"- **Prompts Found:** {len(data['prompts'])}")
            if data["regex_patterns"]:
                report.append(f"- **Regex Patterns:** {len(data['regex_patterns'])}")
                for regex_pattern in data["regex_patterns"]:
                    report.append(f"  - `{regex_pattern}`")
            report.append("")

    _atomic_write(output_path, "\n".join(report) + "\n")
    print(f"Report Generated: {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract prompt and regex value from apps_shared/legacy Python files.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--legacy-root", help="Directory to scan instead of apps_shared/legacy.")
    parser.add_argument("--output", help="Output markdown report path.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    legacy_root = (
        Path(args.legacy_root).expanduser().resolve() if args.legacy_root else repo_root / DEFAULT_LEGACY_ROOT
    )
    output_path = Path(args.output).expanduser().resolve() if args.output else repo_root / DEFAULT_OUTPUT
    return generate_report(legacy_root, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
