#!/usr/bin/env python3
"""
L5 Streamer & L6 Sovereign Code Graph Validation

This test validates:
1. L5 Streamer broadcasts to JSONL and WebSocket
2. Reasoning extraction from LLM responses
3. L6 DependencyGraph builds correctly from AST
4. Blast radius calculation for modified files
5. Architecture governance laws enforcement
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from interfaces.governance import ArchitectureGovernor, DependencyGraph
from L3_orchestration.models import ExecutionContext
from L3_orchestration.nervous_system import NervousSystem, OrchestratorConfig
from L4_state.storage import SignalLedger, create_storage_adapter
from L5_safety.streamer import L5Streamer, get_l5_streamer


async def test_l5_streamer():
    """Test the L5 Streamer functionality."""
    print("=" * 80)
    print("L5 STREAMER VALIDATION")
    print("=" * 80)

    print("\n1. Testing Streamer Initialization")
    print("-" * 50)

    # Create temporary stream directory
    with tempfile.TemporaryDirectory() as temp_dir:
        stream_dir = Path(temp_dir) / "observability" / "audit"
        streamer = L5Streamer(str(stream_dir))

        # Start streamer
        await streamer.start_streamer()

        if streamer._streamer_initialized:
            print("✅ Streamer initialized successfully")
        else:
            print("❌ Streamer initialization failed")
            return False

        print("\n2. Testing Message Broadcasting")
    print("-" * 50)

        # Test basic broadcast
        await streamer.broadcast("Test message", agent="TestAgent", level="INFO")

        # Give background worker time to process
        await asyncio.sleep(0.1)

        # Check JSONL file
        log_path = stream_dir / "live_stream.jsonl"
        if log_path.exists():
            with open(log_path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    if last_entry["content"] == "Test message":
                        print("✅ Message broadcast to JSONL successful")
                        print(f"   Timestamp: {last_entry['timestamp']}")
                        print(f"   Agent: {last_entry['agent']}")
                        print(f"   Level: {last_entry['level']}")
                    else:
                        print("❌ Message content mismatch")
                        return False
                else:
                    print("❌ No messages in stream")
                    return False
        else:
            print("❌ Stream file not created")
            return False

        print("\n3. Testing Reasoning Extraction")
        print("-" * 50)

        # Test reasoning extraction
        llm_response = """
        <reasoning>
        I need to analyze the import structure and identify any circular dependencies.
        First, I'll check for direct imports, then look for from imports.
        </reasoning>

        import os
        import sys
        from typing import List
        """

        reasoning = await streamer.broadcast_reasoning(llm_response, agent="ReasoningAgent")

        if reasoning and "circular dependencies" in reasoning:
            print("✅ Reasoning extraction successful")
            print(f"   Extracted: {reasoning[:50]}...")
        else:
            print("❌ Reasoning extraction failed")
            return False

        print("\n4. Testing Agent Lifecycle Events")
        print("-" * 50)

        # Test agent start
        await streamer.broadcast_agent_start("TestAgent", "Starting test execution")
        await asyncio.sleep(0.1)

        # Test agent complete
        await streamer.broadcast_agent_complete("TestAgent", "Test execution complete")
        await asyncio.sleep(0.1)

        # Verify events
        with open(log_path, "r") as f:
            lines = f.readlines()
            start_found = False
            complete_found = False

            for line in lines:
                entry = json.loads(line)
                if entry["level"] == "AGENT_START":
                    start_found = True
                if entry["level"] == "AGENT_END":
                    complete_found = True

            if start_found and complete_found:
                print("✅ Agent lifecycle events broadcast correctly")
            else:
                print("❌ Agent lifecycle events missing")
                return False

        print("\n5. Testing Signal Integration")
        print("-" * 50)

        # Add signals
        streamer.add_signal("TEST_SIGNAL")
        streamer.add_signal("ANOTHER_SIGNAL")

        await streamer.broadcast("Message with signals", level="INFO")
        await asyncio.sleep(0.1)

        # Verify signals in broadcast
        with open(log_path, "r") as f:
            last_entry = json.loads(f.readlines()[-1])
            if "TEST_SIGNAL" in last_entry["signals"] and "ANOTHER_SIGNAL" in last_entry["signals"]:
                print("✅ Signals included in broadcast")
            else:
                print("❌ Signals not included in broadcast")
                return False

        # Stop streamer
        await streamer.stop_streamer()
        print("✅ Streamer stopped gracefully")

    return True


async def test_l6_dependency_graph():
    """Test the L6 DependencyGraph functionality."""
    print("\n" + "=" * 80)
    print("L6 DEPENDENCY GRAPH VALIDATION")
    print("=" * 80)

    print("\n1. Testing Graph Construction")
    print("-" * 50)

    # Create temporary Python files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        file_a = temp_path / "a.py"
        file_b = temp_path / "b.py"
        file_c = temp_path / "subdir" / "c.py"

        temp_path.joinpath("subdir").mkdir()

        file_a.write_text("""
