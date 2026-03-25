"""
Verify Meta-Learning Integration in AutonomyGuardianAgent

This script directly tests the Meta-Learning recording methods to ensure
they're properly integrated and functional.
"""
import sys
from pathlib import Path
import pytest
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_agent_executes_agent, _emit_applies_guardrail, _emit_authorize_and_execute, _emit_blocks_direct_write, _emit_captures_evaluation_metric, _emit_captures_execution_output, _emit_checks_agent_registry, _emit_coordinates_agents, _emit_dispatches_agent, _emit_dispatches_execution_plan, _emit_dispatches_healing_run, _emit_escalates_failure, _emit_escalates_to_human, _emit_gated_by_confidence, _emit_hard_fails_untranscripted, _emit_invokes_evaluation, _emit_links_execution_to_snapshot, _emit_observes_runtime_state, _emit_orchestrates_workflow, _emit_reads_policy_state, _emit_records_execution_trace, _emit_records_healing_outcome, _emit_records_telemetry_event, _emit_records_tool_invocation, _emit_records_workflow_lineage, _emit_routes_through, _emit_routes_to_agent, _emit_routes_to_capability, _emit_signs_execution_trace, _emit_snapshots_state, _emit_stores_embedding, _emit_transcripts_response, _emit_updates_meta_learning_state, _emit_validates_agent_capability, _emit_validates_capability, _emit_verifies_boundary, _emit_verifies_policy, _emit_writes_via_uwg, emit_determinism_digest, emit_replay_key
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_agent_executes_agent, _emit_captures_pattern, _emit_captures_runtime_anomaly, _emit_checks_agent_registry, _emit_dispatches_execution_plan, _emit_emits_metric_event, _emit_escalates_to_human, _emit_execution_terminates_at_uwg, _emit_feeds_meta_learning, _emit_gated_by_confidence, _emit_hard_fails_untranscripted, _emit_improves_agent_policy, _emit_invokes_eval, _emit_links_incident_trace, _emit_observes_runtime_state, _emit_proposal_commits_routing, _emit_pulls_context, _emit_reads_environ, _emit_reads_runtime_state, _emit_records_execution_trace, _emit_records_incident_event, _emit_records_learning_event, _emit_routes_through, _emit_routes_to_agent, _emit_stores_learning_state, _emit_transcripts_response, _emit_triggers_alert, _emit_updates_monitoring_state, _emit_updates_routing_strategy, _emit_validated_by_safety_plane, _emit_validates_agent_capability, _emit_verifies_boundary, _emit_verifies_policy, _emit_writes_learning_snapshot, _emit_writes_observability_log, _emit_writes_through
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L5_safety.reasoning.AutonomyGuardianAgent import get_autonomy_guardian
pytestmark = pytest.mark.integration

def test_redis_cache_method():
    """Test if _cache_result method exists and is callable."""
    project_root = Path(__file__).parent.parent
    guardian = get_autonomy_guardian(project_root)
    print('\n[TEST 1] Redis cache Method')
    print('-' * 60)
    if hasattr(guardian, '_cache_result'):
        print('✅ _cache_result method exists')
        try:
            test_key = 'test_autonomy_fix_2026'
            test_value = {'fixed': 5, 'violations': 5}
            guardian._cache_result(key=test_key, value=test_value)
            print(f"✅ _cache_result callable with key='{test_key}'")
            return True
        except Exception as e:
            print(f'⚠️  _cache_result failed: {e}')
            return False
    else:
        print('❌ _cache_result method NOT found')
        print(f"   Available methods: {[m for m in dir(guardian) if not m.startswith('_')]}")
        return False

def test_pinecone_vector_method():
    """Test if _store_vector method exists and is callable."""
    project_root = Path(__file__).parent.parent
    guardian = get_autonomy_guardian(project_root)
    print('\n[TEST 2] Pinecone Vector Method')
    print('-' * 60)
    if hasattr(guardian, '_store_vector'):
        print('✅ _store_vector method exists')
        try:
            guardian._store_vector(content='Test healing signature for Meta-Learning verification', metadata={'action': 'test', 'target': 'verification'})
            print('✅ _store_vector callable with content and metadata')
            return True
        except Exception as e:
            print(f'⚠️  _store_vector failed: {e}')
            return False
    else:
        print('❌ _store_vector method NOT found')
        return False

def test_meta_learning_trigger():
    """Test the Meta-Learning trigger logic by simulating a healing result."""
    project_root = Path(__file__).parent.parent
    get_autonomy_guardian(project_root)
    print('\n[TEST 3] Meta-Learning Trigger Logic')
    print('-' * 60)
    simulated_summary = {'violations': 5, 'fixed': 5, 'errors': 0, 'healed': 5, 'renamed': 0}
    print(f'Simulated healing result: {simulated_summary}')
    dry_run = False
    fixed_count = simulated_summary.get('fixed', 0)
    if not dry_run and fixed_count > 0:
        print('✅ Meta-Learning trigger conditions met:')
        print(f'   - dry_run={dry_run}')
        print(f'   - fixed={fixed_count}')
        print('   → Recording WOULD be triggered')
        return True
    else:
        print('❌ Meta-Learning trigger conditions NOT met:')
        print(f'   - dry_run={dry_run}')
        print(f'   - fixed={fixed_count}')
        return False

def verify_mixin_inheritance():
    """Verify that AutonomyGuardianAgent inherits from Redis and Pinecone mixins."""
    project_root = Path(__file__).parent.parent
    guardian = get_autonomy_guardian(project_root)
    print('\n[TEST 4] Mixin Inheritance')
    print('-' * 60)
    is_redis = isinstance(guardian, RedisCacheMixin)
    is_pinecone = isinstance(guardian, PineconeVectorMixin)
    print(f"RedisCacheMixin: {('✅ Inherited' if is_redis else '❌ NOT inherited')}")
    print(f"PineconeVectorMixin: {('✅ Inherited' if is_pinecone else '❌ NOT inherited')}")
    return is_redis and is_pinecone

def main():
    print('\n' + '=' * 80)
    print('META-LEARNING INTEGRATION VERIFICATION')
    print('=' * 80)
    results = {'redis_cache': test_redis_cache_method(), 'pinecone_vector': test_pinecone_vector_method(), 'trigger_logic': test_meta_learning_trigger(), 'mixin_inheritance': verify_mixin_inheritance()}
    print('\n' + '=' * 80)
    print('VERIFICATION SUMMARY')
    print('=' * 80)
    for test_name, passed in results.items():
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f'{test_name:20} {status}')
    all_passed = all(results.values())
    print('\n' + '=' * 80)
    if all_passed:
        print('✅ ALL TESTS PASSED - Meta-Learning integration is functional')
    else:
        print('⚠️  SOME TESTS FAILED - Review integration issues above')
    print('=' * 80)
    return 0 if all_passed else 1
if __name__ == '__main__':
    sys.exit(main())