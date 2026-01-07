from __future__ import annotations
import json
from pathlib import Path

# Canonical Repository Root
REPO = Path(r"C:\Git\Agentic-Workflow")
SSOT_PATH = REPO / "agent_discovery_full.json"

def run_audit():
    if not SSOT_PATH.exists():
        print(f"[FATAL] SSOT not found at {SSOT_PATH}")
        return

    with open(SSOT_PATH, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    violations = []
    missing_signals = []
    total_agents = len(data)

    for entry in data:
        path = entry.get("path", "").replace("\\", "/")
        layer = entry.get("layer", "UNKNOWN")
        
        # 1. Gravity Check: Does path match layer?
        if layer != "UNKNOWN" and layer.startswith("L"):
            expected_dir = f"agentic_core/{layer}"
            if expected_dir not in path and layer != "NOT_AN_AGENT":
                violations.append(f"GRAVITY VIOLATION: {path} is assigned to {layer}")

        # 2. Phase 4 Signal Check: Are hardened metrics present?
        if "schema_strictness" not in entry or "proper_base_class" not in entry:
            missing_signals.append(path)

    print(f"--- SSOT AUDIT REPORT: {total_agents} Agents ---")
    print(f"Gravity Violations: {len(violations)}")
    for v in violations[:10]:
        print(f"  [!] {v}")
    
    print(f"\nMissing Phase 4 Signals: {len(missing_signals)}")
    if missing_signals:
        print(f"  [i] First 5 missing: {missing_signals[:5]}")
        print("  [ACTION] Re-run discovery agent to populate AST signals.")
    
    if not violations and not missing_signals:
        print("\n✅ SSOT is HARDENED and GRAVITY-ALIGNED.")

if __name__ == "__main__":
    run_audit()
