"""Print gap analysis results from ast_gap_results.json."""

import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    TESTS_DIR,
    get_validated_project_root,
    APPS_SHARED_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)

ROOT = get_validated_project_root()
data = json.loads((ROOT / "ops_scripts/ci/ast_gap_results.json").read_text())

print("=== SOURCE SUMMARY ===")
for t, s in data["source_summary"].items():
    line = (
        "  "
        + t
        + ": "
        + str(s["files"])
        + " files, "
        + str(s["n_classes"])
        + " classes, "
        + str(s["n_funcs"])
        + " funcs"
    )
    print(line)
    for se in s["syntax_errors"]:
        print("    SYNTAX: " + se["path"])

print()
print("=== TEST SUMMARY ===")
ts = data["test_summary"]
print("  Total test files: " + str(ts["total_test_files"]))
print("  Total test funcs: " + str(ts["total_test_funcs"]))
for se in ts["syntax_errors"]:
    print("  Test syntax error: " + se)

print()
print("=== GAPS BY SEVERITY ===")
gaps = data["coverage_gaps"]
by_sev = {}
for g in gaps:
    by_sev.setdefault(g["severity"], []).append(g)

for sev in ["CRITICAL", "HIGH", "LOW", "SYNTAX_ERROR"]:
    items = by_sev.get(sev, [])
    print("  " + sev + ": " + str(len(items)))

print()
print("=== CRITICAL GAPS (>3 symbols, no tests) ===")
for g in sorted(by_sev.get("CRITICAL", []), key=lambda x: x["path"]):
    cls = g.get("top_classes", [])
    print(
        "  [" + g["target"] + "] " + g["path"] + "  cls=" + str(g["n_classes"]) + " fn=" + str(g["n_funcs"])
    )
    if cls:
        print("    classes: " + str(cls))

print()
print("=== HIGH GAPS (1-3 symbols, no tests) ===")
for g in sorted(by_sev.get("HIGH", []), key=lambda x: x["path"]):
    cls = g.get("top_classes", [])
    print(
        "  [" + g["target"] + "] " + g["path"] + "  cls=" + str(g["n_classes"]) + " fn=" + str(g["n_funcs"])
    )
    if cls:
        print("    classes: " + str(cls))

print()
print("=== COVERED: " + str(len(data["covered"])) + " modules ===")

# Per-target gap count
print()
print("=== GAP COUNT BY TARGET ===")
target_gaps = {}
for g in gaps:
    if g["severity"] in ("CRITICAL", "HIGH", "LOW"):
        target_gaps.setdefault(g["target"], {"CRITICAL": 0, "HIGH": 0, "LOW": 0})
        target_gaps[g["target"]][g["severity"]] += 1
for tgt, counts in sorted(target_gaps.items()):
    print(
        "  "
        + tgt
        + ": CRITICAL="
        + str(counts["CRITICAL"])
        + " HIGH="
        + str(counts["HIGH"])
        + " LOW="
        + str(counts["LOW"])
    )

# Guardian-specific check: does tests/guardian or tests/architecture exist?
print()
print("=== GUARDIAN / ARCHITECTURE TEST INVENTORY ===")
for subdir in ["guardian", "architecture", AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]:
    p = ROOT / TESTS_DIR / subdir
    if p.exists():
        files = list(p.rglob("test_*.py"))
        print("  tests/" + subdir + ": " + str(len(files)) + " test files")
    else:
        print("  tests/" + subdir + ": MISSING")
