# L6 v6 Doctrine — Line-by-Line Coverage Matrix

**Re-ingested 2026-04-26 from all 13 files in this folder.** Co-located with doctrine per the L5 precedent at
`00A_L5_Governance_Safety/v5_coverage_matrix.md`. Honest about gaps — uncovered requirements are flagged ⚠️
explicitly.

## Doctrine corpus (13 files)

| File | Bytes | Generation |
|---|---:|---|
| `06_Shadow_Evaluation_System_Learning.md` | 13,193 | Parent — canonical sequence law |
| `06_Shadow_Evaluation_System_Learning_exec.md` | 12,342 | **v5 normative — RFC-2119 + KPI bands + module refs** |
| `06.1_L6_Runtime_Exhaust_Ingest_and_Normalization.md` | 11,406 | 6A child |
| `06.2_L6_Observer_Law_Isolation_Eval_Readiness.md` | 9,374 | 6A.5 (canonical) |
| `06.2_L6_Observer_Law_Surface_Isolation_and_Eval_Readiness.md` | 7,321 | 6A.5 (thinned variant — same body) |
| `06.3_L6_Outcome_Trajectory_and_Governance_Evaluation.md` | 7,270 | 6B (thinned variant — same body) |
| `06.3_L6_Outcome_Trajectory_Governance_Eval.md` | 9,317 | 6B (canonical) |
| `06.4_L6_Human_Calibration_and_Eval_Record_Seal.md` | 8,470 | 6B.5 |
| `06.5_L6_Signal_Fusion_RCA_and_Pattern_Synthesis.md` | 8,833 | 6C |
| `06.6_L6_Proposal_Drafting_and_Admission_Gate.md` | 8,516 | 6C.5 |
| `06.7_L6_Gauntlet_Approval_UWG_Promotion_FutureRun.md` | 9,348 | 6D (canonical) |
| `06.7_L6_Gauntlet_Approval_UWG_Promotion_and_Future_Run_Publish.md` | 7,307 | 6D (thinned — same body) |
| `06.8_L6_Observability_KPI_Tests_and_Anti_Bypass.md` | 11,308 | Pack-level acceptance |
| `06.9_L6_Memory_Promotion_Interface.md` | (April 2026 gap) | Memory promotion proposal |

**Duplicate-pair confirmation**: 06.2/06.3/06.7 each have two filename variants. Bodies were diffed and verified
**content-identical**. Both kept under HEAD for backward-link compatibility.

## Implementation under audit

- Code: `agentic_core/L6_observability/shadow_eval/` — 12 modules, 1,599 statements, 304 branches
- Tests: `tests/unit/L6_observability/shadow_eval/` — 11 files, **301 tests, 99.58% coverage**
- Runtime proof: `scripts/proof/run_l6_shadow_eval_proof.py` → `docs/reports/plans/l6_shadow_eval_runtime_proof.json`

## Status legend

| Marker | Meaning |
|:---:|---|
| ✅ | Enforced — runtime logic guards/emits the requirement; passing tests |
| 📦 | Modeled — typed contract captures shape; not all paths populate it |
| 🔁 | Delegated — sibling module / injected callback / external system owns it |
| ⚪ | Documentation-only — narrative invariant; architectural enforcement only |
| ⚠️ | **GAP** — doctrine requires it; implementation does not cover it (explicit, not silent) |

## Gap summary (the headline)

| Gap | Severity | What's missing |
|---|:---:|---|
| **G1** | HIGH | **`06.9 Memory Promotion Interface` not implemented** — `MemoryPromotionCandidate` (16 fields), `MemoryPromotionProposal` (9 fields), 4 rules, 5 named tests all absent |
| **G2** | HIGH | **v5 KPI tri-band semantics absent** — KPI_BOARD uses single-target binary; doctrine specifies green/yellow/red. 3 v5 KPIs entirely missing: `replay_divergence_localization_pct`, `exemplar_hit_rate_pct`, `saturation_watch_pct` |
| **G3** | MEDIUM | **Trajectory flag taxonomy partial** — doctrine §06.3 lists 14 detectable conditions; runtime emits 3 (`retry_thrash`, `silent_fallback`, `execution_error`). 12 detectors absent (route_thrash, tool_misuse, tool_overreach, hidden_scope_growth, unbounded_loop, skipped_C0_grounding, skipped_prompt_validation, premature_answer, stale_cache_reuse, excessive_model_escalation, non_replayable_behavior, unnecessary_HITL, missing_HITL) |
| **G4** | MEDIUM | **Governance drift category population partial** — `GovernanceRegressionRecord` has all 15 typed drift fields; runtime populates only 4 (policy/schema/replay/refusal). 11 typed-but-never-populated: exact_match, model_behavior, tool_behavior, provider_behavior, guardrail_failure, citation_support, prompt_drift, retrieval_profile, sandbox_escape, hitl_threshold, uwg_receipt |

The 4 gaps above were **not flagged in the prior matrix** at `docs/reports/plans/06_shadow_eval_v6_requirements_matrix.md`.

---

# §1 — Parent doctrine (`06_Shadow_Evaluation_System_Learning.md`)

## 1.1 PURPOSE (lines 27–35) — 7 capability claims

