# ADR-023 Review Request

> **Companion tracker** to `ADR-023-runtime-hitl-exit-control.md`. This file
> records reviewer sign-off. When all three reviewers check off, flip the
> ADR status from `PROPOSED — AWAITING REVIEW` → `ACCEPTED` and unblock
> `runtime-hitl-exit-control-c4e7b3.md` W1+.

## Review window

- **Opened:** 2026-04-21
- **Target close:** 2026-04-28 (one-week SLA)
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

Once all three sign-offs complete:

1. Edit `ADR-023-runtime-hitl-exit-control.md` status → `ACCEPTED`
2. Write a Notion ADR Registry row: `API-post-page` into database_id
   `6ed25e12-bd92-4352-ac7a-3a971311f024` with:
   - ADR ID: `ADR-023`
   - Status: `Accepted`
   - Decision Date: `YYYY-MM-DD`
   - Impact Layers: `L3, L5, L6, apps`
   - Summary: (one-line from ADR Section 1)
   - Filename: `ADR-023-runtime-hitl-exit-control.md`
3. Unblock `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md` W1 (policy
   classifier) and W2 (exit_controller) — they may execute in parallel.
4. Leave this tracker file in place as a historical record (do not delete).

## Reference

- ADR: `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
- Contract: `docs/contracts/L5_exit_control_hitl.md`
- Plan (blocked): `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md`
- Related (harness, distinct): `.windsurf/plans/harness-enforcement-rename-a8f21c.md`
- v30 source: `docs/reference/_notes/agentic_process_mapping_v34.md` §[5]
