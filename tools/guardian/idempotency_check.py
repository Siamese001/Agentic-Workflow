"""
Guardian Idempotency Checker — W3.6

Detects duplicate guardian comments in Python files:
  1. Same line has multiple '# guardian: allow-*' annotations
  2. Same (file, line_number) has a guardian already AND the incoming edit adds another

Usage:
  python tools/guardian/idempotency_check.py [path ...]   # scan files or directories
  python tools/guardian/idempotency_check.py .            # scan whole repo
  python tools/guardian/idempotency_check.py --json       # JSON output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]

_GUARDIAN_RE = re.compile(r"#\s*guardian:\s*allow-\w[\w-]*")
_GENERIC_JUSTIFICATIONS = frozenset(
    {
        "needed",
        "required",
        "temporary",
        "legacy",
        "fixme",
        "todo",
        "workaround",
        "temp",
        "hack",
        "wip",
    }
)


def _count_guardians_on_line(line: str) -> int:
    """Count guardian annotations on a single line."""
    return len(_GUARDIAN_RE.findall(line))


def _check_justification_quality(line: str) -> str | None:
    """
    Returns an error message if the guardian comment has a weak/missing justification.
    Returns None if justification is acceptable.
    """
    matches = _GUARDIAN_RE.finditer(line)
    for match in tqdm(matches, desc="Processing", unit="item"):
        after = line[match.end() :]
        # Accept both ' -- ' (canonical) and ' - ' (legacy) as separators
        if "--" in after:
            justification = after.split("--", 1)[-1].strip()
        else:
            _m = re.search(r"(?<!-) - (?!-)", after)
            if _m:
                justification = after[_m.end() :].strip()
            else:
                justification = ""
        has_justification = len(justification) > 3
        if not has_justification:
            return "Missing justification — add '# guardian: allow-<type> -- <specific justification>'"
        for generic in _GENERIC_JUSTIFICATIONS:
            if justification == generic or justification.startswith(generic + " "):
                return f"Generic justification '{generic}' is forbidden — be specific about why this exemption is needed"
    return None


def scan_file(filepath: Path) -> list[dict]:
    """
    Scan a single Python file for guardian idempotency violations.
    Returns list of {file, line, line_no, issue} dicts.
    """
    issues: list[dict] = []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return issues

    try:
        rel_path = str(filepath.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        rel_path = str(filepath).replace("\\", "/")

    for i, line in tqdm(enumerate(lines, 1), desc="Processing", unit="item"):
        guardian_count = _count_guardians_on_line(line)
        if guardian_count > 1:
            issues.append(
                {
                    "file": rel_path,
                    "line_no": i,
                    "line": line.strip(),
                    "issue": f"DUPLICATE: {guardian_count} guardian annotations on one line",
                }
            )
        elif guardian_count == 1:
            quality_err = _check_justification_quality(line)
            if quality_err:
                issues.append(
                    {
                        "file": rel_path,
                        "line_no": i,
                        "line": line.strip(),
                        "issue": f"WEAK_JUSTIFICATION: {quality_err}",
                    }
                )

    return issues


def scan_new_string(new_string: str, existing_content: str | None = None) -> list[str]:
    """
    Check if new_string introduces duplicate guardians.
    Returns list of violation messages (empty = clean).
    Used by pre_write_gate for real-time checking.
    """
    violations = []
    for line in tqdm(new_string.splitlines(), desc="Processing", unit="item"):
        count = _count_guardians_on_line(line)
        if count > 1:
            violations.append(
                f"Duplicate guardian annotations on one line ({count} found) — each line may have at most one '# guardian: allow-*'.",
            )
        elif count == 1:
            err = _check_justification_quality(line)
            if err:
                violations.append(err)

    if existing_content and new_string:
        existing_guardians: set[str] = set()
        for line in existing_content.splitlines():
            for m in _GUARDIAN_RE.finditer(line):
                existing_guardians.add(m.group(0).strip())

        for line in new_string.splitlines():
            for m in _GUARDIAN_RE.finditer(line):
                tag = m.group(0).strip()
                if tag in existing_guardians:
                    violations.append(
                        f"Duplicate guardian tag '{tag}' already exists in file — "
                        "each guardian annotation must be unique per file.",
                    )

    return violations


def scan_paths(paths: list[Path], exclude_dirs: set[str] | None = None) -> list[dict]:
    """Scan a list of file/directory paths for guardian issues."""
    if exclude_dirs is None:
        exclude_dirs = {".git", "__pycache__", "node_modules", "_archive", "archives"}

    all_issues = []
    for path in tqdm(paths, desc="Processing", unit="item"):
        if path.is_file() and path.suffix == ".py":
            all_issues.extend(scan_file(path))
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                if not any(part in exclude_dirs for part in py_file.parts):
                    all_issues.extend(scan_file(py_file))
    return all_issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Guardian Idempotency Checker (W3.6)")
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to scan")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    parser.add_argument(
        "--production-only",
        action="store_true",
        help="Only scan production dirs (agentic_core/, apps_*/, system_learning/)",
    )
    args = parser.parse_args()

    scan_targets: list[Path]
    if args.production_only:
        scan_targets = []
        for pat in ("agentic_core", "apps_*", "system_learning"):
            scan_targets.extend(ROOT.glob(pat))
    else:
        scan_targets = [Path(p) for p in args.paths]
        scan_targets = [p if p.is_absolute() else ROOT / p for p in scan_targets]

    issues = scan_paths(scan_targets)

    duplicate_count = sum(1 for i in issues if i["issue"].startswith("DUPLICATE"))
    weak_count = sum(1 for i in issues if i["issue"].startswith("WEAK"))

    if args.as_json:
        print(
            json.dumps(
                {
                    "total_issues": len(issues),
                    "duplicate_guardian_lines": duplicate_count,
                    "weak_justification_lines": weak_count,
                    "issues": issues,
                },
                indent=2,
            )
        )
    else:
        if not issues:
            print("[guardian-idempotency] Clean — no duplicate or weak guardian annotations found.")
            return

        print(
            f"[guardian-idempotency] Found {len(issues)} issues ({duplicate_count} duplicates, {weak_count} weak justifications)"
        )
        for issue in issues[:50]:
            print(f"  {issue['file']}:{issue['line_no']}  {issue['issue']}")
            print(f"    {issue['line'][:120]}")
        if len(issues) > 50:
            print(f"  ... and {len(issues) - 50} more")

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
