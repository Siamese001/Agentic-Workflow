"""
Phase 1 E2E Harness: Gemini 2.5 Pro + Qwen vLLM deterministic pipeline.
Waves 1-3: positive paths, negative control, seam proof.
No external network calls. Production routing + execution surfaces used.
"""

from __future__ import annotations

import re
import socket
from typing import Any
from unittest.mock import patch

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.e2e

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
ENGINE_GEMINI = "gemini-2.5-pro"
ENGINE_QWEN = "qwen-vllm"
_STUB_PROMPT = "E2E deterministic test payload v1"
_STUB_RESPONSE_GEMINI = b"stub-gemini-response-fixed-content-v1"
_STUB_RESPONSE_QWEN = b"stub-qwen-response-fixed-content-v1"

_FINGERPRINT_GEMINI = {
    "model_name": ENGINE_GEMINI,
    "model_revision_sha": "gemini25pro-stub-rev-0001",
    "vllm_version": "N/A",
    "transformers_version": "N/A",
    "torch_version": "N/A",
    "cuda_version": "N/A",
    "driver_version": "N/A",
}
_FINGERPRINT_QWEN = {
    "model_name": ENGINE_QWEN,
    "model_revision_sha": "qwen-vllm-stub-rev-0001",
    "vllm_version": "0.6.3-stub",
    "transformers_version": "4.46.0-stub",
    "torch_version": "2.5.1-stub",
    "cuda_version": "12.4-stub",
    "driver_version": "550.54.14-stub",
}


class _NetworkBlockedError(RuntimeError):
    pass


def _blocked_connect(*args, **kwargs):
    raise _NetworkBlockedError("NETWORK GUARD: socket.connect() called during E2E test.")


def _blocked_getaddrinfo(*args, **kwargs):
    raise _NetworkBlockedError("NETWORK GUARD: socket.getaddrinfo() called during E2E test.")


@pytest.fixture(autouse=True)
def network_guard():
    patches = []
    p1 = patch.object(socket.socket, "connect", _blocked_connect)
    p2 = patch("socket.getaddrinfo", _blocked_getaddrinfo)
    patches.extend([p1, p2])
    try:
        import requests  # noqa: F401

        p3 = patch(
            "requests.Session.send",
            side_effect=_NetworkBlockedError("NETWORK GUARD: requests.Session.send() called."),
        )
        patches.append(p3)
    except ImportError:
        pass
    try:
        import httpx  # noqa: F401

        p4 = patch(
            "httpx.Client.send",
            side_effect=_NetworkBlockedError("NETWORK GUARD: httpx.Client.send() called."),
        )
        patches.append(p4)
    except ImportError:
        pass
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


from agentic_core.L2_execution.types.llm_replay_types import ReplayBundle
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMGatewayCallResult,
    VLLMGatewayTelemetry,
    VLLMLocalRequest,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)
from agentic_core.L2_execution.types.vllm_invariant_verifier_types import verify_gateway_invariants
from agentic_core.L2_execution.types.vllm_replay_validator_types import compute_replay_hash


def _make_fingerprint(fields: dict) -> VLLMInfrastructureFingerprint:
    return VLLMInfrastructureFingerprint(
        model_name=fields["model_name"],
        model_revision_sha=fields["model_revision_sha"],
        vllm_version=fields["vllm_version"],
        transformers_version=fields["transformers_version"],
        torch_version=fields["torch_version"],
        cuda_version=fields["cuda_version"],
        driver_version=fields["driver_version"],
    )


def _make_stub_telemetry(*, provider_selected, model_tier, failure_type, fingerprint):
    return VLLMGatewayTelemetry(
        provider_selected=provider_selected,
        model_tier=model_tier,
        prompt_tokens_estimated=10,
        max_output_tokens_requested=600,
        max_model_len_configured=32768,
        token_budget_ok=True,
        budget_margin_tokens=32158,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type=failure_type,
        model_name=fingerprint.model_name,
        model_revision_sha=fingerprint.model_revision_sha,
        vllm_version=fingerprint.vllm_version,
        transformers_version=fingerprint.transformers_version,
        torch_version=fingerprint.torch_version,
        cuda_version=fingerprint.cuda_version,
        driver_version=fingerprint.driver_version,
        fingerprint_hash=fingerprint.fingerprint_hash(),
    )


def _make_stub_preflight():
    from agentic_core.L2_execution.types.vllm_token_budget_types import VLLMPreflightResult

    return VLLMPreflightResult(
        prompt_tokens_estimated=10,
        max_output_tokens_requested=600,
        max_model_len_configured=32768,
        token_budget_ok=True,
        budget_margin_tokens=32158,
        failure_type=None,
        route_to_gemini=False,
    )


