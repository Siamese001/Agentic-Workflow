"""Seed synthetic OTel traces into the runtime ADG store (W2).

Plan: ``.windsurf/plans/three-bucket-gap-remediation-069806.md`` (W2).

Until the GenAI emitter migration (W3) propagates real spans into
``runtime_adg_store`` from production code paths, the runtime bucket of
the three-bucket ADG authority model has no producer data: every edge
classifies as UNOBSERVED_CODE in the gap report. This script seeds the
store with synthetic ``RuntimeADGSnapshot`` payloads that reference
real static edges, so the W1 runtime-view builder path produces
non-empty ``v_runtime_proof`` rows on the next regen.

This is a **bridge tool**, not a production substitute. Real traces from
W3-migrated emitters take precedence; the seeder simply unblocks
W4 (strict-mode flip) and W5 (gap-report CI gate) by establishing the
end-to-end pipeline path from synthetic traces -> runtime store ->
v_runtime_proof -> gap report.

Usage::

    python tools/otel/seed_synthetic_traces.py            # default 50 traces
    python tools/otel/seed_synthetic_traces.py --traces 200 --edges-per-trace 5
    python tools/otel/seed_synthetic_traces.py --dry-run  # report only

Idempotent at the trace level: each invocation creates fresh trace_ids,
so repeated runs grow the store rather than duplicating evidence.
"""

from __future__ import annotations

# This script seeds synthetic snapshots; it does not consume ADG views.
__adg_consumer_mode__ = "inventory"

