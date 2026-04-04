#!/usr/bin/env python3
"""Analyze the test surface inventory and produce MECE classification."""

import json
from collections import Counter

with open("artifacts/test_surface_inventory.json") as f:
    report = json.load(f)

findings = report["findings"]

# 1. Skip call analysis
skip_calls = [f for f in findings if f["pattern_type"] == "pytest.skip_call"]
print(f"Total pytest.skip calls: {len(skip_calls)}")

reason_counter = Counter()
first_party_skips = []
deps_unavailable_skips = []
no_reason_skips = []

for f in skip_calls:
    reason = f.get("reason", "")
    dep = f.get("dependency", "")

    reason_lower = reason.lower()
    if "deps unavailable" in reason_lower or "not available" in reason_lower or "not importable" in reason_lower:
        reason_counter["deps_unavailable"] += 1
        deps_unavailable_skips.append(f)
    elif "schema.py" in reason_lower or "schema" in reason_lower:
        reason_counter["schema_related"] += 1
        deps_unavailable_skips.append(f)
    elif "redis" in reason_lower:
        reason_counter["redis"] += 1
    elif "platform" in reason_lower or "windows" in reason_lower or "linux" in reason_lower:
        reason_counter["platform"] += 1
    elif "optional" in reason_lower:
        reason_counter["optional_dep"] += 1
    elif reason == "":
        reason_counter["no_reason"] += 1
        no_reason_skips.append(f)
    else:
        reason_counter["other"] += 1

print()
print("SKIP REASON CATEGORIES:")
for r, c in reason_counter.most_common():
    print(f"  {r}: {c}")

print()
print(f"Deps-unavailable skips (likely first-party): {len(deps_unavailable_skips)}")
print(f"No-reason skips: {len(no_reason_skips)}")

# Sample deps_unavailable
print()
print("SAMPLE deps_unavailable skips (first 10):")
for f in deps_unavailable_skips[:10]:
    print(f"  {f['file']}:{f['line']} reason={f.get('reason', '')[:80]}")

# 2. Try/except import swallowers
swallowers = [f for f in findings if f["pattern_type"] == "try_except_import_swallower"]
fp_swallowers = [f for f in swallowers if f.get("classification") == "first-party"]
tp_swallowers = [f for f in swallowers if f.get("classification") == "third-party"]
print()
print(f"Try/except import swallowers: {len(swallowers)}")
print(f"  First-party: {len(fp_swallowers)}")
print(f"  Third-party: {len(tp_swallowers)}")
print(f"  Unknown: {len(swallowers) - len(fp_swallowers) - len(tp_swallowers)}")

print()
print("FIRST-PARTY swallowers (all):")
for f in fp_swallowers:
    print(f"  {f['file']}:{f['line']} dep={f.get('dependency', '')} exc={f.get('exception_type', '')}")

# 3. Import-only tests
io_tests = [f for f in findings if f["pattern_type"] == "import_only_test"]
print()
print(f"Import-only tests: {len(io_tests)}")
print("SAMPLE import-only tests (first 10):")
for f in io_tests[:10]:
    print(f"  {f['file']}:{f['line']} test={f.get('test_name', '')} severity={f.get('severity', '')}")

# 4. Shallow assertion tests
shallow = [f for f in findings if f["pattern_type"] == "shallow_assertion_only"]
print()
print(f"Shallow assertion-only tests: {len(shallow)}")

# 5. xfail
xfails = [f for f in findings if f["pattern_type"] == "@pytest.mark.xfail"]
print()
print(f"xfail tests: {len(xfails)}")
for xf in xfails:
    strict = xf.get("strict", "")
    reason = xf.get("reason", "")
    print(f"  {xf['file']}:{xf['line']} strict={strict} reason={reason[:60]}")

# 6. skipif
skipifs = [f for f in findings if f["pattern_type"] == "@pytest.mark.skipif"]
print()
print(f"skipif tests: {len(skipifs)}")
for sf in skipifs[:10]:
    reason = sf.get("reason", "")
    condition = sf.get("condition", "")[:60]
    print(f"  {sf['file']}:{sf['line']} condition={condition} reason={reason[:60]}")

# 7. Conftest patterns
conftest_findings = [f for f in findings if "conftest" in f.get("pattern_type", "")]
print()
print(f"Conftest optionalization patterns: {len(conftest_findings)}")
for cf in conftest_findings:
    print(f"  {cf['file']}:{cf['line']} dep={cf.get('dependency', '')} classification={cf.get('classification', '')}")

# 8. Fixture swallowers
fixture_swallowers = [f for f in findings if f["pattern_type"] == "try_except_import_error_in_fixture"]
print()
print(f"Fixture import error swallowers: {len(fixture_swallowers)}")
for fs in fixture_swallowers:
    print(f"  {fs['file']}:{fs['line']} fixture={fs.get('test_name', '')} severity={fs.get('severity', '')}")

# MECE CLASSIFICATION SUMMARY
print()
print("=" * 70)
print("MECE CLASSIFICATION SUMMARY")
print("=" * 70)

invalid_count = len(fp_swallowers) + len(deps_unavailable_skips) + len(io_tests) + len([x for x in xfails if x.get("strict", "") != "True"])
avoidable_count = len(tp_swallowers) + len(shallow)
valid_count = len([f for f in skip_calls if "redis" in f.get("reason", "").lower() or "platform" in f.get("reason", "").lower()])
questionable_count = len(no_reason_skips) + len(skipifs)

print(f"A. INVALID (must fix): ~{invalid_count}")
print(f"   - First-party import swallowers: {len(fp_swallowers)}")
print(f"   - Deps-unavailable skips (first-party): {len(deps_unavailable_skips)}")
print(f"   - Import-only tests: {len(io_tests)}")
print(f"   - xfail without strict=True: {len([x for x in xfails if x.get('strict', '') != 'True'])}")
print()
print(f"B. VALID BUT AVOIDABLE (should reduce): ~{avoidable_count}")
print(f"   - Third-party import swallowers: {len(tp_swallowers)}")
print(f"   - Shallow assertion-only tests: {len(shallow)}")
print()
print(f"C. VALID REQUIRED (keep narrow): ~{valid_count}")
print(f"   - Platform-specific skips: {reason_counter.get('platform', 0)}")
print(f"   - Redis/external service skips: {reason_counter.get('redis', 0)}")
print()
print(f"D. QUESTIONABLE (needs decision): ~{questionable_count}")
print(f"   - No-reason skips: {len(no_reason_skips)}")
print(f"   - skipif tests: {len(skipifs)}")
