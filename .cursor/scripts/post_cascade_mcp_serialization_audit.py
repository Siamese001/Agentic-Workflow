#!/usr/bin/env python3
"""post_cascade_mcp_serialization_audit.py — MCP serialization enforcement.

Reads the Cascade response from stdin (post_cascade_response payload). Detects
responses that batch an MCP tool call (`mcp*_` prefix) with any other tool call
in the same turn — the pattern that trips the Anthropic MCP client transport
race (see `anthropics/claude-agent-sdk-typescript#41`). Logs violations to
``artifacts/windsurf/mcp_serialization_violations.jsonl``.

Policy: **advisory only** — always exits 0, never blocks. Fail-open on any
internal error so a broken hook never wedges a turn. Auto-retires when
``.windsurf/config/mcp_serialization_ttl.json`` declares ``retired_after`` in
the past (sunset clause from the rule).

Companion rule: ``.windsurf/rules/mcp-serialization.md`` (always-on).
Constitutional rule: §25.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]
violations_log = repo_root / "artifacts" / "windsurf" / "mcp_serialization_violations.jsonl"
ttl_config = repo_root / ".windsurf" / "config" / "mcp_serialization_ttl.json"

# ---------------------------------------------------------------------------
# Tool-name classification
# ---------------------------------------------------------------------------

# Pattern for MCP tool invocations: "mcp<digits>_<name>".
# Matches at function-call syntax positions (name followed by `(` or XML
# `<invoke name="...">`) to reduce false positives from prose mentions.
_MCP_NAME_RE = re.compile(r"\bmcp\d+_[A-Za-z0-9_\-]+\b")

# Pattern for stripping the `mcpN_` server-index prefix from a tool name.
# Server indexes shift when `.windsurf/mcp_config.json` is reordered; the
# tool-name suffix is stable per server identity. We classify remote vs local
# off the suffix.
_MCP_PREFIX_STRIP_RE = re.compile(r"^mcp\d+_")

# Tool-name suffix patterns identifying REMOTE / network-bound MCP servers.
# Calls to these MUST be serialized (no siblings in the same function_calls
# block); calls to any other MCP server are LOCAL and may batch freely.
# Empirically derived from the Anthropic upstream race issues, which manifest
# in concurrent dispatch through HTTP/proxy transport (notion, tavily, etc.),
# not in local stdio subprocesses.
_REMOTE_MCP_SUFFIX_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^API-"),                                                # notion
    re.compile(r"^tavily[_-]"),                                          # tavily
    re.compile(r"^(ask_question|read_wiki_)"),                           # deepwiki
    re.compile(r"^(query-docs|resolve-library-id)$"),                    # context7
    re.compile(r"^(git_|gitkraken_|gitlens_|issues_|pull_request_|repository_)"),  # GitKraken
)

# Native Cascade tools that can be batched freely with each other but NOT
# with an mcp*_ call. This set is the authoritative allow-list; anything
# not here and not mcp*_ is treated as unknown (ignored).
_NATIVE_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "ask_user_question",
        "browser_preview",
        "check_deploy_status",
        "command_status",
        "create_memory",
        "deploy_web_app",
        "edit",
        "edit_notebook",
        "find_by_name",
        "grep_search",
        "list_dir",
        "list_resources",
        "multi_edit",
        "read_deployment_config",
        "read_file",
        "read_media_file",
        "read_multiple_files",  # note: NOT mcp4_*
        "read_notebook",
        "read_resource",
        "read_terminal",
        "read_text_file",
        "read_url_content",
        "run_command",
        "search_files",
        "search_web",
        "skill",
        "todo_list",
        "trajectory_search",
        "view_content_chunk",
        "write_to_file",
    }
)

# Match <invoke name="TOOL"> from the function_calls XML that Cascade emits.
# This is the most reliable signal for detecting an actually-dispatched tool
# call (prose mentions in Cascade's own analysis don't emit invoke tags).
_INVOKE_TAG_RE = re.compile(r'<invoke\s+name="([^"]+)"', re.IGNORECASE)

# Match <function_calls> ... </function_calls> blocks so we can scope the
# detection to "calls dispatched together in a single batch".
_FUNCTION_CALLS_BLOCK_RE = re.compile(
    r"<function_calls>(.*?)</function_calls>",
    re.DOTALL | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Sunset / bypass
# ---------------------------------------------------------------------------


def _is_retired() -> bool:
    """Honor the sunset TTL file if present and past the retirement date."""
    if not ttl_config.exists():
        return False
    try:
        payload = json.loads(ttl_config.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    retired_after = payload.get("retired_after")
    if not isinstance(retired_after, str):
        return False
    try:
        cutoff = datetime.fromisoformat(retired_after.replace("Z", "+00:00"))
    except ValueError:
        return False
    if cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= cutoff


def _is_bypass() -> bool:
    return os.environ.get("MCP_SERIAL_BYPASS", "").strip() == "1"


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _classify(tool_name: str) -> str:
    """Return one of ``{"mcp_remote", "mcp_local", "native", "unknown"}``.

    Remote MCPs go through the HTTP/proxy transport layer that exhibits the
    Anthropic SDK concurrent-dispatch race; their calls must be serialized.
    Local stdio MCPs run as same-machine subprocesses and may batch freely.
    """

    if _MCP_NAME_RE.fullmatch(tool_name):
        suffix = _MCP_PREFIX_STRIP_RE.sub("", tool_name)
        for pattern in _REMOTE_MCP_SUFFIX_PATTERNS:
            if pattern.search(suffix):
                return "mcp_remote"
        return "mcp_local"
    if tool_name in _NATIVE_TOOL_NAMES:
        return "native"
    return "unknown"


def detect_violations(response_text: str) -> list[dict[str, Any]]:
    """Scan *response_text* and return any serialization violations.

    A violation is any ``<function_calls>`` block that contains:
    - ≥1 remote MCP call AND ≥1 sibling tool call (local MCP, native, or
      another remote MCP) — the remote MCP races against the sibling
      dispatch through the HTTP/proxy transport.
    - ≥2 remote MCP calls in the same batch (any combination).

    All-local-MCP, all-native, and mixed local-MCP+native batches are
    compliant (not flagged) under the 2026-05-01 hardened scope.
    """

    violations: list[dict[str, Any]] = []

    if not response_text:
        return violations

    for block_idx, block_match in enumerate(_FUNCTION_CALLS_BLOCK_RE.finditer(response_text)):
        block_body = block_match.group(1)
        tool_names = _INVOKE_TAG_RE.findall(block_body)
        if len(tool_names) < 2:
            continue  # single-call batches are always compliant

        classifications = [(name, _classify(name)) for name in tool_names]
        remote_mcp_calls = [n for n, c in classifications if c == "mcp_remote"]
        local_mcp_calls = [n for n, c in classifications if c == "mcp_local"]
        # Treat "unknown" as native for violation purposes — anything that
        # isn't classifiable as MCP counts as a sibling of any remote MCP.
        native_calls = [n for n, c in classifications if c in ("native", "unknown")]

        if not remote_mcp_calls:
            continue  # batches without any remote MCP are compliant under hardened scope

        # We have at least one remote MCP and at least 2 total calls -> violation
        if len(remote_mcp_calls) >= 2:
            violation_type = "multi_remote_mcp_in_single_batch"
        elif local_mcp_calls and not native_calls:
            violation_type = "remote_mcp_mixed_with_local_mcp"
        elif native_calls and not local_mcp_calls:
            violation_type = "remote_mcp_mixed_with_native"
        else:
            violation_type = "remote_mcp_mixed_with_local_mcp_and_native"

        violations.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "violation_type": violation_type,
                "severity": "error",
                "block_index": block_idx,
                "tool_names": tool_names,
                "remote_mcp_calls": remote_mcp_calls,
                "local_mcp_calls": local_mcp_calls,
                "native_calls": native_calls,
                "remote_mcp_count": len(remote_mcp_calls),
                "remediation": (
                    "Split each remote MCP tool call into its own response (no sibling tools)."
                    " Local MCPs (adg_sqlite, redis, memory, filesystem, vector_db, pytest_mcp,"
                    " otel_mcp, task_manager, playwright) may batch freely with each other and"
                    " with native tools."
                ),
                "rule": "constitutional.md §25, mcp-serialization.md (hardened 2026-05-01)",
                "upstream": "anthropics/claude-agent-sdk-typescript#41",
                "scope": "remote-only-since-2026-05-01",
            }
        )

    return violations


def _append_violations(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _append_bypass() -> None:
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "violation_type": "bypass",
                        "severity": "info",
                        "reason": "MCP_SERIAL_BYPASS=1",
                    }
                )
                + "\n"
            )
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _extract_response_text(payload: object) -> str:
    """Extract the assistant response text from the hook payload (various shapes)."""

    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info", payload)
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        for key in ("response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    # Sunset clause — no-op once upstream fix is verified in deployment.
    if _is_retired():
        return 0

    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    if _is_bypass():
        _append_bypass()
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    try:
        violations = detect_violations(text)
    except re.error:  # defensive — regex engine fault
        return 0

    if violations:
        _append_violations(violations)
        print(
            f"[mcp_serialization] DETECTED {len(violations)} violation(s). "
            f"See: artifacts/windsurf/mcp_serialization_violations.jsonl",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
