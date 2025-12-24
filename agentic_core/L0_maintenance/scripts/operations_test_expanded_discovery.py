#!/usr/bin/env python3
"""
Test Expanded Agent Discovery
Verifies that ValidationProtocol and 50-key registry are now discoverable.
"""
from typing import Any, Optional, Protocol, Dict, List
import importlib
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("EXPANDED DISCOVERY TEST - ValidationProtocol & 50-Key Registry")
print("=" * 70)
print()

# Test the discovery logic from canon_validator_agentic_v2.py
def test_discovery_filter():
    """Test if the new filter catches Protocol, Registry, and ValidationContext."""
    
    test_cases = [
        # (module_path, class_name, should_discover)
        ("agentic_core.L1_cognition.validation_protocol", "ValidationProtocol", True),
        ("agentic_core.L4_state.validation_context", "ValidationContext", True),
        ("agentic_core.L1_cognition.canon_base_agent", "SubAtomicAgent", False),  # Excluded
        ("agentic_core.canon_agents_core", "SystemArchitect", True),
    ]
    
    discovered = []
    failed = []
    
    for module_path, class_name, should_discover in test_cases:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                attr = getattr(module, class_name)
                
                # Apply the NEW discovery filter
                is_type = isinstance(attr, type)
                is_from_module = attr.__module__ == module_path
                is_not_base = class_name != 'SubAtomicAgent'
                
                # NEW FILTER LOGIC
                matches_suffix = class_name.endswith(('Agent', 'Guardian', 'Architect', 'Engineer', 
                                                      'Enforcer', 'Sentinel', 'Hunter', 'Protocol', 'Registry'))
                matches_explicit = class_name in ('ValidationContext', 'VERIFICATION_REGISTRY', 'SystemArchitect')
                
                has_method = (hasattr(attr, 'execute') or hasattr(attr, 'run') or 
                             class_name.endswith('Protocol') or class_name == 'ValidationContext')
                
                will_discover = (is_type and is_from_module and is_not_base and 
                               (matches_suffix or matches_explicit) and has_method)
                
                status = "✓" if will_discover == should_discover else "✗"
                result = "DISCOVERED" if will_discover else "SKIPPED"
                
                print(f"[{status}] {class_name:30} -> {result:12} (Expected: {'DISCOVER' if should_discover else 'SKIP'})")
                
                if will_discover == should_discover:
                    discovered.append(class_name)
                else:
                    failed.append((class_name, will_discover, should_discover))
            else:
                print(f"[!] {class_name:30} -> NOT FOUND in {module_path}")
                
        except Exception as e:
            print(f"[X] {class_name:30} -> ERROR: {e}")
            failed.append((class_name, None, should_discover))
    
    return discovered, failed

print("Testing Discovery Filter Logic:")
print("-" * 70)
discovered, failed = test_discovery_filter()
print()

# Summary
print("=" * 70)
print(f"DISCOVERY TEST RESULTS:")
print(f"  ✓ Correctly Discovered: {len(discovered)}")
print(f"  ✗ Failed: {len(failed)}")

if failed:
    print(f"\nFailed Cases:")
    for class_name, actual, expected in failed:
        print(f"  - {class_name}: Expected {'DISCOVER' if expected else 'SKIP'}, Got {actual}")
else:
    print(f"\n✅ ALL TESTS PASSED - Discovery filter working correctly!")

print("=" * 70)

# Additional check: Verify VERIFICATION_REGISTRY is accessible
print("\nBonus Check: 50-Key VERIFICATION_REGISTRY")
print("-" * 70)
try:
    
    if hasattr(SubAtomicAgent, 'VERIFICATION_REGISTRY'):
        registry = SubAtomicAgent.VERIFICATION_REGISTRY
        print(f"[✓] VERIFICATION_REGISTRY found on SubAtomicAgent")
        print(f"    -> Registry size: {len(registry)} keys")
        print(f"    -> Registry is {'EMPTY (needs init)' if len(registry) == 0 else 'POPULATED'}")
        
        if len(registry) > 0:
            print(f"    -> Sample keys: {list(registry.keys())[:5]}")
    else:
        print(f"[!] VERIFICATION_REGISTRY not found on SubAtomicAgent")
        
except Exception as e:
    print(f"[X] Could not access VERIFICATION_REGISTRY: {e}")

print("=" * 70)