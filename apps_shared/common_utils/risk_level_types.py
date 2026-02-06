"""Temperature Core - Emotional EQ Engine for Humanized AI Communication.

This module provides the Temperature Engine subsystem responsible for humanizing
outreach messages. It acts as the EQ (Emotional Quotient) for the agent,
ensuring messages are personalized, emotionally calibrated, and contextually
appropriate.
"""

import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level for sentiment analysis."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SentimentMood(str, Enum):
    """Mood categories for sentiment analysis."""

    OPTIMISTIC = "OPTIMISTIC"
    NEUTRAL = "NEUTRAL"
    CAUTIOUS = "CAUTIOUS"
    HOSTILE = "HOSTILE"


class DepthScore(BaseModel):
    """Score indicating personalization depth."""

    level: int = Field(..., ge=0, le=3, description="0=Generic, 3=Deep")
    score: float = Field(..., ge=0.0, le=1.0, description="Depth score")
    rationale: list[str] = Field(default_factory=list, description="Reasoning for score")

    @property
    def is_deep(self) -> bool:
        """Check if this represents deep personalization."""
        return self.level >= 2


class MicroHook(BaseModel):
    """Micro-hook for unique message openers."""

    phrase: str = Field(..., description="Hook phrase template")
    trigger_type: str = Field(..., description="Type of trigger that generated this")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score")

    @property
    def is_highly_relevant(self) -> bool:
        """Check if hook is highly relevant."""
        return self.relevance >= 0.8


class SentimentProfile(BaseModel):
    """Profile of recipient's sentiment."""

    mood: SentimentMood = Field(..., description="Detected mood")
    risk_level: RiskLevel = Field(..., description="Associated risk level")
    keywords_detected: list[str] = Field(
        default_factory=list, description="Keywords that determined mood",
    )

    @property
    def is_safe_to_contact(self) -> bool:
        """Check if it's safe to contact based on sentiment."""
        return self.risk_level != RiskLevel.CRITICAL


class WarmthSetting(BaseModel):
    """Settings for message warmth and formality."""

    formality_level: float = Field(..., ge=0.0, le=1.0, description="0=Casual, 1=Formal")
    strategy_name: str = Field(..., description="Name of warmth strategy")
    max_emojis: int = Field(..., ge=0, le=5, description="Maximum emojis allowed")


