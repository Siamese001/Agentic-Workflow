"""ADG Pipeline Profiler v5 — Patch C: artifact path instrumentation.

Measures:
  - Top-level single-source pipeline stopwatch (scan → build → write → plumbing)
  - build_artifact sub-stages (populate_relations, module_entities, symbol_entities,
    identity_health, structural_metrics, blind_spots, digest)
  - write_all_artifacts sub-spans (snapshot_build, snapshot_write, normalizer,
    sqlite_ddl, sqlite_nodes, sqlite_edges, sqlite_violations, sqlite_commit,
    split_planes, json_writes)

Usage:
    python tools/profile_adg_phases_v5.py          # warm-path, writes artifacts to tmp dir
    python tools/profile_adg_phases_v5.py --no-write  # skip actual file writes
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sqlite3
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore[import]
    _PROC = psutil.Process()
    def _rss_mb() -> float:
        return _PROC.memory_info().rss / 1024 / 1024
except ImportError:
    def _rss_mb() -> float:
        return 0.0

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Minimal timer context
# ---------------------------------------------------------------------------

@dataclass
class PhaseResult:
    name: str
    wall: float
    cpu: float
    rss_delta_mb: float
    gc_gen0: int
    gc_gen1: int
    extra: dict

    def display(self, indent: int = 0) -> str:
        pad = " " * indent
        extra_str = "  " + "  ".join(f"{k}={v}" for k, v in self.extra.items()) if self.extra else ""
        return (
            f"{pad}[{self.name:<42}] wall={self.wall:6.3f}s  cpu={self.cpu:6.3f}s"
            f"  rss={self.rss_delta_mb:+5.0f}MB  gc=[{self.gc_gen0},{self.gc_gen1}]"
            f"{extra_str}"
        )


class _Timer:
    def __init__(self, name: str) -> None:
        self.name = name
        self._wall0 = self._cpu0 = self._rss0 = 0.0
        self._gc0: list[dict] = []
        self.result: PhaseResult | None = None

    def __enter__(self) -> "_Timer":
        gc.collect()
        self._gc0 = gc.get_stats()
        self._wall0 = time.perf_counter()
        self._cpu0 = time.process_time()
        self._rss0 = _rss_mb()
        return self

    def __exit__(self, *_: Any) -> None:
        wall = time.perf_counter() - self._wall0
        cpu = time.process_time() - self._cpu0
        rss = _rss_mb() - self._rss0
        gc1 = gc.get_stats()
        dg0 = gc1[0]["collections"] - self._gc0[0]["collections"]
        dg1 = gc1[1]["collections"] - self._gc0[1]["collections"]
        self.result = PhaseResult(self.name, wall, cpu, rss, dg0, dg1, {})


def _phase(name: str) -> _Timer:
    return _Timer(name)


# ---------------------------------------------------------------------------
# Instrumented build_artifact
# ---------------------------------------------------------------------------

def _build_artifact_instrumented(result: Any, repo_root: Path) -> tuple[Any, list[PhaseResult]]:
    """Run ADGArtifactBuilder.build() with per-stage timing."""
    from agentic_core.adg.artifact.builder_types import (
        ADGArtifact,
        ADGArtifactBuilder,
    )

    builder = ADGArtifactBuilder(repo_root=repo_root)
    phases: list[PhaseResult] = []

    artifact = ADGArtifact(
        commit_sha=result.commit_sha or "",
        repo_state_hash=result.repo_state_hash or "",
        scanner_digest=result.digest or "",
        type_surface_map=getattr(result, "type_surface_map", {}),
        hollow_file_map=getattr(result, "hollow_file_map", {}),
        boilerplate_ratio_map=getattr(result, "boilerplate_ratio_map", {}),
    )

    stages = [
        ("BA1_populate_relations",   builder._populate_relations),
        ("BA2_module_entities",      builder._populate_module_entities),
        ("BA3_symbol_entities",      builder._populate_symbol_entities),
        ("BA4_identity_health",      builder._build_identity_health),
        ("BA5_structural_metrics",   builder._compute_structural_metrics),
        ("BA6_blind_spots",          builder._collect_blind_spots),
    ]

    for stage_name, fn in stages:
        with _phase(stage_name) as t:
            # Some methods take (result, artifact), others take (artifact,)
            try:
                fn(result, artifact)  # type: ignore[call-arg]
            except TypeError:
                fn(artifact)  # type: ignore[call-arg]
        assert t.result is not None
        phases.append(t.result)

    with _phase("BA7_artifact_digest") as t:
        artifact.compute_digest()
    assert t.result is not None
    phases.append(t.result)

    return artifact, phases


# ---------------------------------------------------------------------------
# Instrumented write_all_artifacts
# ---------------------------------------------------------------------------

def _write_all_instrumented(artifact: Any, out_dir: Path) -> list[PhaseResult]:
    """Run write_all_artifacts with per-sub-span timing."""
    import json as _json

    from agentic_core.adg.artifact.ArtifactPaths import (
        _build_snapshot,
    )
    from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer
    from agentic_core.adg.artifact.SplitArtifact import split_artifact

    phases: list[PhaseResult] = []
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- W1: Build snapshot dict ---
    with _phase("W1_snapshot_build") as t:
        snap_dict = _build_snapshot(artifact)
    assert t.result is not None
    phases.append(t.result)

    # --- W2: Write snapshot JSON to disk ---
    snap_path = out_dir / "adg_snapshot_v5probe.json"
    with _phase("W2_snapshot_write") as t:
        snap_bytes = _json.dumps(snap_dict, sort_keys=True, indent=2).encode("utf-8")
        snap_path.write_bytes(snap_bytes)
    assert t.result is not None
    t.result.extra["bytes"] = f"{len(snap_bytes):,}"
    phases.append(t.result)

    # --- W3: ArtifactNormalizer.normalize (projection to compact form) ---
    with _phase("W3_normalizer") as t:
        normalizer = ArtifactNormalizer()
        ng_full = normalizer.normalize(artifact)
    assert t.result is not None
    t.result.extra["nodes"] = str(len(ng_full.nodes))
    t.result.extra["edges"] = str(len(ng_full.edges))
    phases.append(t.result)

    # --- W4–W8: SQLite sub-spans ---
    db_path = out_dir / "adg_indexed_v5probe.sqlite"
    if db_path.exists():
        db_path.unlink()

    from agentic_core.adg.artifact.ArtifactPaths import _DDL  # type: ignore[attr-defined]

    conn = sqlite3.connect(str(db_path))
    try:
        with _phase("W4_sqlite_ddl") as t:
            conn.executescript(_DDL)
        assert t.result is not None
        phases.append(t.result)

        # Node rows
        node_rows = []
        for nid_str, node in ng_full.nodes.items():
            node_rows.append((
                int(nid_str),
                node.get("n", ""), node.get("t", ""), node.get("l", ""),
                node.get("k", ""), node.get("c", ""), node.get("p", ""),
                node.get("pt", "symbol"),
                node.get("ss", 0), node.get("se", 0), node.get("sl", 0), node.get("sc", 0),
                node.get("sel", 0), node.get("sec", 0),
                node.get("lsid", 0), node.get("cpid", ""), node.get("to", 0),
                node.get("ts", ""), node.get("es", ""),
            ))
        with _phase("W5_sqlite_nodes") as t:
            conn.executemany(
                "INSERT OR REPLACE INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path,"
                "precision_type,span_start,span_end,span_line,span_column,span_end_line,span_end_column,"
                "logical_sequence_id,control_path_id,temporal_order,type_surface,enclosing_symbol) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                node_rows,
            )
        assert t.result is not None
        t.result.extra["rows"] = str(len(node_rows))
        phases.append(t.result)

        # Edge rows
        edge_rows = []
        for e in ng_full.edges:
            edge_rows.append((
                e["s"], e["d"], e["r"], e["k"], e["f"], e["ln"],
                e.get("sym", ""), e.get("st", ""), e.get("conf", 1.0),
                e.get("sss", 0), e.get("sse", 0), e.get("ssl", 0), e.get("ssc", 0),
                e.get("tss", 0), e.get("tse", 0), e.get("tsl", 0), e.get("tsc", 0),
                e.get("dr", ""),
            ))
        with _phase("W6_sqlite_edges") as t:
            conn.executemany(
                "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol,"
                "semantic_type,confidence_score,source_span_start,source_span_end,source_span_line,source_span_column,"
                "target_span_start,target_span_end,target_span_line,target_span_column,dynamic_resolution) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                edge_rows,
            )
        assert t.result is not None
        t.result.extra["rows"] = str(len(edge_rows))
        phases.append(t.result)

        with _phase("W7_sqlite_violations") as t:
            conn.execute(
                """INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                SELECT id, relation_type, symbol, source_file, line_no,
                    CASE WHEN relation_type = 'antipattern' AND (
                        symbol LIKE 'except:Exception%' OR symbol LIKE 'except:bare%'
                    ) AND (
                        source_file LIKE 'agentic_core/L0_routing/%' OR
                        source_file LIKE 'agentic_core/L5_safety/%' OR
                        source_file LIKE 'agentic_core/L2_execution/%' OR
                        source_file LIKE 'agentic_core/L3_orchestration/%'
                    ) THEN 'HIGH'
                    WHEN relation_type = 'antipattern' AND (
                        symbol LIKE 'except:Exception%' OR symbol LIKE 'except:bare%'
                    ) THEN 'MEDIUM'
                    WHEN relation_type = 'antipattern' THEN 'LOW'
                    ELSE 'MEDIUM'
                    END as severity
                FROM edges WHERE relation_type IN ('violates', 'antipattern', 'dynamic_exec')""",
            )
        assert t.result is not None
        phases.append(t.result)

        meta_rows = [
            ("schema_version", ng_full.schema_version),
            ("commit_sha", ng_full.commit_sha),
            ("repo_state_hash", ng_full.repo_state_hash),
            ("scanner_digest", ng_full.scanner_digest),
            ("artifact_digest", ng_full.artifact_digest),
            ("total_nodes", str(len(ng_full.nodes))),
            ("total_edges", str(len(ng_full.edges))),
        ]
        conn.executemany("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", meta_rows)

        with _phase("W8_sqlite_commit") as t:
            conn.commit()
        assert t.result is not None
        sz_mb = db_path.stat().st_size / 1024 / 1024 if db_path.exists() else 0
        t.result.extra["size_mb"] = f"{sz_mb:.1f}"
        phases.append(t.result)
    finally:
        conn.close()

    # --- W9: split_artifact (projects into 3 planes) ---
    with _phase("W9_split_planes") as t:
        planes = split_artifact(artifact)
    assert t.result is not None
    phases.append(t.result)

    # --- W10–W12: JSON serialization + write for each plane ---
    plane_specs = [
        ("W10_file_graph_write",     out_dir / "adg_file_graph_v5probe.json",     planes.file_graph),
        ("W11_symbol_graph_write",   out_dir / "adg_symbol_graph_v5probe.json",   planes.symbol_graph),
        ("W12_governance_graph_write", out_dir / "adg_governance_graph_v5probe.json", planes.governance_graph),
    ]
    for pname, ppath, plane in plane_specs:
        with _phase(pname) as t:
            plane.write(ppath, indent=None)
        assert t.result is not None
        sz = ppath.stat().st_size if ppath.exists() else 0
        t.result.extra["size_mb"] = f"{sz / 1024 / 1024:.1f}"
        phases.append(t.result)

    return phases


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true", help="Skip actual file writes (build only)")
    args = parser.parse_args()

    os.environ.setdefault("ADG_SKIP_SELF_TEST", "1")

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
    if not cache_path.exists():
        print(f"ERROR: warm cache not found at {cache_path}")
        print("Run `python tools/generate_full_adg.py` once first to populate the cache.")
        sys.exit(1)

    print("=" * 80)
    print("ADG Pipeline Profiler v5 — Artifact Path Instrumentation")
    print(f"pid={os.getpid()}  cache={cache_path.stat().st_size // 1024 // 1024}MB")
    print(f"no_write={args.no_write}")
    print("=" * 80)

    # ---- Phase P1: scanner.scan() (warm, uses cache) ----
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    scanner = ADGStaticScanner(
        repo_root=ROOT,
        include_tests=True,
        cache_path=cache_path,
    )

    t_pipeline_start = time.perf_counter()

    with _phase("P_scan") as t_scan:
        result = scanner.scan()
    assert t_scan.result is not None
    t_scan.result.extra["edges"] = str(len(result.edges))
    t_scan.result.extra["digest"] = result.digest[:16] + "..."

    print(t_scan.result.display())
    print()

    # ---- Phase P2: build_artifact sub-stages ----
    print("  === build_artifact sub-stages ===")
    artifact, build_phases = _build_artifact_instrumented(result, ROOT)
    build_total = sum(p.wall for p in build_phases)
    for p in build_phases:
        print(p.display(indent=2))
    print(f"  build_artifact TOTAL: {build_total:.3f}s")
    print()

    # ---- Phase P3: write_all_artifacts sub-spans ----
    if not args.no_write:
        print("  === write_all_artifacts sub-spans ===")
        with tempfile.TemporaryDirectory(prefix="adg_v5_probe_") as tmpdir:
            write_phases = _write_all_instrumented(artifact, Path(tmpdir))
        write_total = sum(p.wall for p in write_phases)
        for p in write_phases:
            print(p.display(indent=2))
        print(f"  write_all_artifacts TOTAL: {write_total:.3f}s")
        print()
    else:
        write_phases = []
        write_total = 0.0
        print("  [write_all_artifacts skipped — use without --no-write to measure]")
        print()

    t_pipeline_end = time.perf_counter()
    pipeline_wall = t_pipeline_end - t_pipeline_start

    # ---- Summary ----
    scan_wall = t_scan.result.wall
    plumbing_wall = pipeline_wall - scan_wall - build_total - write_total

    print("=" * 80)
    print("Pipeline Stopwatch (single true top-level timer)")
    print("=" * 80)
    print(f"  scan            : {scan_wall:7.3f}s  ({100*scan_wall/pipeline_wall:.1f}%)")
    print(f"  build_artifact  : {build_total:7.3f}s  ({100*build_total/pipeline_wall:.1f}%)")
    if not args.no_write:
        print(f"  write_artifacts : {write_total:7.3f}s  ({100*write_total/pipeline_wall:.1f}%)")
    print(f"  plumbing (diff) : {plumbing_wall:7.3f}s  ({100*plumbing_wall/pipeline_wall:.1f}%)")
    print(f"  PIPELINE TOTAL  : {pipeline_wall:7.3f}s  (100.0%)")
    print()

    if not args.no_write:
        print("  write_all_artifacts breakdown:")
        write_phase_names = {
            "W1_snapshot_build": "  snapshot build   ",
            "W2_snapshot_write": "  snapshot write   ",
            "W3_normalizer":     "  normalizer       ",
            "W4_sqlite_ddl":     "  sqlite DDL       ",
            "W5_sqlite_nodes":   "  sqlite nodes     ",
            "W6_sqlite_edges":   "  sqlite edges     ",
            "W7_sqlite_violations":"sqlite violations",
            "W8_sqlite_commit":  "  sqlite commit    ",
            "W9_split_planes":   "  split planes     ",
            "W10_file_graph_write":   "  file_graph write",
            "W11_symbol_graph_write": "  symbol_graph write",
            "W12_governance_graph_write": "  gov_graph write ",
        }
        for p in write_phases:
            label = write_phase_names.get(p.name, p.name)
            pct = 100 * p.wall / write_total if write_total > 0 else 0
            extra = "  " + "  ".join(f"{k}={v}" for k, v in p.extra.items()) if p.extra else ""
            print(f"    {label}: {p.wall:6.3f}s ({pct:4.1f}%){extra}")
        print()

    # ---- Save evidence ----
    evidence = {
        "scan_wall": scan_wall,
        "build_total_wall": build_total,
        "write_total_wall": write_total,
        "pipeline_wall": pipeline_wall,
        "plumbing_wall": plumbing_wall,
        "build_stages": [
            {"name": p.name, "wall": p.wall, "cpu": p.cpu, "rss_mb": p.rss_delta_mb, "extra": p.extra}
            for p in build_phases
        ],
        "write_stages": [
            {"name": p.name, "wall": p.wall, "cpu": p.cpu, "rss_mb": p.rss_delta_mb, "extra": p.extra}
            for p in write_phases
        ],
    }
    out_path = ROOT / "artifacts" / "adg_p8_v5_profile.json"
    out_path.write_text(json.dumps(evidence, indent=2))
    print(f"Evidence saved: {out_path}")


if __name__ == "__main__":
    main()
