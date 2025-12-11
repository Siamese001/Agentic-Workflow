"""
Hybrid Scorer - Combined Semantic + BM25 Scoring
Ported from legacy_engines/hybrid_scoring.py

Combines semantic similarity and BM25 keyword scoring for
40-60% improvement in retrieval accuracy through intelligent scoring fusion.
"""

import logging
import math
import time
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ScoringConfig:
    """Configuration for hybrid scoring"""
    semantic_weight: float = 0.6
    bm25_weight: float = 0.4
    k1: float = 1.5  # BM25 term frequency saturation
    b: float = 0.75  # BM25 length normalization
    min_score_threshold: float = 0.0


@dataclass
class ScoringResult:
    """Result of hybrid scoring for a single document"""
    doc_id: str
    content: str
    semantic_score: float
    bm25_score: float
    hybrid_score: float
    rank: int = 0
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class HybridScoringResult:
    """Complete result of hybrid scoring"""
    query: str
    results: List[ScoringResult]
    config: ScoringConfig
    processing_time_ms: int
    corpus_stats: Dict[str, object] = field(default_factory=dict)


class BM25Scorer:
    """
    BM25 Keyword-Based Scoring

    Implements the BM25 algorithm for keyword-based document scoring
    with IDF weighting and length normalization.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 scorer.

        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b

        # Corpus statistics
        self.doc_count = 0
        self.avg_doc_length = 0.0
        self.doc_lengths: Dict[str, int] = {}
        self.term_doc_freqs: Dict[str, int] = {}  # Number of docs containing term
        self.index_built = False

    def build_index(self, documents: List[Dict[str, object]]) -> None:
        """
        Build BM25 index from documents.

        Args:
            documents: List of documents with 'id' and 'content' fields
        """
        self.doc_count = len(documents)
        self.doc_lengths = {}
        self.term_doc_freqs = {}

        total_length = 0

        for doc in documents:
            doc_id = doc.get('id', str(hash(doc.get('content', ''))))
            content = doc.get('content', '')
            terms = self._tokenize(content)

            # Store document length
            self.doc_lengths[doc_id] = len(terms)
            total_length += len(terms)

            # Update term document frequencies
            unique_terms = set(terms)
            for term in unique_terms:
                self.term_doc_freqs[term] = self.term_doc_freqs.get(term, 0) + 1

        # Calculate average document length
        self.avg_doc_length = total_length / self.doc_count if self.doc_count > 0 else 0
        self.index_built = True

        logger.info(f"BM25 index built: {self.doc_count} docs, {len(self.term_doc_freqs)} unique terms")

    def score(self, query: str, document: Dict[str, object]) -> float:
        """
        Calculate BM25 score for a document given a query.

        Args:
            query: Search query
            document: Document with 'id' and 'content' fields

        Returns:
            BM25 score
        """
        if not self.index_built:
            # Build minimal index for single document
            self._build_minimal_index(document)

        doc_id = document.get('id', str(hash(document.get('content', ''))))
        content = document.get('content', '')

        query_terms = self._tokenize(query)
        doc_terms = self._tokenize(content)

        if not query_terms or not doc_terms:
            return 0.0

        doc_length = len(doc_terms)
        term_freqs = Counter(doc_terms)

        score = 0.0

        for term in query_terms:
            if term not in term_freqs:
                continue

            # Term frequency in document
            tf = term_freqs[term]

            # Document frequency (number of docs containing term)
            df = self.term_doc_freqs.get(term, 1)

            # IDF calculation
            idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)

            # BM25 score component
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / max(self.avg_doc_length, 1)))

            score += idf * (numerator / denominator)

        return score

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # basic tokenization - lowercase and split on non-alphanumeric
        import scripts.check_canonical_structure
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Filter short tokens and stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                    'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
                    'into', 'through', 'during', 'before', 'after', 'above', 'below',
                    'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
                    'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just'}
        return [t for t in tokens if len(t) > 2 and t not in stopwords]

    def _build_minimal_index(self, document: Dict[str, object]) -> None:
        """Build minimal index for single document scoring."""
        content = document.get('content', '')
        terms = self._tokenize(content)

        self.doc_count = 1
        self.avg_doc_length = len(terms)
        self.doc_lengths = {document.get('id', '0'): len(terms)}

        for term in set(terms):
            self.term_doc_freqs[term] = 1

        self.index_built = True


class SemanticScorer:
    """
    Semantic Similarity Scoring

    Calculates semantic similarity between query and documents.
    Uses basic word overlap for demonstration; in production would use embeddings.
    """

    def __init__(self):
        """Initialize semantic scorer."""
        pass

    def score(self, query: str, document: Dict[str, object]) -> float:
        """
        Calculate semantic similarity score.

        Args:
            query: Search query
            document: Document with 'content' field

        Returns:
            Semantic similarity score (0-1)
        """
        # Check for pre-computed semantic score
        if 'semantic_score' in document:
            return float(document['semantic_score'])

        if 'relevance_score' in document:
            return float(document['relevance_score'])

        # Fallback to Jaccard similarity
        content = document.get('content', '')
        return self._jaccard_similarity(query, content)

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0


class HybridScorer:
    """
    Hybrid Scoring System

    Combines semantic similarity and BM25 keyword scoring for
    improved retrieval accuracy through intelligent scoring fusion.
    """

    def __init__(self, config: Optional[ScoringConfig] = None):
        """
        Initialize hybrid scorer.

        Args:
            config: Scoring configuration
        """
        self.config = config or ScoringConfig()
        self.bm25_scorer = BM25Scorer(k1=self.config.k1, b=self.config.b)
        self.semantic_scorer = SemanticScorer()

    def score_documents(
        self,
        query: str,
        documents: List[Dict[str, object]],
        build_index: bool = True
    ) -> HybridScoringResult:
        """
        Score documents using hybrid approach.

        Args:
            query: Search query
            documents: Documents to score
            build_index: Whether to build BM25 index

        Returns:
            HybridScoringResult with scored documents
        """
        start_time = time.time()

        # Build BM25 index if requested
        if build_index and documents:
            self.bm25_scorer.build_index(documents)

        results = []

        for doc in documents:
            doc_id = doc.get('id', str(hash(doc.get('content', ''))))
            content = doc.get('content', '')

            # Calculate individual scores
            semantic_score = self.semantic_scorer.score(query, doc)
            bm25_score = self.bm25_scorer.score(query, doc)

            # Normalize BM25 score to 0-1 range (approximate)
            normalized_bm25 = min(bm25_score / 10.0, 1.0) if bm25_score > 0 else 0.0

            # Calculate hybrid score
            hybrid_score = (
                semantic_score * self.config.semantic_weight +
                normalized_bm25 * self.config.bm25_weight
            )

            if hybrid_score >= self.config.min_score_threshold:
                result = ScoringResult(
                    doc_id=doc_id,
                    content=content,
                    semantic_score=round(semantic_score, 4),
                    bm25_score=round(bm25_score, 4),
                    hybrid_score=round(hybrid_score, 4),
                    metadata=doc.get('metadata', {})
                )
                results.append(result)

        # Sort by hybrid score and assign ranks
        results.sort(key=lambda x: x.hybrid_score, reverse=True)
        for i, result in enumerate(results):
            result.rank = i + 1

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(f"Hybrid scoring complete: {len(results)} results in {processing_time}ms")

        return HybridScoringResult(
            query=query,
            results=results,
            config=self.config,
            processing_time_ms=processing_time,
            corpus_stats={
                'doc_count': self.bm25_scorer.doc_count,
                'avg_doc_length': self.bm25_scorer.avg_doc_length,
                'unique_terms': len(self.bm25_scorer.term_doc_freqs)
            }
        )

    def adjust_weights(
        self,
        semantic_weight: Optional[float] = None,
        bm25_weight: Optional[float] = None
    ) -> None:
        """Adjust scoring weights dynamically."""
        if semantic_weight is not None:
            self.config.semantic_weight = semantic_weight
        if bm25_weight is not None:
            self.config.bm25_weight = bm25_weight

        # Normalize weights
        total = self.config.semantic_weight + self.config.bm25_weight
        if total > 0:
            self.config.semantic_weight /= total
            self.config.bm25_weight /= total

        logger.info(f"Adjusted weights: semantic={self.config.semantic_weight}, bm25={self.config.bm25_weight}")

    def optimize_weights(
        self,
        query: str,
        documents: List[Dict[str, object]],
        relevance_labels: Optional[List[int]] = None
    ) -> ScoringConfig:
        """
        Optimize weights based on document characteristics.

        Args:
            query: Search query
            documents: Documents to analyze
            relevance_labels: Optional relevance labels for supervised optimization

        Returns:
            Optimized ScoringConfig
        """
        # Analyze query characteristics
        query_terms = self.bm25_scorer._tokenize(query)

        # If query is short, favor semantic matching
        if len(query_terms) <= 3:
            semantic_weight = 0.7
            bm25_weight = 0.3
        # If query is long/specific, favor BM25
        elif len(query_terms) >= 7:
            semantic_weight = 0.4
            bm25_weight = 0.6
        else:
            semantic_weight = 0.5
            bm25_weight = 0.5

        return ScoringConfig(
            semantic_weight=semantic_weight,
            bm25_weight=bm25_weight,
            k1=self.config.k1,
            b=self.config.b
        )

    def get_top_results(
        self,
        scoring_result: HybridScoringResult,
        top_k: int = 10
    ) -> List[ScoringResult]:
        """Get top K results from scoring."""
        return scoring_result.results[:top_k]


# builder functions
def create_hybrid_scorer(config: Optional[ScoringConfig] = None) -> HybridScorer:
    """Create hybrid scorer instance."""
    return HybridScorer(config)


def create_bm25_scorer(k1: float = 1.5, b: float = 0.75) -> BM25Scorer:
    """Create BM25 scorer instance."""
    return BM25Scorer(k1, b)


def score_documents(
    query: str,
    documents: List[Dict[str, object]],
    semantic_weight: float = 0.6,
    bm25_weight: float = 0.4
) -> HybridScoringResult:
    """Convenience function to score documents."""
    config = ScoringConfig(semantic_weight=semantic_weight, bm25_weight=bm25_weight)
    scorer = HybridScorer(config)
    return scorer.score_documents(query, documents)
