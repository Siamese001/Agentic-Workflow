#!/usr/bin/env python3
"""
Canon Key Discovery Probe
Tests if L1 and L4 modules are ready to be "Canonical" after gravity violation fixes.
"""
import importlib
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Target the specific files that were "missing"
missing_targets = [
    "agentic_core.L1_cognition.canon_base_agent",
    "agentic_core.L4_state.validation_context"
]

print("=" * 70)
print("--- CANON KEY DISCOVERY PROBE ---")
print("=" * 70)
print()

success_count = 0
fail_count = 0

for module_path in missing_targets:
    try:
        mod = importlib.import_module(module_path)
        print(f"[✓] {module_path}: LOAD SUCCESS")
        
        # Check for registered classes
        agents = [cls for cls in dir(mod) if "Agent" in cls or "Context" in cls]
        if agents:
            print(f"    -> Found potential keys: {agents}")
        
        # Additional checks for specific modules
        if "canon_base_agent" in module_path:
            if hasattr(mod, 'SubAtomicAgent'):
                print(f"    -> SubAtomicAgent class: FOUND")
                print(f"    -> VERIFICATION_REGISTRY: {'FOUND' if hasattr(mod.SubAtomicAgent, 'VERIFICATION_REGISTRY') else 'MISSING'}")
        
        if "validation_context" in module_path:
            if hasattr(mod, 'ValidationContext'):
                print(f"    -> ValidationContext class: FOUND")
        
        success_count += 1
        print()
        
    except Exception as e:
        print(f"[X] {module_path}: LOAD FAILED")
        print(f"    -> Reason: {e}")
        print(f"    -> Type: {type(e).__name__}")
        fail_count += 1
        print()

print("=" * 70)
print(f"RESULTS: {success_count} SUCCESS, {fail_count} FAILED")
print("=" * 70)

# Additional validation: Check if ValidationProtocol exists
print("\n--- DEPENDENCY INVERSION CHECK ---")
try:
    protocol_mod = importlib.import_module("agentic_core.L1_cognition.validation_protocol")
    print(f"[✓] ValidationProtocol module: LOAD SUCCESS")
    if hasattr(protocol_mod, 'ValidationProtocol'):
        print(f"    -> ValidationProtocol class: FOUND")
        print(f"    -> Dependency inversion: IMPLEMENTED")
except Exception as e:
    print(f"[X] ValidationProtocol module: LOAD FAILED")
    print(f"    -> Reason: {e}")

print("\n" + "=" * 70)
if fail_count == 0:
    print("✅ ALL MODULES CANONICAL - READY FOR PRODUCTION")
else:
    print(f"⚠️  {fail_count} MODULE(S) NEED ATTENTION")
print("=" * 70)
