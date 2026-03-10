from dataclasses import dataclass
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
LIC Code Interpreter Tool - Fast loop for deterministic evaluation.

Ported from: archives/legacy_lic/Agentic LIC/tools_LIC.py
"""


@dataclass
class ScoredCandidate:
    """A scored candidate message."""

    candidate_index: int
    candidate_text: str
    scores: dict[str, float]
    total_score: float


@dataclass
class ScoringCriteria:
    """Criteria for scoring candidates."""

    strategic_alignment: float = 0.5
    keyword_density: float = 0.3
    readability: float = 0.2


@dataclass
class SimilarityResult:
    """Result of a similarity check."""

    score: float
    method: str
    text1_length: int
    text2_length: int


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""

    keywords: list[str]
    source_text_length: int
    top_n: int


# shared English stop words
STOP_WORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
        "the",
        "this",
        "but",
        "they",
        "have",
        "had",
        "what",
        "when",
        "where",
        "who",
        "which",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "can",
        "just",
        "should",
        "now",
        "also",
        "into",
        "over",
        "after",
        "before",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "any",
        "about",
    ],
)


class LICCodeInterpreter:
    """
    Safe code execution environment for deterministic evaluation.

    Provides a "Fast Loop" for validation and scoring before committing
    to expensive LLM calls. Used by HOP-6 (ValidationAgent) to:
    - Score message drafts for similarity to strategic brief
    - Rank N candidates without LLM synthesis
    - Run deterministic validation checks
    """

    def __init__(self) -> None:
        """Initialize code interpreter with safe function registry."""
        self.functions: dict[str, Callable[..., Any]] = {
            "run_similarity_check": self.run_similarity_check,
            "run_scoring_competition": self.run_scoring_competition,
            "extract_keywords": self.extract_keywords,
            "calculate_overlap": self.calculate_overlap,
            "rank_by_metric": self.rank_by_metric,
            "validate_structure": self.validate_structure,
        }

    def execute(self, function_name: str, **kwargs: object) -> object:
        """
        Execute a registered function safely.

        Args:
            function_name: Name of function to execute
            **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            ValueError: If function not registered
        """
        if function_name not in self.functions:
            raise ValueError(
                f"Function '{function_name}' not registered. Available: {list(self.functions.keys())}",
            )

        func = self.functions[function_name]
        return func(**kwargs)

    def run_similarity_check(
        self,
        text1: str,
        text2: str,
        method: str = "cosine",
    ) -> SimilarityResult:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            method: Similarity method ("cosine", "jaccard")

        Returns:
            SimilarityResult with score
        """
        if method == "cosine":
            score = self._cosine_similarity(text1, text2)
        elif method == "jaccard":
            score = self._jaccard_similarity(text1, text2)
        else:
            raise ValueError(f"Unknown similarity method: {method}")

        return SimilarityResult(
            score=score,
            method=method,
            text1_length=len(text1),
            text2_length=len(text2),
        )

    def run_scoring_competition(
        self,
        candidates: list[str],
        strategic_brief: str,
        criteria: ScoringCriteria | None = None,
    ) -> list[ScoredCandidate]:
        """
        Score N candidate messages against strategic brief.

        This is the "Fast Loop" that replaces LLM synthesis for C_LEVEL.
        Instead of using an LLM to synthesize 3 drafts, we score them
        deterministically and select the winner.

        Args:
            candidates: List of candidate message texts
            strategic_brief: Strategic brief text to align with
            criteria: Optional scoring weights (defaults to equal)

        Returns:
            List of scored candidates, sorted by score (highest first)
        """
        if criteria is None:
            criteria = ScoringCriteria()

        scored: list[ScoredCandidate] = []

        for i, candidate in enumerate(candidates):
            scores: dict[str, float] = {}

            # 1. Strategic alignment (cosine similarity to brief)
            alignment_result = self.run_similarity_check(candidate, strategic_brief, method="cosine")
            scores["strategic_alignment"] = alignment_result.score

            # 2. Keyword density (how many strategic keywords present)
            brief_keywords = self.extract_keywords(strategic_brief, top_n=20)
            candidate_words = set(candidate.lower().split())

            keyword_matches = sum(1 for kw in brief_keywords.keywords if kw in candidate_words)
            scores["keyword_density"] = (
                keyword_matches / len(brief_keywords.keywords) if brief_keywords.keywords else 0.0
            )

            # 3. Readability (word count in target range, sentence length)
            scores["readability"] = self._calculate_readability(candidate)

            # Calculate weighted total
            total_score = (
                scores["strategic_alignment"] * criteria.strategic_alignment
                + scores["keyword_density"] * criteria.keyword_density
                + scores["readability"] * criteria.readability
            )

            scored.append(
                ScoredCandidate(
                    candidate_index=i,
                    candidate_text=candidate,
                    scores=scores,
                    total_score=total_score,
                ),
            )

        # Sort by total score (highest first)
        scored.sort(key=lambda x: x.total_score, reverse=True)

        return scored

    def extract_keywords(
        self,
        text: str,
        top_n: int = 10,
        min_length: int = 4,
    ) -> KeywordExtractionResult:
        """
        Extract top keywords from text using word frequency.

        Args:
            text: Input text
            top_n: Number of keywords to return
            min_length: Minimum word length

        Returns:
            KeywordExtractionResult with keywords
        """

        words = [
            w.lower()
            for w in re.findall(r"\b\w+\b", text)
            if len(w) >= min_length and w.lower() not in STOP_WORDS
        ]

        if not words:
            return KeywordExtractionResult(
                keywords=[],
                source_text_length=len(text),
                top_n=top_n,
            )

        # Count word frequencies
        word_counts: dict[str, int] = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Sort by frequency and take top N
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_words[:top_n]]

        return KeywordExtractionResult(
            keywords=keywords,
            source_text_length=len(text),
            top_n=top_n,
        )

    def calculate_overlap(
        self,
        text1: str,
        text2: str,
        min_word_length: int = 4,
    ) -> dict[str, object]:
        """
        Calculate word overlap between two texts.

        Args:
            text1: First text
            text2: Second text
            min_word_length: Minimum word length to consider

        Returns:
            Dictionary with overlap statistics
        """
        words1 = {
            w.lower()
            for w in re.findall(r"\b\w+\b", text1)
            if len(w) >= min_word_length and w.lower() not in STOP_WORDS
        }
        words2 = {
            w.lower()
            for w in re.findall(r"\b\w+\b", text2)
            if len(w) >= min_word_length and w.lower() not in STOP_WORDS
        }

        intersection = words1 & words2
        union = words1 | words2

        return {
            "overlap_count": len(intersection),
            "overlap_words": list(intersection),
            "text1_unique_count": len(words1 - words2),
            "text2_unique_count": len(words2 - words1),
            "jaccard_similarity": len(intersection) / len(union) if union else 0.0,
        }

    def rank_by_metric(
        self,
        items: list[dict[str, object]],
        metric_key: str,
        descending: bool = True,
    ) -> list[dict[str, object]]:
        """
        Rank items by a specific Metric.

        Args:
            items: List of items with metrics
            metric_key: Key to sort by
            descending: Sort in descending order

        Returns:
            Sorted list of items
        """
        return sorted(
            items,
            key=lambda x: x.get(metric_key, 0),
            reverse=descending,
        )

    def validate_structure(
        self,
        text: str,
        requirements: dict[str, object],
    ) -> dict[str, object]:
        """
        Validate text structure against requirements.

        Args:
            text: Text to validate
            requirements: Structure requirements

        Returns:
            Validation result dictionary
        """
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        # Word count validation
        word_count = len(text.split())
        result["metrics"]["word_count"] = word_count

        if "min_words" in requirements:
            if word_count < requirements["min_words"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Word count {word_count} below minimum {requirements['min_words']}",
                )

        if "max_words" in requirements:
            if word_count > requirements["max_words"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Word count {word_count} above maximum {requirements['max_words']}",
                )

        # Character count validation
        char_count = len(text)
        result["metrics"]["char_count"] = char_count

        if "max_chars" in requirements:
            if char_count > requirements["max_chars"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Character count {char_count} above maximum {requirements['max_chars']}",
                )

        # Sentence count validation
        sentences = re.split(r"[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])
        result["metrics"]["sentence_count"] = sentence_count

        if "min_sentences" in requirements:
            if sentence_count < requirements["min_sentences"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Sentence count {sentence_count} below minimum {requirements['min_sentences']}",
                )

        return result

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity using TF-IDF-like approach."""
        # Tokenize
        words1 = re.findall(r"\b\w+\b", text1.lower())
        words2 = re.findall(r"\b\w+\b", text2.lower())

        # Build vocabulary
        vocab = set(words1) | set(words2)
        if not vocab:
            return 0.0

        # Build term frequency vectors
        tf1 = {word: words1.count(word) for word in vocab}
        tf2 = {word: words2.count(word) for word in vocab}

        # Calculate cosine similarity
        dot_product = sum(tf1[word] * tf2[word] for word in vocab)
        magnitude1 = sum(tf1[word] ** 2 for word in vocab) ** 0.5
        magnitude2 = sum(tf2[word] ** 2 for word in vocab) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity on words."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1 & words2
        union = words1 | words2

        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score (0-1).

        Based on:
        - Word count in target range (140-250 words)
        - Average sentence length (15-25 words ideal)
        """
        words = text.split()
        word_count = len(words)

        # Word count score (peak at 180 words)
        if 140 <= word_count <= 250:
            word_score = 1.0 - abs(word_count - 180) / 110
        else:
            word_score = max(0.0, 1.0 - abs(word_count - 180) / 180)

        # Sentence length score
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]

        if sentences:
            avg_sentence_length = word_count / len(sentences)
            # Ideal is 15-25 words per sentence
            if 15 <= avg_sentence_length <= 25:
                sentence_score = 1.0
            else:
                sentence_score = max(0.0, 1.0 - abs(avg_sentence_length - 20) / 20)
        else:
            sentence_score = 0.5

        # Combine scores
        return (word_score + sentence_score) / 2


def create_code_interpreter() -> LICCodeInterpreter:
    """builder function to create a code interpreter."""
    return LICCodeInterpreter()
