#!/usr/bin/env python3
"""
check_deferred_scope_markers.py — pre-commit + CI gate for DEFERRED_SCOPE marker contract.

Scans plan files (`.cursor/plans/*.md`) for prose deferred-scope language.
If any are present AND the file lacks a matching `DEFERRED_SCOPE:` marker,
a violation is reported.

Policy: `.claude/rules/deferred-scope-capture.md`

Modes:
  --staged (default): Scan only git-staged plan files (pre-commit mode)
  --all: Scan all plan files on disk (CI mode)

Scoped narrowly to avoid false positives:
  - Only .cursor/plans/*.md files (where backlog is recorded)
  - In --staged mode: only added lines (`+` in diff)
  - In --all mode: all lines (baseline scan)
  - Only if file lacks ANY DEFERRED_SCOPE: marker
  - Rule / doc files with meta-discussion are NOT scanned

Usage:
    python ops_scripts/ci/check_deferred_scope_markers.py [--staged|--all] [--json]

Exit codes:
    0 — no violations (or no plan files to scan)
    1 — violations found (commit/CI blocked)

Environment:
    DEFERRED_SCOPE_GATE_BYPASS=1 — skip check
    DEFERRED_SCOPE_GATE_FAIL_CLOSED=1 — exit 1 on violations (CI mode)

Output:
    artifacts/ci/deferred_scope_gate.json (in --all mode)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Phrases that suggest deferred scope without a marker
PROSE_PATTERNS = [
    re.compile(
        r"\bdeferred\s+to\s+(?:a\s+)?(?:future|later|next)\s+(?:wave|phase|session|sprint)\b", re.IGNORECASE
    ),
    re.compile(r"\bout\s+of\s+scope\s+for\s+this\s+(?:wave|phase|plan|session)\b", re.IGNORECASE),
    re.compile(r"\bfuture\s+work\b", re.IGNORECASE),
    re.compile(r"\bwill\s+be\s+done\s+(?:later|next|in\s+a\s+future)\b", re.IGNORECASE),
    re.compile(r"\bparked\s+indefinitely\b", re.IGNORECASE),
    re.compile(r"\bnot\s+yet\s+tackled\b", re.IGNORECASE),
    re.compile(r"\baddressed\s+in\s+a\s+later\s+(?:wave|phase|plan)\b", re.IGNORECASE),
]
MARKER_RE = re.compile(r"^\s*DEFERRED_SCOPE:\s*", re.IGNORECASE | re.MULTILINE)

# Files scoped to this gate
PLAN_GLOB_RE = re.compile(r"^\.cursor/plans/.+\.md$")


def _run(argv: list[str]) -> str:
    try:
        result = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout or ""


def _staged_plan_files() -> list[str]:
    out = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
    return [line for line in out.splitlines() if PLAN_GLOB_RE.match(line)]


def _staged_added_lines(path: str) -> list[tuple[int, str]]:
    """Return (line_no, text) for added lines in the staged diff of `path`."""
    out = _run(["git", "diff", "--cached", "--unified=0", "--", path])
    added: list[tuple[int, str]] = []
    current_line = 0
    for raw in out.splitlines():
        # Hunk header: @@ -a,b +c,d @@
        if raw.startswith("@@"):
            m = re.match(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@", raw)
            if m:
                current_line = int(m.group(1))
            continue
        if raw.startswith("+++") or raw.startswith("---"):
            continue
        if raw.startswith("+"):
            added.append((current_line, raw[1:]))
            current_line += 1
        elif raw.startswith("-"):
            pass
        else:
            current_line += 1
    return added


def _file_has_marker(path: str) -> bool:
    """Check whether the staged (post-commit) version of the file has a marker."""
    content = _run(["git", "show", f":{path}"])
    return bool(MARKER_RE.search(content))


def _all_plan_files() -> list[Path]:
    """Return all plan files on disk (CI mode)."""
    plans_dir = REPO_ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    if not plans_dir.exists():
        return []
    return list(plans_dir.glob("*.md"))


def _file_lines(path: Path) -> list[tuple[int, str]]:
    """Return (line_no, text) for all lines in file."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return [(i + 1, line) for i, line in enumerate(content.splitlines())]


