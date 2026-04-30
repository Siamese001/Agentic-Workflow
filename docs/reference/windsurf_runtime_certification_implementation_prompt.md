# Windsurf implementation prompt — Runtime Certification CSV hardening

You are working in `C:\Git\Agentic-Workflow-FRESH`.

Use this CSV as the implementation source of truth:

`/mnt/data/runtime_certification_requirements_100_percent_hardened.csv`

If copied into the repo, place it at:

`docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv`

## Goal

Implement the hardened runtime certification requirements as executable, fail-closed verification gates.

Do not summarize the CSV. Implement it.

## Non-negotiable rules

1. Do not call any row ACCEPTED unless `actual_proof_depth >= required_proof_depth`.
2. Do not allow COMPOSITION_PROOF to satisfy INTEGRATED_RUNTIME_PROOF, REAL_OTEL_EXPORT, REPLAY_DETERMINISM, or PRODUCTION_DEPENDENCY_PROOF.
3. Do not accept semantic cache final proof unless all R1B subclaims pass:
   - R1B_DENSE_SIMILARITY_COMPOSITION_PROOF
   - R1B_APPROVED_MODEL_PROOF
   - R1B_PRODUCTION_THRESHOLD_PROOF
   - R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF
   - R1B_NEGATIVE_CONTROL_PROOF
   - R1B_TERMINAL_EXIT_PROOF
   - R1B_INTEGRATED_RUNTIME_PROOF when runtime certification is claimed
   - R1B_REAL_OTEL_PROOF when observability is claimed
   - R1B_REPLAY_PROOF when replay is claimed
4. Do not silently lower semantic-cache thresholds. If production threshold fails, emit CALIBRATION_GAP unless an ADR/calibration study exists.
5. Do not silently fall back from BGE-M3 to MiniLM and call the model proof PASS. Use MISMATCH_EXPLAINED or BLOCKED.
6. Do not emit a Merkle root if leaf_count is 0 or lower than the canonical requirement universe.
7. If one verifier sees 0 requirements and another sees N, fail with SOURCE_DIVERGENCE.
8. Harnesses may observe production artifacts but must not stamp, synthesize, or invent them.
9. Collector-backed OTEL is required for OBSERVABILITY_RUNTIME. In-memory spans are not enough.
10. Replay claims require original/replay bundle comparison and mutation negative tests.

## Implementation waves

### W0 — Certification source of truth and CI fail-closed

Implement:
- `scripts/verify_runtime_certification_matrix.py`
- `scripts/verify_runtime_certification_matrix_schema.py`
- `scripts/verify_runtime_certification_acceptance.py`
- `scripts/verify_source_divergence.py`
- `scripts/verify_artifact_payload_hashes.py`
- CI workflow: `.github/workflows/runtime-certification.yml`

Must prove:
- CSV schema valid
- enums valid
- proof-depth legality enforced
- source divergence fails closed
- artifact payload hash recomputation works
- composition proof cannot promote to integrated runtime proof

### W1 — Semantic cache and cache state closeout

Implement:
- `scripts/verify_semantic_cache_certification.py`
- `scripts/verify_semantic_cache_model.py`
- `scripts/verify_semantic_cache_threshold.py`
- `scripts/verify_semantic_cache_threshold_adr.py`
- `scripts/verify_semantic_cache_negatives.py`
- `scripts/verify_semantic_cache_calibration.py`
- `scripts/verify_l4_cache_schema.py`
- tests under `tests/runtime/test_semantic_cache_*.py`

Must prove:
- seed_query != live_query
- L1 exact miss
- L2 dense similarity hit
- reason_code=d2_semantic_hit
- expected model and actual model recorded
- BGE-M3 operational for approved model proof, or BLOCKED/MISMATCH_EXPLAINED
- production threshold passes without override, or CALIBRATION_GAP with ADR path
- NEG-5 expired freshness
- NEG-6 missing embedding ref
- NEG-7 unsafe semantic reuse
- tenant, namespace, policy, lexical-overlap, distance negatives
- TerminalRetPacket, ExitReviewPacket, X3 disposition

### W2 — Integrated runtime entrypoint

Implement or expose one production entrypoint that drives:

ValidatedRequest -> L1PlanContract -> RouteContract -> RuntimeGateVerdictBundle -> TerminalRetPacket or L2SealedArtifact -> ExitReviewPacket -> X3Disposition -> RuntimeExhaustBundle.

Add:
- `scripts/verify_integrated_runtime_entrypoint.py`
- `scripts/verify_r1b_integrated_runtime.py`
- `tests/runtime/test_integrated_runtime_entrypoint.py`

Composition harness sequencing may remain, but it must only earn COMPOSITION_PROOF.

### W3 — OTEL and replay

Implement:
- collector-backed OTEL docker compose or approved local collector
- `scripts/verify_otel_export.py`
- `scripts/verify_r1b_otel.py`
- `scripts/verify_replay_determinism.py`
- `scripts/verify_r1b_replay.py`

Must prove:
- parent scenario span
- route/cache/Exit child spans
- counter deltas with attributes
- exported collector artifact
- original/replay pair same route, same reason code, same X3, stable digest
- mutation replay negative fails closed

### W4 — Reports, Merkle, and final gate

Implement:
- `generate_runtime_certification_reports.py`
- semantic cache certification report
- runtime certification report
- OTEL certification report
- replay certification report
- downgraded rows report
- source divergence report
- Merkle root report
- all requirements gate report

Final gate can pass only when:
- no scoped blockers remain
- Merkle root non-empty
- leaf_count equals canonical requirement universe
- failed_commands=[]
- hardening_result=PASSED
- no accepted row has weaker proof than required
- no language overclaims its proof class

## Required first output

Before editing code, produce a short implementation plan with:

- files to create
- files to modify
- tests to add
- artifacts to generate
- rows covered in the first wave
- any ambiguity or source-owned boundary issue

Then implement W0 first. Do not jump to semantic cache until the matrix and acceptance validator can fail closed.
