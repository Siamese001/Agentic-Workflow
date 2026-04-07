"""Reporting module for execute_ssot - extracted during Wave 1 modularization.

This module contains reporting and output formatting functionality.
"""

import json
import time
from typing import Any


class ExecutionReporter:
    """Generates execution reports and handles output formatting."""

    def __init__(self, console: Any = None, verbose: bool = False):
        self.console = console
        self.verbose = verbose
        self.logs: list[dict] = []

    def log(self, message: str, level: str = "info") -> None:
        """Log a message with timestamp.

        Args:
            message: Message to log
            level: Log level (info, warning, error)
        """
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
        }
        self.logs.append(entry)

        if self.console:
            # Console output
            pass

    def generate_summary(self, phase_results: dict[str, Any]) -> dict[str, Any]:
        """Generate execution summary from phase results.

        Args:
            phase_results: Results from each phase

        Returns:
            Summary dictionary
        """
        summary = {
            "phases_completed": list(phase_results.keys()),
            "total_phases": len(phase_results),
            "timestamp": time.time(),
            "logs": self.logs,
        }
        return summary

    def generate_json_report(self, data: dict[str, Any]) -> str:
        """Generate JSON formatted report.

        Args:
            data: Report data

        Returns:
            JSON string
        """
        return json.dumps(data, indent=2, default=str)

    def generate_markdown_report(self, data: dict[str, Any]) -> str:
        """Generate Markdown formatted report.

        Args:
            data: Report data

        Returns:
            Markdown string
        """
        lines = [
            "# Execution Report",
            "",
            f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Phases Completed:** {data.get('total_phases', 0)}",
            "",
            "## Phase Results",
            "",
        ]

        for phase, result in data.get('phase_results', {}).items():
            lines.append(f"### {phase}")
            lines.append("```")
            lines.append(json.dumps(result, indent=2, default=str))
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def save_report(self, filepath: str, data: dict[str, Any], format: str = "json") -> tuple[bool, str | None]:
        """Save report to file.

        Args:
            filepath: Output file path
            data: Report data
            format: Output format (json, markdown)

        Returns:
            Tuple of (success, error_message)
        """
        if not filepath:
            return False, "Filepath cannot be empty"

        if not data:
            return False, "Data cannot be empty"

        try:
            if format == "json":
                content = self.generate_json_report(data)
            elif format == "markdown":
                content = self.generate_markdown_report(data)
            else:
                return False, f"Unsupported format: {format}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, None
        except UnicodeEncodeError as e:
            return False, f"Encoding error: {str(e)}"
        except OSError as e:
            return False, f"IO error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
