# Agent Guidance — Agentic-Workflow

## Plan First. Execute Second.

**For complex tasks (T2/T3), the first output MUST be a plan — never edits.**

A task is T2/T3 if it involves:
- 2 or more files
- Cross-layer changes (e.g. L0→L3)
- Architecture decisions
- Multi-file debugging
- New features or refactoring affecting more than one module

**For T2/T3 tasks, emit this block before any tool calls:**

```
## SR_INTAKE
Objective: <one sentence>
Constraints: [list]
Assumptions: [list]
Tier: T2 | T3

## SR_PLAN
1. [verb-first step]
2. ...
N. [verification step]

Tools needed: [list]
Risks: [list]
```

Then gather evidence (reads only). Then emit `SR_APPROVAL: APPROVED` before any writes or edits.

**T0/T1 tasks (single file, ≤20 lines, questions) are exempt — answer or edit directly.**

## Layer Separation

Keep these four layers separate at all times:

| Layer | Rule |
|-------|------|
| Reasoning | Native Cascade only — no tool calls |
| Routing | Tool selection and MCP health checks only |
| Execution | Edits/writes/commands — only after SR_APPROVAL |
| Verification | Tests, diffs, health checks — after execution |

## MCP Quick Reference

| Need | Tool |
|------|------|
| ADG scope / blast radius | `adg_health`, `adg_edge_fanout` (server: `adg_sqlite`) |
| Session context | `mem_recall_session_start` (server: `memory`) |
| Task tracking | `create_task`, `update_task` (server: `task_manager`) |
| File reads | `read_text_file` (server: `filesystem`) or native `read_file` |
| Tests | `run_tests` (server: `pytest_mcp`) or `run_command` with pytest |
| Git state | `git_status` (server: `GitKraken`) or `run_command` with git |

If any MCP hangs: STOP, do not retry, route around it, note `[MCP UNAVAILABLE]`.

## Constitutional Constraints (always-on)

- No PowerShell — use `subprocess.run(argv, shell=False)` or `run_command`
- No `pytest.mark.skip` without `strict=True`
- No `except Exception` without guardian exemption
- No edits during planning phase
- ADG graph is the primary analysis primitive — not grep

Full rules: `.windsurf/rules/` and `.windsurf/RULES_INDEX.md`

## Windsurf Configuration Docs

- Local docs: `docs/windsurf/llms-full.txt` (broad coverage), `docs/windsurf/*.md` (per-topic Markdown)
- Check local docs first. Use web search only for version-sensitive or newly-changed features.
- Hooks: `command`, `show_output`, `working_directory` only — `file_pattern` is non-standard and FORBIDDEN.
- Skills: entry file MUST be `SKILL.md` (uppercase). Supporting files live alongside it in the skill directory.
- Rules: `model_decision` and `glob` triggers MUST have a single-sentence `description` field in frontmatter.
- Plans SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `C:\Users\*\` or `docs/reports/plans/`.
