"""Structured-slot replay-key digest (phase RH2B.1).

Plan: prompt-reception-followups-a7b3c4.

Historical context
------------------
Prior to this phase, replay-cache keys (``agentic_core.L4_state.cache.gptcache_client``)
were computed as ``sha256(flat_query_string)`` where the flat string was the
joined ``final_system_string + final_user_string`` of a
``CompiledPromptArtifact``. This had three problems:

1. **Prompt-drift false negatives.** Semantically identical prompts with
   different slot interleavings produced different keys, so the cache missed
   equivalent requests.
2. **Exemplar-insensitive.** Changing an E0 exemplar rotated every key even
   when the rest of the prompt was stable.
3. **Irreplayable after W6 structured-slot introduction.** The gateway now
   consumes a ``PromptMessages`` IR; the flat-string key is no longer the
   canonical request surface.

New scheme
----------
``compute_slot_digest_key(prompt_messages)`` hashes a canonical JSON
representation of the slot map — slot codes sorted, content trimmed — with
an explicit scheme version prefix so future migrations are identifiable in
stored keys.

Adoption status (2026-04-23)
----------------------------
This module is **additive scaffolding**. No production call site currently
caches ``CompiledPromptArtifact`` envelopes by a flat-string replay key:

- ``agentic_core.L4_state.cache.gptcache_client.NativePersistentCacheClient``
  is a *semantic* cache keyed by arbitrary query strings (BGE-M3 embedding
  similarity) — not a prompt-envelope replay cache. Its ``_get_id`` does
  ``sha256(query_string)`` on free-form queries, so there is nothing to
  dual-read here.
- ``agentic_core.L6_observability.utils.engines.replay_key_computer`` is a
  broader telemetry-side replay-key computer covering many components
  (timestamps, layer context, C0 hash). Not prompt-envelope specific.

When a future call site DOES cache ``CompiledPromptArtifact`` by
envelope, it should follow the dual-read pattern below — which is why the
utility ships now, ahead of the call site.

Dual-read migration pattern (for future call sites)
---------------------------------------------------

1. Compute the new ``slot_digest_key`` from ``PromptMessages``.
2. On cache miss, fall back to the legacy ``flat_string_key`` built from
   ``artifact.final_system_string + final_user_string``.
3. On a legacy-hit, rewrite the entry under the new key (write-through).

Helper ``legacy_flat_key(system_str, user_str)`` is provided so both schemes
can coexist during the warm window. Callers opt in; this module does not
mutate existing cache storage on its own.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages


# Prefix lets us recognize which scheme produced a stored key — critical for
# dual-read migration and for future scheme rotations. Bump the version when
# the canonicalization rules change.
SLOT_DIGEST_SCHEME_VERSION = "v1"
SLOT_DIGEST_PREFIX = f"rkslot-{SLOT_DIGEST_SCHEME_VERSION}-"
LEGACY_FLAT_PREFIX = "rkflat-v0-"


def compute_slot_digest_key(prompt_messages: PromptMessages) -> str:
    """Compute a replay-cache key from a ``PromptMessages`` IR.

    The key is scheme-prefixed so callers can detect which version produced
    it when inspecting stored entries.

    Canonicalization rules:

    - Slot codes are upper-cased.
    - Slot content strings are ``rstrip()``-ed (trailing whitespace is
      semantically irrelevant to the model) but not otherwise altered.
    - Keys are sorted lexicographically before hashing.
    - ``metadata`` and ``exemplars`` are NOT included — the rationale is
      that exemplars live inside E0 slot content already, and metadata is
      provenance rather than request shape.
    """
    canonical = {code.upper(): content.rstrip() for code, content in prompt_messages.slot_map.items()}
    payload = json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"{SLOT_DIGEST_PREFIX}{digest}"


def legacy_flat_key(system_string: str, user_string: str) -> str:
    """Compute the legacy flat-string replay-cache key.

    Retained only for the dual-read migration window. New call sites MUST
    use :func:`compute_slot_digest_key`. The scheme prefix lets stored
    entries be triaged when we tighten the cache during the removal phase.
    """
    flat = (system_string or "") + (user_string or "")
    digest = hashlib.sha256(flat.encode("utf-8")).hexdigest()
    return f"{LEGACY_FLAT_PREFIX}{digest}"


def is_slot_digest_key(key: str) -> bool:
    """Return True if the key was produced by the new slot-digest scheme."""
    return isinstance(key, str) and key.startswith(SLOT_DIGEST_PREFIX)


def is_legacy_flat_key(key: str) -> bool:
    """Return True if the key was produced by the pre-RH2B.1 flat scheme."""
    return isinstance(key, str) and key.startswith(LEGACY_FLAT_PREFIX)


@dataclass(frozen=True)
class DualReadResult:
    """Outcome of a dual-read cache lookup across replay-key schemes.

    Attributes:
        value: The cached value, or ``None`` on a cache miss under both schemes.
        hit_scheme: Which scheme produced the hit — ``"slot_digest"``,
            ``"legacy_flat"``, or ``None`` on miss.
        slot_key: The slot-digest key used for lookup and for write-through
            on a legacy hit.
        legacy_key: The legacy flat key used for fallback lookup.
    """

    value: Optional[Any]
    hit_scheme: Optional[str]
    slot_key: str
    legacy_key: str

    @property
    def is_hit(self) -> bool:
        return self.hit_scheme is not None

    @property
    def needs_rekey(self) -> bool:
        """True iff the hit came from the legacy scheme and should be rewritten."""
        return self.hit_scheme == "legacy_flat"


def dual_read_replay_key(
    prompt_messages: "PromptMessages",
    legacy_system_string: str,
    legacy_user_string: str,
    cache_lookup: Callable[[str], Optional[Any]],
) -> DualReadResult:
    """Look up a cached entry under the new slot-digest key, falling back to legacy.

    This is the canonical consumer-side helper for the RH2B.1 migration: call
    it from any cache client that needs to verify pre-merge artifacts whose
    original keying scheme may have been either the pre-RH2B.1 flat hash or
    the new slot-digest.

    The ``cache_lookup`` callable receives a fully-prefixed key string and
    must return the cached value, or ``None`` on miss. It MUST NOT raise on
    miss — a raising lookup is a programmer error at the consumer, not a
    migration concern.

    Args:
        prompt_messages: The structured IR used to compute the slot-digest key.
        legacy_system_string: ``CompiledPromptArtifact.final_system_string``
            at the time of the original cache write. Required for the legacy
            fallback only.
        legacy_user_string: ``CompiledPromptArtifact.final_user_string`` at
            the time of the original cache write.
        cache_lookup: Callable that returns the cached value for a key, or
            ``None`` on miss.

    Returns:
        A :class:`DualReadResult` describing the hit (if any) and carrying
        both candidate keys for a subsequent ``rekey_legacy_to_slot`` call.
    """
    slot_key = compute_slot_digest_key(prompt_messages)
    legacy_key = legacy_flat_key(legacy_system_string, legacy_user_string)

    slot_hit = cache_lookup(slot_key)
    if slot_hit is not None:
        return DualReadResult(
            value=slot_hit,
            hit_scheme="slot_digest",
            slot_key=slot_key,
            legacy_key=legacy_key,
        )

    legacy_hit = cache_lookup(legacy_key)
    if legacy_hit is not None:
        return DualReadResult(
            value=legacy_hit,
            hit_scheme="legacy_flat",
            slot_key=slot_key,
            legacy_key=legacy_key,
        )

    return DualReadResult(
        value=None,
        hit_scheme=None,
        slot_key=slot_key,
        legacy_key=legacy_key,
    )


def rekey_legacy_to_slot(
    dual_read: DualReadResult,
    cache_write: Callable[[str, Any], None],
) -> bool:
    """Rewrite a legacy-scheme cache hit under the new slot-digest key.

    Call this after a :func:`dual_read_replay_key` result whose
    ``needs_rekey`` is ``True``. The function is a no-op on a fresh miss or a
    slot-digest hit, so consumers can call it unconditionally after every
    dual-read.

    The ``cache_write`` callable takes ``(key, value)`` and stores it. It is
    NOT responsible for invalidating the legacy entry; callers that want to
    evict legacy keys should do so explicitly once the warm window closes.

    Returns:
        ``True`` if a rewrite was performed, ``False`` otherwise.
    """
    if not dual_read.needs_rekey or dual_read.value is None:
        return False
    cache_write(dual_read.slot_key, dual_read.value)
    return True


__all__ = [
    "LEGACY_FLAT_PREFIX",
    "SLOT_DIGEST_PREFIX",
    "SLOT_DIGEST_SCHEME_VERSION",
    "DualReadResult",
    "compute_slot_digest_key",
    "dual_read_replay_key",
    "is_legacy_flat_key",
    "is_slot_digest_key",
    "legacy_flat_key",
    "rekey_legacy_to_slot",
]
