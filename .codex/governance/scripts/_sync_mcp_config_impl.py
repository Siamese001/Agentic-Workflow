#!/usr/bin/env python3
"""Validate and sync the repo MCP config to AGENTS.md.

Usage:
    python .codex/governance/scripts/sync_mcp_config.py
    python .codex/governance/scripts/sync_mcp_config.py --check
    python .codex/governance/scripts/sync_mcp_config.py --dry-run

This script is stdlib-only and is safe to call from hooks.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[3]
repo_config = repo_root / ".mcp.json"
agents_md = repo_root / "AGENTS.md"
notion_databases_yaml = repo_root / "config" / "notion_databases.yaml"
default_user_config = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"

# Canonical aliases for downstream hooks/tests.
REPO_ROOT = repo_root
REPO_CONFIG = repo_config
GLOBAL_CONFIG = repo_config
AGENTS_MD = agents_md
NOTION_DATABASES_YAML = notion_databases_yaml
DEFAULT_USER_CONFIG = default_user_config
global_config = GLOBAL_CONFIG

USER_CONFIG_BLOCK_START = "# AGENTIC-WORKFLOW-MCP:START"
USER_CONFIG_BLOCK_END = "# AGENTIC-WORKFLOW-MCP:END"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_REQUIRED = False
DEFAULT_STARTUP_TIMEOUT_SEC = 15
DEFAULT_TOOL_TIMEOUT_SEC = 120
_ENV_PLACEHOLDER_RE = re.compile(r"\$\{(?:env:)?([A-Za-z_][A-Za-z0-9_]*)\}")
_EXACT_PLACEHOLDER_RE = re.compile(r"\A\$\{(?:env:)?([A-Za-z_][A-Za-z0-9_]*)\}\Z")

# Each row: (server_id, use_for, example_tools, notes, skill)
# `skill` is the slug under .codex/skills/<slug>/ that documents the
# canonical routing/usage for this MCP. Empty string = no dedicated skill yet.
# Rows may include dormant/restorable MCPs so compatibility notes can keep
# metadata close by; AGENTS.md renders only server IDs present in root .mcp.json.
server_rows = [
    (
        "GitKraken",
        "Git operations, GitLens, pull requests, issues",
        "git_status, git_add_or_commit, git_log_or_diff, pull_request_create",
        "Use as the git/PR authority.",
        "gitkraken",
    ),
    (
        "adg_sqlite",
        "Dependency graph, blast radius, layer analysis, refactoring hotspots, graph-layer primitives (mv_*, v_p*, semantic edges)",
        "adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file, adg_nodes_by_layer, adg_violations, adg_p0_wave_plan",
        "Structural deps + T2/T3 plans; §22 graph layer (mv_*, P-views, semantic edges).",
        "adg-sqlite",
    ),
    (
        "deepwiki",
        "External GitHub repository docs and wiki Q&A",
        "read_wiki_structure, read_wiki_contents, ask_question",
        "Do not use for this repo's own code.",
        "deepwiki",
    ),
    (
        "filesystem",
        "Filesystem MCP operations and directory traversal",
        "read_text_file, read_multiple_files, directory_tree, write_file",
        "Prefer native reads for ordinary file reads when available.",
        "filesystem-mcp",
    ),
    (
        "memory",
        "Persistent cross-session knowledge graph",
        "mem_recall_session_start, create_entities, add_observations, search_nodes",
        "Read at session start; write back major decisions.",
        "memory-mcp",
    ),
    (
        "vector_db",
        "Semantic search and embeddings",
        "semantic_search, query_collection, vector_stats, list_collections",
        "Not for structural dependency analysis.",
        "vector-db",
    ),
    (
        "otel_mcp",
        "Telemetry, traces, anomalies, runtime ADG ingest",
        "otel_server_info, otel_trace, otel_anomalies, otel_ingest_to_runtime_adg",
        "Check otel_server_info before restart logic.",
        "otel-telemetry",
    ),
    (
        "task_manager",
        "Task decomposition and task state tracking",
        "create_task, decompose_task, update_task, task_info",
        "Use when the user explicitly wants tracked multi-step work.",
        "task-manager-mcp",
    ),
    (
        "redis",
        "Redis cache health, keys, TTL, namespace stats",
        "redis_health, redis_keys, redis_hgetall, redis_namespace_stats",
        "Use for hot-cache inspection and invalidation.",
        "redis-cache",
    ),
    (
        "pytest_mcp",
        "Test discovery, runs, and coverage",
        "discover_tests, run_tests, get_test_details, analyze_test_coverage",
        "Prefer over plain pytest CLI when possible.",
        "pytest-mcp",
    ),
    (
        "playwright",
        "Browser automation, accessibility snapshots, end-to-end UI verification",
        "browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_evaluate, browser_take_screenshot",
        "Live UI/E2E; output in artifacts/mcp/playwright/ (gitignored). Close tabs after use.",
        "playwright",
    ),
    (
        "notion",
        "Notion pages and project-management databases",
        "API-query-data-source, API-retrieve-a-page, API-patch-page",
        "Manual page/DB read+write only; no plan-status enforcement (Notion plan/wave/status governance removed).",
        "mcp-integration",
    ),
    (
        "tavily",
        "AI-optimized web search, extraction, crawling, and site mapping",
        "tavily-search, tavily-extract, tavily-crawl, tavily-map",
        "Web search authority; requires TAVILY_API_KEY.",
        "tavily-research",
    ),
    (
        "context7",
        "Up-to-date, versioned official documentation for external libraries",
        "resolve-library-id, get-library-docs",
        "External package docs; not this repo. CONTEXT7_API_KEY optional.",
        "context7",
    ),
]


def load_repo_config(path: Path = repo_config) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level JSON object")
    return data


def validate_config(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        issues.append("Missing or invalid top-level 'mcpServers' object.")
        return issues
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            issues.append(f"Server '{name}' must map to an object.")
            continue
        if not any(key in cfg for key in ("command", "url", "serverUrl")):
            issues.append(f"Server '{name}' must define command, url, or serverUrl.")
        env = cfg.get("env")
        if env is not None and not isinstance(env, dict):
            issues.append(f"Server '{name}' env must be an object when present.")
        required = cfg.get("required")
        if required is not None and not isinstance(required, bool):
            issues.append(f"Server '{name}' required must be a boolean when present.")
        for key in ("startup_timeout_sec", "tool_timeout_sec"):
            value = cfg.get(key)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value <= 0
            ):
                issues.append(f"Server '{name}' {key} must be a positive integer when present.")
    return issues


def _live_server_rows(data: dict[str, Any] | None = None) -> list[tuple[str, str, str, str, str]]:
    """Return metadata rows for MCP servers that are live in root .mcp.json."""
    if data is None:
        data = load_repo_config()
    servers = data.get("mcpServers", {}) or {}
    if not isinstance(servers, dict):
        return []
    live_ids = {
        server_id
        for server_id, cfg in servers.items()
        if isinstance(cfg, dict) and not cfg.get("disabled")
    }
    return [row for row in server_rows if row[0] in live_ids]


def _repo_root_for_toml(root: Path = repo_root) -> str:
    return str(root.resolve()).replace("\\", "/")


def _default_env_value(name: str, root: Path = repo_root) -> str:
    if name in {"AGENTIC_REPO_ROOT", "ADG_REPO_ROOT", "PYTHONPATH"}:
        return _repo_root_for_toml(root)
    if name == "ADG_REDIS_URL":
        return os.environ.get(name, DEFAULT_REDIS_URL)
    if name == "MEMORY_DB":
        return os.environ.get(name, "artifacts/memory/knowledge_graph.sqlite")
    if name == "GITKRAKEN_GK_PATH":
        return os.environ.get(name, "gk")
    return os.environ.get(name, "")


def _expand_mcp_placeholders(value: str, root: Path = repo_root) -> str:
    def _replace(match: re.Match[str]) -> str:
        return _default_env_value(match.group(1), root)

    return _ENV_PLACEHOLDER_RE.sub(_replace, value).replace("\\", "/")


def _toml_string(value: str) -> str:
    return json.dumps(value)


def _toml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_scalar(item) for item in value) + "]"
    return _toml_string(str(value))


def _server_required(_server_id: str, cfg: dict[str, Any]) -> bool:
    value = cfg.get("required", DEFAULT_REQUIRED)
    return value if isinstance(value, bool) else DEFAULT_REQUIRED


def _server_positive_int(_server_id: str, cfg: dict[str, Any], key: str, default: int) -> int:
    value = cfg.get(key, default)
    if isinstance(value, bool):
        return default
    if isinstance(value, int) and value > 0:
        return value
    return default


def _server_startup_timeout(server_id: str, cfg: dict[str, Any]) -> int:
    return _server_positive_int(server_id, cfg, "startup_timeout_sec", DEFAULT_STARTUP_TIMEOUT_SEC)


def _server_tool_timeout(server_id: str, cfg: dict[str, Any]) -> int:
    return _server_positive_int(server_id, cfg, "tool_timeout_sec", DEFAULT_TOOL_TIMEOUT_SEC)


def _codex_command_projection(command: str, args: list[Any], root: Path) -> tuple[str, list[str]]:
    expanded_command = _expand_mcp_placeholders(command, root)
    expanded_args = [_expand_mcp_placeholders(str(arg), root) for arg in args]
    if expanded_command.lower() == "cmd":
        return expanded_command, expanded_args
    return "cmd", ["/c", expanded_command, *expanded_args]


def _env_projection(env: dict[str, Any], root: Path) -> tuple[dict[str, str], list[str]]:
    static_env: dict[str, str] = {}
    passthrough_vars: list[str] = []
    for key, raw_value in sorted(env.items()):
        value = str(raw_value)
        match = _EXACT_PLACEHOLDER_RE.match(value)
        if match and match.group(1) == key and key not in {"ADG_REDIS_URL", "MEMORY_DB"}:
            passthrough_vars.append(key)
            continue
        static_env[key] = _expand_mcp_placeholders(value, root)
    return static_env, passthrough_vars


def render_codex_user_mcp_block(data: dict[str, Any], root: Path = repo_root) -> str:
    """Render the repo MCP registry as the Codex Desktop runtime projection.

    Startup and tool-call policy is projected from each enabled `.mcp.json`
    server entry so optional/task-specific MCPs do not become global blockers.
    """
    servers = data.get("mcpServers", {}) or {}
    lines: list[str] = [
        USER_CONFIG_BLOCK_START,
        "# Generated from repo .mcp.json by .codex/governance/scripts/sync_mcp_config.py.",
        "# Keep repo-specific governance in the repository; this is the Codex Desktop runtime projection.",
        "# Run: python .codex/governance/scripts/sync_mcp_config.py --sync-user-config",
        "",
    ]
    cwd = _repo_root_for_toml(root)

    for server_id, cfg_value in servers.items():
        if not isinstance(cfg_value, dict) or cfg_value.get("disabled"):
            continue
        cfg = cfg_value
        lines.append(f"[mcp_servers.{server_id}]")
        if url := cfg.get("url") or cfg.get("serverUrl"):
            lines.append(f"url = {_toml_string(_expand_mcp_placeholders(str(url), root))}")
        if command := cfg.get("command"):
            projected_command, projected_args = _codex_command_projection(
                str(command),
                list(cfg.get("args", []) or []),
                root,
            )
            lines.append(f"command = {_toml_string(projected_command)}")
            lines.append(f"args = {_toml_scalar(projected_args)}")
            lines.append(f"cwd = {_toml_string(cwd)}")
        lines.append(f"required = {_toml_scalar(_server_required(server_id, cfg))}")
        lines.append(f"startup_timeout_sec = {_server_startup_timeout(server_id, cfg)}")
        lines.append(f"tool_timeout_sec = {_server_tool_timeout(server_id, cfg)}")

        env = cfg.get("env")
        static_env: dict[str, str] = {}
        passthrough_vars: list[str] = []
        if isinstance(env, dict):
            static_env, passthrough_vars = _env_projection(env, root)
        if passthrough_vars:
            lines.append(f"env_vars = {_toml_scalar(passthrough_vars)}")
        if static_env:
            lines.append("")
            lines.append(f"[mcp_servers.{server_id}.env]")
            for key, value in static_env.items():
                lines.append(f"{key} = {_toml_string(value)}")
        lines.append("")

    lines.append(USER_CONFIG_BLOCK_END)
    return "\n".join(lines)


def replace_user_config_block(text: str, block: str) -> str:
    start_idx = text.find(USER_CONFIG_BLOCK_START)
    end_idx = text.find(USER_CONFIG_BLOCK_END)
    block = block.rstrip() + "\n"
    if start_idx == -1 and end_idx == -1:
        if text and not text.endswith("\n"):
            text += "\n"
        return text + "\n" + block
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError("malformed AGENTIC-WORKFLOW-MCP block in Codex user config")
    return text[:start_idx] + block + text[end_idx + len(USER_CONFIG_BLOCK_END) :].lstrip("\n")


def sync_user_config(
    data: dict[str, Any],
    user_config: Path = default_user_config,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    block = render_codex_user_mcp_block(data)
    existing = user_config.read_text(encoding="utf-8") if user_config.exists() else ""
    updated = replace_user_config_block(existing, block)
    changed = updated != existing
    if changed and not dry_run:
        user_config.parent.mkdir(parents=True, exist_ok=True)
        user_config.write_text(updated, encoding="utf-8")
    return {
        "status": "PASS",
        "user_config": str(user_config),
        "changed": changed,
        "dry_run": dry_run,
        "server_count": len(data.get("mcpServers", {}) or {}),
    }


def check_user_config_projection(
    data: dict[str, Any],
    user_config: Path = default_user_config,
) -> dict[str, Any]:
    block = render_codex_user_mcp_block(data).rstrip()
    if not user_config.exists():
        return {
            "status": "FAIL",
            "user_config": str(user_config),
            "reason": "missing_user_config",
        }
    text = user_config.read_text(encoding="utf-8")
    start_idx = text.find(USER_CONFIG_BLOCK_START)
    end_idx = text.find(USER_CONFIG_BLOCK_END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        return {
            "status": "FAIL",
            "user_config": str(user_config),
            "reason": "missing_or_malformed_agentic_workflow_block",
        }
    current = text[start_idx : end_idx + len(USER_CONFIG_BLOCK_END)].strip()
    return {
        "status": "PASS" if current == block else "FAIL",
        "user_config": str(user_config),
        "reason": "ok" if current == block else "projection_drift",
        "server_count": len(data.get("mcpServers", {}) or {}),
    }


def generate_mcp_quick_reference_block() -> str:
    """Inner payload for the MCP-QUICK-REFERENCE autogen block (markers excluded)."""
    lines: list[str] = []
    lines.append("")
    lines.append("| Server ID | Use For | Example Tools | Notes | Skill |")
    lines.append("|---|---|---|---|---|")
    for sid, use_for, tools, notes, skill in _live_server_rows():
        skill_cell = f"[`{skill}`](.codex/skills/{skill}/SKILL.md)" if skill else "—"
        lines.append(f"| `{sid}` | {use_for} | `{tools}` | {notes} | {skill_cell} |")
    lines.append("")
    return "\n".join(lines)


def generate_agents_quick_reference() -> str:
    """Full MCP Quick Reference section (heading + intro + autogen block)."""
    lines: list[str] = []
    lines.append("## MCP Quick Reference")
    lines.append("")
    lines.append(
        "> Stable IDs are the `mcpServers` keys in root `.mcp.json` (repo MCP SSOT). "
        "Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. "
        "Resolve the live prefix from the current tool list in-session."
    )
    lines.append("")
    lines.append("<!-- MCP-QUICK-REFERENCE:START -->")
    lines.append(generate_mcp_quick_reference_block())
    lines.append("<!-- MCP-QUICK-REFERENCE:END -->")
    lines.append("")
    lines.append(
        "Per-server `SKILL.md` files under `.codex/skills/<name>/` are **redirect stubs**; "
        "procedural SSOT is [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) sections §1–§13."
    )
    lines.append("")
    return "\n".join(lines)


def extract_agents_quick_reference(text: str) -> str:
    """Extract the canonical MCP Quick Reference section from AGENTS.md text."""
    start = "## MCP Quick Reference"
    next_heading = "\n## "
    start_idx = text.find(start)
    if start_idx == -1:
        return ""
    end_idx = text.find(next_heading, start_idx + len(start))
    if end_idx == -1:
        return text[start_idx:].strip()
    return text[start_idx:end_idx].strip()


def load_notion_databases() -> dict[str, Any]:
    """Parse config/notion_databases.yaml with a minimal stdlib parser.

    The file is hand-curated and follows a strict schema: top-level `workspace`
    mapping + `databases` list of mappings. Using PyYAML is acceptable but this
    module is stdlib-only (called from hooks), so we parse the narrow format.
    """
    if not notion_databases_yaml.exists():
        raise FileNotFoundError(f"Missing SSOT: {notion_databases_yaml}")
    text = notion_databases_yaml.read_text(encoding="utf-8")

    # Narrow parser: strip comments, parse workspace block + databases list.
    workspace: dict[str, str] = {}
    databases: list[dict[str, str]] = []
    section: str | None = None
    # Use a 1-element list so Pylint's flow analysis retains dict type through
    # the else-branch. Functionally equivalent to Optional[dict].
    current_holder: list[dict[str, str]] = []

    def _current() -> dict[str, str]:
        return current_holder[0]

    def _has_current() -> bool:
        return bool(current_holder)

    def _flush_current() -> None:
        if current_holder:
            databases.append(current_holder.pop())

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("workspace:"):
            section = "workspace"
            continue
        if line.startswith("databases:"):
            section = "databases"
            continue
        if section == "workspace" and line.startswith("  ") and ":" in line:
            k, _, v = stripped.partition(":")
            workspace[k.strip()] = _unquote_yaml(v.strip())
        elif section == "databases":
            if stripped.startswith("- "):
                _flush_current()
                current_holder.append({})
                inline = stripped[2:]
                if ":" in inline:
                    k, _, v = inline.partition(":")
                    _current()[k.strip()] = _unquote_yaml(v.strip())
            elif _has_current() and ":" in stripped:
                k, _, v = stripped.partition(":")
                _current()[k.strip()] = _unquote_yaml(v.strip())
    _flush_current()

    return {"workspace": workspace, "databases": databases}


def _unquote_yaml(value: str) -> str:
    """Unquote a YAML scalar using the subset the Notion config uses."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        inner = value[1:-1]
        # YAML doubled-quote escape for single-quoted strings
        if value[0] == "'":
            inner = inner.replace("''", "'")
        else:
            inner = inner.replace('\\"', '"')
        return inner
    return value


