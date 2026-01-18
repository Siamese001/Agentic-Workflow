"""
Analyze which 2 agents were lost during bulk extraction.
Compare pre-extraction (285) vs post-extraction (283).
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

import json
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# The extraction log shows what was extracted
log_path = Path('surgical_extraction_log.json')
with open(log_path) as f:
    log = json.load(f)

extracted_agents = set(log['extractions'].keys())

print("="*80)
print("AGENT LOSS ANALYSIS")
print("="*80)
print()

# Current state
current_registry = Path(AGENT_DISCOVERY_JSON)
with open(current_registry) as f:
    current = json.load(f)

current_agents = {a['class_name']: a for a in current}

print(f"Current agent count: {len(current_agents)}")
print(f"Extracted during bulk: {len(extracted_agents)}")
print()

# The issue: We extracted 47 agents from 21 multi-class files
# Expected: 285 agents (pre-extraction baseline)
# Actual: 283 agents (post-extraction)
# Loss: 2 agents

# Theory 1: Some agents were in files that got modified but weren't extracted
# Theory 2: Some agents were deleted during the extraction process
# Theory 3: Discovery script is now detecting fewer agents

# Check for agents that might have been in the same files as extracted agents
print("CHECKING FOR COLLATERAL DAMAGE:")
print("(Agents that were in the same files as extracted agents)")
print()

# Get list of files that were processed
processed_files = set()
for agent_name, mapping in log['extractions'].items():
    # The old_module tells us which file the agent came from
    old_module = mapping['old_module']
    processed_files.add(old_module)

print(f"Files processed during extraction: {len(processed_files)}")
for f in sorted(processed_files):
    print(f"  - {f}")

print()
print("="*80)
print("POSSIBLE CAUSES")
print("="*80)
print()
print("1. BaseAgent duplicates in campaign_rag.py files")
print("   - We extracted from L2 campaign_rag.py")
print("   - We extracted from apps_lic campaign_rag.py")
print("   - If BaseAgent was in both, we may have lost one")
print()
print("2. RgTemplateOptimizerAgent duplicates")
print("   - Extracted from ContentQualityAgent.py")
print("   - But there were 3 instances across different files")
print("   - May have overwritten or lost duplicates")
print()
print("3. RgReflectionAgent / StrategicPlannerAgent")
print("   - Both were in multiple files")
print("   - May have lost one during extraction")
print()

# Check current registry for these suspects
suspects = ['BaseAgent', 'TemplateOptimizerAgent', 'ReflectionAgent', 'StrategicPlannerAgent']

print("CURRENT STATUS OF SUSPECT AGENTS:")
for suspect in suspects:
    if suspect in current_agents:
        agent = current_agents[suspect]
        print(f"✓ {suspect}: {agent['path']}")
    else:
        print(f"✗ {suspect}: NOT FOUND (possibly lost)")

print()
print("="*80)
print("RECOMMENDATION")
print("="*80)
print("The 2 missing agents are likely:")
print("1. One of the BaseAgent duplicates from campaign_rag.py")
print("2. One of the RgTemplateOptimizerAgent duplicates")
print()
print("Since we had 294 → 285 (dedup) → 283 (extraction),")
print("and we know MockAgent is a nested class (not counted),")
print("the loss is likely from duplicate handling during extraction.")