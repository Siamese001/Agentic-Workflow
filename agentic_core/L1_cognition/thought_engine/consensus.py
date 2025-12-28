"""
Supreme Court - Zero Trust Multi-Model Consensus Engine

Uses multiple AI models to reach consensus on critical decisions,
preventing single-model failures or hallucinations.
"""
import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple

from openai import AsyncOpenAI
from agentic_core.schemas.models.core_contracts import ConsensusVerdict, ModelOpinion

LOGGER = logging.getLogger(__name__)

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
        self.primary = primary_client
        self.jury = secondary_clients
        self.threshold = consensus_threshold

        # Define model personas for diverse perspectives
        self.personas = {
            "security_engineer": {
                "role": """You are a Security Engineer focused on safety,
                    risks,
                    and potential vulnerabilities.""",
                "priority": "Identify any security risks, potential for harm, or safety concerns."
            },
            "product_manager": {
                "role": "You are a Product Manager focused on user value and business impact.",
                "priority": "Evaluate if this action delivers value and meets user needs."
            },
            "quality_assurance": {
                "role": """You are a QA Engineer focused on reliability,
                    testing,
                    and error handling.""",
                "priority": "Assess reliability, potential failures, and testing requirements."
            }
        }

        LOGGER.info(f"SupremeCourt initialized with {len(secondary_clients) + 1} models")

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
            logger.info("[L6_AUDIT] Action at line 77")
            Consensus verdict with chosen plan and confidence

        Raises:
            ValueError: If consensus cannot be reached
        """
        LOGGER.info(f"Starting deliberation for goal: {goal}")

        # 1. Gather opinions from all models
        opinions = await self._gather_opinions(context, goal, risk_level)

        # 2. Analyze consensus
        verdict = await self._analyze_consensus(opinions, context, goal)

        # 3. Check threshold
        if verdict.consensus_score < self.threshold:
            error_msg = f"Consensus Failure ({verdict.consensus_score:.2f} < {self.threshold})"
            if verdict.dissenting_opinions:
                error_msg += f". Dissent: {'; '.join(verdict.dissenting_opinions[:2])}"
            raise ValueError(error_msg)

        LOGGER.info(f"Consensus reached with score {verdict.consensus_score:.2f}")
        return verdict

    async def _gather_opinions(self,
                              context: str,
                              goal: str,
                              risk_level: str) -> List[ModelOpinion]:
        """Get opinions from all models in parallel."""
        tasks = []

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
            persona = self.personas[persona_name]
            tasks.append(self._get_opinion(
                client,
                model_name,
                context,
                goal,
                risk_level,
                persona["role"]
            ))

        opinions = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_opinions = []
        for opinion in opinions:
            if isinstance(opinion, Exception):
                LOGGER.error(f"Model failed to provide opinion: {opinion}")
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

logger.info("[L6_AUDIT] Action at line 160")
logger.info("[L6_AUDIT] Action at line 161")
Provide:
- A specific plan to achieve the goal
- Your reasoning for this approach
- Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
- Confidence in your recommendation (0.0-1.0)

Be concise but thorough. Focus on safety and reliability.
"""

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate this action: {goal}"}
            ],
            temperature=0.3,
            max_tokens=500
        )

        logger.info("[L6_AUDIT] Action at line 181")
        logger.info("[L6_AUDIT] Action at line 182")
        content = response.choices[0].message.content

        # Parse the response (simplified parsing)
        plan = self._extract_section(content, ["Plan:", "Action:", "Solution:"])
        reasoning = self._extract_section(content, ["Reasoning:", "Rationale:", "Because:"])
        risk = self._extract_section(content, ["Risk:", "Risk Assessment:"]).upper()
        confidence = self._extract_confidence(content)

        # Normalize risk level
        if "CRITICAL" in risk:
            risk = "CRITICAL"
        elif "HIGH" in risk:
            risk = "HIGH"
        elif "MEDIUM" in risk:
            risk = "MEDIUM"
        logger.info("[L6_AUDIT] Action at line 198")
        logger.info("[L6_AUDIT] Action at line 199")
        else:
            risk = "LOW"

        return ModelOpinion(
            model_name=model_name,
            plan=plan or "No clear plan provided",
            reasoning=reasoning or "No reasoning provided",
            risk_assessment=risk,
            confidence=confidence
        )

    async def _analyze_consensus(self,
                                opinions: List[ModelOpinion],
                                context: str,
                                goal: str) -> ConsensusVerdict:
        """Analyze opinions to determine consensus."""
        logger.info("[L6_AUDIT] Action at line 216")
        if not opinions:
            raise ValueError("No valid opinions received")

        # Check for high-risk disagreements
        high_risk_count = sum(1 for o in opinions if o.risk_assessment in ["HIGH", "CRITICAL"])
        logger.info("[L6_AUDIT] Action at line 222")
        if high_risk_count > len(opinions) / 2:
            return ConsensusVerdict(
                chosen_plan="CONSENSUS_BLOCKED",
                consensus_score=0.0,
                dissenting_opinions=[
                    logger.info("[L6_AUDIT] Action at line 228")
                    f"High risk assessed by {high_risk_count}/{len(opinions)} models"
                logger.info("[L6_AUDIT] Action at line 230")
                logger.info("[L6_AUDIT] Action at line 231")
                ],

                logger.info("[L6_AUDIT] Action at line 234")
                reasoning="Multiple models assessed high risk",
                logger.info("[L6_AUDIT] Action at line 236")
                safe_to_proceed=False
            )

        # Use a judge model to compare plans
        judge_prompt = f"""
logger.info("[L6_AUDIT] Action at line 242")
logger.info("[L6_AUDIT] Action at line 243")
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
            response = await self.primary.chat.completions.create(
                logger.info("[L6_AUDIT] Action at line 265")
                model="gpt-4",
                messages=[
                    logger.info("[L6_AUDIT] Action at line 268")
                    {"role": "system",
                        "content": "You are a consensus judge. Respond with valid JSON only."},
                    logger.info("[L6_AUDIT] Action at line 271")
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            judge_result = json.loads(response.choices[0].message.content)

            # Extract dissenting opinions
            dissenting = []
            for o in opinions:
                if o.risk_assessment in ["HIGH", "CRITICAL"]:
                    dissenting.append(f"{o.model_name}: {o.reasoning}")

            return ConsensusVerdict(
                chosen_plan=judge_result.get("consensus_plan", opinions[0].plan),
                consensus_score=judge_result.get("similarity_score", 0.5),
                dissenting_opinions=dissenting[:3],  # Limit to top 3
                logger.info("[L6_AUDIT] Action at line 290")
                reasoning=judge_result.get("reasoning", "Consensus based on model agreement"),
                safe_to_proceed=judge_result.get("safe_to_proceed", True)
            logger.info("[L6_AUDIT] Action at line 293")
            )

        except Exception as e:
            LOGGER.error(f"Judge analysis failed: {e}")
            # Fallback to simple majority
            return self._simple_consensus(opinions)

    logger.info("[L6_AUDIT] Action at line 301")
    def _simple_consensus(self, opinions: List[ModelOpinion]) -> ConsensusVerdict:
        """Simple fallback consensus method."""
        logger.info("[L6_AUDIT] Action at line 304")
        # Count risk levels
        risk_counts = {}
        for o in opinions:
            risk_counts[o.risk_assessment] = risk_counts.get(o.risk_assessment, 0) + 1

        # If any critical risks, block
        if risk_counts.get("CRITICAL", 0) > 0:
            return ConsensusVerdict(
                chosen_plan="BLOCKED_CRITICAL_RISK",
                logger.info("[L6_AUDIT] Action at line 314")
                consensus_score=0.0,
                dissenting_opinions=["Critical risk detected"],
                reasoning="Critical risk assessment requires blocking",
                safe_to_proceed=False
            )

        # Use the highest confidence plan
        best_opinion = max(opinions, key=lambda o: o.confidence)

        return ConsensusVerdict(
            chosen_plan=best_opinion.plan,
            consensus_score=0.6,  # Moderate confidence in simple consensus
            dissenting_opinions=[],
            reasoning="Selected highest confidence plan",
            safe_to_proceed=True
        )

    def _extract_section(self, text: str, markers: List[str]) -> str:
        """Extract a section from model response."""
        for marker in markers:
            if marker in text:
                start = text.find(marker) + len(marker)
                # Find next marker or end
                next_markers = ["\n\n", "Plan:", "Action:", "Reasoning:", "Risk:", "Confidence:"]
                end_pos = len(text)
                for next_marker in next_markers:
                    pos = text.find(next_marker, start)
                    if pos != -1:
                        end_pos = min(end_pos, pos)
                return text[start:end_pos].strip()
        return ""

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from text."""
        # Look for patterns like "confidence: 0.8" or "80% confident"
        patterns = [
            r"confidence[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)%?\s*confident",
            r"(\d+\.?\d*)/10",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                if value > 1:  # If it's a percentage or /10
                    value = value / 10 if value <= 10 else value / 100
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