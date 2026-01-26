# File: tools_LIC.py
# Description: Tool-Augmented Agents - "Fast Loop" tools for deterministic evaluation
# v13.0: Replaces expensive LLM calls with cheap, fast, deterministic code

__version__ = "13.0"

import re


class CodeInterpreterTool:
    """
    v13.0: Safe code execution environment for deterministic evaluation

    Provides a "Fast Loop" for validation and scoring before committing
    to expensive LLM calls. Used by HOP-6 (ValidationAgent) to:
    - Score message drafts for similarity to strategic brief
    - Rank N candidates without LLM synthesis
    - Run deterministic validation checks
    """

    def __init__(self):
        """Initialize code interpreter with safe function registry"""
        self.functions = {
            "run_similarity_check": self.run_similarity_check,
            "run_scoring_competition": self.run_scoring_competition,
            "extract_keywords": self.extract_keywords,
            "calculate_overlap": self.calculate_overlap,
            "rank_by_metric": self.rank_by_metric,
            "validate_structure": self.validate_structure,
        }

        print("[CodeInterpreter] Initialized with safe function registry")

    def execute(self, function_name: str, **kwargs) -> Any:
        """
        Execute a registered function safely

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
                f"Function '{function_name}' not registered. Available: {list(self.functions.keys())}"
            )

        func = self.functions[function_name]

        print(f"[CodeInterpreter] Executing: {function_name}")

        return func(**kwargs)

    def run_similarity_check(self, text1: str, text2: str, method: str = "cosine") -> float:
        """
        Calculate similarity between two texts

        Args:
            text1: First text
            text2: Second text
            method: Similarity method ("cosine", "jaccard")

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if method == "cosine":
            # TF-IDF + Cosine similarity
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

            return float(similarity)

        elif method == "jaccard":
            # Jaccard similarity on words
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            intersection = words1 & words2
            union = words1 | words2

            if len(union) == 0:
                return 0.0

            return len(intersection) / len(union)

        else:
            raise ValueError(f"Unknown similarity method: {method}")

    def run_scoring_competition(
        self, candidates: list[str], strategic_brief: str, criteria: dict[str, float] | None = None
    ) -> list[dict[str, Any]]:
        """
        Score N candidate messages against strategic brief

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
            criteria = {"strategic_alignment": 0.5, "keyword_density": 0.3, "readability": 0.2}

        print(f"[CodeInterpreter] scoring {len(candidates)} candidates")

        scored = []

        for i, candidate in enumerate(candidates):
            scores = {}

            # 1. Strategic alignment (cosine similarity to brief)
            scores["strategic_alignment"] = self.run_similarity_check(
                candidate, strategic_brief, method="cosine"
            )

            # 2. Keyword density (how many strategic keywords present)
            brief_keywords = self.extract_keywords(strategic_brief, top_n=20)
            candidate_words = set(candidate.lower().split())

            keyword_matches = sum(1 for kw in brief_keywords if kw in candidate_words)
            scores["keyword_density"] = (
                keyword_matches / len(brief_keywords) if brief_keywords else 0.0
            )

            # 3. Readability (word count in target range, sentence length)
            scores["readability"] = self._calculate_readability(candidate)

            # Calculate weighted total
            total_score = sum(
                scores[criterion] * weight
                for criterion, weight in criteria.items()
                if criterion in scores
            )

            scored.append(
                {
                    "candidate_index": i,
                    "candidate_text": candidate,
                    "scores": scores,
                    "total_score": total_score,
                }
            )

        # Sort by total score (highest first)
        scored.sort(key=lambda x: x["total_score"], reverse=True)

        print(
            f"[CodeInterpreter] Winner: candidate {scored[0]['candidate_index']} (score: {scored[0]['total_score']:.3f})"
        )

        return scored

    def extract_keywords(self, text: str, top_n: int = 10, min_length: int = 4) -> list[str]:
        """
        Extract top keywords from text using TF-IDF

        Args:
            text: Input text
            top_n: Number of keywords to return
            min_length: Minimum word length

        Returns:
            List of keywords
        """
        # Remove common stop words and short words
        words = [
            w.lower()
            for w in text.split()
            if len(w) >= min_length and w.lower() not in self._get_stopwords()
        ]

        if not words:
            return []

        # Simple frequency-based extraction

        word_counts = Counter(words)

        return [word for word, count in word_counts.most_common(top_n)]

    def calculate_overlap(
        self, text: str, keyword_set: list[str], min_word_length: int = 4
    ) -> dict[str, Any]:
        """
        Calculate keyword overlap between text and keyword set

        Args:
            text: Input text
            keyword_set: List of keywords to check for
            min_word_length: Minimum word length to consider

        Returns:
            Dictionary with overlap statistics
        """
        # Extract words from text
        text_words = set(
            w.lower().strip(".,!?;:") for w in text.split() if len(w) >= min_word_length
        )

        # Convert keyword set to lowercase
        keywords = set(kw.lower() for kw in keyword_set)

        # Calculate overlap
        overlap = text_words & keywords

        overlap_ratio = len(overlap) / len(keywords) if keywords else 0.0
        coverage_ratio = len(overlap) / len(text_words) if text_words else 0.0

        return {
            "overlap_count": len(overlap),
            "overlap_keywords": list(overlap),
            "overlap_ratio": overlap_ratio,  # % of keywords found in text
            "coverage_ratio": coverage_ratio,  # % of text words that are keywords
            "total_keywords": len(keywords),
            "total_words": len(text_words),
        }

    def rank_by_metric(
        self, items: list[dict[str, Any]], metric_key: str, descending: bool = True
    ) -> list[dict[str, Any]]:
        """
        Rank items by a metric value

        Args:
            items: List of item dictionaries
            metric_key: Key to sort by
            descending: Sort descending (highest first)

        Returns:
            Sorted list of items
        """
        sorted_items = sorted(items, key=lambda x: x.get(metric_key, 0), reverse=descending)

        return sorted_items

    def validate_structure(
        self,
        text: str,
        expected_sections: list[str],
        section_patterns: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Validate message structure against expected sections

        Args:
            text: Message text
            expected_sections: List of required section names
            section_patterns: Optional regex patterns for each section

        Returns:
            Validation results
        """
        results = {
            "valid": True,
            "found_sections": [],
            "missing_sections": [],
            "section_analysis": {},
        }

        if section_patterns is None:
            section_patterns = self._get_default_section_patterns()

        for section in expected_sections:
            pattern = section_patterns.get(section)

            if pattern:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                found = len(matches) > 0
            else:
                # Simple check: section name appears in text
                found = section.lower() in text.lower()

            if found:
                results["found_sections"].append(section)
                results["section_analysis"][section] = {
                    "found": True,
                    "match_count": len(matches) if pattern else 1,
                }
            else:
                results["missing_sections"].append(section)
                results["section_analysis"][section] = {"found": False}
                results["valid"] = False

        return results

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate simple readability score

        Based on:
        - Word count in reasonable range
        - Average sentence length
        - Vocabulary diversity

        Returns:
            Readability score (0.0 to 1.0)
        """
        # Word count
        words = text.split()
        word_count = len(words)

        # Word count score (target: 200-250 words)
        if 180 <= word_count <= 270:
            word_count_score = 1.0
        elif 150 <= word_count <= 300:
            word_count_score = 0.8
        else:
            word_count_score = 0.5

        # Sentence length
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

            # Target: 15-25 words per sentence
            if 15 <= avg_sentence_length <= 25:
                sentence_score = 1.0
            elif 10 <= avg_sentence_length <= 30:
                sentence_score = 0.8
            else:
                sentence_score = 0.6
        else:
            sentence_score = 0.5

        # Vocabulary diversity (unique words / total words)
        unique_words = set(w.lower() for w in words)
        diversity_ratio = len(unique_words) / len(words) if words else 0.0

        # Target: 0.6-0.8 diversity
        if 0.6 <= diversity_ratio <= 0.8:
            diversity_score = 1.0
        elif 0.5 <= diversity_ratio <= 0.85:
            diversity_score = 0.8
        else:
            diversity_score = 0.6

        # Weighted average
        readability = word_count_score * 0.4 + sentence_score * 0.3 + diversity_score * 0.3

        return readability

    def _get_stopwords(self) -> set:
        """Get common English stop words"""
        return {
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
            "will",
            "with",
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
        }

    def _get_default_section_patterns(self) -> dict[str, str]:
        """Get default regex patterns for message sections"""
        return {
            "greeting": r"^(Hi|Hello|Dear|Good morning|Good afternoon)",
            "opening": r"(I\'m reaching out|I wanted to connect|Following up)",
            "body": r".{100,}",  # At least 100 chars
            "cta": r"(Would you|Could we|I\'d welcome|Would you be open)",
            "signature": r"(Best regards|Sincerely|Thanks|Best)",
        }


class ValidationToolkit:
    """
    Collection of deterministic validation tools
    Used for "Fast Loop" validation before expensive LLM calls
    """

    @staticmethod
    def check_word_count_range(
        text: str, target: int, tolerance: float = 0.15
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if text is within word count range

        Args:
            text: Input text
            target: Target word count
            tolerance: Tolerance as fraction (0.15 = ±15%)

        Returns:
            (is_valid, details_dict)
        """
        word_count = len(text.split())

        min_words = int(target * (1 - tolerance))
        max_words = int(target * (1 + tolerance))

        is_valid = min_words <= word_count <= max_words

        details = {
            "word_count": word_count,
            "target": target,
            "min_words": min_words,
            "max_words": max_words,
            "tolerance": tolerance,
            "is_valid": is_valid,
            "deviation": word_count - target,
        }

        return is_valid, details

    @staticmethod
    def check_forbidden_patterns(
        text: str, forbidden_patterns: list[str]
    ) -> tuple[bool, list[str]]:
        """
        Check for forbidden patterns in text

        Args:
            text: Input text
            forbidden_patterns: List of regex patterns to check

        Returns:
            (is_clean, list_of_violations)
        """
        violations = []

        for pattern in forbidden_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.extend(matches)

        is_clean = len(violations) == 0

        return is_clean, violations

    @staticmethod
    def check_required_keywords(
        text: str, required_keywords: list[str], min_count: int = 1
    ) -> tuple[bool, dict[str, int]]:
        """
        Check if required keywords appear in text

        Args:
            text: Input text
            required_keywords: List of keywords that must appear
            min_count: Minimum occurrences per keyword

        Returns:
            (all_present, keyword_counts_dict)
        """
        text_lower = text.lower()

        keyword_counts = {}

        for keyword in required_keywords:
            count = text_lower.count(keyword.lower())
            keyword_counts[keyword] = count

        all_present = all(count >= min_count for count in keyword_counts.values())

        return all_present, keyword_counts

    @staticmethod
    def check_ascii_only(text: str) -> tuple[bool, list[tuple[int, str]]]:
        """
        Check if text contains only ASCII characters

        Args:
            text: Input text

        Returns:
            (is_ascii_only, list_of_non_ascii_chars)
        """
        non_ascii = []

        for i, char in enumerate(text):
            if ord(char) > 127:
                non_ascii.append((i, char))

        is_ascii_only = len(non_ascii) == 0

        return is_ascii_only, non_ascii


