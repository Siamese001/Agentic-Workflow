"""
Outreach Engine Package

Provides outreach automation capabilities including:
- Lead vetting and contact validation
- Message generation and compliance
- Campaign orchestration
- Autonomous self-healing
- HOP-based agent architecture (v13.0)

Migrated from archives/Reachout Engine Archive/Agentic LIC/ (2026-01-01):
- workflow_orchestrator.py: HOP2_ResearchAgent and workflow orchestration
- hop_agents/: HOP1_ProfileAnalysisAgent, HOP3_SenderGroundingAgent
- intelligence_librarian.py: IntelligenceLibrarian for offline research
- tools/code_interpreter.py: CodeInterpreterTool, ValidationToolkit
"""


__version__ = "2.0.0"
__author__ = "Agentic Workflow"
__description__ = "Outreach Engine with autonomous capabilities and HOP architecture"

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    # HOP Agents (v13.0 architecture)
    "HOP1_ProfileAnalysisAgent",
    "HOP2_ResearchAgent",
    "HOP3_SenderGroundingAgent",
    # Tools
    "CodeInterpreterTool",
    "ValidationToolkit",
    # Services
    "IntelligenceLibrarian",
]
