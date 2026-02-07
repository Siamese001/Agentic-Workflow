"""
Investigation Script - Phase 7 Overlaps
Compares 3 medium-risk file pairs to determine if they are identical or distinct
"""

import hashlib
from pathlib import Path

PAIRS = [
    (
        "agentic_core/L0_maintenance/scripts/dashboard_ssot_definitions.py",
        "agentic_core/L5_safety/validators/dashboard_ssot_definitions.py",
    ),
    (
        "agentic_core/L3_orchestration/reasoning/intervention_server.py",
        "agentic_core/L5_safety/validators/intervention_server.py",
    ),
    (
        "agentic_core/config/blueprint_sovereign/sovereign_domain_constitution.py",
        "agentic_core/L1_cognition/thought_engine/sovereign_domain_constitution.py",
    ),
]


def check_overlaps():
    print("--- INVESTIGATING PHASE 7 OVERLAPS ---")
    root = Path(__file__).parent.parent.parent
    for f1_rel, f2_rel in PAIRS:
        f1 = root / f1_rel
        f2 = root / f2_rel
        if not f1.exists() or not f2.exists():
            print(f"[MISSING] {f1_rel} | {f2_rel}")
            continue
        h1 = hashlib.md5(f1.read_bytes()).hexdigest()
        h2 = hashlib.md5(f2.read_bytes()).hexdigest()
        if h1 == h2:
            print(f"[IDENTICAL] Safe to archive one:\n  A: {f1_rel}\n  B: {f2_rel}")
        else:
            print(f"[DIFFERENT] Manual merge required:\n  A: {f1_rel}\n  B: {f2_rel}")


if __name__ == "__main__":
    check_overlaps()
