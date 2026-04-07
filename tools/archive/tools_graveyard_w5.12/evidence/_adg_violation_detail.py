"""Get layer details for violation files."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row

# Layer of L6_observability
rows = conn.execute(
    "SELECT adg_name, layer, resolved_path FROM nodes WHERE resolved_path LIKE 'agentic_core/L6_observability/%' LIMIT 5",
).fetchall()
print("L6 observability nodes:")
for r in rows:
    print(f"  layer={r['layer']}  path={r['resolved_path']}")

# Layer of adg.runtime
rows2 = conn.execute(
    "SELECT adg_name, layer, resolved_path FROM nodes WHERE resolved_path LIKE 'agentic_core/adg/runtime/%' LIMIT 5",
).fetchall()
print("\nadg.runtime nodes:")
for r in rows2:
    print(f"  layer={r['layer']}  path={r['resolved_path']}")

# Layer of credential_access_guard itself
rows3 = conn.execute(
    "SELECT adg_name, layer, resolved_path FROM nodes WHERE resolved_path = 'agentic_core/L5_safety/enforcement/security/credential_access_guard.py'",
).fetchall()
print("\ncredential_access_guard:")
for r in rows3:
    print(f"  layer={r['layer']}")

# Layer of elevator_shaft
rows4 = conn.execute(
    "SELECT adg_name, layer, resolved_path FROM nodes WHERE resolved_path = 'agentic_core/L4_state/enforcement/elevator_shaft_consistency_enforcer.py'",
).fetchall()
print("\nelevator_shaft:")
for r in rows4:
    print(f"  layer={r['layer']}")

# semantic_clock_validator layer
rows5 = conn.execute(
    "SELECT adg_name, layer, resolved_path FROM nodes WHERE resolved_path LIKE '%semantic_clock_validator%'",
).fetchall()
print("\nsemantic_clock_validator:")
for r in rows5:
    print(f"  layer={r['layer']}  path={r['resolved_path']}")

# What does execute_ssot.py import from _ssot_pipeline that causes TYPE_CHECKING dead imports?
# The _ssot_pipeline TYPE_CHECKING imports — are they used as annotations?
# Check if Any is used anywhere in _ssot_pipeline
conn.close()
print("\nDONE.")
