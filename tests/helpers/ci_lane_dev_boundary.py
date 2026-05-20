"""CI lane-dev boundary helpers — library only (no CLI, no product proof execution).

Extracted from the retired ``ops_scripts/ci/prove_apps_rg_e2e_runtime.py`` harness for unit tests.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from apps_rg.runtime.non_product_proof_stamp import (
    CI_LANE_DEV_HARNESS_CLASSIFICATION,
    CONTRACT_TEST_PROOF_CLASSIFICATION,
)

_AGENTIC_CORE_UNTRACKED_ONLY = "PRE_EXISTING_UNTRACKED_AGENTIC_CORE_PATH"
_AGENTIC_CORE_TRACKED_ONLY = "TRACKED_AGENTIC_CORE_WORKING_TREE_CHANGES"
_AGENTIC_CORE_MIXED = "TRACKED_AND_UNTRACKED_AGENTIC_CORE_CHANGES"


def run_git_cmd(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False, shell=False, env=env)


def classify_agentic_core_porcelain_lines(lines: list[str]) -> dict[str, Any]:
    trimmed = [ln.rstrip("\r") for ln in lines if ln.strip()]
    tracked = False
    untracked = False
    raw_paths: list[str] = []

    for entry in trimmed:
        if entry.startswith("??"):
            untracked = True
            rest = entry[2:].lstrip()
        else:
            tracked = True
            rest = entry[3:].lstrip() if len(entry) > 3 else entry.lstrip()

        if " -> " in rest:
            raw_paths.extend(p.strip() for p in rest.split(" -> "))
        else:
            raw_paths.append(rest.strip())

    paths_sorted = sorted({p for p in raw_paths if p})
    dirty = tracked or untracked
    if not dirty:
        reason = ""
    elif untracked and not tracked:
        reason = _AGENTIC_CORE_UNTRACKED_ONLY
    elif tracked and untracked:
        reason = _AGENTIC_CORE_MIXED
    else:
        reason = _AGENTIC_CORE_TRACKED_ONLY

    return {
        "agentic_core_modified": dirty,
        "agentic_core_dirty_reason": reason,
        "agentic_core_dirty_paths": paths_sorted,
    }


def finalize_boundary_no_bypass(artifact: dict[str, Any], repo: Path) -> None:
    raw = run_git_cmd(["git", "status", "--porcelain=v1", "--", "agentic_core"], cwd=repo)
    klass = classify_agentic_core_porcelain_lines((raw.stdout or "").splitlines())
    box = artifact.setdefault("boundary_no_bypass", {})
    box.update(klass)
    box["agentic_core_modified_by_this_task"] = False
    box.setdefault("new_app_literals_in_core", False)
    box.setdefault("direct_l2_chroma_bypass", False)
    box.setdefault("direct_l4_write_bypass", False)
    box.setdefault("mock_pass", False)
    box["direct_bypass"] = bool(box.get("direct_l2_chroma_bypass")) or bool(box.get("direct_l4_write_bypass"))


def persist_ci_lane_dev_proof_artifact(
    artifact: dict[str, Any],
    repo: Path,
    *,
    artifact_path: Path,
    proof_classification: str | None = None,
) -> None:
    """Stamp non-product CI lane-dev classification and write proof JSON (test/fixture use)."""
    finalize_boundary_no_bypass(artifact, repo)
    u = run_git_cmd(["git", "diff", "--name-only"], cwd=repo)
    c = run_git_cmd(["git", "diff", "--name-only", "--cached"], cwd=repo)
    names = {
        ln.strip()
        for ln in (u.stdout or "").splitlines() + (c.stdout or "").splitlines()
        if ln.strip()
    }
    artifact["files_changed"] = sorted(names)
    artifact["proof_classification"] = proof_classification or CI_LANE_DEV_HARNESS_CLASSIFICATION
    if artifact["proof_classification"] == CONTRACT_TEST_PROOF_CLASSIFICATION:
        artifact.setdefault("explicit_non_claims", []).append("contract test proof only")
    artifact["product_certification"] = "NOT_CLAIMED"
    artifact["l7_certification"] = "NOT_CLAIMED"
    artifact["fort_knox_certification"] = "NOT_CLAIMED"
    artifact["integrated_r4_invoked"] = False
    artifact["explicit_non_claims"] = [
        "CI lane rollup harness only",
        "not product runtime certification",
        "not L7 or Fort Knox proof",
        "integrated R4 requires python -m apps_rg whole-run gate separately",
    ]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


def minimal_ci_lane_dev_artifact() -> dict[str, Any]:
    """Minimal artifact shell for harness unit tests (boundary_no_bypass contracts)."""
    return {
        "boundary_no_bypass": {
            "mock_pass": False,
            "direct_l2_chroma_bypass": False,
            "direct_l4_write_bypass": False,
        },
        "commands_run": [],
        "pa": {},
        "route": {},
        "c0": {},
        "exit": {},
    }