def generate_notion_map_block() -> str:
    """Inner payload for the NOTION-MAP autogen block (markers excluded).

    Covers: workspace attribution + database table + auto-routing rules + sync
    enforcement pointers. Sourced from `config/notion_databases.yaml`.
    """
    data = load_notion_databases()
    ws = data["workspace"]
    dbs = data["databases"]

    lines: list[str] = []
    lines.append("")
    lines.append(f"Bot: **{ws.get('bot', '?')}** | Workspace: **{ws.get('space', '?')}**")
    lines.append("")
    lines.append(
        "| Database | Data Source ID (reads) | Database ID (writes) | Read Trigger | Write Trigger (auto-route) |"
    )
    lines.append(
        "|----------|-----------------------|----------------------|--------------|----------------------------|"
    )
    for db in dbs:
        if db.get("archived"):
            id_col = f"~~`{db['id']}`~~"
            db_id_col = f"~~`{db.get('database_id', '— MISSING —')}`~~"
        else:
            id_col = f"`{db['id']}`"
            db_id_col = f"`{db.get('database_id', '— MISSING —')}`"
        lines.append(
            f"| {db['name']} | {id_col} | {db_id_col} | "
            f"{db.get('read_trigger', '')} | {db.get('write_trigger', '')} |"
        )
    lines.append("")
    lines.append(
        "**Query pattern (reads)**: `API-query-data-source` with `data_source_id` from column 2. Add `filter`/`sorts` as needed."
    )
    lines.append(
        '**Write pattern (creates)**: `API-post-page` with `parent: {type: "database_id", database_id: <column 3>}`. '
        "Using data_source_id for writes returns 404."
    )
    lines.append("")
    return "\n".join(lines)


