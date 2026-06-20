========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 00X_Requirements_Traceability_and_No_Loss_Map.md
Layer / subsystem: Cross-cutting — Global REQ_ID Registry, Traceability, and No-Loss Map
Parent file: docs/reference/README.md
Ownership surface: Global REQ_ID registry rules, traceability matrix schema, status vocabulary, evidence vocabulary, release fail rules, no-overlap reconciliation, orphan detection rules, anti-cheat encodings.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: 00X owns REQ_ID rules and the cross-pack traceability map only. It does not own runtime behavior, gate law, durable write admission, certification evidence, retrieval, planning, routing, execution, or end-to-end proof harness. Each layer pack owns its own atomic REQ_ID rows under the namespace this file assigns.
Source authority notes: Supersedes the 2026-04-26 prose-grade traceability ledger. Aligned with constitutional rule §22 (graph-layer evidence required), §23 (ADG canonical invariants), §24 (deferred scope marker), and the Author-Gate enforcement family.
Predecessor preserved at: 00X_Requirements_Traceability_and_No_Loss_Map.md.pre-reqid-rewrite.bak
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This file is the **executable contract** for the requirements pack. It is not narrative documentation.

It uniquely owns:
- the global REQ_ID naming and namespace rules
- the per-layer namespace assignment table
- the canonical traceability matrix schema
- the status vocabulary used by every requirement row in every layer file
- the evidence vocabulary used by every requirement row
- the release-fail computation rules
- the orphan-requirement / orphan-implementation / orphan-test detection rules
- the anti-cheat failure-mode encodings (FAKE / MOCK_ONLY / DOC_ONLY / UNVERIFIED / PARTIAL)
- the no-overlap reconciliation contract

It explicitly does **not** own:
- any layer's runtime behavior
- any layer's atomic REQ_ID rows (those live in the layer pack files)
- the E2E evidence compiler implementation contract (that is `99.11_E2E_Requirements_To_Runtime_Evidence_Compiler.md`)
- the live G01–G29 gate law (that is `00C/`)
- the certification evidence (that is `00A/`)
- the durable-write admission contract (that is `00B.6_UWG_Durable_Write_Gateway.md`)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**:
- Each canonical layer parent file declares its REQ_ID namespace.
- Each canonical layer child file owns rows under its parent's namespace.

**Downstream outputs**:
- A single global REQ_ID registry that the E2E compiler (`99.11`) consumes.
- A status vocabulary that every release-gate decision must use verbatim.
- A no-overlap law every layer file must comply with.

**Forbidden behaviors**:
- 00X must not declare runtime behavior.
- 00X must not invent REQ_IDs that belong to a layer pack.
- 00X must not fabricate evidence rows; it only enumerates *rules*.

**Allowed outputs only**:
- REQ_ID grammar rules
- Namespace ownership tables
- Status / evidence / fail-reason vocabularies
- Detection rules (orphan, doc-only, mock-only, fake, unverified)
- Cross-pack traceability schema

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
00X itself does not emit domain REQ_IDs. It defines the rules for REQ_IDs across every other file.

The following REQ_ID **pattern grammar** is binding for every layer pack:

```
REQ-<NAMESPACE>-<SEMANTIC-NAME>-<3-DIGIT-SEQ>
```

- `<NAMESPACE>` ∈ namespace map below; uppercase, no hyphens internally.
- `<SEMANTIC-NAME>` is a stable, descriptive identifier (no positional row numbering when a semantic name is available).
- `<3-DIGIT-SEQ>` is a zero-padded counter scoped to the namespace + semantic name (e.g., `001`, `002`).
- `-` separates segments; no whitespace; no underscores.
- A REQ_ID is **immutable** once published. Renames are forbidden. Replacements supersede via the registry table below.
- Examples:
  - `REQ-U0-INGRESS-ENVELOPE-001`
  - `REQ-L0-ROUTE-EXACTLY-ONE-001`
  - `REQ-C0-EVIDENCE-LINEAGE-001`
  - `REQ-PA-AUTHORITY-ORDER-001`
  - `REQ-L2-NO-DIRECT-L4-WRITE-001`
  - `REQ-EXIT-ONE-DISPOSITION-001`
  - `REQ-UWG-SOLE-DURABLE-WRITE-001`
  - `REQ-GATE-G28-TRACE-COMPLETE-001`
  - `REQ-E2E-REQ-MATRIX-COMPILER-001`
  - `REQ-TRACE-PARENT-CHILD-LINK-001`

