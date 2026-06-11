---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\core-judge-panel-harness-f3c8d1.md'
original_relative_path: '_archive\\2026-05\\core-judge-panel-harness-f3c8d1.md'
source_sha256: dfbc4309c3a482f9ffb9f7b2495f23704ceae1b10ba41adf1870e5efec7725ed
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: core-judge-panel-harness-f3c8d1
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: artifacts/governance/migration_receipts/20260524_core_judge_panel_harness.json
dod_exempt: false
---

# Agentic Core — Multi-Provider Judge Panel Harness

**North star:** Generic spine infrastructure so any `apps_*` proof panel grades **one canonical judge contract** (stable digest) through **N provider adapters** with **transport parity receipts**, **provider-neutral pass math**, and **app-supplied gate-closure reconcile maps** — preventing “same packet, three different effective rules.”

**Problem this solves:** `apps_rg` built a parallel X1D stack (`run_llm_judges` + hand-rolled `_call_gemini` / `_call_openai` / `_call_anthropic`) outside `agentic_core/runtime/judges/llm_judge_gateway.py`. Core has single-judge gateway, judge jury (candidate selection), Exit-eval HTTP judges, and **reasoning** transport parity (`transport_capabilities` + `reasoning_control_resolver`) — but **no** multi-provider panel harness. That gap allowed transport and objective drift (Brown & Brown Claude-only soft-fail while X2 all PASS).

**Anti-pattern (forbidden):** Moving `apps_rg` rubrics, X2 gate definitions, or executive-summary copy into `agentic_core`. Core owns **orchestration law**; apps own **content and closure maps**.

**Related (coordinate, do not duplicate):**
- [`exec-summary-x1d-transport-parity-d8f2a1.md`](exec-summary-x1d-transport-parity-d8f2a1.md) — **apps_rg remediation** (rubric/packet/reconcile/transport in place). Ship or complete W1–W2 there **before** apps_rg migrates onto core harness (W3 here).
- [`exec-summary-operator-ship-a3f7c2.md`](exec-summary-operator-ship-a3f7c2.md) — CERTIFIED / 3/3 operator semantics.
- [`apps-rg-v40-spine-gap-c4a8f1.md`](apps-rg-v40-spine-gap-c4a8f1.md) — judges migrate to apps; core keeps gateway (this plan defines the gateway shape).

