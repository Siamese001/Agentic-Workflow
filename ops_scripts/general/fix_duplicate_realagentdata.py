#!/usr/bin/env python3
"""Remove duplicate ``realAgentData`` declarations from the autonomy dashboard.

This utility scans the dashboard HTML, keeps the first valid
``const realAgentData = { ... };`` declaration, and removes later duplicates.
It defaults to dry-run mode so accidental edits are avoided.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)

try:
    from agentic_core.L0_routing.config.path_constants import DASHBOARD_DIR as _DASHBOARD_DIR
except Exception:
    _DASHBOARD_DIR = "dashboard"

DEFAULT_DASHBOARD_BASENAME = "autonomy_dashboard.html"
ASSIGNMENT_PATTERN = re.compile(r"\bconst\s+realAgentData\s*=\s*\{", re.MULTILINE)
COMMENT_PATTERN = re.compile(r"//\s*Real per-agent data.*", re.IGNORECASE)


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / "agentic_core").exists():
            return candidate

    return Path.cwd().resolve()


def _resolve_dashboard_path(explicit_path: str | None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()

    root = _resolve_project_root()
    candidate = root / _DASHBOARD_DIR / DEFAULT_DASHBOARD_BASENAME
    if candidate.exists():
        return candidate

    fallback_matches = list(root.rglob(DEFAULT_DASHBOARD_BASENAME))
    if fallback_matches:
        return fallback_matches[0]

    return candidate


def _find_matching_brace(text: str, open_brace_index: int) -> int | None:
    depth = 0
    in_single = False
    in_double = False
    in_template = False
    escaped = False

    for index in range(open_brace_index, len(text)):
        char = text[index]

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if not in_double and not in_template and char == "'":
            in_single = not in_single
            continue
        if not in_single and not in_template and char == '"':
            in_double = not in_double
            continue
        if not in_single and not in_double and char == "`":
            in_template = not in_template
            continue

        if in_single or in_double or in_template:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index

    return None


def _find_assignment_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []

    for match in ASSIGNMENT_PATTERN.finditer(text):
        open_brace_index = text.find("{", match.start())
        if open_brace_index < 0:
            continue

        close_brace_index = _find_matching_brace(text, open_brace_index)
        if close_brace_index is None:
            LOGGER.warning("Skipping unmatched declaration at index %s", match.start())
            continue

        semicolon_index = close_brace_index + 1
        while semicolon_index < len(text) and text[semicolon_index].isspace():
            semicolon_index += 1
        if semicolon_index < len(text) and text[semicolon_index] == ";":
            semicolon_index += 1

        comment_match = COMMENT_PATTERN.search(text, 0, match.start())
        start_index = match.start()
        if comment_match:
            line_start = text.rfind("\n", 0, comment_match.start()) + 1
            if line_start >= 0 and comment_match.end() <= match.start():
                start_index = line_start

        ranges.append((start_index, semicolon_index))

    return ranges


def _apply_fix(html: str) -> tuple[str, int]:
    ranges = _find_assignment_ranges(html)
    if len(ranges) <= 1:
        return html, 0

    cleaned = html
    removed = 0
    for start, end in reversed(ranges[1:]):
        cleaned = cleaned[:start] + cleaned[end:]
        removed += 1

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned, removed


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard-path", help="Override dashboard HTML path.")
    parser.add_argument("--execute", action="store_true", help="Persist the cleaned file.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    dashboard_path = _resolve_dashboard_path(args.dashboard_path)
    if not dashboard_path.exists():
        LOGGER.error("Dashboard file not found: %s", dashboard_path)
        return 2

    html = dashboard_path.read_text(encoding="utf-8")
    cleaned_html, removed = _apply_fix(html)

    LOGGER.info("Found %s duplicate declaration(s)", removed)
    if removed == 0:
        return 0

    if not args.execute:
        LOGGER.info("Dry run only. Use --execute to write changes.")
        return 0

    _atomic_write(dashboard_path, cleaned_html)
    LOGGER.info("Updated %s", dashboard_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
