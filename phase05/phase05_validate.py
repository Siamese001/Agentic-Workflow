#!/usr/bin/env python3
"""
phase05_validate.py
VALIDATOR FOR PHASE 0.5 COMPLETION KEYS (STRUCTURAL)

Checks:
  • Global domain completeness
  • Bucket completeness
  • Pointer → global reference integrity
  • SSoT YAML presence
  • POSIX-only paths (no backslashes)
"""

from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

CANONICAL_ROOTS = {
    "01_agentic_core": "agentic_core",
    "02_schemas": "schemas",
    "03_runtime": "runtime",
    "04_prompt_governance": "prompt_governance",
    "05_config": "config",
    "06_data_source": "data_source",
    "07_observability": "observability",
    "08_scripts": "scripts",
    "09_apps": "apps",
    "10_tests": "tests",
}

GLOBAL_DOMAINS = [
    "ast", "embeddings", "diffs", "meta",
    "golden", "safety", "integrity"
]

def validate():
    errors = []
    print("=== PHASE 0.5 VALIDATION ===")

    # A-series: SSoT YAML
    if not (PROJECT_ROOT / "unified_structure_subatomic.yaml").exists():
        errors.append("A1: missing unified_structure_subatomic.yaml")
    if not (PROJECT_ROOT / "unified_structure_subatomic_meta.yaml").exists():
        errors.append("A4: missing unified_structure_subatomic_meta.yaml")

    # C-series: global domains exist and non-empty
    for d in GLOBAL_DOMAINS:
        dom = CACHE_ROOT / d
        if not dom.exists():
            errors.append(f"C4: missing global domain directory: {d}")
            continue
        if not any(dom.rglob("*.json")):
            errors.append(f"C12: global domain empty: {d}")

    # E-series: each bucket exists and non-empty
    for root, bucket in CANONICAL_ROOTS.items():
        p = CACHE_ROOT / bucket
        if not p.exists():
            errors.append(f"E1: missing bucket: {bucket}")
            continue
        if not any(p.rglob("*.json")):
            errors.append(f"E2: bucket empty: {bucket}")

    # F10: No backslashes anywhere
    for p in CACHE_ROOT.rglob("*"):
        if "\\" in str(p):
            errors.append(f"F10: backslash in path {p}")

    # Pointer/global integrity
    for root, bucket in CANONICAL_ROOTS.items():
        for pointer in (CACHE_ROOT / bucket).rglob("*.json"):
            try:
                data = json.load(pointer.open("r", encoding="utf-8"))
            except Exception:
                errors.append(f"Invalid JSON pointer: {pointer}")
                continue

            # Validate global references
            if "global" in data:
                for dom, rel in data["global"].items():
                    gpath = CACHE_ROOT / rel
                    if not gpath.exists():
                        errors.append(f"Pointer {pointer} missing global: {rel}")

    # RESULT
    if errors:
        print("\n❌ VALIDATION FAILED")
        for e in errors:
            print("  -", e)
        return 1

    print("✔ PHASE 0.5 COMPLETE — ALL STRUCTURAL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