3.1 PER-LAYER NAMESPACE OWNERSHIP TABLE

| Namespace | Owning pack | Owning parent file | Description |
|---|---|---|---|
| `REQ-L5-*` | `00A_L5_Governance_Safety/` | `00A_L5_Governance_Safety.md` | Governance certification evidence rows |
| `REQ-L4-*` | `00B_L4_State_Archive_and_UWG/` | `00B_L4_State_Archive_and_UWG.md` | Durable state and read-surface invariants |
| `REQ-UWG-*` | `00B_L4_State_Archive_and_UWG/` | `00B.6_UWG_Durable_Write_Gateway.md` | Sole durable-write admission gateway invariants |
| `REQ-GATE-G01-*`..`REQ-GATE-G29-*` | `00C_Runtime_Gates_Current_Run_Mesh/` | `00C_Runtime_Gates_Current_Run_Mesh.md` | Per-gate verdict law (G01..G29) |

**Parent-pack gap matrix (2026-05-23):** [l5-l4-00c-parent-gap-matrix-b8e4f2.json](../reports/plans/l5-l4-00c-parent-gap-matrix-b8e4f2.json) — plan [l5-l4-00c-parent-gap-b8e4f2.md](../../.codex/plans/l5-l4-00c-parent-gap-b8e4f2.md); 00C schema SSOT: [ADR-00C-7-gate-verdict-ssot-b8e4f2.md](../adr/ADR-00C-7-gate-verdict-ssot-b8e4f2.md).
| `REQ-U0-*` | `01_Request_Intake/` | `01_request_intake.md` | Request envelope, identity, schema, idempotency |
| `REQ-L1-*` | `02_L1_Reasoning_Plan/` | `02_L1_Reasoning_Plan_Generation.md` | Plan, route hints, support expectation |
| `REQ-L0-*` | `03_L0_Route_Decision/` | `03_L0_Route_Decision_Switching_L3.md` | Deterministic RouteContract |
| `REQ-L3-*` | `03_L0_Route_Decision/` | `03_L0_Route_Decision_Switching_L3.md` | Managed-workflow shaping |
| `REQ-C0-*` | `03A_C0_Context_Engine/` | `C0_Context_Engine.md` | Retrieval, evidence shaping, FinalEvidenceContract |
| `REQ-PA-*` | `03B_PA_Prompt_Assembly/` | `PA_Prompt_Assembly.md` | Authority-tiered PromptEnvelope |
| `REQ-L2-*` | `04_L2_Execute/` | `04_L2_Execute.md` | Bounded execution, E1..E5, PTC, sealed_l2_artifact, proposed_state_diff |
| `REQ-EXIT-*` | `05_Exit_Evaluation_and_Control/` | `05_Live_Runtime_Exit_Control_&_Evaluation.md` | ExitReviewPacket, X1A..X1J, X3A..X3E |
| `REQ-L6-*` | `06_L6_Observability_and_System_Learning/` | `06_Shadow_Evaluation_System_Learning.md` | Completed-run eval, RCA, proposal, gauntlet |
| `REQ-E2E-*` | `99_End_to_End_Runtime_Proof_and_Acceptance/` | `99_End_to_End_Runtime_Proof_and_Acceptance.md` | E2E proof scenarios |
| `REQ-TRACE-*` | `99_End_to_End_Runtime_Proof_and_Acceptance/` | `99.4_E2E_OTEL_Trace_and_Span_Tree_Proof.md` | OTEL span-tree completeness rows |
| `REQ-COMPILER-*` | `99_End_to_End_Runtime_Proof_and_Acceptance/` | `99.11_E2E_Requirements_To_Runtime_Evidence_Compiler.md` | Compiler contract rows |
| `REQ-APP-PROOF-*` | `apps_proof/` (out-of-tree code) | `apps_proof/` | Apps-proof-harness rows linking apps to E2E proof |

