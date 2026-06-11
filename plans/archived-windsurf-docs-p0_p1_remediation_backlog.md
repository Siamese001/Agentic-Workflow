---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\p0_p1_remediation_backlog.md'
original_relative_path: 'p0_p1_remediation_backlog.md'
source_sha256: c92fc36f9e3fc6e254cf2eb45f95b4ccadefeae2d69eda85298446380753a633
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P0–P1 REMEDIATION BACKLOG

**Derived from**: `v5_forensic_gap_analysis_report_clean.md`
**Discovery commit**: `7f6d87befab360bf9cff3dd87772832cbbcbf742`
**Discovery SHA-256**: `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4`
**Extraction date**: 2026-02-09

---

## Extraction Criteria

- **Included**: All FAIL and MISSING findings gated by **P1** (Fail-Closed Defaults)
- **Excluded**: All findings gated exclusively by P2–P6 (frozen as accepted technical debt)
- **Mixed gating**: If a finding is gated by P1 AND other invariants, it is included here

---

## P0 — DISCOVERY INFRASTRUCTURE (Completed)

All P0 items were resolved in PHASE 0 before the audit re-run.

| ID | Item | Status | Evidence |
|---|---|---|---|
| P0-1 | Canonical SHA-256 for `forensic_discovery_prep.py` in structure blueprint | **DONE** | `structure_blueprint/ssot.py` lines 167–172, `discovery_integrity.sha256` |
| P0-2 | Fix discovery script import path in-source | **DONE** | Line 50: `agentic_core.L0_maintenance.utils.ssot_discovery_util` |
| P0-3 | Unify discovery schema field mapping | **DONE** | Lines 247, 267–268: `file`/`class_name`. Schema bumped to `1.3.0` |
| P0-4 | Clean discovery execution | **DONE** | 150 ACTIVE, 40 INVALID, exit code 0, no runtime patching |

---

## P1 — FAIL-CLOSED DEFAULTS (Remediation Required)

These are findings where the audit determined FAIL or MISSING and the gating invariant includes **P1 (Fail-Closed Defaults)**. P1 requires that every decision defaults to the most restrictive option unless explicitly overridden by a typed artifact.

### P1 FAIL Items

| Backlog ID | Audit ID | Capability | Status | Current State | Gating |
|---|---|---|---|---|---|
| P1-F-01 | 3.1 | RouteDecision typed artifact (6 required fields) | **FAIL** | `contextual_router_config.py::RouteDecision` (line 40) is an `Enum` with 4 values. Missing: `timestamp`, `route_path`, `risk_score`, `budget_est`, `rationale_enum`, `policy_config_hash` | P1, P2, P4, P5, P6 |
| P1-F-02 | 3.3 | Routing paths strictly defined (5 paths) | **FAIL** | 4 paths: `BYPASS`, `VALIDATE`, `HUMAN_REVIEW`, `REJECT`. Missing: "Policy Challenge Loop", "Route Recovery (Budget Overflow)" | P1 |

### P1 MISSING Items

| Backlog ID | Audit ID | Capability | Status | Gating |
|---|---|---|---|---|
| P1-M-01 | 3.2 | Rationale restricted to finite enum | **MISSING** | P1 |
| P1-M-02 | 3.6 | Law Slot Handler / Read-Only Twins / Capability Depletion | **MISSING** | P1, P5 |
| P1-M-03 | 4.1 | `policy_config` read-once per healing wave | **MISSING** | P1, P2 |
| P1-M-04 | 4.3 | Policy mutation during wave = critical incident | **MISSING** | P1 |
| P1-M-05 | 6.3 | Prompt augmentation (≤300 tokens, TokenControl Artifact) | **MISSING** | P1 |
| P1-M-06 | 6.4 | Static Policy Alignment Check | **MISSING** | P1 |
| P1-M-07 | 7.3 | Guardrail Guard (Budget, Payload, Safety Markers, Boundary Tokens) | **MISSING** | P1 |
| P1-M-08 | 7.5 | Absence of artifact/signature = automatic failure | **MISSING** | P1 |
| P1-M-09 | 7.6 | Meta-Guardian ≥95% invariant coverage in CI | **MISSING** | P1 |
| P1-M-10 | 7.7 | Aggregate Gate Rule (Guardian validates AGGREGATE before L2) | **MISSING** | P1 |
| P1-M-11 | 10.1 | Healing inside transactional boundary | **MISSING** | P1 |
| P1-M-12 | 10.4 | RESULT emission exclusive to L2 post-heal | **MISSING** | P1 |
| P1-M-13 | 11.1 | TokenCap Enforcement (pre-route, pre-LLM, TokenCap Artifact) | **MISSING** | P1, P2 |
| P1-M-14 | 11.2 | Route Recovery (TokenOverflow → RouteRecovery) | **MISSING** | P1 |
| P1-M-15 | 15.1 | Tiered Vigilance (Tier I/II/III, Evacuation Protocol) | **MISSING** | P1 |
| P1-M-16 | 15.4 | Capability Depletion (tool slot depletion rate) | **MISSING** | P1 |
| P1-M-17 | 15.6 | INCIDENT and RESULT emit telemetry events | **MISSING** | P1 |
| P1-M-18 | 2.5 | Pipe order enforced (1..10) — per-agent | **MISSING** | P1 |
| P1-M-19 | 2.8 | AGGREGATE→Heal boundary typed — per-agent | **MISSING** | P1 |
| P1-M-20 | 5.4 | L6 SelfHealingTrigger emission — per-agent | **MISSING** | P1 |
| P1-M-21 | 11.1 | TokenCap & Perms — per-agent | **MISSING** | P1 |
| P1-M-22 | 15.1 | Tier III Evacuation — per-agent | **MISSING** | P1 |

