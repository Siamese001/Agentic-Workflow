#!/usr/bin/env python3
"""Advisory audit: flag Chroma collections using DefaultEmbeddingFunction (W3.2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    chroma_dir = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not chroma_dir:
        chroma_dir = __import__("os").environ.get("CHROMA_PERSIST_DIR", "").strip()
    if not chroma_dir:
        print(json.dumps({"ok": True, "skipped": True, "reason": "CHROMA_PERSIST_DIR unset"}))
        return 0
    root = Path(chroma_dir)
    if not root.is_dir():
        print(json.dumps({"ok": False, "error": f"chroma path missing: {root.as_posix()}"}))
        return 1
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": f"chromadb unavailable: {exc}"}))
        return 1

    client = chromadb.PersistentClient(path=str(root))
    violations: list[dict[str, str]] = []
    for coll in client.list_collections():
        name = getattr(coll, "name", str(coll))
        meta = getattr(coll, "metadata", None) or {}
        ef_name = str(meta.get("embedding_function") or meta.get("_embedding_function") or "")
        if "DefaultEmbeddingFunction" in ef_name or meta.get("hnsw:space") == "cosine" and not meta.get(
            "chroma_default_ef_forbidden"
        ):
            violations.append({"collection": name, "hint": ef_name or "unknown_ef"})
        try:
            cfg = coll.get_configuration() if hasattr(coll, "get_configuration") else {}
            if isinstance(cfg, dict) and "default" in json.dumps(cfg).lower():
                violations.append({"collection": name, "hint": "configuration mentions default EF"})
        except Exception:
            pass
    try:
        _ = DefaultEmbeddingFunction()
        default_ef_available = True
    except Exception:
        default_ef_available = False
    out = {
        "ok": len(violations) == 0,
        "chroma_persist_dir": root.as_posix(),
        "collection_count": len(list(client.list_collections())),
        "violations": violations,
        "default_ef_class_available": default_ef_available,
        "advisory": True,
    }
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
