"""
Clarity & Brevity Filter for L1 Content Refinement
Refines outreach messages for maximum clarity and impact
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

logger = logging.getLogger("ClarityFilter")  # GLOBAL: Review if this should be constant


@dataclass
class FilterResult:
    """Result of clarity and brevity filtering"""
    original_text: str
    filtered_text: str
    changes_made: List[str]
    clarity_score: float  # 0 to 1
    brevity_score: float  # 0 to 1
    word_count_reduction: int
    readability_improvement: float


class ClarityBrevityFilter:
    """
    Refines outreach messages for clarity and brevity
    """

    def __init__(self):
        # Configuration
        self.max_sentence_length = 20  # words
        self.target_reading_level = 8  # grade level
        self.min_brevity_score = 0.7  # minimum acceptable

        # Common filler words and phrases to remove
        self.filler_words = {
            "actually", "basically", "literally", "really", "very", "quite",
            "rather", "somewhat", "somehow", "in order to", "due to the fact that",
            "in the event that", "for the purpose of", "with regard to",
            "in terms of", "on the basis of", "as a matter of fact",
            "i think that", "i feel that", "i believe that", "in my opinion"
        }

        # Corporate jargon to simplify
        self.jargon_map = {
            "synergize": "work together",
            "leverage": "use",
            "optimize": "improve",
            "paradigm": "approach",
            "methodology": "method",
            "utilize": "use",
            "facilitate": "help",
            "implement": "put in place",
            "strategic": "planned",
            "initiative": "plan",
            "deliverable": "result",
            "stakeholder": "person involved",
            "bandwidth": "time",
            "circle back": "return to",
            "touch base": "talk",
            "action items": "tasks",
            "low-hanging fruit": "easy wins",
            "deep dive": "detailed look",
            "ping": "contact"
        }

        # Redundant phrases
        self.redundant_phrases = [
            (r"\bcompletely\s+finished\b", "finished"),
            (r"\bfinal\s+outcome\b", "outcome"),
            (r"\bbasic\s+fundamentals\b", "fundamentals"),
            (r"\bend\s+result\b", "result"),
            (r"\bfirst\began\b", "began"),
            (r"\bjoin\s+together\b", "join"),
            (r"\bnew\b+innovation\b", "innovation"),
            (r"\bpast\s+history\b", "history"),
            (r"\btrue\s+facts\b", "facts"),
            (r"\bunexpected\s+surprise\b", "surprise")
        ]

    def _calculate_readability(self, text: str) -> float:
        """Calculate approximate reading level (lower is better)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 20  # Very poor

        total_words = sum(len(s.split()) for s in sentences)
        avg_sentence_length = total_words / len(sentences)

        # Simplified Flesch-Kincaid approximation
        # Lower score = easier to read
        reading_level = (avg_sentence_length * 0.39) + 10

        return reading_level

    def _remove_fillers(self, text: str) -> Tuple[str, List[str]]:
        """Remove filler words and phrases"""
        changes = []
        filtered = text

        for filler in self.filler_words:
            pattern = r'\b' + re.escape(filler) + r'\b'
            if re.search(pattern, filtered, re.IGNORECASE):
                filtered = re.sub(pattern, '', filtered, flags=re.IGNORECASE)
                changes.append(f"Removed filler: '{filler}'")

        # Clean up extra spaces
        filtered = re.sub(r'\s+', ' ', filtered).strip()

        return filtered, changes

    def _simplify_jargon(self, text: str) -> Tuple[str, List[str]]:
        """Replace corporate jargon with simpler terms"""
        changes = []
        filtered = text

        for jargon, simple in self.jargon_map.items():
            pattern = r'\b' + re.escape(jargon) + r'\b'
            if re.search(pattern, filtered, re.IGNORECASE):
                filtered = re.sub(pattern, simple, filtered,
                                  flags=re.IGNORECASE)
                changes.append(f"Simplified: '{jargon}' → '{simple}'")

        return filtered, changes

    def _fix_redundancies(self, text: str) -> Tuple[str, List[str]]:
        """Fix redundant phrases"""
        changes = []
        filtered = text

        for pattern, replacement in self.redundant_phrases:
            if re.search(pattern, filtered, re.IGNORECASE):
                filtered = re.sub(pattern, replacement,
                                  filtered, flags=re.IGNORECASE)
                changes.append(f"Fixed redundancy")

        return filtered, changes

    def _improve_sentence_structure(self, text: str) -> Tuple[str, List[str]]:
        """Improve sentence structure for clarity"""
        changes = []

        # Split long sentences
        sentences = re.split(r'([.!?]+)', text)
        improved_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            word_count = len(sentence.split())

            # If sentence is too long, try to split it
            if word_count > self.max_sentence_length and sentence.endswith(('.', '!', '?')):
                # Look for natural split points
                split_points = [' but ', ' and ', ' however, ',
                                ' therefore, ', ' meanwhile, ']

                for split_point in split_points:
                    if split_point in sentence.lower():
                        parts = re.split(split_point, sentence,
                                         flags=re.IGNORECASE)
                        if len(parts) == 2:
                            improved_sentences.extend(
                                [parts[0].strip() + '.', parts[1].strip() + '.'])
                            changes.append(
                                f"Split long sentence ({word_count} words)")
                            break
                else:
                    improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)

        return ' '.join(improved_sentences), changes

    def _enhance_clarity(self, text: str) -> Tuple[str, List[str]]:
        """Apply various clarity improvements"""
        changes = []
        filtered = text

        # Convert passive voice to active where possible
        passive_patterns = [
            (r'(\w+)\s+is\s+(\w+)\s+by\s+(\w+)', r'\3 \2 \1'),
            (r'(\w+)\s+are\s+(\w+)\s+by\s+(\w+)', r'\3 \2 \1'),
            (r'(\w+)\s+was\s+(\w+)\s+by\s+(\w+)', r'\3 \2 \1'),
            (r'(\w+)\s+were\s+(\w+)\s+by\s+(\w+)', r'\3 \2 \1')
        ]

        for pattern, replacement in passive_patterns:
            if re.search(pattern, filtered):
                filtered = re.sub(pattern, replacement, filtered)
                changes.append("Converted passive to active voice")

        # Ensure consistent capitalization
        filtered = filtered[0].upper() + filtered[1:] if filtered else filtered

        # Remove excessive punctuation
        filtered = re.sub(r'([.!?])\1+', r'\1', filtered)

        # Fix common typos
        typo_fixes = {
            ' teh ': ' the ',
            ' adn ': ' and ',
            ' thier ': ' their ',
            ' recieve ': ' receive ',
            ' beleive ': ' believe '
        }

        for typo, correct in typo_fixes.items():
            if typo in filtered.lower():
                filtered = filtered.replace(typo, correct)
                changes.append(f"Fixed typo: {typo.strip()}")

        return filtered, changes

    def _calculate_scores(self, original: str, filtered: str) -> Tuple[float, float, int, float]:
        """Calculate clarity and brevity scores"""
        # Brevity score (based on word reduction)
        original_words = len(original.split())
        filtered_words = len(filtered.split())

        if original_words > 0:
            word_reduction = original_words - filtered_words
            # 30% reduction = perfect score
            brevity_score = min(1.0, word_reduction / (original_words * 0.3))
        else:
            word_reduction = 0
            brevity_score = 1.0

        # Clarity score (based on readability improvement)
        original_readability = self._calculate_readability(original)
        filtered_readability = self._calculate_readability(filtered)

        readability_improvement = max(
            0, original_readability - filtered_readability)

        # Score based on how close to target reading level
        if filtered_readability <= self.target_reading_level:
            clarity_score = 1.0
        else:
            clarity_score = max(
                0, 1 - (filtered_readability - self.target_reading_level) / 10)

        return clarity_score, brevity_score, word_reduction, readability_improvement

    def filter_content(
        self,
        text: str,
        aggressive: bool = False,
        preserve_personalization: bool = True,
        logger: Optional[Any] = None
    ) -> FilterResult:
        """
        Filter content for clarity and brevity

        Args:
            text: Original text to filter
            aggressive: Use aggressive filtering (more reductions)
            preserve_personalization: Preserve personalization elements
            logger: Logger instance

        Returns:
            FilterResult with filtered text and metrics
        """

        if logger:
            logger.info(f"🔍 Applying clarity & brevity filter")

        original_text = text
        all_changes = []

        # Step 1: Remove filler words
        filtered, changes = self._remove_fillers(text)
        all_changes.extend(changes)

        # Step 2: Simplify jargon
        filtered, changes = self._simplify_jargon(filtered)
        all_changes.extend(changes)

        # Step 3: Fix redundancies
        filtered, changes = self._fix_redundancies(filtered)
        all_changes.extend(changes)

        # Step 4: Improve sentence structure
        filtered, changes = self._improve_sentence_structure(filtered)
        all_changes.extend(changes)

        # Step 5: Enhance clarity
        filtered, changes = self._enhance_clarity(filtered)
        all_changes.extend(changes)

        # Aggressive mode: additional filtering
        if aggressive:
            # Remove very short sentences (likely fragments)
            sentences = re.split(r'([.!?]+)', filtered)
            filtered_sentences = []

            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence.split()) >= 3 or sentence in ['.', '!', '?']:
                    filtered_sentences.append(sentence)

            filtered = ' '.join(filtered_sentences)
            all_changes.append("Removed sentence fragments")

        # Preserve personalization markers if requested
        if preserve_personalization:
            # Ensure [Personalization Point] markers remain
            if '[Personalization Point]' in original_text:
                if '[Personalization Point]' not in filtered:
                    filtered += '\n\n[Personalization Point]'
                    all_changes.append("Preserved personalization marker")

        # Calculate scores
        clarity_score, brevity_score, word_reduction, readability_improvement = self._calculate_scores(
            original_text, filtered
        )

        if logger:
            logger.info(f"✅ Content filtered:")
            logger.info(f"   Words reduced: {word_reduction}")
            logger.info(f"   Clarity score: {clarity_score:.2f}")
            logger.info(f"   Brevity score: {brevity_score:.2f}")
            logger.info(
                f"   Readability improvement: {readability_improvement:.1f} grade levels")

        return FilterResult(
            original_text=original_text,
            filtered_text=filtered,
            changes_made=all_changes,
            clarity_score=clarity_score,
            brevity_score=brevity_score,
            word_count_reduction=word_reduction,
            readability_improvement=readability_improvement
        )


# Global filter instance
_clarity_filter = None


def get_clarity_brevity_filter() -> ClarityBrevityFilter:
    """Get or create the global Clarity & Brevity Filter instance"""
    global _clarity_filter
    if _clarity_filter is None:
        _clarity_filter = ClarityBrevityFilter()
    return _clarity_filter


def filter_content(
    text: str,
    aggressive: bool = False,
    preserve_personalization: bool = True,
    logger: Optional[Any] = None
) -> FilterResult:
    """
    Convenience function to filter content for clarity and brevity

    Args:
        text: Original text to filter
        aggressive: Use aggressive filtering
        preserve_personalization: Preserve personalization elements
        logger: Logger instance

    Returns:
        FilterResult with filtered text and metrics
    """
    filter_instance = get_clarity_brevity_filter()
    return filter_instance.filter_content(text, aggressive, preserve_personalization, logger)

