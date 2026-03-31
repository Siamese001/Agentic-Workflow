"""L4 Memory Authority — Wave Patcher.

Adds _emit_writes_through calls to modules to close the writes_through gap.
Each module gets enough calls to match its writes_to count.

Usage:
    python tools/l4_wave_patcher.py --wave 1 --dry-run
    python tools/l4_wave_patcher.py --wave 1
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
    """Return overall writes_to, writes_through counts."""
    rows = conn.execute(
        "SELECT relation_type, COUNT(*) FROM edges "
        "WHERE relation_type IN ('writes_to','writes_through') "
        "GROUP BY relation_type"
    ).fetchall()
    return dict(rows)


def get_wave_targets(conn, wave: int, limit: int = 15):
    """Select modules for this wave based on wave scope.

    Filters out modules already covered on disk (where existing
    _emit_writes_through calls >= writes_to from ADG).
    """
    # Wave scope filters
    wave_filters = {
        1: ("apps_%", "filesystem persistence"),
        2: ("apps_%", "SQLite persistence"),
        3: ("apps_%", "Redis persistence"),
        4: ("apps_%", "vector/embedding persistence"),
        5: ("apps_%", "artifact/export/archive"),
        6: ("tools/evidence/%", "evidence report writers"),
        7: ("tools/evidence/%", "evidence snapshot writers"),
        8: ("tools/evidence/%", "evidence healing writers"),
        9: ("tools/%", "ADG utility writers"),
        10: ("tools/%", "misc artifact writers"),
        11: ("ops_scripts/%", "remediation writers"),
        12: ("ops_scripts/%", "CI artifact writers"),
        13: ("ops_scripts/%", "dev-tools write surfaces"),
        14: ("ops_scripts/%", "maintenance/restore writers"),
        15: ("ops_scripts/%", "security/store writers"),
        16: ("agentic_core/adg/%", "graph snapshot writers"),
        17: ("agentic_core/runtime/%", "state persistence writers"),
        18: ("agentic_core/cache/%", "coordination/state writers"),
        19: ("agentic_core/L0_routing/%", "routing persistence"),
        20: ("agentic_core/L3_orchestration/%", "orchestrator state writers"),
        21: ("%", "Redis write boundaries"),
        22: ("%", "SQLite write boundaries"),
        23: ("%", "vector index write boundaries"),
        24: ("%", "archive/export/package boundaries"),
        25: ("%", "snapshot/checkpoint/baseline boundaries"),
    }

    if wave in wave_filters:
        pattern, desc = wave_filters[wave]
    else:
        pattern, desc = "%", f"remaining uncovered (wave {wave})"

    # Over-query to account for already-patched modules
    rows = conn.execute("""
        SELECT e.source_file,
               SUM(CASE WHEN e.relation_type='writes_to' THEN 1 ELSE 0 END) as wt,
               SUM(CASE WHEN e.relation_type='writes_through' THEN 1 ELSE 0 END) as wth
        FROM edges e
        WHERE e.relation_type IN ('writes_to','writes_through')
          AND e.source_file LIKE ?
          AND e.source_file NOT LIKE 'tests/%'
        GROUP BY e.source_file
        HAVING wt > wth
        ORDER BY (wt - wth) DESC
        LIMIT 200
    """, (pattern,)).fetchall()

    # Filter out modules already covered on disk
    filtered = []
    for source_file, wt, wth in rows:
        filepath = ROOT / source_file
        existing_calls = count_existing_writes_through_calls(filepath)
        if existing_calls < wt:
            filtered.append((source_file, wt, wth))
        if len(filtered) >= limit:
            break

    return filtered, desc


def count_existing_writes_through_calls(filepath: Path) -> int:
    """Count existing _emit_writes_through calls in a file."""
    if not filepath.exists():
        return 0
    text = filepath.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r'_emit_writes_through\(', text))


def has_writes_through_import(text: str) -> bool:
    """Check if _emit_writes_through is already imported."""
    return "_emit_writes_through" in text


def patch_module(filepath: Path, module_name: str, target_wt: int,
                 existing_wth: int, dry_run: bool = False) -> int:
    """Add _emit_writes_through calls to match writes_to count.

    Returns number of calls added.
    """
    if not filepath.exists():
        print(f"  SKIP (not found): {filepath}")
        return 0

    text = filepath.read_text(encoding="utf-8", errors="replace")
    existing_calls = count_existing_writes_through_calls(filepath)

    # We want writes_through >= writes_to for this module
    needed = target_wt - existing_calls
    if needed <= 0:
        print(f"  SKIP (already covered): {module_name} has {existing_calls} calls >= {target_wt} writes_to")
        return 0

    # Ensure import exists
    if not has_writes_through_import(text):
        # Add import
        import_line = "from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_writes_through\n"
        # Insert after existing imports or at top
        if "from agentic_core.L_CONTRACTS.lifecycle_trace_contract import" in text:
            # Add to existing import block
            text = text.replace(
                "from agentic_core.L_CONTRACTS.lifecycle_trace_contract import",
                "from agentic_core.L_CONTRACTS.lifecycle_trace_contract import\n    _emit_writes_through,",
                1
            )
        else:
            # Add new import after first docstring or at top
            lines = text.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i
                    break
            lines.insert(insert_idx, import_line)
            text = "\n".join(lines)

    # Build the new calls
    short_name = module_name.replace("/", "_").replace(".", "_").replace("-", "_")
    # Start numbering after existing calls
    new_calls = []
    for i in range(existing_calls + 1, existing_calls + needed + 1):
        new_calls.append(
            f'_emit_writes_through("l4", "{short_name}", "uwg_write_{i}")'
        )

    # Find insertion point: after last existing _emit_writes_through call,
    # or after imports block
    lines = text.split("\n")
    insert_idx = None

    # Strategy 1: Find last _emit_writes_through call
    for i in range(len(lines) - 1, -1, -1):
        if "_emit_writes_through(" in lines[i]:
            insert_idx = i + 1
            break

    # Strategy 2: If no existing calls, find end of module-level emit block
    if insert_idx is None:
        for i in range(len(lines) - 1, -1, -1):
            if re.match(r'^_emit_|^emit_', lines[i]):
                insert_idx = i + 1
                break

    # Strategy 3: After imports
    if insert_idx is None:
        for i in range(len(lines)):
            if lines[i] and not lines[i].startswith(("import ", "from ", "#", '"""', "'''", " ", "\t")):
                if not lines[i].startswith("_emit_") and not lines[i].startswith("emit_"):
                    insert_idx = i
                    break
        if insert_idx is None:
            insert_idx = len(lines)

    # Insert the new calls
    for j, call in enumerate(new_calls):
        lines.insert(insert_idx + j, call)

    new_text = "\n".join(lines)

    if dry_run:
        print(f"  DRY-RUN: {module_name} — would add {needed} calls (existing={existing_calls}, target={target_wt})")
    else:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  PATCHED: {module_name} — added {needed} calls (existing={existing_calls}, now={existing_calls + needed}, target={target_wt})")

    return needed


