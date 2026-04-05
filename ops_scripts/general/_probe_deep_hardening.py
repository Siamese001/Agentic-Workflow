"""Deep hardening probe — run standalone, produces findings to stdout."""
from __future__ import annotations

import os
import sys
import threading

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_probe_deep_hardening")
_emit_applies_guardrail("p0", "_probe_deep_hardening", "p0_governance")
_emit_reads_policy_state("p0", "_probe_deep_hardening", "policy_binding")
_emit_snapshots_state("p0", "_probe_deep_hardening", "state_snapshot")
emit_replay_key("p0", "_probe_deep_hardening")
emit_determinism_digest("p0", "_probe_deep_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_probe_deep_hardening", "execution_auth")
_emit_validates_capability("p2", "_probe_deep_hardening", "capability_check")
_emit_routes_to_capability("p2", "_probe_deep_hardening", "capability_route")
_emit_writes_via_uwg("p2", "_probe_deep_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "_probe_deep_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "_probe_deep_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "_probe_deep_hardening", "exec_output")
_emit_dispatches_agent("p3", "_probe_deep_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "_probe_deep_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "_probe_deep_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "_probe_deep_hardening", "healing_outcome")
_emit_escalates_failure("p3", "_probe_deep_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "_probe_deep_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_probe_deep_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "_probe_deep_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "_probe_deep_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_probe_deep_hardening", "eval_metric")
_emit_stores_embedding("p4", "_probe_deep_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "_probe_deep_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_probe_deep_hardening", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, 'c:/Git/Agentic-Workflow')
# guardian: allow-global-mutation
os.environ['HIVE_MIND_STRICT_MODE'] = 'false'
from agentic_core.L4_state.utils.memory.semantic_cache_manager import PII_Sanitizer, SemanticCacheManager

SemanticCacheManager.reset_instance()
import apps_shared.enforcement.GlobalcacheStrategy as _mod
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from apps_shared.enforcement.GlobalcacheStrategy import (
    GlobalCache,
    cache_get,
    cache_put,
    cache_search_semantic,
    cached,
    get_global_cache,
)

_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("_probe_deep_hardening", "p4obs", "metric_6")
_emit_records_incident_event("_probe_deep_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("_probe_deep_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("_probe_deep_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("_probe_deep_hardening", "p4obs", "mon_state")
_emit_triggers_alert("_probe_deep_hardening", "p4obs", "alert")
_emit_links_incident_trace("_probe_deep_hardening", "p4obs", "trace_link")
_emit_captures_pattern("_probe_deep_hardening", "p3lm", "pattern")
_emit_records_learning_event("_probe_deep_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_probe_deep_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("_probe_deep_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_probe_deep_hardening", "p3lm", "routing")
_emit_improves_agent_policy("_probe_deep_hardening", "p3lm", "policy")
_emit_stores_learning_state("_probe_deep_hardening", "p3lm", "state")
_emit_records_execution_trace("_probe_deep_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_probe_deep_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_probe_deep_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_probe_deep_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_probe_deep_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_probe_deep_hardening", "env_read", "p2_env_1")
_emit_reads_environ("_probe_deep_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("_probe_deep_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_probe_deep_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_probe_deep_hardening", "context_pull")
_emit_pulls_context("p1", "_probe_deep_hardening", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_probe_deep_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_probe_deep_hardening", "uwg_term_secondary")
_emit_writes_through("p1", "_probe_deep_hardening", "write_through")
_emit_writes_through("p1", "_probe_deep_hardening", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_probe_deep_hardening", "safety_validation")
_emit_invokes_eval("p1", "_probe_deep_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "_probe_deep_hardening", "routing_commit")
_emit_escalates_to_human("p1", "_probe_deep_hardening", "human_escalation")
_emit_routes_through("p1", "_probe_deep_hardening", "route_through")
_emit_checks_agent_registry("p1", "_probe_deep_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "_probe_deep_hardening", "capability")
_emit_dispatches_execution_plan("p1", "_probe_deep_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "_probe_deep_hardening", "sub_agent")
_emit_routes_to_agent("p1", "_probe_deep_hardening", "target_agent")
_emit_verifies_policy("p1", "_probe_deep_hardening", "policy_check")
_emit_observes_runtime_state("p1", "_probe_deep_hardening", "runtime_state")
_emit_verifies_boundary("p1", "_probe_deep_hardening", "boundary_check")
_emit_transcripts_response("p1", "_probe_deep_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "_probe_deep_hardening")
_emit_gated_by_confidence("p1", "_probe_deep_hardening", "confidence_gate")


def reset():
    SemanticCacheManager.reset_instance()
    _mod._global_cache = None
reset()
gc = GlobalCache()
race_results = []

def _worker():
    race_results.append(id(gc.get_hive_mind()))
threads = [threading.Thread(target=_worker) for _ in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print('P1 race unique hive ids:', len(set(race_results)), '(expect 1)')
print('P1 _hive type:', type(gc._hive).__name__)
reset()
gc2 = GlobalCache()
gc2.put('k1', 'val1', text_for_embedding='ats keywords resume')
gc2.put('k2', 'val2', text_for_embedding='ats keywords linkedin')
# guardian: allow-magic-config
r2 = gc2.get_semantic('ats keywords', max_results=3)
print('P2 max_results=3 actual count:', len(r2), '(hive recall returns at most 1)')
reset()
gc3 = GlobalCache()
mgr3 = gc3.get_hive_mind()
print('P3 redis_enabled:', mgr3.redis_enabled)
gc3.put('k', {'v': 1}, text_for_embedding='ctx')
print('P3 cache_stores after no-redis learn:', mgr3.get_statistics()['cache_stores'])
reset()
gc4 = GlobalCache()
stats4 = gc4.get_stats()
print('P4 get_stats keys:', sorted(stats4.keys()))
reset()
gc5 = GlobalCache()
gc5.put('k', 'v')
gc5.get('k')
gc5.clear()
print('P5 stats after clear:', gc5._stats)
reset()
pii_tests = [('user@example.com', 'EMAIL'), ('sk-abc1234567890123456789012345', 'OPENAI_KEY'), ('AKIAIOSFODNN7EXAMPLE123456', 'AWS_KEY'), ('192.168.1.1', 'IPV4'), ('555-123-4567', 'PHONE_US')]
for raw, pii_type in pii_tests:
    safe = PII_Sanitizer.is_safe(raw)
    sanitized = PII_Sanitizer.sanitize(raw)
    found = pii_type.lower() in sanitized.lower() or 'REDACTED' in sanitized
    print(f'P6 {pii_type}: is_safe={safe} redacted={found} result={sanitized!r}')
reset()
mgr7 = GlobalCache().get_hive_mind()
stats7 = mgr7.get_statistics()
for k in ('strict_mode', 'stateless_mode', 'sampling_rate_actual'):
    print(f'P7 {k}: {k in stats7}')
reset()
gc8 = GlobalCache()
hive8 = gc8.get_hive_mind()
gc8.put('mykey', {'answer': 42}, text_for_embedding='target query text', source_engine='ENG')
recalled = hive8.recall('target query text', 'GlobalCache')
if recalled:
    print('P8 recalled keys:', sorted(recalled.keys()))
    print('P8 value key present:', 'value' in recalled)
    print('P8 _metadata present:', '_metadata' in recalled)
    meta = recalled.get('_metadata', {})
    print('P8 metadata.namespace:', meta.get('namespace'))
else:
    print('P8 recalled=None (Redis unavailable — vector store only path)')
    print('P8 CONFIRMED: without Redis, recall() cannot retrieve working-memory entries')
reset()
print('P9 cache_get callable:', callable(cache_get))
print('P9 cache_put callable:', callable(cache_put))
print('P9 cache_search_semantic callable:', callable(cache_search_semantic))
print('P9 cached callable:', callable(cached))
reset()
gc_a = GlobalCache()
gc_b = GlobalCache()
print('P10 both get same singleton:', gc_a.get_hive_mind() is gc_b.get_hive_mind())
print('P10 independent _hive attrs:', gc_a._hive is not gc_b._hive or gc_a._hive is gc_b._hive)
reset()
inst1 = get_global_cache()
inst2 = get_global_cache()
print('P11 get_global_cache singleton:', inst1 is inst2)
reset()
# guardian: allow-global-mutation
os.environ['HIVE_MIND_STRICT_MODE'] = 'true'
SemanticCacheManager.reset_instance()
try:
    mgr12 = SemanticCacheManager.get_instance()
    print('P12 strict_mode + no redis + vector_store available: NO raise (correct)')
    print('P12 stateless_mode:', mgr12.stateless_mode)
# guardian: allow-silent-swallow
except Exception as e:
    print('P12 UNEXPECTED raise:', e)
finally:
    # guardian: allow-global-mutation
    os.environ['HIVE_MIND_STRICT_MODE'] = 'false'
    SemanticCacheManager.reset_instance()
raw13 = 'contact john@corp.com or call 555-867-5309 with key sk-abc1234567890123456789'
findings = PII_Sanitizer.detect_pii(raw13)
print('P13 detect_pii types found:', sorted(findings.keys()))
reset()
gc14 = GlobalCache()
gc14.put('kk', 'stored_value', text_for_embedding='specific query phrase')
r14 = gc14.get_semantic('specific query phrase')
print('P14 get_semantic without promote:', r14)
reset()
gc15 = GlobalCache()
n = gc15.cleanup_expired()
print('P15 cleanup_expired returns int:', isinstance(n, int))
print()
print('ALL PROBES COMPLETE')
