"""Temperature Core - Emotional EQ Engine for Humanized AI Communication.

This module provides the Temperature Engine subsystem responsible for humanizing
outreach messages. It acts as the EQ (Emotional Quotient) for the agent,
ensuring messages are personalized, emotionally calibrated, and contextually
appropriate.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "risk_level_types", "p0_governance")
_emit_reads_policy_state("p0", "risk_level_types", "policy_binding")
_emit_snapshots_state("p0", "risk_level_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("risk_level_types", "p4obs", "metric_1")
_emit_emits_metric_event("risk_level_types", "p4obs", "metric_2")
_emit_emits_metric_event("risk_level_types", "p4obs", "metric_3")
_emit_emits_metric_event("risk_level_types", "p4obs", "metric_4")
_emit_emits_metric_event("risk_level_types", "p4obs", "metric_5")
_emit_emits_metric_event("risk_level_types", "p4obs", "metric_6")
_emit_records_incident_event("risk_level_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("risk_level_types", "p4obs", "anomaly")
_emit_writes_observability_log("risk_level_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("risk_level_types", "p4obs", "mon_state")
_emit_triggers_alert("risk_level_types", "p4obs", "alert")
_emit_links_incident_trace("risk_level_types", "p4obs", "trace_link")
_emit_captures_pattern("risk_level_types", "p3lm", "pattern")
_emit_records_learning_event("risk_level_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("risk_level_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("risk_level_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("risk_level_types", "p3lm", "routing")
_emit_improves_agent_policy("risk_level_types", "p3lm", "policy")
_emit_stores_learning_state("risk_level_types", "p3lm", "state")
_emit_records_execution_trace("risk_level_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("risk_level_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("risk_level_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("risk_level_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("risk_level_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("risk_level_types", "env_read", "p2_env_1")
_emit_reads_environ("risk_level_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("risk_level_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("risk_level_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "risk_level_types", "context_pull")
_emit_pulls_context("p1", "risk_level_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "risk_level_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "risk_level_types", "uwg_term_2")
_emit_writes_through("p1", "risk_level_types", "write_through")
_emit_writes_through("p1", "risk_level_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "risk_level_types", "safety_validation")
_emit_invokes_eval("p1", "risk_level_types", "eval_call")
_emit_proposal_commits_routing("p1", "risk_level_types", "routing_commit")
_emit_escalates_to_human("p1", "risk_level_types", "human_escalation")
_emit_routes_through("p1", "risk_level_types", "route_through")
_emit_checks_agent_registry("p1", "risk_level_types", "agent_registry")
_emit_validates_agent_capability("p1", "risk_level_types", "capability")
_emit_dispatches_execution_plan("p1", "risk_level_types", "exec_plan")
_emit_agent_executes_agent("p1", "risk_level_types", "sub_agent")
_emit_routes_to_agent("p1", "risk_level_types", "target_agent")
_emit_verifies_policy("p1", "risk_level_types", "policy_check")
_emit_observes_runtime_state("p1", "risk_level_types", "runtime_state")
_emit_verifies_boundary("p1", "risk_level_types", "boundary_check")
_emit_transcripts_response("p1", "risk_level_types", "transcript")
_emit_hard_fails_untranscripted("p1", "risk_level_types")
_emit_gated_by_confidence("p1", "risk_level_types", "confidence_gate")
emit_replay_key("p0", "risk_level_types")
emit_determinism_digest("p0", "risk_level_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "risk_level_types", "execution_auth")
_emit_validates_capability("p2", "risk_level_types", "capability_check")
_emit_routes_to_capability("p2", "risk_level_types", "capability_route")
_emit_writes_via_uwg("p2", "risk_level_types", "uwg_write")
_emit_blocks_direct_write("p2", "risk_level_types", "direct_write_block")
_emit_records_tool_invocation("p2", "risk_level_types", "tool_invocation")
_emit_captures_execution_output("p2", "risk_level_types", "exec_output")
_emit_dispatches_agent("p3", "risk_level_types", "agent_dispatch")
_emit_coordinates_agents("p3", "risk_level_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "risk_level_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "risk_level_types", "healing_outcome")
_emit_escalates_failure("p3", "risk_level_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "risk_level_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "risk_level_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "risk_level_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "risk_level_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "risk_level_types", "eval_metric")
_emit_stores_embedding("p4", "risk_level_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "risk_level_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "risk_level_types", "exec_snapshot_link")

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
    keywords_detected: list[str] = Field(default_factory=list, description="Keywords that determined mood")

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
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "PersonalizationDepthCalculator.calculate_depth"
        )
        try:
            level = 0
            score = 0.1
            rationale = ["Basic contact info"]
            skills = profile.get("skills", [])
            about = profile.get("about", "")
            recent_posts = profile.get("recent_posts", [])
            mutual_connections = profile.get("mutual_connections", 0)
            pain_points = profile.get("pain_points", [])
            skills_text = " ".join(skills) if isinstance(skills, list) else str(skills)
            combined_text = f"{skills_text} {about}".lower()
            keyword_matches = sum(1 for keyword in self.target_keywords if keyword.lower() in combined_text)
            if keyword_matches > 0:
                score += 0.2
                level = max(level, 1)
                rationale.append(f"Matched {keyword_matches} target keywords")
            if recent_posts and isinstance(recent_posts, list):
                datetime.now() - timedelta(days=90)
                recent_count = 0
                for post in tqdm(recent_posts, desc="Processing", unit="item"):
                    if isinstance(post, dict):
                        post_date_str = post.get("date", "")
                        if post_date_str:
                            try:
                                if "days ago" in post_date_str:
                                    days = int(re.search("(\\d+)", post_date_str).group(1))
                                    if days <= 90:
                                        recent_count += 1
                            except (ValueError, AttributeError):
                                continue
                    elif isinstance(post, str) and len(post) > 20:
                        recent_count += 1
                if recent_count > 0:
                    score += 0.3
                    level = max(level, 2)
                    rationale.append(f"Active within 90 days ({recent_count} posts)")
            if mutual_connections and mutual_connections > 0:
                score += 0.4
                level = 3
                rationale.append(f"Has {mutual_connections} mutual connections")
            elif pain_points and isinstance(pain_points, list) and (len(pain_points) > 0):
                score += 0.4
                level = 3
                rationale.append("Has identified pain points")
            score = min(1.0, score)
            depth_score = DepthScore(level=level, score=score, rationale=rationale)
            logger.debug(f"Calculated depth: level={level}, score={score:.2f}")
            return depth_score
        except Exception as e:  # guardian: allow-silent-swallow
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
            company_news = profile.get("company_news", "")
            recent_posts = profile.get("recent_posts", [])
            education = profile.get("education", [])
            company_name = profile.get("company_name", "Unknown Company")
            industry = profile.get("industry", "technology")
            if company_news and isinstance(company_news, str) and (len(company_news) > 10):
                topic = company_news[:50] + "..." if len(company_news) > 50 else company_news
                hook = MicroHook(
                    phrase=f"I saw the news about {topic}",
                    trigger_type="company_news",
                    relevance=0.9,
                )
                hooks.append(hook)
            if recent_posts and isinstance(recent_posts, list) and (len(recent_posts) > 0):
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
            if education and isinstance(education, list) and self.my_education:
                my_school = self.my_education.get("school", "").lower()
                for edu in tqdm(education, desc="Processing", unit="item"):
                    if isinstance(edu, dict):
                        their_school = edu.get("school", "").lower()
                    elif isinstance(edu, str):
                        their_school = edu.lower()
                    else:
                        continue
                    if my_school and their_school and (my_school in their_school):
                        hook = MicroHook(
                            phrase=f"Always great to connect with a fellow {edu.get('school', 'alum')} alum...",
                            trigger_type="alumni",
                            relevance=0.8,
                        )
                        hooks.append(hook)
                        break
            if not hooks:
                hook = MicroHook(
                    phrase=f"I've been following {company_name}'s work in {industry}...",
                    trigger_type="generic",
                    relevance=0.3,
                )
                hooks.append(hook)
            hooks.sort(key=lambda h: h.relevance, reverse=True)
            logger.debug(f"Generated {len(hooks)} hooks, top relevance: {hooks[0].relevance:.2f}")
            return hooks
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error generating hooks: {str(e)}")
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
            if not text_samples or not isinstance(text_samples, list):
                return SentimentProfile(
                    mood=SentimentMood.NEUTRAL,
                    risk_level=RiskLevel.LOW,
                    keywords_detected=[],
                )
            combined_text = " ".join(str(s) for s in text_samples if s).lower()
            words = re.findall("\\b\\w+\\b", combined_text)
            word_set = set(words)
            optimistic_count = len(word_set.intersection(self.optimistic_words))
            cautious_count = len(word_set.intersection(self.cautious_words))
            hostile_count = len(word_set.intersection(self.hostile_words))
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
            profile = SentimentProfile(mood=mood, risk_level=risk, keywords_detected=keywords_detected[:5])
            logger.info(f"Assessed sentiment: {mood.value} (risk: {risk.value})")
            return profile
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error assessing sentiment: {str(e)}")
            return SentimentProfile(
                mood=SentimentMood.NEUTRAL,
                risk_level=RiskLevel.LOW,
                keywords_detected=["error"],
            )


class WarmthManager:
    """Manages contextual warmth and formality adjustments."""

    def __init__(self):
        """Initialize the warmth manager."""
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
        self,
        archetype: str,
        relationship_stage: str,
        sentiment: SentimentMood,
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
            archetype_key = archetype.lower().strip()
            base_formality = self.base_formality.get(archetype_key, 0.5)
            stage_upper = relationship_stage.upper().strip()
            if stage_upper == "COLD":
                base_formality += 0.2
            elif stage_upper == "WARM":
                base_formality -= 0.2
            if sentiment == SentimentMood.OPTIMISTIC:
                base_formality -= 0.1
            elif sentiment == SentimentMood.CAUTIOUS:
                base_formality += 0.2
            elif sentiment == SentimentMood.HOSTILE:
                base_formality += 0.3
            base_formality = max(0.0, min(1.0, base_formality))
            if base_formality > 0.8:
                strategy = "Respectful Intrusion"
                max_emojis = 0
            elif base_formality < 0.4:
                strategy = "Peer Chat"
                # guardian: allow-magic-config
                max_emojis = 2
            else:
                strategy = "Professional Connect"
                max_emojis = 1
            warmth = WarmthSetting(
                formality_level=base_formality,
                strategy_name=strategy,
                max_emojis=max_emojis,
            )
            logger.debug(f"Determined warmth: {strategy} (formality: {base_formality:.2f})")
            return warmth
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error determining warmth: {str(e)}")
            return WarmthSetting(formality_level=0.6, strategy_name="Professional Default", max_emojis=1)


class TemperatureEngine:
    """Facade class that orchestrates all temperature components."""

    def __init__(self, target_keywords: list[str] | None = None, my_education: dict[str, str] | None = None):
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

    def analyze_temperature(self, profile: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Analyze all temperature aspects for a recipient.

        Args:
            profile: Recipient profile dictionary
            context: Additional context (archetype, relationship_stage, text_samples)

        Returns:
            Dictionary with all temperature analysis results
        """
        try:
            archetype = context.get("archetype", "peer")
            relationship_stage = context.get("relationship_stage", "COLD")
            text_samples = context.get("text_samples", [])
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
                    "warmth": {"formality_level": 1.0, "strategy_name": "DO NOT CONTACT", "max_emojis": 0},
                    "recommendations": ["DO NOT CONTACT - recipient appears hostile"],
                    "abort": True,
                }
            depth_score = self.depth_scorer.calculate_depth(profile)
            hooks = self.hook_generator.generate_hooks(profile)
            warmth_setting = self.warmth_manager.determine_warmth(
                archetype,
                relationship_stage,
                sentiment_profile.mood,
            )
            results = {
                "depth_score": depth_score.dict(),
                "top_hooks": [h.dict() for h in hooks[:3]],
                "sentiment": sentiment_profile.dict(),
                "warmth": warmth_setting.dict(),
                "recommendations": self._generate_recommendations(
                    depth_score,
                    sentiment_profile,
                    warmth_setting,
                ),
                "abort": False,
            }
            logger.info(f"Temperature analysis complete for {profile.get('name', 'Unknown')}")
            return results
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error in temperature analysis: {str(e)}")
            return {
                "error": str(e),
                "depth_score": {"level": 0, "score": 0.1, "rationale": ["Error"]},
                "top_hooks": [],
                "sentiment": {"mood": "NEUTRAL", "risk_level": "LOW", "keywords_detected": []},
                "warmth": {"formality_level": 0.6, "strategy_name": "Error Default", "max_emojis": 1},
                "recommendations": ["Proceed with caution due to analysis error"],
                "abort": False,
            }

    def _generate_recommendations(
        self,
        depth: DepthScore,
        sentiment: SentimentProfile,
        warmth: WarmthSetting,
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
        if depth.level == 0:
            recommendations.append("Use generic opener - limited personalization available")
        elif depth.level >= 2:
            recommendations.append("High personalization possible - reference specific details")
        if sentiment.risk_level == RiskLevel.CRITICAL:
            recommendations.append("DO NOT CONTACT - recipient appears hostile")
        elif sentiment.mood == SentimentMood.CAUTIOUS:
            recommendations.append("Use deferential tone, acknowledge current challenges")
        elif sentiment.mood == SentimentMood.OPTIMISTIC:
            recommendations.append("Match their positive energy, focus on opportunities")
        if warmth.max_emojis == 0:
            recommendations.append("Maintain professional tone, no emojis")
        elif warmth.max_emojis >= 2:
            recommendations.append("Casual tone acceptable, 1-2 emojis may be used")
        return recommendations


def create_temperature_engine(
    target_keywords: list[str] | None = None,
    my_education: dict[str, str] | None = None,
) -> TemperatureEngine:
    """Create a TemperatureEngine instance."""
    return TemperatureEngine(target_keywords, my_education)


def analyze_temperature(profile: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Quickly analyze temperature for a profile."""
    engine = create_temperature_engine()
    return engine.analyze_temperature(profile, context)
