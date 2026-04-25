import sqlite3

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")

# Total class-shaped symbols
q1 = """
SELECT COUNT(*) FROM nodes
 WHERE entity_type='symbol'
   AND adg_name LIKE 'ADG::Symbol::%'
"""
print("total Symbol nodes:", c.execute(q1).fetchone())

# Count symbols whose adg_name tail has ≥2 dots (method-ish)
q2 = """
SELECT COUNT(*) FROM nodes
 WHERE entity_type='symbol'
   AND adg_name LIKE 'ADG::Symbol::%.%.%'
"""
print("symbol nodes with >= 3 dotted parts (method-ish):", c.execute(q2).fetchone())

# Sample 10
q3 = """
SELECT adg_name, resolved_path FROM nodes
 WHERE entity_type='symbol'
   AND adg_name LIKE 'ADG::Symbol::agentic_core.%.%.%'
 LIMIT 10
"""
print("\nsample method-ish symbols:")
for r in c.execute(q3):
    print(" ", r)

# Check a specific class we know exists: SovereignBaseAgent
q4 = """
SELECT id, adg_name, resolved_path FROM nodes
 WHERE adg_name LIKE 'ADG::Symbol::agentic_core.base_agents.SovereignBaseAgent%'
 LIMIT 20
"""
print("\nSovereignBaseAgent symbols:")
for r in c.execute(q4):
    print(" ", r)
