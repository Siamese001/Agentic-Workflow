---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\runtime-cert-hardened-w0-7e3c9a.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-hardened-w0-7e3c9a.md'
source_sha256: 7c7495abcb4b542d359cdb3c3af3e02b8f299c675ab2d20b28d46dba7165914b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Certification Hardened Matrix — W0 Implementation Plan

- Plan slug: `runtime-cert-hardened-w0-7e3c9a`
- Status: Completed (W0-W4 all waves done 2026-05-08)
- Tier: T3
- Author-Gate decision: 2026-04-30 (refactor_scope) — selected `all_20_W0_rows_W0_depth_only`
- Source of truth: `docs/reference/runtime_certification_requirements_100_percent_hardened.csv` (86 rows)
- Implementation prompt: `docs/reference/windsurf_runtime_certification_implementation_prompt.md`

## Wave Structure

| Wave  | Phase IDs | Focus                                                    | Est. Tokens | Assumptions                                                                                         | Status        | Success Criteria |
|-------|-----------|----------------------------------------------------------|------------:|-----------------------------------------------------------------------------------------------------|---------------|------------------|
| W0    | W0.1–W0.6 | Certification source-of-truth + fail-closed CI matrix    | ~30k        | Source CSV at `docs/reference/runtime_certification_requirements_100_percent_hardened.csv` is bound | ✅ DONE       | All 20 W0 rows enforced; 5 verifiers fail-closed; CI workflow valid; 25 tests pass |
| W1    | W1.1-W1.2j | Semantic cache + cache state closeout                   | ~50k        | W0 fail-closed proven                                                                               | ✅ DONE       | 10 probes, 5 tests, ADR generator implemented |
| W2b   | W2b.1-W2b.7 | Live provider acceptance + safe reuse                 | ~25k        | W1 done                                                                                             | ✅ DONE       | 7 steps, readiness + rubric + safe reuse probes |
| W3    | W3.1-W3.4  | OTel collector + replay verifier                         | ~40k        | W2 done                                                                                             | ✅ DONE       | 2 probes, 2 test files, RTC-REQ-113/114 complete |
| W4    | W4         | G-1/G-29 runtime gates structural validation             | ~25k        | W3 done                                                                                             | ✅ DONE       | test_runtime_gates_g01_g29.py complete |

## Phase-Level Summary (W0 only)

| Phase ID | Title                                  | Scope (files)                                                                                                                                  | Pain Points                                                              | Est. Tokens | Status      |
|----------|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|------------:|-------------|
| W0.1     | Canonical CSV binding                  | `docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv` (copy)                                    | Single SSOT must match source bytes                                       | 1k          | Pending     |
| W0.2     | Prove-requirements package             | `agentic_core/runtime/prove_requirements/{__init__,matrix_loader,proof_depth_ladder,acceptance_validator,artifact_payload_hasher}.py`          | Single loader prevents source divergence; ladder enforces composition rule| 8k          | Pending     |
| W0.3     | Five verifier scripts                  | `scripts/verify_runtime_certification_{matrix,matrix_schema,acceptance}.py` + `verify_source_divergence.py` + `verify_artifact_payload_hashes.py` | Each verifier emits expected_fail_reason + actual_fail_reason             | 10k         | Pending     |
| W0.4     | Four test files                        | `tests/runtime/test_runtime_certification_{matrix_schema,acceptance}.py` + `test_source_divergence.py` + `test_artifact_payload_hashes.py`     | ~25 cases covering all W0 fail-closed paths                              | 8k          | Pending     |
| W0.5     | CI workflow                            | `.github/workflows/runtime-certification.yml`                                                                                                  | Must run all 5 verifiers; fail-closed on any non-zero exit               | 1k          | Pending     |
| W0.6     | Verification + commit                  | run all verifiers + tests, validate 6 artifacts; commit + push                                                                                 | First-run must produce all 6 artifacts deterministically                  | 2k          | Pending     |

## W0 rows covered (20 of 86 — confirmed by user 2026-04-30)

