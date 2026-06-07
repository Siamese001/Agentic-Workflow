"""Build + ingest meaningful per-section fact vectors into the Chroma ``fact_vectors`` collection.

PURPOSE
-------
C0.2 dense retrieval reads the ``fact_vectors`` Chroma collection as NON-AUTHORITATIVE
enrichment on top of the authoritative ledger/graph proof pool. Historically that collection
held only ~25 smoke/operator-seeded docs, so dense enrichment was thin and often fell back to
SMOKE_* anchors. This tool walks the canonical candidate-fact ledger, assigns each fact to the
resume sections it can meaningfully support, and upserts one embeddable chunk per fact
(BGE-M3) into ``fact_vectors`` with a generous ``section_targets`` tag.

BOUNDARY
--------
- Chroma ``fact_vectors`` is enrichment ONLY. This tool does NOT change proof authority
  (ledger + graph + proof pool remain the X2 proof substrate). It improves recall.
- Only HIGH-confidence / proof-eligible facts are embedded (matches
  ``c02_atom_ingest_eligible``): MEDIUM/LOW/NEEDS_VERIFICATION facts are skipped so the dense
  lane never surfaces non-promotable claims as if they were proof.
- Reuses the proven runtime path (``_atom_from_ledger_row`` →
  ``atoms_to_fact_vector_chunks`` → ``upsert_fact_vector_chunks``). Chunk ids are stable
  (``apps_rg:fv:{fact_id}``) so re-running is idempotent.

SECTION ASSIGNMENT
------------------
Facts carry ``company`` + ``role_families_supported`` but no explicit section eligibility. We
map to sections heuristically so each fact lands where it can plausibly enrich:
  - employer facts -> that employer's bullets + narrative (IBM -> ibm_bullets/ibm_narrative;
    Unify/current -> unify_bullets/unify_narrative)
  - every HIGH fact -> competencies + headline + executive_summary (cross-section enrichment)
Authority still gates which facts actually appear in output; this only widens dense recall.

USAGE
-----
    python tools/apps_rg/build_section_fact_vectors.py            # dry run (no writes)
    python tools/apps_rg/build_section_fact_vectors.py --execute  # embed + upsert
    python tools/apps_rg/build_section_fact_vectors.py --execute --reset  # rebuild from scratch
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.fact_inventory.candidate_fact_ledger import (  # noqa: E402
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.runtime.c0.c02_evidence_fetch import _atom_from_ledger_row  # noqa: E402
from apps_rg.runtime.c0.c02_fact_vector_ingest import (  # noqa: E402
    atoms_to_fact_vector_chunks,
    c02_atom_ingest_eligible,
    upsert_fact_vector_chunks,
)

# Seven C0-enabled resume sections (SSOT order in generated_lane_rollup).
ALL_SECTIONS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "unify_narrative",
    "ibm_narrative",
    "executive_summary",
    "headline",
)

# Cross-section enrichment sections: any HIGH fact can support these.
CROSS_SECTION_TARGETS: tuple[str, ...] = (
    "competencies",
    "headline",
    "executive_summary",
)


def _employer_sections(company: str) -> list[str]:
    c = (company or "").strip().lower()
    if "ibm" in c:
        return ["ibm_bullets", "ibm_narrative"]
    # Unify / current-role / platform employer facts feed the Unify lanes.
    if c and ("unify" in c or "current" in c or "platform" in c):
        return ["unify_bullets", "unify_narrative"]
    return []


def assign_sections_for_fact(row: dict[str, Any]) -> list[str]:
    """Sections this HIGH ledger fact can meaningfully enrich (generous union)."""
    sections: set[str] = set(CROSS_SECTION_TARGETS)
    sections.update(_employer_sections(str(row.get("company") or "")))
    # If no employer match, still allow both employer narratives' bullets via role family so
    # platform/engineering facts enrich the current-role lanes (enrichment only).
    rf = {str(r).upper() for r in (row.get("role_families_supported") or [])}
    if {"ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE", "PRODUCT_TECHNICAL_STRATEGY"} & rf:
        sections.update({"unify_bullets", "unify_narrative"})
    return sorted(s for s in sections if s in ALL_SECTIONS)


def build_section_atoms(
    *,
    repo_root: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build one atom per eligible HIGH ledger fact, tagged with multi-section targets."""
    root = repo_root or REPO_ROOT
    ledger = load_master_candidate_fact_ledger(repo_root=root, path=default_ledger_path(root))
    facts = [r for r in (ledger.get("candidate_facts") or []) if isinstance(r, dict)]
    atoms: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()
    skipped: list[dict[str, str]] = []
    for row in facts:
        # Build the atom via the canonical runtime mapping (proof_status derived from confidence).
        atom = _atom_from_ledger_row(row, section_id="competencies")
        targets = assign_sections_for_fact(row)
        atom["allowed_sections"] = targets
        ok, reason = c02_atom_ingest_eligible(atom)
        if not ok:
            skipped.append({"fact_id": atom["fact_id"], "reason": reason})
            continue
        atoms.append(atom)
        for s in targets:
            section_counts[s] += 1
    summary = {
        "ledger_path": default_ledger_path(root).as_posix(),
        "total_ledger_facts": len(facts),
        "eligible_atoms": len(atoms),
        "skipped_count": len(skipped),
        "skipped": skipped[:50],
        "per_section_target_counts": dict(sorted(section_counts.items())),
    }
    return atoms, summary


def _reset_collection(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        existing = client.get_collection(collection_name)
        n = existing.count()
    except Exception:  # noqa: BLE001 - collection may not exist yet
        return 0
    client.delete_collection(collection_name)
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build per-section fact_vectors for C0 enrichment.")
    ap.add_argument("--execute", action="store_true", help="Embed + upsert (default: dry run).")
    ap.add_argument("--reset", action="store_true", help="Delete the collection before ingest.")
    ap.add_argument(
        "--chroma-path",
        default=os.environ.get("CHROMA_PERSIST_DIR", "")
        or str(REPO_ROOT / "data" / "cache" / "chromadb"),
    )
    args = ap.parse_args(argv)

    # Ensure embedding env (CHROMA dir, BGE path) is bootstrapped for the dense ingest.
    from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env

    os.environ.setdefault("CHROMA_PERSIST_DIR", args.chroma_path)
    bootstrap_apps_rg_embedding_env(repo_root=REPO_ROOT)
    chroma_path = os.environ.get("CHROMA_PERSIST_DIR", args.chroma_path)

    atoms, summary = build_section_atoms()
    summary["chroma_path"] = chroma_path
    summary["execute"] = bool(args.execute)

    if args.execute and args.reset:
        summary["reset_deleted_count"] = _reset_collection(chroma_path)

    if args.execute:
        # Group atoms by section so each chunk carries its section_type while
        # section_targets keeps the full union (upsert is idempotent on fact_id).
        chunks, chunk_atoms, chunk_skipped = atoms_to_fact_vector_chunks(
            atoms,
            section_id="competencies",  # primary section_type; section_targets holds the union
        )
        upserted = upsert_fact_vector_chunks(
            chunks,
            chroma_path=chroma_path,
            atoms=chunk_atoms,
        )
        summary["chunks_built"] = len(chunks)
        summary["chunk_skipped"] = chunk_skipped[:50]
        summary["upserted_count"] = upserted

        import chromadb

        client = chromadb.PersistentClient(path=chroma_path)
        try:
            summary["collection_count_after"] = client.get_collection("fact_vectors").count()
        except Exception:  # noqa: BLE001
            summary["collection_count_after"] = None

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
