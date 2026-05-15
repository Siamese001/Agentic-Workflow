"""Governance tests — apps_rg UWG cache-write sovereignty (L6-W1).

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f

Proves ``check_no_direct_semantic_cache_write`` is clean and inert proposal types exist.
"""
from __future__ import annotations

import dataclasses
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_no_direct_semantic_cache_write.py"


def test_gate_clean_l6_w1() -> None:
    """L6-W1 gate must exit 0 on the patched codebase."""
    result = subprocess.run(
        [sys.executable, str(GATE_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Expected gate exit 0, got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_cache_write_proposal_is_frozen() -> None:
    from apps_rg.runtime.schemas import SectionCacheWriteProposal

    p = SectionCacheWriteProposal(
        section_id="s1",
        cache_key="k1",
        content_digest="d1",
        metadata_ref="m1",
    )
    assert p.proposal_status == "PENDING_UWG"
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.section_id = "x"  # type: ignore[misc]


def test_exit_result_has_cache_write_proposals_tuple() -> None:
    from apps_rg.runtime.bindings.exit_binding import ExitBindingResult, ExitDisposition, ExitResult
    import typing

    d = ExitDisposition(
        outcome_authorized=True,
        gate_results=[],
        c0_blocking=False,
    )
    r = ExitResult(disposition=d, artifact_commit_candidates=[], cache_write_proposals=())
    assert r.cache_write_proposals == ()
    hints = typing.get_type_hints(ExitResult)
    ann = hints.get("cache_write_proposals")
    assert ann is not None
    assert getattr(ann, "__origin__", None) is tuple


def test_r1b_semantic_not_imported_in_exit_binding() -> None:
    """AST: exit_binding must not import r1b_semantic writer."""
    exit_binding = REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "exit_binding.py"
    src = exit_binding.read_text(encoding="utf-8")
    assert "r1b_semantic" not in src
    assert "write_section_to_semantic_cache" not in src
