# L5 No-Overlap Reconciliation Report

Bottom line: all uploaded L5 parent/child files were ingested, canonicalized, and overwritten as a non-overlapping L5 contract pack.

## Inputs read

| File | Lines read |
|---|---:|
| 00_L5_Governance_Safety_detailed.md | 851 |
| 00.1_L5_Safety_Enforcement_Plane_detailed.md | 1006 |
| 00.2_L5_Authority_Context_Registry_Binding_detailed.md | 1768 |
| 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md | 1568 |
| 00.4_L5_HITL__Reclearance_and_Human_Input_Governance_detailed.md | 1181 |
| 00.5_L5_Egress_and_Provider_Governance_detailed.md | 1487 |
| 00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md | 1522 |
| 00.7_L5_Static_Governance_and_Strucure_Drift_detailed.md | 1546 |
| Evaluation_Runtime_Gates_detailed.md | 1348 |
| 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md | 1008 |
| 04_L2_Execute_detailed.md | 735 |
| C0_Context_Engine_detailed.md | 1149 |
| C0.3_Graph_RAG_detailed.md | 1130 |
| Prompt_Assembly_detailed.md | 567 |
| 06_Shadow_Evaluation_System_Learning_detailed.md | 1438 |
| agentic_system_process_map_exec.md | 111 |

## Output files written

| File | Lines | SHA256 |
|---|---:|---|
| 00.1_L5_Safety_Enforcement_Plane_detailed.md | 1073 | `5a9310b17a14949d3331dc38fc2a157654d0d1d4cbe1aa5ed7f2c97a54231f90` |
| 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md | 1835 | `e8d041641cba574eff9f70117cae5a55c6a157952b16103e0f822d7b6c533137` |
| 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md | 1627 | `6295809f4453174581a778d5a5a3e9135699e91d76965d1126fce2215e0207a5` |
| 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md | 1241 | `cdbcebebb9999c10b4697a45b56f848dc1657c927a8fc419d23370e33e97390c` |
| 00.5_L5_Egress_and_Provider_Governance_detailed.md | 1532 | `af7785daccb01e7b6247ff9f5cc7266a485def485885da8af6f36452d0fea07d` |
| 00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md | 1577 | `1d0e7cb74cfd601ecf7f8e0a14de4d06c501b497187bddf822c9ec3bc3ddfdc2` |
| 00.7_L5_Static_Governance_and_Structure_Drift_detailed.md | 1613 | `89c379c2e611320ab51ffd3b57b8367f03dc371af9e50d16ed100865e2a4654e` |
| 00_L5_Governance_Safety_detailed.md | 258 | `771ebdb1d671bc5ee135783e5ca1a856013fb1d6ac544ccb772136652b138a4f` |

## Canonical corrections applied

- Renamed `00.2_L5_Authority_Context_Registry_Binding_detailed.md` to `00.2_L5_Authority_Context_and_Registry_Binding_detailed.md`.
- Renamed `00.4_L5_HITL__Reclearance_and_Human_Input_Governance_detailed.md` to `00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md`.
- Renamed `00.7_L5_Static_Governance_and_Strucure_Drift_detailed.md` to `00.7_L5_Static_Governance_and_Structure_Drift_detailed.md`.
- Rewrote parent `00_L5_Governance_Safety_detailed.md` as doctrine/index only, so child implementation details are not duplicated upward.
- Added an overwrite reconciliation header to every child with unique ownership, non-ownership, forbidden outputs, and external source boundaries.

## Non-overlap ownership matrix

