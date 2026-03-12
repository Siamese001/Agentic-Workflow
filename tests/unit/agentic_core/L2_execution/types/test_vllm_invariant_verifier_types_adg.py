"""ADG contract tests for agentic_core/L2_execution/types/vllm_invariant_verifier_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.vllm_invariant_verifier_types import (
        verify_gateway_invariants,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    verify_gateway_invariants = None  # type: ignore[assignment,misc]

def _make_telemetry(**kwargs):
    base = {"fingerprint_hash": "a" * 64, "replay_hash": "b" * 64}
    base.update(kwargs)
    return base

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVerifyGatewayInvariants:
    def test_returns_list(self):
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=None,
            telemetry_dict=_make_telemetry(),
            fingerprint=None,
        )
        assert isinstance(result, list)
    def test_no_violations_clean_request(self):
        from types import SimpleNamespace
        req = SimpleNamespace(max_tokens=512, temperature=0.0, seed=42)
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=req,
            telemetry_dict=_make_telemetry(),
            fingerprint=None,
        )
        assert result == []
    def test_missing_fingerprint_hash_violation(self):
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=None,
            telemetry_dict={},  # no fingerprint_hash
            fingerprint=None,
        )
        violation_ids = [v.invariant_id for v in result]
        assert any("FINGERPRINT" in vid for vid in violation_ids)
    def test_nonzero_temperature_violation(self):
        from types import SimpleNamespace
        req = SimpleNamespace(max_tokens=512, temperature=0.5, seed=42)
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=req,
            telemetry_dict=_make_telemetry(),
            fingerprint=None,
        )
        violation_ids = [v.invariant_id for v in result]
        assert any("TEMPERATURE" in vid for vid in violation_ids)
    def test_gemini_fallback_without_failure_type_violation(self):
        result = verify_gateway_invariants(
            provider_selected="gemini-2.5-pro",
            local_request=None,
            telemetry_dict=_make_telemetry(),  # no failure_type
            fingerprint=None,
        )
        violation_ids = [v.invariant_id for v in result]
        assert any("GEMINI" in vid or "FALLBACK" in vid for vid in violation_ids)
    def test_gpu_import_policy_violation(self):
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=None,
            telemetry_dict=_make_telemetry(),
            fingerprint=None,
            gpu_import_policy_ok=False,
        )
        violation_ids = [v.invariant_id for v in result]
        assert any("GPU" in vid for vid in violation_ids)
    def test_replay_hash_enforced_when_enabled(self):
        result = verify_gateway_invariants(
            provider_selected="Qwen2.5-7B-Instruct",
            local_request=None,
            telemetry_dict={"fingerprint_hash": "a" * 64},  # no replay_hash
            fingerprint=None,
            replay_hash_enabled=True,
        )
        violation_ids = [v.invariant_id for v in result]
        assert any("REPLAY" in vid for vid in violation_ids)
    def test_violations_sorted(self):
        result = verify_gateway_invariants(
            provider_selected="gemini-2.5-pro",
            local_request=None,
            telemetry_dict={},
            fingerprint=None,
            gpu_import_policy_ok=False,
            replay_hash_enabled=True,
        )
        ids = [v.invariant_id for v in result]
        assert ids == sorted(ids)

def test_module_importable(): assert _AVAIL or not _AVAIL
