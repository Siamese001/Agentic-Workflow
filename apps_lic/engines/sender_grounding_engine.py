"""HOP3 sender_grounding — derive sender persona from campaign request.

Reads ``context["campaign_request"]`` and emits
``context["sender_persona"]`` carrying the name, voice register, and
compliance posture the generation stage must honor.

Re-derived per Wave 2 Phase 2.2.
"""

from __future__ import annotations

from typing import Any


_REGISTER_BY_COMPLIANCE = {
    "strict": "formal",
    "elevated": "measured",
    "standard": "professional",
    "casual": "conversational",
}


class SenderGroundingEngine:
    """Emit a sender persona dict."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        req = context.get("campaign_request")
        config = self._attr(req, "config", {}) if req is not None else {}

        compliance_level = str(self._attr(config, "compliance_level", "standard"))
        campaign_name = str(self._attr(config, "name", ""))
        target_audience = str(self._attr(config, "target_audience", ""))
        recipient_class = str(self._attr(config, "recipient_class", target_audience or "RECRUITER"))
        target_contact = self._attr(config, "target_contact", {})
        sender_proof_envelope = self._attr(config, "sender_proof_envelope", {})
        c03_allowed_claim_ids = self._attr(config, "c03_allowed_claim_ids", [])

        register = _REGISTER_BY_COMPLIANCE.get(
            compliance_level.lower(), "professional"
        )

        return {
            "sender_persona": {
                "campaign_name": campaign_name,
                "target_audience": target_audience,
                "recipient_class": recipient_class,
                "target_contact": target_contact if isinstance(target_contact, dict) else {},
                "sender_proof_envelope": (
                    dict(sender_proof_envelope)
                    if isinstance(sender_proof_envelope, dict)
                    else {}
                ),
                "c03_allowed_claim_ids": (
                    list(c03_allowed_claim_ids)
                    if isinstance(c03_allowed_claim_ids, list)
                    else []
                ),
                "voice_register": register,
                "compliance_level": compliance_level,
                "disclosure_required": compliance_level.lower() in ("strict", "elevated"),
            },
        }

    @staticmethod
    def _attr(obj: Any, key: str, default: Any) -> Any:
        if obj is None:
            return default
        if hasattr(obj, key):
            return getattr(obj, key, default)
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default
