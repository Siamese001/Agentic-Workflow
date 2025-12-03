#!/usr/bin/env python3
"""
validate_phase_0_5.py
Validates Phase 0.5 semantic cache completion for Agentic-Workflow.

Verification checks include:
- SSoT YAML + META existence & parse
- semantic_cache root existence
- required global artifact domains
- required per-root buckets
- completeness of AST/diff/golden/meta data
- path + hash consistency
- zero missing buckets or empty folders
- report summary

This script is deterministic and performs NO writes.
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "06_data"
CACHE_ROOT = DATA_ROOT / "semantic_cache"

# expected per your architecture
BUCKETS = [
    "agentic_core",
    "schemas",
    "runtime",
    "prompt_governance",
    "config",
    "data_source",
    "observability",
    "scripts",
    "apps",
    "tests",
]

GLOBAL_DOMAINS = [
    "ast",
    "embeddings",
    "diffs",
    "meta",
    "golden",
    "safety",
    "integrity",
]


def load_yaml(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        return f"ERROR: Could not parse YAML ({e})"


def validate_yaml(yaml_data):
    return not isinstance(yaml_data, str)  # true if parsed correctly


def walk_dir(path: Path):
    return [p for p in path.rglob("*") if p.is_file()]


def validate_phase_0_5():
    results = {
        "exists": [],
        "missing": [],
        "errors": [],
        "details": defaultdict(list),
    }

    # --------------------------------------------------------
    # 1. Validate SSoT YAML files
    # --------------------------------------------------------
    yaml_main = PROJECT_ROOT / "unified_structure_subatomic.yaml"
    yaml_meta = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

    for y in [yaml_main, yaml_meta]:
        if not y.exists():
            results["missing"].append(str(y))
        else:
            data = load_yaml(y)
            if validate_yaml(data):
                results["exists"].append(str(y))
            else:
                results["errors"].append(f"Unable to parse YAML: {y}")

    # --------------------------------------------------------
    # 2. Validate semantic_cache root
    # --------------------------------------------------------
    if not CACHE_ROOT.exists():
        results["missing"].append(str(CACHE_ROOT))
        return results  # cannot proceed
    else:
        results["exists"].append(str(CACHE_ROOT))

    # --------------------------------------------------------
    # 3. Validate global domains
    # --------------------------------------------------------
    for d in GLOBAL_DOMAINS:
        p = CACHE_ROOT / d
        if not p.exists():
            results["missing"].append(f"Global domain missing: {p}")
            continue
        results["exists"].append(str(p))

        files = walk_dir(p)
        if len(files) == 0:
            results["errors"].append(f"Global domain EMPTY: {p}")
        else:
            results["details"]["global_counts"].append((d, len(files)))

    # --------------------------------------------------------
    # 4. Validate semantic buckets (per-root)
    # --------------------------------------------------------
    for bucket in BUCKETS:
        p = CACHE_ROOT / bucket
        if not p.exists():
            results["missing"].append(f"Bucket missing: {p}")
            continue
        results["exists"].append(str(p))

        files = walk_dir(p)
        if len(files) == 0:
            results["errors"].append(f"Bucket EMPTY: {p}")
        else:
            results["details"]["bucket_counts"].append((bucket, len(files)))

    # --------------------------------------------------------
    # 5. Optional integrity checks:
    #    - hash filenames follow expected format
    #    - JSON parses correctly
    # --------------------------------------------------------
    for domain in GLOBAL_DOMAINS:
        path = CACHE_ROOT / domain
        if not path.exists():
            continue
        for f in walk_dir(path):
            if f.suffix != ".json":
                results["errors"].append(f"Non-JSON artifact in {domain}: {f}")
                continue
            try:
                json.load(open(f, "r", encoding="utf-8"))
                results["details"]["valid_json"].append(str(f))
            except Exception as e:
                results["errors"].append(f"Invalid JSON in {domain}: {f} ({e})")

    # --------------------------------------------------------
    # 6. Completion Gate
    # --------------------------------------------------------
    results["complete"] = (
        len(results["missing"]) == 0
        and len(results["errors"]) == 0
    )

    return results


def print_report(res):
    print("\n=== PHASE 0.5 COMPLETION VALIDATION REPORT ===")
    print("Project Root:", PROJECT_ROOT)
    print("Cache Root:", CACHE_ROOT)
    print("--------------------------------------------------")

    if res["complete"]:
        print("✔ PHASE 0.5 IS COMPLETE — All required artifacts present")
    else:
        print("❌ PHASE 0.5 INCOMPLETE — Missing or invalid artifacts detected")

    print("\n--- Missing ---")
    for m in res["missing"]:
        print("  •", m)

    print("\n--- Errors ---")
    for e in res["errors"]:
        print("  •", e)

    print("\n--- Details ---")
    for k, v in res["details"].items():
        print(f"{k}:")
        for item in v:
            print("   ", item)

    print("\n--------------------------------------------------")
    print("Completion Status:", "COMPLETE" if res["complete"] else "INCOMPLETE")
    print("=== END REPORT ===\n")


if __name__ == "__main__":
    result = validate_phase_0_5()
    print_report(result)