A namespace MUST NOT span two packs. A pack MAY own multiple namespaces (e.g. `00B` owns `REQ-L4-*` and `REQ-UWG-*`) only when this table records that relationship.

4. CANONICAL ATOMIC REQUIREMENTS TABLE SCHEMA
------------------------------------------------------------------------------------------------------------------------
Every layer pack child file MUST include an `Atomic Requirements Table` whose rows match this schema **exactly**:

| Column | Required | Description | Empty-cell rule |
|---|---|---|---|
| `REQ_ID` | yes | Globally unique under the namespace grammar (§3) | never blank |
| `Requirement` | yes | One MUST / MUST NOT statement per row | never blank, never bundles two requirements |
| `Owner` | yes | Owning pack and file path | never blank |
| `Inputs` | yes | Upstream contract(s) consumed | `NONE` allowed only for U0 envelope |
| `Outputs` | yes | Downstream contract(s) emitted | `NONE` allowed only for terminal-failure rows |
| `Runtime Evidence` | yes | Artifact name pattern + required fields | never blank; if non-applicable use `NOT_APPLICABLE: <reason>` |
| `OTEL Span` | yes | Span name + parent + required attributes | never blank; if non-applicable use `NOT_APPLICABLE: <reason>` |
| `Artifact / Receipt` | yes | Receipt file or contract object | never blank |
| `Validator` | yes | Validator name + scope (runtime / CI / release-gate) | never blank |
| `Negative Control` | yes | Adversarial control id | `NOT_APPLICABLE: <reason>` if no adversarial counterpart exists |
| `Expected Fail Reason` | yes | Stable failure code surfaced when the negative control trips | required when Negative Control is not `NOT_APPLICABLE` |
| `Replay Check` | yes | Replay digest comparison the row imposes | never blank |
| `Release Gate` | yes | Initial release-gate status (PASS / PARTIAL / MISSING / DOC_ONLY / MOCK_ONLY / FAKE / UNVERIFIED / NOT_APPLICABLE) | never blank |

Rules for filling cells:
- One requirement per row. Bundled requirements (e.g. "X and Y must hold") MUST be split.
- "should" language is forbidden in `Requirement` unless the row is explicitly advisory and `Release Gate` is `NOT_APPLICABLE`.
- Every MUST / MUST NOT clause MUST have non-blank `Runtime Evidence`, `OTEL Span`, `Artifact / Receipt`, `Validator`, `Replay Check`, and `Release Gate`. `Negative Control` and `Expected Fail Reason` follow the rule above.
- A row with **any** blank required cell is invalid and the file fails the registry validator.

5. STATUS VOCABULARY (BINDING)
------------------------------------------------------------------------------------------------------------------------
The `Release Gate` column and the compiler output (`99.11`) MUST use exactly one of these status tokens. No other tokens are permitted.

