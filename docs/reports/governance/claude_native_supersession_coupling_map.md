# Claude-Native Supersession — W0 Coupling Map

> Plan: [claude-native-supersession-9d3f7a.md](../../../plans/claude-native-supersession-9d3f7a.md)
> Branch: `claude/native-supersession` (off `origin/main` @ `d1e2b7e4f2`)
> Generated: W0 audit, 2026-06-07. Read-only — no edits made producing this map.

## Purpose

Before any teardown, enumerate the **exact CI gates, pre-commit hooks, governance scripts,
skills, rules, and constitutional §-citations** coupled to each emulation surface (S1–S6), so
each wave can retire markers/scripts **in lockstep** with their gates. The cardinal failure mode:
remove a marker but leave its gate → CI breaks; remove a gate but leave its marker producer → drift.

## Baseline naming note (critical)

`origin/main` still uses the **old `post_cursor_agent_*` script names**. The `post_agent_*` rename
is uncommitted W5 work parked on `w5/w3-script-rename`. All paths below use the **`post_cursor_agent_*`
baseline names** — that is what this branch actually contains.

## Active enforcement surface (baseline)

- **Hooks** (`.claude/settings.json`): `before_submit_prompt`, `pre_user_prompt_author_gate_reminder`
  (UserPromptSubmit); `before_shell_execution`, `before_read_file`, `before_grep`, `before_mcp_execution`
  (PreToolUse); `after_file_edit` (PostToolUse); `stop_task_audit`, `after_agent_governance_dispatch` (Stop).
- **Stop dispatch chain** (`after_agent_governance_dispatch.py`): runs `post_cursor_agent_adg_audit.py`
  + a 10-script AG/MCP chain + the unified Notion auditor + in-process `post_cursor_agent_dispatch.py`
  = **~12 subprocesses per Stop**.
- **Pre-commit** (`.pre-commit-config.yaml`): ~50 hooks.
- **CI assurance plane** (`ops_scripts/ci/run_contract_gates.py`).

## Decision Matrix — per surface

### S1 · Author-Gate → native `AskUserQuestion` + file-memory precedent  (Wave W1, leverage ★★★★★)

