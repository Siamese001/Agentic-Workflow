"""W2b Phase P7 — tests for _live_provider_attestation helper.

Exercises ``build_attestation_payload`` and ``write_attestation``. No
network calls. All tests run on unit path.

Plan: docs/archive/windsurf/legacy-tree/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 3, § 7
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence._live_provider_attestation import (  # noqa: E402
    APPROVED_PROVIDERS,
    ATTESTATION_SCHEMA_VERSION,
    build_attestation_payload,
    write_attestation,
)
from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID  # noqa: E402


@pytest.fixture
def rubric_file(tmp_path):
    p = tmp_path / "rubric.md"
    p.write_text("# Rubric\nSAFE: equivalent intent.\n", encoding="utf-8")
    return p


def _canonical_kwargs(rubric):
    return dict(
        provider="local_qwen",
        model_id=QWEN_LOCAL_MODEL_ID,
        model_version=QWEN_LOCAL_MODEL_ID,
        rubric_path=rubric,
        raw_response='{"verdict":"SAFE","confidence":0.9}',
        response_hash_mode="paraphrase_tolerant",
        verdict="SAFE",
        confidence=0.9,
        latency_ms=120.0,
        llm_judge_invocation_count=1,
        veto_stage_class="LLMJudgeVeto",
        deterministic_proof_stage_used=False,
        x3_disposition="X3D",
        safe_reuse_allow=True,
    )


class TestAttestationShape:
    def test_schema_version_matches(self, rubric_file):
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        assert p["schema_version"] == ATTESTATION_SCHEMA_VERSION

    def test_required_keys_present(self, rubric_file):
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        required = {
            "schema_version", "attestation_kind", "provider", "model_id",
            "rubric_hash_sha256", "response_hash_sha256", "response_hash_mode",
            "verdict", "confidence", "veto_stage_class",
            "deterministic_proof_stage_used", "x3_disposition",
            "safe_reuse_allow", "mock_safe_used", "approved_provider",
            "env_probe",
        }
        assert required.issubset(p.keys())

    def test_rubric_hash_is_sha256_hex(self, rubric_file):
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        h = p["rubric_hash_sha256"]
        assert isinstance(h, str) and len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_approved_flag_true_for_local_qwen(self, rubric_file):
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        assert p["approved_provider"] is True
        assert p["mock_safe_used"] is False
        assert p["provider"] in APPROVED_PROVIDERS

    def test_approved_flag_false_for_mock_safe(self, rubric_file):
        kw = _canonical_kwargs(rubric_file)
        kw["provider"] = "mock_safe"
        p = build_attestation_payload(**kw)
        assert p["mock_safe_used"] is True
        assert p["approved_provider"] is False

    def test_paraphrase_tolerant_hash_uses_parsed_verdict(self, rubric_file):
        kw = _canonical_kwargs(rubric_file)
        kw["raw_response"] = '{"verdict":"SAFE","confidence":0.9}'
        h1 = build_attestation_payload(**kw)["response_hash_sha256"]
        kw["raw_response"] = "Yes, SAFE with confidence 0.9 in different wording"
        h2 = build_attestation_payload(**kw)["response_hash_sha256"]
        # Paraphrase tolerance means hash stays stable across wordings
        # because the hash is computed from the parsed verdict object.
        assert h1 == h2

    def test_exact_hash_mode_changes_with_raw(self, rubric_file):
        kw = _canonical_kwargs(rubric_file)
        kw["response_hash_mode"] = "exact"
        kw["raw_response"] = "A"
        h1 = build_attestation_payload(**kw)["response_hash_sha256"]
        kw["raw_response"] = "B"
        h2 = build_attestation_payload(**kw)["response_hash_sha256"]
        assert h1 != h2


class TestAttestationEnvProbe:
    def test_env_probe_records_mock_safe_flag_state(self, rubric_file, monkeypatch):
        monkeypatch.delenv("LLMJUDGEVETO_APPROVED_MOCK_SAFE", raising=False)
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        assert p["env_probe"]["LLMJUDGEVETO_APPROVED_MOCK_SAFE"] == "unset"

    def test_env_probe_does_not_include_api_key_value(self, rubric_file, monkeypatch):
        secret = "sk-ant-12345-should-never-leak"
        monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        assert p["env_probe"]["ANTHROPIC_API_KEY_present"] is True
        # Serialize and check the secret doesn't appear anywhere
        assert secret not in json.dumps(p)


class TestAttestationWrite:
    def test_write_roundtrips(self, rubric_file, tmp_path):
        p = build_attestation_payload(**_canonical_kwargs(rubric_file))
        out = write_attestation(tmp_path, p)
        assert out.exists()
        restored = json.loads(out.read_text(encoding="utf-8"))
        assert restored == p
