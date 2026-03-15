"""
SurgicalContext - Structured Context for Zero-Loss Healing

Provides AST-level coordinates and violation constraints for surgical healing operations.
Eliminates Resolution Asymmetry by preserving all detection information.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class ASTCoordinate:
    """Precise AST node coordinate."""

    node_id: str
    node_type: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)


@dataclass
class ViolationConstraint:
    """Specific constraint that was violated."""

    constraint_type: str
    severity: str
    message: str
    rule_id: str | None = None
    expected_pattern: str | None = None
    actual_pattern: str | None = None
    fix_type: str | None = None


@dataclass
class SurgicalContext:
    """
    Comprehensive context for surgical healing operations.

    This structure ensures zero information loss between detection and healing.
    All coordinates are preserved for AST-level mutations.
    """

    file_path: Path
    file_content: str
    ast_tree: ast.Module
    violation_id: str
    violations: list[ViolationConstraint]
    target_coordinates: list[ASTCoordinate]
    detector_agent: str
    detection_method: str
    detection_timestamp: str
    surrounding_context: dict[str, Any] = field(default_factory=dict)
    related_violations: list[str] = field(default_factory=list)
    suggested_fixes: list[dict[str, Any]] = field(default_factory=list)
    preservation_rules: list[str] = field(default_factory=list)

    def get_target_node(self, coordinate: ASTCoordinate) -> ast.AST | None:
        """Get AST node by coordinate."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SurgicalContext.get_target_node")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SurgicalContext.get_target_node".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for node in ast.walk(self.ast_tree):
            if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                if node.lineno == coordinate.line and node.col_offset == coordinate.column:
                    return node
        return None

    def get_nodes_by_type(self, node_type: str) -> list[ast.AST]:
        """Get all nodes of a specific type."""
        nodes = []
        for node in ast.walk(self.ast_tree):
            if type(node).__name__ == node_type:
                nodes.append(node)
        return nodes

    def get_line_range(self, coordinate: ASTCoordinate) -> tuple[int, int]:
        """Get line range for a coordinate."""
        start = coordinate.line
        end = coordinate.end_line or coordinate.line
        return (start, end)

    def extract_source_segment(self, coordinate: ASTCoordinate) -> str:
        """Extract source code for the coordinate."""
        lines = self.file_content.splitlines(keepends=True)
        start, end = self.get_line_range(coordinate)
        if start == end:
            return lines[start - 1]
        else:
            return "".join(lines[start - 1 : end])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "violation_id": self.violation_id,
            "violations": [v.__dict__ for v in self.violations],
            "target_coordinates": [c.__dict__ for c in self.target_coordinates],
            "detector_agent": self.detector_agent,
            "detection_method": self.detection_method,
            "detection_timestamp": self.detection_timestamp,
            "surrounding_context": self.surrounding_context,
            "related_violations": self.related_violations,
            "suggested_fixes": self.suggested_fixes,
            "preservation_rules": self.preservation_rules,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SurgicalContext:
        """Create from dictionary."""
        tree = ast.parse(data["file_content"])
        violations = [ViolationConstraint(**v) for v in data["violations"]]
        coordinates = [ASTCoordinate(**c) for c in data["target_coordinates"]]
        return cls(
            file_path=Path(data["file_path"]),
            file_content=data["file_content"],
            ast_tree=tree,
            violation_id=data["violation_id"],
            violations=violations,
            target_coordinates=coordinates,
            detector_agent=data["detector_agent"],
            detection_method=data["detection_method"],
            detection_timestamp=data["detection_timestamp"],
            surrounding_context=data.get("surrounding_context", {}),
            related_violations=data.get("related_violations", []),
            suggested_fixes=data.get("suggested_fixes", []),
            preservation_rules=data.get("preservation_rules", []),
        )


class SurgicalContextBuilder:
    """Builder for creating SurgicalContext from detection results."""

    def __init__(self, file_path: Path, detector_agent: str, detection_method: str):
        self.file_path = file_path
        self.detector_agent = detector_agent
        self.detection_method = detection_method
        self.file_content = file_path.read_text(encoding="utf-8")
        self.ast_tree = ast.parse(self.file_content)

    def build_context(
        self, violation_id: str, violations: list[dict[str, Any]], target_nodes: list[ast.AST], **kwargs
    ) -> SurgicalContext:
        """Build SurgicalContext from detection results."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SurgicalContextBuilder.build_context")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SurgicalContextBuilder.build_context".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from datetime import datetime

        violation_constraints = []
        for v in violations:
            violation_constraints.append(ViolationConstraint(**v))
        coordinates = []
        for i, node in enumerate(target_nodes):
            coord = ASTCoordinate(
                node_id=f"{self.detection_method}_{i}_{node.lineno}_{node.col_offset}",
                node_type=type(node).__name__,
                line=node.lineno,
                column=node.col_offset,
                end_line=getattr(node, "end_lineno", None),
                end_column=getattr(node, "end_col_offset", None),
            )
            coordinates.append(coord)
        return SurgicalContext(
            file_path=self.file_path,
            file_content=self.file_content,
            ast_tree=self.ast_tree,
            violation_id=violation_id,
            violations=violation_constraints,
            target_coordinates=coordinates,
            detector_agent=self.detector_agent,
            detection_method=self.detection_method,
            detection_timestamp=datetime.now().isoformat(),
            **kwargs,
        )


__all__ = ["SurgicalContext", "SurgicalContextBuilder", "ASTCoordinate", "ViolationConstraint"]
