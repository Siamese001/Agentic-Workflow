r"""Verify Agentic-Workflow Codex enforcement lives under the repository.

This guard is intentionally narrow. It does not inspect the whole Codex app
profile because the desktop app owns runtime config, plugin caches, and session
state there. It only rejects Agentic-Workflow enforcement artifacts that must
be versioned from the repo under ``C:\Git``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_USER_CODEX_HOME = Path(os.environ.get("CODEX_HOME", r"C:\Users\amita\.codex"))

EXPECTED_REPO = Path(r"C:\Git\Agentic-Workflow-FRESH")
AUTOMATION_IDS = (
    "on-demand-pr-main-publisher",
    "on-demand-apps-rg-anthropic-partnership-fresh-s2e",
    "weekly-adg-audit-and-burndown",
    "adg-p0-blocker-burndown",
    "adg-p1-ratchet-burndown",
    "adg-bcg-p2-next-action",
    "adg-p3-promotion-hygiene",
    "weekly-svp-readme-documentation-refresh",
)
AUTOMATION_DIR_BY_ID = {
    "weekly-adg-audit-and-burndown": "adg-audit-and-burndown",
    "weekly-svp-readme-documentation-refresh": "svp-readme-documentation-refresh",
}
FORBIDDEN_REPO_CODEX_TREES = (
    ".codex/agent-instructions",
    ".codex/automation",
)
FORBIDDEN_REPO_ENFORCEMENT_TREES = {
    ".agents": "Agentic-Workflow skills must live under .codex/skills; root .agents is not a Codex SSOT",
    "memory/codex/skills": "memory/codex may reference skills, but must not host SKILL.md execution surfaces",
}
ALLOWED_CODEX_PLAN_TOP_LEVEL_FILES = {"README.md"}
FORBIDDEN_SCHEMA_AUTHORITY_REF_RE = re.compile(
    r"SSOT:\s+\.cursor|Location:\s+\.cursor|Applied by:\s+\.cursor|"
    r"\.cursor/(?:scripts|schemas|skills)|\.windsurf/(?:plans|rules)",
    re.IGNORECASE,
)
MANUAL_AUTOMATION_IDS = (
    "on-demand-pr-main-publisher",
    "on-demand-apps-rg-anthropic-partnership-fresh-s2e",
)
USER_PROFILE_REPO_AUTOMATION_IDS = AUTOMATION_IDS + (
    "on-demand-pr-main-publisher-2",
)
REPO_SKILL_IDS = ("agentic-workflow-governance", "agentic-workflow-verification")
AUTOMATION_PROJECTION_SCHEMA = "agentic-workflow-codex-automation-ui-mirror/v1"
AUTOMATION_PROJECTION_FIELDS = (
    "schema",
    "projection_kind",
    "automation_id",
    "enabled",
    "repo_root",
    "contract_path",
    "contract_sha256",
    "id",
    "kind",
    "name",
    "prompt",
    "status",
    "rrule",
    "model",
    "reasoning_effort",
    "execution_environment",
    "cwds",
)
USER_PROFILE_FORBIDDEN_AUTOMATION_FIELDS = (
    "runtime_optimization",
    "handoff",
)

PUBLICATION_REQUIRED_PROMPT_SNIPPETS = (
    "Capture one state snapshot per phase and reuse it until a mutation changes git, PR, CI, or worktree state",
    "Read-only commands may enrich the current evidence packet, but they must not trigger a full re-audit by themselves",
    "If git branch --no-merged origin/main is empty, record that empty output and skip deep prior-branch inspection",
    "Run local validation once per committed tree",
    "Dirty preservation is not publication; incoherent, local_or_config_scope, and unsafe_or_unknown_scope files must be stashed or retained, not merged to main.",
    "Do not reuse a head branch that already had a merged or closed PR unless this run is explicitly an ancestry-recording PR.",
    "Do not publish generated ADG reports or ratchet baselines unless the source generator changed and regeneration proof is included.",
    "Run strict workspace topology closeout after publication proof",
    "Capture the PR headRefOid and watch only checks/runs for that exact SHA",
    "Prefer gh pr checks <number> --watch --fail-fast",
    "Before merge, block on unresolved GitHub review threads with P1 or P2 findings for the PR head.",
    "Run codex_main_closeout.py --apply --fetch --json --publication-only once after PR merge",
    "HEAD == origin/main",
    "git status --short --branch shows only ## main...origin/main",
    "git diff --stat has no output",
    "git diff --cached --stat has no output",
    "publication_closeout.status PASS",
    "proof table with columns requirement, runtime evidence, and result",
    "codex_main_closeout.py --apply --fetch --json",
    "codex_main_closeout.py --check --fetch --json",
    "The merge command must chain publication closeout proof in the same shell command",
    "codex_readiness.py --git-publication --require-publication-closeout",
    "codex_publication_audit.py --json --branch-limit 100 --require-ancestor-cleanup --require-publication-closeout",
    "publication readiness with --require-publication-closeout PASS",
    "workspace_topology_closeout.status PASS or retained-worktree RCA",
)
PUBLICATION_FORBIDDEN_PROMPT_SNIPPETS = (
    "dirty protected worktrees reported and preserved",
    "retained dirty worktrees",
    "preserved dirty worktrees",
    "commit all non-disposable dirty files there",
    "push it, publish it through a GitHub PR, merge it into main after green checks",
)
PUBLICATION_RUNTIME_OPTIMIZATION_CONTRACT = {
    "schema": "publisher-runtime-optimization/v1",
    "snapshot_granularity": "phase",
    "rerun_policy": "mutation_triggered",
    "strict_single_main_phase": "post_merge",
    "ci_watch_mode": "pr_checks_watch_fail_fast",
    "ci_identity_field": "headRefOid",
    "skip_deep_branch_inspection_when_no_unmerged": True,
    "local_validation_cache_key": "tree_hash",
    "closeout_apply_check_policy": "once_then_repeat_after_remediation",
    "broad_run_list_policy": "only_when_checks_missing_or_ambiguous",
    "evidence_packet_required": True,
    "mutation_events": [
        "stash",
        "restore",
        "commit",
        "cherry_pick",
        "merge",
        "rebase",
        "branch_create_delete",
        "worktree_add_remove",
        "push",
        "pr_create_update_merge_close",
        "ci_rerun",
        "closeout_cleanup_apply",
    ],
}

ADG_REQUIRED_PROMPT_SNIPPETS = (
    "clean main-branch state",
    "python tools/adg/run_full_adg_audit.py --mode certification --format both --continue-on-p0",
    "artifact_status",
    "repair_ready",
    "downstream_release_status=released",
    "RCA block",
)

ADG_P0_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "P0=0 before merge",
    "Burn down all P0 FIX queue/report items first",
    "If P0_FIX=0 and P0_WAVE>0",
    "Never consume overwritten latest files as source of truth",
    "Use a non-squash merge method. Do not squash.",
    "codex_main_closeout.py --check --fetch --json",
)

ADG_P1_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "fresh post-P0 full ADG receipt proving P0=0",
    "ordinary_p1_target = current_ordinary_p1_count",
    "ratchet_target = max(25 rows, ceil(selected_gate_rows * 0.05))",
    "Use a non-squash merge method. Do not squash.",
    "codex_main_closeout.py --check --fetch --json",
)

ADG_P2_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "same released ADG receipt",
    "P0 blocker lane has proven P0=0",
    "P1 ratchet lane has met its target",
)

ADG_P3_REQUIRED_PROMPT_SNIPPETS = (
    "artifact_status=certified or artifact_status=repair_ready",
    "P0=0",
    "P1 ratchet lane has met its target",
    "P2 lane has no safe actionable blocker",
    "P2 should remain ahead",
)

SVP_DOCS_REQUIRED_PROMPT_SNIPPETS = (
    "svp_docs_x1d/v1",
    "svp_docs_x2/v1",
    "svp_docs_x3/v1",
    "Every blocking X1D finding must include file, line, claim, finding_type, severity, evidence, and required_fix",
    "x2_architecture_status_consistency",
    "x2_claim_evidence_map",
    "x2_proof_command_resolves",
    "x2_receipt_schema_validate",
    "x2_approval_mode",
    "x2_no_absolute_unproven_language",
    "PLAN_ONLY",
    "ALLOW_TO_PR",
    "ESCALATE_HUMAN",
    "X1D decides whether the docs read like serious SVP/CTO engineering material",
    "X2 decides whether the docs are mechanically true, scoped, current, and safe",
    "X3 decides whether this weekly Codex run may publish, must stop at plan, or must block",
    "Eval never waives a runtime or publication gate",
)
APPS_RG_S2E_REQUIRED_PROMPT_SNIPPETS = (
    "Run the Agentic-Workflow apps_rg Anthropic partnership fresh source-to-end E2E",
    "python -m apps_rg --target-company \"Anthropic\"",
    "--target-role \"Manager of Applied AI Architecture, Partnerships\"",
    "--target-level \"Manager\"",
    "--jd apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt",
    "--manual-brief apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md",
    "artifacts/apps_rg/runs/on_demand_anthropic_partnership_fresh_s2e",
    "BCG_EXECUTIVE_OUTPUT.md",
    "APPS_RG_MANDATORY_RUN_OUTPUT.md",
    "APPS_RG_MANDATORY_RUN_OUTPUT.json",
    "python tools/apps_rg/render_run_summary.py <run_dir>",
    "Do not reschedule, enable, or convert this automation to recurring active mode",
    "Do not claim success from process exit alone",
)

ADG_HANDOFF_SCHEMA = "adg-severity-lanes/v1"
ADG_HANDOFF_RECEIPT_PATH = "docs/reports/adg/AUDIT_PIPELINE_RECEIPT.json"
ADG_HANDOFF_POINTER_PATH = "artifacts/adg/handoffs/adg_repair_handoff_latest.json"
ADG_HANDOFF_VALIDATOR = (
    "python tools/adg/consume_adg_repair_handoff.py "
    "--handoff-pointer artifacts/adg/handoffs/adg_repair_handoff_latest.json --json"
)
ADG_HANDOFF_STATUSES = ("certified", "repair_ready")
ADG_HANDOFF_CHAIN = (
    "weekly-adg-audit-and-burndown",
    "adg-p0-blocker-burndown",
    "adg-p1-ratchet-burndown",
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
        "handoff_pointer_path": ADG_HANDOFF_POINTER_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "requires_digest_bound_handoff_pointer": True,
        "depends_on": [],
        "unblocks": ["adg-p0-blocker-burndown"],
        "requires_prior_lane_clean": [],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-p0-blocker-burndown": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p0_blocker_burndown",
        "role": "consumer",
        "order": 1,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "handoff_pointer_path": ADG_HANDOFF_POINTER_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "requires_digest_bound_handoff_pointer": True,
        "depends_on": ["weekly-adg-audit-and-burndown"],
        "unblocks": ["adg-p1-ratchet-burndown"],
        "requires_prior_lane_clean": [],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-p1-ratchet-burndown": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p1_ratchet_burndown",
        "role": "consumer",
        "order": 2,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "handoff_pointer_path": ADG_HANDOFF_POINTER_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "requires_digest_bound_handoff_pointer": True,
        "depends_on": ["weekly-adg-audit-and-burndown", "adg-p0-blocker-burndown"],
        "unblocks": ["adg-bcg-p2-next-action"],
        "requires_prior_lane_clean": ["adg-p0-blocker-burndown"],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-bcg-p2-next-action": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p2_next_action",
        "role": "consumer",
        "order": 3,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "handoff_pointer_path": ADG_HANDOFF_POINTER_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "requires_digest_bound_handoff_pointer": True,
        "depends_on": [
            "weekly-adg-audit-and-burndown",
            "adg-p0-blocker-burndown",
            "adg-p1-ratchet-burndown",
        ],
        "unblocks": ["adg-p3-promotion-hygiene"],
        "requires_prior_lane_clean": ["adg-p0-blocker-burndown", "adg-p1-ratchet-burndown"],
        "requires_prior_lane_not_actionable": [],
    },
    "adg-p3-promotion-hygiene": {
        "chain": ADG_HANDOFF_SCHEMA,
        "lane": "p3_promotion_hygiene",
        "role": "consumer",
        "order": 4,
        "producer_id": "weekly-adg-audit-and-burndown",
        "receipt_path": ADG_HANDOFF_RECEIPT_PATH,
        "handoff_pointer_path": ADG_HANDOFF_POINTER_PATH,
        "validator": ADG_HANDOFF_VALIDATOR,
        "consumable_artifact_statuses": list(ADG_HANDOFF_STATUSES),
        "requires_direct_artifact_status_source": True,
        "requires_digest_bound_handoff_pointer": True,
        "depends_on": [
            "weekly-adg-audit-and-burndown",
            "adg-p0-blocker-burndown",
            "adg-p1-ratchet-burndown",
            "adg-bcg-p2-next-action",
        ],
        "unblocks": [],
        "requires_prior_lane_clean": ["adg-p0-blocker-burndown", "adg-p1-ratchet-burndown"],
        "requires_prior_lane_not_actionable": ["adg-bcg-p2-next-action"],
    },
}
ADG_DIRECT_HANDOFF_EDGES = (
    ("weekly-adg-audit-and-burndown", "adg-p0-blocker-burndown"),
    ("adg-p0-blocker-burndown", "adg-p1-ratchet-burndown"),
    ("adg-p1-ratchet-burndown", "adg-bcg-p2-next-action"),
    ("adg-bcg-p2-next-action", "adg-p3-promotion-hygiene"),
)


@dataclass(frozen=True)
class EnforcementHomeIssue:
    code: str
    detail: str


def _norm_path(path: str | Path) -> str:
    return str(Path(path)).replace("/", "\\").rstrip("\\").casefold()


def _git_common_repo_root(root: Path) -> Path | None:
    """Return the primary repository root for a linked worktree when provable."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    common_dir = proc.stdout.strip()
    if not common_dir:
        return None
    path = Path(common_dir)
    if path.name.casefold() != ".git":
        return None
    return path.parent.resolve()


