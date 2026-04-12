#!/usr/bin/env python3
"""
pre_prompt_classifier.py — Windsurf pre_user_prompt hard gate + context seeder (Phase 1.4).

Reads JSON payload from stdin. Payload field:
  tool_info.prompt  — the user's prompt text

Classifies the prompt as T0/T1/T2/T3 based on keyword heuristics and writes
tier tag + mandatory requirements to stderr so Cascade sees them (show_output: true).

Exits 0 for T0/T1.
Exits 2 (BLOCK) for T2/T3 when ADG health is red or Redis is down (hard gate).
Exits 0 for T2/T3 when healthy — but emits MANDATORY structured reasoning requirements
so Cascade is instructed to call mcp8_create_task before proceeding.

Fail policy: OPEN for infrastructure errors (probe missing/timeout), CLOSED for T2/T3 with confirmed red ADG/Redis.
Zero hardcoded paths.
"""

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "closed_for_t2t3_adg"

REPO_ROOT = Path(__file__).resolve().parents[2]
# Namespaced per logical session — matches pre_mcp_gate.py and post_mcp_audit.py.
_SESSION_ID = os.environ.get("VSCODE_PID") or str(os.getppid())
SESSION_STATE = REPO_ROOT / "artifacts" / "windsurf" / f"session_state_{_SESSION_ID}.json"

T3_KEYWORDS = {
    "architecture",
    "architectural",
    "cross-layer",
    "refactor",
    "modularize",
    "wave",
    "governance",
    "tier",
    "migration",
    "extract",
    "consolidate",
    "redesign",
    "restructure",
    "multi-file",
    "blast radius",
}

T2_KEYWORDS = {
    "update",
    "modify",
    "fix",
    "debug",
    "add test",
    "change",
    "rename",
    "move",
    "edit",
    "patch",
    "implement",
    "create",
    "write",
}

T1_KEYWORDS = {
    "typo",
    "docstring",
    "comment",
    "whitespace",
    "format",
    "rename variable",
    "single line",
    "one line",
    "trivial",
}

T0_KEYWORDS = {
    "explain",
    "what is",
    "how does",
    "describe",
    "list",
    "show me",
    "review",
    "summarize",
    "tell me",
    "what are",
}

# Tight keyword set — only prompts explicitly about Notion workspace trigger the hint.
# Single-word trigger is sufficient; all notion-intent prompts contain "notion".
NOTION_KEYWORDS: frozenset[str] = frozenset({"notion"})

# Keywords that indicate pytest / test-execution intent — route to pytest_mcp, not run_command.
_PYTEST_SIGNALS: frozenset[str] = frozenset(
    {
        "pytest",
        "run test",
        "run tests",
        "discover test",
        "discover tests",
        "test coverage",
        "coverage report",
        "pytest config",
        "test suite",
        "failing test",
        "failing tests",
        "test output",
        "test results",
        "collect tests",
        "test discovery",
        "run suite",
    }
)


def _detect_pytest_intent(prompt: str) -> bool:
    """Return True when the prompt signals a pytest/test-execution need that pytest_mcp should serve."""
    lower = prompt.lower()
    return any(sig in lower for sig in _PYTEST_SIGNALS)


# Keywords that indicate semantic / meaning-based retrieval need (not structural deps, not literal text).
_SEMANTIC_SIGNALS: frozenset[str] = frozenset(
    {
        "semantic",
        "similar",
        "conceptually",
        "concept",
        "meaning",
        "related content",
        "cross-file",
        "find passages",
        "what talks about",
        "embedding",
        "retrieve context",
        "search for",
        "look for",
        "find similar",
        "grounded retrieval",
        "rag",
    }
)
# Signals that indicate ADG structural territory — exclude to avoid false positives.
_STRUCTURAL_SIGNALS: frozenset[str] = frozenset(
    {
        "imports",
        "depends on",
        "who uses",
        "blast radius",
        "consumers of",
        "import graph",
        "fanin",
        "fanout",
    }
)


