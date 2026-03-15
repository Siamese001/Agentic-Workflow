"""
RootHygieneValidatorAgent - L5 Pure Validator.

Read-only scan of root hygiene violations via RootHygieneAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class RootHygieneValidatorAgent:
    """L5 Certify-only validator for root directory hygiene violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self) -> dict[str, Any]:
        """Delegate to RootHygieneAgent.scan_root_violations (read-only)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RootHygieneValidatorAgent.scan_root_violations")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:RootHygieneValidatorAgent.scan_root_violations".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent

        agent = RootHygieneAgent(project_root=self.project_root, dry_run=True)
        return agent.scan_root_violations()
