"""
DeliverabilityAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from apps_lic.utils.lic_engine_validation_capability import LICEngineValidationCapability
from apps_lic.utils.LICAgentBase import LICAgentBase


@dataclass
class DeliverabilityAgent(LICEngineValidationCapability, SubatomicTestingMixin, LICAgentBase):
    """Sovereign Deliverability Monitor."""

    # LICEngineValidationCapability configuration
    SIGNAL_NAME: ClassVar[str] = "DELIVERABILITY_ISSUE"
    VALIDATION_LABEL: ClassVar[str] = "Deliverability OK"

    # Sovereign Configuration
    monitored_domains: list[str] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=lambda: {"spam_rate": 0.01})
    spam_triggers: list[str] = field(default_factory=lambda: ["$$$", "!!!", "CAPS LOCK", "FREE", "BUY NOW"])

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    async def execute(self) -> None:
        """Execute deliverability validation via capability harness."""
        messages = self.ctx.messages

        if not messages:
            self.record_result(True, "No messages to check")
            return

        self.run_validation()

    def _validate(self) -> list[str]:
        """Deliverability-specific validation rules."""
        messages = self.ctx.messages
        issues: list[str] = []

        # Sovereign deliverability check using configured triggers
        for i, message in enumerate(messages):
            content = message.get("content", "")

            # Check for spam triggers using sovereign configuration
            for trigger in self.spam_triggers:
                if trigger in content:
                    issues.append(f"Message {i}: Spam trigger '{trigger}'")

            # Check link count
            link_count = content.count("http")
            if link_count > 3:
                issues.append(f"Message {i}: Too many links ({link_count})")

            # Check image count (placeholder check)
            img_count = content.count("<img")
            if img_count > 2:
                issues.append(f"Message {i}: Too many images ({img_count})")

        return issues

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by DeliverabilityAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"DeliverabilityAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"DeliverabilityAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
