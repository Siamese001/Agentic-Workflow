from pathlib import Path
import importlib.util

mods = [
    "agentic_core.runtime.contracts.lifecycle_trace_contract",
    "agentic_core.L_CONTRACTS.lifecycle_trace_contract",
    "tools.generate.validation.gates",
    "agentic_core.L5_safety.config.structure_blueprint",
    "tools.generate.adg_graph_watchlist_builder",
    "tools.generate.generate_full_adg",
    "config.feature_schemas",
    "ops_scripts.ci.adg_gates.gate_policy",
    "ops_scripts.ci._adg_wiring_gate_base",
]
for m in mods:
    spec = None
    try:
        spec = importlib.util.find_spec(m)
    except (ImportError, ValueError, ModuleNotFoundError):
        spec = None
    rel = m.replace(".", "/")
    on_disk = Path(rel + ".py").exists() or Path(rel + "/__init__.py").exists()
    parent_dir_exists = Path(rel).parent.exists()
    has_marker = "YES" if spec else "NO"
    print(f"  spec={has_marker:3s}  ondisk={on_disk}  parent={parent_dir_exists}  {m}")
