"""LICValidationExecutor — Canonical parameterized LIC validation agent.

Consolidates: CampaignBalanceAgent, DeliverabilityAgent, MessageComplianceAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
Updated: 2026-03-11 (P1-A: absorbed MessageComplianceAgent as rule_set="message_compliance")
Updated: 2026-03-11 (P3-A: now subclasses ParameterizedValidator)
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from apps_lic.utils.lic_engine_validation_capability_util import LICEngineValidationCapability
from apps_shared.reasoning.ParameterizedValidator import ParameterizedValidator


@dataclass
class LICValidationExecutor(LICEngineValidationCapability, ParameterizedValidator):
    """Parameterized LIC engine validation agent.

    Usage:
        validator = LICValidationExecutor(rule_set="campaign_balance")

    Inherits execute(), collect_issues(), and _RULE_REGISTRY dispatch
    from ParameterizedValidator (P3-A). Rule handlers registered below.
    """

    rule_set: str = "generic"

    def collect_issues(self, data: dict, **kwargs) -> list[dict]:
        """Dispatch to rule-specific validation (LIC-local registry)."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"LICValidationExecutor.collect_issues:{self.rule_set}")
        if self.rule_set == "campaign_balance":
            return self._validate_campaign_balance(data)
        elif self.rule_set == "deliverability":
            return self._validate_deliverability(data)
        elif self.rule_set == "message_compliance":
            return self._validate_message_compliance(data)
        return super().collect_issues(data, **kwargs)

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

    _MESSAGE_COMPLIANCE_FORBIDDEN_WORDS = [
        "guaranteed",
        "free money",
        "act now",
        "limited time",
        "winner",
        "congratulations",
        "urgent",
        "click here",
    ]
    _MESSAGE_COMPLIANCE_MAX_LENGTH = 5000

    def _validate_message_compliance(self, data: dict) -> list[dict]:
        """Message compliance validation rules.

        Absorbed from MessageComplianceAgent (2026-03-11, P1-A).
        Checks: forbidden words, unsubscribe link presence, message length.

        Expected data shape:
            {"messages": [{"content": str, "subject": str}, ...]}
        """
        issues = []
        messages = data.get("messages", [])
        for i, message in enumerate(messages):
            content = message.get("content", "").lower()
            subject = message.get("subject", "").lower()
            for word in self._MESSAGE_COMPLIANCE_FORBIDDEN_WORDS:
                if word in content or word in subject:
                    issues.append({"type": "compliance_forbidden_word", "message_index": i, "word": word})
            if "unsubscribe" not in content:
                issues.append({"type": "compliance_missing_unsubscribe", "message_index": i})
            if len(content) > self._MESSAGE_COMPLIANCE_MAX_LENGTH:
                issues.append(
                    {
                        "type": "compliance_message_too_long",
                        "message_index": i,
                        "length": len(content),
                        "max": self._MESSAGE_COMPLIANCE_MAX_LENGTH,
                    }
                )
        return issues
