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
    "adg-bcg-p2-next-action",
    "adg-p3-promotion-hygiene",
    "weekly-svp-readme-documentation-refresh",
)
AUTOMATION_DIR_BY_ID = {
    "weekly-adg-audit-and-burndown": "adg-audit-and-burndown",
    "weekly-svp-readme-documentation-refresh": "svp-readme-documentation-refresh",
}
FORBIDDEN_REPO_CODEX_TREES = (
    ".codex/automation",
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

ADG_P2_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "same released ADG receipt",
    "P0/P1 lane has proven P0/P1 clean",
    "stop and defer to the P0/P1 automation",
)

ADG_P3_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "P0/P1 is clean for the same released ADG receipt",
    "P2 lane has no safe actionable blocker",
    "P2 should remain ahead",
)

ADG_HANDOFF_SCHEMA = "adg-severity-lanes/v1"
ADG_HANDOFF_RECEIPT_PATH = "docs/reports/adg/AUDIT_PIPELINE_RECEIPT.json"
ADG_HANDOFF_VALIDATOR = (
    "python tools/adg/consume_adg_repair_handoff.py "
    "--receipt docs/reports/adg/AUDIT_PIPELINE_RECEIPT.json --json"
)
ADG_HANDOFF_STATUSES = ("certified", "repair_ready")
ADG_HANDOFF_CHAIN = (
    "weekly-adg-audit-and-burndown",
    "adg-p0-p1-burndown",
    "adg-bcg-p2-next-action",
    "adg-p3-promotion-hygiene",
)
ADG_HANDOFF_CONTRACTS = {
    "weekly-adg-audit-and-burndown": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "generate_full_adg",
        "role": "producer",
        "order": 0,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "depends_on": [],
        "unblocks": ["adg-p0-p1-burndown"],
        "requires_prior_lane_clean": [],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-p0-p1-burndown": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p0_p1_burndown",
        "role": "consumer",
        "order": 1,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "depends_on": ["weekly-adg-audit-and-burndown"],
        "unblocks": ["adg-bcg-p2-next-action"],
        "requires_prior_lane_clean": [],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-bcg-p2-next-action": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p2_next_action",
        "role": "consumer",
        "order": 2,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "depends_on": ["weekly-adg-audit-and-burndown", "adg-p0-p1-burndown"],
        "unblocks": ["adg-p3-promotion-hygiene"],
        "requires_prior_lane_clean": ["adg-p0-p1-burndown"],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-p3-promotion-hygiene": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p3_promotion_hygiene",
        "role": "consumer",
        "order": 3,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "depends_on": [
            "weekly-adg-audit-and-burndown",
            "adg-p0-p1-burndown",
            "adg-bcg-p2-next-action",
        ],
        "unblocks": [],
        "requires_prior_lane_clean": ["adg-p0-p1-burndown"],
        "requires_prior_lane_not_actionable": ["adg-bcg-p2-next-action"],
    },
}
ADG_DIRECT_HANDOFF_EDGES = (
    ("weekly-adg-audit-and-burndown", "adg-p0-p1-burndown"),
    ("adg-p0-p1-burndown", "adg-bcg-p2-next-action"),
    ("adg-bcg-p2-next-action", "adg-p3-promotion-hygiene"),
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
    automation_dir = AUTOMATION_DIR_BY_ID.get(automation_id, automation_id)
    return root / ".codex" / "automations" / automation_dir / "automation.toml"


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


def _validate_prompt_snippets(
    *,
    automation_id: str,
    prompt: str,
    snippets: tuple[str, ...],
    code: str,
) -> list[EnforcementHomeIssue]:
    issues: list[EnforcementHomeIssue] = []
    for snippet in snippets:
        if snippet not in prompt:
            issues.append(
                EnforcementHomeIssue(
                    code,
                    f"{automation_id}: prompt missing {snippet!r}",
                )
            )
    return issues


def _validate_adg_handoff_metadata(
    automation_id: str,
    data: dict[str, Any],
) -> list[EnforcementHomeIssue]:
    expected = ADG_HANDOFF_CONTRACTS.get(automation_id)
    if expected is None:
        return []
    handoff = data.get("handoff")
    if not isinstance(handoff, dict):
        return [
            EnforcementHomeIssue(
                "adg_handoff_missing",
                f"{automation_id}: missing [handoff] metadata for ADG automation chain",
            )
        ]

    issues: list[EnforcementHomeIssue] = []
    for field, expected_value in expected.items():
        actual_value = handoff.get(field)
        if actual_value != expected_value:
            issues.append(
                EnforcementHomeIssue(
                    "adg_handoff_contract",
                    f"{automation_id}: handoff.{field} expected {expected_value!r}, got {actual_value!r}",
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
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=ADG_P0_P1_REQUIRED_PROMPT_SNIPPETS,
                code="adg_p0_p1_prompt_missing",
            )
        )
    if automation_id == "adg-bcg-p2-next-action":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=ADG_P2_REQUIRED_PROMPT_SNIPPETS,
                code="adg_p2_prompt_missing",
            )
        )
    if automation_id == "adg-p3-promotion-hygiene":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=ADG_P3_REQUIRED_PROMPT_SNIPPETS,
                code="adg_p3_prompt_missing",
            )
        )
    issues.extend(_validate_adg_handoff_metadata(automation_id, data))
    return issues


