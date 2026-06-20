<!-- Trigger: model_decision (load when about to orchestrate sub-agents / workflows).
     The invariant is mirrored always-on in AGENTS.md § Agent fan-out restraint. -->

# Agent / Workflow Fan-Out Restraint — Don't Re-Discover What the Plan Provides

> ✅ **Multiple workflows / agents are welcome.** Parallel fan-out is a tool, and effort tier
> (`max`, `ultracode`, `/code-review … ultra`) raises **depth and rigor**, not a ceiling on
> agent **count**. Spin up as many as the work genuinely benefits from.
>
> ⛔ The **one** restraint: don't spend that fan-out **re-running discovery a plan (or prior
> results) already provides**. When the facts are already established — by a detailed plan or
> earlier results — **execute and produce the outputs**, don't re-inventory the codebase
> through agents. (Sub-agent fan-out can cost large token volumes, so redundant rediscovery is
> the expensive mistake; legitimate parallel work is not.)

## When this fires

Any time you are about to call `Workflow`, `Agent`, or `Task` **and the fan-out's work would be
discovery / inventory a plan or prior results already cover** — that is the one shape to avoid.
Fanning out many agents for *independent* work (under `ultracode`, a high `/code-review` tier,
or any effort) is fine; rediscovery is the thing to catch, at any agent count.

## Good reasons to fan out (use freely)

| Justified | Why |
|---|---|
| Independent, parallelizable subtasks | Real wall-clock / comprehensiveness win one context can't get |
| Scale beyond one context | Migration / audit / sweep too large to hold inline |
| Adversarial / independent verification | High-stakes findings need a skeptic, not an echo |
| Breadth sweep where you only need the conclusion | `Explore`-style fan-out that returns the answer, not file dumps |

## Do NOT fan out to…

| Anti-pattern | Do instead |
|---|---|
| Re-discover / re-map a codebase already understood | Use the ADG, the existing map, or prior-turn results |
| Re-run inventory/discovery a **detailed plan already provides** | Execute the plan; produce the outputs |
| "Look thorough" because the effort tier is high | Raise rigor inline; **depth ≠ agent count** |
| A single-fact lookup you could do directly | Read the file / run the one query yourself |
| Sequential, coherent authoring with no independent parts | Do it inline (this very rule was authored that way) |

## Effort tiers ≠ agent count

`max` / `ultracode` / `ultra` change **how well**, not a ceiling on **how many**. Use as many
agents as the task genuinely benefits from — count is not the thing to minimise. What a detailed
plan in hand *does* change: discovery is already done, so spend the fan-out on **execution +
verification of the outputs**, not on rediscovery. The Workflow contract frames it the same —
"**Scale to what the user asked for**."

## Enforcement

- **Doctrine (primary lever):** this rule + the always-on summary in `AGENTS.md` shape the
  decision at the point of orchestration. This is what actually governs the choice.
- **Deterministic backstop:** `.codex/hooks/pre_workflow_fanout_gate.py` (PreToolUse on
  `Workflow`) inspects the inline script and surfaces a confirm **only on the pure-rediscovery
  shape** — discovery/inventory-dominant **AND no plan-execution or output intent**. **Decoupled
  from agent count by design**: a large parallel fan-out never fires on scale alone, and a
  discovery-shaped fan-out that *also* executes a plan / produces outputs passes untouched (the
  execution-intent escape valve). Verification, migration, parallel-implementation, judge-panel,
  and `scriptPath`/named re-runs are never flagged. Logs to
  `artifacts/governance/agent_fanout_restraint.jsonl`.
- **Modes:** `FANOUT_RESTRAINT_ENFORCE=ask|warn|block` (default `ask`). **Bypass:**
  `FANOUT_RESTRAINT_BYPASS=1` (scripted/batch runs, or a fan-out you have already justified).
- `Agent` / `Task` restraint is **doctrine-enforced** (model-read); `Workflow` (the mass-fan-out
  surface where most token burn concentrates) is **also hook-backstopped**.

## References

- `.codex/rules/001-runtime-seam-execution.md` — bounded L2 executor; avoid multi-wave unless explicitly asked
- `.codex/rules/scope-containment.md` — retrieval budgets; no gold-plating; one task at a time
- `.codex/rules/work-item-classification.md` — tier-aware Fix / File / Plan; `PLAN_MICRO` = native plan mode only
- Workflow tool contract — opt-in only; scale to the ask; pipeline/parallel patterns are tools, not defaults
