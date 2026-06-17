"""Verify the repo-owned Codex primary execution adapter.

This verifier checks the contract and executable hooks that make Codex the
primary local execution surface while keeping governance rules versioned in the
repository instead of a private Codex-only registry.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from collections.abc import Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "AGENTS.md",
    "docs/codex-primary-execution.md",
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
        "GitKraken",
        "Codex must ask a plain-text clarifying question directly in the assistant response",
    ],
    "docs/codex-primary-execution.md": [
        "Codex primary execution surface",
        "scripts/governance/codex_readiness.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/verify_codex_primary.py",
        "GitKraken",
        "No parallel registry",
        "Codex must ask a plain-text clarifying question directly in the assistant response",
    ],
}

FORBIDDEN_PHRASES = {
    "AGENTS.md": [
        "CLAUDE.md",
        "Claude hook parity",
        "Claude-specific workflows",
        "AskUserQuestion",
        "request_user_input",
    ],
    "docs/codex-primary-execution.md": [
        "AskUserQuestion",
        "request_user_input",
        "Claude hook parity",
        "Claude-specific workflows",
        "Codex-vs-Claude",
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


def forbidden_phrase_failures(phrase_map: Mapping[str, list[str]], root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, phrases in phrase_map.items():
        path = root / relative_path
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase in text:
                failures.append(f"{path}: forbidden phrase {phrase!r}")
    return failures


def validate(root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(str(path) for path in missing_paths(REQUIRED_FILES, root))
    if failures:
        return failures
    failures.extend(missing_anchors(REQUIRED_ANCHORS, root))
    failures.extend(forbidden_phrase_failures(FORBIDDEN_PHRASES, root))
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
