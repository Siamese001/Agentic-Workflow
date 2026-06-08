"""HOP2 evidence normalization from C0/manual/preloaded data.

Consumes ``context["profile_features"]`` (from HOP1) and
``context["retrieval_chunks"]`` (bounded C0 evidence injected by L2) and emits
``context["evidence_bundle"]``. This stage performs no live web search, no
cross-app delegation, and no research-app calls.

Re-derived per Wave 2 Phase 2.2.
"""

from __future__ import annotations

from typing import Any


class ResearchEngine:
    """Normalize retrieved chunks into an evidence bundle."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        chunks = context.get("retrieval_chunks") or []
        features = context.get("profile_features") or {}
        support_status = str(context.get("c0_support_status", "") or "")
        evidence_sufficiency_score = float(
            context.get("c0_evidence_sufficiency_score", 0.0) or 0.0
        )

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
                "support_status": support_status,
                "evidence_sufficiency_score": evidence_sufficiency_score,
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