class DepthScorer:
    """Calculates personalization depth based on profile information."""

    def __init__(self, target_keywords: list[str] | None = None):
        """Initialize the depth scorer.

        Args:
            target_keywords: Keywords to match against profile
        """
        self.target_keywords = target_keywords or [
            "python",
            "ai",
            "machine learning",
            "leadership",
            "strategy",
            "engineering",
            "product",
            "growth",
            "startup",
            "technology",
        ]
        logger.info(f"Initialized DepthScorer with {len(self.target_keywords)} keywords")

    def calculate_depth(self, profile: dict[str, Any]) -> DepthScore:
        """Calculate personalization depth from profile.

        Args:
            profile: Recipient profile dictionary

        Returns:
            DepthScore with level and rationale
        """
        try:
            # Initialize base score
            level = 0
            score = 0.1
            rationale = ["Basic contact info"]

            # Safe access to profile fields
            skills = profile.get("skills", [])
            about = profile.get("about", "")
            recent_posts = profile.get("recent_posts", [])
            mutual_connections = profile.get("mutual_connections", 0)
            pain_points = profile.get("pain_points", [])

            # Check 1: Keywords in skills/about
            skills_text = " ".join(skills) if isinstance(skills, list) else str(skills)
            combined_text = f"{skills_text} {about}".lower()

            keyword_matches = sum(
                1 for keyword in self.target_keywords if keyword.lower() in combined_text
            )

            if keyword_matches > 0:
                score += 0.2
                level = max(level, 1)
                rationale.append(f"Matched {keyword_matches} target keywords")

            # Check 2: Recent activity
            if recent_posts and isinstance(recent_posts, list):
                # Look for posts within last 90 days
                datetime.now() - timedelta(days=90)
                recent_count = 0

                for post in recent_posts:
                    if isinstance(post, dict):
                        post_date_str = post.get("date", "")
                        if post_date_str:
                            try:
                                # Simple date parsing
                                if "days ago" in post_date_str:
                                    days = int(re.search(r"(\d+)", post_date_str).group(1))
                                    if days <= 90:
                                        recent_count += 1
                            except (ValueError, AttributeError):
                                continue
                    elif (
                        isinstance(post, str) and len(post) > 20
                    ):  # Assume recent if non-empty string
                        recent_count += 1

                if recent_count > 0:
                    score += 0.3
                    level = max(level, 2)
                    rationale.append(f"Active within 90 days ({recent_count} posts)")

            # Check 3: Connections or pain points
            if mutual_connections and mutual_connections > 0:
                score += 0.4
                level = 3
                rationale.append(f"Has {mutual_connections} mutual connections")
            elif pain_points and isinstance(pain_points, list) and len(pain_points) > 0:
                score += 0.4
                level = 3
                rationale.append("Has identified pain points")

            # Clamp score to maximum
            score = min(1.0, score)

            depth_score = DepthScore(level=level, score=score, rationale=rationale)

            logger.debug(f"Calculated depth: level={level}, score={score:.2f}")

            return depth_score

        except Exception as e:
            logger.error(f"Error calculating depth: {str(e)}")
            return DepthScore(level=0, score=0.1, rationale=["Error in calculation"])


class MicroHookGenerator:
    """Generates unique bridge phrases to kill template fatigue."""

    def __init__(self, my_education: dict[str, str] | None = None):
        """Initialize the hook generator.

        Args:
            my_education: My education background for alumni matching
        """
        self.my_education = my_education or {}
        logger.info("Initialized MicroHookGenerator")

    def generate_hooks(self, profile: dict[str, Any]) -> list[MicroHook]:
        """Generate micro-hooks based on profile triggers.

        Args:
            profile: Recipient profile dictionary

        Returns:
            List of MicroHook objects sorted by relevance
        """
        try:
            hooks = []

            # Safe access to profile fields
            company_news = profile.get("company_news", "")
            recent_posts = profile.get("recent_posts", [])
            education = profile.get("education", [])
            company_name = profile.get("company_name", "Unknown Company")
            industry = profile.get("industry", "technology")

            # News trigger
            if company_news and isinstance(company_news, str) and len(company_news) > 10:
                # Extract topic (simple approach)
                topic = company_news[:50] + "..." if len(company_news) > 50 else company_news
                hook = MicroHook(
                    phrase=f"I saw the news about {topic}",
                    trigger_type="company_news",
                    relevance=0.9,
                )
                hooks.append(hook)

            # Recent posts trigger (highest priority)
            if recent_posts and isinstance(recent_posts, list) and len(recent_posts) > 0:
                latest_post = recent_posts[0]
                if isinstance(latest_post, dict):
                    post_topic = latest_post.get("topic", latest_post.get("content", ""))[:30]
                elif isinstance(latest_post, str):
                    post_topic = latest_post[:30]
                else:
                    post_topic = "your recent post"

                if post_topic:
                    hook = MicroHook(
                        phrase=f"I was just reading your thoughts on {post_topic}...",
                        trigger_type="recent_post",
                        relevance=1.0,
                    )
                    hooks.append(hook)

            # Education/alumni trigger
            if education and isinstance(education, list) and self.my_education:
                my_school = self.my_education.get("school", "").lower()
                for edu in education:
                    if isinstance(edu, dict):
                        their_school = edu.get("school", "").lower()
                    elif isinstance(edu, str):
                        their_school = edu.lower()
                    else:
                        continue

                    if my_school and their_school and my_school in their_school:
                        hook = MicroHook(
                            phrase=f"Always great to connect with a fellow {edu.get('school', 'alum')} alum...",
                            trigger_type="alumni",
                            relevance=0.8,
                        )
                        hooks.append(hook)
                        break

            # Generic fallback
            if not hooks:
                hook = MicroHook(
                    phrase=f"I've been following {company_name}'s work in {industry}...",
                    trigger_type="generic",
                    relevance=0.3,
                )
                hooks.append(hook)

            # Sort by relevance descending
            hooks.sort(key=lambda h: h.relevance, reverse=True)

            logger.debug(f"Generated {len(hooks)} hooks, top relevance: {hooks[0].relevance:.2f}")

            return hooks

        except Exception as e:
            logger.error(f"Error generating hooks: {str(e)}")
            # Return generic hook as fallback
            return [
                MicroHook(
                    phrase="I came across your profile and was impressed...",
                    trigger_type="fallback",
                    relevance=0.2,
                ),
            ]


