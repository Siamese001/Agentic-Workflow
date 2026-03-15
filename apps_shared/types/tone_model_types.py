"""Advanced Tone Model - Emotional Brain for AI Communication.

This module provides tone analysis and adaptation capabilities to humanize AI
generation by analyzing recipient communication styles and calibrating the agent's
voice to match, preventing the "Generic AI" voice.

# guardian: allow-magic-config
"""

import logging
import re
from enum import Enum

from pydantic import BaseModel, Field, confloat, validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class ToneType(str, Enum):
    """Primary tone types for communication style analysis."""

    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    ENTHUSIASTIC = "enthusiastic"
    DIRECT = "direct"


class StyleProfile(BaseModel):
    """Profile defining a communication style."""

    primary_tone: ToneType = Field(..., description="Primary tone type")
    formality_level: confloat(ge=0.0, le=1.0) = Field(
        default=0.7, description="Formality level (0=Casual, 1=Academic)"
    )
    emoji_frequency: confloat(ge=0.0, le=1.0) = Field(default=0.2, description="Emoji usage frequency")
    sentence_length_avg: int = Field(default=15, ge=5, le=50, description="Target words per sentence")
    vocabulary_complexity: confloat(ge=0.0, le=1.0) = Field(default=0.5, description="Vocabulary complexity")
    confidence_level: confloat(ge=0.0, le=1.0) = Field(default=0.8, description="Confidence in analysis")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class GenerationConfig(BaseModel):
    """configuration for LLM generation based on tone profile."""

    system_prompt_fragment: str = Field(..., description="Instruction to inject into prompts")
    temperature_setting: confloat(ge=0.1, le=1.0) = Field(..., description="LLM temperature")
    banned_phrases: list[str] = Field(default_factory=list, description="Phrases to avoid")
    preferred_transitions: list[str] = Field(default_factory=list, description="Preferred transition words")
    max_sentence_length: int = Field(default=25, ge=5, le=100, description="Max words per sentence")

    @validator("temperature_setting")
    def clamp_temperature(cls, v):
        """Ensure temperature is within valid range."""
        return max(0.1, min(1.0, v))


