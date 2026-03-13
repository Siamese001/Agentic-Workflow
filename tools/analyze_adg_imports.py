#!/usr/bin/env python3
"""Analyze ADG to find test import/dependency issues."""

import json
from collections import defaultdict
from pathlib import Path

# Load the latest ADG
adg_path = Path("artifacts/adg/adg_full_20260310T012640Z.json")
print(f"Loading ADG from {adg_path}...")
print(f"File size: {adg_path.stat().st_size / 1024 / 1024:.2f} MB\n")

with open(adg_path, encoding="utf-8") as f:
    adg = json.load(f)

print("ADG Structure:")
print(f"  Keys: {list(adg.keys())}")
print(f"  Total nodes: {len(adg.get('nodes', {}))}")
print(f"  Total edges: {len(adg.get('edges', []))}")

# Find test files
test_nodes = {k: v for k, v in adg.get("nodes", {}).items() if "tests/" in k}
print(f"\nTest nodes: {len(test_nodes)}")

# Analyze test node structure
print("\nSample test node structure:")
sample_count = 0
for node_id, node_data in test_nodes.items():
    if sample_count >= 3:
        break
    print(f"\n{sample_count + 1}. {node_id}")
    print(f"   Keys: {list(node_data.keys())}")

    if "imports" in node_data:
        imports = node_data["imports"]
        print(f"   Imports ({len(imports)}): {list(imports)[:5]}")

    if "missing_imports" in node_data:
        missing = node_data["missing_imports"]
        print(f"   Missing imports: {missing}")

    if "parse_error" in node_data:
        print(f"   Parse error: {node_data['parse_error']}")

    sample_count += 1

# Find all test files with potential import issues
print("\n" + "=" * 80)
print("ANALYZING IMPORT ISSUES IN TEST FILES")
print("=" * 80)

missing_imports_by_file = defaultdict(list)
broken_imports = []

for node_id, node_data in test_nodes.items():
    # Check for various import issue indicators
    if "parse_error" in node_data and node_data["parse_error"]:
        broken_imports.append(
            {"file": node_id, "issue": "parse_error", "detail": str(node_data["parse_error"])[:200]}
        )

    if "missing_imports" in node_data and node_data["missing_imports"]:
        for missing in node_data["missing_imports"]:
            missing_imports_by_file[node_id].append(missing)

    # Check if imports reference non-existent modules
    if "imports" in node_data:
        for imp in node_data["imports"]:
            # Check if the imported module exists in the ADG
            if imp not in adg.get("nodes", {}):
                # This might be a missing module
                missing_imports_by_file[node_id].append(imp)

print(f"\nFiles with parse errors: {len(broken_imports)}")
print(f"Files with missing/broken imports: {len(missing_imports_by_file)}")

if broken_imports:
    print("\n--- Parse Errors (first 10) ---")
    for i, item in enumerate(broken_imports[:10], 1):
        print(f"{i}. {item['file']}")
        print(f"   {item['detail']}")

if missing_imports_by_file:
    print("\n--- Missing/Broken Imports (first 20) ---")
    for i, (file, imports) in enumerate(list(missing_imports_by_file.items())[:20], 1):
        print(f"{i}. {file}")
        print(f"   Missing: {', '.join(imports[:5])}")
        if len(imports) > 5:
            print(f"   ... and {len(imports) - 5} more")
