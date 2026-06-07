"""Negative controls for apps_rg/core L7 ownership verifier."""
from __future__ import annotations

import json
from pathlib import Path

from tools.cert.verify_apps_rg_l7_ownership_boundary import verify_dir


def _write(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def test_valid_section_refs_only_boundary_passes(tmp_path: Path) -> None:
    _write(tmp_path / "x2_gate_outputs.json", {"gates": []})
    _write(
        tmp_path / "section_runtime_proof_bundle.json",
        {"schema_version": "section_runtime_proof_bundle_v1"},
    )
    _write(
        tmp_path / "evidence_package_index.json",
        {
            "verified_external_refs": [
                {
                    "artifact_name": "agentic_core_how_trace.json",
                    "source_path": "artifacts/apps_rg/runs/cli_x/agentic_core_how_trace.json",
                    "local_path": None,
                }
            ],
            "durable_vector_persistence_proven": False,
        },
    )
    assert verify_dir(tmp_path) == []


def test_fake_local_core_l7_is_violation(tmp_path: Path) -> None:
    _write(
        tmp_path / "agentic_core_how_trace.json",
        {
            "producer_component": "apps_rg.runtime.section_lane",
            "runtime_subject": "agentic_core",
            "evidence_plane": "L7_AUDITABILITY",
        },
    )
    violations = verify_dir(tmp_path)
    assert violations
    assert "producer_component" in violations[0]


def test_verified_external_ref_with_local_path_is_violation(tmp_path: Path) -> None:
    _write(
        tmp_path / "evidence_package_index.json",
        {
            "verified_external_refs": [
                {
                    "artifact_name": "agentic_core_spine_proof.json",
                    "source_path": "artifacts/apps_rg/runs/cli_x/agentic_core_spine_proof.json",
                    "local_path": "artifacts/apps_rg/runtime_proofs/es/run/agentic_core_spine_proof.json",
                }
            ]
        },
    )
    violations = verify_dir(tmp_path)
    assert violations
    assert "local_path=null" in violations[0]
