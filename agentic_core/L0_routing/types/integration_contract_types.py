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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class Finding:
    """A single finding from a governance tool run."""

    code: str
    severity: str  # INFO | WARN | ERROR
    message: str
    context: dict | None = None

    def to_ordered_dict(self) -> dict:
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
        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
        path.write_text(self.to_json(), encoding="utf-8")
