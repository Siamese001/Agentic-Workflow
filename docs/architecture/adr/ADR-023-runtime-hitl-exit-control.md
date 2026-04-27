# ADR-023 — Runtime HITL Exit Control (v30 Step [5] ESCALATE Branch)

> 🔔 **REVIEW REQUESTED — 2026-04-21.** This ADR is blocking the entire runtime
> HITL subsystem (W1–W7 of `runtime-hitl-exit-control-c4e7b3.md`, ~140k tokens
> of downstream work). Sign-off tracker: **`ADR-023-review-request.md`** in the
> same directory. Target decision date: **2026-04-28** (one week review window).

- **Status:** PROPOSED — AWAITING REVIEW
- **Date:** 2026-04-21
- **Target decision date:** 2026-04-28
- **Deciders:** L3 orchestration owner, L5 safety owner, compliance reviewer
- **Supersedes:** none
- **Superseded by:** none
- **Related plan:** `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md`
- **Related sibling plan (distinct concern):** `.windsurf/plans/harness-enforcement-rename-a8f21c.md`
- **Related contract:** `docs/contracts/L5_exit_control_hitl.md` (P0.2 deliverable)
- **Impact layers:** L3 orchestration, L5 safety, L6 observability, apps_*

---

## 1. Context

The canonical agentic process map (`docs/reference/_notes/agentic_process_mapping_v34.md`) step [5]
"LIVE RUNTIME EXIT CONTROL + CURRENT-RUN EVALUATION" defines three mutually exclusive
dispositions after a sealed L2 artifact arrives:

- **DENY / REROUTE** — reject or rework
- **ESCALATE (HITL)** — human review gate
- **COMMIT REQUEST** — route to Universal Write Gate → L4

Audit of the current runtime path (governed runners in `apps_*/integrations/governed_*_run.py`
+ engines in `apps_*/engines/*_engine.py`) shows DENY and COMMIT branches are implemented.
**The ESCALATE (HITL) branch is not implemented.** Step [5] is partially built; its
human-review branch is a doctrinal requirement without a code surface.

This ADR selects the architecture for the missing branch and binds it to the L5 policy plane
(Safety Officer) per v30 cross-cutting authority.

### 1.1 What this is not

This ADR **is not** about developer-loop / IDE-side approval of Cascade code changes. That
concern — previously mislabeled "HITL" in `.windsurf/` — is harness enforcement in the
Fowler taxonomy and is governed by the sibling plan. The two systems share a schema pattern
(candidates, scores, approval, outcome, integrity) but must not share a schema, a table, a
ledger, or an approver pool.

---

## 2. Forces

| Force | Weight |
|-------|--------|
| v30 doctrinal completeness — step [5] ESCALATE must exist | high |
| Compliance — SOC2 / regulated-industry audit requires approver binding and immutable evidence | high |
| Operational velocity — must not block non-escalate paths (DENY/COMMIT unchanged) | high |
| Adapter heterogeneity — organizations use Notion, Slack, Orkes, Jira, PagerDuty, email | medium |
| Timeout safety — escalation must have bounded latency + default fallback | high |
| Shadow-eval learning loop — outcomes must flow through step [6] via UWG, never direct writes | constitutional |
| No coupling to developer harness ledger | high |

---

## 3. Decision

### 3.1 Authority

**L5 Policy Plane owns escalation classification, approver-pool resolution, timeout, and
fallback.** L3 orchestration owns dispatch mechanics. Apps own business-level trigger
signals but never escalation policy.

### 3.2 Dispatch point

`exit_controller.classify_exit(sealed_folder, policy_snapshot) → {DENY, ESCALATE_HITL, COMMIT}`
is the single runtime decision primitive for step [5]. Each governed runner must call it
immediately after sealing (E5) and before any UWG invocation.

### 3.3 Pluggable approval adapter

Introduce `HumanApprovalAdapter` abstract base with one concrete adapter per approval surface
(Notion, Slack, Orkes HUMAN task, email magic link). L5 `hitl_policy.resolve_approver_pool`
returns the concrete adapter binding per escalation class.

### 3.4 Suspension semantics

On ESCALATE_HITL: the **production run** is suspended (not Cascade, not the orchestrator
process — the specific run keyed by `run_id` / `trace_id`). State is persisted to
`runtime_hitl_ledger`. Resume is event-driven from adapter callback or scheduled timeout.