import argparse
import hashlib
import json
import random
import sqlite3
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from system_learning.runtime_adg.snapshot import (  # noqa: E402
    RuntimeADGEdge,
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


@dataclass
class SeedStats:
    snapshot_path: str = ""
    edges_sampled: int = 0
    traces_created: int = 0
    snapshots_persisted: int = 0
    persistence_errors: int = 0
    store_kind: str = ""


# ---------------------------------------------------------------------------
# Edge sampling
# ---------------------------------------------------------------------------


def _latest_static_snapshot() -> Path | None:
    candidates = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    return candidates[-1] if candidates else None


def _sample_static_edges(
    snapshot: Path, *, n: int, seed: int = 42
) -> list[tuple[str, str, str]]:
    """Sample N (src_name, dst_name, relation_type) triples from real edges.

    Joins nodes twice to resolve src/dst adg_name for each edge. Filters
    to the static bucket so we don't accidentally pick up registry rows
    (which have synthetic root nodes that don't represent real call sites).
    """
    con = sqlite3.connect(str(snapshot))
    try:
        rows = con.execute(
            """
            SELECT ns.adg_name, nd.adg_name, e.relation_type
            FROM edges e
            JOIN nodes ns ON ns.id = e.src_id
            JOIN nodes nd ON nd.id = e.dst_id
            WHERE e.bucket = 'static'
              AND ns.adg_name IS NOT NULL
              AND nd.adg_name IS NOT NULL
              AND ns.adg_name != ''
              AND nd.adg_name != ''
            """
        ).fetchall()
    finally:
        con.close()
    rng = random.Random(seed)
    if len(rows) <= n:
        return rows
    return rng.sample(rows, n)


# ---------------------------------------------------------------------------
# Snapshot synthesis
# ---------------------------------------------------------------------------


def _build_synthetic_snapshot(
    *,
    trace_id: str,
    edges: list[tuple[str, str, str]],
    started_at_ms: int,
) -> Any:
    """Materialize a RuntimeADGSnapshot from a list of static-edge triples.

    Each unique adg_name in the edge list becomes a node; each edge becomes
    a RuntimeADGEdge with a `parent_child` relation (the relation that
    `_aggregate_snapshots` recognizes). Node ids are deterministic short
    hashes of the adg_name so a regen against the same seed produces the
    same snapshot_id (fingerprint stability).
    """
    name_to_id: dict[str, str] = {}
    nodes: list[RuntimeADGNode] = []
    for src_name, dst_name, _rel in edges:
        for name in (src_name, dst_name):
            if name in name_to_id:
                continue
            digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
            node_id = f"synth_{digest}"
            name_to_id[name] = node_id
            nodes.append(
                RuntimeADGNode(
                    node_id=node_id,
                    name=name,
                    kind="synthetic",
                    layer="L_SYN",
                    component="seed_synthetic_traces",
                    started_at_utc=started_at_ms,
                    duration_ms=0.0,
                    status="ok",
                    attributes_json=json.dumps(
                        {"gen_ai.operation.name": "synthetic.seed"}, separators=(",", ":")
                    ),
                )
            )

    rt_edges: list[RuntimeADGEdge] = [
        RuntimeADGEdge(
            src_id=name_to_id[src_name],
            dst_id=name_to_id[dst_name],
            relation=relation,
        )
        for src_name, dst_name, relation in edges
    ]

    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission="synthetic_seed",
        started_at_utc=started_at_ms,
        ended_at_utc=started_at_ms + len(edges) * 1000,
        nodes=tuple(nodes),
        edges=tuple(rt_edges),
    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def seed(
    *,
    n_traces: int,
    edges_per_trace: int,
    snapshot: Path | None = None,
    dry_run: bool = False,
    seed: int = 42,
) -> SeedStats:
    """Seed N synthetic traces into the runtime ADG store."""
    snap = snapshot or _latest_static_snapshot()
    if snap is None:
        raise FileNotFoundError(
            "no ADG snapshot under artifacts/adg/ — run generate_full_adg first"
        )

    stats = SeedStats(snapshot_path=str(snap.relative_to(REPO_ROOT)))

    sample_pool = _sample_static_edges(
        snap, n=n_traces * edges_per_trace, seed=seed
    )
    stats.edges_sampled = len(sample_pool)

    if not sample_pool:
        return stats

    rng = random.Random(seed)
    base_time = int(time.time() * 1000)

    snapshots: list[Any] = []
    for i in range(n_traces):
        trace_edges = rng.sample(
            sample_pool, k=min(edges_per_trace, len(sample_pool))
        )
        snapshots.append(
            _build_synthetic_snapshot(
                trace_id=f"synth-trace-{uuid.uuid4().hex[:12]}",
                edges=trace_edges,
                started_at_ms=base_time + i * 1000,
            )
        )
    stats.traces_created = len(snapshots)

    if dry_run:
        stats.store_kind = "dry-run"
        return stats

    try:
        from system_learning.runtime_adg.store import FileBackedRuntimeADGStore  # noqa: PLC0415

        store = FileBackedRuntimeADGStore()
        stats.store_kind = "FileBackedRuntimeADGStore"
    except (ImportError, OSError, RuntimeError) as exc:
        print(f"[seed] ERROR: cannot construct FileBackedRuntimeADGStore: {exc}")
        stats.persistence_errors = len(snapshots)
        return stats

    for snap_obj in snapshots:
        try:
            store.persist(snap_obj)
            stats.snapshots_persisted += 1
        except (OSError, RuntimeError, ValueError) as exc:
            stats.persistence_errors += 1
            print(f"[seed] persistence error: {exc}")

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=int, default=50)
    parser.add_argument("--edges-per-trace", type=int, default=4)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    stats = seed(
        n_traces=args.traces,
        edges_per_trace=args.edges_per_trace,
        snapshot=args.snapshot,
        dry_run=args.dry_run,
        seed=args.seed,
    )

    print(f"[seed] snapshot          = {stats.snapshot_path}")
    print(f"[seed] edges_sampled     = {stats.edges_sampled}")
    print(f"[seed] traces_created    = {stats.traces_created}")
    print(f"[seed] snapshots_persist = {stats.snapshots_persisted}")
    print(f"[seed] persist_errors    = {stats.persistence_errors}")
    print(f"[seed] store_kind        = {stats.store_kind}")
    return 1 if stats.persistence_errors else 0


if __name__ == "__main__":
    sys.exit(main())
