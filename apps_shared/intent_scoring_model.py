"""
Intent Scoring Model for L4 Cost Governance
Analyzes lead intent and likelihood of reply using historical data and real-time context
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("IntentScoring")  # GLOBAL: Review if this should be constant


@dataclass
class IntentFeatures:
    """Features used for intent scoring"""
    # Lead profile features
    industry: str
    role: str
    company_size: str  # small, medium, large, enterprise

    # Engagement features
    previous_interactions: int
    email_open_rate: float
    response_rate: float

    # Context features from News RAG
    has_recent_news: bool
    news_sentiment: float  # -1 to 1
    company_growth_stage: str  # seed, growth, mature

    # Temporal features
    days_since_last_contact: int
    contact_frequency: str  # low, medium, high

    # Content features
    personalization_score: float  # 0 to 1
    template_relevance: float  # 0 to 1


@dataclass
class IntentScore:
    """Intent scoring result"""
    lead_id: str
    overall_score: float  # 0 to 100
    reply_probability: float  # 0 to 1
    priority: str  # low, medium, high, critical

    # Component scores
    engagement_score: float
    context_score: float
    timing_score: float
    content_score: float

    # Recommendations
    recommended_action: str
    optimal_send_time: str
    personalization_notes: List[str]

    # Metadata
    scored_at: str
    model_version: str


class IntentScoringModel:
    """
    Intent Scoring Model for predicting lead reply likelihood
    """

    def __init__(self):
        self.model_version = "1.0.0"
        self.feature_weights = {
            "engagement": 0.35,
            "context": 0.25,
            "timing": 0.20,
            "content": 0.20
        }

        # Industry engagement benchmarks (mock data for demo)
        self.industry_benchmarks = {
            "technology": {"avg_response": 0.25, "avg_open": 0.45},
            "healthcare": {"avg_response": 0.20, "avg_open": 0.40},
            "finance": {"avg_response": 0.18, "avg_open": 0.35},
            "education": {"avg_response": 0.22, "avg_open": 0.42},
            "energy": {"avg_response": 0.15, "avg_open": 0.30},
            "retail": {"avg_response": 0.12, "avg_open": 0.28}
        }

        # Role-based priorities
        self.role_priorities = {
            "CEO": 1.5,
            "CTO": 1.4,
            "CFO": 1.3,
            "VP": 1.2,
            "Director": 1.1,
            "Manager": 1.0,
            "Senior": 0.9,
            "Lead": 0.8,
            "Specialist": 0.7,
            "Analyst": 0.6,
            "Associate": 0.5
        }

    def _extract_features(
        self,
        lead_profile: Dict[str, Any],
        engagement_data: Dict[str, Any],
        news_context: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> IntentFeatures:
        """Extract features from lead data"""

        # Basic profile features
        industry = lead_profile.get("industry", "unknown").lower()
        role = lead_profile.get("role", "unknown").upper()
        company_size = lead_profile.get("company_size", "medium").lower()

        # Engagement features
        previous_interactions = engagement_data.get("previous_interactions", 0)
        email_open_rate = engagement_data.get("email_open_rate", 0.0)
        response_rate = engagement_data.get("response_rate", 0.0)

        # News context features
        has_recent_news = news_context.get("news_available", False)
        news_sentiment = news_context.get("sentiment_score", 0.0)
        company_growth_stage = news_context.get(
            "growth_stage", "mature").lower()

        # Temporal features
        days_since_last_contact = engagement_data.get(
            "days_since_last_contact", 30)
        contact_frequency = engagement_data.get(
            "contact_frequency", "low").lower()

        # Content features
        personalization_score = personalization_data.get(
            "personalization_score", 0.5)
        template_relevance = personalization_data.get(
            "template_relevance", 0.5)

        return IntentFeatures(
            industry=industry,
            role=role,
            company_size=company_size,
            previous_interactions=previous_interactions,
            email_open_rate=email_open_rate,
            response_rate=response_rate,
            has_recent_news=has_recent_news,
            news_sentiment=news_sentiment,
            company_growth_stage=company_growth_stage,
            days_since_last_contact=days_since_last_contact,
            contact_frequency=contact_frequency,
            personalization_score=personalization_score,
            template_relevance=template_relevance
        )

    def _score_engagement(self, features: IntentFeatures) -> float:
        """Score based on historical engagement"""
        score = 0.0

        # Response rate (40% weight)
        score += features.response_rate * 40

        # Open rate (30% weight)
        score += features.email_open_rate * 30

        # Previous interactions (20% weight)
        if features.previous_interactions > 0:
            interaction_score = min(
                features.previous_interactions / 10, 1.0) * 20
            score += interaction_score

        # Days since last contact (10% weight)
        if features.days_since_last_contact < 7:
            score += 10
        elif features.days_since_last_contact < 30:
            score += 5
        else:
            score += 0

        return min(score, 100)

    def _score_context(self, features: IntentFeatures) -> float:
        """Score based on current context and news"""
        score = 50.0  # Base score

        # News availability (30 points)
        if features.has_recent_news:
            score += 30

            # News sentiment (20 points)
            score += features.news_sentiment * 20

        # Industry benchmarks (20 points)
        industry = features.industry
        if industry in self.industry_benchmarks:
            benchmark = self.industry_benchmarks[industry]
            score += benchmark["avg_response"] * 100

        # Company growth stage (15 points)
        if features.company_growth_stage == "growth":
            score += 15
        elif features.company_growth_stage == "seed":
            score += 10

        # Company size (15 points)
        if features.company_size in ["medium", "large"]:
            score += 15
        elif features.company_size == "enterprise":
            score += 10

        return min(score, 100)

    def _score_timing(self, features: IntentFeatures) -> float:
        """Score based on optimal timing"""
        score = 50.0  # Base score

        # Contact frequency (30 points)
        if features.contact_frequency == "low":
            score += 30
        elif features.contact_frequency == "medium":
            score += 20
        else:
            score += 10

        # Days since last contact (40 points)
        if 7 <= features.days_since_last_contact <= 21:
            score += 40  # Sweet spot
        elif features.days_since_last_contact < 7:
            score += 20  # Too recent
        elif features.days_since_last_contact <= 60:
            score += 30  # Acceptable
        else:
            score += 10  # Too long

        # Role priority (30 points)
        role = features.role
        if role in self.role_priorities:
            score += self.role_priorities[role] * 20

        return min(score, 100)

    def _score_content(self, features: IntentFeatures) -> float:
        """Score based on content quality and relevance"""
        score = 0.0

        # Personalization score (50% weight)
        score += features.personalization_score * 50

        # Template relevance (40% weight)
        score += features.template_relevance * 40

        # Industry-role match (10% weight)
        # Check if template is well-matched to industry and role
        if features.industry != "unknown" and features.role != "UNKNOWN":
            score += 10

        return min(score, 100)

    def _calculate_priority(self, overall_score: float) -> str:
        """Determine priority based on overall score"""
        if overall_score >= 80:
            return "critical"
        elif overall_score >= 65:
            return "high"
        elif overall_score >= 45:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        features: IntentFeatures,
        scores: Dict[str, float]
    ) -> Tuple[str, str, List[str]]:
        """Generate recommendations based on scores"""

        # Recommended action
        if scores["overall"] >= 70:
            action = "Send immediately with high personalization"
        elif scores["overall"] >= 50:
            action = "Send within 24 hours with standard personalization"
        else:
            action = "Delay outreach or use low-effort template"

        # Optimal send time
        if features.contact_frequency == "low":
            optimal_time = "Tuesday-Thursday, 10:00-11:00 AM"
        elif features.contact_frequency == "medium":
            optimal_time = "Monday or Wednesday, 2:00-3:00 PM"
        else:
            optimal_time = "Friday, 9:00-10:00 AM"

        # Personalization notes
        notes = []

        if scores["context"] > 70:
            notes.append("Leverage recent news in opening")

        if scores["engagement"] < 40:
            notes.append("Use compelling subject line to improve open rate")

        if features.has_recent_news:
            notes.append("Reference company's latest developments")

        if features.company_growth_stage == "growth":
            notes.append("Focus on scaling and efficiency benefits")

        if scores["timing"] < 50:
            notes.append("Consider waiting for better timing")

        return action, optimal_time, notes

    def score_lead_intent(
        self,
        lead_id: str,
        lead_profile: Dict[str, Any],
        engagement_data: Optional[Dict[str, Any]] = None,
        news_context: Optional[Dict[str, Any]] = None,
        personalization_data: Optional[Dict[str, Any]] = None,
        logger: Optional[Any] = None
    ) -> IntentScore:
        """
        Score lead intent and reply likelihood

        Args:
            lead_id: Unique identifier for the lead
            lead_profile: Lead profile information
            engagement_data: Historical engagement data
            news_context: News RAG context data
            personalization_data: Content personalization metrics
            logger: Logger instance

        Returns:
            IntentScore with detailed scoring and recommendations
        """

        if logger:
            logger.info(f"🎯 Scoring intent for lead {lead_id}")

        # Default values if not provided
        if engagement_data is None:
            engagement_data = {}
        if news_context is None:
            news_context = {}
        if personalization_data is None:
            personalization_data = {}

        # Extract features
        features = self._extract_features(
            lead_profile,
            engagement_data,
            news_context,
            personalization_data
        )

        # Calculate component scores
        engagement_score = self._score_engagement(features)
        context_score = self._score_context(features)
        timing_score = self._score_timing(features)
        content_score = self._score_content(features)

        # Calculate weighted overall score
        overall_score = (
            engagement_score * self.feature_weights["engagement"] +
            context_score * self.feature_weights["context"] +
            timing_score * self.feature_weights["timing"] +
            content_score * self.feature_weights["content"]
        )

        # Convert to reply probability (0-1)
        reply_probability = overall_score / 100

        # Determine priority
        priority = self._calculate_priority(overall_score)

        # Generate recommendations
        action, optimal_time, notes = self._generate_recommendations(
            features,
            {
                "overall": overall_score,
                "engagement": engagement_score,
                "context": context_score,
                "timing": timing_score,
                "content": content_score
            }
        )

        # Create result
        result = IntentScore(
            lead_id=lead_id,
            overall_score=round(overall_score, 1),
            reply_probability=round(reply_probability, 2),
            priority=priority,
            engagement_score=round(engagement_score, 1),
            context_score=round(context_score, 1),
            timing_score=round(timing_score, 1),
            content_score=round(content_score, 1),
            recommended_action=action,
            optimal_send_time=optimal_time,
            personalization_notes=notes,
            scored_at=datetime.now().isoformat(),
            model_version=self.model_version
        )

        if logger:
            logger.info(
                f"✅ Intent scored: {overall_score:.1f}/100 ({priority} priority)")
            logger.info(f"   Reply probability: {reply_probability:.0%}")
            logger.info(f"   Recommended: {action}")

        return result


class IntentScoringModelManager:
    """Manager for Intent Scoring Model without global state"""
    
    def __init__(self):
        self._instance = None
    
    def get_model(self) -> IntentScoringModel:
        """Get or create the Intent Scoring Model instance"""
        if self._instance is None:
            self._instance = IntentScoringModel()
        return self._instance


# Global manager instance (acceptable as it's a dependency injection container)
_model_manager = IntentScoringModelManager()


def get_intent_scoring_model() -> IntentScoringModel:
    """Get or create the global Intent Scoring Model instance"""
    return _model_manager.get_model()


def score_lead_intent(
    lead_id: str,
    lead_profile: Dict[str, Any],
    engagement_data: Optional[Dict[str, Any]] = None,
    news_context: Optional[Dict[str, Any]] = None,
    personalization_data: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None
) -> IntentScore:
    """
    Convenience function to score lead intent

    Args:
        lead_id: Unique identifier for the lead
        lead_profile: Lead profile information
        engagement_data: Historical engagement data
        news_context: News RAG context data
        personalization_data: Content personalization metrics
        logger: Logger instance

    Returns:
        IntentScore with detailed scoring and recommendations
    """
    model = get_intent_scoring_model()
    return model.score_lead_intent(
        lead_id,
        lead_profile,
        engagement_data,
        news_context,
        personalization_data,
        logger
    )

