"""HOP5 generation — produce a draft message from the routed prompt.

Originally a deterministic scaffold (W2 Phase 2.2). Wired Qwen-first
2026-05-02 per plan ``qwen-rollout-followup-burndown-d2a4f8`` Phase
P1.1 (closes the W4 P4.1 follow-up from the predecessor rollout
plan ``apps-eval-qwen32b-rollout-b7c4d9``).

Cascade order:
    1. Local Qwen-32B vLLM via ``openai.OpenAI`` sync client (matches
       the W2/W3/W5 cascade pattern used elsewhere in the rollout —
       narrative_judge_scorer / company_brief_engine /
       apps_rg._llm_client). Fails soft on every preflight, SDK,
       gateway, or empty-response path.
    2. Deterministic template-filled scaffold (the original behavior).
       Carries the prompt signature so downstream validation / QA
       stages always have a non-empty body to check.

Failure semantics
-----------------
Returns the same ``{"draft_message": {...}}`` shape regardless of
which generator fired. The ``generator`` field on the dict is one
of ``qwen_local`` (Qwen accepted) or ``scaffold`` (deterministic
fallback) so downstream observability can distinguish the source.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class GenerationEngine:
    """Emit a draft message. Qwen-first cascade with deterministic fallback."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        prompt = str(context.get("generation_prompt", ""))
        persona = context.get("sender_persona") or {}

        audience = persona.get("target_audience", "")
        register = persona.get("voice_register", "professional")
        template_sig = hashlib.sha1(prompt.encode("utf-8", errors="ignore")).hexdigest()[:8]

        # Phase P1.1 — try Qwen first; fall through to deterministic scaffold.
        qwen_body = self._try_qwen_generation(prompt=prompt, register=register)
        if qwen_body:
            return {
                "draft_message": {
                    "body": qwen_body,
                    "register": register,
                    "template_signature": template_sig,
                    "attempts": 1,
                    "generator": "qwen_local",
                },
            }

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

    @staticmethod
    def _try_qwen_generation(*, prompt: str, register: str) -> str:
        """Run prompt through local Qwen-32B; return generated text or ``""``.

        Returns empty string on every failure path so :meth:`execute`
        falls through to the deterministic scaffold. Mirrors the
        W2/W3/W5 cascade pattern (preflight → SDK lazy import →
        model_registry lazy import → sync ``openai.OpenAI`` client →
        per-call fail-soft).
        """
        if not prompt.strip():
            return ""

        # Preflight via L2 health probe.
        try:
            from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
                is_qwen_available,
            )
        except ImportError:
            return ""
        if not is_qwen_available():
            _emit_hop5_marker(
                accepted=False,
                model_used="qwen_unavailable",
                fallback_reason="preflight_failed",
            )
            return ""

        try:
            import openai  # type: ignore  # noqa: PLC0415
        except ImportError:
            return ""

        try:
            from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                QWEN_LOCAL_MODEL_ID,
                VLLM_BASE_URL,
            )
        except ImportError:
            return ""

        try:
            client = openai.OpenAI(
                base_url=VLLM_BASE_URL,
                api_key="not-needed",  # vLLM ignores auth in local mode
                timeout=30.0,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI client init heterogeneous (ssl, network, env); fail-soft cascades to deterministic scaffold
            _LOGGER.info("[apps_lic.generation_engine] qwen client init failed: %s", exc)
            _emit_hop5_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="client_init_failed",
            )
            return ""

        try:
            resp = client.chat.completions.create(
                model=QWEN_LOCAL_MODEL_ID,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior B2B copywriter producing crisp, "
                            "compliance-aware LinkedIn outreach. Return ONLY "
                            f"the message body in a {register} register — no "
                            "preamble, no JSON, no markdown fence."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=400,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-SDK-over-vLLM raises heterogeneous (APIError/Connection/Timeout); fail-soft cascades to deterministic scaffold
            _LOGGER.info("[apps_lic.generation_engine] qwen call failed: %s", exc)
            _emit_hop5_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="gateway_exception",
            )
            return ""

        text = (resp.choices[0].message.content or "") if resp.choices else ""
        if not text.strip():
            _emit_hop5_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="empty_response",
            )
            return ""

        _emit_hop5_marker(
            accepted=True,
            model_used=QWEN_LOCAL_MODEL_ID,
            fallback_reason="none",
        )
        return text.strip()


def _emit_hop5_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
) -> None:
    """Best-effort ``JUDGE_DECISION`` marker for HOP5 generation availability.

    Same shape as :class:`apps_lic.integrations.qwen_llm_client.QwenLLMClient`
    so the calibration harness aggregates both surfaces under
    ``app_name=apps_lic.hop5_generation``. Never raises.
    """
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415
    except ImportError:
        return
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_lic.hop5_generation, "
        "rubric_id=lic_hop5_generation_v1, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        "composite=0.0, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        "latency_ms=0.0"
    )
    try:
        append_marker(payload, session_hint="apps_lic.generation_engine")
    except (OSError, PermissionError):
        pass
