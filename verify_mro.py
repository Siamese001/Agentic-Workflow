#!/usr/bin/env python3
"""Verify MRO chain for migrated agents."""

from agentic_core.L4_state.ValidationContext.StateValidatorAgent import StateValidatorAgent

print("\n" + "="*70)
print("MIGRATED AGENT MRO VERIFICATION")
print("="*70)

print("\nStateValidatorAgent MRO Chain:")
for i, cls in enumerate(StateValidatorAgent.__mro__):
    print(f"  {i}. {cls.__name__}")

print("\nExpected Chain:")
print("  0. StateValidatorAgent")
print("  1. SovereignBaseAgent")
print("  2. InfrastructureMixin")
print("  3. HealerMixin")
print("  4. MCPHardenedMixin")
print("  5. SubatomicTestingMixin")
print("  6. InstructionalInjectionMixin")
print("  7. object")

# Verify expected classes are in MRO
expected_classes = [
    'StateValidatorAgent',
    'SovereignBaseAgent',
    'InfrastructureMixin',
    'HealerMixin',
    'MCPHardenedMixin',
    'SubatomicTestingMixin',
    'InstructionalInjectionMixin',
]

mro_names = [cls.__name__ for cls in StateValidatorAgent.__mro__]
all_present = all(name in mro_names for name in expected_classes)

print("\n" + "="*70)
if all_present:
    print("✅ MRO VERIFICATION PASSED")
    print("   All expected classes present in correct order")
else:
    print("❌ MRO VERIFICATION FAILED")
    missing = [name for name in expected_classes if name not in mro_names]
    print(f"   Missing classes: {missing}")
print("="*70 + "\n")
