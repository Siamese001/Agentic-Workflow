"""
SurgicalContext - Structured Context for Zero-Loss Healing

Provides AST-level coordinates and violation constraints for surgical healing operations.
Eliminates Resolution Asymmetry by preserving all detection information.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ASTCoordinate:
    """Precise AST node coordinate."""

    node_id: str  # Unique identifier for the node
    node_type: str  # ast.ClassDef, ast.FunctionDef, etc.
    line: int  # Line number (1-based)
    column: int  # Column offset
    end_line: Optional[int] = None  # End line for multi-line nodes
    end_column: Optional[int] = None  # End column
    parent_id: Optional[str] = None  # Parent node ID
    children_ids: List[str] = field(default_factory=list)  # Child node IDs


@dataclass
class ViolationConstraint:
    """Specific constraint that was violated."""

    constraint_type: str  # e.g., "missing_docstring", "invalid_import"
    severity: str  # "error", "warning", "info"
    message: str  # Human-readable description
    rule_id: Optional[str] = None  # Rule identifier
    expected_pattern: Optional[str] = None  # What was expected
    actual_pattern: Optional[str] = None  # What was found
    fix_type: Optional[str] = None  # "insert", "replace", "delete", "move"


@dataclass
class SurgicalContext:
    """
    Comprehensive context for surgical healing operations.

    This structure ensures zero information loss between detection and healing.
    All coordinates are preserved for AST-level mutations.
    """

    # File information
    file_path: Path
    file_content: str
    ast_tree: ast.Module

    # Violation details
    violation_id: str
    violations: List[ViolationConstraint]

    # AST coordinates for precise targeting
    target_coordinates: List[ASTCoordinate]

    # Detection metadata
    detector_agent: str
    detection_method: str
    detection_timestamp: str

    # Additional context
    surrounding_context: Dict[str, Any] = field(default_factory=dict)
    related_violations: List[str] = field(default_factory=list)

    # Healing hints
    suggested_fixes: List[Dict[str, Any]] = field(default_factory=list)
    preservation_rules: List[str] = field(default_factory=list)  # What must be preserved

    def get_target_node(self, coordinate: ASTCoordinate) -> Optional[ast.AST]:
        """Get AST node by coordinate."""
        for node in ast.walk(self.ast_tree):
            if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                if node.lineno == coordinate.line and node.col_offset == coordinate.column:
                    return node
        return None

    def get_nodes_by_type(self, node_type: str) -> List[ast.AST]:
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
        return start, end

    def extract_source_segment(self, coordinate: ASTCoordinate) -> str:
        """Extract source code for the coordinate."""
        lines = self.file_content.splitlines(keepends=True)
        start, end = self.get_line_range(coordinate)

        if start == end:
            return lines[start - 1]
        else:
            return "".join(lines[start - 1 : end])

    def to_dict(self) -> Dict[str, Any]:
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
    def from_dict(cls, data: Dict[str, Any]) -> SurgicalContext:
        """Create from dictionary."""
        # Reconstruct AST tree from file content
        tree = ast.parse(data["file_content"])

        # Reconstruct objects
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
        self,
        violation_id: str,
        violations: List[Dict[str, Any]],
        target_nodes: List[ast.AST],
        **kwargs,
    ) -> SurgicalContext:
        """Build SurgicalContext from detection results."""
        from datetime import datetime

        # Convert violations to ViolationConstraint objects
        violation_constraints = []
        for v in violations:
            violation_constraints.append(ViolationConstraint(**v))

        # Generate coordinates for target nodes
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
