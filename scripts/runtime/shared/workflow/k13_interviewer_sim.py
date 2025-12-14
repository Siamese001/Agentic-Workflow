"""K.13 Interviewer Simulation Agent - Oppositional Preparation."""

from typing import Dict, Any, Optional
from scripts.runtime.shared.workflow.base_agent import BaseExecutiveAgent
from scripts.runtime.shared.workflow.schema_definitions import InterviewerProfile
from scripts.runtime.shared.workflow.infrastructure_resilience import resilient_execution
from scripts.runtime.shared.workflow.prompt_providers import K13PromptProvider


class K13InterviewerSimulationAgent(BaseExecutiveAgent):
    """K.13: Oppositional Interview Simulation Agent.

    Simulates the specific interviewer's questioning style based on
    their public digital footprint and background.
    """

    def __init__(self,
        data_source_provider=None,
        prompt_provider: Optional[K13PromptProvider] = None):
        """Initialize K.13 agent.

        Args:
            data_source_provider: Optional data source provider for profile research
            prompt_provider: Optional prompt provider for dynamic prompts
        """
        super().__init__()
        self.data_sources = data_source_provider
        self.prompt_provider = prompt_provider or K13PromptProvider()
        self.stats = {"k13_executions": 0}

    @resilient_execution(fallback_model="gpt-4o")
    async def execute(
        self,
        interviewer_linkedin: str,
        resume_text: str,
        config: Dict[str, Any]
    ) -> InterviewerProfile:
        """Execute K.13 Interviewer Simulation.

        Args:
            interviewer_linkedin: LinkedIn profile URL
            resume_text: Candidate's resume text
            config: Node configuration

        Returns:
            InterviewerProfile with simulation insights
        """
        self.logger.info("Executing K.13 Interviewer Simulation")
        self.stats["k13_executions"] += 1

        # Gather interviewer background
        interviewer_background = ""
        if self.data_sources:
            interviewer_background = await self.
                .data_sources.
                .get_interviewer_profile(interviewer_linkedin)

        # Return mock response if instructor not available
        if not hasattr(self, 'openai_client') or not self.openai_client:
            return InterviewerProfile(
                interviewer_name="Senior Engineering Manager",
                role="VP of Engineering",
                company_background="Fast-growing SaaS company",
                interview_style="Technical deep-dive with behavioral questions",
                key_biases=[
                    {
                        "category": "Technical",
                        "preference": "Hands-on coding experience",
                        "aversion": "Pure management without technical depth",
                        "how_to_leverage": "Emphasize recent technical contributions"
                    }
                ],
                kill_chain_questions=[
                    {
                        "question_text": "Tell me about a time you had to make a difficult technical trade-off",
                        "question_type": "Technical",
                        "rationale": "Wants to see technical judgment and decision-making",
                        "recommended_angle": "Focus on systematic evaluation and business impact",
                        "difficulty": "Hard",
                        "follow_up_likelihood": "High"
                    }
                ],
                conversation_starters=["Tell me about your background",
                    "What brings you here today?"],
                decision_factors=["Technical depth", "Leadership experience", "Culture fit"],
                red_flags=["Arrogance", "Blaming others", "No concrete examples"]
            )

        # Execute with structured output
        client, model = self._get_client_and_model(config)
        temperature = config.get("infrastructure_config", {}).get("temperature_override", 0.7)

        # Get system prompt from prompt provider
        system_prompt = self.prompt_provider.get_system_prompt({})

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=InterviewerProfile,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",
                        "content": f"Interviewer Profile:\n\n{interviewer_background}\n\nCandidate Resume:\n\n{resume_text}"}
                ],
                temperature=temperature
            )

            self.logger.info("K.13 completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"K.13 execution failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset execution statistics."""
        self.stats["k13_executions"] = 0
