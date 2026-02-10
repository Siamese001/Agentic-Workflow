"""Competitor Recon Agent - Strategic Competitive Intelligence.

This agent analyzes target company's competitors to identify strategic gaps
and generates outreach hooks that position the candidate as a solution
to competitive threats.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CompetitorMove:
    """Represents a recent competitive move or feature launch."""

    competitor_name: str
    recent_launch: str
    source_url: str | None = None
    date: str = ""

    def __post_init__(self):
        """Ensure date is in reasonable format."""
        try:
            # Accept various date formats
            if "ago" in self.date.lower():
                pass
            elif "month" in self.date.lower() or "week" in self.date.lower():
                pass
            else:
                # Try to parse as date
                datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            object.__setattr__(self, "date", "Recent")


@dataclass
class StrategicHook:
    """Strategic outreach hook based on competitive intelligence."""

    hook_text: str
    relevance_score: float
    competitive_gap: str

    @property
    def is_highly_relevant(self) -> bool:
        """Check if hook is highly relevant."""
        return self.relevance_score >= 0.8


class IntelProvider(ABC):
    """Abstract base class for competitive intelligence providers."""

    @abstractmethod
    def get_competitors(self, target_company: str, industry: str) -> list[str]:
        """Get list of competitors for target company.

        Args:
            target_company: Company to analyze
            industry: Industry sector

        Returns:
            List of competitor names
        """
        pass

    @abstractmethod
    def get_recent_moves(self, competitor: str, months: int = 6) -> list[CompetitorMove]:
        """Get recent AI/ML moves by competitor.

        Args:
            competitor: Competitor name
            months: Number of months to look back

        Returns:
            List of recent competitive moves
        """
        pass


class MockIntelProvider(IntelProvider):
    """Mock intelligence provider for testing and development."""

    def __init__(self):
        """Initialize mock provider with sample data."""
        self.mock_competitors = {
            "technology": ["OpenAI", "Anthropic", "Google", "Microsoft", "Meta"],
            "finance": ["Stripe", "Square", "PayPal", "Adyen", "Braintree"],
            "healthcare": ["Tempus", "Flatiron", "Verily", "IBM Watson", "Philips"],
            "retail": ["Amazon", "Shopify", "BigCommerce", "Magento", "WooCommerce"],
            # Gravity Merge: Extracted from legacy_market_intel.py
            "biotech": ["Ginkgo Bioworks", "Recursion", "Twist Bioscience", "Benchling"],
            "agritech": [
                "Indigo Ag",
                "Farmers Business Network",
                "John Deere AI",
                "Blue River",
            ],
        }

        self.mock_moves = {
            "OpenAI": [
                CompetitorMove(
                    competitor_name="OpenAI",
                    recent_launch="GPT-4 Turbo with 128K context",
                    source_url="https://openai.com/blog",
                    date="2 months ago",
                ),
                CompetitorMove(
                    competitor_name="OpenAI",
                    recent_launch="Assistants API for agent building",
                    source_url="https://openai.com/blog",
                    date="1 month ago",
                ),
            ],
            "Anthropic": [
                CompetitorMove(
                    competitor_name="Anthropic",
                    recent_launch="Claude 3 with improved reasoning",
                    source_url="https://anthropic.com",
                    date="3 months ago",
                ),
            ],
            "Google": [
                CompetitorMove(
                    competitor_name="Google",
                    recent_launch="Gemini Pro with multimodal capabilities",
                    source_url="https://deepmind.google",
                    date="2 months ago",
                ),
            ],
            "Meta": [
                CompetitorMove(
                    competitor_name="Meta",
                    recent_launch="Llama 3 open source model",
                    source_url="https://ai.meta.com",
                    date="1 month ago",
                ),
            ],
            "Microsoft": [
                CompetitorMove(
                    competitor_name="Microsoft",
                    recent_launch="Copilot Studio for custom AI agents",
                    source_url="https://microsoft.com/ai",
                    date="3 months ago",
                ),
            ],
        }

    def get_competitors(self, target_company: str, industry: str) -> list[str]:
        """Get mock competitors for target company."""
        industry_lower = industry.lower()
        return self.mock_competitors.get(
            industry_lower,
            ["Market Leader A", "Market Leader B", "Market Leader C"],
        )[:3]

    def get_recent_moves(self, competitor: str, months: int = 6) -> list[CompetitorMove]:
        """Get mock recent moves for competitor."""
        return self.mock_moves.get(competitor, [])


@dataclass
class CompetitorReconAgent:
    """Analyzes competitors and generates strategic hooks."""

    intel_provider: Any = None

    def __post_init__(self):
        """Initialize the competitor recon agent."""
        if self.intel_provider is None:
            self.intel_provider = MockIntelProvider()

        # Skill to feature mapping for matching
        self.skill_feature_map = {
            "llm": ["GPT", "LLM", "language model", "chatbot", "assistant"],
            "vector search": ["vector search", "embedding", "retrieval", "RAG"],
            "computer vision": ["vision", "image", "video", "computer vision"],
            "recommendation": ["recommendation", "personalization", "ranking"],
            "nlp": ["NLP", "text processing", "sentiment", "classification"],
            "mlops": ["MLOps", "deployment", "monitoring", "pipeline"],
            "agents": ["agent", "autonomous", "workflow", "automation"],
            "multimodal": ["multimodal", "vision-language", "cross-modal"],
        }

        logger.info("Initialized CompetitorReconAgent")

    def generate_fomo_hook(
        self,
        target_company: str,
        industry: str,
        candidate_skills: list[str],
    ) -> StrategicHook | None:
        """Generate FOMO hook based on competitive intelligence.

        Args:
            target_company: Target company name
            industry: Industry sector
            candidate_skills: List of candidate's skills

        Returns:
            Strategic hook or None if no competitive advantage found
        """
        try:
            # Identify competitors
            competitors = self._identify_competitors(target_company, industry)

            if not competitors:
                logger.warning("No competitors identified")
                return None

            # Gather intelligence
            all_moves = []
            for competitor in competitors:
                moves = self._gather_intel(competitor)
                all_moves.extend(moves)

            if not all_moves:
                logger.warning("No competitive moves found")
                return None

            # Find skill-feature matches
            matches = self._find_skill_matches(all_moves, candidate_skills)

            if matches:
                # Generate targeted hook based on match
                best_match = max(matches, key=lambda m: m["relevance"])
                return self._create_targeted_hook(best_match, target_company)
            else:
                # Generate speed hook as fallback
                return self._create_speed_hook(all_moves[0], target_company, candidate_skills)

        except Exception as e:
            logger.error(f"Error generating FOMO hook: {str(e)}")
            return None

    def get_strategic_ps(self, target_company: str, industry: str, candidate_skills: list[str]) -> str | None:
        """Get strategic P.S. line for emails.

        Args:
            target_company: Target company name
            industry: Industry sector
            candidate_skills: List of candidate's skills

        Returns:
            P.S. line or None
        """
        try:
            hook = self.generate_fomo_hook(target_company, industry, candidate_skills)

            if hook and hook.is_highly_relevant:
                return f"P.S. {hook.hook_text}"

            return None

        except Exception as e:
            logger.error(f"Error getting strategic P.S.: {str(e)}")
            return None

    def _identify_competitors(self, target_company: str, industry: str) -> list[str]:
        """Identify competitors for target company.

        Args:
            target_company: Company to analyze
            industry: Industry sector

        Returns:
            List of competitor names
        """
        try:
            competitors = self.intel_provider.get_competitors(target_company, industry)

            # Filter out the target company itself
            filtered = [c for c in competitors if c.lower() != target_company.lower()]

            logger.debug(f"Identified competitors for {target_company}: {filtered}")

            return filtered

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error identifying competitors: {str(e)}")
            return []

    def _gather_intel(self, competitor: str) -> list[CompetitorMove]:
        """Gather intelligence on competitor's recent moves.

        Args:
            competitor: Competitor name

        Returns:
            List of recent competitive moves
        """
        try:
            moves = self.intel_provider.get_recent_moves(competitor)

            # Anti-hallucination check
            if not moves:
                logger.debug(f"No verified moves found for {competitor}")
                return []

            logger.debug(f"Found {len(moves)} moves for {competitor}")

            return moves

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error gathering intel on {competitor}: {str(e)}")
            return []

    def _find_skill_matches(self, moves: list[CompetitorMove], skills: list[str]) -> list[dict[str, Any]]:
        """Find matches between candidate skills and competitor moves.

        Args:
            moves: List of competitive moves
            skills: List of candidate skills

        Returns:
            List of matches with relevance scores
        """
        try:
            matches = []

            for move in moves:
                move_text = move.recent_launch.lower()

                for skill in skills:
                    skill_lower = skill.lower()

                    # Check direct skill match
                    if skill_lower in move_text:
                        matches.append(
                            {"move": move, "skill": skill, "relevance": 0.9, "match_type": "direct"},
                        )
                        continue

                    # Check feature mapping
                    if skill_lower in self.skill_feature_map:
                        features = self.skill_feature_map[skill_lower]
                        for feature in features:
                            if feature in move_text:
                                matches.append(
                                    {
                                        "move": move,
                                        "skill": skill,
                                        "relevance": 0.7,
                                        "match_type": "feature",
                                    },
                                )
                                break

            logger.debug(f"Found {len(matches)} skill-feature matches")

            return matches

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error finding skill matches: {str(e)}")
            return []

    def _create_targeted_hook(self, match: dict[str, Any], target_company: str) -> StrategicHook:
        """Create targeted hook based on skill-feature match.

        Args:
            match: Skill-feature match data
            target_company: Target company name

        Returns:
            Strategic hook
        """
        try:
            move = match["move"]
            skill = match["skill"]

            # Create analytical, helpful hook
            hook_text = (
                f"I noticed {move.competitor_name} recently launched {move.recent_launch}. "
                f"Having led similar {skill} initiatives to achieve competitive parity, "
                f"I have a playbook to help {target_company} close this gap."
            )

            gap = f"{target_company} lacks {move.recent_launch} that {move.competitor_name} has"

            return StrategicHook(hook_text=hook_text, relevance_score=match["relevance"], competitive_gap=gap)

        except Exception as e:
            logger.error(f"Error creating targeted hook: {str(e)}")
            raise

    def _create_speed_hook(
        self,
        move: CompetitorMove,
        target_company: str,
        skills: list[str],
    ) -> StrategicHook:
        """Create speed-focused hook when no direct feature match.

        Args:
            move: Competitive move
            target_company: Target company name
            skills: Candidate skills

        Returns:
            Strategic hook focused on speed
        """
        try:
            # Create speed/velocity hook
            hook_text = (
                f"The pace of AI shipping at {move.competitor_name} is accelerating. "
                f"My specialty is establishing high-velocity AI development cycles "
                f"to maintain competitive positioning."
            )

            gap = f"Development velocity gap with {move.competitor_name}"

            return StrategicHook(hook_text=hook_text, relevance_score=0.6, competitive_gap=gap)

        except Exception as e:
            logger.error(f"Error creating speed hook: {str(e)}")
            raise


# Factory function for easy instantiation
def create_competitor_recon_agent(
    intel_provider: IntelProvider | None = None,
) -> CompetitorReconAgent:
    """Create a CompetitorReconAgent instance.

    Args:
        intel_provider: Optional custom intelligence provider

    Returns:
        Configured CompetitorReconAgent
    """
    return CompetitorReconAgent(intel_provider)


# Convenience function for quick hook generation
def generate_competitive_hook(target_company: str, industry: str, candidate_skills: list[str]) -> str | None:
    """Quickly generate a competitive hook.

    Args:
        target_company: Target company name
        industry: Industry sector
        candidate_skills: List of candidate skills

    Returns:
        Hook text or None
    """
    agent = create_competitor_recon_agent()
    hook = agent.generate_fomo_hook(target_company, industry, candidate_skills)
    return hook.hook_text if hook else None
