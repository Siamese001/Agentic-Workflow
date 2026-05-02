"""HOP2 research — assemble an evidence bundle from retrieval + features.

Consumes ``context["profile_features"]`` (from HOP1) and
``context["retrieval_chunks"]`` (injected by the outer substrate's C0
retrieval phase) and emits ``context["evidence_bundle"]`` — a normalized
list of citation-bearing evidence items for downstream grounding.

Re-derived per Wave 2 Phase 2.2.
"""

from __future__ import annotations

from typing import Any


class ResearchEngine:
    """Normalize retrieved chunks into an evidence bundle."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        chunks = context.get("retrieval_chunks") or []
        features = context.get("profile_features") or {}

        evidence_items: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks):
            text = self._text_of(chunk)
            source = self._source_of(chunk)
            score = self._score_of(chunk)
            if not text:
                continue
            evidence_items.append(
                {
                    "id": f"ev-{idx + 1}",
                    "text": text,
                    "source": source,
                    "score": score,
                }
            )

        return {
            "evidence_bundle": {
                "items": evidence_items,
                "count": len(evidence_items),
                "archetype_hint": features.get("archetype_hint", "GENERIC"),
            },
        }

    # ------------------------------------------------------------------
    # Chunk shape normalization — hybrid retrieval returns heterogeneous
    # types (HybridSearchResult, dicts, tuples). Read defensively.
    # ------------------------------------------------------------------

    @staticmethod
    def _text_of(chunk: Any) -> str:
        for attr in ("text", "content", "body"):
            if hasattr(chunk, attr):
                return str(getattr(chunk, attr) or "")
        if isinstance(chunk, dict):
            for key in ("text", "content", "body"):
                if key in chunk:
                    return str(chunk[key] or "")
        return ""

    @staticmethod
    def _source_of(chunk: Any) -> str:
        for attr in ("source", "doc_id", "id"):
            if hasattr(chunk, attr):
                return str(getattr(chunk, attr) or "")
        if isinstance(chunk, dict):
            for key in ("source", "doc_id", "id"):
                if key in chunk:
                    return str(chunk[key] or "")
        return ""

    @staticmethod
    def _score_of(chunk: Any) -> float:
        for attr in ("combined_score", "score", "rank_score"):
            if hasattr(chunk, attr):
                try:
                    return float(getattr(chunk, attr))
                except (TypeError, ValueError):
                    continue
        if isinstance(chunk, dict):
            for key in ("combined_score", "score", "rank_score"):
                if key in chunk:
                    try:
                        return float(chunk[key])
                    except (TypeError, ValueError):
                        continue
        return 0.0
