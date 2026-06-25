r"""Verify Agentic-Workflow Codex enforcement lives under the repository.

This guard is intentionally narrow. It does not inspect the whole Codex app
profile because the desktop app owns runtime config, plugin caches, and session
state there. It only rejects Agentic-Workflow enforcement artifacts that must
be versioned from the repo under ``C:\Git``.
"""

from __future__ import annotations

import argparse
import json
import os
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_USER_CODEX_HOME = Path(os.environ.get("CODEX_HOME", r"C:\Users\amita\.codex"))

EXPECTED_REPO = Path(r"C:\Git\Agentic-Workflow-FRESH")
AUTOMATION_IDS = (
    "on-demand-pr-main-publisher",
    "weekly-adg-audit-and-burndown",
    "adg-p0-p1-burndown",
)
# Codex app deployment records live under CODEX_HOME/automations. This guard
# only rejects legacy repo-source copies that were historically misplaced there.
FORBIDDEN_USER_PROFILE_AUTOMATION_IDS = (
    "on-demand-pr-main-publisher",
    "weekly-adg-audit-and-burndown",
)
REPO_SKILL_IDS = ("agentic-workflow-governance", "agentic-workflow-verification")

PUBLICATION_REQUIRED_PROMPT_SNIPPETS = (
    "HEAD == origin/main",
    "git status --short --branch shows only ## main...origin/main",
    "git diff --stat has no output",
    "git diff --cached --stat has no output",
    "exactly one git worktree remains",
    "proof table with columns requirement, runtime evidence, and result",
    "codex_main_closeout.py --apply --fetch --json",
    "codex_main_closeout.py --check --fetch --json",
    "The merge command must chain local closeout proof in the same shell command",
    "codex_readiness.py --git-publication --require-single-main-worktree",
    "codex_publication_audit.py --json --branch-limit 100 --require-ancestor-cleanup --require-single-main-worktree",
    "strict single-main and strict publication readiness gates PASS",
    "keep working the remediation loop until every required gate passes",
)
PUBLICATION_FORBIDDEN_PROMPT_SNIPPETS = (
    "dirty protected worktrees reported and preserved",
    "retained dirty worktrees",
    "preserved dirty worktrees",
)

ADG_REQUIRED_PROMPT_SNIPPETS = (
    "clean main-branch state",
    "python tools/adg/run_full_adg_audit.py --mode certification --format both --continue-on-p0",
    "artifact_status",
    "repair_ready",
    "RCA block",
)

ADG_P0_P1_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "Burn down all P0 FIX queue/report items first",
    "Only after P0 FIX is zero",
    "Never consume overwritten latest files as the source of truth",
    "P1 reaches 0 before 4:00 AM",
    "Mandatory burndown tale",
)


@dataclass(frozen=True)
class EnforcementHomeIssue:
    code: str
    detail: str


def _norm_path(path: str | Path) -> str:
    return str(Path(path)).replace("/", "\\").rstrip("\\").casefold()