def _load_automation(root: Path, automation_id: str) -> dict[str, Any] | None:
    path = _automation_path(root, automation_id)
    if not path.exists():
        return None
    data, error = _load_toml(path)
    if error is not None:
        return None
    return data


def _validate_adg_handoff_graph(root: Path) -> list[EnforcementHomeIssue]:
    loaded = {
        automation_id: _load_automation(root, automation_id)
        for automation_id in ADG_HANDOFF_CHAIN
    }
    if any(data is None for data in loaded.values()):
        return []

    issues: list[EnforcementHomeIssue] = []
    handoffs = {
        automation_id: data.get("handoff")  # type: ignore[union-attr]
        for automation_id, data in loaded.items()
    }
    if any(not isinstance(handoff, dict) for handoff in handoffs.values()):
        return issues
    orders = {
        automation_id: handoff.get("order")
        for automation_id, handoff in handoffs.items()
    }
    if any(not isinstance(order, int) for order in orders.values()):
        return issues
    observed_chain = tuple(sorted(orders, key=lambda item: orders[item]))
    if observed_chain != ADG_HANDOFF_CHAIN:
        issues.append(
            EnforcementHomeIssue(
                "adg_handoff_graph_order",
                f"ADG handoff order expected {ADG_HANDOFF_CHAIN!r}, got {observed_chain!r}",
            )
        )

    for source, target in ADG_DIRECT_HANDOFF_EDGES:
        source_handoff = handoffs[source]
        target_handoff = handoffs[target]
        if target not in source_handoff.get("unblocks", []):
            issues.append(
                EnforcementHomeIssue(
                    "adg_handoff_graph_edge",
                    f"{source}: must unblock {target}",
                )
            )
        if source not in target_handoff.get("depends_on", []):
            issues.append(
                EnforcementHomeIssue(
                    "adg_handoff_graph_edge",
                    f"{target}: must depend on {source}",
                )
            )

    for index, automation_id in enumerate(ADG_HANDOFF_CHAIN):
        if index == 0:
            continue
        prior = list(ADG_HANDOFF_CHAIN[:index])
        handoff = handoffs[automation_id]
        missing = [dependency for dependency in prior if dependency not in handoff.get("depends_on", [])]
        if missing:
            issues.append(
                EnforcementHomeIssue(
                    "adg_handoff_graph_dependency",
                    f"{automation_id}: missing prior-lane dependencies {missing!r}",
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


def _forbidden_repo_paths(root: Path) -> list[Path]:
    return [root / relative_path for relative_path in FORBIDDEN_REPO_CODEX_TREES]


def validate(root: Path = REPO_ROOT, user_codex_home: Path = DEFAULT_USER_CODEX_HOME) -> list[EnforcementHomeIssue]:
    root = root.resolve()
    user_codex_home = user_codex_home.resolve()
    issues: list[EnforcementHomeIssue] = []

    for path in _forbidden_repo_paths(root):
        if path.exists():
            issues.append(
                EnforcementHomeIssue(
                    "repo_duplicate_enforcement_home",
                    f"{path}: automation contracts must live under {root / '.codex' / 'automations'}",
                )
            )

    for automation_id in AUTOMATION_IDS:
        issues.extend(_validate_automation(root, automation_id))
    issues.extend(_validate_adg_handoff_graph(root))

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