class SentimentAnalyzer:
    """Analyzes recipient text to prevent tone-deafness."""

    def __init__(self):
        """Initialize the sentiment analyzer."""
        # Word dictionaries for sentiment analysis
        self.optimistic_words = {
            "hiring",
            "growth",
            "excited",
            "happy",
            "launch",
            "celebrate",
            "congrats",
            "opportunity",
            "success",
            "thriving",
            "expanding",
            "achievement",
            "milestone",
            "breakthrough",
            "innovation",
        }

        self.cautious_words = {
            "layoff",
            "reduction",
            "restructure",
            "downsize",
            "challenging",
            "tough",
            "sad",
            "difficult",
            "uncertain",
            "cautious",
            "concern",
            "struggle",
            "setback",
            "obstacle",
            "hurdle",
            "pressure",
        }

        self.hostile_words = {
            "spam",
            "stop",
            "unsubscribe",
            "annoying",
            "hate",
            "remove",
            "go away",
            "leave me alone",
            "bothering",
            "pestering",
        }

        logger.info("Initialized SentimentAnalyzer with word dictionaries")

    def assess_sentiment(self, text_samples: list[str]) -> SentimentProfile:
        """Assess sentiment from text samples.

        Args:
            text_samples: List of text samples to analyze

        Returns:
            SentimentProfile with mood and risk level
        """
        try:
            # Validate input
            if not text_samples or not isinstance(text_samples, list):
                return SentimentProfile(
                    mood=SentimentMood.NEUTRAL, risk_level=RiskLevel.LOW, keywords_detected=[],
                )

            # Combine and tokenize text
            combined_text = " ".join(str(s) for s in text_samples if s).lower()
            words = re.findall(r"\b\w+\b", combined_text)
            word_set = set(words)

            # Count matches for each category
            optimistic_count = len(word_set.intersection(self.optimistic_words))
            cautious_count = len(word_set.intersection(self.cautious_words))
            hostile_count = len(word_set.intersection(self.hostile_words))

            # Determine mood and risk
            keywords_detected = []

            if hostile_count > 0:
                mood = SentimentMood.HOSTILE
                risk = RiskLevel.CRITICAL
                keywords_detected = list(word_set.intersection(self.hostile_words))
            elif cautious_count > optimistic_count:
                mood = SentimentMood.CAUTIOUS
                risk = RiskLevel.HIGH
                keywords_detected = list(word_set.intersection(self.cautious_words))
            elif optimistic_count > 0:
                mood = SentimentMood.OPTIMISTIC
                risk = RiskLevel.LOW
                keywords_detected = list(word_set.intersection(self.optimistic_words))
            else:
                mood = SentimentMood.NEUTRAL
                risk = RiskLevel.LOW
                keywords_detected = []

            profile = SentimentProfile(
                mood=mood,
                risk_level=risk,
                keywords_detected=keywords_detected[:5],  # Limit to top 5
            )

            logger.info(f"Assessed sentiment: {mood.value} (risk: {risk.value})")

            return profile

        except Exception as e:
            logger.error(f"Error assessing sentiment: {str(e)}")
            return SentimentProfile(
                mood=SentimentMood.NEUTRAL, risk_level=RiskLevel.LOW, keywords_detected=["error"],
            )


