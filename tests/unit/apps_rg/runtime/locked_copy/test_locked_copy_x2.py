from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.locked_copy import locked_copy_x2 as subject


_SECTION_IDS = (
    "company_names",
    "titles",
    "locations",
    "dates",
    "education",
    "certifications",
    "insurtech",
    "ey",
    "early_career",
)


def _manifest() -> dict:
    return {
        "base_resume_json_ref": "base_resume.json",
        "provider_calls_made": False,
        "rewrite_allowed": False,
        "sections": [
            {
                "section_id": section_id,
                "byte_for_byte_match": True,
                "source_hash": f"hash-{section_id}",
                "copied_hash": f"hash-{section_id}",
                "rewrite_allowed": False,
                "copied_text": f"copy:{section_id}",
            }
            for section_id in _SECTION_IDS
        ],
    }


def test_run_locked_copy_x2_gates_passes_for_canonical_locked_sections(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(subject, "load_base_resume", lambda repo_root: ({}, None, None))
    monkeypatch.setattr(
        subject,
        "build_locked_sections",
        lambda base: [
            SimpleNamespace(section_id=section_id, copied_text=f"copy:{section_id}")
            for section_id in _SECTION_IDS
        ],
    )

    gates = subject.run_locked_copy_x2_gates(
        manifest=_manifest(),
        artifact_dir=tmp_path,
        repo_root=tmp_path,
    )

    assert gates
    assert all(gate.pass_ for gate in gates)
    assert {gate.gate_type for gate in gates} == {"deterministic"}


def test_run_locked_copy_x2_gates_fails_closed_when_provider_artifact_present(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(subject, "load_base_resume", lambda repo_root: ({}, None, None))
    monkeypatch.setattr(
        subject,
        "build_locked_sections",
        lambda base: [
            SimpleNamespace(section_id=section_id, copied_text=f"copy:{section_id}")
            for section_id in _SECTION_IDS
        ],
    )
    (tmp_path / "provider_request.json").write_text("{}", encoding="utf-8")

    gates = subject.run_locked_copy_x2_gates(
        manifest=_manifest(),
        artifact_dir=tmp_path,
        repo_root=tmp_path,
    )

    provider_gate = next(g for g in gates if g.gate_id == "x2_locked_copy_no_llm_provider")
    assert provider_gate.pass_ is False
    assert provider_gate.failure_reason == "Provider artifact present in locked_copy dir"


def test_write_x2_gate_outputs_serializes_pass_key(tmp_path: Path) -> None:
    gate = subject.X2GateResult(
        gate_id="g1",
        gate_type="deterministic",
        pass_=False,
        observed_value="bad",
        threshold=True,
        failure_reason="failed",
        evidence_ref="ref",
    )

    payload = subject.write_x2_gate_outputs(tmp_path / "x2.json", [gate])

    assert payload["failed_gates"] == ["g1"]
    assert payload["x2_failed"] == 1
    raw = json.loads((tmp_path / "x2.json").read_text(encoding="utf-8"))
    assert raw["gates"][0]["pass"] is False
    assert "pass_" not in raw["gates"][0]
