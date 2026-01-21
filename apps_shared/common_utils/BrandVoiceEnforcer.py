"""Brand Voice Enforcer - Ensures consistent personal brand across all engines.

This module enforces linguistic constraints (sentence length, vocabulary,
active voice) across all generated text in both Resume and Outreach engines.
"""

import logging
import re
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToneVoice(str, Enum):
    """Primary voice types for brand consistency."""

    AUTHORITATIVE = "AUTHORITATIVE"  # "Led", "Drove", "Built"
    COLLABORATIVE = "COLLABORATIVE"  # "Partnered", "Enabled", "Supported"
    TECHNICAL = "TECHNICAL"  # High jargon density
    EXECUTIVE = "EXECUTIVE"  # Strategic, high-level
    CREATIVE = "CREATIVE"  # Innovative, visionary


class ToneSettings(BaseModel):
    """Settings for tone enforcement."""

    primary_voice: ToneVoice
    max_sentence_length: int = Field(default=25, ge=5, le=100)
    min_sentence_length: int = Field(default=5, ge=1, le=20)
    banned_words: list[str] = Field(default_factory=list)
    required_keywords: list[str] = Field(default_factory=list)
    preferred_verbs: dict[str, list[str]] = Field(default_factory=dict)
    voice_intensity: float = Field(default=0.8, ge=0.0, le=1.0)
    formality_level: str = Field(default="professional")  # casual, professional, formal
    max_passive_voice_percent: float = Field(default=20.0, ge=0.0, le=100.0)


class ToneViolation(BaseModel):
    """A tone rule violation."""

    type: str  # e.g., "sentence_length", "banned_word", "passive_voice"
    severity: str  # "error", "warning", "info"
    message: str
    location: str | None = None  # Text snippet where violation occurred
    suggestion: str | None = None


