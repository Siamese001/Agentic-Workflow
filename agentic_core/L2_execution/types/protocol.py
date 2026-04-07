"""
L2 Agent Protocol — Unified subphase interface for execute_ssot pipeline.

Defines the four-method taxonomy that every pipeline adapter must implement:
  pre_commit  — read-only fast gate (no mutations)
  validate    — deep read-only scan (may be slow)
  execute     — confidence-gated mutations (dry_run or live)
  heal        — confidence-gated residual repair (live)

These types are imported by ssot_adapters.py and execute_ssot.py.
No agent modules are imported here. Zero side effects at import time.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


@dataclass
class SubphaseResult:
    """Result from a single subphase execution."""

    violations: list[dict] = field(default_factory=list)
    fixed: list[dict] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""
    error: str | None = None


@dataclass
class AgentRunResult:
    """Aggregated result for one agent across all four subphases."""

    subphases: dict[str, SubphaseResult] = field(default_factory=dict)
    gated: bool = False
    gate_reason: str = ""
    error: str | None = None
    violations_total: int = 0
    mutations_applied: int = 0

    @property
    def has_error(self) -> bool:
        """True if any error occurred during execution."""
        return self.error is not None or any(
            sp.error is not None for sp in self.subphases.values()
        )


@runtime_checkable
class L2AgentProtocol(Protocol):
    """Protocol every pipeline adapter must satisfy."""

    def pre_commit(self, territory: str, ctx: object) -> SubphaseResult:
        """Read-only fast gate. Must never mutate filesystem."""
        ...

    def validate(self, territory: str, ctx: object) -> SubphaseResult:
        """Deep read-only scan. Must never mutate filesystem."""
        ...

    def execute(self, territory: str, ctx: object) -> SubphaseResult:
        """Confidence-gated mutations."""
        ...

    def heal(self, territory: str, ctx: object) -> SubphaseResult:
        """Confidence-gated residual repair."""
        ...


PIPELINE_SUBPHASES: tuple[str, ...] = ("pre_commit", "validate", "execute", "heal")


def compute_pipeline_digest(
    pipeline_order: list[str],
    adapter_keys: list[str],
    territory: str,
    heal: bool,
    enable_llm: bool,
    tamper_token: str = "",
) -> str:
    """Compute a stable SHA-256 digest from pipeline configuration.

    Args:
        pipeline_order: Ordered list of agent_id strings (AGENT_PIPELINE).
        adapter_keys:   Sorted list of keys present in adapters dict.
        territory:      The target territory string.
        heal:           ctx.heal flag.
        enable_llm:     ctx.enable_llm flag.
        tamper_token:   When SSOT_ORCH_NEGCTRL_TAMPER=1, contains "1"; else "0".

    Returns:
        64-char lowercase hex SHA-256 digest.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_pipeline_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_pipeline_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_pipeline_digest")
    payload = "|".join(
        [
            ",".join(pipeline_order),
            ",".join(sorted(adapter_keys)),
            territory,
            str(heal),
            str(enable_llm),
            tamper_token,
        ],
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def emit_pipeline_digest(
    pipeline_order: list[str], adapter_keys: list[str], territory: str, heal: bool, enable_llm: bool,
) -> str:
    """Compute digest, print the canonical line, and return the digest string.

    Printed line format (exactly once per run):
        EXECUTE_SSOT_PIPELINE_DIGEST: <64-hex>

    When env var SSOT_ORCH_NEGCTRL_TAMPER=1, the tamper token is included
    in the payload so the digest differs from a clean run — used by the
    negative-control test.
    """
    tamper_token = os.environ.get("SSOT_ORCH_NEGCTRL_TAMPER", "0")
    digest = compute_pipeline_digest(
        pipeline_order=pipeline_order,
        adapter_keys=adapter_keys,
        territory=territory,
        heal=heal,
        enable_llm=enable_llm,
        tamper_token=tamper_token,
    )
    print(f"EXECUTE_SSOT_PIPELINE_DIGEST: {digest}")
    return digest
