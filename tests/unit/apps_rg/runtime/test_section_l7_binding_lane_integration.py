from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime import section_l7_binding_lane_integration as subject


def test_finalize_section_l7_binding_writes_manifest_and_payload_refs(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "run"
    artifact_dir.mkdir()
    runtime_payload = {"run_id": "run-1", "correlation_id": "corr-1"}

    monkeypatch.setattr(
        subject,
        "discover_integrated_correlation",
        lambda repo_root, artifact_dir, *, section_id: {"integrated": section_id},
    )

    def fake_manifest(**kwargs):
        return {
            "section_id": kwargs["section_id"],
            "run_id": kwargs["run_id"],
            "command_surface": kwargs["command_surface"],
            "correlation": kwargs["correlation"],
        }

    monkeypatch.setattr(subject, "build_section_l7_binding_manifest", fake_manifest)

    def fake_finalize(**kwargs):
        assert kwargs["binding_manifest"]["run_id"] == "run-1"
        assert kwargs["correlation_id"] == "corr-1"
        return {
            "evidence_package_index_path": artifact_dir / "evidence_package_index.json",
            "subphase_coverage_index_path": artifact_dir / "spine_subphase_coverage_index.json",
        }

    monkeypatch.setattr(subject, "finalize_section_evidence_package", fake_finalize)

    path = subject.finalize_section_l7_binding(
        artifact_dir,
        section_id="headline",
        runtime_payload=runtime_payload,
        repo_root=tmp_path,
    )

    assert path == artifact_dir / "section_l7_binding_manifest.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "section_id": "headline",
        "run_id": "run-1",
        "command_surface": "python -m apps_rg --section headline",
        "correlation": {"integrated": "headline"},
    }
    assert runtime_payload["section_l7_binding_manifest_ref"] == path.name
    assert runtime_payload["evidence_package_index_ref"] == "evidence_package_index.json"
    assert runtime_payload["spine_subphase_coverage_index_ref"] == (
        "spine_subphase_coverage_index.json"
    )
