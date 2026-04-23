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

Dual-read migration path
------------------------
Call sites that cache-by-key should transitionally:

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
from typing import TYPE_CHECKING

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
    canonical = {
        code.upper(): content.rstrip() for code, content in prompt_messages.slot_map.items()
    }
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


__all__ = [
    "LEGACY_FLAT_PREFIX",
    "SLOT_DIGEST_PREFIX",
    "SLOT_DIGEST_SCHEME_VERSION",
    "compute_slot_digest_key",
    "is_legacy_flat_key",
    "is_slot_digest_key",
    "legacy_flat_key",
]
