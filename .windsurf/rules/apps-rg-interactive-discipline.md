---
trigger: always_on
description: Apply when invoking `python -m apps_rg` or discussing target-company/role/JD/briefing. Enforces Cascade discipline complementing the in-app wizard and cross-company guard.
---

# apps_rg Interactive Discipline

> ⛔ Cascade MUST NOT pre-fill `--target-company`, `--target-role`, `--jd`, or `--manual-brief` from inferred context. The in-app wizard owns these decisions.

> ⛔ When the user asks Cascade to run apps_rg without naming all required inputs in the SAME turn, Cascade MUST issue ONE prompt requesting ALL inputs at once — never multi-turn back-and-forth.

## Single-Prompt Template

```
To run apps_rg, please provide all of the following in your next message:
1. Target company (e.g. "Brown & Brown")
2. Target role (e.g. "SVP IT Strategy & Innovation")
3. Target level (optional — SENIOR / STAFF / EXECUTIVE / skip)
4. Source resume — file path OR paste text
5. Job description — file path OR paste text
6. Research briefing — file path to pre-built brief, OR "auto-internal", OR "auto-tavily", OR "skip"
```

If the user omits a field, ask for ONLY the missing field(s) in a single follow-up.

## Hard Rules

1. **Verbatim invocation**: `python -m apps_rg` without company/role in the SAME turn → run exactly as typed, no flag additions. Wizard prompts interactively.
2. **Context surfacing OK**: MAY list `apps_rg/scripts/` files as info. Does NOT pre-fill flags.
3. **Same-turn only**: MAY auto-fill `--target-company`/`--target-role` ONLY when user names both in the SAME turn. ❌ MUST NOT infer from prior turns or reuse from session memory.
4. **No stale-file scanning**: MUST NOT scan `apps_rg/scripts/` for `jd_*.json`/`company_research*.json` to auto-fill flags.

## References

Constitutional §6, §18. Sibling: `scope-containment.md`. Runtime guards: `_interactive_wizard`, `_assert_artifact_matches_company` in `apps_rg/__main__.py`. Tests: `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py`.
