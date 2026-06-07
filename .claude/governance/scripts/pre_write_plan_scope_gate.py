#!/usr/bin/env python3
"""pre_write_plan_scope_gate.py — plan Files-In-Scope advisory gate.

Reads JSON payload from stdin (pre_write_code hook). When an active plan
is detected (most-recently-modified `.claude/plans/*.md` within the last
24 hours) and the plan has an `## Phase-Level Summary` table with a
`Scope (files)` column, this gate:

  - Extracts all file tokens listed in that column across all phases.
  - Compares the write target to those tokens.
  - If the target matches no listed token AND looks like a source file
    (.py/.md/.json/.yaml/.toml), emits a stderr warning.

Default behavior: ADVISORY (exit 0 + warning). This avoids false-positive
blocks during exploratory work.

Strict behavior: set `PLAN_SCOPE_STRICT=1` to upgrade the warning to a
block (exit 2).

Bypass: set `PLAN_SCOPE_BYPASS=1` to skip entirely (logs to stderr).

Fail-open on any internal error — scope enforcement must never break
writes when the gate itself has a bug.

Scope-containment rule reference: `.claude/rules/scope-containment.md`.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".claude" / "plans"
# Freshness window: plans modified in the last 24h are "active".
PLAN_FRESHNESS_SEC = 24 * 3600
# File extensions we treat as "code/docs" for scope enforcement.
_SOURCE_EXT = (".py", ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".sql")
# Heuristic: tokens in the Scope column that look like file paths.
_PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]+")


def _latest_active_plan() -> Path | None:
    if not PLANS_DIR.is_dir():
        return None
    now = time.time()
    candidates: list[tuple[float, Path]] = []
    for p in PLANS_DIR.glob("*.md"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if (now - mtime) <= PLAN_FRESHNESS_SEC:
            candidates.append((mtime, p))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _extract_scope_tokens(plan_text: str) -> set[str]:
    """Parse the `## Phase-Level Summary` table and return file-path tokens
    appearing in the Scope column."""
    tokens: set[str] = set()
    # Locate the Phase-Level Summary heading.
    idx = plan_text.find("## Phase-Level Summary")
    if idx < 0:
        return tokens
    section = plan_text[idx:]
    # Stop at the next top-level heading.
    end = section.find("\n## ", 2)
    if end > 0:
        section = section[:end]
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Header / separator rows don't carry tokens we care about.
        if len(cells) < 3:
            continue
        # Expected column order per template: Phase ID | Title | Scope (files) | ...
        scope_cell = cells[2] if len(cells) >= 3 else ""
        for m in _PATH_TOKEN_RE.findall(scope_cell):
            # Normalize separators for cross-platform comparison.
            tokens.add(m.replace("\\", "/"))
    return tokens


def _is_source_file(path: str) -> bool:
    return path.lower().endswith(_SOURCE_EXT)


def _normalize(path: str) -> str:
    p = path.replace("\\", "/")
    # Drop leading ./ and repo-root prefix if present.
    if p.startswith("./"):
        p = p[2:]
    return p


def _path_in_scope(write_path: str, scope_tokens: set[str]) -> bool:
    """Return True iff the write target matches any scope token.

    Matching is substring/suffix based because scope cells commonly use
    partial paths (e.g. `pre_write_gate.py` rather than the full path).
    """
    wp = _normalize(write_path)
    wp_base = wp.rsplit("/", 1)[-1]
    for tok in scope_tokens:
        t = _normalize(tok)
        if not t:
            continue
        if t in wp or wp.endswith(t) or wp_base == t.rsplit("/", 1)[-1]:
            return True
    return False


def _read_payload() -> dict | None:
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return None
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        return None
    return payload if isinstance(payload, dict) else None


def main() -> int:
    if os.environ.get("PLAN_SCOPE_BYPASS", "").strip() == "1":
        sys.stderr.write("[plan-scope-gate] bypass active (PLAN_SCOPE_BYPASS=1)\n")
        return 0

    if sys.stdin.isatty():
        return 0

    try:
        payload = _read_payload()
        if payload is None:
            return 0
        tool_info = payload.get("tool_info", payload) if isinstance(payload, dict) else {}
        if not isinstance(tool_info, dict):
            return 0
        file_path = tool_info.get("file_path") or tool_info.get("target_file") or ""
        if not isinstance(file_path, str) or not file_path:
            return 0
        if not _is_source_file(file_path):
            return 0

        plan = _latest_active_plan()
        if plan is None:
            return 0

        try:
            plan_text = plan.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0
        scope_tokens = _extract_scope_tokens(plan_text)
        if not scope_tokens:
            return 0  # no parseable scope → cannot enforce

        if _path_in_scope(file_path, scope_tokens):
            return 0

        strict = os.environ.get("PLAN_SCOPE_STRICT", "").strip() == "1"
        msg = (
            f"[plan-scope-gate] {'BLOCKED' if strict else 'WARNING'}: "
            f"'{file_path}' is NOT listed in `## Phase-Level Summary · Scope (files)` of "
            f"active plan '{plan.name}'. "
            f"See .claude/rules/scope-containment.md. "
            f"Bypass: PLAN_SCOPE_BYPASS=1. Strict toggle: PLAN_SCOPE_STRICT=1.\n"
        )
        sys.stderr.write(msg)
        return 2 if strict else 0
    except (OSError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"[plan-scope-gate] fail-open: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
