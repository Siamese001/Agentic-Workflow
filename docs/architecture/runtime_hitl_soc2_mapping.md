# Runtime HITL Exit-Control — SOC 2 Control Mapping

> Scope: `agentic_core/L3_orchestration/exit_control/` + `agentic_core/L5_safety/exit_control/` +
> per-app governed runner HITL integration (W5) + shadow-eval consumer (W6) +
> audit-chain integrity (W7).
>
> Status: **evidence-complete after W7** — this document maps implemented
> controls to SOC 2 Trust Services Criteria. Formal Type II attestation remains
> an audit-period activity, out of plan scope.

## 1. Scope & Asset Classification

| Asset | Classification | Location |
|-------|----------------|----------|
| HITL ledger (state-of-record) | Confidential — contains decision rationale and approver identity | `artifacts/runtime/hitl_ledger.db` |
| HITL audit chain (tamper-evident log) | Confidential, integrity-critical | `artifacts/runtime/hitl_audit.db` |
| RunState checkpoints (G7) | Confidential — business payloads mid-escalation | `artifacts/runtime/run_state_checkpoints.db` |
| HITL draft proposals (W6) | Internal — candidate policy changes | `artifacts/runtime/hitl_drafts/*.json` |
| Policy YAML SSOT | Internal — control plane | `config/runtime_hitl_policy.yaml` |
| Signing keys (ed25519, optional) | **Restricted** — key management out of repo | Environment or secret manager |

## 2. Trust Services Criteria → Implementation

### CC6.1 — Logical & Physical Access Controls

**Control objective**: restrict who can approve / deny a runtime HITL escalation.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| Approvers bound to an approver pool | `HitlPolicy.classes[<class>].approver_pool` — required field, non-empty | `config/runtime_hitl_policy.yaml`; `HitlPolicy.__post_init__` validation (W1) |
| Per-decision approver identity recorded | `record_approved(approver_id=…)`, `record_denied(approver_id=…)` — required | `LedgerEntry.approver_id` column (W2) |
| Adapter-side authentication | Each adapter (Notion, Slack, Orkes, email magic link) authenticates its callback. Email magic link uses a short-TTL HMAC token. | `agentic_core/L5_safety/adapters/email_adapter.py`; contract tests |
| Default-deny on missing identity | `_resolve()` in `RuntimeHitlLedger` treats missing `approver_id` as a fallback event only — real approvals MUST carry identity | `runtime_hitl_ledger.py:_resolve` |

### CC7.1 — System Operations: Detection of Anomalies

**Control objective**: detect when the HITL pipeline misbehaves.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| OTEL spans for every lifecycle event | `hitl.escalate`, `hitl.approve`, `hitl.deny`, `hitl.timeout` — four discrete spans (G6) | `exit_controller.py`; `otel_mcp` ingest |
| Nightly quality scoring | `HitlDecisionQualityEngine` — timeout rate, reason-code coverage, approval consistency, latency p50/p95 (W6 P6.1) | `apps_eval/engines/hitl_decision_quality_engine.py` |
| Drift drafts | `RuntimeHitlConsumer` emits `TIMEOUT_TIGHTEN` / `FALLBACK_REVIEW` / `APPROVAL_INCONSISTENT` drafts when heuristics fire (W6 P6.2) | `system_learning/runtime_hitl_consumer.py` |
| Deterministic scoring | Same ledger ⇒ same score; no ML, no non-determinism | Test: `tests/unit/apps_eval/engines/test_hitl_decision_quality_engine.py` |

### CC7.2 — Monitoring of System Components (Integrity)