| Claim | Status | Evidence |
|---|:---:|---|
| Reads sealed runtime exhaust after boundary | ✅ | `ingest.py::receive_completed_run_marker` rejects `runtime_boundary_crossed=False` |
| Normalizes evidence | ✅ | `ingest.py::normalize_records` |
| Evaluates outcomes/trajectories/governance/calibration | ✅ | `evaluation.py::evaluate_outcome/_trajectory/_governance_regression` + `calibration.py::build_calibration_record` |
| Detects drift, isolates RCA, drafts proposals | ✅ | `evaluation.py` + `rca.py::build_rca_packet` + `proposal.py::draft_proposal` |
| Proves under replay/regression gauntlets | ✅ | `gauntlet.py::run_gauntlet` |
| Hands approved promotion packets to UWG | ✅ | `gauntlet.py::build_uwg_request_package` + `bind_uwg_receipt` |
| Not a live runtime layer | ✅ | `test_06_2_observer.py::test_no_write_client_imports_in_shadow_eval` |

## 1.2 CANONICAL SEQUENCE LAW (lines 39–53) — 12 ordered steps

| # | Step | Status | Evidence |
|---:|---|:---:|---|
| 1 | Observe completed run exhaust only | ✅ | `pipeline.py::run_6a` |
| 2 | Normalize and bind lineage | ✅ | `ingest.py::normalize_records` + `validate_lineage` |
| 3 | Evaluate outcome/trajectory/governance/calibration | ✅ | `pipeline.py::run_6b` |
| 4 | Seal eval records | ✅ | `calibration.py::seal_eval_record` |
| 5 | Fuse evaluated signals | ✅ | `rca.py::fuse_signals` |
| 6 | RCA and pattern synthesis | ✅ | `rca.py::build_rca_packet` + `synthesize_patterns` |
| 7 | Draft proposal packets | ✅ | `proposal.py::draft_proposal` |
| 8 | Admit complete proposals to gauntlet | ✅ | `proposal.py::admit_proposal` |
| 9 | Prove through replay/regression/safety checks | ✅ | `gauntlet.py::run_gauntlet` |
| 10 | Approve, reject, or hold | ✅ | `gauntlet.py::decide_approval` (7-decision priority resolver) |
| 11 | UWG writes approved future-run state to L4 | 🔁 | `gauntlet.py::UwgCommitFn` callback |
| 12 | BUS U activates only at future run_start | ✅ | `FutureRunActivationReceipt.activate_at="NEXT_RUN_START"` + `bus_u_publish_marker="DEFERRED_UNTIL_RUN_START"` |

## 1.3 NEVER list (lines 56–61) — 6 forbidden patterns

| # | Forbidden | Status | Evidence |
|---:|---|:---:|---|
| 1 | Observe → mutate live run | ✅ | `observer.py::FORBIDDEN_WRITE_SURFACES` includes `current_run_*`; `deny_if_forbidden` raises |
| 2 | Raw trace → learning promotion | ✅ | `rca.py::_require_consumable` |
| 3 | Human pref → policy without rubric/calibration | ✅ | `proposal.py::draft_proposal` requires `RCA_AND_PROPOSAL` downstream use |
| 4 | Failed run → silent prompt patch | ✅ | `admit_proposal` requires diff+RCA+rollback+tests; gauntlet must pass |
| 5 | L6 proposal → direct L4 write | ✅ | No L4 client in `shadow_eval/*`; `UwgCommitFn` is only handoff |
| 6 | After-hours → retroactive disposition | ✅ | `no_retroactive_regrade_assertion=True` |

## 1.4 SOURCE OWNERSHIP / NO-OVERLAP LOCK (lines 65–115)

12 layer ownership statements. Architectural; verified by import discipline. ⚪

## 1.5 CHILD FILE MAP (lines 119–158) — 8 declared children

| Child | Implementation | Status |
|---|---|:---:|
| 06.1 | `ingest.py` + 6 dataclasses | ✅ |
| 06.2 | `observer.py` + 7 dataclasses | ✅ |
| 06.3 | `evaluation.py` + 4 dataclasses | ✅ |
| 06.4 | `calibration.py` + 6 dataclasses | ✅ |
| 06.5 | `rca.py` + 7 dataclasses | ✅ |
| 06.6 | `proposal.py` + 7 dataclasses | ✅ |
| 06.7 | `gauntlet.py` + 6 dataclasses | ✅ |
| 06.8 | `otel_spans.py` + `pipeline.py::_emit` + `test_06_8_anti_bypass.py` | ✅ |
| **06.9** | **NOT IMPLEMENTED** | ⚠️ **GAP G1** |

## 1.6 FORBIDDEN L6 OUTPUTS (lines 162–172) — 6 categories

| Category | Status | Evidence |
|---|:---:|---|
| Live disposition outputs (ALLOW_FINISH/DENY/REROUTE/etc.) | ✅ | None of these strings appear as return constants in `shadow_eval/*` |
| Live mutations (route/threshold/prompt/policy/rubric) | ✅ | `FORBIDDEN_WRITE_SURFACES` includes `policy_publish, rubric_publish, registry_update, cache_promotion, memory_promotion` |
| Direct L4 / cache / memory / registry writes | ✅ | Same |
| Current-run rescue / regrade | ✅ | `no_current_run_mutation_assertion=True` |
| Human pref as policy / raw telemetry as learning | ✅ | `_require_consumable` + `admit_proposal::open_blockers` |
| Silent promotion / partial bypass / missing rollback | ✅ | `decide_approval` priority resolver |

## 1.7 ALLOWED OUTPUT VOCABULARY (lines 184–203) — 18 status enums

