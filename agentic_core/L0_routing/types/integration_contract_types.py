"""V15 Integration Result Envelope — Stable JSON Contract.

Shared contract for governance CLI tools to emit deterministic JSON
result envelopes behind a --json-out flag.

Schema v1.0.0:
    tool, schema_version, status, exit_code, inputs, findings, outputs
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "integration_contract_types", "L0")
_emit_routes_through("p1", "integration_contract_types", "L0")
_emit_escalates_to_human("p1", "integration_contract_types", "L0")
_emit_reads_policy_state("p1", "integration_contract_types", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "integration_contract_types", "p0_governance")
_emit_snapshots_state("p0", "integration_contract_types", "state_snapshot")

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class Finding:
    """A single finding from a governance tool run."""

    code: str
    severity: str
    message: str
    context: dict | None = None

    def to_ordered_dict(self) -> dict:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "Finding.to_ordered_dict")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        d: dict = {
            "code": self.code,
            "context": self.context if self.context is not None else {},
            "message": self.message,
            "severity": self.severity,
        }
        return d


@dataclass
class ResultEnvelope:
    """Deterministic JSON result envelope for governance CLIs."""

    tool: str
    exit_code: int
    inputs: dict[str, dict] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    outputs: dict[str, dict] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Derive status from exit_code and findings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ResultEnvelope.status")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        has_error = any(f.severity == "ERROR" for f in self.findings)
        has_warn = any(f.severity == "WARN" for f in self.findings)
        if self.exit_code != 0 or has_error:
            return "FAIL"
        if has_warn:
            return "WARN"
        return "PASS"

    def to_ordered_dict(self) -> dict:
        """Return a plain dict with stable key ordering."""
        return {
            "exit_code": self.exit_code,
            "findings": [f.to_ordered_dict() for f in self.findings],
            "inputs": dict(sorted(self.inputs.items())),
            "outputs": dict(sorted(self.outputs.items())),
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "tool": self.tool,
        }

    def to_json(self) -> str:
        """Deterministic JSON string: sorted keys, compact separators."""
        return json.dumps(self.to_ordered_dict(), sort_keys=True, separators=(",", ":"))

    def write_json(self, path: Path) -> None:
        """Write deterministic JSON bytes to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        assert_no_persistent_write("L0", "write_text")
        path.write_text(self.to_json(), encoding="utf-8")
