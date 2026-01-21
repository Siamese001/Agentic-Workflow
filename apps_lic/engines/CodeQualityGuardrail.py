"""
Code Quality Guardrail - Consolidated Code Quality Checks

Merges:
- CodeFormatter
- DuplicateDetector
- UnusedCleanup
- DependencyPruning
- GitHygiene

Composable Rules:
- formatting: Code style enforcement
- duplication: Duplicate code detection
- unused_code: Unused variable/function removal
- dependencies: Dependency cleanup
- git_hygiene: Git best practices
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodeIssue:
    """Represents a code quality issue."""
    rule: str
    severity: str  # "info", "warning", "error"
    message: str
    file_path: str | None = None
    line_number: int | None = None
    suggestion: str | None = None


@dataclass
class QualityResult:
    """Result of code quality check."""
    valid: bool
    issues: list[CodeIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class CodeQualityGuardrail:
    """
    Consolidated Code Quality Guardrail.

    Provides unified code quality checks with:
    - Code formatting validation
    - Duplicate code detection
    - Unused code detection
    - Dependency analysis
    - Git hygiene checks
    """

    def __init__(self):
        """Initialize code quality guardrail."""
        self.enabled_rules: list[str] = [
            "formatting",
            "duplication",
            "unused_code",
            "dependencies",
            "git_hygiene",
        ]

        # Formatting rules
        self.max_line_length = 120
        self.max_function_length = 50
        self.max_file_length = 500

        # Duplicate detection
        self.min_duplicate_lines = 5
        self.code_hashes: dict[str, list[str]] = {}

        # Unused code patterns
        self.unused_patterns = [
            r"^\s*#\s*TODO",
            r"^\s*#\s*FIXME",
            r"^\s*pass\s*$",
        ]

        # Git hygiene patterns
        self.bad_commit_patterns = [
            r"^fix$",
            r"^wip$",
            r"^test$",
            r"^asdf",
        ]

        # Statistics
        self.checks_performed = 0
        self.issues_found = 0

    async def validate(self, code: str, file_path: str | None = None) -> QualityResult:
        """
        Validate code quality.

        Args:
            code: Code to validate
            file_path: Optional file path for context

        Returns:
            QualityResult with issues
        """
        self.checks_performed += 1
        issues = []

        # Apply enabled rules
        if "formatting" in self.enabled_rules:
            issues.extend(self._check_formatting(code, file_path))

        if "duplication" in self.enabled_rules:
            issues.extend(self._check_duplication(code, file_path))

        if "unused_code" in self.enabled_rules:
            issues.extend(self._check_unused(code, file_path))

        self.issues_found += len(issues)

        return QualityResult(
            valid=not any(i.severity == "error" for i in issues),
            issues=issues,
            metrics={
                "line_count": len(code.splitlines()),
                "issue_count": len(issues)
            }
        )

    def _check_formatting(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check code formatting."""
        issues = []
        lines = code.splitlines()

        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                issues.append(CodeIssue(
                    rule="formatting",
                    severity="warning",
                    message=f"Line exceeds {self.max_line_length} characters ({len(line)})",
                    file_path=file_path,
                    line_number=i,
                    suggestion="Consider breaking this line"
                ))

        # Check file length
        if len(lines) > self.max_file_length:
            issues.append(CodeIssue(
                rule="formatting",
                severity="warning",
                message=f"File exceeds {self.max_file_length} lines ({len(lines)})",
                file_path=file_path,
                suggestion="Consider splitting into multiple files"
            ))

        # Check trailing whitespace
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                issues.append(CodeIssue(
                    rule="formatting",
                    severity="info",
                    message="Trailing whitespace",
                    file_path=file_path,
                    line_number=i
                ))

        return issues

    def _check_duplication(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check for duplicate code."""
        issues = []
        lines = code.splitlines()

        # Check for duplicate blocks
        for i in range(len(lines) - self.min_duplicate_lines):
            block = "\n".join(lines[i:i + self.min_duplicate_lines])
            block_hash = hashlib.md5(block.encode()).hexdigest()

            if block_hash in self.code_hashes:
                if file_path not in self.code_hashes[block_hash]:
                    issues.append(CodeIssue(
                        rule="duplication",
                        severity="warning",
                        message="Duplicate code block detected",
                        file_path=file_path,
                        line_number=i + 1,
                        suggestion="Consider extracting to shared function"
                    ))
            else:
                self.code_hashes[block_hash] = []

            if file_path:
                self.code_hashes[block_hash].append(file_path)

        return issues

    def _check_unused(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check for unused code patterns."""
        issues = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            for pattern in self.unused_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        rule="unused_code",
                        severity="info",
                        message="Potential cleanup needed",
                        file_path=file_path,
                        line_number=i,
                        suggestion="Review and remove if no longer needed"
                    ))

        return issues

    def validate_commit_message(self, message: str) -> QualityResult:
        """
        Validate git commit message.

        Args:
            message: Commit message to validate

        Returns:
            QualityResult with issues
        """
        issues = []

        # Check for bad patterns
        for pattern in self.bad_commit_patterns:
            if re.match(pattern, message.lower().strip()):
                issues.append(CodeIssue(
                    rule="git_hygiene",
                    severity="error",
                    message="Commit message too short or unclear",
                    suggestion="Use descriptive commit messages"
                ))

        # Check minimum length
        if len(message.strip()) < 10:
            issues.append(CodeIssue(
                rule="git_hygiene",
                severity="warning",
                message="Commit message is too short",
                suggestion="Add more context to the commit message"
            ))

        return QualityResult(
            valid=not any(i.severity == "error" for i in issues),
            issues=issues
        )

    def validate_dependencies(self, dependencies: list[str], used: set[str]) -> QualityResult:
        """
        Validate dependencies.

        Args:
            dependencies: List of declared dependencies
            used: Set of actually used dependencies

        Returns:
            QualityResult with unused dependencies
        """
        issues = []
        unused = set(dependencies) - used

        for dep in unused:
            issues.append(CodeIssue(
                rule="dependencies",
                severity="warning",
                message=f"Unused dependency: {dep}",
                suggestion="Consider removing from dependencies"
            ))

        return QualityResult(
            valid=len(issues) == 0,
            issues=issues,
            metrics={
                "total_dependencies": len(dependencies),
                "unused_dependencies": len(unused)
            }
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get code quality statistics."""
        return {
            "checks_performed": self.checks_performed,
            "issues_found": self.issues_found,
            "enabled_rules": self.enabled_rules
        }
