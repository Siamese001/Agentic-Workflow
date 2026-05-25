#!/usr/bin/env python3
"""Capture byte-stable semantic-cache fingerprints for a bounded namespace.

Plan: semantic-cache-fingerprint-proof-c9f1a3 (W2.1–W2.2).
Scope: Redis semantic-cache manager stats + optional Chroma collection listing.
Does NOT claim global cache immutability — only named namespace/collection scope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
_REPO = next((p for p in [_HERE.parent, *_HERE.parents] if (p / "pyproject.toml").exists()), _HERE.parents[2])
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_DEFAULT_OUT = _REPO / "artifacts" / "governance" / "semantic_cache_fingerprint.json"
_RECEIPT = _REPO / "artifacts" / "governance" / "semantic_cache_fingerprint_receipt.md"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _capture_manager(namespace: str) -> dict[str, Any]:
    out: dict[str, Any] = {"namespace": namespace, "source": "SemanticCacheManager"}
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            SemanticCacheManager,
        )

        sc = SemanticCacheManager.get_instance()
        stats = dict(sc.stats or {})
        out["stateless_mode"] = bool(sc.stateless_mode)
        out["redis_enabled"] = bool(sc.redis_enabled)
        out["gptcache_enabled"] = bool(sc.gptcache_enabled)
        out["stats"] = stats
        payload = _canonical_json(
            {
                "namespace": namespace,
                "stats": stats,
                "redis_enabled": out["redis_enabled"],
                "gptcache_enabled": out["gptcache_enabled"],
            }
        )
        out["payload_sha256"] = _sha256_bytes(payload.encode("utf-8"))
    except Exception as exc:  # guardian: allow-broad-exception -- proof script must degrade
        out["error"] = f"{type(exc).__name__}:{exc}"
        out["payload_sha256"] = _sha256_bytes(b"unavailable")
    return out


def _capture_chroma(collections: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {"source": "ChromaDB", "collections": {}}
    try:
        import chromadb  # type: ignore[import-untyped]

        persist = Path(
            str(
                __import__("os").environ.get("CHROMA_PERSIST_DIR")
                or (_REPO / "artifacts" / "chroma" / "persist")
            )
        )
        client = chromadb.PersistentClient(path=str(persist))
        try:
            names = collections or [c.name for c in client.list_collections()]
            for name in names[:32]:
                coll = client.get_collection(name)
                count = int(coll.count())
                meta = dict(coll.metadata or {})
                row = {"count": count, "metadata": meta}
                out["collections"][name] = row
            payload = _canonical_json(out["collections"])
            out["collections_sha256"] = _sha256_bytes(payload.encode("utf-8"))
        finally:
            client.close()
    except Exception as exc:  # guardian: allow-broad-exception -- optional Chroma probe
        out["error"] = f"{type(exc).__name__}:{exc}"
        out["collections_sha256"] = _sha256_bytes(b"unavailable")
    return out


def capture_fingerprint(
    *,
    namespace: str = "apps_rg",
    collections: list[str] | None = None,
    label: str = "snapshot",
) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    doc: dict[str, Any] = {
        "schema_version": "semantic_cache_fingerprint_v1",
        "label": label,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope_limit": (
            f"namespace={namespace!r} only; not a claim of global cache immutability"
        ),
        "manager": _capture_manager(namespace),
        "chromadb": _capture_chroma(list(collections or [])),
    }
    composite = _canonical_json(
        {
            "manager": doc["manager"].get("payload_sha256"),
            "chromadb": doc["chromadb"].get("collections_sha256"),
            "namespace": namespace,
            "label": label,
        }
    )
    doc["composite_sha256"] = _sha256_bytes(composite.encode("utf-8"))
    doc["artifact_basename"] = f"semantic_cache_fingerprint_{label}_{ts}.json"
    return doc


def write_artifacts(doc: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        art_rel = out_path.relative_to(_REPO).as_posix()
    except ValueError:
        art_rel = str(out_path)
    receipt = (
        f"# Semantic cache fingerprint receipt\n\n"
        f"- **Scope:** {doc.get('scope_limit')}\n"
        f"- **Label:** {doc.get('label')}\n"
        f"- **Composite SHA256:** `{doc.get('composite_sha256')}`\n"
        f"- **Artifact:** `{art_rel}`\n"
        f"- **Captured:** {doc.get('captured_at_utc')}\n"
    )
    _RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    _RECEIPT.write_text(receipt, encoding="utf-8")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--namespace", default="apps_rg")
    ap.add_argument("--label", default="snapshot")
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    ap.add_argument("--collection", action="append", default=[])
    args = ap.parse_args()
    doc = capture_fingerprint(
        namespace=args.namespace,
        collections=args.collection or None,
        label=args.label,
    )
    path = write_artifacts(doc, args.out)
    print(f"OK semantic_cache_fingerprint label={args.label} path={path}")
    print(f"composite_sha256={doc['composite_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
