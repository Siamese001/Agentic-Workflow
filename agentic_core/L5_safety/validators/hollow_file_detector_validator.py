"""
Hollow File Detector — AST Semantic Verification

Detects files with minimal behavioral content relative to boilerplate instrumentation.
Targets the "Hollow Books" anti-patterns: Archaeological Residue, Automated Scaffolding,
Process-Driven Stubs.
"""

import ast
import logging
from enum import Enum
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
)

_emit_records_execution_trace("p0", "hollow_file_detector_validator", "L5_POLICY")
_emit_applies_guardrail("p0", "hollow_file_detector_validator", "p0_governance")
_emit_reads_policy_state("p0", "hollow_file_detector_validator", "policy_binding")
_emit_snapshots_state("p0", "hollow_file_detector_validator", "state_snapshot")
emit_replay_key("p0", "hollow_file_detector_validator")
emit_determinism_digest("p0", "hollow_file_detector_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hollow_file_detector_validator", "execution_auth")
_emit_validates_capability("p2", "hollow_file_detector_validator", "capability_check")
_emit_routes_to_capability("p2", "hollow_file_detector_validator", "capability_route")
_emit_writes_via_uwg("p2", "hollow_file_detector_validator", "uwg_write")

Logger = logging.getLogger(__name__)


class HollowFileClassification(str, Enum):
    """Classification of hollow file severity."""

    HOLLOW = "hollow"  # 0 behavioral nodes - completely empty of logic
    SCAFFOLDING = "scaffolding"  # ClassDef with only pass/.../NotImplementedError
    BOILERPLATE_HEAVY = "boilerplate_heavy"  # >70% boilerplate statements
    HEALTHY = "healthy"  # Active behavioral logic present


class BehavioralNodeCounter(ast.NodeVisitor):
    """Counts behavioral nodes in AST."""

    def __init__(self):
        self.behavioral_functions = 0
        self.behavioral_classes = 0
        self.behavioral_methods = 0
        self.total_statements = 0
        self.boilerplate_statements = 0
        self.import_statements = 0
        self.string_literals = 0

    def visit_Module(self, node: ast.Module):
        """Visit module level."""
        for stmt in node.body:
            self.total_statements += 1
            self.visit(stmt)
        return node

    def visit_Import(self, node: ast.Import):
        """Count import statements."""
        self.import_statements += 1
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Count import from statements."""
        self.import_statements += 1
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definition."""
        # Check if function has non-trivial body
        if self._has_behavioral_body(node.body):
            if node.name.startswith('_emit_'):
                # Module-level emit calls are boilerplate
                self.boilerplate_statements += 1
            else:
                self.behavioral_functions += 1
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Analyze async function definition."""
        if self._has_behavioral_body(node.body):
            if node.name.startswith('_emit_'):
                self.boilerplate_statements += 1
            else:
                self.behavioral_functions += 1
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definition."""
        # Check if class has behavioral methods
        behavioral_methods = 0
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._has_behavioral_body([item]):
                    if not item.name.startswith('_emit_'):
                        behavioral_methods += 1

        if behavioral_methods > 0:
            self.behavioral_classes += 1
            self.behavioral_methods += behavioral_methods
        elif len(node.body) == 1 and self._is_stub_body(node.body[0]):
            # Class with only stub method
            pass
        else:
            # Empty or only boilerplate class
            pass

        return node

    def visit_Expr(self, node: ast.Expr):
        """Analyze expression statements."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            # Module-level string literals (likely docstrings or comments)
            self.string_literals += 1
        elif (isinstance(node.value, ast.Call) and
              isinstance(node.value.func, ast.Name) and
              node.value.func.id.startswith('_emit_')):
            # Module-level emit calls
            self.boilerplate_statements += 1
        return node

    def _has_behavioral_body(self, body: list[ast.stmt]) -> bool:
        """Check if function/class body has behavioral content."""
        if len(body) == 0:
            return False

        # Check for stub bodies (pass, ..., NotImplementedError)
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                return False
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value == Ellipsis:
                    return False
            elif (isinstance(stmt, ast.Raise) and
                  isinstance(stmt.exc, ast.Call) and
                  isinstance(stmt.exc.func, ast.Name) and
                  stmt.exc.func.id == 'NotImplementedError'):
                return False

        # Look for actual behavioral statements
        for stmt in body:
            if self._is_behavioral_statement(stmt):
                return True

        return False

    def _is_behavioral_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement represents behavioral logic."""
        # Behavioral statements include: assignments, returns, if/for/while/try,
        # function calls (except emits), etc.
        if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            return True
        elif isinstance(stmt, ast.Return):
            return True
        elif isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try)):
            return True
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            # Function call - check if it's not just an emit
            call = stmt.value
            if not (isinstance(call.func, ast.Name) and call.func.id.startswith('_emit_')):
                return True
        elif isinstance(stmt, ast.With):
            return True

        return False

    def _is_stub_body(self, stmt: ast.stmt) -> bool:
        """Check if statement is a stub (pass, ..., NotImplementedError)."""
        if isinstance(stmt, ast.Pass):
            return True
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value == Ellipsis:
                return True
        elif (isinstance(stmt, ast.Raise) and
              isinstance(stmt.exc, ast.Call) and
              isinstance(stmt.exc.func, ast.Name) and
              stmt.exc.func.id == 'NotImplementedError'):
            return True

        return False

    def get_boilerplate_ratio(self) -> float:
        """Calculate ratio of boilerplate to total statements."""
        if self.total_statements == 0:
            return 0.0
        return self.boilerplate_statements / self.total_statements

    def classify(self) -> HollowFileClassification:
        """Classify file based on behavioral content."""
        behavioral_nodes = self.behavioral_functions + self.behavioral_classes
        boilerplate_ratio = self.get_boilerplate_ratio()

        if behavioral_nodes == 0:
            return HollowFileClassification.HOLLOW
        elif (self.behavioral_classes > 0 and
              self.behavioral_methods == 0 and
              behavioral_nodes == self.behavioral_classes):
            # Classes exist but no behavioral methods
            return HollowFileClassification.SCAFFOLDING
        elif boilerplate_ratio > 0.7:
            return HollowFileClassification.BOILERPLATE_HEAVY
        else:
            return HollowFileClassification.HEALTHY


