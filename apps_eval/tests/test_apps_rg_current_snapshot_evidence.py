from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_eval.adapters.apps_rg import normalize_existing_apps_rg_run_snapshot
from apps_eval.runner.core import (
    run_current_snapshot_eval,
    verify_apps_rg_eval_package_seal,
)
from apps_eval.tests._apps_rg_evidence import emit_verified_current_run_evidence


def _source_digest(root: Path) -> str:
    rows: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.relative_to(root).parts[0] == "apps_eval":
            continue
        rows.append(
            (
                path.relative_to(root).as_posix(),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def test_current_snapshot_record_is_identity_and_source_digest_bound(
    tmp_path: Path,
    monkeypatch,
) -> None:
    run_root = tmp_path / "product_run"
    outputs = run_root / "outputs"
    evidence_dir = run_root / "evidence"
    outputs.mkdir(parents=True)
    evidence_dir.mkdir()
    evidence = evidence_dir / "fact.json"
    evidence.write_text('{"fact":"led modernization"}', encoding="utf-8")
    evidence_digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    (outputs / "generated_resume.json").write_text(
        json.dumps(
            {
                "sections": {
                    "executive_summary": "Strategic technology leader " * 5,
                    "experience": {
                        "text": "Led enterprise modernization " * 8,
                        "source_ref": "evidence/fact.json",
                        "source_digest": evidence_digest,
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    (outputs / "resume.md").write_text("# Resume\n\nVerified output\n", encoding="utf-8")
    emit_verified_current_run_evidence(run_root, monkeypatch)
    before = _source_digest(run_root)

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="current-run",
        result={
            "x3_disposition": "X3D_ALLOW_FINISH",
            "outcome_authorized": True,
        },
        artifact_dir=run_root,
    )
    record = run_current_snapshot_eval(
        snapshot,
        out_dir=str(run_root / "apps_eval"),
        expected={
            "required_sections": [],
            "expected_x3": "X3D",
            "required_output_keys": ["runtime", "sections"],
            "required_artifacts": ["generated_resume.json", "resume.md"],
            "grounded_claims_required": True,
            "allow_side_effects": False,
        },
    )

    assert _source_digest(run_root) == before
    assert record.parent_run_id == "parent-1"
    assert record.child_run_id == "child-1"
    assert record.section_attempt_id == "attempt-1"
    assert record.eval_record_id == record.record_id
    assert record.runtime_exhaust_bundle_id == "exhaust-1"
    assert record.snapshot_digest == snapshot.snapshot_digest
    assert record.registry_digest == record.microstep_contract_digest
    required_rows = [row for row in record.scorecard.scorecard_rows if row["required"]]
    assert required_rows
    assert all(row["eval_record_id"] == record.record_id for row in required_rows)
    assert all(row["snapshot_digest"] == snapshot.snapshot_digest for row in required_rows)
    assert all(row["registry_digest"] == record.registry_digest for row in required_rows)
    assert record.scorecard.dimension_scores["section_structure"] == 0.0
    assert record.scorecard.dimension_scores["x3_disposition"] == 1.0
    assert Path(record.artifact_paths["eval_record"]).is_file()
    package_rows = [
        row
        for row in record.scorecard.scorecard_rows
        if row["component_id"] == "apps_rg.eval_package"
    ]
    assert package_rows
    assert all(row["verdict"] == "PASS" for row in package_rows)
    assert Path(record.artifact_paths["eval_package_seal"]).is_file()
    assert verify_apps_rg_eval_package_seal(
        Path(record.artifact_paths["eval_record"]).parent
    ) == (True, [])
    Path(record.artifact_paths["coverage_matrix"]).write_text(
        "tampered\n",
        encoding="utf-8",
    )
    valid, errors = verify_apps_rg_eval_package_seal(
        Path(record.artifact_paths["eval_record"]).parent
    )
    assert valid is False
    assert "eval_package_seal_artifact_digest_mismatch:coverage_matrix" in errors
