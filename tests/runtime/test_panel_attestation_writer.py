"""Panel attestation writer tests — schema v3 + control-surface stamping.

Ensures ``_panel_attestation.build_panel_attestation`` emits:
  - ``attestation_schema_version == 3``
  - top-level ``control_surface == "llm_as_judge"``
  - top-level ``purpose == "certification"``
  - per-juror ``control_surface == "llm_as_judge"`` for every juror
  - all required per-juror fields enumerated in the gate

Per operator directive 2026-05-01 14:15 UTC-04:00.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from tools.certification.evidence._panel_attestation import (
    ATTESTATION_KIND,
    build_panel_attestation,
)
from tools.certification.safety.consensus_veto import JurorVerdict
from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    GEMINI_JUROR,
    OPENAI_JUROR,
)


def _mk_safe_verdicts() -> list[JurorVerdict]:
    return [
        JurorVerdict(
            juror_id=GEMINI_JUROR.juror_id,
            family=GEMINI_JUROR.provider_family,
            model_id=GEMINI_JUROR.model_id,
            verdict="SAFE",
            confidence=0.95,
            rationale="ok",
            latency_ms=1200.0,
            raw_response_sha256="aa" * 32,
        ),
        JurorVerdict(
            juror_id=ANTHROPIC_JUROR.juror_id,
            family=ANTHROPIC_JUROR.provider_family,
            model_id=ANTHROPIC_JUROR.model_id,
            verdict="SAFE",
            confidence=0.93,
            rationale="ok",
            latency_ms=1400.0,
            raw_response_sha256="bb" * 32,
        ),
        JurorVerdict(
            juror_id=OPENAI_JUROR.juror_id,
            family=OPENAI_JUROR.provider_family,
            model_id=OPENAI_JUROR.model_id,
            verdict="SAFE",
            confidence=0.91,
            rationale="ok",
            latency_ms=900.0,
            raw_response_sha256="cc" * 32,
        ),
    ]


@pytest.fixture
def panel_payload(tmp_path: Path) -> dict:
    """Build a panel attestation with all-SAFE jurors using a fake rubric path."""
    rubric = tmp_path / "rubric.md"
    rubric.write_text("rubric body", encoding="utf-8")
    logging.info("C3 write receipt: tests/runtime/test_panel_attestation_writer.py write side effect recorded")
    return build_panel_attestation(
        jurors=_mk_safe_verdicts(),
        final_consensus_verdict="SAFE",
        final_safe_reuse_allow=True,
        final_x3_disposition="X3D",
        rubric_path=rubric,
        request_text="What is the capital of France?",
        cache_candidate_text="What city is the capital of France?",
        invocation_count=3,
    )


class TestSchemaV3TopLevel:
    def test_schema_version_is_3(self, panel_payload):
        assert panel_payload["attestation_schema_version"] == 3

    def test_top_level_control_surface_is_llm_as_judge(self, panel_payload):
        assert panel_payload["control_surface"] == "llm_as_judge"

    def test_top_level_purpose_is_certification(self, panel_payload):
        assert panel_payload["purpose"] == "certification"

    def test_attestation_kind_is_panel(self, panel_payload):
        assert panel_payload["attestation_kind"] == ATTESTATION_KIND
        assert ATTESTATION_KIND == "rtc_req_056_consensus_jury_panel"

    def test_certification_scope_is_rtc_req_056(self, panel_payload):
        assert panel_payload["certification_scope"] == "RTC-REQ-056"


class TestPerJurorSurfaceStamp:
    def test_every_juror_has_control_surface(self, panel_payload):
        assert len(panel_payload["jurors"]) == 3
        for j in panel_payload["jurors"]:
            assert j["control_surface"] == "llm_as_judge"

    def test_juror_required_fields_present(self, panel_payload):
        required = {
            "juror_id",
            "control_surface",
            "provider_family",
            "provider",
            "model_id",
            "target_provider_family",
            "target_provider",
            "target_model_id",
            "provider_match_status",
            "model_match_status",
            "approved_provider",
            "verdict",
            "confidence",
            "latency_ms",
            "response_hash_sha256",
            "parse_status",
            "timeout_count",
            "error_count",
            "unknown_count",
            "unsafe_count",
            "parse_fail_count",
            "mock_safe_used",
            "deterministic_proof_stage_used",
            "raw_output_retention_mode",
        }
        for j in panel_payload["jurors"]:
            missing = required - set(j.keys())
            assert not missing, f"juror missing fields: {missing}"


class TestGateAcceptsWriterOutput:
    """Round-trip: the panel writer's output must pass the gate."""

    def test_writer_output_passes_gate(self, panel_payload):
        from tools.certification.safety.rtc_req_056_gate import (
            validate_panel_attestation,
        )
        result = validate_panel_attestation(panel_payload)
        assert result.accepted is True, (
            f"writer output rejected by gate: {result.reason_codes}"
        )
        assert result.row_status == "ACCEPTED"


class TestRequestAndPanelHashesStable:
    def test_request_hash_populated(self, panel_payload):
        assert len(panel_payload["request_hash_sha256"]) == 64

    def test_panel_response_hash_populated(self, panel_payload):
        assert len(panel_payload["panel_response_hash_sha256"]) == 64

    def test_artifact_hash_populated(self, panel_payload):
        assert len(panel_payload["artifact_hash"]) == 64
