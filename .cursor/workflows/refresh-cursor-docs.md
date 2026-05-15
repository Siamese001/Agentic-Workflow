---
description: Refresh local Cursor documentation cache in docs/cursor/ - run when docs may be stale or changelog.md is out of date
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Refresh Cursor Docs Workflow

Invoke with `/refresh-cursor-docs`. Run this when local Cursor docs in `docs/cursor/` may be stale or when `changelog.md` needs updating.

---

## Steps

1. Open a PowerShell terminal at the repo root.
2. Run the refresh script:
   ```powershell
   .\.cursor\scripts\refresh-cursor-docs.ps1
   ```
3. Confirm all files were fetched without errors.
4. Verify `docs/cursor/FETCHED_AT.txt` shows the current timestamp.

---

## What the script does

- Creates `docs/cursor/` if missing.
- Downloads `llms-full.txt` and 11 per-page `.md` docs from `docs.cursor.com` and `cursor.com`.
- Overwrites existing files (idempotent).
- Writes a UTC fetch timestamp to `docs/cursor/FETCHED_AT.txt`.

## Target files refreshed

| File | Source |
|---|---|
| `llms-full.txt` | https://docs.cursor.com/llms-full.txt |
| `context-awareness-overview.md` | https://docs.cursor.com/context-awareness/overview |
| `advanced-configuration.md` | https://docs.cursor.com/cursor/advanced |
| `memories-rules.md` | https://docs.cursor.com/cursor/cursor_agent/memories |
| `agents-md.md` | https://docs.cursor.com/cursor/cursor_agent/agents-md |
| `skills.md` | https://docs.cursor.com/cursor/cursor_agent/skills |
| `workflows.md` | https://docs.cursor.com/cursor/cursor_agent/workflows |
| `hooks.md` | https://docs.cursor.com/cursor/cursor_agent/hooks |
| `mcp.md` | https://docs.cursor.com/cursor/cursor_agent/mcp |
| `web-search.md` | https://docs.cursor.com/cursor/cursor_agent/web-search |
| `prompt-engineering.md` | https://docs.cursor.com/best-practices/prompt-engineering |
| `changelog.md` | https://cursor.com/changelog |