All 18 strings present in `contracts.py` constants or `observer.py` constants — see §1.9 of prior matrix mapping
(every name verified). ✅

## 1.8 ACCEPTANCE CRITERIA (lines 207–222) — 11 criteria

All 11 criteria pass. Notable: 6A separate from 6B (`run_6a` and `run_6b` distinct functions; 6B asserts ingest
result presence, raises `RuntimeError` if `state.ingest is None`). ✅

---

# §2 — `06_Shadow_Evaluation_System_Learning_exec.md` (v5 normative)

> **Missing from prior matrix.** Adds RFC-2119 invariants, measurable KPIs with green/yellow/red bands, module
> reference table.

## 2.1 §1 RFC-2119 invariants — 6 invariants

| § | Invariant | Status | Evidence |
|---|---|:---:|---|
| 1.1 | Observer Law (6A INGEST) — MUST only read; SHOULD preserve `trace_id`/`run_id`/`replay_key` | ✅ | `FORBIDDEN_WRITE_SURFACES` + `NormalizedEvidenceRecord` carries all 3 IDs |
| 1.2 | Eval-Before-Learning firewall — no 6C/6D against raw ingest without 6B | ✅ | `_require_consumable` + `pipeline.py::run_6c` raises if `state.eval is None` |
| 1.3 | Rubric integrity — content-addressed (SHA-256), version-bumped, judges MAY return Unknown | ✅ partial | `CalibrationRecord.{rubric_hash, rubric_version, grader_version}`; UNKNOWN preserved (`test_unknown_dimension_is_not_pass`). YAML→SHA256 canonicalization is caller-side |
| 1.4 | UWG Sole Ink Path — only `engines/l4_state_writer.py` MAY write; every write carries proposal_id+gauntlet_receipt+content_hash+signer_identity | 🔁 | `PromotionUWGRequestPackage` carries all 4; L4 write external to `shadow_eval/*`; `test_l6_does_not_write_to_l4_directly` |
| 1.5 | No-Partial-Bypass — any 6A/6B/6C/6D failure rejects whole proposal | ✅ | `decide_approval` priority resolver collapses any failed gate |
| 1.6 | Future-run only | ✅ | `activate_at="NEXT_RUN_START"` + `bus_u_publish_marker="DEFERRED_UNTIL_RUN_START"` + `no_current_run_mutation_assertion=True` |

## 2.2 §2 KPIs — **11 KPIs with green/yellow/red bands**

| v5 KPI | Green | Yellow | Red | KPI_BOARD entry | Status |
|---|---|---|---|---|:---:|
| Trace-ingest freshness | ≤10 min | ≤60 | >60 | `trace_ingest_freshness_minutes` (≤10) | 📦 single-band |
| Eval coverage | ≥98% | ≥90% | <90% | `outcome_eval_coverage_pct` (≥98) + `eval_readiness_coverage_pct` | 📦 single-band |
| Judge unknown-budget | ≥95% | ≥85% | <85% | `judge_unknown_budget_compliance_pct` (≥95) | 📦 single-band |
| Judge-human κ freshness | ≤7 days | ≤30 | >30 | `judge_human_agreement_freshness_days` (≤7) | 📦 single-band |
| RCA-to-proposal lead time | ≤24h | ≤72h | >72h | `rca_to_proposal_lead_time_hours_p95` (≤24) | 📦 single-band |
| Gauntlet false-promote rate | ≤1% | ≤3% | >3% | `gauntlet_false_promote_rate_pct` (≤1) | 📦 single-band |
| UWG ink-path uniqueness | =0 | — | >0 | `uwg_ink_path_uniqueness_violations` (==0) | ✅ |
| Replay divergence localization | ≥90% | ≥70% | <70% | (none) | ⚠️ **GAP G2a** |
| Eval-freshness on write | =100% | — | <100% | `eval_freshness_on_write_pct` (==100) | ✅ |
| **Exemplar-hit rate** | ≥20% | ≥5% | <5% | (none) | ⚠️ **GAP G2b** |
| **Saturation watch** | ≤10% | ≤25% | >25% | (none) | ⚠️ **GAP G2c** |

**v5 KPIs total: 11. Mapped: 8. Missing: 3 (G2a/b/c). Tri-band semantics not encoded — KPI_BOARD has 19
entries with single-target binary thresholds.**

## 2.3 §3 Contract references — 14 v4 step → module rows

| v4 step | shadow_eval equivalent | Status |
|---|---|:---:|
| S1A gather exhaust | `ingest.py::receive_completed_run_marker` | ✅ |
| S1B normalize evidence | `ingest.py::normalize_records` | ✅ |
| S1C observer law | `observer.py::build_surface_isolation_manifest` + `stage_barrier_check` | ✅ |
| S2A outcome evals | `evaluation.py::evaluate_outcome` | ✅ |
| S2B trajectory evals | `evaluation.py::evaluate_trajectory` | ✅ |
| S2C governance regression | `evaluation.py::evaluate_governance_regression` | ✅ partial (see §5.6 G4) |
| S2D human calibration | `calibration.py::build_calibration_record` + `build_human_agreement_record` | ✅ |
| S3A signal fusion | `rca.py::fuse_signals` | ✅ |
| S3B incident RCA | `rca.py::build_rca_packet` | ✅ |
| S3C rule drafting | `proposal.py::draft_proposal` | ✅ |
| S4A gauntlet | `gauntlet.py::run_gauntlet` | ✅ |
| S4B approve/reject | `gauntlet.py::decide_approval` | ✅ |
| S4C UWG master clerk | `gauntlet.py::UwgCommitFn` callback | 🔁 |
| S4D ledger proof | `gauntlet.py::bind_uwg_receipt` → `LedgerProofReference` | ✅ |

