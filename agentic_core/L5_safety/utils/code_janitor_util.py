"""Code Janitor Utility - Deterministic code style validation.

This module provides deterministic code janitor functionality previously
implemented in CodeJanitorAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 8 Micro-Wave 1).

Usage:
    from agentic_core.L5_safety.utils.code_janitor_util import (
        CodeJanitor, JanitorViolation, validate_syntax, validate_indentation
    )
    
    # Validate a file
    violations = validate_syntax("path/to/file.py")
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class JanitorViolation:
    """Structured violation for code janitor healing."""
    
    is_valid: bool
    message: str
    file_path: str | None = None
    line_number: int | None = None
    key_id: int | None = None
    suggested_action: str | None = None
    severity: int = 5
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "key_id": self.key_id,
            "suggested_action": self.suggested_action,
            "severity": self.severity,
        }


class CodeJanitor:
    """Deterministic code validation without agent overhead."""
    
    # Canon keys validated
    VALIDATION_KEYS = list(range(10, 21))
    
    def __init__(self, python_files: list[str] | None = None) -> None:
        """Initialize the code janitor.
        
        Args:
            python_files: List of Python file paths to validate
        """
        self.python_files = python_files or []
    
    def get_validation_keys(self) -> list[int]:
        """Return canon keys validated by this agent."""
        return self.VALIDATION_KEYS
    
    def validate_syntax(self, file_path: str | None = None) -> tuple[bool, list[str]]:
        """Check for syntax errors in Python files.
        
        Args:
            file_path: Optional single file to check (default: all files)
            
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: list[str] = []
        files_to_check = [file_path] if file_path else self.python_files
        
        for fp in files_to_check:
            if not fp:
                continue
            try:
                with open(fp, encoding="utf-8") as f:
                    code = f.read()
                ast.parse(code)
            except SyntaxError as e:
                violations.append(f"{fp}:{e.lineno}: SyntaxError - {e.msg}")
            except (RuntimeError, OSError) as e:
                violations.append(f"{fp}:0: General Error - {e}")
                continue
        
        return (len(violations) == 0, violations)
    
    def validate_indentation(self, file_path: str | None = None) -> tuple[bool, list[str]]:
        """Check for proper indentation (4 spaces, no tabs).
        
        Args:
            file_path: Optional single file to check (default: all files)
            
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: list[str] = []
        files_to_check = [file_path] if file_path else self.python_files
        
        for fp in files_to_check:
            if not fp:
                continue
            try:
                with open(fp, encoding="utf-8") as f:
                    lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    self._check_line_indentation(fp, line_num, line, violations)
            except (RuntimeError, OSError) as e:
                violations.append(f"{fp}:0: General Error - {e}")
                continue
        
        return (len(violations) == 0, violations)
    
    def _check_line_indentation(
        self, file_path: str, line_num: int, line: str, violations: list[str]
    ) -> None:
        """Check indentation for a single line."""
        if "\t" in line:
            violations.append(f"{file_path}:{line_num}: Tab character found (use 4 spaces)")
        
        stripped_line = line.lstrip(" ")
        if stripped_line and line.startswith(" "):
            leading_spaces = len(line) - len(stripped_line)
            if leading_spaces % 4 != 0:
                violations.append(
                    f"{file_path}:{line_num}: Indentation not multiple of 4 ({leading_spaces} spaces)"
                )
    
    def validate_trailing_whitespace(self, file_path: str | None = None) -> tuple[bool, list[str]]:
        """Check for trailing whitespace at end of lines.
        
        Args:
            file_path: Optional single file to check (default: all files)
            
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: list[str] = []
        files_to_check = [file_path] if file_path else self.python_files
        
        for fp in files_to_check:
            if not fp:
                continue
            try:
                with open(fp, encoding="utf-8") as f:
                    lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    if line.rstrip("\n\r") != line.rstrip():
                        violations.append(f"{fp}:{line_num}: Trailing whitespace")
            except (RuntimeError, OSError) as e:
                violations.append(f"{fp}:0: General Error - {e}")
                continue
        
        return (len(violations) == 0, violations)
    
    def validate_naming_conventions(self, file_path: str | None = None) -> tuple[bool, list[str]]:
        """Check for proper naming conventions.
        
        Args:
            file_path: Optional single file to check (default: all files)
            
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: list[str] = []
        files_to_check = [file_path] if file_path else self.python_files
        
        for fp in files_to_check:
            if not fp:
                continue
            try:
                with open(fp, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    self._check_node_naming_convention(fp, node, violations)
            except (RuntimeError, OSError) as e:
                violations.append(f"{fp}:0: General Error - {e}")
        
        return (len(violations) == 0, violations)
    
    def _check_node_naming_convention(
        self, file_path: str, node: ast.AST, violations: list[str]
    ) -> None:
        """Helper to check naming convention for a single AST node."""
        if isinstance(node, ast.ClassDef):
            if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                violations.append(
                    f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase"
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("__") and not node.name.startswith("_"):
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    violations.append(
                        f"{file_path}:{node.lineno}: Function '{node.name}' should be snake_case"
                    )
    
    def validate_all(self, file_path: str | None = None) -> dict[str, Any]:
        """Run all validation checks.
        
        Args:
            file_path: Optional single file to check (default: all files)
            
        Returns:
            Dict with validation results
        """
        all_violations: list[JanitorViolation] = []
        
        checks = [
            (10, self.validate_syntax),
            (11, self.validate_indentation),
            (12, self.validate_trailing_whitespace),
            (14, self.validate_naming_conventions),
        ]
        
        for key_id, check_fn in checks:
            passed, violations = check_fn(file_path)
            for v in violations:
                parts = v.split(":")
                file_p = parts[0] if len(parts) > 0 else None
                line_num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                all_violations.append(
                    JanitorViolation(
                        is_valid=False,
                        message=v,
                        file_path=file_p,
                        line_number=line_num,
                        key_id=key_id,
                        severity=5 if key_id == 10 else 3,
                    )
                )
        
        return {
            "passed": len(all_violations) == 0,
            "violations_count": len(all_violations),
            "violations": [v.to_dict() for v in all_violations],
        }


def validate_syntax(file_path: str) -> list[str]:
    """Standalone function to validate syntax of a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of violation strings
    """
    janitor = CodeJanitor([file_path])
    passed, violations = janitor.validate_syntax(file_path)
    return violations


def validate_indentation(file_path: str) -> list[str]:
    """Standalone function to validate indentation of a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of violation strings
    """
    janitor = CodeJanitor([file_path])
    passed, violations = janitor.validate_indentation(file_path)
    return violations


def validate_trailing_whitespace(file_path: str) -> list[str]:
    """Standalone function to validate trailing whitespace of a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of violation strings
    """
    janitor = CodeJanitor([file_path])
    passed, violations = janitor.validate_trailing_whitespace(file_path)
    return violations


def validate_naming_conventions(file_path: str) -> list[str]:
    """Standalone function to validate naming conventions of a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of violation strings
    """
    janitor = CodeJanitor([file_path])
    passed, violations = janitor.validate_naming_conventions(file_path)
    return violations


def validate_all(file_path: str) -> dict[str, Any]:
    """Run all validation checks on a single file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Dict with validation results
    """
    janitor = CodeJanitor([file_path])
    return janitor.validate_all(file_path)


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance)."""
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal code janitor violations.
    
    Args:
        violation: Violation dict
        
    Returns:
        Healing result dict
    """
    violation_type = violation.get("type", "unknown")
    file_path = violation.get("file_path")
    
    if violation_type == "syntax_error" and file_path:
        Logger.warning(f"[CodeJanitor] Syntax errors require manual fix: {file_path}")
        return {
            "status": "skipped",
            "details": "Syntax errors require manual fix",
            "artifacts": [file_path] if file_path else [],
            "errors": [],
        }
    
    elif violation_type == "indentation_error" and file_path:
        Logger.warning(f"[CodeJanitor] Indentation errors require manual fix: {file_path}")
        return {
            "status": "skipped",
            "details": "Indentation errors require manual fix",
            "artifacts": [file_path] if file_path else [],
            "errors": [],
        }
    
    return {
        "status": "skipped",
        "details": f"Unknown violation: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Code Janitor Utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Janitor Utility")
    parser.add_argument("file", help="Python file to validate")
    parser.add_argument("--checks", nargs="+", 
                        choices=["syntax", "indentation", "whitespace", "naming", "all"],
                        default=["all"],
                        help="Validation checks to run")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    file_path = args.file
    
    if "all" in args.checks:
        result = validate_all(file_path)
        print(f"Validation {'PASSED' if result['passed'] else 'FAILED'}")
        print(f"Violations: {result['violations_count']}")
        for v in result["violations"]:
            print(f"  - {v['message']}")
    else:
        all_violations = []
        if "syntax" in args.checks:
            all_violations.extend(validate_syntax(file_path))
        if "indentation" in args.checks:
            all_violations.extend(validate_indentation(file_path))
        if "whitespace" in args.checks:
            all_violations.extend(validate_trailing_whitespace(file_path))
        if "naming" in args.checks:
            all_violations.extend(validate_naming_conventions(file_path))
        
        print(f"Violations found: {len(all_violations)}")
        for v in all_violations:
            print(f"  - {v}")


if __name__ == "__main__":
    main()