---

## P1 Summary

| Category | Count |
|---|---|
| P1 FAIL | 2 |
| P1 MISSING | 22 |
| **P1 Total** | **24** |

---

## ACCEPTED TECHNICAL DEBT (P2–P6 Only, Frozen)

The following findings are gated **exclusively** by P2–P6 invariants (no P1 involvement). They are tracked but not scheduled for immediate remediation.

### P2 (Determinism & Replayability) — 14 items

| Audit ID | Capability | Status |
|---|---|---|
| 1.1 | SurgicalManifest as exclusive execution input | MISSING |
| 1.2 | Forbidden execution inputs (raw paths, regex, diffs) | FAIL |
| 1.3 | SurgicalManifest schema (10 required fields) | MISSING |
| 1.4 | Deterministic AST serialization | MISSING |
| 6.1 | Episodic memory queried before planning | MISSING |
| 6.2 | Trajectory reuse | MISSING |
| 6.6 | Knowledge Supervisor | MISSING |
| 6.8 | Memory Hypostates | MISSING |
| 6.10 | Episodic ↔ Semantic Linking | MISSING |
| 10.2 | Boundary Snapshot Artifact | MISSING |
| 10.3 | Post-rollback hash matches pre-wave snapshot | MISSING |
| 13.1 | Semantic Clock (Step ID + Vector Clock) | FAIL |
| 13.1.1 | Semantic Clock advances only on valid StateCommit | MISSING |
| 13.2 | No wall-clock in hashes/signatures/dedup | FAIL |
| 15.3 | Forensic Trace Buffer | MISSING |
| 2.1 | Validator emits SurgicalManifest — per-agent | MISSING |
| 5.1 | Dedupe uses SHA-256 — per-agent | MISSING |

### P3 (No Silent State Mutation) — 3 items

| Audit ID | Capability | Status |
|---|---|---|
| 9.2 | heal() domain reasoning only (per-agent) | COMPLIANT |
| 12.2 | Side-effect registry — per-agent | MISSING |
| 12.3 | Read-Only Boundary (L0, L4, L6) — per-agent | MISSING |

### P4 (Immutable Traceability) — 10 items

| Audit ID | Capability | Status |
|---|---|---|
| 1.6 | Hash Verification (manifest_hash) | MISSING |
| 1.7 | Secondary Typed Artifacts | MISSING |
| 3.4 | Human escalation generates EvidencePack | MISSING |
| 4.2 | SHA-256 of policy config at wave start | MISSING |
| 6.5 | RAG Artifact Chain | MISSING |
| 6.7 | Plan Provenance artifact | MISSING |
| 5.2 | Error signature (type+node+vector_clock) — per-agent | MISSING |
| 15.2 | Cognitive Diff Bundle — per-agent | MISSING |
| 15.5 | Trace ID `CC3AL1-` format — per-agent | FAIL |

### P5 (Authority Is Tokenized) — 7 items

| Audit ID | Capability | Status |
|---|---|---|
| 1.5 | SSOT Binding (node_id resolves to structure_blueprint) | MISSING |
| 3.5 | Bidirectional Feedback (PolicyUpdateProposal) | MISSING |
| 3.7 | Policy Challenge Protocol (PolicyExceptionArtifact) | MISSING |
| 6.9 | Knowledge Graph advisory-only constraint | MISSING |
| 7.2 | Artifact Guard (Replay Comparison + Valid Signature) | MISSING |
| 7.2.1 | GuardianArtifact signed | FAIL |
| 7.4 | Guardian signed artifact (env metadata, commit hash, signature) | FAIL |
| 7.4.1 | Signature Enclave subsystem | MISSING |
| 7.4.2 | Signatures verifiable against pinned Public Keys | MISSING |

### P6 (Explicit Boundaries / Zero Trust Between Layers) — 2 items

| Audit ID | Capability | Status |
|---|---|---|
| 3.8 | Context Retrieval Request Artifact (L0→L4) | MISSING |
| 12.1 | Inter-agent schema validation — per-agent | MISSING |

### Debt Summary

| Invariant | Items | FAIL | MISSING | COMPLIANT |
|---|---|---|---|---|
| P2 | 17 | 3 | 14 | 0 |
| P3 | 3 | 0 | 2 | 1 |
| P4 | 9 | 1 | 8 | 0 |
| P5 | 9 | 2 | 7 | 0 |
| P6 | 2 | 0 | 2 | 0 |
| **Total debt** | **40** | **6** | **33** | **1** |

---

## Integrity Anchors

| Artifact | SHA-256 |
|---|---|
| `forensic_discovery_prep.py` (corrected) | `b08c3cdbabf064c9be69aa0b063d8573bf97392a30d8fff531a5fc9a2b1d2d31` |
| `forensic_discovery_output.json` | `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4` |
| `discovery_integrity.sha256` | stored in `agentic_core/L5_safety/config/structure_blueprint/discovery_integrity.sha256` |
| `blueprint_integrity.sha256` | `56ce497ea5703d884c1849187431e72bd18a254e271518596669860266158ea0` |
| Discovery commit | `7f6d87befab360bf9cff3dd87772832cbbcbf742` |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

