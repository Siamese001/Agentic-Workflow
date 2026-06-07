
<!-- Converted from `.claude/rules/apps-rg-interactive-discipline.md`. Original Cursor trigger: `always_on`. -->

# apps_rg Interactive Discipline

> ⛔ Claude Code MUST NOT pre-fill `--target-company`, `--target-role`, `--jd`, or `--manual-brief` from inferred context. The in-app wizard owns these decisions.

> ⛔ When the user asks Claude Code to run apps_rg without naming all required inputs in the SAME turn, Claude Code MUST issue ONE prompt requesting ALL inputs at once — never multi-turn back-and-forth.

## Static Inputs (configured once, never re-asked)

- **Source resume**: stored at `ops_scripts/apps_rg/` or user-configured path. Claude Code resolves from the most recent `*_resume*.json` or `*_resume*.docx` in that folder. If no resume file exists, ask ONCE and remember the path for the session.

## Single-Prompt Template

When the user says `python -m apps_rg` without all dynamic inputs in the same turn:

```
To run apps_rg, please provide in your next message:
1. Target: company, role, and level (e.g. "Brown & Brown, SVP IT Strategy & Innovation, EXECUTIVE")
2. Job description — file path OR paste text
3. Research briefing — file path to pre-built brief, OR "auto-internal", OR "auto-tavily", OR "skip"
```

- Item 1 is a single cluster (company + role + optional level) — ask together, not separately.
- Source resume is STATIC — do not ask for it every run. Use the configured/most-recent path.
- If the user omits a field, ask for ONLY the missing field(s) in a single follow-up.

## Hard Rules

1. **Verbatim invocation**: `python -m apps_rg` without company/role in the SAME turn → run exactly as typed, no flag additions. Wizard prompts interactively.
2. **Context surfacing OK**: MAY list `apps_rg/scripts/` files as info. Does NOT pre-fill flags.
3. **Same-turn only**: MAY auto-fill `--target-company`/`--target-role` ONLY when user names both in the SAME turn. ❌ MUST NOT infer from prior turns or reuse from session memory.
4. **No stale-file scanning**: MUST NOT scan `apps_rg/scripts/` for `jd_*.json`/`company_research*.json` to auto-fill flags.

## References

Constitutional §6, §18. Sibling: `scope-containment.md`. Runtime guards: `_interactive_wizard`, `_assert_artifact_matches_company` in `apps_rg/__main__.py`. Tests: `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py`.
