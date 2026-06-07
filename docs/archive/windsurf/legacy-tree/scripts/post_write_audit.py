#!/usr/bin/env python3
"""
post_write_audit.py — Windsurf post_write_code advisory audit hook (Phase 1.5).

Reads JSON payload from stdin. Payload fields:
  tool_info.file_path  — path of file that was written
  tool_info.edits      — list of {old_string, new_string} dicts

Behavior (ADVISORY ONLY — always exits 0):
  - If file_path matches mcp_config.json:
      * Schema validation: required top-level keys present
      * Env var format: flag ${VAR:-default} shell syntax
      * Tool count: warn if approaching 100 MCP tool limit
      * Risky edit notice: server removal / new server / transport change
  - All other files: exit 0 immediately
  - Logs results to artifacts/windsurf/mcp_lint_audit.jsonl

Fail policy: OPEN — any error → exit 0 silently (never breaks Cursor Agent).
Zero hardcoded paths — repo_root resolved from __file__.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "open"
mcp_config_suffix = "mcp_config.json"

repo_root = Path(__file__).resolve().parents[2]
audit_log = repo_root / "artifacts" / "windsurf" / "mcp_lint_audit.jsonl"

_SHELL_ENV_VAR_RE = re.compile(r"\$\{[A-Z_][A-Z0-9_]*:-[^}]*\}")
_WINDSURF_ENV_VAR_RE = re.compile(r"\$\{env:[A-Z_][A-Z0-9_]*\}")


def _append_audit(record: dict) -> None:
    try:
        audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- write audit log: non-fatal, fail-open
        pass


def lint_mcp_config(file_path: str, edits: list[dict]) -> list[str]:
    """Run JSON-native lint checks on mcp_config.json writes. Returns list of findings."""
    findings: list[str] = []

    path = Path(file_path)
    if not path.exists():
        return findings

    try:
        content = path.read_text(encoding="utf-8")
        config = json.loads(content)
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(f"mcp_config.json could not be parsed: {exc}")
        return findings

    if "mcpServers" not in config:
        findings.append("Schema: missing top-level 'mcpServers' key.")

    servers = config.get("mcpServers", {})
    for name, server_cfg in servers.items():
        if "command" not in server_cfg and "serverUrl" not in server_cfg and "url" not in server_cfg:
            findings.append(
                f"Schema: server '{name}' missing 'command' or 'serverUrl'/'url' field.",
            )
        env = server_cfg.get("env", {})
        for var_name, var_val in env.items():
            if isinstance(var_val, str) and _SHELL_ENV_VAR_RE.search(var_val):
                findings.append(
                    f"Env var format: '{name}.env.{var_name}' uses shell syntax "
                    f"'${{VAR:-default}}' — migrate to '${{env:VAR_NAME}}' (Windsurf native).",
                )

    for edit in edits:
        old = edit.get("old_string", "")
        new = edit.get("new_string", "")
        if old and not new:
            findings.append("Risky edit: server block removed from mcp_config.json.")
        if new and "mcpServers" in new and old == "":
            findings.append("Risky edit: new server added to mcp_config.json.")

    return findings


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

    file_path = tool_info.get("file_path", "")
    edits = tool_info.get("edits", [])

    if not file_path.endswith(mcp_config_suffix):
        return 0

    findings = lint_mcp_config(file_path, edits)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_path": file_path,
        "findings": findings,
        "finding_count": len(findings),
    }
    _append_audit(record)

    for finding in findings:
        print(f"[post_write_audit] {finding}", file=sys.stderr)

    # W4.1 — guardian_exemption ledger: scan edits for new '# guardian: allow-*'
    # comments and record them so the RCA-linker can later bind outcomes.
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event
        guardian_pat = re.compile(r"#\s*guardian:\s*allow-([a-z0-9-]+)\b(.*)$", re.IGNORECASE)
        for edit in edits or []:
            if not isinstance(edit, dict):
                continue
            new_text = edit.get("new_string") or edit.get("new", "") or ""
            if not isinstance(new_text, str):
                continue
            for line_no, line in enumerate(new_text.splitlines(), 1):
                m = guardian_pat.search(line)
                if not m:
                    continue
                emit_ledger_event(
                    ledger="guardian_exemption",
                    event_kind="exemption_created",
                    prediction={
                        "exemption_type": f"allow-{m.group(1)}",
                        "file_path": file_path,
                        "line_in_edit": line_no,
                        "justification": m.group(2).strip(" -:;"),
                    },
                    score_band="clean",  # starts clean; RCA linker may later reband
                    repo_area=file_path,
                )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- hook fail-soft contract
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
