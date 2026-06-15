"""
tests/runtime/test_source_manifest_integrity.py

Phase 0 acceptance test.

Asserts that source_manifest.json:
  * exists at the canonical export location
  * declares exactly 12 source folders found
  * lists at least one ingested file
  * has empty missing_folders and empty_folders arrays
  * carries a sha256, line_count, mtime, and ingested=True for every entry
  * the markdown summary is consistent with the JSON

These guarantees are the foundation every later phase depends on. Failure
here means the foolproof rule "do not silently substitute another folder"
has been violated.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

EXPECTED_FOLDERS = frozenset(
    {
        "docs/reference/06_L6_Observability_and_System_Learning",
        "docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance",
        "docs/reference/00A_L5_Governance_Safety",
        "docs/reference/00B_L4_State_Archive_and_UWG",
        "docs/reference/00C_Runtime_Gates_Current_Run_Mesh",
        "docs/reference/01_Request_Intake",
        "docs/reference/02_L1_Reasoning_Plan",
        "docs/reference/03_L0_Route_Decision",
        "docs/reference/03A_C0_Context_Engine",
        "docs/reference/03B_PA_Prompt_Assembly",
        "docs/reference/04_L2_Execute",
        "docs/reference/05_Exit_Evaluation_and_Control",
    }
)


@pytest.fixture(scope="module")
def manifest(proof_artifacts: Path) -> dict:
    p = proof_artifacts / "source_manifest.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_manifest_file_exists(proof_artifacts: Path) -> None:
    p = proof_artifacts / "source_manifest.json"
    assert p.exists(), f"source_manifest.json missing at {p}"


def test_manifest_summary_well_formed(manifest: dict) -> None:
    assert "summary" in manifest
    assert "files" in manifest
    s = manifest["summary"]
    for key in (
        "folder_count_expected",
        "folder_count_found",
        "file_count_ingested",
        "missing_folders",
        "empty_folders",
        "excluded_files",
        "generated_at_utc",
        "repo_root",
    ):
        assert key in s, f"missing summary key: {key}"


def test_manifest_all_12_folders_found(manifest: dict) -> None:
    s = manifest["summary"]
    assert s["folder_count_expected"] == 12
    assert s["folder_count_found"] == 12, (
        f"folder_count_found={s['folder_count_found']}, missing={s['missing_folders']}"
    )
    assert s["missing_folders"] == []
    assert s["empty_folders"] == []


def test_manifest_has_ingested_files(manifest: dict) -> None:
    assert manifest["summary"]["file_count_ingested"] > 0
    assert len(manifest["files"]) == manifest["summary"]["file_count_ingested"]


def test_manifest_covers_all_12_folders(manifest: dict) -> None:
    """Every expected folder must contribute at least one file."""
    found = set()
    for entry in manifest["files"]:
        rel = entry["relative_path"].replace("\\", "/")
        parts = rel.split("/")
        if len(parts) >= 3:
            found.add("/".join(parts[:3]))
    missing = EXPECTED_FOLDERS - found
    assert not missing, f"folders with zero ingested files: {sorted(missing)}"


def test_every_file_entry_well_formed(manifest: dict) -> None:
    required = {
        "source_folder",
        "path",
        "relative_path",
        "sha256",
        "line_count",
        "mtime",
        "ingested",
    }
    for entry in manifest["files"]:
        missing = required - set(entry.keys())
        assert not missing, f"{entry.get('path')} missing keys {missing}"
        assert isinstance(entry["sha256"], str)
        assert len(entry["sha256"]) == 64, f"sha256 wrong length for {entry['relative_path']}"
        assert all(c in "0123456789abcdef" for c in entry["sha256"]), (
            f"sha256 not lowercase hex for {entry['relative_path']}"
        )
        assert entry["line_count"] >= 1
        assert entry["ingested"] is True


def test_every_file_entry_path_resolvable(manifest: dict, repo_root: Path) -> None:
    for entry in manifest["files"]:
        p = Path(entry["path"])
        assert p.exists(), f"declared path does not exist on disk: {p}"
        rel = repo_root / entry["relative_path"]
        assert rel.exists(), f"declared relative_path does not resolve: {rel}"


def test_no_excluded_artifact_files_ingested(manifest: dict) -> None:
    """The excluded path 'artifacts/runtime/requirements_proof' must not appear."""
    for entry in manifest["files"]:
        rel = entry["relative_path"].replace("\\", "/")
        assert "artifacts/runtime/requirements_proof" not in rel
        assert not rel.endswith(".tmp")
        assert not rel.endswith(".bak")


def test_manifest_md_consistent_with_json(proof_artifacts: Path, manifest: dict) -> None:
    md = (proof_artifacts / "source_manifest.md").read_text(encoding="utf-8")
    assert "# Source Manifest" in md
    n = manifest["summary"]["folder_count_found"]
    assert f"folder_count_found: **{n}**" in md
    files_n = manifest["summary"]["file_count_ingested"]
    assert f"file_count_ingested: **{files_n}**" in md
