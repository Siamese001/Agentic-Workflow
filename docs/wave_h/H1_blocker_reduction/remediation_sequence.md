# H1 — Remediation Sequence (Dependency-Ordered)

wave: H1
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 1. Dependency logic

Sequence is determined by dependency, not severity:

- canonical-state and ownership foundations first,
- contract-authority and governance trust next,
- broad taxonomy and resilience hardening after foundational decisions,
- secondary watch/defer items remain out of critical path.

## 2. Wave-H1 sequence

| seq | remediation_unit | blockers | dependency_reasoning | parallel_group |
|---|---|---|---|---|
| 1 | Canonical memory-state decision package | B7-G4-03, B7-G6-03 | storage/control-plane production cards cannot be trusted until canonical state is singular and explicit | A |
| 2 | Ownership formalization baseline | B7-G6-05 | owner clarity is prerequisite for resolving contract authority and governance accountability | A |
| 3 | Contract-authority resolution | B7-G6-01, B7-G6-02 | depends on ownership baseline; removes authoritative-contract ambiguity | B |
| 4 | Governance hardening package | B7-G2b-06, DISABLE_RUNTIME_MUTATION_GUARD | can run in parallel with seq 3 once owner/accountability model is stable | B |
| 5 | Taxonomy reduction for production-safe packaging | B7-G6-04 | uses outputs from seq 1-4 to avoid reclassifying unstable authority/ownership surfaces | C |
| 6 | Gateway resilience production alignment | B7-G3-05 | best finalized after ownership/governance and taxonomy constraints are clearer | C |
| 7 | Production gate re-evaluation checkpoint | all mandatory blockers | objective closure-test pass/fail against `closure_criteria.md` | D |

## 3. Parallelization map

- **Parallel group A** (can run together):
  - canonical-state decision package
  - ownership formalization baseline
- **Parallel group B** (can run together after A baseline):
  - contract-authority resolution
  - governance hardening package
- **Parallel group C** (can run together after A/B):
  - taxonomy reduction
  - gateway resilience alignment

## 4. Secondary residual handling (non-critical path)

These do not block H1 critical-path closure and should be tracked in watch/defer lane:

- B7-G3-04 partial replay topology
- B7-G3-06 partial system_learning topology
- REDIS default ambiguity
- provider/model selector layering ambiguity
- SOVEREIGN_AUTO_APPROVE / ARCHIVE_BATCH_ACCEPT override posture
- G5 opaque restart semantics

## 5. Exit criteria for H1 sequence completion

H1 sequence is complete when:

- each mandatory blocker has closure score (0-3 rubric) recorded,
- unresolved blockers have explicit next-wave remediation ownership,
- production-readiness delta is updated with unambiguous H2 recommendation.
