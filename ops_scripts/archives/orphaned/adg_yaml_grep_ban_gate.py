"""ADG YAML Grep-Ban Gate — enforce no grep/rg in GitHub Actions workflow files.

Rejects workflow YAML files that invoke grep/rg/ripgrep in shell `run:` steps
as ADG query substitutes.  GitHub Actions workflows must use the ADG accelerators
or Python-based equivalents instead of raw grep.

Why this matters
────────────────
A `run: grep -r "pattern" agentic_core/` in CI is just as bad as the same call
in a Python file — it bypasses the ADG graph and produces brittle, slow results.

Banned patterns (in YAML `run:` blocks)
─────────────────────────────────────────
  run: grep <args>
  run: rg <args>
  run: ripgrep <args>
  run: | <multiline with grep/rg on a line>

Exemptions
──────────
  Per-line YAML comment:  # guardian: allow-grep-yaml -- <justification>
  The comment must appear on the SAME shell command line within the run block.

  File-level skip:  # adg-yaml-grep-ban: skip-file  (first 5 lines of YAML)

Exit codes
──────────
  0 — no violations
  1 — violations found (hard fail)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

# ---------------------------------------------------------------------------
# Patterns for shell command lines inside YAML run: blocks
# ---------------------------------------------------------------------------

# Shell command line that invokes grep/rg/ripgrep as the first command
# Matches: "  grep -r ..." or "  rg ..." or "  | grep ..." or "  && grep ..."
_SHELL_GREP_CMD_RE = re.compile(
    r"(?:^|&&|\|\||\|)\s*\b(?:grep|rg|ripgrep|ag|ack)\b",
)

# Whole-line run: grep ... (single-line run step)
_YAML_INLINE_RUN_RE = re.compile(
    r"^\s+run:\s+\S",
)

# Per-line YAML exemption comment
_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-grep-yaml\s+--\s+\S")

# File-level skip (first 5 lines)
_FILE_SKIP_RE = re.compile(r"#\s*adg-yaml-grep-ban:\s*skip-file")


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def _is_shell_command_line(line: str) -> bool:
    """Return True if the line looks like a shell command inside a run: block."""
    stripped = line.strip()
    # Skip blank lines and pure YAML keys
    if not stripped or stripped.endswith(":") and " " not in stripped:
        return False
    # Skip YAML list indicators that are not commands
    if stripped.startswith("name:") or stripped.startswith("uses:") or stripped.startswith("with:"):
        return False
    return True


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return (1-indexed line_no, line_text) for each violation in path."""
    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
        return violations

    # File-level skip (first 5 lines)
    for header_line in lines[:5]:
        if _FILE_SKIP_RE.search(header_line):
            return violations

    in_run_block = False

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Detect start of a run: block
        if re.match(r"^\s+run:\s*[|>]?\s*$", line) or re.match(r"^\s+run:\s+\S", line):
            in_run_block = True

        # Detect end of run: block (de-indentation or new YAML key at same level)
        if in_run_block and line_no > 1:
            # If we hit a YAML key at the step level (2-space or 4-space indent key)
            if re.match(r"^\s{2,4}[a-zA-Z_-]+:", line) and not re.match(r"^\s{6,}", line):
                in_run_block = False

        # Skip YAML comments
        if stripped.startswith("#"):
            continue

        # Check for exemption on this line
        if _EXEMPTION_RE.search(line):
            continue

        # Scan shell command lines within run blocks, or inline run: grep
        is_inline_run = bool(re.match(r"^\s+run:\s+\S", line))
        is_in_block = in_run_block and _is_shell_command_line(line)

        if is_inline_run or is_in_block:
            # Check if this line contains a grep/rg invocation
            check_content = line
            if is_inline_run:
                # Strip the "run: " prefix for matching
                check_content = re.sub(r"^\s+run:\s+", "", line)

            if _SHELL_GREP_CMD_RE.search(check_content):
                violations.append((line_no, line.rstrip()))

    return violations


def scan_files(paths: list[Path]) -> dict[Path, list[tuple[int, str]]]:
    result: dict[Path, list[tuple[int, str]]] = {}
    for p in paths:
        vs = scan_file(p)
        if vs:
            result[p] = vs
    return result


def _get_all_workflow_files(root: Path) -> list[Path]:
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.exists():
        return []
    r = subprocess.run(
        ["git", "ls-files", ".github/workflows/"],
        cwd=str(root), capture_output=True, encoding="utf-8", timeout=30,
    )
    return [
        root / f for f in r.stdout.splitlines()
        if f.endswith(".yml") or f.endswith(".yaml")
    ]


def _get_staged_yaml_files(root: Path) -> list[Path]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        cwd=str(root), capture_output=True, encoding="utf-8", timeout=30,
    )
    return [
        root / f for f in r.stdout.splitlines()
        if f.endswith(".yml") or f.endswith(".yaml")
    ]


def _cli() -> int:
    import argparse
    import sys

    # Add project root for schema imports
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel

    parser = argparse.ArgumentParser(
        prog="adg_yaml_grep_ban_gate",
        description="Hard-fail gate: no grep/rg in GitHub Actions run: steps.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument(
        "--all-yaml",
        action="store_true",
        dest="all_yaml",
        help="Scan all YAML workflow files tracked by git",
    )
    parser.add_argument(
        "--json-output",
        metavar="PATH",
        help="Write structured issues to JSON lines file",
    )
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files if f.endswith((".yml", ".yaml"))]
    elif args.all_yaml:
        paths = _get_all_workflow_files(ROOT)
    else:
        paths = _get_staged_yaml_files(ROOT)

    paths = [p for p in paths if p.is_file()]

    if not paths:
        print("OK: no YAML workflow files to scan.")
        return 0

    violations = scan_files(paths)

    # Build structured issues for JSON output
    json_issues = []
    for path, vs in violations.items():
        for line_no, line_text in vs:
            issue = PreCommitIssue(
                hook_id="adg-yaml-grep-ban-gate",
                hook_name="ADG YAML Grep Ban",
                severity=SeverityLevel.CRITICAL,
                file_path=str(path.relative_to(ROOT)),
                line_number=line_no,
                message="Grep/rg found in GitHub Actions run step",
                explanation="Use ADG accelerators or Python scripts instead of grep in CI workflows. Shell grep lacks semantic awareness.",
                issue_type="yaml_grep_ban",
            )
            json_issues.append(issue)

    # Write JSON output if requested
    if args.json_output and json_issues:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for issue in json_issues:
                f.write(issue.to_json() + "\n")

    if not violations:
        print(f"OK: no yaml-grep-ban violations in {len(paths)} workflow file(s).")
        return 0

    total = sum(len(vs) for vs in violations.values())
    print(f"\nFAIL: {total} yaml-grep-ban violation(s) in {len(violations)} workflow file(s).", file=sys.stderr)
    print("Do not use grep/rg in GitHub Actions run: steps. Use ADG accelerators instead.", file=sys.stderr)
    print("  Exemption: # guardian: allow-grep-yaml -- <justification>", file=sys.stderr)
    print("", file=sys.stderr)
    for path, vs in sorted(violations.items()):
        for line_no, line in vs:
            rel = path.relative_to(ROOT) if path.is_absolute() else path
            print(f"  {rel}:{line_no}: {line.strip()}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(_cli())