> **plan_id discipline:** `core-judge-panel-harness-f3c8d1` ↔ file stem ↔ markers `plan=core-judge-panel-harness-f3c8d1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-24
LAST_UPDATED: 2026-05-24

NOTION_PAGE_ID: 36a27693-f55c-81d5-a1cf-ddc37cbbfad2
NOTION_PLAN_URL: https://www.notion.so/core-judge-panel-harness-f3c8d1-36a27693f55c81d5a1cfddc37cbbfad2

PLAN_CREATED: slug=core-judge-panel-harness-f3c8d1 path=.cursor/plans/core-judge-panel-harness-f3c8d1.md status=Completed notion_page=36a27693-f55c-81d5-a1cf-ddc37cbbfad2
PLAN_COMPLETE: plan=core-judge-panel-harness-f3c8d1 note="core panel harness + apps_rg GRADE_ONLY migration; closeout artifacts/apps_rg/core_judge_panel_harness_closeout_receipt.md"

---

## Context (SCQA)

- **Situation** — `agentic_core` provides `LLMJudgeGateway` (one profile → one provider), `JudgeJuryRunner` (score candidates), L3 `BaseHttpJudge` (Exit dimensions), and reasoning transport receipts. `apps_rg` owns X1D semantic quality via `executive_summary_x1d.run_llm_judges` and section policies requiring Gemini + OpenAI + Claude on proof sections.
- **Complication** — Without a core panel harness, each app reimplements fan-out, pass math, JSON locks, token budgets, and reconcile policy. `apps_rg` drifted: identical user packet, divergent system/transport, conflicting rubric vs X2 gates. Local test harness (`x1d_judge_transport_contract.py`) audits source after the fact; nothing enforces parity at runtime in core.
- **Question** — How do we add **generic** infrastructure so multi-provider judge panels cannot silently apply different rules?
- **Answer** — Introduce `agentic_core/runtime/judges/panel/` with **CanonicalJudgeContract**, **JudgePanelRunner**, **JudgeProviderAdapter** protocol, **TransportParityAuditor**, **ScoreNormalizationLaw**, and **GateClosureReconcileEngine** (algorithm in core, map in app). Migrate `apps_rg` adapters behind the protocol after apps remediation plan stabilizes contracts.

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | Core panel harness is **app-agnostic**: no `apps_rg` / `apps_lic` literals, gate IDs, or rubric prose in `agentic_core`. |
| INV-2 | Apps supply: rendered contract bytes, `deterministic_gate_summary`, gate-closure map profile ref, provider registry keys. |
| INV-3 | **One** `judge_contract_hash` per grading invocation; every provider request receipt logs it. |
| INV-4 | **One** rendered user payload per hash; providers may not mutate objectives in transport layer. |
| INV-5 | Transport adapters differ only in HTTP/API mechanics (schema placement, `json_object`, `responseSchema`, etc.). |
| INV-6 | **ScoreNormalizationLaw** in core is the only authority for `pass` / `decisive_failure` from parsed JSON. |
| INV-7 | **GateClosureReconcileEngine** may suppress findings only via app map + passed gate evidence; never blanket FAIL→PASS. |
| INV-8 | Transport failure (truncation, parse error after bounded retry) → `BLOCKED` / `INCONCLUSIVE`, not content FAIL/PASS. |
| INV-9 | `UNKNOWN` is never PASS; mocked/stub paths cannot satisfy proof-required panel slots without explicit flag. |
| INV-10 | Existing `llm_judge_gateway` remains for single-judge profile flows; panel harness is additive, not a breaking replace in W1. |
| INV-11 | Boundary migration receipt required before merge (`artifacts/governance/migration_receipts/`). |
| INV-12 | Author-Gate approval required at W0 (core addition). |

---

## Product Decisions (lock W0)

| ID | Decision |
|----|----------|
| PD-1 | New package path: `agentic_core/runtime/judges/panel/` (not `evaluation/judges/` — runtime orchestration SSOT). |
| PD-2 | Reuse **pattern** from `reasoning_control_resolver` + `TransportCapabilities` for judge transport receipts (new types, no coupling to SovereignLLMGateway). |
| PD-3 | `JudgeProviderAdapter` registered by **provider_key** string; apps register implementations at startup or via entrypoint factory. |
| PD-4 | Gate-closure map loaded from app profile (YAML/JSON/Python) validated by core schema; exec summary map stays in `apps_rg`. |
| PD-5 | **W2 migration** of `apps_rg` is optional until `exec-summary-x1d-transport-parity-d8f2a1` W1–W2 green; harness ships with core tests + fake adapters first. |
| PD-6 | Deprecate `inspect.getsource` transport audits in apps over time; replace with core preflight API + contract tests. |
| PD-7 | Second consumer (`apps_lic` or research) is **W4 optional** — only if product needs same 3-provider proof panel. |

---

## Core Module Map (target)

| Module | Responsibility |
|--------|----------------|
| `canonical_contract.py` | Immutable contract artifact, stable digest, validation |
| `adapter_protocol.py` | `JudgeProviderAdapter` — build request, parse response, declare capabilities |
| `panel_runner.py` | Fan-out, shared prompt/hash, bounded retry policy, aggregate outcomes |
| `transport_parity.py` | Declared vs observed transport audit (tokens, json lock, truncation field) |
| `score_law.py` | Provider-neutral pass / decisive_failure / scale normalization |
| `gate_closure_reconcile.py` | Reconcile algorithm + receipt schema |
| `panel_types.py` | `PanelJudgeOutcome`, `TransportReceipt`, `ReconciliationReceipt` |
| `panel_registry.py` | Register adapters by provider_key (generic dict, no app imports) |

---

## Execution Order

| Wave | Focus | Est. Tokens |
|------|-------|-------------|
| **W0** | ADR, boundary receipt, Author-Gate, protocol spec | ~40K |
| **W1** | Core harness + unit tests (fake adapters) | ~120K |
| **W2** | `apps_rg` adapter migration + parity proof | ~100K |
| **W3** | CI governance, deprecate ad-hoc audits, docs | ~50K |

**Dependency:** `exec-summary-x1d-transport-parity-d8f2a1` W1–W2 should complete (or be explicitly merged into W2 here) before `apps_rg` deletes hand-rolled `_call_*` orchestration.

---

## Status Tables

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.0–W0.2 | ADR + Author-Gate + boundary receipt | ~40K | Core edit authorized | ✅ DONE | Receipt + ADR merged; protocol frozen |
| W1 | W1.0–W1.5 | Panel package + tests | ~120K | No live API in unit tests | ✅ DONE | `pytest tests/unit/agentic_core/runtime/judges/panel/` PASS |
| W2 | W2.0–W2.3 | apps_rg adapters + migration | ~100K | Transport parity plan W2 done | ✅ DONE | `run_llm_judges` GRADE_ONLY → panel; transport tests green |
| W3 | W3.0–W3.2 | CI + docs + audit deprecation | ~50K | W2 merged | ✅ DONE | GOV-JPH PASS; drift gate invokes panel boundary |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.0 | ADR + protocol spec | `docs/adr/ADR-082-*.md`, plan | undefined harness API | ~15K | ✅ DONE |
| W0.1 | Author-Gate + migration receipt | `artifacts/governance/migration_receipts/` | core glob-lock | ~10K | ✅ DONE |
| W0.2 | Interface review with apps_rg | `docs/reports/cursor/core_judge_panel_w02_cross_plan_sync.md` | duplicate work | ~15K | ✅ DONE |
| W1.0 | `canonical_contract` + digest | `agentic_core/runtime/judges/panel/` | hash instability | ~25K | ✅ DONE |
| W1.1 | `adapter_protocol` + registry | panel package | provider drift | ~20K | ✅ DONE |
| W1.2 | `panel_runner` fan-out | panel package | duplicate prompts | ~25K | ✅ DONE |
| W1.3 | `transport_parity` auditor | panel package | no runtime guard | ~20K | ✅ DONE |
| W1.4 | `score_law` + reconcile engine | panel package | pass laundering | ~20K | ✅ DONE |
| W1.5 | Core unit + contract tests | `tests/unit/agentic_core/...` | no proof without tests | ~30K | ✅ DONE |
| W2.0 | apps_rg transport adapters | `apps_rg/runtime/judges/adapters/` | `_call_* duplication | ~35K | ✅ DONE |
| W2.1 | Wire `run_llm_judges` → panel | `executive_summary_x1d.py` | regression risk | ~35K | ✅ DONE |
| W2.2 | Gate-closure map → core export | `executive_summary_x1d_gate_closure_map.py` | reconcile gap | ~20K | ✅ DONE |
| W2.3 | Transport tests + core preflight | tests, `x1d_panel_preflight.py` | inspect.getsource debt | ~10K | ✅ DONE |
| W3.0 | CI: GOV-JPH boundary | `check_judge_panel_harness_boundary.py` | undocumented core | ~20K | ✅ DONE |
| W3.1 | Core-backed transport audits | `x1d_judge_transport_contract.py` | dual SSOT | ~15K | ✅ DONE |
| W3.2 | AGENTS + gateway doc | `AGENTS.md`, `docs/cursor/judge_panel_vs_llm_gateway.md` | discoverability | ~15K | ✅ DONE |

