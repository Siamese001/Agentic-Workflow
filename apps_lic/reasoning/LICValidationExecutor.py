"""LICValidationExecutor — Canonical parameterized LIC validation agent.

Consolidates: CampaignBalanceAgent, DeliverabilityAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass

from apps_lic.utils.lic_engine_validation_capability import LICEngineValidationCapability
from apps_lic.utils.LICAgentBase import LICAgentBase


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class LICValidationExecutor(LICEngineValidationCapability, LICAgentBase):
    """Parameterized LIC engine validation agent.

    Usage:
        validator = LICValidationExecutor(rule_set="campaign_balance")
    """

    rule_set: str = "generic"

    def _validate(self, data: dict, **kwargs) -> list[dict]:
        """Dispatch to rule-specific validation."""
        if self.rule_set == "campaign_balance":
            return self._validate_campaign_balance(data)
        elif self.rule_set == "deliverability":
            return self._validate_deliverability(data)
        return []

    def _validate_campaign_balance(self, data: dict) -> list[dict]:
        """Campaign balance validation rules."""
        issues = []
        channels = data.get("channels", {})
        total = sum(channels.values()) if channels else 0
        if total > 0:
            for ch, val in channels.items():
                ratio = val / total
                if ratio > 0.7:
                    issues.append({"type": "channel_imbalance", "channel": ch, "ratio": ratio})
        return issues

    def _validate_deliverability(self, data: dict) -> list[dict]:
        """Deliverability validation rules."""
        issues = []
        if data.get("spam_score", 0) > 5:
            issues.append({"type": "high_spam_score", "score": data["spam_score"]})
        if not data.get("dkim_valid", True):
            issues.append({"type": "dkim_invalid"})
        if not data.get("spf_valid", True):
            issues.append({"type": "spf_invalid"})
        return issues
