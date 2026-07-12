"""Render cache-safe native Anthropic payloads for apps_rg section prompts.

Anthropic cache markers are prefix breakpoints.  This module therefore marks
stability-tier boundaries, preserves the exact compiled system prompt, and
keeps repair/path-specific content outside the cached prefix.
"""
from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CACHE_TTL_1H,
    CACHE_TTL_5M,
    min_cacheable_chars,
)

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
FALLBACK_REPEATED_USER_WORKLOADS = frozenset(
    {
        AnthropicCacheWorkloadKind.SELF_CONSISTENCY.value,
        AnthropicCacheWorkloadKind.SUITE_REPLAY.value,
    }
)
TIER1_SLOTS = frozenset({"S0", "D0", "I0"})
TIER2_SLOTS = frozenset({"C0", "E0", "Y0"})
VOLATILE_SLOTS = frozenset({"U0", "R0", "H0", "M0"})


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


def _hash(parts: Sequence[str]) -> str:
    text = "\n\n".join(str(part) for part in parts if str(part))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""


def _workload(value: str | AnthropicCacheWorkloadKind | None) -> str:
    raw = str(value.value if isinstance(value, AnthropicCacheWorkloadKind) else value or "").strip().upper()
    allowed = {item.value for item in AnthropicCacheWorkloadKind}
    return raw if raw in allowed else AnthropicCacheWorkloadKind.ONE_SHOT.value


def _role(message: Mapping[str, Any]) -> str:
    role = str(message.get("role") or "user").strip().lower()
    return role if role in {"system", "user", "assistant"} else "user"


def _text(value: Any) -> str:
    if not isinstance(value, Mapping):
        return str(value or "")
    content = value.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(block.get("text") or block.get("content") or "")
            if isinstance(block, Mapping)
            else str(block or "")
            for block in content
        ).strip()
    return str(content or "")


def _messages(
    artifact: Any | None,
    supplied: Sequence[Mapping[str, Any]] | None,
) -> list[Mapping[str, Any]]:
    if supplied is not None:
        return [item for item in supplied if isinstance(item, Mapping)]
    raw = getattr(artifact, "messages", None)
    return [item for item in raw if isinstance(item, Mapping)] if isinstance(raw, list) else []


def _system_text(messages: Sequence[Mapping[str, Any]]) -> str:
    return "\n\n".join(_text(message) for message in messages if _role(message) == "system" and _text(message)).rstrip()


def _native_content(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}] if content else []
    if isinstance(content, list):
        out: list[dict[str, Any]] = []
        for item in content:
            if isinstance(item, Mapping):
                block = dict(item)
                block.pop("cache_control", None)
                out.append(block)
            elif str(item or ""):
                out.append({"type": "text", "text": str(item)})
        return out
    return [{"type": "text", "text": str(content)}] if content else []


