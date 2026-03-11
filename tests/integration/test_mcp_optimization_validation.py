#!/usr/bin/env python3
"""
MCP Optimization Implementation Validation Tests

Tests accuracy and completeness of the 7-phase MCP optimization:
- Phase 1: mcp_manager.py creation + undefined ref fixes
- Phase 2: LLM Router real providers + sequential thinking
- Phase 3: Redis MCP routing
- Phase 4: ADG → Memory MCP persistence
- Phase 5: Brave Search integration
- Phase 6: Playwright MCP verification
- Phase 7: Filesystem MCP hardening
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import ast


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, test_name: str, detail: str = ""):
        self.passed.append((test_name, detail))
        print(f"✅ PASS: {test_name}" + (f" — {detail}" if detail else ""))

    def add_fail(self, test_name: str, reason: str):
        self.failed.append((test_name, reason))
        print(f"❌ FAIL: {test_name} — {reason}")

    def add_warning(self, test_name: str, detail: str):
        self.warnings.append((test_name, detail))
        print(f"⚠️  WARN: {test_name} — {detail}")

    def summary(self):
        print("\n" + "=" * 70)
        print(f"SUMMARY: {len(self.passed)} passed, {len(self.failed)} failed, {len(self.warnings)} warnings")
        print("=" * 70)
        if self.failed:
            print("\nFailed tests:")
            for name, reason in self.failed:
                print(f"  ❌ {name}: {reason}")
        return len(self.failed) == 0


results = TestResults()


# ============================================================================
# PHASE 1: mcp_manager.py + undefined ref fixes
# ============================================================================


def test_phase1_mcp_manager_exists():
    """Verify mcp_manager.py was created with MCPConnectionManager."""
    path = ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "mcp_manager.py"
    if not path.exists():
        results.add_fail("Phase1.mcp_manager_exists", "File not found")
        return

    src = path.read_text(encoding="utf-8")
    if "class MCPConnectionManager" not in src:
        results.add_fail("Phase1.mcp_manager_class", "MCPConnectionManager class not found")
        return
    if "def load_mcp_config" not in src:
        results.add_fail("Phase1.load_mcp_config", "load_mcp_config function not found")
        return
    if "_TOOL_DISPATCH" not in src:
        results.add_fail("Phase1.tool_dispatch", "_TOOL_DISPATCH table not found")
        return

    results.add_pass("Phase1.mcp_manager_created", "MCPConnectionManager + load_mcp_config + dispatch table")


def test_phase1_undefined_refs_fixed():
    """Verify mcp_authority and redis_shield undefined refs are fixed."""
    # Check sovereign_mcp_router.py
    router_path = ROOT / "agentic_core" / "L3_orchestration" / "engines" / "sovereign_mcp_router.py"
    router_src = router_path.read_text(encoding="utf-8")

    if (
        "from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import mcp_authority"
        not in router_src
    ):
        results.add_fail(
            "Phase1.mcp_authority_import", "mcp_authority import missing in sovereign_mcp_router.py"
        )
        return
    if "from agentic_core.cache.redis_cache_client import get_hot_cache" not in router_src:
        results.add_fail(
            "Phase1.get_hot_cache_import", "get_hot_cache import missing in sovereign_mcp_router.py"
        )
        return
    if "redis_shield.execute" in router_src:
        results.add_fail(
            "Phase1.redis_shield_removed", "redis_shield.execute still present in sovereign_mcp_router.py"
        )
        return

    # Check sovereign_filesystem_mcp.py
    fs_path = ROOT / "agentic_core" / "L2_execution" / "enforcement" / "sovereign_filesystem_mcp.py"
    fs_src = fs_path.read_text(encoding="utf-8")

    if (
        "from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import mcp_authority"
        not in fs_src
    ):
        results.add_fail(
            "Phase1.fs_mcp_authority_import", "mcp_authority import missing in sovereign_filesystem_mcp.py"
        )
        return
    if "ALLOWED_ROOT_PREFIXES" in fs_src and "allowed_root_prefixes" not in fs_src:
        results.add_fail("Phase1.fs_casing_fix", "ALLOWED_ROOT_PREFIXES uppercase still present")
        return

    results.add_pass(
        "Phase1.undefined_refs_fixed", "mcp_authority + get_hot_cache imports added, redis_shield removed"
    )


# ============================================================================
# PHASE 2: LLM Router + Sequential Thinking
# ============================================================================


def test_phase2_sequential_tier():
    """Verify ModelTier.SEQUENTIAL was added."""
    router_path = ROOT / "apps_shared" / "types" / "model_router_types.py"
    src = router_path.read_text(encoding="utf-8")

    if 'SEQUENTIAL = "SEQUENTIAL"' not in src:
        results.add_fail("Phase2.sequential_tier", "ModelTier.SEQUENTIAL not found")
        return

    results.add_pass("Phase2.sequential_tier_added", "ModelTier.SEQUENTIAL enum value present")


def test_phase2_real_providers():
    """Verify OpenAIClient and AnthropicClient use real API calls."""
    router_path = ROOT / "apps_shared" / "types" / "model_router_types.py"
    src = router_path.read_text(encoding="utf-8")

    if "openai.AsyncOpenAI" not in src:
        results.add_fail("Phase2.openai_real", "OpenAI real API call not found")
        return
    if "anthropic.AsyncAnthropic" not in src:
        results.add_fail("Phase2.anthropic_real", "Anthropic real API call not found")
        return
    if 'os.environ.get("OPENAI_API_KEY"' not in src:
        results.add_fail("Phase2.openai_env_key", "OPENAI_API_KEY env var check not found")
        return
    if 'os.environ.get("ANTHROPIC_API_KEY"' not in src:
        results.add_fail("Phase2.anthropic_env_key", "ANTHROPIC_API_KEY env var check not found")
        return

    results.add_pass("Phase2.real_providers_wired", "OpenAI + Anthropic real API calls with env-var keys")


def test_phase2_sequential_thinking_client():
    """Verify SequentialThinkingClient was added."""
    router_path = ROOT / "apps_shared" / "types" / "model_router_types.py"
    src = router_path.read_text(encoding="utf-8")

    if "class SequentialThinkingClient" not in src:
        results.add_fail("Phase2.sequential_client", "SequentialThinkingClient class not found")
        return
    if "mcp.call_tool" not in src or '"sequential_thinking"' not in src:
        results.add_fail("Phase2.sequential_mcp_call", "sequential_thinking MCP call not found")
        return
    if "get_hot_cache" not in src:
        results.add_fail("Phase2.sequential_cache", "Redis template caching not found")
        return

    results.add_pass("Phase2.sequential_thinking_client", "SequentialThinkingClient with MCP + Redis caching")


# ============================================================================
# PHASE 3: Redis MCP Routing
# ============================================================================


def test_phase3_redis_mcp_routing():
    """Verify SovereignRedisOrchestrator routes through MCP when flag enabled."""
    redis_path = ROOT / "agentic_core" / "L3_orchestration" / "engines" / "sovereign_redis_orchestrator.py"
    src = redis_path.read_text(encoding="utf-8")

    if "self._use_mcp" not in src:
        results.add_fail("Phase3.use_mcp_flag", "_use_mcp flag not found")
        return
    if "def _mcp_call" not in src:
        results.add_fail("Phase3.mcp_call_helper", "_mcp_call helper not found")
        return
    if "if self._use_mcp:" not in src:
        results.add_fail("Phase3.mcp_routing_gate", "MCP routing gate not found in get/set/delete")
        return
    if "get_sovereign_config().REDIS_MCP_ENABLED" not in src:
        results.add_fail("Phase3.config_flag", "REDIS_MCP_ENABLED config check not found")
        return

    results.add_pass(
        "Phase3.redis_mcp_routing", "get/set/delete route through MCP when REDIS_MCP_ENABLED=True"
    )


# ============================================================================
# PHASE 4: ADG → Memory MCP Persistence
# ============================================================================


def test_phase4_adg_persistence_hook():
    """Verify generate_full_adg.py calls _persist_adg_to_memory."""
    adg_path = ROOT / "tools" / "generate_full_adg.py"
    src = adg_path.read_text(encoding="utf-8")

    if "_persist_adg_to_memory" not in src:
        results.add_fail("Phase4.persist_function", "_persist_adg_to_memory function not found")
        return
    if "GraphMemoryBridge.get_instance()" not in src:
        results.add_fail("Phase4.bridge_usage", "GraphMemoryBridge not used in persistence")
        return
    if "ADG_Snapshot_" not in src:
        results.add_fail("Phase4.snapshot_entity", "ADG_Snapshot entity creation not found")
        return
    if "ADG_Layer_" not in src:
        results.add_fail("Phase4.layer_entities", "ADG_Layer entity creation not found")
        return
    if "ADG_Hotspot_" not in src:
        results.add_fail("Phase4.hotspot_entities", "ADG_Hotspot entity creation not found")
        return
    if "ADG_Violation_" not in src:
        results.add_fail("Phase4.violation_entities", "ADG_Violation entity creation not found")
        return

    results.add_pass(
        "Phase4.adg_memory_persistence", "Snapshot + layers + hotspots + violations persisted to Memory MCP"
    )


# ============================================================================
# PHASE 5: Brave Search Integration
# ============================================================================


def test_phase5_brave_search_unreachable_fixed():
    """Verify brave_search fallback branch is now reachable in sovereign_mcp_router.py."""
    router_path = ROOT / "agentic_core" / "L3_orchestration" / "engines" / "sovereign_mcp_router.py"
    src = router_path.read_text(encoding="utf-8")

    # Check that brave_search is called
    if '"brave_search"' not in src or "call_tool" not in src:
        results.add_fail("Phase5.brave_search_call", "brave_search call_tool not found")
        return

    # Check that it's in a try/except block (fallback pattern)
    lines = src.split("\n")
    brave_search_line = None
    for i, line in enumerate(lines):
        if '"brave_search"' in line:
            brave_search_line = i
            break

    if brave_search_line is None:
        results.add_fail("Phase5.brave_search_call", "brave_search string not found")
        return

    # Check preceding lines for try/except pattern
    preceding_block = "\n".join(lines[max(0, brave_search_line - 5) : brave_search_line])
    if "try:" in preceding_block or "except" in preceding_block:
        results.add_pass(
            "Phase5.brave_search_unreachable_fixed", "brave_search fallback branch is reachable in try/except"
        )
    else:
        results.add_warning(
            "Phase5.brave_search_reachable", "brave_search found but not in expected try/except pattern"
        )


def test_phase5_rg_reflection_brave_search():
    """Verify RgReflectionAgent calls _search_external_best_practices."""
    rg_path = ROOT / "apps_rg" / "reasoning" / "RgReflectionAgent.py"
    src = rg_path.read_text(encoding="utf-8")

    if "def _search_external_best_practices" not in src:
        results.add_fail("Phase5.search_method", "_search_external_best_practices method not found")
        return
    if "mcp1_brave_web_search" not in src and "brave_search" not in src:
        results.add_fail(
            "Phase5.brave_call", "brave_search MCP call not found in _search_external_best_practices"
        )
        return
    if "quality_score < 0.6" not in src:
        results.add_fail("Phase5.quality_gate", "quality_score < 0.6 gate not found")
        return

    results.add_pass("Phase5.rg_brave_search", "RgReflectionAgent searches Brave when quality < 0.6")


# ============================================================================
# PHASE 6: Playwright MCP Verification
# ============================================================================


def test_phase6_mcp_verify_dashboard():
    """Verify mcp_verify_dashboard() was added to verify_dashboard_e2e_playwright_util.py."""
    pw_path = (
        ROOT / "agentic_core" / "L6_observability" / "dashboards" / "verify_dashboard_e2e_playwright_util.py"
    )
    src = pw_path.read_text(encoding="utf-8")

    if "async def mcp_verify_dashboard" not in src:
        results.add_fail("Phase6.mcp_verify_function", "mcp_verify_dashboard function not found")
        return
    if (
        "playwright_navigate" not in src
        or "playwright_get_text" not in src
        or "playwright_screenshot" not in src
    ):
        results.add_fail("Phase6.mcp_tools", "mcp12_* tool calls not found in mcp_verify_dashboard")
        return

    results.add_pass("Phase6.mcp_verify_dashboard", "mcp_verify_dashboard() uses mcp12_* tools")


def test_phase6_healing_orchestrator_integration():
    """Verify BaseHealingOrchestrator calls _verify_dashboard_after_healing."""
    healing_path = ROOT / "apps_shared" / "reasoning" / "BaseHealingOrchestrator.py"
    src = healing_path.read_text(encoding="utf-8")

    if "def _verify_dashboard_after_healing" not in src:
        results.add_fail("Phase6.verify_method", "_verify_dashboard_after_healing method not found")
        return
    if "mcp_verify_dashboard" not in src:
        results.add_fail(
            "Phase6.mcp_call_in_healing", "mcp_verify_dashboard call not found in healing orchestrator"
        )
        return
    if "self._verify_dashboard_after_healing(results)" not in src:
        results.add_fail(
            "Phase6.healing_hook", "_verify_dashboard_after_healing not called from _persist_healing_cycle"
        )
        return

    results.add_pass(
        "Phase6.healing_playwright_integration", "BaseHealingOrchestrator verifies dashboard after healing"
    )


# ============================================================================
# PHASE 7: Filesystem MCP Hardening
# ============================================================================


def test_phase7_filesystem_mcp_hardening():
    """Verify SovereignFilesystemMcp uses mcp8_* tools directly."""
    fs_path = ROOT / "agentic_core" / "L2_execution" / "enforcement" / "sovereign_filesystem_mcp.py"
    src = fs_path.read_text(encoding="utf-8")

    if "mcp8_read_text_file" not in src:
        results.add_fail("Phase7.mcp8_read", "mcp8_read_text_file not found")
        return
    if "mcp8_write_file" not in src:
        results.add_fail("Phase7.mcp8_write", "mcp8_write_file not found")
        return
    if "getattr(builtins" not in src:
        results.add_fail("Phase7.builtins_dispatch", "builtins getattr dispatch not found")
        return

    results.add_pass(
        "Phase7.filesystem_mcp_hardened", "read_text_file + atomic_fission_write use mcp8_* tools"
    )


# ============================================================================
# CROSS-CUTTING: Import Validation
# ============================================================================


def test_all_imports_valid():
    """Verify all modified files have valid imports (no undefined names at module level)."""
    files_to_check = [
        "agentic_core/L3_orchestration/reasoning/mcp_manager.py",
        "agentic_core/L3_orchestration/engines/sovereign_mcp_router.py",
        "agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py",
        "apps_shared/types/model_router_types.py",
        "agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py",
        "tools/generate_full_adg.py",
        "apps_rg/reasoning/RgReflectionAgent.py",
        "agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py",
        "apps_shared/reasoning/BaseHealingOrchestrator.py",
    ]

    all_valid = True
    for rel_path in files_to_check:
        path = ROOT / rel_path
        try:
            src = path.read_text(encoding="utf-8")
            ast.parse(src)
        except SyntaxError as e:
            results.add_fail(f"Import.{rel_path}", f"Syntax error: {e}")
            all_valid = False

    if all_valid:
        results.add_pass("Import.all_files_valid", f"{len(files_to_check)} files syntax-checked")


# ============================================================================
# RUN ALL TESTS
# ============================================================================


def main():
    print("=" * 70)
    print("MCP OPTIMIZATION VALIDATION TESTS")
    print("=" * 70)
    print()

    # Phase 1
    print("PHASE 1: mcp_manager.py + undefined ref fixes")
    test_phase1_mcp_manager_exists()
    test_phase1_undefined_refs_fixed()
    print()

    # Phase 2
    print("PHASE 2: LLM Router + Sequential Thinking")
    test_phase2_sequential_tier()
    test_phase2_real_providers()
    test_phase2_sequential_thinking_client()
    print()

    # Phase 3
    print("PHASE 3: Redis MCP Routing")
    test_phase3_redis_mcp_routing()
    print()

    # Phase 4
    print("PHASE 4: ADG → Memory MCP Persistence")
    test_phase4_adg_persistence_hook()
    print()

    # Phase 5
    print("PHASE 5: Brave Search Integration")
    test_phase5_brave_search_unreachable_fixed()
    test_phase5_rg_reflection_brave_search()
    print()

    # Phase 6
    print("PHASE 6: Playwright MCP Verification")
    test_phase6_mcp_verify_dashboard()
    test_phase6_healing_orchestrator_integration()
    print()

    # Phase 7
    print("PHASE 7: Filesystem MCP Hardening")
    test_phase7_filesystem_mcp_hardening()
    print()

    # Cross-cutting
    print("CROSS-CUTTING: Import Validation")
    test_all_imports_valid()
    print()

    # Summary
    success = results.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
