"""
Tool Registry Smoke Test

Verifies:
1. Tools in Sovereign Territory are accepted
2. Tools in archives/ are rejected
3. Bulk registration works correctly
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from apps_shared.utils.tool_registry import ToolRegistry


def dummy_tool():
    """Placeholder tool function for testing."""
    return "executed"


def test_sovereign_territory_acceptance():
    """Test that tools in valid locations are accepted."""
    print("=" * 60)
    print("TEST 1: Sovereign Territory Acceptance")
    print("=" * 60)
    
    registry = ToolRegistry.get_instance()
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    
    # Valid paths that should be accepted
    valid_paths = [
        "agentic_core/L2_execution/ToolRegistry/tools.py",
        "agentic_core/L2_execution/ToolRegistry/mcp_tools.py",
        "agentic_core/utils/sovereign_index.py",
        "apps_shared/utils/tool_registry.py",
    ]
    
    accepted = 0
    for i, path in enumerate(valid_paths):
        result = registry.register_tool(
            tool_name=f"valid_tool_{i}",
            tool_path=path,
            tool_func=dummy_tool,
            description=f"Test tool from {path}"
        )
        if result:
            print(f"  ✅ ACCEPTED: {path}")
            accepted += 1
        else:
            print(f"  ❌ REJECTED (unexpected): {path}")
    
    print(f"\nResult: {accepted}/{len(valid_paths)} valid tools accepted")
    return accepted == len(valid_paths)


def test_archives_rejection():
    """Test that tools in archives/ are rejected."""
    print("\n" + "=" * 60)
    print("TEST 2: Archives Rejection")
    print("=" * 60)
    
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    
    # Invalid paths that should be rejected
    invalid_paths = [
        "archives/void_violations/rogue_tool.py",
        "archives/legacy/old_tool.py",
        "/tmp/temp_tool.py",
        ".sovereign_healing_backup/tool.py",
    ]
    
    rejected = 0
    for i, path in enumerate(invalid_paths):
        result = registry.register_tool(
            tool_name=f"rogue_tool_{i}",
            tool_path=path,
            tool_func=dummy_tool
        )
        if not result:
            print(f"  ✅ REJECTED (correct): {path}")
            rejected += 1
        else:
            print(f"  ❌ ACCEPTED (unexpected): {path}")
    
    print(f"\nResult: {rejected}/{len(invalid_paths)} invalid tools correctly rejected")
    return rejected == len(invalid_paths)


def test_bulk_registration():
    """Test bulk registration from discovered tools."""
    print("\n" + "=" * 60)
    print("TEST 3: Bulk Registration from L2_execution")
    print("=" * 60)
    
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    
    # Discover tool files
    discovered = registry.discover_tools("*_tools.py", PROJECT_ROOT)
    print(f"  Discovered {len(discovered)} *_tools.py files")
    
    # Filter to only L2_execution tools
    l2_tools = [p for p in discovered if "L2_execution" in str(p)]
    print(f"  Found {len(l2_tools)} tools in L2_execution/")
    
    # Register each
    registered = 0
    for tool_path in l2_tools:
        rel_path = tool_path.relative_to(PROJECT_ROOT)
        tool_name = tool_path.stem
        result = registry.register_tool(
            tool_name=tool_name,
            tool_path=str(rel_path),
            tool_func=dummy_tool,
            description=f"Auto-registered from {tool_path.name}"
        )
        if result:
            registered += 1
            print(f"    ✅ {tool_name}")
    
    print(f"\nResult: {registered}/{len(l2_tools)} L2 tools registered")
    return registered > 0


def test_tool_retrieval():
    """Test that registered tools can be retrieved."""
    print("\n" + "=" * 60)
    print("TEST 4: Tool Retrieval")
    print("=" * 60)
    
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    
    # Register a tool
    registry.register_tool(
        tool_name="retrieval_test",
        tool_path="agentic_core/L2_execution/ToolRegistry/tools.py",
        tool_func=dummy_tool,
        description="Test retrieval"
    )
    
    # Retrieve it
    func = registry.get_tool_func("retrieval_test")
    if func and callable(func):
        result = func()
        if result == "executed":
            print("  ✅ Tool retrieved and executed successfully")
            return True
    
    print("  ❌ Tool retrieval failed")
    return False


def main():
    """Run all smoke tests."""
    print("\n" + "=" * 60)
    print("TOOL REGISTRY SMOKE TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Sovereign Territory Acceptance", test_sovereign_territory_acceptance()))
    results.append(("Archives Rejection", test_archives_rejection()))
    results.append(("Bulk Registration", test_bulk_registration()))
    results.append(("Tool Retrieval", test_tool_retrieval()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SMOKE TESTS PASSED!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