class ToneAnalyzer:
    """Analyzes communication style from content samples."""

    # guardian: allow-magic-config
    def __init__(self, min_sample_length: int = 50):
        """Initialize the tone analyzer.

        Args:
            min_sample_length: Minimum characters for valid analysis
        """
        self.min_sample_length = min_sample_length
        self.tone_keywords = {
            ToneType.AUTHORITATIVE: [
                "expert",
                "leader",
                "strategy",
                "vision",
                "decisive",
                "results",
                "execution",
                "accountability",
                "ownership",
                "leadership",
            ],
            ToneType.EMPATHETIC: [
                "understand",
                "support",
                "team",
                "people",
                "culture",
                "values",
                "together",
                "collaborate",
                "community",
                "care",
            ],
            ToneType.ANALYTICAL: [
                "data",
                "analysis",
                "metrics",
                "research",
                "study",
                "findings",
                "evidence",
                "statistics",
                "trends",
                "insights",
            ],
            ToneType.ENTHUSIASTIC: [
                "excited",
                "amazing",
                "awesome",
                "love",
                "fantastic",
                "incredible",
                "thrilled",
                "passionate",
                "energy",
                "opportunity",
            ],
            ToneType.DIRECT: [
                "action",
                "implement",
                "execute",
                "deliver",
                "achieve",
                "complete",
                "done",
                "focus",
                "priority",
                "result",
            ],
        }
        self.formal_indicators = ["furthermore", "moreover", "consequently", "therefore"]
        self.casual_indicators = ["hey", "yeah", "cool", "awesome", "btw"]
        logger.info(f"Initialized ToneAnalyzer with min_sample_length={min_sample_length}")

    def analyze_style(self, content_samples: list[str]) -> StyleProfile:
        """Analyze communication style from content samples.

        Args:
            content_samples: List of text samples to analyze

        Returns:
            StyleProfile with detected characteristics
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "StyleAnalyzer.analyze_style")
        try:
            if not content_samples or not isinstance(content_samples, list):
                logger.warning("Empty or invalid content samples, returning neutral profile")
                return self._get_neutral_profile()
            combined_text = " ".join(str(s) for s in content_samples if s)
            combined_text = combined_text.strip()
            if len(combined_text) < self.min_sample_length:
                logger.warning(
                    f"Insufficient content length ({len(combined_text)}), returning neutral profile"
                )
                return self._get_neutral_profile()
            metrics = self._calculate_metrics(combined_text)
            primary_tone = self._detect_primary_tone(combined_text, metrics)
            formality = self._calculate_formality(combined_text, metrics)
            emoji_freq = self._calculate_emoji_frequency(combined_text)
            vocab_complexity = self._calculate_vocabulary_complexity(combined_text)
            profile = StyleProfile(
                primary_tone=primary_tone,
                formality_level=formality,
                emoji_frequency=emoji_freq,
                sentence_length_avg=metrics["avg_sentence_length"],
                vocabulary_complexity=vocab_complexity,
                confidence_level=metrics["confidence"],
            )
            logger.info(
                f"Analyzed tone: {primary_tone.value} (confidence: {metrics['confidence']:.2f})",
                extra={"tone": primary_tone.value, "confidence": metrics["confidence"]},
            )
            return profile
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error analyzing style: {str(e)}")
            return self._get_neutral_profile()

    def _get_neutral_profile(self) -> StyleProfile:
        """Get a neutral/default style profile."""
        return StyleProfile(
            primary_tone=ToneType.AUTHORITATIVE,
            formality_level=0.7,
            emoji_frequency=0.1,
            sentence_length_avg=15,
            vocabulary_complexity=0.5,
            confidence_level=0.3,
        )

    def _calculate_metrics(self, text: str) -> dict[str, float]:
        """Calculate basic text metrics.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of calculated metrics
        """
        try:
            sentences = re.split("[.!?]+", text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                return {
                    "avg_sentence_length": 15,
                    "exclamation_ratio": 0,
                    "question_ratio": 0,
                    "confidence": 0.0,
                }
            word_counts = [len(s.split()) for s in sentences]
            avg_sentence_length = sum(word_counts) / len(word_counts)
            exclamation_count = text.count("!")
            question_count = text.count("?")
            total_sentences = len(sentences)
            exclamation_ratio = exclamation_count / max(total_sentences, 1)
            question_ratio = question_count / max(total_sentences, 1)
            confidence = min(1.0, len(text) / 1000)
            return {
                "avg_sentence_length": avg_sentence_length,
                "exclamation_ratio": exclamation_ratio,
                "question_ratio": question_ratio,
                "confidence": confidence,
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {"avg_sentence_length": 15, "exclamation_ratio": 0, "question_ratio": 0, "confidence": 0.0}

    def _detect_primary_tone(self, text: str, metrics: dict[str, float]) -> ToneType:
        """Detect the primary tone from text and metrics.

        Args:
            text: Text to analyze
            metrics: Pre-calculated metrics

        Returns:
            Detected primary tone
        """
        try:
            text_lower = text.lower()
            tone_scores = {}
            for tone, keywords in self.tone_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                tone_scores[tone] = score
            if metrics["exclamation_ratio"] > 0.2:
                tone_scores[ToneType.ENTHUSIASTIC] += 2
            if metrics["avg_sentence_length"] > 20:
                tone_scores[ToneType.ANALYTICAL] += 1
            elif metrics["avg_sentence_length"] < 10:
                tone_scores[ToneType.DIRECT] += 2
            if metrics["question_ratio"] > 0.1:
                tone_scores[ToneType.EMPATHETIC] += 1
            if not tone_scores or max(tone_scores.values()) == 0:
                return ToneType.AUTHORITATIVE
            return max(tone_scores, key=tone_scores.get)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error detecting primary tone: {str(e)}")
            return ToneType.AUTHORITATIVE

    def _calculate_formality(self, text: str, metrics: dict[str, float]) -> float:
        """Calculate formality level (0.0 = casual, 1.0 = academic).

        Args:
            text: Text to analyze
            metrics: Pre-calculated metrics

        Returns:
            Formality level
        """
        try:
            text_lower = text.lower()
            formal_count = sum(1 for word in self.formal_indicators if word in text_lower)
            casual_count = sum(1 for word in self.casual_indicators if word in text_lower)
            length_factor = min(1.0, metrics["avg_sentence_length"] / 20)
            if formal_count > casual_count:
                indicator_factor = 0.8
            elif casual_count > 0:
                indicator_factor = 0.3
            else:
                indicator_factor = 0.5
            formality = length_factor * 0.6 + indicator_factor * 0.4
            return max(0.0, min(1.0, formality))
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error calculating formality: {str(e)}")
            return 0.7

    def _calculate_emoji_frequency(self, text: str) -> float:
        """Calculate emoji usage frequency.

        Args:
            text: Text to analyze

        Returns:
            Emoji frequency (0.0 = never, 1.0 = every sentence)
        """
        try:
            emoji_pattern = re.compile("[😀-🙏🌀-🗿🚀-\U0001f6ff\U0001f1e0-🇿☀-⛿✀-➿]+")
            emoji_count = len(emoji_pattern.findall(text))
            sentence_count = len(re.split("[.!?]+", text))
            if sentence_count == 0:
                return 0.0
            frequency = emoji_count / sentence_count
            return min(1.0, frequency)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error calculating emoji frequency: {str(e)}")
            return 0.1

    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity.

        Args:
            text: Text to analyze

        Returns:
            Complexity score (0.0 = simple, 1.0 = jargon-heavy)
        """
        try:
            words = text.lower().split()
            if not words:
                return 0.5
            avg_word_length = sum(len(word) for word in words) / len(words)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_ratio = complex_words / len(words)
            complexity = avg_word_length / 10 * 0.4 + complex_ratio * 0.6
            return max(0.0, min(1.0, complexity))
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error calculating vocabulary complexity: {str(e)}")
            return 0.5


