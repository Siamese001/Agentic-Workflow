"""
Deliverability Validator - Deterministic Deliverability Validation

Zero-Ambiguity Standard: Renamed from deliverability_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Spam trigger detection (keyword matching)
- Link count validation (counting)
- Image count validation (counting)
- Content analysis (pattern matching)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class DeliverabilityResult:
    """Result of deliverability validation."""
    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

class DeliverabilityValidator:
    """
    Pure deterministic deliverability validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None=None) -> None:
        """
        Initialize with deliverability validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.spam_triggers = config.get('spam_triggers', ['$$$', '!!!', 'CAPS LOCK', 'FREE', 'BUY NOW', 'CLICK HERE', 'ACT NOW'])
        self.max_links = config.get('max_links', 3)
        self.max_images = config.get('max_images', 2)
        self.spam_rate_threshold = config.get('spam_rate_threshold', 0.01)

    def validate_deliverability(self, messages: list[dict[str, Any]]) -> DeliverabilityResult:
        """
        Validate deliverability using purely deterministic logic.

        Args:
            messages: List of message dictionaries with 'content' field

        Returns:
            DeliverabilityResult with deterministic findings
        """
        if not messages:
            return DeliverabilityResult(passed=True, issues=[], score=1.0, metadata={'validation_type': 'deterministic', 'message_count': 0})
        issues: list[str] = []
        for i, message in enumerate(messages):
            content = message.get('content', '')
            spam_issues = self._check_spam_triggers(content, i)
            issues.extend(spam_issues)
            link_issues = self._check_link_count(content, i)
            issues.extend(link_issues)
            image_issues = self._check_image_count(content, i)
            issues.extend(image_issues)
        score = self._calculate_deliverability_score(issues, len(messages))
        return DeliverabilityResult(passed=len(issues) == 0, issues=issues, score=score, metadata={'validation_type': 'deterministic', 'message_count': len(messages)})

    def _check_spam_triggers(self, content: str, message_index: int) -> list[str]:
        """
        Check for spam triggers using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching logic
        """
        issues: list[str] = []
        for trigger in self.spam_triggers:
            if trigger in content:
                issues.append(f"Message {message_index}: Spam trigger '{trigger}'")
        return issues

    def _check_link_count(self, content: str, message_index: int) -> list[str]:
        """
        Check link count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        """
        issues: list[str] = []
        link_count = content.count('http')
        if link_count > self.max_links:
            issues.append(f'Message {message_index}: Too many links ({link_count})')
        return issues

    def _check_image_count(self, content: str, message_index: int) -> list[str]:
        """
        Check image count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        """
        issues: list[str] = []
        img_count = content.count('<img')
        if img_count > self.max_images:
            issues.append(f'Message {message_index}: Too many images ({img_count})')
        return issues

    def _calculate_deliverability_score(self, issues: list[str], message_count: int) -> float:
        """
        Calculate deliverability score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        if message_count == 0:
            return 1.0
        base_score = 1.0
        issue_penalty = len(issues) * 0.1
        base_score -= issue_penalty
        return max(0.0, min(1.0, base_score))

    def check_single_message(self, content: str) -> DeliverabilityResult:
        """
        Check a single message for deliverability issues.

        Convenience method for single message validation.
        """
        return self.validate_deliverability([{'content': content}])

    def get_spam_trigger_count(self, content: str) -> int:
        """
        Count spam triggers in content.

        Moved to Deterministic: Pure counting logic
        """
        count = 0
        for trigger in self.spam_triggers:
            count += content.count(trigger)
        return count

    def analyze_content_risk(self, content: str) -> dict[str, Any]:
        """
        Analyze content risk using deterministic rules.

        Returns detailed risk analysis for content.
        """
        spam_count = self.get_spam_trigger_count(content)
        link_count = content.count('http')
        image_count = content.count('<img')
        risk_score = 0
        if spam_count > 0:
            risk_score += spam_count * 2
        if link_count > self.max_links:
            risk_score += (link_count - self.max_links) * 1
        if image_count > self.max_images:
            risk_score += (image_count - self.max_images) * 1
        risk_level = 'low' if risk_score == 0 else 'medium' if risk_score < 5 else 'high'
        return {'spam_trigger_count': spam_count, 'link_count': link_count, 'image_count': image_count, 'risk_score': risk_score, 'risk_level': risk_level}