| Status | Meaning | Release effect |
|---|---|---|
| `PASS` | Runtime artifact, OTEL span, validator receipt, negative control (when applicable) with matching `expected_fail_reason`, and replay check are all present and consistent. | Permits release for this row. |
| `PARTIAL` | At least one applicable evidence dimension is missing or weakened. | Release-blocking. |
| `MISSING` | Required evidence dimension is absent. | Release-blocking. |
| `DOC_ONLY` | Markdown declares the requirement; no code, validator, span, artifact, or test maps to it. | Release-blocking. |
| `MOCK_ONLY` | Test or harness satisfies row only via a mock; no real runtime artifact or live OTEL span proves execution. | Release-blocking. |
| `FAKE` | Validator caught by accident (path missing instead of hash mismatch), index-only artifact validation without referenced payload `content_hash`, negative-control caught without `expected_fail_reason` match, or any anti-cheat signature in §11. | Release-blocking. |
| `UNVERIFIED` | Implementation exists but no runtime artifact proves execution; or evidence lacks one of `hash`, `lineage`, `trace_id`, `policy_hash`, `replay_key`, or `validator receipt`. | Release-blocking. |
| `NOT_APPLICABLE` | Row has no applicable adversarial control / OTEL span / runtime artifact AND a written justification is recorded in the same cell using `NOT_APPLICABLE: <reason>`. | Permits release for this row. |

The set `{PARTIAL, MISSING, DOC_ONLY, MOCK_ONLY, FAKE, UNVERIFIED}` is the **release-blocking set**. A release MUST fail if any row's `Release Gate` is in this set.

6. EVIDENCE VOCABULARY (BINDING)
------------------------------------------------------------------------------------------------------------------------
6.1 RUNTIME ARTIFACT EVIDENCE — required field set per row
- `request_id`
- `run_id`
- `trace_root` (or `trace_id` for span-scoped artifacts)
- `policy_hash`
- `blueprint_hash`
- `replay_key`
- `content_hash` (for any payload referenced by an index file)
- `lineage` (parent contract IDs and producer span ID)
- `validator_receipt_id` when the validator is non-trivial

6.2 OTEL SPAN EVIDENCE — required attribute set per row
- `span.name` matches the row's declared span
- `span.parent` matches declared parent (or `ROOT` for trace_root)
- `attributes.req_id` = the row's REQ_ID
- `attributes.policy_hash`, `attributes.blueprint_hash`, `attributes.replay_key`
- `status_code` ∈ {`OK`, `ERROR`}; `OK` required for PASS, `ERROR` required for negative controls expecting failure
- For failure spans: `attributes.fail_reason_code` MUST equal the row's `Expected Fail Reason`

6.3 VALIDATOR EVIDENCE
- Validator name: stable identifier; lives in `ops_scripts/ci/`, `apps_proof/`, or `tools/validators/`.
- Validator output: a `validator_receipt` JSON object with `req_id`, `result` ∈ {`pass`, `fail`}, `reason_code`, `evidence_refs[]`, `replay_refs[]`.
- A validator that catches via the wrong path (e.g. file-not-found instead of hash mismatch) is `FAKE` (see §11.4).

6.4 NEGATIVE CONTROL EVIDENCE
- Each negative control has a `control_id` of the form `NC-<NAMESPACE>-<SEMANTIC-NAME>-<3-DIGIT-SEQ>` matching the target row.
- The control attempts a specific tamper / bypass.
- The validator MUST emit `result=fail` AND `reason_code` MUST match `Expected Fail Reason` exactly.
- A control that records `caught=true` without `reason_code` matching `Expected Fail Reason` is `FAKE` per §11.1.

6.5 REPLAY EVIDENCE
- Replay obligation is one of: `byte_identical`, `semantic_identical`, `digest_match_only`, `not_applicable`.
- The row MUST declare which.
- Replay receipt fields: `first_run_digest`, `second_run_digest`, `match_type`, `allowed_nondeterminism[]`.

7. RELEASE FAIL RULES (BINDING)
------------------------------------------------------------------------------------------------------------------------
A release MUST fail if **any** of the following hold:
1. Any row's `Release Gate` ∈ release-blocking set.
2. Any row's `Negative Control` is non-`NOT_APPLICABLE` but `Expected Fail Reason` is empty.
3. Any row's `Runtime Evidence`, `OTEL Span`, `Artifact / Receipt`, `Validator`, or `Replay Check` is blank.
4. Any pack contains a duplicate REQ_ID.
5. Any pack child file lacks an `Atomic Requirements Table` when its parent declares a namespace.
6. Any anti-cheat detector in §11 returns a positive match.
7. The compiler `99.11` reports `release_blocking=true` for any row.