class ToneAdapter:
    """Adapts messages to match target tone profile."""

    def __init__(self):
        """Initialize the tone adapter."""
        self.adaptation_rules = {
            ToneType.DIRECT: {
                "remove_patterns": [
                    "\\b(?:in order to|in an effort to|for the purpose of)\\b",
                    "\\b(?:very|quite|rather|extremely)\\s+\\w+",
                    "\\b(?:it is important to note that|it should be mentioned that)\\b",
                ],
                "replacements": {
                    "utilize": "use",
                    "facilitate": "help",
                    "leverage": "use",
                    "optimize": "improve",
                    "implement": "do",
                    "strategize": "plan",
                },
            },
            ToneType.ENTHUSIASTIC: {
                "add_transitions": ["Absolutely!", "Fantastic!", "What's great is", "Excited to"],
                "emoji_places": ["greeting", "closing"],
            },
            ToneType.ANALYTICAL: {
                "add_transitions": ["Based on the data,", "The evidence suggests,", "Analysis indicates,"],
                "require_evidence": True,
            },
            ToneType.EMPATHETIC: {
                "add_openers": ["I understand that", "Recognizing that", "Appreciating that"],
                "soften_language": True,
            },
        }
        logger.info("Initialized ToneAdapter with adaptation rules")

    def adapt_message(self, draft: str, target_profile: StyleProfile) -> str:
        """Adapt a draft message to match the target tone profile.

        Args:
            draft: Original draft message
            target_profile: Target tone profile to match

        Returns:
            Adapted message
        """
        try:
            if not draft or not isinstance(draft, str):
                logger.warning("Invalid draft message")
                return draft or ""
            adapted = draft
            tone = target_profile.primary_tone
            if tone in self.adaptation_rules:
                rules = self.adaptation_rules[tone]
                if "remove_patterns" in rules:
                    for pattern in rules["remove_patterns"]:
                        adapted = re.sub(pattern, "", adapted, flags=re.IGNORECASE)
                if "replacements" in rules:
                    for old, new in rules["replacements"].items():
                        adapted = re.sub(f"\\b{old}\\b", new, adapted, flags=re.IGNORECASE)
                if "add_transitions" in rules and adapted.count(".") > 1:
                    sentences = adapted.split(".")
                    if len(sentences) > 1:
                        transition = rules["add_transitions"][0]
                        sentences[0] = f"{transition} {sentences[0].strip()}"
                        adapted = ". ".join(sentences)
                if target_profile.sentence_length_avg < 15:
                    adapted = self._shorten_sentences(adapted)
                elif target_profile.sentence_length_avg > 20:
                    adapted = self._lengthen_sentences(adapted)
            adapted = re.sub("\\s+", " ", adapted).strip()
            logger.debug(f"Adapted message for tone: {tone.value}")
            return adapted
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error adapting message: {str(e)}")
            return draft

    def _shorten_sentences(self, text: str) -> str:
        """Shorten sentences for more direct communication."""
        try:
            sentences = re.split("[.!?]+", text)
            shortened = []
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                words = sentence.split()
                if len(words) > 12:
                    mid = len(words) // 2
                    shortened.append(" ".join(words[:mid]))
                    shortened.append(" ".join(words[mid:]))
                else:
                    shortened.append(sentence)
            return ". ".join(shortened)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error shortening sentences: {str(e)}")
            return text

    def _lengthen_sentences(self, text: str) -> str:
        """Lengthen sentences for more analytical communication."""
        try:
            connectors = ["which means that", "indicating that", "suggesting that"]
            sentences = text.split(".")
            for i in range(len(sentences) - 1):
                if len(sentences[i].split()) < 8 and len(sentences[i + 1].split()) < 8:
                    connector = connectors[i % len(connectors)]
                    sentences[i] = f"{sentences[i].strip()} {connector}"
            return ". ".join(sentences)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error lengthening sentences: {str(e)}")
            return text


