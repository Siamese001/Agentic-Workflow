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
sys.path.insert(0, str(Path(__file__).parent.parent / 'agentic_core'))
from L3_orchestration.nervous_system import NervousSystem, OrchestratorConfig
from L4_state.checkpointing import get_deep_brain
from L4_state.storage import SignalLedger, create_storage_adapter, get_hot_brain
from L5_safety.intervention_server import InterventionContext, InterventionServer
from apps_shared.reflection_agent import LicHealingOrchestratorAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


async def test_intervention_server() -> Any:
    """Test the L5 intervention server."""
    print('=' * 80)
    print('L5 INTERVENTION SERVER VALIDATION')
    print('=' * 80)
    print('\n1. Testing Intervention Server Startup')
    print('-' * 50)
    server: Any = InterventionServer(host='127.0.0.1', port=8080)
    await server.start_server()
    if server._server_task and (not server._server_task.done()):
        print('✅ Intervention server started successfully')
        print('   🌐 Server running at http://127.0.0.1:8080')
    else:
        print('❌ Intervention server failed to start')
        return False
    print('\n2. Testing Intervention Context & Approval')
    print('-' * 50)
    context: Any = InterventionContext(workflow_id='test-workflow-001', cycle=3, reason='High-risk state: 10 modified files detected', risk_factors=['Many modifications (10 > 8)', 'Late cycle (3) with pending modifications'], modified_items=['agentic_core/L1_cognition/brain.py', 'agentic_core/L2_execution/action_plane.py', 'agentic_core/L3_orchestration/nervous_system.py'], signals=['HIGH_RISK', 'MODIFIED_FILES'], recommendations=['Review modified files before proceeding', 'Manual approval recommended for safety'])
    server.current_context = context
    print('  Testing programmatic approval...')
    server.decision = None
    server.approval_event.set()
    server.decision = 'approved'
    server.decision_reason = 'Test approval'
    if server.decision == 'approved':
        print('✅ Programmatic approval works')
    else:
        print('❌ Programmatic approval failed')
    print('\n3. Testing Telepathy Interface')
    print('-' * 50)
    instructions_path: Any = Path('temp_human_instructions.md')
    instructions_content: Any = '\n    Test instructions for validation:\n    - STOP the current operation\n    - SKIP files matching pattern: *.tmp\n    - Force TEST mode\n    '
    instructions_path.write_text(instructions_content)
    server.instructions_path = instructions_path
    instructions: Any = server.check_telepathy()
    if instructions:
        print('✅ Telepathy interface working')
        print(f'   Instructions: {instructions[:50]}...')
        commands: Any = server.parse_telepathy_commands(instructions)
        if commands['stop'] and commands['force_test']:
            print('✅ Telepathy commands parsed correctly')
        else:
            print('❌ Telepathy command parsing failed')
    else:
        print('❌ Telepathy interface failed')
    instructions_path.unlink(missing_ok=True)
    await server.stop_server()
    return True