A release MAY pass only when **every** row is `PASS` or `NOT_APPLICABLE` with explicit reason text.

8. ORPHAN DETECTION RULES
------------------------------------------------------------------------------------------------------------------------
8.1 ORPHAN REQUIREMENT — a markdown REQ_ID exists but no code, validator, span, artifact, or test is discoverable for it.
- Detection: compiler scans for `REQ_ID` literal in `agentic_core/`, `apps_proof/`, `apps_*/`, `ops_scripts/`, `tools/`, and the `tests/` tree. If zero hits, mark `DOC_ONLY`.

8.2 ORPHAN IMPLEMENTATION — a runtime artifact, validator, or OTEL span exists but no REQ_ID maps to it.
- Detection: compiler scans every emitted artifact's `req_id` attribute and every span's `attributes.req_id`. Unknown values are reported as `OrphanRuntimeSurfaces` rows.

8.3 ORPHAN TEST — a test exists in `tests/` but does not reference any REQ_ID.
- Detection: compiler greps `tests/` for `REQ-` literals. Tests without a REQ_ID reference are reported as `OrphanTests`.

8.4 FAKE / MOCK_ONLY DETECTION
- Mock-only: test references REQ_ID but no live runtime artifact carrying that REQ_ID was produced in the same trace_root.
- Fake: see §11.

8.5 UNVERIFIED DETECTION
- Implementation present but no runtime artifact emits the REQ_ID under a real run.
- Evidence present but missing one of `content_hash`, `lineage`, `trace_id`, `policy_hash`, `replay_key`.

9. NO-OVERLAP RECONCILIATION RULES
------------------------------------------------------------------------------------------------------------------------
9.1 OWNERSHIP UNIQUENESS — every requirement maps to exactly one owning pack. The namespace map in §3.1 is the binding source of truth. A requirement that appears to belong to two packs MUST be split into two rows in their respective owning packs (each with a distinct REQ_ID), or one pack MUST be removed as the owner.

9.2 GLOBAL OWNERSHIP MODEL (binding for all 12 packs)
- `00A_L5_Governance_Safety` owns governance certification evidence.
- `00B_L4_State_Archive_and_UWG` owns durable state, durable-write admission, read surfaces.
- `00C_Runtime_Gates_Current_Run_Mesh` owns G01–G29 GateVerdict law.
- `01_Request_Intake` owns request envelope validation and identity baseline.
- `02_L1_Reasoning_Plan` owns intent, plan, route hints, support expectation.
- `03_L0_Route_Decision` owns the deterministic RouteContract and managed workflow shaping.
- `03A_C0_Context_Engine` owns retrieval and evidence shaping.
- `03B_PA_Prompt_Assembly` owns prompt construction.
- `04_L2_Execute` owns bounded execution and sealed artifacts.
- `05_Exit_Evaluation_and_Control` owns current-run aggregation and exactly one X3 disposition.
- `06_L6_Observability_and_System_Learning` owns completed-run eval and future-run learning attempts through UWG.
- `99_End_to_End_Runtime_Proof_and_Acceptance` owns proof harnesses only.

9.3 FORBIDDEN OUTPUT VOCABULARY — a pack that is not the owner of a runtime decision MUST NOT emit that decision in its REQ_ID rows. Specifically:
- 00A MUST NOT emit live `ALLOW`/`DENY` runtime dispositions.
- 00B MUST NOT make routing or final-response decisions.
- 00C MUST NOT own end-to-end scenario proof bundles.
- 99 MUST NOT own any runtime authority.
- L1 / L0 / C0 / PA / L3 / L2 MUST NOT mutate L4 directly.
- L6 MUST NOT mutate the current run.

