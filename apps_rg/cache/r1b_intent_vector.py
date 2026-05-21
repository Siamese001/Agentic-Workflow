"""Deterministic intent digest + pseudo-vector for R1B lookup (no Chroma / fact_vectors)."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any


_VECTOR_DIM = 32


def normalized_intent_digest(intent_text: str) -> str:
    text = intent_text.strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def intent_text_from_request(raw: dict[str, Any]) -> str:
    """Canonical ROLE_TARGET_RUN intent string (apps_rg)."""
    company = str(raw.get("target_company") or "").strip().lower()
    role = str(raw.get("target_role") or "").strip().lower()
    jd_hash = str(raw.get("jd_hash") or "").strip()
    brief_hash = str(raw.get("brief_hash") or "").strip()
    resume_hash = str(raw.get("resume_hash") or "").strip()
    gen_mode = str(raw.get("generation_mode") or "strategic_tailor").strip().lower()
    envelope = "|".join(
        (
            "apps_rg",
            "role_target_run",
            company,
            role,
            gen_mode,
            jd_hash,
            brief_hash,
            resume_hash,
        )
    )
    return envelope


def pseudo_vector_from_digest(digest_hex: str) -> list[float]:
    """Expand sha256 digest into a fixed-dim unit vector for cosine similarity."""
    raw = bytes.fromhex(digest_hex[:64].ljust(64, "0")[:64])
    floats: list[float] = []
    for i in range(_VECTOR_DIM):
        chunk = raw[i % len(raw) : (i % len(raw)) + 4]
        if len(chunk) < 4:
            chunk = chunk + raw[: 4 - len(chunk)]
        val = struct.unpack(">i", chunk.ljust(4, b"\0")[:4])[0]
        floats.append(float(val))
    norm = math.sqrt(sum(x * x for x in floats)) or 1.0
    return [x / norm for x in floats]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return max(-1.0, min(1.0, dot))


def vector_ref_relative(record_id: str) -> str:
    return f"vectors/{record_id}.json"


def vector_payload(digest: str, *, intent_text: str = "") -> dict[str, Any]:
    if intent_text.strip():
        from apps_rg.cache.r1b_bge_embedding import intent_vector_payload

        return intent_vector_payload(intent_text=intent_text, digest=digest)
    return {
        "subsystem": "apps_rg_r1b_semantic_cache",
        "not_c0_fact_vectors": True,
        "normalized_intent_digest": digest,
        "dimensions": _VECTOR_DIM,
        "values": pseudo_vector_from_digest(digest),
    }


__all__ = [
    "cosine_similarity",
    "intent_text_from_request",
    "normalized_intent_digest",
    "pseudo_vector_from_digest",
    "vector_payload",
    "vector_ref_relative",
]
