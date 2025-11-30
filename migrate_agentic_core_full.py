import os
import shutil
import re

# ================================================================
# CONFIG: Blueprint for FULL agentic_core folder structure
# ================================================================

ROOT = "agentic_core"

# Engines & naming prefixes
ENGINES = {
    "resume_engine": "rg_",
    "outreach_engine": "lic_"
}

# L1–L5 folders
LAYERS = {
    "l1_planning":    ["planners", "strategies", "inputs"],
    "l2_execution":   ["executors", "tools", "adapters"],
    "l3_orchestration": ["orchestrators", "dag_definitions", "routing", "error_paths"],
    "l4_memory_state":  ["rag", "temporal_kg", "memory", "hydration", "embeddings"],
    "l5_safety":        ["policies", "validators", "filters", "classifiers"]
}

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_full_structure():
    """Build entire -1 → -5 folder tree."""
    for engine, prefix in ENGINES.items():
        engine_root = os.path.join(ROOT, engine)
        ensure(engine_root)

        for layer, subs in LAYERS.items():
            layer_dir = os.path.join(engine_root, layer)
            ensure(layer_dir)

            for sub in subs:
                ensure(os.path.join(layer_dir, sub))

def detect_engine(filename, fullpath):
    """Determine engine based on prefix or path."""
    if filename.startswith("rg_"):
        return "resume_engine"
    if filename.startswith("lic_"):
        return "outreach_engine"

    # Detect by folder keywords (fallback)
    low = fullpath.lower()
    if "resume" in low:
        return "resume_engine"
    if "outreach" in low:
        return "outreach_engine"

    # Default if unknown → resume_engine
    return "resume_engine"

def detect_layer(filename, fullpath):
    name = filename.lower()
    full = fullpath.lower()

    # Detect via keywords
    if any(k in full or k in name for k in ["planner", "strategy"]):
        return "l1_planning"
    if any(k in full or k in name for k in ["executor", "exec", "tool", "adapter"]):
        return "l2_execution"
    if any(k in full or k in name for k in ["orchestr", "dag", "route"]):
        return "l3_orchestration"
    if any(k in full or k in name for k in ["rag", "temporal", "kg", "memory", "embed"]):
        return "l4_memory_state"
    if any(k in full or k in name for k in ["safety", "policy", "validator", "filter", "classif"]):
        return "l5_safety"

    # Default fallback
    return "l1_planning"

def detect_subsystem(layer, filename, fullpath):
    name = filename.lower()
    full = fullpath.lower()

    for sub in LAYERS[layer]:
        if sub in name or sub in full:
            return sub

    # Default fallback: first subsystem in the layer
    return LAYERS[layer][0]

def rename_with_prefix(engine, filename):
    prefix = ENGINES[engine]
    # Strip existing prefixes
    filename = re.sub(r"^(rg_|lic_)", "", filename)
    return prefix + filename

def find_all_py_files():
    """Walk agentic_core and return all .py files NOT in expected structure."""
    discovered = []
    for root, dirs, files in os.walk(ROOT):
        # Skip the final structure paths to avoid double-processing
        if any(engine in root for engine in ENGINES.keys()):
            continue

        for f in files:
            if f.endswith(".py"):
                discovered.append(os.path.join(root, f))
    return discovered

# ================================================================
# MIGRATION
# ================================================================

def migrate_file(fullpath):
    filename = os.path.basename(fullpath)

    # ENGINE
    engine = detect_engine(filename, fullpath)

    # LAYER
    layer = detect_layer(filename, fullpath)

    # SUBSYSTEM
    subsystem = detect_subsystem(layer, filename, fullpath)

    # RENAME
    new_filename = rename_with_prefix(engine, filename)

    dest = os.path.join(
        ROOT,
        engine,
        layer,
        subsystem,
        new_filename
    )

    # Ensure destination exists
    ensure(os.path.dirname(dest))

    print(f"[MOVE] {fullpath} → {dest}")
    shutil.move(fullpath, dest)

    return (fullpath, dest)

# ================================================================
# GAP REPORTING (WHAT FILES ARE MISSING)
# ================================================================

def compute_expected_files():
    """Build set of all required files so gaps can be printed."""
    required = []
    for engine, prefix in ENGINES.items():
        for layer, subs in LAYERS.items():
            for sub in subs:
                expected_folder = os.path.join(ROOT, engine, layer, sub)
                required.append(expected_folder)
    return required

def report_gaps():
    """List any empty folder or missing content."""
    print("\n=== GAP REPORT ===")
    for engine, prefix in ENGINES.items():
        for layer, subs in LAYERS.items():
            for sub in subs:
                folder = os.path.join(ROOT, engine, layer, sub)
                files = os.listdir(folder)
                if len(files) == 0:
                    print(f"[GAP] EMPTY: {folder}")


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":
    print("\n=== Building folder structure ===")
    create_full_structure()

    print("\n=== Locating unmigrated Python files ===")
    py_files = find_all_py_files()

    print(f"Found {len(py_files)} files to migrate.\n")

    print("=== Migrating files ===")
    for f in py_files:
        migrate_file(f)

    print("\n=== Migration complete ===")

    report_gaps()

    print("\n=== DONE ===")
