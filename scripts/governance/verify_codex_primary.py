"""Verify the repo-owned Codex primary execution adapter.

This verifier checks the contract and executable hooks that make Codex the
primary local execution surface while keeping governance rules versioned in the
repository instead of a private Codex-only registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/codex-primary-execution.md",
    "docs/codex-backup-adapter.md",
    "docs/reports/codex/codex_primary_mcp_live_snapshot.md",
    "docs/reports/codex/codex_primary_mcp_live_snapshot.json",
    "scripts/governance/audit_codex_mcp_transports.py",
    "scripts/governance/check_windows_path_budget.py",
    "scripts/governance/codex_readiness.py",
    "scripts/governance/verify_codex_run_receipt.py",
    "scripts/governance/verify_codex_primary.py",
]

REQUIRED_ANCHORS = {
    "AGENTS.md": [
        "## Codex primary execution adapter",
        "docs/codex-primary-execution.md",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/verify_codex_primary.py",
    ],
    "docs/codex-primary-execution.md": [
        "Codex primary execution surface",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/verify_codex_primary.py",
        "docs/reports/codex/codex_primary_mcp_live_snapshot.md",
        "No parallel registry",
    ],
    "docs/codex-backup-adapter.md": [
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/verify_codex_run_receipt.py",
    ],
}


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


def snapshot_failures(snapshot_path: Path) -> list[str]:
    failures: list[str] = []
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "codex-primary-mcp-snapshot/v1":
        failures.append(f"{snapshot_path}: schema_version must be codex-primary-mcp-snapshot/v1")
    routes = payload.get("routes")
    if not isinstance(routes, list) or not routes:
        failures.append(f"{snapshot_path}: routes must be a non-empty list")
        return failures
    for route in routes:
        if not isinstance(route, dict):
            failures.append(f"{snapshot_path}: every route must be an object")
            continue
        for field in ("server_id", "codex_status", "evidence", "run_policy"):
            if not isinstance(route.get(field), str) or not route[field].strip():
                failures.append(f"{snapshot_path}: route {route.get('server_id')!r} missing {field}")
    return failures


def validate(root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(str(path) for path in missing_paths(REQUIRED_FILES, root))
    if failures:
        return failures
    failures.extend(missing_anchors(REQUIRED_ANCHORS, root))
    failures.extend(snapshot_failures(root / "docs/reports/codex/codex_primary_mcp_live_snapshot.json"))
    return failures


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to verify")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures = validate(args.root)
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
