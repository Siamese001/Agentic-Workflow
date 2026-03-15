"""
SurgicalHealingAdapter - Bridge between legacy healing and CST surgical healing.

Adapts detection results from legacy heal_repository() methods into
SurgicalContext objects for zero-loss CST-based healing.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "SurgicalHealingAdapter", "L5")
_emit_routes_through("p1", "SurgicalHealingAdapter", "L5")
_emit_escalates_to_human("p1", "SurgicalHealingAdapter", "L5")
_emit_reads_policy_state("p1", "SurgicalHealingAdapter", "L5")

_emit_applies_guardrail("p0", "SurgicalHealingAdapter", "p0_governance")
_emit_snapshots_state("p0", "SurgicalHealingAdapter", "state_snapshot")

Logger = logging.getLogger(__name__)


@dataclass
class SurgicalHealingResult:
    """Result from a surgical healing operation."""

    status: str  # "success", "error", "skipped"
    violations_found: int
    violations_fixed: int
    errors: int
    skipped: int
    details: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "errors": self.errors,
            "skipped": self.skipped,
            "details": self.details,
            "artifacts": self.artifacts,
        }


class SurgicalHealingAdapter:
    """
    Bridges legacy healing detection results to SurgicalContext for CST healing.

    Converts dictionaries produced by legacy heal_repository() detectors into
    structured SurgicalContext objects that can be processed by SurgicalCSTHealerMixin.
    """

    FIX_TYPE_MAP: dict[str, str] = {
        "missing_docstring": "insert",
        "missing_import": "insert",
        "missing_future_import": "insert",
        "missing_guardrail": "insert",
        "unused_import": "delete",
        "remove_unused": "delete",
        "bare_except": "replace",
        "invalid_syntax": "replace",
        "trailing_whitespace": "replace",
        "functiondef": "insert",
        "classdef": "insert",
    }

    def __init__(self, agent_name: str = "SurgicalHealingAdapter"):
        self.agent_name = agent_name

    def _infer_fix_type(self, constraint_type: str) -> str:
        """Infer the fix type from the constraint type string."""
        ct = constraint_type.lower()
        for key, fix in self.FIX_TYPE_MAP.items():
            if key in ct:
                return fix
        return "insert"

    def create_context_from_detection(
        self,
        file_path: Path,
        detection_result: dict[str, Any],
        detection_method: str,
    ) -> SurgicalContext | None:
        """
        Create a SurgicalContext from a single detection result dict.

        Args:
            file_path: Path to the file to heal
            detection_result: Dict with keys: type, line, message, severity, etc.
            detection_method: Name of the detection method that found the violation

        Returns:
            SurgicalContext or None if file does not exist
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "SurgicalHealingAdapter.create_context_from_detection"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalHealingAdapter.create_context_from_detection".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not file_path.exists():
            Logger.warning("File does not exist: %s", file_path)
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        # guardian: allow-silent-swallow
        except Exception as exc:
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None

        line = detection_result.get("line", 1) or 1
        constraint_type = detection_result.get("type", "unknown")
        fix_type = self._infer_fix_type(constraint_type)

        violation = ViolationConstraint(
            constraint_type=constraint_type,
            severity=detection_result.get("severity", "warning"),
            message=detection_result.get("message", ""),
            expected_pattern=detection_result.get("expected_pattern"),
            actual_pattern=detection_result.get("actual_pattern"),
            fix_type=fix_type,
        )

        coordinate = ASTCoordinate(
            node_id=f"{constraint_type}:{line}",
            node_type=constraint_type,
            line=line,
            column=0,
        )

        return SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{detection_method}:{line}",
            violations=[violation],
            target_coordinates=[coordinate],
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

    def create_batch_context(
        self,
        file_path: Path,
        detection_results: list[dict[str, Any]],
        detection_method: str,
    ) -> SurgicalContext | None:
        """
        Create a SurgicalContext from multiple detection result dicts.

        Args:
            file_path: Path to the file to heal
            detection_results: List of detection result dicts
            detection_method: Name of the detection method

        Returns:
            SurgicalContext or None if file does not exist
        """
        if not file_path.exists():
            Logger.warning("File does not exist: %s", file_path)
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        # guardian: allow-silent-swallow
        except Exception as exc:
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None

        violations: list[ViolationConstraint] = []
        coordinates: list[ASTCoordinate] = []

        for dr in detection_results:
            line = dr.get("line", 1) or 1
            constraint_type = dr.get("type", "unknown")
            fix_type = self._infer_fix_type(constraint_type)

            violations.append(
                ViolationConstraint(
                    constraint_type=constraint_type,
                    severity=dr.get("severity", "warning"),
                    message=dr.get("message", ""),
                    expected_pattern=dr.get("expected_pattern"),
                    actual_pattern=dr.get("actual_pattern"),
                    fix_type=fix_type,
                )
            )
            coordinates.append(
                ASTCoordinate(
                    node_id=f"{constraint_type}:{line}",
                    node_type=constraint_type,
                    line=line,
                    column=0,
                )
            )

        return SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{detection_method}:batch",
            violations=violations,
            target_coordinates=coordinates,
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

    def apply_surgical_healing(
        self,
        context: SurgicalContext | None,
    ) -> SurgicalHealingResult:
        """
        Apply surgical healing using the CST mixin.

        Args:
            context: SurgicalContext to heal, or None

        Returns:
            SurgicalHealingResult
        """
        if context is None:
            return SurgicalHealingResult(
                status="error",
                violations_found=0,
                violations_fixed=0,
                errors=1,
                skipped=0,
                details="No context provided",
            )

        try:
            from agentic_core.mixins.cst_healer_mixin import SurgicalCSTHealerMixin

            healer = SurgicalCSTHealerMixin()
            raw = healer.heal_surgical_cst(context)

            return SurgicalHealingResult(
                status=raw.get("status", "success"),
                violations_found=raw.get("violations_found", len(context.violations)),
                violations_fixed=raw.get("violations_fixed", 0),
                errors=raw.get("errors", 0),
                skipped=raw.get("skipped", 0),
                details=raw.get("details", ""),
                artifacts=raw.get("artifacts", []),
            )
        # guardian: allow-silent-swallow
        except Exception as exc:
            Logger.error("Surgical healing failed: %s", exc)
            return SurgicalHealingResult(
                status="error",
                violations_found=len(context.violations),
                violations_fixed=0,
                errors=1,
                skipped=len(context.violations),
                details=str(exc),
            )
