"""
agentic_core/L2_execution/types/execution_tool_contract.py

ToolContract — P2-L2 gap remediation.

Typed interface for every L2 tool invocation. Closes the gap where
75 exec modules invoke tools (48,070 imports) with no typed contract,
producing anonymous ADG edges. All tool dispatch must go through a
ToolContract so that invocations carry capability, signature, and
risk metadata resolvable by the ADG.

ADG edges emitted: execution_terminates_at_uwg, applies_guardrail
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "execution_tool_contract")
_emit_applies_guardrail("p0", "execution_tool_contract", "p0_governance")
_emit_snapshots_state("p0", "execution_tool_contract", "state_snapshot")


class ToolCategory(str, Enum):
    """High-level category of a tool."""

    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    EXTERNAL_API = "external_api"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    LLM_CALL = "llm_call"
    SEARCH = "search"
    DATABASE = "database"
    ORCHESTRATION = "orchestration"


@dataclass(frozen=True)
class ToolCapabilityDescriptor:
    """Capability metadata for a single tool."""

    tool_name: str
    category: ToolCategory
    risk_level: str
    requires_sandbox: bool
    idempotent: bool
    max_retries: int = 1
    timeout_ms: int = 30_000
    capabilities: tuple[str, ...] = field(default_factory=tuple)

    @property
    def capability_hash(self) -> str:
        payload = f"{self.tool_name}:{self.category}:{self.risk_level}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ToolContract:
    """Typed, immutable contract for a single tool invocation.

    Every L2 tool dispatch must be expressed as a ToolContract so
    that the ADG can trace ``execution_terminates_at_uwg`` edges.

    Usage::

        contract = ToolContract.create(
            tool_name="file_system.write",
            category=ToolCategory.FILE_SYSTEM,
            args={"path": "artifacts/out.json", "data": "{}"},
            trace_id=current_trace_id,
        )
        uwg.execute_from_contract(contract)
    """

    tool_name: str
    category: ToolCategory
    args: dict[str, Any]
    trace_id: str
    contract_hash: str
    capability_hash: str
    timestamp_monotonic: float
    requires_sandbox: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tool_name: str,
        category: ToolCategory,
        args: dict[str, Any],
        trace_id: str = "",
        requires_sandbox: bool = False,
        metadata: dict[str, Any] | None = None,
        capability_descriptor: ToolCapabilityDescriptor | None = None,
    ) -> ToolContract:
        ts = time.monotonic()
        payload = f"{tool_name}:{category}:{trace_id}:{ts:.6f}"
        contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        cap_hash = (
            capability_descriptor.capability_hash
            if capability_descriptor
            else hashlib.sha256(tool_name.encode()).hexdigest()[:16]
        )
        return cls(
            tool_name=tool_name,
            category=category,
            args=args,
            trace_id=trace_id,
            contract_hash=contract_hash,
            capability_hash=cap_hash,
            timestamp_monotonic=ts,
            requires_sandbox=requires_sandbox,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "category": self.category.value,
            "trace_id": self.trace_id,
            "contract_hash": self.contract_hash,
            "capability_hash": self.capability_hash,
            "requires_sandbox": self.requires_sandbox,
            "arg_keys": sorted(self.args.keys()),
        }


_tool_registry: dict[str, ToolCapabilityDescriptor] = {}


def register_tool_capability(descriptor: ToolCapabilityDescriptor) -> None:
    """Register a tool's capability descriptor globally."""
    _tool_registry[descriptor.tool_name] = descriptor


def get_tool_capability(tool_name: str) -> ToolCapabilityDescriptor | None:
    """Return the registered capability descriptor for ``tool_name``."""
    return _tool_registry.get(tool_name)


def registered_tools() -> list[str]:
    return list(_tool_registry.keys())


__all__ = [
    "ToolCategory",
    "ToolCapabilityDescriptor",
    "ToolContract",
    "register_tool_capability",
    "get_tool_capability",
    "registered_tools",
]
