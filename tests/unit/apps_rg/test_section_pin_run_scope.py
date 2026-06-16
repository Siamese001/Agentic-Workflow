from __future__ import annotations

import json
from pathlib import Path

from apps_rg import __main__ as cli


def _write_pin(
    repo_root: Path,
    section_id: str,
    *,
    source_run_id: str | None,
    body: str = "Pinned headline",
) -> Path:
    sec_dir = repo_root / "artifacts" / "apps_rg" / "_pinned" / section_id
    sec_dir.mkdir(parents=True, exist_ok=True)
    (sec_dir / "headline_output.txt").write_text(body, encoding="utf-8")
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


def _read_status(out_dir: Path) -> dict:
    return json.loads((out_dir / "assemble_status.json").read_text(encoding="utf-8"))


def test_assemble_from_pinned_accepts_same_integrated_run_pin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_pin(repo, "headline", source_run_id="full_resume_today")

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 4  # other sections are intentionally absent in this focused fixture
    status = _read_status(run_dir)
    assert status["sections"]["headline"]["usable"] is True
    assert status["sections"]["headline"]["pin_reason"] == "same_e2e_run"
    assert "Pinned headline" in (run_dir / "resume_assembled.md").read_text(encoding="utf-8")


def test_assemble_from_pinned_rejects_old_integrated_run_pin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_today"
    _write_pin(repo, "headline", source_run_id="full_resume_three_days_ago")

    code = cli._assemble_from_pinned_dirs(repo, str(run_dir))

    assert code == 5
    status = _read_status(run_dir)
    assert status["invalid_pins"] == ["headline"]
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


def test_assemble_from_pinned_requires_full_resume_artifact_context(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    out_dir = repo / "artifacts" / "apps_rg" / "_pinned" / "_assembled"
    _write_pin(repo, "headline", source_run_id="full_resume_today")

    code = cli._assemble_from_pinned_dirs(repo, str(out_dir))

    assert code == 5
    status = _read_status(out_dir)
    assert status["status"] == "blocked"
    assert status["reason"] == "missing_e2e_run_context"