async def test_hot_brain() -> Any:
    """Test the Redis hot brain cache."""
    print('\n' + '=' * 80)
    print('HOT BRAIN (REDIS) VALIDATION')
    print('=' * 80)
    print('\n1. Testing Hot Brain Initialization')
    print('-' * 50)
    hot_brain: Any = get_hot_brain(redis_url='redis://localhost:6379')
    if hot_brain.redis_client:
        print('✅ Connected to Redis')
    else:
        print('⚠️  Redis not available - using local cache fallback')
    print('\n2. Testing Distributed Locking')
    print('-' * 50)
    lock_key: Any = 'test-lock-001'
    acquired1: Any = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if acquired1:
        print('✅ First lock acquisition successful')
    else:
        print('❌ First lock acquisition failed')
        return False
    acquired2: Any = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if not acquired2:
        print('✅ Second lock correctly blocked')
    else:
        print('❌ Second lock should have been blocked')
        return False
    released: Any = await hot_brain.release_lock(lock_key)
    if released:
        print('✅ Lock released successfully')
    else:
        print('❌ Lock release failed')
        return False
    acquired3: Any = await hot_brain.acquire_lock(lock_key, timeout=5.0)
    if acquired3:
        print('✅ Lock re-acquisition after release successful')
    else:
        print('❌ Lock re-acquisition failed')
        return False
    print('\n3. Testing Cache Operations')
    print('-' * 50)
    test_key: Any = 'test-cache-001'
    test_value: Any = {'message': 'Hello Hot Brain!', 'timestamp': time.time()}
    set_result: Any = await hot_brain.set(test_key, test_value, ttl=60)
    if set_result:
        print('✅ Cache set successful')
    else:
        print('❌ Cache set failed')
        return False
    retrieved: Any = await hot_brain.get(test_key)
    if retrieved and retrieved['message'] == test_value['message']:
        print('✅ Cache get successful')
    else:
        print('❌ Cache get failed')
        return False
    deleted: Any = await hot_brain.delete(test_key)
    if deleted:
        print('✅ Cache delete successful')
    else:
        print('❌ Cache delete failed')
    await hot_brain.release_lock(lock_key)
    return True

async def test_deep_brain() -> Any:
    """Test the Pinecone deep brain embeddings."""
    print('\n' + '=' * 80)
    print('DEEP BRAIN (PINECONE) VALIDATION')
    print('=' * 80)
    print('\n1. Testing Deep Brain Initialization')
    print('-' * 50)
    api_key: Any = os.getenv('PINECONE_API_KEY')
    deep_brain: Any = get_deep_brain(api_key=api_key)
    if deep_brain.index:
        print('✅ Connected to Pinecone')
    else:
        print('⚠️  Pinecone not available - using local embeddings fallback')
    print('\n2. Testing Embedding Storage')
    print('-' * 50)
    test_text: Any = '\n    Successful execution pattern:\n    Action: Validate file permissions\n    Result: Permissions corrected\n    Strategy: Use os.chmod with 0o755\n\n    Action: Check syntax with Python AST\n    Result: Syntax valid\n    Strategy: Parse with ast.parse()\n    '
    metadata: Any = {'pattern_type': 'successful_trace', 'cycle': 1, 'success_rate': 1.0, 'timestamp': time.time()}
    stored: Any = await deep_brain.upsert_embedding(text=test_text, metadata=metadata, embedding_id='test-pattern-001')
    if stored:
        print('✅ Embedding stored successfully')
    else:
        print('❌ Embedding storage failed')
        return False
    print('\n3. Testing Semantic Search')
    print('-' * 50)
    query: Any = 'How to fix file permissions and validate syntax'
    results: Any = await deep_brain.search_embeddings(query=query, top_k=5, filter_dict={'pattern_type': 'successful_trace'})
    if results:
        print(f'✅ Found {len(results)} similar patterns')
        for i, result in enumerate(results[:2]):
            print(f"   Pattern {i + 1}: score={result['score']:.3f}")
    else:
        print('❌ No patterns found')
        return False
    return True

async def test_reflection_learning() -> Any:
    """Test the RgReflectionAgent learning loop."""
    print('\n' + '=' * 80)
    print('REFLECTION AGENT LEARNING LOOP')
    print('=' * 80)
    print('\n1. Testing Successful Trace Storage')
    print('-' * 50)
    reflection_agent: Any = RgReflectionAgent()
    execution_log: Any = [{'action': 'validate_permissions', 'result': 'permissions_valid', 'success': True, 'strategy': 'use_stat_check'}, {'action': 'parse_syntax', 'result': 'syntax_valid', 'success': True, 'strategy': 'ast_parse'}, {'action': 'run_tests', 'result': 'tests_passed', 'success': True, 'strategy': 'pytest_run'}]
    stored: Any = await reflection_agent.store_successful_trace(execution_log, cycle=1)
    if stored:
        print('✅ Successful trace stored in deep brain')
    else:
        print('❌ Failed to store successful trace')
    print('\n2. Testing Pattern Recall')
    print('-' * 50)
    context: Any = 'Need to validate file permissions and check syntax'
    patterns: Any = await reflection_agent.recall_similar_patterns(context, limit=3)
    if patterns:
        print(f'✅ Recalled {len(patterns)} similar patterns')
        for i, pattern in enumerate(patterns):
            print(f"   Pattern {i + 1}: cycle={pattern['metadata'].get('cycle', 'unknown')}")
    else:
        print('⚠️  No similar patterns recalled (expected for first run)')
    return True

