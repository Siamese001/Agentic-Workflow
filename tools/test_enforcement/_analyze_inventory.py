"""Analyze the test inventory JSON for detailed breakdown."""
import collections
import json

with open("artifacts/test_enforcement/test_inventory.json") as f:
    data = json.load(f)

valid = [d for d in data if "error" not in d]
errors = [d for d in data if "error" in d]

print(f"Total: {len(data)}, Valid: {len(valid)}, Errors: {len(errors)}")

# Third-party deps
tp = [d for d in valid if d.get("first_party_or_third_party") == "third_party"]
deps = collections.Counter(d.get("dependency", "?").split(".")[0] for d in tp)
print(f"\nThird-party deps ({len(tp)} total):")
for k, v in deps.most_common(20):
    print(f"  {k}: {v}")

# pytest.skip calls
skips = [d for d in valid if d["skip_pattern"] == "pytest_skip_call"]
print(f"\npytest.skip() calls: {len(skips)}")
for d in skips[:15]:
    print(f"  {d['file_path']}:{d['line']} -> {d['current_behavior'][:100]}")

# skipif_import
skipifs = [d for d in valid if d["skip_pattern"] == "skipif_import"]
print(f"\nskipif_import: {len(skipifs)}")
for d in skipifs[:10]:
    print(f"  {d['file_path']}:{d['line']} dep={d['dependency']} -> {d['current_behavior'][:100]}")

# importorskip
ios = [d for d in valid if d["skip_pattern"] == "importorskip"]
print(f"\nimportorskip: {len(ios)}")
for d in ios:
    print(f"  {d['file_path']}:{d['line']} dep={d['dependency']}")

# skip_decorator
sd = [d for d in valid if d["skip_pattern"] in ("skip_decorator", "skip_decorator_bare")]
print(f"\nskip decorators: {len(sd)}")
for d in sd:
    print(f"  {d['file_path']}:{d['line']} -> {d['current_behavior'][:100]}")

# First-party try/except by handler behavior
fp = [d for d in valid if d.get("first_party_or_third_party") == "first_party"]
fp_behaviors = collections.Counter(d.get("handler_behavior", "?") for d in fp)
print(f"\nFirst-party try/except behaviors ({len(fp)} total):")
for k, v in fp_behaviors.most_common():
    print(f"  {k}: {v}")

# Sample first-party stub patterns
fp_stubs = [d for d in fp if d.get("handler_behavior") == "stub"]
print("\nFirst-party stub samples:")
for d in fp_stubs[:10]:
    print(f"  {d['file_path']}:{d['line']} dep={d['dependency']}")

# Unknown party
unk = [d for d in valid if d.get("first_party_or_third_party") == "unknown"]
print(f"\nUnknown party: {len(unk)}")
unk_patterns = collections.Counter(d["skip_pattern"] for d in unk)
for k, v in unk_patterns.most_common():
    print(f"  {k}: {v}")

# Syntax error file directories
err_dirs = collections.Counter("/".join(d["file_path"].split("/")[:3]) for d in errors)
print(f"\nSyntax error dirs ({len(errors)} total):")
for k, v in err_dirs.most_common(10):
    print(f"  {k}: {v}")
