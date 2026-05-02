"""HOP5 generation — produce a draft message from the routed prompt.

Minimal scaffold that emits a deterministic draft string. A follow-up
plan will wire Qwen (preferred) / Gemini (fallback) per the apps_rg
pattern; until then, this stage returns a template-filled placeholder
that carries the prompt signature so downstream stages can run
validation and QA end-to-end.

Re-derived per Wave 2 Phase 2.2. LLM wiring is deferred.
"""

from __future__ import annotations

import hashlib
from typing import Any


class GenerationEngine:
    """Emit a draft message. Deterministic scaffold until LLM wiring lands."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        prompt = str(context.get("generation_prompt", ""))
        persona = context.get("sender_persona") or {}

        audience = persona.get("target_audience", "")
        register = persona.get("voice_register", "professional")
        template_sig = hashlib.sha1(prompt.encode("utf-8", errors="ignore")).hexdigest()[:8]

        body = (
            f"Hello,\n\n"
            f"I'm reaching out because your focus on {audience or 'this area'} "
            f"aligns with what we're building. I'd appreciate a brief conversation "
            f"to see if there's a fit.\n\n"
            f"Best regards."
        )

        return {
            "draft_message": {
                "body": body,
                "register": register,
                "template_signature": template_sig,
                "attempts": 1,
                "generator": "scaffold",
            },
        }
