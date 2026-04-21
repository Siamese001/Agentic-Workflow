# Runtime Author-Gate Exit Control (v30 Step [5])

**Plan ID:** `runtime-hitl-exit-control-c4e7b3`
**Type:** T3 (net-new subsystem, cross-layer)
**Status:** W0 DELIVERED (DRAFT) — ADR-023 + L3↔L5 contract drafted 2026-04-21; awaiting reviewer sign-off before W1

**W0 Deliverables (complete, pending acceptance):**
- `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md` — ADR (PROPOSED status)
- `docs/contracts/L5_exit_control_hitl.md` — L3↔L5 contract (DRAFT, v1.0.0-draft)
- Notion ADR Registry row: **DEFERRED** — integration lacks access to DB `e59d7640-dc09-48f9-8bdc-b0c94bf98c2a`. Share database with `Agentic-Workflow` integration, then POST row.

**W0 Gap Resolutions (recorded in ADR §7):**
- G1 state store → SQLite file (v1), migrate to Postgres for multi-tenant
- G2 Notion DB → separate `Runtime Author-Gate Decisions` DB (not reuse developer Author-Gate Ledger)
- G3 novelty detection → reuse `system_learning/confidence/engine.py`
- G4 timeout defaults → financial=3600s, safety=1800s, regulated=7200s, novel_context=900s, low_confidence=600s, policy_override=86400s
- G5 guardrail interaction → serial (guardrail pre-seal, exit-control post-seal); no double-gating
- G6 OTel long-suspend → decouple: four discrete event spans
- G7 L3 RunState serialization → W2 audit pre-req (deferred; may expand W2.1 budget)
- G8 UWG authority → authoritative; shadow consumer produces drafts only
**Depends on:** `@docs/reference/agentic_process_mapping_v30.md` step [5]; L5 safety plane
**Siblings:** `harness-enforcement-rename-a8f21c.md` (distinct concern, do not merge)

---

## Context & Motivation

`@docs/reference/agentic_process_mapping_v30.md` step [5] defines three runtime exit-control
branches after a sealed L2 artifact arrives: **DENY / REROUTE**, **ESCALATE (Author-Gate)**,
**COMMIT REQUEST** → Universal Write Gate → L4.

Today, the repo's governed runners (`apps_*/integrations/governed_*_run.py`,
`apps_*/engines/*_engine.py`) implement DENY and COMMIT paths but do **not** implement the
ESCALATE (Author-Gate) branch. Step [5] is partially built — specifically its human-review branch
is missing.

This plan scopes the construction of that missing branch. It is:

- **Not** an IDE or developer-side concern — lives entirely in `agentic_core/`, `apps_*/`,
  `system_learning/`, and external approval surfaces (Notion/Slack/Orkes/Jira).
