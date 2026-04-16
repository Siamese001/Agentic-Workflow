"""C4.1 freeze-gate audit against the current post-C2.2 collection state.

Imports the 20 audit queries, REQUIRED_FIELDS, and grounding logic from the
canonical Wave B audit module (`tools/eval/audit_wave_b_target_state.py`) so
the computation is identical to B7. Writes the C4.1 report ONLY to
`docs/reports/wave_c_freeze_gates.md`. Does NOT touch the B7 canonical
artifacts (wave_b_freeze_gates.json, wave_b_external_target_state_audit.md).

Temporary probe — safe to delete after C4.1 closeout.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval.audit_wave_b_target_state import (  # noqa: E402
    ADEQUATE_DIST,
    AUDIT_QUERIES,
    REQUIRED_FIELDS,
    STRONG_DIST,
    answer_support_check,
    grounding_verdict,
)

CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
EMBEDDING_MODEL = "BAAI/bge-m3"
OUT_MD = REPO_ROOT / "docs" / "reports" / "wave_c_freeze_gates.md"


def main() -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    t0 = time.perf_counter()
    model = SentenceTransformer(EMBEDDING_MODEL)
    model.max_seq_length = 512
    print(f"model_load_s={round(time.perf_counter() - t0, 3)}")

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    available = {c.name for c in client.list_collections()}
    print(f"collections={sorted(available)}")

    ext_col = client.get_collection("ext_authority")
    repo_col = client.get_collection("repo_evidence")
    raw_col = client.get_collection("ext_raw") if "ext_raw" in available else None

    ext_count = ext_col.count()
    repo_count = repo_col.count()
    raw_count = raw_col.count() if raw_col else 0
    print(f"ext_authority={ext_count} repo_evidence={repo_count} ext_raw={raw_count}")

    # Fetch metadata (no documents — gate checks only)
    print("fetching_metadata...")
    ext_metas = ext_col.get(include=["metadatas"])["metadatas"]
    repo_metas = repo_col.get(include=["metadatas"])["metadatas"]
    raw_metas = raw_col.get(include=["metadatas"])["metadatas"] if raw_col else []

    gates: dict[str, dict] = {}

    # --- Metadata gates (G1-G8) ----------------------------------------------
    g1_bad = [m for m in ext_metas if m.get("invalid_for_normative_use") is not False]
    gates["G1"] = {
        "pass": not g1_bad,
        "detail": f"{len(g1_bad)} chunks with invalid_for_normative_use != False",
        "count": len(ext_metas),
    }

    g2_bad = [m for m in ext_metas if not m.get("source_url", "").startswith("https://")]
    gates["G2"] = {
        "pass": not g2_bad,
        "detail": f"{len(g2_bad)} chunks with non-https source_url",
        "count": len(ext_metas),
    }

    g3_bad = [m for m in ext_metas if not REQUIRED_FIELDS.issubset(m.keys())]
    gates["G3"] = {
        "pass": not g3_bad,
        "detail": f"{len(g3_bad)} chunks missing required fields",
        "count": len(ext_metas),
    }

    g4_bad = [m for m in repo_metas if m.get("invalid_for_normative_use") is not True]
    gates["G4"] = {
        "pass": not g4_bad,
        "detail": f"{len(g4_bad)} chunks with invalid_for_normative_use != True",
        "count": len(repo_metas),
    }

    g5_bad = [m for m in repo_metas if m.get("source_url", "").startswith("https://")]
    gates["G5"] = {
        "pass": not g5_bad,
        "detail": f"{len(g5_bad)} chunks with https:// source_url",
        "count": len(repo_metas),
    }

    g6_bad = [m for m in repo_metas if not REQUIRED_FIELDS.issubset(m.keys())]
    gates["G6"] = {
        "pass": not g6_bad,
        "detail": f"{len(g6_bad)} chunks missing required fields",
        "count": len(repo_metas),
    }

    g7_bad = [m for m in raw_metas if m.get("invalid_for_normative_use") is not True]
    gates["G7"] = {
        "pass": not g7_bad,
        "detail": f"{len(g7_bad)} chunks with invalid_for_normative_use != True",
        "count": len(raw_metas),
    }

    ext_urls = {m["source_url"] for m in ext_metas if m.get("source_url")}
    g8_bad = [m for m in raw_metas if m.get("source_url") in ext_urls]
    gates["G8"] = {
        "pass": not g8_bad,
        "detail": f"{len(g8_bad)} chunks with source_url already in ext_authority",
        "count": len(raw_metas),
    }

    # --- Retrieval gates (G9/G10/G11) ----------------------------------------
    print(f"running {len(AUDIT_QUERIES)} target-state audit queries...")
    audit_results = []
    for qi, q in enumerate(AUDIT_QUERIES, 1):
        emb = model.encode(q["text"], normalize_embeddings=True, show_progress_bar=False).tolist()
        raw = ext_col.query(
            query_embeddings=[emb],
            n_results=5,
            include=["documents", "metadatas", "distances"],
        )
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        top5 = []
        for doc, meta, dist in zip(docs, metas, dists):
            top5.append(
                {
                    "dist": round(float(dist), 4),
                    "source_url": meta.get("source_url", ""),
                    "heading_path": meta.get("heading_path", ""),
                    "authority_tier": meta.get("authority_tier", ""),
                    "source_band": meta.get("source_band", ""),
                    "topic_bucket": meta.get("topic_bucket", ""),
                    "collection": meta.get("source_collection", ""),
                    "answer_support": answer_support_check(doc, q["text"]),
                }
            )
        d1 = top5[0]["dist"] if top5 else 2.0
        support = top5[0]["answer_support"] if top5 else False
        audit_results.append(
            {
                "query": q,
                "top5": top5,
                "dist_at_1": d1,
                "grounding": grounding_verdict(d1, support),
            }
        )
        if qi % 5 == 0:
            print(f"  [{qi:02d}/{len(AUDIT_QUERIES)}] done")

    strong = sum(1 for r in audit_results if r["grounding"] == "STRONG")
    adequate = sum(1 for r in audit_results if r["grounding"] == "ADEQUATE")
    weak = sum(1 for r in audit_results if r["grounding"] == "WEAK")
    empty = sum(1 for r in audit_results if r["grounding"] == "EMPTY")
    covered = strong + adequate

    # G9 threshold: >= 15/20 per canonical script (== >=75%)
    gates["G9"] = {
        "pass": covered >= 15,
        "detail": f"Strong={strong} Adequate={adequate} Weak={weak} Empty={empty} covered={covered}/{len(AUDIT_QUERIES)}",
        "count": len(AUDIT_QUERIES),
    }

    repo_contam = sum(
        1
        for r in audit_results
        for h in r["top5"]
        if h["collection"] != "ext_authority" and h["collection"] != ""
    )
    gates["G10"] = {
        "pass": repo_contam == 0,
        "detail": f"{repo_contam} non-ext_authority chunks in target-state audit top-5s",
        "count": sum(len(r["top5"]) for r in audit_results),
    }

    raw_contam = sum(1 for r in audit_results for h in r["top5"] if h["collection"] == "ext_raw")
    gates["G11"] = {
        "pass": raw_contam == 0,
        "detail": f"{raw_contam} ext_raw chunks in target-state audit top-5s",
        "count": sum(len(r["top5"]) for r in audit_results),
    }

    # --- Print summary to stdout ---------------------------------------------
    all_pass = all(g["pass"] for g in gates.values())
    print("\n===== GATE RESULTS =====")
    for gk, gv in gates.items():
        print(f"  {gk}: {'PASS' if gv['pass'] else 'FAIL'} — {gv['detail']}")
    print(f"\nverdict={'PASS' if all_pass else 'FAIL'}")
    print(f"collection_counts: ext_authority={ext_count} repo_evidence={repo_count} ext_raw={raw_count}")

    # --- Dump structured JSON for the writer phase ---------------------------
    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {"ext_authority": ext_count, "repo_evidence": repo_count, "ext_raw": raw_count},
        "grounding": {"STRONG": strong, "ADEQUATE": adequate, "WEAK": weak, "EMPTY": empty},
        "gates": gates,
        "audit_per_query": [
            {
                "id": r["query"]["id"],
                "topic": r["query"]["topic"],
                "dist_at_1": r["dist_at_1"],
                "grounding": r["grounding"],
                "top1_source": r["top5"][0]["source_url"][:80] if r["top5"] else "",
                "top1_collection": r["top5"][0]["collection"] if r["top5"] else "",
            }
            for r in audit_results
        ],
        "all_pass": all_pass,
    }
    out_json = REPO_ROOT / "tools" / "debug" / "wave_c_freeze_gates_results.json"
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"results_json={out_json}")


if __name__ == "__main__":
    main()
