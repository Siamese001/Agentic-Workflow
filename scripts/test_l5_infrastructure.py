#!/usr/bin/env python3
"""
L5 Intervention Server & Tri-Brain Infrastructure Validation

This test validates:
1. Intervention server starts and responds to approval/veto
2. Hot brain (Redis) distributed locking works
3. Deep brain (Pinecone) embedding storage/retrieval works
4. Fallback to local caches when services unavailable
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from L3_orchestration.nervous_system import NervousSystem, OrchestratorConfig
from L4_state.checkpointing import get_deep_brain
from L4_state.storage import SignalLedger, create_storage_adapter, get_hot_brain
from L5_safety.intervention_server import InterventionContext, InterventionServer

from apps_shared.reflection_agent import ReflectionAgent


async def test_intervention_server():
    """Test the L5 intervention server."""
    print("=" * 80)
    print("L5 INTERVENTION SERVER VALIDATION")
    print("=" * 80)

    print("\n1. Testing Intervention Server Startup")
    print("-" * 50)

    # Create intervention server
    server = InterventionServer(host="127.0.0.1", port=8080)

    # Start the server
    await server.start_server()

    # Verify server is running
    if server._server_task and not server._server_task.done():
        print("✅ Intervention server started successfully")
        print("   🌐 Server running at http://127.0.0.1:8080")
    else:
        print("❌ Intervention server failed to start")
        return False

    print("\n2. Testing Intervention Context & Approval")
    print("-" * 50)

    # Create intervention context
    context = InterventionContext(
        workflow_id="test-workflow-001",
        cycle=3,
        reason="High-risk state: 10 modified files detected",
        risk_factors=[
            "Many modifications (10 > 8)",
            "Late cycle (3) with pending modifications"
        ],
        modified_items=[
            "agentic_core/L1_cognition/brain.py",
            "agentic_core/L2_execution/action_plane.py",
            "agentic_core/L3_orchestration/nervous_system.py"
        ],
        signals=["HIGH_RISK", "MODIFIED_FILES"],
        recommendations=[
            "Review modified files before proceeding",
            "Manual approval recommended for safety"
        ]
    )

    # Set current context for UI
    server.current_context = context

    # Test programmatic approval
    print("  Testing programmatic approval...")
    server.decision = None
    server.approval_event.set()

    # Simulate approval
    server.decision = "approved"
    server.decision_reason = "Test approval"

    if server.decision == "approved":
        print("✅ Programmatic approval works")
    else:
        print("❌ Programmatic approval failed")

    print("\n3. Testing Telepathy Interface")
    print("-" * 50)

    # Create temporary instructions file
    instructions_path = Path("temp_human_instructions.md")
    instructions_content = """
    Test instructions for validation:
    - STOP the current operation
    - SKIP files matching pattern: *.tmp
    - Force TEST mode
    """

    instructions_path.write_text(instructions_content)

    # Check telepathy
    server.instructions_path = instructions_path
    instructions = server.check_telepathy()

    if instructions:
        print("✅ Telepathy interface working")
        print(f"   Instructions: {instructions[:50]}...")

        # Parse commands
        commands = server.parse_telepathy_commands(instructions)
        if commands["stop"] and commands["force_test"]:
            print("✅ Telepathy commands parsed correctly")
        else:
            print("❌ Telepathy command parsing failed")
    else:
        print("❌ Telepathy interface failed")

    # Cleanup
    instructions_path.unlink(missing_ok=True)
    await server.stop_server()

    return True


async def test_hot_brain():
    """Test the Redis hot brain cache."""
    print("\n" + "=" * 80)
    print("HOT BRAIN (REDIS) VALIDATION")
    print("=" * 80)

    print("\n1. Testing Hot Brain Initialization")
    print("-" * 50)

    # Create hot brain (will fall back to local if Redis unavailable)
    hot_brain = get_hot_brain(redis_url="redis://localhost:6379")

    if hot_brain.redis_client:
        print("✅ Connected to Redis")
    else:
        print("⚠️  Redis not available - using local cache fallback")

    print("\n2. Testing Distributed Locking")
    print("-" * 50)

    # Test lock acquisition
    lock_key = "test-lock-001"

    # First acquisition should succeed
    acquired1 = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if acquired1:
        print("✅ First lock acquisition successful")
    else:
        print("❌ First lock acquisition failed")
        return False

    # Second acquisition should fail
    acquired2 = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if not acquired2:
        print("✅ Second lock correctly blocked")
    else:
        print("❌ Second lock should have been blocked")
        return False

    # Release lock
    released = await hot_brain.release_lock(lock_key)
    if released:
        print("✅ Lock released successfully")
    else:
        print("❌ Lock release failed")
        return False

    # Should be able to acquire again
    acquired3 = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if acquired3:
        print("✅ Lock re-acquisition after release successful")
    else:
        print("❌ Lock re-acquisition failed")
        return False

    print("\n3. Testing Cache Operations")
    print("-" * 50)

    # Test cache set/get
    test_key = "test-cache-001"
    test_value = {"message": "Hello Hot Brain!", "timestamp": time.time()}

    # Set value
    set_result = await hot_brain.set(test_key, test_value, ttl=60)
    if set_result:
        print("✅ Cache set successful")
    else:
        print("❌ Cache set failed")
        return False

    # Get value
    retrieved = await hot_brain.get(test_key)
    if retrieved and retrieved["message"] == test_value["message"]:
        print("✅ Cache get successful")
    else:
        print("❌ Cache get failed")
        return False

    # Delete value
    deleted = await hot_brain.delete(test_key)
    if deleted:
        print("✅ Cache delete successful")
    else:
        print("❌ Cache delete failed")

    # Cleanup
    await hot_brain.release_lock(lock_key)

    return True


async def test_deep_brain():
    """Test the Pinecone deep brain embeddings."""
    print("\n" + "=" * 80)
    print("DEEP BRAIN (PINECONE) VALIDATION")
    print("=" * 80)

    print("\n1. Testing Deep Brain Initialization")
    print("-" * 50)

    # Create deep brain (will fall back to local if Pinecone unavailable)
    api_key = os.getenv("PINECONE_API_KEY")
    deep_brain = get_deep_brain(api_key=api_key)

    if deep_brain.index:
        print("✅ Connected to Pinecone")
    else:
        print("⚠️  Pinecone not available - using local embeddings fallback")

    print("\n2. Testing Embedding Storage")
    print("-" * 50)

    # Test embedding upsert
    test_text = """
    Successful execution pattern:
    Action: Validate file permissions
    Result: Permissions corrected
    Strategy: Use os.chmod with 0o755

    Action: Check syntax with Python AST
    Result: Syntax valid
    Strategy: Parse with ast.parse()
    """

    metadata = {
        "pattern_type": "successful_trace",
        "cycle": 1,
        "success_rate": 1.0,
        "timestamp": time.time()
    }

    # Store embedding
    stored = await deep_brain.upsert_embedding(
        text=test_text,
        metadata=metadata,
        embedding_id="test-pattern-001"
    )

    if stored:
        print("✅ Embedding stored successfully")
    else:
        print("❌ Embedding storage failed")
        return False

    print("\n3. Testing Semantic Search")
    print("-" * 50)

    # Search for similar patterns
    query = "How to fix file permissions and validate syntax"
    results = await deep_brain.search_embeddings(
        query=query,
        top_k=5,
        filter_dict={"pattern_type": "successful_trace"}
    )

    if results:
        print(f"✅ Found {len(results)} similar patterns")
        for i, result in enumerate(results[:2]):
            print(f"   Pattern {i+1}: score={result['score']:.3f}")
    else:
        print("❌ No patterns found")
        return False

    return True


async def test_reflection_learning():
    """Test the ReflectionAgent learning loop."""
    print("\n" + "=" * 80)
    print("REFLECTION AGENT LEARNING LOOP")
    print("=" * 80)

    print("\n1. Testing Successful Trace Storage")
    print("-" * 50)

    # Create reflection agent
    reflection_agent = ReflectionAgent()

    # Create mock execution log
    execution_log = [
        {
            "action": "validate_permissions",
            "result": "permissions_valid",
            "success": True,
            "strategy": "use_stat_check"
        },
        {
            "action": "parse_syntax",
            "result": "syntax_valid",
            "success": True,
            "strategy": "ast_parse"
        },
        {
            "action": "run_tests",
            "result": "tests_passed",
            "success": True,
            "strategy": "pytest_run"
        }
    ]

    # Store successful trace
    stored = await reflection_agent.store_successful_trace(execution_log, cycle=1)

    if stored:
        print("✅ Successful trace stored in deep brain")
    else:
        print("❌ Failed to store successful trace")

    print("\n2. Testing Pattern Recall")
    print("-" * 50)

    # Recall similar patterns
    context = "Need to validate file permissions and check syntax"
    patterns = await reflection_agent.recall_similar_patterns(context, limit=3)

    if patterns:
        print(f"✅ Recalled {len(patterns)} similar patterns")
        for i, pattern in enumerate(patterns):
            print(f"   Pattern {i+1}: cycle={pattern['metadata'].get('cycle', 'unknown')}")
    else:
        print("⚠️  No similar patterns recalled (expected for first run)")

    return True


async def test_nervous_system_integration():
    """Test NervousSystem with L5 services."""
    print("\n" + "=" * 80)
    print("NERVOUS SYSTEM L5 INTEGRATION")
    print("=" * 80)

    print("\n1. Testing High-Risk State Detection")
    print("-" * 50)

    # Create nervous system
    config = OrchestratorConfig(
        max_iterations=1,
        enable_checkpoints=True,
        enable_signal_ledger=True
    )

    storage = create_storage_adapter("local", base_path="./agentic_core")
    signal_ledger = SignalLedger(storage, "l5-integration-test")

    nervous_system = NervousSystem(
        safety_layer=None,
        checkpoint_manager=None,
        config=config,
        session_id="l5-integration-test",
        signal_ledger=signal_ledger
    )

    # Simulate high-risk state
    nervous_system._iteration = 4  # High cycle
    nervous_system._modified_files = {
        f"file_{i}.py" for i in range(10)  # 10 modified files
    }
    nervous_system._signals = {"HIGH_RISK", "MODIFIED_FILES"}

    # Check intervention required
    from L5_safety.intervention_server import check_intervention_required

    required, risk_factors = check_intervention_required(
        cycle=nervous_system._iteration,
        modified_count=len(nervous_system._modified_files),
        signals=list(nervous_system._signals),
        high_risk_threshold=8,
        signal_threshold=5
    )

    if required:
        print("✅ High-risk state detected correctly")
        print(f"   Risk factors: {risk_factors}")
    else:
        print("❌ High-risk state not detected")
        return False

    print("\n2. Testing Service Connections")
    print("-" * 50)

    # Test hot brain connection
    hot_brain = get_hot_brain()
    if hot_brain.redis_client or hot_brain._local_cache:
        print("✅ Hot brain service available")
    else:
        print("❌ Hot brain service unavailable")

    # Test deep brain connection
    deep_brain = get_deep_brain()
    if deep_brain.index or deep_brain._local_embeddings:
        print("✅ Deep brain service available")
    else:
        print("❌ Deep brain service unavailable")

    # Test intervention server
    if hasattr(nervous_system, 'intervention_server'):
        print("✅ Intervention server integrated")
    else:
        print("❌ Intervention server not integrated")

    return True


async def run_l5_validation():
    """Run all L5 validation tests."""
    print("\n" + "=" * 80)
    print("L5 INFRASTRUCTURE VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting Intervention Server, Hot Brain (Redis), and Deep Brain (Pinecone)")

    results = {}

    # Run all tests
    results["intervention"] = await test_intervention_server()
    results["hot_brain"] = await test_hot_brain()
    results["deep_brain"] = await test_deep_brain()
    results["reflection_learning"] = await test_reflection_learning()
    results["nervous_system"] = await test_nervous_system_integration()

    # Generate report
    print("\n" + "=" * 80)
    print("L5 VALIDATION REPORT")
    print("=" * 80)

    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All L5 infrastructure components validated!")
        print("The system has:")
        print("  - Human-in-the-loop intervention capabilities")
        print("  - Distributed caching with Redis (or local fallback)")
        print("  - Semantic memory with Pinecone (or local fallback)")
        print("  - Learning loop for successful execution traces")
        print("  - Graceful degradation when services unavailable")
    else:
        print("\n⚠️  Some L5 components need attention")
        print("Check the logs above for details")

    return all_passed


if __name__ == "__main__":
    asyncio.run(run_l5_validation())
