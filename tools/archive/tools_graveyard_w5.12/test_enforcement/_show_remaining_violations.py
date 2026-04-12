"""Show remaining violations for Wave 2+ fixing."""

import collections
import json

with open("artifacts/test_enforcement/test_violations.json") as f:
    data = json.load(f)

print(f"Total remaining violations: {len(data)}")
by_type = collections.Counter(v["violation_type"] for v in data)
for k, v in by_type.most_common():
    print(f"  {k}: {v}")

print("\n=== core_test_import_skip ===")
for v in data:
    if v["violation_type"] == "core_test_import_skip":
        print(f"  {v['file_path']}:{v.get('line', '')} {v.get('why_invalid', '')[:120]}")

print("\n=== first_party_import_skip ===")
for v in data:
    if v["violation_type"] == "first_party_import_skip":
        print(f"  {v['file_path']}:{v.get('line', '')} {v.get('why_invalid', '')[:120]}")

print("\n=== importorskip_in_core ===")
for v in data:
    if v["violation_type"] == "importorskip_in_core":
        print(f"  {v['file_path']}:{v.get('line', '')} {v.get('why_invalid', '')[:120]}")