def _non_system_messages(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for message in messages:
        if _role(message) == "system":
            continue
        content = _native_content(message.get("content"))
        if content:
            out.append({"role": _role(message), "content": content})
    return out


def _slot_payloads(artifact: Any | None) -> list[Any]:
    raw = getattr(artifact, "slot_payloads", None) or []
    return [item for item in raw if str(getattr(item, "slot_id", "") or "").strip()]


def _slot_text(slot_id: str, content: str) -> str:
    return f"<!-- SLOT: {slot_id} -->\n{content}"


def _compiled_slot_text(slots: Sequence[Any]) -> str:
    return "\n\n".join(
        _slot_text(str(getattr(slot, "slot_id", "") or "").strip(), str(getattr(slot, "content", "") or ""))
        for slot in slots
        if str(getattr(slot, "content", "") or "")
    ).rstrip()


def _cache_control(ttl: str) -> dict[str, str]:
    return {"type": "ephemeral", "ttl": "1h"} if ttl == CACHE_TTL_1H else {"type": "ephemeral"}


def _prefix_chars(entries: Sequence[Mapping[str, str]], end: int) -> int:
    return len("\n\n".join(str(entry.get("text") or "") for entry in entries[: end + 1]))


def _mark_legacy_user_prefix(
    *,
    system_entries: Sequence[Mapping[str, str]],
    messages: list[dict[str, Any]],
    workload: str,
    floor_chars: int,
) -> tuple[bool, list[str], int]:
    """Cache one legacy user prompt only for repeat-safe batch workloads."""
    if workload not in FALLBACK_REPEATED_USER_WORKLOADS or len(messages) != 1:
        return False, [], 0
    message = messages[0]
    content = message.get("content")
    if message.get("role") != "user" or not isinstance(content, list) or not content:
        return False, [], 0
    text_indices = [
        index
        for index, block in enumerate(content)
        if isinstance(block, Mapping) and str(block.get("type") or "text") == "text" and str(block.get("text") or "")
    ]
    if not text_indices:
        return False, [], 0
    final = text_indices[-1]
    parts = [str(entry.get("text") or "") for entry in system_entries]
    parts.extend(
        str(block.get("text") or "")
        for block in content[: final + 1]
        if isinstance(block, Mapping) and str(block.get("text") or "")
    )
    chars = len("\n\n".join(part for part in parts if part))
    if chars < floor_chars:
        return False, parts, chars
    content[final]["cache_control"] = _cache_control(CACHE_TTL_5M)
    return True, parts, chars


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
    workload = _workload(workload_kind)
    source_messages = _messages(compiled_prompt_artifact, messages)
    slots = _slot_payloads(compiled_prompt_artifact)
    floor_chars = min_cacheable_chars(model)
    entries: list[dict[str, str]] = []
    semantics_preserved = True
    supplemental_tail = ""

    if slots:
        compiled = _system_text(source_messages)
        reconstructed = _compiled_slot_text(slots)
        if compiled == reconstructed:
            supplemental_tail = ""
        elif compiled.startswith(reconstructed) and compiled[len(reconstructed) :].startswith("\n"):
            supplemental_tail = compiled[len(reconstructed) :].lstrip("\n")
        else:
            semantics_preserved = False
        if semantics_preserved:
            for slot in slots:
                slot_id = str(getattr(slot, "slot_id", "") or "").strip()
                content = str(getattr(slot, "content", "") or "")
                if not content:
                    continue
                tier = "tier1_stable" if slot_id in TIER1_SLOTS else "tier2_repeated" if slot_id in TIER2_SLOTS else "volatile_or_schema"
                entries.append({"slot_id": slot_id, "tier": tier, "text": _slot_text(slot_id, content)})
            if supplemental_tail:
                entries.append({"slot_id": "POST_COMPILE_SYSTEM_TAIL", "tier": "post_compile_volatile", "text": supplemental_tail})
        elif compiled:
            entries.append({"slot_id": "COMPILED_SYSTEM_FALLBACK", "tier": "semantic_fallback_uncached", "text": compiled})
    else:
        system = _system_text(source_messages)
        if system:
            entries.append({"slot_id": "FALLBACK_SYSTEM", "tier": "fallback_stable", "text": system})

    candidates: list[tuple[int, str, str]] = []
    if entries and semantics_preserved:
        if slots:
            tier1 = [index for index, entry in enumerate(entries) if entry["slot_id"] in TIER1_SLOTS]
            if tier1:
                candidates.append((max(tier1), "tier1_stable_prefix", CACHE_TTL_1H))
            if workload in REPEATED_C0_WORKLOADS:
                tier2 = [index for index, entry in enumerate(entries) if entry["slot_id"] in TIER2_SLOTS]
                if tier2 and (not candidates or max(tier2) > candidates[-1][0]):
                    candidates.append((max(tier2), "tier2_repeated_prefix", CACHE_TTL_5M))
        else:
            candidates.append((0, "fallback_system_prefix", CACHE_TTL_1H))

    markers: dict[int, dict[str, str]] = {}
    marker_meta: dict[int, dict[str, Any]] = {}
    active_ttls: list[str] = []
    for index, reason, ttl in candidates[:MAX_ANTHROPIC_CACHE_MARKERS]:
        chars = _prefix_chars(entries, index)
        marked = chars >= floor_chars
        marker_meta[index] = {
            "marked": marked,
            "reason": reason if marked else "below_model_cache_floor",
            "prefix_chars": chars,
            "min_cacheable_chars": floor_chars,
            "ttl": ttl if marked else None,
        }
        if marked:
            markers[index] = _cache_control(ttl)
            active_ttls.append(ttl)

    system_blocks: list[dict[str, Any]] = []
    hints: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        block: dict[str, Any] = {"type": "text", "text": entry["text"]}
        if index in markers:
            block["cache_control"] = markers[index]
        system_blocks.append(block)
        meta = marker_meta.get(index)
        if meta:
            reason = meta["reason"]
        elif entry["slot_id"] in TIER1_SLOTS:
            reason = "covered_by_tier1_boundary"
        elif entry["slot_id"] in TIER2_SLOTS:
            reason = "covered_by_tier2_boundary" if workload in REPEATED_C0_WORKLOADS else "one_shot_after_stable_boundary"
        elif entry["slot_id"] == "POST_COMPILE_SYSTEM_TAIL":
            reason = "post_compile_control_preserved_uncached"
        elif entry["slot_id"] == "COMPILED_SYSTEM_FALLBACK":
            reason = "compiled_system_mismatch_fail_closed_uncached"
        elif entry["slot_id"] in VOLATILE_SLOTS:
            reason = "volatile_or_schema_unmarked"
        else:
            reason = "unmarked"
        hints.append(
            {
                "system_block_index": index,
                "slot_id": entry["slot_id"],
                "tier": entry["tier"],
                "marked": index in markers,
                "reason": reason,
                "prefix_chars": meta.get("prefix_chars") if meta else None,
                "min_cacheable_chars": meta.get("min_cacheable_chars") if meta else None,
                "ttl": meta.get("ttl") if meta else None,
            }
        )

    native_messages = _non_system_messages(source_messages)
    legacy_marked = False
    legacy_parts: list[str] = []
    legacy_chars = 0
    if not slots and semantics_preserved:
        legacy_marked, legacy_parts, legacy_chars = _mark_legacy_user_prefix(
            system_entries=entries,
            messages=native_messages,
            workload=workload,
            floor_chars=floor_chars,
        )
        if legacy_marked:
            active_ttls.append(CACHE_TTL_5M)
            hints.append(
                {
                    "message_index": 0,
                    "content_block_index": len(native_messages[0]["content"]) - 1,
                    "slot_id": "FALLBACK_REPEATED_USER_PREFIX",
                    "tier": "tier2_legacy_repeated_user",
                    "marked": True,
                    "reason": "legacy_self_consistency_user_prefix",
                    "prefix_chars": legacy_chars,
                    "min_cacheable_chars": floor_chars,
                    "ttl": CACHE_TTL_5M,
                }
            )
    if not native_messages:
        native_messages = [{"role": "user", "content": ANTHROPIC_SYSTEM_ONLY_USER_PROMPT}]

    final_system_marker = max(markers) if markers else -1
    tier1_indices = [index for index, entry in enumerate(entries) if entry["slot_id"] in TIER1_SLOTS]
    stable_end = max(tier1_indices) if tier1_indices else -1
    stable_parts = [entry["text"] for entry in entries[: stable_end + 1]] if stable_end >= 0 else [entry["text"] for entry in entries if entry["slot_id"] == "FALLBACK_SYSTEM"]
    tier2_parts = [entry["text"] for entry in entries if entry["slot_id"] in TIER2_SLOTS]

    if legacy_marked:
        effective_parts = legacy_parts
        volatile_parts: list[str] = []
    else:
        effective_parts = [entry["text"] for entry in entries[: final_system_marker + 1]] if final_system_marker >= 0 else []
        volatile_parts = [entry["text"] for entry in entries[final_system_marker + 1 :]]
        volatile_parts.extend(_text(message) for message in source_messages if _role(message) != "system")

    stable_hash = _hash(stable_parts)
    tier2_hash = _hash(tier2_parts or (legacy_parts if legacy_marked else []))
    effective_hash = _hash(effective_parts)
    volatile_hash = _hash(volatile_parts)
    group_hash = _hash([section_id, model, effective_hash]) if effective_hash else ""
    marker_count = len(markers) + int(legacy_marked)

    if slots and not semantics_preserved:
        strategy = "pa_compiled_system_fallback_uncached_v1"
    elif slots and marker_count:
        strategy = "pa_slot_prefix_tiers_v2"
    elif slots:
        strategy = "pa_slot_no_cacheable_prefix_v2"
    elif legacy_marked:
        strategy = "fallback_system_user_prefix_v3"
    elif marker_count:
        strategy = "fallback_system_prefix_v2"
    else:
        strategy = "fallback_system_no_cacheable_prefix_v2"

    payload = {
        "system": system_blocks or "Return compact JSON only.",
        "messages": native_messages,
    }
    seed = {
        "provider": "external_claude",
        "model": str(model or ""),
        "section_id": str(section_id or ""),
        "cache_enabled": marker_count > 0,
        "cache_strategy": strategy,
        "workload_kind": workload,
        "stable_prefix_hash": stable_hash,
        "c0_prefix_hash": tier2_hash,
        "tier2_prefix_hash": tier2_hash,
        "effective_cached_prefix_hash": effective_hash,
        "volatile_tail_hash": volatile_hash,
        "cache_group_hash": group_hash,
        "sc_group_hash": group_hash if workload == AnthropicCacheWorkloadKind.SELF_CONSISTENCY.value else "",
        "cache_marker_count": marker_count,
        "model_cache_floor_chars": floor_chars,
        "cache_ttl_policy": {"tier1": CACHE_TTL_1H, "tier2": CACHE_TTL_5M},
        "active_cache_ttls": active_ttls,
        "prompt_semantics_preserved": semantics_preserved,
        "supplemental_system_tail_hash": _hash([supplemental_tail]),
        "legacy_repeated_user_prefix": legacy_marked,
        "input_tokens": None,
        "output_tokens": None,
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "cache_hit_ratio": None,
        "estimated_uncached_input_tokens": None,
        "estimated_cached_input_tokens": None,
        "cache_savings_estimate_source": "pending_anthropic_usage" if marker_count else "no_cacheable_prefix",
        "run_id": str(run_id or ""),
        "prompt_hash": str(prompt_hash or ""),
        "input_payload_hash": str(input_payload_hash or ""),
    }
    return AnthropicSectionCachePayload(
        anthropic_payload=copy.deepcopy(payload),
        cache_strategy=strategy,
        stable_prefix_hash=stable_hash,
        c0_prefix_hash=tier2_hash,
        volatile_tail_hash=volatile_hash,
        cache_boundary_hints=hints,
        cache_marker_count=marker_count,
        cache_receipt_seed=dict(seed),
    )


__all__ = [
    "ANTHROPIC_SYSTEM_ONLY_USER_PROMPT",
    "AnthropicCacheWorkloadKind",
    "AnthropicSectionCachePayload",
    "FALLBACK_REPEATED_USER_WORKLOADS",
    "MAX_ANTHROPIC_CACHE_MARKERS",
    "build_anthropic_section_cache_payload",
]
