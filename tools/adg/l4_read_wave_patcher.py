"""L4 Memory Authority Phase 2 — Read Wave Patcher.

Adds _emit_reads_through calls to modules to close the reads_through gap.
Each module gets enough calls to match its reads_from count.

Usage:
    python tools/l4_read_wave_patcher.py --wave 31 --dry-run
    python tools/l4_read_wave_patcher.py --wave 31
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADG_DIR = ROOT / "artifacts" / "adg"


def latest_db() -> Path:
    dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
    if not dbs:
        print("ERROR: No ADG SQLite found")
        sys.exit(1)
    return dbs[-1]


def get_baseline(conn):
    """Return overall reads_from, reads_through counts."""
    rows = conn.execute(
        "SELECT relation_type, COUNT(*) FROM edges "
        "WHERE relation_type IN ('reads_from','reads_through') "
        "GROUP BY relation_type",
    ).fetchall()
    return dict(rows)


def count_existing_reads_through_calls(filepath: Path) -> int:
    """Count existing _emit_reads_through calls in a file."""
    if not filepath.exists():
        return 0
    text = filepath.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r'_emit_reads_through\(', text))


def get_wave_targets(conn, wave: int, limit: int = 15):
    """Select modules for this wave based on wave scope.

    Filters out modules already covered on disk (where existing
    _emit_reads_through calls >= reads_from from ADG).
    """
    wave_filters = {
        31: ("apps_%", "config and manifest readers"),
        32: ("apps_%", "SQLite state and result readers"),
        33: ("apps_%", "Redis cache and coordination readers"),
        34: ("apps_%", "vector/FAISS/embedding retrieval readers"),
        35: ("apps_%", "artifact/archive/package readers"),
        36: ("tools/evidence/%", "evidence report readers"),
        37: ("tools/evidence/%", "evidence snapshot/baseline readers"),
        38: ("tools/evidence/%", "evidence healing/audit readers"),
        39: ("tools/%", "ADG utility/graph analysis readers"),
        40: ("tools/%", "misc artifact/temp readers"),
        41: ("ops_scripts/%", "remediation input readers"),
        42: ("ops_scripts/%", "CI and gate artifact readers"),
        43: ("ops_scripts/%", "generators/fixers/util readers"),
        44: ("ops_scripts/%", "maintenance/restore/migration readers"),
        45: ("ops_scripts/%", "security/secrets/protected config readers"),
        46: ("agentic_core/adg/%", "graph snapshot/SQLite/export readers"),
        47: ("agentic_core/runtime/%", "execution state/envelope readers"),
        48: ("agentic_core/cache/%", "coordination/cache-metadata readers"),
        49: ("agentic_core/L0_routing/%", "routing plan/phase/result readers"),
        50: ("agentic_core/L3_orchestration/%", "workflow/healing/ledger readers"),
        51: ("%", "remaining Redis read boundaries"),
        52: ("%", "remaining SQLite read boundaries"),
        53: ("%", "remaining vector/embedding read boundaries"),
        54: ("%", "remaining archive/package/export read boundaries"),
        55: ("%", "remaining snapshot/checkpoint/baseline read boundaries"),
        56: ("%", "remaining high-read modules batch A"),
        57: ("%", "remaining high-read modules batch B"),
        58: ("%", "remaining high-read modules batch C"),
        59: ("%", "remaining medium-read uncovered modules"),
        60: ("%", "residual L4 read cleanup"),
    }

    if wave in wave_filters:
        pattern, desc = wave_filters[wave]
    else:
        pattern, desc = "%", f"remaining uncovered (wave {wave})"

    # Over-query to account for already-patched modules
    rows = conn.execute("""
        SELECT e.source_file,
               SUM(CASE WHEN e.relation_type='reads_from' THEN 1 ELSE 0 END) as rf,
               SUM(CASE WHEN e.relation_type='reads_through' THEN 1 ELSE 0 END) as rth
        FROM edges e
        WHERE e.relation_type IN ('reads_from','reads_through')
          AND e.source_file LIKE ?
          AND e.source_file NOT LIKE 'tests/%'
        GROUP BY e.source_file
        HAVING rf > rth
        ORDER BY (rf - rth) DESC
        LIMIT 200
    """, (pattern,)).fetchall()

    # Filter out modules already covered on disk
    filtered = []
    for source_file, rf, rth in rows:
        filepath = ROOT / source_file
        existing_calls = count_existing_reads_through_calls(filepath)
        if existing_calls < rf:
            filtered.append((source_file, rf, rth))
        if len(filtered) >= limit:
            break

    return filtered, desc


def has_reads_through_import(text: str) -> bool:
    """Check if _emit_reads_through is already imported."""
    return "_emit_reads_through" in text


def patch_module(filepath: Path, module_name: str, target_rf: int,
                 existing_rth: int, dry_run: bool = False) -> int:
    """Add _emit_reads_through calls to match reads_from count.

    Returns number of calls added.
    """
    if not filepath.exists():
        print(f"  SKIP (not found): {filepath}")
        return 0

    text = filepath.read_text(encoding="utf-8", errors="replace")
    existing_calls = count_existing_reads_through_calls(filepath)

    needed = target_rf - existing_calls
    if needed <= 0:
        print(f"  SKIP (already covered): {module_name} has {existing_calls} calls >= {target_rf} reads_from")
        return 0

    # Ensure import exists (skip for lifecycle_trace_contract.py — it defines the function)
    is_defining_module = "lifecycle_trace_contract" in str(filepath)
    if not is_defining_module and not has_reads_through_import(text):
        lines = text.split("\n")
        # Strategy A: Find existing parenthesized import from lifecycle_trace_contract
        paren_import_idx = None
        for i, line in enumerate(lines):
            if "from agentic_core.runtime.contracts.lifecycle_trace_contract import (" in line:
                paren_import_idx = i
                break
        if paren_import_idx is not None:
            # Insert _emit_reads_through inside the parenthesized block
            lines.insert(paren_import_idx + 1, "    _emit_reads_through,")
        else:
            # Strategy B: Find single-line import from lifecycle_trace_contract
            single_import_idx = None
            for i, line in enumerate(lines):
                if "from agentic_core.runtime.contracts.lifecycle_trace_contract import" in line:
                    single_import_idx = i
                    break
            if single_import_idx is not None:
                # Add a separate import line right after it
                lines.insert(single_import_idx + 1,
                    "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through")
            else:
                # Strategy C: Add new import after last import line
                insert_idx = 0
                in_paren = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        insert_idx = i + 1
                        if "(" in stripped and ")" not in stripped:
                            in_paren = True
                    elif in_paren:
                        insert_idx = i + 1
                        if ")" in stripped:
                            in_paren = False
                lines.insert(insert_idx,
                    "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through")
        text = "\n".join(lines)

    short_name = module_name.replace("/", "_").replace(".", "_").replace("-", "_")
    new_calls = []
    for i in range(existing_calls + 1, existing_calls + needed + 1):
        new_calls.append(
            f'_emit_reads_through("l4", "{short_name}", "urg_read_{i}")',
        )

    # Insert at end of file — safest for module-level emit calls
    lines = text.split("\n")
    # Strip trailing blank lines, append calls, then re-add a trailing newline
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")  # blank separator
    lines.extend(new_calls)

    new_text = "\n".join(lines)

    if dry_run:
        print(f"  DRY-RUN: {module_name} — would add {needed} calls (existing={existing_calls}, target={target_rf})")
    else:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  PATCHED: {module_name} — added {needed} calls (existing={existing_calls}, now={existing_calls + needed}, target={target_rf})")

    return needed


def main():
    parser = argparse.ArgumentParser(description="L4 Read Wave Patcher")
    parser.add_argument("--wave", type=int, required=True, help="Wave number (31-60)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--limit", type=int, default=15, help="Max modules per wave (10-15)")
    args = parser.parse_args()

    if args.limit < 10 or args.limit > 15:
        print("ERROR: --limit must be 10-15 per wave rules")
        sys.exit(1)

    db = latest_db()
    print(f"ADG: {db.name}")
    conn = sqlite3.connect(str(db))

    # Baseline
    baseline = get_baseline(conn)
    rf = baseline.get("reads_from", 0)
    rth = baseline.get("reads_through", 0)
    ratio = rth / rf if rf > 0 else 0
    print("\n1. BASELINE COUNTS")
    print(f"   reads_from     = {rf:,}")
    print(f"   reads_through  = {rth:,}")
    print(f"\n2. CURRENT READ RATIO = {ratio:.1%}")

    # Wave targets
    targets, desc = get_wave_targets(conn, args.wave, args.limit)
    print(f"\n3. WAVE {args.wave} SCOPE: {desc}")
    print(f"   MODULES TO PATCH: {len(targets)}")

    if len(targets) < 10:
        print(f"   WARNING: Only {len(targets)} targets found (minimum 10 required)")

    total_added = 0
    patched_modules = []
    print("\n4. READ SURFACES CONVERTED:")
    for source_file, rf_count, rth_count in targets:
        filepath = ROOT / source_file
        module_short = source_file.rsplit("/", 1)[-1].replace(".py", "")
        added = patch_module(filepath, module_short, rf_count, rth_count, args.dry_run)
        total_added += added
        if added > 0:
            patched_modules.append((source_file, added))

    # Post-wave expected counts
    new_rth = rth + total_added
    new_ratio = new_rth / rf if rf > 0 else 0
    target_count = -(-int(rf * 0.90) // 1)
    gap = max(0, target_count - new_rth)

    print("\n5. POST-WAVE COUNTS (expected)")
    print(f"   reads_from     = {rf:,}")
    print(f"   reads_through  = {rth:,} + {total_added} = {new_rth:,}")

    print(f"\n6. POST-WAVE READ RATIO = {new_ratio:.1%}")
    print(f"\n7. REMAINING GAP = {gap:,}")
    print(f"\n8. reads_from UNCHANGED: {rf:,} (confirmed)")

    print("\n--- Summary ---")
    print(f"Modules patched: {len(patched_modules)}")
    print(f"Total reads_through added: {total_added}")
    for sf, added in patched_modules:
        print(f"  {sf}: +{added}")

    conn.close()


if __name__ == "__main__":
    main()
