# P5 Audit Delta — Cryptographic Trust & Signing

**Generated**: 2026-02-09
**Scope**: P5 items only (§7.4.1, §7.4.2, §7.4, §7.2.1, §1.7, §7.2, §2.6)
**Audit contract**: Prompt v5.0 Enhanced (unchanged)
**Discovery hash**: `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4` (unchanged)

---

## P5 Items — Before / After

| Audit § | Capability | Before | After | Evidence |
| --- | --- | --- | --- | --- |
| §7.4.1 | Signature Enclave subsystem | MISSING | **COMPLIANT** | `agentic_core/L0_maintenance/types/v15_p5_types.py::SignatureEnclave` (ABC, lines 258–274) + `DeterministicTestEnclave` (lines 277–316) — deterministic HMAC-SHA256, no wall-clock/env |
| §7.4.2 | Signatures verifiable against pinned Public Keys | MISSING | **COMPLIANT** | `v15_p5_types.py::TrustRoot` (lines 72–90) + `v15_p5_contracts.py::verify_signature` (lines 93–128) — key lookup, ACTIVE/REVOKED check, fail-closed |
| §7.4 | Guardian signed artifact (env metadata, commit hash, signature) | FAIL | **COMPLIANT** | `v15_p5_contracts.py::sign_artifact` (lines 51–79) → `SignatureEnvelope` (lines 101–131 in types) — trace_id, artifact_hash, key_id, signature, algorithm, semantic_clock_tick |
| §7.2.1 | GuardianArtifact signed (trace_id, signature, prestaged_perms) | FAIL | **COMPLIANT** | `v15_p5_types.py::SignedGuardianArtifact` (lines 140–175) — frozen, 6 required fields per spec |
| §1.7 | SignedModify artifact | MISSING | **COMPLIANT** | `v15_p5_types.py::SignedModify` (lines 196–230) — frozen, trace_id + human_reviewer_id + resolution (APPROVE/REJECT/MODIFY) + modified_manifest + signature |
| §7.2 | Artifact Guard (Replay Comparison + Valid Signature) | MISSING | **COMPLIANT** | `v15_p5_contracts.py::ReplayGuardStore` (lines 143–175) + `record_and_block_replay` (lines 178–184) — blocks on second sighting, fail-closed |
| §2.6 | ≥2 hash mismatches → human escalation | MISSING | **COMPLIANT** | `v15_p5_types.py::HashMismatchTracker` (lines 244–256) + `v15_p5_contracts.py::record_hash_mismatch` (lines 193–201) — threshold=2, raises EscalationRequiredError |

**P5 Total: 7/7 COMPLIANT**

---

## Enforcement Contracts

| Contract | File | Purpose |
| --- | --- | --- |
| `hash_artifact_canonical()` | `v15_p5_contracts.py` (lines 34–36) | Canonical SHA-256 hashing |
| `sign_artifact()` | `v15_p5_contracts.py` (lines 51–79) | §7.4 — Sign via enclave, produce SignatureEnvelope |
| `verify_signature()` | `v15_p5_contracts.py` (lines 93–128) | §7.4.2 — Verify against trust root, fail-closed |
| `record_and_block_replay()` | `v15_p5_contracts.py` (lines 178–184) | §7.2 — Replay guard, fail-closed on second sighting |
| `record_hash_mismatch()` | `v15_p5_contracts.py` (lines 193–201) | §2.6 — Escalation on ≥2 mismatches |
| `build_signed_guardian_artifact()` | `v15_p5_contracts.py` (lines 214–243) | §7.2.1 — Build signed guardian artifact via enclave |

---

## Regression Tests

| Suite | File | Tests | Skips | Status |
| --- | --- | --- | --- | --- |
| P5 Compliance | `tests/guardian/test_v15_p5_compliance.py` | 52 | 0 | PASS |

---

## Non-P5 Suites (Unchanged)

| Suite | Tests | Skips | Status |
| --- | --- | --- | --- |
| P1 Compliance | 60 | 0 | PASS |
| P2 Compliance | 64 | 0 | PASS |
| P3 Compliance | 47 | 0 | PASS |
| P4 Compliance | 53 | 0 | PASS |
| Baseline Pins | 3 | 0 | PASS |
| Integration Wiring | 17 | 0 | PASS |
| **Combined** | **296** | **0** | **PASS** |

---

## Frozen Priorities (No Movement)

| Priority | Status |
| --- | --- |
| P1 | 24/24 COMPLIANT (unchanged) |
| P2 | 17/17 COMPLIANT (unchanged) |
| P3 | 3/3 COMPLIANT (unchanged) |
| P4 | 8/8 COMPLIANT (unchanged) |
| P6 | Deferred — not in scope |

---

## Discovery Integrity

| Artifact | SHA-256 | Status |
| --- | --- | --- |
| `artifacts/forensic_discovery_output.json` | `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4` | UNCHANGED |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

