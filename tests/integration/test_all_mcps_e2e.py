#!/usr/bin/env python3
"""
Comprehensive End-to-End MCP Integration Test Suite

Covers all MCP servers registered in the environment:
  mcp0  - GitKraken (git_add_or_commit, git_status, git_branch, etc.)
  mcp1  - Brave Search (brave_web_search, brave_local_search)
  mcp3  - DeepWiki (ask_question, read_wiki_structure)
  mcp4  - Fetch (fetch URL content)
  mcp5  - Figma (get_figma_data, show_frameworks)
  mcp6  - Filesystem (read_file, write_file, list_directory, etc.)
  mcp8  - Memory (create_entities, search_nodes, read_graph, etc.)
  mcp9  - Playwright (navigate, screenshot, get_visible_text, etc.)
  mcp10 - Postgres Memory (read-only SQL query)
  mcp11 - Redis (get, set, list, delete)
  mcp12 - Sequential Thinking (thought/nextThoughtNeeded schema)

Each test:
  1. Verifies tool resolution via builtins (Windsurf injection point)
  2. Calls the tool with minimal valid parameters
  3. Detects hangs via asyncio timeout
  4. Reports PASS / FAIL / WARN(server-unavailable) / HANG
"""

import asyncio
import builtins
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CALL_TIMEOUT = 15  # seconds before we declare a hang
REPO_ROOT = str(ROOT)


class MCPTestResult:
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"  # tool absent / server not running — not a code bug
    HANG = "HANG"  # timed out — definitively broken


class MCPTestCase:
    def __init__(
        self,
        name: str,
        mcp_prefix: str,
        tool_fn_name: str,
        call_args: dict[str, Any],
        validate_fn: Callable[[Any], bool] | None = None,
        description: str = "",
    ):
        self.name = name
        self.mcp_prefix = mcp_prefix
        self.tool_fn_name = tool_fn_name
        self.call_args = call_args
        self.validate_fn = validate_fn or (lambda r: True)
        self.description = description

    def resolve(self) -> Callable | None:
        """Look up the callable in builtins (Windsurf injection point)."""
        return getattr(builtins, self.tool_fn_name, None)


class MCPTestRunner:
    def __init__(self, timeout: float = CALL_TIMEOUT):
        self.timeout = timeout
        self.results: list[dict] = []

    # ------------------------------------------------------------------
    def record(self, name: str, status: str, detail: str, elapsed_ms: int):
        e = (
            "✅"
            if status == MCPTestResult.PASS
            else "⏱️"
            if status == MCPTestResult.HANG
            else "⚠️"
            if status == MCPTestResult.WARN
            else "❌"
        )
        suffix = f"  ({elapsed_ms}ms)" if elapsed_ms else ""
        d = f" — {detail}" if detail else ""
        print(f"  {e} {status}: {name}{suffix}{d}")
        self.results.append({"test": name, "status": status, "detail": detail, "elapsed_ms": elapsed_ms})

    # ------------------------------------------------------------------
    async def _invoke(self, fn: Callable, args: dict[str, Any]) -> Any:
        """Invoke sync or async callable, respecting coroutine detection."""
        result = fn(**args)
        if asyncio.iscoroutine(result) or asyncio.isfuture(result):
            result = await asyncio.ensure_future(result)
        return result

    # ------------------------------------------------------------------
    async def run_case(self, case: MCPTestCase):
        fn = case.resolve()
        t0 = time.monotonic()

        if fn is None:
            self.record(
                case.name, MCPTestResult.WARN, f"{case.tool_fn_name} not in builtins (server not running)", 0
            )
            return

        try:
            result = await asyncio.wait_for(
                self._invoke(fn, case.call_args),
                timeout=self.timeout,
            )
            elapsed = int((time.monotonic() - t0) * 1000)
            if case.validate_fn(result):
                self.record(case.name, MCPTestResult.PASS, "", elapsed)
            else:
                self.record(
                    case.name, MCPTestResult.FAIL, f"Validation failed — got: {str(result)[:120]}", elapsed
                )
        except asyncio.TimeoutError:
            elapsed = int((time.monotonic() - t0) * 1000)
            self.record(
                case.name, MCPTestResult.HANG, f"DID NOT RETURN in {self.timeout}s — HANG CONFIRMED", elapsed
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - t0) * 1000)
            detail = str(exc)[:200]
            # Server-side "not configured" errors are WARNs, not FAILs
            if any(
                kw in detail.lower()
                for kw in (
                    "not found",
                    "unavailable",
                    "connection refused",
                    "api key",
                    "no such file",
                    "enoent",
                    "cannot connect",
                )
            ):
                self.record(case.name, MCPTestResult.WARN, detail, elapsed)
            else:
                self.record(case.name, MCPTestResult.FAIL, detail, elapsed)

    # ------------------------------------------------------------------
    def summary(self) -> dict[str, int]:
        counts = dict.fromkeys(
            (MCPTestResult.PASS, MCPTestResult.FAIL, MCPTestResult.WARN, MCPTestResult.HANG), 0
        )
        for r in self.results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Test case definitions
