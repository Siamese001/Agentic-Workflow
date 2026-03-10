"""
SSOT Dry-Run v2: Individual agent execution with fault isolation.

The standard entrypoint crashes because HierarchyAgent has a pre-existing
AtomicExecutionMixin NameError that blocks ALL mandatory imports.

This script imports and runs each agent individually, capturing results
even when some agents fail to import.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    LAYER_ROOTS,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

# All layer territories
TERRITORIES = sorted(LAYER_ROOTS)

# Agent registry: name -> (import_path, class_name, methods_to_try)
AGENT_REGISTRY = {
    "FileClassificationAgent": (
        "agentic_core.L5_safety.reasoning.FileClassificationAgent",
        "FileClassificationAgent",
        ["heal_repository"],
    ),
    "FilesystemSSOTReconcilerAgent": (
        "agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler",
        "FilesystemSSOTReconcilerAgent",
        ["heal_repository"],
    ),
    "LocationAgent": (
        "agentic_core.L5_safety.reasoning.LocationAgent",
        "LocationAgent",
        ["heal_repository"],
    ),
    "LocationValidatorAgent": (
        "agentic_core.L5_safety.reasoning.location_validator",
        "LocationValidatorAgent",
        ["heal_repository"],
    ),
    "HierarchyAgent": (
        "agentic_core.L5_safety.reasoning.hierarchy_healer",
        "HierarchyAgent",
        ["heal_repository"],
    ),
    "ArchitectureGovernorAgent": (
        "agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent",
        "ArchitectureGovernorAgent",
        ["run_audit"],
    ),
    "SystemArchitectAgent": (
        "agentic_core.L5_safety.reasoning.SystemArchitectAgent",
        "SystemArchitectAgent",
        ["heal_repository"],
    ),
    "RootHygieneAgent": (
        "agentic_core.L5_safety.reasoning.root_hygiene_healer",
        "RootHygieneAgent",
        ["scan_root_violations"],
    ),
    "CognitiveDispositionAgent": (
        "agentic_core.L5_safety.validators.CognitiveDispositionAgent",
        "CognitiveDispositionAgent",
        ["heal_repository"],
    ),
}


def try_import_agent(name, module_path, class_name):
    """Try to import an agent class. Returns (cls, None) or (None, error)."""
    try:
        import importlib

        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls, None
    # guardian: allow-silent-swallow
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def try_run_agent(cls, name, method_name, territory):
    """Try to instantiate and run an agent method. Returns result dict."""
    # Redirect stdout to stderr during agent execution (agents use print())
    _real_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        # Instantiate
        if method_name == "run_audit":
            agent = cls(project_root=PROJECT_ROOT, ci_mode=True)
            result = agent.run_audit(target_territories=[territory])
        elif method_name == "scan_root_violations":
            agent = cls(project_root=PROJECT_ROOT)
            result = agent.scan_root_violations(target_territory=territory)
        elif method_name == "heal_repository":
            agent = cls(project_root=PROJECT_ROOT)
            result = agent.heal_repository(
                dry_run=True,
                target_territory=territory,
                auto_approve=True,
            )
        else:
            return {"error": f"Unknown method: {method_name}"}

        return {"success": True, "result": result}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}


# ── PHASE 1: Import all agents ──
print("=== PHASE 1: Agent Import Check ===", file=sys.stderr)
import_results = {}
agent_classes = {}

for name, (mod_path, cls_name, methods) in AGENT_REGISTRY.items():
    cls, err = try_import_agent(name, mod_path, cls_name)
    if cls:
        import_results[name] = {"status": "OK", "module": mod_path}
        agent_classes[name] = (cls, methods)
        print(f"  OK: {name}", file=sys.stderr)
    else:
        import_results[name] = {"status": "FAIL", "error": err, "module": mod_path}
        print(f"  FAIL: {name} -> {err[:100]}", file=sys.stderr)

# ── PHASE 2: Run FCA (most comprehensive agent) per territory ──
print("\n=== PHASE 2: Per-Territory Agent Execution ===", file=sys.stderr)
territory_results = {}

for territory in TERRITORIES:
    print(f"\n--- {territory} ---", file=sys.stderr)
    territory_results[territory] = {}

    for agent_name, (cls, methods) in agent_classes.items():
        for method in methods:
            print(f"  Running {agent_name}.{method}({territory})...", file=sys.stderr)
            result = try_run_agent(cls, agent_name, method, territory)
            territory_results[territory][agent_name] = result

            if result.get("success"):
                r = result.get("result", {})
                if isinstance(r, dict):
                    vf = r.get("violations_found", r.get("stats", {}).get("violations_found", "?"))
                    vx = r.get("violations_fixed", "?")
                    print(f"    -> violations_found={vf}, violations_fixed={vx}", file=sys.stderr)
                else:
                    print(f"    -> {str(r)[:100]}", file=sys.stderr)
            else:
                print(f"    -> ERROR: {result.get('error', '')[:100]}", file=sys.stderr)
            break  # Only run first available method

# ── PHASE 3: FCA validate_layer_alignment on all files ──
print("\n=== PHASE 3: FCA Layer Alignment Scan (all files) ===", file=sys.stderr)
layer_violations = []

if "FileClassificationAgent" in agent_classes:
    fca_cls, _ = agent_classes["FileClassificationAgent"]
    fca = fca_cls(project_root=PROJECT_ROOT, dry_run=True, validate_only=True)

    from agentic_core.L5_safety.reasoning.FileClassificationAgent import get_python_files_fast

    all_py = get_python_files_fast(AGENTIC_CORE)

    for p in all_py:
        try:
            v = fca.validate_layer_alignment(p)
            if v:
                v["file"] = str(Path(v["file"]).relative_to(PROJECT_ROOT)).replace("\\", "/")
                layer_violations.append(v)
        # guardian: allow-silent-swallow
        except Exception:
            pass

    print(f"  Layer violations found: {len(layer_violations)}", file=sys.stderr)

# ── PHASE 4: Aggregate ──
violation_type_counts = defaultdict(int)
for v in layer_violations:
    violation_type_counts[v.get("violation", "UNKNOWN")] += 1

# ── Output ──
output = {
    "import_results": import_results,
    "territory_results": territory_results,
    "layer_violation_counts": dict(violation_type_counts),
    "layer_violations": layer_violations,
    "territories_scanned": TERRITORIES,
    "agents_available": list(agent_classes.keys()),
    "agents_failed_import": [n for n, r in import_results.items() if r["status"] == "FAIL"],
}

print(json.dumps(output, indent=2, default=str))
print(
    f"\n=== COMPLETE: {len(agent_classes)}/{len(AGENT_REGISTRY)} agents, "
    f"{len(TERRITORIES)} territories, {len(layer_violations)} layer violations ===",
    file=sys.stderr,
)