class WarmthManager:
    """Manages contextual warmth and formality adjustments."""

    def __init__(self):
        """Initialize the warmth manager."""
        # Base formality levels by archetype
        self.base_formality = {
            "founder": 0.4,
            "ceo": 0.4,
            "cto": 0.6,
            "vp": 0.6,
            "vp engineering": 0.6,
            "recruiter": 0.5,
            "talent acquisition": 0.5,
            "hr manager": 0.5,
            "peer": 0.3,
            "manager": 0.5,
            "director": 0.6,
        }

        logger.info("Initialized WarmthManager with formality mappings")

    def determine_warmth(
        self, archetype: str, relationship_stage: str, sentiment: SentimentMood,
    ) -> WarmthSetting:
        """Determine warmth settings based on context.

        Args:
            archetype: Recipient's job archetype
            relationship_stage: Current relationship stage
            sentiment: Detected sentiment mood

        Returns:
            WarmthSetting with formality and strategy
        """
        try:
            # Get base formality
            archetype_key = archetype.lower().strip()
            base_formality = self.base_formality.get(archetype_key, 0.5)

            # Apply relationship modifier
            stage_upper = relationship_stage.upper().strip()
            if stage_upper == "COLD":
                base_formality += 0.2
            elif stage_upper == "WARM":
                base_formality -= 0.2

            # Apply sentiment modifier
            if sentiment == SentimentMood.OPTIMISTIC:
                base_formality -= 0.1  # Match their energy
            elif sentiment == SentimentMood.CAUTIOUS:
                base_formality += 0.2  # Show deference
            elif sentiment == SentimentMood.HOSTILE:
                base_formality += 0.3  # Be extra formal

            # Clamp to valid range
            base_formality = max(0.0, min(1.0, base_formality))

            # Determine strategy and emoji allowance
            if base_formality > 0.8:
                strategy = "Respectful Intrusion"
                max_emojis = 0
            elif base_formality < 0.4:
                strategy = "Peer Chat"
                max_emojis = 2
            else:
                strategy = "Professional Connect"
                max_emojis = 1

            warmth = WarmthSetting(
                formality_level=base_formality, strategy_name=strategy, max_emojis=max_emojis,
            )

            logger.debug(f"Determined warmth: {strategy} (formality: {base_formality:.2f})")

            return warmth

        except Exception as e:
            logger.error(f"Error determining warmth: {str(e)}")
            return WarmthSetting(
                formality_level=0.6, strategy_name="Professional Default", max_emojis=1,
            )


