"""apps_rg ``bootstrap fact-vectors`` — build the C0.2 fact_vectors collection from tracked sources.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W3; gaps G2-build, G3, G10, G14).

Source = the canonical **candidate fact ledger** (tracked, checked-in) — NEVER the base resume.
Each eligible HIGH / proof-eligible ledger fact becomes one embeddable atom, assigned to the resume
lanes it can enrich, embedded with BGE-M3, and upserted **idempotently** (stable chunk ids) into the
Chroma ``fact_vectors`` collection. A manifest + checksum is emitted as the pre-run index receipt.

``--strict`` fails loud (non-zero) when the build produces no eligible atoms or leaves the collection
empty — a fresh checkout must be able to detect a failed bootstrap, not silently proceed.

EY / InsurTech lanes are **locked-deterministic** per the constitutional floor ("InsurTech, EY ...
stays deterministic"); they are intentionally NOT generated from fact_vectors and carry no atoms here
(the manifest records them as locked). Invoked via ``python -m apps_rg bootstrap fact-vectors``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.cli_exit_codes import EXIT_CONFIG_ERROR, EXIT_GENERIC_FAILURE, EXIT_SUCCESS

# Generated resume lanes that draw dense enrichment from fact_vectors (employer bullets + narratives
# for the confirmed-wired employers + cross-section). EY/InsurTech are excluded by design (locked).
GENERATED_LANES: tuple[str, ...] = (
    "competencies",
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)
# Any HIGH fact can enrich these cross-section lanes.
CROSS_SECTION_TARGETS: tuple[str, ...] = ("competencies", "headline", "executive_summary")
# Locked-deterministic per constitutional floor — never generated from fact_vectors.
LOCKED_DETERMINISTIC_LANES: tuple[str, ...] = (
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
)

MANIFEST_REL = "artifacts/apps_rg/c0/fact_vectors_bootstrap_manifest.json"


def _repo_root() -> Path:
    # apps_rg/runtime/fact_vectors_bootstrap.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def _employer_sections(company: str) -> list[str]:
    c = (company or "").strip().lower()
    if "ibm" in c:
        return ["ibm_bullets", "ibm_narrative"]
    if c and ("unify" in c or "current" in c or "platform" in c):
        return ["unify_bullets", "unify_narrative"]
    return []


def assign_sections_for_fact(row: dict[str, Any]) -> list[str]:
    """Generated lanes a HIGH ledger fact can meaningfully enrich (generous union, recall only)."""
    sections: set[str] = set(CROSS_SECTION_TARGETS)
    sections.update(_employer_sections(str(row.get("company") or "")))
    role_families = {str(r).upper() for r in (row.get("role_families_supported") or [])}
    if {"ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE", "PRODUCT_TECHNICAL_STRATEGY"} & role_families:
        sections.update({"unify_bullets", "unify_narrative"})
    return sorted(s for s in sections if s in GENERATED_LANES)


def build_section_atoms(*, repo_root: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build one atom per eligible ledger fact (tracked source), tagged with generated-lane targets."""
    from apps_rg.fact_inventory.candidate_fact_ledger import (
        default_ledger_path,
        load_master_candidate_fact_ledger,
    )
    from apps_rg.runtime.c0.c02_evidence_fetch import _atom_from_ledger_row
    from apps_rg.runtime.c0.c02_fact_vector_ingest import c02_atom_ingest_eligible

    root = repo_root or _repo_root()
    ledger = load_master_candidate_fact_ledger(repo_root=root, path=default_ledger_path(root))
    facts = [r for r in (ledger.get("candidate_facts") or []) if isinstance(r, dict)]
    atoms: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()
    skipped: list[dict[str, str]] = []
    for row in facts:
        atom = _atom_from_ledger_row(row, section_id="competencies")
        atom["allowed_sections"] = assign_sections_for_fact(row)
        ok, reason = c02_atom_ingest_eligible(atom)
        if not ok:
            skipped.append({"fact_id": atom["fact_id"], "reason": reason})
            continue
        atoms.append(atom)
        for section in atom["allowed_sections"]:
            section_counts[section] += 1
    # Every generated lane appears in the manifest (0 where no fact supports it) for auditability.
    per_section = {lane: int(section_counts.get(lane, 0)) for lane in GENERATED_LANES}
    summary = {
        "ledger_path": default_ledger_path(root).as_posix(),
        "total_ledger_facts": len(facts),
        "eligible_atoms": len(atoms),
        "skipped_count": len(skipped),
        "skipped": skipped[:50],
        "per_section_target_counts": per_section,
    }
    return atoms, summary


