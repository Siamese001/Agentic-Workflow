"""HOP4 routing — pick a generation prompt template from profile + evidence.

Consumes profile features, evidence bundle, and sender persona, and emits
a ``routing_decision`` (which template family to use) plus a
``generation_prompt`` (the concrete string or prompt-template handle the
generation stage will consume).

Re-derived per Wave 2 Phase 2.2.
"""

from __future__ import annotations

from typing import Any


_TEMPLATE_BY_ARCHETYPE = {
    "RECRUITER": "lic.outreach.recruiter.v1",
    "SENIOR_TA": "lic.outreach.senior_ta.v1",
    "HIRING_MANAGER": "lic.outreach.hiring_manager.v1",
    "EXECUTIVE": "lic.outreach.executive.v1",
    "ENGINEER": "lic.outreach.engineer.v1",
    "GENERIC": "lic.outreach.generic.v1",
}


class RoutingEngine:
    """Select template family and compose a generation prompt."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        features = context.get("profile_features") or {}
        evidence = context.get("evidence_bundle") or {}
        persona = context.get("sender_persona") or {}
        reasoning_policy = context.get("reasoning_policy") or {}

        archetype = str(features.get("archetype_hint", "GENERIC"))
        template_id = _TEMPLATE_BY_ARCHETYPE.get(archetype, _TEMPLATE_BY_ARCHETYPE["GENERIC"])
        recipient_class = str(features.get("recipient_class") or archetype or "GENERIC")
        target_contact = features.get("target_contact") or {}
        target_name = ""
        target_title = ""
        target_company = ""
        if isinstance(target_contact, dict):
            target_name = str(target_contact.get("verified_name", "") or "")
            target_title = str(target_contact.get("title", "") or "")
            target_company = str(target_contact.get("company_name", "") or "")

        evidence_preview = self._top_evidence_text(evidence, n=3)
        audience = persona.get("target_audience", "") or features.get(
            "target_audience", ""
        )
        register = persona.get("voice_register", "professional")
        allowed_claim_ids = _allowed_claim_ids(
            context.get("sender_proof_envelope")
            or persona.get("sender_proof_envelope")
            or {}
        )
        allowed_claim_text = ", ".join(allowed_claim_ids) if allowed_claim_ids else "(none)"

        prompt = (
            f"[template={template_id}] [register={register}] "
            f"[recipient_class={recipient_class}]\n"
            f"Audience: {audience}\n"
            f"Target contact: {target_name} | {target_title} | {target_company}\n"
            f"Sender proof allowed claim IDs: {allowed_claim_text}\n"
            "claims_used may contain only the sender proof allowed claim IDs above.\n"
            "Reasoning policy:\n"
            f"- sc_level: {reasoning_policy.get('sc_level', 'SC-1')}\n"
            f"- reasoning_intensity: {reasoning_policy.get('reasoning_intensity', 'R1_STANDARD')}\n"
            f"- judge_profile: {reasoning_policy.get('judge_profile', 'normal_default')}\n"
            f"- max_candidates: {reasoning_policy.get('max_candidates', 1)}\n"
            f"- evidence_support_status: {evidence.get('support_status', '')}\n"
            f"Evidence:\n{evidence_preview}\n"
            f"Produce a short outreach message grounded strictly in the evidence above."
        )

        return {
            "routing_decision": {
                "archetype": archetype,
                "template_id": template_id,
                "register": register,
                "recipient_class": recipient_class,
                "target_contact": target_contact if isinstance(target_contact, dict) else {},
                "reasoning_policy": (
                    dict(reasoning_policy) if isinstance(reasoning_policy, dict) else {}
                ),
                "evidence_support_status": evidence.get("support_status", ""),
                "allowed_claim_ids": list(allowed_claim_ids),
            },
            "generation_prompt": prompt,
        }

    @staticmethod
    def _top_evidence_text(evidence: dict[str, Any], *, n: int) -> str:
        items = evidence.get("items") or []
        top = sorted(items, key=lambda it: float(it.get("score", 0.0)), reverse=True)[:n]
        if not top:
            return "(no evidence available)"
        return "\n".join(
            f"- [{it.get('id', '?')}] {it.get('text', '')[:900]}" for it in top
        )


def _allowed_claim_ids(envelope: Any) -> tuple[str, ...]:
    if not isinstance(envelope, dict):
        return ()
    raw = envelope.get("allowed_claim_ids") or ()
    if not isinstance(raw, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(str(item).strip() for item in raw if str(item).strip()))
