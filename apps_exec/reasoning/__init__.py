"""
apps_exec Reasoning Layer — Executive Brief Generator Agents.

Multi-agent ecosystem for source ingestion, brief assembly, and style compliance.
"""

from apps_exec.reasoning.BriefAssemblyAgent import BriefAssemblyAgent
from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
from apps_exec.reasoning.SourceIngestionAgent import SourceIngestionAgent
from apps_exec.reasoning.StyleComplianceAgent import StyleComplianceAgent

__all__ = [
    "ExecOrchestrator",
    "SourceIngestionAgent",
    "BriefAssemblyAgent",
    "StyleComplianceAgent",
]
