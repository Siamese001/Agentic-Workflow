"""Hybrid Scorer for RAG systems.

Combines multiple scoring strategies for optimal document ranking.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math
import re
from collections import Counter


@dataclass
class ScoringWeights:
    """Weights for different scoring components."""
    bm25_weight: float = 0.4
    semantic_weight: float = 0.3
    tfidf_weight: float = 0.2
    freshness_weight: float = 0.1


@dataclass
class ScoringResult:
    """Result of scoring operation."""
    document_id: str
    bm25_score: float
    semantic_score: float
    tfidf_score: float
    freshness_score: float
    final_score: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BM25Scorer:
    """BM25 scoring algorithm implementation."""
    
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        """Initialize BM25 scorer.
        
        Args:
            k1: Controls term frequency saturation
            b: Controls document length normalization
        """
        self.k1 = k1
        self.b = b
        self.doc_freqs: Dict[str, int] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_length = 0.0
        
    def build_index(self, documents: List[str]) -> None:
        """Build BM25 index from documents.
        
        Args:
            documents: List of document texts
        """
        # Calculate document frequencies
        all_terms = []
        for doc in documents:
            terms = self._tokenize(doc)
            all_terms.append(terms)
            self.doc_lengths.append(len(terms))
            
            # Count unique terms in this document
            for term in set(terms):
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
        
        # Calculate average document length
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Store tokenized documents for scoring
        self.documents = all_terms
    
    def score(self, query: str, doc_idx: int) -> float:
        """Score document against query using BM25.
        
        Args:
            query: Query string
            doc_idx: Index of document to score
            
        Returns:
            BM25 score
        """
        if doc_idx >= len(self.documents):
            return 0.0
        
        query_terms = self._tokenize(query)
        doc_terms = self.documents[doc_idx]
        doc_length = self.doc_lengths[doc_idx]
        
        if not query_terms or doc_length == 0:
            return 0.0
        
        score = 0.0
        doc_term_counts = Counter(doc_terms)
        
        for term in query_terms:
            if term in doc_term_counts:
                # BM25 formula components
                tf = doc_term_counts[term]
                df = self.doc_freqs.get(term, 0)
                idf = math.log((len(self.documents) - df + 0.5) / (df + 0.5))
                
                # BM25 score for this term
                term_score = idf * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
                )
                score += term_score
        
        return score
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        return re.findall(r"\b\w+\b", text.lower())


class HybridScorer:
    """Hybrid scorer combining multiple scoring strategies."""
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """Initialize hybrid scorer.
        
        Args:
            weights: Scoring weights for different components
        """
        self.weights = weights or ScoringWeights()
        self.bm25_scorer = BM25Scorer()
        self.documents: List[Dict[str, Any]] = []
        
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Index documents for scoring.
        
        Args:
            documents: List of document dictionaries with 'id' and 'content'
        """
        self.documents = documents
        doc_texts = [doc["content"] for doc in documents]
        self.bm25_scorer.build_index(doc_texts)
    
    def score_documents(self, query: str, top_k: Optional[int] = None) -> List[ScoringResult]:
        """Score all documents against query.
        
        Args:
            query: Query string
            top_k: Optional limit on number of results
            
        Returns:
            List of scoring results
        """
        results = []
        
        for i, doc in enumerate(self.documents):
            # Calculate individual scores
            bm25_score = self.bm25_scorer.score(query, i)
            semantic_score = self._calculate_semantic_score(doc["content"], query)
            tfidf_score = self._calculate_tfidf_score(doc["content"], query)
            freshness_score = self._calculate_freshness_score(doc)
            
            # Calculate weighted final score
            final_score = (
                self.weights.bm25_weight * bm25_score +
                self.weights.semantic_weight * semantic_score +
                self.weights.tfidf_weight * tfidf_score +
                self.weights.freshness_weight * freshness_score
            )
            
            result = ScoringResult(
                document_id=doc["id"],
                bm25_score=bm25_score,
                semantic_score=semantic_score,
                tfidf_score=tfidf_score,
                freshness_score=freshness_score,
                final_score=final_score,
                metadata={"content_length": len(doc["content"])}
            )
            
            results.append(result)
        
        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)
        
        if top_k:
            results = results[:top_k]
        
        return results
    
    def _calculate_semantic_score(self, content: str, query: str) -> float:
        """Calculate semantic similarity score (mock implementation)."""
        # Simple overlap-based semantic score
        content_words = set(re.findall(r"\b\w+\b", content.lower()))
        query_words = set(re.findall(r"\b\w+\b", query.lower()))
        
        if not query_words:
            return 0.0
        
        overlap = len(content_words & query_words)
        return overlap / len(query_words)
    
    def _calculate_tfidf_score(self, content: str, query: str) -> float:
        """Calculate TF-IDF score."""
        query_terms = re.findall(r"\b\w+\b", query.lower())
        content_terms = re.findall(r"\b\w+\b", content.lower())
        
        if not query_terms or not content_terms:
            return 0.0
        
        # Calculate TF
        content_counter = Counter(content_terms)
        total_terms = len(content_terms)
        
        # Simple TF-IDF calculation
        score = 0.0
        for term in query_terms:
            tf = content_counter.get(term, 0) / total_terms
            # IDF would require corpus stats, using simple heuristic
            idf = 1.0 if term in content_counter else 0.0
            score += tf * idf
        
        return min(score, 1.0)
    
    def _calculate_freshness_score(self, doc: Dict[str, Any]) -> float:
        """Calculate freshness score."""
        # Default to neutral score
        return 0.5
