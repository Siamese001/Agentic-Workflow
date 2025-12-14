"""K.12 Strategy Roadmap Agent - 30-60-90 Day Architect."""

from typing import Dict, Any, Optional
from .base_agent import BaseExecutiveAgent
from .schema_definitions import TechnicalSWOT, StrategyRoadmap
from .infrastructure_resilience import resilient_execution
from .prompt_providers import K12PromptProvider


class K12StrategyRoadmapAgent(BaseExecutiveAgent):
    """K.12: 30-60-90 Day Strategy Architect Agent.

    Synthesizes identified gaps and technical reality into a tactical
    executive roadmap using People-Process-Technology framework.
    """

    def __init__(self, prompt_provider: Optional[K12PromptProvider] = None):
        """Initialize K.12 agent.

        Args:
            prompt_provider: Optional prompt provider for dynamic prompts
        """
        super().__init__()
        self.prompt_provider = prompt_provider or K12PromptProvider()
        self.stats = {"k12_executions": 0}

    @resilient_execution(fallback_model="gpt-4o")
    async def execute(
        self,
        job_description: str,
        technical_swot: TechnicalSWOT,
        config: Dict[str, Any]
    ) -> StrategyRoadmap:
        """Execute K.12 Strategy Roadmap generation.

        Args:
            job_description: Job description text
            technical_swot: Results from K.11 analysis
            config: Node configuration

        Returns:
            StrategyRoadmap with 30-60-90 day plan
        """
        self.logger.info("Executing K.12 Strategy Roadmap")
        self.stats["k12_executions"] += 1

        # Return mock response if instructor not available
        if not hasattr(self, 'openai_client') or not self.openai_client:
            return StrategyRoadmap(
                executive_summary="Transform engineering organization to deliver scalable AI-powered solutions while improving developer productivity and
                    system reliability.",
                primary_objective="Establish modern MLOps infrastructure and
                    high-performing engineering culture",
                milestones=[
                    {
                        "timeframe": "Day 30",
                        "focus_area": "People",
                        "initiative": "Conduct team assessments and
                            establish 1:1s with all engineers",
                        "success_metric": "100% team assessment completion",
                        "risk_level": "Low"
                    },
                    {
                        "timeframe": "Day 30",
                        "focus_area": "Process",
                        "initiative": "Implement daily standups and sprint planning",
                        "success_metric": "Sprint velocity baseline established",
                        "risk_level": "Low"
                    },
                    {
                        "timeframe": "Day 60",
                        "focus_area": "Technology",
                        "initiative": "Deploy CI/CD pipeline for main applications",
                        "success_metric": "Deployment frequency increased by 50%",
                        "risk_level": "Medium"
                    },
                    {
                        "timeframe": "Day 90",
                        "focus_area": "Technology",
                        "initiative": "Launch first ML model in production",
                        "success_metric": "Model serving with <100ms latency",
                        "risk_level": "High"
                    }
                ],
                immediate_wins=[
                    {
                        "initiative": "Fix top 3 production bugs",
                        "impact": "High",
                        "effort": "Low",
                        "timeline_days": 7
                    },
                    {
                        "initiative": "Set up monitoring dashboard",
                        "impact": "Medium",
                        "effort": "Low",
                        "timeline_days": 14
                    }
                ],
                key_stakeholders=["CTO", "VP Engineering", "Product Lead", "Engineering Managers"],
                success_criteria="90% deployment success rate,
                    40% reduction in incident response time"
            )

        # Execute with structured output
        client, model = self._get_client_and_model(config)
        temperature = config.get("infrastructure_config", {}).get("temperature_override", 0.5)

        # Get system prompt from prompt provider
        system_prompt = self.prompt_provider.get_system_prompt({})

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=StrategyRoadmap,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",
                        "content": f"Job Description:\n\n{job_description}\n\nTechnical SWOT:\n\n{technical_swot}"}
                ],
                temperature=temperature
            )

            self.logger.info("K.12 completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"K.12 execution failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset execution statistics."""
        self.stats["k12_executions"] = 0