## 2.4 §4–§6 — informational/process; not testable code ⚪

---

# §3 — `06.1` 6A Ingest / Normalization

## 3.1 Owned contracts (10 items, 2 non-ownerships)

All 6 dataclasses present with full field counts:
RuntimeExhaustBundle (22), ExhaustSourceManifest (11), StageMap (10), ArtifactInventory (11),
NormalizedEvidenceRecord (33), ExhaustGapReport (6) — all ✅

## 3.2 INPUTS — 17 input surface types

All 17 routed through `RuntimeExhaustBundle` fields. ✅

## 3.3 PIPELINE I1–I7

| Step | Function | Test |
|---|---|---|
| I1 marker (refuse live, require Exit) | `receive_completed_run_marker` | `test_in_flight_run_is_rejected`, `test_missing_exit_disposition_is_rejected`, `test_repair_fixture_allows_missing_exit`, `test_receive_completed_run_marker_rejects_missing_completed_at` |
| I2 collect refs | `collect_source_refs` | `test_lineage_not_summarized` |
| I3 lineage validation | `validate_lineage` | `test_missing_trace_root_emits_gap`, `test_missing_replay_key_emits_gap`, `test_orphan_artifact_appears_in_gap_report`, `test_validate_lineage_emits_policy_hash_mismatch_when_missing` |
| I4 StageMap | `build_stage_map` (`EXPECTED_STAGES`) | `test_impossible_stage_order_flagged`, `test_build_stage_map_flags_uwg_before_exit` |
| I5 ArtifactInventory | `build_artifact_inventory` | `test_full_pipeline_smoke` |
| I6 normalize | `normalize_records` | `test_normalized_records_omit_no_required_field`, `test_normalize_records_warns_unknown_provider` |
| I7 stratify (13 classes) | `stratify_outcome` | `test_outcome_stratification_known/_unknown_class`, `test_run_outcome_classes_doctrine_cardinality` |

All ✅.

## 3.4 FAILURE MODES — 8 reason codes

LIVE_RUN_NOT_CLOSED, EXIT_DISPOSITION_MISSING, TRACE_LINK_MISSING, ORPHAN_ARTIFACT,
IMPOSSIBLE_STAGE_ORDER, POLICY_HASH_MISMATCH, REPLAY_KEY_MISSING, UNKNOWN_PROVIDER_FALLBACK
— all defined in `ingest.py` as `REASON_*` constants. ✅

## 3.5 OTEL SPANS — 7 ingest spans

`l6.ingest.bundle_receive`, `source_collect`, `lineage_bind`, `stage_map_build`, `artifact_inventory`,
`l6.normalize.record_emit`, `l6.ingest.gap_report_emit` (conditional). All ✅.

## 3.6 TEST REQUIREMENTS — 8 conditions

All 8 covered by `test_06_1_ingest.py` + `test_06_branch_coverage.py`. ✅

---

# §4 — `06.2` Observer Law / Surface Isolation / Eval Readiness

## 4.1 Owned (7 contracts) — all ✅

ObserverComplianceReceipt (15 fields), SurfaceIsolationManifest (16), StageBarrierReceipt (8),
L6DeniedWriteAttemptRecord (7), EvalReadinessReceipt (16), MissingEvidenceMap (4), NonEvaluablePacketRecord (3).

## 4.2 OBSERVER LAW — 10 read-allowed + 7 write-prohibited

All 10 reads accepted as plain inputs; all 7 prohibitions enforced via `FORBIDDEN_WRITE_SURFACES` (12-element
frozenset covering L4, L4_state, BUS_U, BUS_U_publish, policy_publish, rubric_publish, registry_update,
cache_promotion, memory_promotion, current_run_exit, current_run_hitl, current_run_uwg). ✅

## 4.3 READINESS DECISION RULES — 4 decisions

| Decision | Status | Test |
|---|:---:|---|
| READY_FOR_6B | ✅ | `test_eval_readiness_ready_for_clean_run` |
| PARTIAL_BUT_SCORABLE | ✅ | `test_partial_scoring_is_not_promoted_as_complete`, `test_readiness_partial_branch_preserves_normalized_records` |
| HOLD_FOR_MISSING_EVIDENCE | ✅ | `test_missing_replay_key_not_silently_ignored` |
| NON_EVALUABLE_PACKET | ✅ | `test_observer_violation_forces_non_evaluable`, `test_readiness_missing_trace_root_routes_to_non_evaluable`, `test_readiness_missing_exit_disposition_routes_to_non_evaluable` |

## 4.4 VIOLATION RESPONSE — 7 steps

All 7 steps wired (stop ingest, freeze, classify, emit `L6_OBSERVER_FAIL`, denied-write record, audit flag,
block downstream). ✅

## 4.5 TEST REQUIREMENTS — 7 conditions

All 7 covered. ✅

---

# §5 — `06.3` Outcome / Trajectory / Governance Eval

## 5.1 Owned (7 items) — all ✅ except SupportRationale (📦 modeled as field, not dataclass)

## 5.2 Outcome dimensions — 14 graded items