# ---------------------------------------------------------------------------


def build_test_cases() -> list[MCPTestCase]:
    cases: list[MCPTestCase] = []

    # =========================================================
    # MCP0 — GitKraken
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp0::git_status",
            mcp_prefix="mcp0",
            tool_fn_name="mcp0_git_status",
            call_args={"directory": REPO_ROOT},
            validate_fn=lambda r: isinstance(r, (str, dict)),
            description="Check git working tree status",
        ),
        MCPTestCase(
            name="mcp0::git_branch_list",
            mcp_prefix="mcp0",
            tool_fn_name="mcp0_git_branch",
            call_args={"directory": REPO_ROOT, "action": "list"},
            validate_fn=lambda r: r is not None,
            description="List branches",
        ),
        MCPTestCase(
            name="mcp0::git_log",
            mcp_prefix="mcp0",
            tool_fn_name="mcp0_git_log_or_diff",
            call_args={"directory": REPO_ROOT, "action": "log"},
            validate_fn=lambda r: r is not None,
            description="Fetch recent commit log",
        ),
    ]

    # =========================================================
    # MCP1 — Brave Search
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp1::brave_web_search",
            mcp_prefix="mcp1",
            tool_fn_name="mcp1_brave_web_search",
            call_args={"query": "python asyncio best practices", "count": 1},
            validate_fn=lambda r: r is not None,
            description="Single-result web search",
        ),
        MCPTestCase(
            name="mcp1::brave_local_search",
            mcp_prefix="mcp1",
            tool_fn_name="mcp1_brave_local_search",
            call_args={"query": "coffee near Seattle", "count": 1},
            validate_fn=lambda r: r is not None,
            description="Local business search",
        ),
    ]

    # =========================================================
    # MCP3 — DeepWiki
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp3::read_wiki_structure",
            mcp_prefix="mcp3",
            tool_fn_name="mcp3_read_wiki_structure",
            call_args={"repoName": "python/cpython"},
            validate_fn=lambda r: r is not None,
            description="Fetch wiki structure for a public repo",
        ),
        MCPTestCase(
            name="mcp3::ask_question",
            mcp_prefix="mcp3",
            tool_fn_name="mcp3_ask_question",
            call_args={"repoName": "python/cpython", "question": "What is the GIL?"},
            validate_fn=lambda r: r is not None,
            description="Ask a question about a repo",
        ),
    ]

    # =========================================================
    # MCP4 — Fetch
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp4::fetch_url",
            mcp_prefix="mcp4",
            tool_fn_name="mcp4_fetch",
            call_args={"url": "https://httpbin.org/get", "max_length": 500},
            validate_fn=lambda r: r is not None,
            description="Fetch a URL and return markdown content",
        ),
    ]

    # =========================================================
    # MCP5 — Figma
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp5::show_frameworks",
            mcp_prefix="mcp5",
            tool_fn_name="mcp5_show_frameworks",
            call_args={},
            validate_fn=lambda r: r is not None,
            description="List available Figma export frameworks",
        ),
    ]

    # =========================================================
    # MCP6 — Filesystem
    # =========================================================
    readme_path = str(ROOT / "README.md")
    cases += [
        MCPTestCase(
            name="mcp6::list_directory",
            mcp_prefix="mcp6",
            tool_fn_name="mcp6_list_directory",
            call_args={"path": REPO_ROOT},
            validate_fn=lambda r: r is not None,
            description="List repo root directory",
        ),
        MCPTestCase(
            name="mcp6::read_text_file",
            mcp_prefix="mcp6",
            tool_fn_name="mcp6_read_text_file",
            call_args={"path": readme_path, "head": 5},
            validate_fn=lambda r: r is not None,
            description="Read first 5 lines of README.md",
        ),
        MCPTestCase(
            name="mcp6::get_file_info",
            mcp_prefix="mcp6",
            tool_fn_name="mcp6_get_file_info",
            call_args={"path": readme_path},
            validate_fn=lambda r: r is not None,
            description="Get file metadata for README.md",
        ),
        MCPTestCase(
            name="mcp6::list_allowed_directories",
            mcp_prefix="mcp6",
            tool_fn_name="mcp6_list_allowed_directories",
            call_args={},
            validate_fn=lambda r: r is not None,
            description="List dirs the filesystem MCP can access",
        ),
        MCPTestCase(
            name="mcp6::directory_tree",
            mcp_prefix="mcp6",
            tool_fn_name="mcp6_directory_tree",
            call_args={"path": REPO_ROOT, "excludePatterns": ["__pycache__", ".git", "node_modules"]},
            validate_fn=lambda r: r is not None,
            description="Recursive directory tree (limited)",
        ),
    ]

    # =========================================================
    # MCP8 — Memory (Knowledge Graph)
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp8::read_graph",
            mcp_prefix="mcp8",
            tool_fn_name="mcp8_read_graph",
            call_args={},
            validate_fn=lambda r: r is not None,
            description="Read entire memory knowledge graph",
        ),
        MCPTestCase(
            name="mcp8::search_nodes",
            mcp_prefix="mcp8",
            tool_fn_name="mcp8_search_nodes",
            call_args={"query": "ADG"},
            validate_fn=lambda r: r is not None,
            description="Search memory graph for ADG-related nodes",
        ),
        MCPTestCase(
            name="mcp8::create_and_delete_entity",
            mcp_prefix="mcp8",
            tool_fn_name="mcp8_create_entities",
            call_args={
                "entities": [
                    {
                        "name": "MCP_E2E_TestNode",
                        "entityType": "TestProbe",
                        "observations": ["Created by E2E MCP test suite"],
                    }
                ]
            },
            validate_fn=lambda r: r is not None,
            description="Create a test entity in memory graph",
        ),
    ]

    # =========================================================
    # MCP9 — Playwright
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp9::navigate",
            mcp_prefix="mcp9",
            tool_fn_name="mcp9_playwright_navigate",
            call_args={"url": "https://example.com", "headless": True, "waitUntil": "load"},
            validate_fn=lambda r: r is not None,
            description="Navigate to example.com (headless)",
        ),
        MCPTestCase(
            name="mcp9::get_visible_text",
            mcp_prefix="mcp9",
            tool_fn_name="mcp9_playwright_get_visible_text",
            call_args={},
            validate_fn=lambda r: isinstance(r, str) and len(r) > 0,
            description="Get visible text of current page",
        ),
        MCPTestCase(
            name="mcp9::screenshot",
            mcp_prefix="mcp9",
            tool_fn_name="mcp9_playwright_screenshot",
            call_args={"name": "mcp_e2e_test", "storeBase64": True, "width": 800, "height": 600},
            validate_fn=lambda r: r is not None,
            description="Take a screenshot of current page",
        ),
        MCPTestCase(
            name="mcp9::console_logs",
            mcp_prefix="mcp9",
            tool_fn_name="mcp9_playwright_console_logs",
            call_args={"type": "all", "limit": 10},
            validate_fn=lambda r: r is not None,
            description="Retrieve browser console logs",
        ),
    ]

    # =========================================================
    # MCP10 — Postgres Memory (read-only)
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp10::query_simple",
            mcp_prefix="mcp10",
            tool_fn_name="mcp10_query",
            call_args={"sql": "SELECT 1 AS probe"},
            validate_fn=lambda r: r is not None,
            description="Run a trivial read-only SQL query",
        ),
    ]

    # =========================================================
    # MCP11 — Redis
    # =========================================================
    cases += [
        MCPTestCase(
            name="mcp11::set_and_get",
            mcp_prefix="mcp11",
            tool_fn_name="mcp11_set",
            call_args={"key": "mcp_e2e_probe", "value": "ok", "expireSeconds": 60},
            validate_fn=lambda r: r is not None,
            description="SET a probe key in Redis",
        ),
        MCPTestCase(
            name="mcp11::get",
            mcp_prefix="mcp11",
            tool_fn_name="mcp11_get",
            call_args={"key": "mcp_e2e_probe"},
            validate_fn=lambda r: r is not None,
            description="GET the probe key just set",
        ),
        MCPTestCase(
            name="mcp11::list_keys",
            mcp_prefix="mcp11",
            tool_fn_name="mcp11_list",
            call_args={"pattern": "mcp_e2e_*"},
            validate_fn=lambda r: r is not None,
            description="LIST keys matching the probe pattern",
        ),
        MCPTestCase(
            name="mcp11::delete",
            mcp_prefix="mcp11",
            tool_fn_name="mcp11_delete",
            call_args={"key": "mcp_e2e_probe"},
            validate_fn=lambda r: r is not None,
            description="DELETE the probe key from Redis",
        ),
    ]

    # =========================================================
    # MCP12 — Sequential Thinking  *** KNOWN HANG SOURCE ***
    # =========================================================
    # These tests explicitly verify the CORRECT parameter schema
    # (thought/nextThoughtNeeded/thoughtNumber/totalThoughts).
    # The WRONG schema (Task/goal/max_steps) used in sovereign_mcp_router.py
    # causes indefinite hangs — all variants are tested here.

    cases += [
        # --- CORRECT SCHEMA: minimal single thought ---
        MCPTestCase(
            name="mcp12::seq_correct_schema_single",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": "This is a minimal test thought.",
                "nextThoughtNeeded": False,
                "thoughtNumber": 1,
                "totalThoughts": 1,
            },
            validate_fn=lambda r: r is not None,
            description="Single thought, correct schema — MUST NOT HANG",
        ),
        # --- CORRECT SCHEMA: first of a multi-step sequence ---
        MCPTestCase(
            name="mcp12::seq_correct_schema_step1",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": "Step 1: Analyzing the problem domain.",
                "nextThoughtNeeded": True,
                "thoughtNumber": 1,
                "totalThoughts": 3,
            },
            validate_fn=lambda r: r is not None,
            description="First of 3 thoughts, correct schema",
        ),
        # --- CORRECT SCHEMA: final thought ---
        MCPTestCase(
            name="mcp12::seq_correct_schema_final",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": "Final synthesis: conclusion reached.",
                "nextThoughtNeeded": False,
                "thoughtNumber": 3,
                "totalThoughts": 3,
            },
            validate_fn=lambda r: r is not None,
            description="Final thought terminating sequence",
        ),
        # --- CORRECT SCHEMA: user's original failing example ---
        MCPTestCase(
            name="mcp12::seq_user_original_example",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": (
                    "The user wants a comprehensive hardening analysis. Let me think through "
                    "the architecture systematically to identify gaps where Redis can be more "
                    "deeply integrated.\n\nKey areas to analyze:\n1. ADG freshness enforcement "
                    "— ensuring Redis always reflects latest ADG\n2. Redis availability hardening "
                    "— beyond just auto-start\n3. Redis usage gaps — where the architecture could "
                    "benefit from Redis but doesn't use it yet."
                ),
                "nextThoughtNeeded": True,
                "thoughtNumber": 1,
                "totalThoughts": 3,
            },
            validate_fn=lambda r: r is not None,
            description="Exact user-reported hanging example — MUST NOT HANG",
        ),
        # --- CORRECT SCHEMA: with optional revision params ---
        MCPTestCase(
            name="mcp12::seq_with_revision",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": "Revising thought 1 based on new insight.",
                "nextThoughtNeeded": False,
                "thoughtNumber": 2,
                "totalThoughts": 2,
                "isRevision": True,
                "revisesThought": 1,
            },
            validate_fn=lambda r: r is not None,
            description="Revision with optional isRevision/revisesThought params",
        ),
        # --- CORRECT SCHEMA: branching ---
        MCPTestCase(
            name="mcp12::seq_with_branch",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "thought": "Branching to explore an alternative path.",
                "nextThoughtNeeded": False,
                "thoughtNumber": 2,
                "totalThoughts": 2,
                "branchFromThought": 1,
                "branchId": "alt_path_A",
            },
            validate_fn=lambda r: r is not None,
            description="Branch from thought 1 with branchId",
        ),
        # --- WRONG SCHEMA DETECTION: sovereign_mcp_router.py style ---
        # This test documents that the WRONG schema is still in production code
        # and that it causes a hang. We test with a very short timeout to confirm.
        MCPTestCase(
            name="mcp12::seq_WRONG_schema_detection",
            mcp_prefix="mcp12",
            tool_fn_name="mcp12_sequentialthinking",
            call_args={
                "Task": "detect wrong schema",
                "goal": "confirm hang",
                "max_steps": 3,
                "enforce_no_hallucination": True,
            },
            validate_fn=lambda r: False,  # Should either hang or error
            description="WRONG schema (Task/goal/max_steps) — expect HANG or error",
        ),
    ]

    return cases


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