def test_code_interpreter():
    """
    Test the code interpreter tool
    """
    print("\n=== Testing Code Interpreter Tool ===\n")

    tool = CodeInterpreterTool()

    # Test 1: Similarity check
    print("--- Test 1: Similarity Check ---")

    text1 = "AI platform for enterprise scalability and cloud migration"
    text2 = "Enterprise AI solutions with scalable cloud infrastructure"

    similarity = tool.execute("run_similarity_check", text1=text1, text2=text2, method="cosine")
    print(f"Cosine similarity: {similarity:.3f}")

    # Test 2: scoring competition
    print("\n--- Test 2: scoring Competition ---")

    strategic_brief = "Focus on AI platform scalability, cloud migration, and enterprise adoption"

    candidates = [
        "I'm reaching out about AI platform opportunities. My background in scalability and cloud can help your enterprise adoption goals.",
        "Hello! Wanted to connect about potential collaboration on technology projects in the industry.",
        "Given your focus on AI platform scalability and cloud migration, I believe my experience with enterprise adoption could add value to your initiatives.",
    ]

    results = tool.execute(
        "run_scoring_competition", candidates=candidates, strategic_brief=strategic_brief
    )

    for i, result in enumerate(results):
        print(f"\nCandidate {result['candidate_index']} (Score: {result['total_score']:.3f}):")
        print(f"  Strategic alignment: {result['scores']['strategic_alignment']:.3f}")
        print(f"  Keyword density: {result['scores']['keyword_density']:.3f}")
        print(f"  Readability: {result['scores']['readability']:.3f}")

    print(f"\n✓ Winner: Candidate {results[0]['candidate_index']}")

    # Test 3: Keyword extraction
    print("\n--- Test 3: Keyword Extraction ---")

    keywords = tool.execute("extract_keywords", text=strategic_brief, top_n=5)

    print(f"Top keywords: {keywords}")

    # Test 4: Overlap calculation
    print("\n--- Test 4: Overlap Calculation ---")

    overlap = tool.execute("calculate_overlap", text=candidates[0], keyword_set=keywords)

    print(f"Overlap count: {overlap['overlap_count']}")
    print(f"Overlap ratio: {overlap['overlap_ratio']:.3f}")
    print(f"Matching keywords: {overlap['overlap_keywords']}")

    print("\nTest complete\n")


