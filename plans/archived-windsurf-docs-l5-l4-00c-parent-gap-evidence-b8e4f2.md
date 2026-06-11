---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\l5-l4-00c-parent-gap-evidence-b8e4f2.md'
original_relative_path: 'l5-l4-00c-parent-gap-evidence-b8e4f2.md'
source_sha256: 3428b16adae9d8a469fcb9788cf9cdc7d78503fae7d0d685d30b2d5cd4601730
recovered_status: LOST_RECOVERED
last_commit: 'ca523a716aa'
last_commit_date: '2026-05-23 14:40:04 -0400'
created_date: '2026-05-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Gap Evidence — 00A / 00B / 00C Parent REQ-ID Packs

**Generated:** 2026-05-23  
**Authority docs (parent packs):**

- [00A_L5_Governance_Safety.md](../../reference/00A_L5_Governance_Safety/00A_L5_Governance_Safety.md)
- [00B_L4_State_Archive_and_UWG.md](../../reference/00B_L4_State_Archive_and_UWG/00B_L4_State_Archive_and_UWG.md)
- [00C_Runtime_Gates_Current_Run_Mesh.md](../../reference/00C_Runtime_Gates_Current_Run_Mesh/00C_Runtime_Gates_Current_Run_Mesh.md)

**Review plan (SSOT):** [.cursor/plans/l5-l4-00c-parent-gap-b8e4f2.md](../../../.cursor/plans/l5-l4-00c-parent-gap-b8e4f2.md) — **COMPLETED 2026-05-23**  
**Gap matrix (W1):** [l5-l4-00c-parent-gap-matrix-b8e4f2.json](l5-l4-00c-parent-gap-matrix-b8e4f2.json)  
**W1 decision:** [ADR-00C-7-gate-verdict-ssot-b8e4f2.md](../../adr/ADR-00C-7-gate-verdict-ssot-b8e4f2.md) — **00C.7 is SSOT**  
**Notion:** [l5-l4-00c-parent-gap-b8e4f2](https://www.notion.so/l5-l4-00c-parent-gap-b8e4f2-36927693f55c81c19831c33eea84babd) — Status **Completed**

### Closeout (W1–W5)

| Deliverable | Path |
|-------------|------|
| L5 integrated evidence | `agentic_core/L5_safety/certification/integrated_l5_evidence.py` |
| 00C export profile | `agentic_core/L5_safety/runtime_gates/export_profile.py` |
| CI validator aliases | `ops_scripts/ci/verify_l5_*`, `verify_uwg_*` |
| Proof bundles | `l4_uwg_runtime_proof.json`, `runtime_gates_runtime_proof.json` |
| Edge tests | `test_integrated_l5_evidence_edge.py`, `test_runtime_exhaust_l5_cert_ref.py`, `test_commit_l5_cert_ref_edge.py` |

---

## Executive summary

| Pack | Implementation posture | Primary gap class |
|------|------------------------|-------------------|
| **00B** L4/UWG | **Strong runtime** (`agentic_core/L4_state/uwg/`, 219+ tests per [l4_uwg_requirements_traceability_matrix.md](l4_uwg_requirements_traceability_matrix.md)) | Parent REQ-ID validators mostly **DOC_ONLY**; traceability matrix predates REQ-ID rewrite |
| **00A** L5 | **Partial** (contracts + egress certifier + packet producer; [coverage_matrix.md](../l5-contracts/coverage_matrix.md)) | Runtime bind, HITL reclearance, cross-child consistency, cert_status vocabulary, release validators |
| **00C** Gates | **Strong mesh** (G01–G29 registered; 452 tests per [runtime_gates_doctrine_requirements_matrix.md](runtime_gates_doctrine_requirements_matrix.md)) | **Schema/semantics drift** vs new parent §4–§5 (disposition/result vocab, G21–G24 band mapping) |

---

## 00B — L4 / UWG (parent invariants)

### Mapped parent REQ_IDs → repo evidence

| REQ_ID | Spec intent | Repo signal | Gap |
|--------|-------------|-------------|-----|
| `REQ-UWG-SOLE-DURABLE-WRITE-001` | Sole UWG admission | `durable_write_gateway.py` `NON_AUTHORIZED_SOURCES`; `tests/uwg/test_no_direct_l4_write.py` | No Python symbol `uwg_sole_admission_validator`; release gate **DOC_ONLY** |
| `REQ-UWG-CLEARED-COMMIT-001` | Cleared CommitRequest only | `DurableWriteGateway.commit` clearance checks | Same — behavioral tests exist; named validator absent |
| `REQ-UWG-LOCK-RECEIPT-AUDIT-001` | Lock + receipt + audit append inseparable | Happy-path pipeline tests + certification bundles under `certification/.../uwg_commit_latest/` | Receipt field parity vs §5 contract not re-baselined to new parent field list |
| `REQ-UWG-VALIDATE-PRE-COMMIT-001` | Pre-commit validation | `_validate` in gateway | — |
| `REQ-L4-DURABLE-STATE-001` | L4 canonical SoR | `L4_state/contracts/records.py` (43+ frozen records) | Shadow-canonical violations in apps overlays not exhaustively proven at parent level |
| `REQ-L4-READ-PROJECTION-001` | Deterministic projections | `refresh_coordinator.py`, `l4.read_projection` spans | `l4_read_projection_validator` not located in CI by name |
| `REQ-L4-REPLAY-SNAPSHOT-001` | Replay manifest | Proof bundle + replay tests | — |
| `REQ-L4-AUDIT-LEDGER-CHAIN-001` | Hash-chained audit | `audit_ledger.py`, gap detection tests | — |
| `REQ-UWG-OBSERVABILITY-001` | All attempts logged | OTel span catalog (44 spans) | Dark-admission negative control not named in CI |
| `REQ-UWG-CONTEXT-INVARIANT-001` | Identical inputs → identical content_hash | E2E determinism tests | — |
| `REQ-UWG-STATE-AUDIT-REPLAY-CONSISTENCY-001` | Three-way consistency | `test_uwg_consistency_gate.py`, contract YAML | — |

### Positive evidence (do not re-build)

- [l4_uwg_requirements_traceability_matrix.md](l4_uwg_requirements_traceability_matrix.md) — row-level GREEN for **detailed** 00B.x children (pre-rewrite filenames).
- [l4_uwg_runtime_proof.json](l4_uwg_runtime_proof.json) — runtime proof bundle schema v3.
- Governance: `tests/governance/test_apps_rg_l4_uwg.py`, `test_l6_promotion_uwg_required.py`, `test_uwg_bypass_ratchet.py`.

### 00B gaps (actionable)

1. **REQ-ID traceability refresh** — Re-map §4 parent table to existing impl/tests (matrix still references `00B_L4_State_Archive_and_UWG_detailed.md`).
2. **Named release validators** — Parent §7 lists `uwg_*_validator` / `l4_*_validator` symbols; repo enforces behavior via pytest + FortKnox RTC rows, not those names.
3. **Child pack deferral** — Parent §13 accepts deferred child atomic tables; children `00B.1`–`00B.9` still own per-domain REQ rows — gap is **documentation completeness**, not missing UWG core.
4. **Dual UWG paths** — `agentic_core/UWG/` and `agentic_core/L4_state/uwg/` + `agentic_core/runtime/uwg/` — verify single admission SSOT (consolidation risk).

---

## 00A — L5 Governance Safety (parent invariants)

### Mapped parent REQ_IDs → repo evidence

| REQ_ID | Spec output | Repo signal | Gap |
|--------|-------------|-------------|-----|
| `REQ-L5-CERTIFICATION-NOT-DISPOSITION-001` | No live ALLOW/DENY | `FORBIDDEN_RUNTIME_DISPOSITIONS` in contracts | **MET** (structural + tests) |
| `REQ-L5-AUTHORITY-BINDING-001` | 4 binding fields on every cert | `L5Result` envelope; partial per-packet fields | Per-artifact field schematization **PARTIAL** (R0613) |
| `REQ-L5-ORIGIN-TRUST-001` | `origin_trust_class` | Contracts cite `L5CertificationResult` | **MET** at contract layer |
| `REQ-L5-HITL-RECLEAR-001` | `L5HITLReclearanceResult` | HITL gate in runtime_gates G06; no `L5HITLReclearanceResult` type | **GAP** — R0615 UNCOVERED |
| `REQ-L5-EGRESS-CERT-001` | `L5EgressCertification` | `egress_certifier.py` | Runtime invariant tests thin vs §5 evidence contract |
| `REQ-L5-REPLAY-AUDIT-CERT-001` | `L5ReplayAuditCertification` | Replay contracts exist in registry | No dedicated runtime certifier path located |
| `REQ-L5-STATIC-DRIFT-001` | `L5StaticDriftCertification` | Structure blueprint / CI drift tooling | Not wired as L5 cert artifact emitter |
| `REQ-L5-CONTEXT-INVARIANT-001` | Immutable cert context | Frozen dataclasses | **MET** structural |
| `REQ-L5-RUNTIME-BIND-001` | `RuntimeCertificationBinding` at run start | `contracts/runtime_binding.py` — **contracts only** | **GAP** — no producer at run start (prior plan W1 note) |
| `REQ-L5-CROSS-CHILD-CONSISTENCY-001` | Matching policy/blueprint across children | `tests/governance/test_l5_cross_child_certification.py` (partial) | **GAP** — R0621 UNCOVERED at contract/compiler level |
| `REQ-L5-NO-WRITE-001` | L5 never writes L4 | Anti-bypass tests block L5 direct write | **GAP** — no `l5_no_write_validator` / audit-ledger negative proof |

### Vocabulary drift (00A §5 vs code)

| Field | Parent spec | Current code |
|-------|-------------|--------------|
| `cert_status` | `certified`, `not_certified`, `expired`, `mismatched`, `pending_reclearance` | `L5_CERTIFIED`, `L5_NOT_CERTIFIED` (packet producer) |
| OTEL spans | `l5.certify`, `l5.authority_bind`, … | Partial / not uniformly emitted per §6 |

### 00A gaps (actionable)

1. Implement **RuntimeCertificationBinding producer** at run start (bind 7 linkage fields).
2. Add **`L5HITLReclearanceResult`** emission path tied to G06/HITL reclear flows.
3. Align **cert_status vocabulary** to parent 5-token set (or document bounded mapping table in 00A.8).
4. Wire **replay/audit** and **static drift** certifiers to emit §5 artifacts with `validator_receipt_id`.
5. Harden **cross-child** and **no-write** with release-gate scripts matching parent validator names.

---

## 00C — Runtime Gates (parent invariants)

### Cross-gate invariants (parent §4)

| REQ_ID | Parent rule | Repo signal | Gap |
|--------|-------------|-------------|-----|
| `REQ-GATE-VERDICT-SCHEMA-001` | 6 dispositions; 4 results; lowercase severity | 15 `Disposition`; 5 `Result` (+WARN); uppercase `Severity` | **SCHEMA DRIFT** — implementation follows **00C.7 detailed** doctrine, not new parent §5 JSON |
| `REQ-GATE-VERDICT-UNKNOWN-NOT-PASS-001` | UNKNOWN ≠ PASS | Tests + orchestrator | **MET** |
| `REQ-GATE-VERDICT-NA-JUSTIFY-001` | NA requires reason_codes | Validators in `tests/runtime_gates/` | **MET** |
| `REQ-GATE-VERDICT-NO-INFER-PASS-001` | Missing verdict = UNKNOWN | `gate_presence` tests / compiler | **MET** (CI/compiler path) |
| `REQ-GATE-G01`…`G29` | Per-gate parent rows | All 29 gates registered under `runtime_gates/g*.py` | **SEMANTIC DRIFT** G21–G24 band (see below) |

### G21–G29 numbering / semantics drift (critical)

New **parent** 00C §4 assigns:

| Gate | Parent 00C (2026 REQ-ID rewrite) | Implementation (`agentic_core/L5_safety/runtime_gates/`) |
|------|----------------------------------|----------------------------------------------------------|
| G21 | Output (payload safety) | `g21_output_schema.py` — schema conformance |
| G22 | Security (auth, integrity, freshness) | `g22_output_quality.py` — answer quality |
| G23 | Replay | `g23_security_leakage.py` — security/leakage |
| G24 | Audit (chain completeness) | `g24_determinism_replay.py` — replay/determinism |
| G25 | Anomaly | `g25_runtime_anomaly.py` | Align |
| G26 | Exit precondition | `g26_exit_disposition.py` | Align (name differs) |
| G27 | Write / UWG eligibility | `g27_durable_write_sovereignty.py` | Align |
| G28 | Trace completeness | `g28_audit_trace_completeness.py` | Parent G24=Audit vs impl G28=audit/trace — **role swap vs parent G24** |
| G29 | Learning firewall | `g29_learning_firewall.py` | Align |

Prior detailed doctrine (`00C.5` … G21–G24 Output/Security/Replay) matches **implementation** better than the **new parent** table. This is a **spec reconciliation** gap, not missing gate code.

### 00C gaps (actionable)

1. **Authority decision:** Treat parent §5 as target schema **or** mark parent as superseded by 00C.7 until reconciliation ADR.
2. **Disposition vocabulary:** Map 15-value mesh dispositions → parent 6-value `GateVerdict.disposition` (+ hints) for external artifacts / FortKnox.
3. **Gate band realignment** (if parent wins): Refactor G21–G24 modules or re-label `GATE_ID` with migration receipts and certification bundle regen.
4. **Named validators** — `gate_verdict_schema_validator` etc. exist as tests/scripts under `tests/runtime_gates/` and `scripts/verify_*` — link explicitly in traceability matrix.
5. **Invocation map** — Parent points to `00C.9`; ensure integrated runtime entrypoints invoke gates per map (spot-check `integrated_*_run.py`).

---

## Cross-pack boundary checks (MECE)

| Violation | Spec | Repo check |
|-----------|------|------------|
| L5 emits live disposition | 00A forbidden | Contracts forbid — **OK** |
| Gates emit final X3 | 00C forbidden | Tests `test_exit_x3_disposition_not_emitted_by_gate_layer` — **OK** |
| Gates write L4 | 00C forbidden | G27 emits `COMMIT_REQUEST` non-write — **OK** |
| L5 writes L4 | 00A forbidden | UWG anti-bypass includes L5 — **OK** |
| UWG skipped | 00B forbidden | Bypass ratchet + governance tests — **OK** |

---

## Suggested verification commands (review wave)

```bash
# L4/UWG
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/l4 tests/uwg -q --tb=no

# Runtime gates
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/runtime_gates tests/unit/agentic_core/L5_safety/runtime_gates -q --tb=no

# L5 contracts coverage
python tools/l5_contracts/build_coverage_matrix.py

# Governance boundaries
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/governance/test_l5_cross_child_certification.py tests/governance/test_apps_rg_l4_uwg.py -q --tb=no
```

---

## References

- [l4_uwg_requirements_traceability_matrix.md](l4_uwg_requirements_traceability_matrix.md)
- [runtime_gates_doctrine_requirements_matrix.md](runtime_gates_doctrine_requirements_matrix.md)
- [coverage_matrix.md](../l5-contracts/coverage_matrix.md) — rows R0612–R0622 (00A parent)
- [00X_Requirements_Traceability_and_No_Loss_Map.md](../../reference/00X_Requirements_Traceability_and_No_Loss_Map.md)