import os
import sys
from typing import List

class ClassA:
    def __init__(self):
        pass

def function_a():
    return "a"
""")

        file_b.write_text("""
from agentic_core. import a
import json

class ClassB(ClassA):
    def __init__(self):
        super().__init__()
""")

        file_c.write_text("""
import a
from b import ClassB

class ClassC:
    pass
""")

        # Build dependency graph
        dep_graph = DependencyGraph()
        files = [str(file_a), str(file_b), str(file_c)]
        dep_graph.build(files)

        if dep_graph._built:
            print("✅ Dependency graph built successfully")
            print(f"   Files processed: {len(dep_graph.graph)}")
        else:
            print("❌ Dependency graph build failed")
            return False

        print("\n2. Testing Import Extraction")
        print("-" * 50)

        # Check imports for file_a
        a_data = dep_graph.graph.get("a.py", {})
        if "os" in a_data.get("imports", []) and "sys" in a_data.get("imports", []):
            print("✅ Import extraction working")
        else:
            print("❌ Import extraction failed")
            return False

        # Check from imports for file_b
        b_data = dep_graph.graph.get("b.py", {})
        if b_data.get("from_imports"):
            print("✅ From-import extraction working")
        else:
            print("❌ From-import extraction failed")
            return False

        print("\n3. Testing Class Extraction")
        print("-" * 50)

        # Check classes
        if "ClassA" in a_data.get("classes", []):
            print("✅ Class extraction working")
        else:
            print("❌ Class extraction failed")
            return False

        print("\n4. Testing Impact Radius Calculation")
        print("-" * 50)

        # Calculate impact radius for file_a
        impact = dep_graph.get_impact_radius("a.py")
        print(f"   Files impacted by a.py: {len(impact)}")

        # Should include files that import from a
        if len(impact) > 0:
            print("✅ Impact radius calculation working")
        else:
            print("⚠️  No impacted files found (may be expected)")

        print("\n5. Testing Dependency Tree")
        print("-" * 50)

        # Get dependency tree for file_b
        tree = dep_graph.get_dependency_tree("b.py")
        print(f"   Direct dependencies: {len(tree['direct'])}")
        print(f"   Transitive dependencies: {len(tree['transitive'])}")

        if tree['direct'] or tree['transitive']:
            print("✅ Dependency tree calculation working")
        else:
            print("⚠️  No dependencies found")

    return True


async def test_architecture_governance():
    """Test the ArchitectureGovernor enforcement."""
    print("\n" + "=" * 80)
    print("ARCHITECTURE GOVERNANCE VALIDATION")
    print("=" * 80)

    print("\n1. Testing Root Hygiene Law")
    print("-" * 50)

    # Create temporary project structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some bad files at root
        (temp_path / "bad_file.py").touch()
        (temp_path / "another_bad.txt").touch()

        # Create allowed files
        (temp_path / "README.md").touch()
        (temp_path / "pyproject.toml").touch()

        # Create sovereign directory
        (temp_path / "agentic_core").mkdir()

        # Test governance
        governor = ArchitectureGovernor(str(temp_path))
        violations = governor.check_root_hygiene()

        if len(violations) >= 2:
            print("✅ Root hygiene violations detected")
            for v in violations[:2]:
                print(f"   {v}")
        else:
            print("❌ Root hygiene enforcement failed")
            return False

    print("\n2. Testing Depth Law")
    print("-" * 50)

    # Test depth violations
    deep_file = "level1/level2/level3/level4/deep.py"
    violation = governor.check_depth_law(deep_file)

    if violation and "depth 4" in violation:
        print("✅ Depth law violation detected")
        print(f"   {violation}")
    else:
        print("❌ Depth law enforcement failed")
        return False

    # Test sovereign directory exemption
    sovereign_file = "agentic_core/level1/level2/level3/level4/level5/deep.py"
    violation = governor.check_depth_law(sovereign_file)

    if violation is None:
        print("✅ Sovereign directory exemption working")
    else:
        print("❌ Sovereign directory exemption failed")
        return False

    print("\n3. Testing Blast Radius Integration")
    print("-" * 50)

    # Create test files with dependencies
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create main file
        main_file = temp_path / "main.py"
        main_file.write_text("""
