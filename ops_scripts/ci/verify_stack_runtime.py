#!/usr/bin/env python3
"""Runtime verification of F1-F5 infrastructure stack fixes.

Validates that all fixes are working in the live runtime environment:
    F1+F5: QWEN_GPU_MEM_UTIL constant is used consistently
    F2:    EmbeddingServiceFactory GPU path is wired correctly
    F3:    LocalFAISSStore.verify_indexes_at_boot is callable
    F4:    Redis health check returns structured response
    F5:    (covered by F1)

Exit 0 on success, 1 on any failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def verify_f1_f5_qwen_gpu_mem_util() -> tuple[bool, str]:
    """F1+F5: Verify QWEN_GPU_MEM_UTIL constant exists and is used."""
    try:
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
        from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

        # 1. Constant exists and has correct value
        if not isinstance(QWEN_GPU_MEM_UTIL, float):
            return False, f"QWEN_GPU_MEM_UTIL is not a float: {type(QWEN_GPU_MEM_UTIL)}"
        if QWEN_GPU_MEM_UTIL != 0.70:
            return False, f"QWEN_GPU_MEM_UTIL={QWEN_GPU_MEM_UTIL}, expected 0.70"

        # 2. vllm_process_manager uses the constant
        for size in ("7B", "14B"):
            cfg = get_model_config(size)
            if cfg["gpu_memory_utilization"] != QWEN_GPU_MEM_UTIL:
                return False, (
                    f"get_model_config('{size}') gpu_memory_utilization="
                    f"{cfg['gpu_memory_utilization']}, expected {QWEN_GPU_MEM_UTIL}"
                )

        # 3. qwen_vllm_inference imports the constant (AST check)
        import ast

        qwen_src = (PROJECT_ROOT / "agentic_core/L2_execution/healers/qwen_vllm_inference.py").read_text()
        tree = ast.parse(qwen_src)
        imported = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "agentic_core.L2_execution.healers.healing_tier_config"
            ):
                for alias in node.names:
                    if alias.name == "QWEN_GPU_MEM_UTIL":
                        imported = True
                        break
        if not imported:
            return False, "qwen_vllm_inference.py does not import QWEN_GPU_MEM_UTIL"

        return True, "QWEN_GPU_MEM_UTIL SSOT verified"
    except Exception as exc:
        raise
        return False, f"F1+F5 verification failed: {exc}"


def verify_f2_embedding_gpu_path() -> tuple[bool, str]:
    """F2: Verify EmbeddingServiceFactory GPU helpers exist and are callable."""
    try:
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        # 1. _faiss_gpu_available exists and returns bool
        if not hasattr(EmbeddingServiceFactory, "_faiss_gpu_available"):
            return False, "EmbeddingServiceFactory._faiss_gpu_available does not exist"
        result = EmbeddingServiceFactory._faiss_gpu_available()
        if not isinstance(result, bool):
            return False, f"_faiss_gpu_available returned {type(result)}, expected bool"

        # 2. _embedding_device exists and returns str
        if not hasattr(EmbeddingServiceFactory, "_embedding_device"):
            return False, "EmbeddingServiceFactory._embedding_device does not exist"
        device = EmbeddingServiceFactory._embedding_device()
        if not isinstance(device, str):
            return False, f"_embedding_device returned {type(device)}, expected str"
        if device not in ("cpu", "cuda"):
            return False, f"_embedding_device returned '{device}', expected 'cpu' or 'cuda'"

        # 3. _build_gpu_index exists and is callable
        if not hasattr(EmbeddingServiceFactory, "_build_gpu_index"):
            return False, "EmbeddingServiceFactory._build_gpu_index does not exist"
        if not callable(EmbeddingServiceFactory._build_gpu_index):
            return False, "_build_gpu_index is not callable"

        return True, f"EmbeddingServiceFactory GPU path verified (device={device}, faiss-gpu={result})"
    except Exception as exc:
        raise
        return False, f"F2 verification failed: {exc}"


def verify_f3_faiss_boot_sweep() -> tuple[bool, str]:
    """F3: Verify LocalFAISSStore.verify_indexes_at_boot exists and is callable."""
    try:
        import tempfile
        from pathlib import Path

        from system_learning.engines.local_faiss_store import LocalFAISSStore

        # 1. Method exists
        if not hasattr(LocalFAISSStore, "verify_indexes_at_boot"):
            return False, "LocalFAISSStore.verify_indexes_at_boot does not exist"

        # 2. Method is callable
        if not callable(LocalFAISSStore.verify_indexes_at_boot):
            return False, "verify_indexes_at_boot is not callable"

        # 3. Method works on empty directory
        with tempfile.TemporaryDirectory() as tmpdir:
            result = LocalFAISSStore.verify_indexes_at_boot(Path(tmpdir))
            if not isinstance(result, dict):
                return False, f"verify_indexes_at_boot returned {type(result)}, expected dict"

        return True, "LocalFAISSStore.verify_indexes_at_boot verified"
    except Exception as exc:
        raise
        return False, f"F3 verification failed: {exc}"


def verify_f4_redis_health_check() -> tuple[bool, str]:
    """F4: Verify check_redis_health returns structured response."""
    try:
        from agentic_core.cache.redis_cache_client import check_redis_health

        # 1. Function exists and is callable
        if not callable(check_redis_health):
            return False, "check_redis_health is not callable"

        # 2. Returns dict with required keys
        result = check_redis_health()
        if not isinstance(result, dict):
            return False, f"check_redis_health returned {type(result)}, expected dict"

        required_keys = {"healthy", "url", "using_fallback", "error", "fix"}
        missing = required_keys - result.keys()
        if missing:
            return False, f"check_redis_health missing keys: {missing}"

        # 3. healthy is bool
        if not isinstance(result["healthy"], bool):
            return False, f"healthy is {type(result['healthy'])}, expected bool"

        # 4. If unhealthy, fix hint must be present
        if not result["healthy"] and not result.get("fix"):
            return False, "unhealthy result missing fix hint"

        status = "healthy" if result["healthy"] else "unhealthy (fallback active)"
        return True, f"Redis health check verified: {status}"
    except Exception as exc:
        raise
        return False, f"F4 verification failed: {exc}"


def main() -> int:
    """Run all runtime verifications."""
    print("=" * 80)
    print("F1-F5 Runtime Stack Verification")
    print("=" * 80)

    verifications = [
        ("F1+F5", "QWEN_GPU_MEM_UTIL SSOT", verify_f1_f5_qwen_gpu_mem_util),
        ("F2", "EmbeddingServiceFactory GPU path", verify_f2_embedding_gpu_path),
        ("F3", "LocalFAISSStore.verify_indexes_at_boot", verify_f3_faiss_boot_sweep),
        ("F4", "Redis health check", verify_f4_redis_health_check),
    ]

    results = []
    for fix_id, description, verify_fn in verifications:
        print(f"\n[{fix_id}] {description}...", end=" ", flush=True)
        passed, message = verify_fn()
        results.append((fix_id, description, passed, message))
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}")
        print(f"     {message}")

    print("\n" + "=" * 80)
    passed_count = sum(1 for _, _, passed, _ in results if passed)
    total_count = len(results)
    print(f"Results: {passed_count}/{total_count} passed")
    print("=" * 80)

    if passed_count == total_count:
        print("\n✓ All runtime verifications PASSED")
        return 0
    else:
        print("\n✗ Some runtime verifications FAILED")
        for fix_id, desc, passed, msg in results:
            if not passed:
                print(f"  [{fix_id}] {desc}: {msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