def _detect_semantic_retrieval(prompt: str) -> bool:
    """Return True when the prompt signals a semantic/concept search need that vector_db should serve."""
    lower = prompt.lower()
    if any(sig in lower for sig in _STRUCTURAL_SIGNALS):
        return False  # ADG territory, not vector_db
    return any(sig in lower for sig in _SEMANTIC_SIGNALS)


# Structured reasoning mandate injected into Cascade context for every T2/T3 prompt.
# show_output: true ensures Cascade sees this output before responding.
_SR_MANDATE = """
[pre_prompt_classifier] STRUCTURED REASONING REQUIRED ({tier}):
  BEFORE making any edits or tool calls:
  0. ADG-FIRST TOOL ROUTING (MANDATORY — check BEFORE every grep_search call):
     IF query involves import/from/consumer/reference/blast-radius/who-uses/depends-on → USE ADG MCP:
       mcp1_adg_nodes_by_file(file_path) → mcp1_adg_edge_fanin(tgt_id, relation_type="imports")
       mcp1_adg_edge_fanout(src_id, relation_type="imports") for outgoing deps
     IF query targets a function/class/constant name in Python files → USE ADG MCP (not grep)
     IF query is about TODOs/FIXMEs/literal strings/non-Python content → grep_search OK
     IF query involves semantic retrieval, cross-file concept search, or meaning-based lookup
        (NOT structural deps, NOT episodic memory, NOT direct file read) → USE vector_db MCP:
       mcp11_semantic_search(query=...) or mcp11_query_collection(collection_name=..., query_text=...)
     The graph-analysis skill has the full decision tree in tool_routing_decision_tree.md.
     NEVER grep_search for dependency analysis. Constitutional §ADG-First — no exceptions.
  1. Call mem_recall_session_start (Memory MCP) — load persistent project context (ArchitectureLayer, ConstitutionalRule)
  2. Call create_task (task_manager MCP) to register this task with goal + definitions of done
  3. Emit SR_INTAKE block: Objective / Constraints / Assumptions / Tier / Complexity
  4. Emit SR_PLAN: numbered verb-first steps + tools needed + risks
  5. Emit SR_APPROVAL: APPROVED before any writes
  Sequential Thinking MCP is RETIRED. Use: Memory MCP + Task Manager MCP + native Cascade reasoning.
  Rule: .windsurf/rules/sequential-thinking-enforcement.md
  Workflow: /structured-reasoning
""".strip()


_MEMORY_MANDATE = """\
[pre_prompt_classifier] MEMORY RECALL REQUIRED (first turn / new session):
  Call mem_recall_session_start NOW — this MUST be the first MCP tool call.
  Server: memory | Tool: mem_recall_session_start | Parameters: none
  Loads: ArchitectureLayer, ConstitutionalRule, ProjectContext (durable across restarts).
  Do NOT proceed with file reads, ADG queries, or task creation before this call.
""".strip()


def _should_emit_memory_mandate() -> bool:
    """
    Return True if mem_recall_session_start has not been called this session.

    Reads memory_recalled from session_state.json.  Returns True when the file
    is absent (new session), the field is absent (pre-fix state), or the field
    is False (not yet called this turn).  Fail-open on any I/O or parse error.
    """
    try:
        if not SESSION_STATE.exists():
            return True
        state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        return not state.get("memory_recalled", False)
    except (OSError, json.JSONDecodeError):
        return True  # fail-open: emit mandate if state unreadable


_NOTION_SR_HINT = (
    "  NOTION INTENT DETECTED: use the notion MCP directly for Notion workspace operations.\n"
    "    Read  \u2192 mcp6_API-retrieve-a-page(page_id=...)  /  mcp6_API-post-search(query=...)\n"
    "    Write \u2192 mcp6_API-post-page(parent=..., properties=...)  /  mcp6_API-patch-page(page_id=...)\n"
    "  Auth: NOTION_TOKEN must be set in OS env (pre_mcp_gate blocks with setup instructions if absent)."
)

