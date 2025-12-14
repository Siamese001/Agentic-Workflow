"""Executive Agent Orchestrator - Thin Coordinator with MCP Integration."""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Add project root to path for mcp_adapter import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from .data_sources import DataSourceProvider
from .k11_shadow_audit import K11ShadowAuditAgent
from .k12_strategy_roadmap import K12StrategyRoadmapAgent
from .k13_interviewer_sim import K13InterviewerSimulationAgent
from .research_tools import TavilyResearcher
from .schema_definitions import get_executive_schema_registry
from .prompt_providers import PromptProviderFactory

try:
    from mcp_adapter import UniversalMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP adapter not available - autonomous browsing/filesystem disabled")


class ExecutiveAgentOrchestrator:
    """Thin orchestrator for executive strategy agents.

    Coordinates K.11, K.12, and K.13 agents without containing
    their implementation details.
    """

    def __init__(self, data_source_provider: Optional[DataSourceProvider] = None, workflow_config: Optional[Dict[str, Any]] = None):
        """Initialize the orchestrator.

        Args:
            data_source_provider: Optional data source provider
            workflow_config: Optional workflow configuration for prompt providers
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

        # Initialize MCP client for autonomous browsing and filesystem
        if MCP_AVAILABLE:
            self.mcp = UniversalMCPClient()
        else:
            self.mcp = None

        # Initialize prompt providers from workflow config
        prompt_providers = PromptProviderFactory.from_workflow_config(workflow_config or {})

        # Initialize agents with their respective prompt providers
        self.k11_agent = K11ShadowAuditAgent(
            data_source_provider=self.data_sources,
            researcher=self.researcher,
            prompt_provider=prompt_providers.get("k11")
        )
        self.k12_agent = K12StrategyRoadmapAgent(
            prompt_provider=prompt_providers.get("k12")
        )
        self.k13_agent = K13InterviewerSimulationAgent(
            data_source_provider=self.data_sources,
            prompt_provider=prompt_providers.get("k13")
        )

        self.logger = logging.getLogger("ExecutiveAgentOrchestrator")

    # K.11 Shadow Audit delegation with MCP browsing
    async def execute_k11_shadow_audit(
        self,
        company_name: str,
        search_context: str = None,
        config: Dict[str, Any] = None
    ):
        """Execute K.11 Shadow Audit via dedicated agent with autonomous browsing."""
        # Check if auto_research is enabled and MCP is available
        auto_research = config.get("auto_research", True) if config else True

        if auto_research and self.mcp and self.researcher:
            self.logger.info(f"🔍 K.11: Autonomous research enabled for {company_name}")

            # Use Tavily to find relevant URLs
            try:
                search_results = await self.researcher.search(
                    f"{company_name} engineering blog technical stack architecture"
                )

                # Browse top 3 results with MCP browser
                browsed_content = []
                for i, result in enumerate(search_results[:3]):
                    try:
                        url = result.get("url", "")
                        self.logger.info(f"📖 Browsing: {url}")

                        # Navigate to URL
                        await self.mcp.execute_tool("browser__navigate", {"url": url})

                        # Get page content
                        content = await self.mcp.execute_tool("browser__get_content", {})
                        browsed_content.append({
                            "url": url,
                            "title": result.get("title", ""),
                            "content": str(content)[:2000]  # Limit content
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to browse {url}: {e}")

                # Append browsed content to search context
                if browsed_content:
                    enriched_context = search_context or ""
                    enriched_context += "\n\n=== AUTONOMOUS BROWSING RESULTS ===\n"
                    for item in browsed_content:
                        enriched_context += f"\nURL: {item['url']}\nTitle: {item['title']}\n"
                        enriched_context += f"Content: {item['content']}\n---\n"

                    search_context = enriched_context
                    self.logger.info(f"✅ Enriched context with {len(browsed_content)} browsed pages")

            except Exception as e:
                self.logger.error(f"Autonomous browsing failed: {e}")

        # Execute K.11 with enriched context
        return await self.k11_agent.execute(
            company_name=company_name,
            search_context=search_context,
            config=config
        )

    # K.12 Strategy Roadmap delegation with MCP filesystem and memory
    async def execute_k12_strategy(
        self,
        job_description: str,
        technical_swot,
        config: Dict[str, Any]
    ):
        """Execute K.12 Strategy Roadmap via dedicated agent with autonomous file saving."""
        # Execute K.12 to generate roadmap
        roadmap = await self.k12_agent.execute(
            job_description=job_description,
            technical_swot=technical_swot,
            config=config
        )

        # Save roadmap to filesystem using MCP
        if self.mcp and roadmap:
            try:
                # Convert roadmap to markdown format
                roadmap_md = f"""# 30-60-90 Day Strategy Roadmap

## Executive Summary
{roadmap.executive_summary}

## Primary Objective
{roadmap.primary_objective}

## 30-Day Milestones
{chr(10).join(f"- {m}" for m in roadmap.milestones_30_days)}

## 60-Day Milestones
{chr(10).join(f"- {m}" for m in roadmap.milestones_60_days)}

## 90-Day Milestones
{chr(10).join(f"- {m}" for m in roadmap.milestones_90_days)}

## Immediate Wins
{chr(10).join(f"- {w}" for w in roadmap.immediate_wins)}

## Key Stakeholders
{chr(10).join(f"- {s}" for s in roadmap.key_stakeholders)}

## Success Criteria
{roadmap.success_criteria}
"""

                # Write to filesystem
                await self.mcp.execute_tool("filesystem__write_file", {
                    "path": "./output/roadmap.md",
                    "content": roadmap_md
                })
                self.logger.info("💾 Roadmap saved to ./output/roadmap.md")

                # Try to save to Postgres memory (optional)
                try:
                    await self.mcp.execute_tool("postgres_memory__query", {
                        "query": f"""
                        INSERT INTO strategies (timestamp, company, roadmap_summary, primary_objective)
                        VALUES (NOW(), '{technical_swot.company_name if hasattr(technical_swot, 'company_name') else 'Unknown'}',
                                '{roadmap.executive_summary[:500]}', '{roadmap.primary_objective[:500]}')
                        """
                    })
                    self.logger.info("🗄️ Roadmap saved to episodic memory")
                except Exception as e:
                    self.logger.warning(f"Could not save to memory (DB may be offline): {e}")

            except Exception as e:
                self.logger.error(f"Failed to save roadmap: {e}")

        return roadmap

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
