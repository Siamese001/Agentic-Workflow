========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 00A_L5_Governance_Safety.md
Layer / subsystem: 00A — L5 Governance Safety (parent)
Parent file: docs/reference/README.md
Ownership surface: L5 governance certification evidence: authority, policy, registry, identity, capability, sandbox, origin trust, egress, HITL re-clearance, replay/audit certification, static governance/structure drift, and runtime certification binding.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: 00A owns governance certification evidence only. It does not emit live runtime dispositions (those belong to `00C` runtime gates and `05` Exit), it does not commit durable writes (UWG/`00B.6`), and it does not own end-to-end scenario proof (`99`).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `00A_L5_Governance_Safety.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the L5 certification evidence contract (the verb is "certify", never "approve a live run")
- per-domain parent REQ_IDs across the 8 L5 sub-domains
- the rule that certification evidence is consumed by 00C/05 at runtime but L5 does not itself decide the live disposition
- the runtime-certification binding contract (`00A.8`)

It does **not** own:
- per-domain detail (lives in `00A.1`..`00A.7a`, `00A.8`, `00A.8a`)
- live runtime dispositions (those are 00C / 05)
- durable write admission (00B.6 UWG)
- end-to-end scenario proof (99)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: policy versions, blueprint versions, registry digests, capability_token specs, sandbox envelopes, identity claims, egress policies, HITL re-clearance requests, replay/audit ledger snapshots, static-governance source.

**Downstream outputs**: `L5CertificationResult` artifacts and certification evidence packets — consumed by 00C (gate verdicts) and 05 (Exit checks).

**Forbidden behaviors**:
- 00A MUST NOT emit live `ALLOW`/`DENY` dispositions as its canonical output.
- 00A MUST NOT mutate L4 directly (UWG only).
- 00A MUST NOT replace 00C runtime gate verdicts.
- 00A MUST NOT make routing, retrieval, or execution decisions.

**Allowed outputs only**: certification statuses (`certified`, `not_certified`, `expired`, `mismatched`, `pending_reclearance`), evidence bundles, and binding receipts.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L5-*`. Per-domain children own their own sub-namespaces (e.g. `REQ-L5-AUTHORITY-*`, `REQ-L5-ORIGIN-TRUST-*`, `REQ-L5-EGRESS-*`).

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-L5-CERTIFICATION-NOT-DISPOSITION-001` | L5 MUST emit certification statuses only; it MUST NOT emit a live runtime disposition (`ALLOW`/`DENY` etc.) as its top-level output. | 00A | governance source | `L5CertificationResult` | output set ⊆ {`certified`, `not_certified`, `expired`, `mismatched`, `pending_reclearance`} | `l5.certify` parent span; status_code OK | `l5_certification_<domain>.json` | `validator: l5_output_vocabulary_validator` (release-gate) | `NC-L5-LIVE-DISPOSITION-LEAK-001`: emit `ALLOW_FINISH` from a 00A.x file | `l5_runtime_disposition_leak` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-L5-AUTHORITY-BINDING-001` | Every L5 certification MUST bind a `policy_hash`, `blueprint_hash`, `registry_digest_set`, and `capability_token_id` to the certification result. | 00A.2 | policy/blueprint/registry/capability | `L5CertificationResult` | result carries the 4 binding fields | `l5.authority_bind` span | `l5_certification_authority.json` | `validator: l5_authority_binding_validator` (release-gate) | `NC-L5-DRIFT-001`: certify with stale policy_hash | `l5_stale_policy_hash` | `byte_identical` | DOC_ONLY |
| `REQ-L5-ORIGIN-TRUST-001` | L5 MUST classify origin trust per source class and bind the classification to certification evidence. | 00A.3 | origin metadata | `L5CertificationResult` | result carries `origin_trust_class`, `content_boundary` | `l5.origin_trust` span | `l5_certification_origin_trust.json` | `validator: l5_origin_trust_validator` (release-gate) | `NC-L5-ORIGIN-MISLABEL-001`: untrusted source labeled trusted | `origin_trust_mislabel` | `byte_identical` | DOC_ONLY |
| `REQ-L5-HITL-RECLEAR-001` | When a run requires HITL re-clearance, L5 MUST emit a re-clearance certification before Exit can resume. | 00A.4 | HITL response | `L5HITLReclearanceResult` | result carries `human_response_hash`, `human_text_treated_as_data=true` | `l5.hitl_reclear` span | `l5_hitl_reclearance.json` | `validator: l5_hitl_reclearance_validator` (release-gate) | `NC-L5-HITL-INSTRUCTION-LEAK-001`: human reply elevated to instruction tier | `human_text_promoted_to_instruction` | `byte_identical` | DOC_ONLY |
| `REQ-L5-EGRESS-CERT-001` | L5 MUST certify egress class and provider governance binding before any external call. | 00A.5 | egress request | `L5EgressCertification` | result carries `egress_class`, `provider_id`, `provider_governance_hash` | `l5.egress_cert` span | `l5_egress_certification.json` | `validator: l5_egress_validator` (release-gate) | `NC-L5-DARK-PROVIDER-001`: provider with no governance hash certified | `provider_governance_hash_missing` | `byte_identical` | DOC_ONLY |
| `REQ-L5-REPLAY-AUDIT-CERT-001` | L5 MUST certify the replay snapshot manifest and the audit ledger pointer for every release-eligible run. | 00A.6 | replay manifest + audit ptr | `L5ReplayAuditCertification` | result carries `snapshot_manifest_hash`, `audit_ledger_ptr`, `audit_chain_hash` | `l5.replay_audit_cert` span | `l5_replay_audit_certification.json` | `validator: l5_replay_audit_validator` (release-gate) | `NC-L5-AUDIT-CHAIN-BREAK-001`: certify with broken audit chain | `audit_chain_break_certified` | `byte_identical` | DOC_ONLY |
| `REQ-L5-STATIC-DRIFT-001` | L5 MUST certify static governance source against expected structure-drift baselines. | 00A.7 | source repo state | `L5StaticDriftCertification` | result carries `repo_drift_findings[]`, `baseline_hash` | `l5.static_drift` span | `l5_static_drift.json` | `validator: l5_static_drift_validator` (release-gate + CI) | `NC-L5-DRIFT-MASKED-001`: drift present but findings list empty | `static_drift_findings_suppressed` | `byte_identical` | DOC_ONLY |
| `REQ-L5-CONTEXT-INVARIANT-001` | L5 governance context invariant MUST hold: certification context cannot be mutated post-issuance; only superseded by a new certification with monotonic version. | 00A.7a | certification artifact | (immutability) | `L5CertificationResult.context_locked=true`; supersession via new artifact only | `l5.context_lock` span | `l5_context_invariant.json` | `validator: l5_context_invariant_validator` (release-gate) | `NC-L5-CONTEXT-EDIT-001`: in-place edit of issued certification | `l5_certification_mutated_in_place` | `byte_identical` | DOC_ONLY |
| `REQ-L5-RUNTIME-BIND-001` | At run start, L5 MUST emit a `RuntimeCertificationBinding` linking `request_id`, `run_id`, `policy_hash`, `blueprint_hash`, `registry_digest_set`, `capability_token_id`, and `origin_trust_class`. Downstream layers consume this binding. | 00A.8 | run start | `RuntimeCertificationBinding` | binding carries the 7 linkage fields | `l5.runtime_bind` span | `runtime_certification_binding_<run_id>.json` | `validator: l5_runtime_bind_validator` (release-gate) | `NC-L5-BIND-MISSING-001`: run starts without binding | `runtime_bind_missing` | `byte_identical` | DOC_ONLY |
| `REQ-L5-CROSS-CHILD-CONSISTENCY-001` | All 00A child certifications MUST present mutually-consistent `policy_hash` and `blueprint_hash`; mismatch is FAIL. | 00A.8a | all 00A.x certs | (cross-check) | every certification artifact for the run carries identical `policy_hash`, `blueprint_hash` | `l5.cross_child_check` span | `l5_cross_child_consistency.json` | `validator: l5_cross_child_consistency_validator` (release-gate) | `NC-L5-MIXED-HASH-001`: 00A.3 cert uses a different policy_hash than 00A.5 cert | `cross_child_hash_drift` | `byte_identical` | DOC_ONLY |
| `REQ-L5-NO-WRITE-001` | L5 MUST NOT issue durable writes; it MAY only emit certification artifacts and consumes the UWG receipt as evidence (not as authority). | 00A | (governance) | (none) | absence of L5-originated writes in `audit_ledger` | NOT_APPLICABLE: anti-pattern detection in compiler | `compiler_anti_cheat_findings.json` | `validator: l5_no_write_validator` (release-gate) | `NC-L5-DIRECT-WRITE-001`: L5 module writes to L4 | `l5_attempted_durable_write` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every L5 certification artifact MUST carry:
- `req_id` (a `REQ-L5-*`)
- `request_id`, `run_id`, `trace_id`, `span_id`
- `policy_hash`, `blueprint_hash`, `registry_digest_set`
- `capability_token_id`
- `origin_trust_class`
- `cert_status` ∈ {`certified`, `not_certified`, `expired`, `mismatched`, `pending_reclearance`}
- `cert_evidence_refs[]`
- `replay_key`
- `validator_receipt_id`

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans (children of `l5.certify` parent):
- `l5.authority_bind`, `l5.origin_trust`, `l5.hitl_reclear`, `l5.egress_cert`, `l5.replay_audit_cert`, `l5.static_drift`, `l5.context_lock`, `l5.runtime_bind`, `l5.cross_child_check`

