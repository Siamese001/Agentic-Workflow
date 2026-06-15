from __future__ import annotations

from pathlib import Path

from apps_rg.runtime import section_one_spine_certification_lane_integration as integration


def test_finalize_section_one_spine_certification_delegates_exact_payload(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_emit(
        artifact_dir: Path,
        *,
        section_id: str,
        runtime_payload: dict[str, object],
        proof_bundle: dict[str, object],
        runtime_generation_status: str,
        full_apps_contract_suite_passed: bool,
    ) -> dict[str, Path]:
        calls.append(
            {
                "artifact_dir": artifact_dir,
                "section_id": section_id,
                "runtime_payload": runtime_payload,
                "proof_bundle": proof_bundle,
                "runtime_generation_status": runtime_generation_status,
                "full_apps_contract_suite_passed": full_apps_contract_suite_passed,
            }
        )
        return {"receipt": artifact_dir / "receipt.json"}

    monkeypatch.setattr(integration, "emit_section_one_spine_certification_artifacts", fake_emit)

    result = integration.finalize_section_one_spine_certification(
        tmp_path,
        "executive_summary",
        {"run_id": "r1"},
        proof_bundle={"proof_eligible": True},
        runtime_generation_status="REAL_LLM",
        full_apps_contract_suite_passed=True,
    )

    assert result == {"receipt": tmp_path / "receipt.json"}
    assert calls == [
        {
            "artifact_dir": tmp_path,
            "section_id": "executive_summary",
            "runtime_payload": {"run_id": "r1"},
            "proof_bundle": {"proof_eligible": True},
            "runtime_generation_status": "REAL_LLM",
            "full_apps_contract_suite_passed": True,
        }
    ]
