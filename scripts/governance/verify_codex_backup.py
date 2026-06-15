"""Verify the thin Codex backup adapter for Agentic-Workflow.

This script checks presence and anchor references only. Claude Code governance
remains authoritative; this verifier guards the Codex adapter against drift.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_SKILLS_ROOT = Path.home() / ".codex" / "skills"

REQUIRED_REPO_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "docs/codex-backup-adapter.md",
    ".claude/rules/windows-path-budget.md",
    ".claude/skills/structured-reasoning/SKILL.md",
    ".claude/skills/mcp-integration/SKILL.md",
    ".claude/skills/plan-governance/SKILL.md",
    ".mcp.json",
    ".claude/settings.json",
    "scripts/governance/check_windows_path_budget.py",
]

REQUIRED_CODEX_SKILLS = [
    "agentic-workflow-governance/SKILL.md",
    "agentic-workflow-verification/SKILL.md",
]

REQUIRED_ANCHORS = {
    "AGENTS.md": [
        "## Codex backup adapter",
        "agentic-workflow-governance",
        "scripts/governance/verify_codex_backup.py",
    ],
    "docs/codex-backup-adapter.md": [
        ".claude/rules/windows-path-budget.md",
        "scripts/governance/check_windows_path_budget.py",
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
        "native plan mode",
    ],
    "agentic-workflow-verification/SKILL.md": [
        "scripts/governance/verify_codex_backup.py",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        "verification phase",
    ],
}


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


def main() -> int:
    failures: list[str] = []

    failures.extend(str(path) for path in missing_paths(REQUIRED_REPO_FILES, REPO_ROOT))
    failures.extend(str(path) for path in missing_paths(REQUIRED_CODEX_SKILLS, CODEX_SKILLS_ROOT))

    if not failures:
        failures.extend(missing_anchors(REQUIRED_ANCHORS, REPO_ROOT))
        failures.extend(missing_anchors(REQUIRED_SKILL_ANCHORS, CODEX_SKILLS_ROOT))

    if failures:
        print("Codex backup adapter verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Codex backup adapter verification passed")
    print(f"- repo: {REPO_ROOT}")
    print(f"- codex skills: {CODEX_SKILLS_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
