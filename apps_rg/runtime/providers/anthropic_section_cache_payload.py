"""PA-slot-aware native Anthropic prompt-cache payload rendering."""
from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping, Sequence


MAX_ANTHROPIC_CACHE_MARKERS = 4
ANTHROPIC_SYSTEM_ONLY_USER_PROMPT = "Return the requested JSON object now."


class AnthropicCacheWorkloadKind(str, Enum):
    ONE_SHOT = "ONE_SHOT"
    REPAIR = "REPAIR"
    SELF_CONSISTENCY = "SELF_CONSISTENCY"
    SELECTOR = "SELECTOR"
    SUITE_REPLAY = "SUITE_REPLAY"


REPEATED_C0_WORKLOADS = frozenset(
    {
        AnthropicCacheWorkloadKind.REPAIR.value,
        AnthropicCacheWorkloadKind.SELF_CONSISTENCY.value,
        AnthropicCacheWorkloadKind.SELECTOR.value,
        AnthropicCacheWorkloadKind.SUITE_REPLAY.value,
    }
)
TIER1_SLOTS = frozenset({"S0", "D0", "I0"})
TIER3_SLOTS = frozenset({"E0", "Y0"})
NEVER_CACHE_SLOTS = frozenset({"U0", "H0", "M0"})


@dataclass(frozen=True)
class AnthropicSectionCachePayload:
    anthropic_payload: dict[str, Any]
    cache_strategy: str
    stable_prefix_hash: str
    c0_prefix_hash: str
    volatile_tail_hash: str
    cache_boundary_hints: list[dict[str, Any]]
    cache_marker_count: int
    cache_receipt_seed: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_text(parts: Sequence[str]) -> str:
    text = "\n\n".join(str(p) for p in parts if str(p))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""


def _normal_workload(value: str | AnthropicCacheWorkloadKind | None) -> str:
    raw = str(value.value if isinstance(value, AnthropicCacheWorkloadKind) else value or "").strip().upper()
    if raw in {k.value for k in AnthropicCacheWorkloadKind}:
        return raw
    return AnthropicCacheWorkloadKind.ONE_SHOT.value


def _slot_payloads(compiled_prompt_artifact: Any) -> list[Any]:
    payloads = list(getattr(compiled_prompt_artifact, "slot_payloads", None) or [])
    return [p for p in payloads if str(getattr(p, "slot_id", "") or "").strip()]


def _message_role(item: Any) -> str:
    if isinstance(item, Mapping):
        role = str(item.get("role") or "user").strip().lower()
        return role if role in {"system", "user", "assistant"} else "user"
    return "user"


def _message_text(item: Any) -> str:
    if not isinstance(item, Mapping):
        return str(item or "")
    content = item.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, Mapping):
                parts.append(str(block.get("text") or block.get("content") or ""))
            else:
                parts.append(str(block or ""))
        return "\n".join(p for p in parts if p)
    return str(content or "")