### 3.5 Timeout + fallback

Every escalation has a per-class timeout. On timeout, the class-defined fallback applies —
**default is DENY** (fail-closed). Classes may declare `fallback=ESCALATE_TO_POOL_B` for
secondary approver routing before the final DENY.

### 3.6 Observability

Four mandatory OTel span kinds:

| Span name | Emitted when | Required attributes |
|-----------|--------------|---------------------|
| `hitl.escalate` | On ESCALATE_HITL dispatch | `run_id`, `trace_id`, `class`, `approver_pool`, `timeout_s`, `policy_snapshot` |
| `hitl.approved` | On human approval | `run_id`, `trace_id`, `approver_id`, `latency_ms`, `rationale_len` |
| `hitl.denied` | On explicit human denial | `run_id`, `trace_id`, `approver_id`, `latency_ms`, `reason_code` |
| `hitl.timeout` | On timeout expiration | `run_id`, `trace_id`, `timeout_s`, `fallback_taken` |

Spans ingested by `otel_mcp` via existing `otel_ingest_to_runtime_adg`. No changes to
OTel server internals.

### 3.7 Ledger

`runtime_hitl_ledger` is a **distinct** persistence surface from the developer-loop
`decision_ledger.db`. Canonical record schema follows the pattern in
`docs/guides/AuthorGate_Decision_Schema.md` (W7 of harness plan) but is bound to
`run_id`/`trace_id` and includes `policy_snapshot`, hash-chain integrity, and optional
ed25519 signature.

### 3.8 Learning loop

Shadow-eval (`system_learning/runtime_hitl_consumer.py`) consumes completed HITL records
and emits **drafts** (rule/prompt/config candidates) to the step [6] promotion path.
All writes to L4 flow through UWG. Zero direct writes from the consumer.

---

## 4. Alternatives Considered

| Option | Verdict |
|--------|---------|
| **A. Fold HITL into guardrail chokepoint (`execution_guardrail_chokepoint`)** | ❌ Conflates safety enforcement with human review; violates v30 step [5] as distinct branch |
| **B. Per-app escalation policy (no central L5 authority)** | ❌ Violates v30 "L5 is cross-cutting authority"; audit fragmentation |
| **C. Single fixed adapter (Notion only)** | ❌ Blocks non-Notion tenants; fails principle of pluggable surface |
| **D. Synchronous blocking call (no suspend/resume)** | ❌ Timeout hazards; orchestrator resource exhaustion on long approvals |
| **E. Fold runtime HITL ledger into developer ledger** | ❌ Compliance violation; approver scope + retention policy differ; cross-contamination risk |
| **F. THIS ADR (L5-owned, pluggable, suspend-resume, per-run ledger)** | ✅ Chosen |

---

## 5. Consequences

### 5.1 Positive

- v30 step [5] doctrine becomes fully implemented
- L5 policy plane gains teeth in the runtime path (currently only advisory)
- Compliance/audit posture improves materially: policy snapshot + approver binding + hash chain
- Adapter pluggability decouples policy from integration choice
- Outcome learning loop closes (via UWG — no shortcuts)
- Developer loop is unaffected — clean separation

### 5.2 Negative

- Net-new L5 subsystem: ~20–25 new files across `agentic_core/L5_safety/` and
  `agentic_core/L3_orchestration/exit_control/`
- Approval adapter integrations require external credential provisioning per tenant
- Suspend/resume semantics require L3 orchestrator serialization surface audit (Gap G7)
- Training cost — approvers must understand escalation classes

### 5.3 Risks

| Risk | Mitigation |
|------|------------|
| Prompt-injection in sealed folder escapes into human-visible approval UI | Adapter must sanitize/escape envelope before rendering |
| Approver fatigue → rubber-stamp | Track `latency_ms`; flag < 5s approvals; calibration report |
| Timeout too aggressive → user-facing failures | Per-class calibration; initial defaults conservative |
| Ledger unavailability blocks runs | Ledger write is best-effort with local spool; escalation proceeds; shadow-reconciliation after |
| Coupling with existing guardrail paths | Contract (P0.2) enumerates non-overlap guarantees |
| Learning loop spoofed by bad outcomes | UWG reviews all drafts; no direct write path |

