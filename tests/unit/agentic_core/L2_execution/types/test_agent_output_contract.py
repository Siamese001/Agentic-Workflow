"""Contract tests for AgentOutputContract (spec [7])."""

import pytest

pytestmark = pytest.mark.unit_min_deps

from pydantic import BaseModel

from agentic_core.L2_execution.types.agent_output_contract_types import (
    AgentOutputContract,
    OutputContractViolation,
    wrap_output,
)

SECRET = b"test-l2-output-secret"


class _FakeOutput(BaseModel):
    result: str
    score: float


def test_wrap_output_produces_signed_contract():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    assert contract.agent_id == "MyAgent"
    assert contract.trace_id == "trace-1"
    assert "FakeOutput" in contract.schema_tag
    assert len(contract.output_contract_hash) == 64
    assert len(contract.signature) == 64


def test_verify_roundtrip():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    contract.verify(SECRET)  # must not raise
    assert True  # no-exception contract


def test_different_payloads_produce_different_hashes():
    c1 = wrap_output("A", "t", _FakeOutput(result="a", score=0.1), SECRET)
    c2 = wrap_output("A", "t", _FakeOutput(result="b", score=0.2), SECRET)
    assert c1.output_contract_hash != c2.output_contract_hash


def test_tampered_contract_rejected():
    contract = wrap_output("MyAgent", "trace-1", _FakeOutput(result="ok", score=0.9), SECRET)
    tampered = AgentOutputContract(
        agent_id=contract.agent_id,
        trace_id=contract.trace_id,
        schema_tag=contract.schema_tag,
        output_contract_hash=contract.output_contract_hash,
        payload=contract.payload,
        signature="deadbeef" * 8,
    )
    with pytest.raises(OutputContractViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_missing_agent_id_rejected():
    with pytest.raises(OutputContractViolation, match="agent_id"):
        AgentOutputContract(
            agent_id="",
            trace_id="t",
            schema_tag="foo.Bar",
            output_contract_hash="a" * 64,
            payload={},
        )


def test_missing_schema_tag_rejected():
    with pytest.raises(OutputContractViolation, match="schema_tag"):
        AgentOutputContract(
            agent_id="A",
            trace_id="t",
            schema_tag="",
            output_contract_hash="a" * 64,
            payload={},
        )