_PYTEST_SR_HINT = (
    "  PYTEST INTENT DETECTED: use pytest_mcp tools instead of run_command for test operations.\n"
    "    Run tests       \u2192 mcp8_run_tests(path=..., keywords=..., verbose=True)\n"
    '    Discover tests  \u2192 mcp8_discover_tests(path="tests")\n'
    '    Coverage        \u2192 mcp8_analyze_test_coverage(path="agentic_core")\n'
    "    Config          \u2192 mcp8_list_pytest_config()\n"
    "    Test details    \u2192 mcp8_get_test_details(test_path=...)\n"
    "  IMPORTANT: pytest_mcp is preferred over run_command for all pytest-specific intents."
)


_TASK_LIFECYCLE_FIELDS = (
    "task_created",
    "task_started",
    "task_decomposed",
    "update_task_count",
    "lessons_captured",
    "memory_recalled",
    "max_memory_block_attempts",
)


def _write_session_state(tier: str) -> None:
    """
    Persist current tier and manage task lifecycle state across prompt turns.

    Reset all lifecycle fields only when transitioning to an independent T0/T1
    prompt (signals prior work is complete).  For T2/T3 prompts — including
    short continuation turns — preserve existing lifecycle fields so active
    tasks are not orphaned mid-session.
    """
    try:
        SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
        if tier in ("T0", "T1"):
            # Independent non-task prompt — full reset is safe.
            state = {
                "current_tier": tier,
                "task_created": False,
                "task_started": False,
                "task_decomposed": False,
                "update_task_count": 0,
                "lessons_captured": False,
                "memory_recalled": False,
                "max_memory_block_attempts": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            # T2/T3 or continuation — preserve existing lifecycle fields.
            try:
                existing = (
                    json.loads(SESSION_STATE.read_text(encoding="utf-8")) if SESSION_STATE.exists() else {}
                )
            except (OSError, json.JSONDecodeError):
                existing = {}
            state = {"current_tier": tier, "timestamp": datetime.now(timezone.utc).isoformat()}
            for field in _TASK_LIFECYCLE_FIELDS:
                default = 0 if field in ("update_task_count", "max_memory_block_attempts") else False
                state[field] = existing.get(field, default)
        SESSION_STATE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass  # fail-open: don't block on state file write failure


def _warn_open_task(tier: str) -> None:
    """
    Emit an advisory warning to stderr when a new T2/T3 prompt arrives while a
    prior task appears to be unclosed (update_task_count < 2).  Warning only —
    never blocks.
    """
    try:
        if not SESSION_STATE.exists():
            return
        state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not state.get("task_created", False):
        return
    if state.get("update_task_count", 0) < 2:
        print(
            f"[pre_prompt_classifier] WARNING: {tier}: prior T2/T3 task was not closed "
            "(update_task_count < 2). Call update_task(status='done', lessons_learned=...) "
            "to close it, or the task will be orphaned.",
            file=sys.stderr,
        )


def classify_tier(prompt: str) -> str:
    lower = prompt.lower()

    t3_hits = sum(1 for kw in T3_KEYWORDS if kw in lower)
    t2_hits = sum(1 for kw in T2_KEYWORDS if kw in lower)
    t1_hits = sum(1 for kw in T1_KEYWORDS if kw in lower)
    t0_hits = sum(1 for kw in T0_KEYWORDS if kw in lower)

    if t3_hits >= 1:
        return "T3"
    if t2_hits >= 2:
        return "T2"
    if t1_hits >= 1:
        return "T1"
    if t0_hits >= 1:
        return "T0"
    if t2_hits >= 1:
        return "T2"

    # Short prompts with zero keyword hits are most likely continuation of
    # ongoing T2/T3 work (e.g. "yes", "proceed", "do it", "implement it").
    # Defaulting to T1 silently bypasses the ADG health gate and SR mandate
    # for all follow-up turns. Conservative default: treat as T2.
    word_count = len(lower.split())
    if word_count <= 4:
        return "T2"

    return "T1"


def check_plan_exists(tier: str) -> bool:
    """Return True if a plan file exists in .windsurf/plans/ for T2/T3."""
    if tier not in ("T2", "T3"):
        return True
    plans_dir = REPO_ROOT / ".windsurf" / "plans"
    if not plans_dir.exists():
        return False
    return any(plans_dir.glob("*.md"))


def check_redis_up() -> bool:
    """
    Return True if Redis is reachable on localhost:6379.
    Fail-open: any socket error other than connection refused returns True (don't block).
    """
    try:
        with socket.create_connection(("localhost", 6379), timeout=2):
            return True  # connected — Redis is up
    except ConnectionRefusedError:
        return False  # Redis is explicitly down
    except OSError:
        return True  # fail-open: network unavailable, don't block


def check_redis_adg_hot() -> bool:
    """
    Return True if the ADG hot cache sentinel key exists in Redis.
    This means ADG was fully ingested into Redis and is ready for queries.
    Fail-open: any error returns False (falls back to ADG MCP probe).
    """
    try:
        import redis

        client = redis.from_url(
            "redis://localhost:6379/0",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        # Find any sentinel key matching adg:v1:*:_hot
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor=cursor, match="adg:v1:*:_hot", count=10)
            if keys:
                return True  # hot cache confirmed
            if cursor == 0:
                break
        return False  # no sentinel found — cache is cold
    except Exception:  # guardian: allow-broad-exception -- startup probe, fail-open
        return False


def check_adg_health_red(repo_root: Path) -> bool:
    """
    Return True if the adg_sqlite MCP server fails a real liveness probe.

    Invokes mcp_health_check.py --server adg_sqlite --json with a 5s timeout.
    Fail-open: any infrastructure error (timeout, missing script, etc.) returns
    False so the gate does not block on probe unavailability.
    """
    probe_script = repo_root / "ops_scripts" / "ci" / "mcp_health_check.py"
    if not probe_script.exists():
        return False  # fail-open: no probe script available

    try:
        result = subprocess.run(
            [sys.executable, str(probe_script), "--server", "adg_sqlite", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=str(repo_root),
        )
    except (subprocess.TimeoutExpired, OSError):
        return False  # fail-open: probe could not run

    if result.returncode == 2:
        return False  # config error — fail-open

    try:
        # JSON block may be preceded by human-readable lines; find the first '{'
        stdout = result.stdout
        json_start = stdout.find("{")
        if json_start < 0:
            return False  # no JSON — fail-open
        data = json.loads(stdout[json_start:])
        servers = data.get("servers", [])
        for srv in servers:
            if srv.get("name") == "adg_sqlite":
                return bool(srv.get("status") != "ok")
        return True  # adg_sqlite absent from probe results — treat as red
    except (json.JSONDecodeError, KeyError):
        return False  # parse error — fail-open (probe infrastructure error)


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    prompt = tool_info.get("user_prompt", "") or tool_info.get("prompt", "")

    if not prompt:
        return 0

    tier = classify_tier(prompt)
    print(f"[pre_prompt_classifier] Tier: {tier}", file=sys.stderr)

    # vector_db routing trace: emitted for every prompt so selection vs non-selection is observable.
    if _detect_semantic_retrieval(prompt):
        print(
            "[pre_prompt_classifier] vector_db: semantic_retrieval=DETECTED "
            "— candidate: mcp11_semantic_search / mcp11_query_collection",
            file=sys.stderr,
        )
    else:
        print("[pre_prompt_classifier] vector_db: semantic_retrieval=NOT_DETECTED", file=sys.stderr)

    # pytest_mcp routing trace: emitted for every prompt so pytest_mcp candidate visibility is observable.
    if _detect_pytest_intent(prompt):
        print(
            "[pre_prompt_classifier] PYTEST_MCP_TRACE: pytest_intent=DETECTED "
            "— candidate: mcp8_run_tests / mcp8_discover_tests / mcp8_list_pytest_config "
            "/ mcp8_analyze_test_coverage / mcp8_get_test_details. "
            "PREFER pytest_mcp over run_command for pytest-specific intents.",
            file=sys.stderr,
        )
    else:
        print("[pre_prompt_classifier] PYTEST_MCP_TRACE: pytest_intent=NOT_DETECTED", file=sys.stderr)

    # Read BEFORE the state write: T0/T1 reset would otherwise shadow a True
    # value and incorrectly re-emit the mandate on a turn where memory was
    # already recalled.
    emit_memory_mandate = _should_emit_memory_mandate()

    # Advisory: warn before state update so we read the prior turn's lifecycle state.
    if tier in ("T2", "T3"):
        _warn_open_task(tier)

    # Persist tier; preserve or reset lifecycle fields per approved design.
    _write_session_state(tier)

    # Memory mandate: fires for ALL tiers on the first turn of each session.
    # Suppressed once post_mcp_audit marks memory_recalled=True in session state.
    if emit_memory_mandate:
        print(_MEMORY_MANDATE, file=sys.stderr)

    if tier in ("T2", "T3"):
        if not check_plan_exists(tier):
            print(
                f"[pre_prompt_classifier] WARNING: {tier} prompt detected but no plan file found "
                "in .windsurf/plans/ — consider creating a plan per constitutional §10.",
                file=sys.stderr,
            )

        # --- ADG health check: Redis first (preferred), ADG MCP as fallback ---
        if check_redis_up():
            if check_redis_adg_hot():
                # Redis is up AND ADG hot cache is populated — preferred path, no ADG MCP probe needed
                print(
                    f"[pre_prompt_classifier] {tier}: Redis ADG hot cache confirmed — proceeding.",
                    file=sys.stderr,
                )
            else:
                # Redis is up but ADG cache is cold — warn and fall back to ADG MCP probe
                print(
                    f"[pre_prompt_classifier] WARNING: {tier}: Redis is up but ADG cache is cold. "
                    "Run: python tools/adg/adg_redis_ingest.py --force",
                    file=sys.stderr,
                )
                if check_adg_health_red(REPO_ROOT):
                    print(
                        f"[pre_prompt_classifier] BLOCKED: {tier} prompt — adg_sqlite MCP is also red. "
                        "Run mcp1_adg_health and /mcp-failure-rca before proceeding (constitutional §13).",
                        file=sys.stderr,
                    )
                    return 2
        else:
            # Redis is down — fall back entirely to ADG MCP probe
            print(
                f"[pre_prompt_classifier] WARNING: {tier}: Redis is down — falling back to adg_sqlite MCP probe.",
                file=sys.stderr,
            )
            if check_adg_health_red(REPO_ROOT):
                print(
                    f"[pre_prompt_classifier] BLOCKED: {tier} prompt — Redis is down AND adg_sqlite MCP is red. "
                    "Start Redis or run mcp1_adg_health and /mcp-failure-rca before proceeding (constitutional §13).",
                    file=sys.stderr,
                )
                return 2

        # Infrastructure healthy — inject structured reasoning mandate into Cascade context.
        # show_output: true in hooks.json ensures Cascade sees this before responding.
        mandate = _SR_MANDATE.format(tier=tier)
        if any(kw in prompt.lower() for kw in NOTION_KEYWORDS):
            mandate = mandate + "\n" + _NOTION_SR_HINT
        if _detect_pytest_intent(prompt):
            mandate = mandate + "\n" + _PYTEST_SR_HINT
        print(mandate, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
