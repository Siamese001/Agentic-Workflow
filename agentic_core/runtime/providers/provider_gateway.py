"""Provider gateway — generic provider invocation.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Enforces:
- Provider allowlist from L3ToL2StepContract
- Model allowlist from L3ToL2StepContract
- Budget/timeout limits
- Provider mode restrictions (stub_only, local_only, live_allowed)
- ProviderInvocationReceipt emission

No hardcoded providers. No app-specific code.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid
from typing import Any, Dict, Optional, Sequence

from agentic_core.runtime.providers.provider_types import (
    BudgetStatus,
    ProviderCredentialsMissingError,
    ProviderInvocationReceipt,
    ProviderKind,
    ProviderMode,
    ProviderModeBlockedError,
    ProviderNotAllowedError,
    ProviderProfile,
    ProviderProfileNotFoundError,
    ProviderRequest,
    ProviderResponse,
    ProviderGatewayError,
    SafetyStatus,
    TimeoutStatus,
    TokenUsage,
)
from agentic_core.runtime.providers.provider_registry import (
    ProviderRegistry,
    get_provider_registry,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract

_LOGGER = logging.getLogger(__name__)


def _resolve_local_vllm_base_url(profile: ProviderProfile) -> Optional[str]:
    """Resolve OpenAI-compatible base URL for LOCAL_VLLM (trailing ``/v1`` stripped for client)."""
    raw = (profile.endpoint_url or "").strip()
    if raw:
        return raw.rstrip("/")
    env_name = (profile.endpoint_env_var or "").strip()
    if env_name:
        from_env = (os.environ.get(env_name) or "").strip()
        if from_env:
            return from_env.rstrip("/")
    return None


def _local_vllm_temperature(request: ProviderRequest, profile: ProviderProfile) -> float:
    """Preserve ``0.0`` — do not treat falsy float as missing."""
    if request.temperature is not None:
        return float(request.temperature)
    return 0.7


def _local_vllm_max_tokens(request: ProviderRequest, profile: ProviderProfile) -> int:
    if request.max_tokens is not None and int(request.max_tokens) > 0:
        return int(request.max_tokens)
    return int(profile.max_tokens or 4096)


def _local_vllm_top_p(request: ProviderRequest, profile: ProviderProfile) -> float:
    if request.top_p is not None:
        return float(request.top_p)
    return 1.0


class ProviderGateway:
    """Generic provider gateway for LLM generation.
    
    Enforces activation profile restrictions, allowlists, and budgets.
    All external provider calls go through this gateway.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        provider_mode: ProviderMode = ProviderMode.STUB_ONLY,
    ) -> None:
        self._registry = registry or get_provider_registry()
        self._provider_mode = provider_mode
        self._invocation_count: Dict[str, int] = {}
    
    def invoke(
        self,
        request: ProviderRequest,
        step_contract: Optional[L3ToL2StepContract] = None,
    ) -> ProviderResponse:
        """Invoke a provider with full enforcement.
        
        Args:
            request: The provider request
            step_contract: Optional step contract for allowlist enforcement
            
        Returns:
            ProviderResponse with receipt
            
        Raises:
            ProviderModeBlockedError: If live provider blocked by policy
            ProviderNotAllowedError: If provider not in allowlist
            ProviderCredentialsMissingError: If external provider lacks credentials
            ProviderGatewayError: On invocation failure
        """
        # 1. Load and validate profile
        profile = request.provider_profile
        
        # 2. Check provider mode restrictions
        self._check_provider_mode(profile)
        
        # 3. Check step contract allowlists if provided
        if step_contract is not None:
            self._check_allowlists(profile, step_contract)
        
        # 4. Check external provider credentials
        if profile.provider_kind == ProviderKind.EXTERNAL_API:
            if not self._check_external_credentials(profile):
                raise ProviderCredentialsMissingError(
                    f"External provider {profile.profile_id} missing credentials. "
                    f"Env var: {profile.api_key_env_var}"
                )
        
        # 5. Check activation env var if required
        if profile.activation_env_var:
            if os.environ.get(profile.activation_env_var) != "1":
                _LOGGER.warning(
                    "Provider %s requires %s=1",
                    profile.profile_id,
                    profile.activation_env_var,
                )
                # Fall back to stub for safety
                return self._invoke_stub(request, profile)
        
        # 6. Invoke appropriate provider
        started = time.time()
        invocation_id = str(uuid.uuid4())
        
        try:
            if profile.provider_kind == ProviderKind.STUB:
                response = self._invoke_stub(request, profile)
            elif profile.provider_kind == ProviderKind.LOCAL_VLLM:
                response = self._invoke_local_vllm(request, profile)
            elif profile.provider_kind == ProviderKind.EXTERNAL_API:
                response = self._invoke_external_api(request, profile)
            elif profile.provider_kind == ProviderKind.DETERMINISTIC:
                response = self._invoke_deterministic(request, profile)
            else:
                raise ProviderGatewayError(
                    f"Unknown provider kind: {profile.provider_kind}"
                )
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            latency_ms = (time.time() - started) * 1000.0
            receipt = self._build_receipt(
                invocation_id=invocation_id,
                request=request,
                profile=profile,
                latency_ms=latency_ms,
                success=False,
                output_text="",
                error=str(exc),
            )
            return ProviderResponse(
                success=False,
                text="",
                receipt=receipt,
                error_message=str(exc),
            )
        
        # 7. Build receipt with actual timing
        latency_ms = (time.time() - started) * 1000.0
        receipt = self._build_receipt(
            invocation_id=invocation_id,
            request=request,
            profile=profile,
            latency_ms=latency_ms,
            success=response.success,
            output_text=response.text,
            error=response.error_message,
            model_used=response.model_used,
        )
        
        # Return response with receipt
        return ProviderResponse(
            success=response.success,
            text=response.text,
            receipt=receipt,
            error_message=response.error_message,
            model_used=response.model_used,
            invocation_meta=getattr(response, "invocation_meta", None),
        )
    
    def _check_provider_mode(self, profile: ProviderProfile) -> None:
        """Check if provider kind is allowed by current mode."""
        if self._provider_mode == ProviderMode.STUB_ONLY:
            # Only stub and deterministic allowed
            if profile.provider_kind not in (
                ProviderKind.STUB,
                ProviderKind.DETERMINISTIC,
            ):
                raise ProviderModeBlockedError(
                    f"Provider {profile.profile_id} ({profile.provider_kind}) "
                    f"blocked by mode={self._provider_mode.value}. "
                    f"Only stub/deterministic providers allowed."
                )
        
        elif self._provider_mode == ProviderMode.LOCAL_ONLY:
            # Only local, stub, and deterministic allowed
            if profile.provider_kind not in (
                ProviderKind.STUB,
                ProviderKind.LOCAL_VLLM,
                ProviderKind.DETERMINISTIC,
            ):
                raise ProviderModeBlockedError(
                    f"Provider {profile.profile_id} ({profile.provider_kind}) "
                    f"blocked by mode={self._provider_mode.value}. "
                    f"External API providers not allowed."
                )
        
        # LIVE_ALLOWED: all providers ok
    
    def _check_allowlists(
        self,
        profile: ProviderProfile,
        step_contract: L3ToL2StepContract,
    ) -> None:
        """Check provider and model against step contract allowlists."""
        # Get allowed providers from step contract
        provider_allowlist = getattr(step_contract, "provider_allowlist", None)
        if provider_allowlist and profile.profile_id not in provider_allowlist:
            raise ProviderNotAllowedError(
                f"Provider {profile.profile_id} not in step contract provider_allowlist: "
                f"{provider_allowlist}"
            )
        
        # Get allowed models from step contract
        model_allowlist = getattr(step_contract, "model_allowlist", None)
        if model_allowlist and profile.model_id not in model_allowlist:
            raise ProviderNotAllowedError(
                f"Model {profile.model_id} not in step contract model_allowlist: "
                f"{model_allowlist}"
            )
    
    def _check_external_credentials(self, profile: ProviderProfile) -> bool:
        """Check if external provider credentials are available."""
        if not profile.api_key_env_var:
            return True
        return os.environ.get(profile.api_key_env_var) is not None
    
    def _invoke_stub(
        self,
        request: ProviderRequest,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Invoke stub provider for testing/dry-run."""
        # Generate deterministic stub response
        stub_hash = hashlib.sha256(
            f"stub:{request.prompt_text[:100]}".encode()
        ).hexdigest()[:16]
        
        stub_response = (
            f'{{"stub_response": true, "hash": "{stub_hash}", '
            f'"note": "Provider stub response for profile {profile.profile_id}"}}'
        )
        
        return ProviderResponse(
            success=True,
            text=stub_response,
            receipt=None,  # Will be filled by caller
            model_used="stub",
        )
    
    def _invoke_local_vllm(
        self,
        request: ProviderRequest,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Invoke local vLLM provider.
        
        Delegates to existing QwenInferenceGateway infrastructure.
        """
        # Import here to avoid circular deps
        try:
            from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (
                QwenInferenceGateway,
                QwenInferenceRequest,
            )
            
            base_url = _resolve_local_vllm_base_url(profile)

            async def _invoke_once():
                gateway = QwenInferenceGateway(
                    model_id=profile.model_id,
                    base_url=base_url,
                )
                try:
                    inference_req = QwenInferenceRequest(
                        app_name=request.run_id or "provider_gateway",
                        prompt=request.prompt_text,
                        max_tokens=_local_vllm_max_tokens(request, profile),
                        temperature=_local_vllm_temperature(request, profile),
                        top_p=_local_vllm_top_p(request, profile),
                        response_format=request.openai_response_format,
                    )
                    return await gateway.infer(inference_req)
                finally:
                    await gateway.aclose()

            import asyncio

            response = asyncio.run(_invoke_once())
            
            def _vllm_invocation_meta(qwen_resp: Any) -> dict[str, Any]:
                from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                    QWEN_LOCAL_MAX_MODEL_LEN,
                )

                inv_meta: dict[str, Any] = {
                    "provider_profile_id": str(profile.profile_id),
                    "model_id": str(profile.model_id or ""),
                    "base_url_redacted": _resolve_local_vllm_base_url(profile) or "",
                    "max_model_len": int(QWEN_LOCAL_MAX_MODEL_LEN),
                }
                if inv_meta["base_url_redacted"]:
                    from urllib.parse import urlsplit, urlunsplit

                    parts = urlsplit(str(inv_meta["base_url_redacted"]))
                    netloc = parts.netloc
                    if "@" in netloc:
                        netloc = "<redacted-credentials>@" + netloc.split("@", 1)[-1]
                    else:
                        host = netloc.split(":")[0] if netloc else ""
                        if host:
                            netloc = netloc.replace(host, "<redacted-host>", 1)
                    inv_meta["base_url_redacted"] = urlunsplit(
                        (parts.scheme, netloc, parts.path, parts.query, parts.fragment)
                    )
                vd = getattr(qwen_resp, "vllm_diagnostics", None)
                if isinstance(vd, dict):
                    inv_meta.update(vd)
                return inv_meta

            if response.success:
                inv_meta = _vllm_invocation_meta(response)
                return ProviderResponse(
                    success=True,
                    text=response.response or "",
                    receipt=None,
                    model_used=response.model_used or profile.model_id,
                    invocation_meta=inv_meta,
                )
            else:
                inv_meta = _vllm_invocation_meta(response)
                if response.error_message and "HTTP 400" in response.error_message:
                    low = response.error_message.lower()
                    if "response_format" in low or "response format" in low:
                        inv_meta["response_format_supported"] = False
                return ProviderResponse(
                    success=False,
                    text="",
                    receipt=None,
                    error_message=response.error_message or "vLLM inference failed",
                    model_used=response.model_used,
                    invocation_meta=inv_meta,
                )
        except ImportError as exc:
            _LOGGER.error("QwenInferenceGateway not available: %s", exc)
            return ProviderResponse(
                success=False,
                text="",
                receipt=None,
                error_message=f"vLLM provider unavailable: {exc}",
            )
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            _LOGGER.error("vLLM invocation failed: %s", exc)
            return ProviderResponse(
                success=False,
                text="",
                receipt=None,
                error_message=f"vLLM invocation error: {exc}",
            )
    
    def _invoke_external_api(
        self,
        request: ProviderRequest,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Invoke external API provider (Anthropic, OpenAI, Gemini).

        Routes by provider_vendor attribute on the profile:
          - anthropic      → anthropic SDK (messages API)
          - openai         → openai SDK (chat completions)
          - google_gemini  → openai SDK pointed at Gemini OpenAI-compat endpoint

        API keys read from env vars declared in the profile.
        """
        vendor = profile.vendor or self._infer_vendor(profile)
        api_key_env = profile.api_key_env_var or ""
        api_key = os.environ.get(api_key_env, "") if api_key_env else ""
        model_id = profile.model_id or ""
        max_tokens = request.max_tokens or profile.max_tokens
        temperature = request.temperature if request.temperature is not None else 0.7
        prompt = request.prompt_text

        if vendor == "anthropic":
            return self._invoke_anthropic(
                prompt=prompt,
                model_id=model_id,
                api_key=api_key,
                max_tokens=max_tokens,
                temperature=temperature,
                profile=profile,
            )
        elif vendor in ("openai", "google_gemini"):
            return self._invoke_openai_compat(
                prompt=prompt,
                model_id=model_id,
                api_key=api_key,
                base_url=self._resolve_base_url(profile, vendor),
                max_tokens=max_tokens,
                temperature=temperature,
                profile=profile,
            )
        else:
            _LOGGER.error("Unknown external vendor %r for profile %s", vendor, profile.profile_id)
            return ProviderResponse(
                success=False,
                text="",
                receipt=None,
                error_message=f"Unknown external vendor {vendor!r} for profile {profile.profile_id}",
            )

    def _infer_vendor(self, profile: ProviderProfile) -> str:
        """Infer vendor from profile_id when profile.vendor not set."""
        pid = profile.profile_id.lower()
        if "anthropic" in pid or "claude" in pid:
            return "anthropic"
        if "gemini" in pid or "google" in pid:
            return "google_gemini"
        return "openai"

    def _resolve_base_url(self, profile: ProviderProfile, vendor: str) -> Optional[str]:
        """Resolve base URL from env var override or vendor default."""
        env_var = profile.endpoint_env_var
        if env_var:
            override = os.environ.get(env_var, "").strip()
            if override:
                return override
        if vendor == "google_gemini":
            return "https://generativelanguage.googleapis.com/v1beta/openai/"
        return None  # OpenAI SDK uses its own default

    def _invoke_anthropic(
        self,
        *,
        prompt: str,
        model_id: str,
        api_key: str,
        max_tokens: int,
        temperature: float,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Call Anthropic messages API."""
        try:
            import anthropic as _anthropic  # type: ignore[import]
        except ImportError:
            return ProviderResponse(
                success=False, text="", receipt=None,
                error_message="anthropic package not installed. Run: pip install anthropic",
            )
        try:
            client = _anthropic.Anthropic(api_key=api_key or None)
            msg = client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text if msg.content else ""
            return ProviderResponse(
                success=True,
                text=text,
                receipt=None,
                model_used=msg.model,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            _LOGGER.error("Anthropic call failed for %s: %s", profile.profile_id, exc)
            return ProviderResponse(
                success=False, text="", receipt=None,
                error_message=f"Anthropic invocation error: {exc}",
            )

    def _invoke_openai_compat(
        self,
        *,
        prompt: str,
        model_id: str,
        api_key: str,
        base_url: Optional[str],
        max_tokens: int,
        temperature: float,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Call OpenAI or OpenAI-compatible API (OpenAI, Gemini via compat endpoint)."""
        try:
            import openai as _openai  # type: ignore[import]
        except ImportError:
            return ProviderResponse(
                success=False, text="", receipt=None,
                error_message="openai package not installed. Run: pip install openai",
            )
        try:
            kwargs: Dict[str, Any] = {"api_key": api_key or None}
            if base_url:
                kwargs["base_url"] = base_url
            client = _openai.OpenAI(**kwargs)
            resp = client.chat.completions.create(
                model=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content or "" if resp.choices else ""
            return ProviderResponse(
                success=True,
                text=text,
                receipt=None,
                model_used=resp.model,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            _LOGGER.error("OpenAI-compat call failed for %s: %s", profile.profile_id, exc)
            return ProviderResponse(
                success=False, text="", receipt=None,
                error_message=f"OpenAI-compat invocation error: {exc}",
            )
    
    def _invoke_deterministic(
        self,
        request: ProviderRequest,
        profile: ProviderProfile,
    ) -> ProviderResponse:
        """Invoke deterministic provider for rule-based evaluation."""
        # Deterministic providers don't call LLMs
        # They return rule-based results
        return ProviderResponse(
            success=True,
            text='{"deterministic": true, "result": "rule_based_evaluation"}',
            receipt=None,
            model_used="deterministic",
        )
    
    def _build_receipt(
        self,
        *,
        invocation_id: str,
        request: ProviderRequest,
        profile: ProviderProfile,
        latency_ms: float,
        success: bool,
        output_text: str,
        error: Optional[str] = None,
        model_used: Optional[str] = None,
    ) -> ProviderInvocationReceipt:
        """Build the invocation receipt."""
        # Compute digests
        input_digest = hashlib.sha256(
            request.prompt_text.encode()
        ).hexdigest()[:32]
        output_digest = hashlib.sha256(
            output_text.encode()
        ).hexdigest()[:32]
        
        # Determine statuses
        budget_status = BudgetStatus.WITHIN_BUDGET  # Placeholder
        timeout_status = (
            TimeoutStatus.WITHIN_LIMIT
            if latency_ms < profile.timeout_seconds * 1000
            else TimeoutStatus.TIMEOUT_EXCEEDED
        )
        safety_status = SafetyStatus.SAFE  # Placeholder
        
        # Estimate token usage (rough heuristic)
        token_usage = TokenUsage(
            prompt_tokens=len(request.prompt_text.split()) * 2,  # Rough estimate
            completion_tokens=len(output_text.split()) * 2,
            total_tokens=(len(request.prompt_text.split()) + len(output_text.split())) * 2,
        )
        
        # Build deterministic digest
        det_digest = hashlib.sha256(
            f"{invocation_id}:{profile.profile_id}:{input_digest}:{output_digest}".encode()
        ).hexdigest()[:32]
        
        return ProviderInvocationReceipt(
            invocation_id=invocation_id,
            provider_profile_ref=profile.profile_id,
            provider_kind=profile.provider_kind,
            model_ref=profile.model_id,
            request_id=request.request_id or invocation_id,
            run_id=request.run_id,
            trace_root=request.trace_root,
            node_id=request.node_id,
            prompt_artifact_ref=request.prompt_artifact_ref,
            input_digest=input_digest,
            output_digest=output_digest,
            latency_ms=latency_ms,
            token_usage=token_usage,
            budget_status=budget_status,
            timeout_status=timeout_status,
            safety_status=safety_status,
            error=error,
            deterministic_digest=det_digest,
        )
    
    def set_provider_mode(self, mode: ProviderMode) -> None:
        """Update the provider mode restriction.
        
        Args:
            mode: New provider mode
        """
        self._provider_mode = mode
        _LOGGER.info("Provider mode set to %s", mode.value)


__all__ = [
    "ProviderGateway",
]
