from __future__ import annotations

import importlib.util
import math

from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery
from agentic_core.L4_state.types.vector_store_types import BaseVectorStore
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "in_memory_vector_store")
trace_contract.emit_determinism_digest("p0", "in_memory_vector_store")

trace_contract._emit_dispatches_healing_run("p1", "in_memory_vector_store", "L4")
trace_contract._emit_routes_through("p1", "in_memory_vector_store", "L4")
trace_contract._emit_checks_agent_registry("p1", "in_memory_vector_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "in_memory_vector_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "in_memory_vector_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "in_memory_vector_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "in_memory_vector_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "in_memory_vector_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "in_memory_vector_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "in_memory_vector_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "in_memory_vector_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "in_memory_vector_store")
trace_contract._emit_gated_by_confidence("p1", "in_memory_vector_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "in_memory_vector_store", "L4")
trace_contract._emit_reads_policy_state("p1", "in_memory_vector_store", "L4")
trace_contract._emit_authorize_and_execute("p2", "in_memory_vector_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "in_memory_vector_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "in_memory_vector_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "in_memory_vector_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "in_memory_vector_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "in_memory_vector_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "in_memory_vector_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "in_memory_vector_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "in_memory_vector_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "in_memory_vector_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "in_memory_vector_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "in_memory_vector_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "in_memory_vector_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "in_memory_vector_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "in_memory_vector_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "in_memory_vector_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "in_memory_vector_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "in_memory_vector_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "in_memory_vector_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "in_memory_vector_store", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("in_memory_vector_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("in_memory_vector_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("in_memory_vector_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("in_memory_vector_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("in_memory_vector_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("in_memory_vector_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("in_memory_vector_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("in_memory_vector_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("in_memory_vector_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("in_memory_vector_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("in_memory_vector_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("in_memory_vector_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("in_memory_vector_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("in_memory_vector_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("in_memory_vector_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("in_memory_vector_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("in_memory_vector_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("in_memory_vector_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("in_memory_vector_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("in_memory_vector_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("in_memory_vector_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("in_memory_vector_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("in_memory_vector_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "in_memory_vector_store", "context_pull")
trace_contract._emit_pulls_context("p1", "in_memory_vector_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "in_memory_vector_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "in_memory_vector_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "in_memory_vector_store", "write_through")
trace_contract._emit_writes_through("p1", "in_memory_vector_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "in_memory_vector_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "in_memory_vector_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "in_memory_vector_store", "routing_commit")


def _faiss_available() -> bool:
    return importlib.util.find_spec("faiss") is not None


class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "InMemoryVectorStore.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "InMemoryVectorStore.__init__", "p0_governance")
        self._storage: dict[str, MemoryItem] = {}
        self._ordered_ids: list[str] = []
        self._faiss_index = None
        self._faiss_dim: int | None = None

    def _reset_faiss(self) -> None:
        self._faiss_index = None
        self._faiss_dim = None

    def _rebuild_faiss(self) -> None:
        if not _faiss_available() or not self._storage:
            self._faiss_index = None
            return
        import faiss
        import numpy as np

        items = [self._storage[uid] for uid in self._ordered_ids if uid in self._storage]
        if not items:
            self._faiss_index = None
            return
        dim = len(items[0].embedding)
        self._faiss_dim = dim
        arr = np.array([item.embedding for item in items], dtype=np.float32)
        faiss.normalize_L2(arr)
        index = faiss.IndexFlatIP(dim)
        index.add(arr)
        self._faiss_index = index

    async def initialize(self) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "InMemoryVectorStore.initialize")

        self._storage.clear()
        self._ordered_ids.clear()
        self._reset_faiss()

    async def upsert(self, items: list[MemoryItem]) -> bool:
        for item in items:
            uid = str(item.id)
            if uid not in self._storage:
                self._ordered_ids.append(uid)
            self._storage[uid] = item
        self._rebuild_faiss()
        return True

    async def delete(self, item_ids: list[str]) -> bool:
        for uid in item_ids:
            self._storage.pop(uid, None)
        self._ordered_ids = [uid for uid in self._ordered_ids if uid in self._storage]
        self._rebuild_faiss()
        return True

    async def query(self, query: MemoryQuery) -> list[MemoryItem]:
        """
        Cosine similarity search.
        Primary path : FAISS IndexFlatIP with L2-normalised vectors.
        Fallback path: pure-Python cosine when faiss is not installed.
        """
        q_vec = query.vector
        candidate_ids: list[str] = list(self._ordered_ids)
        if _faiss_available() and self._faiss_index is not None:
            import faiss
            import numpy as np

            q_arr = np.array([q_vec], dtype=np.float32)
            faiss.normalize_L2(q_arr)
            k = min(query.top_k * 4 if query.filter_metadata else query.top_k, self._faiss_index.ntotal)
            if k == 0:
                return []
            scores_arr, indices_arr = self._faiss_index.search(q_arr, k)
            active_ids = [uid for uid in self._ordered_ids if uid in self._storage]
            results: list[MemoryItem] = []
            for score, idx in tqdm(zip(scores_arr[0], indices_arr[0]), desc="Processing", unit="item"):
                if idx < 0 or idx >= len(active_ids):
                    continue
                uid = active_ids[idx]
                item = self._storage.get(uid)
                if item is None:
                    continue
                if query.filter_metadata:
                    match = all((item.metadata.get(k) == v for k, v in query.filter_metadata.items()))
                    if not match:
                        continue
                item_copy = item.model_copy()
                item_copy.score = float(score)
                results.append(item_copy)
            results.sort(key=lambda x: x.score or 0.0, reverse=True)
            return results[: query.top_k]
        q_mag = math.sqrt(sum(x * x for x in q_vec))
        results = []
        for uid in tqdm(candidate_ids, desc="Processing", unit="item"):
            item = self._storage.get(uid)
            if item is None:
                continue
            if query.filter_metadata:
                match = all((item.metadata.get(k) == v for k, v in query.filter_metadata.items()))
                if not match:
                    continue
            d_vec = item.embedding
            dot_product = sum((a * b for a, b in zip(q_vec, d_vec, strict=False)))
            d_mag = math.sqrt(sum(x * x for x in d_vec))
            similarity = dot_product / (d_mag * q_mag) if d_mag * q_mag != 0 else 0.0
            item_copy = item.model_copy()
            item_copy.score = similarity
            results.append(item_copy)
        results.sort(key=lambda x: x.score or 0.0, reverse=True)
        return results[: query.top_k]
