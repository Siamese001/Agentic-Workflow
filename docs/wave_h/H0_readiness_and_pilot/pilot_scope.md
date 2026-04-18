# H0 — Pilot Scope

wave: H0
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 1. Pilot objective

Validate that ADG-grounded, stability-labeled semantic cards improve runtime explainability and architecture Q&A for selected app workflows without introducing production dependency or unstable canonical claims.

## 2. Bounded pilot scope

### 2.1 Initial app use cases (1–2)

1. **APP-RESEARCH support use case** (`apps_research`)
   - Focus: architecture/runtime Q&A and dependency/path explanations for retrieval-heavy flows.
2. **APP-EXEC support use case** (`apps_exec`)
   - Focus: request-flow and failure-domain explainability for execution/inference-support flows.

### 2.2 Included card families

- symbol cards (`safe_now`)
- path cards (`safe_now`)
- hotspot cards (`safe_now`)
- failure-domain cards (`safe_now`)
- constrained pipeline/state-machine cards (`safe_for_pilot_only`, only canonical non-partial segments)

### 2.3 Excluded card families/use

- storage/control-plane canonical cards (wait for blocker resolution)
- replay-deep and system_learning-deep cards
- any cards requiring production-truth resolution of unresolved canonical-state/ownership blockers

## 3. Explicit non-goals

- No production card generation.
- No Chroma writes.
- No ADG schema changes.
- No runtime code dependency on pilot card outputs.

## 4. Evaluation plan

| eval_dimension | metric | target_for_pilot_success |
|---|---|---|
| grounding fidelity | % sampled answers with correct source refs | >= 95% |
| structural correctness | % sampled path/symbol claims matching ADG truth | >= 97% |
| residual transparency | % sampled cards with correct instability/residual tags | 100% |
| usefulness | operator/dev rating on scoped Q&A tasks | >= 4/5 median |
| safety | count of unstable facts labeled canonical | 0 |

## 5. Success criteria

Pilot is successful if all are met:

- all pilot-start gates pass,
- metrics meet or exceed targets,
- no unstable canonical-claim violations,
- pilot demonstrates measurable value for selected use cases,
- no production dependency is introduced.

## 6. Failure criteria

Pilot is failed (or paused) if any occur:

- canonical mislabeling of unresolved facts,
- repeated ADG/card mismatch beyond thresholds,
- pilot scope creep into blocked families,
- dependency pressure to use pilot outputs in production path.

## 7. Pilot exit decision

- **Promote to H1 implementation planning** only if pilot success criteria pass and production blockers are independently on closure path.
- Otherwise, run **H1 blocker-reduction first**.