def _replace_block(text: str, marker: str, new_inner: str) -> str:
    """Replace content between `<!-- marker:START -->` and `<!-- marker:END -->`.

    Appends the block at EOF if the markers are absent. Raises ValueError if
    only one marker is present (invalid state; force user to repair manually).
    """
    start_tag = f"<!-- {marker}:START -->"
    end_tag = f"<!-- {marker}:END -->"
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    # Normalise inner to have exactly one blank line separating the START/END
    # markers from surrounding table content (matches the full-section render
    # produced by generate_agents_quick_reference for byte-identical integrity).
    stripped_inner = new_inner.strip("\n")
    block = f"{start_tag}\n\n{stripped_inner}\n\n{end_tag}"
    if start_idx == -1 and end_idx == -1:
        if not text.endswith("\n"):
            text += "\n"
        return text + "\n" + block + "\n"
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError(
            f"Invalid autogen block state for marker '{marker}': malformed or out-of-order markers"
        )
    # Replace [start_tag ... end_tag] inclusive
    return text[:start_idx] + block + text[end_idx + len(end_tag) :]


def sync_agents_md(agents_path: Path = agents_md) -> bool:
    """Refresh all autogen blocks in AGENTS.md.

    Blocks refreshed:
      - MCP-QUICK-REFERENCE (live .mcp.json servers via server_rows metadata)
      - NOTION-MAP         (from config/notion_databases.yaml)

    The surrounding `## MCP Quick Reference` heading + intro paragraph are NOT
    regenerated; they are hand-authored narrative. Only the content between
    markers is replaced.

    Returns True when the file was updated (or no-op write because unchanged),
    False when AGENTS.md does not exist.
    """
    if not agents_path.exists():
        return False
    original = agents_path.read_text(encoding="utf-8")
    text = original
    text = _replace_block(text, "MCP-QUICK-REFERENCE", generate_mcp_quick_reference_block())
    try:
        text = _replace_block(text, "NOTION-MAP", generate_notion_map_block())
    except FileNotFoundError:  # guardian: allow-silent-swallow -- notion_databases.yaml missing: non-fatal, AGENTS.md block unchanged
        # notion_databases.yaml missing — skip block, leave AGENTS.md as-is
        pass
    if text != original:
        agents_path.write_text(text, encoding="utf-8")
    return True


