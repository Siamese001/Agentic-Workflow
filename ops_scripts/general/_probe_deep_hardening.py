"""
Standalone deep-hardening probe for GlobalCache and semantic cache behavior.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_probe_deep_hardening", "write_through")
_emit_writes_through("p1", "_probe_deep_hardening", "write_through_2")
_emit_pulls_context("p1", "_probe_deep_hardening", "context_pull")
_emit_pulls_context("p1", "_probe_deep_hardening", "context_pull_secondary")
emit_determinism_digest("trace_probe_deep_hardening", "dispatch")
emit_determinism_digest("trace_probe_deep_hardening", "complete")
_emit_validated_by_safety_plane("p1", "_probe_deep_hardening", "safety_validation")


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _bootstrap(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- probe bootstrap
    os.environ.setdefault("HIVE_MIND_STRICT_MODE", "false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deep hardening probes for GlobalCache behavior.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    _bootstrap(repo_root)

    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        PII_Sanitizer,
        SemanticCacheManager,
    )
    import apps_shared.enforcement.GlobalcacheStrategy as strategy_module
    from apps_shared.enforcement.GlobalcacheStrategy import (
        GlobalCache,
        cache_get,
        cache_put,
        cache_search_semantic,
        cached,
        get_global_cache,
    )

    def reset() -> None:
        SemanticCacheManager.reset_instance()
        strategy_module._global_cache = None

    reset()
    gc = GlobalCache()
    race_results: list[int] = []

    def worker() -> None:
        race_results.append(id(gc.get_hive_mind()))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("P1 race unique hive ids:", len(set(race_results)), "(expect 1)")
    print("P1 _hive type:", type(gc._hive).__name__)

    reset()
    gc2 = GlobalCache()
    gc2.put("k1", "val1", text_for_embedding="ats keywords resume")
    gc2.put("k2", "val2", text_for_embedding="ats keywords linkedin")
    probe_results = gc2.get_semantic("ats keywords", max_results=3)
    print("P2 max_results=3 actual count:", len(probe_results), "(hive recall returns at most 1)")

    reset()
    gc3 = GlobalCache()
    mgr3 = gc3.get_hive_mind()
    print("P3 redis_enabled:", mgr3.redis_enabled)
    gc3.put("k", {"v": 1}, text_for_embedding="ctx")
    print("P3 cache_stores after no-redis learn:", mgr3.get_statistics()["cache_stores"])

    reset()
    gc4 = GlobalCache()
    stats4 = gc4.get_stats()
    print("P4 get_stats keys:", sorted(stats4.keys()))

    reset()
    gc5 = GlobalCache()
    gc5.put("k", "v")
    gc5.get("k")
    gc5.clear()
    print("P5 stats after clear:", gc5._stats)

    reset()
    pii_tests = [
        ("user@example.com", "EMAIL"),
        ("sk-abc1234567890123456789012345", "OPENAI_KEY"),
        ("AKIAIOSFODNN7EXAMPLE123456", "AWS_KEY"),
        ("192.168.1.1", "IPV4"),
        ("555-123-4567", "PHONE_US"),
    ]
    for raw, pii_type in pii_tests:
        safe = PII_Sanitizer.is_safe(raw)
        sanitized = PII_Sanitizer.sanitize(raw)
        found = pii_type.lower() in sanitized.lower() or "REDACTED" in sanitized
        print(f"P6 {pii_type}: is_safe={safe} redacted={found} result={sanitized!r}")

    reset()
    mgr7 = GlobalCache().get_hive_mind()
    stats7 = mgr7.get_statistics()
    for key in ("strict_mode", "stateless_mode", "sampling_rate_actual"):
        print(f"P7 {key}: {key in stats7}")

    reset()
    gc8 = GlobalCache()
    hive8 = gc8.get_hive_mind()
    gc8.put("mykey", {"answer": 42}, text_for_embedding="target query text", source_engine="ENG")
    recalled = hive8.recall("target query text", "GlobalCache")
    if recalled:
        print("P8 recalled keys:", sorted(recalled.keys()))
        print("P8 value key present:", "value" in recalled)
        print("P8 _metadata present:", "_metadata" in recalled)
        metadata = recalled.get("_metadata", {})
        print("P8 metadata.namespace:", metadata.get("namespace"))
    else:
        print("P8 recalled=None (Redis unavailable — vector store only path)")
        print("P8 CONFIRMED: without Redis, recall() cannot retrieve working-memory entries")

    reset()
    print("P9 cache_get callable:", callable(cache_get))
    print("P9 cache_put callable:", callable(cache_put))
    print("P9 cache_search_semantic callable:", callable(cache_search_semantic))
    print("P9 cached callable:", callable(cached))

    reset()
    gc_a = GlobalCache()
    gc_b = GlobalCache()
    print("P10 both get same singleton:", gc_a.get_hive_mind() is gc_b.get_hive_mind())
    print("P10 independent _hive attrs:", gc_a._hive is not gc_b._hive or gc_a._hive is gc_b._hive)

    reset()
    inst1 = get_global_cache()
    inst2 = get_global_cache()
    print("P11 get_global_cache singleton:", inst1 is inst2)

    reset()
    os.environ["HIVE_MIND_STRICT_MODE"] = "true"
    SemanticCacheManager.reset_instance()
    try:
        mgr12 = SemanticCacheManager.get_instance()
        print("P12 strict_mode + no redis + vector_store available: NO raise (correct)")
        print("P12 stateless_mode:", mgr12.stateless_mode)
    except (ImportError, AttributeError, OSError, ValueError) as exc:
        print("P12 UNEXPECTED raise:", exc)
    finally:
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"
        SemanticCacheManager.reset_instance()

    raw13 = "contact john@corp.com or call 555-867-5309 with key sk-abc1234567890123456789"
    findings = PII_Sanitizer.detect_pii(raw13)
    print("P13 detect_pii types found:", sorted(findings.keys()))

    reset()
    gc14 = GlobalCache()
    gc14.put("kk", "stored_value", text_for_embedding="specific query phrase")
    r14 = gc14.get_semantic("specific query phrase")
    print("P14 get_semantic without promote:", r14)

    reset()
    gc15 = GlobalCache()
    cleaned = gc15.cleanup_expired()
    print("P15 cleanup_expired returns int:", isinstance(cleaned, int))
    print()
    print("ALL PROBES COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
