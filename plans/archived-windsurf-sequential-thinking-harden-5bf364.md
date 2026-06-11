---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\sequential-thinking-harden-5bf364.md'
original_relative_path: 'sequential-thinking-harden-5bf364.md'
source_sha256: 5af751d4f646bc6c924a66bd6ac756bafe8949dbf30e7663630e50d4236923ba
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Harden Sequential Thinking MCP — Model-Agnostic, Debt-Free

Remove dead K2.5-specific Python scaffolding and add a model-agnostic Windsurf rule that enforces `mcp7_sequentialthinking` for all complex tasks across all models (Phoenix and beyond).

---

## Audit Summary

| Category | Status |
|---|---|
| `mcp7_sequentialthinking` in `config/mcp_servers.yaml` | ✅ Live, model-agnostic |
| K2.5 Python forcing files (7 files in `tools/mcp/`) | ❌ Dead — zero production callers |
| `ops_scripts/setup/deploy_sequential_thinking.py` | ❌ Dead standalone script |
| `tools/testing/test_seq_thinking_deployment.py` | ❌ Tests dead code |
| `tests/unit/.../test_sequential_thinking_hardened.py` | ⚠️ Tests `sequential_thinking_booster.py` only |
| `apps_shared/prompts/sequential_thinking_templates.py` | ✅ Keep — reusable templates |
| `tools/utils/planning/token_estimator.py` | ✅ Keep — live utility |

---

## Wave Summary

| Wave | Action | Files | Goal |
|---|---|---|---|
| **W1** | Write Windsurf rule | 1 new `.windsurf/rules/sequential-thinking-enforcement.md` | Model-agnostic enforcement for Phoenix + all models |
| **W2** | Regenerate `.windsurfrules` | Run `python tools/windsurf/preprocess_rules.py` | Rule active in Windsurf |
| **W3** | Archive dead Python debt | 7 files → `tools/archive/seq_thinking_k25/` | Remove noise, preserve history |
| **W4** | Delete/update dead tests | Archive 2 test files that test dead code | No zombie tests |
| **W5** | Validate | Confirm no broken imports, rule text correct | Done |

---

## Wave 1 — New Windsurf Rule (model-agnostic)

**File:** `.windsurf/rules/sequential-thinking-enforcement.md`

**Rule content (summary):**
- `mcp7_sequentialthinking` MUST be called before any T2/T3 task (multi-file, architecture, planning, debugging)
- Trigger conditions: planning, design, debugging, refactoring, analysis, architecture, test strategy
- NOT required for T0/T1 (questions, typo fixes, single-line edits)
- Works for ANY model in Windsurf — Phoenix, SWE, or future models
- No model-name mentions — purely behavioral/complexity-based
- Links to existing tier classification in `.windsurfrules` §0

---

## Wave 3 — Files to Archive

Move to `tools/archive/seq_thinking_k25/` (SVP archival discipline):

```
tools/mcp/kimi_k2_5_cascade_integration.py
tools/mcp/intelligent_sequential_thinking.py
tools/mcp/sequential_thinking_auto_invoker.py
tools/mcp/cascade_preprocessor.py
tools/mcp/sequential_thinking_forcer.py
tools/mcp/sequential_thinking_booster.py
ops_scripts/setup/deploy_sequential_thinking.py
```

---

## Wave 4 — Test Cleanup

Archive (not delete) these test files since they test archived code:
- `tools/testing/test_seq_thinking_deployment.py`
- `tests/unit/agentic_core/L5_safety/enforcement/test_sequential_thinking_hardened.py`

---

## Status: ✅ COMPLETE (2026-04-06)

All waves executed successfully. Sequential thinking MCP is now enforced via model-agnostic Windsurf rule for all models (Phoenix, SWE, and future models). Dead K2.5-specific Python scaffolding archived with SVP archival discipline.

---

## Execution Summary

| Wave | Status | Outcome |
|---|---|---|
| **W1** | ✅ Complete | `.windsurf/rules/sequential-thinking-enforcement.md` created |
| **W2** | ✅ Complete | `.windsurfrules` regenerated with new rule integrated |
| **W3** | ✅ Complete | 7 dead Python files archived to `tools/archive/seq_thinking_k25/` |
| **W4** | ✅ Complete | 2 dead test files archived |
| **W5** | ✅ Complete | No broken imports, validation passed |

---

## What Changes for Phoenix

**Before:** Sequential thinking only encouraged via K2.5-specific Python wrappers — never invoked at runtime, no rule enforcement.

**After:** Windsurf rule forces `mcp7_sequentialthinking` at the start of every T2/T3 task, regardless of which model is active. Phoenix gets identical enforcement as any other model.

---

## What Does NOT Change

- `config/mcp_servers.yaml` — no changes needed (mcp7 already registered and enabled)
- `apps_shared/prompts/sequential_thinking_templates.py` — kept as live utility
- `tools/utils/planning/token_estimator.py` — kept
- No Python production code changes required — enforcement is pure Windsurf rule layer
