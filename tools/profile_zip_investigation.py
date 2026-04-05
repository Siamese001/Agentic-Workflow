"""ZIP investigation: profile compression path for full-mode zip_creation.

Measures:
  - File count and uncompressed bytes going into the zip
  - Per-file compression time and size delta
  - CPU time vs I/O time split (using os.times)
  - Whether compresslevel=9 is justified or if level=1 (speed) is comparable
  - Re-read cost: how much time is spent reading already-written files vs in-memory

Outputs artifacts/adg_zip_profile.json.
"""
from __future__ import annotations

import json
import os
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent


def profile_zip(artifact_paths: list[Path], label: str, compresslevel: int) -> dict:
    """Zip artifact_paths at the given compresslevel, record per-file stats."""
    import tempfile

    per_file: list[dict] = []
    total_uncompressed = 0
    total_compressed = 0

    t_cpu_before = sum(os.times()[:4])
    t_wall_start = time.perf_counter()

    with tempfile.TemporaryDirectory() as td:
        zip_path = Path(td) / f"probe_{label}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zf:
            for ap in artifact_paths:
                if not ap.exists():
                    continue
                uncompressed = ap.stat().st_size
                t_file_start = time.perf_counter()
                zf.write(ap, f"adg/{ap.name}")
                t_file = time.perf_counter() - t_file_start

                # compressed size = difference in zip file size after adding
                info = zf.getinfo(f"adg/{ap.name}")
                compressed = info.compress_size
                total_uncompressed += uncompressed
                total_compressed += compressed
                per_file.append({
                    "name": ap.name,
                    "uncompressed_mb": round(uncompressed / 1024 / 1024, 2),
                    "compressed_mb": round(compressed / 1024 / 1024, 2),
                    "ratio": round(compressed / uncompressed, 4) if uncompressed else 0,
                    "wall_s": round(t_file, 4),
                })

        t_wall_total = time.perf_counter() - t_wall_start
        t_cpu_after = sum(os.times()[:4])
        t_cpu_total = t_cpu_after - t_cpu_before

        zip_size = zip_path.stat().st_size

    return {
        "label": label,
        "compresslevel": compresslevel,
        "file_count": len(per_file),
        "total_uncompressed_mb": round(total_uncompressed / 1024 / 1024, 2),
        "total_compressed_mb": round(total_compressed / 1024 / 1024, 2),
        "zip_file_mb": round(zip_size / 1024 / 1024, 2),
        "compression_ratio": round(total_compressed / total_uncompressed, 4) if total_uncompressed else 0,
        "wall_s": round(t_wall_total, 4),
        "cpu_s": round(t_cpu_total, 4),
        "io_fraction": round(max(0, t_wall_total - t_cpu_total) / t_wall_total, 3) if t_wall_total else 0,
        "per_file": per_file,
    }


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))

    adg_dir = ROOT / "artifacts" / "adg"

    # Find the most recent set of ADG artifacts
    snapshots = sorted(adg_dir.glob("adg_snapshot_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    sqlites = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    file_graphs = sorted(adg_dir.glob("adg_file_graph_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    sym_graphs = sorted(adg_dir.glob("adg_symbol_graph_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    gov_graphs = sorted(adg_dir.glob("adg_governance_graph_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    graphsnaps = sorted(adg_dir.glob("adg_graphsnap_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    artifact_paths: list[Path] = []
    for candidates in [snapshots, sqlites, file_graphs, sym_graphs, gov_graphs, graphsnaps]:
        if candidates:
            artifact_paths.append(candidates[0])

    if not artifact_paths:
        print("ERROR: No ADG artifacts found in artifacts/adg/")
        return

    print("=== ZIP Investigation: compression path profiling ===")
    print()
    print(f"Artifacts selected ({len(artifact_paths)} files):")
    total_raw = 0
    for ap in artifact_paths:
        sz = ap.stat().st_size / 1024 / 1024
        total_raw += sz
        print(f"  {ap.name:<55}  {sz:>8.1f} MB")
    print(f"  {'TOTAL':<55}  {total_raw:>8.1f} MB")
    print()

    results: dict[str, dict] = {}

    for level, label in [(9, "level9_max"), (6, "level6_default"), (1, "level1_fast"), (0, "level0_store")]:
        print(f"Testing compresslevel={level} ({label})...")
        r = profile_zip(artifact_paths, label, level)
        results[label] = r
        print(f"  wall={r['wall_s']:.2f}s  cpu={r['cpu_s']:.2f}s  "
              f"io_fraction={r['io_fraction']:.1%}  "
              f"zip={r['zip_file_mb']:.1f} MB  ratio={r['compression_ratio']:.3f}")

    print()
    print("=" * 72)
    print("COMPRESSION LEVEL COMPARISON")
    print("=" * 72)
    print(f"  {'Level':<20}  {'Wall':>8}  {'CPU':>8}  {'ZIP MB':>8}  {'Ratio':>8}  {'vs level9':>10}")
    base_wall = results["level9_max"]["wall_s"]
    for label, r in results.items():
        speedup = base_wall - r["wall_s"]
        print(f"  {label:<20}  {r['wall_s']:>8.2f}s  {r['cpu_s']:>8.2f}s  "
              f"{r['zip_file_mb']:>8.1f}  {r['compression_ratio']:>8.3f}  "
              f"{speedup:>+9.2f}s")

    print()
    print("Per-file breakdown (level=9, current production):")
    ref = results["level9_max"]
    print(f"  {'File':<50}  {'Raw MB':>8}  {'Zip MB':>8}  {'Ratio':>8}  {'Wall':>8}")
    for pf in sorted(ref["per_file"], key=lambda x: -x["wall_s"]):
        print(f"  {pf['name']:<50}  {pf['uncompressed_mb']:>8.1f}  "
              f"{pf['compressed_mb']:>8.1f}  {pf['ratio']:>8.3f}  {pf['wall_s']:>8.2f}s")

    print()
    level1 = results["level1_fast"]
    level9 = results["level9_max"]
    size_penalty_mb = level1["zip_file_mb"] - level9["zip_file_mb"]
    time_savings = level9["wall_s"] - level1["wall_s"]
    print(f"Level-1 vs Level-9 trade-off:")
    print(f"  Time savings:  {time_savings:+.2f}s")
    print(f"  Size penalty:  {size_penalty_mb:+.1f} MB larger at level 1")
    print(f"  Recommendation: {'Use level=1 (fast) — significant time saving for minimal size penalty' if time_savings > 1.0 else 'Level=9 justified — time difference is small'}")

    profile = {
        "version": "zip_v1",
        "note": "ZIP investigation: compression level comparison on current ADG artifacts",
        "artifact_paths": [str(p) for p in artifact_paths],
        "total_raw_mb": round(total_raw, 2),
        "results": results,
        "recommendation": {
            "level1_wall_s": level1["wall_s"],
            "level9_wall_s": level9["wall_s"],
            "time_savings_s": round(time_savings, 3),
            "size_penalty_mb": round(size_penalty_mb, 2),
        },
    }
    out_path = ROOT / "artifacts" / "adg_zip_profile.json"
    out_path.write_text(json.dumps(profile, indent=2))
    print(f"\nProfile written: {out_path}")


if __name__ == "__main__":
    main()
