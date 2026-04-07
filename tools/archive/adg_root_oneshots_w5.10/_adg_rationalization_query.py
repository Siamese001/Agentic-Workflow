"""Query the fresh ADG SQLite for precise per-file data on rationalized agents."""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"

dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not dbs:
    raise FileNotFoundError("No ADG sqlite found")
db_path = dbs[-1]
print(f"Using: {db_path.name}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

KEY_FILES = [
    # New base classes
    "apps_shared/reasoning/BaseReflectionAgent.py",
    "apps_shared/reasoning/BaseProactiveAgent.py",
    "apps_shared/reasoning/BaseDispatchAgent.py",
    "apps_shared/reasoning/BaseHealingOrchestrator.py",
    "apps_shared/reasoning/ParameterizedValidator.py",
    # LIC subclasses
    "apps_lic/reasoning/LicReflectionAgent.py",
    "apps_lic/reasoning/OutreachProactiveAgent.py",
    "apps_lic/reasoning/DispatchOutreachToolsAgent.py",
    "apps_lic/reasoning/LicHealingOrchestrator.py",
    "apps_lic/reasoning/LICValidationExecutor.py",
    "apps_lic/reasoning/MessageComplianceAgent.py",
    "apps_lic/reasoning/ArchetypeIndicatorsAgent.py",
    "apps_lic/config/archetype_indicator_config.py",
    # RG subclasses
    "apps_rg/reasoning/RgReflectionAgent.py",
    "apps_rg/reasoning/ProactiveAgent.py",
    "apps_rg/reasoning/DispatchResumeToolsAgent.py",
    "apps_rg/reasoning/RgHealingOrchestrator.py",
    "apps_rg/reasoning/RGValidationExecutor.py",
    # Misplaced scripts
    "apps_shared/reasoning/restore_all_archived_agents.py",
    "apps_shared/reasoning/restore_app_agents.py",
    "apps_shared/reasoning/restore_void_agents.py",
    "apps_shared/reasoning/update_orchestrator_imports.py",
    "apps_shared/reasoning/runtime_observability_agentic_spans.py",
]

# Build node id -> row lookup
all_nodes = {r["id"]: r for r in conn.execute("SELECT * FROM nodes").fetchall()}
path_to_node = {}
for nid, row in all_nodes.items():
    rp = row["resolved_path"] or ""
    if rp:
        path_to_node[rp] = row

# Build fan-in / fan-out counts
fan_out = {}  # src_id -> count of outgoing import edges
fan_in = {}  # dst_id -> count of incoming import edges
import_edges = conn.execute(
    "SELECT src_id, dst_id, relation_type, symbol FROM edges WHERE relation_type='imports'",
).fetchall()
for e in import_edges:
    fan_out[e["src_id"]] = fan_out.get(e["src_id"], 0) + 1
    fan_in[e["dst_id"]] = fan_in.get(e["dst_id"], 0) + 1


# For each key file: get node info + its import targets (what it imports)
# and import sources (who imports it)






print("=" * 70)
print("ADG RATIONALIZATION PRECISION REPORT")
print("=" * 70)

missing = []
found_data = {}

for fp in KEY_FILES:
    node = path_to_node.get(fp)
    if not node:
        missing.append(fp)
        continue

    nid = node["id"]
    imports = get_imports_of(nid)
    imported_by = get_imported_by(nid)
    viols = get_violations(nid)

    # Filter imports to only in-repo (skip stdlib/third-party = no resolved_path)
    repo_imports = [(r["resolved_path"], r["symbol"]) for r in imports if r["resolved_path"]]
    external_imports = [r["symbol"] for r in imports if not r["resolved_path"]]
    repo_imported_by = [(r["resolved_path"], r["symbol"]) for r in imported_by if r["resolved_path"]]

    found_data[fp] = {
        "adg_name": node["adg_name"],
        "entity_type": node["entity_type"],
        "layer": node["layer"],
        "confidence": node["confidence"],
        "fan_out_total": fan_out.get(nid, 0),
        "fan_in_total": fan_in.get(nid, 0),
        "repo_imports": repo_imports,
        "external_count": len(external_imports),
        "imported_by": repo_imported_by,
        "violations": [(r["resolved_path"], r["symbol"]) for r in viols],
    }

# ---- OUTPUT ----

print("\n## MISSING FROM ADG (not yet scanned)")
for f in missing:
    print("  MISSING:", f)

print("\n## BASE CLASS FAN-IN (how many files import each base)")
for fp in KEY_FILES:
    if "Base" in fp or "Parameterized" in fp:
        if fp in found_data:
            d = found_data[fp]
            print(f"  {fp}")
            print(f"    fan-in={d['fan_in_total']}  layer={d['layer']}  confidence={d['confidence']}")
            for imp_path, sym in d["imported_by"]:
                print(f"      <- {imp_path}  [{sym}]")

print("\n## SUBCLASS → BASE IMPORT EDGES")
SUBCLASS_FILES = [
    f
    for f in KEY_FILES
    if "Base" not in f
    and "Parameterized" not in f
    and "archetype" not in f.lower()
    and "misplaced" not in f.lower()
    and f
    not in [
        "apps_shared/reasoning/restore_all_archived_agents.py",
        "apps_shared/reasoning/restore_app_agents.py",
        "apps_shared/reasoning/restore_void_agents.py",
        "apps_shared/reasoning/update_orchestrator_imports.py",
        "apps_shared/reasoning/runtime_observability_agentic_spans.py",
    ]
]
BASE_KEYWORDS = ["BaseReflection", "BaseProactive", "BaseDispatch", "BaseHealing", "ParameterizedValidator"]
for fp in SUBCLASS_FILES:
    if fp not in found_data:
        continue
    d = found_data[fp]
    base_imports = [
        (p, s) for p, s in d["repo_imports"] if any(k in (p or "") or k in (s or "") for k in BASE_KEYWORDS)
    ]
    print(f"  {fp}")
    if base_imports:
        for p, s in base_imports:
            print(f"    OK  -> {p}  [{s}]")
    else:
        print("    NO BASE IMPORT FOUND")

print("\n## VIOLATIONS TOUCHING RATIONALIZED FILES")
total_viols = 0
for fp, d in found_data.items():
    if d["violations"]:
        for vp, vs in d["violations"]:
            print(f"  {fp} -> {vp}  [{vs}]")
            total_viols += 1
if total_viols == 0:
    print("  0 violations")

print("\n## MISPLACED SCRIPTS STATUS")
MISPLACED = [
    "apps_shared/reasoning/restore_all_archived_agents.py",
    "apps_shared/reasoning/restore_app_agents.py",
    "apps_shared/reasoning/restore_void_agents.py",
    "apps_shared/reasoning/update_orchestrator_imports.py",
    "apps_shared/reasoning/runtime_observability_agentic_spans.py",
]
for fp in MISPLACED:
    d = found_data.get(fp)
    if d:
        print(
            f"  STILL PRESENT: {fp}  layer={d['layer']}  fan-in={d['fan_in_total']}  fan-out={d['fan_out_total']}",
        )
    else:
        print(f"  MISSING FROM ADG: {fp}")

print("\n## DIAGNOSTIC: raw import edges for LicReflectionAgent + LicHealingOrchestrator")
DIAG_FILES = [
    "apps_lic/reasoning/LicReflectionAgent.py",
    "apps_lic/reasoning/LicHealingOrchestrator.py",
    "apps_lic/reasoning/LICValidationExecutor.py",
    "apps_rg/reasoning/RgReflectionAgent.py",
    "apps_rg/reasoning/ProactiveAgent.py",
    "apps_rg/reasoning/RgHealingOrchestrator.py",
]
for fp in DIAG_FILES:
    node = path_to_node.get(fp)
    if not node:
        print(f"  NODE MISSING: {fp}")
        continue
    nid = node["id"]
    # Raw edges from this node
    raw = conn.execute(
        "SELECT e.relation_type, e.symbol, n.resolved_path FROM edges e "
        "LEFT JOIN nodes n ON e.dst_id=n.id WHERE e.src_id=?",
        (nid,),
    ).fetchall()
    print(f"  {fp}  (node_id={nid}, total_edges={len(raw)})")
    for r in raw:
        sym = r["symbol"] or ""
        rp = r["resolved_path"] or ""
        if any(k in sym or k in rp for k in ["Base", "Parameterized", "apps_shared"]):
            print(f"    [{r['relation_type']}]  sym={sym}  resolved={rp}")

conn.close()
