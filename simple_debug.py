print("Starting simple debug test...")

# Test 1: UWG validation
print("\n1. Testing UWG validation...")
try:
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    # Test production mode should fail
    try:
        uwg = UniversalWriteGateway(replay_mode=False, policy_hash="")
        print("✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised: {e}")

    # Test replay mode should work
    uwg = UniversalWriteGateway(replay_mode=True, policy_hash="", parent_snapshot_hash="")
    print("✓ Replay mode works")

except Exception as e:
    print(f"✗ UWG test failed: {e}")

# Test 2: Layer inference
print("\n2. Testing layer inference...")
try:
    from tools.generate_full_adg import _infer_layer

    layer = _infer_layer("agentic_core/L0_routing/config.py")
    print(f"✓ L0 test: {layer}")

    layer = _infer_layer("apps_eval/config.py")
    print(f"✓ L_APP test: {layer}")

except Exception as e:
    print(f"✗ Layer inference failed: {e}")

# Test 3: Critical edge patterns
print("\n3. Testing critical edge patterns...")
try:
    from agentic_core.adg.extraction.static_scanner import _CriticalEdgeVisitor

    visitor = _CriticalEdgeVisitor("test_module", "test.py")

    result = visitor._is_determinism_seed("random.seed", None)
    print(f"✓ determinism_seed pattern: {result}")

    result = visitor._is_guardian_gate("run_gateway_bypass_guardian", None)
    print(f"✓ guardian_gate pattern: {result}")

except Exception as e:
    print(f"✗ Critical edge test failed: {e}")

print("\nSimple debug test complete!")