def _allowed_automation_cwd_roots(root: Path) -> set[str]:
    allowed = {_norm_path(root)}
    common_root = _git_common_repo_root(root)
    if common_root is not None:
        allowed.add(_norm_path(common_root))
    return allowed


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
    manual = automation_id in MANUAL_AUTOMATION_IDS
    expected_kind = "manual" if manual else "cron"
    expected_status = "ON_DEMAND" if manual else "ACTIVE"
    if data.get("id") != automation_id:
        issues.append(
            EnforcementHomeIssue(
                "automation_id",
                f"{automation_id}: expected id {automation_id!r}, got {data.get('id')!r}",
            )
        )
    if data.get("kind") != expected_kind:
        issues.append(
            EnforcementHomeIssue(
                "automation_kind",
                f"{automation_id}: kind must be {expected_kind!r}",
            )
        )
    if data.get("status") != expected_status:
        issues.append(
            EnforcementHomeIssue(
                "automation_status",
                f"{automation_id}: status must be {expected_status}",
            )
        )
    if manual and "rrule" in data:
        issues.append(EnforcementHomeIssue("automation_rrule", f"{automation_id}: manual automation must not have rrule"))

    cwds = data.get("cwds")
    allowed_roots = _allowed_automation_cwd_roots(root)
    if not isinstance(cwds, list) or not allowed_roots.intersection({_norm_path(str(item)) for item in cwds}):
        issues.append(
            EnforcementHomeIssue(
                "automation_cwd",
                f"{automation_id}: cwds must include {root} or this worktree's canonical repo root",
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


def _validate_publication_runtime_optimization(
    automation_id: str,
    data: dict[str, Any],
) -> list[EnforcementHomeIssue]:
    runtime = data.get("runtime_optimization")
    if not isinstance(runtime, dict):
        return [
            EnforcementHomeIssue(
                "publication_runtime_optimization_missing",
                f"{automation_id}: missing [runtime_optimization] metadata",
            )
        ]

    issues: list[EnforcementHomeIssue] = []
    for field, expected_value in PUBLICATION_RUNTIME_OPTIMIZATION_CONTRACT.items():
        actual_value = runtime.get(field)
        if actual_value != expected_value:
            issues.append(
                EnforcementHomeIssue(
                    "publication_runtime_optimization_contract",
                    f"{automation_id}: runtime_optimization.{field} expected {expected_value!r}, got {actual_value!r}",
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
        issues.extend(_validate_publication_runtime_optimization(automation_id, data))
    if automation_id == "on-demand-apps-rg-anthropic-partnership-fresh-s2e":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=APPS_RG_S2E_REQUIRED_PROMPT_SNIPPETS,
                code="apps_rg_s2e_prompt_missing",
            )
        )
    if automation_id == "weekly-adg-audit-and-burndown":
        issues.extend(_validate_adg_prompt(automation_id, prompt))
    if automation_id == "adg-p0-blocker-burndown":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=ADG_P0_REQUIRED_PROMPT_SNIPPETS,
                code="adg_p0_prompt_missing",
            )
        )
    if automation_id == "adg-p1-ratchet-burndown":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=ADG_P1_REQUIRED_PROMPT_SNIPPETS,
                code="adg_p1_prompt_missing",
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
    if automation_id == "weekly-svp-readme-documentation-refresh":
        issues.extend(
            _validate_prompt_snippets(
                automation_id=automation_id,
                prompt=prompt,
                snippets=SVP_DOCS_REQUIRED_PROMPT_SNIPPETS,
                code="svp_docs_prompt_missing",
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


def _automation_contract_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_user_profile_projection(root: Path, automation_id: str) -> dict[str, Any] | None:
    """Build the allowed Codex Desktop UI mirror for an active repo cron contract."""
    root = root.resolve()
    data = _load_automation(root, automation_id)
    if data is None:
        return None
    if data.get("kind") != "cron" or data.get("status") != "ACTIVE" or not isinstance(data.get("rrule"), str):
        return None
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return None
    contract_path = _automation_path(root, automation_id).resolve()
    return {
        "schema": AUTOMATION_PROJECTION_SCHEMA,
        "projection_kind": "repo_contract_ui_mirror",
        "automation_id": automation_id,
        "enabled": True,
        "repo_root": str(root),
        "contract_path": str(contract_path),
        "contract_sha256": _automation_contract_digest(contract_path),
        "id": data.get("id"),
        "kind": data.get("kind"),
        "name": data.get("name", automation_id),
        "prompt": prompt,
        "status": data.get("status"),
        "rrule": data.get("rrule"),
        "model": data.get("model"),
        "reasoning_effort": data.get("reasoning_effort"),
        "execution_environment": data.get("execution_environment"),
        "cwds": data.get("cwds"),
    }


def iter_user_profile_projections(root: Path) -> list[dict[str, Any]]:
    projections: list[dict[str, Any]] = []
    for automation_id in AUTOMATION_IDS:
        projection = build_user_profile_projection(root, automation_id)
        if projection is not None:
            projections.append(projection)
    return projections


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


def _value_references_repo(value: object, root: Path) -> bool:
    root_text = str(root)
    markers = (
        root_text,
        root_text.replace("\\", "/"),
        root_text.replace("/", "\\"),
        "Agentic-Workflow-FRESH",
        "Agentic-Workflow",
    )
    if isinstance(value, str):
        return any(marker in value for marker in markers)
    if isinstance(value, (list, tuple)):
        return any(_value_references_repo(item, root) for item in value)
    if isinstance(value, dict):
        return any(_value_references_repo(item, root) for item in value.values())
    return False


def _automation_toml_references_repo(path: Path, root: Path) -> bool:
    data, error = _load_toml(path)
    if data is not None:
        return _value_references_repo(data, root)
    try:
        return _value_references_repo(path.read_text(encoding="utf-8", errors="ignore"), root)
    except OSError:
        return error is not None


def _is_valid_user_profile_projection(path: Path, root: Path) -> bool:
    data, error = _load_toml(path)
    if data is None or error is not None:
        return False
    if any(field in data for field in USER_PROFILE_FORBIDDEN_AUTOMATION_FIELDS):
        return False
    automation_id = data.get("automation_id")
    if not isinstance(automation_id, str):
        return False
    expected = build_user_profile_projection(root, automation_id)
    if expected is None:
        return False
    for field in AUTOMATION_PROJECTION_FIELDS:
        if data.get(field) != expected.get(field):
            return False
    return True


def _user_profile_automation_artifacts(user_codex_home: Path, root: Path) -> list[Path]:
    automations_root = user_codex_home / "automations"
    if not automations_root.exists():
        return []
    artifacts: list[Path] = []
    try:
        automation_dirs = sorted(path for path in automations_root.iterdir() if path.is_dir())
    except OSError:
        return [automations_root]
    for automation_dir in automation_dirs:
        automation_toml = automation_dir / "automation.toml"
        if automation_toml.exists() and _is_valid_user_profile_projection(automation_toml, root):
            continue
        if automation_dir.name in USER_PROFILE_REPO_AUTOMATION_IDS:
            artifacts.append(automation_toml if automation_toml.exists() else automation_dir)
            continue
        if automation_toml.exists() and _automation_toml_references_repo(automation_toml, root):
            artifacts.append(automation_toml)
    return artifacts


def _forbidden_user_profile_skill_paths(user_codex_home: Path) -> list[Path]:
    return [user_codex_home / "skills" / skill_id / "SKILL.md" for skill_id in REPO_SKILL_IDS]


def _forbidden_repo_paths(root: Path) -> list[Path]:
    return [root / relative_path for relative_path in FORBIDDEN_REPO_CODEX_TREES]


def _forbidden_repo_enforcement_paths(root: Path) -> list[tuple[Path, str]]:
    return [
        (root / relative_path, detail)
        for relative_path, detail in FORBIDDEN_REPO_ENFORCEMENT_TREES.items()
    ]


def _codex_top_level_plan_artifacts(root: Path) -> list[Path]:
    plans_root = root / ".codex" / "plans"
    if not plans_root.exists():
        return []
    return [
        path
        for path in sorted(plans_root.glob("*.md"))
        if path.name not in ALLOWED_CODEX_PLAN_TOP_LEVEL_FILES
    ]


def _legacy_codex_rule_files(root: Path) -> list[Path]:
    rules_root = root / ".codex" / "rules"
    if not rules_root.exists():
        return []
    return sorted(path for path in rules_root.glob("*.mdc") if path.is_file())


def _forbidden_schema_authority_refs(root: Path) -> list[tuple[Path, int, str]]:
    schemas_root = root / ".codex" / "schemas"
    if not schemas_root.exists():
        return []
    matches: list[tuple[Path, int, str]] = []
    for path in sorted(p for p in schemas_root.rglob("*") if p.is_file()):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, 1):
            if FORBIDDEN_SCHEMA_AUTHORITY_REF_RE.search(line):
                matches.append((path, line_number, line.strip()))
    return matches


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

    for path, detail in _forbidden_repo_enforcement_paths(root):
        if path.exists():
            issues.append(
                EnforcementHomeIssue(
                    "repo_duplicate_enforcement_home",
                    f"{path}: {detail}",
                )
            )

    for path in _codex_top_level_plan_artifacts(root):
        issues.append(
            EnforcementHomeIssue(
                "repo_plan_archive_only",
                f"{path}: .codex/plans is archive-only; active plan files must live under {root / 'plans'}",
            )
        )

    for path in _legacy_codex_rule_files(root):
        issues.append(
            EnforcementHomeIssue(
                "repo_legacy_rule_extension",
                f"{path}: active Codex rules must use .md; .mdc is historical only",
            )
        )

    for path, line_number, line in _forbidden_schema_authority_refs(root):
        issues.append(
            EnforcementHomeIssue(
                "repo_stale_schema_authority_ref",
                f"{path}:{line_number}: stale authority reference in active schema comment: {line}",
            )
        )

    for automation_id in AUTOMATION_IDS:
        issues.extend(_validate_automation(root, automation_id))
    issues.extend(_validate_adg_handoff_graph(root))

    for skill_id in REPO_SKILL_IDS:
        skill_path = root / ".codex" / "skills" / skill_id / "SKILL.md"
        if not skill_path.exists():
            issues.append(EnforcementHomeIssue("repo_skill_missing", f"{skill_path}: missing repo-owned skill"))

    for path in _user_profile_automation_artifacts(user_codex_home, root):
        issues.append(
            EnforcementHomeIssue(
                "user_profile_enforcement_artifact",
                f"{path}: Agentic-Workflow automation artifacts must live under {root / '.codex' / 'automations'}, not under the user Codex profile",
            )
        )

    for path in _forbidden_user_profile_skill_paths(user_codex_home):
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
