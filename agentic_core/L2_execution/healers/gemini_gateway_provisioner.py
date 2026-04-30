"""Gemini gateway provisioner — closes G6 from
``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md``.

The W1 ``HealingRouter._dispatch_gemini`` requires a pre-provisioned
``gateway`` object exposing an awaitable ``route_generation(request)``
that returns an object with a ``.content`` attribute. Without one, all
LOW-tier dispatches return ``{"dry_plan": True, "error":
"gemini_gateway_not_provisioned"}`` — which is correct for tests but
prevents real cascade fallback in production.

This module provides:

  - ``GeminiGatewayConfig`` — env-driven config (api_key, model overrides,
    timeout, max retries).
  - ``MinimalGeminiGateway`` — a thin async gateway that uses the
    ``google.generativeai`` SDK when available and falls back to a clear
    error envelope when not.
  - ``provision_router(router)`` — module-level helper that attaches a
    provisioned gateway to a ``HealingRouter`` instance when
    ``GEMINI_API_KEY`` is set.

Adoption is opt-in. Apps and tests that don't call ``provision_router``
keep the existing dry-plan behavior. Production deployments call
``provision_router`` once at startup (typically in their composition
root) so cascade fallback can actually round-trip to Gemini.

Layer purity: lives at L2 alongside ``HealingRouter``. Reads model IDs
from L0 ``model_registry`` SSOT; never touches L4 / L5.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.model_registry import (
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
)

_LOGGER = logging.getLogger(__name__)

# Env vars consumed at provision time. Names match existing apps_*/config
# conventions where they exist.
ENV_GEMINI_API_KEY: str = "GEMINI_API_KEY"
ENV_GEMINI_FLASH_OVERRIDE: str = "GEMINI_FLASH_MODEL"
ENV_GEMINI_PRO_OVERRIDE: str = "GEMINI_PRO_MODEL"
ENV_GEMINI_TIMEOUT: str = "GEMINI_TIMEOUT_SECONDS"
ENV_GEMINI_MAX_TOKENS: str = "GEMINI_MAX_OUTPUT_TOKENS"


@dataclass(frozen=True)
class GeminiGatewayConfig:
    """Resolved provisioning config for the Gemini cascade target.

    Constructed from env vars by :func:`from_env`. Immutable so it can
    be safely cached on the ``HealingRouter`` for the process lifetime.
    """

    api_key: str
    flash_model: str
    pro_model: str
    timeout_seconds: int
    max_output_tokens: int

    @staticmethod
    def from_env() -> GeminiGatewayConfig | None:
        """Return a config when ``GEMINI_API_KEY`` is set, else ``None``.

        Returning ``None`` is a positive signal: it tells the caller that
        no provisioning should happen, and the router should stay in
        dry-plan mode (e.g. CI where no real Gemini key is available).
        """
        key = (os.getenv(ENV_GEMINI_API_KEY) or "").strip()
        if not key:
            return None
        try:
            timeout = int(os.getenv(ENV_GEMINI_TIMEOUT, "60"))
        except ValueError:
            timeout = 60
        try:
            max_tokens = int(os.getenv(ENV_GEMINI_MAX_TOKENS, "4096"))
        except ValueError:
            max_tokens = 4096
        return GeminiGatewayConfig(
            api_key=key,
            flash_model=os.getenv(ENV_GEMINI_FLASH_OVERRIDE, GEMINI_FLASH_MODEL_ID),
            pro_model=os.getenv(ENV_GEMINI_PRO_OVERRIDE, GEMINI_PRO_MODEL_ID),
            timeout_seconds=timeout,
            max_output_tokens=max_tokens,
        )


@dataclass
class _GeminiResponse:
    """Minimal response envelope matching the contract of
    ``HealingRouter._dispatch_gemini``: an object with ``.content`` and
    ``.model``.
    """

    content: str | None
    model: str
    error: str | None = None


class MinimalGeminiGateway:
    """Thin async wrapper around ``google.generativeai``.

    Implements the single method ``HealingRouter._dispatch_gemini``
    actually invokes (``route_generation``) with the minimum surface area
    needed for cascade fallback. NOT a substitute for
    :class:`SovereignLLMGateway` — that gateway carries signature
    verification, telemetry, and circuit-breaker logic. This class is
    intentionally simple so it can be provisioned in apps that don't yet
    consume the full Sovereign machinery.
    """

    def __init__(self, config: GeminiGatewayConfig) -> None:
        self._config = config
        self._sdk: Any | None = None  # lazy-initialised on first call

    @property
    def config(self) -> GeminiGatewayConfig:
        return self._config

    def _load_sdk(self) -> Any | None:
        if self._sdk is not None:
            return self._sdk
        try:
            import google.generativeai as genai  # noqa: PLC0415
        except ImportError:
            _LOGGER.warning(
                "google.generativeai not installed — MinimalGeminiGateway will "
                "return error envelopes. Install with: pip install google-generativeai"
            )
            return None
        try:
            genai.configure(api_key=self._config.api_key)
        except (RuntimeError, ValueError) as exc:
            _LOGGER.warning("genai.configure failed: %s", exc)
            return None
        self._sdk = genai
        return genai

    async def route_generation(self, request: Any) -> _GeminiResponse:
        """Async dispatch matching ``HealingRouter._dispatch_gemini`` contract.

        ``request`` is a ``GenerationRequest`` with attributes ``prompt``,
        ``model``, and ``max_tokens``. Returns a ``_GeminiResponse``
        whose ``.content`` is the generated text on success.
        """
        prompt = getattr(request, "prompt", "")
        model_id = getattr(request, "model", self._config.flash_model)
        max_tokens = getattr(request, "max_tokens", self._config.max_output_tokens)

        sdk = self._load_sdk()
        if sdk is None:
            return _GeminiResponse(
                content=None,
                model=model_id,
                error="gemini_sdk_unavailable",
            )

        try:
            model = sdk.GenerativeModel(model_id)
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": 0.0,
            }
            # Newer SDKs expose generate_content_async; older expose
            # generate_content (sync). Prefer async; fall back to sync via
            # asyncio.to_thread when only sync is available.
            generate_async = getattr(model, "generate_content_async", None)
            if generate_async is not None:
                response = await generate_async(prompt, generation_config=generation_config)
            else:
                import asyncio  # noqa: PLC0415

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config=generation_config,
                )
            content = getattr(response, "text", None)
            return _GeminiResponse(
                content=content,
                model=model_id,
                error=None if content else "gemini_empty_response",
            )
        except (RuntimeError, ValueError, OSError, AttributeError) as exc:
            return _GeminiResponse(
                content=None,
                model=model_id,
                error=f"gemini_call_error:{type(exc).__name__}:{exc}",
            )


def provision_router(router: Any, config: GeminiGatewayConfig | None = None) -> bool:
    """Attach a ``MinimalGeminiGateway`` to a ``HealingRouter`` instance.

    Args:
        router: A ``HealingRouter`` (or any object whose
            ``_gemini_gateway`` attribute the dispatch path checks).
        config: Optional explicit config; defaults to
            :meth:`GeminiGatewayConfig.from_env`.

    Returns:
        ``True`` when a gateway was attached (env had key + provisioning
        succeeded); ``False`` when no key was found and the router was
        left in dry-plan mode. Never raises — provisioning is best-effort
        so a missing API key cannot crash app startup.
    """
    cfg = config if config is not None else GeminiGatewayConfig.from_env()
    if cfg is None:
        _LOGGER.info(  # pii: allow-env-var-name -- ENV_GEMINI_API_KEY is the env var NAME constant, not the API key value
            "Gemini API key not set; HealingRouter cascade fallback stays in "
            "dry-plan mode (set %s to enable real Gemini round-trip).",
            ENV_GEMINI_API_KEY,
        )
        return False
    router._gemini_gateway = MinimalGeminiGateway(cfg)  # noqa: SLF001 -- intentional facade attach
    _LOGGER.info(
        "HealingRouter provisioned with Gemini cascade target (flash=%s, pro=%s)",
        cfg.flash_model,
        cfg.pro_model,
    )
    return True


__all__ = [
    "ENV_GEMINI_API_KEY",
    "ENV_GEMINI_FLASH_OVERRIDE",
    "ENV_GEMINI_MAX_TOKENS",
    "ENV_GEMINI_PRO_OVERRIDE",
    "ENV_GEMINI_TIMEOUT",
    "GeminiGatewayConfig",
    "MinimalGeminiGateway",
    "provision_router",
]