---

## Out Of Scope

- Rewriting Exit-eval L3 judges to use panel harness (separate track)
- Replacing `JudgeJuryRunner` candidate-selection semantics
- `agentic_core` owning apps_rg rubric text or X2 validator implementations
- Mandatory second-app (`apps_lic`) adoption in initial release
- Weakening X2 gates or judge thresholds to force panel PASS
- Live API proof as sole DoD for W1 (unit tests + fake adapters only)

---

## Wave 0 — ADR, Author-Gate, Protocol Freeze

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: A
WAVE_COMPLETE: plan=core-judge-panel-harness-f3c8d1 wave=0 note="ADR-082 + migration receipt + W0.2 sync doc"

**Phases**:
- **W0.0** — ADR: `ADR-082-multi-provider-judge-panel-harness.md` | ~15K | PHASE_STATUS: DONE
- **W0.1** — `artifacts/governance/migration_receipts/20260524_core_judge_panel_harness.json` | ~10K | PHASE_STATUS: DONE
- **W0.2** — `docs/reports/cursor/core_judge_panel_w02_cross_plan_sync.md` | ~15K | PHASE_STATUS: DONE

**Acceptance**:
- Author-Gate captured with `author_gate_receipt_ref` populated in plan frontmatter
- ADR lists explicit non-goals (no apps_rg rubric in core)
- Protocol sketch reviewed: adapter methods, receipt fields, reconcile inputs

---

## Wave 1 — Core Panel Harness (Generic)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B
WAVE_COMPLETE: plan=core-judge-panel-harness-f3c8d1 wave=1 note="7 panel unit tests PASS"

**Phases**:
- **W1.0** — `CanonicalJudgeContract` | ~25K | PHASE_STATUS: DONE
- **W1.1** — `JudgeProviderAdapter` + `PanelAdapterRegistry` | ~20K | PHASE_STATUS: DONE
- **W1.2** — `JudgePanelRunner.run` | ~25K | PHASE_STATUS: DONE
- **W1.3** — `audit_transport_parity` | ~20K | PHASE_STATUS: DONE
- **W1.4** — `normalize_panel_score` + `reconcile_against_gate_closures` | ~20K | PHASE_STATUS: DONE
- **W1.5** — `tests/unit/agentic_core/runtime/judges/panel/` | ~30K | PHASE_STATUS: DONE

