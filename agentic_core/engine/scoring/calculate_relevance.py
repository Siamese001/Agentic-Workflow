"""Calculate Relevance - Utility for calculating relevance scores.

This module provides utilities for calculating relevance scores between queries
and documents, including various ranking algorithms and scoring methods.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum
import math
import re

logger = logging.getLogger(__name__)


class RelevanceMethod(Enum):
    """Methods for calculating relevance."""
    TF_IDF = "tf_idf"
    BM25 = "bm25"
    COSINE_SIMILARITY = "cosine_similarity"
    JACCARD = "jaccard"
    CUSTOM = "custom"


@dataclass
class QueryDocument:
    """Document with text and metadata."""
    id: str
    text: str
    tokens: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelevanceConfig:
    """Configuration for relevance calculations."""
    method: RelevanceMethod = RelevanceMethod.TF_IDF
    k1: float = 1.2  # BM25 parameter
    b: float = 0.75  # BM25 parameter
    min_doc_freq: int = 1
    max_doc_freq: int = None
    normalize_scores: bool = True


@dataclass
class RelevanceResult:
    """Result of relevance calculation."""
    document_id: str
    relevance_score: float
    method: RelevanceMethod
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelevanceRanking:
    """Complete relevance ranking results."""
    query: str
    results: List[RelevanceResult]
    total_documents: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class RelevanceCalculator:
    """Main class for calculating relevance scores."""

    def __init__(self, config: Optional[RelevanceConfig] = None):
        self.config = config or RelevanceConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._document_corpus: List[QueryDocument] = []
        self._idf_cache: Dict[str, float] = {}
        self._doc_freqs: Dict[str, int] = {}

    def add_documents(self, documents: List[QueryDocument]) -> None:
        """Add documents to the corpus.
        
        Args:
            documents: List of documents to add
        """
        self._document_corpus.extend(documents)
        self._update_statistics()
        self.logger.info(f"Added {len(documents)} documents to corpus")

    def calculate_relevance(self, query: str, document: QueryDocument,
                           method: Optional[RelevanceMethod] = None) -> RelevanceResult:
        """Calculate relevance score for a single document.
        
        Args:
            query: Query string
            document: Document to score
            method: Scoring method to use
            
        Returns:
            RelevanceResult: Relevance score and details
        """
        method = method or self.config.method
        
        try:
            # Tokenize query and document
            query_tokens = self._tokenize(query)
            doc_tokens = document.tokens if document.tokens else self._tokenize(document.text)
            
            # Calculate relevance based on method
            if method == RelevanceMethod.TF_IDF:
                score, details = self._tf_idf_score(query_tokens, doc_tokens)
            elif method == RelevanceMethod.BM25:
                score, details = self._bm25_score(query_tokens, doc_tokens)
            elif method == RelevanceMethod.COSINE_SIMILARITY:
                score, details = self._cosine_similarity_score(query_tokens, doc_tokens)
            elif method == RelevanceMethod.JACCARD:
                score, details = self._jaccard_score(query_tokens, doc_tokens)
            else:
                score, details = 0.0, {}
            
            result = RelevanceResult(
                document_id=document.id,
                relevance_score=score,
                method=method,
                details=details
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Relevance calculation failed: {str(e)}")
            return RelevanceResult(
                document_id=document.id,
                relevance_score=0.0,
                method=method,
                details={"error": str(e)}
            )

    def rank_documents(self, query: str, top_k: Optional[int] = None,
                      method: Optional[RelevanceMethod] = None) -> RelevanceRanking:
        """Rank all documents by relevance to query.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            method: Scoring method to use
            
        Returns:
            RelevanceRanking: Ranked results
        """
        self.logger.info(f"Ranking {len(self._document_corpus)} documents for query: {query[:50]}...")
        
        try:
            # Calculate relevance for all documents
            results = []
            
            for document in self._document_corpus:
                result = self.calculate_relevance(query, document, method)
                results.append(result)
            
            # Sort by relevance score (descending)
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Apply top_k limit
            if top_k:
                results = results[:top_k]
            
            # Normalize scores if configured
            if self.config.normalize_scores and results:
                max_score = max(r.relevance_score for r in results)
                if max_score > 0:
                    for result in results:
                        result.relevance_score = result.relevance_score / max_score
            
            ranking = RelevanceRanking(
                query=query,
                results=results,
                total_documents=len(self._document_corpus),
                metadata={
                    "ranked_at": datetime.utcnow().isoformat(),
                    "method": (method or self.config.method).value,
                    "top_k": top_k
                }
            )
            
            self.logger.info(f"Ranking completed: {len(results)} results")
            return ranking
            
        except Exception as e:
            self.logger.error(f"Document ranking failed: {str(e)}")
            return RelevanceRanking(
                query=query,
                results=[],
                total_documents=len(self._document_corpus),
                metadata={"error": str(e)}
            )

    def get_document_frequency(self, term: str) -> int:
        """Get document frequency for a term.
        
        Args:
            term: Term to look up
            
        Returns:
            int: Number of documents containing the term
        """
        return self._doc_freqs.get(term.lower(), 0)

    def get_idf(self, term: str) -> float:
        """Get IDF score for a term.
        
        Args:
            term: Term to calculate IDF for
            
        Returns:
            float: IDF score
        """
        term = term.lower()
        if term in self._idf_cache:
            return self._idf_cache[term]
        
        df = self.get_document_frequency(term)
        if df == 0:
            idf = 0.0
        else:
            n = len(self._document_corpus)
            idf = math.log(n / df)
        
        self._idf_cache[term] = idf
        return idf

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Simple tokenization - can be enhanced with more sophisticated methods
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def _update_statistics(self) -> None:
        """Update document frequency statistics."""
        self._doc_freqs.clear()
        self._idf_cache.clear()
        
        for document in self._document_corpus:
            tokens = document.tokens if document.tokens else self._tokenize(document.text)
            unique_tokens = set(tokens)
            
            for token in unique_tokens:
                self._doc_freqs[token] = self._doc_freqs.get(token, 0) + 1

    def _tf_idf_score(self, query_tokens: List[str], doc_tokens: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Calculate TF-IDF relevance score."""
        # Calculate term frequencies
        doc_tf = {}
        for token in doc_tokens:
            doc_tf[token] = doc_tf.get(token, 0) + 1
        
        # Calculate TF-IDF score
        score = 0.0
        term_scores = {}
        
        for token in query_tokens:
            tf = doc_tf.get(token, 0)
            idf = self.get_idf(token)
            term_score = tf * idf
            score += term_score
            term_scores[token] = term_score
        
        return score, {"term_scores": term_scores, "method": "tf_idf"}

    def _bm25_score(self, query_tokens: List[str], doc_tokens: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Calculate BM25 relevance score."""
        # Calculate document statistics
        doc_len = len(doc_tokens)
        avg_doc_len = sum(len(d.tokens if d.tokens else self._tokenize(d.text)) 
                         for d in self._document_corpus) / len(self._document_corpus)
        
        # Calculate term frequencies
        doc_tf = {}
        for token in doc_tokens:
            doc_tf[token] = doc_tf.get(token, 0) + 1
        
        # Calculate BM25 score
        score = 0.0
        term_scores = {}
        
        for token in query_tokens:
            tf = doc_tf.get(token, 0)
            idf = self.get_idf(token)
            
            # BM25 formula
            numerator = tf * (self.config.k1 + 1)
            denominator = tf + self.config.k1 * (1 - self.config.b + self.config.b * (doc_len / avg_doc_len))
            
            term_score = idf * (numerator / denominator)
            score += term_score
            term_scores[token] = term_score
        
        return score, {"term_scores": term_scores, "method": "bm25"}

    def _cosine_similarity_score(self, query_tokens: List[str], doc_tokens: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Calculate cosine similarity relevance score."""
        # Create term vectors
        all_terms = set(query_tokens + doc_tokens)
        
        query_vector = []
        doc_vector = []
        
        for term in all_terms:
            query_tf = query_tokens.count(term)
            doc_tf = doc_tokens.count(term)
            
            # Apply IDF weighting
            idf = self.get_idf(term)
            query_vector.append(query_tf * idf)
            doc_vector.append(doc_tf * idf)
        
        # Calculate cosine similarity
        dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
        query_norm = math.sqrt(sum(q * q for q in query_vector))
        doc_norm = math.sqrt(sum(d * d for d in doc_vector))
        
        if query_norm == 0 or doc_norm == 0:
            score = 0.0
        else:
            score = dot_product / (query_norm * doc_norm)
        
        return score, {"method": "cosine_similarity", "query_norm": query_norm, "doc_norm": doc_norm}

    def _jaccard_score(self, query_tokens: List[str], doc_tokens: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Calculate Jaccard similarity relevance score."""
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        
        intersection = query_set.intersection(doc_set)
        union = query_set.union(doc_set)
        
        if len(union) == 0:
            score = 0.0
        else:
            score = len(intersection) / len(union)
        
        return score, {
            "method": "jaccard",
            "intersection_size": len(intersection),
            "union_size": len(union)
        }


# Factory function for easy instantiation
def create_relevance_calculator(
    method: str = "tf_idf",
    k1: float = 1.2,
    b: float = 0.75,
    normalize_scores: bool = True,
    **kwargs
) -> RelevanceCalculator:
    """Create a configured relevance calculator."""
    config = RelevanceConfig(
        method=RelevanceMethod(method),
        k1=k1,
        b=b,
        normalize_scores=normalize_scores,
        **kwargs
    )
    return RelevanceCalculator(config)


# Convenience function for direct usage
def calculate_relevance(
    query: str,
    documents: List[Dict[str, Any]],
    method: str = "tf_idf",
    top_k: int = 10
) -> Dict[str, Any]:
    """Calculate relevance scores for documents.
    
    Args:
        query: Query string
        documents: List of documents with id and text
        method: Scoring method
        top_k: Number of top results
        
    Returns:
        Dict: Relevance ranking results
    """
    calculator = create_relevance_calculator(method=method)
    
    # Convert documents
    doc_objects = []
    for doc in documents:
        doc_obj = QueryDocument(
            id=doc["id"],
            text=doc["text"],
            metadata=doc.get("metadata", {})
        )
        doc_objects.append(doc_obj)
    
    # Add documents and rank
    calculator.add_documents(doc_objects)
    ranking = calculator.rank_documents(query, top_k=top_k)
    
    # Convert results
    return {
        "query": ranking.query,
        "results": [
            {
                "document_id": r.document_id,
                "relevance_score": r.relevance_score,
                "method": r.method.value,
                "details": r.details
            }
            for r in ranking.results
        ],
        "total_documents": ranking.total_documents,
        "metadata": ranking.metadata
    }