class TemperatureEngine:
    """Facade class that orchestrates all temperature components."""

    def __init__(
        self, target_keywords: list[str] | None = None, my_education: dict[str, str] | None = None,
    ):
        """Initialize the temperature engine.

        Args:
            target_keywords: Keywords for depth scoring
            my_education: Education background for alumni matching
        """
        self.depth_scorer = DepthScorer(target_keywords)
        self.hook_generator = MicroHookGenerator(my_education)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.warmth_manager = WarmthManager()

        logger.info("Initialized TemperatureEngine with all components")

    def analyze_temperature(
        self, profile: dict[str, Any], context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze all temperature aspects for a recipient.

        Args:
            profile: Recipient profile dictionary
            context: Additional context (archetype, relationship_stage, text_samples)

        Returns:
            Dictionary with all temperature analysis results
        """
        try:
            # Extract context with safe defaults
            archetype = context.get("archetype", "peer")
            relationship_stage = context.get("relationship_stage", "COLD")
            text_samples = context.get("text_samples", [])

            # Early sentiment check - exit if hostile
            sentiment_profile = self.sentiment_analyzer.assess_sentiment(text_samples)
            if sentiment_profile.risk_level == RiskLevel.CRITICAL:
                logger.warning(
                    f"Hostile sentiment detected for {profile.get('name', 'Unknown')}, aborting further analysis",
                )
                return {
                    "depth_score": {
                        "level": 0,
                        "score": 0.0,
                        "rationale": ["Analysis aborted due to hostile sentiment"],
                    },
                    "top_hooks": [],
                    "sentiment": sentiment_profile.dict(),
                    "warmth": {
                        "formality_level": 1.0,
                        "strategy_name": "DO NOT CONTACT",
                        "max_emojis": 0,
                    },
                    "recommendations": ["DO NOT CONTACT - recipient appears hostile"],
                    "abort": True,
                }

            # Run remaining analyses
            depth_score = self.depth_scorer.calculate_depth(profile)
            hooks = self.hook_generator.generate_hooks(profile)
            warmth_setting = self.warmth_manager.determine_warmth(
                archetype, relationship_stage, sentiment_profile.mood,
            )

            # Aggregate results
            results = {
                "depth_score": depth_score.dict(),
                "top_hooks": [h.dict() for h in hooks[:3]],  # Top 3 hooks
                "sentiment": sentiment_profile.dict(),
                "warmth": warmth_setting.dict(),
                "recommendations": self._generate_recommendations(
                    depth_score, sentiment_profile, warmth_setting,
                ),
                "abort": False,
            }

            logger.info(f"Temperature analysis complete for {profile.get('name', 'Unknown')}")

            return results

        except Exception as e:
            logger.error(f"Error in temperature analysis: {str(e)}")
            return {
                "error": str(e),
                "depth_score": {"level": 0, "score": 0.1, "rationale": ["Error"]},
                "top_hooks": [],
                "sentiment": {"mood": "NEUTRAL", "risk_level": "LOW", "keywords_detected": []},
                "warmth": {
                    "formality_level": 0.6,
                    "strategy_name": "Error Default",
                    "max_emojis": 1,
                },
                "recommendations": ["Proceed with caution due to analysis error"],
                "abort": False,
            }

    def _generate_recommendations(
        self, depth: DepthScore, sentiment: SentimentProfile, warmth: WarmthSetting,
    ) -> list[str]:
        """Generate recommendations based on analysis.

        Args:
            depth: Depth score result
            sentiment: Sentiment profile
            warmth: Warmth settings

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Depth-based recommendations
        if depth.level == 0:
            recommendations.append("Use generic opener - limited personalization available")
        elif depth.level >= 2:
            recommendations.append("High personalization possible - reference specific details")

        # Sentiment-based recommendations
        if sentiment.risk_level == RiskLevel.CRITICAL:
            recommendations.append("DO NOT CONTACT - recipient appears hostile")
        elif sentiment.mood == SentimentMood.CAUTIOUS:
            recommendations.append("Use deferential tone, acknowledge current challenges")
        elif sentiment.mood == SentimentMood.OPTIMISTIC:
            recommendations.append("Match their positive energy, focus on opportunities")

        # Warmth-based recommendations
        if warmth.max_emojis == 0:
            recommendations.append("Maintain professional tone, no emojis")
        elif warmth.max_emojis >= 2:
            recommendations.append("Casual tone acceptable, 1-2 emojis may be used")

        return recommendations


# Factory functions for easy instantiation
def create_temperature_engine(
    target_keywords: list[str] | None = None, my_education: dict[str, str] | None = None,
) -> TemperatureEngine:
    """Create a TemperatureEngine instance."""
    return TemperatureEngine(target_keywords, my_education)


def analyze_temperature(profile: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Quickly analyze temperature for a profile."""
    engine = create_temperature_engine()
    return engine.analyze_temperature(profile, context)