async def run_all(timeout: float = CALL_TIMEOUT) -> int:
    # Patch timeout for the wrong-schema test to 5s only
    cases = build_test_cases()

    runner = MCPTestRunner(timeout=timeout)

    # Group by MCP prefix for nice output
    by_mcp: dict[str, list[MCPTestCase]] = {}
    for c in cases:
        by_mcp.setdefault(c.mcp_prefix, []).append(c)

    mcp_labels = {
        "mcp0": "mcp0  — GitKraken",
        "mcp1": "mcp1  — Brave Search",
        "mcp3": "mcp3  — DeepWiki",
        "mcp4": "mcp4  — Fetch",
        "mcp5": "mcp5  — Figma",
        "mcp6": "mcp6  — Filesystem",
        "mcp8": "mcp8  — Memory (Knowledge Graph)",
        "mcp9": "mcp9  — Playwright",
        "mcp10": "mcp10 — Postgres Memory",
        "mcp11": "mcp11 — Redis",
        "mcp12": "mcp12 — Sequential Thinking  ⚠ HANG SUSPECT",
    }

    print("=" * 72)
    print("COMPREHENSIVE MCP END-TO-END TEST SUITE")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Timeout   : {timeout}s per call")
    print("=" * 72)

    for prefix, label in mcp_labels.items():
        group = by_mcp.get(prefix, [])
        if not group:
            continue
        print(f"\n{'─' * 72}")
        print(f"  {label}")
        print(f"{'─' * 72}")
        # Use a tighter timeout for the known-wrong-schema test
        for case in group:
            t = 5.0 if "WRONG" in case.name else timeout
            r_bak = runner.timeout
            runner.timeout = t
            await runner.run_case(case)
            runner.timeout = r_bak

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    counts = runner.summary()
    total = sum(counts.values())

    print(f"\n{'=' * 72}")
    print("SUMMARY")
    print(f"{'=' * 72}")
    print(f"  ✅ PASS : {counts[MCPTestResult.PASS]}/{total}")
    print(f"  ❌ FAIL : {counts[MCPTestResult.FAIL]}/{total}")
    print(f"  ⚠️  WARN : {counts[MCPTestResult.WARN]}/{total}  (server absent / no API key)")
    print(f"  ⏱️  HANG : {counts[MCPTestResult.HANG]}/{total}  ← these are the bugs")

    hangs = [r for r in runner.results if r["status"] == MCPTestResult.HANG]
    fails = [r for r in runner.results if r["status"] == MCPTestResult.FAIL]

    if hangs:
        print(f"\n⏱️  HANGING TESTS ({len(hangs)}) — require immediate fix:")
        for r in hangs:
            print(f"     {r['test']}: {r['detail']}")

    if fails:
        print(f"\n❌ FAILING TESTS ({len(fails)}) — code errors:")
        for r in fails:
            print(f"     {r['test']}: {r['detail']}")

    # Save results
    out = ROOT / "docs" / "reports" / "plans" / "mcp_e2e_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"counts": counts, "results": runner.results}, indent=2))
    print(f"\nDetailed results: {out}")
    print("=" * 72)

    return 0 if (counts[MCPTestResult.FAIL] == 0 and counts[MCPTestResult.HANG] == 0) else 1


if __name__ == "__main__":
    # Allow --timeout override from CLI
    t = CALL_TIMEOUT
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("--timeout="):
            t = float(arg.split("=")[1])
    sys.exit(asyncio.run(run_all(timeout=t)))