| Coupling type | Artifacts |
|---|---|
| **CI gates** (run_contract_gates.py) | `author_gate/check_ledger_schema.py`, `check_refactor_decision_ledger_ssot.py`, `author_gate/check_outcome_coverage.py`, `author_gate/check_ledger_integrity.py`, `author_gate/check_ask_user_question_packet_freshness.py`, `check_author_gate_pipeline_freshness.py`, `check_author_gate_v2_completeness.py`, `author_gate/detect_author_gate_ledger_anomalies.py`, `author_gate/rollup_governance_bypass_logs.py` |
| **Pre-commit** | T6d `author-gate-ledger-schema`, T6d2 `author-gate-ui-conformance`, T7e `author-gate-ledger-coverage`, T7t `ag-queue-seed-markers` |
| **Governance scripts** | `pre_author_gate.py`, `pre_ask_user_question_gate.py`, `pre_user_prompt_author_gate_reminder.py`, `pre_user_prompt_ag_queue_surface.py`, `capture_author_gate.py`, `author_gate_marker_validator.py`, `author_gate_ledger_integrity.py`, `promote_author_gate_patterns.py`, `_author_gate_queue.py`, `_author_gate_pipeline_check.py`, `post_cursor_agent_author_gate_*` (capture/miss_detector/ui_audit/schema_audit/pipeline_audit), `post_cursor_agent_ask_user_question_packet_audit.py`, `post_cursor_agent_ag_queue_{seed_capture,drain_audit}.py` |
| **Skills** | `author-gate-packet-builder`, `author-gate-ui-renderer`, `refactor-decision-memory` (precedent — reshape to file memory, don't delete concept) |
| **Rules** | `003-author-gate-hitl.md`, `author-gate-enforcement.md`, `author-gate-decision-points.md`, `author-gate-svp-calibration.md`, `author-gate-queue-drain.md`, `anti-pattern-author-gate.md` (already deprecated) |
| **Constitutional** | §6 (Author-Gate for ambiguous decisions — **invariant kept**), §30 (capture health — retire), §35 (queue drain — retire) |
| **Markers retired** | `AUTHOR_GATE_PACKET:`, `DECISION_CAPTURED:`, `AG_QUEUE_SEED:`, `AG_QUEUE_PENDING:` |
| **Invariant preserved** | "Stop and ask via `AskUserQuestion` before edits when ≥2 plausible approaches with different blast radius and no unambiguous directive." (one CLAUDE.md line) |
| **Reversibility** | High — scripts archived not deleted; gates removed from registries (re-addable). Ledger SQLite preserved read-only. |

### S2 · SR_* markers → native plan mode  (Wave W2, leverage ★★★★)

| Coupling type | Artifacts |
|---|---|
| **Governance scripts** | `pre_prompt_classifier.py` (hosts SR classification **and** ADG step-0 — split, keep ADG) |
| **Rules** | `plan-first-enforcement.md`, `CLAUDE.md` "Plan First" section |
| **Skills** | `structured-reasoning` (+ `/structured-reasoning` alias) — keep retrieval-discipline content, drop marker scheme |
| **Markers retired** | `SR_INTAKE`, `SR_PLAN`, `SR_APPROVAL`, `SR_EXECUTE`, `SR_VERIFY` |
| **Invariant preserved** | "T2/T3 ⇒ enter plan mode (no edits before approval)." |
| **Reversibility** | High — no CI gate enforces SR markers directly (advisory rule only). Low blast radius. |

### S3 · Memory MCP ritual → native file memory  (Wave W3, leverage ★★★★)

| Coupling type | Artifacts |
|---|---|
| **CI gates** | `check_memory_health.py` (daily) |
| **Governance / tools** | `mem_recall_session_start` mandate, `pre_mcp_gate.py` memory-first block, `tools/memory/purge_sync.py`, `mem_cleanup_stale` |
| **Rules** | `memory-management.md`, `memory-notion-writeback.md`, `writeback-discipline` skill |
| **Constitutional** | §17 (session-start recall — reshape to native memory) |
| **Invariant preserved** | "Recall project memory at session start; write back significant decisions (15/3 rule)." Target shifts MCP→native files. |
| **Reversibility** | Medium — memory-first `pre_mcp_gate` block is load-bearing for other MCP ordering; reshape carefully. Keep knowledge-graph MCP for genuine graph queries. |

### S4 · Deferred-scope / next-step → `spawn_task`  (Wave W4, leverage ★★★)

| Coupling type | Artifacts |
|---|---|
| **CI gates** | `check_deferred_scope_markers.py` (run_contract_gates + T6e1 + T7i pre-commit), `check_notion_schema_mece.py` (T7j) |
| **Governance scripts** | `post_cursor_agent_deferred_scope_capture.py`, `post_cursor_agent_next_step_capture.py`, `post_cursor_agent_next_step_miss_detector.py`, `pre_user_prompt_deferred_scope_recovery.py`, `_deferred_scope_plan_scaffold.py`, `tools/priority/deferred_scope_scorer.py` |
| **Rules** | `deferred-scope-capture.md`, `next-step-capture.md` |
| **Constitutional** | §24 (deferred-scope capture — reshape: scored wave-deferral stays, agent-suggestion path → `spawn_task`) |
| **Markers** | `DEFERRED_SCOPE:`, `NEXT_STEP:` |
| **Reversibility** | Medium — §24 also feeds ADG burndown markers (`adg-gates-markers`). Keep the scored-wave-deferral marker; only retire the agent-suggestion capture path. |

### S5 · Wave-lifecycle markers → TodoWrite + explicit Notion  (Wave W5, leverage ★★★)

| Coupling type | Artifacts |
|---|---|
| **CI gates** | `check_plan_registration_freshness.py` (T7u / §36), `post_cursor_agent_plan_wave_summary_audit.py` |
| **Governance scripts** | `_wave_execution_state.py`, `post_cursor_agent_wave_completion_audit.py`, `post_cursor_agent_wave_lifecycle_capture.py`, `plan_driven_closer.py`, `post_commit_phase_closer.py` |
| **Rules** | `notion-plan-wave-deferral.md`, `plan-lifecycle-procedures.md`, `plan-update-enforcement.md` |
| **Constitutional** | §36 (plan–Notion registration — keep Notion as explicit store; retire in-session marker emulation) |
| **Markers** | `WAVE_COMPLETE:`, `PHASE_COMPLETE:`, `PLAN_COMPLETE:`, `WAVE_START:` |
| **Reversibility** | Medium — Notion is a real external store; only the *in-session orchestration markers* are emulation. |

### S6 · Hook overhead / legacy / alias commands / mcp-serialization  (Wave W5, leverage ★★★)

| Coupling type | Artifacts |
|---|---|
| **Dispatch** | `after_agent_governance_dispatch.py` (slim the 12-subprocess chain to survivors) |
| **Legacy trees** | `.claude/governance/scripts/_legacy_cursor/`, `_legacy_windsurf/` (delete after zero-import proof) |
| **Commands** | thin-alias `.claude/commands/*.md`: `tavily-*` (6), `adg-repair-loop`, `adg-test-triage-gate`, `antipattern-author-gate`, `author-gate-decision-gate`, `structured-reasoning`, `author-gate-calibration-report` |
| **Rules** | `mcp-serialization.md` (one-MCP-per-block batching — Cursor constraint, retire) |
| **Governance** | `pre_mcp_gate.py` serialization sentinel (keep Notion-token + GitKraken checks; drop batching) |
| **Reversibility** | High — mechanical cleanup; legacy trees already segregated. |

## Lockstep retirement order (per wave)

For each wave Wn: **(1)** rewrite invariant into CLAUDE.md/rule → **(2)** move procedure to native feature →
**(3)** remove coupled CI-gate entries from `run_contract_gates.py` **and** `.pre-commit-config.yaml` →
**(4)** drop the chain members from `after_agent_governance_dispatch.py` →
**(5)** `git mv` scripts to `archives/claude_native_supersession_2026-06-07/` →
**(6)** run `python ops_scripts/ci/run_contract_gates.py` green → **(7)** commit (`--no-verify` sanctioned for
governance per `approval-exception-policy.md`) → **(8)** one ADR.

## Governance commit policy for this work

`approval-exception-policy.md` explicitly permits `git commit --no-verify` for **"Wave governance commits
(policy docs, rules)"** and **"Hook infrastructure fixes."** This teardown is exactly that class. Each wave
commit will state the rationale. Production-code anti-pattern bypass remains forbidden (none here).
