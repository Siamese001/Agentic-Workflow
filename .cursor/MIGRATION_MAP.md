# Cursor to Cursor Migration Map

> **W1 SSOT (2026-05-19):** Author new governance in `.cursor/rules/*.mdc` only.  
> `.windsurf/rules/*.md` is a **read-only mirror** for legacy CI/budget reporting — see [.windsurf/rules/README.md](../.windsurf/rules/README.md).  
> **W3 hooks (2026-05-19):** `afterAgentResponse` → single [`after_agent_governance_dispatch.py`](../.cursor/hooks/after_agent_governance_dispatch.py) (ADG + Author-Gate chain + Notion audit + in-process dispatch).

## Rule conversion
| Original Cursor rule | Cursor rule | Trigger | alwaysApply | Globs | Description |
|---|---|---|---:|---|---|
| `.cursor/rules/adg-analysis-procedures.md` | `.cursor/rules/adg-analysis-procedures.mdc` | `model_decision` | `false` | `` | Use this rule when performing ADG analysis, refactoring planning, hotspot assessment, graph-layer queries, P7 artifact c |
| `.cursor/rules/adg-canonical-invariants.md` | `.cursor/rules/adg-canonical-invariants.mdc` | `always_on` | `true` | `` | Converted from Cursor rule adg-canonical-invariants.md |
| `.cursor/rules/adg-graph-layer-enforcement.md` | `.cursor/rules/adg-graph-layer-enforcement.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into adg-analysis-procedures.md (W3.P2 2026-05-12). Use adg-analysis-procedures.md for all ADG graph |
| `.cursor/rules/adg-hotspot-enforcement.md` | `.cursor/rules/adg-hotspot-enforcement.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into adg-analysis-procedures.md (W3.P2 2026-05-12). Use adg-analysis-procedures.md for all ADG hotsp |
| `.cursor/rules/adg-p7-analyst-artifacts.md` | `.cursor/rules/adg-p7-analyst-artifacts.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into adg-analysis-procedures.md (W3.P2 2026-05-12). Use adg-analysis-procedures.md for all P7 artifa |
| `.cursor/rules/adg-repair-discipline.md` | `.cursor/rules/adg-repair-discipline.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into adg-analysis-procedures.md (W3.P2 2026-05-12). Use adg-analysis-procedures.md for all ADG repai |
| `.cursor/rules/adg-test-accelerator-enforcement.md` | `.cursor/rules/adg-test-accelerator-enforcement.mdc` | `glob` | `false` | `` | DEPRECATED — Merged into adg-analysis-procedures.md (W3.P2 2026-05-12). Use adg-analysis-procedures.md §6 for test accel |
| `.cursor/rules/agentic-core-glob-lock.md` | `.cursor/rules/agentic-core-glob-lock.mdc` | `model_decision` | `false` | `agentic_core/**` | Before editing any file under agentic_core/, require generic justification |
| `.cursor/rules/agentic-core-static.md` | `.cursor/rules/agentic-core-static.mdc` | `always_on` | `true` | `` | Core architecture law: agentic_core is app-agnostic governed runtime. |
| `.cursor/rules/anti-pattern-author-gate.md` | `.cursor/rules/anti-pattern-author-gate.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into author-gate-enforcement.md (W3.P1 2026-05-12). Use author-gate-enforcement.md for all Author-Ga |
| `.cursor/rules/approval-exception-policy.md` | `.cursor/rules/approval-exception-policy.mdc` | `model_decision` | `false` | `` | Use this rule when evaluating guardian exemptions, approval classes, or exception evidence requirements. |
| `.cursor/rules/apps-customization.md` | `.cursor/rules/apps-customization.mdc` | `model_decision` | `false` | `apps_*/**` | App-specific behavior belongs in apps_* directories. Guide customization |
| `.cursor/rules/apps-folder-taxonomy.md` | `.cursor/rules/apps-folder-taxonomy.mdc` | `model_decision` | `false` | `` | Apps folder taxonomy (ADR-082) enforcement — load when editing any apps_*/ tree, authoring new files under apps_*, movin |
| `.cursor/rules/apps-rg-interactive-discipline.md` | `.cursor/rules/apps-rg-interactive-discipline.mdc` | `always_on` | `true` | `` | Apply when invoking `python -m apps_rg` or discussing target-company/role/JD/briefing. Enforces Cursor Agent discipline compl |
| `.cursor/rules/apps-rg-post-run-summary.md` | `.cursor/rules/apps-rg-post-run-summary.mdc` | `model_decision` | `false` | `` | Apply when Cursor Agent has just invoked apps_rg (e.g. `python -m apps_rg ...`, `python -m apps_rg.scripts.narrative_pass ... |
| `.cursor/rules/apps-test-surface-taxonomy.md` | `.cursor/rules/apps-test-surface-taxonomy.mdc` | `model_decision` | `false` | `` | Converted from Cursor rule apps-test-surface-taxonomy.md |
| `.cursor/rules/artifact-provenance-discipline.md` | `.cursor/rules/artifact-provenance-discipline.mdc` | `model_decision` | `false` | `` | Converted from Cursor rule artifact-provenance-discipline.md |
| `.cursor/rules/author-gate-decision-points.md` | `.cursor/rules/author-gate-decision-points.mdc` | `model_decision` | `false` | `` | Use this rule when a Author-Gate decision point is reached to apply the correct trigger pattern, option shape, scoring g |
| `.cursor/rules/author-gate-enforcement.md` | `.cursor/rules/author-gate-enforcement.mdc` | `always_on` | `true` | `` | Author-Gate enforcement — pipeline steps, four-requirement contract, canonical-emitter invariant, pipeline-completion in |
| `.cursor/rules/author-gate-queue-drain.md` | `.cursor/rules/author-gate-queue-drain.mdc` | `always_on` | `true` | `` | Converted from Cursor rule author-gate-queue-drain.md |
| `.cursor/rules/author-gate-svp-calibration.md` | `.cursor/rules/author-gate-svp-calibration.mdc` | `model_decision` | `false` | `` | Use this rule for the SVP recommendation lens (1st-5th priorities) and the Red/Yellow/Green Author-Gate calibration metr |
| `.cursor/rules/boundary-audit-required.md` | `.cursor/rules/boundary-audit-required.mdc` | `model_decision` | `false` | `` | Trigger boundary audit when agentic_core files changed or app-specific |
| `.cursor/rules/closed-loop-router-enforcement.md` | `.cursor/rules/closed-loop-router-enforcement.mdc` | `model_decision` | `false` | `` | Apply when authoring or modifying any of the 10 routing/promotion/calibration/feedback decision points (L0/bandit, L0/r5 |
| `.cursor/rules/constitutional.md` | `.cursor/rules/constitutional.mdc` | `always_on` | `true` | `` | Converted from Cursor rule constitutional.md |
| `.cursor/rules/deferred-scope-capture.md` | `.cursor/rules/deferred-scope-capture.mdc` | `model_decision` | `false` | `` | Apply when introducing any deferred scope item (descoping work from a wave/phase, capturing future-work items, or any "w |
| `.cursor/rules/evaluation-promotion-gate.md` | `.cursor/rules/evaluation-promotion-gate.mdc` | `model_decision` | `false` | `` | Apply when promoting any prompt, policy, rubric, or config change through UWG to L4 via v33 §6D. Enforces a mandatory re |
| `.cursor/rules/fortknox-certification-discipline.md` | `.cursor/rules/fortknox-certification-discipline.mdc` | `model_decision` | `false` | `` | Apply for any task mentioning runtime certification, signoff, RTC-REQ-*, attestation, evidence assertions, mutation reje |
| `.cursor/rules/global_rules.md` | `.cursor/rules/global_rules.mdc` | `always_on` | `true` | `` | Converted from Cursor rule global_rules.md |
| `.cursor/rules/intelligence-ledger-family.md` | `.cursor/rules/intelligence-ledger-family.mdc` | `model_decision` | `false` | `` | Apply when extending any post-hook, calibration script, or consulting skill participating in the ten intelligence ledger |
| `.cursor/rules/judge-calibration-cadence.md` | `.cursor/rules/judge-calibration-cadence.mdc` | `model_decision` | `false` | `` | Apply when relying on an LLM-rubric judge at runtime (§5 trace-grader) or in shadow (§6B). Enforces periodic human calib |
| `.cursor/rules/local-llm-wsl2-gpu.md` | `.cursor/rules/local-llm-wsl2-gpu.mdc` | `model_decision` | `false` | `` | Apply when advising on local LLM model size, quantization, VRAM budgeting, or vLLM/llama.cpp configuration on the local  |
| `.cursor/rules/mcp-config-ssot.md` | `.cursor/rules/mcp-config-ssot.mdc` | `glob` | `false` | `.cursor/mcp.json` | Apply when reading or editing the MCP server configuration file to enforce SSOT discipline, strict JSON validity, sync r |
| `.cursor/rules/mcp-pytest-enforcement.md` | `.cursor/rules/mcp-pytest-enforcement.mdc` | `glob` | `false` | `**/test_*.py, **/conftest.py` | Apply when reading or editing test files or conftest to enforce MCP server test coverage, hung-process detection, and py |
| `.cursor/rules/mcp-serialization.md` | `.cursor/rules/mcp-serialization.mdc` | `always_on` | `true` | `` | Converted from Cursor rule mcp-serialization.md |
| `.cursor/rules/memory-management.md` | `.cursor/rules/memory-management.mdc` | `model_decision` | `false` | `` | Use this rule when reading or writing to the persistent memory graph, purging stale entities, or syncing ADG context int |
| `.cursor/rules/memory-notion-writeback.md` | `.cursor/rules/memory-notion-writeback.mdc` | `model_decision` | `false` | `` | Apply when non-trivial work completes and a writeback to Memory MCP (procedural patterns, invariants) or Notion MCP (ADR |
| `.cursor/rules/next-step-capture.md` | `.cursor/rules/next-step-capture.mdc` | `model_decision` | `false` | `` | Apply when Cursor Agent suggests a follow-up action — "could do later", "consider X", optional polish. Demoted from always_on |
| `.cursor/rules/notion-archived-databases.md` | `.cursor/rules/notion-archived-databases.mdc` | `model_decision` | `false` | `` | Reference when deciding whether to write to a Notion database. Five databases were archived 2026-05-02; filesystem is no |
| `.cursor/rules/notion-backlog-plan-linkage.md` | `.cursor/rules/notion-backlog-plan-linkage.mdc` | `conditional` | `false` | `` | DEPRECATED — Merged into plan-lifecycle-procedures.md (W3.P3 2026-05-12). Use consolidated procedures for backlog-plan l |
| `.cursor/rules/notion-plan-identity-verification.md` | `.cursor/rules/notion-plan-identity-verification.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into plan-lifecycle-procedures.md (W3.P3 2026-05-12). Use consolidated procedures for identity verif |
| `.cursor/rules/notion-plan-wave-deferral.md` | `.cursor/rules/notion-plan-wave-deferral.mdc` | `always_on` | `true` | `` | Core invariant only — No Notion MCP calls during multi-wave execution. Full protocol moved to plan-lifecycle-procedures. |
| `.cursor/rules/notion-plans-taxonomy.md` | `.cursor/rules/notion-plans-taxonomy.mdc` | `model_decision` | `false` | `` | Use this rule when interacting with Notion Plans or Backlog Items databases — status field values, invariants for In Pro |
| `.cursor/rules/plan-lifecycle-procedures.md` | `.cursor/rules/plan-lifecycle-procedures.mdc` | `model_decision` | `false` | `` | Use when interacting with plan lifecycle operations — registration, updates, wave execution, deferrals, identity verific |
| `.cursor/rules/plan-location.md` | `.cursor/rules/plan-location.mdc` | `always_on` | `true` | `` | Converted from Cursor rule plan-location.md |
| `.cursor/rules/plan-registration-enforcement.md` | `.cursor/rules/plan-registration-enforcement.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into plan-lifecycle-procedures.md (W3.P3 2026-05-12). Core invariants remain in plan-location.md. |
| `.cursor/rules/plan-update-enforcement.md` | `.cursor/rules/plan-update-enforcement.mdc` | `always_on` | `true` | `` | Core invariant only — Scope expansion authorization requires AUTHORIZATION_DECISION marker. Full procedures moved to pla |
| `.cursor/rules/python-dash-c-quote-hazard.md` | `.cursor/rules/python-dash-c-quote-hazard.mdc` | `model_decision` | `false` | `` | Use when considering `python -c "..."` invocations via run_command — quote-hazard patterns hang pwsh forever. Determinis |
| `.cursor/rules/query-progress-bar.md` | `.cursor/rules/query-progress-bar.mdc` | `model_decision` | `false` | `` | Use when authoring code that contains loops over >10 items, subprocess calls, or functions named scan_/build_/query_/sea |
| `.cursor/rules/refactor-decision-memory.md` | `.cursor/rules/refactor-decision-memory.mdc` | `model_decision` | `false` | `` | Before opening a Author-Gate packet for any refactor-class decision, consult the refactor-decision-memory skill to surfa |
| `.cursor/rules/scope-containment.md` | `.cursor/rules/scope-containment.mdc` | `always_on` | `true` | `` | Converted from Cursor rule scope-containment.md |
| `.cursor/rules/security-hardening.md` | `.cursor/rules/security-hardening.mdc` | `model_decision` | `false` | `` | Use this rule when handling credentials, environment variables, secrets, API keys, or any code path that touches externa |
| `.cursor/rules/sequential-thinking-enforcement.md` | `.cursor/rules/sequential-thinking-enforcement.mdc` | `model_decision` | `false` | `` | Use this rule when a T2/T3 task requires structured reasoning — planning, architecture decisions, multi-file debugging,  |
| `.cursor/rules/ssot-folder-enforcement.md` | `.cursor/rules/ssot-folder-enforcement.mdc` | `always_on` | `true` | `` | SSOT folder routing — every NEW Python file must land in its canonical folder. scripts/, repo-root, tools/_oneoff/, tool |
| `.cursor/rules/wave-completion-discipline.md` | `.cursor/rules/wave-completion-discipline.mdc` | `model_decision` | `false` | `` | DEPRECATED — Merged into plan-lifecycle-procedures.md (W3.P3 2026-05-12). Core wave markers remain in always-on rules. |
| `.cursor/rules/cursor-config-lookup.md` | `.cursor/rules/cursor-config-lookup.mdc` | `model_decision` | `false` | `` | Use for Cursor IDE configuration, rules, hooks, skills, workflows, and local Cursor documentation lookup questions. |

## Directory mapping
- `.cursor/plans/` -> `.cursor/plans/`
- `.cursor/workflows/` -> `.cursor/workflows/`
- `.cursor/skills/` -> `.cursor/skills/`
- `.cursor/scripts/` -> `.cursor/scripts/`
- `.cursor/schemas/` -> `.cursor/schemas/`
- `.cursor/templates/` -> `.cursor/templates/`
- `.cursor/state/` -> `.cursor/state/`
- `.cursor/reminders/` -> `.cursor/reminders/`
- `.cursor/scratch/` -> `.cursor/scratch/`
- `.cursor/mcp.json` -> `.cursor/mcp.json` and `.cursor/cursor_compat/mcp.json`
- `.cursor/hooks.json` -> `.cursor/cursor_compat/hooks.json` (visibility only, not Cursor-native automatic hooks)
