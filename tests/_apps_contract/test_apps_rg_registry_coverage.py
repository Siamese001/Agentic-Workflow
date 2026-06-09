"""W4 contract tests for apps_rg registry coverage CI gate."""

from __future__ import annotations

from pathlib import Path

from ops_scripts.ci.check_apps_rg_registry_coverage import (
    EXPECTED_PROOF_SOURCE,
    RegistryCoverageViolation,
    audit_apps_rg_registry_coverage,
    audit_gate_advertise_emit_coverage,
    audit_judge_registry_coverage,
    audit_lane_registry_coverage,
    audit_proof_source_literal_coverage,
)


def _codes(violations: list[RegistryCoverageViolation]) -> set[str]:
    return {v.code for v in violations}


def test_apps_rg_registry_coverage_gate_is_green() -> None:
    assert audit_apps_rg_registry_coverage() == []


def test_registry_coverage_gate_is_wired_into_contract_gates() -> None:
    gate_runner = Path("ops_scripts/ci/run_contract_gates.py").read_text(encoding="utf-8")
    assert "ops_scripts/ci/check_apps_rg_registry_coverage.py" in gate_runner


def test_lane_registry_red_path_missing_generated_lane() -> None:
    violations = audit_lane_registry_coverage(
        generated_lanes=("lane_a", "lane_b"),
        lane_spec_ids=("lane_a",),
        alignment_ids=("lane_a", "lane_b"),
        rubric_lane_ids=("lane_a", "lane_b"),
        policy_section_ids=("lane_a", "lane_b"),
    )
    assert "registry_missing_ssot_keys" in _codes(violations)
    assert any("lane_b" in v.detail for v in violations)


def test_lane_registry_allows_locked_non_generated_alignment_rows() -> None:
    violations = audit_lane_registry_coverage(
        generated_lanes=("lane_a",),
        lane_spec_ids=("lane_a",),
        alignment_ids=("lane_a", "education", "certifications", "early_career"),
        rubric_lane_ids=("lane_a",),
        policy_section_ids=("lane_a",),
    )
    assert violations == []


def test_judge_registry_red_path_self_judge_in_required_roster() -> None:
    violations = audit_judge_registry_coverage(
        required_provider_keys=("gemini_pro", "openai_chatgpt", "anthropic_claude"),
        harness_default_csv="gemini_pro,openai_chatgpt,anthropic_claude",
        transport_provider_keys=("gemini_pro", "openai_chatgpt", "anthropic_claude"),
        policy_provider_map={
            "executive_summary": (
                "gemini_pro",
                "openai_chatgpt",
                "anthropic_claude",
            )
        },
    )
    assert "self_judge_in_required_roster" in _codes(violations)
    assert "self_judge_in_section_policy" in _codes(violations)


def test_judge_registry_red_path_harness_default_drift() -> None:
    violations = audit_judge_registry_coverage(
        required_provider_keys=("gemini_pro", "openai_chatgpt"),
        harness_default_csv="gemini_pro",
        transport_provider_keys=("gemini_pro", "openai_chatgpt"),
        policy_provider_map={"executive_summary": ("gemini_pro", "openai_chatgpt")},
    )
    assert "harness_default_not_policy_roster" in _codes(violations)


def test_gate_advertise_emit_red_path_missing_runtime_gate() -> None:
    violations = audit_gate_advertise_emit_coverage(
        generated_lanes=("lane_a",),
        advertised_gate_ids_by_lane={"lane_a": {"x2_lane_a_required"}},
        runtime_gate_ids_by_lane={"lane_a": set()},
    )
    assert "advertised_gate_not_emitted" in _codes(violations)
    assert "x2_lane_a_required" in violations[0].detail


def test_proof_source_literal_red_path(tmp_path: Path) -> None:
    drift_file = tmp_path / "proof_source_drift.py"
    drift_file.write_text(f'PROOF_SOURCE = "{EXPECTED_PROOF_SOURCE}"\n', encoding="utf-8")
    violations = audit_proof_source_literal_coverage(scan_paths=(drift_file,))
    assert "proof_source_literal_retyped" in _codes(violations)
