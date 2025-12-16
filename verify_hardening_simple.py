import unittest
import json
import os
import tempfile
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Test 1: Manifest Integrity Check
def test_manifest_integrity():
    """Test that corrupt manifests are rejected."""
    print("\n🛡️  Running Test 1: Integrity Gate (Sabotage)...")

    # Import the function
    from orchestrator import validate_manifest_integrity

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        # Write broken JSON
        tmp.write('{"files": { "broken_entry": [ }')
        tmp_path = tmp.name

    try:
        result = validate_manifest_integrity(tmp_path)
        if not result:
            print("   ✅ Orchestrator successfully rejected corrupt manifest.")
            return True
        else:
            print("   ❌ Security Flaw: Orchestrator accepted corrupt JSON!")
            return False
    finally:
        os.remove(tmp_path)

# Test 2: Memory Ghost Shield
def test_memory_filtering():
    """Test that memory queries include hash filtering."""
    print("🛡️  Running Test 2: Memory Ghost Shield...")

    try:
        from agent_logic_connectivity import CanonValidator

        # Create a mock validator
        validator = CanonValidator(manifest_path="active_manifest.json")

        # Mock the necessary components
        class MockPinecone:
            def __init__(self):
                self.query_args = None

            def query(self, **kwargs):
                self.query_args = kwargs
                return {"matches": []}

        validator.pinecone_index = MockPinecone()
        validator.embedding_fn = lambda x: [0.1, 0.2]
        validator._get_file_hash = lambda x: "HASH_V2_NEW"

        # Run query
        validator.query_semantic_memory("login logic", context_file="auth.py")

        # Check filter was applied
        actual_filter = validator.pinecone_index.query_args.get('filter', {})
        expected_filter = {"file_path": "auth.py", "content_hash": "HASH_V2_NEW"}

        if actual_filter == expected_filter:
            print(f"   ✅ Query included strict hash filter: {actual_filter}")
            return True
        else:
            print(f"   ❌ Security Flaw: Filter missing! Expected {expected_filter}, got {actual_filter}")
            return False

    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

# Test 3: Error Classification
def test_error_classification():
    """Test that errors are properly classified."""
    print("🛡️  Running Test 3: Zombie Prevention...")

    try:
        # Import the error definitions
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps_rg', 'L3_orchestration'))
        from hardened_orchestrator import TERMINAL_ERRORS

        # Check that SyntaxError is in terminal errors
        if SyntaxError in TERMINAL_ERRORS:
            print("   ✅ SyntaxError correctly classified as terminal error.")
            return True
        else:
            print("   ❌ SyntaxError not in terminal errors!")
            return False

    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🔬 WINDSURF HARDENING VERIFICATION")
    print("=" * 60)

    results = []

    # Run tests
    results.append(test_manifest_integrity())
    results.append(test_memory_filtering())
    results.append(test_error_classification())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("System is properly hardened!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print("System has security vulnerabilities!")
        return 1

if __name__ == '__main__':
    sys.exit(main())

