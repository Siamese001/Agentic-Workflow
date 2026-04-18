#!/usr/bin/env python3
"""Validate and sync the repo MCP config to Windsurf's global config and AGENTS.md.

Usage:
    python .windsurf/scripts/sync_mcp_config.py
    python .windsurf/scripts/sync_mcp_config.py --check
    python .windsurf/scripts/sync_mcp_config.py --dry-run

This script is stdlib-only and is safe to call from hooks.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[2]
repo_config = repo_root / ".windsurf" / "mcp_config.json"
global_config = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
agents_md = repo_root / "AGENTS.md"
global_backup = Path.home() / ".codeium" / "windsurf" / "mcp_config.backup.json"

server_rows = [
    (
        "GitKraken",
        "Git operations, GitLens, pull requests, issues",
        "git_status, git_add_or_commit, git_log_or_diff, pull_request_create",
        "Use as the git/PR authority.",
    ),
    (
        "adg_sqlite",
        "Dependency graph, blast radius, layer analysis",
        "adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file",
        "Primary authority for structural dependencies.",
    ),
    (
        "deepwiki",
        "External GitHub repository docs and wiki Q&A",
        "read_wiki_structure, read_wiki_contents, ask_question",
        "Do not use for this repo's own code.",
    ),
    (
        "enhanced_http",
        "Programmatic HTTP calls, webhooks, endpoint checks",
        "http_get, http_post, test_connectivity, batch_requests",
        "Use for autonomous/programmatic HTTP only.",
    ),
    (
        "filesystem",
        "Filesystem MCP operations and directory traversal",
        "read_text_file, read_multiple_files, directory_tree, write_file",
        "Prefer native reads for ordinary file reads when available.",
    ),
    (
        "memory",
        "Persistent cross-session knowledge graph",
        "mem_recall_session_start, create_entities, add_observations, search_nodes",
        "Read at session start; write back major decisions.",
    ),
    (
        "vector_db",
        "Semantic search and embeddings",
        "semantic_search, query_collection, vector_stats, list_collections",
        "Not for structural dependency analysis.",
    ),
    (
        "otel_mcp",
        "Telemetry, traces, anomalies, runtime ADG ingest",
        "otel_server_info, otel_trace, otel_anomalies, otel_ingest_to_runtime_adg",
        "Check otel_server_info before restart logic.",
    ),
    (
        "task_manager",
        "Task decomposition and task state tracking",
        "create_task, decompose_task, update_task, task_info",
        "Use when the user explicitly wants tracked multi-step work.",
    ),
    (
        "redis",
        "Redis cache health, keys, TTL, namespace stats",
        "redis_health, redis_keys, redis_hgetall, redis_namespace_stats",
        "Use for hot-cache inspection and invalidation.",
    ),
    (
        "pytest_mcp",
        "Test discovery, runs, and coverage",
        "discover_tests, run_tests, get_test_details, analyze_test_coverage",
        "Prefer over plain pytest CLI when possible.",
    ),
    (
        "notion",
        "Notion pages and project-management databases",
        "API-query-data-source, API-retrieve-a-page, API-patch-page",
        "Use for ADRs, HITL ledgers, MCP registry, and plan/status data.",
    ),
]


def load_repo_config(path: Path = repo_config) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


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


def generate_agents_quick_reference() -> str:
    lines: list[str] = []
    lines.append("## MCP Quick Reference")
    lines.append("")
    lines.append(
        "> Stable IDs are the `mcpServers` keys in `.windsurf/mcp_config.json`. Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session."
    )
    lines.append("")
    lines.append("<!-- MCP-QUICK-REFERENCE:START -->")
    lines.append("")
    lines.append("| Server ID | Use For | Example Tools | Notes |")
    lines.append("|---|---|---|---|")
    for sid, use_for, tools, notes in server_rows:
        lines.append(f"| `{sid}` | {use_for} | `{tools}` | {notes} |")
    lines.append("")
    lines.append("<!-- MCP-QUICK-REFERENCE:END -->")
    lines.append("")
    return "\n".join(lines)


def sync_agents_md(agents_path: Path = agents_md) -> bool:
    if not agents_path.exists():
        return False
    text = agents_path.read_text(encoding="utf-8")
    section = generate_agents_quick_reference().rstrip() + "\n"
    start = "## MCP Quick Reference"
    next_heading = "\n## "
    start_idx = text.find(start)
    if start_idx == -1:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + section
    else:
        end_idx = text.find(next_heading, start_idx + len(start))
        if end_idx == -1:
            text = text[:start_idx] + section
        else:
            text = text[:start_idx] + section + text[end_idx + 1 :]
    agents_path.write_text(text, encoding="utf-8")
    return True


def sync_global_config(data: dict[str, Any], global_path: Path = global_config) -> None:
    global_path.parent.mkdir(parents=True, exist_ok=True)
    if global_path.exists():
        shutil.copy2(global_path, global_backup)
    global_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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
    sync_global_config(data)
    print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to {global_config}")
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