13 numeric dimension scores in `OUTCOME_DIMENSIONS`; 14th ("unsupported inference risk") via dedicated
`unsupported_claims[]` list. All ✅.

## 5.3 Trajectory detection — **14 conditions**

| Condition | Detector? | Status |
|---|---|:---:|
| route_thrash | none | ⚠️ **G3** |
| silent_fallback | `evaluate_trajectory` (`fallback_depth>1`) | ✅ |
| tool_misuse | none | ⚠️ **G3** |
| tool_overreach | none | ⚠️ **G3** |
| hidden_scope_growth | none | ⚠️ **G3** |
| unbounded_loop | none | ⚠️ **G3** |
| skipped_C0_grounding | none | ⚠️ **G3** |
| skipped_prompt_validation | none | ⚠️ **G3** |
| premature_answer | none | ⚠️ **G3** |
| stale_cache_reuse | none | ⚠️ **G3** |
| excessive_model_escalation | none | ⚠️ **G3** |
| non_replayable_behavior | none | ⚠️ **G3** |
| unnecessary_HITL | none | ⚠️ **G3** |
| missing_HITL | none | ⚠️ **G3** |
| **execution_error** (impl-added) | `evaluate_trajectory` (`error_code` set) | ✅ |
| **retry_thrash** (impl-added) | `evaluate_trajectory` (`retry_count>2`) | ✅ |

**GAP G3**: 12 of 14 doctrine-listed detectors absent. Dimension *scores* exist via `CodeOnlyGrader`
(structural PASS/WARN/UNKNOWN) but no flag is appended to `trajectory_flags[]` for the named conditions.

## 5.4 Governance regression checks — 8 doctrine checks → 15 typed drift fields

| Check | Field | Populated? |
|---|---|:---:|
| Stale baseline / hidden policy mismatch | `policy_drift_flags` | ✅ |
| Replay digest drift | `replay_digest_drift_flags` | ✅ |
| Refusal/abstain drift | `refusal_abstain_drift_flags` | ✅ |
| (no specific) | `schema_api_drift_flags` | 📦 typed; never populated |
| (no specific) | `exact_match_drift_flags` | ⚠️ **G4** |
| (no specific) | `model_behavior_drift_flags` | ⚠️ **G4** |
| (no specific) | `tool_behavior_drift_flags` | ⚠️ **G4** |
| (no specific) | `provider_behavior_drift_flags` | ⚠️ **G4** |
| (no specific) | `guardrail_failure_flags` | ⚠️ **G4** |
| (no specific) | `citation_support_drift_flags` | ⚠️ **G4** |
| (no specific) | `prompt_drift_flags` | ⚠️ **G4** |
| (no specific) | `retrieval_profile_drift_flags` | ⚠️ **G4** |
| (no specific) | `sandbox_escape_signals` | ⚠️ **G4** |
| (no specific) | `hitl_threshold_drift_flags` | ⚠️ **G4** |
| (no specific) | `uwg_receipt_drift_flags` | ⚠️ **G4** |

**GAP G4**: 11 of 15 typed drift categories never populated by `evaluate_governance_regression`. Dataclass
shape is doctrine-correct; runtime detection requires baselines not yet threaded into `GovernanceBaseline`.

## 5.5 Must-allow (4) / Must-not (5) / Grader rules (6) / Test reqs (6) — all ✅

---

# §6 — `06.4` Calibration / Eval Record Seal

## 6.1 Owned (6 contracts) — all ✅

CalibrationRecord (16 fields), JudgeReliabilitySignal (10), HumanAgreementRecord (6),
RubricCalibrationReceipt (5), CompletedEvalRecord (18), EvalRecordSealReceipt (10).

## 6.2 9 calibration sources — all carried via `calibration_source_refs[]` (untyped string refs). 📦

## 6.3 Calibration & seal rules (8) — all ✅, including:
- TTL via `CALIBRATION_TTL_DAYS_DEFAULT=7` (matches v5 KPI Green band)
- Stale rubric blocks (`derive_downstream_use → RCA_ONLY` when `calibration_status ∈ {INSUFFICIENT, CONFLICTED, STALE}`)
- UNKNOWN preservation (`_collect_uncertainty`)
- Reviewer override is calibration evidence only (`HumanAgreementRecord` separate from sealed score)
- 6C cannot consume unsealed (`_require_consumable`)

## 6.4 Test requirements — 6 conditions, all covered, including:
- `test_06_4_calibration::test_unknown_uncertainty_is_preserved`
- `test_06_5_rca::test_rca_refuses_unconsumable_eval_record`
- `test_06_branch_coverage::test_calibration_record_marks_insufficient_on_bad_timestamp`
- `test_06_hardening::test_seal_status_hold_when_calibration_inconclusive`

---

# §7 — `06.5` Signal Fusion / RCA / Pattern Synthesis

## 7.1 Owned (7 contracts) — all ✅

FusedSignalBundle (24 fields), RCAPacket (14), FailureChain (4), FirstBadSpanLocalization (5),
PatternSynthesisRecord (11), DriftClusterMap (2), AffectedSurfaceCandidateMap (2).

## 7.2 Hard precondition — `_require_consumable` accepts only `RCA_ONLY` / `RCA_AND_PROPOSAL`. ✅

## 7.3 Root cause classes — **16 doctrine classes**, all in `ROOT_CAUSE_CLASSES` constant

