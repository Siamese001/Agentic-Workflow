"""Unit tests for ChunkManifest.situated_context (W1.3, ADR-045 schema 1.1).

Covers the deferred-scope item posted to Notion as
"[P1] W1 W1.3 — Add situated_context field to canonical ChunkManifest schema"
(page 34c27693f55c815cad4cfc11f26bd077).

Properties verified:
1. Default is empty string (back-compat: a chunk with no contextualization
   serializes identically to a 1.0-era chunk except for the new key).
2. New manifests stamp schema_version="1.1" by default.
3. to_dict round-trip preserves situated_context.
4. from_dict on a legacy (1.0) payload that lacks situated_context yields
   situated_context="" without raising.
5. from_dict on a 1.1 payload preserves the field.
6. content_hash continues to be derived from raw_text only — situated_context
   does NOT participate in hashing (it's a sidecar, not a corpus mutation).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make repo root importable when run standalone.
_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.knowledge.canonical.chunk_manifest import ChunkManifest


def test_situated_context_defaults_to_empty_string():
    m = ChunkManifest(chunk_id="c1", raw_text="hello")
    assert m.situated_context == ""


def test_default_schema_version_is_1_1():
    m = ChunkManifest(chunk_id="c1", raw_text="hello")
    assert m.schema_version == "1.1"


def test_situated_context_round_trips_through_to_dict_from_dict():
    ctx = "This chunk defines the RetrievalPrefilter class within the C0 pipeline."
    original = ChunkManifest(
        chunk_id="c1",
        raw_text="class RetrievalPrefilter: ...",
        situated_context=ctx,
    )
    payload = original.to_dict()
    assert payload["situated_context"] == ctx
    assert payload["schema_version"] == "1.1"

    restored = ChunkManifest.from_dict(payload)
    assert restored.situated_context == ctx
    assert restored.schema_version == "1.1"
    assert restored.chunk_id == "c1"
    assert restored.raw_text == "class RetrievalPrefilter: ..."


def test_legacy_1_0_payload_reads_with_empty_situated_context():
    """A serialized 1.0 manifest (no situated_context, no 1.1 stamp) must
    deserialize cleanly with situated_context defaulted to '' and the legacy
    schema_version preserved as 1.0."""
    legacy_payload = {
        "chunk_id": "c2",
        "raw_text": "legacy chunk text",
        "schema_version": "1.0",
        # NOTE: no situated_context key — this is the back-compat case.
    }
    restored = ChunkManifest.from_dict(legacy_payload)
    assert restored.situated_context == ""
    assert restored.schema_version == "1.0"  # preserved, not auto-upgraded
    assert restored.raw_text == "legacy chunk text"


def test_situated_context_does_not_affect_content_hash():
    """Hashing rule (line 178 chunk_manifest.py): content_hash derives from
    raw_text only. Adding situated_context must NOT change the hash, because
    the situated_context is a retrieval-time presentation sidecar and changing
    it must not invalidate downstream caches keyed on content_hash."""
    bare = ChunkManifest(chunk_id="c1", raw_text="payload")
    enriched = ChunkManifest(
        chunk_id="c1",
        raw_text="payload",
        situated_context="this chunk explains the payload contract",
    )
    assert bare.content_hash == enriched.content_hash
    assert bare.content_hash != ""  # sanity: it WAS computed


def test_explicit_empty_situated_context_serializes_as_empty_string():
    """Belt-and-braces: confirm to_dict always emits the key even when empty,
    so downstream readers can rely on the key being present in 1.1 payloads."""
    m = ChunkManifest(chunk_id="c1", raw_text="x", situated_context="")
    payload = m.to_dict()
    assert "situated_context" in payload
    assert payload["situated_context"] == ""
