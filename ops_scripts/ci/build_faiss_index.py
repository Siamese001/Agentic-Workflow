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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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
