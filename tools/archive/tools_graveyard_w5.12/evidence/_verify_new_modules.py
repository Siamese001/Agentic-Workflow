import sys

# guardian: allow-global-mutation
sys.path.insert(0, r"c:\Git\Agentic-Workflow")

results = []

modules = [
    "agentic_core.L2_execution.enforcement.write_governor_mixin",
    "agentic_core.L2_execution.enforcement.static_dispatch_registry",
    "agentic_core.L5_safety.enforcement.security.credential_access_guard",
    "agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer",
]

for mod in modules:
    try:
        m = __import__(mod, fromlist=["_"])
        results.append(f"OK   {mod}")
    except Exception as e:  # guardian: allow-silent-swallow
        results.append(f"FAIL {mod}: {type(e).__name__}: {e}")

for r in results:
    print(r)
