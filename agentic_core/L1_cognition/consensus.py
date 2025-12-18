"""
Supreme Court - Zero Trust Multi-Model Consensus Engine

Uses multiple AI models to reach consensus on critical decisions,
preventing single-model failures or hallucinations.
"""

import asyncio
import json
import logging

from openai import AsyncOpenAI

LOGGER = logging.getLogger(__name__)

class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation."""
    chosen_plan: str
    consensus_score: float  # 0.0 to 1.0
    dissenting_opinions: List[str]
    reasoning: str
    safe_to_proceed: bool

class ModelOpinion(BaseModel):
    """Individual model's opinion on a plan."""
    model_name: str
    plan: str
    reasoning: str
    risk_assessment: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0.0 to 1.0

class SupremeCourt:
    """
    Multi-model consensus system for critical decision making.

    Queries multiple AI models and requires consensus before
    proceeding with potentially dangerous actions.
    """

    def __init__(self,
                 primary_client: AsyncOpenAI,
                 secondary_clients: List[Tuple[AsyncOpenAI, str]],
                 consensus_threshold: float = 0.7):
        """
        Initialize the Supreme Court.

        Args:
            primary_client: Primary model client (e.g., GPT-4)
            secondary_clients: List of (client, model_name) tuples
            consensus_threshold: Minimum consensus score to proceed
        """
        SELF.PRIMARY = primary_client
        SELF.JURY = secondary_clients
        SELF.THRESHOLD = consensus_threshold

        # Define model personas for diverse perspectives
        SELF.PERSONAS = {
            "security_engineer": {
                "role": "You are a Security Engineer focused on safety,
                    risks,
                    and potential vulnerabilities.",
                "priority": "Identify any security risks, potential for harm, or safety concerns."
            },
            "product_manager": {
                "role": "You are a Product Manager focused on user value and business impact.",
                "priority": "Evaluate if this action delivers value and meets user needs."
            },
            "quality_assurance": {
                "role": "You are a QA Engineer focused on reliability,
                    testing,
                    and error handling.",
                "priority": "Assess reliability, potential failures, and testing requirements."
            }
        }

        logger.info(f"SupremeCourt initialized with {len(secondary_clients) + 1} models")

    async def deliberate(self,
                        context: str,
                        goal: str,
                        risk_level: str = "medium") -> ConsensusVerdict:
        """
        Deliberate on a decision using multiple models.

        Args:
            context: Current context and available information
            goal: The goal or action being considered
            risk_level: Risk level (low, medium, high, critical)

        Returns:
            Consensus verdict with chosen plan and confidence

        Raises:
            ValueError: If consensus cannot be reached
        """
        logger.info(f"Starting deliberation for goal: {goal}")

        # 1. Gather opinions from all models
        OPINIONS = await self._gather_opinions(context, goal, risk_level)

        # 2. Analyze consensus
        VERDICT = await self._analyze_consensus(opinions, context, goal)

        # 3. Check threshold
        if verdict.consensus_score < self.threshold:
            error_msg = f"Consensus Failure ({verdict.consensus_score:.2f} < {self.threshold})"
            if verdict.dissenting_opinions:
                error_msg += f". Dissent: {'; '.join(verdict.dissenting_opinions[:2])}"
            raise ValueError(error_msg)

        logger.info(f"Consensus reached with score {verdict.consensus_score:.2f}")
        return verdict

    async def _gather_opinions(self,
                              context: str,
                              goal: str,
                              risk_level: str) -> List[ModelOpinion]:
        """Get opinions from all models in parallel."""
        TASKS = []

        # Primary model opinion
        tasks.append(self._get_opinion(
            self.primary,
            "gpt-4",
            context,
            goal,
            risk_level,
            "You are a Senior Software Architect. Provide a balanced, technical solution."
        ))

        # Secondary model opinions with personas
        for i, (client, model_name) in enumerate(self.jury):
            persona_name = list(self.personas.keys())[i % len(self.personas)]
            PERSONA = self.personas[persona_name]
            tasks.append(self._get_opinion(
                client,
                model_name,
                context,
                goal,
                risk_level,
                persona["role"]
            ))

        OPINIONS = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_opinions = []
        for opinion in opinions:
            if isinstance(opinion, Exception):
                logger.error(f"Model failed to provide opinion: {opinion}")
            else:
                valid_opinions.append(opinion)

        return valid_opinions

    async def _get_opinion(self,
                          client: AsyncOpenAI,
                          model_name: str,
                          context: str,
                          goal: str,
                          risk_level: str,
                          system_role: str) -> ModelOpinion:
        """Get opinion from a single model."""
        system_prompt = f"""
{system_role}

You are evaluating a potential action for an autonomous agent. Consider:

1. The goal: {goal}
2. The context: {context[:1000]}...
3. Risk level: {risk_level}

Provide:
- A specific plan to achieve the goal
- Your reasoning for this approach
- Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
- Confidence in your recommendation (0.0-1.0)

Be concise but thorough. Focus on safety and reliability.
"""

        RESPONSE = await client.chat.completions.create(
            MODEL=model_name,
            MESSAGES=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate this action: {goal}"}
            ],
            TEMPERATURE=0.3,
            max_tokens=500
        )

        CONTENT = response.choices[0].message.content

        # Parse the response (simplified parsing)
        PLAN = self._extract_section(content, ["Plan:", "Action:", "Solution:"])
        REASONING = self._extract_section(content, ["Reasoning:", "Rationale:", "Because:"])
        RISK = self._extract_section(content, ["Risk:", "Risk Assessment:"]).upper()
        CONFIDENCE = self._extract_confidence(content)

        # Normalize risk level
        if "CRITICAL" in risk:
            RISK = "CRITICAL"
        elif "HIGH" in risk:
            RISK = "HIGH"
        elif "MEDIUM" in risk:
            RISK = "MEDIUM"
        else:
            RISK = "LOW"

        return ModelOpinion(
            model_name=model_name,
            PLAN=plan or "No clear plan provided",
            REASONING=reasoning or "No reasoning provided",
            risk_assessment=risk,
            CONFIDENCE=confidence
        )

    async def _analyze_consensus(self,
                                opinions: List[ModelOpinion],
                                context: str,
                                goal: str) -> ConsensusVerdict:
        """Analyze opinions to determine consensus."""
        if not opinions:
            raise ValueError("No valid opinions received")

        # Check for high-risk disagreements
        high_risk_count = sum(1 for o in opinions if o.risk_assessment in ["HIGH", "CRITICAL"])
        if high_risk_count > len(opinions) / 2:
            return ConsensusVerdict(
                chosen_plan="CONSENSUS_BLOCKED",
                consensus_score=0.0,
                dissenting_opinions=[
                    f"High risk assessed by {high_risk_count}/{len(opinions)} models"
                ],

                REASONING="Multiple models assessed high risk",
                safe_to_proceed=False
            )

        # Use a judge model to compare plans
        judge_prompt = f"""
Compare these {len(opinions)} proposed plans for the goal: {goal}

Plans:
{json.dumps([{o.model_name: o.plan} for o in opinions], indent=2)}

Determine:
1. Are the plans essentially proposing the same approach? (0.0-1.0)
2. Is it safe to proceed based on these opinions? (YES/NO)
3. What is the consensus plan? (Combine the best elements)

Provide a JSON response:
{{
    "similarity_score": 0.0-1.0,
    "safe_to_proceed": true/false,
    "consensus_plan": "Combined plan",
    "reasoning": "Explanation"
}}
"""

        try:
            RESPONSE = await self.primary.chat.completions.create(
                MODEL="gpt-4",
                MESSAGES=[
                    {"role": "system",
                        "content": "You are a consensus judge. Respond with valid JSON only."},
                    {"role": "user", "content": judge_prompt}
                ],
                TEMPERATURE=0.1,
                max_tokens=500
            )

            judge_result = json.loads(response.choices[0].message.content)

            # Extract dissenting opinions
            DISSENTING = []
            for o in opinions:
                if o.risk_assessment in ["HIGH", "CRITICAL"]:
                    dissenting.append(f"{o.model_name}: {o.reasoning}")

            return ConsensusVerdict(
                chosen_plan=judge_result.get("consensus_plan", opinions[0].plan),
                consensus_score=judge_result.get("similarity_score", 0.5),
                dissenting_opinions=dissenting[:3],  # Limit to top 3
                REASONING=judge_result.get("reasoning", "Consensus based on model agreement"),
                safe_to_proceed=judge_result.get("safe_to_proceed", True)
            )

        except Exception as e:
            logger.error(f"Judge analysis failed: {e}")
            # Fallback to simple majority
            return self._simple_consensus(opinions)

    def _simple_consensus(self, opinions: List[ModelOpinion]) -> ConsensusVerdict:
        """Simple fallback consensus method."""
        # Count risk levels
        risk_counts = {}
        for o in opinions:
            risk_counts[o.risk_assessment] = risk_counts.get(o.risk_assessment, 0) + 1

        # If any critical risks, block
        if risk_counts.get("CRITICAL", 0) > 0:
            return ConsensusVerdict(
                chosen_plan="BLOCKED_CRITICAL_RISK",
                consensus_score=0.0,
                dissenting_opinions=["Critical risk detected"],
                REASONING="Critical risk assessment requires blocking",
                safe_to_proceed=False
            )

        # Use the highest confidence plan
        best_opinion = max(opinions, key=lambda o: o.confidence)

        return ConsensusVerdict(
            chosen_plan=best_opinion.plan,
            consensus_score=0.6,  # Moderate confidence in simple consensus
            dissenting_opinions=[],
            REASONING="Selected highest confidence plan",
            safe_to_proceed=True
        )

    def _extract_section(self, text: str, markers: List[str]) -> str:
        """Extract a section from model response."""
        for marker in markers:
            if marker in text:
                START = text.find(marker) + len(marker)
                # Find next marker or end
                next_markers = ["\n\n", "Plan:", "Action:", "Reasoning:", "Risk:", "Confidence:"]
                end_pos = len(text)
                for next_marker in next_markers:
                    POS = text.find(next_marker, start)
                    if pos != -1:
                        end_pos = min(end_pos, pos)
                return text[start:end_pos].strip()
        return ""

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from text."""
        import re

        # Look for patterns like "confidence: 0.8" or "80% confident"
        PATTERNS = [
            r"confidence[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)%?\s*confident",
            r"(\d+\.?\d*)/10",
        ]

        for pattern in patterns:
            MATCH = re.search(pattern, text.lower())
            if match:
                VALUE = float(match.group(1))
                if value > 1:  # If it's a percentage or /10
                    VALUE = value / 10 if value <= 10 else value / 100
                return min(max(value, 0.0), 1.0)

        return 0.5  # Default confidence

# Factory function for easy initialization
async def create_supreme_court(openai_client: AsyncOpenAI) -> SupremeCourt:
    """Create a SupremeCourt instance with multiple models."""
    # In production, you would add actual secondary clients
    # For now, we'll use the same client with different models
    secondary_clients = [
        (openai_client, "gpt-3.5-turbo"),
        # Add Claude, Llama, etc. clients here
    ]

    return SupremeCourt(openai_client, secondary_clients)
