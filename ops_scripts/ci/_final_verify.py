#!/usr/bin/env python3
"""Final infrastructure verification — F1-F5."""

import json
import os
import pathlib
import sys
import urllib.request

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_final_verify")
_emit_applies_guardrail("p0", "_final_verify", "p0_governance")
_emit_reads_policy_state("p0", "_final_verify", "policy_binding")
_emit_snapshots_state("p0", "_final_verify", "state_snapshot")
emit_replay_key("p0", "_final_verify")
emit_determinism_digest("p0", "_final_verify")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# guardian: allow-global-mutation
sys.path.insert(0, "c:/Git/Agentic-Workflow")

results = {}

# F1: vLLM running
try:
    # guardian: allow-magic-config
    with urllib.request.urlopen("http://localhost:8000/v1/models", timeout=3) as r:
        data = json.loads(r.read())
        results["F1_vllm"] = "PASS: " + data["data"][0]["id"]
except Exception as e:
    raise
    results["F1_vllm"] = f"FAIL: {e}"

# F2: faiss-gpu + embedding env
try:
    import faiss

    has_gpu = hasattr(faiss, "StandardGpuResources")
    emb_dev = os.environ.get("EMBEDDING_DEVICE", "not set -> cpu")
    emb_en = os.environ.get("EMBEDDING_ENABLED", "not set -> false")
    if has_gpu and emb_dev == "cuda" and emb_en == "true":
        results["F2_embedding"] = "PASS: faiss-gpu + EMBEDDING_DEVICE=cuda + EMBEDDING_ENABLED=true"
    else:
        missing = []
        if not has_gpu:
            missing.append("faiss-gpu unavailable (no pip wheel for CUDA 12.8/Windows)")
        if emb_dev != "cuda":
            missing.append(f"EMBEDDING_DEVICE={emb_dev!r}")
        if emb_en != "true":
            missing.append(f"EMBEDDING_ENABLED={emb_en!r}")
        results["F2_embedding"] = "FAIL: " + "; ".join(missing)
except Exception as e:
    raise
    results["F2_embedding"] = f"FAIL: {e}"

# F3: FAISS index boot sweep
try:
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    idx_dir = pathlib.Path("C:/AgenticEmbeddings/indexes")
    boot = LocalFAISSStore.verify_indexes_at_boot(idx_dir)
    if boot:
        first_digest = list(boot.values())[0]
        results["F3_faiss_index"] = f"PASS: {list(boot.keys())} digest={first_digest[:16]}..."
    else:
        results["F3_faiss_index"] = "FAIL: no indexes found"
except Exception as e:
    raise
    results["F3_faiss_index"] = f"FAIL: {e}"

# F4: Redis
try:
    from agentic_core.cache.redis_cache_client import check_redis_health

    h = check_redis_health()
    if h["healthy"]:
        results["F4_redis"] = f"PASS: healthy, mem={h.get('used_memory_human', '?')}"
    else:
        results["F4_redis"] = f"FAIL: {h['error']}"
except Exception as e:
    raise
    results["F4_redis"] = f"FAIL: {e}"

# F5: GPU mem util SSOT
try:
    from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
    from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

    cfg7 = get_model_config("7B")["gpu_memory_utilization"]
    cfg14 = get_model_config("14B")["gpu_memory_utilization"]
    if QWEN_GPU_MEM_UTIL == 0.70 and cfg7 == 0.70 and cfg14 == 0.70:
        results["F5_gpu_util_ssot"] = f"PASS: QWEN_GPU_MEM_UTIL={QWEN_GPU_MEM_UTIL} (7B={cfg7}, 14B={cfg14})"
    else:
        results["F5_gpu_util_ssot"] = f"FAIL: const={QWEN_GPU_MEM_UTIL} 7B={cfg7} 14B={cfg14}"
except Exception as e:
    raise
    results["F5_gpu_util_ssot"] = f"FAIL: {e}"

print("=" * 60)
print("FINAL INFRASTRUCTURE STATUS")
print("=" * 60)
fails = []
for k, v in results.items():
    if str(v).startswith("PASS"):
        print(f"[OK] {k}: {v}")
    else:
        print(f"[!!] {k}: {v}")
        fails.append(k)

print("=" * 60)
if fails:
    print(f"RESULT: {len(fails)} FAIL(s): {fails}")
    sys.exit(1)
else:
    print("RESULT: ALL PASS")
    sys.exit(0)