Required attributes on every L5 span: `req_id`, `cert_status`, `policy_hash`, `blueprint_hash`, `replay_key`. Status code: `OK` for `certified`/`pending_reclearance`; `ERROR` (with `attributes.fail_reason_code`) for `not_certified`/`expired`/`mismatched`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `l5_output_vocabulary_validator` (release-gate)
- `l5_authority_binding_validator` (release-gate)
- `l5_origin_trust_validator` (release-gate)
- `l5_hitl_reclearance_validator` (release-gate)
- `l5_egress_validator` (release-gate)
- `l5_replay_audit_validator` (release-gate)
- `l5_static_drift_validator` (release-gate + CI)
- `l5_context_invariant_validator` (release-gate)
- `l5_runtime_bind_validator` (release-gate)
- `l5_cross_child_consistency_validator` (release-gate)
- `l5_no_write_validator` (release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every `NC-L5-*` listed in §4 has a target REQ_ID, tamper kind, expected validator, and `Expected Fail Reason` matching the row. Cross-pack invariants:
- L5 MUST NOT redirect a runtime decision; tamper attempts that bypass 00C/05 are routed to `NC-GATE-*` / `NC-EXIT-*`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every L5 certification artifact MUST replay byte-identical for the same `(domain, policy_hash, blueprint_hash, registry_digest_set, input)`. Allowed nondeterminism: only `span_id`, `trace_id`, `cert_issued_at_utc`. Any other diff is release-blocking.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 00A row's `Release Gate` is `PASS` only when:
- L5 emits no live runtime dispositions
- All cross-child consistency checks pass
- No anti-cheat detector triggers
- Negative controls trip with the matching `Expected Fail Reason`

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L5 certification evidence parent invariants.

**Related files own**: per-domain detail in `00A.1`..`00A.8a`; the calibration / assurance / capability / guardrail / risk supporting docs.

**Forbidden duplicated ownership**: 00A MUST NOT redefine `GateVerdict` (00C) or `X3 disposition` (05). 00C/05 MUST NOT redefine certification status vocabulary.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`. The token `policy_certified` is allowed only inside an `L5CertificationResult.cert_status` field.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `00A.1_L5_Safety_Enforcement_Plane.md` — `REQ-L5-SAFETY-*`
- `00A.2_L5_Authority_Context_and_Registry_Binding.md` — `REQ-L5-AUTHORITY-*`
- `00A.3_L5_Origin_Trust_and_Content_Boundary.md` — `REQ-L5-ORIGIN-TRUST-*`
- `00A.4_L5_HITL_Reclearance_Human_Input_Gov.md` — `REQ-L5-HITL-*`
- `00A.5_L5_Egress_and_Provider_Governance.md` — `REQ-L5-EGRESS-*`
- `00A.6_L5_Replay_Audit_and_Certification_Evidence.md` — `REQ-L5-REPLAY-AUDIT-*`
- `00A.7_L5_Static_Governance_and_Structure_Drift.md` — `REQ-L5-STATIC-*`
- `00A.7a_L5_Governance_Context_Invariant.md` — `REQ-L5-CONTEXT-*`
- `00A.8_L5_Runtime_Certification_Binding.md` — `REQ-L5-BIND-*`
- `00A.8a_L5_Cross_Child_Certification_Consistency_Tests.md` — `REQ-L5-CROSS-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- The 8 L5 sub-domains each have a parent row pointing to their child.
- The certification status vocabulary in §2/§5 has exactly 5 tokens.
- The OTEL span contract in §6 names every L5 span and required attribute.
- The forbidden output vocabulary in §11 reproduces the global ban list.
- Release gate is fail-closed.

END OF 00A — L5 GOVERNANCE SAFETY PARENT
========================================================================================================================