- **Not** the harness-enforcement work (that's `harness-enforcement-rename-a8f21c.md`).
- **Cross-cutting under L5 policy plane** — L5 is the Safety Officer per v30 and owns
  escalation authority.

---

## Scope Boundary

| In scope | Out of scope |
|----------|--------------|
| Runtime exit-control escalation (step [5] ESCALATE) | Any `.windsurf/` rule/skill/workflow (harness-only) |
| L5 policy plane integration for escalation classification | Retraining or fine-tuning (step [6] concern) |
| External approval adapter (pluggable: Notion, Slack, Orkes HUMAN task, PagerDuty) | Generic notification infra |
| OTel emission of Author-Gate spans (`otel_mcp` ingests) | OTel server internals |
| Persistent runtime Author-Gate ledger (bound to `run_id` / `trace_id`) | Local developer ledger (`decision_ledger.db` — harness scope) |
| Shadow-eval consumption of Author-Gate outcomes → system_learning → [6] promotion via UWG | Direct rule/prompt rewrites (UWG-mediated only) |
| Unit + integration tests in `tests/apps/*/exit_control/` + `tests/agentic_core/L5_safety/` | IDE-side Author-Gate tests |

---

## Architecture Skeleton

```
                                  [5] LIVE RUNTIME EXIT CONTROL
                           (v30 canonical: post-L2 sealed artifact)
                                              │
                                              ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ exit_controller.classify_exit(sealed_folder, policy_snapshot)       │
    │   → EXIT_DECISION ∈ { DENY, ESCALATE_HITL, COMMIT }                 │
    └─────────────────────────────────────────────────────────────────────┘
                                              │
                      ┌───────────────────────┼─────────────────────────┐
                      ▼                       ▼                         ▼
             ┌─────────────────┐   ┌────────────────────┐    ┌───────────────────┐
             │ DENY / REROUTE  │   │ ESCALATE (Author-Gate)    │    │ COMMIT REQUEST    │
             │ existing        │   │  (NEW — THIS PLAN) │    │ existing → UWG    │
             └─────────────────┘   └─────────┬──────────┘    └───────────────────┘
                                             │
                                             ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ L5 Policy Plane:                                                    │
    │   classify_escalation_class(envelope, policy_snapshot)              │
    │     → { financial, safety, regulated, novel_context, low_conf, ... }│
    │   resolve_approver_pool(class, tenant, time_of_day) → [approver_id] │
    │   set_timeout(class) → seconds; set_fallback(class) → default-deny  │
    └──────────────────────────────────────┬──────────────────────────────┘
                                           │
                                           ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ human_approval_adapter (pluggable):                                 │
    │   enqueue(run_id, trace_id, envelope, class, approver_pool, timeout)│
    │     adapter ∈ { notion_db, slack_interactive, orkes_human_task,     │
    │                 jira_approval, pagerduty_incident, email_magic_link}│
    │   returns: pending_handle                                           │
    └──────────────────────────────────────┬──────────────────────────────┘
                                           │
                                           ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ suspend_run(run_id)    # run paused; NOT the IDE, the production run│
    │   persist RunState to runtime_hitl_ledger                           │
    │   emit OTel span: hitl.escalate (class, approver_pool, timeout)     │
    └──────────────────────────────────────┬──────────────────────────────┘
                                           │
                           ┌───────────────┴────────────────┐
                           │                                │
                           ▼                                ▼
            ┌──────────────────────────┐       ┌──────────────────────────┐
            │ approved(approver_id,    │       │ timeout / denied         │
            │   rationale?)            │       │   apply_fallback(class)  │
            └────────────┬─────────────┘       └────────────┬─────────────┘
                         │                                  │
                         ▼                                  ▼
            ┌──────────────────────────┐       ┌──────────────────────────┐
            │ route → UWG → L4         │       │ route → DENY / REROUTE   │
            │ emit hitl.approved       │       │ emit hitl.denied/.timeout│
            └────────────┬─────────────┘       └────────────┬─────────────┘
                         │                                  │
                         └─────────────────┬────────────────┘
                                           │
                                           ▼
                            [6] SHADOW EVAL + SYSTEM LEARNING
                            (outcomes feed UWG-mediated rule
                             and policy updates — not in this plan)
```

---

## File Map (Target Layout)

| Path | Purpose |
|------|---------|
| `agentic_core/L5_safety/exit_control/__init__.py` | Module init |
| `agentic_core/L5_safety/exit_control/hitl_policy.py` | `classify_escalation_class`, `resolve_approver_pool`, `set_timeout`, `set_fallback` |
| `agentic_core/L5_safety/exit_control/hitl_classes.py` | Enumerated classes: `financial`, `safety`, `regulated`, `novel_context`, `low_confidence`, `policy_override` |
| `agentic_core/L5_safety/adapters/human_approval_adapter.py` | Abstract base: `enqueue`, `poll`, `cancel` |
| `agentic_core/L5_safety/adapters/notion_approval_adapter.py` | Notion DB implementation |
| `agentic_core/L5_safety/adapters/slack_approval_adapter.py` | Slack interactive message |
| `agentic_core/L5_safety/adapters/orkes_approval_adapter.py` | Orkes HUMAN task |
| `agentic_core/L5_safety/adapters/email_magic_link_adapter.py` | Stateless magic-link fallback |
| `agentic_core/L3_orchestration/exit_control/exit_controller.py` | Orchestrator-side dispatch: DENY \| ESCALATE_HITL \| COMMIT |
| `agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py` | Persistent state store bound to `run_id`/`trace_id` |
| `apps_*/integrations/governed_*_run.py` | Modified — call `exit_controller.classify_exit` before UWG |
| `config/runtime_hitl_policy.yaml` | Classes, thresholds, approvers, timeouts, fallbacks |
| `system_learning/runtime_hitl_consumer.py` | Ingests outcomes → candidate rule/prompt drafts for UWG review |
| `tools/otel/otel_mcp_server.py` | **NO CHANGE** — already supports ingest via `otel_ingest_to_runtime_adg` |
| `tests/agentic_core/L5_safety/test_hitl_policy.py` | Classification, routing, fallback |
| `tests/agentic_core/L5_safety/adapters/test_*_adapter.py` | Per-adapter contract tests |
| `tests/apps/*/exit_control/test_hitl_escalation.py` | End-to-end escalation in each app |
| `tests/apps/*/exit_control/test_hitl_timeout_fallback.py` | Timeout + default-deny paths |
| `apps_eval/engines/hitl_decision_quality_engine.py` | New eval dimension: Author-Gate decision quality scoring |
| `docs/architecture/adr/ADR-NNN-runtime-hitl-exit-control.md` | ADR — approach, tradeoffs, compliance mapping |
| `docs/architecture/architecture/runtime_hitl_architecture.md` | Full architecture reference |
| `docs/contracts/L5_exit_control_hitl.md` | L3↔L5 contract (peer of `guardian_to_L6.md`) |

---

## Wave Structure (Skeleton — Detailed Decomposition Required Before Execution)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-------------------|
| W0 | P0.1–P0.2 | ADR + architecture doc + contract | ~12k | ADR process via `docs/architecture/adr/` | TODO | ADR accepted; contract reviewed by L3 + L5 owners |
| W1 | P1.1–P1.3 | Policy classifier + class/timeout/fallback tables | ~20k | Policy YAML SSOT; no tenancy first | TODO | `classify_escalation_class` unit tests green; 100% coverage |
| W2 | P2.1–P2.3 | `exit_controller` + runtime ledger + OTel spans | ~25k | Runtime ADG store available (`runtime_adg_store`) | TODO | Escalate path emits 3 OTel spans (escalate/approved/denied-or-timeout); ledger round-trip |
| W3 | P3.1–P3.4 | First adapter (Notion — already configured) + contract tests | ~25k | `mcp6_notion` tool authority stable; Author-Gate Ledger DB exists | TODO | E2E: governed run → escalate → Notion row → approve → UWG commit; timeout path default-deny |
| W4 | P4.1–P4.3 | Additional adapters (Slack, Orkes, email magic link) | ~30k | External credentials provisioned | TODO | Three adapters pass contract tests; adapter swap requires zero exit-controller change |
| W5 | P5.1–P5.2 | App integration — `apps_lic`, `apps_underwriting_ai`, `apps_exec` governed runners | ~25k | Each app's sealed-folder shape stable | TODO | Each app emits `hitl.escalate` in expected scenarios; regression-free on non-escalate paths |
| W6 | P6.1–P6.3 | Eval engine + shadow-eval consumption | ~20k | `apps_eval` engine extension surface stable; [6] UWG path exists | TODO | Author-Gate decision quality dimension scored nightly; UWG receives rule drafts |
| W7 | P7.1–P7.2 | Compliance hardening — hash-chain, policy-snapshot binding, SOC2 mapping | ~15k | ed25519 signing key available in prod | TODO | `check_runtime_hitl_ledger_integrity.py` green; SOC2 mapping doc accepted |

Total est: ~172k — **exceeds T3 single-plan ceiling; must be decomposed** via
`decompose_task` before execution. W1, W3, W5 are hot candidates for further split.

**Token estimator status:** DIRECTLY OBSERVED (2026-04-21) at plan level.
Budget SSOT: `python tools/utils/planning/token_estimator.py --budget`
→ `{HARD_MAX_CONTEXT: 262000, SAFE_OPERATING_CAP: 223000, WARNING_THRESHOLD: 197000}`.
Per-wave estimates (12–30k) all 🟢 GREEN individually. Total 172k ≈ 87% of warning
threshold → plan-level 🟡 YELLOW — must `decompose_task` (W3/W5 most likely split points)
before execution.

**BLOCKER for execution:** ADR-023 (W0) must be accepted first.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|----------------|-------------|-------------|--------|
| P0.1 | ADR draft | `docs/architecture/adr/ADR-NNN-runtime-hitl-exit-control.md` | Approach, adapters, fallback semantics, SOC2 | 6k | TODO |
| P0.2 | Architecture + contract | `runtime_hitl_architecture.md`, `L5_exit_control_hitl.md` | L3↔L5 boundary, OTel span contract | 6k | TODO |
| P1.1 | Policy classes | `hitl_classes.py`, `runtime_hitl_policy.yaml` | Class catalog stable across apps | 6k | TODO |
| P1.2 | Classifier | `hitl_policy.py` | Novel-context detection threshold | 8k | TODO |
| P1.3 | Tests | `tests/agentic_core/L5_safety/test_hitl_policy.py` | 100% coverage required at L5 | 6k | TODO |
| P2.1 | Exit controller | `exit_controller.py` | Idempotency on resume | 9k | TODO |
| P2.2 | Runtime ledger | `runtime_hitl_ledger.py` | State store choice (SQLite vs Postgres vs existing) | 9k | TODO |
| P2.3 | OTel spans | Span schema + `otel_mcp` ingest test | Span attribute SSOT | 7k | TODO |
| P3.1 | Adapter base | `human_approval_adapter.py` abstract | Timeout + cancel semantics | 6k | TODO |
| P3.2 | Notion adapter | `notion_approval_adapter.py` + Notion DB schema | Maps to Author-Gate Decision Ledger DB already present | 8k | TODO |
| P3.3 | Contract tests | `test_*_adapter.py` | Hermetic contract for all adapters | 6k | TODO |
| P3.4 | E2E | `test_hitl_escalation.py` in one app | First app integration | 5k | TODO |
| P4.1 | Slack | `slack_approval_adapter.py` | Interactive message auth; bot creds | 10k | TODO |
| P4.2 | Orkes | `orkes_approval_adapter.py` | HUMAN task integration | 10k | TODO |
| P4.3 | Email magic link | `email_magic_link_adapter.py` | Signed link + stateless validate | 10k | TODO |
| P5.1 | apps_lic | `governed_lic_run.py` integration | Licensing has multiple exit points | 10k | TODO |
| P5.2 | apps_underwriting_ai | `governed_*_run.py` integration | Covenant exception path | 8k | TODO |
| P5.3 | apps_exec | `governed_exec_run.py` integration | External action gating | 7k | TODO |
| P6.1 | Eval dimension | `hitl_decision_quality_engine.py` | Ground truth for Author-Gate quality | 8k | TODO |
| P6.2 | Shadow consumer | `runtime_hitl_consumer.py` | Draft → UWG review, never direct write | 7k | TODO |
| P6.3 | Promotion path | `system_learning/` rule/prompt draft generator | Must use UWG, not direct writes | 5k | TODO |
| P7.1 | Integrity | Hash chain + signing for `runtime_hitl_ledger` | Key mgmt | 8k | TODO |
| P7.2 | Compliance | SOC2 mapping doc + audit log retention | Retention policy | 7k | TODO |

---

## Gap Register (Open Questions)

| # | Gap | Impact | Proposed Resolution |
|---|-----|--------|---------------------|
| G1 | Which state store for `runtime_hitl_ledger`? Local SQLite (like harness), Postgres, or reuse an existing production DB? | Affects W2 entirely | Author-Gate packet during ADR |
| G2 | Notion Author-Gate Decision Ledger DB (`5b60fdde-7259-491e-9f2d-e088f1f741ef`) already exists for developer Author-Gate. Do we reuse it or create a separate DB for runtime Author-Gate? | Reuse risks conflating two loops | Author-Gate packet — recommend separate DB |
| G3 | Novel-context detection — is there an embedding-based novelty score already? | Classifier accuracy | Check `system_learning/confidence/` + `vector_db` |
| G4 | Timeout defaults per class — who owns these? | Compliance baseline | L5 policy owner + product + legal |
| G5 | How does this interact with the existing `execution_guardrail_chokepoint` / guardian-exemption paths? | Potential double-gating | Architecture doc P0.2 must clarify |
| G6 | Are `otel_mcp` runtime ADG ingest semantics stable under prolonged suspend? | Long-running escalations | Verify with `otel_ingest_to_runtime_adg` + suspended-run simulation |
| G7 | RunState serialization during pause — does the existing L3 orchestrator support it? | Resume correctness | Audit L3 orchestrator for serialization surface |
| G8 | UWG commit authority on shadow-eval-generated rule drafts from runtime Author-Gate | Closes learning loop | ADR must define — peer of existing `system_learning/` pathways |

---

## Success Criteria (plan-level — all require W0 ADR accepted)

- [ ] Step [5] ESCALATE branch implemented, not stubbed
- [ ] L5 policy plane is the sole authority for escalation classification (no app-local policy)
- [ ] At least 2 adapters (Notion + one other) pass contract tests; adapter-agnostic controller
- [ ] OTel spans `hitl.escalate`, `hitl.approved`, `hitl.denied`, `hitl.timeout` emitted with
      mandatory attributes: `run_id`, `trace_id`, `class`, `approver_id?`, `latency_ms`, `outcome`
- [ ] Timeout with default-deny proven in E2E test
- [ ] Runtime Author-Gate ledger distinct from developer `decision_ledger.db` (no schema coupling)
- [ ] Ledger hash-chain integrity verifiable by CI
- [ ] Shadow-eval consumer produces rule/prompt drafts; zero direct writes (all via UWG)
- [ ] SOC2 / compliance mapping doc accepted by reviewer
- [ ] No developer-loop artifacts touched (`.windsurf/` unchanged by this plan — enforced by
      CI: paths under `.windsurf/` must not appear in this plan's commits)

---

## Explicit Non-Goals

- ❌ Any file under `.windsurf/` — that belongs to `harness-enforcement-rename-a8f21c.md`
- ❌ Modifying `decision_ledger.db` schema (developer-side)
- ❌ Changing Cascade behavior, rules, skills, or hooks
- ❌ Replacing DENY or COMMIT paths (they exist; only ESCALATE is missing)
- ❌ Direct writes to L4 outside UWG
- ❌ Direct rule or prompt mutation from runtime outcomes (all changes flow [6] → UWG → L4)

---

## Rollback

Each wave is behind a feature flag (`RUNTIME_HITL_ENABLED=false` default). Rollback = flip
flag; ESCALATE branch returns to previous behavior (= COMMIT with current policy). Per-app
integration (W5) also feature-flagged per app. No destructive migrations until W7.

---

## Open Decisions Requiring Author-Gate (meta-note)

This plan's own execution will generate `architecture_choice` decisions that should flow
through the **harness** Author-Gate system once that exists. That's expected and fine — the two
systems compose. No circular dependency.
