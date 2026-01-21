"""Evidence Ranker - Freshness and Corroboration-Based Evidence Ranking.

This module provides a post-retrieval ranking layer that prioritizes fresh (recent)
and corroborated (multi-source) evidence over older or isolated claims, ensuring
the Resume Engine cites the most current and verified truth.
"""

import logging
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, confloat, validator

logger = logging.getLogger(__name__)


class RankedEvidence(BaseModel):
    """Ranked evidence with freshness and corroboration metrics."""

    content: str = Field(..., description="Document content")
    final_score: confloat(ge=0.0, le=1.0) = Field(..., description="Final ranking score")
    freshness_score: confloat(ge=0.0, le=1.0) = Field(..., description="Freshness score")
    corroboration_count: int = Field(..., ge=0, description="Number of corroborating sources")
    year_detected: int | None = Field(None, description="Year extracted from content")
    semantic_score: confloat(ge=0.0, le=1.0) = Field(..., description="Original semantic score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    key_entities: list[str] = Field(default_factory=list, description="Corroborated entities")
    doc_id: str | None = Field(None, description="Document identifier for logging")

    @validator("year_detected")
    def validate_year(cls, v):
        """Validate year is within reasonable range."""
        if v is not None:
            current_year = datetime.now().year
            if v < 2000 or v > current_year + 1:
                logger.warning(f"Suspicious year detected: {v}")
                return None
        return v

    @property
    def is_recent(self) -> bool:
        """Check if evidence is from the last 2 years."""
        if self.year_detected is None:
            return False
        current_year = datetime.now().year
        return current_year - self.year_detected <= 2

    @property
    def is_corroborated(self) -> bool:
        """Check if evidence has multiple sources."""
        return self.corroboration_count >= 2


class EvidenceRanker:
    """Evidence ranker that prioritizes fresh and corroborated content.

    This ranker re-shuffles passed signals based on freshness and corroboration
    to ensure the most current and verified evidence is ranked highest.
    """

    def __init__(
        self,
        freshness_weight: float = 0.4,
        corroboration_weight: float = 0.2,
        semantic_weight: float = 0.4,
        current_year: int | None = None,
    ):
        """Initialize the evidence ranker.

        Args:
            freshness_weight: Weight for freshness in final score
            corroboration_weight: Weight for corroboration in final score
            semantic_weight: Weight for original semantic score
            current_year: Reference year for freshness calculation
        """
        self.freshness_weight = freshness_weight
        self.corroboration_weight = corroboration_weight
        self.semantic_weight = semantic_weight
        self.current_year = current_year or datetime.now().year

        # Normalize weights
        total_weight = freshness_weight + corroboration_weight + semantic_weight
        if total_weight != 1.0:
            self.freshness_weight /= total_weight
            self.corroboration_weight /= total_weight
            self.semantic_weight /= total_weight

        # Year extraction patterns
        self.year_patterns = [
            r"\b(20[2-3][0-9])\b",  # 2020-2039
            r"\b([2-3][0-9]{3})\b",  # 2000-3999 (broader)
        ]

        # Entity extraction patterns
        self.entity_patterns = [
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",  # Capitalized phrases
            r"\b([A-Z]{2,})\b",  # Acronyms
            r"\$[\d,]+(?:\.\d+)?[kmb]?",  # Money values
            r"\b\d+(?:,\d{3})*(?:\.\d+)?%\b",  # Percentages
        ]

        logger.info(
            f"Initialized EvidenceRanker with weights: "
            f"freshness={self.freshness_weight:.2f}, "
            f"corroboration={self.corroboration_weight:.2f}, "
            f"semantic={self.semantic_weight:.2f}"
        )

    def rank_evidence(
        self, signals: list[dict[str, Any]], current_year: int | None = None
    ) -> list[RankedEvidence]:
        """Rank evidence based on freshness and corroboration.

        Args:
            signals: List of signal dictionaries with 'content', 'score', and 'metadata'
            current_year: Override current year for freshness calculation

        Returns:
            List of RankedEvidence sorted by final_score descending
        """
        try:
            if current_year:
                self.current_year = current_year

            # Validate input
            if not signals or not isinstance(signals, list):
                logger.warning("Invalid or empty signals list")
                return []

            # Extract entities from all signals for corroboration checking
            all_entities = self._extract_all_entities(signals)

            # Calculate scores for each signal
            ranked_signals = []

            for idx, signal in enumerate(signals):
                try:
                    # Extract signal data with defaults
                    content = signal.get("content", "")
                    semantic_score = float(signal.get("score", 0.0))
                    metadata = signal.get("metadata", {})
                    doc_id = signal.get("doc_id") or signal.get("id") or str(idx)

                    # Validate inputs
                    if not isinstance(content, str):
                        logger.warning(f"Invalid content type for doc {doc_id}: {type(content)}")
                        continue

                    if not 0.0 <= semantic_score <= 1.0:
                        logger.warning(
                            f"Semantic score out of bounds for doc {doc_id}: {semantic_score}"
                        )
                        semantic_score = max(0.0, min(1.0, semantic_score))

                    # Calculate freshness score
                    freshness_score, year_detected = self._score_freshness(content, metadata)

                    # Calculate corroboration count
                    corroboration_count, key_entities = self._count_corroboration(
                        content, all_entities, signals
                    )

                    # Calculate final score
                    corroboration_normalized = min(
                        1.0, corroboration_count / 3.0
                    )  # Normalize to 0-1
                    final_score = (
                        semantic_score * self.semantic_weight
                        + freshness_score * self.freshness_weight
                        + corroboration_normalized * self.corroboration_weight
                    )

                    # Create ranked evidence
                    ranked = RankedEvidence(
                        content=content,
                        final_score=final_score,
                        freshness_score=freshness_score,
                        corroboration_count=corroboration_count,
                        year_detected=year_detected,
                        semantic_score=semantic_score,
                        metadata=metadata if isinstance(metadata, dict) else {},
                        key_entities=key_entities,
                        doc_id=doc_id,
                    )

                    ranked_signals.append(ranked)

                    logger.debug(
                        f"Ranked signal {doc_id}: final={final_score:.3f}, "
                        f"semantic={semantic_score:.3f}, "
                        f"freshness={freshness_score:.3f}, "
                        f"corroboration={corroboration_count}",
                        extra={"doc_id": doc_id, "final_score": final_score},
                    )

                except Exception as e:
                    logger.error(f"Error processing signal at index {idx}: {str(e)}")
                    continue

            # Sort by final score descending
            ranked_signals.sort(key=lambda x: x.final_score, reverse=True)

            logger.info(
                f"Ranked {len(signals)} signals, top score: {ranked_signals[0].final_score:.3f if ranked_signals else 0:.3f}"
            )
            return ranked_signals

        except Exception as e:
            logger.error(f"Error in rank_evidence: {str(e)}")
            return []

    def _score_freshness(self, content: str, metadata: dict[str, str]) -> tuple[float, int | None]:
        """Score content based on freshness (recency).

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            Tuple of (freshness_score, detected_year)
        """
        try:
            # Try to extract year from content first
            year = self._extract_year(content)

            # If not found in content, check metadata
            if year is None:
                for key in ["date", "year", "timestamp", "created_at"]:
                    if key in metadata:
                        year = self._extract_year(str(metadata[key]))
                        if year:
                            break

            # If still no year found, return neutral score
            if year is None:
                return 0.5, None

            # Calculate freshness score based on year difference
            year_diff = self.current_year - year

            if year_diff < 0:
                # Future date - penalize heavily
                return 0.1, year
            elif year_diff == 0:
                # Current year - maximum freshness
                return 1.0, year
            elif year_diff == 1:
                # Last year - very fresh
                return 0.9, year
            elif year_diff == 2:
                # 2 years ago - fresh
                return 0.7, year
            elif year_diff == 3:
                # 3 years ago - somewhat fresh
                return 0.5, year
            elif year_diff == 4:
                # 4 years ago - getting stale
                return 0.3, year
            else:
                # 5+ years ago - stale
                return 0.2, year
        except Exception as e:
            logger.error(f"Error scoring freshness: {str(e)}")
            return 0.5, None

    def _extract_year(self, text: str) -> int | None:
        """Extract a 4-digit year from text.

        Args:
            text: Text to search for year

        Returns:
            Extracted year or None
        """
        try:
            for pattern in self.year_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        year = int(match)
                        # Validate reasonable year range
                        if 2020 <= year <= 2030:
                            return year
                    except ValueError:
                        continue
            return None
        except Exception as e:
            logger.error(f"Error extracting year: {str(e)}")
            return None

    def _count_corroboration(
        self, content: str, all_entities: dict[str, list[str]], all_signals: list[dict[str, Any]]
    ) -> tuple[int, list[str]]:
        """Count how many other signals corroborate this one.

        Args:
            content: Content to check for corroboration
            all_entities: Pre-extracted entities from all signals
            all_signals: All signals for overlap checking

        Returns:
            Tuple of (corroboration_count, key_entities_found)
        """
        try:
            # Extract entities from this signal
            entities = self._extract_entities(content)

            if not entities:
                return 0, []

            # Count corroboration for each entity
            corroboration_counts = {}
            for entity in entities:
                if entity in all_entities:
                    # Count how many other signals contain this entity
                    corroboration_counts[entity] = len(all_entities[entity])

            # Calculate total corroboration (sum of corroborating signals)
            total_corroboration = sum(
                count - 1 for count in corroboration_counts.values() if count > 1
            )

            # Identify key entities (those with corroboration)
            key_entities = [entity for entity, count in corroboration_counts.items() if count > 1]

            return total_corroboration, key_entities
        except Exception as e:
            logger.error(f"Error counting corroboration: {str(e)}")
            return 0, []

    def _extract_all_entities(self, signals: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Extract entities from all signals for corroboration checking.

        Args:
            signals: List of all signals

        Returns:
            Dictionary mapping entity to list of signal indices containing it
        """
        try:
            entity_map = {}

            for idx, signal in enumerate(signals):
                content = signal.get("content", "")
                if isinstance(content, str):
                    entities = self._extract_entities(content)

                    for entity in entities:
                        if entity not in entity_map:
                            entity_map[entity] = []
                        entity_map[entity].append(idx)

            return entity_map
        except Exception as e:
            logger.error(f"Error extracting all entities: {str(e)}")
            return {}

    def _extract_entities(self, content: str) -> list[str]:
        """Extract key entities from content.

        Args:
            content: Text to extract entities from

        Returns:
            List of extracted entities
        """
        try:
            entities = []

            # Extract using patterns
            for pattern in self.entity_patterns:
                matches = re.findall(pattern, content)
                entities.extend(matches)

            # Filter and normalize entities
            normalized_entities = []
            for entity in entities:
                # Skip very short or very long entities
                if len(entity) < 2 or len(entity) > 50:
                    continue

                # Skip common words
                common_words = {
                    "the",
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
                    "this",
                    "that",
                    "these",
                    "those",
                }

                if entity.lower() not in common_words:
                    normalized_entities.append(entity)

            # Remove duplicates while preserving order
            seen = set()
            unique_entities = []
            for entity in normalized_entities:
                if entity not in seen:
                    seen.add(entity)
                    unique_entities.append(entity)

            return unique_entities
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []

    def get_ranking_summary(self, ranked_evidence: list[RankedEvidence]) -> dict[str, Any]:
        """Get a summary of the ranking results.

        Args:
            ranked_evidence: List of ranked evidence

        Returns:
            Summary statistics
        """
        try:
            if not ranked_evidence:
                return {"total": 0}

            recent_count = sum(1 for e in ranked_evidence if e.is_recent)
            corroborated_count = sum(1 for e in ranked_evidence if e.is_corroborated)

            years_detected = [e.year_detected for e in ranked_evidence if e.year_detected]
            avg_year = sum(years_detected) / len(years_detected) if years_detected else None

            return {
                "total": len(ranked_evidence),
                "recent_count": recent_count,
                "corroborated_count": corroborated_count,
                "avg_freshness": sum(e.freshness_score for e in ranked_evidence)
                / len(ranked_evidence),
                "avg_corroboration": sum(e.corroboration_count for e in ranked_evidence)
                / len(ranked_evidence),
                "year_range": (min(years_detected), max(years_detected))
                if years_detected
                else None,
                "avg_year": avg_year,
                "top_score": ranked_evidence[0].final_score,
                "bottom_score": ranked_evidence[-1].final_score,
            }
        except Exception as e:
            logger.error(f"Error getting ranking summary: {str(e)}")
            return {"error": str(e)}


# Factory function for easy instantiation
def create_evidence_ranker(
    freshness_weight: float = 0.4,
    corroboration_weight: float = 0.2,
    semantic_weight: float = 0.4,
    current_year: int | None = None,
) -> EvidenceRanker:
    """Create an EvidenceRanker instance.

    Args:
        freshness_weight: Weight for freshness in scoring
        corroboration_weight: Weight for corroboration in scoring
        semantic_weight: Weight for semantic similarity in scoring
        current_year: Reference year for freshness

    Returns:
        Configured EvidenceRanker instance
    """
    return EvidenceRanker(
        freshness_weight=freshness_weight,
        corroboration_weight=corroboration_weight,
        semantic_weight=semantic_weight,
        current_year=current_year,
    )


# Convenience function for quick ranking
def rank_evidence(
    signals: list[dict[str, Any]],
    prioritize_freshness: bool = True,
    current_year: int | None = None,
) -> list[RankedEvidence]:
    """Quickly rank evidence by freshness and corroboration.

    Args:
        signals: List of signals to rank
        prioritize_freshness: Whether to emphasize freshness in ranking
        current_year: Reference year for freshness calculation

    Returns:
        List of ranked evidence
    """
    weights = (0.5, 0.2, 0.3) if prioritize_freshness else (0.4, 0.2, 0.4)

    ranker = create_evidence_ranker(
        freshness_weight=weights[0],
        corroboration_weight=weights[1],
        semantic_weight=weights[2],
        current_year=current_year,
    )

    return ranker.rank_evidence(signals)
