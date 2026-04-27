# Tier 1 Requirement Selection

> **Selection only. No implementation or proof performed.**
>
> Companion JSON: `TIER1_SELECTION.json` (machine-readable).

## Index

- **Total rows reviewed**: ~150 (all rows in `docs/reference/contracts/step1/*.md`, including the 17 Tier 0 rows and ~13 reference / overview / coverage-matrix rows that are non-blocking by construction)
- **Tier 0 rows excluded**: 17
- **Tier 1 selected count**: 15
- **Selection window**: 10–15 (within bound)
- **Inputs**: `docs/reference/contracts/step1/*.md` (read-only)
- **Outputs**: this file + `TIER1_SELECTION.json`
- **Status vocabulary used**: `RELEASE_BLOCKING` only (no proof-claim tokens emitted)

## Selected REQ_ID Table

| Rank | REQ_ID | Owner | Strength | Risk Category |
|---:|---|---|---|---|
| 1 | REQ-L4-NO-DIRECT-WRITE-FROM-L2-001 | UWG / WriteSovereignty | MUST_NOT | write_sovereignty |
| 2 | REQ-L4-NO-DIRECT-WRITE-FROM-L6-001 | UWG / WriteSovereignty | MUST_NOT | write_sovereignty |
| 3 | REQ-UWG-OBS-ANTI-BYPASS-001 | UWG / AntiBypass | MUST_NOT | write_sovereignty |
| 4 | REQ-GATE-OBS-ANTI-BYPASS-001 | RuntimeGates / AntiBypass | MUST_NOT | gate_integrity |
| 5 | REQ-L5-SAFETY-ENFORCE-PLANE-001 | L5 / SafetyPlane | MUST_NOT | authority_bypass |
| 6 | REQ-L5-ORIGIN-TRUST-BOUNDARY-001 | L5 / OriginTrust | MUST_NOT | prompt_boundary |
| 7 | REQ-PA-AUTHORITY-REDTEAM-001 | PA / RedTeam | MUST_NOT | prompt_boundary |
| 8 | REQ-C0-OBS-ANTI-BYPASS-001 | C0 / AntiBypass | MUST_NOT | retrieval_boundary |
| 9 | REQ-L2-OBS-ANTI-BYPASS-001 | L2 / AntiBypass | MUST_NOT | execution_safety |
| 10 | REQ-PA-FINAL-EMIT-ARTIFACT-001 | PA / PromptArtifact | MUST | artifact_integrity |
| 11 | REQ-EXIT-X1G-X1I-REPLAY-001 | Exit / X1Replay | MUST | replay_integrity |
| 12 | REQ-L4-REPLAY-SNAPSHOT-AUDIT-001 | L4 / ReplaySnapshot | MUST | audit_traceability |
| 13 | REQ-L6-GAUNTLET-FUTURE-RUN-001 | L6 / Gauntlet | ONLY | learning_firewall |
| 14 | REQ-EXIT-OBS-ANTI-BYPASS-001 | Exit / AntiBypass | MUST_NOT | output_disposition |
| 15 | REQ-L5-STATIC-GOV-DRIFT-001 | L5 / StaticGov | MUST | proof_false_confidence |

All 15 rows have `Release_Gate_Rule = RELEASE_BLOCKING` in their source matrices. Detailed per-row evidence/test/artifact/replay/negative-control gap predictions are in `TIER1_SELECTION.json`.

## Tier 0 Rows Excluded (17)

Tier 0 protected by `scripts/verify_tier0_enforcement_gate.py` and `scripts/verify_tier0_runtime_proof_gate.py`:

REQ-UWG-WRITE-SOLE-PATH-001, REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001, REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001, REQ-C0-EVIDENCE-NO-ANSWER-001, REQ-PA-ASSEMBLY-NO-RETRIEVAL-001, REQ-PA-ASSEMBLY-NO-EXECUTE-001, REQ-L0-ROUTE-EXACTLY-ONE-001, REQ-L2-EXECUTE-BOUNDED-PACKET-001, REQ-L2-WRITE-NO-DIRECT-L4-001, REQ-EXIT-X3-ONE-DISPOSITION-001, REQ-EXIT-WRITE-NO-L4-MUTATION-001, REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001, REQ-L6-WRITE-NO-DIRECT-L4-001, REQ-E2E-PROOF-NEGATIVE-REASON-001, REQ-E2E-PROOF-PAYLOAD-HASH-001, REQ-TRACE-OTEL-CRITICAL-SPANS-001, REQ-TRACE-REPLAY-ROUTE-EXIT-STABLE-001.

None are duplicated in Tier 1.

