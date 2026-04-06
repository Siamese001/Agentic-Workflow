"""
Pre-Commit Issue Schema — Dataclasses for structured issue reporting.

Provides a standardized format for pre-commit hooks to emit issues
for aggregation into the end-of-run summary table.

SEVERITY SSOT: Uses agentic_core.L5_safety.config.severity.SeverityLevel
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from agentic_core.L5_safety.config.severity import SeverityLevel as _SeverityLevel

# Backward-compatible alias
SeverityLevel = _SeverityLevel


@dataclass(frozen=True)
class PreCommitIssue:
    """
    Structured representation of a pre-commit issue.

    Attributes:
        hook_id: The pre-commit hook ID (e.g., "adg-burndown-gate")
        hook_name: Human-readable hook name
        severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        file_path: Path to the file with the issue (optional for global issues)
        line_number: Line number where issue occurs (optional)
        issue_type: Category/type of issue (e.g., "hollow_file", "anti_pattern")
        message: Brief issue description
        explanation: Detailed explanation of why this matters and how to fix
        suggestion: Optional specific fix suggestion
    """

    hook_id: str
    hook_name: str
    severity: SeverityLevel
    message: str
    explanation: str
    file_path: str | None = None
    line_number: int | None = None
    issue_type: str = "general"
    suggestion: str | None = None

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> PreCommitIssue:
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        data["severity"] = SeverityLevel(data["severity"])
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data

    @classmethod
    def passed(cls, hook_id: str, hook_name: str) -> PreCommitIssue:
        """Create a "passed" issue for clean hooks."""
        return cls(
            hook_id=hook_id,
            hook_name=hook_name,
            severity=SeverityLevel.INFO,
            message="No issues detected",
            explanation="Hook completed successfully with no violations found.",
            issue_type="passed",
        )

    @classmethod
    def skipped(cls, hook_id: str, hook_name: str, reason: str) -> PreCommitIssue:
        """Create a "skipped" issue for hooks that didn't run."""
        return cls(
            hook_id=hook_id,
            hook_name=hook_name,
            severity=SeverityLevel.INFO,
            message=f"Skipped: {reason}",
            explanation="Hook was skipped (e.g., no matching files staged).",
            issue_type="skipped",
        )


@dataclass
class IssueCollection:
    """Collection of issues from a single hook run."""

    hook_id: str
    hook_name: str
    timestamp: str
    issues: list[PreCommitIssue] = field(default_factory=list)

    def add(self, issue: PreCommitIssue) -> None:
        """Add an issue to the collection."""
        self.issues.append(issue)

    def to_json_lines(self) -> str:
        """Serialize all issues as JSON lines."""
        return "\n".join(issue.to_json() for issue in self.issues)

    def save_to_file(self, path: Path) -> None:
        """Save issues to a JSON lines file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json_lines())
            if self.issues:
                f.write("\n")

    @classmethod
    def load_from_file(cls, hook_id: str, hook_name: str, path: Path) -> IssueCollection:
        """Load issues from a JSON lines file."""
        from datetime import datetime

        collection = cls(
            hook_id=hook_id,
            hook_name=hook_name,
            timestamp=datetime.now().isoformat(),
        )

        if not path.exists():
            return collection

        malformed_count = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        issue = PreCommitIssue.from_json(line)
                        collection.add(issue)
                    except json.JSONDecodeError:
                        malformed_count += 1
                        continue

        if malformed_count > 0:
            import sys
            print(
                f"[pre-commit-summary] WARNING: {malformed_count} malformed JSON lines skipped in {path}",
                file=sys.stderr,
            )

        return collection


# Severity color mapping for terminal output
SEVERITY_COLORS = {
    SeverityLevel.CRITICAL: "\033[91m",  # Bright red
    SeverityLevel.HIGH: "\033[93m",  # Bright yellow
    SeverityLevel.MEDIUM: "\033[94m",  # Bright blue
    SeverityLevel.LOW: "\033[97m",  # Bright white
    SeverityLevel.INFO: "\033[92m",  # Bright green
}

SEVERITY_ICONS = {
    SeverityLevel.CRITICAL: "⛔",
    SeverityLevel.HIGH: "⚠️",
    SeverityLevel.MEDIUM: "🔹",
    SeverityLevel.LOW: "ℹ️",
    SeverityLevel.INFO: "✓",
}

RESET_COLOR = "\033[0m"


def colorize_severity(severity: SeverityLevel, text: str, use_color: bool = True) -> str:
    """Wrap text with color codes for a severity level."""
    if not use_color:
        return text
    color = SEVERITY_COLORS.get(severity, "")
    return f"{color}{text}{RESET_COLOR}"


def get_severity_icon(severity: SeverityLevel) -> str:
    """Get the icon for a severity level."""
    return SEVERITY_ICONS.get(severity, "•")
