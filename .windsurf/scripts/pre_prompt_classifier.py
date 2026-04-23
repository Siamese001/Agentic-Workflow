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
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "closed_for_t2t3_adg"

repo_root = Path(__file__).resolve().parents[2]
# Namespaced per logical session — matches pre_mcp_gate.py and post_mcp_audit.py.
_session_id = os.environ.get("VSCODE_PID") or str(os.getppid())
session_state = repo_root / "artifacts" / "windsurf" / f"session_state_{_session_id}.json"

t3_keywords = {
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

t2_keywords = {
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

t1_keywords = {
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

t0_keywords = {
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
notion_keywords: frozenset[str] = frozenset({"notion"})

# Keywords that indicate runtime observability intent — route to otel_mcp.
_OTEL_SIGNALS: frozenset[str] = frozenset(
    {
        "otel",
        "opentelemetry",
        "runtime trace",
        "runtime traces",
        "live span",
        "live spans",
        "telemetry",
        "healing chain",
        "policy decision",
        "policy decisions",
        "circuit breaker",
        "safety plane",
        "runtime anomal",
        "runtime rca",
        "what happened at runtime",
        "what happened during",
    }
)

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


def _detect_otel_intent(prompt: str) -> bool:
    """Return True when the prompt signals a runtime observability need that otel_mcp should serve."""
    lower = prompt.lower()
    return any(sig in lower for sig in _OTEL_SIGNALS)


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

# Keywords that indicate ADG structural graph-query intent — route to adg_sqlite first.
_ADG_GRAPH_SIGNALS: frozenset[str] = frozenset(
    {
        "who imports",
        "who uses",
        "who calls",
        "depends on",
        "blast radius",
        "blast-radius",
        "fanin",
        "fanout",
        "fan-in",
        "fan-out",
        "consumers of",
        "consumers",
        "import graph",
        "importers of",
        "dependency graph",
        "which files import",
        "what imports",
        "what depends on",
        "impact analysis",
        "graph query",
        "adg query",
    }
)


def _detect_adg_graph_intent(prompt: str) -> bool:
    """Return True when the prompt signals an ADG structural graph query."""
    lower = prompt.lower()
    return any(sig in lower for sig in _ADG_GRAPH_SIGNALS)


def _detect_semantic_retrieval(prompt: str) -> bool:
    """Return True when the prompt signals a semantic/concept search need that vector_db should serve."""
    lower = prompt.lower()
    if any(sig in lower for sig in _STRUCTURAL_SIGNALS):
        return False  # ADG territory, not vector_db
    return any(sig in lower for sig in _SEMANTIC_SIGNALS)


# Structured reasoning mandate injected into Cascade context for every T2/T3 prompt.
# show_output: true ensures Cascade sees this output before responding.
_sr_mandate = """
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
     DEGRADED FALLBACK (graph queries only): grep is ONLY allowed after mcp1_adg_health confirms red.
       Required: call mcp1_adg_health first → if red, emit DEGRADED_FALLBACK: reason=<adg_red|snapshot_missing|...>
       Silent grep-for-graph (no health check + no reason code) = POLICY VIOLATION.
  0b. REFACTORING-ONLY — ADG GRAPH LAYER IS PRIMARY (constitutional §22):
     ARCHITECTURE: ADG is SQLite (relational) + a graph-layer overlay (nodes/edges
     tables + materialized views + pre-classified P-views + semantic edges).
     The overlay provides graph-DB semantics (fan-in, blast radius, centrality,
     chokepoints, critical paths) WITHOUT a separate Neo4j-style store.
     Refactoring MUST use graph-layer primitives (MVs / P-views / semantic edges),
     NOT raw `SELECT COUNT(*) FROM violations` or grep.
     If this task involves refactoring / wave planning / antipattern burndown / prioritization:
     REQUIRED BEFORE target selection:
       (i)   Hotspot report — query `mv_graph_reverse_dependency_hotspots`,
             `mv_debt_concentration_hotspots`, `mv_hotspot_centrality` via the
             ADG SQLite snapshot. Plan MUST contain `## ADG_HOTSPOT_REPORT`.
       (ii)  Graph-layer evidence — cite at least 3 materialized views (`mv_*`),
             at least 1 semantic edge beyond `imports` (`flows_to`, `reads_from`,
             `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite`)
             OR 1 pre-built P-view (`v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*`).
             Plan MUST contain `## ADG_GRAPH_LAYER_EVIDENCE`.
       (iii) Wave ordering — derive from `mcp1_adg_p0_wave_plan` output,
             not from alphabetical / "feels important" intuition.
       (iv)  Hotspot classification — every row in ## ADG_HOTSPOT_REPORT MUST
             include one of 4 archetypes (CENTRAL_DEPENDENCY, ORCHESTRATOR,
             STATE_NODE, SAFETY_GATEKEEPER) AND cross-reference the 5 ADG
             Surfaces (Execution / Write / Security / State / Observability).
       (v)   Layer multiplier — apply L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75.
       (vi)  Static vs Runtime — use `adg_sqlite` for structural queries;
             use `otel_mcp` for runtime span/trace/healing-chain questions.
             Do not conflate them.
       (vii) SSOT hierarchy — SQLite=truth, Redis=hot projection, MCP=read-only.
             If Redis or MCP disagrees with SQLite, SQLite wins.
     FORBIDDEN: refactoring plans citing only raw `edges`/`violations` counts
     or lacking archetype/surface classification.
     Rules: adg-canonical-invariants.md, adg-hotspot-enforcement.md, adg-graph-layer-enforcement.md
     CI gate: ops_scripts/ci/check_graph_layer_evidence.py
  1. Call mem_recall_session_start (Memory MCP) — load persistent project context (ArchitectureLayer, ConstitutionalRule)
  2. Call create_task (task_manager MCP) to register this task with goal + definitions of done
  3. Emit SR_INTAKE block: Objective / Constraints / Assumptions / Tier / Complexity
  4. Emit SR_PLAN: numbered verb-first steps + tools needed + risks
  5. Emit SR_APPROVAL: APPROVED before any writes
  Sequential Thinking MCP is RETIRED. Use: Memory MCP + Task Manager MCP + native Cascade reasoning.
  Rule: .windsurf/rules/sequential-thinking-enforcement.md
  Workflow: /structured-reasoning
""".strip()


_memory_mandate = (
    "[pre_prompt_classifier] memory: mem_recall_session_start not yet called this session"
    " (human diagnostic — pre_mcp_gate enforces via exit 2)."
)


def _should_emit_memory_mandate() -> bool:
    """
    Return True if mem_recall_session_start has not been called this session.

    Reads memory_recalled from session_state.json.  Returns True when the file
    is absent (new session), the field is absent (pre-fix state), or the field
    is False (not yet called this turn).  Fail-open on any I/O or parse error.
    """
    try:
        if not session_state.exists():
            return True
        state = json.loads(session_state.read_text(encoding="utf-8"))
        return not state.get("memory_recalled", False)
    except (OSError, json.JSONDecodeError):
        return True  # fail-open: emit mandate if state unreadable


_adg_graph_sr_hint = (
    "  ADG GRAPH INTENT DETECTED: adg_sqlite tools REQUIRED for this query.\n"
    "    Routing matrix:\n"
    "      imports/consumers/blast-radius/fanin/fanout → mcp1_adg_edge_fanin / mcp1_adg_edge_fanout\n"
    "      function/class/constant name in *.py       → mcp1_adg_find_node → mcp1_adg_edge_fanin\n"
    "      layer analysis (L0-L6)                     → mcp1_adg_nodes_by_layer\n"
    "      file-level deps                            → mcp1_adg_nodes_by_file\n"
    "  Health-first rule: if adg_sqlite may be red, call mcp1_adg_health BEFORE any grep fallback.\n"
    "  Degraded fallback: ONLY after health red — emit DEGRADED_FALLBACK: reason=<adg_red|...>\n"
    "  Silent grep-for-graph (no health check, no reason code) is a POLICY VIOLATION."
)

_notion_sr_hint = (
    "  NOTION INTENT DETECTED: use the notion MCP directly for Notion workspace operations.\n"
    "    Read  \u2192 mcp6_API-retrieve-a-page(page_id=...)  /  mcp6_API-post-search(query=...)\n"
    "    Write \u2192 mcp6_API-post-page(parent=..., properties=...)  /  mcp6_API-patch-page(page_id=...)\n"
    "  Auth: NOTION_TOKEN must be set in OS env (pre_mcp_gate blocks with setup instructions if absent)."
)

_otel_sr_hint = (
    "  OTEL INTENT DETECTED: use otel_mcp tools for runtime observability.\n"
    "    Health / freshness  \u2192 mcp7_otel_status()\n"
    "    Fetch trace         \u2192 mcp7_otel_trace(trace_id=...)\n"
    "    Agent spans         \u2192 mcp7_otel_spans_by_agent(agent_class=...)\n"
    "    Anomalies           \u2192 mcp7_otel_anomalies(severity='any')\n"
    "    Healing chain       \u2192 mcp7_otel_healing_chain(trace_id=...)\n"
    "    Policy decisions    \u2192 mcp7_otel_policy_decisions(time_window_hours=24)\n"
    "    Metrics             \u2192 mcp7_otel_metrics_summary()\n"
    "  Note: mcp7_ prefix may shift on server add/remove — server name otel_mcp is the SSOT."
)

_pytest_sr_hint = (
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
        session_state.parent.mkdir(parents=True, exist_ok=True)
        if tier in ("T0", "T1"):
            # Independent non-task prompt — task lifecycle reset is safe.
            # Preserve memory_recalled: it is a session-level flag, not a task flag.
            try:
                _prior = (
                    json.loads(session_state.read_text(encoding="utf-8")) if session_state.exists() else {}
                )
            except (OSError, json.JSONDecodeError):
                _prior = {}
            state = {
                "current_tier": tier,
                "task_created": False,
                "task_started": False,
                "task_decomposed": False,
                "update_task_count": 0,
                "lessons_captured": False,
                "memory_recalled": _prior.get("memory_recalled", False),
                "max_memory_block_attempts": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            # T2/T3 or continuation — preserve existing lifecycle fields.
            try:
                existing = (
                    json.loads(session_state.read_text(encoding="utf-8")) if session_state.exists() else {}
                )
            except (OSError, json.JSONDecodeError):
                existing = {}
            state = {"current_tier": tier, "timestamp": datetime.now(timezone.utc).isoformat()}
            for field in _TASK_LIFECYCLE_FIELDS:
                default = 0 if field in ("update_task_count", "max_memory_block_attempts") else False
                state[field] = existing.get(field, default)
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except OSError:  # guardian: allow-silent-swallow -- session state write: non-fatal, fail-open
        pass  # fail-open: don't block on state file write failure


def _warn_open_task(tier: str) -> None:
    """
    Emit an advisory warning to stderr when a new T2/T3 prompt arrives while a
    prior task appears to be unclosed (update_task_count < 2).  Warning only —
    never blocks.
    """
    try:
        if not session_state.exists():
            return
        state = json.loads(session_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-silent-swallow -- task lifecycle check: non-fatal, check skipped
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

    t3_hits = sum(1 for kw in t3_keywords if kw in lower)
    t2_hits = sum(1 for kw in t2_keywords if kw in lower)
    t1_hits = sum(1 for kw in t1_keywords if kw in lower)
    t0_hits = sum(1 for kw in t0_keywords if kw in lower)

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
    plans_dir = repo_root / ".windsurf" / "plans"
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
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
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


def _check_mcp_config_drift() -> None:
    """
    Detect and auto-fix env-block drift between repo MCP config and global Windsurf config.

    Windsurf IDE can overwrite ~/.codeium/windsurf/mcp_config.json (e.g. via the MCP
    settings UI) and silently drop custom env blocks (e.g. NOTION_TOKEN).  This check
    runs on every pre_user_prompt event, compares env blocks, and re-syncs from the
    repo SSOT when any server has env in repo but is missing or different in global.
    Fail-open: any I/O or parse error is silently ignored.
    """
    repo_cfg = repo_root / ".windsurf" / "mcp_config.json"
    global_cfg = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
    try:
        repo_data = json.loads(repo_cfg.read_text(encoding="utf-8"))
        global_data = json.loads(global_cfg.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-silent-swallow -- MCP config read: non-fatal, check skipped
        return

    repo_servers = repo_data.get("mcpServers", {})
    global_servers = global_data.get("mcpServers", {})

    drifted: list[str] = []
    for name, cfg in repo_servers.items():
        if not isinstance(cfg, dict):
            continue
        repo_env = cfg.get("env")
        if repo_env is None:
            continue
        global_entry = global_servers.get(name, {})
        global_env = global_entry.get("env") if isinstance(global_entry, dict) else None
        if global_env != repo_env:
            drifted.append(name)

    if not drifted:
        return

    try:
        global_backup = global_cfg.parent / "mcp_config.backup.json"
        if global_cfg.exists():
            shutil.copy2(global_cfg, global_backup)
        global_cfg.write_text(json.dumps(repo_data, indent=2) + "\n", encoding="utf-8")
        print(
            "[pre_prompt_classifier] MCP_CONFIG_DRIFT_FIXED: env drift detected in: "
            f"{', '.join(drifted)} — global config re-synced from repo SSOT. "
            "Restart Windsurf MCP servers to pick up the new env blocks.",
            file=sys.stderr,
        )
    except (OSError, ValueError) as exc:
        print(
            "[pre_prompt_classifier] MCP_CONFIG_DRIFT_DETECTED: env drift in: "
            f"{', '.join(drifted)} — auto-fix failed ({exc}); run: "
            "python .windsurf/scripts/sync_mcp_config.py",
            file=sys.stderr,
        )


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
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

    _check_mcp_config_drift()

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

    # otel_mcp routing trace: emitted for every prompt so otel_mcp candidate visibility is observable.
    if _detect_otel_intent(prompt):
        print(
            "[pre_prompt_classifier] OTEL_MCP_TRACE: otel_intent=DETECTED "
            "\u2014 candidate: mcp7_otel_status / mcp7_otel_trace / mcp7_otel_spans_by_agent "
            "/ mcp7_otel_anomalies / mcp7_otel_healing_chain / mcp7_otel_policy_decisions.",
            file=sys.stderr,
        )
    else:
        print("[pre_prompt_classifier] OTEL_MCP_TRACE: otel_intent=NOT_DETECTED", file=sys.stderr)

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

    # adg_sqlite graph routing trace: emitted for every prompt for observability.
    if _detect_adg_graph_intent(prompt):
        print(
            "[pre_prompt_classifier] ADG_GRAPH_TRACE: adg_graph_intent=DETECTED "
            "\u2014 required: mcp1_adg_edge_fanin / mcp1_adg_edge_fanout / "
            "mcp1_adg_nodes_by_file / mcp1_adg_nodes_by_layer. "
            "Health-first: call mcp1_adg_health before any grep fallback.",
            file=sys.stderr,
        )
    else:
        print("[pre_prompt_classifier] ADG_GRAPH_TRACE: adg_graph_intent=NOT_DETECTED", file=sys.stderr)

    # Read BEFORE the state write: T0/T1 reset would otherwise shadow a True
    # value and incorrectly re-emit the mandate on a turn where memory was
    # already recalled.
    emit_memory_mandate = _should_emit_memory_mandate()

    # Advisory: warn before state update so we read the prior turn's lifecycle state.
    if tier in ("T2", "T3"):
        _warn_open_task(tier)

    # Persist tier; preserve or reset lifecycle fields per approved design.
    _write_session_state(tier)

    # Human diagnostic (exit 0 stderr — not injected into Cascade context).
    # Gate enforces recall via exit 2 in pre_mcp_gate.py.
    if emit_memory_mandate:
        print(_memory_mandate, file=sys.stderr)

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
                if check_adg_health_red(repo_root):
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
            if check_adg_health_red(repo_root):
                print(
                    f"[pre_prompt_classifier] BLOCKED: {tier} prompt — Redis is down AND adg_sqlite MCP is red. "
                    "Start Redis or run mcp1_adg_health and /mcp-failure-rca before proceeding (constitutional §13).",
                    file=sys.stderr,
                )
                return 2

        # Infrastructure healthy — inject structured reasoning mandate into Cascade context.
        # show_output: true in hooks.json ensures Cascade sees this before responding.
        mandate = _sr_mandate.format(tier=tier)
        if any(kw in prompt.lower() for kw in notion_keywords):
            mandate = mandate + "\n" + _notion_sr_hint
        if _detect_otel_intent(prompt):
            mandate = mandate + "\n" + _otel_sr_hint
        if _detect_pytest_intent(prompt):
            mandate = mandate + "\n" + _pytest_sr_hint
        if _detect_adg_graph_intent(prompt):
            mandate = mandate + "\n" + _adg_graph_sr_hint
        print(mandate, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
