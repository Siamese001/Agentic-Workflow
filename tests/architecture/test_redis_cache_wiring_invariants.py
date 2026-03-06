"""Architecture invariant tests for Redis cache seam wiring.

Verifies three structural properties of the cache layer:

  1. SEAM WIRING CONTRACT — every seam class exposes a ``get_or_fetch``
     read-through method so engines can call cache-before-L4 in one call.

  2. NO SHADOW REDIS IN L4 — ``L4_state`` must contain no live Redis
     client classes (checked via AST).  The tombstoned ``_Tombstoned*``
     stubs are allowed.

  3. HASH VALIDATION STRICTNESS — ``_require_hash_segment`` must reject
     non-SHA-256 strings in strict mode and accept them when the env-var
     override is set.
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
L4_STATE_DIR = REPO_ROOT / "agentic_core" / "L4_state"

# ---------------------------------------------------------------------------
# §1  SEAM WIRING CONTRACT
# ---------------------------------------------------------------------------


def _make_fake_cache() -> MagicMock:
    """Return a DeterministicRedisCache mock that always misses."""
    fake = MagicMock()
    fake.get_json.return_value = None
    fake.get.return_value = None
    return fake


# --- L0 RouteDecisionCache ---


def test_route_decision_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    assert hasattr(RouteDecisionCache, "get_or_fetch"), "RouteDecisionCache must expose get_or_fetch()"


def test_route_decision_cache_get_or_fetch_on_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    cache = RouteDecisionCache(cache=fake)
    sentinel = {"decision": "path_a"}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, fetch)
    assert result is sentinel
    assert fetch_called, "fetch_from_l4 must be called on a miss"
    fake.set_json.assert_called_once()


def test_route_decision_cache_get_or_fetch_on_hit():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    cached_val = {"decision": "cached"}
    fake.get_json.return_value = cached_val
    cache = RouteDecisionCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: fetch_called.append(True))
    assert result is cached_val
    assert not fetch_called, "fetch_from_l4 must NOT be called on a hit"
    fake.set_json.assert_not_called()


def test_route_decision_cache_get_or_fetch_replay_bypasses_cache():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"decision": "stale"}
    cache = RouteDecisionCache(cache=fake)
    sentinel = {"decision": "replayed"}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch, replay_mode=True)
    assert result is sentinel
    assert fetch_called, "replay_mode must bypass the cache and call fetch"


# --- L0 RoutingRuleSurfaceCache ---


def test_routing_rule_surface_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import RoutingRuleSurfaceCache

    assert hasattr(RoutingRuleSurfaceCache, "get_or_fetch")


def test_routing_rule_surface_get_or_fetch_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import RoutingRuleSurfaceCache

    fake = _make_fake_cache()
    cache = RoutingRuleSurfaceCache(cache=fake)
    sentinel = {"rules": []}
    result = cache.get_or_fetch("a" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


# --- L0 CapabilityRegistryCache ---


def test_cap_registry_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import CapabilityRegistryCache

    assert hasattr(CapabilityRegistryCache, "get_or_fetch")


def test_cap_registry_get_or_fetch_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import CapabilityRegistryCache

    fake = _make_fake_cache()
    cache = CapabilityRegistryCache(cache=fake)
    sentinel = {"tools": ["tool_a"]}
    result = cache.get_or_fetch("a" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


# --- L1 CompiledPromptCache ---


def test_compiled_prompt_cache_has_get_or_fetch():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    assert hasattr(CompiledPromptCache, "get_or_fetch")


def test_compiled_prompt_get_or_fetch_miss():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    fake = _make_fake_cache()
    cache = CompiledPromptCache(cache=fake)
    sentinel = {"artifact_signature": "sig1"}
    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, h, h, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_compiled_prompt_get_or_fetch_hit():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    fake = _make_fake_cache()
    hit = {"artifact_signature": "cached_sig"}
    fake.get_json.return_value = hit
    cache = CompiledPromptCache(cache=fake)
    fetch_called = []

    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, h, h, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


# --- L1 TemplateRenderCache ---


def test_template_render_cache_has_get_or_fetch():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    assert hasattr(TemplateRenderCache, "get_or_fetch")


def test_template_render_get_or_fetch_miss():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    fake = _make_fake_cache()
    fake.get.return_value = None
    cache = TemplateRenderCache(cache=fake)
    result = cache.get_or_fetch("tmpl_id", "v1", "a" * 64, lambda: "rendered text")
    assert result == "rendered text"
    fake.set.assert_called_once()


def test_template_render_get_or_fetch_hit():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    fake = _make_fake_cache()
    fake.get.return_value = b"cached rendered text"
    cache = TemplateRenderCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("tmpl_id", "v1", "a" * 64, lambda: fetch_called.append(True))
    assert result == "cached rendered text"
    assert not fetch_called


# --- L3 OrchestrationPlanCache ---


def test_orch_plan_cache_has_get_or_fetch():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    assert hasattr(OrchestrationPlanCache, "get_or_fetch")


def test_orch_plan_get_or_fetch_miss():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    fake = _make_fake_cache()
    cache = OrchestrationPlanCache(cache=fake)
    sentinel = {"step_dag": [], "plan_hash": "a" * 64, "tool_budget_hash": "b" * 64}
    result = cache.get_or_fetch("trace-001", "a" * 64, "b" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_orch_plan_get_or_fetch_hit():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    fake = _make_fake_cache()
    hit = {"step_dag": ["step1"], "plan_hash": "a" * 64}
    fake.get_json.return_value = hit
    cache = OrchestrationPlanCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("trace-001", "a" * 64, "b" * 64, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


# --- L5 SafetyEvalCache ---


def test_safety_eval_cache_has_get_or_fetch():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    assert hasattr(SafetyEvalCache, "get_or_fetch")


def test_safety_eval_get_or_fetch_miss():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    cache = SafetyEvalCache(cache=fake)
    sentinel = {"decision": "allow", "compliance_hash": "a" * 64}
    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_safety_eval_get_or_fetch_hit():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    hit = {"decision": "block", "compliance_hash": "d" * 64}
    fake.get_json.return_value = hit
    cache = SafetyEvalCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


def test_safety_eval_get_or_fetch_replay_bypasses_cache():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"decision": "stale", "compliance_hash": "e" * 64}
    cache = SafetyEvalCache(cache=fake)
    sentinel = {"decision": "allow", "compliance_hash": "f" * 64}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch, replay_mode=True)
    assert result is sentinel
    assert fetch_called


# ---------------------------------------------------------------------------
# §2  NO SHADOW REDIS IN L4
# ---------------------------------------------------------------------------

_LIVE_REDIS_INDICATORS = {
    "redis.Redis",
    "redis.from_url",
    "redis.asyncio",
    "aioredis",
    "Redis(",
}

_TOMBSTONE_CLASS_PREFIX = "_Tombstoned"


def _ast_has_live_redis(source: str, filepath: Path) -> list[str]:
    """Return list of AST node descriptions where live Redis is imported at module level.

    Guarded imports inside function/method bodies (e.g. ``try: import redis``) are
    acceptable optional-dependency patterns and are NOT flagged.  Only module-level
    imports create unconditional shadow Redis clients.
    """
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []

    # Collect all import nodes that are direct children of the module (top-level)
    module_level_imports: set[int] = set()
    for node in ast.iter_child_nodes(tree):
        module_level_imports.add(id(node))

    violations: list[str] = []

    for node in ast.walk(tree):
        if id(node) not in module_level_imports:
            continue  # skip imports inside functions/methods/classes
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("redis") or alias.name.startswith("aioredis"):
                    violations.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and (node.module.startswith("redis") or node.module.startswith("aioredis")):
                violations.append(f"line {node.lineno}: from {node.module} import ...")

    return violations


def _is_tombstone_file(source: str) -> bool:
    """Return True if the file is a tombstone (no live symbols)."""
    return "TOMBSTONED" in source


def test_no_live_redis_client_in_l4_state():
    """AST-scan: L4_state must not contain live Redis imports outside tombstones."""
    violations: dict[str, list[str]] = {}

    for py_file in L4_STATE_DIR.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8", errors="replace")
        if _is_tombstone_file(source):
            continue
        hits = _ast_has_live_redis(source, py_file)
        if hits:
            rel = py_file.relative_to(REPO_ROOT)
            violations[str(rel)] = hits

    assert not violations, (
        "L4_state must not own live Redis clients. "
        "Route through agentic_core.cache instead.\n"
        + "\n".join(f"  {path}:\n" + "\n".join(f"    {v}" for v in hits) for path, hits in violations.items())
    )


def test_tombstoned_redis_classes_raise_on_instantiation():
    """Tombstoned shadow-Redis classes must raise RuntimeError, not silently succeed."""
    from agentic_core.L4_state.memory import blob_storage_provider as bsp

    assert hasattr(bsp, "_TombstonedRedisDistributedLock")
    assert hasattr(bsp, "_TombstonedRedisHotCache")
    assert hasattr(bsp, "_TombstonedHotBrainCache")

    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisDistributedLock()

    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisHotCache()

    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedHotBrainCache()


def test_l4_caching_redis_mcp_client_has_no_live_symbols():
    """redis_mcp_client.py must be a tombstone with no callable symbols."""
    redis_mcp = REPO_ROOT / "agentic_core" / "L4_state" / "caching" / "redis_mcp_client.py"
    source = redis_mcp.read_text(encoding="utf-8", errors="replace")
    assert "TOMBSTONED" in source, "redis_mcp_client.py must be tombstoned"
    tree = ast.parse(source, filename=str(redis_mcp))
    live_classes = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_Tombstoned")
    ]
    live_functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert not live_classes, f"redis_mcp_client.py has live classes: {live_classes}"
    assert not live_functions, f"redis_mcp_client.py has live functions: {live_functions}"


# ---------------------------------------------------------------------------
# §3  HASH VALIDATION STRICTNESS
# ---------------------------------------------------------------------------


def test_require_hash_segment_strict_mode_rejects_short_strings(monkeypatch):
    """In strict mode, non-64-hex strings must raise ValueError."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    # Force reimport to pick up env-var at call time (function reads env inline)
    from agentic_core.cache.cache_key_builders import _require_hash_segment

    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "abc123")

    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "g" * 64)  # invalid hex char

    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "a" * 63)  # one short


def test_require_hash_segment_strict_mode_accepts_valid_sha256(monkeypatch):
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment

    valid = "a" * 64
    _require_hash_segment("test_hash", valid)  # must not raise


def test_require_hash_segment_permissive_mode_accepts_short_strings(monkeypatch):
    """With REDIS_CACHE_STRICT_HASH_VALIDATION=0, any non-empty string is accepted."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")
    from agentic_core.cache.cache_key_builders import _require_hash_segment

    _require_hash_segment("test_hash", "short-placeholder")  # must not raise
    _require_hash_segment("test_hash", "x" * 10)


def test_require_hash_segment_rejects_empty_in_all_modes(monkeypatch):
    """Empty string must always be rejected regardless of strict mode."""
    for val in ("0", "1"):
        monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", val)
        from agentic_core.cache.cache_key_builders import _require_hash_segment

        with pytest.raises(ValueError, match="must not be empty"):
            _require_hash_segment("test_hash", "")
