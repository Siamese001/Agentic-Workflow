from __future__ import annotations

import json
from pathlib import Path

from apps_rg import __main__ as cli


def _write_pin(
    repo_root: Path,
    section_id: str,
    *,
    source_run_id: str | None,
    text_filename: str = "headline_output.txt",
    body: str = "Pinned headline",
) -> Path:
    sec_dir = repo_root / "artifacts" / "apps_rg" / "_pinned" / section_id
    sec_dir.mkdir(parents=True, exist_ok=True)
    (sec_dir / text_filename).write_text(body, encoding="utf-8")
    (sec_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    if source_run_id is not None:
        (sec_dir / cli._SECTION_PIN_MANIFEST_FILENAME).write_text(
            json.dumps(
                {
                    "schema": "apps_rg.section_pin_manifest.v1",
                    "section_id": section_id,
                    "source_integrated_run_id": source_run_id,
                    "same_e2e_run_required": True,
                }
            ),
            encoding="utf-8",
    )
    return sec_dir


def _write_complete_pin_set(repo_root: Path, *, source_run_id: str) -> None:
    for section_id, text_filename, label in cli._PINNED_SECTION_TEXT_FILES:
        _write_pin(
            repo_root,
            section_id,
            source_run_id=source_run_id,
            text_filename=text_filename,
            body=f"Pinned {label}",
        )


def _read_status(out_dir: Path) -> dict:
    return json.loads((out_dir / "assemble_status.json").read_text(encoding="utf-8"))


def test_assemble_from_pinned_accepts_complete_same_integrated_run_pin_set(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_complete_pin_set(repo, source_run_id="full_resume_today")

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 0
    status = _read_status(run_dir)
    assert status["status"] == "assembled"
    assert status["complete"] is True
    assert status["missing"] == []
    assert status["invalid_pins"] == []
    assert "Pinned Headline" in (run_dir / "resume_assembled.md").read_text(encoding="utf-8")


def test_assemble_from_pinned_blocks_incomplete_pin_set(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_pin(repo, "headline", source_run_id="full_resume_today")

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 4
    status = _read_status(run_dir)
    assert status["status"] == "blocked"
    assert status["complete"] is False
    assert status["reason"] == "incomplete_section_pin_set"
    assert status["sections"]["headline"]["usable"] is True
    assert "Pinned headline" in (run_dir / "resume_assembled.md").read_text(encoding="utf-8")


def test_assemble_from_pinned_rejects_old_integrated_run_pin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_pin(repo, "headline", source_run_id="full_resume_three_days_ago")

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 5
    status = _read_status(run_dir)
    assert status["invalid_pins"] == ["headline"]
    assert status["status"] == "blocked"
    assert status["complete"] is False
    assert status["sections"]["headline"]["usable"] is False
    assert "pin_run_mismatch:full_resume_three_days_ago!=full_resume_today" == (
        status["sections"]["headline"]["pin_reason"]
    )
    assert "Pinned headline" not in (run_dir / "resume_assembled.md").read_text(encoding="utf-8")


def test_assemble_from_pinned_rejects_legacy_pin_without_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_pin(repo, "headline", source_run_id=None)

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 5
    status = _read_status(run_dir)
    assert status["sections"]["headline"]["pin_reason"] == "missing_or_unreadable_section_pin_manifest"
    assert status["status"] == "blocked"
    assert status["complete"] is False


def test_assemble_from_pinned_requires_full_resume_artifact_context(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    out_dir = repo / "artifacts" / "apps_rg" / "_pinned" / "_assembled"
    _write_pin(repo, "headline", source_run_id="full_resume_today")

    code = cli._assemble_from_pinned_dirs(repo, str(out_dir))

    assert code == 5
    status = _read_status(out_dir)
    assert status["status"] == "blocked"
    assert status["reason"] == "missing_e2e_run_context"


def test_new_e2e_start_clears_prior_section_pins_and_writes_receipt(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_pin(repo, "headline", source_run_id="full_resume_yesterday")
    assembled = repo / "artifacts" / "apps_rg" / "_pinned" / "_assembled"
    assembled.mkdir(parents=True, exist_ok=True)
    (assembled / "resume_assembled.md").write_text("old assembled", encoding="utf-8")
    receipts = repo / "artifacts" / "apps_rg" / "_pinned" / "_cleanup_receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    (receipts / "prior.json").write_text("{}", encoding="utf-8")

    receipt = cli._clear_section_pins_for_new_e2e_run(
        repo,
        "artifacts/apps_rg/runs/full_resume_today",
    )

    assert sorted(receipt["removed"]) == ["_assembled", "headline"]
    assert receipt["pin_validity_scope"] == "current_e2e_run_only"
    assert not (repo / "artifacts" / "apps_rg" / "_pinned" / "headline").exists()
    assert not assembled.exists()
    assert (receipts / "prior.json").is_file()
    receipt_path = (
        repo
        / "artifacts"
        / "apps_rg"
        / "runs"
        / "full_resume_today"
        / cli._SECTION_PIN_CLEANUP_RECEIPT_FILENAME
    )
    assert receipt_path.is_file()
    persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert persisted["removed_count"] == 2
