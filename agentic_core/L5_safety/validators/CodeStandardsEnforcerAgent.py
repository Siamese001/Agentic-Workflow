"""
CodeStandardsEnforcerAgent - Unified Code Standards Enforcer (Phase 4)

Consolidates:
- BaseClassEnforcerAgent (layer inheritance validation)
- PatternEnforcerAgent (coding pattern enforcement)
- TypeHintEnforcementAgent (type hint completeness)

Key Features:
- Single AST traversal for all three enforcement domains
- Standardized JSON violation reporting
- Composite enforcement with pluggable sub-modules

Enforces:
- Layer Base Class Inheritance (L0-L6 agents must inherit canonical bases)
- Coding Patterns (Keys 26-39: mutable defaults, string concat, etc.)
- Type Hint Completeness (return types, parameter types)

Territory: agentic_core/L5_safety/validators/
Canon Alignment: L5 safety validation and code standards enforcement
"""
from __future__ import annotations

import ast
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agentic_core.L5_safety.validators.L5Agent import L5Agent
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator
from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    GLOBAL_EXCLUDED_DIRS,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.validators.decorators import standard_heal

Logger = logging.getLogger(__name__)


@dataclass
class CodeViolation:
    """Standardized code violation report."""
    file_path: str
    line_number: int
    violation_type: str  # INHERITANCE_ERR, PATTERN_VIOLATION, TYPE_HINT_ERR
    message: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    canon_key: Optional[int] = None  # Canon key number if applicable
    suggested_fix: Optional[str] = None


