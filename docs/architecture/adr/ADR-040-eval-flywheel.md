# ADR-040 — Eval Flywheel: Trace → Dataset Promotion

- **Status:** Proposed
- **Date:** 2026-04-23
- **Deciders:** Eval Lab, Safety Officer (L5), Architecture
- **Impact Layers:** L6 shadow, apps_eval, v33 §6
- **Relates to:** ADR-028 (eval SL publisher), ADR-036 (trace-grader), ADR-037 (trajectory)

## 1. Context

OpenAI's agent-eval guidance explicitly names the flywheel: interesting runtime
traces → curated datasets → eval runs → prompt optimizer → deploy. v33 §6C
"RCA/SYNTH" mentions aggregating graded signals but there is no named bridge
that lifts sealed runtime traces into `data/eval/golden/` for repeatable
regression runs.

## 2. Decision

Declare a **flywheel promoter** owned by L6 (shadow lane, observer posture
only — never mutates live runtime) that identifies promotion-candidate
`EvalEvent` rows and writes them into the eval dataset tree.

### 2.1 Candidate signals

An `EvalEvent` is a promotion candidate when **any** of:

| Signal | Rationale |
|---|---|
| `exit_decision.disposition == escalate_hitl` | HITL escalations are high-signal failure modes |
| `exit_decision.disposition == deny_reroute` | Denial reasons belong in regression suite |
| `exit_decision.quality.verdict == fail` | Current-run failure → regression candidate |
| `exit_decision.safety.policy_violation == true` | Every safety breach becomes a permanent test |
| `replication.is_replicate == true AND replication.pass_rate_0_1 < 0.9` | Non-determinism hotspot |
| `trajectory.exact_match == 0 AND reference existed` | Trajectory regression candidate |
| Operator-tagged | Manual flag set on the run |

These signals are **OR'd** — any match flags the event. The `flywheel.promote_candidate`
field on the EvalEvent schema carries the result so downstream tooling is
deterministic.

### 2.2 Target dataset routing

| Candidate signal | Target dataset path |
|---|---|
| safety_violation | `data/eval/golden/safety/` |
| trajectory mismatch | `data/eval/golden/trajectory/` |
| groundedness fail | `data/eval/golden/rag/` |
| generic quality fail | `data/eval/golden/quality/` |
| other | `data/eval/golden/triage/` (awaiting routing) |

`flywheel.target_dataset` on the EvalEvent schema carries the target.

### 2.3 Curation gate (human-in-the-loop, not automated)

- The promoter **proposes** a scenario file; it does not directly commit to
  `data/eval/golden/`. It writes to a staging area
  (`data/eval/triage/<event_id>.json`) and opens a review packet.
- An operator reviews, refines, and promotes by moving the scenario into the
  target dataset directory.
- This matches v33 §6D "gated review" invariant — no automated promotion that
  bypasses human review.

### 2.4 Capability → regression graduation

Once a promoted scenario has shipped, it enters the **capability** suite with a
tracked pass-rate target (see `rubrics.yaml → eval_taxonomy.capability`). When
pass rate sustains above `min_pass_rate_target: 0.50` for N consecutive runs
(N configurable, default 10), the scenario **graduates** to the regression
suite with the higher threshold (`min_pass_rate_target: 0.98`). This is the
Anthropic capability→regression graduation pattern.

## 3. Consequences

- **Positive:** closes the OpenAI flywheel; makes regression coverage grow
  organically from real failures; safety breaches become permanent tests.
- **Negative:** triage queue needs human attention; without it, `data/eval/triage/`
  grows unbounded.
- **Risk:** dataset bloat. Mitigated by the human curation gate.

## 4. Alternatives Considered

- **Auto-promote candidates.** Rejected — violates v33 §6D gated-review invariant.
- **Dataset-only, no flywheel.** Rejected — OpenAI doc calls out the flywheel as
  core practice; absent it, datasets go stale.

## 5. Open Items

- Code execution plan: promoter script + triage staging wiring (blocked on
  this ADR + ADR-036 + ADR-037).
- Triage UI / CLI surface.
- Retention policy for `data/eval/triage/`.
