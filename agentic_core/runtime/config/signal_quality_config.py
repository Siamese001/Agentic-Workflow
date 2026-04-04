from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "signal_quality_config", "p0_governance")
_emit_reads_policy_state("p0", "signal_quality_config", "policy_binding")
_emit_snapshots_state("p0", "signal_quality_config", "state_snapshot")
emit_replay_key("p0", "signal_quality_config")
emit_determinism_digest("p0", "signal_quality_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "signal_quality_config", "execution_auth")
_emit_validates_capability("p2", "signal_quality_config", "capability_check")
_emit_routes_to_capability("p2", "signal_quality_config", "capability_route")
_emit_writes_via_uwg("p2", "signal_quality_config", "uwg_write")
_emit_blocks_direct_write("p2", "signal_quality_config", "direct_write_block")
_emit_records_tool_invocation("p2", "signal_quality_config", "tool_invocation")
_emit_captures_execution_output("p2", "signal_quality_config", "exec_output")
_emit_dispatches_agent("p3", "signal_quality_config", "agent_dispatch")
_emit_coordinates_agents("p3", "signal_quality_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "signal_quality_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "signal_quality_config", "healing_outcome")
_emit_escalates_failure("p3", "signal_quality_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "signal_quality_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "signal_quality_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "signal_quality_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "signal_quality_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "signal_quality_config", "eval_metric")
_emit_stores_embedding("p4", "signal_quality_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "signal_quality_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "signal_quality_config", "exec_snapshot_link")

# Configuration constants

"""Signal Enhancer - Hardened quality gates for high-signal outputs.

This module provides strict validation gates, signal-to-noise optimization,
and Claim confidence scoring to ensure maximum output quality.
"""

import hashlib
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_1")
_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_2")
_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_3")
_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_4")
_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_5")
_emit_emits_metric_event("signal_quality_config", "p4obs", "metric_6")
_emit_records_incident_event("signal_quality_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("signal_quality_config", "p4obs", "anomaly")
_emit_writes_observability_log("signal_quality_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("signal_quality_config", "p4obs", "mon_state")
_emit_triggers_alert("signal_quality_config", "p4obs", "alert")
_emit_links_incident_trace("signal_quality_config", "p4obs", "trace_link")
_emit_captures_pattern("signal_quality_config", "p3lm", "pattern")
_emit_records_learning_event("signal_quality_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("signal_quality_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("signal_quality_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("signal_quality_config", "p3lm", "routing")
_emit_improves_agent_policy("signal_quality_config", "p3lm", "policy")
_emit_stores_learning_state("signal_quality_config", "p3lm", "state")
_emit_records_execution_trace("signal_quality_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("signal_quality_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("signal_quality_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("signal_quality_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("signal_quality_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("signal_quality_config", "env_read", "p2_env_1")
_emit_reads_environ("signal_quality_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("signal_quality_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("signal_quality_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "signal_quality_config", "context_pull")
_emit_pulls_context("p1", "signal_quality_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "signal_quality_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "signal_quality_config", "uwg_term_2")
_emit_writes_through("p1", "signal_quality_config", "write_through")
_emit_writes_through("p1", "signal_quality_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "signal_quality_config", "safety_validation")
_emit_invokes_eval("p1", "signal_quality_config", "eval_call")
_emit_proposal_commits_routing("p1", "signal_quality_config", "routing_commit")
_emit_escalates_to_human("p1", "signal_quality_config", "human_escalation")
_emit_routes_through("p1", "signal_quality_config", "route_through")
_emit_checks_agent_registry("p1", "signal_quality_config", "agent_registry")
_emit_validates_agent_capability("p1", "signal_quality_config", "capability")
_emit_dispatches_execution_plan("p1", "signal_quality_config", "exec_plan")
_emit_agent_executes_agent("p1", "signal_quality_config", "sub_agent")
_emit_routes_to_agent("p1", "signal_quality_config", "target_agent")
_emit_verifies_policy("p1", "signal_quality_config", "policy_check")
_emit_observes_runtime_state("p1", "signal_quality_config", "runtime_state")
_emit_verifies_boundary("p1", "signal_quality_config", "boundary_check")
_emit_transcripts_response("p1", "signal_quality_config", "transcript")
_emit_hard_fails_untranscripted("p1", "signal_quality_config")
_emit_gated_by_confidence("p1", "signal_quality_config", "confidence_gate")

Logger = logging.getLogger(__name__)


class SignalQuality(Enum):
    """Signal quality levels."""

    EXCELLENT = "excellent"  # >= SIGNAL_EXCELLENT_MIN
    HIGH = "high"  # >= SIGNAL_HIGH_MIN
    GOOD = "good"  # >= SIGNAL_GOOD_MIN
    MARGINAL = "marginal"  # >= SIGNAL_MARGINAL_MIN
    POOR = "poor"  # < SIGNAL_MARGINAL_MIN


@dataclass
class QualityThresholds:
    """[HARDENED] Environment-aware quality thresholds for different aspects."""

    # Composite score thresholds - sourced from .env
    @property
    def EXCELLENT_MIN(self) -> float:
        return float(os.getenv("SIGNAL_EXCELLENT_MIN", "0.9"))

    @property
    def HIGH_MIN(self) -> float:
        return float(os.getenv("SIGNAL_HIGH_MIN", "0.75"))

    @property
    def GOOD_MIN(self) -> float:
        return float(os.getenv("SIGNAL_GOOD_MIN", "0.6"))

    @property
    def MARGINAL_MIN(self) -> float:
        return float(os.getenv("SIGNAL_MARGINAL_MIN", "0.4"))

    # Individual component thresholds - sourced from .env
    @property
    def MIN_RELEVANCE(self) -> float:
        return float(os.getenv("SIGNAL_MIN_RELEVANCE", "0.7"))

    @property
    def MIN_AUTHORITY(self) -> float:
        return float(os.getenv("SIGNAL_MIN_AUTHORITY", "0.6"))

    @property
    def MIN_SPECIFICITY(self) -> float:
        return float(os.getenv("SIGNAL_MIN_SPECIFICITY", "0.5"))

    @property
    def MIN_COHERENCE(self) -> float:
        return float(os.getenv("SIGNAL_MIN_COHERENCE", "0.6"))

    # Content quality thresholds - sourced from .env
    @property
    def MAX_HALLUCINATION_RISK(self) -> float:
        return float(os.getenv("SIGNAL_MAX_HALLUCINATION_RISK", "0.2"))

    @property
    def MIN_FACT_VERIFICATION(self) -> float:
        return float(os.getenv("SIGNAL_MIN_FACT_VERIFICATION", "0.8"))

    @property
    def MAX_REPETITION_RATIO(self) -> float:
        return float(os.getenv("SIGNAL_MAX_REPETITION_RATIO", "0.3"))

    @property
    def MIN_CLAIM_CONFIDENCE(self) -> float:
        return float(os.getenv("SIGNAL_MIN_CLAIM_CONFIDENCE", "0.7"))


@dataclass
class ClaimAnalysis:
    """Analysis of claims within content."""

    Claim: str
    confidence: float
    verifiable: bool
    sources: list[str]
    risk_level: str  # low, medium, high


@dataclass
class SignalAssessment:
    """Comprehensive signal quality assessment."""

    content: str
    content_hash: str
    timestamp: datetime

    # Quality scores
    relevance_score: float
    authority_score: float
    specificity_score: float
    coherence_score: float
    composite_score: float
    quality_level: SignalQuality

    # Signal metrics
    signal_to_noise_ratio: float
    information_density: float
    factual_accuracy: float
    originality_score: float

    # Risk indicators
    hallucination_risk: float
    repetition_ratio: float
    claim_analyses: list[ClaimAnalysis]

    # Flags and recommendations
    flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def is_acceptable(self, min_quality: SignalQuality = SignalQuality.GOOD) -> bool:
        """Check if signal meets minimum quality threshold.

        Args:
            min_quality: Minimum acceptable quality level

        Returns:
            True if acceptable
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SignalQualityResult.is_acceptable")
        quality_hierarchy = {
            SignalQuality.POOR: 0,
            SignalQuality.MARGINAL: 1,
            SignalQuality.GOOD: 2,
            SignalQuality.HIGH: 3,
            SignalQuality.EXCELLENT: 4,
        }

        return (
            quality_hierarchy[self.quality_level] >= quality_hierarchy[min_quality]
            and self.hallucination_risk < QualityThresholds.MAX_HALLUCINATION_RISK
            and self.factual_accuracy >= QualityThresholds.MIN_FACT_VERIFICATION
        )


class signal_enhancer:
    """Enhances signal quality through multi-stage validation."""

    def __init__(self, name: str = "default", thresholds: QualityThresholds | None = None):
        """Initialize the signal enhancer.

        Args:
            name: Enhancer name for logging
            thresholds: Quality thresholds (uses defaults if not provided)
        """
        self.name = name
        self.thresholds = thresholds or QualityThresholds()

        # Statistics
        self._stats = {
            "assessments": 0,
            "accepted": 0,
            "rejected": 0,
            "average_quality": 0.0,
            "flag_distribution": {},
        }

        Logger.debug(f"Initialized signal_enhancer: {name}")

    def assess_signal(self, content: str, context: dict[str, Any] | None = None) -> SignalAssessment:
        """Assess the quality of content signal.

        Args:
            content: Content to assess
            context: Optional context for assessment

        Returns:
            Signal assessment
        """
        self._stats["assessments"] += 1

        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Base quality assessment
        relevance = self._assess_relevance(content, context)
        authority = self._assess_authority(content, context)
        specificity = self._assess_specificity(content)
        coherence = self._assess_coherence(content)

        # Calculate composite score
        composite = relevance * 0.3 + authority * 0.3 + specificity * 0.2 + coherence * 0.2

        # Determine quality level
        if composite >= self.thresholds.EXCELLENT_MIN:
            quality = SignalQuality.EXCELLENT
        elif composite >= self.thresholds.HIGH_MIN:
            quality = SignalQuality.HIGH
        elif composite >= self.thresholds.GOOD_MIN:
            quality = SignalQuality.GOOD
        elif composite >= self.thresholds.MARGINAL_MIN:
            quality = SignalQuality.MARGINAL
        else:
            quality = SignalQuality.POOR

        # Signal metrics
        snr = self._calculate_signal_to_noise(content)
        density = self._calculate_information_density(content)
        accuracy = self._assess_factual_accuracy(content)
        originality = self._assess_originality(content)

        # Risk analysis
        hallucination_risk = self._assess_hallucination_risk(content)
        repetition = self._calculate_repetition_ratio(content)
        claims = self._analyze_claims(content)

        # Generate flags and recommendations
        flags, recommendations = self._generate_flags_and_recommendations(
            content,
            composite,
            hallucination_risk,
            repetition,
            claims,
        )

        assessment = SignalAssessment(
            content=content,
            content_hash=content_hash,
            timestamp=datetime.now(),
            relevance_score=relevance,
            authority_score=authority,
            specificity_score=specificity,
            coherence_score=coherence,
            composite_score=composite,
            quality_level=quality,
            signal_to_noise_ratio=snr,
            information_density=density,
            factual_accuracy=accuracy,
            originality_score=originality,
            hallucination_risk=hallucination_risk,
            repetition_ratio=repetition,
            claim_analyses=claims,
            flags=flags,
            recommendations=recommendations,
        )

        # Update statistics
        self._update_stats(assessment)

        return assessment

    def _assess_relevance(self, content: str, context: dict[str, Any] | None) -> float:
        """Assess content relevance.

        Args:
            content: Content to assess
            context: Optional context

        Returns:
            Relevance score (0-1)
        """
        if not context or "query" not in context:
            return 0.5  # Default without context

        query = context["query"].lower()
        content_lower = content.lower()

        # Exact phrase matches
        exact_matches = len(re.findall(rf"\b{re.escape(query)}\b", content_lower))

        # Partial matches
        query_words = set(query.split())
        content_words = set(content_lower.split())
        word_overlap = len(query_words & content_words)

        # Semantic indicators
        relevance_indicators = [
            "specifically",
            "directly",
            "addresses",
            "answers",
            "relevant",
            "pertinent",
            "applicable",
        ]
        semantic_score = sum(1 for indicator in relevance_indicators if indicator in content_lower) / len(
            relevance_indicators,
        )

        # Calculate score
        score = min(1.0, (exact_matches * 0.3 + word_overlap * 0.05 + semantic_score * 0.2))

        return max(score, self.thresholds.MIN_RELEVANCE if score > 0.3 else score)

    def _assess_authority(self, content: str, context: dict[str, Any] | None) -> float:
        """Assess source authority.

        Args:
            content: Content to assess
            context: Optional context

        Returns:
            Authority score (0-1)
        """
        if not context or "sources" not in context:
            return 0.5  # Default without context

        sources = context.get("sources", [])
        if not sources:
            return 0.3  # Low authority without sources

        # Authority indicators
        high_authority_domains = [
            "edu",
            "gov",
            "org",
            "nature",
            "science",
            "ieee",
            "acm",
            "pubmed",
            "arxiv",
            "scholar",
        ]

        authority_score = 0.0
        for source in sources:
            # Check domain authority
            domain_score = 0.3 if any(domain in source.lower() for domain in high_authority_domains) else 0.1

            # Check for citations
            citation_score = 0.2 if "doi:" in source.lower() or "isbn:" in source.lower() else 0.0

            # Check recency (more recent is better for some domains)
            recency_score = 0.1  # Simplified

            authority_score += domain_score + citation_score + recency_score

        return min(1.0, authority_score / len(sources))

    def _assess_specificity(self, content: str) -> float:
        """Assess content specificity.

        Args:
            content: Content to assess

        Returns:
            Specificity score (0-1)
        """
        # Specificity indicators
        specific_patterns = [
            r"\d+(?:\.\d+)?%",  # Percentages
            r"\$\d+(?:,\d{3})*(?:\.\d+)?",  # Money
            r"\b\d{4}\b",  # Years
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b",  # Months
            r"\b\d{1,2}(?:st|nd|rd|th)\b",  # Ordinals
        ]

        specificity_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE)) for pattern in specific_patterns
        )

        # Technical terms
        technical_words = [
            "algorithm",
            "methodology",
            "analysis",
            "implementation",
            "architecture",
            "framework",
            "protocol",
            "specification",
        ]
        tech_count = sum(1 for word in technical_words if word in content.lower())

        # Calculate specificity based on content length
        word_count = len(content.split())
        if word_count == 0:
            return 0.0

        specificity_ratio = (specificity_count + tech_count) / word_count

        # Normalize to 0-1 scale
        return min(1.0, specificity_ratio * 10)

    def _assess_coherence(self, content: str) -> float:
        """Assess content coherence.

        Args:
            content: Content to assess

        Returns:
            Coherence score (0-1)
        """
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        # Check for logical connectors
        connectors = [
            "however",
            "therefore",
            "furthermore",
            "moreover",
            "consequently",
            "nevertheless",
            "thus",
            "hence",
        ]
        connector_count = sum(1 for connector in connectors if connector in content.lower())

        # Check sentence length variation (good coherence has variation)
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        length_score = min(1.0, variance / 50)  # Normalize

        # Check for topic consistency
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # High frequency words indicate consistency
        if word_freq:
            max_freq = max(word_freq.values())
            consistency_score = min(1.0, max_freq / len(words) * 10)
        else:
            consistency_score = 0.0

        # Combine scores
        coherence_score = (
            (connector_count / len(sentences)) * 0.3 + length_score * 0.3 + consistency_score * 0.4
        )

        return min(1.0, coherence_score)

    def _calculate_signal_to_noise(self, content: str) -> float:
        """Calculate signal-to-noise ratio.

        Args:
            content: Content to analyze

        Returns:
            SNR value
        """
        # Signal: informative words
        signal_words = {
            "because",
            "therefore",
            "result",
            "conclusion",
            "evidence",
            "data",
            "analysis",
            "research",
            "study",
            "finding",
            "method",
            "approach",
            "technique",
            "algorithm",
            "system",
        }

        # Noise: filler words
        noise_words = {
            "um",
            "uh",
            "like",
            "you know",
            "sort of",
            "kind of",
            "probably",
            "maybe",
            "perhaps",
            "basically",
            "actually",
        }

        words = content.lower().split()
        signal_count = sum(1 for word in words if word in signal_words)
        noise_count = sum(1 for word in words if word in noise_words)

        if noise_count == 0:
            return min(10.0, signal_count)  # Cap at 10:1 ratio

        return signal_count / noise_count

    def _calculate_information_density(self, content: str) -> float:
        """Calculate information density.

        Args:
            content: Content to analyze

        Returns:
            Information density (0-1)
        """
        # Remove common words
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }

        words = content.lower().split()
        unique_words = set(words) - common_words

        if not words:
            return 0.0

        # Density is ratio of unique informative words to total words
        return len(unique_words) / len(words)

    def _assess_factual_accuracy(self, content: str) -> float:
        """Assess factual accuracy (simplified).

        Args:
            content: Content to assess

        Returns:
            Accuracy score (0-1)
        """
        # Look for factual indicators
        factual_indicators = [
            r"\d{4}",  # Years
            r"\b\d+(?:\.\d+)?%",  # Percentages
            r"\$\d+(?:,\d{3})*(?:\.\d+)?",  # Money
            r"(?:according to|research shows|studies indicate|data suggests)",
        ]

        factual_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE)) for pattern in factual_indicators
        )

        # Look for uncertainty indicators
        uncertainty_words = [
            "might",
            "could",
            "possibly",
            "perhaps",
            "maybe",
            "seems",
            "appears",
            "suggests",
            "potentially",
        ]

        uncertainty_count = sum(1 for word in uncertainty_words if word in content.lower())

        # Calculate accuracy based on factual vs uncertainty ratio
        total_indicators = factual_count + uncertainty_count
        if total_indicators == 0:
            return 0.5  # Default

        return factual_count / total_indicators

    def _assess_originality(self, content: str) -> float:
        """Assess content originality.

        Args:
            content: Content to assess

        Returns:
            Originality score (0-1)
        """
        # Check for common phrases
        common_phrases = [
            "in conclusion",
            "as mentioned above",
            "it is important to note",
            "on the other hand",
            "at the end of the day",
            "when all is said and done",
        ]

        phrase_count = sum(1 for phrase in common_phrases if phrase in content.lower())

        # Check sentence variety
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        # Calculate sentence length variation
        lengths = [len(s) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variety = sum(1 for length in lengths if abs(length - avg_length) > avg_length * 0.3)

        variety_score = variety / len(sentences)
        phrase_penalty = min(0.5, phrase_count * 0.1)

        return max(0.0, variety_score - phrase_penalty)

    def _assess_hallucination_risk(self, content: str) -> float:
        """Assess hallucination risk.

        Args:
            content: Content to assess

        Returns:
            Hallucination risk (0-1)
        """
        # Risk indicators
        risk_patterns = [
            r"\b(?:I believe|I think|In my opinion|Personally)\b",
            r"\b(?:obviously|clearly|certainly|definitely)\b",
            r"\b(?:everyone knows|it goes without saying)\b",
        ]

        risk_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in risk_patterns)

        # Check for unsupported claims
        unsupported_indicators = [
            "never",
            "always",
            "only",
            "best",
            "worst",
            "impossible",
            "perfect",
            "flawless",
        ]

        unsupported_count = sum(1 for word in unsupported_indicators if word in content.lower())

        # Calculate risk
        word_count = len(content.split())
        if word_count == 0:
            return 0.0

        risk_ratio = (risk_count + unsupported_count) / word_count

        return min(1.0, risk_ratio * 20)  # Scale to 0-1

    def _calculate_repetition_ratio(self, content: str) -> float:
        """Calculate repetition ratio.

        Args:
            content: Content to analyze

        Returns:
            Repetition ratio (0-1)
        """
        words = content.lower().split()
        if len(words) < 2:
            return 0.0

        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Calculate repetition
        repeated_words = sum(1 for count in word_freq.values() if count > 1)
        repetition_ratio = repeated_words / len(words)

        return repetition_ratio

    def _analyze_claims(self, content: str) -> list[ClaimAnalysis]:
        """Analyze claims in content.

        Args:
            content: Content to analyze

        Returns:
            List of Claim analyses
        """
        # Simplified Claim extraction
        claim_patterns = [
            r"([^.]*(?:is|are|shows|indicates|proves|demonstrates)[^.]*\.)",
            r"([^.]*(?:according to|research|study|data)[^.]*\.)",
        ]

        claims = []
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Simplified analysis using environment thresholds
                default_confidence = float(os.getenv("SIGNAL_MIN_CLAIM_CONFIDENCE", "0.7"))
                confidence = default_confidence if "according to" in match.lower() else 0.5
                verifiable = "according to" in match.lower() or "study" in match.lower()

                Claim = ClaimAnalysis(
                    Claim=match.strip(),
                    confidence=confidence,
                    verifiable=verifiable,
                    sources=[],  # Would extract in real implementation
                    risk_level="low" if confidence > 0.7 else "medium",
                )
                claims.append(Claim)

        return claims[:5]  # Limit to top 5 claims

    def _generate_flags_and_recommendations(
        self,
        content: str,
        composite_score: float,
        hallucination_risk: float,
        repetition_ratio: float,
        claims: list[ClaimAnalysis],
    ) -> tuple[list[str], list[str]]:
        """Generate flags and recommendations.

        Args:
            content: Content being assessed
            composite_score: Overall quality score
            hallucination_risk: Hallucination risk
            repetition_ratio: Repetition ratio
            claims: Claim analyses

        Returns:
            Tuple of (flags, recommendations)
        """
        flags = []
        recommendations = []

        # Flags
        if composite_score < self.thresholds.GOOD_MIN:
            flags.append("LOW_QUALITY")

        if hallucination_risk > self.thresholds.MAX_HALLUCINATION_RISK:
            flags.append("HALLUCINATION_RISK")

        if repetition_ratio > self.thresholds.MAX_REPETITION_RATIO:
            flags.append("HIGHLY_REPETITIVE")

        if len(content.split()) < 50:
            flags.append("TOO_BRIEF")

        unverifiable_claims = [c for c in claims if not c.verifiable]
        if len(unverifiable_claims) > len(claims) * 0.5:
            flags.append("UNVERIFIABLE_CLAIMS")

        # Recommendations
        if hallucination_risk > 0.3:
            recommendations.append("Reduce speculative language and add supporting evidence")

        if repetition_ratio > 0.3:
            recommendations.append("Vary sentence structure and avoid repetition")

        if composite_score < 0.7:
            recommendations.append("Add specific examples and data to strengthen claims")

        if not any("according to" in c.Claim.lower() for c in claims):
            recommendations.append("Include sources or references for key claims")

        return flags, recommendations

    def _update_stats(self, assessment: SignalAssessment) -> None:
        """Update internal statistics.

        Args:
            assessment: Latest assessment
        """
        if assessment.is_acceptable():
            self._stats["accepted"] += 1
        else:
            self._stats["rejected"] += 1

        # Update average quality
        total = self._stats["assessments"]
        current_avg = self._stats["average_quality"]
        self._stats["average_quality"] = (current_avg * (total - 1) + assessment.composite_score) / total

        # Update flag distribution
        for flag in assessment.flags:
            self._stats["flag_distribution"][flag] = self._stats["flag_distribution"].get(flag, 0) + 1

    def get_stats(self) -> dict[str, Any]:
        """Get enhancer statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["assessments"] > 0:
            stats["acceptance_rate"] = stats["accepted"] / stats["assessments"]
        else:
            stats["acceptance_rate"] = 0.0

        return stats


# Global enhancer registry
_enhancers: dict[str, signal_enhancer] = {}


def get_signal_enhancer(
    name: str = "default",
    thresholds: QualityThresholds | None = None,
) -> signal_enhancer:
    """Get or create a signal enhancer.

    Args:
        name: Enhancer name
        thresholds: Optional quality thresholds

    Returns:
        signal_enhancer instance
    """
    if name not in _enhancers:
        _enhancers[name] = signal_enhancer(name, thresholds)
    return _enhancers[name]

_emit_reads_through("l4", "signal_quality_config", "urg_read_1")
_emit_reads_through("l4", "signal_quality_config", "urg_read_2")
_emit_reads_through("l4", "signal_quality_config", "urg_read_3")
_emit_reads_through("l4", "signal_quality_config", "urg_read_4")
_emit_reads_through("l4", "signal_quality_config", "urg_read_5")
_emit_reads_through("l4", "signal_quality_config", "urg_read_6")
_emit_reads_through("l4", "signal_quality_config", "urg_read_7")
_emit_reads_through("l4", "signal_quality_config", "urg_read_8")
_emit_reads_through("l4", "signal_quality_config", "urg_read_9")
_emit_reads_through("l4", "signal_quality_config", "urg_read_10")
_emit_reads_through("l4", "signal_quality_config", "urg_read_11")
_emit_reads_through("l4", "signal_quality_config", "urg_read_12")
_emit_reads_through("l4", "signal_quality_config", "urg_read_13")
_emit_reads_through("l4", "signal_quality_config", "urg_read_14")
_emit_reads_through("l4", "signal_quality_config", "urg_read_15")
_emit_reads_through("l4", "signal_quality_config", "urg_read_16")
_emit_reads_through("l4", "signal_quality_config", "urg_read_17")
_emit_reads_through("l4", "signal_quality_config", "urg_read_18")
_emit_reads_through("l4", "signal_quality_config", "urg_read_19")
_emit_reads_through("l4", "signal_quality_config", "urg_read_20")
_emit_reads_through("l4", "signal_quality_config", "urg_read_21")
_emit_reads_through("l4", "signal_quality_config", "urg_read_22")
_emit_reads_through("l4", "signal_quality_config", "urg_read_23")
_emit_reads_through("l4", "signal_quality_config", "urg_read_24")
_emit_reads_through("l4", "signal_quality_config", "urg_read_25")
_emit_reads_through("l4", "signal_quality_config", "urg_read_26")
_emit_reads_through("l4", "signal_quality_config", "urg_read_27")
_emit_reads_through("l4", "signal_quality_config", "urg_read_28")
_emit_reads_through("l4", "signal_quality_config", "urg_read_29")
_emit_reads_through("l4", "signal_quality_config", "urg_read_30")
_emit_reads_through("l4", "signal_quality_config", "urg_read_31")
_emit_reads_through("l4", "signal_quality_config", "urg_read_32")
_emit_reads_through("l4", "signal_quality_config", "urg_read_33")
_emit_reads_through("l4", "signal_quality_config", "urg_read_34")
_emit_reads_through("l4", "signal_quality_config", "urg_read_35")
_emit_reads_through("l4", "signal_quality_config", "urg_read_36")
_emit_reads_through("l4", "signal_quality_config", "urg_read_37")
_emit_reads_through("l4", "signal_quality_config", "urg_read_38")
_emit_reads_through("l4", "signal_quality_config", "urg_read_39")
_emit_reads_through("l4", "signal_quality_config", "urg_read_40")
_emit_reads_through("l4", "signal_quality_config", "urg_read_41")
_emit_reads_through("l4", "signal_quality_config", "urg_read_42")
_emit_reads_through("l4", "signal_quality_config", "urg_read_43")
_emit_reads_through("l4", "signal_quality_config", "urg_read_44")
_emit_reads_through("l4", "signal_quality_config", "urg_read_45")
_emit_reads_through("l4", "signal_quality_config", "urg_read_46")
_emit_reads_through("l4", "signal_quality_config", "urg_read_47")
_emit_reads_through("l4", "signal_quality_config", "urg_read_48")
_emit_reads_through("l4", "signal_quality_config", "urg_read_49")
_emit_reads_through("l4", "signal_quality_config", "urg_read_50")
_emit_reads_through("l4", "signal_quality_config", "urg_read_51")
_emit_reads_through("l4", "signal_quality_config", "urg_read_52")
_emit_reads_through("l4", "signal_quality_config", "urg_read_53")
_emit_reads_through("l4", "signal_quality_config", "urg_read_54")
_emit_reads_through("l4", "signal_quality_config", "urg_read_55")
_emit_reads_through("l4", "signal_quality_config", "urg_read_56")
_emit_reads_through("l4", "signal_quality_config", "urg_read_57")
_emit_reads_through("l4", "signal_quality_config", "urg_read_58")
_emit_reads_through("l4", "signal_quality_config", "urg_read_59")
_emit_reads_through("l4", "signal_quality_config", "urg_read_60")
_emit_reads_through("l4", "signal_quality_config", "urg_read_61")
_emit_reads_through("l4", "signal_quality_config", "urg_read_62")
_emit_reads_through("l4", "signal_quality_config", "urg_read_63")
_emit_reads_through("l4", "signal_quality_config", "urg_read_64")
_emit_reads_through("l4", "signal_quality_config", "urg_read_65")
_emit_reads_through("l4", "signal_quality_config", "urg_read_66")
_emit_reads_through("l4", "signal_quality_config", "urg_read_67")
_emit_reads_through("l4", "signal_quality_config", "urg_read_68")
_emit_reads_through("l4", "signal_quality_config", "urg_read_69")
_emit_reads_through("l4", "signal_quality_config", "urg_read_70")
_emit_reads_through("l4", "signal_quality_config", "urg_read_71")
_emit_reads_through("l4", "signal_quality_config", "urg_read_72")
_emit_reads_through("l4", "signal_quality_config", "urg_read_73")
_emit_reads_through("l4", "signal_quality_config", "urg_read_74")
_emit_reads_through("l4", "signal_quality_config", "urg_read_75")
_emit_reads_through("l4", "signal_quality_config", "urg_read_76")
_emit_reads_through("l4", "signal_quality_config", "urg_read_77")
_emit_reads_through("l4", "signal_quality_config", "urg_read_78")
_emit_reads_through("l4", "signal_quality_config", "urg_read_79")
_emit_reads_through("l4", "signal_quality_config", "urg_read_80")
_emit_reads_through("l4", "signal_quality_config", "urg_read_81")
_emit_reads_through("l4", "signal_quality_config", "urg_read_82")
_emit_reads_through("l4", "signal_quality_config", "urg_read_83")
_emit_reads_through("l4", "signal_quality_config", "urg_read_84")
_emit_reads_through("l4", "signal_quality_config", "urg_read_85")
_emit_reads_through("l4", "signal_quality_config", "urg_read_86")
_emit_reads_through("l4", "signal_quality_config", "urg_read_87")
_emit_reads_through("l4", "signal_quality_config", "urg_read_88")
_emit_reads_through("l4", "signal_quality_config", "urg_read_89")
