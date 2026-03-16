"""Find modules that are truly missing P1 emitters by checking source files."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

# Get all modules with calls but missing writes_through
missing_wt = [r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='writes_through'
    )
    ORDER BY e1.source_file
""").fetchall()]

print(f"ADG says {len(missing_wt)} modules missing writes_through")

# Check which of these TRULY lack _emit_writes_through in their source
truly_missing = []
for mod in missing_wt:
    try:
        with open(mod, "r", encoding="utf-8") as f:
            content = f.read()
        if "_emit_writes_through" not in content and "_emit_pulls_context" not in content:
            truly_missing.append(mod)
    except FileNotFoundError:
        pass

print(f"\nTruly missing P1 emitters in source: {len(truly_missing)}")
for m in truly_missing[:20]:
    print(f"  {m}")

# Also check: which modules have calls but missing the MOST near-100% metrics?
# Check captures_pattern (gap=6)
missing_cp = set(r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='captures_pattern'
    )
""").fetchall())

print(f"\nMissing captures_pattern in ADG: {len(missing_cp)}")
# Verify these truly lack the emitter
truly_missing_cp = []
for mod in missing_cp:
    try:
        with open(mod, "r", encoding="utf-8") as f:
            content = f.read()
        if "_emit_captures_pattern" not in content:
            truly_missing_cp.append(mod)
    except FileNotFoundError:
        pass

print(f"Truly missing _emit_captures_pattern in source: {len(truly_missing_cp)}")
for m in truly_missing_cp[:10]:
    print(f"  {m}")

# Check covers (gap=120) - this is a test coverage metric
missing_covers = conn.execute("""
    SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'
""").fetchone()[0] - conn.execute("""
    SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='covers'
""").fetchone()[0]
print(f"\nMissing covers: gap={missing_covers}")

# What about escalates_to_human (gap=1853)?
missing_eth = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='escalates_to_human'").fetchone()[0]
total = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]
print(f"escalates_to_human: {missing_eth}/{total} = {missing_eth/total*100:.1f}%")

conn.close()
