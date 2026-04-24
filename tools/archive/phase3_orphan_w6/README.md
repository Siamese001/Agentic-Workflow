# phase3_auto_remediation — archived 2026-04-24

## Why archived

Orphaned module (zero callers anywhere in the repo) that proposed auto-narrowing
`except Exception` → `except ValueError`. Never wired into any pipeline,
workflow, hook, or CI gate.

## Why it will not be revived

Session-RCA on 2026-04-24 concluded auto-P0-fix is unsafe:

1. **P0 classes are semantic, not mechanical.** Every P0 gate
   (`infra_wiring`, `write_sovereignty`, `capability_egress`,
   `critical_path_integrity`, `authority_boundary`, `dynamic_exec`) requires a
   design decision — adapter choice, tenant context, policy routing — that a
   mechanical rewriter cannot make.
2. **Empirical false-positive rate ~87%.** Evidence from
   `docs/reports/plans/p1-guardian-burndown-final-04202026.md`: 87 sites
   reviewed, only 11 (12.6%) were real bugs. 76 (87.4%) were doctrinally-valid
   best-effort patterns an auto-fixer would have corrupted.
3. **Violates constitutional §23** (ADG canonical invariants): "The ADG wins
   conflicts. Fix the graph, not your analysis." Auto-fix makes nodes lie.
4. **Violates constitutional §6 / §8** (Author-Gate for ambiguous decisions,
   guardian exemptions). Every non-trivial P0 fix has a decision. An
   auto-fixer either skips Author-Gate (violation) or prompts for every fix
   (no throughput gain over manual).

## Canonical P0 remediation path

`tools/adg/core/p0_wave_plan.py` emits a read-only ranked markdown plan at
`artifacts/adg/issues/p0_remediation_wave_plan_<ts>.md`. Humans read the plan,
apply targeted fixes, rerun `python tools/generate_full_adg.py`.

See `.windsurf/workflows/adg-repair-loop.md` §P0 Remediation.

## Self-violations in the orphan

Per `tools/archive/orphan_hooks_w5.3/burndown_budget.json`, the orphan module
itself contained `silent_swallower: 2` — exactly the kind of antipattern it
claimed to fix.

## Do not revive without

1. Author-Gate approval covering constitutional §6, §8, §23.
2. A classification of which P1 kinds (not P0 — P0 is permanently off-limits)
   are genuinely mechanical (e.g. pure token rewriter for
   `_GUARDIAN_MAP` mismatches).
3. A dry-run harness that proves ≥95% precision against a human-labeled
   gold set of ≥100 sites.
