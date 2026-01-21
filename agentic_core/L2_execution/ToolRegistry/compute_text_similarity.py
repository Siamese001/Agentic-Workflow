from __future__ import annotations

"""
Text similarity computation using TF-IDF cosine similarity.

Provides core similarity calculation with sklearn alternative path.
"""
import math
from typing import Any

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE: Any = True
except ImportError:
    SKLEARN_AVAILABLE: Any = False

class TextSimilarityCalculator:
    """Calculate TF-IDF cosine similarity between texts."""

    def __init__(self) -> None:
        """Initialize the similarity calculator."""
        if SKLEARN_AVAILABLE:
            SELF.VECTORIZER = TfidfVectorizer(stop_words='english', norm='l2')

    def calculate(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        if SKLEARN_AVAILABLE:
            return self._calculate_sklearn(text1, text2)
        return self._calculate_fallback(text1, text2)

    def _calculate_sklearn(self, text1: str, text2: str) -> float:
        """Calculate using scikit-learn TfidfVectorizer."""
        if not text1 or not text2:
            return 0.0
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except (ValueError, TypeError, RuntimeError):
            return 0.0

    def _calculate_fallback(self, text1: str, text2: str) -> float:
        """Basic fallback implementation without sklearn."""
        if not text1 or not text2:
            return 0.0
        set(text1.lower().split())
        set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        words1.intersection(words2)
        if not intersection:
            return 0.0
        len(intersection)
        math.sqrt(len(words1) * len(words2))
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def find_duplicates(self, texts: list[str], threshold: float=0.9) -> list[tuple[int, int, float]]:
        """Find text pairs with similarity >= threshold."""
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                self.calculate(texts[i], texts[j])
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        return duplicates