**Acceptance**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest tests/unit/agentic_core/runtime/judges/panel/ -q
```
- All tests PASS without network
- No imports from `apps_rg` in `agentic_core/runtime/judges/panel/`

**Key files (new)**:
- `agentic_core/runtime/judges/panel/*.py`
- `tests/unit/agentic_core/runtime/judges/panel/test_*.py`

---

## Wave 2 — apps_rg Migration (First Consumer)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C
WAVE_COMPLETE: plan=core-judge-panel-harness-f3c8d1 wave=2 note="GRADE_ONLY panel bridge + adapters package"

**Prerequisite:** [`exec-summary-x1d-transport-parity-d8f2a1`](exec-summary-x1d-transport-parity-d8f2a1.md) W1–W2 complete.

**Phases**:
- **W2.0** — `x1d_panel_adapters.py` + `adapters/` re-export | ~35K | PHASE_STATUS: DONE
- **W2.1** — `run_llm_judges` GRADE_ONLY → `x1d_panel_bridge` | ~35K | PHASE_STATUS: DONE
- **W2.2** — `core_gate_closure_map()` export + bridge test | ~20K | PHASE_STATUS: DONE
- **W2.3** — Core preflight in transport contract + panel tests | ~10K | PHASE_STATUS: DONE

**Acceptance**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest tests/unit/apps_rg/test_x1d_judge_transport_parity.py tests/unit/apps_rg/test_executive_summary_x1d_judge_contract.py -q
python ops_scripts/ci/check_section_x2_x1d_drift.py
```
- Transport + coherence tests PASS
- Live Brown optional smoke documented in receipt (not sole W2 gate)

---

## Wave 3 — Governance, CI, Documentation

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D
WAVE_COMPLETE: plan=core-judge-panel-harness-f3c8d1 wave=3 note="GOV-JPH + drift invokes panel boundary + docs"

**Phases**:
- **W3.0** — `check_judge_panel_harness_boundary.py` (GOV-JPH) | ~20K | PHASE_STATUS: DONE
- **W3.1** — Core preflight wrappers in `x1d_judge_transport_contract.py` | ~15K | PHASE_STATUS: DONE
- **W3.2** — `AGENTS.md` + `docs/cursor/judge_panel_vs_llm_gateway.md` | ~15K | PHASE_STATUS: DONE

**Acceptance**:
- Boundary audit subagent or script reports no app leakage in panel package
- Plan cross-link from `exec-summary-x1d-transport-parity` notes core harness as long-term SSOT

---

## Gap Register

**GAP-1: Dual judge stacks during migration**
- `LLMJudgeGateway` (profile-based) vs `JudgePanelRunner` (contract-based) coexist until unified profile refs land.
- Mitigation: document when to use each; W3 docs only, no forced merge.

**GAP-2: apps_rg transport parity plan overlap**
- Risk of implementing same fix twice (apps-only vs core).
- Mitigation: W0.2 sequencing — apps plan remediates; core plan extracts harness.

**GAP-3: Author-Gate receipt** — **RESOLVED**
- `author_gate_receipt_ref`: `artifacts/governance/migration_receipts/20260524_core_judge_panel_harness.json`

---

## Definition of Done

DoD-1: Core panel package exists with frozen public API and unit tests
- Evidence: `pytest tests/unit/agentic_core/runtime/judges/panel/ -q` → 0 failed
- Status: DONE

DoD-2: Core smoke import (executable surface)
- Evidence: `python -c "from agentic_core.runtime.judges.panel import JudgePanelRunner, CanonicalJudgeContract"` exits 0
- Status: DONE

DoD-3: apps_rg `run_llm_judges` delegates to core panel with three adapters registered
- Evidence: `pytest tests/unit/apps_rg/test_x1d_judge_transport_parity.py -q` → 0 failed (after transport-parity prerequisites)
- Status: DONE

DoD-4: Boundary migration receipt + Author-Gate on disk
- Evidence: `artifacts/governance/migration_receipts/*_core_judge_panel*.json` exists; plan frontmatter `author_gate_receipt_ref` set
- Status: DONE

DoD-5: CI governance green for core addition
- Evidence: `python ops_scripts/ci/check_judge_panel_harness_boundary.py` → PASS (GOV-JPH in run_contract_gates)
- Status: DONE

### Verification vs Deferral

| Item | Verify in this plan | Deferred |
|------|---------------------|----------|
| Core harness API + tests | W1 | — |
| apps_rg rubric/packet text fixes | — | `exec-summary-x1d-transport-parity-d8f2a1` |
| Live Brown 3/3 CERTIFIED proof | W2 optional smoke | operator-ship plan |
| apps_lic second consumer | — | future plan |
| Exit-eval judge unification | — | separate ADR |

---

## Marker Quick Reference

```
WAVE_START: plan=core-judge-panel-harness-f3c8d1 wave=<N>
WAVE_COMPLETE: plan=core-judge-panel-harness-f3c8d1 wave=<N> note="+N tests, N files, scope=panel-harness"
PLAN_COMPLETE: plan=core-judge-panel-harness-f3c8d1 note="core panel harness + apps_rg migration"
```
