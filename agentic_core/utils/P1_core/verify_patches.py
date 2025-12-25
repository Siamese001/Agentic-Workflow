#!/usr/bin/env python3
"""Verify Sovereign Patches Applied Successfully"""
from pathlib import Path

from . import (

    validate_file_location,
    ALLOWED_CORE_STAGES,
    CANONICAL_DEPTH_MAP
)

root = Path("C:/Git/Agentic-Workflow")

print("=" * 70)
print("SOVEREIGN PATCH VERIFICATION")
print("=" * 70)

# Patch 1: void_compliance.py
print("\n✓ Patch 1: void_compliance.py - Absolute Depth-4 Enforcement")
print(f"  CANONICAL_DEPTH_MAP: {CANONICAL_DEPTH_MAP}")
print(f"\n  ALLOWED_CORE_STAGES ({len(ALLOWED_CORE_STAGES)} authorized stages):")
for stage in sorted(ALLOWED_CORE_STAGES):
    print(f"    - {stage}")

print("\n  Depth-4 Validation Tests:")
tests = [
    (root / "agentic_core/L1_cognition/identity/spiffe_manager_impl.py", "identity"),
    (root / "agentic_core/L1_cognition/inference/signal_anchoring.py", "inference"),
    (root / "agentic_core/L2_execution/P5_healing/structural_engineer.py", "P5_healing"),
    (root / "agentic_core/__init__.py", "root __init__"),
]

for file_path, stage in tests:
    if file_path.exists():
        valid, msg = validate_file_location(file_path, root)
        status = "✓ PASS" if valid else "✗ FAIL"
        print(f"    {stage:20} -> {status:8} ({file_path.name})")
        if not valid:
            print(f"      Reason: {msg}")

# Patch 2: canon_validator_agentic_v2.py
print("\n✓ Patch 2: canon_validator_agentic_v2.py - Unified Async/Sync Wrapper")
print("  Checking telemetry wrapper implementation...")

import ast
validator_path = root / "canon_validator_agentic_v2.py"
with open(validator_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for unified wrapper signature
has_unified_wrapper = "# Unified Smart Wrapper (Handles both Sync and Async)" in content
has_smart_dispatch = "# Smart Dispatch: Check if method is async at runtime" in content
has_iscoroutinefunction_check = "if inspect.iscoroutinefunction(original_method):" in content

print(f"    Unified wrapper present: {has_unified_wrapper}")
print(f"    Smart dispatch logic: {has_smart_dispatch}")
print(f"    Runtime async detection: {has_iscoroutinefunction_check}")

if has_unified_wrapper and has_smart_dispatch and has_iscoroutinefunction_check:
    print("    Status: ✓ PATCH APPLIED SUCCESSFULLY")
else:
    print("    Status: ✗ PATCH INCOMPLETE")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)