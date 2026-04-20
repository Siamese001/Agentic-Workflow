---
description: Refresh local Windsurf documentation cache in docs/windsurf/ - run when docs may be stale or changelog.md is out of date
---

> **Claude workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Refresh Windsurf Docs Workflow

Invoke with `/refresh-windsurf-docs`. Run this when local Windsurf docs in `docs/windsurf/` may be stale or when `changelog.md` needs updating.

---

## Steps

1. Open a PowerShell terminal at the repo root.
2. Run the refresh script:
   ```powershell
   .\.windsurf\scripts\refresh-windsurf-docs.ps1
   ```
3. Confirm all files were fetched without errors.
4. Verify `docs/windsurf/FETCHED_AT.txt` shows the current timestamp.

---

## What the script does

- Creates `docs/windsurf/` if missing.
- Downloads `llms-full.txt` and 11 per-page `.md` docs from `docs.windsurf.com` and `windsurf.com`.
- Overwrites existing files (idempotent).
- Writes a UTC fetch timestamp to `docs/windsurf/FETCHED_AT.txt`.

## Target files refreshed

| File | Source |
|---|---|
| `llms-full.txt` | https://docs.windsurf.com/llms-full.txt |
| `context-awareness-overview.md` | https://docs.windsurf.com/context-awareness/overview |
| `advanced-configuration.md` | https://docs.windsurf.com/windsurf/advanced |
| `memories-rules.md` | https://docs.windsurf.com/windsurf/cascade/memories |
| `agents-md.md` | https://docs.windsurf.com/windsurf/cascade/agents-md |
| `skills.md` | https://docs.windsurf.com/windsurf/cascade/skills |
| `workflows.md` | https://docs.windsurf.com/windsurf/cascade/workflows |
| `hooks.md` | https://docs.windsurf.com/windsurf/cascade/hooks |
| `mcp.md` | https://docs.windsurf.com/windsurf/cascade/mcp |
| `web-search.md` | https://docs.windsurf.com/windsurf/cascade/web-search |
| `prompt-engineering.md` | https://docs.windsurf.com/best-practices/prompt-engineering |
| `changelog.md` | https://windsurf.com/changelog |
