"""W1 P8.01 catalog: inventory L5 modules grouped by guardrail concern."""
import csv
import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
out = Path("docs/reports/maintenance/l5_guardrail_family_catalog.csv")
out.parent.mkdir(parents=True, exist_ok=True)

# G01-G29 taxonomy mapping (path-fragment → G-id) per W4-P8 plan rows in Notion
# Best-effort initial mapping; ADR will refine
TAXONOMY: list[tuple[str, str, str]] = [
    ("runtime_gates", "G01", "Named guardrail family catalog"),
    ("identity",      "G04", "End-user identity propagation"),
    ("token",         "G07", "Capability token TTL & single-use"),
    ("approval",      "G02", "Layered guardrail banks (client+agent)"),
    ("severity",      "G03", "Risk-tier proportionate enforcement"),
    ("ingress",       "G02", "Client-side guardrail bank"),
    ("egress",        "G08", "Output-side AI firewall"),
    ("sanitiz",       "G13", "Data perimeter SAIF sanitization"),
    ("a2a",           "G05", "A2A handoff validation"),
    ("permission",    "G06", "Graduated permission ladder"),
    ("redteam",       "G11", "Continuous red-team assurance"),
    ("audit",         "G09", "Audit emission (cross-cutting)"),
    ("policy",        "G10", "Policy plane"),
    ("enforcement",   "G12", "Enforcement chokepoint"),
    ("blueprint",     "G14", "Structure blueprint (config)"),
    ("v5",            "G16", "v5 governance plane"),
    ("adapters",      "G02", "Approval adapters (HITL channels)"),
    ("config",        "G14", "Config/blueprint"),
]


def classify(path: str) -> tuple[str, str]:
    p = path.lower()
    for frag, gid, desc in TAXONOMY:
        if frag in p:
            return gid, desc
    return "G-UNCLASSIFIED", "Needs human triage"


con = sqlite3.connect(snap)
cur = con.cursor()
# Get all L5 module nodes with hotspot data
cur.execute("""
    SELECT n.resolved_path,
           COALESCE(h.fan_in, 0) AS fan_in,
           COALESCE(h.fan_out, 0) AS fan_out,
           COALESCE(h.betweenness_approx, 0.0) AS bw
    FROM nodes n
    LEFT JOIN mv_hotspot_centrality h ON h.node_id = n.id
    WHERE n.layer = 'L5' AND n.entity_type = 'module'
      AND n.resolved_path NOT LIKE '%__init__.py'
      AND n.resolved_path NOT LIKE '%/types/%'
    ORDER BY fan_in DESC
""")
rows = cur.fetchall()

with out.open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["G_id", "concern", "module_path", "fan_in", "fan_out", "betweenness"])
    for path, fi, fo, bw in rows:
        gid, desc = classify(path)
        w.writerow([gid, desc, path, fi, fo, f"{bw:.2f}"])

# Coverage summary
import collections
g_counter: collections.Counter[str] = collections.Counter()
for path, fi, fo, bw in rows:
    gid, _ = classify(path)
    g_counter[gid] += 1

print(f"Wrote {len(rows)} L5 modules to {out}\n")
print("Taxonomy coverage:")
for gid, n in sorted(g_counter.items()):
    print(f"  {gid:18s} {n:3d} modules")
unclass = g_counter.get("G-UNCLASSIFIED", 0)
print(f"\nClassified: {len(rows) - unclass}/{len(rows)} ({100*(len(rows)-unclass)/max(1,len(rows)):.0f}%)")
con.close()