def _text_block(text: str, *, cache: bool, slot_id: str | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {"type": "text", "text": text}
    if slot_id:
        block["slot_id"] = slot_id
    if cache:
        block["cache_control"] = {"type": "ephemeral"}
    return block


def _non_system_messages(messages: Sequence[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in list(messages or []):
        role = _message_role(item)
        if role == "system":
            continue
        text = _message_text(item)
        if text:
            out.append({"role": role, "content": [{"type": "text", "text": text}]})
    return out


def _system_text_from_messages(messages: Sequence[Mapping[str, Any]] | None) -> str:
    return "\n\n".join(
        _message_text(item)
        for item in list(messages or [])
        if _message_role(item) == "system" and _message_text(item)
    ).strip()


def build_anthropic_section_cache_payload(
    *,
    section_id: str,
    model: str,
    compiled_prompt_artifact: Any | None = None,
    messages: Sequence[Mapping[str, Any]] | None = None,
    workload_kind: str | AnthropicCacheWorkloadKind | None = None,
    run_id: str | None = None,
    prompt_hash: str | None = None,
    input_payload_hash: str | None = None,
) -> AnthropicSectionCachePayload:
    workload = _normal_workload(workload_kind)
    payloads = _slot_payloads(compiled_prompt_artifact)
    marker_count = 0
    hints: list[dict[str, Any]] = []
    stable_parts: list[str] = []
    c0_parts: list[str] = []
    volatile_parts: list[str] = []
    system_blocks: list[dict[str, Any]] = []

    if payloads:
        for slot_payload in payloads:
            slot_id = str(getattr(slot_payload, "slot_id", "") or "").strip()
            content = str(getattr(slot_payload, "content", "") or "")
            if not content:
                continue
            cache_allowed = False
            tier = "volatile"
            reason = "not_cacheable"
            if slot_id in TIER1_SLOTS:
                cache_allowed = True
                tier = "tier1_stable"
                reason = "stable_instruction_prefix"
                stable_parts.append(content)
            elif slot_id == "C0":
                cache_allowed = workload in REPEATED_C0_WORKLOADS
                tier = "tier2_c0"
                reason = "repeated_c0_prefix" if cache_allowed else "one_shot_c0_skipped"
                c0_parts.append(content)
            elif slot_id in TIER3_SLOTS:
                cache_allowed = True
                tier = "tier3_style_or_examples"
                reason = "stable_before_volatile_tail"
            elif slot_id == "R0":
                cache_allowed = False
                tier = "schema_unmarked"
                reason = "r0_not_provider_native_schema"
                volatile_parts.append(content)
            elif slot_id in NEVER_CACHE_SLOTS:
                volatile_parts.append(content)
            else:
                volatile_parts.append(content)

            marked = bool(cache_allowed and marker_count < MAX_ANTHROPIC_CACHE_MARKERS)
            if marked:
                marker_count += 1
            system_blocks.append(_text_block(f"<!-- SLOT: {slot_id} -->\n{content}", cache=marked, slot_id=slot_id))
            hints.append(
                {
                    "slot_id": slot_id,
                    "tier": tier,
                    "marked": marked,
                    "reason": reason if marked or cache_allowed else reason,
                }
            )
    else:
        system_text = _system_text_from_messages(messages)
        if system_text:
            marker_count = 1
            stable_parts.append(system_text)
            system_blocks.append(_text_block(system_text, cache=True, slot_id="fallback_system"))
            hints.append(
                {
                    "slot_id": "fallback_system",
                    "tier": "fallback_stable",
                    "marked": True,
                    "reason": "fallback_system_message",
                }
            )

    volatile_messages = _non_system_messages(messages)
    for msg in volatile_messages:
        for block in msg.get("content") or []:
            if isinstance(block, Mapping):
                volatile_parts.append(str(block.get("text") or ""))
    if not volatile_messages:
        volatile_messages = [{"role": "user", "content": ANTHROPIC_SYSTEM_ONLY_USER_PROMPT}]

    anthropic_payload = {
        "system": system_blocks or "Return compact JSON only.",
        "messages": volatile_messages,
    }
    stable_hash = _hash_text(stable_parts)
    c0_hash = _hash_text(c0_parts)
    volatile_hash = _hash_text(volatile_parts)
    cache_group_hash = _hash_text([str(section_id or ""), stable_hash, c0_hash])
    seed = {
        "provider": "external_claude",
        "model": str(model or ""),
        "section_id": str(section_id or ""),
        "cache_enabled": True,
        "cache_strategy": "pa_slot_tiered_v1" if payloads else "fallback_system_v1",
        "workload_kind": workload,
        "stable_prefix_hash": stable_hash,
        "c0_prefix_hash": c0_hash,
        "volatile_tail_hash": volatile_hash,
        "cache_group_hash": cache_group_hash,
        "sc_group_hash": cache_group_hash if workload == AnthropicCacheWorkloadKind.SELF_CONSISTENCY.value else "",
        "cache_marker_count": marker_count,
        "input_tokens": None,
        "output_tokens": None,
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "cache_hit_ratio": None,
        "estimated_uncached_input_tokens": None,
        "estimated_cached_input_tokens": None,
        "cache_savings_estimate_source": "pending_anthropic_usage",
        "run_id": str(run_id or ""),
        "prompt_hash": str(prompt_hash or ""),
        "input_payload_hash": str(input_payload_hash or ""),
    }
    return AnthropicSectionCachePayload(
        anthropic_payload=copy.deepcopy(anthropic_payload),
        cache_strategy=str(seed["cache_strategy"]),
        stable_prefix_hash=str(seed["stable_prefix_hash"]),
        c0_prefix_hash=str(seed["c0_prefix_hash"]),
        volatile_tail_hash=str(seed["volatile_tail_hash"]),
        cache_boundary_hints=hints,
        cache_marker_count=marker_count,
        cache_receipt_seed=dict(seed),
    )


__all__ = [
    "ANTHROPIC_SYSTEM_ONLY_USER_PROMPT",
    "AnthropicCacheWorkloadKind",
    "AnthropicSectionCachePayload",
    "MAX_ANTHROPIC_CACHE_MARKERS",
    "build_anthropic_section_cache_payload",
]
