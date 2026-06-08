"""HOP5 generation for LinkedIn recruiter outreach drafts.

Generation is Qwen/vLLM-primary. The only deterministic generation path is the
explicit ``APPS_LIC_TEST_PROVIDER_STUB=1`` mode used by tests. When Qwen/vLLM is
unavailable outside that test mode, this engine emits a non-passing draft shape
or raises when ``APPS_LIC_REQUIRE_QWEN_VLLM=1`` so downstream gates fail closed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib import request as urllib_request

from apps_lic.policy.reasoning_intensity import compact_policy, default_reasoning_policy

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_MODEL = "Qwen/Qwen2.5-32B-Instruct-AWQ"
DEFAULT_PROVIDER = "vllm"
DEFAULT_PROVIDER_PROFILE = "qwen_vllm"
DEFAULT_TEMPERATURE = 0.82
DEFAULT_TOP_P = 0.92
DEFAULT_MAX_GENERATION_ATTEMPTS = 1


@dataclass(frozen=True)
class ProviderSettings:
    """Resolved Qwen/vLLM settings for one generation attempt."""

    base_url: str
    model: str
    target_provider: str
    provider_profile: str
    timeout_seconds: float
    require_qwen_vllm: bool
    healthcheck_enabled: bool
    temperature: float
    top_p: float
    max_generation_attempts: int


class GenerationEngine:
    """Emit a LinkedIn recruiter draft from the PA prompt."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        prompt = str(context.get("generation_prompt", ""))
        persona = context.get("sender_persona") or {}
        reasoning_policy = compact_policy(
            context.get("reasoning_policy") or default_reasoning_policy()
        )
        register = str(persona.get("voice_register", "professional") or "professional")
        recipient_class = _normalise_recipient_class(
            persona.get("recipient_class") or _prompt_recipient_class(prompt)
        )
        target_contact = (
            persona.get("target_contact")
            if isinstance(persona.get("target_contact"), dict)
            else _prompt_target_contact(prompt)
        )
        template_sig = hashlib.sha1(prompt.encode("utf-8", errors="ignore")).hexdigest()[:8]
        settings = _resolve_provider_settings()

        if _truthy(os.environ.get("APPS_LIC_TEST_PROVIDER_STUB", "0")):
            return {
                "draft_message": _stub_draft(
                    register=register,
                    recipient_class=recipient_class,
                    target_contact=target_contact,
                    template_signature=template_sig,
                    settings=settings,
                    reasoning_policy=reasoning_policy,
                )
            }

        qwen_text = self._try_qwen_generation(
            prompt=prompt,
            register=register,
            recipient_class=recipient_class,
            settings=settings,
            reasoning_policy=reasoning_policy,
        )
        draft = _draft_from_model_text(
            qwen_text,
            register=register,
            recipient_class=recipient_class,
            target_contact=target_contact,
            template_signature=template_sig,
            settings=settings,
            reasoning_policy=reasoning_policy,
        )
        if draft:
            return {"draft_message": draft}

        if settings.require_qwen_vllm:
            raise RuntimeError("apps_lic_qwen_vllm_required_unavailable")

        return {
            "draft_message": {
                "message_text": "",
                "body": "",
                "channel": "linkedin",
                "recipient_class": _recipient_class_value(recipient_class),
                "recipient_category": recipient_class,
                "target_contact_name": str(target_contact.get("verified_name", "") or ""),
                "target_contact_title": str(target_contact.get("title", "") or ""),
                "target_contact_company": str(target_contact.get("company_name", "") or ""),
                "intended_next_step": "",
                "claims_used": [],
                "unsupported_claims": ["qwen_vllm_unavailable"],
                "omitted_claims": [],
                "qa_notes": ["qwen_vllm_unavailable_no_test_stub"],
                "register": register,
                "template_signature": template_sig,
                "attempts": 1,
                "sc_level": reasoning_policy["sc_level"],
                "reasoning_intensity": reasoning_policy["reasoning_intensity"],
                "judge_profile": reasoning_policy["judge_profile"],
                "reasoning_policy": reasoning_policy,
                "max_candidates": reasoning_policy["max_candidates"],
                "candidate_count": 0,
                "candidate_selection_strategy": "none_provider_unavailable",
                "validation_repair_passes": reasoning_policy["validation_repair_passes"],
                "generation_temperature": settings.temperature,
                "top_p": settings.top_p,
                "max_generation_attempts": settings.max_generation_attempts,
                "generator": "qwen_vllm_unavailable",
                "provider_profile": settings.provider_profile,
                "target_provider": settings.target_provider,
                "model": settings.model,
            }
        }

    @staticmethod
    def _try_qwen_generation(
        *,
        prompt: str,
        register: str,
        recipient_class: str,
        settings: ProviderSettings,
        reasoning_policy: dict[str, Any],
    ) -> str:
        """Run prompt through local Qwen/vLLM and return raw assistant text."""
        if not prompt.strip():
            return ""

        if settings.healthcheck_enabled and not _healthcheck_vllm(settings):
            _emit_hop5_marker(
                accepted=False,
                model_used=settings.model,
                fallback_reason="vllm_healthcheck_failed",
            )
            return ""

        try:
            import openai  # type: ignore  # noqa: PLC0415
        except ImportError:
            _emit_hop5_marker(
                accepted=False,
                model_used=settings.model,
                fallback_reason="openai_sdk_unavailable",
            )
            return ""

        try:
            client = openai.OpenAI(
                base_url=settings.base_url,
                api_key="not-needed",
                timeout=settings.timeout_seconds,
            )
            resp = client.chat.completions.create(
                model=settings.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You draft concise LinkedIn outreach for Amit Ayer. "
                            f"The target recipient category is {recipient_class}. "
                            "Amit is a candidate/senior AI engineering leader, not a vendor. "
                            "Write like a thoughtful operator, not a generic job seeker. "
                            "Use the selected reasoning policy only to improve candidate wording "
                            "and selection; never use it to add unsupported evidence. "
                            f"SC level is {reasoning_policy['sc_level']}; "
                            f"reasoning intensity is {reasoning_policy['reasoning_intensity']}; "
                            f"consider at most {reasoning_policy['max_candidates']} candidate(s) "
                            "internally and return the single best selected message. "
                            "Return one JSON object only with message_text, intended_next_step, "
                            "claims_used, unsupported_claims, omitted_claims, qa_notes, "
                            "provider_profile, and model. No markdown, no subject, no em dash. "
                            "message_text must be 600 characters or fewer, max 2 short paragraphs, "
                            "with no signature or sign-off block. "
                            "Include one AIG-specific operating insight and one concrete Amit proof point. "
                            "Amit proof is limited to the sender evidence; do not invent prior-company metrics, "
                            "percent improvements, or unnamed case studies. "
                            "Avoid generic phrases: potential synergies, discuss opportunities, "
                            "I noticed your role, I believe my background aligns, given your expertise. "
                            f"Use a {register} register."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.temperature,
                top_p=settings.top_p,
                max_tokens=500,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-over-vLLM raises heterogeneous transport/API errors; fail closed outside explicit test stub
            _LOGGER.info("[apps_lic.generation_engine] qwen/vllm call failed: %s", exc)
            _emit_hop5_marker(
                accepted=False,
                model_used=settings.model,
                fallback_reason="gateway_exception",
            )
            return ""

        text = (resp.choices[0].message.content or "") if resp.choices else ""
        if not text.strip():
            _emit_hop5_marker(
                accepted=False,
                model_used=settings.model,
                fallback_reason="empty_response",
            )
            return ""

        _emit_hop5_marker(
            accepted=True,
            model_used=settings.model,
            fallback_reason="none",
        )
        return text.strip()


def _resolve_provider_settings() -> ProviderSettings:
    base_url = (
        os.environ.get("APPS_LIC_VLLM_BASE_URL")
        or os.environ.get("VLLM_BASE_URL")
        or DEFAULT_BASE_URL
    )
    model = (
        os.environ.get("APPS_LIC_QWEN_MODEL")
        or os.environ.get("APPS_LIC_TARGET_MODEL")
        or os.environ.get("QWEN_VLLM_MODEL")
        or DEFAULT_MODEL
    )
    target_provider = (
        os.environ.get("APPS_LIC_TARGET_PROVIDER")
        or os.environ.get("APPS_LIC_PROVIDER_PROFILE")
        or DEFAULT_PROVIDER
    )
    provider_profile = os.environ.get("APPS_LIC_PROVIDER_PROFILE") or DEFAULT_PROVIDER_PROFILE
    timeout_seconds = _float_env("APPS_LIC_QWEN_TIMEOUT_SECONDS", 120.0)
    temperature = _float_env("APPS_LIC_QWEN_TEMPERATURE", DEFAULT_TEMPERATURE)
    top_p = _float_env("APPS_LIC_QWEN_TOP_P", DEFAULT_TOP_P)
    return ProviderSettings(
        base_url=base_url,
        model=model,
        target_provider=target_provider,
        provider_profile=provider_profile,
        timeout_seconds=timeout_seconds,
        require_qwen_vllm=_truthy(os.environ.get("APPS_LIC_REQUIRE_QWEN_VLLM", "0")),
        healthcheck_enabled=_truthy(
            os.environ.get("APPS_LIC_VLLM_HEALTHCHECK_ENABLED", "1")
        ),
        temperature=_clamp_float(temperature, lo=0.0, hi=1.0),
        top_p=_clamp_float(top_p, lo=0.1, hi=1.0),
        max_generation_attempts=DEFAULT_MAX_GENERATION_ATTEMPTS,
    )


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _truthy(raw: str | None) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on"}


def _clamp_float(value: float, *, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _healthcheck_vllm(settings: ProviderSettings) -> bool:
    endpoint = f"{settings.base_url.rstrip('/')}/models"
    try:
        with urllib_request.urlopen(
            endpoint,
            timeout=min(settings.timeout_seconds, 5.0),
        ) as response:
            return 200 <= int(response.status) < 500
    except Exception as exc:  # guardian: allow-broad-exception -- urllib surfaces heterogeneous local transport failures; generation must fail closed
        _LOGGER.info("[apps_lic.generation_engine] vllm healthcheck failed: %s", exc)
        return False


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _draft_from_model_text(
    text: str,
    *,
    register: str,
    recipient_class: str,
    target_contact: dict[str, Any],
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        parsed = json.loads(_strip_json_fence(text))
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    if isinstance(parsed.get("draft_message"), dict):
        parsed = parsed["draft_message"]

    message_text = str(parsed.get("message_text") or parsed.get("body") or "").strip()
    if not message_text:
        return {}
    claims_used = parsed.get("claims_used")
    unsupported_claims = parsed.get("unsupported_claims")
    omitted_claims = parsed.get("omitted_claims")
    qa_notes = parsed.get("qa_notes")
    return {
        "message_text": message_text,
        "body": message_text,
        "channel": "linkedin",
        "recipient_class": _recipient_class_value(
            parsed.get("recipient_class") or recipient_class
        ),
        "recipient_category": recipient_class,
        "target_contact_name": str(target_contact.get("verified_name", "") or ""),
        "target_contact_title": str(target_contact.get("title", "") or ""),
        "target_contact_company": str(target_contact.get("company_name", "") or ""),
        "intended_next_step": str(parsed.get("intended_next_step") or "").strip(),
        "claims_used": claims_used if isinstance(claims_used, list) else [],
        "unsupported_claims": (
            unsupported_claims if isinstance(unsupported_claims, list) else []
        ),
        "omitted_claims": omitted_claims if isinstance(omitted_claims, list) else [],
        "qa_notes": qa_notes if isinstance(qa_notes, list) else [],
        "register": register,
        "template_signature": template_signature,
        "attempts": 1,
        "sc_level": reasoning_policy["sc_level"],
        "reasoning_intensity": reasoning_policy["reasoning_intensity"],
        "judge_profile": reasoning_policy["judge_profile"],
        "reasoning_policy": reasoning_policy,
        "max_candidates": reasoning_policy["max_candidates"],
        "candidate_count": reasoning_policy["max_candidates"],
        "candidate_selection_strategy": "single_best_selected_by_policy",
        "validation_repair_passes": reasoning_policy["validation_repair_passes"],
        "generation_temperature": settings.temperature,
        "top_p": settings.top_p,
        "max_generation_attempts": settings.max_generation_attempts,
        "generator": "qwen_vllm",
        "provider_profile": settings.provider_profile,
        "target_provider": settings.target_provider,
        "model": settings.model,
    }


def _stub_draft(
    *,
    register: str,
    recipient_class: str,
    target_contact: dict[str, Any],
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
) -> dict[str, Any]:
    target_name = str(target_contact.get("verified_name", "") or "").strip()
    target_title = str(target_contact.get("title", "") or "").strip()
    target_company = str(target_contact.get("company_name", "") or "AIG").strip()
    salutation = f"Hi {target_name.split()[0]}," if target_name else "Hi,"
    message_text = _stub_message_text(
        salutation=salutation,
        recipient_class=recipient_class,
        target_title=target_title,
        target_company=target_company,
    )
    return {
        "message_text": message_text,
        "body": message_text,
        "channel": "linkedin",
        "recipient_class": _recipient_class_value(recipient_class),
        "recipient_category": recipient_class,
        "target_contact_name": target_name,
        "target_contact_title": target_title,
        "target_contact_company": target_company,
        "intended_next_step": "quick chat or resume review",
        "claims_used": [],
        "unsupported_claims": [],
        "omitted_claims": [],
        "qa_notes": ["deterministic_test_provider_stub"],
        "register": register,
        "template_signature": template_signature,
        "attempts": 1,
        "sc_level": reasoning_policy["sc_level"],
        "reasoning_intensity": reasoning_policy["reasoning_intensity"],
        "judge_profile": reasoning_policy["judge_profile"],
        "reasoning_policy": reasoning_policy,
        "max_candidates": reasoning_policy["max_candidates"],
        "candidate_count": reasoning_policy["max_candidates"],
        "candidate_selection_strategy": "deterministic_stub_single_best",
        "validation_repair_passes": reasoning_policy["validation_repair_passes"],
        "generation_temperature": settings.temperature,
        "top_p": settings.top_p,
        "max_generation_attempts": settings.max_generation_attempts,
        "generator": "test_provider_stub",
        "provider_profile": settings.provider_profile,
        "target_provider": settings.target_provider,
        "model": settings.model,
    }


def _normalise_recipient_class(raw: Any) -> str:
    value = str(raw or "RECRUITER").strip().upper().replace("-", "_")
    aliases = {
        "SENIOR TA": "SENIOR_TA",
        "HIRING MANAGER": "HIRING_MANAGER",
        "C LEVEL": "C_LEVEL",
        "C-LEVEL": "C_LEVEL",
        "VP ENG": "VP_ENG",
    }
    value = aliases.get(value.replace("_", " "), value)
    allowed = {
        "RECRUITER",
        "SENIOR_TA",
        "HIRING_MANAGER",
        "EXECUTIVE",
        "C_LEVEL",
        "VP_ENG",
        "CTO",
        "REFERRAL_CONTACT",
    }
    return value if value in allowed else "RECRUITER"


def _recipient_class_value(recipient_class: Any) -> str:
    return _normalise_recipient_class(recipient_class).lower()


def _prompt_recipient_class(prompt: str) -> str:
    match = re.search(r"\[recipient_class=([A-Za-z0-9_\- ]+)\]", prompt)
    return match.group(1) if match else "RECRUITER"


def _prompt_target_contact(prompt: str) -> dict[str, Any]:
    match = re.search(r"^Target contact:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$", prompt, re.M)
    if not match:
        return {}
    return {
        "verified_name": match.group(1).strip(),
        "title": match.group(2).strip(),
        "company_name": match.group(3).strip(),
    }


def _stub_message_text(
    *,
    salutation: str,
    recipient_class: str,
    target_title: str,
    target_company: str,
) -> str:
    if recipient_class in {"EXECUTIVE", "C_LEVEL", "CTO"}:
        return (
            f"{salutation} {target_company}'s Agentic AI role reads less like "
            "model building and more like an operating-model rewrite across "
            "underwriting, claims, and GenAI standards. I have built governed "
            "agent workflows with evals, telemetry, and human control baked in. "
            "Worth a brief call on proof I could bring to the rollout?"
        )
    if recipient_class == "SENIOR_TA":
        return (
            f"{salutation} the {target_company} brief is unusually execution-heavy "
            "for AI: claims, underwriting, GenAI standards, and change adoption. "
            "My angle is senior engineering leadership that turns that into "
            "governed agent systems, not slideware. Open to a resume review or "
            "quick chat on where this fits your search?"
        )
    if recipient_class in {"HIRING_MANAGER", "VP_ENG"}:
        return (
            f"{salutation} the {target_title or 'team'} lane at {target_company} "
            "looks like applied agentic AI delivery under real governance pressure. "
            "I bring senior engineering work in orchestration, evals, and safe "
            "workflow automation. Worth a brief call on the execution gap I could cover?"
        )
    return (
        f"{salutation} this {target_company} Agentic AI search looks like the rare "
        "one where production AI, insurance workflows, and governance all matter. "
        "My background is senior agentic AI engineering with evals, orchestration, "
        "and safety built in. Open to a quick resume review for the VP search?"
    )


def _emit_hop5_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
) -> None:
    """Best-effort marker for HOP5 generation availability."""
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


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "DEFAULT_PROVIDER_PROFILE",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_TOP_P",
    "GenerationEngine",
    "ProviderSettings",
]