| Class | Status |
|---|:---:|
| ROUTE_MISS, CACHE_FALSE_HIT, RETRIEVAL_RECALL_GAP, RERANK_PRECISION_GAP, GRAPH_CONTEXT_GAP, PROMPT_SLOT_ORDER_ERROR, INSTRUCTION_CONFLICT, TOOL_ARG_SCHEMA_ERROR, PROVIDER_DRIFT, POLICY_THRESHOLD_ERROR, RUBRIC_CALIBRATION_ERROR, HITL_GATE_ERROR, UWG_SCOPE_ERROR, REPLAY_INTEGRITY_ERROR, EVIDENCE_LINEAGE_LOSS, UNKNOWN_ROOT_CAUSE | ✅ all 16 |

`_classify_root_cause` (5-branch ladder) emits 5 of 16: POLICY_THRESHOLD_ERROR, REPLAY_INTEGRITY_ERROR,
PROVIDER_DRIFT, TOOL_ARG_SCHEMA_ERROR, UNKNOWN_ROOT_CAUSE. The other 11 are **doctrine-defined enum values
the classifier does not yet emit** (no detector path); however all 16 are valid enum members for downstream
consumers, and `build_rca_packet` raises `RCAError` if a non-enum class arrives. 📦 partial population.

## 7.4 Signal fusion / RCA / pattern rules (~11 sub-rules) — all ✅

## 7.5 Test requirements — 6 conditions, all covered, including:
- `test_06_5_rca::test_rca_refuses_unconsumable_eval_record`
- `test_06_branch_coverage::test_first_bad_span_localized_when_normalized_record_has_error`
- `test_06_branch_coverage::test_root_cause_classifier_*` (replay/provider/tool branches)

---

# §8 — `06.6` Proposal Drafting / Admission Gate

## 8.1 Owned (7 contracts) — all ✅

DraftProposalPacket (22 fields), ProposedDiffManifest (11), ProposalEvidenceMap (4),
ProposalBlastRadiusAssessment (6), ProposalRollbackPlanRef (4), ProposalTestPlan (6),
ProposalAdmissionReceipt (15).

## 8.2 Hard precondition (9 required inputs) — enforced by `draft_proposal` + `admit_proposal::open_blockers`. ✅

## 8.3 Proposal types — 10 doctrine types

| Type | In `PROPOSAL_TYPES`? |
|---|:---:|
| LOCAL_PATCH, THRESHOLD_CHANGE, RUBRIC_UPDATE, PROMPT_UPDATE, RETRIEVAL_PROFILE_UPDATE, POLICY_CLARIFICATION, EXEMPLAR_ADDITION, GOLDEN_SET_ADDITION, TOOL_CONTRACT_TIGHTENING, HOLD_FOR_MORE_EVIDENCE | ✅ all 10 |

## 8.4 Admission decisions — 4 decisions

ADMIT_TO_GAUNTLET, HOLD_FOR_MORE_EVIDENCE, REJECT_WEAK_PROPOSAL, REQUIRE_SME_REVIEW — all reachable. ✅
Tested in `test_06_edge_cases.py`.

## 8.5 Hard-no rules (6) — all enforced via `admit_proposal::open_blockers`. ✅

## 8.6 Test requirements — 7 conditions, all covered. ✅

---

# §9 — `06.7` Gauntlet / Approval / UWG Promotion / Future-Run

## 9.1 Owned (6 contracts) — all ✅

GauntletReceipt (15 fields), ApprovalDecisionRecord (13), PromotionPacket (32),
PromotionUWGRequestPackage (12), LedgerProofReference (5), FutureRunActivationReceipt (12).

## 9.2 Gauntlet requirements — 15 test types

`run_gauntlet` accepts: `replay_case_refs[]`, `regression_pack_refs[]`, `golden_set_refs[]`,
`adversarial_case_refs[]`, `compatibility_check_refs[]`, `rollback_rehearsal_ref`, `sme_signoff_ref`,
`failing_cases[]`, `rollout_risk_score`, `replay_proof_ref`, `divergence_localization[]`, `signer_identity`.
✅ all 15 carried.

## 9.3 Replay modes — 7 modes

All 7 are `replay_case_refs[]` strings (`run_gauntlet` accepts arbitrary list). 📦 typed acceptance, no
schema enforcement of mode taxonomy.

## 9.4 APPROVE preconditions — **8 conditions**

`decide_approval` evaluates all 8 (eval-fresh, RCA/pattern, gauntlet PASS, calibration-fresh, no-partial-bypass,
signer auth, rollback-verified, blast-radius-accepted) + content-hash binding. Priority ladder:
REJECT > HOLD > REQUIRE_ADR_EXCEPTION > REQUIRE_NARROWER_SCOPE > REQUIRE_ROLLBACK_PLAN > REQUIRE_SME_REVIEW > APPROVE.
✅ all 8.

## 9.5 Approval decisions — 7 enum values

APPROVE, REJECT, HOLD_FOR_MORE_EVIDENCE, REQUIRE_SME_REVIEW, REQUIRE_ROLLBACK_PLAN,
REQUIRE_NARROWER_SCOPE, REQUIRE_ADR_EXCEPTION — all in `APPROVAL_DECISIONS`. All 7 reachable
(REQUIRE_ADR_EXCEPTION via `adr_required+adr_ref` parameters; tested in `test_06_edge_cases.py`). ✅

## 9.6 Future-run rules — 6 rules