class ToneModel:
    """Main tone model that combines analysis and configuration."""

    def __init__(self):
        """Initialize the tone model."""
        self.analyzer = ToneAnalyzer()
        self.adapter = ToneAdapter()
        # guardian: allow-magic-config
        self.config_templates = {
            ToneType.AUTHORITATIVE: GenerationConfig(
                system_prompt_fragment="Use confident, expert language. Lead with insights. Be decisive and clear.",
                temperature_setting=0.4,
                banned_phrases=["maybe", "perhaps", "might", "could", "I think"],
                preferred_transitions=["Therefore", "Consequently", "Based on"],
                max_sentence_length=20,
            ),
            ToneType.EMPATHETIC: GenerationConfig(
                system_prompt_fragment="Use supportive, understanding language. Focus on people and values. Show genuine care.",
                temperature_setting=0.6,
                banned_phrases=["must", "require", "mandatory", "failure"],
                preferred_transitions=["Understanding that", "Recognizing that", "Appreciating that"],
                max_sentence_length=18,
            ),
            ToneType.ANALYTICAL: GenerationConfig(
                system_prompt_fragment="Use data-driven, logical language. Provide evidence and reasoning. Be thorough.",
                temperature_setting=0.3,
                banned_phrases=["feel", "believe", "intuition", "gut"],
                preferred_transitions=["According to", "Based on", "Analysis shows"],
                max_sentence_length=25,
            ),
            ToneType.ENTHUSIASTIC: GenerationConfig(
                system_prompt_fragment="Use energetic, positive language. Express excitement and possibility. Be engaging.",
                temperature_setting=0.7,
                banned_phrases=["problem", "issue", "challenge", "difficult"],
                preferred_transitions=["Excited to", "Thrilled about", "What's great is"],
                max_sentence_length=15,
            ),
            ToneType.DIRECT: GenerationConfig(
                system_prompt_fragment="Use concise, action-oriented language. Be clear and specific. No fluff.",
                temperature_setting=0.3,
                banned_phrases=["delve", "tapestry", "journey", "utilize", "facilitate"],
                preferred_transitions=["Next", "Then", "After that"],
                max_sentence_length=12,
            ),
        }
        logger.info("Initialized ToneModel with all components")

    def analyze_and_configure(
        self, content_samples: list[str], archetype: str | None = None
    ) -> tuple[StyleProfile, GenerationConfig]:
        """Analyze content and generate configuration.

        Args:
            content_samples: Content samples to analyze
            archetype: Optional recipient archetype

        Returns:
            Tuple of (StyleProfile, GenerationConfig)
        """
        try:
            profile = self.analyzer.analyze_style(content_samples)
            config = self.config_templates.get(
                profile.primary_tone, self.config_templates[ToneType.AUTHORITATIVE]
            )
            if profile.formality_level > 0.8:
                config.temperature_setting = max(0.1, config.temperature_setting - 0.1)
            elif profile.formality_level < 0.4:
                config.temperature_setting = min(1.0, config.temperature_setting + 0.1)
            if archetype:
                config = self._adjust_for_archetype(config, archetype)
            logger.info(
                f"Generated config for tone {profile.primary_tone.value} with temperature {config.temperature_setting}"
            )
            return (profile, config)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error in analyze_and_configure: {str(e)}")
            return (self.analyzer._get_neutral_profile(), self.config_templates[ToneType.AUTHORITATIVE])

    def _adjust_for_archetype(self, config: GenerationConfig, archetype: str) -> GenerationConfig:
        """Adjust configuration based on recipient archetype.

        Args:
            config: Base configuration
            archetype: Recipient archetype

        Returns:
            Adjusted configuration
        """
        try:
            archetype_lower = archetype.lower()
            if any(role in archetype_lower for role in ["cto", "vp engineering", "technical"]):
                config.temperature_setting = max(0.2, config.temperature_setting - 0.1)
                config.system_prompt_fragment += " Include technical details and metrics."
            elif any(role in archetype_lower for role in ["ceo", "founder", "executive"]):
                config.temperature_setting = min(0.6, config.temperature_setting + 0.1)
                config.system_prompt_fragment += " Focus on business impact and strategic vision."
            elif any(role in archetype_lower for role in ["recruiter", "hr", "talent"]):
                config.temperature_setting = min(0.7, config.temperature_setting + 0.1)
                config.system_prompt_fragment += " Emphasize culture and human connection."
            return config
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error adjusting for archetype: {str(e)}")
            return config


def create_tone_model() -> ToneModel:
    """Create a ToneModel instance."""
    return ToneModel()


def analyze_tone(content_samples: list[str]) -> StyleProfile:
    """Quickly analyze tone from content samples."""
    analyzer = ToneAnalyzer()
    return analyzer.analyze_style(content_samples)


def adapt_to_tone(draft: str, target_profile: StyleProfile) -> str:
    """Quickly adapt a message to a target tone."""
    adapter = ToneAdapter()
    return adapter.adapt_message(draft, target_profile)