## Rationale by Risk Category

### write_sovereignty (3 selections — ranks 1, 2, 3)
Tier 0 establishes UWG as the *sole* write path. Tier 1 closes the per-layer enforcement: L2 cannot bypass (rank 1), L6 cannot bypass via promotion (rank 2), and a catch-all anti-bypass scanner detects unforeseen paths (rank 3). The trio is needed because the Tier 0 sole-path rule alone cannot prove which layers respect it.

### gate_integrity (1 selection — rank 4)
Tier 0 covers two **schema** invariants on gate verdicts. Tier 1 closes the **structural** risk: a code path that runs without invoking a gate at all. A skipped gate is silently equivalent to PASS — schema rules cannot detect that.

### authority_bypass (1 selection — rank 5)
L5 is governance-only by contract; if L5 ever emits a live GateVerdict or X3 disposition the chain of custody for runtime authority breaks. Tier 0 has no L5-authority-scope row.

### prompt_boundary (2 selections — ranks 6, 7)
Two complementary defenses: (a) origin-side labeling (rank 6) prevents untrusted content from entering trusted assembly unlabeled; (b) PA-side red-team (rank 7) detects unauthorized slot insertions when content does cross. Together they bracket the prompt-injection vector.

### retrieval_boundary (1 selection — rank 8)
Catches retrieval performed *without* a sealed C0 evidence contract — the orthogonal failure mode to Tier 0's REQ-C0-EVIDENCE-NO-ANSWER-001 (which restricts what C0 emits) and REQ-PA-ASSEMBLY-NO-RETRIEVAL-001 (which restricts what PA does).

### execution_safety (1 selection — rank 9)
Tier 0 covers the bounded-execution-packet *entry*. Tier 1 covers post-entry sequencer/sandbox compliance — code paths that skip the sequencer or escape the sandbox after admission.

### artifact_integrity (1 selection — rank 10)
The PA→L2 prompt-artifact seal is the foundation of replay determinism and audit chain. Without it, L2 cannot prove which prompt it executed.

### replay_integrity (1 selection — rank 11)
Tier 0 covers payload-hash and route/exit stability. Tier 1 covers the broader X1G–X1I consistency window where missing or malformed replay evidence becomes a release blocker.

### audit_traceability (1 selection — rank 12)
The 1:1 mutation-to-snapshot-and-ledger contract is the durable audit backbone. Tier 0 has no row covering this — it covers boundaries, not the trail.

### learning_firewall (1 selection — rank 13)
Tier 0 covers the L6 firewall against current-run mutation (REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001). Tier 1 covers the complementary publish-direction invariant: gauntlet decisions go *only* to future-run state.

### output_disposition (1 selection — rank 14)
Tier 0's REQ-EXIT-X3-ONE-DISPOSITION-001 enforces *exactly one* disposition. Tier 1 covers the orthogonal failure: a response leaving Exit with *no* X3 record at all.

### proof_false_confidence (1 selection — rank 15)
The meta-gate. If declared governance state drifts away from runtime structure, every other proof can pass while the contract being proved has silently changed. Detecting drift before promotion prevents the entire Tier 0 / Tier 1 stack from giving false confidence.

## Selection Discipline

Each row was chosen by:
1. **RELEASE_BLOCKING** (✓ all 15 rows)
2. **MUST / MUST_NOT / ONLY** strength (✓ all 15 rows: 9 MUST_NOT, 5 MUST, 1 ONLY)
3. **Cross-layer or boundary-sensitive** (✓ each row crosses or guards a layer/authority/contract boundary)
4. **Likely to need runtime proof, not just doc** (✓ each gap-prediction column lists runtime evidence / replay / artifact / negative-control needs)
5. **Not in Tier 0** (✓ verified against the 17-ID exclusion list)

## Validation

| Check | Expected | Actual | Result |
|---|---|---|---|
| Selected count in [10, 15] | 10–15 | 15 | PASS |
| No Tier 0 REQ_IDs included | 0 overlap | 0 | PASS |
| Every selected REQ_ID exists in Step 1 matrices | 15 | 15 | PASS |
| Every selected row has a risk_category | 15 | 15 | PASS |
| Every selected row has why_tier1 | 15 | 15 | PASS |
| risk_category drawn only from allowed list | yes | yes | PASS |
| No proof-claim tokens emitted | yes | yes | PASS |

## Disclaimer

**Selection only. No implementation or proof performed.** No runtime behavior was modified. No tests were run. No proof harness was run. No replay was executed. No OTEL exporter was run. `docs/reference/contracts/step1/` was not modified. Tier 0 gates and CI workflows were not touched.
