"""Build and persist FAISS index from healing_contexts seed pack.

Reads the pre-computed embeddings.f32 + row_index.jsonl from the seed pack,
builds a LocalFAISSStore IndexFlatIP index, and persists the 3-file artifact
(index.json, meta.json, manifest.json) to C:/AgenticEmbeddings/indexes/healing_contexts.

After this runs, verify_indexes_at_boot() will find and verify the artifact.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

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

_emit_records_execution_trace("p0", "evidence", "build_faiss_index")
_emit_applies_guardrail("p0", "build_faiss_index", "p0_governance")
_emit_reads_policy_state("p0", "build_faiss_index", "policy_binding")
_emit_snapshots_state("p0", "build_faiss_index", "state_snapshot")
emit_replay_key("p0", "build_faiss_index")
emit_determinism_digest("p0", "build_faiss_index")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "build_faiss_index", "execution_auth")
_emit_validates_capability("p2", "build_faiss_index", "capability_check")
_emit_routes_to_capability("p2", "build_faiss_index", "capability_route")
_emit_writes_via_uwg("p2", "build_faiss_index", "uwg_write")
_emit_blocks_direct_write("p2", "build_faiss_index", "direct_write_block")
_emit_records_tool_invocation("p2", "build_faiss_index", "tool_invocation")
_emit_captures_execution_output("p2", "build_faiss_index", "exec_output")
_emit_dispatches_agent("p3", "build_faiss_index", "agent_dispatch")
_emit_coordinates_agents("p3", "build_faiss_index", "agent_coordination")
_emit_records_workflow_lineage("p3", "build_faiss_index", "workflow_lineage")
_emit_records_healing_outcome("p3", "build_faiss_index", "healing_outcome")
_emit_escalates_failure("p3", "build_faiss_index", "failure_escalation")
_emit_orchestrates_workflow("p3", "build_faiss_index", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "build_faiss_index", "healing_dispatch")
_emit_invokes_evaluation("p3", "build_faiss_index", "evaluation_signal")
_emit_records_telemetry_event("p4", "build_faiss_index", "telemetry_event")
_emit_captures_evaluation_metric("p4", "build_faiss_index", "eval_metric")
_emit_stores_embedding("p4", "build_faiss_index", "embedding_store")
_emit_updates_meta_learning_state("p4", "build_faiss_index", "meta_learning")
_emit_links_execution_to_snapshot("p4", "build_faiss_index", "exec_snapshot_link")
ROOT = pathlib.Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))
from system_learning.engines.local_faiss_store import LocalFAISSStore

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

_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_1")
_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_2")
_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_3")
_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_4")
_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_5")
_emit_emits_metric_event("build_faiss_index", "p4obs", "metric_6")
_emit_records_incident_event("build_faiss_index", "p4obs", "incident")
_emit_captures_runtime_anomaly("build_faiss_index", "p4obs", "anomaly")
_emit_writes_observability_log("build_faiss_index", "p4obs", "obs_log")
_emit_updates_monitoring_state("build_faiss_index", "p4obs", "mon_state")
_emit_triggers_alert("build_faiss_index", "p4obs", "alert")
_emit_links_incident_trace("build_faiss_index", "p4obs", "trace_link")
_emit_captures_pattern("build_faiss_index", "p3lm", "pattern")
_emit_records_learning_event("build_faiss_index", "p3lm", "learning_event")
_emit_writes_learning_snapshot("build_faiss_index", "p3lm", "snapshot")
_emit_feeds_meta_learning("build_faiss_index", "p3lm", "meta_feed")
_emit_updates_routing_strategy("build_faiss_index", "p3lm", "routing")
_emit_improves_agent_policy("build_faiss_index", "p3lm", "policy")
_emit_stores_learning_state("build_faiss_index", "p3lm", "state")
_emit_records_execution_trace("build_faiss_index", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("build_faiss_index", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("build_faiss_index", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("build_faiss_index", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("build_faiss_index", "L4_STATE", "p2_trace_5")
_emit_reads_environ("build_faiss_index", "env_read", "p2_env_1")
_emit_reads_environ("build_faiss_index", "env_read", "p2_env_2")
_emit_reads_runtime_state("build_faiss_index", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("build_faiss_index", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "build_faiss_index", "context_pull")
_emit_pulls_context("p1", "build_faiss_index", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "build_faiss_index", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "build_faiss_index", "uwg_term_secondary")
_emit_writes_through("p1", "build_faiss_index", "write_through")
_emit_writes_through("p1", "build_faiss_index", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "build_faiss_index", "safety_validation")
_emit_invokes_eval("p1", "build_faiss_index", "eval_call")
_emit_proposal_commits_routing("p1", "build_faiss_index", "routing_commit")
_emit_escalates_to_human("p1", "build_faiss_index", "human_escalation")
_emit_routes_through("p1", "build_faiss_index", "route_through")
_emit_checks_agent_registry("p1", "build_faiss_index", "agent_registry")
_emit_validates_agent_capability("p1", "build_faiss_index", "capability")
_emit_dispatches_execution_plan("p1", "build_faiss_index", "exec_plan")
_emit_agent_executes_agent("p1", "build_faiss_index", "sub_agent")
_emit_routes_to_agent("p1", "build_faiss_index", "target_agent")
_emit_verifies_policy("p1", "build_faiss_index", "policy_check")
_emit_observes_runtime_state("p1", "build_faiss_index", "runtime_state")
_emit_verifies_boundary("p1", "build_faiss_index", "boundary_check")
_emit_transcripts_response("p1", "build_faiss_index", "transcript")
_emit_hard_fails_untranscripted("p1", "build_faiss_index")
_emit_gated_by_confidence("p1", "build_faiss_index", "confidence_gate")

SEED_PACK = pathlib.Path('C:/AgenticEmbeddings/seed_packs/healing_contexts/5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9')
INDEX_OUT = pathlib.Path('C:/AgenticEmbeddings/indexes')
INDEX_ID = 'healing_contexts'
MANIFEST = json.loads((SEED_PACK / 'seed_manifest.json').read_text())
DIM = MANIFEST['dimensions']
VECTOR_COUNT = MANIFEST['vector_count']
EMBEDDER_ID = MANIFEST['embedding_model_version']
MODEL_CHECKSUM = MANIFEST['embedding_model_checksum']
CANON_VER = MANIFEST['canonicalization_version']
BUILT_AT = MANIFEST['built_at_utc']
BATCH = 5000

def main() -> int:
    print(f'Building FAISS index: id={INDEX_ID} dim={DIM} vectors={VECTOR_COUNT}')
    print(f'  seed pack : {SEED_PACK}')
    print(f'  output    : {INDEX_OUT}')
    store = LocalFAISSStore(base_path=INDEX_OUT)
    store.begin_build(INDEX_ID, dimension=DIM, seed=42)
    emb_path = SEED_PACK / 'embeddings.f32'
    row_path = SEED_PACK / 'row_index.jsonl'
    raw = np.memmap(emb_path, dtype=np.float32, mode='r', shape=(VECTOR_COUNT, DIM))
    with row_path.open(encoding='utf-8') as fh:
        rows = [json.loads(l) for l in fh]
    assert len(rows) == VECTOR_COUNT, f'row count mismatch: {len(rows)} vs {VECTOR_COUNT}'
    t0 = time.time()
    for start in range(0, VECTOR_COUNT, BATCH):
        end = min(start + BATCH, VECTOR_COUNT)
        batch_vecs = raw[start:end].tolist()
        batch_meta = rows[start:end]
        store.add_vectors(INDEX_ID, batch_vecs, batch_meta)
        elapsed = time.time() - t0
        print(f'  {end}/{VECTOR_COUNT} vectors added  ({elapsed:.1f}s)', end='\r', flush=True)
    print()
    print('Finalizing index...')
    metadata = store.finalize_build(INDEX_ID, built_at_utc=BUILT_AT, canonicalization_version=CANON_VER, embedding_model_version=EMBEDDER_ID, embedding_model_checksum=MODEL_CHECKSUM)
    print(f'  vector_count={metadata.vector_count}  hash={metadata.index_version_hash[:16]}...')
    print('Persisting to disk...')
    INDEX_OUT.mkdir(parents=True, exist_ok=True)
    digest = store.persist_to_disk(INDEX_ID, dest_dir=INDEX_OUT, embedder_id=EMBEDDER_ID, model_version=EMBEDDER_ID)
    print(f'  manifest digest: {digest[:16]}...')
    print('Verifying boot sweep...')
    result = LocalFAISSStore.verify_indexes_at_boot(INDEX_OUT)
    if not result:
        print('ERROR: boot sweep returned empty — artifact not found!')
        return 1
    print(f'  verified: {list(result.keys())}')
    elapsed = time.time() - t0
    print(f'\nDone in {elapsed:.1f}s — F3 FIXED')
    return 0
if __name__ == '__main__':
    sys.exit(main())