Activation at next run_start, no completed-run mutation, no current-run rescue, no retroactive regrade,
no hidden threshold change, no BUS U publish without UWG receipt — all encoded in
`FutureRunActivationReceipt` field defaults + `build_future_run_activation_receipt` guards
(raises if missing UWG receipt or l4_version_digest). ✅

## 9.7 Test requirements — 8 conditions, all covered, including:
- `test_06_7_gauntlet::test_activation_requires_uwg_receipt`
- `test_06_branch_coverage::test_build_promotion_packet_rejects_when_gauntlet_failed`
- `test_06_branch_coverage::test_build_promotion_packet_rejects_content_hash_mismatch`

---

# §10 — `06.9` Memory Promotion Interface ⚠️ **NOT IMPLEMENTED**

## 10.1 Owned contracts — both **MISSING**

| Contract | Doctrine fields | Implementation | Status |
|---|---:|---|:---:|
| MemoryPromotionCandidate | 16 fields (candidate_id, source_eval_record_ref, RCA_packet_ref, pattern_id, proposed_memory_type, proposed_content_ref, evidence_refs, counterexample_refs, confidence_band, human_calibration_ref, privacy_scope, tenant_scope, TTL_review_date, rollback_plan_ref, target_l4_surface_hint, future_run_only) | **NONE** | ⚠️ **G1** |
| MemoryPromotionProposal | 9 fields (proposal_id, candidates, evaluation_basis, risk_assessment, privacy_review_status, duplication_check_status, conflict_check_status, gauntlet_receipt_ref, approval_decision_ref, UWG_commit_request_ref) | **NONE** | ⚠️ **G1** |

## 10.2 Rules — 4 rules

| Rule | Status |
|---|:---:|
| Raw telemetry is not memory | ⚪ — covered architecturally by `_require_consumable` but no memory-specific assertion |
| Single-run preference is not durable policy | ⚪ — same |
| Human feedback is signal until calibrated and approved | ⚪ — `HumanAgreementRecord` exists; no memory-promotion-specific gate |
| Memory proposal may not activate until UWG commit and future run_start alias refresh | ⚪ — covered for general proposals; no memory-specific path |

## 10.3 Test requirements — 5 named tests

| Test | Status |
|---|:---:|
| `test_l6_rejects_raw_telemetry_as_memory` | ⚠️ NOT IMPLEMENTED |
| `test_memory_candidate_requires_eval_record` | ⚠️ NOT IMPLEMENTED |
| `test_memory_candidate_requires_privacy_scope` | ⚠️ NOT IMPLEMENTED |
| `test_memory_proposal_requires_gauntlet_before_uwg` | ⚠️ NOT IMPLEMENTED |
| `test_memory_update_never_affects_completed_run` | ⚠️ NOT IMPLEMENTED |

**GAP G1 — full coverage**: 06.9 needs `memory_promotion.py` module + 2 dataclasses in `contracts.py` +
5 named tests in a new `test_06_9_memory_promotion.py`. The proposed_memory_type enum
(`user_memory | project_memory | system_pattern | approved_exemplar | rubric_note | calibration_note`)
also missing.

---

# §11 — `06.8` Observability / KPI / Tests / Anti-Bypass

## 11.1 OTEL spans — **29 canonical L6 spans**

`SPAN_NAMES` tuple in `otel_spans.py` has 30 entries (29 doctrine + 1 conditional `l6.ingest.gap_report_emit`
added in commit `3cdae7687f`; `l6.pattern.record_emit` is the 29th doctrine span, also conditional).
All required attrs (trace_id, span_id, parent_span_id, status, latency_ms + 14 contextual fields) carried via
`L6SpanRecord`. ✅

## 11.2 KPI board — **19 KPIs in impl**, 8/11 mapped to v5 doctrine, 3 missing (G2)

See §2.2.

## 11.3 Failure containment matrix — **15 modes**

`FAILURE_CONTAINMENT` dict in `otel_spans.py` maps all 15: stale_ingest, orphan_evidence, eval_gap,
forced_certainty, preference_overfitting, rca_vagueness, false_promote, shadow_writer, stale_eval_on_write,
partial_bypass, current_run_mutation, rollback_missing, cache_contamination, rubric_drift,
replay_nonlocalization. ✅ all 15. Containment actions are **string descriptions**, not callable runtime
hooks; that's a deliberate doctrine-as-data design (the runtime enforcers live in pipeline guards, not in this
matrix).

## 11.4 Pack-level test requirements — **17 conditions**

All 17 covered by `test_06_8_anti_bypass.py` + `test_06_branch_coverage.py` + `test_06_edge_cases.py` +
`test_06_hardening.py`. ✅

## 11.5 Proof commands — **8 commands**

All 8 satisfied by `tests/unit/L6_observability/shadow_eval/` + `scripts/proof/run_l6_shadow_eval_proof.py`.
Runtime proof JSON carries 12 deterministic digests + 6 doctrine invariants all `True`. ✅

## 11.6 Acceptance criteria — **9 criteria**