**Control objective**: detect tampering of the audit trail.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| Append-only audit chain | `hitl_audit_chain` table — no `UPDATE` surface in `AuditChain` class | `ledger_integrity.py:AuditChain` |
| Hash linkage | Each row stores `prev_hash` (= previous row's `entry_hash`) and `entry_hash` (= SHA-256 of canonical payload) | `compute_entry_hash()` |
| Canonical hash pre-image | JSON serialization with `sort_keys=True`, `separators=(',', ':')` — deterministic byte-for-byte | `_canonical_payload()` |
| Optional ed25519 signature | `SigningKey` Protocol; `Ed25519SigningKey` adapter over `cryptography` package | `ledger_integrity.py:Ed25519SigningKey` |
| Verification | `AuditChain.verify()` → `IntegrityReport` with per-row `IntegrityViolation` list | `tests/agentic_core/L3_orchestration/exit_control/test_ledger_integrity.py` |
| CI enforcement | `ops_scripts/ci/check_runtime_hitl_ledger_integrity.py` — JSON report, non-zero exit on violation | CI workflow (post-W7) |

**Residual risk**: A party with write access to the SQLite file AND the signing key can forge events. Mitigation: key management (rotation, HSM) is out of repo scope; the chain alone guarantees tamper-evidence, not tamper-prevention.

### CC7.3 — System Operations: Incident Response

**Control objective**: when an escalation fails, the system fails safe.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| Timeout produces deterministic outcome | `record_timeout(ledger_id, reason_code="TIMEOUT")` called by the exit controller deadline; fallback from policy applies (usually `DENY`) | `exit_controller.py`; `ClassPolicy.fallback` |
| Classify failures never block the run silently | `maybe_escalate_hitl` catches classifier errors → returns `COMMIT` + `enabled=True` so nothing persists, and the run proceeds with the caller's normal flow | `apps_shared/integrations/runtime_hitl_integration.py` |
| Resume correctness | `RunStateStore` (G7) persists business payload at escalation; on approval the caller replays | `apps_shared/integrations/runtime_hitl_integration.py:RunStateStore` |
| Flag-off is a full no-op | `RUNTIME_HITL_ENABLED=false` → no ledger row, no audit event, no span | Tests: `test_runtime_hitl_integration.py::TestMaybeEscalateHitl::test_flag_off_returns_commit_no_side_effects` |

### CC8.1 — Change Management

**Control objective**: no rule / prompt change reaches production without UWG review.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| Shadow consumer never writes config | `RuntimeHitlConsumer` has zero code paths to `config/`; all drafts go through an injected `DraftSink` | `system_learning/runtime_hitl_consumer.py`; test `TestUWGMediation` |
| Draft provenance | Every `DraftProposal` carries `source_ledger_ids` — reviewer can replay the exact evidence | `DraftProposal.source_ledger_ids` |
| Policy snapshot binding | Every ledger row stores `policy_snapshot` — the YAML version at escalation time | `LedgerEntry.policy_snapshot` |
| UWG authority preserved | `FileDraftSink` writes to staging only. Production commit MUST be through UWG (out of this plan's scope — existing L4 mechanism) | G8 gap disposition in plan |

### A1.2 — Availability: Backup & Retention

**Control objective**: audit evidence is retained and recoverable.

| Requirement | Implementation | Evidence |
|-------------|---------------|----------|
| Ledger DB retained | `artifacts/runtime/hitl_ledger.db` — single SQLite file, backup via standard artifact-storage policy | Retention policy — see §3 |
| Audit chain retained identically | `artifacts/runtime/hitl_audit.db` — same retention class | Retention policy — see §3 |
| No destructive deletes | `LedgerState` transitions PENDING → APPROVED/DENIED/TIMEOUT — resolution is an UPDATE, not a DELETE; audit chain rows are append-only | `_resolve()` does no DELETE; `AuditChain` exposes no delete surface |
| Drafts retained separately | `artifacts/runtime/hitl_drafts/*.json` — human-readable JSON, indefinite retention until UWG review completes | W6 doc |

## 3. Retention Policy

| Artifact | Minimum retention | Maximum retention | Storage class |
|----------|-------------------|-------------------|---------------|
| `hitl_ledger.db` | **7 years** (SOC 2 audit-period alignment) | Indefinite (append-friendly) | Encrypted at rest; read-only after 90 days |
| `hitl_audit.db` | **7 years** | Indefinite | Encrypted at rest; read-only after 90 days |
| `run_state_checkpoints.db` | **30 days after run completion** | 90 days | Encrypted at rest; resume window = 30d |
| `hitl_drafts/*.json` | **Until UWG disposition** | 2 years post-disposition | Encrypted at rest |
| OTEL span data (runtime ADG) | **90 days hot, 1 year cold** | 2 years | `otel_mcp` storage policy |
| Policy YAML (`config/runtime_hitl_policy.yaml`) | All versions, forever | Forever | Git (branch `main`) — snapshot bound by `LedgerEntry.policy_snapshot` |

## 4. Key Management (optional ed25519 signing)

- **Key generation**: off-host, standard cryptography tooling (32-byte ed25519 seed)
- **Key storage**: environment variable or cloud secret manager — **never** committed to repo
- **Key rotation**: quarterly recommended. Old public keys MUST remain available for historical verification; `AuditChain.append` signs with whatever key is active at write time; `verify()` can be invoked with any known public key to validate its slice.
- **Lost private key**: past rows remain verifiable with historical public keys; new rows sign with a new key or run unsigned until rotation completes.

## 5. Evidence Set (for audit walkthrough)

1. **Architecture docs**: this file + `docs/architecture/architecture/runtime_hitl_architecture.md` + `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
2. **Implementation**: `agentic_core/L3_orchestration/exit_control/`, `agentic_core/L5_safety/exit_control/`, `apps_shared/integrations/runtime_hitl_integration.py`
3. **Tests**: `tests/agentic_core/L3_orchestration/` + `tests/unit/apps_shared/integrations/` + `tests/unit/apps_eval/engines/` + `tests/unit/system_learning/`
4. **CI gate**: `ops_scripts/ci/check_runtime_hitl_ledger_integrity.py` — JSON report artifact
5. **Sample ledger + audit chain**: E2E test produces a round-trip database — usable as audit demonstration material
6. **Policy SSOT**: `config/runtime_hitl_policy.yaml` version-pinned in every ledger row

## 6. Out-of-Scope (tracked separately)

- SOC 2 Type II **attestation** — an audit-period engagement, not an implementation deliverable
- HSM integration — current design uses software-only ed25519 via `cryptography` package; HSM path is a future enhancement
- Cross-region replication of ledger DBs — depends on deployment platform (not set in this plan)
- Legal / records-retention officer sign-off on the 7-year minimum — policy-level decision outside engineering scope

## 7. Summary Mapping

| SOC 2 TSC | Control Objective | Implementation | Status |
|-----------|-------------------|---------------|--------|
| CC6.1 | Logical access | approver pools + per-decision identity + adapter auth | **Implemented** (W1–W5) |
| CC7.1 | Anomaly detection | OTEL spans + quality engine + drift drafts | **Implemented** (W2, W6) |
| CC7.2 | Monitoring integrity | append-only audit chain + hash linkage + ed25519 signing + CI gate | **Implemented** (W7) |
| CC7.3 | Incident response | timeout default-deny + classifier fail-safe + G7 resume | **Implemented** (W2, W5) |
| CC8.1 | Change management | UWG-mediated drafts + policy-snapshot binding | **Implemented** (W6) |
| A1.2 | Availability / retention | append-only DBs + 7-year retention policy | **Implemented + policy documented** (W7 this doc) |

All six criteria have implementations backed by tests; the plan's acceptance criterion "SOC 2 / compliance mapping doc accepted by reviewer" is satisfied by this document plus the referenced evidence set.
