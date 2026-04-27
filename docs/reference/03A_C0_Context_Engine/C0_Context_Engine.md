========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: C0_Context_Engine.md
Layer / subsystem: 03A — C0 Context Engine (parent)
Parent file: docs/reference/README.md
Ownership surface: Retrieval planning; evidence fetch; graph expansion (Graph-RAG); shape/rerank/stratify; weak-support refinement; FinalEvidenceContract emission; C0-wide observability and anti-bypass.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: C0 retrieves and shapes evidence. It does not answer, route (L0), assemble prompts (PA), execute (L2), commit (UWG), approve (L5), evaluate (L6), or decide final disposition (Exit).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `C0_Context_Engine.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the `FinalEvidenceContract` schema invariants
- the rule that retrieved text is **data**, never instruction
- the support-score and contradiction-preservation rules
- the gap-report contract on weak support
- the "weak stays weak" invariant (no fabrication to make support pass)

It does **not** own:
- per-stage detail (lives in `C0.0`..`C0.7`)
- prompt assembly (PA)
- routing or execution

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: `RouteContract` indicating `execution_form` requires grounding (`grounded_read`, parts of `managed_workflow`).
**Downstream outputs**: `FinalEvidenceContract` (or `RefinedEvidenceContract` after weak-support loop) handed to PA.
**Forbidden behaviors**: answering, routing, executing, committing, approving, deciding final disposition; fabricating evidence; hiding contradictions; promoting retrieved text to instruction tier.
**Allowed outputs only**: `RetrievalPlan`, `CandidateEvidencePool`, `GraphExpandedEvidencePool`, `ShapedEvidenceSet`, `FinalEvidenceContract`, `RefinedEvidenceContract`, `GapReport`.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-C0-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-C0-NO-ANSWER-001` | C0 MUST NOT emit a final answer or runtime disposition; C0 emits evidence contracts only. | 03A | (governance) | (none) | trace shows no L2/exit/uwg children of `c0.*` | NOT_APPLICABLE: anti-pattern detection in compiler | `compiler_anti_cheat_findings.json` | `validator: c0_no_answer_validator` (release-gate) | `NC-C0-ANSWER-LEAK-001`: C0 produces final answer text | `c0_emitted_final_answer` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-C0-PREFLIGHT-ELIGIBILITY-001` | C0 MUST run preflight grounding-eligibility checks (route grants grounding, origin trust bound, source class legality, instruction-as-data invariant) before any retrieval. Failure produces `C0PreflightStatus.blocked` with stable `blocked_reason`. | C0.0 | RouteContract | `C0PreflightStatus` | preflight artifact carries `eligible=true|false`, `blocked_reason?` | `c0.preflight` span | `c0_preflight_status.json` | `validator: c0_preflight_validator` (release-gate) | `NC-C0-PREFLIGHT-SKIP-001`: retrieval runs without preflight | `c0_preflight_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-C0-RETRIEVAL-PLAN-001` | C0 MUST emit a deterministic `RetrievalPlan` per request with stable lanes, support-target types, and per-lane budgets. | C0.1 | preflight pass | `RetrievalPlan` | plan carries `lanes[]`, `support_targets[]`, `budgets[]` | `c0.retrieval_plan` span | `retrieval_plan_<request_id>.json` | `validator: c0_retrieval_plan_validator` (release-gate) | `NC-C0-PLAN-DRIFT-001`: plan differs across replay for same input | `retrieval_plan_drift` | `byte_identical` | DOC_ONLY |
| `REQ-C0-EVIDENCE-LINEAGE-001` | Every retrieved evidence item MUST carry `source_id`, `version`, `acl_class`, `citation_anchor`, `lineage`, `support_score`, and `contradiction_flag` fields end-to-end. | C0.2..C0.5 | retrieval result | `CandidateEvidencePool` → `FinalEvidenceContract` | every evidence row carries the 7 fields | `c0.lineage_check` span | `final_evidence_contract.json` | `validator: c0_lineage_validator` (release-gate) | `NC-C0-LINEAGE-STRIP-001`: drop `lineage` mid-pipeline | `evidence_lineage_stripped` | `byte_identical` | DOC_ONLY |
| `REQ-C0-FAB-EVIDENCE-001` | C0 MUST NOT fabricate evidence; an evidence item without resolvable `source_id` is FAIL. | C0.2..C0.5 | retrieval result | (validation) | every evidence row resolvable to source store | `c0.evidence_resolve` span | `final_evidence_contract.json` | `validator: c0_no_fabrication_validator` (release-gate) | `NC-C0-FAB-CITATION-001`: inject evidence with non-resolvable source_id | `fabricated_evidence_source` | `byte_identical` | DOC_ONLY |
| `REQ-C0-STALE-EVIDENCE-001` | C0 MUST NOT silently use stale evidence; freshness binding to `policy_hash` and `source_snapshot_manifest` MUST be verified. | C0.2 | evidence | freshness check | every evidence row carries `freshness_validated_at_utc` and `snapshot_id` | `c0.freshness_check` span | `final_evidence_contract.json` | `validator: c0_freshness_validator` (release-gate) | `NC-C0-STALE-001`: evidence beyond freshness window admitted silently | `stale_evidence_admitted` | `byte_identical` | DOC_ONLY |
| `REQ-C0-CONTRADICTION-PRESERVE-001` | C0 MUST surface contradictions; contradictions MUST NOT be hidden or silently filtered. | C0.4 | shaped evidence | `FinalEvidenceContract` | `contradiction_flag=true` rows preserved | `c0.contradiction_scan` span | `final_evidence_contract.json` | `validator: c0_contradiction_validator` (release-gate) | `NC-C0-CONTRADICTION-HIDE-001`: filter out contradicting evidence | `contradiction_hidden` | `byte_identical` | DOC_ONLY |
| `REQ-C0-WEAK-STAYS-WEAK-001` | C0 MUST NOT promote weak support to strong; weak-support refinement MUST emit `RefinedEvidenceContract` with the same support category or with new evidence — never a relabeling. | C0.6 | weak evidence | `RefinedEvidenceContract` or `GapReport` | refinement receipt records source of new evidence; relabeling-only is FAIL | `c0.refine_loop` span | `refined_evidence_contract.json` | `validator: c0_weak_support_validator` (release-gate) | `NC-C0-RELABEL-001`: weak support relabeled strong without new evidence | `support_strength_relabel` | `byte_identical` | DOC_ONLY |
| `REQ-C0-INSTRUCTION-AS-DATA-001` | Retrieved text MUST be treated as data, never as instruction; injection findings MUST be flagged. | C0.0..C0.5 | retrieval result | injection findings | every evidence row carries `injection_findings[]` | `c0.injection_scan` span | `final_evidence_contract.json` | `validator: c0_instruction_as_data_validator` (release-gate) | `NC-C0-INSTRUCTION-LEAK-001`: retrieved text elevated to instruction tier | `retrieved_text_promoted_to_instruction` | `byte_identical` | DOC_ONLY |
| `REQ-C0-FINAL-EVIDENCE-CONTRACT-001` | C0 MUST emit exactly one `FinalEvidenceContract` per grounded request; the contract MUST be hand-off-ready for PA. | C0.5 | shaped evidence | `FinalEvidenceContract` | one contract per grounded request | `c0.final_evidence` span | `final_evidence_contract.json` | `validator: c0_final_evidence_validator` (release-gate) | `NC-C0-DUAL-CONTRACT-001`: emit two FinalEvidenceContracts | `dual_evidence_contract` | `byte_identical` | DOC_ONLY |
| `REQ-C0-OBSERVABILITY-001` | C0 MUST emit observability for every preflight, retrieval, expansion, shaping, and refinement event. | C0.7 | every C0 stage | observability stream | every stage logged | `c0.observability` span | `c0_observability.json` | `validator: c0_observability_validator` (release-gate) | `NC-C0-DARK-RETRIEVAL-001`: retrieval not logged | `c0_dark_retrieval` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`FinalEvidenceContract` MUST carry: `evidence_contract_id`, `request_id`, `route_id`, `trace_root`, `trace_id`, `span_id`, `evidence_items[]` (each with `source_id`, `version`, `acl_class`, `citation_anchor`, `lineage`, `support_score`, `contradiction_flag`, `freshness_validated_at_utc`, `snapshot_id`, `injection_findings[]`), `aggregate_support_class`, `gap_report?`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `validator_receipt_id`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans (children of `c0.run` parent):
`c0.preflight`, `c0.retrieval_plan`, `c0.evidence_fetch`, `c0.graph_expand`, `c0.shape_rerank`, `c0.contradiction_scan`, `c0.injection_scan`, `c0.lineage_check`, `c0.evidence_resolve`, `c0.freshness_check`, `c0.refine_loop` (when triggered), `c0.final_evidence`, `c0.observability`.

Required attributes: `req_id`, `request_id`, `route_id`, `evidence_contract_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `parent_contract_id`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `c0_no_answer_validator`, `c0_preflight_validator`, `c0_retrieval_plan_validator`, `c0_lineage_validator`, `c0_no_fabrication_validator`, `c0_freshness_validator`, `c0_contradiction_validator`, `c0_weak_support_validator`, `c0_instruction_as_data_validator`, `c0_final_evidence_validator`, `c0_observability_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-C0-*` row in §4 is mandatory. The 4 critical-severity controls are: `NC-C0-FAB-CITATION-001`, `NC-C0-STALE-001`, `NC-C0-CONTRADICTION-HIDE-001`, `NC-C0-INSTRUCTION-LEAK-001`. These map to the failure modes that the C0 owner-summary explicitly forbids.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(RouteContract, source_snapshot_manifest, retrieval_plan_inputs, policy_hash, blueprint_hash, seed)`, `FinalEvidenceContract.content_hash` MUST replay byte-identical. Allowed nondeterminism: `evidence_contract_id`, `span_id`, `trace_id`, `created_at_utc`.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 03A row's `Release Gate` is `PASS` only when: preflight ran; retrieval plan deterministic; evidence carries lineage end-to-end; no fabrication; freshness validated; contradictions preserved; weak stays weak; retrieved text remains data; one final contract; observability complete.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: C0 retrieval and evidence shaping invariants.

**Related files own**: per-stage detail in `C0.0`..`C0.7`; `C0_Context_Engine_example.md` is a non-normative example; `C0_Requirements_Traceability_Matrix.md` is historical (subsumed by `00X` registry per `00X §13`).

**Forbidden duplicated ownership**: C0 MUST NOT answer, route, assemble prompts, execute, commit, approve, evaluate, or decide final disposition.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `prompt_envelope_constructed`, `learning_promoted`. The token `evidence_contract_issued` is allowed only inside a `FinalEvidenceContract.status` field.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `C0.0_Preflight_Grounding_Eligibility.md` — `REQ-C0-PREFLIGHT-*`
- `C0.1_Retrieval_Plan.md` — `REQ-C0-PLAN-*`
- `C0.2_Evidence_Fetch.md` — `REQ-C0-FETCH-*`
- `C0.3_Graph_RAG.md` — `REQ-C0-GRAPH-*`
- `C0.4_Shape_Rerank_Stratify.md` — `REQ-C0-SHAPE-*`, `REQ-C0-CONTRADICTION-*`
- `C0.5_Final_Evidence_Contract.md` — `REQ-C0-FINAL-*`
- `C0.6_Weak_Support_Refinement.md` — `REQ-C0-REFINE-*`
- `C0.7_C0_Observability_Tests_Anti_Bypass.md` — `REQ-C0-OBS-*`, `REQ-C0-ANTIBYPASS-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 8 child files own per-stage REQ_IDs (deferred for full conversion).
- The "weak stays weak" invariant is binding.
- Retrieved-text-is-data invariant is binding.

END OF 03A — C0 CONTEXT ENGINE PARENT
========================================================================================================================
