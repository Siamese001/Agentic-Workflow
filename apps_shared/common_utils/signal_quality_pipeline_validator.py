"""Multi-Stage Signal Quality Pipeline - Quality Control for RAG Retrieval.

This module provides a quality control layer that evaluates retrieved chunks against
multiple quality standards before they reach the generation agents. Low-quality or
unverifiable content is filtered out to ensure only high-signal content is used.
"""

import logging
import re

logger = logging.getLogger(__name__)


class QualityAssessment(BaseModel):
    """Assessment result for a document's signal quality."""

    is_pass: bool = Field(..., description="Overall pass/fail decision")
    relevance_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Relevance to query")
    authority_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Source authority")
    specificity_score: confloat(ge=0.0, le=1.0) = Field(
        default=0.0, description="Metric specificity"
    )
    coherence_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Content coherence")
    flags: list[str] = Field(default_factory=list, description="Quality flags/warnings")
    doc_id: str | None = Field(None, description="Document identifier for logging")

    @validator("flags", pre=True)
    def validate_flags(cls, v):
        """Ensure flags is a list of strings."""
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []

    @property
    def composite_score(self) -> float:
        """Calculate composite quality score."""
        # Weighted average of all scores
        weights = {"relevance": 0.3, "authority": 0.3, "specificity": 0.2, "coherence": 0.2}
        return (
            self.relevance_score * weights["relevance"]
            + self.authority_score * weights["authority"]
            + self.specificity_score * weights["specificity"]
            + self.coherence_score * weights["coherence"]
        )

    def has_flag(self, flag: str) -> bool:
        """Check if a specific flag is present."""
        return flag in self.flags

    def add_flag(self, flag: str) -> None:
        """Add a quality flag."""
        if flag not in self.flags:
            self.flags.append(flag)


