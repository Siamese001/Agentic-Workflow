#!/usr/bin/env python3
"""
Test script to verify all canonical imports work correctly after Phase 2 fixes.
"""

print("Testing canonical imports after Phase 2 fixes...")

try:
    # Test 1: Shared Models
    from shared.models import APICallMetrics
    print("✅ APICallMetrics imported successfully from shared.models")
    
    # Test 2: SDK Registry
    from runtime.shared.sdk_registry import SDK_REGISTRY, SDKCategory, SDKEntry
    print("✅ SDK_REGISTRY imported successfully from runtime.shared.sdk_registry")
    
    # Test 3: Prompt Governance
    from prompt_governance import prompts
    print("✅ prompt_governance.prompts imported successfully")
    
    # Test 4: Hardening Module (The ultimate goal)
    import apps_shared.rag.hardening as hardening
    print("✅ apps_shared.rag.hardening imported successfully!")
    
    # Test specific imports from hardening
    from apps_shared.rag.hardening import workflow, rag, validation, utils
    print("✅ All hardening submodules imported successfully!")
    
    # Test some key types
    metrics = APICallMetrics()
    print(f"  - APICallMetrics created: call_count={metrics.call_count}")
    
    print("\n🎉 All canonical imports working! Phase 2 fixes successful!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