def _file_has_marker_disk(path: Path) -> bool:
    """Check whether file on disk has a DEFERRED_SCOPE marker."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return bool(MARKER_RE.search(content))


def check_all_plans() -> dict[str, list[dict[str, Any]]]:
    """Check all plan files on disk (CI mode). Returns violations by file."""
    violations: list[dict[str, Any]] = []
    files_scanned = 0
    
    for path in _all_plan_files():
        files_scanned += 1
        if _file_has_marker_disk(path):
            continue  # file has marker — assumed compliant
        
        rel_path = f".cursor/plans/{path.name}"
        for line_no, text in _file_lines(path):
            for pattern in PROSE_PATTERNS:
                m = pattern.search(text)
                if m:
                    violations.append({
                        "path": rel_path,
                        "line": line_no,
                        "phrase": m.group(0),
                        "snippet": text.strip()[:120],
                    })
                    break  # one violation per line enough
    
    return {
        "files_scanned": files_scanned,
        "violation_count": len(violations),
        "violations": violations,
    }


def write_ci_report(report: dict[str, Any]) -> None:
    """Write JSON report for CI mode."""
    report_path = REPO_ROOT / "artifacts" / "ci" / "deferred_scope_gate.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import json
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except (OSError, ImportError):
        pass


def _run_staged_mode() -> tuple[list[tuple[str, int, str, str]], int]:
    """Run pre-commit staged scan. Returns (violations, file_count)."""
    plan_files = _staged_plan_files()
    if not plan_files:
        return [], 0

    violations: list[tuple[str, int, str, str]] = []
    for path in plan_files:
        if _file_has_marker(path):
            continue  # file has at least one marker — assumed compliant
        added = _staged_added_lines(path)
        for line_no, text in added:
            for pattern in PROSE_PATTERNS:
                m = pattern.search(text)
                if m:
                    violations.append((path, line_no, m.group(0), text.strip()))
                    break
    return violations, len(plan_files)


def _is_ci_environment() -> bool:
    """Detect if running in CI environment."""
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "JENKINS_URL", "BUILDKITE"]
    return any(os.environ.get(var) for var in ci_vars)


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="DEFERRED_SCOPE marker compliance gate")
    parser.add_argument("--staged", action="store_true", help="Pre-commit mode: scan staged files only")
    parser.add_argument("--all", dest="all_files", action="store_true", help="CI mode: scan all plan files")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on violations")
    args = parser.parse_args(argv)

    # Environment bypass
    if os.environ.get("DEFERRED_SCOPE_GATE_BYPASS") == "1":
        print("[deferred_scope_gate] BYPASS engaged", file=sys.stderr)
        return 0

    fail_closed = args.fail_closed or (os.environ.get("DEFERRED_SCOPE_GATE_FAIL_CLOSED") == "1")

    # Determine mode: explicit > CI detection > default (staged)
    if args.all_files:
        ci_mode = True
    elif args.staged:
        ci_mode = False
    elif _is_ci_environment():
        ci_mode = True  # Auto-detect CI
    else:
        ci_mode = False  # Default to staged for local runs

    if ci_mode:
        # CI mode: scan all plan files
        report = check_all_plans()
        write_ci_report(report)

        if args.json:
            print(json.dumps(report, indent=2))
            return 0

        print("=== Deferred Scope Marker Compliance (CI mode) ===")
        print(f"Files scanned: {report['files_scanned']}")
        print(f"Violations: {report['violation_count']}")

        if report["violations"]:
            print("\nDeferred-scope prose without DEFERRED_SCOPE marker:")
            for v in report["violations"]:
                print(f"\n  {v['path']}:{v['line']}")
                print(f"    Phrase: '{v['phrase']}'")
                print(f"    Line: {v['snippet'][:80]}...")
        else:
            print("\n✅ All plan files have DEFERRED_SCOPE markers where needed")

        if fail_closed and report["violation_count"] > 0:
            return 1
        return 0

    else:
        # Pre-commit staged mode
        violations, file_count = _run_staged_mode()

        if not violations:
            return 0

        print("", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        print("BLOCKED: deferred-scope prose without DEFERRED_SCOPE marker", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        print(
            "The following staged plan files introduce deferred-scope prose "
            "without emitting a DEFERRED_SCOPE: marker. This violates the "
            "deferred-scope-capture rule.",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        for path, line_no, phrase, full_line in violations:
            snippet = full_line[:100] + ("..." if len(full_line) > 100 else "")
            print(
                f"  {path}:{line_no}  phrase='{phrase}'\n    {snippet}",
                file=sys.stderr,
            )
        print("", file=sys.stderr)
        print("Fix options:", file=sys.stderr)
        print(
            "  1. Add a DEFERRED_SCOPE: marker line to the same file (see "
            ".claude/rules/deferred-scope-capture.md for schema).",
            file=sys.stderr,
        )
        print(
            "  2. Rephrase the prose to remove deferred-scope language if this is "
            "historical commentary, not a new deferred item.",
            file=sys.stderr,
        )
        print(
            "  3. Emergency bypass: DEFERRED_SCOPE_GATE_BYPASS=1 git commit ...",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