class HollowFileDetector(AntiPatternDetector):
    """
    Detects hollow files with minimal behavioral content.

    Hollow files are those that contain primarily boilerplate instrumentation
    (_emit_* calls, imports, docstrings) with little or no actual behavioral logic.
    """

    @property
    def category(self) -> AntiPatternCategory:
        """Return the anti-pattern category this detector handles."""
        return AntiPatternCategory.HOLLOW_FILE

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """
        Detect hollow files in the given AST.

        Args:
            file_path: Path to the file being analyzed
            tree: Parsed AST of the file

        Returns:
            List of detected violations
        """
        violations = []

        # Count behavioral and boilerplate content
        counter = BehavioralNodeCounter()
        counter.visit(tree)

        classification = counter.classify()

        # Generate violations based on classification
        if classification == HollowFileClassification.HOLLOW:
            violations.append(AntiPatternViolation(
                file_path=file_path,
                line_number=1,
                category=self.category,
                message="File contains no behavioral logic - only boilerplate",
                evidence=f"Behavioral nodes: 0, Boilerplate ratio: {counter.get_boilerplate_ratio():.2%}",
                severity="error",
                suggested_fix="Delete file or add behavioral logic",
                metadata={
                    "classification": classification.value,
                    "behavioral_functions": counter.behavioral_functions,
                    "behavioral_classes": counter.behavioral_classes,
                    "boilerplate_statements": counter.boilerplate_statements,
                    "total_statements": counter.total_statements,
                },
            ))
        elif classification == HollowFileClassification.SCAFFOLDING:
            violations.append(AntiPatternViolation(
                file_path=file_path,
                line_number=1,
                category=self.category,
                message="File contains only scaffolding - classes with no behavioral methods",
                evidence=f"Classes: {counter.behavioral_classes}, Behavioral methods: 0",
                severity="warning",
                suggested_fix="Implement behavioral methods or delete scaffolding",
                metadata={
                    "classification": classification.value,
                    "behavioral_classes": counter.behavioral_classes,
                    "total_statements": counter.total_statements,
                },
            ))
        elif classification == HollowFileClassification.BOILERPLATE_HEAVY:
            violations.append(AntiPatternViolation(
                file_path=file_path,
                line_number=1,
                category=self.category,
                message=f"File is {counter.get_boilerplate_ratio():.1%} boilerplate",
                evidence=f"Boilerplate: {counter.boilerplate_statements}/{counter.total_statements}",
                severity="warning",
                suggested_fix="Consider reducing boilerplate or extracting to separate module",
                metadata={
                    "classification": classification.value,
                    "boilerplate_ratio": counter.get_boilerplate_ratio(),
                    "boilerplate_statements": counter.boilerplate_statements,
                    "total_statements": counter.total_statements,
                },
            ))

        return violations


__all__ = [
    "HollowFileDetector",
    "HollowFileClassification",
    "BehavioralNodeCounter",
]