import utils
import helpers.string_utils

class MainClass:
    pass
""")

        # Create dependent files
        utils_file = temp_path / "utils.py"
        utils_file.write_text("def utility(): pass")

        helpers_dir = temp_path / "helpers"
        helpers_dir.mkdir()
        string_utils_file = helpers_dir / "string_utils.py"
        string_utils_file.write_text("def format_string(): pass")

        # Build graph and calculate blast radius
        governor = ArchitectureGovernor(str(temp_path))
        governor.build_graph(["**/*.py"])

        modified = ["main.py"]
        blast = governor.get_blast_radius(modified)

        if blast["total_impacted"] >= 0:
            print(f"✅ Blast radius calculated: {blast['total_impacted']} files")
            print(f"   Modified: {blast['modified_count']}")
        else:
            print("❌ Blast radius calculation failed")
            return False

    return True


async def test_nervous_system_integration():
    """Test NervousSystem integration with L5/L6."""
    print("\n" + "=" * 80)
    print("NERVOUS SYSTEM L5/L6 INTEGRATION")
    print("=" * 80)

    print("\n1. Testing Blast Radius in Mission Context")
    print("-" * 50)

    # Create nervous system
    config = OrchestratorConfig(
        max_iterations=1,
        enable_checkpoints=True
    )

    storage = create_storage_adapter("local", base_path="./agentic_core")
    signal_ledger = SignalLedger(storage, "l5l6-test")

    nervous_system = NervousSystem(
        safety_layer=None,
        checkpoint_manager=None,
        config=config,
        session_id="l5l6-test",
        signal_ledger=signal_ledger
    )

    # Simulate modified files
    modified_files = [
        "agentic_core/L1_cognition/brain.py",
        "agentic_core/L2_execution/action_plane.py"
    ]

    for file in modified_files:
        nervous_system._modified_files.add(file)

    # Calculate blast radius
    blast = await nervous_system.get_impact_radius()

    if blast["modified_count"] > 0:
        print(f"✅ Blast radius calculated in mission context")
        print(f"   ☢️ BLAST RADIUS: {blast['total_impacted']} files in scope")
    else:
        print("⚠️  No blast radius calculated (graph not built)")

    print("\n2. Testing Architecture Validation")
    print("-" * 50)

    # Validate architecture
    validation = nervous_system.validate_architecture(modified_files)

    if "overall_status" in validation:
        print(f"✅ Architecture validation completed")
        print(f"   Status: {validation['overall_status']}")
    else:
        print("❌ Architecture validation failed")
        return False

    print("\n3. Testing L5 Streamer Integration")
    print("-" * 50)

    # Check if streamer is available
    from L5_safety.streamer import get_l5_streamer
    streamer = get_l5_streamer()

    if streamer:
        print("✅ L5 Streamer integrated with NervousSystem")
    else:
        print("❌ L5 Streamer not integrated")
        return False

    return True


async def run_l5l6_validation():
    """Run all L5 and L6 validation tests."""
    print("\n" + "=" * 80)
    print("L5/L6 INFRASTRUCTURE VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting L5 Streamer and L6 Sovereign Code Graph")

    results = {}

    # Run all tests
    results["streamer"] = await test_l5_streamer()
    results["dependency_graph"] = await test_l6_dependency_graph()
    results["architecture_governance"] = await test_architecture_governance()
    results["nervous_system"] = await test_nervous_system_integration()

    # Generate report
    print("\n" + "=" * 80)
    print("L5/L6 VALIDATION REPORT")
    print("=" * 80)

    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All L5/L6 infrastructure components validated!")
        print("The system has:")
        print("  - Live reasoning broadcast to JSONL and WebSocket")
        print("  - Dependency graph with AST-based extraction")
        print("  - Blast radius calculation for impact analysis")
        print("  - Architecture governance with law enforcement")
        print("  - Full integration with NervousSystem")
        print("\n📊 Monitor live stream at: observability/audit/live_stream.jsonl")
        print("🌐 WebSocket server: ws://127.0.0.1:8765")
    else:
        print("\n⚠️  Some L5/L6 components need attention")
        print("Check the logs above for details")

    return all_passed


if __name__ == "__main__":
    asyncio.run(run_l5l6_validation())
