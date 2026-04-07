from __future__ import annotations

"\nChange Tracker - Sovereign Healing Audit Trail\nCanon-compliant utility for tracking file modifications by healer/fixer agents.\n\nLocation: agentic_core/utils/general_helpers/change_tracker.py\nDepth: 3 (per SSOT semantic_l2_registry['utils']['general_helpers'])\nPurpose: Domain-agnostic core utility for miscellaneous tracking\n"
import uuid
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)


class ChangeRecord:
    """Record of a single file modification by a healer/fixer agent."""

    def __init__(self, agent: str, file_path: str | Path, description: str):
        self.agent = agent
        self.file_path = str(Path(file_path).resolve())
        self.description = description


class ChangeTracker:
    """
    Tracks all file modifications during healing operations.

    Provides exact traceability of which healer/fixer touched which file,
    producing a detailed Markdown report with by-agent and by-file views.
    """

    def __init__(self):
        self.records: list[ChangeRecord] = []

    def record(self, agent: str, file_path: str | Path, description: str):
        """Record a successful file modification immediately after writing."""
        self.records.append(ChangeRecord(agent, file_path, description))

    def _group_by_agent(self) -> dict[str, list[tuple[str, str]]]:
        """Group all records by agent name."""
        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for rec in self.records:
            groups[rec.agent].append((rec.file_path, rec.description))
        return groups

    def _group_by_file(self) -> dict[str, list[tuple[str, str]]]:
        """Group all records by file path."""
        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for rec in self.records:
            groups[rec.file_path].append((rec.agent, rec.description))
        return groups

    def generate_markdown_report(self) -> str:
        """Generate a detailed Markdown report of all changes."""
        _emit_snapshots_state(str(uuid.uuid4()), "ChangeTracker.generate_markdown_report", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ChangeTracker.generate_markdown_report",
        )

        by_agent = self._group_by_agent()
        by_file = self._group_by_file()
        lines = ["## Sovereign Healing Change Report (Canon-Compliant)\n"]
        lines.append("### Changes by Healer/Fixer\n")
        for agent, changes in sorted(by_agent.items()):
            lines.append(f"\n**{agent}** — {len(changes)} file(s) modified")
            for file_path, desc in changes:
                lines.append(f"- `{file_path}`: {desc}")
        lines.append("\n### Changes by File\n")
        for file_path, changes in sorted(by_file.items()):
            lines.append(f"\n**`{file_path}`** — modified by {len(changes)} healer(s)")
            for agent, desc in changes:
                lines.append(f"- {agent}: {desc}")
        lines.append(f"\n**Total recorded modifications:** {len(self.records)}\n")
        return "\n".join(lines)

    def clear(self):
        """Clear all recorded changes."""
        self.records.clear()

    def __len__(self) -> int:
        """Return the number of recorded changes."""
        return len(self.records)