def _reset_collection(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        existing = client.get_collection(collection_name)
        count = int(existing.count())
    except Exception:  # guardian: allow-broad-exception -- collection may not exist yet; nothing to reset
        return 0
    client.delete_collection(collection_name)
    return count


def _build_sparse_sidecar(chroma_path: str, manifest: dict[str, Any]) -> None:
    """G22: build the FTS5/BM25 sparse sidecar so the mandatory C0.2 sparse lane is available.

    Reads the just-upserted fact_vectors collection and writes data/cache/sparse/fact_vectors.db
    (read by agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index). Best-effort; the
    outcome is recorded in the manifest so --strict can gate on it.
    """
    try:
        from tools.generate.ingestion import build_sparse_index as sparse_builder

        sparse_builder.CHROMA_PATH = Path(chroma_path)
        stats = sparse_builder.build_for_collection("fact_vectors")
        from agentic_core.L4_state.utils.memory.bm25_store import sparse_sidecar_exists

        manifest["sparse_sidecar_built"] = bool(sparse_sidecar_exists("fact_vectors"))
        manifest["sparse_doc_count"] = int(stats.get("doc_count") or 0)
        manifest["sparse_term_count"] = int(stats.get("term_count") or 0)
    except Exception as exc:  # guardian: allow-broad-exception -- sparse build is best-effort; recorded in manifest for strict gating
        manifest["sparse_sidecar_built"] = False
        manifest["sparse_sidecar_error"] = f"{type(exc).__name__}: {exc}"


def _collection_count(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        return int(client.get_collection(collection_name).count())
    except Exception:  # guardian: allow-broad-exception -- absent collection reports 0
        return 0


def _sha256_json(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _write_manifest(repo_root: Path, manifest: dict[str, Any]) -> Path:
    path = repo_root / MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_bootstrap_fact_vectors(
    *,
    strict: bool,
    reset: bool = False,
    dry_run: bool = False,
    chroma_path: str | None = None,
    repo_root: Path | None = None,
    timestamp: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Build + upsert fact_vectors from the candidate fact ledger; return (manifest, exit_code)."""
    root = repo_root or _repo_root()
    from apps_rg.runtime.c0.c02_fact_vector_ingest import (
        _ledger_version_hash,
        atoms_to_fact_vector_chunks,
        upsert_fact_vector_chunks,
    )
    from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env

    resolved = (
        (chroma_path or "").strip()
        or os.environ.get("CHROMA_PERSIST_DIR", "").strip()
        or str(root / "data" / "cache" / "chromadb")
    )
    os.environ.setdefault("CHROMA_PERSIST_DIR", resolved)
    bootstrap_apps_rg_embedding_env(repo_root=root)
    chroma = os.environ.get("CHROMA_PERSIST_DIR", resolved)

    atoms, summary = build_section_atoms(repo_root=root)
    manifest: dict[str, Any] = {
        "schema_version": "apps_rg.fact_vectors_bootstrap_manifest.v1",
        "plan": "apps-rg-e2e-gap-remediation-7e2d9c",
        "generated_at_utc": timestamp or datetime.now(timezone.utc).isoformat(),
        "source": "candidate_fact_ledger (tracked); base resume is NOT a source (G14)",
        "chroma_path": chroma,
        "dry_run": bool(dry_run),
        "ledger_version_hash": _ledger_version_hash(root),
        "locked_deterministic_lanes": list(LOCKED_DETERMINISTIC_LANES),
        **summary,
        "chunks_built": 0,
        "upserted_count": 0,
        "collection_count_after": None,
        "sparse_sidecar_built": False,
    }

    if not dry_run:
        if reset:
            manifest["reset_deleted_count"] = _reset_collection(chroma)
        ledger_hash = _ledger_version_hash(root)
        chunks, chunk_atoms, chunk_skipped = atoms_to_fact_vector_chunks(
            atoms, section_id="competencies", ledger_version_hash=ledger_hash
        )
        upserted = upsert_fact_vector_chunks(chunks, chroma_path=chroma, atoms=chunk_atoms)
        manifest["chunks_built"] = len(chunks)
        manifest["chunk_skipped"] = chunk_skipped[:50]
        manifest["upserted_count"] = upserted
        manifest["collection_count_after"] = _collection_count(chroma)
        # G22 (W6): the C0.2 sparse lane is independently mandatory — build its FTS5/BM25 sidecar
        # from the same fact_vectors collection so generated lanes are not blocked on sparse.
        _build_sparse_sidecar(chroma, manifest)

    manifest["manifest_checksum"] = _sha256_json(
        {k: v for k, v in manifest.items() if k != "manifest_checksum"}
    )
    manifest["manifest_path"] = _write_manifest(root, manifest).as_posix()

    exit_code = EXIT_SUCCESS
    if strict:
        if int(summary.get("eligible_atoms") or 0) == 0:
            exit_code = EXIT_GENERIC_FAILURE
        elif not dry_run and int(manifest.get("collection_count_after") or 0) <= 0:
            exit_code = EXIT_GENERIC_FAILURE
        elif not dry_run and not manifest.get("sparse_sidecar_built"):
            exit_code = EXIT_GENERIC_FAILURE
    return manifest, exit_code


def run_bootstrap_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m apps_rg bootstrap",
        description="Build apps_rg C0.2 retrieval state from tracked sources (plan apps-rg-e2e-gap-remediation-7e2d9c).",
    )
    parser.add_argument(
        "resource",
        choices=["fact-vectors"],
        help="What to bootstrap (currently: fact-vectors).",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on an empty/unpopulated build.")
    parser.add_argument("--reset", action="store_true", help="Delete the collection before ingest.")
    parser.add_argument("--dry-run", action="store_true", help="Build + report atoms without writing to Chroma.")
    parser.add_argument("--chroma-path", default=None, help="Override CHROMA_PERSIST_DIR for this build.")
    namespace = parser.parse_args(argv)

    manifest, exit_code = run_bootstrap_fact_vectors(
        strict=namespace.strict,
        reset=namespace.reset,
        dry_run=namespace.dry_run,
        chroma_path=namespace.chroma_path,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False), flush=True)
    if namespace.strict and exit_code != EXIT_SUCCESS:
        print(
            "BOOTSTRAP FAILED (strict): no eligible atoms or empty collection after upsert. "
            "Check the candidate fact ledger and EMBEDDING_ENABLED / BGE model path.",
            flush=True,
        )
    return exit_code


__all__ = [
    "GENERATED_LANES",
    "LOCKED_DETERMINISTIC_LANES",
    "assign_sections_for_fact",
    "build_section_atoms",
    "run_bootstrap_cli",
    "run_bootstrap_fact_vectors",
]
