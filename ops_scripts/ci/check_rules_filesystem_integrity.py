#!/usr/bin/env python3
"""
check_rules_filesystem_integrity.py — CI gate for .claude/rules/ validation.

Validates:
1. All .md files in .claude/rules/ have frontmatter (--- delimited)
2. No duplicate rule titles (based on first h1 heading)
3. File names follow kebab-case convention
4. All internal references in rules point to valid files

Advisory by default. Fail-closed: RULES_INTEGRITY_FAIL_CLOSED=1
Bypass: RULES_INTEGRITY_BYPASS=1

Registered in run_contract_gates.py as "RULES1 Rules filesystem integrity (advisory)".
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

def _find_repo_root() -> Path:
    """Find repo root from script location or CWD."""
    # Try script location first (parents[3] from ops_scripts/ci/)
    script_root = Path(__file__).resolve().parents[3]
    if (script_root / ".claude" / "rules").exists():
        return script_root
    # Fall back to CWD
    cwd = Path.cwd()
    if (cwd / ".claude" / "rules").exists():
        return cwd
    # Last resort: try to find by walking up from CWD
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude" / "rules").exists():
            return parent
    # Known repo location (when running in Windsurf environment)
    known_path = Path("C:/Git/Agentic-Workflow-FRESH")
    if (known_path / ".claude" / "rules").exists():
        return known_path
    return script_root  # Default to script-based root


REPO_ROOT = _find_repo_root()
RULES_DIR = REPO_ROOT / ".claude" / "rules"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "ci" / "rules_integrity_gate.json"

# Kebab-case pattern: lowercase, hyphens, numbers, no leading hyphen
KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9-]*\.md$")

# Frontmatter delimiter
FRONTMATTER_RE = re.compile(r"^---\s*$", re.MULTILINE)

# First h1 heading: # Title
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

# Internal rule references: `rule-name.md` or @.claude/rules/rule-name.md
RULE_REF_RE = re.compile(r"[@`]\.claude/rules/([a-z0-9-]+\.md)`|([a-z0-9-]+\.md)`")


def _log_event(event: dict[str, Any]) -> None:
    """Append to JSONL log (fail-soft)."""
    try:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
            json.dump(event, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _has_frontmatter(content: str) -> bool:
    """Check for YAML frontmatter delimited by ---."""
    matches = FRONTMATTER_RE.findall(content)
    return len(matches) >= 2


def _extract_title(content: str, filepath: Path) -> str | None:
    """Extract first h1 heading as title."""
    m = H1_RE.search(content)
    if m:
        return m.group(1).strip()
    # Fallback to filename without extension
    return filepath.stem.replace("-", " ").title()


def _check_kebab_case(filename: str) -> bool:
    """Verify filename follows kebab-case convention."""
    return KEBAB_CASE_RE.match(filename) is not None


def _find_rule_references(content: str) -> list[str]:
    """Find all rule file references in content."""
    refs = []
    for m in RULE_REF_RE.finditer(content):
        ref = m.group(1) or m.group(2)
        if ref:
            refs.append(ref)
    return refs


def main() -> int:
    if os.environ.get("RULES_INTEGRITY_BYPASS") == "1":
        _log_event({"status": "bypass", "checks": []})
        print("[RULES1] BYPASS: RULES_INTEGRITY_BYPASS=1 set")
        return 0

    if not RULES_DIR.exists():
        _log_event({"status": "error", "reason": "rules_dir_missing", "path": str(RULES_DIR)})
        print(f"[RULES1] ERROR: Rules directory not found: {RULES_DIR}")
        return 0 if not os.environ.get("RULES_INTEGRITY_FAIL_CLOSED") == "1" else 1

    findings: list[dict[str, Any]] = []
    titles: dict[str, Path] = {}
    exit_code = 0

    for md_file in sorted(RULES_DIR.glob("*.md")):
        check_result = {
            "file": md_file.name,
            "path": str(md_file.relative_to(REPO_ROOT)),
            "errors": [],
            "warnings": [],
        }

        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            check_result["errors"].append(f"read_failed: {exc}")
            findings.append(check_result)
            exit_code = 1
            continue

        # Check 1: Frontmatter
        if not _has_frontmatter(content):
            check_result["warnings"].append("missing_frontmatter")

        # Check 2: Title uniqueness
        title = _extract_title(content, md_file)
        if title:
            if title in titles:
                check_result["errors"].append(
                    f"duplicate_title: '{title}' also in {titles[title].name}"
                )
                exit_code = 1
            else:
                titles[title] = md_file

        # Check 3: Kebab-case filename
        if not _check_kebab_case(md_file.name):
            check_result["errors"].append(
                f"invalid_filename: {md_file.name} (expected kebab-case.md)"
            )
            exit_code = 1

        # Check 4: Internal references
        refs = _find_rule_references(content)
        for ref in refs:
            ref_path = RULES_DIR / ref
            if not ref_path.exists():
                check_result["errors"].append(f"broken_ref: {ref} not found")
                exit_code = 1

        if check_result["errors"] or check_result["warnings"]:
            findings.append(check_result)

    # Summary
    error_count = sum(len(f["errors"]) for f in findings)
    warning_count = sum(len(f["warnings"]) for f in findings)

    result = {
        "status": "fail" if exit_code else "pass",
        "files_checked": len(list(RULES_DIR.glob("*.md"))),
        "error_count": error_count,
        "warning_count": warning_count,
        "findings": findings,
    }
    _log_event(result)

    # Output
    severity = "ERROR" if exit_code else "OK"
    print(
        f"[RULES1] {severity}: {result['files_checked']} rules checked, "
        f"{error_count} errors, {warning_count} warnings"
    )
    for f in findings:
        for err in f["errors"]:
            print(f"  [ERROR] {f['file']}: {err}")
        for warn in f["warnings"]:
            print(f"  [WARN] {f['file']}: {warn}")

    if os.environ.get("RULES_INTEGRITY_FAIL_CLOSED") == "1" and exit_code:
        print("[RULES1] FAIL-CLOSED: Exiting with error due to RULES_INTEGRITY_FAIL_CLOSED=1")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