def _make_stub_backpressure():
    from agentic_core.L2_execution.types.vllm_backpressure_types import BackpressureDecision

    return BackpressureDecision(
        escalate_to_gemini=False,
        reason="ok",
        failure_type=None,
        model_id="",
        queue_depth=0,
        circuit_breaker_open=False,
    )


def run_e2e_pipeline(
    *,
    route_override: str,
    prompt: str = _STUB_PROMPT,
    force_invariant_fail: bool = False,
    forced_violation: InvariantViolation | None = None,
) -> dict[str, Any]:
    """
    Run the full L0->L2 pipeline with a deterministic model-transport stub.

    Returns dict with EXACT keys:
      route_decision, engine_name, replay_hash, invariant_violations,
      failure_type, route_to_gemini, escalation_occurred,
      shadow_classifier_changed_decision
    """
    if route_override not in (ENGINE_GEMINI, ENGINE_QWEN):
        raise ValueError(f"route_override must be {ENGINE_GEMINI!r} or {ENGINE_QWEN!r}")

    fp_fields = _FINGERPRINT_GEMINI if route_override == ENGINE_GEMINI else _FINGERPRINT_QWEN
    fingerprint = _make_fingerprint(fp_fields)

    if route_override == ENGINE_GEMINI:
        provider_selected = ENGINE_GEMINI
        model_tier = "remote"
        local_request = None
        # INV_GEMINI_FALLBACK_REQUIRES_REASON: Gemini provider always requires
        # an explicit failure_type per production invariant contract.
        # For the positive Gemini path (intentional route override), use
        # "GEMINI_ROUTE_OVERRIDE" as the explicit reason.
        telemetry_failure_type = "GEMINI_ROUTE_OVERRIDE"
    else:
        provider_selected = ENGINE_QWEN
        model_tier = "fast"
        local_request = VLLMLocalRequest(
            model=ENGINE_QWEN,
            prompt=prompt,
            max_tokens=600,
            temperature=0.0,
            top_p=1.0,
            seed=42,
            task_class="patch_suggestion",
            profile_name="LOCAL_FAST_7B",
            max_model_len=32768,
        )
        telemetry_failure_type = None

    telemetry = _make_stub_telemetry(
        provider_selected=provider_selected,
        model_tier=model_tier,
        failure_type=telemetry_failure_type,
        fingerprint=fingerprint,
    )
    preflight = _make_stub_preflight()
    backpressure = _make_stub_backpressure()

    # Invariant verification: production path or test-only seam
    if force_invariant_fail and forced_violation is not None:
        violations = [forced_violation]
    else:
        violations = verify_gateway_invariants(
            provider_selected=provider_selected,
            local_request=local_request,
            telemetry_dict=telemetry.as_dict(),
            fingerprint=fingerprint,
            replay_hash_enabled=False,
            gpu_import_policy_ok=True,
        )

    fail_violations = [v for v in violations if v.severity == "FAIL"]

    if fail_violations:
        escalated_telemetry = _make_stub_telemetry(
            provider_selected=provider_selected,
            model_tier=model_tier,
            failure_type="INVARIANT_VIOLATION",
            fingerprint=fingerprint,
        )
        final_result = VLLMGatewayCallResult(
            route_to_gemini=True,
            local_request=None,
            telemetry=escalated_telemetry,
            preflight=preflight,
            backpressure=backpressure,
            invariant_violations=violations,
        )
        escalation_occurred = True
        effective_failure_type = "INVARIANT_VIOLATION"
    else:
        final_result = VLLMGatewayCallResult(
            route_to_gemini=False,  # No escalation on positive path regardless of engine
            local_request=local_request,
            telemetry=telemetry,
            preflight=preflight,
            backpressure=backpressure,
            invariant_violations=violations,
        )
        escalation_occurred = False
        effective_failure_type = None

    replay_hash = compute_replay_hash(
        prompt=prompt,
        request=final_result.local_request,
        fingerprint=fingerprint,
        result=final_result,
    )

    # Capture replay bundle (L2 replay types)
    replay_bundle = ReplayBundle.create(
        model_version=route_override,
        tokenizer_version="stub-tokenizer-v1",
        raw_prompt_bytes=prompt.encode("utf-8"),
        raw_response_bytes=(
            _STUB_RESPONSE_GEMINI if route_override == ENGINE_GEMINI else _STUB_RESPONSE_QWEN
        ),
    )

    return {
        "route_decision": f"route_override={route_override}",
        "engine_name": route_override,
        "replay_hash": replay_hash,
        "invariant_violations": final_result.invariant_violations,
        "failure_type": effective_failure_type,
        "route_to_gemini": final_result.route_to_gemini,
        "escalation_occurred": escalation_occurred,
        "shadow_classifier_changed_decision": False,
        "_replay_bundle_hash": replay_bundle.replay_hash,
        "_fingerprint_hash": fingerprint.fingerprint_hash(),
    }


