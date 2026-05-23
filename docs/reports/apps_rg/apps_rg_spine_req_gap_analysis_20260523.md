# apps_rg Spine REQ Gap Analysis (U0 → L6)

**Generated:** 2026-05-23  
**Scope:** `apps_rg` product runtime vs spine REQ parent contracts  
**Prior v40 overlay:** [apps_rg_v40_spine_gap_analysis_20260523.md](apps_rg_v40_spine_gap_analysis_20260523.md)  
**PA-only drill-down:** [pa_exec_flowchart_gap_analysis_20260523.md](pa_exec_flowchart_gap_analysis_20260523.md)  
**Machine audit:** [apps_rg_spine_req_gap_audit.json](../../artifacts/apps_rg/plans/apps_rg_spine_req_gap_audit.json)  
**Execution plan:** [.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md](../../.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md)  
**Notion:** [pa-exec-flowchart-gap-f2a8c3](https://www.notion.so/pa-exec-flowchart-gap-f2a8c3-36927693f55c8138afb7fe72202f206a)

---

## Executive summary

Reference spine docs (`01`–`06`, `03A` C0, `03B` PA) define **REQ-* parent invariants**: staged receipts, OTEL spans, HMAC where required, exactly-one handoff contracts, and **no layer authority leakage**.

**Target architecture (user-confirmed, Anthropic-aligned):**

- **apps_rg owns** domain config + prompt content (`config/domain_contract/`, `prompt_assembly/`).
- **agentic_core owns** generic engines; **U0 ingests** the domain packet once (`RuntimeCustomizationPackage` + registry).
- **One governed pipeline** per layer on product paths (no parallel section vs integrated bypass).

**Current state:** App-owned bindings (`u0_binding`, `l1_binding`, …) produce core **contracts** but often **skip** core generic pipelines, REQ receipts, and OTEL child spans. Section CLI (`--section`) and integrated spine diverge on U0, C0, PA, L2, and Exit.

| Priority | Count | Theme |
|----------|-------|--------|
| **P0** | 5 | Dual product path; U0 package not core-ingested; PA not on core pipeline; section bypasses spine contracts; missing signed handoffs |
| **P1** | 12 | Per-layer receipt/span gaps; L1/L0 HMAC & refinement; C0 graph; L2 SealedL2Artifact; Exit X1/X3 spine |
| **P2** | 8 | L3 packaging; L6 exhaust schema; docs/registry drift |
| **P3** | 3 | Accepted deferrals (L1 refine N/A, dual contract trees) |

---

## Reference map

| Layer | SSOT parent | apps_rg bind surface |
|-------|-------------|---------------------|
| U0 | [01_request_intake.md](../../reference/01_Request_Intake/01_request_intake.md) | [u0_binding.py](../../apps_rg/runtime/bindings/u0_binding.py) |
| L1 | [02_L1_Reasoning_Plan_Generation.md](../../reference/02_L1_Reasoning_Plan/02_L1_Reasoning_Plan_Generation.md) | [l1_binding.py](../../apps_rg/runtime/bindings/l1_binding.py) |
| L0/L3 | [03_L0_Route_Decision_Switching_L3.md](../../reference/03_L0_Route_Decision/03_L0_Route_Decision_Switching_L3.md) | [l0_binding.py](../../apps_rg/runtime/bindings/l0_binding.py) |
| C0 | [03A_C0_Context_Engine/](../../reference/03A_C0_Context_Engine/) | [c0_binding.py](../../apps_rg/runtime/bindings/c0_binding.py), [c03_graphrag_bound.py](../../apps_rg/runtime/c03_graphrag_bound.py) |
| PA | [03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md](../../reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md) | [pa_binding.py](../../apps_rg/runtime/bindings/pa_binding.py), [compiler.py](../../apps_rg/prompt_assembly/compiler.py) |
| L2 | [04_L2_Execute.md](../../reference/04_L2_Execute/04_L2_Execute.md) | [l2_binding.py](../../apps_rg/runtime/bindings/l2_binding.py), section lanes |
| Exit | [05_Live_Runtime_Exit_Control_&_Evaluation.md](../../reference/05_Exit_Evaluation_and_Control/05_Live_Runtime_Exit_Control_&_Evaluation.md) | [exit_binding.py](../../apps_rg/runtime/bindings/exit_binding.py), lane X2/X3 |
| L6 | [06_Shadow_Evaluation_System_Learning.md](../../reference/06_L6_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning.md) | [runtime/shadow/](../../apps_rg/runtime/shadow/) |

**Benchmark (other apps):** [apps_research/runtime/u0/binding.py](../../apps_research/runtime/u0/binding.py) uses `RuntimeCustomizationPackage`; apps_rg does **not** call [u0_runtime_package_binding.py](../../agentic_core/runtime/entry/u0_runtime_package_binding.py).

---

## Cross-cutting gaps

| gap_id | Sev | REQ / theme | Finding |
|--------|-----|-------------|---------|
| GAP-SPINE-DUAL-PATH | P0 | All layers | Section CLI vs integrated spine — different U0, C0, PA, L2, Exit ([one_spine_inventory.py](../../apps_rg/runtime/one_spine_inventory.py)) |
| GAP-SPINE-U0-PKG | P0 | REQ-U0-* | No `runtime_customization_package.yaml` SSOT; `u0_validate_apps_rg` inlines `profile_manifest` refs — core package binding unused |
| GAP-SPINE-PA-CORE | P0 (partial W5) | REQ-PA-* | Integrated path: `pa_compose_apps_rg` → `assemble_prompt` / PA.0–PA.7; section lanes still domain compiler + slot BOM receipt (core PA on section front spine deferred W6+) |
| GAP-SPINE-SIGN | P0 (partial W3/W5/W6) | REQ-L0-HMAC-001, PA.7, L2-ENTRY | W3 route HMAC; W5 PA manifest HMAC; W6 governed L2 marker — full `L2HandoffEnvelope` still open |
| GAP-SPINE-L2-SECTION | P0 (partial W6) | REQ-L2-* | Section `sealed_l2_artifact.json` + L2ExecutionPacket receipts; integrated `l2_execute_apps_rg` via governed compose |
| GAP-SPINE-EXIT-ONE | P0 (partial W6) | REQ-EXIT-* | Section `exit_disposition_receipt.json` + ExitEvalPipeline; integrated exhaust bundle — spine RuntimeExhaust on section lanes W7 |
| GAP-SPINE-OTEL | P1 | All `u0.*`…`l6.*` spans | Parent span trees largely DOC_ONLY on product paths |
| GAP-SPINE-REJECT | P1 | REQ-U0-REJECTION-TERMINAL-001 | App raises `ValueError` vs sealed `RejectedRequest` |

---

## U0 — [01_request_intake.md](../../reference/01_Request_Intake/01_request_intake.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-U0-INGRESS-ENVELOPE-001 | PARTIAL | Coerces envelope + required keys | No `envelope_validated` flag / schema hash receipt |
| REQ-U0-IDENTITY-STAMP-001 | PARTIAL | Stamps request/run/trace/tenant/replay | Missing `session_id`, `trace_root`, `caller_scope_baseline` per spec |
| REQ-U0-QUOTA-BASELINE-001 | MISSING | No quota ledger | No `RejectedRequest` quota_exceeded |
| REQ-U0-SCHEMA-NORMALIZE-001 | PARTIAL | Synthesizes task/query in app_payload | Not separate normalize substep + `payload_schema_hash` |
| REQ-U0-IDEMPOTENCY-001 | PARTIAL | `idempotency_key` derived | No duplicate `RejectedRequest` / idempotency receipt |
| REQ-U0-ORIGIN-TRIAGE-001 | PARTIAL | Forbidden authority field scan | No `origin_trust_class`, `data_labels[]` |
| REQ-U0-REJECTION-TERMINAL-001 | DIVERGENT | Raises on failure | No sealed `RejectedRequest` artifact |
| REQ-U0-VALIDATED-HANDOFF-001 | PARTIAL | Returns `ValidatedRequest` | Section path may skip full U0 ([GAP-SPINE-DUAL-PATH](../../apps_rg/runtime/section_spine_terminology.py)) |
| REQ-U0-OBSERVABILITY-001 | MISSING | No `u0.*` span tree on product path | — |

**P0:** GAP-SPINE-U0-PKG — ingest domain packet via [u0_runtime_package_binding.py](../../agentic_core/runtime/entry/u0_runtime_package_binding.py); add `apps_rg/config/domain_contract/runtime_customization_package.yaml` + `runtime_package_registry.yaml` (pattern: [apps_qna/config/domain_contract/runtime_package_registry.yaml](../../apps_qna/config/domain_contract/runtime_package_registry.yaml)).

---

## L1 — [02_L1_Reasoning_Plan_Generation.md](../../reference/02_L1_Reasoning_Plan/02_L1_Reasoning_Plan_Generation.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-L1-PLAN-NO-EXECUTE-001 | ALIGNED | Single-pass plan, no tools | — |
| REQ-L1-INTENT-FRAME-001 | PARTIAL | task/query/support/output on contract | No explicit `intent_frame` |
| REQ-L1-AMBIGUITY-REGISTER-001 | ALIGNED | `ambiguity_register` on `L1PlanContract` when signals incomplete | — |
| REQ-L1-PLAN-PRIORS-001 | PARTIAL | Profile refs in app_payload | No `plan_priors_id` / `rule_bundle_id` on contract |
| REQ-L1-REFINE-LOOP-BOUND-001 | N/A | Single pass by design | Document waiver |
| REQ-L1-ROUTE-HINTS-ADVISORY-001 | ALIGNED | `route_hints` + ADVISORY_ONLY | W-A closed |
| REQ-L1-PLAN-VALIDATION-001 | PARTIAL | `validation_receipt_id` on plan path (manifest + planning digests) | Self-repair loop still N/A |
| REQ-L1-HANDOFF-CONTRACT-001 | ALIGNED | One `L1PlanContract` per request | — |

**P1:** GAP-SPINE-L1-INTENT-FRAME (closed W3 for ambiguity + validation receipt)

---

## L0 / L3 — [03_L0_Route_Decision_Switching_L3.md](../../reference/03_L0_Route_Decision/03_L0_Route_Decision_Switching_L3.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-L0-ROUTE-EXACTLY-ONE-001 | ALIGNED | One `RouteContract` | — |
| REQ-L0-DETERMINISTIC-DIGEST-001 | ALIGNED | `route_digest` via `l0_route_evidence` on product binding | — |
| REQ-L0-EXECUTION-FORM-001 | ALIGNED | Profile-driven forms | — |
| REQ-L0-NO-RETRIEVE-EXECUTE-001 | ALIGNED | Binding only | — |
| REQ-L0-HMAC-SIGNED-001 | ALIGNED | `hmac_sig` + `signature` on `RouteContract` (pytest secret in CI) | Production secret via `APPS_RG_ROUTE_HMAC_SECRET` |
| REQ-L0-CACHE-FALLBACK-001 | PARTIAL | Cache preflight in dispatch | Terminal cache route proof incomplete |
| REQ-L0-GROUNDED-HANDOFF-001 | PARTIAL | Integrated dispatch wires C0→PA | Section path bypasses |
| REQ-L3-MANAGED-WORKFLOW-ELIGIBLE-001 | PARTIAL | Core W9 E2E + [L3_managed_workflow_scope.md](../../apps_rg/config/domain_contract/L3_managed_workflow_scope.md) (core-owned) | No apps_rg L3 step packaging |
| REQ-L3-DAG-BOUNDED-001 | PARTIAL | Core generic | — |
| REQ-L0-NO-REROUTE-MID-RUN-001 | ALIGNED | Single route per run | — |

**P0/P1:** GAP-SPINE-L0-HMAC closed W3; GAP-AR-L3-1 (no app L3 step packaging; scope doc added)

---

## C0 — [03A_C0_Context_Engine](../../reference/03A_C0_Context_Engine/)

| Stage | Fit | apps_rg | Gap |
|-------|-----|---------|-----|
| C0.0 Preflight | PARTIAL | `c0_binding` + section `StopAsEvidenceGapError` when grounding weak | Evidence room still ledger-first |
| C0.1 Retrieval plan | PARTIAL | Dense + sparse | Graph lane NA |
| C0.2 Evidence fetch | PARTIAL | Chroma when enabled | Live sparse/BM25 blocked in some envs |
| C0.3 Graph RAG | MISSING | Deferred | GAP-AR-C0-3 |
| C0.4 Stratify | ALIGNED | FEC support status | — |
| C0.5 FEC | PARTIAL | Spine `c0_retrieve_apps_rg` on section FEC bridge (W4); evidence room emits FEC | Core canonical C0.5 still open for all lanes |
| C0.6 Weak support retry | PARTIAL | Env-gated | GAP-AR-C0-4 |

**P0 (path A):** GAP-SPINE-C0-SECTION — W4 closed for product FEC bridge (`section_c0_retrieve`); evidence-room ledger path remains; core Graph RAG still deferred.

---

## PA — [03B_PA_Prompt_Assembly](../../reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md)

See [pa_exec_flowchart_gap_analysis_20260523.md](pa_exec_flowchart_gap_analysis_20260523.md). **E0 SSOT closed** (b8e4f1). **W5 (2026-05-23):** integrated PA wired to core `assemble_prompt`. **Spine pipeline open:** GAP-SPINE-PA-CORE (section full core PA), GAP-PA-SIGN-1 / GAP-SPINE-SIGN (L2 handoff W6).

---

## L2 — [04_L2_Execute.md](../../reference/04_L2_Execute/04_L2_Execute.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-L2-NO-DIRECT-L4-WRITE-001 | ALIGNED | No direct L4 in bindings | — |
| REQ-L2-ENTRY-AUTHORITY-001 | PARTIAL | Envelope adapter checks CPA type | Section: direct provider call |
| REQ-L2-E1-PREP-RECEIPT-001 | PARTIAL | Frozen context in adapter | No full `prep_receipt.json` per E1 |
| REQ-L2-E2-SAME-BLUEPRINT-VALIDATION-001 | PARTIAL | Precheck exists | E1..E5 sequencer not proven on section |
| REQ-L2-E3-EXEC-LANES-001 | DIVERGENT | Section vLLM/Qwen direct | GAP-AR-L2-1 |
| REQ-L2-E5-SEAL-ARTIFACT-001 | MISSING | Section: `l2_output.json` | GAP-AR-L2-4 — no `SealedL2Artifact` |
| REQ-L2-SEQUENCER-CONTRACT-001 | PARTIAL | Core package-driven path | Section skips E1→E5 order proof |

**P0:** GAP-SPINE-L2-SECTION — section L2 must seal `SealedL2Artifact` or block with spine disposition.

---

## Exit — [05_Live_Runtime_Exit_Control_&_Evaluation.md](../../reference/05_Exit_Evaluation_and_Control/05_Live_Runtime_Exit_Control_&_Evaluation.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-EXIT-INPUT-NORMALIZATION-001 | PARTIAL | Lane aggregates | No canonical `ExitReviewPacket` on section path |
| REQ-EXIT-EXACTLY-ONE-DISPOSITION-001 | DIVERGENT | Path A: lane X3; Path B: ExitEvalPipeline | GAP-AR-EXIT-1 |
| REQ-EXIT-DISPOSITION-VOCAB-001 | PARTIAL | ALLOW/REVIEW/BLOCK locally | Not always `X3A`..`X3E` spine vocabulary |
| REQ-EXIT-X1A-X1F-CHECKS-001 | PARTIAL | X2 + X1D on section | Not full X1A..X1J bundle |
| REQ-EXIT-RUNTIME-EXHAUST-001 | PARTIAL | Lane `runtime_exhaust_bundle.json` | GAP-AR-EXIT-3 — not spine sealed bundle |
| REQ-EXIT-NO-L6-RESCUE-001 | ALIGNED | L6 shadow after boundary | — |

**P0:** GAP-SPINE-EXIT-ONE — one Exit path + exactly one X3 per run on all product entrypoints.

---

## L6 — [06_Shadow_Evaluation_System_Learning.md](../../reference/06_L6_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning.md)

| REQ_ID | Fit | apps_rg | Gap |
|--------|-----|---------|-----|
| REQ-L6-NO-LIVE-MUTATION-001 | ALIGNED | Shadow offline only | — |
| REQ-L6-NO-DIRECT-L4-WRITE-001 | ALIGNED | No L4 from shadow | — |
| REQ-L6-EXHAUST-INGEST-001 | PARTIAL | Shadow package from lane | Input not always sealed spine `RuntimeExhaustBundle` |
| REQ-L6-EVAL-BEFORE-LEARN-001 | PARTIAL | Shadow eval package | No full `EvalRecord` / gauntlet / UWG promotion path on section |
| REQ-L6-PROMOTE-VIA-UWG-001 | MISSING | — | Learning adapter in core; apps_rg section does not emit `LearningPromotionRequest` |

**P2 (partial W7):** GAP-SPINE-L6-EXHAUST — section `runtime_exhaust_bundle.json` + L6 handoff gate; integrated core bundle via W6 governed exit; full L6 promotion pipeline still deferred.

---

## Two-path matrix (product)

| Capability | `--section` | Integrated |
|------------|-------------|------------|
| Core U0 package ingest | No | No |
| `RejectedRequest` terminal | No | No |
| Spine FEC from C0 | No (proof-pool / shape) | Yes |
| Core PA pipeline | No (local compiler) | No (`pa_compose_apps_rg`) |
| `SealedL2Artifact` | No | Partial |
| Spine Exit X3 + exhaust | No | Yes (ExitEvalPipeline) |
| L6 sealed exhaust ingest | Shadow only | Partial |

---

## Gap roll-up

| Owner | P0 | P1 | P2 | P3 |
|-------|----|----|----|-----|
| apps_rg (GAP-SPINE-AR / GAP-AR-*) | 5 | 10 | 7 | 2 |
| agentic_core (GAP-SPINE-AC / GAP-AC-*) | 0 | 2 | 1 | 0 |

**P0 blockers for “one governed pipeline”:**

1. GAP-SPINE-U0-PKG  
2. GAP-SPINE-DUAL-PATH  
3. GAP-SPINE-PA-CORE  
4. GAP-SPINE-SIGN  
5. GAP-SPINE-EXIT-ONE (section exit)

---

## Architecture authorization (W0 — 2026-05-23)

```text
AUTHORIZATION_DECISION: plan=pa-exec-flowchart-gap-f2a8c3 decision=ACCEPTED authorized_by=author_gate decisive_reason="spine_full_convergence — one governed pipeline U0→L6+PA"
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg, selected=spine_full_convergence, outcome=executed, confidence=0.88, decision_id=dec_19e55e81295a26123
```

| Binding | Authorized approach |
|---------|---------------------|
| U0 | Core [u0_runtime_package_binding.py](../../agentic_core/runtime/entry/u0_runtime_package_binding.py) ingests `RuntimeCustomizationPackage` from `apps_rg/config/domain_contract/` |
| Entry | All product lanes via [section_front_spine_bridge.py](../../apps_rg/runtime/section_front_spine_bridge.py) after W2 |
| PA | apps_rg [compiler.py](../../apps_rg/prompt_assembly/compiler.py) builds domain slots → core [assemble_prompt](../../agentic_core/prompt_governance/orchestrator.py) (PA.0–PA.8) |
| Core edits | Allowed with migration receipt per plan `touches_agentic_core: true` |

Precedent at decision time: **none** (`COLD_CORPUS`). Rejected alternate: incremental U0-only (`u0_package_only`).

---

## Explicit non-claims

- No live E2E proof run for integrated spine on this document date.
- REQ tables are parent-level; child REQ files not fully converted in repo.
- `agentic_core` changes require author-gate + migration receipt.

---

## Related artifacts

| Artifact | Role |
|----------|------|
| [apps_rg_pa_prompt_contract.md](../../guides/apps_rg_pa_prompt_contract.md) | PA 8-slot app contract |
| [apps-rg-pa-ssot-gap-b8e4f1.md](../../.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md) | Closed E0 hydration wave |
| [pa_exec_flowchart_gap_audit.json](../../artifacts/apps_rg/plans/pa_exec_flowchart_gap_audit.json) | PA-only machine audit |