| File | Owns | Does not own |
|---|---|---|
| 00_L5_Governance_Safety_detailed.md | Doctrine, canonical status language, child map, source boundaries | Child implementation details, runtime decisions, execution, retrieval, prompt assembly, durable writes, learning |
| 00.1_L5_Safety_Enforcement_Plane_detailed.md | Concrete L5 enforcement substrate only | Runtime dispositions, Exit checkout, L2 execution, C0 retrieval, Prompt Assembly, UWG, L6 learning, full authority binding, full origin/HITL/egress/replay/static drift children. |
| 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md | L5 authority context and registry binding evidence only | Concrete scanners/gateway, origin sanitization, HITL lifecycle, egress invocation/certification, replay certification packet, static drift scanning, Runtime Gates, Exit, L2, C0, PA, UWG, L6. |
| 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md | L5 origin labels and content boundary evidence only | C0 retrieval/scoring, Prompt Assembly slot build, HITL lifecycle, Egress certification, Replay certification, Runtime Gates, Exit, L2 execution, UWG, L6. |
| 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md | L5 human-input boundary and re-clearance evidence only | Runtime decision to escalate/continue, Exit escalation workflow, L2 pause/resume execution mechanics, C0 retrieval, Prompt Assembly, UWG commit, L6 calibration. |
| 00.5_L5_Egress_and_Provider_Governance_detailed.md | L5 egress/provider certification evidence only | Sovereign LLM Gateway implementation, direct static scanner implementation, actual model/tool/connector/network invocation, Tool arg gate, Exit output egress, UWG commit, L6 drift learning. |
| 00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md | L5 certification packet, replay/audit binding, and reconstruction readiness evidence only | L2 seal mechanics, replay execution/comparison, Runtime Gate replay decision, Exit final checkout, UWG commit record, L6 RCA/learning. |
| 00.7_L5_Static_Governance_and_Structure_Drift_detailed.md | L5 static governance drift evidence only | Concrete classification/blueprint/gateway scanner implementation, Runtime Gates anomaly containment, L2 validation, C0 retrieval, Prompt Assembly, UWG, L6 promotion. |

## Source-file boundary locks

- Runtime Gates remain the owner of `ALLOW / DENY / CLARIFY / ABSTAIN / REROUTE / SHRINK_SCOPE / RETRY / HEAL / ESCALATE_HITL / QUARANTINE / REDACT / SAFE_FALLBACK / MARK_DEGRADED / COMMIT_REQUEST / BLOCK_COMMIT`.
- Exit remains the owner of final current-run checkout.
- L2 remains the owner of execution lifecycle and seal mechanics.
- C0 remains the owner of retrieval, hydration, evidence scoring, and support status.
- C0.3 remains the owner of GraphRAG traversal mechanics.
- Prompt Assembly remains the owner of slot construction and signed prompt compilation.
- UWG remains the owner of durable write admission.
- L6 remains the owner of completed-run learning, RCA, promotion, and future-run updates.

## Overlap reductions applied

- `00.5` hidden/static egress sections now consume scanner/static evidence from `00.1`/`00.7` instead of owning scanner implementation.
- `00.6` static replay/audit section now consumes static evidence instead of owning static drift review.
- `00.4` static HITL section now consumes static HITL evidence instead of owning static drift review.
- `00.3` static origin-trust section now consumes static boundary evidence instead of owning static drift review.
- `00.1` static regression wording was narrowed to component-level static regression evidence so `00.7` remains the static governance drift owner.

## Duplicate-line scan

Exact duplicate lines across L5 outputs were scanned after excluding common boilerplate, headings, and explicit boundary phrases.
Repeated lines that remain are mostly intentional no-overlap law, downstream ownership references, shared status names, or traceability vocabulary.

- Distinct repeated non-boilerplate lines detected: 134

Sample repeated lines retained intentionally:

- `00.1_L5_Safety_Enforcement_Plane_detailed.md` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:3, 00_L5_Governance_Safety_detailed.md:122
- `Overwrite mode: full-file, no-overlap, implementation-grade child contract` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:9, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:9, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:9, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:9
- `Parent: 00_L5_Governance_Safety_detailed.md` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:10, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:10, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:10, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:10
- `- Runtime Gates own live dispositions and G01-G29 decisions.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:23, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:23, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:23, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:23
- `- Exit Eval owns final current-run checkout.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:24, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:24, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:133, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:24
- `- L2 owns execution lifecycle and sealing mechanics.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:25, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:25, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:25, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:25
- `- C0 owns retrieval, hydration, evidence scoring, and support status.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:26, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:26, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:26, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:26
- `- C0.3 owns GraphRAG traversal mechanics.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:27, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:27, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:27, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:27
- `- Prompt Assembly owns slot construction and signed prompt compilation.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:28, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:28, 00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md:28, 00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md:28
- `- UWG owns durable write admission.` appears in 00.1_L5_Safety_Enforcement_Plane_detailed.md:29, 00.1_L5_Safety_Enforcement_Plane_detailed.md:124, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:29, 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:137

## Final no-overlap rule

Each child is allowed to reference upstream/downstream owners for traceability, but not to implement their mechanics or emit their outputs.
All child files are evidence contracts only.

