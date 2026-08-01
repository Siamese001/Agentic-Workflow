"""Verify the repo-owned Codex primary execution adapter.

This verifier checks the contract and executable hooks that make Codex the
primary local execution surface while keeping governance rules versioned in the
repository instead of a private Codex-only registry.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import verify_codex_enforcement_home_portable as verify_codex_enforcement_home

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "AGENTS.md",
    "docs/codex-primary-execution.md",
    "scripts/governance/audit_codex_mcp_transports.py",
    "scripts/governance/check_windows_path_budget.py",
    "scripts/governance/codex_main_closeout.py",
    "scripts/governance/codex_readiness.py",
    "scripts/governance/ensure_searxng_readiness.py",
    "scripts/governance/svp_docs_review.py",
    "scripts/governance/verify_codex_enforcement_home.py",
    "scripts/governance/verify_codex_enforcement_home_portable.py",
    "scripts/governance/verify_codex_run_receipt.py",
    "scripts/governance/verify_codex_primary.py",
    ".codex/config.toml",
    ".codex/automations/on-demand-pr-main-publisher/automation.toml",
    ".codex/automations/on-demand-svp-documentation-refresh/automation.toml",
    ".codex/automations/adg-audit-and-burndown/automation.toml",
    ".codex/automations/adg-bcg-p2-next-action/automation.toml",
    ".codex/automations/adg-p3-promotion-hygiene/automation.toml",
    ".codex/automations/svp-readme-documentation-refresh/automation.toml",
    ".codex/automations/svp-readme-documentation-refresh/reviewer_packet.v1.json",
    ".codex/schemas/svp_docs_approval_v1.schema.json",
    ".codex/schemas/svp_docs_x1d_v1.schema.json",
    ".codex/schemas/svp_docs_x2_v1.schema.json",
    ".codex/schemas/svp_docs_x3_v1.schema.json",
    ".codex/schemas/svp_docs_run_v1.schema.json",
    ".codex/hooks.json",
    ".codex/hooks/selected_avatar_guard.py",
    ".codex/skills/agentic-workflow-governance/SKILL.md",
    ".codex/skills/agentic-workflow-verification/SKILL.md",
    ".codex/hooks/lib/codex_hook_common.py",
    ".codex/governance/scripts/filesystem_mcp_launcher.js",
]

REQUIRED_ANCHORS = {
    "AGENTS.md": [
        "## Codex primary execution adapter",
        "docs/codex-primary-execution.md",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/codex_main_closeout.py",
        "scripts/governance/verify_codex_enforcement_home.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/verify_codex_primary.py",
        "GitKraken",
        "Codex must ask a plain-text clarifying question directly in the assistant response",
        ".codex/hooks.json",
        ".codex/automations/",
    ],
    "docs/codex-primary-execution.md": [
        "Codex primary execution surface",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/codex_main_closeout.py",
        "scripts/governance/verify_codex_enforcement_home.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/verify_codex_primary.py",
        "GitKraken",
        "No parallel registry",
        "Codex must ask a plain-text clarifying question directly in the assistant response",
        ".codex/hooks.json",
        ".codex/automations/",
    ],
    ".codex/automations/svp-readme-documentation-refresh/automation.toml": [
        'mode = "audit_only"',
        "allow_edits = false",
        "allow_publication = false",
        'publication_handoff = "on-demand-pr-main-publisher"',
        "The weekly job must never emit ALLOW_TO_PR",
        "scripts/governance/svp_docs_review.py",
    ],
    ".codex/automations/on-demand-svp-documentation-refresh/automation.toml": [
        'mode = "approved_edit"',
        "require_approval_receipt = true",
        "allow_publication = false",
        'publication_handoff = "on-demand-pr-main-publisher"',
        "ALLOW_TO_PR",
        "scripts/governance/svp_docs_review.py",
    ],
    ".codex/automations/svp-readme-documentation-refresh/reviewer_packet.v1.json": [
        '"schema_version": "svp_docs_reviewer_packet/v1"',
        '"publication_handoff": "on-demand-pr-main-publisher"',
        '"apps_shared/integrations/app_registry.py"',
    ],
    ".codex/schemas/svp_docs_x1d_v1.schema.json": ['"$id": "svp_docs_x1d/v1"'],
    ".codex/schemas/svp_docs_x2_v1.schema.json": ['"$id": "svp_docs_x2/v1"'],
    ".codex/schemas/svp_docs_x3_v1.schema.json": ['"$id": "svp_docs_x3/v1"'],
    ".codex/schemas/svp_docs_run_v1.schema.json": ['"$id": "svp_docs_run/v1"'],
    ".codex/schemas/svp_docs_approval_v1.schema.json": ['"$id": "svp_docs_approval/v1"'],
}

FORBIDDEN_CODEX_ONLY_TEXT = ("CLAUDE" + ".md", "CLAUDE_PROJECT" + "_DIR")
FORBIDDEN_LEGACY_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])\.claude(?=($|[\\/]))")


def missing_paths(paths: list[str], root: Path) -> list[Path]:
    return [root / path for path in paths if not (root / path).exists()]


def missing_anchors(anchor_map: Mapping[str, list[str]], root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, anchors in anchor_map.items():
        path = root / relative_path
        text = path.read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                failures.append(f"{path}: missing anchor {anchor!r}")
    return failures


def hook_target_failures(hooks_path: Path, root: Path) -> list[str]:
    failures: list[str] = []
    hooks_config = json.loads(hooks_path.read_text(encoding="utf-8"))
    for event, groups in hooks_config.get("hooks", {}).items():
        for group in groups:
            matcher = group.get("matcher", "*")
            for hook in group.get("hooks", []):
                command = str(hook.get("command", ""))
                matches = re.findall(r"\$AGENTIC_REPO_ROOT/([^\"\s]+)", command)
                if not matches and "$AGENTIC_REPO_ROOT" in command:
                    failures.append(f"{hooks_path}: could not parse hook target for {event}/{matcher}: {command}")
                    continue
                for relative_target in matches:
                    target = root / relative_target
                    if not target.exists():
                        failures.append(f"{hooks_path}: missing hook target for {event}/{matcher}: {target}")
    return failures


def codex_only_failures(root: Path) -> list[str]:
    failures: list[str] = []
    legacy_governance_dir = root / ("." + "claude")
    if legacy_governance_dir.exists():
        failures.append(f"{legacy_governance_dir}: forbidden legacy governance directory exists")

    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode == 0:
        files = [root / relative_path for relative_path in proc.stdout.splitlines()]
    else:
        files = [
            path
            for path in root.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and ".pytest_cache" not in path.parts
        ]

    for path in files:
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            failures.append(f"{path}: could not read file: {exc}")
            continue
        if b"\0" in raw:
            continue
        text = raw.decode("utf-8", errors="ignore")
        for forbidden in FORBIDDEN_CODEX_ONLY_TEXT:
            if forbidden in text:
                failures.append(f"{path}: forbidden Codex-only reference {forbidden!r}")
        if FORBIDDEN_LEGACY_PATH_RE.search(text):
            failures.append(f"{path}: forbidden legacy governance path reference")
    return failures


def validate(root: Path = REPO_ROOT, *, repo_only: bool = False) -> list[str]:
    failures: list[str] = []
    failures.extend(str(path) for path in missing_paths(REQUIRED_FILES, root))
    if failures:
        return failures
    failures.extend(missing_anchors(REQUIRED_ANCHORS, root))
    failures.extend(hook_target_failures(root / ".codex" / "hooks.json", root))
    failures.extend(codex_only_failures(root))
    if not repo_only:
        failures.extend(
            f"{issue.code}: {issue.detail}"
            for issue in verify_codex_enforcement_home.validate(root)
        )
    return failures


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to verify")
    parser.add_argument(
        "--repo-only",
        action="store_true",
        help="Compatibility no-op for repo-scoped verification.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures = validate(args.root, repo_only=args.repo_only)
    if failures:
        print("Codex primary execution verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Codex primary execution verification passed")
    print(f"- repo: {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