10. TRACEABILITY MATRIX SCHEMA (BINDING)
------------------------------------------------------------------------------------------------------------------------
The compiler `99.11` materializes a `RequirementsCoverageMatrix` whose rows have **exactly** these columns:

```
REQ_ID
source_doc
source_section
requirement_text
owning_layer
expected_runtime_artifact
actual_runtime_artifact_found
expected_otel_span
actual_otel_span_found
expected_validator
actual_validator_found
expected_negative_control
actual_negative_control_found
expected_fail_reason
actual_fail_reason_found
expected_replay_check
actual_replay_check_found
expected_test
actual_test_found
status
gap_reason
required_fix
severity
release_blocking
```

Status values come from §5. Severity ∈ {`critical`, `high`, `medium`, `low`} per §11.6.

11. ANTI-CHEAT FAILURE-MODE ENCODINGS (BINDING)
------------------------------------------------------------------------------------------------------------------------
The compiler MUST detect each of these and assign the indicated status. Each detector is testable and must have a corresponding unit test in `tests/unit/tools/compiler/test_anti_cheat_detectors.py` (or equivalent under the compiler's home).

11.1 CAUGHT-WITHOUT-REASON-MATCH (FAKE / UNVERIFIED)
- Trigger: `validator_receipt.result=fail` AND `result_caught=true` AND (`reason_code` empty OR `reason_code` ≠ row's `Expected Fail Reason`).
- Status: `FAKE` if `reason_code` is wrong; `UNVERIFIED` if `reason_code` is empty.
- Severity: `critical`.

11.2 INDEX-ONLY ARTIFACT VALIDATION (FAKE)
- Trigger: validator inspects an index file (e.g. `manifest.json`) and confirms the entry exists, but does not verify the referenced payload's `content_hash` against the recorded value.
- Status: `FAKE`.
- Severity: `critical`.

11.3 OTEL TRACE PRESENT BUT INCOMPLETE (PARTIAL / UNVERIFIED)
- Trigger: trace tree exists but at least one required span name is missing OR a parent/child link is broken.
- Status: `PARTIAL` when the span is recoverable; `UNVERIFIED` when the missing link breaks chain-of-custody.
- Severity: `high`.

11.4 ACCIDENTAL CATCH (FAKE)
- Trigger: validator returns `fail` for a reason unrelated to the requirement (e.g., file-not-found vs the row's declared `Expected Fail Reason` of `evidence_hash_mismatch`).
- Status: `FAKE`.
- Severity: `critical`.

11.5 ORPHAN TEST (NOT PROOF)
- Trigger: pytest passes but the test references zero REQ_IDs.
- Status: test is excluded from coverage. Row that the test claimed to cover is `UNVERIFIED` until a REQ_ID-bound test exists.
- Severity: `high`.

11.6 IMPLEMENTATION WITHOUT RUNTIME ARTIFACT (UNVERIFIED)
- Trigger: code reference to REQ_ID exists; no runtime artifact under any `trace_root` carries that REQ_ID.
- Status: `UNVERIFIED`.
- Severity: `high`.

11.7 DOC-ONLY (DOC_ONLY)
- Trigger: REQ_ID present in markdown; zero code / validator / span / artifact / test references.
- Status: `DOC_ONLY`.
- Severity: `medium` initially, escalates to `high` if requirement is on the release-blocking surface.

11.8 MOCK_ONLY (MOCK_ONLY)
- Trigger: tests pass but only via mock objects; no live runtime artifact under any `trace_root` carries the REQ_ID.
- Status: `MOCK_ONLY`.
- Severity: `high`.

11.9 GENERATED ARTIFACT MISSING REQUIRED FIELDS (UNVERIFIED)
- Trigger: artifact exists but lacks one of `content_hash`, `lineage`, `trace_id`, `policy_hash`, `replay_key`, or `validator_receipt`.
- Status: `UNVERIFIED`.
- Severity: `high`.

11.10 NEGATIVE CONTROL WITHOUT EXPECTED-FAIL-REASON (PARTIAL)
- Trigger: `Negative Control` cell is not `NOT_APPLICABLE` but `Expected Fail Reason` cell is empty.
- Status: `PARTIAL` (release-blocking).
- Severity: `critical`.

11.11 SEVERITY OVERRIDE
- A row whose owning pack is `00C` (gates), `00B.6` (UWG), `05` (Exit), or `99` (E2E proof) is automatically `severity=critical` regardless of the per-detector default. The release-blocking decision uses the higher of the two.

12. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**:
- Global REQ_ID grammar and namespace map.
- Status, evidence, and fail-reason vocabularies.
- Anti-cheat encodings.
- Cross-pack traceability matrix schema.
- No-overlap reconciliation rules.

**Related files own**:
- `99.11_E2E_Requirements_To_Runtime_Evidence_Compiler.md` owns the compiler implementation contract that consumes this file's rules.
- Each layer pack parent owns its namespace's atomic REQ_ID rows.
- `00C` owns gate verdict law and per-gate REQ_IDs.
- `00B.6` owns UWG durable-write admission REQ_IDs.
- `00A` owns L5 certification REQ_IDs.
- `99` owns scenario-level E2E REQ_IDs.

**Forbidden duplicated ownership**:
- 00X MUST NOT redefine any atomic layer REQ_ID.
- 00X MUST NOT declare runtime behavior, gate verdicts, certification statuses, or durable-write outcomes.
- No layer pack may redefine the global status / evidence / fail-reason vocabulary.
- No layer pack may emit a REQ_ID under a namespace it does not own.

**Forbidden output vocabulary** (00X is non-runtime by construction):
- `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`
- `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
This file is complete only when every bullet below holds:
- The REQ_ID grammar in §3 is published.
- The per-layer namespace ownership table in §3.1 enumerates every owning pack.
- The Atomic Requirements Table schema in §4 lists 13 columns with non-blank-required rules.
- The status vocabulary in §5 has exactly the 8 listed tokens; none extra; none missing.
- The evidence vocabulary in §6 enumerates required artifact, span, validator, negative-control, and replay fields.
- The release fail rules in §7 are fail-closed.
- The orphan detection rules in §8 cover requirement, implementation, and test orphans.
- The no-overlap reconciliation rules in §9 forbid every cross-pack output the prior architecture allowed.
- The traceability matrix schema in §10 has exactly 23 columns matching `99.11`.
- The anti-cheat encodings in §11 cover at least 11 detectors and each has an assigned severity and status.
- The no-overlap lock in §12 names this file's owned surface and the forbidden vocabulary.
- The compiler `99.11` references this file as its rule source.
- Every layer pack parent file references this file's namespace map for its own REQ_ID prefix.
- This file emits zero atomic domain REQ_IDs (it owns rules, not rows).

REGISTRY OF SUPERSEDED PROSE LEDGERS
------------------------------------------------------------------------------------------------------------------------
The following prior content is superseded and MUST NOT be cited as authoritative:

| Prior surface | Superseded by | Action |
|---|---|---|
| 00X "REQUIREMENT COVERAGE LEDGER" (REQ-001..REQ-015 prose rows) | §3.1 namespace map + each owning pack's Atomic Requirements Table | Historical only; no new authoritative use. |
| 00X "ZERO-LOSS REDISTRIBUTION MATRIX" (prior version) | §9.2 ownership model + namespace map | Superseded; ownership tied to namespace, not narrative. |
| `C0_Requirements_Traceability_Matrix.md` | §3.1 + 99.11 compiler output | Reduced to historical artifact. |
| `03B_PA_Prompt_Assembly/REQUIREMENT_TRACEABILITY_MATRIX.md` | §3.1 + 99.11 compiler output | Reduced to historical artifact. |
| Predecessor 00X (preserved as `.pre-reqid-rewrite.bak`) | This file | Preserved on disk for audit. |

END OF 00X — REQ_ID REGISTRY CONTRACT
========================================================================================================================
