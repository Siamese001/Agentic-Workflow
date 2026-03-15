"""AgentOutputContract — signed wrapper for every apps_* agent execute() return.

Spec contract [7]: every agent output must carry:
  - agent_id: stable registry key
  - trace_id: correlates back to InstructionPacket / SandboxEnvelope
  - schema_tag: dotted qualified name of the payload Pydantic model
  - output_contract_hash: SHA-256 of canonical payload bytes
  - signature: HMAC-SHA256 over the signable dict (excl. sig field)
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class OutputContractViolation(ValueError):
    """Raised when AgentOutputContract invariants are broken."""


@dataclass(frozen=True)
class AgentOutputContract:
    """Signed envelope for a single agent execute() call result."""

    agent_id: str
    trace_id: str
    schema_tag: str
    output_contract_hash: str
    payload: dict[str, Any]
    signature: str = field(default="")

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise OutputContractViolation("agent_id is required")
        if not self.schema_tag:
            raise OutputContractViolation("schema_tag is required")
        if not self.output_contract_hash:
            raise OutputContractViolation("output_contract_hash is required")

    def _signable_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "output_contract_hash": self.output_contract_hash,
            "schema_tag": self.schema_tag,
            "trace_id": self.trace_id,
        }

    def sign(self, secret: bytes) -> AgentOutputContract:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "AgentOutputContract.sign")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentOutputContract.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        return AgentOutputContract(
            agent_id=self.agent_id,
            trace_id=self.trace_id,
            schema_tag=self.schema_tag,
            output_contract_hash=self.output_contract_hash,
            payload=self.payload,
            signature=mac.hexdigest().lower(),
        )

    def verify(self, secret: bytes) -> None:
        if not self.signature:
            raise OutputContractViolation("signature absent")
        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        if not hmac.compare_digest(self.signature, mac.hexdigest().lower()):
            raise OutputContractViolation("signature mismatch")


def wrap_output(agent_id: str, trace_id: str, payload_model: Any, secret: bytes) -> AgentOutputContract:
    """Convenience: hash + sign a Pydantic model output."""
    schema_tag = f"{type(payload_model).__module__}.{type(payload_model).__qualname__}"
    payload_bytes = payload_model.model_dump_json(by_alias=False).encode("utf-8")
    contract_hash = hashlib.sha256(payload_bytes).hexdigest()
    contract = AgentOutputContract(
        agent_id=agent_id,
        trace_id=trace_id,
        schema_tag=schema_tag,
        output_contract_hash=contract_hash,
        payload=payload_model.model_dump(),
    )
    return contract.sign(secret)


__all__ = ["AgentOutputContract", "OutputContractViolation", "wrap_output"]
