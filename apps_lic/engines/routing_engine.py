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

        archetype = str(features.get("archetype_hint", "GENERIC"))
        template_id = _TEMPLATE_BY_ARCHETYPE.get(archetype, _TEMPLATE_BY_ARCHETYPE["GENERIC"])

        evidence_preview = self._top_evidence_text(evidence, n=3)
        audience = persona.get("target_audience", "") or features.get(
            "target_audience", ""
        )
        register = persona.get("voice_register", "professional")

        prompt = (
            f"[template={template_id}] [register={register}]\n"
            f"Audience: {audience}\n"
            f"Evidence:\n{evidence_preview}\n"
            f"Produce a short outreach message grounded strictly in the evidence above."
        )

        return {
            "routing_decision": {
                "archetype": archetype,
                "template_id": template_id,
                "register": register,
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
            f"- [{it.get('id', '?')}] {it.get('text', '')[:240]}" for it in top
        )
