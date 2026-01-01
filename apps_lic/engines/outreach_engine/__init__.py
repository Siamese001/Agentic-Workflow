"""
Outreach Engine Package

Provides outreach automation capabilities including:
- Lead vetting and contact validation
- Message generation and compliance
- Campaign orchestration
- Autonomous self-healing
- HOP-based agent architecture (v13.1)

Migrated from archives/Reachout Engine Archive/Agentic LIC/ (2026-01-01):
- workflow_orchestrator.py: HOP2ResearchAgent and workflow orchestration
- hop_agents/: HOP1ProfileAnalysisAgent, HOP3SenderGroundingAgent
- intelligence_librarian.py: IntelligenceLibrarian for offline research
- tools/code_interpreter.py: CodeInterpreterTool, ValidationToolkit

HARDENED: 2026-01-01 - PascalCase naming + MCPHardenedMixin applied to all agents
"""


__version__ = "2.1.0"
__author__ = "Agentic Workflow"
__description__ = "Outreach Engine with autonomous capabilities and HOP architecture"

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    # HOP Agents (v13.1 architecture - MCP Hardened, PascalCase)
    "HOP1ProfileAnalysisAgent",
    "HOP2ResearchAgent",
    "HOP3SenderGroundingAgent",
    "HOP4RoutingAgent",
    "HOP5GenerationAgent",
    "HOP6ValidationAgent",
    "HOP7GateDecisionAgent",
    "HOP8QAReportAgent",
    # Tools
    "CodeInterpreterTool",
    "ValidationToolkit",
    # Services
    "IntelligenceLibrarian",
]