---

## 6. Compliance Mapping (SOC2 preview)

| Control | Mechanism |
|---------|-----------|
| CC6.1 — logical access | Approver pool resolution bound to identity provider |
| CC7.2 — anomaly detection | OTel spans + `hitl.timeout` alerts |
| CC7.3 — evaluate events | Shadow eval → step [6] rule drafts |
| CC8.1 — change authorization | UWG + approver binding + policy snapshot |
| CC9.2 — third-party | Per-adapter contract tests |

Full mapping deferred to W7 of the plan.

---

## 7. Resolutions to Plan Gaps

Each gap in `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md` §Gap Register, resolved
by this ADR:

| Gap | Resolution |
|-----|------------|
| G1 — state store choice | **SQLite file** (`artifacts/runtime/hitl_ledger.db`) for v1; migrate to Postgres when multi-tenant. Keeps ops simple per SVP priorities. |
| G2 — reuse Notion HITL DB vs separate | **Separate Notion DB** (new `Runtime HITL Decisions`). Existing `HITL Decision Ledger` DB (`5b60fdde-…`) is developer-loop; cross-contamination risk too high. |
| G3 — novel-context detection | **Reuse** `system_learning/confidence/engine.py` novelty scorer + `vector_db` similarity. No new embedding infra. |
| G4 — timeout defaults per class | **Conservative initial defaults:** `financial=3600s`, `safety=1800s`, `regulated=7200s`, `novel_context=900s`, `low_confidence=600s`, `policy_override=86400s`. Class owner = L5 policy YAML. |
| G5 — interaction with `execution_guardrail_chokepoint` | Guardrail runs **before** step [5] exit-control. If guardrail blocks, no escalation (fail-closed). If guardrail passes, exit-controller may still escalate. Not double-gating — serial. Contract doc formalizes. |
| G6 — OTel runtime ADG ingest on long suspend | **Decouple:** spans emitted on escalate, approve, deny, timeout — each is a discrete event. No streaming. Proven-stable pattern. |
| G7 — L3 orchestrator RunState serialization | **Required audit in W2**. If absent, suspend-resume must be implemented in W2.1 as pre-req; wave budget adjusted then. |
| G8 — UWG authority on draft rules/prompts | **UWG is authoritative.** Shadow consumer produces drafts with `status=proposed`; UWG reviewer accepts/rejects. Zero direct write. Mirrors existing `system_learning/` patterns. |

---

## 8. Non-Goals

- Changing DENY or COMMIT paths in step [5]
- Modifying developer-loop harness artifacts (any file under `.windsurf/`)
- Modifying OTel server internals
- Direct L4 writes outside UWG
- Retraining or fine-tuning (explicitly a step [6] concern)

---

## 9. Acceptance Criteria

This ADR is accepted when:

- [ ] L3 orchestration owner sign-off on suspend/resume semantics + exit-controller contract
- [ ] L5 safety owner sign-off on policy classification authority + timeout defaults
- [ ] Compliance reviewer sign-off on approver-binding + policy-snapshot + hash-chain design
- [ ] Gap G7 (L3 RunState serialization) resolved with concrete path forward
- [ ] Sibling contract doc `docs/contracts/L5_exit_control_hitl.md` drafted and reviewed
- [ ] Notion ADR Registry row created for this ADR (data_source_id: `e59d7640-dc09-48f9-8bdc-b0c94bf98c2a`)

---

## 10. References

- `docs/reference/_notes/agentic_process_mapping_v34.md` — canonical v30 map (step [5])
- `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md` — execution plan (waves W0–W7)
- `.windsurf/plans/harness-enforcement-rename-a8f21c.md` — sibling (distinct concern, do not merge)
- Fowler, M. "Humans and Agents in Software Engineering Loops" (2026-03) — taxonomy
- Anthropic "Claude Code auto mode" — classifier + deny-and-continue patterns (informs G5)
- LangGraph interrupt + checkpointer docs — suspend/resume inspiration
- OpenAI Agents SDK `needsApproval` + RunState versioning — adapter contract inspiration
- Cordum "AI Agent Audit Trails" — compliance schema basis
- ACM "Characteristically Auditable Agentic AI Systems" — integrity pattern basis