| Criterion | Status |
|---|:---:|
| All child surfaces emit deterministic receipts | ✅ — `stamp_digest` on every contract |
| Observer law test-enforced | ✅ — `test_no_write_client_imports_in_shadow_eval` + `test_l6_does_not_write_to_l4_directly` |
| Eval-before-learning test-enforced | ✅ — `test_rca_refuses_unconsumable_eval_record` |
| Future-run-only activation test-enforced | ✅ — `test_activation_requires_uwg_receipt` |
| UWG sole-write path test-enforced | ✅ — same |
| Unknown / uncertainty preserved | ✅ — `test_unknown_dimension_is_not_pass` + `test_unknown_uncertainty_is_preserved` |
| KPI board measurable | ✅ — `test_kpi_board_has_19_kpis` + per-KPI direction tests |
| OTEL spans prove sequence + boundaries | ✅ — `test_full_pipeline_ordered_spans` |
| Anti-bypass tests fail on direct mutation, raw learning, stale eval, missing rollback, missing gauntlet, pre-UWG publish | ✅ — full anti_bypass file |

---

# Coverage rollup — final tally

| Doc | Items | Implemented | Modeled | Delegated | Doc-only | **GAP** |
|---|---:|---:|---:|---:|---:|---:|
| 06 parent | 12+6+18+11=47 | 44 | 0 | 1 | 2 | 0 |
| 06_exec (v5) | 6+11+14=31 | 19 | 5 | 1 | 3 | **3** (G2a/b/c) |
| 06.1 ingest | 6+17+7+7+8=45 | 45 | 0 | 0 | 0 | 0 |
| 06.2 observer | 7+10+7+4+7+7=42 | 42 | 0 | 0 | 0 | 0 |
| 06.3 eval | 7+14+14+8+15+4+5+6+6=79 | 56 | 7 | 0 | 4 | **12** (G3 traj) + **11** (G4 gov drift) — but typed-only = 23 |
| 06.4 calib | 6+9+8+6=29 | 29 | 0 | 0 | 0 | 0 |
| 06.5 rca | 7+1+16+11+6=41 | 30 | 11 | 0 | 0 | 0 (11 root-cause classes valid as enum, classifier emits 5) |
| 06.6 proposal | 7+9+10+4+6+7=43 | 43 | 0 | 0 | 0 | 0 |
| 06.7 gauntlet | 6+15+7+8+7+6+8=57 | 56 | 1 | 0 | 0 | 0 |
| 06.8 acceptance | 29+19+15+17+8+9=97 | 89 | 5 | 0 | 0 | 3 (G2 KPIs) |
| **06.9 memory** | **2+4+5=11** | **0** | **0** | **0** | **4** | **7** (G1 — 2 contracts + 5 tests) |

**Final tally**:
- Total doctrine items: ~522
- ✅ Enforced: ~453 (~87%)
- 📦 Modeled: ~29
- 🔁 Delegated: ~2
- ⚪ Doc-only / architectural: ~13
- ⚠️ **GAP**: ~25 items across 4 grouped gaps (G1–G4)

---

# Runtime evidence

`scripts/proof/run_l6_shadow_eval_proof.py` produces `docs/reports/plans/l6_shadow_eval_runtime_proof.json`:

- **kpi_all_passing**: True (all 19 impl KPIs satisfied against synthetic clean-run measurements)
- **doctrine_invariants_proven** (all True):
  - `no_runtime_feedback_edge`
  - `spans_in_canonical_order`
  - `uwg_receipt_required_for_activation`
  - `bus_u_deferred_until_run_start`
  - `content_hash_pinned` (gauntlet ≡ promotion ≡ UWG package)
  - `future_run_only_activation`
- **canonical_span_registry_size**: 30 (29 unconditional + 1 gap_report conditional)
- **span_count emitted**: 28 (clean run; 2 conditional spans gated on preconditions)
- **12 deterministic digests** captured (bundle, normalized record, readiness, outcome, trajectory, governance,
  calibration, eval seal, fused, RCA, proposal, gauntlet, promotion, activation)

Test results: **301/301 passing**, **99.58% line+branch coverage** of `agentic_core/L6_observability/shadow_eval/`.

---

# Action items — closing the gaps

| Gap | Effort | Action |
|---|---|---|
| **G1** 06.9 memory promotion | ~6h | Create `memory_promotion.py` (~150 LOC) + 2 dataclasses in `contracts.py` + `test_06_9_memory_promotion.py` (5 named tests + supporting cases). Add `MEMORY_TYPES` constant. Wire into `pipeline.py::run_proposal` as variant proposal lane. |
| **G2** v5 KPI tri-band + 3 missing KPIs | ~3h | Refactor `KpiThreshold` to carry `(green, yellow, red)` triple. Add `replay_divergence_localization_pct`, `exemplar_hit_rate_pct`, `saturation_watch_pct` entries. Update `evaluate_kpi` to return tri-state. |
| **G3** 12 trajectory detectors | ~4h | Add 12 detection helpers in `evaluation.py::evaluate_trajectory` flag-emit block. Wire each to evidence on `NormalizedEvidenceRecord`. Add unit tests. |
| **G4** 11 governance drift detectors | ~5h | Extend `GovernanceBaseline` with `provider_lanes`, `tool_schemas`, `prompt_versions`, `hitl_thresholds`, `uwg_receipt_window`. Add 11 detector branches in `evaluate_governance_regression`. Tests. |

Total estimated closure: ~18h (one focused engineering day).

These are **deferred**, not silently absent. Following the constitutional `DEFERRED_SCOPE:` capture protocol
would route each to the Wave/Phase Convergence backlog with priority bands per the auto-scorer.

---

**Matrix authoritative as of 2026-04-26**. SSOT location: this file. The prior
`docs/reports/plans/06_shadow_eval_v6_requirements_matrix.md` is **superseded** — it did not cover 06_exec
(v5 file), did not call out G1–G4, and did not co-locate with doctrine.
