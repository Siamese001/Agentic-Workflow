"""
Tone Model - Advanced Tone/Voice Adaptation
Ported from legacy_engines/content_quality_enhancements.py

Applies sophisticated tone adjustments to content based on
persona configurations, including word choice, sentence structure,
and formality adaptations.
"""

import logging
import re
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ToneType(Enum):
    """Types of tone for content"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CONFIDENT = "confident"
    EMPATHETIC = "empathetic"
    AUTHORITATIVE = "authoritative"
    CASUAL = "casual"
    FORMAL = "formal"
    PERSUASIVE = "persuasive"


class FormalityLevel(Enum):
    """Formality levels"""
    VERY_FORMAL = "very_formal"
    FORMAL = "formal"
    NEUTRAL = "neutral"
    INFORMAL = "informal"
    CASUAL = "casual"


@dataclass
class ToneProfile:
    """Configuration for tone adaptation"""
    tone_type: ToneType
    formality_level: FormalityLevel
    confidence_level: float  # 0-1
    warmth_level: float  # 0-1
    word_choices: Dict[str, str] = field(default_factory=dict)
    sentence_patterns: List[str] = field(default_factory=list)
    avoid_patterns: List[str] = field(default_factory=list)


@dataclass
class ToneAdaptation:
    """Result of tone adaptation"""
    original_content: str
    adapted_content: str
    tone_profile: ToneProfile
    changes_made: List[str]
    adaptation_confidence: float
    word_replacements: int = 0
    structure_changes: int = 0


class AdvancedToneModel:
    """
    Advanced Tone/Voice Adaptation Model
    
    Applies sophisticated tone adjustments to content based on
    persona configurations, including word choice, sentence structure,
    and formality adaptations.
    """
    
    def __init__(self):
        """Initialize tone model with default configurations."""
        self.tone_profiles = self._load_default_profiles()
        self.word_mappings = self._load_word_mappings()
        self.formality_patterns = self._load_formality_patterns()
    
    def adapt_tone(
        self,
        content: str,
        target_tone: ToneType,
        formality: FormalityLevel = FormalityLevel.NEUTRAL,
        context: Optional[Dict[str, object]] = None
    ) -> ToneAdaptation:
        """
        Adapt content to target tone and formality.
        
        Args:
            content: Original content
            target_tone: Target tone type
            formality: Target formality level
            context: Additional context
            
        Returns:
            ToneAdaptation with adapted content
        """
        context = context or {}
        changes_made = []
        
        # Get or create tone profile
        profile = self._get_tone_profile(target_tone, formality, context)
        
        adapted_content = content
        word_replacements = 0
        structure_changes = 0
        
        # Apply word choice adaptations
        adapted_content, word_count = self._apply_word_choices(adapted_content, profile)
        word_replacements = word_count
        if word_count > 0:
            changes_made.append(f"Replaced {word_count} words for tone alignment")
        
        # Apply formality adjustments
        adapted_content, formality_count = self._apply_formality_adjustments(
            adapted_content, formality
        )
        if formality_count > 0:
            changes_made.append(f"Made {formality_count} formality adjustments")
            structure_changes += formality_count
        
        # Apply sentence structure adaptations
        adapted_content, structure_count = self._apply_sentence_structure(
            adapted_content, profile
        )
        if structure_count > 0:
            changes_made.append(f"Adjusted {structure_count} sentence structures")
            structure_changes += structure_count
        
        # Apply confidence adjustments
        if profile.confidence_level > 0.7:
            adapted_content, confidence_count = self._boost_confidence(adapted_content)
            if confidence_count > 0:
                changes_made.append(f"Enhanced confidence in {confidence_count} phrases")
        
        # Apply warmth adjustments
        if profile.warmth_level > 0.6:
            adapted_content, warmth_count = self._add_warmth(adapted_content)
            if warmth_count > 0:
                changes_made.append(f"Added warmth to {warmth_count} phrases")
        
                adapted_content, removed_count = self._remove_avoided_patterns(adapted_content, profile)
        if removed_count > 0:
            changes_made.append(f"Removed {removed_count} inappropriate patterns")
        
        # Calculate adaptation confidence
        adaptation_confidence = self._calculate_adaptation_confidence(
            content, adapted_content, changes_made
        )
        
        logger.info(f"Tone adaptation complete: {len(changes_made)} changes, confidence={adaptation_confidence:.2f}")
        
        return ToneAdaptation(
            original_content=content,
            adapted_content=adapted_content,
            tone_profile=profile,
            changes_made=changes_made,
            adaptation_confidence=adaptation_confidence,
            word_replacements=word_replacements,
            structure_changes=structure_changes
        )
    
    def _get_tone_profile(
        self,
        tone_type: ToneType,
        formality: FormalityLevel,
        context: Dict[str, object]
    ) -> ToneProfile:
        """Get or create tone profile for target tone."""
        base_profile = self.tone_profiles.get(tone_type)
        
        if base_profile:
            # Clone and adjust for formality
            return ToneProfile(
                tone_type=tone_type,
                formality_level=formality,
                confidence_level=base_profile.confidence_level,
                warmth_level=base_profile.warmth_level,
                word_choices=base_profile.word_choices.copy(),
                sentence_patterns=base_profile.sentence_patterns.copy(),
                avoid_patterns=base_profile.avoid_patterns.copy()
            )
        
        # Create default profile
        return ToneProfile(
            tone_type=tone_type,
            formality_level=formality,
            confidence_level=0.7,
            warmth_level=0.5
        )
    
    def _apply_word_choices(
        self,
        content: str,
        profile: ToneProfile
    ) -> tuple[str, int]:
        """Apply word choice adaptations."""
        adapted = content
        replacement_count = 0
        
        # Get word mappings for this tone
        mappings = self.word_mappings.get(profile.tone_type, {})
        mappings.update(profile.word_choices)
        
        for original, replacement in mappings.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            matches = len(re.findall(pattern, adapted, re.IGNORECASE))
            if matches > 0:
                adapted = re.sub(pattern, replacement, adapted, flags=re.IGNORECASE)
                replacement_count += matches
        
        return adapted, replacement_count
    
    def _apply_formality_adjustments(
        self,
        content: str,
        formality: FormalityLevel
    ) -> tuple[str, int]:
        """Apply formality-based adjustments."""
        adapted = content
        adjustment_count = 0
        
        patterns = self.formality_patterns.get(formality, {})
        
        # Contraction handling
        if formality in [FormalityLevel.VERY_FORMAL, FormalityLevel.FORMAL]:
            # Expand contractions
            contractions = {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "shouldn't": "should not",
                "wouldn't": "would not",
                "couldn't": "could not",
                "isn't": "is not",
                "aren't": "are not",
                "wasn't": "was not",
                "weren't": "were not",
                "haven't": "have not",
                "hasn't": "has not",
                "hadn't": "had not",
                "I'm": "I am",
                "you're": "you are",
                "we're": "we are",
                "they're": "they are",
                "it's": "it is",
                "that's": "that is",
                "there's": "there is",
                "here's": "here is",
                "what's": "what is",
                "who's": "who is",
                "let's": "let us"
            }
            
            for contraction, expansion in contractions.items():
                pattern = r'\b' + re.escape(contraction) + r'\b'
                matches = len(re.findall(pattern, adapted, re.IGNORECASE))
                if matches > 0:
                    adapted = re.sub(pattern, expansion, adapted, flags=re.IGNORECASE)
                    adjustment_count += matches
        
        elif formality in [FormalityLevel.INFORMAL, FormalityLevel.CASUAL]:
            # Add contractions where appropriate
            expansions = {
                "do not": "don't",
                "will not": "won't",
                "cannot": "can't",
                "should not": "shouldn't",
                "would not": "wouldn't",
                "could not": "couldn't",
                "is not": "isn't",
                "are not": "aren't",
                "I am": "I'm",
                "you are": "you're",
                "we are": "we're",
                "they are": "they're",
                "it is": "it's"
            }
            
            for expansion, contraction in expansions.items():
                pattern = r'\b' + re.escape(expansion) + r'\b'
                matches = len(re.findall(pattern, adapted, re.IGNORECASE))
                if matches > 0:
                    adapted = re.sub(pattern, contraction, adapted, flags=re.IGNORECASE)
                    adjustment_count += matches
        
        return adapted, adjustment_count
    
    def _apply_sentence_structure(
        self,
        content: str,
        profile: ToneProfile
    ) -> tuple[str, int]:
        """Apply sentence structure adaptations."""
        adapted = content
        change_count = 0
        
        # Apply sentence patterns from profile
        for pattern in profile.sentence_patterns:
            # Pattern application logic would go here
            pass
        
        return adapted, change_count
    
    def _boost_confidence(self, content: str) -> tuple[str, int]:
        """Boost confidence in language."""
        adapted = content
        boost_count = 0
        
        # Replace hedging language with confident alternatives
        hedging_replacements = {
            "I think": "I believe",
            "maybe": "likely",
            "perhaps": "certainly",
            "might be able to": "can",
            "could possibly": "will",
            "I guess": "I'm confident",
            "sort of": "",
            "kind of": "",
            "a little bit": "",
            "somewhat": ""
        }
        
        for hedge, confident in hedging_replacements.items():
            pattern = r'\b' + re.escape(hedge) + r'\b'
            matches = len(re.findall(pattern, adapted, re.IGNORECASE))
            if matches > 0:
                adapted = re.sub(pattern, confident, adapted, flags=re.IGNORECASE)
                boost_count += matches
        
        # Clean up extra spaces
        adapted = re.sub(r'\s+', ' ', adapted).strip()
        
        return adapted, boost_count
    
    def _add_warmth(self, content: str) -> tuple[str, int]:
        """Add warmth to language."""
        adapted = content
        warmth_count = 0
        
        # Replace cold language with warmer alternatives
        warmth_replacements = {
            "You must": "I'd encourage you to",
            "You need to": "You might want to",
            "You should": "I'd suggest",
            "It is required": "It would be helpful",
            "You are required": "You're invited",
            "immediately": "at your earliest convenience"
        }
        
        for cold, warm in warmth_replacements.items():
            pattern = r'\b' + re.escape(cold) + r'\b'
            matches = len(re.findall(pattern, adapted, re.IGNORECASE))
            if matches > 0:
                adapted = re.sub(pattern, warm, adapted, flags=re.IGNORECASE)
                warmth_count += matches
        
        return adapted, warmth_count
    
    def _remove_avoided_patterns(
        self,
        content: str,
        profile: ToneProfile
    ) -> tuple[str, int]:
        """Remove patterns that should be avoided."""
        adapted = content
        removed_count = 0
        
        for pattern in profile.avoid_patterns:
            try:
                matches = len(re.findall(pattern, adapted, re.IGNORECASE))
                if matches > 0:
                    adapted = re.sub(pattern, '', adapted, flags=re.IGNORECASE)
                    removed_count += matches
            except re.error:
                pass
        
        # Clean up extra spaces
        adapted = re.sub(r'\s+', ' ', adapted).strip()
        
        return adapted, removed_count
    
    def _calculate_adaptation_confidence(
        self,
        original: str,
        adapted: str,
        changes: List[str]
    ) -> float:
        """Calculate confidence in adaptation quality."""
        if original == adapted:
            return 1.0 if not changes else 0.5
        
        # Base confidence
        confidence = 0.8
        
        # Adjust based on number of changes
        if len(changes) > 5:
            confidence -= 0.1
        
        # Adjust based on content length change
        length_ratio = len(adapted) / len(original) if original else 1.0
        if length_ratio < 0.8 or length_ratio > 1.2:
            confidence -= 0.1
        
        return max(0.3, min(1.0, confidence))
    
    def _load_default_profiles(self) -> Dict[ToneType, ToneProfile]:
        """Load default tone profiles."""
        return {
            ToneType.PROFESSIONAL: ToneProfile(
                tone_type=ToneType.PROFESSIONAL,
                formality_level=FormalityLevel.FORMAL,
                confidence_level=0.8,
                warmth_level=0.5,
                avoid_patterns=[r'\b(awesome|cool|amazing)\b']
            ),
            ToneType.FRIENDLY: ToneProfile(
                tone_type=ToneType.FRIENDLY,
                formality_level=FormalityLevel.INFORMAL,
                confidence_level=0.7,
                warmth_level=0.9,
                word_choices={"Hello": "Hi", "Greetings": "Hey"}
            ),
            ToneType.CONFIDENT: ToneProfile(
                tone_type=ToneType.CONFIDENT,
                formality_level=FormalityLevel.NEUTRAL,
                confidence_level=0.95,
                warmth_level=0.6
            ),
            ToneType.EMPATHETIC: ToneProfile(
                tone_type=ToneType.EMPATHETIC,
                formality_level=FormalityLevel.NEUTRAL,
                confidence_level=0.6,
                warmth_level=0.95
            ),
            ToneType.AUTHORITATIVE: ToneProfile(
                tone_type=ToneType.AUTHORITATIVE,
                formality_level=FormalityLevel.FORMAL,
                confidence_level=0.9,
                warmth_level=0.4
            )
        }
    
    def _load_word_mappings(self) -> Dict[ToneType, Dict[str, str]]:
        """Load word mappings for different tones."""
        return {
            ToneType.PROFESSIONAL: {
                "get": "obtain",
                "use": "utilize",
                "help": "assist",
                "need": "require",
                "show": "demonstrate",
                "find": "identify",
                "make": "create",
                "big": "significant",
                "good": "excellent",
                "bad": "suboptimal"
            },
            ToneType.FRIENDLY: {
                "obtain": "get",
                "utilize": "use",
                "assist": "help",
                "require": "need",
                "demonstrate": "show",
                "identify": "find",
                "significant": "big",
                "excellent": "great",
                "suboptimal": "not great"
            },
            ToneType.CONFIDENT: {
                "might": "will",
                "could": "can",
                "possibly": "definitely",
                "perhaps": "certainly"
            }
        }
    
    def _load_formality_patterns(self) -> Dict[FormalityLevel, Dict[str, object]]:
        """Load formality-specific patterns."""
        return {
            FormalityLevel.VERY_FORMAL: {
                "use_titles": True,
                "avoid_contractions": True,
                "use_passive_voice": True
            },
            FormalityLevel.FORMAL: {
                "use_titles": True,
                "avoid_contractions": True,
                "use_passive_voice": False
            },
            FormalityLevel.NEUTRAL: {
                "use_titles": False,
                "avoid_contractions": False,
                "use_passive_voice": False
            },
            FormalityLevel.INFORMAL: {
                "use_titles": False,
                "avoid_contractions": False,
                "use_passive_voice": False
            },
            FormalityLevel.CASUAL: {
                "use_titles": False,
                "avoid_contractions": False,
                "use_passive_voice": False
            }
        }


# Factory functions
def create_tone_model() -> AdvancedToneModel:
    """Create tone model instance."""
    return AdvancedToneModel()


def adapt_tone(
    content: str,
    target_tone: ToneType,
    formality: FormalityLevel = FormalityLevel.NEUTRAL
) -> ToneAdaptation:
    """Convenience function to adapt content tone."""
    model = AdvancedToneModel()
    return model.adapt_tone(content, target_tone, formality)
