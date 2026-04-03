"""
Advanced C0 Feature Extractor

Extracts enhanced features for C0 advanced reranking model including
semantic embeddings, attention patterns, document relevance,
and retrieval optimization signals.
"""

import math
from datetime import datetime
from typing import Dict, Any

from .base_extractor import DeterministicFeatureExtractor
from ..config.feature_schemas import FeatureSchemas, FeatureSchema


class AdvancedC0FeatureExtractor(DeterministicFeatureExtractor):
    """
    Advanced feature extractor for C0 transformer reranking.

    Extracts enhanced deterministic features for advanced reranking:
    - Semantic embeddings and similarity calculations
    - Attention patterns and relevance signals
    - Document authority and quality metrics
    - Retrieval performance and optimization indicators
    - User interaction patterns and engagement signals
    - Contextual relevance and temporal factors
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("advanced_c0_reranker")
        if not schema:
            # Create schema for advanced C0 reranker
            schema = self._create_advanced_c0_schema()
        super().__init__(schema)

    def _create_advanced_c0_schema(self) -> FeatureSchema:
        """Create feature schema for advanced C0 reranker."""
        from ..config.feature_schemas import FeatureSchema, FeatureDefinition, FeatureType

        features = [
            FeatureDefinition(
                name="embedding_similarity",
                feature_type=FeatureType.NUMERIC,
                description="Embedding similarity between query and document",
                provenance="reranking.embedding.similarity",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="attention_score",
                feature_type=FeatureType.NUMERIC,
                description="Attention-based relevance score",
                provenance="reranking.attention.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="document_authority",
                feature_type=FeatureType.NUMERIC,
                description="Authority score of the document source",
                provenance="reranking.document.authority",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="relevance_confidence",
                feature_type=FeatureType.NUMERIC,
                description="Confidence in document relevance",
                provenance="reranking.relevance.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="user_engagement",
                feature_type=FeatureType.NUMERIC,
                description="Historical user engagement with similar documents",
                provenance="reranking.user.engagement",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="temporal_relevance",
                feature_type=FeatureType.NUMERIC,
                description="Temporal relevance of the document",
                provenance="reranking.temporal.relevance",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="semantic_density",
                feature_type=FeatureType.NUMERIC,
                description="Semantic density of the document content",
                provenance="reranking.semantic.density",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="retrieval_precision",
                feature_type=FeatureType.NUMERIC,
                description="Precision of retrieval for this document type",
                provenance="reranking.retrieval.precision",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="context_alignment",
                feature_type=FeatureType.NUMERIC,
                description="Alignment with current context",
                provenance="reranking.context.alignment",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="reranking_confidence",
                feature_type=FeatureType.NUMERIC,
                description="Overall confidence in reranking decision",
                provenance="reranking.overall.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="advanced_c0_reranker",
            schema_version="1.0",
            description="Enhanced features for C0 transformer reranking model",
            features=features
        )

    def _register_extraction_functions(self) -> None:
        """Register advanced C0-specific feature extraction functions."""
        self.register_extraction_function("embedding_similarity", self._extract_embedding_similarity)
        self.register_extraction_function("attention_score", self._extract_attention_score)
        self.register_extraction_function("document_authority", self._extract_document_authority)
        self.register_extraction_function("relevance_confidence", self._extract_relevance_confidence)
        self.register_extraction_function("user_engagement", self._extract_user_engagement)
        self.register_extraction_function("temporal_relevance", self._extract_temporal_relevance)
        self.register_extraction_function("semantic_density", self._extract_semantic_density)
        self.register_extraction_function("retrieval_precision", self._extract_retrieval_precision)
        self.register_extraction_function("context_alignment", self._extract_context_alignment)
        self.register_extraction_function("reranking_confidence", self._extract_reranking_confidence)

    def _extract_embedding_similarity(self, context: Dict[str, Any]) -> float:
        """Extract embedding similarity (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct embedding similarity if provided
        if "embedding_similarity" in reranking:
            return float(reranking["embedding_similarity"])

        # Calculate from query and document embeddings
        query_embedding = reranking.get("query_embedding", [])
        document_embedding = reranking.get("document_embedding", [])

        if not query_embedding or not document_embedding:
            return 0.5  # Default if no embeddings

        if len(query_embedding) != len(document_embedding):
            return 0.5  # Incompatible embeddings

        # Cosine similarity
        dot_product = sum(q * d for q, d in zip(query_embedding, document_embedding))
        query_norm = math.sqrt(sum(q * q for q in query_embedding))
        doc_norm = math.sqrt(sum(d * d for d in document_embedding))

        if query_norm > 0 and doc_norm > 0:
            similarity = dot_product / (query_norm * doc_norm)
        else:
            similarity = 0.0

        return round(max(0.0, min(1.0, similarity)), 3)

    def _extract_attention_score(self, context: Dict[str, Any]) -> float:
        """Extract attention-based relevance score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct attention score if provided
        if "attention_score" in reranking:
            return float(reranking["attention_score"])

        # Calculate from attention weights
        attention_weights = reranking.get("attention_weights", [])

        if not attention_weights:
            return 0.5  # Default if no attention weights

        # Average attention weight as score
        avg_attention = sum(attention_weights) / len(attention_weights)

        # Normalize to 0-1 range
        normalized_attention = min(1.0, avg_attention)

        return round(max(0.0, normalized_attention), 3)

    def _extract_document_authority(self, context: Dict[str, Any]) -> float:
        """Extract document authority score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct document authority if provided
        if "document_authority" in reranking:
            return float(reranking["document_authority"])

        # Calculate from document metadata
        document_metadata = reranking.get("document_metadata", {})

        if not document_metadata:
            return 0.5  # Default if no metadata

        authority_factors = {
            "source_reliability": 0.3,
            "citation_count": 0.25,
            "peer_reviewed": 0.2,
            "publication_quality": 0.15,
            "author_reputation": 0.1
        }

        authority_score = 0.0

        # Source reliability
        source_reliability = document_metadata.get("source_reliability", 0.5)
        authority_score += authority_factors["source_reliability"] * source_reliability

        # Citation count (normalized)
        citation_count = document_metadata.get("citation_count", 0)
        citation_score = min(1.0, math.log(max(1, citation_count)) / 10)  # Log scale, normalize to 10
        authority_score += authority_factors["citation_count"] * citation_score

        # Peer reviewed
        peer_reviewed = document_metadata.get("peer_reviewed", False)
        peer_score = 1.0 if peer_reviewed else 0.5
        authority_score += authority_factors["peer_reviewed"] * peer_score

        # Publication quality
        publication_quality = document_metadata.get("publication_quality", 0.5)
        authority_score += authority_factors["publication_quality"] * publication_quality

        # Author reputation
        author_reputation = document_metadata.get("author_reputation", 0.5)
        authority_score += authority_factors["author_reputation"] * author_reputation

        return round(max(0.0, min(1.0, authority_score)), 3)

    def _extract_relevance_confidence(self, context: Dict[str, Any]) -> float:
        """Extract relevance confidence (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct relevance confidence if provided
        if "relevance_confidence" in reranking:
            return float(reranking["relevance_confidence"])

        # Calculate from relevance signals
        relevance_signals = reranking.get("relevance_signals", {})

        if not relevance_signals:
            return 0.5  # Default if no relevance signals

        confidence_factors = {
            "keyword_match": 0.3,
            "semantic_match": 0.25,
            "topic_relevance": 0.2,
            "query_coverage": 0.15,
            "answer_completeness": 0.1
        }

        confidence_score = 0.0

        # Keyword match
        keyword_match = relevance_signals.get("keyword_match", 0.5)
        confidence_score += confidence_factors["keyword_match"] * keyword_match

        # Semantic match
        semantic_match = relevance_signals.get("semantic_match", 0.5)
        confidence_score += confidence_factors["semantic_match"] * semantic_match

        # Topic relevance
        topic_relevance = relevance_signals.get("topic_relevance", 0.5)
        confidence_score += confidence_factors["topic_relevance"] * topic_relevance

        # Query coverage
        query_coverage = relevance_signals.get("query_coverage", 0.5)
        confidence_score += confidence_factors["query_coverage"] * query_coverage

        # Answer completeness
        answer_completeness = relevance_signals.get("answer_completeness", 0.5)
        confidence_score += confidence_factors["answer_completeness"] * answer_completeness

        return round(max(0.0, min(1.0, confidence_score)), 3)

    def _extract_user_engagement(self, context: Dict[str, Any]) -> float:
        """Extract user engagement score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct user engagement if provided
        if "user_engagement" in reranking:
            return float(reranking["user_engagement"])

        # Calculate from user interaction data
        user_data = reranking.get("user_data", {})

        if not user_data:
            return 0.5  # Default if no user data

        engagement_factors = {
            "click_through_rate": 0.3,
            "dwell_time": 0.25,
            "user_ratings": 0.2,
            "share_frequency": 0.15,
            "bookmark_rate": 0.1
        }

        engagement_score = 0.0

        # Click through rate
        ctr = user_data.get("click_through_rate", 0.5)
        engagement_score += engagement_factors["click_through_rate"] * ctr

        # Dwell time (normalized)
        dwell_time = user_data.get("dwell_time", 60)  # seconds
        dwell_score = min(1.0, dwell_time / 300)  # Normalize to 5 minutes
        engagement_score += engagement_factors["dwell_time"] * dwell_score

        # User ratings
        user_ratings = user_data.get("user_ratings", 3.0)  # 1-5 scale
        rating_score = user_ratings / 5.0
        engagement_score += engagement_factors["user_ratings"] * rating_score

        # Share frequency
        share_frequency = user_data.get("share_frequency", 0.5)
        engagement_score += engagement_factors["share_frequency"] * share_frequency

        # Bookmark rate
        bookmark_rate = user_data.get("bookmark_rate", 0.5)
        engagement_score += engagement_factors["bookmark_rate"] * bookmark_rate

        return round(max(0.0, min(1.0, engagement_score)), 3)

    def _extract_temporal_relevance(self, context: Dict[str, Any]) -> float:
        """Extract temporal relevance score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct temporal relevance if provided
        if "temporal_relevance" in reranking:
            return float(reranking["temporal_relevance"])

        # Calculate from temporal factors
        temporal_data = reranking.get("temporal_data", {})

        if not temporal_data:
            return 0.5  # Default if no temporal data

        temporal_factors = {
            "recency": 0.4,
            "seasonality": 0.3,
            "trend_alignment": 0.2,
            "time_sensitivity": 0.1
        }

        temporal_score = 0.0

        # Recency
        document_date = temporal_data.get("document_date")
        if document_date:
            try:
                doc_datetime = datetime.fromisoformat(document_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - doc_datetime).days
                recency_score = max(0.0, 1.0 - (days_old / 365))  # Decay over 1 year
            except:
                recency_score = 0.5
        else:
            recency_score = 0.5

        temporal_score += temporal_factors["recency"] * recency_score

        # Seasonality
        seasonality = temporal_data.get("seasonality", 0.5)
        temporal_score += temporal_factors["seasonality"] * seasonality

        # Trend alignment
        trend_alignment = temporal_data.get("trend_alignment", 0.5)
        temporal_score += temporal_factors["trend_alignment"] * trend_alignment

        # Time sensitivity
        time_sensitivity = temporal_data.get("time_sensitivity", 0.5)
        temporal_score += temporal_factors["time_sensitivity"] * time_sensitivity

        return round(max(0.0, min(1.0, temporal_score)), 3)

    def _extract_semantic_density(self, context: Dict[str, Any]) -> float:
        """Extract semantic density score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct semantic density if provided
        if "semantic_density" in reranking:
            return float(reranking["semantic_density"])

        # Calculate from content analysis
        content_analysis = reranking.get("content_analysis", {})

        if not content_analysis:
            return 0.5  # Default if no content analysis

        density_factors = {
            "information_density": 0.3,
            "concept_coverage": 0.25,
            "semantic_coherence": 0.2,
            "topic_depth": 0.15,
            "answer_specificity": 0.1
        }

        density_score = 0.0

        # Information density
        info_density = content_analysis.get("information_density", 0.5)
        density_score += density_factors["information_density"] * info_density

        # Concept coverage
        concept_coverage = content_analysis.get("concept_coverage", 0.5)
        density_score += density_factors["concept_coverage"] * concept_coverage

        # Semantic coherence
        semantic_coherence = content_analysis.get("semantic_coherence", 0.5)
        density_score += density_factors["semantic_coherence"] * semantic_coherence

        # Topic depth
        topic_depth = content_analysis.get("topic_depth", 0.5)
        density_score += density_factors["topic_depth"] * topic_depth

        # Answer specificity
        answer_specificity = content_analysis.get("answer_specificity", 0.5)
        density_score += density_factors["answer_specificity"] * answer_specificity

        return round(max(0.0, min(1.0, density_score)), 3)

    def _extract_retrieval_precision(self, context: Dict[str, Any]) -> float:
        """Extract retrieval precision score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct retrieval precision if provided
        if "retrieval_precision" in reranking:
            return float(reranking["retrieval_precision"])

        # Calculate from retrieval performance data
        retrieval_data = reranking.get("retrieval_data", {})

        if not retrieval_data:
            return 0.5  # Default if no retrieval data

        # Historical precision for similar documents
        historical_precision = retrieval_data.get("historical_precision", 0.5)

        # Current retrieval score
        retrieval_score = retrieval_data.get("retrieval_score", 0.5)

        # Precision factors
        precision_factors = {
            "historical": 0.6,
            "current": 0.4
        }

        precision_score = (
            precision_factors["historical"] * historical_precision +
            precision_factors["current"] * retrieval_score
        )

        return round(max(0.0, min(1.0, precision_score)), 3)

    def _extract_context_alignment(self, context: Dict[str, Any]) -> float:
        """Extract context alignment score (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct context alignment if provided
        if "context_alignment" in reranking:
            return float(reranking["context_alignment"])

        # Calculate from context factors
        context_factors = reranking.get("context_factors", {})

        if not context_factors:
            return 0.5  # Default if no context factors

        alignment_indicators = {
            "session_context": 0.3,
            "user_preferences": 0.25,
            "domain_relevance": 0.2,
            "task_alignment": 0.15,
            "environmental_fit": 0.1
        }

        alignment_score = 0.0

        # Session context
        session_context = context_factors.get("session_context", 0.5)
        alignment_score += alignment_indicators["session_context"] * session_context

        # User preferences
        user_preferences = context_factors.get("user_preferences", 0.5)
        alignment_score += alignment_indicators["user_preferences"] * user_preferences

        # Domain relevance
        domain_relevance = context_factors.get("domain_relevance", 0.5)
        alignment_score += alignment_indicators["domain_relevance"] * domain_relevance

        # Task alignment
        task_alignment = context_factors.get("task_alignment", 0.5)
        alignment_score += alignment_indicators["task_alignment"] * task_alignment

        # Environmental fit
        environmental_fit = context_factors.get("environmental_fit", 0.5)
        alignment_score += alignment_indicators["environmental_fit"] * environmental_fit

        return round(max(0.0, min(1.0, alignment_score)), 3)

    def _extract_reranking_confidence(self, context: Dict[str, Any]) -> float:
        """Extract overall reranking confidence (0.0 to 1.0)."""
        reranking = context.get("reranking", {})

        # Direct reranking confidence if provided
        if "reranking_confidence" in reranking:
            return float(reranking["reranking_confidence"])

        # Calculate from individual confidence factors
        confidence_factors = {
            "embedding_similarity": 0.2,
            "attention_score": 0.15,
            "document_authority": 0.15,
            "relevance_confidence": 0.15,
            "user_engagement": 0.1,
            "temporal_relevance": 0.1,
            "semantic_density": 0.05,
            "retrieval_precision": 0.05,
            "context_alignment": 0.05
        }

        # Extract individual confidences
        embedding_confidence = self._extract_embedding_similarity(context)
        attention_confidence = self._extract_attention_score(context)
        authority_confidence = self._extract_document_authority(context)
        relevance_confidence = self._extract_relevance_confidence(context)
        engagement_confidence = self._extract_user_engagement(context)
        temporal_confidence = self._extract_temporal_relevance(context)
        density_confidence = self._extract_semantic_density(context)
        precision_confidence = self._extract_retrieval_precision(context)
        alignment_confidence = self._extract_context_alignment(context)

        # Weighted combination
        reranking_confidence = (
            confidence_factors["embedding_similarity"] * embedding_confidence +
            confidence_factors["attention_score"] * attention_confidence +
            confidence_factors["document_authority"] * authority_confidence +
            confidence_factors["relevance_confidence"] * relevance_confidence +
            confidence_factors["user_engagement"] * engagement_confidence +
            confidence_factors["temporal_relevance"] * temporal_confidence +
            confidence_factors["semantic_density"] * density_confidence +
            confidence_factors["retrieval_precision"] * precision_confidence +
            confidence_factors["context_alignment"] * alignment_confidence
        )

        return round(max(0.0, min(1.0, reranking_confidence)), 3)
