# Windsurf always_on demotion map — 2026-05-26

**Plan:** `governance-dedup-closeout-e8a4c2` wave W4  
**Generated:** 2026-05-26

## Summary

| Metric | Before | After |
|--------|--------|-------|
| `trigger: always_on` file count | 13 | **0** |
| Windsurf always_on bytes (gate scan) | 47,493 | **0** |
| Tier-1 Cursor (`alwaysApply` + AGENTS.md) | 19,674 B | **PASS** (unchanged) |

## Demotion table

| Windsurf rule | Cursor on-demand SSOT | Before (B) | Action |
|---------------|----------------------|------------|--------|
| [adg-canonical-invariants.md](../../.windsurf/rules/adg-canonical-invariants.md) | [adg-canonical-invariants.mdc](../../.cursor/rules/adg-canonical-invariants.mdc) | 1,980 | `model_decision` |
| [agentic-core-static.md](../../.windsurf/rules/agentic-core-static.md) | [agentic-core-static.mdc](../../.cursor/rules/agentic-core-static.mdc) | 3,703 | `model_decision` |
| [apps-rg-interactive-discipline.md](../../.windsurf/rules/apps-rg-interactive-discipline.md) | [apps-rg-interactive-discipline.mdc](../../.cursor/rules/apps-rg-interactive-discipline.mdc) | 2,509 | `model_decision` |
| [author-gate-enforcement.md](../../.windsurf/rules/author-gate-enforcement.md) | [author-gate-enforcement.mdc](../../.cursor/rules/author-gate-enforcement.mdc) | 7,611 | `model_decision` |
| [author-gate-queue-drain.md](../../.windsurf/rules/author-gate-queue-drain.md) | [author-gate-queue-drain.mdc](../../.cursor/rules/author-gate-queue-drain.mdc) | 2,408 | `model_decision` |
| [constitutional.md](../../.windsurf/rules/constitutional.md) | [constitutional.mdc](../../.cursor/rules/constitutional.mdc) | 11,653 | `model_decision` |
| [global_rules.md](../../.windsurf/rules/global_rules.md) | [global_rules.mdc](../../.cursor/rules/global_rules.mdc) | 4,652 | `model_decision` |
| [mcp-serialization.md](../../.windsurf/rules/mcp-serialization.md) | [mcp-serialization.mdc](../../.cursor/rules/mcp-serialization.mdc) | 1,233 | `model_decision` |
| [notion-plan-wave-deferral.md](../../.windsurf/rules/notion-plan-wave-deferral.md) | [notion-plan-wave-deferral.mdc](../../.cursor/rules/notion-plan-wave-deferral.mdc) | 1,725 | `model_decision` |
| [plan-location.md](../../.windsurf/rules/plan-location.md) | [plan-location.mdc](../../.cursor/rules/plan-location.mdc) | 3,091 | `model_decision` |
| [plan-update-enforcement.md](../../.windsurf/rules/plan-update-enforcement.md) | [plan-update-enforcement.mdc](../../.cursor/rules/plan-update-enforcement.mdc) | 1,436 | `model_decision` |
| [scope-containment.md](../../.windsurf/rules/scope-containment.md) | [scope-containment.mdc](../../.cursor/rules/scope-containment.mdc) | 3,175 | `model_decision` |
| [ssot-folder-enforcement.md](../../.windsurf/rules/ssot-folder-enforcement.md) | [ssot-folder-enforcement.mdc](../../.cursor/rules/ssot-folder-enforcement.mdc) | 2,317 | `model_decision` |

**Total demoted:** 47,493 bytes (~11,873 tokens) removed from Windsurf always-on load.

## Policy

- Windsurf mirror is **legacy read-only** for CI parity; Cursor agents use `.cursor/rules/*.mdc` (`alwaysApply: false` for all rows above).
- Tier-1 budget: four `000`–`003` `.mdc` + `AGENTS.md` only (`check_always_on_token_budget.py`).
- Tool: [windsurf_always_on_demote_w4.py](../../tools/cursor/windsurf_always_on_demote_w4.py) (idempotent; skips files already demoted).

## Verification

```bash
python ops_scripts/ci/check_always_on_token_budget.py
# windsurf_legacy_always_on: files: 0, WINDSURF_ALWAYS_ON_TOTAL: 0
```
