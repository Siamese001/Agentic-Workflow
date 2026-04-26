"""PA.6 Provider-Aware Rendering — five lanes (spec lines 1276-1402).

Each lane converts the canonical slot composition + R0 + tool binding into
a deterministic provider-shaped wire payload. Renderers do not dispatch;
they only construct the dict the L2 dispatcher will hand to the SDK.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .pa1_bom_resolver import PromptBOMResolved
from .pa2_slot_composition import CompositionResult


PROVIDER_LANES: tuple[str, ...] = (
    "anthropic",
    "openai_chat",
    "openai_reasoning",
    "gemini",
    "local",
)

LOCAL_SYS_OPEN = "[SYSTEM]"
LOCAL_SYS_CLOSE = "[/SYSTEM]"
LOCAL_USER_OPEN = "[USER]"
LOCAL_USER_CLOSE = "[/USER]"
LOCAL_ASSISTANT_OPEN = "[ASSISTANT]"


@dataclass(frozen=True)
class RenderedPayload:
    provider_lane: str
    model_id: str
    payload: Mapping[str, Any]
    schema_bound: bool
    tools_bound: bool


def _system_text(comp: CompositionResult) -> str:
    parts: list[str] = []
    for slot in ("S0", "D0", "I0", "M0", "Y0"):
        entry = comp.stack.slot(slot)
        if entry and entry.content:
            parts.append("[" + slot + "]\n" + entry.content)
    return "\n\n".join(parts)


def _user_text(comp: CompositionResult) -> str:
    parts: list[str] = []
    for slot in ("E0", "C0", "U0", "H0"):
        entry = comp.stack.slot(slot)
        if entry and entry.content:
            label = "[USER_TASK]" if slot == "U0" else "[" + slot + "]"
            parts.append(label + "\n" + entry.content)
    if parts:
        return "\n\n".join(parts)
    u0 = comp.stack.slot("U0")
    return u0.content if u0 else ""


def _tools_payload(bom: PromptBOMResolved) -> list[dict[str, Any]]:
    return [dict(t) for t in bom.tool_binding_manifest.tools]


def render_anthropic(bom: PromptBOMResolved, comp: CompositionResult) -> RenderedPayload:
    payload: dict[str, Any] = {
        "model": bom.execution_metadata.model_id,
        "system": _system_text(comp),
        "messages": [{"role": "user", "content": _user_text(comp)}],
        "max_tokens": bom.execution_metadata.budget_ceiling or 4096,
    }
    if bom.execution_metadata.temperature is not None:
        payload["temperature"] = bom.execution_metadata.temperature
    if bom.tool_binding_manifest.tools:
        payload["tools"] = _tools_payload(bom)
    if bom.r0.valid and bom.r0.schema:
        payload["response_format"] = {"type": "json_schema", "json_schema": bom.r0.schema}
    return RenderedPayload(
        provider_lane="anthropic",
        model_id=bom.execution_metadata.model_id,
        payload=payload,
        schema_bound=bom.r0.valid,
        tools_bound=bool(bom.tool_binding_manifest.tools),
    )


def render_openai_chat(bom: PromptBOMResolved, comp: CompositionResult) -> RenderedPayload:
    messages: list[dict[str, str]] = []
    sys_text = _system_text(comp)
    if sys_text:
        messages.append({"role": "system", "content": sys_text})
    messages.append({"role": "user", "content": _user_text(comp)})
    payload: dict[str, Any] = {
        "model": bom.execution_metadata.model_id,
        "messages": messages,
    }
    if bom.execution_metadata.temperature is not None:
        payload["temperature"] = bom.execution_metadata.temperature
    if bom.tool_binding_manifest.tools:
        payload["tools"] = [{"type": "function", "function": t} for t in _tools_payload(bom)]
    if bom.r0.valid and bom.r0.schema:
        payload["response_format"] = {"type": "json_schema", "json_schema": bom.r0.schema}
    return RenderedPayload(
        provider_lane="openai_chat",
        model_id=bom.execution_metadata.model_id,
        payload=payload,
        schema_bound=bom.r0.valid,
        tools_bound=bool(bom.tool_binding_manifest.tools),
    )


def render_openai_reasoning(bom: PromptBOMResolved, comp: CompositionResult) -> RenderedPayload:
    base = render_openai_chat(bom, comp)
    payload = dict(base.payload)
    if bom.execution_metadata.thinking_level:
        payload["reasoning_effort"] = bom.execution_metadata.thinking_level
    payload.pop("temperature", None)
    return RenderedPayload(
        provider_lane="openai_reasoning",
        model_id=base.model_id,
        payload=payload,
        schema_bound=base.schema_bound,
        tools_bound=base.tools_bound,
    )


def render_gemini(bom: PromptBOMResolved, comp: CompositionResult) -> RenderedPayload:
    payload: dict[str, Any] = {
        "model": bom.execution_metadata.model_id,
        "system_instruction": {"parts": [{"text": _system_text(comp)}]},
        "contents": [{"role": "user", "parts": [{"text": _user_text(comp)}]}],
    }
    cfg: dict[str, Any] = {}
    if bom.execution_metadata.temperature is not None:
        cfg["temperature"] = bom.execution_metadata.temperature
    if bom.execution_metadata.budget_ceiling:
        cfg["max_output_tokens"] = bom.execution_metadata.budget_ceiling
    if bom.r0.valid and bom.r0.schema:
        cfg["response_schema"] = bom.r0.schema
        cfg["response_mime_type"] = "application/json"
    if cfg:
        payload["generation_config"] = cfg
    if bom.tool_binding_manifest.tools:
        payload["tools"] = [{"function_declarations": _tools_payload(bom)}]
    return RenderedPayload(
        provider_lane="gemini",
        model_id=bom.execution_metadata.model_id,
        payload=payload,
        schema_bound=bom.r0.valid,
        tools_bound=bool(bom.tool_binding_manifest.tools),
    )


def render_local(bom: PromptBOMResolved, comp: CompositionResult) -> RenderedPayload:
    sys_block = _system_text(comp)
    user_block = _user_text(comp)
    flat = "\n".join(
        [
            LOCAL_SYS_OPEN,
            sys_block,
            LOCAL_SYS_CLOSE,
            LOCAL_USER_OPEN,
            user_block,
            LOCAL_USER_CLOSE,
            LOCAL_ASSISTANT_OPEN,
        ]
    )
    payload: dict[str, Any] = {
        "model": bom.execution_metadata.model_id,
        "prompt": flat,
        "max_tokens": bom.execution_metadata.budget_ceiling or 2048,
    }
    if bom.execution_metadata.temperature is not None:
        payload["temperature"] = bom.execution_metadata.temperature
    if bom.r0.valid and bom.r0.schema:
        payload["response_format"] = {"type": "json_schema", "json_schema": bom.r0.schema}
    return RenderedPayload(
        provider_lane="local",
        model_id=bom.execution_metadata.model_id,
        payload=payload,
        schema_bound=bom.r0.valid,
        tools_bound=False,
    )


_RENDERERS = {
    "anthropic": render_anthropic,
    "openai_chat": render_openai_chat,
    "openai_reasoning": render_openai_reasoning,
    "gemini": render_gemini,
    "local": render_local,
}


def render_for_provider(
    bom: PromptBOMResolved,
    comp: CompositionResult,
    provider_lane: str,
) -> RenderedPayload:
    """Dispatch to the correct lane renderer."""
    lane = (provider_lane or "").lower()
    if lane not in _RENDERERS:
        raise ValueError(
            "unknown provider_lane: " + repr(provider_lane) + "; expected one of " + repr(PROVIDER_LANES)
        )
    return _RENDERERS[lane](bom, comp)


__all__ = [
    "PROVIDER_LANES",
    "RenderedPayload",
    "render_anthropic",
    "render_for_provider",
    "render_gemini",
    "render_local",
    "render_openai_chat",
    "render_openai_reasoning",
]
