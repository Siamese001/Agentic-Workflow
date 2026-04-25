"""Verify R5-W1 detector outputs (A6 entrypoint, A8 hidden_write, A12 gate_self_test).

Auto-selects the latest ENRICHED ADG snapshot (one that has the truth-expansion
tables). Bare snapshots without truth expansion are skipped.
"""

import os
import sqlite3
import sys

ENRICHMENT_MARKER_TABLES = ("module_entrypoints", "gate_self_consistency", "overlay_violations")


def _is_enriched(sqlite_path: str) -> bool:
    """Return True if the snapshot has the R5-W1 truth-expansion tables."""
    try:
        conn = sqlite3.connect(sqlite_path)
        names = {
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        conn.close()
    except sqlite3.DatabaseError:
        return False
    return all(t in names for t in ENRICHMENT_MARKER_TABLES)


def _latest_enriched(adg_dir: str) -> str | None:
    """Return path to the latest enriched snapshot, or None."""
    candidates = [
        f
        for f in os.listdir(adg_dir)
        if f.startswith("adg_indexed") and f.endswith(".sqlite") and not f.endswith(".tmp")
    ]
    for name in sorted(candidates, reverse=True):
        full = os.path.join(adg_dir, name)
        if _is_enriched(full):
            return full
    return None


def main() -> int:
    adg_dir = "artifacts/adg"
    snapshot = _latest_enriched(adg_dir)
    if snapshot is None:
        print(f"[verify_r5w1] ERROR: no enriched snapshot found in {adg_dir}")
        print("Run: python tools/generate_full_adg.py --no-zip --no-reports")
        return 1

    print(f"Using enriched snapshot: {os.path.basename(snapshot)}")
    conn = sqlite3.connect(snapshot)
    cur = conn.cursor()

    # ----- A6 entrypoint_kind -----
    a6_edges = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='entrypoint_kind'").fetchone()[0]
    a6_table = cur.execute("SELECT COUNT(*) FROM module_entrypoints").fetchone()[0]
    print(f"\n[A6] entrypoint_kind edges: {a6_edges}")
    print(f"[A6] module_entrypoints rows: {a6_table}")
    try:
        kinds = cur.execute("SELECT kind, n FROM mv_entrypoint_kind_summary ORDER BY n DESC").fetchall()
        print(f"[A6] kinds: {', '.join(f'{k}={n}' for k, n in kinds)}")
    except sqlite3.OperationalError:
        print("[A6] mv_entrypoint_kind_summary: missing")

    # ----- A8 hidden_write_path -----
    a8_violations = cur.execute(
        "SELECT COUNT(*) FROM overlay_violations WHERE category='hidden_write_outside_uwg'"
    ).fetchone()[0]
    print(f"\n[A8] hidden_write_outside_uwg violations: {a8_violations}")
    try:
        a8_overlay = cur.execute("SELECT COUNT(*) FROM mv_hidden_writes_overlay").fetchone()[0]
        print(f"[A8] mv_hidden_writes_overlay rows: {a8_overlay}")
    except sqlite3.OperationalError:
        print("[A8] mv_hidden_writes_overlay: missing")

    # ----- A12 gate_self_test -----
    a12_edges = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='gate_self_test'").fetchone()[0]
    a12_table = cur.execute("SELECT COUNT(*) FROM gate_self_consistency").fetchone()[0]
    print(f"\n[A12] gate_self_test edges: {a12_edges}")
    print(f"[A12] gate_self_consistency rows: {a12_table}")

    # ----- Synthetic node sanity -----
    syn_eps = cur.execute("SELECT COUNT(*) FROM nodes WHERE adg_name LIKE 'ADG::Entrypoint::%'").fetchone()[0]
    syn_gst = cur.execute("SELECT COUNT(*) FROM nodes WHERE adg_name LIKE 'ADG::GateSelfTest::%'").fetchone()[
        0
    ]
    print(f"\n[synthetic] Entrypoint nodes: {syn_eps}")
    print(f"[synthetic] GateSelfTest nodes: {syn_gst}")

    conn.close()

    # ----- Pass/fail summary -----
    print("\n=== Summary ===")
    failures = []
    if a6_edges == 0:
        failures.append("A6 entrypoint_kind edges = 0")
    if a8_violations == 0:
        failures.append("A8 hidden_write_outside_uwg violations = 0")
    if a12_edges == 0:
        failures.append("A12 gate_self_test edges = 0")

    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print("  PASS: all R5-W1 detectors producing edges/violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
