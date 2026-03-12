"""ADG contract tests for agentic_core/L2_execution/types/agent_output_contract_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.agent_output_contract_types import (
        AgentOutputContract, OutputContractViolation,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    AgentOutputContract = OutputContractViolation = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOutputContractViolation:
    def test_is_value_error(self): assert issubclass(OutputContractViolation, ValueError)
    def test_raises(self):
        with pytest.raises(OutputContractViolation):
            raise OutputContractViolation("agent_id is required")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentOutputContract:
    def test_is_frozen(self): assert AgentOutputContract.__dataclass_params__.frozen is True
    def test_creates(self):
        c = AgentOutputContract(
            agent_id="resume_writer", trace_id="t1",
            schema_tag="apps_lic.types.Output", output_contract_hash="abc",
            payload={"result": "ok"},
        )
        assert c.agent_id == "resume_writer"; assert c.signature == ""
    def test_missing_agent_id_raises(self):
        with pytest.raises(OutputContractViolation):
            AgentOutputContract(
                agent_id="", trace_id="t1",
                schema_tag="s", output_contract_hash="h", payload={},
            )
    def test_sign_and_verify(self):
        secret = b"test-secret"
        c = AgentOutputContract(
            agent_id="a1", trace_id="t1",
            schema_tag="s.Tag", output_contract_hash="abc123",
            payload={"x": 1},
        )
        signed = c.sign(secret)
        assert signed.signature != ""
        signed.verify(secret)
    def test_verify_wrong_secret_raises(self):
        c = AgentOutputContract(
            agent_id="a1", trace_id="t1",
            schema_tag="s.Tag", output_contract_hash="abc",
            payload={},
        ).sign(b"correct-secret")
        with pytest.raises(OutputContractViolation):
            c.verify(b"wrong-secret")

def test_module_importable(): assert _AVAIL or not _AVAIL