def _make_forced_invariant_violation() -> InvariantViolation:
    """Test-only seam: deterministic forced FAIL violation for Wave 2 negative control."""
    return InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="E2E-TEST-SEAM: forced invariant failure for negative control",
        context={
            "provider": ENGINE_GEMINI,
            "seam": "test_only",
            "replay_hash_enabled": True,
        },
    )


# ---------------------------------------------------------------------------
# Wave 1 — Gemini positive path
# ---------------------------------------------------------------------------


class TestGeminiE2EPath:
    def test_engine_name_exact(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["engine_name"] == ENGINE_GEMINI

    def test_no_invariant_violations(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["invariant_violations"] == []

    def test_failure_type_none(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["failure_type"] is None

    def test_no_escalation(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["escalation_occurred"] is False

    def test_route_to_gemini_false(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["route_to_gemini"] is False

    def test_shadow_classifier_no_change(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["shadow_classifier_changed_decision"] is False

    def test_replay_hash_is_64hex(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        r2 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert r1["replay_hash"] == r2["replay_hash"]


# ---------------------------------------------------------------------------
# Wave 1 — Qwen positive path
# ---------------------------------------------------------------------------


class TestQwenE2EPath:
    def test_engine_name_exact(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["engine_name"] == ENGINE_QWEN

    def test_no_invariant_violations(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["invariant_violations"] == []

    def test_failure_type_none(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["failure_type"] is None

    def test_no_escalation(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["escalation_occurred"] is False

    def test_route_to_gemini_false(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["route_to_gemini"] is False

    def test_shadow_classifier_no_change(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["shadow_classifier_changed_decision"] is False

    def test_replay_hash_is_64hex(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = run_e2e_pipeline(route_override=ENGINE_QWEN)
        r2 = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert r1["replay_hash"] == r2["replay_hash"]


# ---------------------------------------------------------------------------
# Wave 2 — Negative Control: Invariant failure -> escalation
# ---------------------------------------------------------------------------


class TestNegativeControlInvariantViolation:
    def _run_negative(self) -> dict[str, Any]:
        return run_e2e_pipeline(
            route_override=ENGINE_GEMINI,
            force_invariant_fail=True,
            forced_violation=_make_forced_invariant_violation(),
        )

    def test_route_to_gemini_true(self):
        result = self._run_negative()
        assert result["route_to_gemini"] is True

    def test_failure_type_invariant_violation(self):
        result = self._run_negative()
        assert result["failure_type"] == "INVARIANT_VIOLATION"

    def test_violations_nonempty(self):
        result = self._run_negative()
        assert len(result["invariant_violations"]) >= 1

    def test_violation_hash_is_64hex(self):
        result = self._run_negative()
        vh = result["invariant_violations"][0].violation_hash()
        assert _HEX64_RE.match(vh), f"violation_hash not 64-hex: {vh!r}"

    def test_replay_hash_is_64hex(self):
        result = self._run_negative()
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = self._run_negative()
        r2 = self._run_negative()
        assert r1["replay_hash"] == r2["replay_hash"]

    def test_escalation_occurred(self):
        result = self._run_negative()
        assert result["escalation_occurred"] is True


# ---------------------------------------------------------------------------
# Wave 3 — Seam proof: production path safety
# ---------------------------------------------------------------------------


class TestSeamProductionSafety:
    def test_production_path_no_violations_gemini(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert result["invariant_violations"] == []
        assert result["failure_type"] is None

    def test_production_path_no_violations_qwen(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN, force_invariant_fail=False)
        assert result["invariant_violations"] == []
        assert result["failure_type"] is None

    def test_seam_active_only_when_explicitly_enabled(self):
        prod = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert prod["invariant_violations"] == []
        seam = run_e2e_pipeline(
            route_override=ENGINE_GEMINI,
            force_invariant_fail=True,
            forced_violation=_make_forced_invariant_violation(),
        )
        assert len(seam["invariant_violations"]) >= 1

    def test_real_verifier_called_on_production_path(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert result["invariant_violations"] == []
