"""Verify the legacy Codex compatibility adapter for Agentic-Workflow.

Codex primary verification is repo-owned and does not depend on personal skills.
This compatibility verifier guards repo anchors and hook targets. Personal
Codex skills are bootstrap shims, so missing or drifted skill files are advisory
by default and strict only when --require-personal-skills is supplied.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections.abc import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_SKILLS_ROOT = Path.home() / ".codex" / "skills"

REQUIRED_REPO_FILES = [
    "AGENTS.md",
    "docs/codex-backup-adapter.md",
    ".claude/rules/001-runtime-seam-execution.md",
    ".claude/rules/002-pass-blocked-proof-contract.md",
    ".claude/rules/plan-first-enforcement.md",
    ".claude/rules/plan-location.md",
    ".claude/rules/windows-path-budget.md",
    ".claude/skills/structured-reasoning/SKILL.md",
    ".claude/skills/mcp-integration/SKILL.md",
    ".claude/templates/execution-plan-template.md",
    ".mcp.json",
    ".claude/mcp-notes.md",
    ".claude/settings.json",
    "scripts/governance/check_windows_path_budget.py",
    "scripts/governance/audit_codex_mcp_transports.py",
]

REQUIRED_CODEX_SKILLS = [
    "agentic-workflow-governance/SKILL.md",
    "agentic-workflow-verification/SKILL.md",
]

REQUIRED_ANCHORS = {
    "AGENTS.md": [
        "## Codex backup adapter",
        "legacy compatibility files are not consulted by the primary path",
        "agentic-workflow-governance",
        "scripts/governance/verify_codex_backup.py",
        ".claude/rules/plan-first-enforcement.md",
        ".claude/rules/plan-location.md",
    ],
    "docs/codex-backup-adapter.md": [
        ".claude/rules/windows-path-budget.md",
        ".claude/rules/plan-first-enforcement.md",
        ".claude/rules/plan-location.md",
        ".claude/templates/execution-plan-template.md",
        "scripts/governance/check_windows_path_budget.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        ".claude/skills/structured-reasoning/SKILL.md",
        ".claude/skills/mcp-integration/SKILL.md",
        "agentic-workflow-verification",
    ],
}

REQUIRED_SKILL_ANCHORS = {
    "agentic-workflow-governance/SKILL.md": [
        ".claude/rules/windows-path-budget.md",
        "scripts/governance/check_windows_path_budget.py",
        ".claude/skills/structured-reasoning/SKILL.md",
        ".claude/skills/mcp-integration/SKILL.md",
        ".claude/rules/plan-first-enforcement.md",
        ".claude/rules/plan-location.md",
        "native plan mode",
    ],
    "agentic-workflow-verification/SKILL.md": [
        "scripts/governance/verify_codex_backup.py",
        "AGENTS.md",
        "verification phase",
    ],
}

FORBIDDEN_ACTIVE_REFS = [
    ".claude/skills/plan-governance/SKILL.md",
    ".cursor/skills/testing-framework/SKILL.md",
]


def missing_paths(paths: list[str], root: Path) -> list[Path]:
    return [root / path for path in paths if not (root / path).exists()]


def missing_anchors(anchor_map: dict[str, list[str]], root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, anchors in anchor_map.items():
        path = root / relative_path
        text = path.read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                failures.append(f"{path}: missing anchor {anchor!r}")
    return failures


def stale_active_refs(paths: list[str], root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in paths:
        path = root / relative_path
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_ACTIVE_REFS:
            if forbidden in text:
                failures.append(f"{path}: stale active reference {forbidden!r}")
    return failures


def hook_target_failures(settings_path: Path) -> list[str]:
    failures: list[str] = []
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    for event, groups in settings.get("hooks", {}).items():
        for group in groups:
            matcher = group.get("matcher", "*")
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                matches = re.findall(r"\$CLAUDE_PROJECT_DIR/([^\"\s]+)", command)
                if not matches and "$CLAUDE_PROJECT_DIR" in command:
                    failures.append(f"{settings_path}: could not parse hook target for {event}/{matcher}: {command}")
                    continue
                for relative_target in matches:
                    target = REPO_ROOT / relative_target
                    if not target.exists():
                        failures.append(f"{settings_path}: missing hook target for {event}/{matcher}: {target}")
    return failures


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-only",
        action="store_true",
        help="Skip personal Codex skill checks entirely. Intended for CI.",
    )
    parser.add_argument(
        "--require-personal-skills",
        action="store_true",
        help="Fail if personal Codex bootstrap skills are missing or drifted.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures: list[str] = []
    warnings: list[str] = []

    failures.extend(str(path) for path in missing_paths(REQUIRED_REPO_FILES, REPO_ROOT))

    if not failures:
        failures.extend(missing_anchors(REQUIRED_ANCHORS, REPO_ROOT))
        failures.extend(stale_active_refs(list(REQUIRED_ANCHORS), REPO_ROOT))
        failures.extend(hook_target_failures(REPO_ROOT / ".claude/settings.json"))

    skill_issues: list[str] = []
    if not args.repo_only:
        skill_issues.extend(str(path) for path in missing_paths(REQUIRED_CODEX_SKILLS, CODEX_SKILLS_ROOT))
        if not skill_issues:
            skill_issues.extend(missing_anchors(REQUIRED_SKILL_ANCHORS, CODEX_SKILLS_ROOT))
            skill_issues.extend(stale_active_refs(list(REQUIRED_SKILL_ANCHORS), CODEX_SKILLS_ROOT))
        if args.require_personal_skills:
            failures.extend(skill_issues)
        else:
            warnings.extend(skill_issues)

    if failures:
        print("Codex backup adapter verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Codex backup adapter verification passed")
    print(f"- repo: {REPO_ROOT}")
    if args.repo_only:
        print("- codex skills: skipped (--repo-only)")
    elif args.require_personal_skills:
        print(f"- codex skills: strict check passed at {CODEX_SKILLS_ROOT}")
    else:
        print(f"- codex skills: advisory check at {CODEX_SKILLS_ROOT}")
        if warnings:
            print("Codex skill advisory warnings:")
            for warning in warnings:
                print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