class ToneAnalysisResult(BaseModel):
    """Result of tone analysis."""

    is_compliant: bool
    violations: list[ToneViolation] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)  # Overall compliance score
    voice_detected: ToneVoice | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class ToneEnforcer:
    """Enforces tone rules across generated content."""

    def __init__(self):
        """Initialize tone enforcer with default profiles."""
        # Default tone profiles
        self.profiles: dict[ToneVoice, ToneSettings] = self._create_default_profiles()

        # Voice-specific patterns
        self.voice_patterns = {
            ToneVoice.AUTHORITATIVE: {
                "verbs": ["led", "drove", "built", "created", "established", "pioneered"],
                "patterns": [r"\bled\b", r"\bdrove\b", r"\bbuilt\b"],
                "avoid": ["helped", "assisted", "participated"],
            },
            ToneVoice.COLLABORATIVE: {
                "verbs": ["partnered", "enabled", "supported", "collaborated", "facilitated"],
                "patterns": [r"\bpartnered\b", r"\benabled\b", r"\bsupported\b"],
                "avoid": ["controlled", "dictated", "commanded"],
            },
            ToneVoice.TECHNICAL: {
                "terms": ["architecture", "scalability", "optimization", "infrastructure"],
                "patterns": [r"\bimplement\b", r"\boptimize\b", r"\barchitect\b"],
                "avoid": ["simple", "easy", "basic"],
            },
            ToneVoice.EXECUTIVE: {
                "verbs": ["strategized", "orchestrated", "spearheaded", "directed"],
                "patterns": [r"\bstrategized\b", r"\borchestrated\b"],
                "avoid": ["executed", "performed", "completed"],
            },
            ToneVoice.CREATIVE: {
                "verbs": ["innovated", "envisioned", "imagined", "designed"],
                "patterns": [r"\binnovated\b", r"\benvisioned\b"],
                "avoid": ["maintained", "preserved", "followed"],
            },
        }

        # Passive voice indicators
        self.passive_patterns = [
            r"\b(was|were|is|are|am|been|being)\s+\w+ed\b",
            r"\b(was|were|is|are|am|been|being)\s+\w+en\b",
            r"\b\w+ed\s+by\s+the\b",
            r"\b\w+ed\s+by\s+\w+\b",
        ]

        logger.info("Initialized ToneEnforcer with default profiles")

    def _create_default_profiles(self) -> dict[ToneVoice, ToneSettings]:
        """Create default tone profiles.

        Returns:
            Dictionary of tone settings by voice
        """
        return {
            ToneVoice.AUTHORITATIVE: ToneSettings(
                primary_voice=ToneVoice.AUTHORITATIVE,
                max_sentence_length=20,
                banned_words=["helped", "assisted", "participated", "contributed"],
                required_keywords=["led", "drove", "built"],
                preferred_verbs={
                    "leadership": ["led", "directed", "managed", "orchestrated"],
                    "creation": ["built", "created", "developed", "established"],
                    "impact": ["drove", "achieved", "delivered", "produced"],
                },
                max_passive_voice_percent=10.0,
            ),
            ToneVoice.COLLABORATIVE: ToneSettings(
                primary_voice=ToneVoice.COLLABORATIVE,
                max_sentence_length=25,
                banned_words=["controlled", "dictated", "commanded", "forced"],
                required_keywords=["partnered", "enabled", "collaborated"],
                preferred_verbs={
                    "teamwork": ["partnered", "collaborated", "teamed", "cooperated"],
                    "support": ["enabled", "supported", "facilitated", "empowered"],
                    "guidance": ["mentored", "guided", "advised", "coached"],
                },
                max_passive_voice_percent=15.0,
            ),
            ToneVoice.TECHNICAL: ToneSettings(
                primary_voice=ToneVoice.TECHNICAL,
                max_sentence_length=30,
                banned_words=["simple", "easy", "basic", "just"],
                required_keywords=["implemented", "optimized", "architected"],
                preferred_verbs={
                    "development": ["implemented", "developed", "programmed", "coded"],
                    "architecture": ["architected", "designed", "structured", "engineered"],
                    "optimization": ["optimized", "enhanced", "improved", "refined"],
                },
                max_passive_voice_percent=20.0,
            ),
            ToneVoice.EXECUTIVE: ToneSettings(
                primary_voice=ToneVoice.EXECUTIVE,
                max_sentence_length=25,
                banned_words=["executed", "performed", "completed", "finished"],
                required_keywords=["strategized", "orchestrated", "spearheaded"],
                preferred_verbs={
                    "strategy": ["strategized", "planned", "envisioned", "conceptualized"],
                    "leadership": ["orchestrated", "spearheaded", "directed", "guided"],
                    "business": ["drove", "grew", "expanded", "scaled"],
                },
                max_passive_voice_percent=5.0,
            ),
            ToneVoice.CREATIVE: ToneSettings(
                primary_voice=ToneVoice.CREATIVE,
                max_sentence_length=30,
                banned_words=["standard", "typical", "conventional", "traditional"],
                required_keywords=["innovated", "designed", "created"],
                preferred_verbs={
                    "innovation": ["innovated", "pioneered", "invented", "conceived"],
                    "design": ["designed", "crafted", "shaped", "formed"],
                    "vision": ["envisioned", "imagined", "conceptualized", "dreamed"],
                },
                max_passive_voice_percent=25.0,
            ),
        }

    def audit_content(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Audit content for tone violations.

        Args:
            text: Text to audit
            settings: Tone settings to enforce

        Returns:
            List of violations found
        """
        violations = []

        # Check sentence length
        violations.extend(self._check_sentence_length(text, settings))

        # Check banned words
        violations.extend(self._check_banned_words(text, settings))

        # Check required keywords
        violations.extend(self._check_required_keywords(text, settings))

        # Check voice consistency
        violations.extend(self._check_voice_consistency(text, settings))

        # Check passive voice
        violations.extend(self._check_passive_voice(text, settings))

        # Check formality level
        violations.extend(self._check_formality(text, settings))

        return violations

    def _check_sentence_length(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check sentence length violations.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []

        # Split into sentences
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        for sentence in sentences:
            word_count = len(sentence.split())

            if word_count > settings.max_sentence_length:
                violations.append(
                    ToneViolation(
                        type="sentence_length",
                        severity="warning",
                        message=f"Sentence too long: {word_count} words (max: {settings.max_sentence_length})",
                        location=sentence[:50] + "..." if len(sentence) > 50 else sentence,
                        suggestion="Consider breaking into shorter sentences",
                    )
                )

            elif word_count < settings.min_sentence_length:
                violations.append(
                    ToneViolation(
                        type="sentence_length",
                        severity="info",
                        message=f"Sentence too short: {word_count} words (min: {settings.min_sentence_length})",
                        location=sentence,
                        suggestion="Consider expanding with more detail",
                    )
                )

        return violations

    def _check_banned_words(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for banned words.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        text_lower = text.lower()

        for word in settings.banned_words:
            if word.lower() in text_lower:
                # Find word in context
                pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                match = pattern.search(text)

                violations.append(
                    ToneViolation(
                        type="banned_word",
                        severity="error",
                        message=f"Banned word detected: '{word}'",
                        location=match.group() if match else word,
                        suggestion="Replace with stronger alternative",
                    )
                )

        return violations

    def _check_required_keywords(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for required keywords.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        text_lower = text.lower()

        missing_keywords = []
        for keyword in settings.required_keywords:
            if keyword.lower() not in text_lower:
                missing_keywords.append(keyword)

        if missing_keywords:
            violations.append(
                ToneViolation(
                    type="missing_keyword",
                    severity="warning",
                    message=f"Missing required keywords: {', '.join(missing_keywords)}",
                    suggestion="Consider incorporating these keywords",
                )
            )

        return violations

    def _check_voice_consistency(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check voice consistency with primary voice.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        voice = settings.primary_voice

        if voice not in self.voice_patterns:
            return violations

        patterns = self.voice_patterns[voice]
        text_lower = text.lower()

        # Check for preferred patterns
        preferred_found = 0
        for pattern in patterns["patterns"]:
            if re.search(pattern, text_lower):
                preferred_found += 1

        # Check for avoided patterns
        for avoid_word in patterns["avoid"]:
            if avoid_word.lower() in text_lower:
                violations.append(
                    ToneViolation(
                        type="voice_inconsistency",
                        severity="warning",
                        message=f"Voice inconsistency: '{avoid_word}' doesn't match {voice.value} tone",
                        suggestion=f"Use {voice.value} voice alternatives: {', '.join(patterns['verbs'][:3])}",
                    )
                )

        # Check if enough preferred patterns found
        if preferred_found == 0 and len(patterns["patterns"]) > 0:
            violations.append(
                ToneViolation(
                    type="voice_weakness",
                    severity="info",
                    message=f"Weak {voice.value} voice: no preferred patterns detected",
                    suggestion=f"Consider using: {', '.join(patterns['verbs'][:3])}",
                )
            )

        return violations

    def _check_passive_voice(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for excessive passive voice.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []

        # Count sentences
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return violations

        # Count passive voice sentences
        passive_count = 0
        for sentence in sentences:
            for pattern in self.passive_patterns:
                if re.search(pattern, sentence.lower()):
                    passive_count += 1
                    break

        # Calculate percentage
        passive_percent = (passive_count / len(sentences)) * 100

        if passive_percent > settings.max_passive_voice_percent:
            violations.append(
                ToneViolation(
                    type="passive_voice",
                    severity="warning",
                    message=f"Too much passive voice: {passive_percent:.1f}% (max: {settings.max_passive_voice_percent}%)",
                    suggestion="Use more active voice construction",
                )
            )

        return violations

    def _check_formality(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check formality level compliance.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []

        if settings.formality_level == "formal":
            # Check for informal elements
            informal_patterns = [
                r"\bgonna\b",
                r"\bwanna\b",
                r"\bgotta\b",
                r"\bkinda\b",
                r"\bsorta\b",
            ]

            for pattern in informal_patterns:
                if re.search(pattern, text.lower()):
                    violations.append(
                        ToneViolation(
                            type="formality",
                            severity="warning",
                            message="Informal language detected in formal tone",
                            suggestion="Use formal language",
                        )
                    )

        elif settings.formality_level == "professional":
            # Check for overly casual elements
            casual_patterns = [r"\by'all\b", r"\bain't\b", r"\bcuz\b"]

            for pattern in casual_patterns:
                if re.search(pattern, text.lower()):
                    violations.append(
                        ToneViolation(
                            type="formality",
                            severity="error",
                            message="Overly casual language detected",
                            suggestion="Use professional language",
                        )
                    )

        return violations

    def analyze_tone(self, text: str) -> ToneAnalysisResult:
        """Analyze tone of text and detect voice.

        Args:
            text: Text to analyze

        Returns:
            Tone analysis result
        """
        # Detect primary voice
        voice_detected = self._detect_voice(text)

        # Use detected voice or default
        settings = self.profiles.get(voice_detected, self.profiles[ToneVoice.AUTHORITATIVE])

        # Audit content
        violations = self.audit_content(text, settings)

        # Calculate score
        score = self._calculate_compliance_score(violations)

        # Calculate metrics
        metrics = self._calculate_metrics(text, violations)

        return ToneAnalysisResult(
            is_compliant=score >= 0.8,
            violations=violations,
            score=score,
            voice_detected=voice_detected,
            metrics=metrics,
        )

    def _detect_voice(self, text: str) -> ToneVoice:
        """Detect the dominant voice in text.

        Args:
            text: Text to analyze

        Returns:
            Detected voice type
        """
        text_lower = text.lower()
        voice_scores = {}

        for voice, patterns in self.voice_patterns.items():
            score = 0

            # Count pattern matches
            for pattern in patterns["patterns"]:
                matches = len(re.findall(pattern, text_lower))
                score += matches

            # Penalize avoided words
            for avoid_word in patterns["avoid"]:
                if avoid_word.lower() in text_lower:
                    score -= 2

            voice_scores[voice] = max(0, score)

        # Return voice with highest score
        if voice_scores:
            return max(voice_scores, key=voice_scores.get)

        return ToneVoice.AUTHORITATIVE  # Default

    def _calculate_compliance_score(self, violations: list[ToneViolation]) -> float:
        """Calculate overall compliance score.

        Args:
            violations: List of violations

        Returns:
            Score between 0.0 and 1.0
        """
        if not violations:
            return 1.0

        # Weight violations by severity
        weights = {"error": 10, "warning": 5, "info": 1}
        total_penalty = sum(weights.get(v.severity, 1) for v in violations)

        # Calculate score (max penalty of 50 points)
        score = max(0.0, 1.0 - (total_penalty / 50))

        return score

    def _calculate_metrics(self, text: str, violations: list[ToneViolation]) -> dict[str, float]:
        """Calculate analysis metrics.

        Args:
            text: Analyzed text
            violations: Found violations

        Returns:
            Metrics dictionary
        """
        # Count violations by type
        violation_counts = {}
        for violation in violations:
            violation_counts[violation.type] = violation_counts.get(violation.type, 0) + 1

        # Calculate text metrics
        sentences = len(re.split(r"[.!?]+", text))
        words = len(text.split())

        return {
            "sentences": float(sentences),
            "words": float(words),
            "avg_sentence_length": words / sentences if sentences > 0 else 0.0,
            "violations_by_type": {k: float(v) for k, v in violation_counts.items()},
        }

    def get_profile(self, voice: ToneVoice) -> ToneSettings:
        """Get tone profile for a voice.

        Args:
            voice: Voice type

        Returns:
            Tone settings
        """
        return self.profiles.get(voice, self.profiles[ToneVoice.AUTHORITATIVE])

    def create_custom_profile(self, voice: ToneVoice, settings: ToneSettings) -> None:
        """Create or update a custom profile.

        Args:
            voice: Voice type
            settings: Tone settings
        """
        self.profiles[voice] = settings
        logger.info(f"Created custom profile for {voice.value} voice")


# Global enforcer instance
_tone_enforcer: ToneEnforcer | None = None


def get_tone_enforcer() -> ToneEnforcer:
    """Get global tone enforcer instance.

    Returns:
        ToneEnforcer instance
    """
    global _tone_enforcer
    if _tone_enforcer is None:
        _tone_enforcer = ToneEnforcer()
    return _tone_enforcer


# Convenience functions
def audit_text(text: str, voice: ToneVoice) -> list[ToneViolation]:
    """Audit text for tone violations.

    Args:
        text: Text to audit
        voice: Voice type to enforce

    Returns:
        List of violations
    """
    enforcer = get_tone_enforcer()
    settings = enforcer.get_profile(voice)
    return enforcer.audit_content(text, settings)


def analyze_tone(text: str) -> ToneAnalysisResult:
    """Analyze tone of text.

    Args:
        text: Text to analyze

    Returns:
        Tone analysis result
    """
    enforcer = get_tone_enforcer()
    return enforcer.analyze_tone(text)
