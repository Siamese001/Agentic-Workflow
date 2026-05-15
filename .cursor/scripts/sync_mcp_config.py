#!/usr/bin/env python3
"""Validate and sync the repo MCP config to Cursor's global config and AGENTS.md.

Usage:
    python .cursor/scripts/sync_mcp_config.py
    python .cursor/scripts/sync_mcp_config.py --check
    python .cursor/scripts/sync_mcp_config.py --dry-run

This script is stdlib-only and is safe to call from hooks.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[2]
repo_config = repo_root / ".cursor" / "mcp.json"
global_config = Path.home() / ".cursor" / "cursor" / "mcp.json"
agents_md = repo_root / "AGENTS.md"
notion_databases_yaml = repo_root / "config" / "notion_databases.yaml"
global_backup = Path.home() / ".cursor" / "cursor" / "mcp_config.backup.json"

# Backward-compatible aliases for downstream hooks/tests.
REPO_ROOT = repo_root
REPO_CONFIG = repo_config
GLOBAL_CONFIG = global_config
AGENTS_MD = agents_md
NOTION_DATABASES_YAML = notion_databases_yaml
GLOBAL_BACKUP = global_backup

# Each row: (server_id, use_for, example_tools, notes, skill)
# `skill` is the slug under .cursor/skills/<slug>/ that documents the
# canonical routing/usage for this MCP. Empty string = no dedicated skill yet.
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
        "Primary authority for structural dependencies AND refactoring analysis. Constitutional §22: mv_* materialized views, v_p0_*/v_p1_*/v_p2_*/v_p3_* P-views, and semantic edges (flows_to, reads_from, writes_to, emits_side_effect, controls_flow, resolves_callsite) MUST drive T2/T3 refactoring plans.",
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
        "io.cursor/mcp-playwright",
        "Browser automation, accessibility snapshots, end-to-end UI verification",
        "browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_evaluate, browser_take_screenshot",
        "Official Microsoft @playwright/mcp thin npx wrapper. Use for live UI/E2E checks, not for static HTML fetching (use direct httpx in code or read_url_content for one-off fetches). Output lands in repo-root .playwright-mcp/ (gitignored). Always close tabs after use.",
        "playwright",
    ),
    (
        "notion",
        "Notion pages and project-management databases",
        "API-query-data-source, API-retrieve-a-page, API-patch-page",
        "Use for Plans DB, Backlog Items, and Anti-Pattern Burndown. MCP Registry, ADR Registry, Constitutional Rules Registry, SC/AP Violation Backlog, and Author-Gate Decision Ledger are **archived** — filesystem SSOT only.",
        "notion",
    ),
    (
        "tavily",
        "AI-optimized web search, extraction, crawling, and site mapping",
        "tavily-search, tavily-extract, tavily-crawl, tavily-map",
        "Sole authority for web search. Use for upstream-issue research (Anthropic MCP race, chromadb bugs), ADR background, and domain research not answerable by deepwiki (GitHub-only) or one-off URL fetch via read_url_content. Requires TAVILY_API_KEY OS env var.",
        "tavily-research",
    ),
    (
        "context7",
        "Up-to-date, versioned official documentation for external libraries",
        "resolve-library-id, get-library-docs",
        "Use for external-package docs (chromadb, FastMCP, sentence-transformers, playwright, pytorch). Distinct from deepwiki (GitHub repo wiki/Q&A) and adg_sqlite (this repo's own code). No API key required; CONTEXT7_API_KEY optional for higher limits.",
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
    return issues


def generate_mcp_quick_reference_block() -> str:
    """Inner payload for the MCP-QUICK-REFERENCE autogen block (markers excluded)."""
    lines: list[str] = []
    lines.append("")
    lines.append("| Server ID | Use For | Example Tools | Notes | Skill |")
    lines.append("|---|---|---|---|---|")
    for sid, use_for, tools, notes, skill in server_rows:
        skill_cell = f"[`{skill}`](.cursor/skills/{skill}/SKILL.md)" if skill else "—"
        lines.append(f"| `{sid}` | {use_for} | `{tools}` | {notes} | {skill_cell} |")
    lines.append("")
    return "\n".join(lines)


def generate_agents_quick_reference() -> str:
    """Full MCP Quick Reference section (heading + intro + autogen block).

    Retained for backward compatibility with check_mcp_sync_integrity.py.
    The autogen block within is identical to generate_mcp_quick_reference_block().
    """
    lines: list[str] = []
    lines.append("## MCP Quick Reference")
    lines.append("")
    lines.append(
        "> Stable IDs are the `mcpServers` keys in `.cursor/mcp.json`. Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session."
    )
    lines.append("")
    lines.append("<!-- MCP-QUICK-REFERENCE:START -->")
    lines.append(generate_mcp_quick_reference_block())
    lines.append("<!-- MCP-QUICK-REFERENCE:END -->")
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
      - MCP-QUICK-REFERENCE (from mcp.json via server_rows)
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


# Minimum plausible server count for the authoritative repo config. This is
# a defensive floor: if a caller passes fewer servers than this, we refuse
# to overwrite a healthy global config. Historical precedent: on 2026-04-22
# a buggy unit test silently wrote a 1-server stub (`{"test": ...}`) to the
# real user-home config every full-suite run, taking the entire MCP fleet
# offline. The production repo has 12+ servers; anything below this floor
# is almost certainly a test fixture escaping its mock boundary.
MIN_PLAUSIBLE_SERVER_COUNT = 5


def sync_global_config(data: dict[str, Any], global_path: Path = global_config) -> bool:
    """Copy the repo SSOT to the Cursor-read global path.

    Returns True if a copy was performed, False if the two paths already point
    to the same file (symlink in place — no-op is correct and zero-drift).

    Refuses to overwrite an existing multi-server global config with a
    payload containing fewer than ``MIN_PLAUSIBLE_SERVER_COUNT`` servers.
    This guards against the failure mode documented at 2026-04-22 where a
    unit test mocked module-level SSOT/GLOBAL but left `global_config`
    (defaulted here) pointing at the real filesystem, writing a 1-server
    stub and killing the entire MCP fleet.
    """
    global_path.parent.mkdir(parents=True, exist_ok=True)
    if _same_file(repo_config, global_path):
        return False

    incoming_servers = data.get("mcpServers", {})
    incoming_count = len(incoming_servers) if isinstance(incoming_servers, dict) else 0

    if global_path.exists():
        # Defense-in-depth: read the current global config and compare counts.
        # If the incoming payload has fewer servers than the plausibility floor
        # AND the current global config has more, refuse the overwrite.
        try:
            existing_raw = json.loads(global_path.read_text(encoding="utf-8"))
            existing_servers = existing_raw.get("mcpServers", {}) if isinstance(existing_raw, dict) else {}
            existing_count = len(existing_servers) if isinstance(existing_servers, dict) else 0
        except (OSError, json.JSONDecodeError, ValueError):
            existing_count = 0

        if incoming_count < MIN_PLAUSIBLE_SERVER_COUNT and existing_count >= MIN_PLAUSIBLE_SERVER_COUNT:
            print(
                f"[mcp_sync] REFUSED: incoming payload has {incoming_count} server(s) "
                f"(< floor {MIN_PLAUSIBLE_SERVER_COUNT}), existing global has {existing_count}. "
                f"Suspected test fixture escaping its mock boundary — refusing to overwrite "
                f"{global_path}. See sync_mcp_config.MIN_PLAUSIBLE_SERVER_COUNT.",
                flush=True,
            )
            return False

        shutil.copy2(global_path, global_backup)

    global_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def run(check_only: bool = False, dry_run: bool = False) -> int:
    data = load_repo_config()
    issues = validate_config(data)
    if issues:
        for issue in issues:
            print(f"[mcp_sync] ERROR: {issue}")
        return 1
    if check_only:
        print(f"[mcp_sync] OK: {len(data['mcpServers'])} MCP servers validated.")
        return 0
    if dry_run:
        print(f"[mcp_sync] DRY RUN: would sync {len(data['mcpServers'])} servers to {global_config}")
        if agents_md.exists():
            print(f"[mcp_sync] DRY RUN: would refresh {agents_md}")
        return 0
    copied = sync_global_config(data)
    if copied:
        print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to {global_config}")
    else:
        print(f"[mcp_sync] No-op: repo SSOT and {global_config} are the same file (symlink).")
    if sync_agents_md():
        print(f"[mcp_sync] Refreshed AGENTS.md MCP Quick Reference at {agents_md}")
    else:
        print("[mcp_sync] AGENTS.md not found; skipped AGENTS sync.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return run(check_only=args.check, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