def test_validation_toolkit():
    """
    Test the validation toolkit
    """
    print("\n=== Testing Validation Toolkit ===\n")

    # Test 1: Word count check
    print("--- Test 1: Word Count Range ---")

    text = "This is a test message with exactly twenty words to check if the word count validation works correctly."

    is_valid, details = ValidationToolkit.check_word_count_range(
        text=text, target=20, tolerance=0.15
    )

    print(f"Valid: {is_valid}")
    print(
        f"Word count: {details['word_count']} (target: {details['target']}, range: {details['min_words']}-{details['max_words']})"
    )

    # Test 2: Forbidden patterns
    print("\n--- Test 2: Forbidden Patterns ---")

    text_with_forbidden = (
        "I hope this finds you well. I wanted to reach out and leverage our synergy."
    )

    forbidden = [r"\bi hope\b", r"\bwanted to\b", r"\bleverage\b"]

    is_clean, violations = ValidationToolkit.check_forbidden_patterns(
        text=text_with_forbidden, forbidden_patterns=forbidden
    )

    print(f"Clean: {is_clean}")
    print(f"Violations: {violations}")

    # Test 3: Required keywords
    print("\n--- Test 3: Required Keywords ---")

    text_with_keywords = "Our AI platform helps with cloud migration and enterprise adoption."

    all_present, counts = ValidationToolkit.check_required_keywords(
        text=text_with_keywords, required_keywords=["platform", "cloud", "enterprise"], min_count=1
    )

    print(f"All present: {all_present}")
    print(f"Keyword counts: {counts}")

    print("\nTest complete\n")


if __name__ == "__main__":
    """
    Test the tool-augmented agents

    Usage:
        python tools_LIC.py
    """
    test_code_interpreter()
    test_validation_toolkit()