def _load_toml(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, str(exc)
    except tomllib.TOMLDecodeError as exc:
        return None, str(exc)


def _automation_path(root: Path, automation_id: str) -> Path:
    return root / ".codex" / "automations" / automation_id / "automation.toml"


def _validate_common_automation(
    *,
    root: Path,
    automation_id: str,
    data: dict[str, Any],
) -> list[EnforcementHomeIssue]:
    issues: list[EnforcementHomeIssue] = []
    if data.get("id") != automation_id:
        issues.append(
            EnforcementHomeIssue(
                "automation_id",
                f"{automation_id}: expected id {automation_id!r}, got {data.get('id')!r}",
            )
        )
    if data.get("kind") != "cron":
        issues.append(EnforcementHomeIssue("automation_kind", f"{automation_id}: kind must be 'cron'"))
    if data.get("status") != "ACTIVE":
        issues.append(EnforcementHomeIssue("automation_status", f"{automation_id}: status must be ACTIVE"))

    cwds = data.get("cwds")
    expected_root = _norm_path(root)
    if not isinstance(cwds, list) or expected_root not in {_norm_path(str(item)) for item in cwds}:
        issues.append(
            EnforcementHomeIssue(
                "automation_cwd",
                f"{automation_id}: cwds must include {root}",
            )
        )
    return issues


def _validate_publication_prompt(automation_id: str, prompt: str) -> list[EnforcementHomeIssue]:
    issues: list[EnforcementHomeIssue] = []
    for snippet in PUBLICATION_REQUIRED_PROMPT_SNIPPETS:
        if snippet not in prompt:
            issues.append(
                EnforcementHomeIssue(
                    "publication_prompt_missing",
                    f"{automation_id}: prompt missing {snippet!r}",
                )
            )
    lowered = prompt.casefold()
    for snippet in PUBLICATION_FORBIDDEN_PROMPT_SNIPPETS:
        if snippet.casefold() in lowered:
            issues.append(
                EnforcementHomeIssue(
                    "publication_prompt_obsolete",
                    f"{automation_id}: prompt contains obsolete success wording {snippet!r}",
                )
            )
    return issues


def _validate_adg_prompt(automation_id: str, prompt: str) -> list[EnforcementHomeIssue]:
    issues: list[EnforcementHomeIssue] = []
    for snippet in ADG_REQUIRED_PROMPT_SNIPPETS:
        if snippet not in prompt:
            issues.append(
                EnforcementHomeIssue(
                    "adg_prompt_missing",
                    f"{automation_id}: prompt missing {snippet!r}",
                )
            )
    return issues


def _validate_automation(root: Path, automation_id: str) -> list[EnforcementHomeIssue]:
    path = _automation_path(root, automation_id)
    if not path.exists():
        return [EnforcementHomeIssue("automation_missing", f"{path}: missing repo-owned automation TOML")]

    data, error = _load_toml(path)
    if data is None:
        return [EnforcementHomeIssue("automation_toml_invalid", f"{path}: {error}")]

    issues = _validate_common_automation(root=root, automation_id=automation_id, data=data)
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        issues.append(EnforcementHomeIssue("automation_prompt", f"{automation_id}: prompt must be non-empty text"))
        return issues
    if automation_id == "on-demand-pr-main-publisher":
        issues.extend(_validate_publication_prompt(automation_id, prompt))
    if automation_id == "weekly-adg-audit-and-burndown":
        issues.extend(_validate_adg_prompt(automation_id, prompt))
    if automation_id == "adg-p0-p1-burndown":
        for snippet in ADG_P0_P1_REQUIRED_PROMPT_SNIPPETS:
            if snippet not in prompt:
                issues.append(
                    EnforcementHomeIssue(
                        "adg_p0_p1_prompt_missing",
                        f"{automation_id}: prompt missing {snippet!r}",
                    )
                )
    return issues


def _forbidden_user_profile_paths(user_codex_home: Path) -> list[Path]:
    paths: list[Path] = []
    paths.extend(
        user_codex_home / "automations" / automation_id / "automation.toml"
        for automation_id in FORBIDDEN_USER_PROFILE_AUTOMATION_IDS
    )
    paths.extend(user_codex_home / "skills" / skill_id / "SKILL.md" for skill_id in REPO_SKILL_IDS)
    return paths


def validate(root: Path = REPO_ROOT, user_codex_home: Path = DEFAULT_USER_CODEX_HOME) -> list[EnforcementHomeIssue]:
    root = root.resolve()
    user_codex_home = user_codex_home.resolve()
    issues: list[EnforcementHomeIssue] = []

    for automation_id in AUTOMATION_IDS:
        issues.extend(_validate_automation(root, automation_id))

    for skill_id in REPO_SKILL_IDS:
        skill_path = root / ".codex" / "skills" / skill_id / "SKILL.md"
        if not skill_path.exists():
            issues.append(EnforcementHomeIssue("repo_skill_missing", f"{skill_path}: missing repo-owned skill"))

    for path in _forbidden_user_profile_paths(user_codex_home):
        if path.exists():
            issues.append(
                EnforcementHomeIssue(
                    "user_profile_enforcement_artifact",
                    f"{path}: Agentic-Workflow enforcement must live under {root}",
                )
            )

    return issues


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to verify")
    parser.add_argument(
        "--user-codex-home",
        type=Path,
        default=DEFAULT_USER_CODEX_HOME,
        help="User-profile Codex home to reject for Agentic-Workflow enforcement artifacts",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    issues = validate(args.root, args.user_codex_home)
    status = "FAIL" if issues else "PASS"
    report = {
        "schema_version": "codex-enforcement-home/v1",
        "status": status,
        "repo_root": str(args.root.resolve()),
        "user_codex_home": str(args.user_codex_home.resolve()),
        "issues": [asdict(issue) for issue in issues],
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"codex-enforcement-home: {status}")
        for issue in issues:
            print(f"- {issue.code}: {issue.detail}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
