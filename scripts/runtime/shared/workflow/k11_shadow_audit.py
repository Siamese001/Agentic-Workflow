"""K.11 Shadow Audit Agent - Technical Due Diligence."""

import logging
from typing import Dict, Any, Optional
from .base_agent import BaseExecutiveAgent
from .schema_definitions import TechnicalSWOT
from .research_tools import TavilyResearcher
from .infrastructure_resilience import resilient_execution
from .prompt_providers import K11PromptProvider


class K11ShadowAuditAgent(BaseExecutiveAgent):
    """K.11: Technical Due Diligence (Shadow Audit) Agent.

    Analyzes target company's engineering blog, GitHub, and leadership
    interviews to infer technical maturity and debt.
    """

    def __init__(self, data_source_provider=None, researcher: Optional[TavilyResearcher] = None, prompt_provider: Optional[K11PromptProvider] = None):
        """Initialize K.11 agent.

        Args:
            data_source_provider: Optional data source provider
            researcher: Optional Tavily researcher for autonomous search
            prompt_provider: Optional prompt provider for dynamic prompts
        """
        super().__init__()
        self.data_sources = data_source_provider
        self.researcher = researcher
        self.prompt_provider = prompt_provider or K11PromptProvider()
        self.stats = {"k11_executions": 0}

    @resilient_execution(fallback_model="gpt-4o")
    async def execute(
        self,
        company_name: str,
        search_context: str = None,
        config: Dict[str, Any] = None
    ) -> TechnicalSWOT:
        """Execute K.11 Shadow Audit.

        Args:
            company_name: Target company name
            search_context: Optional manual search context (if None, will use automated search)
            config: Node configuration

        Returns:
            TechnicalSWOT analysis
        """
        self.logger.info(f"Executing K.11 Shadow Audit for {company_name}")
        self.stats["k11_executions"] += 1

        # Use automated search if no manual context provided
        if search_context is None:
            # Check if auto-research is enabled in config
            if config and config.get("auto_research", {}).get("enabled", False) and self.researcher:
                self.logger.info("Using autonomous TavilyResearcher for deep search")
                search_context = self.researcher.execute_shadow_audit_search(company_name)
            else:
                self.logger.info("Using fallback automated search via DataSourceProvider")
                search_context = self.data_sources.automated_company_research(company_name)
        else:
            self.logger.info("Using manually provided search context")

        # Return mock response if instructor not available
        if not hasattr(self, 'openai_client') or not self.openai_client:
            return TechnicalSWOT(
                current_stack=[
                    {
                        "category": "Frontend",
                        "tool_name": "React",
                        "confidence_score": 0.9,
                        "evidence_source": "Engineering Blog 2023",
                        "maturity_level": "Modern"
                    },
                    {
                        "category": "Backend",
                        "tool_name": "Python/Django",
                        "confidence_score": 0.8,
                        "evidence_source": "GitHub repos",
                        "maturity_level": "Stable"
                    },
                    {
                        "category": "Data",
                        "tool_name": "PostgreSQL",
                        "confidence_score": 0.7,
                        "evidence_source": "Job postings",
                        "maturity_level": "Stable"
                    }
                ],
                suspected_bottlenecks=[
                    "Legacy monolith architecture slowing deployment",
                    "Limited automated testing coverage",
                    "On-premise data warehouse limiting scalability"
                ],
                gen_ai_maturity_score=2,
                strategic_opportunity="Lead migration to modern MLOps stack with automated CI/CD"
            )

        # Execute with structured output
        if config is None:
            config = {}
        client, model = self._get_client_and_model(config)
        temperature = config.get("infrastructure_config", {}).get("temperature_override", 0.2)

        # Get system prompt from prompt provider
        system_prompt = self.prompt_provider.get_system_prompt({"company_name": company_name})

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=TechnicalSWOT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Search Context:\n\n{search_context}"}
                ],
                temperature=temperature
            )

            self.logger.info(f"K.11 completed successfully for {company_name}")
            return result

        except Exception as e:
            self.logger.error(f"K.11 execution failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset execution statistics."""
        self.stats["k11_executions"] = 0
