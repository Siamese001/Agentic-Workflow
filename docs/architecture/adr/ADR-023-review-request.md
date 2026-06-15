# ADR-023 Review Request

**Status:** Closed (historical tracker)

> **Companion tracker** to `ADR-023-runtime-hitl-exit-control.md`. This file
> records the historical reviewer sign-off request. Current status:
> **closed 2026-06-15**; ADR-023 is accepted in the filesystem ADR record.

## Review window

- **Opened:** 2026-04-21
- **Target close:** 2026-04-28 (one-week SLA)
- **Closed:** 2026-06-15 status reconciliation
- **Escalation if no response by close:** owner of
  `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md` proceeds with a
  documented interim decision; final reviewer sign-off still required before
  W7 compliance hardening ships.

## Why this blocks

ADR-023 defines the contract between L3 orchestration and L5 safety for the
runtime HITL ESCALATE branch (v30 step [5]). Until it is accepted:

- W1 (policy classifier) cannot start — policy classes are defined in the ADR
- W2 (exit_controller) cannot start — controller API is defined in the ADR
- W3–W7 (adapters, app integration, compliance) all depend on W1+W2

Estimated unblock leverage: ~140k tokens of downstream engineering.

## Review checklist

Each reviewer: read `ADR-023-runtime-hitl-exit-control.md` end-to-end, confirm
or raise issues in the matching sections below.

### L3 orchestration owner

Focus: controller API shape, RunState serialization (G7), policy hook
placement, retry/escalation semantics.

- [ ] Section 2 (Decision) — controller contract is implementable
- [ ] Section 3 (Consequences) — failure modes acceptable
- [ ] Section 4 (Rejected alternatives) — none re-openable
- [ ] Gap G7 (RunState audit) — resolution path agreed
- [ ] **Sign-off:** `name`, `YYYY-MM-DD`, commit SHA: _________

### L5 safety owner

Focus: safety-plane policy hooks, policy snapshot immutability (G4), fallback
behavior when approval adapter is unreachable, exception-class invariants.

- [ ] Section 2 (Decision) — safety hooks preserve guardrail semantics
- [ ] Section 3 (Consequences) — no regression on existing L5 guarantees
- [ ] Gap G3 (novelty reuse) — policy classifier scope acceptable
- [ ] Gap G4 (policy snapshot) — immutability guarantees sufficient
- [ ] Gap G6 (fallback behavior) — default is fail-closed
- [ ] **Sign-off:** `name`, `YYYY-MM-DD`, commit SHA: _________

### Compliance reviewer

Focus: audit trail completeness, tamper-evidence, data retention, evidence
reproducibility for SOC2 CC8.1 / CC8.2.

- [ ] Runtime ledger design — write-ahead + append-only + hash-chain (can
  reuse `author_gate_ledger_integrity.py` pattern from harness W5)
- [ ] Gap G2 (approval ledger scope) — runtime vs harness separation clear
- [ ] Gap G5 (identity capture) — approver identity captured on every ESCALATE
- [ ] Retention policy defined
- [ ] **Sign-off:** `name`, `YYYY-MM-DD`, commit SHA: _________

## Outstanding questions

(Reviewers: add open questions here during review. Resolve before sign-off.)

1. _(open)_
2. _(open)_

## After acceptance

Closed actions:

1. `ADR-023-runtime-hitl-exit-control.md` status is `ACCEPTED`.
2. No Notion ADR Registry row is created. The ADR Registry database is archived;
   filesystem ADR files are the source of truth.
3. This tracker remains in place as a historical record.

## Reference

- ADR: `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
- Contract: `docs/contracts/L5_exit_control_hitl.md`
- Plan (blocked): `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md`
- Related (harness, distinct): `.windsurf/plans/harness-enforcement-rename-a8f21c.md`
- v30 source: `docs/reference/_notes/agentic_process_mapping_v34.md` §[5]
