#!/usr/bin/env python3
"""
scripts/verify_manifest_cleanliness.py
Executes full_agent_discovery.py and validates that deleted legacy bases
are absent from the resulting JSON manifest.
"""

import json
import os
import sys
from pathlib import Path

# 1. Run the discovery script
print("[*] Running full_agent_discovery.py...")
# Set PYTHONPATH to include project root and run from correct directory
env_cmd = "set PYTHONPATH=../../../.. && cd agentic_core/L0_maintenance/scripts && python full_agent_discovery.py"
exit_code = os.system(env_cmd)
# Note: Discovery script may have compliance failures but still generates manifest
print(f"[*] Discovery script exit code: {exit_code}")
if exit_code != 0:
    print("[!] Discovery script had compliance issues, but checking manifest...")

# 2. Load the generated manifest
manifest_path = Path("agent_discovery_full.json")
if not manifest_path.exists():
    print("[-] Manifest file was not generated.")
    sys.exit(1)

with open(manifest_path) as f:
    data = json.load(f)

# 3. Define the blacklist (Deleted Agents)
BLACKLIST = {
    "L1CognitionBaseAgent",
    "L2ExecutionBaseAgent",
    "L3OrchestrationBaseAgent",
    "L4StateBaseAgent",
    "L5SafetyBaseAgent",
    "L6ObservabilityBaseAgent",
    "MaintenanceBaseAgent",
}

# 4. Audit the manifest
found_agents = {agent["class_name"] for agent in data}
violations = found_agents.intersection(BLACKLIST)

print(f"[*] Total Agents Discovered: {len(found_agents)}")

if violations:
    print("[-] CRITICAL FAILURE: The following deleted agents are still in the manifest:")
    for v in violations:
        print(f"   - {v}")
    sys.exit(1)
else:
    print("[+] SUCCESS: Manifest is clean. No legacy base classes detected.")
    sys.exit(0)
