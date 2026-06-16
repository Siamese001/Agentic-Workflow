"""Provider-neutral section generation seam for apps_rg lanes.

Replaces the retired Qwen/vLLM slice (``section_qwen_slice``) and the Qwen request
builder (``qwen_vllm_provider.build_qwen_request``). Section lanes build an
OpenAI-compatible ``messages`` payload with :func:`build_section_request` and execute
it through the apps_rg ``ProviderGateway`` (external Claude by default) via
:func:`generate_section`. No local-model transport, preflight, or retry logic remains —
the external provider owns transport.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.providers.provider_contract import ProviderRequest, ProviderResult
from apps_rg.runtime.providers.provider_gateway import resolve_provider_profile
from apps_rg.runtime.providers.section_provider_call import call_section_model_provider
from apps_rg.runtime.section_model_limits import SECTION_MODEL_ID

DEFAULT_SECTION_TIMEOUT_SECONDS = 90

__all__ = [
    "DEFAULT_SECTION_TIMEOUT_SECONDS",
    "assert_temperature_in_profile",
    "build_section_request",
    "generate_section",
    "merge_transport_context",
    "tag_reasoning_lane",
]


def tag_reasoning_lane(payload: dict[str, Any], lane_key: str) -> dict[str, Any]:
    """Tag a provider payload with its section lane (consumed by reasoning-intent receipts)."""
    merged = dict(payload)
    merged["_reasoning_section_lane"] = str(lane_key)
    return merged


def merge_transport_context(**kwargs: Any) -> None:
    """Neutral no-op transport-context sink.

    The Qwen transport-diagnostics context store was removed with the local-model
    provider. Section lanes still call this to record run/artifact context; there is no
    longer a local-transport consumer, so it intentionally does nothing.
    """
    return None


def assert_temperature_in_profile(
    temperature: float,
    low: float = 0.0,
    high: float = 0.99,
) -> None:
    if not (low <= temperature <= high):
        raise ValueError(f"temperature {temperature} outside allowed bounds [{low}, {high}]")


def build_section_request(
    *,
    messages: list[dict[str, str]],
    prompt_hash: str,
    input_payload_hash: str,
    temperature: float = 0.45,
    max_tokens: int = 700,
    timeout_seconds: int = DEFAULT_SECTION_TIMEOUT_SECONDS,
    base_url: str = "",
    model: str = SECTION_MODEL_ID,
    temperature_bounds: tuple[float, float] = (0.0, 0.99),
) -> tuple[ProviderRequest, dict[str, Any]]:
    """Build an OpenAI-compatible section generation request for the apps_rg provider gateway.

    Neutral successor to ``build_qwen_request``: identical payload shape, but the provenance
    record and default model reference the apps_rg generation model (external Claude), not a
    local Qwen serve name.
    """
    t_low, t_high = temperature_bounds
    bounded = float(min(max(float(temperature), t_low), t_high))
    assert_temperature_in_profile(bounded, low=t_low, high=t_high)
    provider_request = ProviderRequest(
        provider_requested="external_claude",
        provider_attempted=True,
        provider_url=base_url,
        model=model,
        temperature=bounded,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        mock_fallback_allowed=False,
    )
    payload = {
        "model": model,
        "messages": messages,
        "temperature": bounded,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout_seconds,
        "response_format": {"type": "json_object"},
    }
    return provider_request, payload


def generate_section(
    payload: dict[str, Any],
    /,
    *,
    artifact_dir: Path | str | None = None,
    run_id: str | None = None,
    temperature_override: float | None = None,
) -> ProviderResult:
    """Execute a section generation payload through the apps_rg provider gateway.

    Neutral successor to ``section_qwen_slice.call_qwen_vllm``: resolves the configured
    apps_rg provider profile (external Claude by default) and dispatches via
    ``call_section_model_provider``. Internal ``_reasoning_section_lane`` tags are stripped
    before transport.
    """
    selection = resolve_provider_profile()
    # Capture the section lane BEFORE stripping internal ``_``-tags, then pass it through as an
    # explicit ``section_id`` so the per-section model pin still applies on this path (the tag
    # itself is stripped from the transport ``body``).
    section_lane = str(payload.get("_reasoning_section_lane") or "").strip() or None
    body = {k: v for k, v in dict(payload).items() if not str(k).startswith("_")}
    return call_section_model_provider(
        selection.profile,
        body,
        artifact_dir=Path(artifact_dir) if artifact_dir is not None else None,
        run_id=run_id,
        temperature_override=temperature_override,
        section_id=section_lane,
    )
