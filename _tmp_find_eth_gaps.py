"""Find modules truly missing escalates_to_human emitter in source."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
conn = sqlite3.connect(db)

# Modules with calls but missing escalates_to_human
missing = [r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='escalates_to_human'
    )
    ORDER BY e1.source_file
""").fetchall()]

print(f"ADG says {len(missing)} modules missing escalates_to_human")

# Check which truly lack _emit_escalates_to_human in source
truly_missing = []
for mod in missing:
    try:
        with open(mod, "r", encoding="utf-8") as f:
            content = f.read()
        if "_emit_escalates_to_human" not in content:
            truly_missing.append(mod)
    except FileNotFoundError:
        pass

print(f"Truly missing _emit_escalates_to_human in source: {len(truly_missing)}")
# Show first 20 with their layer
for m in truly_missing[:20]:
    print(f"  {m}")

# Also check: what about validated_by_safety_plane (gap=36)?
missing_vsp = [r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='validated_by_safety_plane'
    )
""").fetchall()]

truly_missing_vsp = []
for mod in missing_vsp:
    try:
        with open(mod, "r", encoding="utf-8") as f:
            content = f.read()
        if "_emit_validated_by_safety_plane" not in content:
            truly_missing_vsp.append(mod)
    except FileNotFoundError:
        pass
print(f"\nTruly missing _emit_validated_by_safety_plane in source: {len(truly_missing_vsp)}")
for m in truly_missing_vsp[:10]:
    print(f"  {m}")

# And proposal_commits_routing (gap=36)?
missing_pcr = [r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='proposal_commits_routing'
    )
""").fetchall()]

truly_missing_pcr = []
for mod in missing_pcr:
    try:
        with open(mod, "r", encoding="utf-8") as f:
            content = f.read()
        if "_emit_proposal_commits_routing" not in content:
            truly_missing_pcr.append(mod)
    except FileNotFoundError:
        pass
print(f"\nTruly missing _emit_proposal_commits_routing in source: {len(truly_missing_pcr)}")
for m in truly_missing_pcr[:10]:
    print(f"  {m}")

conn.close()
