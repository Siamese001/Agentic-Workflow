"""W2b Phase P7 — tests for composer + verifier rejection matrix.

Covers W2b § 7 matrix cases T3-T8 (unit tests). T1 and T2 (live-provider
acceptance) require ``pytest.mark.integration`` and are skipped when the
live endpoints are not available.

Plan: docs/archive/windsurf/legacy-tree/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 7
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compose_semantic_cache_subclaims import (  # noqa: E402
    _validate_live_provider_attestation,
)


def _canonical_att(**overrides):
    att = {
        "schema_version": 1,
        "attestation_kind": "live_provider_allow_path",
        "provider": "local_qwen",
        "model_id": "Qwen2.5-7B-Instruct",
        "model_version": "Qwen2.5-7B-Instruct",
        "rubric_path": "config/certification/llm_judge_rubric.md",
        "rubric_hash_sha256": "a" * 64,
        "response_hash_sha256": "b" * 64,
        "response_hash_mode": "paraphrase_tolerant",
        "verdict": "SAFE",
        "confidence": 0.9,
        "latency_ms": 120.0,
        "wall_clock_utc": "2026-05-01T00:00:00Z",
        "llm_judge_invocation_count": 1,
        "veto_stage_class": "LLMJudgeVeto",
        "deterministic_proof_stage_used": False,
        "x3_disposition": "X3D",
        "safe_reuse_allow": True,
        "mock_safe_used": False,
        "approved_provider": True,
        "env_probe": {
            "LLMJUDGEVETO_APPROVED_MOCK_SAFE": "unset",
            "LOCAL_QWEN_ENDPOINT": "http://localhost:8000/v1",
            "ANTHROPIC_API_KEY_present": False,
        },
    }
    att.update(overrides)
    return att


def _write_att(tmp_path, payload=None):
    payload = payload if payload is not None else _canonical_att()
    p = tmp_path / "live_provider_attestation.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


class TestComposerAttestationGate:
    """T4-T8 matrix cases exercised via the composer helper."""

    def test_canonical_attestation_passes(self, tmp_path):
        p = _write_att(tmp_path)
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is True
        assert reason == ""

    def test_missing_file_rejects(self, tmp_path):
        p = tmp_path / "live_provider_attestation.json"
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_MISSING_ATTESTATION"

    def test_malformed_json_rejects(self, tmp_path):
        p = tmp_path / "live_provider_attestation.json"
        p.write_text("{ not valid json", encoding="utf-8")
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_ATTESTATION_SCHEMA_INVALID"

    def test_mock_safe_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(
            provider="mock_safe", mock_safe_used=True, approved_provider=False,
        ))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_MOCK_SAFE_IN_CERTIFICATION"

    def test_unapproved_provider_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(
            provider="some_random_model", approved_provider=False,
        ))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_UNAPPROVED_PROVIDER"

    def test_deterministic_proof_stage_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(
            deterministic_proof_stage_used=True,
        ))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_DETERMINISTIC_PROOF_STAGE_IN_CERTIFICATION"

    def test_wrong_veto_stage_class_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(
            veto_stage_class="DeterministicProofStage",
        ))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_UNAPPROVED_VETO_STAGE_CLASS"

    def test_non_safe_verdict_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(verdict="UNCERTAIN"))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_NON_SAFE_AS_ALLOW"

    def test_not_allow_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(safe_reuse_allow=False))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_NON_SAFE_AS_ALLOW"

    def test_non_x3d_disposition_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(x3_disposition="X3A"))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_NON_SAFE_AS_ALLOW"

    def test_empty_rubric_hash_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(rubric_hash_sha256=""))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_SAFE_WITHOUT_RUBRIC_HASH"

    def test_empty_response_hash_rejects(self, tmp_path):
        p = _write_att(tmp_path, _canonical_att(response_hash_sha256=""))
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_SAFE_WITHOUT_RESPONSE_HASH"

    def test_missing_required_key_rejects(self, tmp_path):
        att = _canonical_att()
        del att["rubric_hash_sha256"]
        p = _write_att(tmp_path, att)
        ok, reason = _validate_live_provider_attestation(p)
        assert ok is False
        assert reason == "REJECT_ATTESTATION_SCHEMA_INVALID"


class TestApprovedProviderSet:
    def test_w2b_approved_set_contains_exactly_two(self):
        from scripts.compose_semantic_cache_subclaims import W2B_APPROVED_PROVIDERS
        assert W2B_APPROVED_PROVIDERS == frozenset({"local_qwen", "anthropic_haiku"})
        assert "mock_safe" not in W2B_APPROVED_PROVIDERS


# ───────────────────────────────────────────────────────────────────────
# Live-provider integration tests — skip unless the provider is reachable.
# These correspond to T1 and T2 in the W2b § 7 matrix. They exercise the
# full probe_integrated_runtime_safe_reuse.py end-to-end.
# ───────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("W2B_LIVE_LOCAL_QWEN") == "1",
    reason="requires W2B_LIVE_LOCAL_QWEN=1 and a running vLLM endpoint",
)
def test_local_qwen_allow_path_accepts_rtc_req_056():
    """T1 — live vLLM local_qwen produces SAFE → ACCEPTED.

    Requires the operator to have confirmed vLLM is running on
    localhost:8000. Exits with a clear skip message otherwise.
    """
    result = subprocess.run(
        [sys.executable,
         "tools/certification/evidence/probe_integrated_runtime_safe_reuse.py"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300, check=False,
    )
    assert result.returncode == 0
    ledger = json.loads(
        (REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
         / "path_proofs_ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["c_primary_allow"]["pass"] is True
    assert ledger["c_primary_allow"]["provider_attempted"] == "local_qwen"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("W2B_LIVE_ANTHROPIC") == "1"
    or not os.environ.get("ANTHROPIC_API_KEY"),
    reason="requires W2B_LIVE_ANTHROPIC=1 and ANTHROPIC_API_KEY set",
)
def test_anthropic_haiku_allow_path_accepts_rtc_req_056():
    """T2 — live Anthropic Haiku produces SAFE → ACCEPTED."""
    env = os.environ.copy()
    # Ensure local_qwen is NOT in the way — the probe ladder picks it first.
    env["LOCAL_QWEN_ENDPOINT"] = "http://localhost:65535/v1"  # unreachable
    result = subprocess.run(
        [sys.executable,
         "tools/certification/evidence/probe_integrated_runtime_safe_reuse.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
        timeout=300, check=False, env=env,
    )
    assert result.returncode == 0
    ledger = json.loads(
        (REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
         / "path_proofs_ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["c_primary_allow"]["pass"] is True
    assert ledger["c_primary_allow"]["provider_attempted"] == "anthropic_haiku"
