"""Docs/CI must not teach disallowed ``python -m apps_rg.runtime.*`` execution commands."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.runtime.outside_main_entry_policy import DISALLOWED_DOC_CI_COMMAND_SUBSTRINGS

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "ops_scripts",
    REPO_ROOT / ".claude" / "rules",
)

# Historical closeout JSON/manifests are evidence, not operator runbooks.
SKIP_SUFFIXES = {".json"}
SKIP_PATH_PARTS = ("_archive", "command_transcripts", "integrated_r4_product_proof_gate_closeout")


def _iter_scan_files() -> list[Path]:
    out: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            if any(part in SKIP_PATH_PARTS for part in path.parts):
                continue
            if path.name in {
                "outside_main_entry_policy.py",
            }:
                continue
            if "runtime/dispatch/" in path.as_posix() and path.suffix == ".py":
                continue
            if path.name == "r4_generation_route.py":
                continue
            if path.suffix.lower() not in {".md", ".mdc", ".py", ".yml", ".yaml", ".sh"}:
                continue
            out.append(path)
    return out


@pytest.mark.parametrize("needle", DISALLOWED_DOC_CI_COMMAND_SUBSTRINGS)
def test_disallowed_command_substrings_absent_from_active_docs_and_scripts(needle: str) -> None:
    hits: list[str] = []
    for path in _iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if needle in text:
            rel = path.relative_to(REPO_ROOT).as_posix()
            hits.append(rel)
    assert not hits, f"Disallowed command {needle!r} found in: {hits[:20]}"


def test_outside_main_policy_lists_forbidden_modules() -> None:
    policy = __import__(
        "apps_rg.runtime.outside_main_entry_policy",
        fromlist=["DELETED_RUNTIME_MODULE_CLI"],
    )
    assert "apps_rg.runtime.orchestrate_full_resume" in policy.DELETED_RUNTIME_MODULE_CLI
    assert "apps_rg.runtime.dispatch.executive_summary_dispatch" in policy.DELETED_RUNTIME_MODULE_CLI