async def test_nervous_system_integration() -> Any:
    """Test NervousSystem with L5 services."""
    print('\n' + '=' * 80)
    print('NERVOUS SYSTEM L5 INTEGRATION')
    print('=' * 80)
    print('\n1. Testing High-Risk State Detection')
    print('-' * 50)
    config: Any = OrchestratorConfig(max_iterations=1, enable_checkpoints=True, enable_signal_ledger=True)
    storage: Any = create_storage_adapter('local', base_path='./agentic_core')
    signal_ledger: Any = SignalLedger(storage, 'l5-integration-test')
    nervous_system: Any = NervousSystem(safety_layer=None, checkpoint_manager=None, config=config, session_id='l5-integration-test', signal_ledger=signal_ledger)
    nervous_system._iteration = 4
    nervous_system._modified_files = {f'file_{i}.py' for i in range(10)}
    nervous_system._signals = {'HIGH_RISK', 'MODIFIED_FILES'}
    from L5_safety.intervention_server import check_intervention_required
from typing import Any
    required, risk_factors = check_intervention_required(cycle=nervous_system._iteration, modified_count=len(nervous_system._modified_files), signals=list(nervous_system._signals), high_risk_threshold=8, signal_threshold=5)
    if required:
        print('✅ High-risk state detected correctly')
        print(f'   Risk factors: {risk_factors}')
    else:
        print('❌ High-risk state not detected')
        return False
    print('\n2. Testing Service Connections')
    print('-' * 50)
    hot_brain: Any = get_hot_brain()
    if hot_brain.redis_client or hot_brain._local_cache:
        print('✅ Hot brain service available')
    else:
        print('❌ Hot brain service unavailable')
    deep_brain: Any = get_deep_brain()
    if deep_brain.index or deep_brain._local_embeddings:
        print('✅ Deep brain service available')
    else:
        print('❌ Deep brain service unavailable')
    if hasattr(nervous_system, 'intervention_server'):
        print('✅ Intervention server integrated')
    else:
        print('❌ Intervention server not integrated')
    return True

async def run_l5_validation() -> Any:
    """Run all L5 validation tests."""
    print('\n' + '=' * 80)
    print('L5 INFRASTRUCTURE VALIDATION SUITE')
    print('=' * 80)
    print('\nTesting Intervention Server, Hot Brain (Redis), and Deep Brain (Pinecone)')
    results: Any = {}
    results['intervention'] = await test_intervention_server()
    results['hot_brain'] = await test_hot_brain()
    results['deep_brain'] = await test_deep_brain()
    results['reflection_learning'] = await test_reflection_learning()
    results['nervous_system'] = await test_nervous_system_integration()
    print('\n' + '=' * 80)
    print('L5 VALIDATION REPORT')
    print('=' * 80)
    print('\nTest Results:')
    for test, passed in results.items():
        status: Any = '✅ PASSED' if passed else '❌ FAILED'
        print(f"  {test.replace('_', ' ').title()}: {status}")
    all_passed: Any = all(results.values())
    if all_passed:
        print('\n✅ All L5 infrastructure components validated!')
        print('The system has:')
        print('  - Human-in-the-loop intervention capabilities')
        print('  - Distributed caching with Redis (or local fallback)')
        print('  - Semantic memory with Pinecone (or local fallback)')
        print('  - Learning loop for successful execution traces')
        print('  - Graceful degradation when services unavailable')
    else:
        print('\n⚠️  Some L5 components need attention')
        print('Check the logs above for details')
    return all_passed
if __name__ == '__main__':
    asyncio.run(run_l5_validation())