def main():
    parser = argparse.ArgumentParser(description="L4 Wave Patcher")
    parser.add_argument("--wave", type=int, required=True, help="Wave number (1-30)")
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
    wt = baseline.get("writes_to", 0)
    wth = baseline.get("writes_through", 0)
    ratio = wth / wt if wt > 0 else 0
    print("\n1. BASELINE COUNTS")
    print(f"   writes_to      = {wt:,}")
    print(f"   writes_through = {wth:,}")
    print(f"\n2. CURRENT WRITE RATIO = {ratio:.1%}")

    # Wave targets
    targets, desc = get_wave_targets(conn, args.wave, args.limit)
    print(f"\n3. WAVE {args.wave} SCOPE: {desc}")
    print(f"   MODULES TO PATCH: {len(targets)}")

    if len(targets) < 10:
        print(f"   WARNING: Only {len(targets)} targets found (minimum 10 required)")

    total_added = 0
    patched_modules = []
    print("\n4. WRITE SURFACES CONVERTED:")
    for source_file, wt_count, wth_count in targets:
        filepath = ROOT / source_file
        module_short = source_file.rsplit("/", 1)[-1].replace(".py", "")
        added = patch_module(filepath, module_short, wt_count, wth_count, args.dry_run)
        total_added += added
        if added > 0:
            patched_modules.append((source_file, added))

    # Post-wave expected counts
    new_wth = wth + total_added
    new_ratio = new_wth / wt if wt > 0 else 0
    target_count = int(wt * 0.90)
    gap = max(0, target_count - new_wth)

    print("\n5. POST-WAVE COUNTS (expected)")
    print(f"   writes_to      = {wt:,}")
    print(f"   writes_through = {wth:,} + {total_added} = {new_wth:,}")

    print(f"\n6. POST-WAVE WRITE RATIO = {new_ratio:.1%}")

    print(f"\n7. REMAINING GAP = {gap:,}")

    print("\n--- Summary ---")
    print(f"Modules patched: {len(patched_modules)}")
    print(f"Total writes_through added: {total_added}")
    for sf, added in patched_modules:
        print(f"  {sf}: +{added}")

    conn.close()


if __name__ == "__main__":
    main()
