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
from dataclasses import dataclass, replace
from typing import Any, Mapping
from urllib import request as urllib_request

from apps_lic.engines.generation_subject_policy import (
    channel_from_length_budget,
    subject_required,
)
from apps_lic.config.model_profiles import (
    resolve_generator_base_url,
    resolve_generator_model,
    resolve_generator_provider,
)
from apps_lic.policy.reasoning_intensity import compact_policy, default_reasoning_policy
from apps_lic.types.linkedin_route_envelope import (
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:8000/v1"
# Resolved from the model-profile SSOT (config/domain_contract/model_profiles.yaml).
DEFAULT_MODEL = resolve_generator_model()
DEFAULT_PROVIDER = resolve_generator_provider()
DEFAULT_PROVIDER_PROFILE = "qwen_vllm"
DEFAULT_TEMPERATURE = 0.82
DEFAULT_TOP_P = 0.92
DEFAULT_MAX_GENERATION_ATTEMPTS = 3
DEFAULT_MAX_TOKENS = 900
_GENERATION_CANDIDATE_PROOF_TERMS = (
    "governed",
    "agent workflows",
    "orchestration",
    "evals",
    "telemetry",
    "safety",
    "senior ai engineering",
    "production ai",
)
_GENERATION_AIG_OPERATING_TERMS = (
    "claims",
    "underwriting",
    "genai",
    "governance",
    "production ai",
    "agent workflows",
)
_GOVERNED_PLATFORM_PROOF = (
    "I designed and operationalized a governed agentic AI platform for "
    "regulated enterprise workflows, combining multi-agent orchestration, "
    "GraphRAG retrieval, policy gating, validation controls, and replayable traces."
)
_GENERIC_DRAFT_PATTERNS = (
    r"\bextensive experience\b",
    r"\bcomplex environments\b",
    r"\bstrategic objectives\b",
    r"\bcurrent initiatives\b",
    r"\bcontribute to your initiatives\b",
    r"\baligns? (?:closely|well)?\b",
    r"\bmy background can support\b",
    r"\bmy expertise\b",
    r"\bsignificantly enhance\b",
    r"\bcomplement your initiatives\b",
    r"\bsupport your goals\b",
    r"\bconversation could be valuable\b",
    r"\bhow might we contribute\b",
    r"\bimpressed by your\b",
    r"\bcame across your leadership\b",
    r"\bhow does .+ approach\b",
    r"\bis it worth 15 minutes\b",
    r"\bwould 15 minutes\b",
    r"\bcould we do 15 minutes\b",
    r"\b15-minute\b",
    r"\bwhich maps to\b",
    r"\bnot demo quality\b",
    r"\bhard call\b",
    r"\bcompare where\b",
    r"\bcontrol plane should live\b",
    r"\brelease[- ]gate\b",
)


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
    max_tokens: int


class GenerationEngine:
    """Emit a LinkedIn recruiter draft from the PA prompt."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        prompt = str(context.get("generation_prompt", ""))
        persona = context.get("sender_persona") or {}
        reasoning_policy = compact_policy(
            context.get("reasoning_policy") or default_reasoning_policy()
        )
        register = str(persona.get("voice_register", "professional") or "professional")
        prompt_recipient_class = _prompt_recipient_class(prompt)
        recipient_class = _normalise_recipient_class(
            context.get("recipient_class")
            or context.get("c03_recipient_class")
            or prompt_recipient_class
            or persona.get("recipient_class")
        )
        prompt_target_contact = _prompt_target_contact(prompt)
        persona_target_contact = (
            persona.get("target_contact") if isinstance(persona.get("target_contact"), dict) else {}
        )
        target_contact = dict(prompt_target_contact)
        target_contact.update(
            {
                key: value
                for key, value in dict(persona_target_contact).items()
                if str(value or "").strip()
            }
        )
        target_role_title = (
            _target_role_title_from_context(context)
            or _target_role_title_from_prompt(prompt)
            or str(target_contact.get("target_role_title", "") or "")
        )
        if target_role_title:
            target_contact["target_role_title"] = target_role_title
        allowed_claim_ids = _allowed_claim_ids_from_context(context, prompt)
        length_budget = _length_budget_from_context(context)
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
                    allowed_claim_ids=allowed_claim_ids,
                    length_budget=length_budget,
                )
            }

        for attempt in range(1, settings.max_generation_attempts + 1):
            qwen_text = self._try_qwen_generation(
                prompt=prompt,
                register=register,
                recipient_class=recipient_class,
                target_company=str(target_contact.get("company_name", "") or ""),
                settings=settings,
                reasoning_policy=reasoning_policy,
                allowed_claim_ids=allowed_claim_ids,
                length_budget=length_budget,
            )
            draft = _draft_from_model_text(
                qwen_text,
                register=register,
                recipient_class=recipient_class,
                target_contact=target_contact,
                template_signature=template_sig,
                settings=settings,
                reasoning_policy=reasoning_policy,
                allowed_claim_ids=allowed_claim_ids,
                length_budget=length_budget,
            )
            if draft:
                draft["attempts"] = attempt
                return {"draft_message": draft}

        if settings.require_qwen_vllm:
            raise RuntimeError("apps_lic_qwen_vllm_required_unavailable")

        return {
            "draft_message": {
                "message_text": "",
                "body": "",
                "channel": _channel_from_length_budget(length_budget),
                "subject_line": "",
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
        target_company: str,
        settings: ProviderSettings,
        reasoning_policy: dict[str, Any],
        allowed_claim_ids: tuple[str, ...],
        length_budget: Mapping[str, Any] | None = None,
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

        company_guidance = _company_prompt_guidance(target_company)
        validation_guidance = _validation_contract_guidance(
            target_company=target_company,
            allowed_claim_ids=allowed_claim_ids,
        )
        hard_cap_chars = _max_chars(length_budget, default=600)
        min_sentences = _min_sentences(length_budget)
        max_sentences = _max_sentences(length_budget) or 3
        min_words = _min_words(length_budget)
        max_words = _max_words(length_budget)
        channel = _channel_from_length_budget(length_budget)
        subject_required = _subject_required(length_budget)
        subject_instruction = (
            "Include subject_line at top level and in each candidate; subject_line must be non-empty and 200 characters or fewer. "
            if subject_required
            else "Do not include a subject_line. "
        )
        route_style_instruction = _route_style_instruction(length_budget)
        cta_instruction = (
            "The last body sentence before the signature must be a low-friction question ending with ?. "
            if subject_required
            else "The final body sentence must be a low-friction connection ask ending with ?. "
        )
        signature_instruction = (
            "End each candidate with Amit on its own final line. "
            if subject_required
            else "Do not add a signature, sender name, or sign-off. "
        )
        proof_instruction = (
            "Include one concrete Amit proof point as one sentence. "
            if subject_required
            else "Use at most one compact Amit proof clause; omit revenue, margin, dollar metrics, and proof stacking. "
        )
        paragraph_instruction = (
            "Use 3 to 4 compact paragraphs if useful. "
            if subject_required
            else "Use max 2 short paragraphs. "
        )
        length_instruction = (
            f"message_text must be {hard_cap_chars} characters or fewer, "
            f"between {min_sentences} and {max_sentences} body sentences, "
            f"and at least {min_words} words. "
            if min_sentences and min_words
            else f"message_text must be {hard_cap_chars} characters or fewer and {max_sentences} sentences or fewer. "
        )
        if max_words:
            length_instruction += f"Aim for no more than {max_words} words. "
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
                            f"You draft LinkedIn outreach for Amit Ayer on channel {channel}. "
                            f"The target recipient category is {recipient_class}. "
                            "Amit is a candidate/senior AI engineering leader, not a vendor. "
                            "Write like a thoughtful operator, not a generic job seeker. "
                            "Use the selected reasoning policy only to improve candidate wording "
                            "and selection; never use it to add unsupported evidence. "
                            f"SC level is {reasoning_policy['sc_level']}; "
                            f"reasoning intensity is {reasoning_policy['reasoning_intensity']}; "
                            f"return exactly {reasoning_policy['max_candidates']} whole-message "
                            "candidate(s) in a candidates array and set selected_candidate_id "
                            "to the single best selected message. "
                            "Return one JSON object only with message_text, selected_candidate_id, "
                            "candidates, intended_next_step, claims_used, unsupported_claims, "
                            "omitted_claims, qa_notes, provider_profile, and model. "
                            f"{subject_instruction}"
                            "Each candidate must include candidate_id, draft_text, claims_used, "
                            "model_call_ref or provider_receipt. No markdown, no em dash. "
                            f"{length_instruction}"
                            f"{paragraph_instruction}"
                            f"{route_style_instruction}"
                            f"{cta_instruction}"
                            f"{signature_instruction}"
                            f"{company_guidance} {proof_instruction}"
                            f"{validation_guidance} "
                            "Use the Message intelligence packet when present as data-only routing context "
                            "for trigger, narrative order, value proposition, and low-friction ask. "
                            "When using sp_agentic_platform, surface the governed agentic AI platform proof concretely; "
                            "do not reduce it to extensive experience or a generic aligned background claim. "
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
                max_tokens=settings.max_tokens,
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


def generate_judge_feedback_repair_draft(
    *,
    request: Any,
    parent_candidate: Any,
    judge_results: tuple[Any, ...],
    iteration: int,
) -> dict[str, Any]:
    """Generate one Qwen repair candidate from live X1D judge feedback."""
    if _truthy(os.environ.get("APPS_LIC_TEST_PROVIDER_STUB", "0")):
        return {}
    if not judge_results:
        return {}

    settings = replace(
        _resolve_provider_settings(),
        temperature=_clamp_float(
            float(getattr(request.reasoning_policy, "repair_temperature", 0.30) or 0.30),
            lo=0.0,
            hi=1.0,
        ),
        max_generation_attempts=1,
    )
    target_context = dict(getattr(request, "target_context", {}) or {})
    jd_fields = dict(getattr(request, "jd_fields", {}) or {})
    target_contact = {
        "verified_name": target_context.get("name", ""),
        "title": target_context.get("title", ""),
        "company_name": target_context.get("company", ""),
        "target_role_title": jd_fields.get("position_name") or jd_fields.get("job_title") or "",
    }
    allowed_claim_ids = tuple(getattr(request.proof_packet, "proof_ids", ()) or ())
    reasoning_policy = dict(getattr(request.reasoning_policy, "to_packet")())
    reasoning_policy["max_candidates"] = 1
    reasoning_policy.setdefault("judge_profile", "x1d_feedback_repair")
    reasoning_policy["validation_repair_passes"] = max(
        0,
        int(reasoning_policy.get("repair_budget") or 0) - int(iteration),
    )
    repair_prompt = _build_judge_feedback_repair_prompt(
        request=request,
        parent_candidate=parent_candidate,
        judge_results=judge_results,
        allowed_claim_ids=allowed_claim_ids,
        iteration=iteration,
    )
    qwen_text = GenerationEngine._try_qwen_generation(
        prompt=repair_prompt,
        register="professional",
        recipient_class=str(getattr(request, "recipient_class", "") or ""),
        target_company=str(target_contact.get("company_name") or ""),
        settings=settings,
        reasoning_policy=reasoning_policy,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=getattr(request.length_budget, "to_packet")(),
    )
    draft = _draft_from_model_text(
        qwen_text,
        register="professional",
        recipient_class=str(getattr(request, "recipient_class", "") or ""),
        target_contact=target_contact,
        template_signature=hashlib.sha1(
            repair_prompt.encode("utf-8", errors="ignore")
        ).hexdigest()[:8],
        settings=settings,
        reasoning_policy=reasoning_policy,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=getattr(request.length_budget, "to_packet")(),
    )
    if draft:
        draft["repair_iteration"] = iteration
        draft["parent_candidate_id"] = str(getattr(parent_candidate, "candidate_id", "") or "")
    return draft


def _resolve_provider_settings() -> ProviderSettings:
    # Model + base URL resolve from the model-profile SSOT
    # (config/domain_contract/model_profiles.yaml). Env vars are documented
    # overrides declared in that file, not the source of truth.
    base_url = resolve_generator_base_url() or DEFAULT_BASE_URL
    model = resolve_generator_model() or DEFAULT_MODEL
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
        max_generation_attempts=_clamp_int(
            _int_env("APPS_LIC_QWEN_MAX_GENERATION_ATTEMPTS", DEFAULT_MAX_GENERATION_ATTEMPTS),
            lo=1,
            hi=3,
        ),
        max_tokens=_clamp_int(
            _int_env("APPS_LIC_QWEN_MAX_TOKENS", DEFAULT_MAX_TOKENS),
            lo=300,
            hi=1500,
        ),
    )


def _build_judge_feedback_repair_prompt(
    *,
    request: Any,
    parent_candidate: Any,
    judge_results: tuple[Any, ...],
    allowed_claim_ids: tuple[str, ...],
    iteration: int,
) -> str:
    length_budget = getattr(request.length_budget, "to_packet")()
    channel = _channel_from_length_budget(length_budget)
    subject_required = _subject_required(length_budget)
    min_sentences = _min_sentences(length_budget)
    max_sentences = _max_sentences(length_budget)
    min_words = _min_words(length_budget)
    max_words = _max_words(length_budget)
    failed = []
    for result in judge_results:
        failed.append(
            {
                "judge_id": str(getattr(result, "judge_id", "") or ""),
                "score": float(getattr(result, "score", 0.0) or 0.0),
                "threshold": float(getattr(result, "threshold", 0.0) or 0.0),
                "passed": bool(getattr(result, "passed", False)),
                "issues": list(getattr(result, "issues", ()) or ()),
                "required_repairs": list(getattr(result, "required_repairs", ()) or ()),
            }
        )
    payload = {
        "task": "repair_linkedin_draft_from_independent_x1d_judge_feedback",
        "iteration": iteration,
        "hard_rules": [
            "Return one JSON object only.",
            "Return exactly one candidate in candidates.",
            "Do not introduce any claim outside allowed_claim_ids.",
            "Use claims_used only from allowed_claim_ids.",
            f"Preserve route channel {channel}.",
            (
                "Use a non-empty InMail subject_line <=200 characters aligned to jd_fields.position_name, not the recipient title."
                if subject_required
                else "Do not add a subject_line for this route."
            ),
            "Change the body materially from parent_candidate; never return the parent draft unchanged.",
            (
                f"For InMail, the body must be {min_sentences}-{max_sentences} sentences, "
                f"at least {min_words} words, and under the hard character cap."
                if subject_required and min_sentences and max_sentences and min_words
                else "Respect the route length budget."
            ),
            (
                f"Aim for no more than {max_words} words."
                if subject_required and max_words
                else "Keep the body concise."
            ),
            "The last body sentence before the signature must be a low-friction question ending with ?.",
            "End the message with Amit on its own final line.",
            "Do not mention judges, scores, validation, gates, or repairs in the message.",
        ],
        "channel": channel,
        "subject_required": subject_required,
        "recipient_class": str(getattr(request, "recipient_class", "") or ""),
        "message_type": str(getattr(request, "message_type", "") or ""),
        "campaign_objective": str(getattr(request, "campaign_objective", "") or ""),
        "desired_next_step": str(getattr(request, "desired_next_step", "") or ""),
        "target_context": dict(getattr(request, "target_context", {}) or {}),
        "jd_fields": dict(getattr(request, "jd_fields", {}) or {}),
        "length_budget": length_budget,
        "allowed_claim_ids": list(allowed_claim_ids),
        "proof_packet": getattr(request.proof_packet, "to_packet")(),
        "message_intelligence_packet": (
            getattr(getattr(request, "message_intelligence_packet", None), "to_packet")()
            if hasattr(getattr(request, "message_intelligence_packet", None), "to_packet")
            else {}
        ),
        "parent_candidate": getattr(parent_candidate, "to_packet")(),
        "judge_feedback": failed,
        "required_json_shape": {
            "message_text": "string",
            "subject_line": "string" if subject_required else "",
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "subject_line": "string" if subject_required else "",
                    "draft_text": "string",
                    "claims_used": list(allowed_claim_ids),
                    "model_call_ref": "string",
                    "provider_receipt": "string",
                }
            ],
            "intended_next_step": "string",
            "claims_used": list(allowed_claim_ids),
            "unsupported_claims": [],
            "omitted_claims": [],
            "qa_notes": [],
            "provider_profile": DEFAULT_PROVIDER_PROFILE,
            "model": DEFAULT_MODEL,
        },
    }
    return (
        "Repair the LinkedIn draft using the independent judge feedback while "
        "staying inside the proof packet and length budget. Return JSON only.\n"
        + json.dumps(payload, sort_keys=True)
    )


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _truthy(raw: str | None) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on"}


def _clamp_float(value: float, *, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _clamp_int(value: int, *, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


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


def _loads_first_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder(strict=False)
    stripped = _strip_json_fence(text)
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _sanitize_message_text(
    text: str,
    *,
    target_company: str,
    target_name: str = "",
    target_title: str = "",
    target_role_title: str = "",
    recipient_class: str = "",
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> str:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"\n\s*(best|regards|thanks),?\s*\n\s*amit ayer\s*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\n\s*amit ayer\s*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\b(best|regards|thanks),?\s+amit\.?\s*$", "", cleaned, flags=re.I)
    replacements = (
        (r"\bpotential synergies\b", "where governed agent workflows fit"),
        (r"\bdiscuss opportunities\b", "compare fit"),
        (r"\bexplore opportunities\b", "compare fit"),
        (r"\bpotential opportunities\b", "where governed agent workflows fit"),
        (r"\bi noticed your role\b", "your role"),
        (r"\bi noticed your leadership\b", "your leadership"),
        (r"\bi noticed you\b", "your work"),
        (r"\bgiven your expertise\b", "given this remit"),
        (r"\bi believe my background aligns\b", "my background maps"),
    )
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if _needs_quality_repair(
        cleaned,
        target_company=target_company,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=length_budget,
    ):
        cleaned = _repair_message_text(
            target_company=target_company,
            target_name=target_name,
            target_title=target_title,
            target_role_title=target_role_title,
            recipient_class=recipient_class,
            allowed_claim_ids=allowed_claim_ids,
            length_budget=length_budget,
        )
    cleaned = _expand_inmail_to_budget(
        cleaned,
        target_company=target_company,
        target_role_title=target_role_title,
        recipient_class=recipient_class,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=length_budget,
    )
    cleaned = _trim_to_sentence_budget(cleaned, length_budget=length_budget)
    return _trim_to_linkedin_limit(cleaned, length_budget=length_budget)


def _needs_quality_repair(
    text: str,
    *,
    target_company: str,
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> bool:
    lowered = text.lower()
    if re.match(r"\s*(?:hi|dear)\s+there\b", text, flags=re.IGNORECASE):
        return True
    if "brief fit review for that role" in lowered:
        return True
    if "?" not in text:
        return True
    required_claim_marker = (
        "governed agentic ai platform"
        if _is_connection_request_budget(length_budget)
        else "designed and operationalized a governed agentic ai platform"
    )
    if allowed_claim_ids and required_claim_marker not in lowered:
        return True
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in _GENERIC_DRAFT_PATTERNS):
        return True
    key = _company_key(target_company)
    if key == "aig":
        return _count_terms(text, ("vp, global head of agentic ai solutions", "regulated insurance", "claims", "underwriting", "genai standards")) < 2
    if key == "citi":
        return _count_terms(text, ("head of ai strategy", "regulated finance", "responsible ai", "risk controls", "platform execution")) < 2
    if key == "neo4j":
        return _count_terms(text, ("vp of product management", "graph intelligence", "knowledge graph", "agentic ai product", "context")) < 2
    return False


def _first_name_from_target(target_name: str, fallback_text: str) -> str:
    name = _clean_text(target_name)
    if name:
        return name.split()[0]
    match = re.search(r"^(?:hi|dear)\s+([^,\n]+)", fallback_text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip().split()[0]
    return "there"


def _repair_connection_request_text(
    *,
    target_company: str,
    target_name: str,
    target_title: str,
    target_role_title: str = "",
    recipient_class: str,
    length_budget: Mapping[str, Any] | None = None,
) -> str:
    key = _company_key(target_company)
    first = _first_name_from_target(target_name, "")
    company = _clean_text(target_company) or "the company"
    title = _clean_text(target_role_title) or _clean_text(target_title)
    recipient = _normalise_recipient_class(recipient_class)
    if key == "aig":
        if recipient in {"RECRUITER", "SENIOR_TA", "TALENT_ACQUISITION"} and title:
            reason = (
                f"{company}'s {title} search connects claims, underwriting, GenAI standards, "
                "and governance with my governed agentic AI platform background."
            )
        else:
            reason = (
                f"{company}'s agentic AI work across claims, underwriting, and governance "
                "overlaps with my governed agentic AI platform background."
            )
    elif key == "citi":
        reason = (
            f"{company}'s responsible-AI work across risk controls and platform execution "
            "overlaps with my governed agentic AI platform background."
        )
    elif key == "neo4j":
        reason = (
            f"{company}'s graph-backed agentic AI work overlaps with my governed agentic AI "
            "platform and GraphRAG background."
        )
    else:
        reason = (
            f"{company}'s AI platform work overlaps with my governed agentic AI platform "
            "background."
        )
    text = f"Hi {first}, {reason} Open to connecting?"
    text = _trim_to_sentence_budget(text, length_budget=length_budget)
    return _trim_to_linkedin_limit(text, length_budget=length_budget)


def _repair_message_text(
    *,
    target_company: str,
    target_name: str,
    target_title: str,
    target_role_title: str = "",
    recipient_class: str,
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> str:
    key = _company_key(target_company)
    first = _first_name_from_target(target_name, "")
    recipient = _normalise_recipient_class(recipient_class)
    title = _clean_text(target_role_title) or _clean_text(target_title)
    c_level_tight = recipient in {"C_LEVEL", "CEO", "CTO"}
    if _is_connection_request_budget(length_budget):
        return _repair_connection_request_text(
            target_company=target_company,
            target_name=target_name,
            target_title=target_title,
            target_role_title=target_role_title,
            recipient_class=recipient,
            length_budget=length_budget,
        )
    proof = _repair_proof_sentence(allowed_claim_ids, c_level_tight=c_level_tight)
    if key == "aig":
        if recipient in {"C_LEVEL", "CEO", "CTO"}:
            opener = (
                "AIG's agentic AI work under the Global CDO puts claims, underwriting, "
                "and governance in the same operating lane."
            )
            ask = "Would a brief fit exchange on governed agent platform execution be useful?"
        elif recipient == "EXECUTIVE":
            opener = (
                "Reinsurance capital optimization and agentic AI share a constraint: "
                "governed decisions must be traceable before they scale."
            )
            ask = "Would a concise exchange on fit for governed AI execution be useful?"
        else:
            opener = (
                "AIG's VP, Global Head of Agentic AI Solutions role sits in regulated "
                "insurance AI across claims, underwriting, GenAI standards, and governance."
            )
            ask = "Would a quick screen on claims, underwriting, and GenAI governance fit be useful?"
    elif key == "citi":
        if recipient in {"C_LEVEL", "CEO", "CTO"}:
            opener = (
                "With Citi Sky making shared technology services visible, the CIO-level AI question is where "
                "policy-gated, traceable agents should ship before teams scale them."
            )
            ask = "Would a brief fit exchange on governed AI platform execution be useful?"
        elif recipient in {"EXECUTIVE", "HIRING_MANAGER", "VP_ENG"}:
            opener = (
                "Citi's responsible AI work needs operating leaders who can connect "
                "risk controls, data governance, and platform execution."
            )
            ask = "Would a quick fit signal for responsible AI platform execution be useful?"
        else:
            opener = (
                "Citi's Head of AI Strategy role needs governed AI that can survive "
                "risk controls and responsible-AI review."
            )
            ask = "Would a quick screen on that firmwide AI governance fit be useful?"
    elif key == "neo4j":
        if recipient in {"C_LEVEL", "CEO", "CTO"}:
            opener = (
                "For Neo4j's CPO, the agentic AI question is product control: "
                "when should graph-backed context become enterprise-agent infrastructure rather than another retrieval feature?"
            )
            ask = "Would a brief exchange on GraphRAG reliability and graph-context controls be useful?"
        elif recipient in {"EXECUTIVE", "HIRING_MANAGER", "VP_ENG"}:
            opener = (
                "Neo4j's agentic AI product work sits where graph intelligence, "
                "knowledge-graph context, and product execution meet."
            )
            ask = "Would a quick fit signal for graph intelligence and agentic AI product execution be useful?"
        else:
            if "sp_runtime_reliability" in allowed_claim_ids:
                opener = (
                    "Neo4j's Agentic AI product mandate needs graph-backed context, "
                    "agent trust, and reliable evaluation loops."
                )
            else:
                opener = (
                    "Neo4j's Agentic AI product mandate needs graph-backed context "
                    "that enterprise agents can trust."
                )
            ask = "Would a quick recruiter screen on the VP Agentic AI product fit be useful?"
    else:
        opener = "The role appears to need governed AI delivery, evidence discipline, and operating judgment."
        ask = "Would a brief fit review be useful?"
    body = f"Hi {first}, {opener} {proof} {ask}"
    return _expand_inmail_to_budget(
        body,
        target_company=target_company,
        target_role_title=title,
        recipient_class=recipient,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=length_budget,
    )


def _expand_inmail_to_budget(
    text: str,
    *,
    target_company: str,
    target_role_title: str,
    recipient_class: str,
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None,
) -> str:
    if not _subject_required(length_budget):
        return text
    min_sentences = _min_sentences(length_budget)
    min_words = _min_words(length_budget)
    max_sentences = _max_sentences(length_budget) or max(min_sentences, 5)
    if not min_sentences and not min_words:
        return text

    body = _strip_terminal_signature(text)
    cta = ""
    sentences = _sentence_pieces(body)
    if sentences and sentences[-1].endswith("?"):
        cta = sentences[-1]
        core_sentences = sentences[:-1]
    else:
        core_sentences = sentences

    def _compose() -> str:
        parts = [*core_sentences]
        if cta:
            parts.append(cta)
        return " ".join(part.strip() for part in parts if part.strip()).strip()

    expanded = _compose()
    for sentence in _inmail_expansion_sentences(
        target_company=target_company,
        target_role_title=target_role_title,
        recipient_class=recipient_class,
        allowed_claim_ids=allowed_claim_ids,
    ):
        if _sentence_count_text(expanded) >= max_sentences:
            break
        if _inmail_budget_satisfied(expanded, min_sentences=min_sentences, min_words=min_words):
            break
        if _contains_sentence(expanded, sentence):
            continue
        core_sentences.append(sentence)
        expanded = _compose()

    return expanded or text


def _inmail_budget_satisfied(text: str, *, min_sentences: int, min_words: int) -> bool:
    sentence_ok = not min_sentences or _sentence_count_text(text) >= min_sentences
    word_ok = not min_words or _word_count_text(text) >= min_words
    return sentence_ok and word_ok


def _inmail_expansion_sentences(
    *,
    target_company: str,
    target_role_title: str,
    recipient_class: str,
    allowed_claim_ids: tuple[str, ...],
) -> tuple[str, ...]:
    key = _company_key(target_company)
    role = _clean_text(target_role_title) or "the open role"
    recipient = _normalise_recipient_class(recipient_class)
    platform_sentence = (
        "The strongest fit signal is governed reuse: policy-gated retrieval, validation controls, and replayable traces that make agent decisions auditable."
        if "sp_agentic_platform" in allowed_claim_ids
        else "The relevant proof is execution depth in governed AI delivery rather than generic AI interest."
    )
    reliability_sentence = (
        "I can also speak to evaluation gates, telemetry, rollback controls, and AI CI/CD discipline in production."
        if "sp_runtime_reliability" in allowed_claim_ids
        else "That gives the note a concrete operating lens rather than a broad background summary."
    )
    commercial_sentence = (
        "My value proposition is practical reuse: turning agentic AI primitives into platform services that teams can govern and adopt repeatedly."
        if "sp_platform_commercialization" in allowed_claim_ids
        else "The fit is strongest where product judgment and governed delivery have to meet."
    )

    if key == "aig":
        base = (
            "That makes the fit specific to AIG: agentic AI has to connect with accountable claims, underwriting, and GenAI standards.",
            platform_sentence,
            reliability_sentence,
        )
    elif key == "citi":
        base = (
            f"That maps to {role}, where responsible-AI review, risk controls, and platform execution have to move together.",
            reliability_sentence,
            platform_sentence,
        )
    elif key == "neo4j":
        base = (
            f"That maps to {role}, where graph context and agent reliability need product-grade execution.",
            platform_sentence,
            "The product execution detail is policy-gated graph retrieval with validation controls and replayable traces for agent reliability.",
        )
    else:
        base = (
            f"That maps to {role}, where the work needs governed AI delivery and practical execution judgment.",
            platform_sentence,
            reliability_sentence,
        )

    if recipient in {"C_LEVEL", "CEO", "CTO", "EXECUTIVE", "HIRING_MANAGER", "VP_ENG"}:
        return (*base[:1], commercial_sentence, *base[1:])
    if recipient in {"RECRUITER", "SENIOR_TA", "TALENT_ACQUISITION"}:
        ta_sentence = (
            "The role-specific bridge is implementation detail: policy-gated retrieval, validation controls, and replayable traces matched to the role scope."
        )
        return (*base[:1], ta_sentence, *base[1:])
    return base


def _strip_terminal_signature(text: str) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(
        r"(?:\n|\A)\s*(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?\s*\Z",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def _sentence_pieces(text: str) -> list[str]:
    matches = list(re.finditer(r"[^.!?]+[.!?]", text))
    pieces = [match.group(0).strip() for match in matches if match.group(0).strip()]
    end = matches[-1].end() if matches else 0
    tail = text[end:].strip()
    if tail:
        pieces.append(tail)
    return pieces


def _contains_sentence(text: str, sentence: str) -> bool:
    return re.sub(r"\W+", " ", sentence).strip().lower() in re.sub(r"\W+", " ", text).strip().lower()


def _repair_proof_sentence(
    allowed_claim_ids: tuple[str, ...],
    *,
    c_level_tight: bool = False,
) -> str:
    allowed = set(allowed_claim_ids)
    if "sp_agentic_platform" in allowed and "sp_platform_commercialization" in allowed:
        if "sp_runtime_reliability" in allowed:
            return (
                "I designed and operationalized a governed agentic AI platform for regulated enterprise workflows, "
                "combining multi-agent orchestration, GraphRAG retrieval, policy gating, validation controls, and replayable traces, "
                "and I productized agentic AI primitives into reusable platform services."
            )
        return (
            "I designed and operationalized a governed agentic AI platform for regulated enterprise workflows, "
            "combining multi-agent orchestration, GraphRAG retrieval, policy gating, validation controls, and replayable traces, "
            "and I productized agentic AI primitives into reusable platform services."
        )
    if (
        c_level_tight
        and "sp_platform_commercialization" in allowed
        and "sp_runtime_reliability" in allowed
    ):
        return (
            "I productized agentic AI primitives into reusable platform services while pairing "
            "delivery with evaluation gates, telemetry, and rollback controls."
        )
    if c_level_tight and "sp_platform_commercialization" in allowed:
        return (
            "I productized agentic AI primitives into reusable platform services for enterprise adoption."
        )
    if "sp_runtime_reliability" in allowed and "sp_platform_commercialization" in allowed:
        return (
            "I productized agentic AI primitives into reusable platform services and strengthened "
            "evaluation gates, telemetry, rollback controls, and AI CI/CD standards."
        )
    if "sp_runtime_reliability" in allowed:
        return (
            "I designed and operationalized a governed agentic AI platform for regulated enterprise workflows, "
            "combining multi-agent orchestration and GraphRAG retrieval, and strengthened evaluation gates, "
            "telemetry, rollback controls, and AI CI/CD standards."
        )
    if "sp_platform_commercialization" in allowed:
        return (
            "I productized agentic AI primitives into reusable platform services for enterprise adoption."
        )
    return _GOVERNED_PLATFORM_PROOF


def _claims_from_message_text(
    text: str,
    *,
    existing_claims: tuple[str, ...],
    allowed_claim_ids: tuple[str, ...],
) -> tuple[str, ...]:
    allowed = set(allowed_claim_ids)
    claims = list(existing_claims)
    lowered = text.lower()
    additions = (
        (
            "sp_agentic_platform",
            "governed agentic ai platform",
        ),
        ("sp_runtime_reliability", "evaluation gates"),
        ("sp_runtime_reliability", "validation controls"),
        ("sp_runtime_reliability", "replayable traces"),
        ("sp_platform_commercialization", "$22m in ip-led revenue"),
        ("sp_platform_commercialization", "productized agentic ai primitives"),
        ("sp_quant_governance_foundation", "governance foundation"),
    )
    for claim_id, marker in additions:
        if claim_id in allowed and marker in lowered and claim_id not in claims:
            claims.append(claim_id)
    return tuple(dict.fromkeys(claim for claim in claims if claim in allowed))


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _count_terms(text: str, terms: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if term in lowered)


def _append_short_sentence(text: str, sentence: str) -> str:
    if sentence.lower() in text.lower():
        return text
    if not text:
        return sentence
    if text.endswith((".", "!", "?")):
        return f"{text} {sentence}"
    return f"{text}. {sentence}"


def _sentence_count_text(text: str) -> int:
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


def _word_count_text(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _min_sentences(length_budget: Mapping[str, Any] | None) -> int:
    if not isinstance(length_budget, Mapping):
        return 0
    try:
        return int(length_budget.get("min_sentences") or 0)
    except (TypeError, ValueError):
        return 0


def _max_sentences(length_budget: Mapping[str, Any] | None) -> int:
    if not isinstance(length_budget, Mapping):
        return 0
    try:
        return int(length_budget.get("max_sentences") or 0)
    except (TypeError, ValueError):
        return 0


def _min_words(length_budget: Mapping[str, Any] | None) -> int:
    if not isinstance(length_budget, Mapping):
        return 0
    try:
        return int(length_budget.get("min_words") or 0)
    except (TypeError, ValueError):
        return 0


def _max_words(length_budget: Mapping[str, Any] | None) -> int:
    if not isinstance(length_budget, Mapping):
        return 0
    try:
        return int(length_budget.get("max_words") or 0)
    except (TypeError, ValueError):
        return 0


def _subject_required(length_budget: Mapping[str, Any] | None) -> bool:
    return subject_required(length_budget)


def _channel_from_length_budget(length_budget: Mapping[str, Any] | None) -> str:
    return channel_from_length_budget(length_budget)


def _is_connection_request_budget(length_budget: Mapping[str, Any] | None) -> bool:
    if _subject_required(length_budget):
        return False
    channel = _channel_from_length_budget(length_budget).strip().lower()
    if channel == "linkedin_chat":
        return True
    if not isinstance(length_budget, Mapping):
        return False
    budget_key = str(length_budget.get("budget_key") or "").strip().lower()
    route_family = str(length_budget.get("route_family") or "").strip().upper()
    if "connection" in budget_key or route_family == "CONNECTION_REQ":
        return True
    try:
        hard_cap = int(length_budget.get("hard_cap_chars") or 0)
    except (TypeError, ValueError):
        hard_cap = 0
    return bool(hard_cap and hard_cap <= CONNECTION_REQUEST_CHAR_CAP)


def _route_style_instruction(length_budget: Mapping[str, Any] | None) -> str:
    if _is_connection_request_budget(length_budget):
        return (
            "This is a LinkedIn connection request, not an InMail or pitch: "
            "relationship-first, at most two compact sentences, no meeting-time ask, "
            "no compare-where framing, no release-gate consulting language, and no "
            "commercial metrics. "
        )
    if _subject_required(length_budget):
        return (
            "This is an InMail, but it must read as a candidate relationship note, "
            "not a sales pitch: company insight, one Amit proof sentence, value "
            "proposition, and a low-pressure fit question; no 15-minute asks, "
            "compare-where framing, or release-gate consulting language. "
        )
    return (
        "Keep the note relationship-first, concrete, and non-salesy; no meeting-time "
        "ask or consulting-style comparison framing. "
    )


def _sanitize_subject_line(
    value: Any,
    *,
    target_company: str = "",
    target_title: str = "",
    target_role_title: str = "",
) -> str:
    subject = _clean_text(value)
    subject = re.sub(r"^(subject|re)\s*:\s*", "", subject, flags=re.IGNORECASE).strip()
    if not subject or _subject_should_use_target_role(
        subject,
        target_title=target_title,
        target_role_title=target_role_title,
    ):
        subject = _default_subject_line(
            target_company=target_company,
            target_title=target_title,
            target_role_title=target_role_title,
        )
    return subject[:200].rstrip(" .")


def _default_subject_line(
    *,
    target_company: str,
    target_title: str = "",
    target_role_title: str = "",
) -> str:
    company = _clean_text(target_company) or "AI platform work"
    title = _clean_text(target_role_title) or _clean_text(target_title)
    if title:
        return f"{title} fit at {company}"[:200].rstrip(" .")
    return f"{company} AI leadership fit"[:200].rstrip(" .")


def _subject_should_use_target_role(
    subject: str,
    *,
    target_title: str,
    target_role_title: str,
) -> bool:
    role_tokens = _meaningful_subject_tokens(target_role_title)
    if not role_tokens:
        return False
    subject_tokens = _meaningful_subject_tokens(subject)
    if subject_tokens & role_tokens:
        return False
    return True


def _meaningful_subject_tokens(value: str) -> set[str]:
    stop = {
        "and",
        "the",
        "for",
        "fit",
        "role",
        "at",
        "with",
        "exploring",
        "opportunities",
        "opportunity",
        "ai",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if token not in stop and (len(token) >= 3 or token == "vp")
    }


def _max_chars(length_budget: Mapping[str, Any] | None, *, default: int = 590) -> int:
    if not isinstance(length_budget, Mapping):
        return default
    try:
        value = int(length_budget.get("hard_cap_chars") or default)
    except (TypeError, ValueError):
        return default
    return max(120, min(INMAIL_BODY_CHAR_CAP, value))


def _append_required_phrase(
    text: str,
    sentence: str,
    clause: str,
    *,
    length_budget: Mapping[str, Any] | None,
) -> str:
    if sentence.lower() in text.lower() or clause.lower() in text.lower():
        return text
    max_sentences = _max_sentences(length_budget)
    if max_sentences and _sentence_count_text(text) >= max_sentences:
        base = text.rstrip(" .!?")
        return f"{base}; {clause}."
    return _append_short_sentence(text, sentence)


def _trim_to_sentence_budget(
    text: str,
    *,
    length_budget: Mapping[str, Any] | None,
) -> str:
    max_sentences = _max_sentences(length_budget)
    if not max_sentences or _sentence_count_text(text) <= max_sentences:
        return text
    pieces = [
        part.strip()
        for part in re.findall(r"[^.!?]+[.!?]?", text)
        if part.strip()
    ]
    trimmed = " ".join(pieces[:max_sentences]).strip()
    if trimmed and not trimmed.endswith((".", "!", "?")):
        trimmed += "."
    return trimmed or text


def _trim_to_linkedin_limit(
    text: str,
    *,
    max_chars: int = 590,
    length_budget: Mapping[str, Any] | None = None,
) -> str:
    max_chars = _max_chars(length_budget, default=max_chars)
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    clipped = cleaned[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:")
    if not clipped.endswith((".", "!", "?")):
        clipped += "."
    return clipped


def _draft_from_model_text(
    text: str,
    *,
    register: str,
    recipient_class: str,
    target_contact: dict[str, Any],
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not text.strip():
        return {}
    parsed = _loads_first_json_object(text)
    if not parsed:
        return {}
    if isinstance(parsed.get("draft_message"), dict):
        parsed = parsed["draft_message"]

    message_text = str(parsed.get("message_text") or parsed.get("body") or "").strip()
    if not message_text:
        return {}
    target_company = str(target_contact.get("company_name", "") or "")
    target_name = str(target_contact.get("verified_name", "") or "")
    target_title = str(target_contact.get("title", "") or "")
    target_role_title = str(target_contact.get("target_role_title", "") or "")
    subject_line = ""
    if _subject_required(length_budget):
        subject_line = _sanitize_subject_line(
            parsed.get("subject_line") or parsed.get("subject"),
            target_company=target_company,
            target_title=target_title,
            target_role_title=target_role_title,
        )
    claims_used = parsed.get("claims_used")
    unsupported_claims = parsed.get("unsupported_claims")
    omitted_claims = parsed.get("omitted_claims")
    qa_notes = parsed.get("qa_notes")
    candidate_entries = _normalized_candidate_entries(
        parsed.get("candidates"),
        template_signature=template_signature,
        settings=settings,
        reasoning_policy=reasoning_policy,
        fallback_claim_ids=claims_used if isinstance(claims_used, list) else [],
        selected_message_text=message_text,
        allowed_claim_ids=allowed_claim_ids,
        target_company=target_company,
        target_name=target_name,
        target_title=target_title,
        target_role_title=target_role_title,
        recipient_class=recipient_class,
        length_budget=length_budget,
    )
    selected_candidate_id = str(parsed.get("selected_candidate_id") or "").strip()
    if not selected_candidate_id and candidate_entries:
        selected_candidate_id = str(candidate_entries[0].get("candidate_id") or "").strip()
    selected_entry = _candidate_by_id(candidate_entries, selected_candidate_id)
    normalized_claims = _candidate_claims(
        fallback_claim_ids=claims_used if isinstance(claims_used, list) else [],
        allowed_claim_ids=allowed_claim_ids,
    )
    if selected_entry is not None:
        selected_text = str(selected_entry.get("draft_text") or selected_entry.get("message_text") or "").strip()
        if selected_text:
            message_text = selected_text
        if _subject_required(length_budget):
            subject_line = _sanitize_subject_line(
                selected_entry.get("subject_line") or subject_line,
                target_company=target_company,
                target_title=target_title,
                target_role_title=target_role_title,
            )
        normalized_claims = _candidate_claims(
            fallback_claim_ids=selected_entry.get("claims_used"),
            allowed_claim_ids=allowed_claim_ids,
        )
    message_text = _sanitize_message_text(
        message_text,
        target_company=target_company,
        target_name=target_name,
        target_title=target_title,
        target_role_title=target_role_title,
        recipient_class=recipient_class,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=length_budget,
    )
    normalized_claims = _claims_from_message_text(
        message_text,
        existing_claims=normalized_claims,
        allowed_claim_ids=allowed_claim_ids,
    )
    if selected_entry is not None:
        selected_entry["subject_line"] = subject_line
        selected_entry["draft_text"] = message_text
        selected_entry["message_text"] = message_text
        selected_entry["claims_used"] = list(normalized_claims)
    return {
        "message_text": message_text,
        "body": message_text,
        "channel": _channel_from_length_budget(length_budget),
        "subject_line": subject_line,
        "recipient_class": _recipient_class_value(
            parsed.get("recipient_class") or recipient_class
        ),
        "recipient_category": recipient_class,
        "target_contact_name": target_name,
        "target_contact_title": target_title,
        "target_contact_company": target_company,
        "intended_next_step": str(parsed.get("intended_next_step") or "").strip(),
        "claims_used": normalized_claims,
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
        "selected_candidate_id": selected_candidate_id,
        "candidates": candidate_entries,
        "candidate_count": (
            len(candidate_entries)
            if candidate_entries
            else int(parsed.get("candidate_count") or reasoning_policy["max_candidates"])
        ),
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


def _candidate_count(reasoning_policy: dict[str, Any]) -> int:
    try:
        value = int(reasoning_policy.get("max_candidates") or 1)
    except (TypeError, ValueError):
        value = 1
    return max(1, min(value, 3))


def _stub_candidate_id(
    *,
    template_signature: str,
    index: int,
    message_text: str,
) -> str:
    digest = hashlib.sha1(
        f"{template_signature}:{index}:{message_text}".encode(
            "utf-8",
            errors="ignore",
        )
    ).hexdigest()[:10]
    return f"draft_candidate_{index + 1}_{digest}"


def _candidate_claims(
    *,
    fallback_claim_ids: Any,
    allowed_claim_ids: tuple[str, ...] = (),
) -> list[str]:
    if isinstance(fallback_claim_ids, list):
        cleaned = [
            str(item).strip()
            for item in fallback_claim_ids
            if str(item).strip()
            and (not allowed_claim_ids or str(item).strip() in allowed_claim_ids)
        ]
        if cleaned:
            return list(dict.fromkeys(cleaned))
    return [allowed_claim_ids[0]] if allowed_claim_ids else []


def _stub_candidates(
    *,
    salutation: str,
    recipient_class: str,
    target_title: str,
    target_company: str,
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index in range(_candidate_count(reasoning_policy)):
        message_text = _stub_message_text(
            salutation=salutation,
            recipient_class=recipient_class,
            target_title=target_title,
            target_company=target_company,
            variant_index=index,
        )
        candidate_id = _stub_candidate_id(
            template_signature=template_signature,
            index=index,
            message_text=message_text,
        )
        model_call_ref = f"mref:{template_signature}:candidate{index + 1}"
        provider_receipt = (
            f"prov:{settings.provider_profile}:{template_signature}:candidate{index + 1}"
        )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "subject_line": (
                    _sanitize_subject_line(
                        "",
                        target_company=target_company,
                        target_title=target_title,
                    )
                    if _subject_required(length_budget)
                    else ""
                ),
                "draft_text": message_text,
                "message_text": message_text,
                "claims_used": _candidate_claims(
                    fallback_claim_ids=[],
                    allowed_claim_ids=allowed_claim_ids,
                ),
                "model_id": settings.model,
                "provider_id": settings.target_provider,
                "generation_temperature": settings.temperature,
                "top_p": settings.top_p,
                "is_whole_message": True,
                "model_call_ref": model_call_ref,
                "provider_receipt": provider_receipt,
                "generation_receipt": f"model_call_ref:{model_call_ref}",
            }
        )
    return candidates


def _normalized_candidate_entries(
    raw: Any,
    *,
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
    fallback_claim_ids: Any,
    selected_message_text: str,
    allowed_claim_ids: tuple[str, ...],
    target_company: str,
    target_name: str = "",
    target_title: str = "",
    target_role_title: str = "",
    recipient_class: str = "",
    length_budget: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    candidates: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        message_text = str(
            item.get("draft_text") or item.get("message_text") or item.get("body") or ""
        ).strip()
        message_text = _sanitize_message_text(
            message_text,
            target_company=target_company,
            target_name=target_name,
            target_title=target_title,
            target_role_title=target_role_title,
            recipient_class=recipient_class,
            allowed_claim_ids=allowed_claim_ids,
            length_budget=length_budget,
        )
        subject_line = ""
        if _subject_required(length_budget):
            subject_line = _sanitize_subject_line(
                item.get("subject_line") or item.get("subject"),
                target_company=target_company,
                target_title=target_title,
                target_role_title=target_role_title,
            )
        candidate_id = str(item.get("candidate_id") or item.get("id") or "").strip()
        if not candidate_id:
            candidate_id = _stub_candidate_id(
                template_signature=template_signature,
                index=index,
                message_text=message_text or selected_message_text,
            )
        model_call_ref = str(item.get("model_call_ref") or "").strip()
        provider_receipt = str(item.get("provider_receipt") or "").strip()
        if not model_call_ref:
            model_call_ref = f"mref:{template_signature}:provider_candidate{index + 1}"
        if not provider_receipt:
            provider_receipt = (
                f"prov:{settings.provider_profile}:{template_signature}:"
                f"provider_candidate{index + 1}"
            )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "subject_line": subject_line,
                "draft_text": message_text,
                "message_text": message_text,
                "claims_used": _candidate_claims(
                    fallback_claim_ids=item.get("claims_used", fallback_claim_ids),
                    allowed_claim_ids=allowed_claim_ids,
                ),
                "model_id": str(item.get("model_id") or item.get("model") or settings.model),
                "provider_id": str(
                    item.get("provider_id") or item.get("provider") or settings.target_provider
                ),
                "generation_temperature": float(
                    item.get("temperature")
                    or item.get("generation_temperature")
                    or settings.temperature
                ),
                "top_p": float(item.get("top_p") or settings.top_p),
                "is_whole_message": bool(item.get("is_whole_message", True)),
                "model_call_ref": model_call_ref,
                "provider_receipt": provider_receipt,
                "generation_receipt": str(
                    item.get("generation_receipt") or f"model_call_ref:{model_call_ref}"
                ),
            }
        )
    return candidates


def _stub_draft(
    *,
    register: str,
    recipient_class: str,
    target_contact: dict[str, Any],
    template_signature: str,
    settings: ProviderSettings,
    reasoning_policy: dict[str, Any],
    allowed_claim_ids: tuple[str, ...],
    length_budget: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    target_name = str(target_contact.get("verified_name", "") or "").strip()
    target_title = str(target_contact.get("title", "") or "").strip()
    target_company = str(target_contact.get("company_name", "") or "the company").strip()
    salutation = f"Hi {target_name.split()[0]}," if target_name else "Hi,"
    candidates = _stub_candidates(
        salutation=salutation,
        recipient_class=recipient_class,
        target_title=target_title,
        target_company=target_company,
        template_signature=template_signature,
        settings=settings,
        reasoning_policy=reasoning_policy,
        allowed_claim_ids=allowed_claim_ids,
        length_budget=length_budget,
    )
    selected = candidates[0]
    message_text = str(selected["draft_text"])
    subject_line = str(selected.get("subject_line") or "")
    claims_used = list(selected["claims_used"])
    return {
        "message_text": message_text,
        "body": message_text,
        "channel": _channel_from_length_budget(length_budget),
        "subject_line": subject_line,
        "recipient_class": _recipient_class_value(recipient_class),
        "recipient_category": recipient_class,
        "target_contact_name": target_name,
        "target_contact_title": target_title,
        "target_contact_company": target_company,
        "intended_next_step": "quick chat or resume review",
        "claims_used": claims_used,
        "unsupported_claims": [],
        "omitted_claims": [],
        "qa_notes": ["deterministic_test_provider_stub"],
        "selected_candidate_id": str(selected["candidate_id"]),
        "candidates": candidates,
        "register": register,
        "template_signature": template_signature,
        "attempts": 1,
        "sc_level": reasoning_policy["sc_level"],
        "reasoning_intensity": reasoning_policy["reasoning_intensity"],
        "judge_profile": reasoning_policy["judge_profile"],
        "reasoning_policy": reasoning_policy,
        "max_candidates": reasoning_policy["max_candidates"],
        "candidate_count": len(candidates),
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
        "CEO",
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


def _company_key(target_company: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", " ", str(target_company or "").lower()).strip()
    if lowered in {"aig", "american international group"}:
        return "aig"
    if "citi" in lowered or "citigroup" in lowered:
        return "citi"
    if "neo4j" in lowered:
        return "neo4j"
    return "generic"


def _company_prompt_guidance(target_company: str) -> str:
    key = _company_key(target_company)
    if key == "aig":
        return (
            "Use AIG-specific operating evidence only when it is present in the prompt; "
            "underwriting, claims, AIG Assist, and insurance language are allowed only for AIG. "
        )
    if key == "citi":
        return (
            "Use Citi evidence around regulated finance, governance, risk controls, "
            "platform execution, or AI strategy; do not borrow AIG underwriting or claims texture. "
        )
    if key == "neo4j":
        return (
            "Use Neo4j evidence around graph data, product/platform work, and agentic AI; "
            "do not borrow AIG insurance, underwriting, or claims texture. "
        )
    return (
        "Use only company-specific evidence from the prompt; do not borrow AIG, "
        "insurance, underwriting, or claims texture unless independently sourced. "
    )


def _validation_contract_guidance(
    *,
    target_company: str,
    allowed_claim_ids: tuple[str, ...],
) -> str:
    proof_hint = ""
    if allowed_claim_ids:
        proof_hint = (
            "Use this concrete sender proof, not a generic experience claim: "
            "designed and operationalized a governed agentic AI platform for "
            "regulated enterprise workflows. "
        )
    key = _company_key(target_company)
    if key == "aig":
        return (
            proof_hint
            + "For AIG, anchor the note to the VP, Global Head of Agentic AI "
            "Solutions role or regulated insurance terms such as claims, "
            "underwriting, GenAI standards, or governance. "
        )
    if key == "citi":
        return (
            proof_hint
            + "For Citi, anchor the note to Head of AI Strategy, regulated "
            "finance, responsible AI, risk controls, data governance, or "
            "platform execution; do not use insurance, claims, or underwriting terms. "
        )
    if key == "neo4j":
        return (
            proof_hint
            + "For Neo4j, anchor the note to VP Product Management, Agentic AI, "
            "graph intelligence, knowledge graph context, or agentic AI product "
            "execution; do not use insurance, claims, or underwriting terms. "
        )
    return proof_hint


def _candidate_by_id(
    candidates: list[dict[str, Any]],
    selected_candidate_id: str,
) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("candidate_id") or "").strip() == selected_candidate_id:
            return candidate
    return None


def _prompt_recipient_class(prompt: str) -> str:
    match = re.search(r"\[recipient_class=([A-Za-z0-9_\- ]+)\]", prompt)
    if match:
        return match.group(1)
    match = re.search(r"^\s*C0-derived recipient class:\s*([A-Za-z0-9_\- ]+)\s*$", prompt, re.M)
    return match.group(1) if match else ""


def _prompt_target_contact(prompt: str) -> dict[str, Any]:
    match = re.search(r"^Target contact:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$", prompt, re.M)
    if match:
        return {
            "verified_name": match.group(1).strip(),
            "title": match.group(2).strip(),
            "company_name": match.group(3).strip(),
        }
    name = re.search(r"^\s*Name:\s*(.*?)\s*$", prompt, re.M)
    title = re.search(r"^\s*Title:\s*(.*?)\s*$", prompt, re.M)
    company = re.search(r"^\s*Company:\s*(.*?)\s*$", prompt, re.M)
    if not any((name, title, company)):
        return {}
    return {
        "verified_name": name.group(1).strip() if name else "",
        "title": title.group(1).strip() if title else "",
        "company_name": company.group(1).strip() if company else "",
    }


def _target_role_title_from_context(context: Mapping[str, Any]) -> str:
    persona = context.get("sender_persona") if isinstance(context.get("sender_persona"), Mapping) else {}
    sources: tuple[Any, ...] = (
        context.get("jd_fields"),
        context.get("c03_jd_fields"),
        context.get("governed_opportunity_jd_fields"),
        persona.get("jd_fields") if isinstance(persona, Mapping) else {},
        persona.get("target_contact") if isinstance(persona, Mapping) else {},
        context,
    )
    keys = (
        "position_name",
        "job_title",
        "target_role_title",
        "target_role",
        "role_title",
        "jd_position_name",
    )
    for source in sources:
        if not isinstance(source, Mapping):
            continue
        for key in keys:
            value = _clean_text(source.get(key))
            if value:
                return value
    return ""


def _target_role_title_from_prompt(prompt: str) -> str:
    patterns = (
        r'"position_name"\s*:\s*"([^"]+)"',
        r'"job_title"\s*:\s*"([^"]+)"',
        r'"jd_position_name"\s*:\s*"([^"]+)"',
        r"^\s*(?:Position|Role|Target role):\s*(.*?)\s*$",
    )
    for pattern in patterns:
        match = re.search(pattern, prompt, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            value = _clean_text(match.group(1))
            if value:
                return value
    return ""


def _allowed_claim_ids_from_context(
    context: dict[str, Any],
    prompt: str,
) -> tuple[str, ...]:
    for source in (
        context.get("sender_proof_envelope"),
        (context.get("sender_persona") or {}).get("sender_proof_envelope")
        if isinstance(context.get("sender_persona"), dict)
        else {},
    ):
        ids = _allowed_claim_ids(source)
        if ids:
            return ids
    raw_ids = context.get("c03_allowed_claim_ids")
    if isinstance(raw_ids, (list, tuple)):
        ids = tuple(dict.fromkeys(str(item).strip() for item in raw_ids if str(item).strip()))
        if ids:
            return ids
    match = re.search(r"^Sender proof allowed claim IDs:\s*(.*?)\s*$", prompt, re.M)
    if match:
        raw = match.group(1).strip()
        if raw and raw != "(none)":
            return tuple(
                dict.fromkeys(part.strip() for part in raw.split(",") if part.strip())
            )
    return ()


def _length_budget_from_context(context: Mapping[str, Any]) -> Mapping[str, Any]:
    raw = context.get("c03_length_budget")
    return raw if isinstance(raw, Mapping) else {}


def _allowed_claim_ids(envelope: Any) -> tuple[str, ...]:
    if not isinstance(envelope, dict):
        return ()
    raw = envelope.get("allowed_claim_ids") or ()
    if not isinstance(raw, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(str(item).strip() for item in raw if str(item).strip()))


def _stub_message_text(
    *,
    salutation: str,
    recipient_class: str,
    target_title: str,
    target_company: str,
    variant_index: int = 0,
) -> str:
    def _variant(options: tuple[str, str, str]) -> str:
        return options[min(max(variant_index, 0), len(options) - 1)]

    company_key = _company_key(target_company)
    if company_key == "aig":
        executive_signal = (
            f"{target_company}'s Agentic AI role reads less like model building "
            "and more like an operating-model rewrite across underwriting, claims, and GenAI standards"
        )
        senior_ta_signal = (
            f"the {target_company} brief is unusually execution-heavy for AI: "
            "claims, underwriting, GenAI standards, and change adoption"
        )
        hiring_signal = (
            f"the {target_title or 'team'} lane at {target_company} looks like "
            "applied agentic AI delivery under real governance pressure"
        )
        recruiter_signal = (
            f"this {target_company} Agentic AI search looks like the rare one "
            "where production AI, insurance workflows, and governance all matter"
        )
    elif company_key == "citi":
        executive_signal = (
            f"{target_company}'s AI agenda reads less like model demos and more "
            "like regulated finance platform execution"
        )
        senior_ta_signal = (
            f"the {target_company} brief is unusually execution-heavy for AI: "
            "risk controls, governance standards, platform reuse, and adoption"
        )
        hiring_signal = (
            f"the {target_title or 'team'} lane at {target_company} looks like "
            "AI platform delivery under regulated finance governance pressure"
        )
        recruiter_signal = (
            f"this {target_company} AI search looks like the rare one where "
            "production AI, regulated finance controls, and governance all matter"
        )
    elif company_key == "neo4j":
        executive_signal = (
            f"{target_company}'s graph data platform work reads less like model demos "
            "and more like product-led AI infrastructure"
        )
        senior_ta_signal = (
            f"the {target_company} brief is unusually product-heavy for AI: "
            "graph context, platform adoption, developer experience, and agentic workflows"
        )
        hiring_signal = (
            f"the {target_title or 'team'} lane at {target_company} looks like "
            "graph-native AI platform delivery under real product pressure"
        )
        recruiter_signal = (
            f"this {target_company} search looks like the rare one where graph data, "
            "production AI, and platform governance all matter"
        )
    else:
        executive_signal = (
            f"{target_company}'s AI work reads less like model demos and more like "
            "platform execution"
        )
        senior_ta_signal = (
            f"the {target_company} brief is unusually execution-heavy for AI: "
            "platform governance, adoption, and delivery discipline"
        )
        hiring_signal = (
            f"the {target_title or 'team'} lane at {target_company} looks like "
            "applied AI delivery under real governance pressure"
        )
        recruiter_signal = (
            f"this {target_company} AI search looks like the rare one where "
            "production AI and governance both matter"
        )

    if recipient_class in {"CEO", "EXECUTIVE", "C_LEVEL", "CTO"}:
        return (
            f"{salutation} {executive_signal}. I have built governed "
            "agent workflows with evals, telemetry, and human control baked in. "
            + _variant(
                (
                    "Worth a brief call on proof I could bring to the rollout?",
                    "Open to a short calibration call on where that proof would help?",
                    "Would a quick call help assess fit for the rollout?",
                )
            )
        )
    if recipient_class == "SENIOR_TA":
        return (
            f"{salutation} {senior_ta_signal}. "
            "My angle is senior engineering leadership that turns that into "
            "governed agent systems, not slideware. "
            + _variant(
                (
                    "Open to a resume review or quick chat on where this fits your search?",
                    "Would a resume review help you assess fit for the search?",
                    "Open to a quick screen on where this fits the role brief?",
                )
            )
        )
    if recipient_class in {"HIRING_MANAGER", "VP_ENG"}:
        return (
            f"{salutation} {hiring_signal}. "
            "I bring senior engineering work in orchestration, evals, and safe "
            "workflow automation. "
            + _variant(
                (
                    "Worth a brief call on the execution gap I could cover?",
                    "Open to a short discussion on the delivery gap I could cover?",
                    "Would a quick call help assess fit for the execution lane?",
                )
            )
        )
    return (
        f"{salutation} {recruiter_signal}. "
        "My background is senior agentic AI engineering with evals, orchestration, "
        "and safety built in. "
        + _variant(
            (
                "Open to a quick resume review for the VP search?",
                "Would a short screen help you assess fit for the VP search?",
                "Open to a quick conversation on where this fits your pipeline?",
            )
        )
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