class SignalQualityPipeline:
    """Multi-stage quality control pipeline for RAG retrieval.

    This pipeline evaluates every retrieved chunk against a 5-stage standard
    to ensure only high-signal, verifiable content reaches the generation agents.
    """

    def __init__(
        self,
        relevance_threshold: float = 0.3,
        authority_threshold: float = 0.4,
        specificity_threshold: float = 0.5,
        enable_coherence_check: bool = False,
    ):
        """Initialize the quality pipeline.

        Args:
            relevance_threshold: Minimum relevance score to pass
            authority_threshold: Minimum authority score to pass
            specificity_threshold: Minimum specificity score to pass
            enable_coherence_check: Whether to run coherence checks (expensive)
        """
        self.relevance_threshold = relevance_threshold
        self.authority_threshold = authority_threshold
        self.specificity_threshold = specificity_threshold
        self.enable_coherence_check = enable_coherence_check

        # Source authority tiers
        self.authority_tiers = {
            # Tier 1: Official financial/regulatory documents
            "tier_1": {
                "score": 1.0,
                "sources": {
                    "10-k",
                    "10-q",
                    "official_report",
                    "sec_filing",
                    "annual_report",
                    "proxy_statement",
                },
            },
            # Tier 2: Professional profiles and verified resumes
            "tier_2": {
                "score": 0.8,
                "sources": {
                    "linkedin",
                    "resume_v1",
                    "official_resume",
                    "company_profile",
                    "verified_profile",
                },
            },
            # Tier 3: Notes and informal sources
            "tier_3": {
                "score": 0.5,
                "sources": {"notes", "blog", "scratchpad", "personal_notes", "draft"},
            },
            # Tier 4: Unverified or low-quality sources
            "tier_4": {"score": 0.2, "sources": {"unknown", "unverified", "cached", "temp"}},
        }

        # Impact words that should have metrics
        self.impact_words = {
            "grew",
            "growth",
            "increased",
            "decreased",
            "reduced",
            "saved",
            "generated",
            "achieved",
            "improved",
            "optimized",
            "accelerated",
            "expanded",
            "launched",
            "delivered",
            "completed",
            "managed",
            "led",
            "built",
            "created",
            "drove",
            "revenue",
            "cost",
            "savings",
            "profit",
            "margin",
            "roi",
            "efficiency",
        }

        # Metric patterns to detect
        self.metric_patterns = [
            r"\$\d+(?:,\d{3})*(?:\.\d+)?[kmb]?",  # Money values
            r"\d+(?:,\d{3})*(?:\.\d+)?%",  # Percentages
            r"\d+(?:,\d{3})*(?:\.\d+)?[kmb]",  # Large numbers with suffix
            r"\d+(?:,\d{3})*(?:\.\d+)?x",  # Multipliers
            r"\d+(?:,\d{3})*(?:\.\d+)?\s*(?:times|fold)",  # Multipliers (words)
            r"\b\d+\s*(?:years?|months?|weeks?|days?)\b",  # Time periods
        ]

        logger.info(
            f"Initialized SignalQualityPipeline with thresholds: "
            f"relevance={relevance_threshold}, authority={authority_threshold}, "
            f"specificity={specificity_threshold}"
        )

    def evaluate_signal(
        self, content: str, metadata: dict[str, str], query: str, doc_id: str | None = None
    ) -> QualityAssessment:
        """Evaluate a signal through all quality checks.

        Args:
            content: Document content to evaluate
            metadata: Document metadata (source, type, etc.)
            query: Original search query for relevance checking
            doc_id: Document identifier for logging

        Returns:
            QualityAssessment with detailed evaluation results
        """
        try:
            assessment = QualityAssessment(is_pass=True, doc_id=doc_id)

            # Validate inputs
            if not content or not isinstance(content, str):
                logger.warning(f"Empty or invalid content for doc {doc_id}")
                assessment.is_pass = False
                assessment.add_flag("EMPTY_CONTENT")
                return assessment

            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata type for doc {doc_id}: {type(metadata)}")
                metadata = {}

            if not query or not isinstance(query, str):
                logger.warning(f"Invalid query for doc {doc_id}: {type(query)}")
                query = ""

            # Stage 1: Relevance Filter
            assessment.relevance_score = self._check_relevance(content, query)
            if assessment.relevance_score < self.relevance_threshold:
                assessment.add_flag("LOW_RELEVANCE")

            # Stage 2: Source Authority
            assessment.authority_score = self._check_authority(metadata)
            if assessment.authority_score < self.authority_threshold:
                assessment.add_flag("LOW_AUTHORITY")

            # Stage 3: Specificity/Metric Check
            assessment.specificity_score = self._check_specificity(content)
            if assessment.specificity_score < self.specificity_threshold:
                assessment.add_flag("MISSING_METRICS")

            # Stage 4: Coherence Check (optional, expensive)
            if self.enable_coherence_check:
                assessment.coherence_score = self._check_coherence(content)
                if assessment.coherence_score < 0.5:
                    assessment.add_flag("LOW_COHERENCE")
            else:
                assessment.coherence_score = 0.5  # Default neutral score

            # Stage 5: Apply hard rules
            if (
                assessment.authority_score < self.authority_threshold
                or assessment.relevance_score < self.relevance_threshold
            ):
                assessment.is_pass = False
                assessment.add_flag("HARD_FAIL")

            logger.debug(
                f"Signal evaluation for doc {doc_id}: relevance={assessment.relevance_score:.2f}, "
                f"authority={assessment.authority_score:.2f}, "
                f"specificity={assessment.specificity_score:.2f}, "
                f"flags={assessment.flags}, pass={assessment.is_pass}",
                extra={"doc_id": doc_id, "flags": assessment.flags, "is_pass": assessment.is_pass},
            )

            return assessment

        except Exception as e:
            logger.error(f"Error evaluating signal for doc {doc_id}: {str(e)}")
            # Return safe fallback
            return QualityAssessment(is_pass=False, flags=["EVALUATION_ERROR"], doc_id=doc_id)

    def _check_relevance(self, content: str, query: str) -> float:
        """Check relevance between content and query using keyword overlap.

        Args:
            content: Document content
            query: Search query

        Returns:
            Relevance score (0.0-1.0)
        """
        try:
            # Normalize and tokenize
            content_words = set(self._normalize_text(content.lower()))
            query_words = set(self._normalize_text(query.lower()))

            if not query_words:
                return 0.0

            # Calculate Jaccard similarity
            intersection = content_words.intersection(query_words)
            union = content_words.union(query_words)

            if not union:
                return 0.0

            jaccard = len(intersection) / len(union)

            # Boost score for exact phrase matches
            query_lower = query.lower()
            content_lower = content.lower()
            if query_lower in content_lower:
                jaccard = min(1.0, jaccard * 1.5)

            return min(1.0, jaccard)
        except Exception as e:
            logger.error(f"Error checking relevance: {str(e)}")
            return 0.0

    def _check_authority(self, metadata: dict[str, str]) -> float:
        """Check source authority based on metadata.

        Args:
            metadata: Document metadata

        Returns:
            Authority score (0.0-1.0)
        """
        try:
            source = metadata.get("source", "").lower()
            doc_type = metadata.get("type", "").lower()

            # Check all source identifiers
            for _tier_name, tier_config in self.authority_tiers.items():
                for source_id in tier_config["sources"]:
                    if source_id in source or source_id in doc_type:
                        return tier_config["score"]

            # Default to tier 4 for unknown sources
            return self.authority_tiers["tier_4"]["score"]
        except Exception as e:
            logger.error(f"Error checking authority: {str(e)}")
            return 0.2  # Conservative default

    def _check_specificity(self, content: str) -> float:
        """Check content specificity based on presence of metrics.

        Args:
            content: Document content

        Returns:
            Specificity score (0.0-1.0)
        """
        try:
            content_lower = content.lower()

            # Check for impact words
            has_impact_words = any(word in content_lower for word in self.impact_words)

            # Check for metrics
            has_metrics = any(
                re.search(pattern, content, re.IGNORECASE) for pattern in self.metric_patterns
            )

            # scoring logic
            if has_impact_words and has_metrics:
                # High specificity: impact claims with supporting metrics
                return 0.9
            elif has_metrics and not has_impact_words:
                # Medium specificity: metrics but no clear impact
                return 0.7
            elif has_impact_words and not has_metrics:
                # Low specificity: impact claims without metrics
                return 0.3
            else:
                # Very low specificity: neither impact nor metrics
                return 0.1
        except Exception as e:
            logger.error(f"Error checking specificity: {str(e)}")
            return 0.1  # Conservative default

    def _check_coherence(self, content: str) -> float:
        """Check content coherence (simplified implementation).

        Args:
            content: Document content

        Returns:
            Coherence score (0.0-1.0)
        """
        try:
            # Simple coherence checks
            sentences = re.split(r"[.!?]+", content)
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return 0.0

            # Check average sentence length (very rough coherence proxy)
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

            # Penalize very short or very long sentences
            if 5 <= avg_length <= 25:
                length_score = 1.0
            elif avg_length < 5:
                length_score = 0.5
            else:
                length_score = 0.7

            # Check for sentence fragments (ending without punctuation)
            fragment_penalty = 0.1 if not content.endswith((".", "!", "?")) else 0.0

            # Check for repeated words (potential duplication)
            words = content.lower().split()
            unique_ratio = len(set(words)) / len(words) if words else 0
            repetition_score = min(1.0, unique_ratio * 1.2)

            # Combine scores
            coherence = length_score * 0.4 + repetition_score * 0.4 + (1.0 - fragment_penalty) * 0.2

            return min(1.0, max(0.0, coherence))
        except Exception as e:
            logger.error(f"Error checking coherence: {str(e)}")
            return 0.5  # Neutral default

    def _normalize_text(self, text: str) -> list[str]:
        """Normalize text and extract meaningful tokens.

        Args:
            text: Text to normalize

        Returns:
            List of normalized tokens
        """
        try:
            # Remove punctuation and split on whitespace
            tokens = re.findall(r"\b\w+\b", text.lower())

            # Filter out very short tokens and common stop words
            stop_words = {
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
                "may",
                "might",
                "can",
                "this",
                "that",
            }

            return [token for token in tokens if len(token) > 2 and token not in stop_words]
        except Exception as e:
            logger.error(f"Error normalizing text: {str(e)}")
            return []

    def batch_evaluate(
        self, documents: list[tuple[str, dict[str, str], str]], filter_failed: bool = True
    ) -> list[tuple[dict[str, str], QualityAssessment]]:
        """Evaluate multiple documents in batch.

        Args:
            documents: List of (content, metadata, query) tuples
            filter_failed: Whether to filter out failed assessments

        Returns:
            List of (metadata, assessment) tuples
        """
        try:
            results = []

            for idx, (content, metadata, query) in enumerate(documents):
                doc_id = metadata.get("doc_id") or metadata.get("id") or str(idx)
                assessment = self.evaluate_signal(content, metadata, query, doc_id)

                if not filter_failed or assessment.is_pass:
                    results.append((metadata, assessment))

            logger.info(f"Batch evaluation: {len(documents)} input, {len(results)} passed")
            return results
        except Exception as e:
            logger.error(f"Error in batch evaluation: {str(e)}")
            return []


