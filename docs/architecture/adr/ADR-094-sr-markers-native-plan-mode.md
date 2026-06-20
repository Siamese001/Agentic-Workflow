# ADR-094 — SR_* reasoning markers superseded by native plan mode

- **Status:** Accepted
- **Date:** 2026-06-07
- **Plan:** [claude-native-supersession-9d3f7a](../../../plans/claude-native-supersession-9d3f7a.md) (Wave W2)

## Context

The structured-reasoning contract required emitting a five-marker packet —
`SR_INTAKE` / `SR_PLAN` / `SR_APPROVAL` / `SR_EXECUTE` / `SR_VERIFY` — to enforce "plan before edits,
no edits before approval" on T2/T3 work. This emulated **plan mode**, which the harness now provides
natively (`EnterPlanMode` / `ExitPlanMode`): the harness itself blocks edits until the plan is approved.

## Decision

- **Invariant kept:** T2/T3 ⇒ plan first, no edits before approval; retrieval discipline (local →
  exact → ADG → semantic → external) unchanged.
- **Retired:** the `SR_*` marker scheme. `AGENTS.md` "Plan First" now points at `EnterPlanMode` /
  `ExitPlanMode`; `plan-first-enforcement.md` reduced to a plan-mode stub that preserves the
  retrieval-discipline guidance; the `structured-reasoning` skill keeps its decomposition/retrieval
  content under a deprecation banner (used *inside* plan mode, not as a marker emitter).
- **Left dormant:** `pre_prompt_classifier.py` also hosts ADG step-0 classification, so it is **not**
  removed — only its SR-marker advisory path is now moot. Swept in W5 if fully unused.

## Consequences

- No marker grammar to emit/parse; the harness enforces the gate structurally.
- No CI gate enforced SR markers, so nothing to remove from `run_contract_gates.py` / pre-commit.
- Reversible: rule text restorable from git history; the skill is unchanged in substance.
