"""
Find the 2 agents lost during bulk extraction.
"""
import json
from pathlib import Path

# Load pre-extraction registry (from pilot - should be 285)
backup_registry = Path('.refactor_backups/agent_discovery_full.json.pre_bulk')

# If backup doesn't exist, we need to analyze the extraction log
log_path = Path('surgical_extraction_log.json')

if not log_path.exists():
    print("❌ No extraction log found")
    exit(1)

with open(log_path) as f:
    log = json.load(f)

print("="*80)
print("EXTRACTION LOG ANALYSIS")
print("="*80)
print(f"Dry run: {log['dry_run']}")
print(f"Pilot file: {log.get('pilot_file', 'None (bulk mode)')}")
print(f"Extractions: {len(log['extractions'])}")
print(f"Import remaps: {len(log['import_remaps'])}")
print()

# List all extracted agents
print("EXTRACTED AGENTS:")
for agent_name, mapping in sorted(log['extractions'].items()):
    print(f"  {agent_name}")
    print(f"    Old module: {mapping['old_module']}")
    print(f"    New module: {mapping['new_module']}")

print()
print(f"Total extracted: {len(log['extractions'])}")
print()

# Check for duplicates in extraction
from collections import Counter
agent_names = list(log['extractions'].keys())
duplicates = {name: count for name, count in Counter(agent_names).items() if count > 1}

if duplicates:
    print("⚠️  DUPLICATE EXTRACTIONS DETECTED:")
    for name, count in duplicates.items():
        print(f"  {name}: extracted {count} times")
    print()
    print("This may explain the missing agents - duplicates may have overwritten each other")
else:
    print("✅ No duplicate extractions detected")

print()
print("="*80)
print("RECOMMENDATION")
print("="*80)
print("Run: python scripts/full_agent_discovery.py")
print("Compare the current 283 count with expected 285")
print("The 2 missing agents are likely in the extraction log duplicates")