def _same_file(a: Path, b: Path) -> bool:
    """True when both paths resolve to the same filesystem object (symlink-aware)."""
    if not a.exists() or not b.exists():
        return False
    try:
        return a.samefile(b)
    except OSError:
        return False


def sync_global_config(data: dict[str, Any], global_path: Path = repo_config) -> bool:
    """Compatibility no-op for the repo SSOT.

    The repo no longer maintains a separate in-tree editor mirror. The only
    authoritative config is `.mcp.json`, so this returns False when the caller
    points at the SSOT itself and otherwise writes only if a separate path is
    explicitly supplied.
    """
    if _same_file(repo_config, global_path):
        return False
    global_path.parent.mkdir(parents=True, exist_ok=True)
    global_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def run(
    check_only: bool = False,
    dry_run: bool = False,
    *,
    sync_user_config_requested: bool = False,
    check_user_config_requested: bool = False,
    user_config: Path = default_user_config,
    json_output: bool = False,
) -> int:
    data = load_repo_config()
    issues = validate_config(data)
    if issues:
        if json_output:
            print(json.dumps({"status": "FAIL", "issues": issues}, indent=2, sort_keys=True))
            return 1
        for issue in issues:
            print(f"[mcp_sync] ERROR: {issue}")
        return 1
    if check_user_config_requested:
        report = check_user_config_projection(data, user_config)
        if json_output:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"[mcp_sync] user config projection: {report['status']} ({report.get('reason', 'ok')})")
        return 0 if report["status"] == "PASS" else 1
    if sync_user_config_requested:
        try:
            report = sync_user_config(data, user_config, dry_run=dry_run)
        except (OSError, ValueError) as exc:
            report = {
                "status": "FAIL",
                "user_config": str(user_config),
                "error": str(exc),
            }
        if json_output:
            print(json.dumps(report, indent=2, sort_keys=True))
        elif report["status"] == "PASS":
            action = "would update" if report["dry_run"] and report["changed"] else (
                "updated" if report["changed"] else "already current"
            )
            print(f"[mcp_sync] Codex user config projection {action}: {user_config}")
        else:
            print(f"[mcp_sync] ERROR: user config projection failed: {report.get('error')}")
        return 0 if report["status"] == "PASS" else 1
    if check_only:
        if json_output:
            print(
                json.dumps(
                    {
                        "status": "PASS",
                        "server_count": len(data["mcpServers"]),
                        "repo_config": str(repo_config),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        print(f"[mcp_sync] OK: {len(data['mcpServers'])} MCP servers validated.")
        return 0
    if dry_run:
        print(f"[mcp_sync] DRY RUN: repo SSOT already contains {len(data['mcpServers'])} servers")
        if agents_md.exists():
            print(f"[mcp_sync] DRY RUN: would refresh {agents_md}")
        return 0
    copied = sync_global_config(data)
    if copied:
        print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to {repo_config}")
    else:
        print(f"[mcp_sync] No-op: repo SSOT already points at {repo_config}.")
    if sync_agents_md():
        print(f"[mcp_sync] Refreshed AGENTS.md MCP Quick Reference at {agents_md}")
    else:
        print("[mcp_sync] AGENTS.md not found; skipped AGENTS sync.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sync-user-config", action="store_true")
    parser.add_argument("--check-user-config", action="store_true")
    parser.add_argument("--user-config", type=Path, default=default_user_config)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    return run(
        check_only=args.check,
        dry_run=args.dry_run,
        sync_user_config_requested=args.sync_user_config,
        check_user_config_requested=args.check_user_config,
        user_config=args.user_config,
        json_output=args.json,
    )


if __name__ == "__main__":
    raise SystemExit(main())
