"""Wave D7.1 gate probe — validates G4/G5/G6 against the post-D7.1 collection state.

Pure metadata-only checks — no embedding model load, no target-state queries.
Reuses REQUIRED_FIELDS from tools.eval.audit_wave_b_target_state so the 14-field
contract stays identical to the Wave B canonical definition.

Temporary probe — safe to delete after D7.1 closeout.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval.audit_wave_b_target_state import REQUIRED_FIELDS  # noqa: E402

CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
EXPECTED_EXT_AUTHORITY = 604  # B7-frozen
EXPECTED_EXT_RAW = 70  # B3-frozen


def main() -> None:
    import chromadb

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    available = {c.name for c in client.list_collections()}
    print(f"collections={sorted(available)}")

    ext_col = client.get_collection("ext_authority")
    repo_col = client.get_collection("repo_evidence")
    raw_col = client.get_collection("ext_raw") if "ext_raw" in available else None

    ext_count = ext_col.count()
    repo_count = repo_col.count()
    raw_count = raw_col.count() if raw_col else 0
    print(f"counts: ext_authority={ext_count} repo_evidence={repo_count} ext_raw={raw_count}")

    # ext_authority / ext_raw count guard (frozen invariants)
    assert ext_count == EXPECTED_EXT_AUTHORITY, (
        f"ext_authority count drift: expected {EXPECTED_EXT_AUTHORITY}, got {ext_count}"
    )
    assert raw_count == EXPECTED_EXT_RAW, f"ext_raw count drift: expected {EXPECTED_EXT_RAW}, got {raw_count}"

    repo_metas = repo_col.get(include=["metadatas"])["metadatas"]
    assert len(repo_metas) == repo_count

    # G4 — invalid_for_normative_use=True on all repo_evidence chunks
    g4_bad = [m for m in repo_metas if m.get("invalid_for_normative_use") is not True]

    # G5 — no https:// source_url on any repo_evidence chunk
    g5_bad = [m for m in repo_metas if str(m.get("source_url", "")).startswith("https://")]

    # G6 — all 14 required metadata fields present
    g6_bad = [m for m in repo_metas if not REQUIRED_FIELDS.issubset(m.keys())]

    # D7.1-specific: the new advisory note contributed new chunks
    d71_chunks = [
        m
        for m in repo_metas
        if m.get("source_url", "").replace("\\", "/").endswith("docs/architecture/write_governance_note.md")
    ]

    gates = {
        "G4": {
            "pass": not g4_bad,
            "count": len(repo_metas),
            "detail": f"{len(g4_bad)} chunks with invalid_for_normative_use != True",
        },
        "G5": {
            "pass": not g5_bad,
            "count": len(repo_metas),
            "detail": f"{len(g5_bad)} chunks with https:// source_url",
        },
        "G6": {
            "pass": not g6_bad,
            "count": len(repo_metas),
            "detail": f"{len(g6_bad)} chunks missing required fields",
        },
    }

    print("\n===== GATE RESULTS =====")
    for k, v in gates.items():
        status = "PASS" if v["pass"] else "FAIL"
        print(f"  {k}: {status} — {v['detail']} (n={v['count']})")

    print("\n===== D7.1 ADVISORY NOTE CHUNKS =====")
    print(f"  write_governance_note chunks: {len(d71_chunks)}")
    if d71_chunks:
        sample = d71_chunks[0]
        print(
            "  sample metadata: "
            + json.dumps(
                {k: sample.get(k) for k in sorted(REQUIRED_FIELDS)},
                default=str,
            )
        )

    print("\n===== FROZEN INVARIANTS =====")
    print(
        f"  ext_authority count: {ext_count} (expected {EXPECTED_EXT_AUTHORITY}) -> "
        f"{'OK' if ext_count == EXPECTED_EXT_AUTHORITY else 'DRIFT'}"
    )
    print(
        f"  ext_raw count:       {raw_count} (expected {EXPECTED_EXT_RAW}) -> "
        f"{'OK' if raw_count == EXPECTED_EXT_RAW else 'DRIFT'}"
    )

    all_pass = all(g["pass"] for g in gates.values())
    print(f"\nverdict={'PASS' if all_pass else 'FAIL'}")

    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "ext_authority": ext_count,
            "repo_evidence": repo_count,
            "ext_raw": raw_count,
        },
        "gates": gates,
        "d71_advisory_note_chunks": len(d71_chunks),
        "frozen_invariants": {
            "ext_authority_expected": EXPECTED_EXT_AUTHORITY,
            "ext_raw_expected": EXPECTED_EXT_RAW,
        },
        "all_pass": all_pass,
    }
    out_json = REPO_ROOT / "tools" / "debug" / "wave_d71_gates_results.json"
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"results_json={out_json}")


if __name__ == "__main__":
    main()