| Req ID         | Title                                          | Wave Tag                          | Verifier              |
|----------------|------------------------------------------------|-----------------------------------|------------------------|
| RTC-REQ-001    | Canonical requirement universe declared        | source-of-truth                   | matrix.py              |
| RTC-REQ-002    | Proof depth fields mandatory                   | source-of-truth                   | matrix_schema.py       |
| RTC-REQ-003    | Claim type enum enforced                       | source-of-truth                   | matrix_schema.py       |
| RTC-REQ-004    | Acceptance legality rule                       | source-of-truth                   | acceptance.py          |
| RTC-REQ-005    | Reference-only rows cannot claim runtime       | source-of-truth                   | acceptance.py          |
| RTC-REQ-006    | Subclaim decomposition mandatory               | source-of-truth                   | matrix_schema.py       |
| RTC-REQ-030    | All-requirements gate readiness                | source-of-truth                   | matrix.py              |
| RTC-REQ-031    | Merkle root non-empty and complete             | source-of-truth                   | matrix.py (presence)   |
| RTC-REQ-032    | Source divergence block                        | source-of-truth                   | source_divergence.py   |
| RTC-REQ-033    | Hardening minimum enforced                     | source-of-truth                   | matrix.py              |
| RTC-REQ-034    | Downgraded rows report required                | source-of-truth                   | acceptance.py          |
| RTC-REQ-110    | Matrix schema CI gate                          | ci-fail-closed                    | CI workflow            |
| RTC-REQ-111    | Acceptance legality CI gate                    | ci-fail-closed                    | CI workflow            |
| RTC-REQ-112    | Semantic cache CI gate **(stub fail-closed)**  | ci-fail-closed                    | CI workflow → W1 ext   |
| RTC-REQ-113    | OTEL collector CI gate **(stub fail-closed)**  | ci-fail-closed                    | CI workflow → W3 ext   |
| RTC-REQ-114    | Replay CI gate **(stub fail-closed)**          | ci-fail-closed                    | CI workflow → W3 ext   |
| RTC-REQ-115    | No-bypass mutation CI gate **(stub fail-closed)** | ci-fail-closed                | CI workflow            |
| RTC-REQ-123    | Artifact payload content-hash validation       | source-of-truth                   | artifact_payload_hashes.py |
| RTC-REQ-124    | Single repo root + output dir binding          | source-of-truth                   | matrix.py              |
| RTC-REQ-127    | COMPOSITION_PROOF cannot promote acceptance    | source-of-truth                   | acceptance.py          |

## W0 boundary (per user 2026-04-30)

W0 implements **CI/verifier enforcement that those claims cannot pass unless required artifacts exist** — but does **NOT** implement:
- Semantic cache evidence emission (W1)
- Real OTel collector or replay execution (W3)
- Per-row INTEGRATED_RUNTIME proof emission (W2)
- Final certification language gate (W4)

Stubs for 112/113/114/115 in W0 are CI-presence + artifact-presence checks that fail closed when the W1/W3 verifiers haven't emitted their evidence files yet. They DO NOT execute semantic-cache, OTel, or replay logic themselves.

## Anti-cheat invariants (W0 fail-closed list)

W0 verifiers MUST fail closed on:
1. Missing canonical CSV
2. Missing required columns from CSV header
3. Invalid enums (claim_type, required_proof_depth)
4. Insufficient proof depth (`actual < required`)
5. Accepted row with weaker proof
6. Source divergence (any verifier sees row count ≠ canonical 86)
7. Missing artifact payload (referenced but absent or unreadable)
8. Composition proof promoted to E6/E7/E8/E9

## Reproduction

```
python scripts/verify_runtime_certification_matrix.py
python scripts/verify_runtime_certification_matrix_schema.py
python scripts/verify_runtime_certification_acceptance.py
python scripts/verify_source_divergence.py
python scripts/verify_artifact_payload_hashes.py
python -m pytest tests/runtime/test_runtime_certification_matrix_schema.py tests/runtime/test_runtime_certification_acceptance.py tests/runtime/test_source_divergence.py tests/runtime/test_artifact_payload_hashes.py -v
```

## Author-Gate decision lineage

- 2026-04-30 (refactor_scope): selected `all_20_W0_rows_W0_depth_only` over `strict_14_row_scope` (gap 0.27, confidence 0.82). User explicitly confirmed: "all 20 W0 rows, but only to the W0 enforcement depth."