# Factory function for easy instantiation
def create_quality_pipeline(
    relevance_threshold: float = 0.3,
    authority_threshold: float = 0.4,
    specificity_threshold: float = 0.5,
    strict_mode: bool = False,
) -> SignalQualityPipeline:
    """Create a SignalQualityPipeline instance.

    Args:
        relevance_threshold: Minimum relevance score
        authority_threshold: Minimum authority score
        specificity_threshold: Minimum specificity score
        strict_mode: If True, use stricter thresholds

    Returns:
        Configured SignalQualityPipeline instance
    """
    if strict_mode:
        return SignalQualityPipeline(
            relevance_threshold=0.4,
            authority_threshold=0.6,
            specificity_threshold=0.7,
            enable_coherence_check=True,
        )

    return SignalQualityPipeline(
        relevance_threshold=relevance_threshold,
        authority_threshold=authority_threshold,
        specificity_threshold=specificity_threshold,
    )


# Convenience function for quick filtering
def filter_high_quality_signals(
    documents: list[tuple[str, dict[str, str], str]], strict_mode: bool = False
) -> list[dict[str, str]]:
    """Quickly filter documents for high-quality signals.

    Args:
        documents: List of (content, metadata, query) tuples
        strict_mode: Whether to use strict filtering

    Returns:
        List of metadata for documents that passed quality checks
    """
    pipeline = create_quality_pipeline(strict_mode=strict_mode)
    results = pipeline.batch_evaluate(documents, filter_failed=True)
    return [metadata for metadata, _ in results]
