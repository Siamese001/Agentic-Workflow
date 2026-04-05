"""
C0 Feature Extractor

Extracts features for C0 retrieval reranking model including
query-document similarity, document authority, recency, usage frequency,
semantic density, source reliability, completeness, and cache metrics.
"""

import hashlib
import math
from datetime import datetime
from typing import Any

from ..config.feature_schemas import FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class C0FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for C0 retrieval reranking.

    Extracts deterministic features for document reranking:
    - Query-document similarity metrics
    - Document quality indicators (authority, recency, completeness)
    - Usage patterns (frequency, cache hits)
    - Semantic analysis (density, complexity)
    - Source reliability and trustworthiness
    - System performance metrics
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("c0_retrieval_reranker")
        if not schema:
            raise ValueError("C0 retrieval reranker schema not found")
        super().__init__(schema)

    def _register_extraction_functions(self) -> None:
        """Register C0-specific feature extraction functions."""
        self.register_extraction_function("query_doc_similarity", self._extract_query_doc_similarity)
        self.register_extraction_function("doc_authority_score", self._extract_doc_authority_score)
        self.register_extraction_function("recency_score", self._extract_recency_score)
        self.register_extraction_function("usage_frequency", self._extract_usage_frequency)
        self.register_extraction_function("semantic_density", self._extract_semantic_density)
        self.register_extraction_function("source_reliability", self._extract_source_reliability)
        self.register_extraction_function("completeness_score", self._extract_completeness_score)
        self.register_extraction_function("query_complexity", self._extract_query_complexity)
        self.register_extraction_function("cache_hit_probability", self._extract_cache_hit_probability)

    def _extract_query_doc_similarity(self, context: dict[str, Any]) -> float:
        """Extract query-document similarity score (0.0-1.0)."""
        query = context.get("query", {})
        document = context.get("document", {})

        # Direct similarity score
        if "similarity_score" in context:
            return float(context["similarity_score"])

        # Calculate from embeddings if available
        query_embedding = query.get("embedding")
        doc_embedding = document.get("embedding")

        if query_embedding and doc_embedding and len(query_embedding) == len(doc_embedding):
            # Cosine similarity
            dot_product = sum(q * d for q, d in zip(query_embedding, doc_embedding))
            query_norm = math.sqrt(sum(q * q for q in query_embedding))
            doc_norm = math.sqrt(sum(d * d for d in doc_embedding))

            if query_norm > 0 and doc_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
                return round(max(0.0, min(1.0, similarity)), 3)

        # Text-based similarity as fallback
        query_text = query.get("text", "").lower()
        doc_text = document.get("text", "").lower()

        if not query_text or not doc_text:
            return 0.0

        # Simple Jaccard similarity
        query_words = set(query_text.split())
        doc_words = set(doc_text.split())

        intersection = len(query_words & doc_words)
        union = len(query_words | doc_words)

        similarity = intersection / union if union > 0 else 0.0
        return round(similarity, 3)

    def _extract_doc_authority_score(self, context: dict[str, Any]) -> float:
        """Extract document authority score (0.0-1.0)."""
        document = context.get("document", {})

        # Direct authority score
        if "authority_score" in document:
            return float(document["authority_score"])

        # Calculate from authority indicators
        authority_indicators = {
            "citation_count": 0.3,
            "reference_count": 0.2,
            "expert_reviewed": 0.25,
            "peer_reviewed": 0.3,
            "official_source": 0.4,
            "version": 0.1
        }

        score = 0.0

        # Citation count (logarithmic scaling)
        citation_count = document.get("citation_count", 0)
        if citation_count > 0:
            score += authority_indicators["citation_count"] * (1.0 - 1.0 / (1.0 + math.log10(max(1, citation_count))))

        # Reference count
        reference_count = document.get("reference_count", 0)
        if reference_count > 0:
            score += authority_indicators["reference_count"] * min(1.0, reference_count / 100.0)

        # Review status
        if document.get("expert_reviewed", False):
            score += authority_indicators["expert_reviewed"]

        if document.get("peer_reviewed", False):
            score += authority_indicators["peer_reviewed"]

        # Source type
        source_type = document.get("source_type", "").lower()
        if source_type in ["official", "government", "academic"]:
            score += authority_indicators["official_source"]

        # Version (newer versions get higher authority)
        version = document.get("version", 1)
        if version > 1:
            score += authority_indicators["version"] * min(1.0, (version - 1) / 10.0)

        return round(min(1.0, score), 3)

    def _extract_recency_score(self, context: dict[str, Any]) -> float:
        """Extract document recency score (0.0-1.0)."""
        document = context.get("document", {})

        # Direct recency score
        if "recency_score" in document:
            return float(document["recency_score"])

        # Calculate from creation/update dates
        now = datetime.now()

        # Try different date fields
        date_fields = ["updated_at", "created_at", "publication_date", "date"]
        doc_date = None

        for field in date_fields:
            if field in document:
                date_value = document[field]
                if isinstance(date_value, str):
                    try:
                        doc_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        break
                    except ValueError:
                        continue
                elif isinstance(date_value, datetime):
                    doc_date = date_value
                    break

        if not doc_date:
            return 0.5  # Default if no date information

        # Calculate recency based on domain-specific rules
        domain = context.get("domain", "general")

        if domain == "technology":
            # Tech docs decay faster (6 months)
            decay_days = 180
        elif domain == "academic":
            # Academic docs have longer relevance (2 years)
            decay_days = 730
        elif domain == "news":
            # News decays very fast (7 days)
            decay_days = 7
        else:
            # General documents (1 year)
            decay_days = 365

        # Calculate recency score using exponential decay
        days_old = (now - doc_date).days
        recency_score = math.exp(-days_old / decay_days)

        return round(max(0.0, min(1.0, recency_score)), 3)

    def _extract_usage_frequency(self, context: dict[str, Any]) -> float:
        """Extract historical usage frequency (0.0-1000.0)."""
        document = context.get("document", {})
        usage_stats = document.get("usage_stats", {})

        # Direct usage frequency
        if "frequency" in usage_stats:
            return float(usage_stats["frequency"])

        # Calculate from usage metrics
        total_uses = usage_stats.get("total_uses", 0)
        recent_uses = usage_stats.get("recent_uses", 0)  # Last 30 days
        monthly_uses = usage_stats.get("monthly_uses", 0)

        # Weight recent usage more heavily
        weighted_frequency = (recent_uses * 3.0) + (monthly_uses * 1.0) + (total_uses * 0.1)

        # Apply logarithmic scaling to handle wide range
        if weighted_frequency > 0:
            scaled_frequency = math.log10(max(1, weighted_frequency)) * 100
        else:
            scaled_frequency = 0.0

        return round(min(1000.0, scaled_frequency), 3)

    def _extract_semantic_density(self, context: dict[str, Any]) -> float:
        """Extract semantic density score (0.0-1.0)."""
        document = context.get("document", {})

        # Direct semantic density
        if "semantic_density" in document:
            return float(document["semantic_density"])

        # Calculate from document characteristics
        text = document.get("text", "")
        if not text:
            return 0.0

        # Calculate semantic density indicators
        word_count = len(text.split())
        unique_words = len(set(text.lower().split()))

        # Domain-specific terms
        domain_terms = context.get("domain_terms", [])
        domain_term_count = sum(1 for term in domain_terms if term.lower() in text.lower())

        # Technical complexity indicators
        technical_indicators = ["algorithm", "method", "analysis", "implementation", "architecture"]
        tech_count = sum(1 for indicator in technical_indicators if indicator.lower() in text.lower())

        # Calculate density metrics
        lexical_diversity = unique_words / max(1, word_count)  # Type-token ratio
        domain_density = domain_term_count / max(1, word_count)
        technical_density = tech_count / max(1, word_count)

        # Combine metrics with weights
        density_score = (
            lexical_diversity * 0.3 +
            domain_density * 0.4 +
            technical_density * 0.3
        )

        # Normalize to 0-1 range
        density_score = min(1.0, density_score * 2.0)  # Scale up since typical values are low

        return round(max(0.0, density_score), 3)

    def _extract_source_reliability(self, context: dict[str, Any]) -> float:
        """Extract source reliability score (0.0-1.0)."""
        document = context.get("document", {})
        source = document.get("source", {})

        # Direct reliability score
        if "reliability_score" in source:
            return float(source["reliability_score"])

        # Calculate from source characteristics
        reliability_score = 0.5  # Base score

        # Source type reliability
        source_type = source.get("type", "").lower()
        source_reliability = {
            "peer_reviewed": 0.9,
            "academic": 0.85,
            "official": 0.8,
            "government": 0.8,
            "reputable": 0.7,
            "commercial": 0.6,
            "blog": 0.4,
            "forum": 0.3,
            "social": 0.2,
            "unknown": 0.3
        }

        reliability_score = source_reliability.get(source_type, 0.5)

        # Adjust based on verification status
        if source.get("verified", False):
            reliability_score += 0.1

        # Adjust based on fact-checking
        if source.get("fact_checked", False):
            reliability_score += 0.1

        # Penalty for retracted content
        if source.get("retracted", False):
            reliability_score -= 0.5

        # Penalty for disputed content
        if source.get("disputed", False):
            reliability_score -= 0.2

        return round(max(0.0, min(1.0, reliability_score)), 3)

    def _extract_completeness_score(self, context: dict[str, Any]) -> float:
        """Extract document completeness score (0.0-1.0)."""
        document = context.get("document", {})

        # Direct completeness score
        if "completeness_score" in document:
            return float(document["completeness_score"])

        # Calculate from document structure
        text = document.get("text", "")
        if not text:
            return 0.0

        completeness_indicators = {
            "has_abstract": 0.1,
            "has_introduction": 0.1,
            "has_methodology": 0.15,
            "has_results": 0.15,
            "has_conclusion": 0.1,
            "has_references": 0.1,
            "word_count": 0.2,
            "structure_score": 0.1
        }

        score = 0.0

        # Check for document sections
        sections = document.get("sections", [])
        section_types = {section.get("type", "").lower() for section in sections}

        if "abstract" in section_types or document.get("abstract"):
            score += completeness_indicators["has_abstract"]

        if "introduction" in section_types:
            score += completeness_indicators["has_introduction"]

        if "methodology" in section_types or "methods" in section_types:
            score += completeness_indicators["has_methodology"]

        if "results" in section_types:
            score += completeness_indicators["has_results"]

        if "conclusion" in section_types:
            score += completeness_indicators["has_conclusion"]

        if document.get("references") or "references" in section_types:
            score += completeness_indicators["has_references"]

        # Word count contribution (logarithmic scaling)
        word_count = len(text.split())
        if word_count > 0:
            word_score = min(1.0, math.log10(max(100, word_count)) / math.log10(10000))
            score += completeness_indicators["word_count"] * word_score

        # Structure score based on section organization
        if len(sections) > 0:
            structure_score = min(1.0, len(sections) / 10.0)
            score += completeness_indicators["structure_score"] * structure_score

        return round(min(1.0, score), 3)

    def _extract_query_complexity(self, context: dict[str, Any]) -> float:
        """Extract query complexity score (0.0-1.0)."""
        query = context.get("query", {})

        # Direct complexity score
        if "complexity_score" in query:
            return float(query["complexity_score"])

        # Calculate from query characteristics
        query_text = query.get("text", "")
        if not query_text:
            return 0.0

        complexity_indicators = {
            "word_count": 0.2,
            "unique_terms": 0.2,
            "technical_terms": 0.2,
            "query_length": 0.1,
            "nested_queries": 0.15,
            "boolean_operators": 0.15
        }

        score = 0.0

        # Word count
        word_count = len(query_text.split())
        word_score = min(1.0, word_count / 50.0)  # Normalize to 50 words as max
        score += complexity_indicators["word_count"] * word_score

        # Unique terms ratio
        words = query_text.lower().split()
        unique_words = set(words)
        unique_ratio = len(unique_words) / max(1, len(words))
        score += complexity_indicators["unique_terms"] * unique_ratio

        # Technical terms
        technical_terms = context.get("technical_terms", [])
        tech_count = sum(1 for term in technical_terms if term.lower() in query_text.lower())
        tech_score = min(1.0, tech_count / 10.0)  # Normalize to 10 technical terms
        score += complexity_indicators["technical_terms"] * tech_score

        # Query length (character count)
        length_score = min(1.0, len(query_text) / 500.0)  # Normalize to 500 chars
        score += complexity_indicators["query_length"] * length_score

        # Nested queries (parentheses, quotes)
        nested_count = query_text.count('(') + query_text.count('"')
        nested_score = min(1.0, nested_count / 5.0)  # Normalize to 5 nested elements
        score += complexity_indicators["nested_queries"] * nested_score

        # Boolean operators
        boolean_operators = ["and", "or", "not", "near", "within"]
        bool_count = sum(1 for op in boolean_operators if f" {op} " in f" {query_text.lower()} ")
        bool_score = min(1.0, bool_count / 3.0)  # Normalize to 3 boolean operators
        score += complexity_indicators["boolean_operators"] * bool_score

        return round(min(1.0, score), 3)

    def _extract_cache_hit_probability(self, context: dict[str, Any]) -> float:
        """Extract cache hit probability (0.0-1.0)."""
        query = context.get("query", {})
        cache_stats = context.get("cache_stats", {})

        # Direct cache hit probability
        if "hit_probability" in cache_stats:
            return float(cache_stats["hit_probability"])

        # Calculate from cache characteristics
        query_hash = query.get("hash", "")
        if not query_hash:
            # Generate query hash
            query_text = query.get("text", "")
            query_hash = hashlib.md5(query_text.encode()).hexdigest()

        # Cache statistics
        total_queries = cache_stats.get("total_queries", 0)
        cache_hits = cache_stats.get("cache_hits", 0)
        recent_queries = cache_stats.get("recent_queries", [])  # Last 100 queries

        # Base hit rate
        base_hit_rate = cache_hits / max(1, total_queries)

        # Boost for frequently repeated queries
        query_frequency = recent_queries.count(query_hash)
        frequency_boost = min(0.3, query_frequency * 0.1)

        # Time-based decay (recent queries more likely to be cached)
        cache_age = cache_stats.get("cache_age_hours", 0)
        age_factor = math.exp(-cache_age / 24.0)  # Decay over 24 hours

        # Combine factors
        hit_probability = (base_hit_rate * 0.6) + frequency_boost + (age_factor * 0.1)

        return round(max(0.0, min(1.0, hit_probability)), 3)
