"""Executive Agent Orchestrator - Thin Coordinator."""

import os
import logging
from typing import Optional, Dict, Any
from .data_sources import DataSourceProvider
from .k11_shadow_audit import K11ShadowAuditAgent
from .k12_strategy_roadmap import K12StrategyRoadmapAgent
from .k13_interviewer_sim import K13InterviewerSimulationAgent
from .research_tools import TavilyResearcher
from .schema_definitions import get_executive_schema_registry


class ExecutiveAgentOrchestrator:
    """Thin orchestrator for executive strategy agents.
    
    Coordinates K.11, K.12, and K.13 agents without containing
    their implementation details.
    """

    def __init__(self, data_source_provider: Optional[DataSourceProvider] = None):
        """Initialize the orchestrator.

        Args:
            data_source_provider: Optional data source provider
        """
        # Initialize data sources with Tavily API key if available
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.data_sources = data_source_provider or DataSourceProvider(tavily_api_key=tavily_api_key)
        self.schema_registry = get_executive_schema_registry()
        
        # Initialize autonomous researcher
        if tavily_api_key:
            self.researcher = TavilyResearcher(api_key=tavily_api_key)
        else:
            self.researcher = None
            logging.warning("TAVILY_API_KEY not set - autonomous research disabled")

        # Initialize agents
        self.k11_agent = K11ShadowAuditAgent(
            data_source_provider=self.data_sources,
            researcher=self.researcher
        )
        self.k12_agent = K12StrategyRoadmapAgent()
        self.k13_agent = K13InterviewerSimulationAgent(
            data_source_provider=self.data_sources
        )

        self.logger = logging.getLogger("ExecutiveAgentOrchestrator")

    # K.11 Shadow Audit delegation
    async def execute_k11_shadow_audit(
        self,
        company_name: str,
        search_context: str = None,
        config: Dict[str, Any] = None
    ):
        """Execute K.11 Shadow Audit via dedicated agent."""
        return await self.k11_agent.execute(
            company_name=company_name,
            search_context=search_context,
            config=config
        )

    # K.12 Strategy Roadmap delegation
    async def execute_k12_strategy(
        self,
        job_description: str,
        technical_swot,
        config: Dict[str, Any]
    ):
        """Execute K.12 Strategy Roadmap via dedicated agent."""
        return await self.k12_agent.execute(
            job_description=job_description,
            technical_swot=technical_swot,
            config=config
        )

    # K.13 Interviewer Simulation delegation
    async def execute_k13_simulation(
        self,
        interviewer_linkedin: str,
        resume_text: str,
        config: Dict[str, Any]
    ):
        """Execute K.13 Interviewer Simulation via dedicated agent."""
        return await self.k13_agent.execute(
            interviewer_linkedin=interviewer_linkedin,
            resume_text=resume_text,
            config=config
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from all agents."""
        stats = {
            "k11_executions": self.k11_agent.get_statistics()["k11_executions"],
            "k12_executions": self.k12_agent.get_statistics()["k12_executions"],
            "k13_executions": self.k13_agent.get_statistics()["k13_executions"],
            "total_cost_estimate": 0.0,
            "total_tokens_used": 0
        }
        return stats

    def reset_statistics(self) -> None:
        """Reset statistics for all agents."""
        self.k11_agent.reset_statistics()
        self.k12_agent.reset_statistics()
        self.k13_agent.reset_statistics()


# Factory function for backward compatibility
def create_executive_orchestrator(
    brave_search_tool=None,
    data_source_provider: Optional[DataSourceProvider] = None
) -> ExecutiveAgentOrchestrator:
    """Create a configured executive agent orchestrator.

    Args:
        brave_search_tool: Optional Brave Search tool (deprecated)
        data_source_provider: Optional custom data source provider

    Returns:
        ExecutiveAgentOrchestrator instance
    """
    if data_source_provider is None:
        data_source_provider = DataSourceProvider()
    
    return ExecutiveAgentOrchestrator(data_source_provider=data_source_provider)
