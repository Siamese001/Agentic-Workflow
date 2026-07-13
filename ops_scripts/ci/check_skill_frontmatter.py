#!/usr/bin/env python3
"""Validate active ``.codex/skills`` against the Agent Skills frontmatter contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.skill_contract import iter_skill_directories, validate_skill_path  # noqa: E402

SKILLS_ROOT = REPO_ROOT / ".codex" / "skills"


def evaluate_skills(skills_root: Path) -> dict[str, list[str]]:
    """Return failures keyed by skill directory name."""

    failures: dict[str, list[str]] = {}
    for skill_dir in iter_skill_directories(skills_root):
        issues = validate_skill_path(skill_dir / "SKILL.md")
        if issues:
            failures[skill_dir.name] = issues
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=SKILLS_ROOT,
        help="override the active skills directory (primarily for tests)",
    )
    args = parser.parse_args(argv)

    skills_root = args.skills_root.resolve()
    if not skills_root.is_dir():
        print(f"[skill_frontmatter] FAIL: skills root not found: {skills_root}", flush=True)
        return 1

    skill_dirs = iter_skill_directories(skills_root)
    if not skill_dirs:
        print(f"[skill_frontmatter] FAIL: no SKILL.md files under {skills_root}", flush=True)
        return 1

    failures = evaluate_skills(skills_root)
    report = {
        "status": "FAIL" if failures else "PASS",
        "skills_root": str(skills_root),
        "skills_total": len(skill_dirs),
        "skills_failed": len(failures),
        "failures": failures,
        "contract": "Agent Skills specification plus repository 500-line budget",
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif failures:
        print("[skill_frontmatter] FAIL:", flush=True)
        for name, issues in failures.items():
            print(f"  {name}/SKILL.md", flush=True)
            for issue in issues:
                print(f"    - {issue}", flush=True)
    else:
        print(
            f"[skill_frontmatter] OK: {len(skill_dirs)} active skills satisfy the "
            "frontmatter contract.",
            flush=True,
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
