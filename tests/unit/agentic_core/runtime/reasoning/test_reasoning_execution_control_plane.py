"""Tests: governed reasoning execution resolver + gateway seam."""

from __future__ import annotations

import json
import pathlib

import pytest

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    ProviderConfig,
    ProviderType,
    SovereignLLMGateway,
)
from agentic_core.L2_execution.reasoning import AuthorityLevel, AuthoritySlot, SlotAssemblyEngine
from agentic_core.runtime.reasoning.reasoning_control_requirement import ReceiptState
from agentic_core.runtime.reasoning.reasoning_control_resolver import (
    ReasoningGovernanceError,
    build_execution_plan,
    canonical_plan_digest,
    reasoning_quality_certification_allowed,
    resolve_gateway_receipt,
)
from agentic_core.runtime.reasoning.reasoning_execution_receipt import ReasoningExecutionReceipt
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities


class _FakePartialTransportProvider:
    """Forwards only temperature; orchestration kwargs are absorbed (strip simulation)."""

    def reasoning_transport_kw_forwarded(self) -> frozenset[str]:
        return frozenset({"temperature"})

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        tools_schema: list[dict] | None = None,
        **kwargs,
    ) -> dict[str, object]:
        return {
            "content": "{}",
            "tokens_used": 1,
            "model": "fake",
            "_reasoning_transport_observed": {"temperature": kwargs.get("temperature")},
        }

    def get_token_count(self, text: str) -> int:
        return max(1, len(text) // 4)


def test_reasoning_execution_receipt_from_primitive_roundtrip() -> None:
    plan = build_execution_plan({"temperature": 0.3})
    caps = TransportCapabilities(
        frozenset({"temperature", "max_tokens", "use_cache", "confidence_threshold"}),
    )
    rec = resolve_gateway_receipt(plan, caps, {"temperature": 0.3})
    d = rec.to_primitive()
    back = ReasoningExecutionReceipt.from_primitive(d)
    assert back is not None
    assert back.quality_certification_denied == rec.quality_certification_denied
    assert len(back.ledger) == len(rec.ledger)


def test_canonical_plan_digest_determinism() -> None:
    a = canonical_plan_digest({"b": 1, "a": 2})
    b = canonical_plan_digest({"a": 2, "b": 1})
    assert a == b


def test_optional_transport_unsupported_warn_only() -> None:
    plan = build_execution_plan({"temperature": 0.55})
    assert plan.plan_digest != ""
    caps = TransportCapabilities(frozenset())
    r = resolve_gateway_receipt(plan, caps, {})
    assert r.aggregate_warn is True
    assert r.aggregate_blocked is False


def test_policy_required_scratch_on_transport_blocked() -> None:
    rk = {"scratchpad": True, "temperature": 0.1}
    plan = build_execution_plan(rk)
    caps = TransportCapabilities(frozenset({"temperature"}))
    r = resolve_gateway_receipt(plan, caps, {"scratchpad": True, "temperature": 0.1})
    assert r.aggregate_blocked is True
    row = next(x for x in r.ledger if x.control_name == "scratchpad_transport_guard")
    assert row.receipt_state == ReceiptState.UNSUPPORTED


def test_strip_simulation_quality_not_applied() -> None:
    plan = build_execution_plan({"cot_paths": 3, "temperature": 0.5})
    prov = _FakePartialTransportProvider()
    raw = prov.generate("", "", None, **dict(plan.requested_values))
    obs = raw["_reasoning_transport_observed"]
    assert isinstance(obs, dict)
    r = resolve_gateway_receipt(plan, TransportCapabilities.from_provider(prov), obs)
    assert reasoning_quality_certification_allowed(r) is False
    row = next(x for x in r.ledger if x.control_name == "cot_paths")
    assert row.receipt_state == ReceiptState.IGNORED


def test_self_consistency_row_records_requested_completed_counts_in_proved_reference() -> None:
    plan = build_execution_plan({"self_consistency_samples": 5.0, "temperature": 0.2})
    rec = resolve_gateway_receipt(plan, TransportCapabilities(frozenset({"temperature"})), {"temperature": 0.2})
    row = next(x for x in rec.ledger if x.control_name == "self_consistency_samples")
    assert row.receipt_state == ReceiptState.IGNORED
    payload = json.loads(row.proved_reference)
    assert payload["samples_requested"] == 5
    assert payload["samples_completed"] == 1


def test_reasoning_quality_certification_positive_path() -> None:
    rk = {"temperature": 0.3}
    plan = build_execution_plan(rk)
    caps = TransportCapabilities(
        frozenset({"temperature", "max_tokens", "use_cache", "confidence_threshold"}),
    )
    rec = resolve_gateway_receipt(plan, caps, {"temperature": 0.3})
    assert reasoning_quality_certification_allowed(rec) is True
    row = next(x for x in rec.ledger if x.control_name == "temperature")
    assert row.receipt_state == ReceiptState.APPLIED


def test_grep_bounded_no_apps_literals_under_runtime_reasoning() -> None:
    root = pathlib.Path(__file__).resolve().parents[5] / "agentic_core" / "runtime" / "reasoning"
    banned = ("apps_rg", "apps_lic", "apps_qna", "apps_research")
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in banned:
            assert token not in text, f"{token} leaked in {path}"


def test_grep_bounded_no_uwg_writes_runtime_reasoning() -> None:
    root = pathlib.Path(__file__).resolve().parents[5] / "agentic_core" / "runtime" / "reasoning"
    denied = ("uwg", "direct_l4_write", "l4_persist", "write_l4")
    for path in sorted(root.rglob("*.py")):
        lower = path.read_text(encoding="utf-8").lower()
        for token in denied:
            assert token not in lower, f"suspicious {token!r} token in {path}"


@pytest.fixture()
def assembled_artifact() -> object:
    eng = SlotAssemblyEngine(secret_key=b"test-secret")
    eng.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
    eng.add_slot(AuthoritySlot("U0", "User request", AuthorityLevel.ZERO, "L4"))
    return eng.assemble()


class TestGenerateWithReasoningGovernanceIntegration:
    def test_simple_tier_returns_receipt_with_quality_review(self, assembled_artifact) -> None:
        """Simple path requests cot_paths=1 — orchestration not executed -> review + cert denied."""
        gw = SovereignLLMGateway(secret_key=b"test-secret", verify_signatures=False)
        gw.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(provider_type=ProviderType.OPENAI, model="x"),
            provider_impl=_FakePartialTransportProvider(),
        )
        out = gw.generate_with_reasoning(
            assembled_artifact,
            complexity_tier="simple",
            provider=ProviderType.OPENAI,
        )
        rec = out["_reasoning_execution_receipt"]
        assert rec["aggregate_blocked"] is False
        assert rec["quality_certification_denied"] is True
        assert rec["aggregate_review"] is True

    def test_complex_tier_reflexion_policy_blocks(self, assembled_artifact) -> None:
        gw = SovereignLLMGateway(secret_key=b"test-secret", verify_signatures=False)
        gw.register_provider(
            ProviderType.OPENAI,
            ProviderConfig(provider_type=ProviderType.OPENAI, model="x"),
            provider_impl=_FakePartialTransportProvider(),
        )
        with pytest.raises(ReasoningGovernanceError):
            gw.generate_with_reasoning(
                assembled_artifact,
                complexity_tier="complex",
                provider=ProviderType.OPENAI,
            )
