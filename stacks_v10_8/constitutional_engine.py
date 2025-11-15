"""Local constitutional rule enforcement for stack outputs."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ConstitutionalRule(BaseModel):
    """Metadata describing a single constitutional principle."""

    id: str
    description: str


class ConstitutionalViolation(BaseModel):
    """Represents a single rule violation emitted by the engine."""

    rule_id: str
    message: str


class ConstitutionalReviewResult(BaseModel):
    """Aggregate review output for a blob of text or node payload."""

    violations: List[ConstitutionalViolation]
    passed: bool


RULEBOOK: List[ConstitutionalRule] = [
    ConstitutionalRule(
        id="no_unverifiable_factual_claims",
        description="No unverifiable factual claims",
    ),
    ConstitutionalRule(
        id="no_invented_entities",
        description="No invented companies / institutions",
    ),
    ConstitutionalRule(
        id="no_fake_contact_details",
        description="No hallucinated contact details",
    ),
    ConstitutionalRule(
        id="no_political_persuasion",
        description="No political persuasion",
    ),
    ConstitutionalRule(
        id="no_discriminatory_framing",
        description="No discriminatory framing",
    ),
    ConstitutionalRule(
        id="require_source_attribution",
        description="Must include source attribution for external statements",
    ),
]


class ConstitutionalEngine:
    """Lightweight rule-enforcement layer used by orchestrators."""

    def __init__(self, rules: Optional[List[ConstitutionalRule]] = None) -> None:
        self._rules = list(rules or RULEBOOK)
        self._rule_map = {rule.id: rule for rule in self._rules}
        self._invented_entity_pattern = re.compile(
            r"\b(imaginary|fictional|fake|made-up|nonexistent)\s+(company|corp|university|institute|organization)",
            re.IGNORECASE,
        )
        self._contact_patterns = [
            re.compile(r"\b555-01\d{2}\b"),
            re.compile(r"\b123-456-7890\b"),
            re.compile(r"[A-Za-z0-9._%+-]+@example\.com\b", re.IGNORECASE),
            re.compile(r"\b555-1234\b"),
        ]
        self._political_phrases = (
            "vote for",
            "support candidate",
            "re-elect",
            "political campaign",
            "endorse our party",
            "cast your ballot",
        )
        self._discriminatory_groups = (
            "women",
            "men",
            "people over 40",
            "people under 30",
            "immigrants",
            "minorities",
            "disabled",
        )
        self._discriminatory_frames = (
            "should not apply",
            "must not apply",
            "are not welcome",
            "are inferior",
            "are better than",
            "cannot perform",
        )
        self._unverifiable_markers = (
            "i guarantee",
            "trust me",
            "undeniable fact",
            "secret internal data",
            "cannot be verified",
            "without evidence",
        )

    # ------------------------------------------------------------------
    # Public APIs
    # ------------------------------------------------------------------
    def review_text(self, text: str) -> ConstitutionalReviewResult:
        normalized = (text or "").strip()
        if not normalized:
            return ConstitutionalReviewResult(violations=[], passed=True)

        lowered = normalized.lower()
        violations: List[ConstitutionalViolation] = []
        violations.extend(self._check_unverifiable_claims(lowered))
        violations.extend(self._check_invented_entities(normalized))
        violations.extend(self._check_contact_details(normalized))
        violations.extend(self._check_political_persuasion(lowered))
        violations.extend(self._check_discriminatory_framing(lowered))
        violations.extend(self._check_source_attribution(lowered))
        return ConstitutionalReviewResult(violations=violations, passed=len(violations) == 0)

    def review_node(self, node_output: Dict[str, Any]) -> ConstitutionalReviewResult:
        try:
            serialized = json.dumps(node_output, ensure_ascii=False, sort_keys=True, default=str)
        except Exception:
            serialized = str(node_output)
        return self.review_text(serialized)

    # ------------------------------------------------------------------
    # Rule detectors
    # ------------------------------------------------------------------
    def _check_unverifiable_claims(self, lowered: str) -> List[ConstitutionalViolation]:
        hits = [phrase for phrase in self._unverifiable_markers if phrase in lowered]
        if not hits and re.search(r"\b\d{3}%\s+accurate", lowered):
            hits.append("hyperbolic accuracy")
        return [
            self._violation(
                "no_unverifiable_factual_claims",
                f"Unverifiable claim detected: '{phrase}'",
            )
            for phrase in hits
        ]

    def _check_invented_entities(self, text: str) -> List[ConstitutionalViolation]:
        matches = self._invented_entity_pattern.findall(text)
        if not matches:
            return []
        descriptions = {f"{adjective} {entity}" for adjective, entity in matches}
        return [
            self._violation(
                "no_invented_entities",
                f"Invented entity reference: '{description}'",
            )
            for description in descriptions
        ]

    def _check_contact_details(self, text: str) -> List[ConstitutionalViolation]:
        hits: List[str] = []
        for pattern in self._contact_patterns:
            for match in pattern.findall(text):
                hits.append(match if isinstance(match, str) else match[0])
        return [
            self._violation(
                "no_fake_contact_details",
                f"Potential hallucinated contact detail '{match}'",
            )
            for match in hits
        ]

    def _check_political_persuasion(self, lowered: str) -> List[ConstitutionalViolation]:
        hits = [phrase for phrase in self._political_phrases if phrase in lowered]
        return [
            self._violation(
                "no_political_persuasion",
                f"Political persuasion detected via phrase '{phrase}'",
            )
            for phrase in hits
        ]

    def _check_discriminatory_framing(self, lowered: str) -> List[ConstitutionalViolation]:
        hits: List[str] = []
        for group in self._discriminatory_groups:
            for frame in self._discriminatory_frames:
                needle = f"{group} {frame}"
                if needle in lowered:
                    hits.append(needle)
        return [
            self._violation(
                "no_discriminatory_framing",
                f"Discriminatory framing detected: '{phrase}'",
            )
            for phrase in hits
        ]

    def _check_source_attribution(self, lowered: str) -> List[ConstitutionalViolation]:
        triggers = ("according to", "reported by", "study shows")
        requires_source = any(trigger in lowered for trigger in triggers)
        has_source = "source:" in lowered or "http" in lowered or "doi" in lowered
        if requires_source and not has_source:
            return [
                self._violation(
                    "require_source_attribution",
                    "External statement missing explicit source attribution",
                )
            ]
        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _violation(self, rule_id: str, message: str) -> ConstitutionalViolation:
        if rule_id not in self._rule_map:
            raise ValueError(f"Unknown rule id '{rule_id}'")
        return ConstitutionalViolation(rule_id=rule_id, message=message)
