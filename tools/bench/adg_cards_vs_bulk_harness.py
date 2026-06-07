#!/usr/bin/env python3
"""Benchmark harness stub: ADG semantic cards vs `repo_adg_graph` bulk edges.

PURPOSE
-------
Document and scaffold the retrieval benchmark that must run before the
``repo_adg_graph`` bulk-edge collection is retired. This is the L4 deferred
scope item from Wave E (``docs/archive/windsurf/legacy-tree/plans/wave-e-adg-card-projection-2df148.md``).

This file is a **harness**, not a completed benchmark. Running it without
real ingested data produces an explicit ``benchmark_not_runnable`` status so
nothing silently claims the retirement decision has been made.

METHODOLOGY (to be implemented when Chroma has both collections populated)
-------------------------------------------------------------------------
1. Build a query set of at least 20 representative retrieval prompts that
   exercise structural, semantic, and layer-aware queries (constitutional §22
   graph-layer primaries should drive selection — see
   ``docs/reference/_primers/AST Dependency Graphs (ADG)/`` for concrete prompt
   archetypes).
2. For each query run:
   a. Baseline: retrieve K=10 from ``repo_adg_graph`` (bulk edges).
   b. Candidate: retrieve K=10 from the four card collections
      (``adg_symbol_cards``, ``adg_hotspot_cards``, ``adg_violation_cards``,
      ``adg_path_cards``) fused via RRF.
3. Metrics:
   - Precision@5 vs a hand-labelled relevance set.
   - MRR over the full K=10 result list.
   - Token cost per query (chunk sizes differ dramatically — edges are tiny,
     cards carry narrative context).
   - p95 latency.
4. Retirement decision rule: retire ``repo_adg_graph`` iff cards beat bulk
   edges on Precision@5 by ≥0.10 AND token cost per query is ≤1.3× AND p95
   latency is within 1.5× of bulk. Any single fail → benchmark inconclusive.

RUNNABLE SURFACE
----------------
The ``check_prerequisites`` function below verifies whether a real benchmark
can run today. It does NOT execute retrieval — that wiring belongs to a
future Wave once both collections are populated and the query corpus is
labeled.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "artifacts" / "chromadb"


@dataclass(frozen=True)
class Prereq:
    """One prerequisite check. ``ok=True`` means the benchmark can proceed."""

    name: str
    ok: bool
    detail: str


def check_prerequisites() -> list[Prereq]:
    """Return the full list of prerequisite checks."""

    results: list[Prereq] = []

    # 1. ChromaDB persist dir exists.
    results.append(
        Prereq(
            name="chromadb_persist_dir",
            ok=CHROMA_DIR.exists(),
            detail=f"expected {CHROMA_DIR}",
        )
    )

    # 2. Card collections present (names only — populating them is out of
    # scope for the harness; we only verify the schema exists).
    card_collections = (
        "adg_symbol_cards",
        "adg_hotspot_cards",
        "adg_violation_cards",
        "adg_path_cards",
    )
    try:
        import chromadb  # type: ignore[import-not-found]

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        existing = {c.name for c in client.list_collections()}
    except ImportError:
        existing = set()
        results.append(
            Prereq(
                name="chromadb_importable",
                ok=False,
                detail="chromadb not installed",
            )
        )
    except (RuntimeError, ValueError, OSError) as exc:
        existing = set()
        results.append(
            Prereq(
                name="chromadb_client",
                ok=False,
                detail=f"client init failed: {exc!r}",
            )
        )
    else:
        results.append(Prereq(name="chromadb_importable", ok=True, detail=""))

    for name in card_collections:
        results.append(
            Prereq(
                name=f"collection:{name}",
                ok=name in existing,
                detail=("present" if name in existing else "missing — run project_adg_cards"),
            )
        )
    results.append(
        Prereq(
            name="collection:repo_adg_graph",
            ok="repo_adg_graph" in existing,
            detail=(
                "present — retirement candidate"
                if "repo_adg_graph" in existing
                else "already absent — nothing to retire"
            ),
        )
    )

    # 3. Labeled query corpus (the harness expects a JSONL file at the
    # canonical path; absence means no benchmark can run).
    query_corpus = REPO_ROOT / "tests" / "fixtures" / "retrieval_benchmark_queries.jsonl"
    results.append(
        Prereq(
            name="labeled_query_corpus",
            ok=query_corpus.exists(),
            detail=str(query_corpus.relative_to(REPO_ROOT))
            + (" — present" if query_corpus.exists() else " — MISSING (blocker)"),
        )
    )

    return results


def main() -> int:
    print("ADG Cards vs repo_adg_graph — benchmark prerequisites")
    print("=" * 60)
    prereqs = check_prerequisites()
    all_ok = all(p.ok for p in prereqs)
    for p in prereqs:
        status = "[OK]  " if p.ok else "[FAIL]"
        print(f"{status} {p.name}: {p.detail}")

    print()
    if all_ok:
        print("STATUS: benchmark_runnable (all prerequisites met)")
        print("NEXT:   implement retrieval + scoring + decision rule per module docstring.")
        return 0

    blockers = [p.name for p in prereqs if not p.ok]
    report = {
        "status": "benchmark_not_runnable",
        "blockers": blockers,
        "retirement_decision": "DEFERRED — prerequisites incomplete",
        "rule": "wave-e-adg-card-projection-2df148 (L4 deferred scope item)",
    }
    print("STATUS: benchmark_not_runnable")
    print(json.dumps(report, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
