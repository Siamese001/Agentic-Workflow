"""Stubs for integration contract types used by review scripts.

These types were previously in agentic_core.L0_routing.types.integration_contract_types
which was deleted as dead code. These minimal stubs are maintained for ops_scripts usage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class FindingSeverity(Enum):
    """Severity level for findings."""
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class Finding:
    """A finding from a review or validation."""
    code: str
    severity: FindingSeverity | str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultEnvelope:
    """Envelope for review/validation results."""
    tool: str
    exit_code: int
    findings: list[Finding] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)

    def write_json(self, path: str | Path) -> None:
        """Write envelope to JSON file."""
        with open(str(path), 'w') as f:
            json.dump({
                'tool': self.tool,
                'exit_code': self.exit_code,
                'findings': [
                    {
                        'code': f.code,
                        'severity': f.severity.value if isinstance(f.severity, FindingSeverity) else f.severity,
                        'message': f.message,
                        'context': f.context,
                    }
                    for f in self.findings
                ],
                'inputs': self.inputs,
                'outputs': self.outputs,
            }, f, indent=2)
