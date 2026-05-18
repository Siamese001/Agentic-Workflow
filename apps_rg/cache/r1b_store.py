"""File-backed R1B semantic cache fixture mirror (not durable production truth)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    DURABLE_WRITE_VIA_UWG,
    FILE_BACKED_SSOT_NOTE,
    STORAGE_TIER_FIXTURE_MIRROR,
)
from apps_rg.cache.r1b_intent_vector import vector_payload
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_store_root(repo_root: Path | None = None) -> Path:
    env = os.environ.get("APPS_RG_R1B_CACHE_ROOT", "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (Path.cwd() / p).resolve()
    root = repo_root or _find_repo_root()
    return root / "artifacts" / "apps_rg" / "r1b_semantic_cache"


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume").exists():
            return parent
    return Path.cwd()


class R1BSemanticCacheStore:
    """Fixture/proof mirror for HistoricalIntentRecord + child chunks (ROLE_TARGET_RUN).

    Durable production persistence requires UWG admission via
    ``apps_rg.cache.r1b_uwg_promotion.promote_and_project_r1b_cache``.
    """

    durable_write_status: str = DURABLE_WRITE_VIA_UWG
    storage_tier: str = STORAGE_TIER_FIXTURE_MIRROR

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()
        self.intents_dir = self.root / "intents"
        self.chunks_dir = self.root / "chunks"
        self.vectors_dir = self.root / "vectors"
        self.index_dir = self.root / "index" / "by_digest"
        for d in (self.intents_dir, self.chunks_dir, self.vectors_dir, self.index_dir):
            d.mkdir(parents=True, exist_ok=True)

    def write_intent(self, record: HistoricalIntentRecord) -> None:
        path = self.intents_dir / f"{record.record_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        vec_path = self.root / record.request_intent_vector_ref.replace("\\", "/")
        vec_path.parent.mkdir(parents=True, exist_ok=True)
        vec_path.write_text(
            json.dumps(vector_payload(record.normalized_intent_digest), indent=2) + "\n",
            encoding="utf-8",
        )
        idx = self.index_dir / f"{record.normalized_intent_digest}.json"
        idx.write_text(
            json.dumps({"record_id": record.record_id, "updated_at_utc": _utc_now()}, indent=2) + "\n",
            encoding="utf-8",
        )

    def write_chunk(self, chunk: HistoricalOutputChunk) -> None:
        parent = self.chunks_dir / chunk.parent_intent_record_id
        parent.mkdir(parents=True, exist_ok=True)
        path = parent / f"{chunk.chunk_id}.json"
        path.write_text(json.dumps(chunk.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def load_intent(self, record_id: str) -> HistoricalIntentRecord | None:
        path = self.intents_dir / f"{record_id}.json"
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if not isinstance(data, dict):
            return None
        return HistoricalIntentRecord.from_dict(data)

    def load_chunks(self, parent_intent_record_id: str) -> list[HistoricalOutputChunk]:
        parent = self.chunks_dir / parent_intent_record_id
        if not parent.is_dir():
            return []
        out: list[HistoricalOutputChunk] = []
        for child in sorted(parent.glob("*.json")):
            try:
                data = json.loads(child.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(data, dict):
                out.append(HistoricalOutputChunk.from_dict(data))
        return out

    def load_intent_vector(self, record: HistoricalIntentRecord) -> list[float]:
        rel = record.request_intent_vector_ref.replace("\\", "/")
        path = self.root / rel
        if not path.is_file():
            from apps_rg.cache.r1b_intent_vector import pseudo_vector_from_digest

            return pseudo_vector_from_digest(record.normalized_intent_digest)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            vals = data.get("values")
            if isinstance(vals, list) and vals:
                return [float(x) for x in vals]
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass
        from apps_rg.cache.r1b_intent_vector import pseudo_vector_from_digest

        return pseudo_vector_from_digest(record.normalized_intent_digest)

    def list_intent_record_ids(self) -> list[str]:
        return sorted(p.stem for p in self.intents_dir.glob("*.json"))

    def store_manifest(self) -> dict[str, Any]:
        return {
            "durable_write_via_uwg": self.durable_write_status,
            "storage_tier": self.storage_tier,
            "is_durable_production_truth": False,
            "file_backed_ssot_note": FILE_BACKED_SSOT_NOTE,
            "root": str(self.root),
            "intent_count": len(self.list_intent_record_ids()),
        }


__all__ = [
    "R1BSemanticCacheStore",
    "default_store_root",
]
