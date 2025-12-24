import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")

# [THE SOVEREIGN MAPPING] Old Path Pattern -> New Canonical Path
REWIRE_MAP = [
    # Core Agents & Tools
    (r"agentic_core\.agents", "agentic_core.L2_execution.tool_registry"),
    (r"agentic_core\.tools", "agentic_core.L2_execution.P2_tools"),
    
    # Cognition & Domain
    (r"agentic_core\.interfaces", "agentic_core.L1_cognition.P1_interfaces"),
    (r"agentic_core\.domain", "agentic_core.L1_cognition.P2_domain"),
    (r"agentic_core\.L1_cognition\.action_registry_modules", "agentic_core.L1_cognition.P1_sensing.action_registry_modules"),
    
    # State & Infrastructure
    (r"agentic_core\.state", "agentic_core.L4_state.S1_store"),
    (r"agentic_core\.infra", "agentic_core.L3_orchestration.S3_vitality"),
    
    # Safety & Security
    (r"agentic_core\.security", "agentic_core.L5_safety.P4_security"),
    
    # Type Fixes (Moving the Snapshot to the Core)
    (r"from apps_rg\.L3_orchestration\.l5_autonomous_orchestrator import WorkflowSnapshot", ""),
]

def rewire_synapses():
    print("[*] STARTING GLOBAL SYNAPTIC REWIRE...")
    rewired_count = 0

    for py_file in ROOT.rglob("*.py"):
        # Skip legacy and internal environments
        if any(p in str(py_file) for p in ["legacy_code", ".venv", "data"]):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            for pattern, replacement in REWIRE_MAP:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [✓] Rewired: {py_file.relative_to(ROOT)}")
                rewired_count += 1
        except Exception as e:
            print(f"  [!] Failed {py_file.name}: {e}")

    print(f"\n[OK] REWIRE COMPLETE. {rewired_count} files aligned with the Sovereign Map.")

if __name__ == "__main__":
    rewire_synapses()