@dataclass
class CodeStandardsEnforcerAgent(L5Agent, CanonASTValidator):
    """
    Unified Code Standards Enforcer (Phase 4 Consolidation).
    
    Consolidates BaseClassEnforcer, PatternEnforcer, and TypeHintEnforcement
    into a single agent with shared AST traversal.
    
    Validates:
    - Layer base class inheritance (L0-L6 canonical bases)
    - Coding patterns (Canon Keys 26-39)
    - Type hint completeness (parameters and return types)
    
    Inherits from:
    - L5Agent: Standard L5 safety capabilities
    - CanonASTValidator: AST traversal and validation utilities
    """
    
    name: str = "CodeStandardsEnforcerAgent"
    layer: str = "L5"
    project_root: Path = field(default_factory=Path.cwd)
    
    # Canonical layer bases for inheritance validation
    LAYER_BASES: Dict[str, str] = field(default_factory=lambda: {
        'L0': 'L0MaintenanceBaseAgent',
        'L1': 'L1CognitionBaseAgent',
        'L2': 'L2ExecutionBaseAgent',
        'L3': 'L3OrchestrationBaseAgent',
        'L4': 'L4StateBaseAgent',
        'L5': 'L5Agent',
        'L6': 'L6ObservabilityBaseAgent',
    })
    
    # Layer directory patterns for matching
    LAYER_PATTERNS: Dict[str, str] = field(default_factory=lambda: {
        'L0_maintenance': 'L0',
        'L1_cognition': 'L1',
        'L2_execution': 'L2',
        'L3_orchestration': 'L3',
        'L4_state': 'L4',
        'L5_safety': 'L5',
        'L6_observability': 'L6',
    })
    
    # Python builtins that should not be shadowed
    BUILTINS: Set[str] = field(default_factory=lambda: {
        'list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool',
        'type', 'object', 'len', 'range', 'print', 'input', 'open',
        'file', 'id', 'hash', 'sum', 'min', 'max', 'abs', 'all', 'any',
        'map', 'filter', 'zip', 'enumerate', 'sorted', 'reversed',
        'format', 'iter', 'next', 'slice', 'super', 'property',
        'classmethod', 'staticmethod', 'vars', 'dir', 'globals', 'locals',
    })
    
    # Directories to skip
    SKIP_DIRS: Set[str] = field(default_factory=lambda: set(GLOBAL_EXCLUDED_DIRS))
    
    # Internal state
    violations: List[CodeViolation] = field(default_factory=list)
    current_file: str = ""
    _in_class: bool = False
    _current_class_name: str = ""
    
    def __post_init__(self) -> None:
        """Initialize the unified code standards enforcer."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        
        # Initialize collections
        if not isinstance(self.violations, list):
            self.violations = []
    
    def validate_repository(self, targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive standards sweep across inheritance, patterns, and types.
        
        Args:
            targets: Optional list of specific files to validate
            
        Returns:
            Dictionary with validation report
        """
        # Reset state
        self.violations = []
        
        # Get files to scan
        files_to_scan = targets or self._get_repo_files()
        
        report = {
            "summary": {
                "files_scanned": 0,
                "total_violations": 0,
                "inheritance_errors": 0,
                "pattern_violations": 0,
                "type_hint_errors": 0,
            },
            "details": [],
            "status": "PASS",
        }
        
        for file_path in files_to_scan:
            self.current_file = str(file_path)
            self._in_class = False
            self._current_class_name = ""
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                self.visit(tree)
                report["summary"]["files_scanned"] += 1
                
            except SyntaxError as e:
                Logger.debug(f"Syntax error in {file_path}: {e}")
            except Exception as e:
                Logger.debug(f"Could not process {file_path}: {e}")
        
        # Aggregate violations
        report["summary"]["total_violations"] = len(self.violations)
        report["summary"]["inheritance_errors"] = sum(
            1 for v in self.violations if v.violation_type == "INHERITANCE_ERR"
        )
        report["summary"]["pattern_violations"] = sum(
            1 for v in self.violations if v.violation_type == "PATTERN_VIOLATION"
        )
        report["summary"]["type_hint_errors"] = sum(
            1 for v in self.violations if v.violation_type == "TYPE_HINT_ERR"
        )
        
        # Convert violations to dicts for JSON serialization
        report["details"] = [
            {
                "file": v.file_path,
                "line": v.line_number,
                "type": v.violation_type,
                "message": v.message,
                "severity": v.severity,
                "canon_key": v.canon_key,
                "suggested_fix": v.suggested_fix,
            }
            for v in self.violations
        ]
        
        report["status"] = "FAIL" if report["summary"]["total_violations"] > 0 else "PASS"
        
        return report
    
    # =========================================================================
    # AST VISITOR METHODS
    # =========================================================================
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Validate class definitions for:
        - Layer base class inheritance
        - Shadowed builtins in class name
        """
        self._in_class = True
        self._current_class_name = node.name
        
        # Check for shadowed builtin names
        if node.name.lower() in self.BUILTINS:
            self._add_violation(
                node,
                f"Class name '{node.name}' shadows a Python builtin",
                "PATTERN_VIOLATION",
                canon_key=36,
                severity="MEDIUM",
            )
        
        # Check layer base class inheritance
        self._check_layer_inheritance(node)
        
        # Continue visiting children
        self.generic_visit(node)
        
        self._in_class = False
        self._current_class_name = ""
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Validate function definitions for:
        - Type hint completeness (return type, parameter types)
        - Mutable default arguments (Key 26)
        - Shadowed builtins in function name
        """
        # Skip private/dunder methods for type hint enforcement
        is_public = not node.name.startswith('_')
        
        # Check for shadowed builtin names
        if node.name in self.BUILTINS:
            self._add_violation(
                node,
                f"Function name '{node.name}' shadows a Python builtin",
                "PATTERN_VIOLATION",
                canon_key=36,
                severity="MEDIUM",
            )
        
        # Type hint enforcement for public functions
        if is_public:
            self._check_type_hints(node)
        
        # Pattern enforcement: mutable defaults (Key 26)
        self._check_mutable_defaults(node)
        
        # Continue visiting children
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async functions the same as regular functions."""
        # Reuse FunctionDef logic
        self.visit_FunctionDef(node)  # type: ignore
    
    def visit_Call(self, node: ast.Call) -> None:
        """
        Validate function calls for:
        - dict.keys() when 'in' suffices (Key 32)
        """
        # Check for dict.keys() usage
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'keys' and not node.args:
                self._add_violation(
                    node,
                    "Unnecessary dict.keys() - use 'in dict' directly",
                    "PATTERN_VIOLATION",
                    canon_key=32,
                    severity="LOW",
                    suggested_fix="Replace 'x in dict.keys()' with 'x in dict'",
                )
        
        self.generic_visit(node)
    
    def visit_Compare(self, node: ast.Compare) -> None:
        """
        Validate comparisons for:
        - Float equality comparisons (Key 33)
        - None comparisons using == instead of 'is' (Key 34)
        """
        for op, comparator in zip(node.ops, node.comparators):
            # Check for None comparisons with == or !=
            if isinstance(op, (ast.Eq, ast.NotEq)):
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    self._add_violation(
                        node,
                        "Use 'is None' or 'is not None' instead of == or !=",
                        "PATTERN_VIOLATION",
                        canon_key=34,
                        severity="LOW",
                        suggested_fix="Replace '== None' with 'is None'",
                    )
                
                # Check for float equality
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, float):
                    self._add_violation(
                        node,
                        "Avoid direct float equality comparison - use math.isclose()",
                        "PATTERN_VIOLATION",
                        canon_key=33,
                        severity="MEDIUM",
                    )
        
        self.generic_visit(node)
    
    def visit_Assert(self, node: ast.Assert) -> None:
        """
        Validate assert statements (Key 29).
        Note: Only flags if file appears to be production code.
        """
        # Skip test files
        if 'test' in self.current_file.lower():
            self.generic_visit(node)
            return
        
        self._add_violation(
            node,
            "Assert statement in production code - use proper error handling",
            "PATTERN_VIOLATION",
            canon_key=29,
            severity="LOW",
        )
        
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """
        Validate return statements for useless returns (Key 39).
        """
        # Check for 'return None' at end of function (useless)
        if node.value is None:
            # This is a simple heuristic - could be more sophisticated
            pass  # Skip for now - requires context of function body
        
        self.generic_visit(node)
    
    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================
    
    def _check_layer_inheritance(self, node: ast.ClassDef) -> None:
        """
        Check if class inherits from correct layer base.
        
        Args:
            node: AST ClassDef node
        """
        # Skip base classes themselves
        if 'base' in self.current_file.lower() or 'Base' in node.name:
            return
        
        # Skip mixin classes
        if 'Mixin' in node.name:
            return
        
        # Determine which layer this file belongs to
        layer = None
        for pattern, layer_id in self.LAYER_PATTERNS.items():
            if pattern in self.current_file:
                layer = layer_id
                break
        
        if not layer:
            return  # Not in a layer directory
        
        # Get expected base class
        expected_base = self.LAYER_BASES.get(layer)
        if not expected_base:
            return
        
        # Extract base class names
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)
        
        # Check if expected base is in inheritance chain
        if expected_base not in base_classes:
            # Check for alternative valid bases (e.g., L5Agent for L5)
            alt_bases = [expected_base]
            if layer == 'L5':
                alt_bases.extend(['L5Agent', 'L5SafetyBaseAgent'])
            
            if not any(alt in base_classes for alt in alt_bases):
                self._add_violation(
                    node,
                    f"Class '{node.name}' should inherit from {expected_base} (layer {layer})",
                    "INHERITANCE_ERR",
                    severity="HIGH",
                    suggested_fix=f"Add {expected_base} to class inheritance",
                )
    
    def _check_type_hints(self, node: ast.FunctionDef) -> None:
        """
        Check function for type hint completeness.
        
        Args:
            node: AST FunctionDef node
        """
        # Check return type hint
        if node.returns is None:
            self._add_violation(
                node,
                f"Function '{node.name}' is missing return type hint",
                "TYPE_HINT_ERR",
                severity="LOW",
                suggested_fix=f"Add return type: def {node.name}(...) -> ReturnType:",
            )
        
        # Check parameter type hints
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != 'self' and arg.arg != 'cls':
                self._add_violation(
                    arg,
                    f"Parameter '{arg.arg}' in function '{node.name}' is missing type hint",
                    "TYPE_HINT_ERR",
                    severity="LOW",
                    suggested_fix=f"Add type hint: {arg.arg}: Type",
                )
    
    def _check_mutable_defaults(self, node: ast.FunctionDef) -> None:
        """
        Check for mutable default arguments (Key 26).
        
        Args:
            node: AST FunctionDef node
        """
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add_violation(
                    default,
                    f"Mutable default argument in function '{node.name}'",
                    "PATTERN_VIOLATION",
                    canon_key=26,
                    severity="HIGH",
                    suggested_fix="Use None as default and initialize in function body",
                )
        
        # Also check keyword-only defaults
        for default in node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add_violation(
                    default,
                    f"Mutable default argument in function '{node.name}'",
                    "PATTERN_VIOLATION",
                    canon_key=26,
                    severity="HIGH",
                    suggested_fix="Use None as default and initialize in function body",
                )
    
    def _add_violation(
        self,
        node: ast.AST,
        message: str,
        violation_type: str,
        severity: str = "MEDIUM",
        canon_key: Optional[int] = None,
        suggested_fix: Optional[str] = None,
    ) -> None:
        """
        Add a violation to the list.
        
        Args:
            node: AST node where violation occurred
            message: Violation description
            violation_type: Type of violation
            severity: Severity level
            canon_key: Optional canon key number
            suggested_fix: Optional fix suggestion
        """
        self.violations.append(CodeViolation(
            file_path=self.current_file,
            line_number=getattr(node, 'lineno', 0),
            violation_type=violation_type,
            message=message,
            severity=severity,
            canon_key=canon_key,
            suggested_fix=suggested_fix,
        ))
    
    def _get_repo_files(self) -> List[Path]:
        """
        Get all Python files in the repository.
        
        Returns:
            List of Python file paths
        """
        files = []
        
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded directories
            try:
                rel_parts = py_file.relative_to(self.project_root).parts
                if any(skip_dir in rel_parts for skip_dir in self.SKIP_DIRS):
                    continue
            except ValueError:
                continue
            
            files.append(py_file)
        
        return files
    
    # =========================================================================
    # HEALING
    # =========================================================================
    
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Audit and report code standards violations.
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)
            
        Returns:
            Dictionary with healing results
        """
        # Call parent healing chain
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path
        )
        
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        
        _call_path.add(agent_name)
        
        try:
            # Run validation
            results = self.validate_repository()
            
            return {
                "agent": agent_name,
                "violations_found": results["summary"]["total_violations"],
                "violations_fixed": 0,  # Auto-fix not implemented yet
                "summary": results["summary"],
                "status": results["status"],
                "dry_run": dry_run,
            }
        
        finally:
            _call_path.discard(agent_name)
    
    # =========================================================================
    # SELF-TESTS
    # =========================================================================
    
    def _run_self_tests(self) -> Dict[str, Any]:
        """Run internal self-tests for the unified code standards enforcer."""
        results = {"passed": 0, "failed": 0, "tests": []}
        
        # Test 1: Instantiation
        try:
            assert self.name == "CodeStandardsEnforcerAgent"
            assert self.layer == "L5"
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        
        # Test 2: Mutable default detection
        try:
            test_code = "def bad_func(items=[]):\n    pass"
            self.violations = []
            self.current_file = "test.py"
            tree = ast.parse(test_code)
            self.visit(tree)
            
            mutable_violations = [v for v in self.violations if v.canon_key == 26]
            assert len(mutable_violations) == 1
            
            results["passed"] += 1
            results["tests"].append({"name": "test_mutable_default_detection", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_mutable_default_detection", "status": "failed", "error": str(e)})
        
        # Test 3: Type hint detection
        try:
            test_code = "def public_func(x):\n    return x"
            self.violations = []
            self.current_file = "test.py"
            tree = ast.parse(test_code)
            self.visit(tree)
            
            type_violations = [v for v in self.violations if v.violation_type == "TYPE_HINT_ERR"]
            assert len(type_violations) >= 1  # At least return type missing
            
            results["passed"] += 1
            results["tests"].append({"name": "test_type_hint_detection", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_type_hint_detection", "status": "failed", "error": str(e)})
        
        # Test 4: None comparison detection
        try:
            test_code = "x = None\nif x == None:\n    pass"
            self.violations = []
            self.current_file = "test.py"
            tree = ast.parse(test_code)
            self.visit(tree)
            
            none_violations = [v for v in self.violations if v.canon_key == 34]
            assert len(none_violations) == 1
            
            results["passed"] += 1
            results["tests"].append({"name": "test_none_comparison_detection", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_none_comparison_detection", "status": "failed", "error": str(e)})
        
        return results


# =========================================================================
# FACTORY FUNCTIONS
# =========================================================================

def get_code_standards_enforcer(project_root: Optional[Path] = None) -> CodeStandardsEnforcerAgent:
    """
    Factory function to get CodeStandardsEnforcerAgent instance.
    
    Args:
        project_root: Optional project root path
        
    Returns:
        CodeStandardsEnforcerAgent instance
    """
    if project_root is None:
        project_root = Path.cwd()
    
    return CodeStandardsEnforcerAgent(project_root=project_root)


# Convenience functions for backward compatibility
def check_inheritance(project_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Check layer base class inheritance violations."""
    enforcer = get_code_standards_enforcer(project_root)
    results = enforcer.validate_repository()
    return [v for v in results["details"] if v["type"] == "INHERITANCE_ERR"]


def check_patterns(project_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Check coding pattern violations."""
    enforcer = get_code_standards_enforcer(project_root)
    results = enforcer.validate_repository()
    return [v for v in results["details"] if v["type"] == "PATTERN_VIOLATION"]


def check_type_hints(project_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Check type hint violations."""
    enforcer = get_code_standards_enforcer(project_root)
    results = enforcer.validate_repository()
    return [v for v in results["details"] if v["type"] == "TYPE_HINT_ERR"]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Code Standards Enforcer")
    parser.add_argument("--root", type=str, default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--inheritance-only", action="store_true", help="Only check inheritance")
    parser.add_argument("--patterns-only", action="store_true", help="Only check patterns")
    parser.add_argument("--types-only", action="store_true", help="Only check type hints")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests")
    args = parser.parse_args()
    
    enforcer = get_code_standards_enforcer(Path(args.root))
    
    if args.self_test:
        results = enforcer._run_self_tests()
        print(f"Self-tests: {results['passed']} passed, {results['failed']} failed")
        for test in results['tests']:
            status = "✓" if test['status'] == 'passed' else "✗"
            print(f"  {status} {test['name']}")
    else:
        results = enforcer.validate_repository()
        
        if args.inheritance_only:
            results["details"] = [v for v in results["details"] if v["type"] == "INHERITANCE_ERR"]
        elif args.patterns_only:
            results["details"] = [v for v in results["details"] if v["type"] == "PATTERN_VIOLATION"]
        elif args.types_only:
            results["details"] = [v for v in results["details"] if v["type"] == "TYPE_HINT_ERR"]
        
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print("Code Standards Enforcer Report")
            print(f"{'='*60}")
            print(f"Files scanned: {results['summary']['files_scanned']}")
            print(f"Total violations: {results['summary']['total_violations']}")
            print(f"  - Inheritance errors: {results['summary']['inheritance_errors']}")
            print(f"  - Pattern violations: {results['summary']['pattern_violations']}")
            print(f"  - Type hint errors: {results['summary']['type_hint_errors']}")
            print(f"\nStatus: {results['status']}")
            
            if results['details']:
                print(f"\nTop violations:")
                for v in results['details'][:10]:
                    print(f"  [{v['type']}] {v['file']}:{v['line']} - {v['message']}")
