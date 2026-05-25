# agentic_core Agent Inventory — Runtime Assessment

**Generated:** 2026-05-25T13:23:39Z

**STATUS:** PARTIAL

## Executive summary

| Metric | Count |
|--------|------:|
| Candidates scanned (AST `*Agent` / aliases) | 118 |
| Truly an agent (reasoning + autonomy heuristic) | 87 |
| Not agent / wrapper / shim (heuristic) | 31 |
| Registered in `AGENT_TAXONOMY_MAP` (`agentic_core` only) | 118 |
| **E2E product-spine invoked (artifact-proven class)** | **0** |
| True agents without E2E product-spine proof | 87 |

### Inventory role rollup (`*Agent` candidates only)

| Inventory role | Count |
|----------------|------:|
| TRUE_AGENT_NOT_ON_PRODUCT_SPINE | 74 |
| GOVERNANCE_CERTIFIER_OR_VALIDATOR | 20 |
| HEALER_OR_DEV_AGENT | 6 |
| UTILITY_OR_WRAPPER | 17 |
| SHIM_OR_DEAD_LEGACY | 1 |

Canonical product spine **functions** (not `*Agent` classes) are listed under [Product spine truth](#decision-1--product-spine-truth) — they are not AST candidates.

## Architecture conclusion

The canonical E2E product spine is currently a **governed functional pipeline**, not a class-agent execution graph. `*Agent` classes exist as adjacent governance, healing, validation, dev, or legacy capabilities unless a receipt proves runtime invocation. Therefore the current taxonomy must **not** be interpreted as the product runtime graph.

<a id="decision-1--product-spine-truth"></a>
## Decision 1 — Product spine truth

This decision is **separate** from inventory/taxonomy cleanup.

| Invariant | Value |
|-----------|-------|
| E2E invoked class count | **0** |
| Taxonomy registration implies runtime invocation | **No** |
| Class name / inheritance implies runtime invocation | **No** |
| Current HOW / spine proof artifacts prove | **Stage / function execution only** (e.g. `U0_INTAKE`, `L1_PLAN`, `producer_component` on entrypoint) |

No `agentic_core` `*Agent` class may be claimed as product-spine-invoked unless a future runtime artifact explicitly proves class identity (see [Acceptance invariant](#acceptance-invariant)).

### Canonical product spine functions (not `*Agent` classes)

| Function | Module |
|----------|--------|
| `run_integrated_single_action_spine` | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` |
| `run_request_intake` | `agentic_core/L0_routing/intake/pipeline.py` |
| `validated_request_to_plan_contract` | `agentic_core/L1_cognition/bridges/u0_to_l1_plan.py` |
| `check_route_gates` | `agentic_core/L0_routing/reasoning/route_gates.py` |
| `resolve_l2_recipe` | `agentic_core/runtime/l2_recipe_resolver.py` |
| `ExitEvalPipeline.run` | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` |

L2 execution on the product path is **`resolve_l2_recipe` → `apps_*` step callables** (out of scope for this `agentic_core` class inventory).

<a id="decision-2--inventory--taxonomy-cleanup"></a>
## Decision 2 — Inventory / taxonomy cleanup

This decision is **not** equivalent to Decision 1. Do **not** collapse all L5/healing classes to `NOT_AGENT` or delete-by-default. Separate:

1. **Agenthood classification** (`Truly an Agent?` column)
2. **Taxonomy registration** (`AGENT_TAXONOMY_MAP` — metadata only)
3. **Product-spine invocation** (`Invoked in E2E spine run?` — artifact-only)
4. **Runtime proof** (receipts / OTEL / registry binding)

### Role definitions

| Role | Meaning |
|------|---------|
| `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | Bounded autonomous agent; not artifact-proven on canonical product spine |
| `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | L5 certify/validate/check surfaces; not product routing/execution/X3/UWG |
| `HEALER_OR_DEV_AGENT` | Healing/dev/CI mission agents; off product spine unless future receipt proves otherwise |
| `UTILITY_OR_WRAPPER` | Base, protocol, L2 wrapper, monitor stub |
| `SHIM_OR_DEAD_LEGACY` | Deprecated re-export or empty shim module |

- Taxonomy registers **118** `agentic_core` classes; AST found **118** candidates.
- **-31** heuristic true-agents lack taxonomy rows — register with **off-spine** role, not as product runtime owners.

<a id="acceptance-invariant"></a>
## Acceptance invariant

No `agentic_core` class may be described as **product-spine invoked** unless an E2E artifact contains at least one of:

- class name
- module path
- registry selected agent id
- execution profile id bound to that class
- OTEL span naming that class/module
- receipt producer/consumer/executor naming that class/module

**Current inspection:** 0/118 candidates satisfy this invariant.

### Runtime proof attempt (harness)

- Spine harness run exit **0** (`_test_mode=True`, mock L2 callable)
- Artifacts dir: [`_spine_proof_run/`](artifacts/reports/agent_inventory/_spine_proof_run/) (18 JSON files)
- [`agentic_core_spine_proof.json`](artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_spine_proof.json): `run_id=95a3e615-ff22-4185-aaa0-725852a96284`, `trace_root=trace-5ab645474d8c4a6f873ce4bc5c3ba8fa`, `success=False`
- [`agentic_core_how_trace.json`](artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_how_trace.json): stages=['U0_INTAKE', 'L1_PLAN', 'L0_ROUTE', 'C0_CONTEXT', 'PROMPT_ASSEMBLY', 'L3_ORCHESTRATION', 'L2_EXECUTE', 'EXIT_X3', 'UWG_L4', 'L6_RUNTIME_EXHAUST']… (no `*Agent` class fields)
- `producer_component` in receipts: `agentic_core.runtime.entrypoints.integrated_single_action_spine_run` (functional entrypoint, not a class agent)
- Proof class: **MOCK_ONLY_PROOF** for spine **functions**; **0** rows with per-class `*Agent` invocation (`incidental_agent_strings=0`).

### W3 live spine proof (production path, no mock L2)

- Report: [`w3_live_spine_proof_report.json`](artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json) (`runtime_proof_class=LIVE_RUNTIME_PROOF`, `mock_harness_backfill=false`)
- Spine attempted: `True`; `a1_invoked_agent_classes=0`; `mock_mode_detected=False`
- L2 fault (live): `L2_EXECUTION_ERROR:RuntimeError:FAILED_MODULAR_R4: decisive='FAIL' failure='fatal_lane_recipe_policy:headline:PHASE1_NO_RUN_DIR; executive_summary:PHASE1_PRIOR_LANE_FAILED; unify_bullets:PHASE1_PRIOR_LANE_FAILED; unify_narrative:PHASE1_PRIO…`
- Evaluation: [`agent_inventory_w3_class_identity_evaluation.md`](docs/reports/cursor/agent_inventory_w3_class_identity_evaluation.md) — **defer** class identity on HOW
- Taxonomy: **no** `ARTIFACT_PROVEN` updates from W3 (`taxonomy_artifact_proven_updates=0`)

### Harness note (not architecture proof)

A minimal import shim at [`agentic_core/L6_system_learning/snapshot/__init__.py`](agentic_core/L6_system_learning/snapshot/__init__.py) re-exports `RuntimeADGSnapshot` so `spine_proof_bundle` can import during **report generation only**. This enables the mock-L2 spine harness to emit HOW/spine JSON; it does **not** prove class-agent architecture or live product execution.

### Layer misplacements (static)

- `SemanticGatekeeperAgent` — L3 path, safety role
- `GospelSyncAgent`, `BootstrapAgent`, `PreCommitSovereignAgent` — L5 folder with L0 routing bases
- L4/L7: no `*Agent` classes (expected)

## NON_CLAIMS

- This report does **not** prove the `*Agent` classes are unused everywhere.
- This report proves they are **not artifact-proven** as invoked by the canonical E2E spine run inspected.
- Mock L2 harness proof is valid only for spine **path shape** (stage/function flow), not live product model/tool execution.
- Taxonomy registration, static import fan-in, and class naming are **not** runtime invocation.

---

## Main inventory table

| Agent | Module path | Layer | Inventory role | Truly an Agent? | Reasoning | Autonomy | Correct layer? | Expected spine role | Invoked E2E? | Runtime proof | Static evidence | Required fix |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AdversarialProbeAgent | `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| AdversarialRedTeamerAgent | `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ArchitectureGovernorAgent | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=22 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ArchitectureGovernorValidatorAgent | `agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | REGISTER_TAXONOMY_AS_CERTIFIER |
| ASTValidatorAgent | `agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py` | L1 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | plan/advisory only | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | REGISTER_TAXONOMY_AS_CERTIFIER |
| AutonomousThreatEvolutionAgent | `agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| AutonomyGuardianAgent | `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=11 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| BenchmarkingAgent | `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | REGISTER_TAXONOMY_AS_CERTIFIER |
| BootstrapAgent | `agentic_core/L5_safety/reasoning/BootstrapAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | NO — L0 base in L5 folder | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| BoundaryTestingAgent | `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ChaosEngineeringAgent | `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| CodeDeduplicationAgent | `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| CodeDetectorAgent | `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=10 | REGISTER_TAXONOMY_AS_CERTIFIER |
| CodeEnforcerAgent | `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| CodeFormatterAgent | `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | REGISTER_TAXONOMY_AS_CERTIFIER |
| CodeHealerAgent | `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| CodeJanitorAgent | `agentic_core/L5_safety/reasoning/CodeJanitorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=9 | REGISTER_TAXONOMY_AS_CERTIFIER |
| CodeValidatorAgent | `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=14 | REGISTER_TAXONOMY_AS_CERTIFIER |
| CognitiveDispositionAgent | `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; execution_profile_registry; git_grep_agentic_core_files=12 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ComplexityAnalyzerAgent | `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ConstitutionalReviewerAgent | `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| CostGovernorAgent | `agentic_core/L5_safety/reasoning/CostGovernorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | LLM API + prompts | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | REGISTER_TAXONOMY_AS_CERTIFIER |
| CoverageAgent | `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | KEEP_AS_UTILITY |
| CredentialScannerAgent | `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DagEngineAgent | `agentic_core/L3_orchestration/reasoning/DagEngineAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DAGMutatorAgent | `agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DDDAlignmentAgent | `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DependencyPruningAgent | `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DocstringComplianceAgent | `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DocumentationAgent | `agentic_core/L5_safety/reasoning/DocumentationAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DomainPlannerAgent | `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DuplicateCodeDetectorAgent | `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DynamicSealAgent | `agentic_core/L5_safety/reasoning/DynamicSealAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| EmbeddingSovereignAgent | `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | L2 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | bounded execution (product spine uses apps_* L2 recipe, not these classes) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=20 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| FeasibilityAnalystAgent | `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| FileClassificationHealerAgent | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | REGISTER_TAXONOMY_AS_CERTIFIER |
| FileClassificationValidatorAgent | `agentic_core/L5_safety/reasoning/file_classification_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | validate-only; dispatches via HEALER_REGISTRY without local act loop | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | REGISTER_TAXONOMY_AS_CERTIFIER |
| FilesystemSSOTReconcilerAgent | `agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | NO — L0 base in L5 folder | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=11 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| FilesystemSSOTValidatorAgent | `agentic_core/L5_safety/reasoning/filesystem_ssot_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | validate-only; dispatches via HEALER_REGISTRY without local act loop | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | REGISTER_TAXONOMY_AS_CERTIFIER |
| FissionManagerAgent | `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| GenerativeGuardAgent | `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| GitHygieneAgent | `agentic_core/L5_safety/reasoning/GitHygieneAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| GospelSyncAgent | `agentic_core/L5_safety/reasoning/GospelSyncAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | NO — L0 base in L5 folder | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| GovernanceAgent | `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| GravityLeakRepairAgent | `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=18 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| GravityLeakValidatorAgent | `agentic_core/L5_safety/validators/gravity_leak_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | analysis without autonomous act | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | REGISTER_TAXONOMY_AS_CERTIFIER |
| GravityStateAgent | `agentic_core/L3_orchestration/reasoning/GravityStateAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | KEEP_AS_UTILITY |
| GravityValidatorAgent | `agentic_core/L5_safety/reasoning/gravity_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | AST / deterministic code analysis | validate-only; dispatches via HEALER_REGISTRY without local act loop | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | REGISTER_TAXONOMY_AS_CERTIFIER |
| HierarchyHealerAgent | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | REGISTER_TAXONOMY_AS_CERTIFIER |
| HierarchyValidatorAgent | `agentic_core/L5_safety/reasoning/hierarchy_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | validate-only; dispatches via HEALER_REGISTRY without local act loop | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | REGISTER_TAXONOMY_AS_CERTIFIER |
| HygieneGuardianAgent | `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| IntegrityGateExecutorAgent | `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| InterfaceBoundaryAgent | `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| IOrchestratorAgent | `agentic_core/L3_orchestration/types/orchestrator_types.py` | L3 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| ITieredAgent | `agentic_core/interfaces/orchestrator_protocol.py` | other | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2EmbeddingSovereignAgent | `agentic_core/L2_execution/utils/__init__.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2ExecutionAgent | `agentic_core/L2_execution/types/l2_execution_contract.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2RedisSovereignAgent | `agentic_core/L2_execution/utils/l2_agent_wrappers.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2SovereignMCPGatewayAgent | `agentic_core/L2_execution/utils/l2_agent_wrappers.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2StructuredEngineAgent | `agentic_core/L2_execution/utils/l2_agent_wrappers.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L2SubAtomicRegistryAgent | `agentic_core/L2_execution/utils/l2_agent_wrappers.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| L5SafetyExerciserAgent | `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| LocationHealerAgent | `agentic_core/L5_safety/utils/location_healer_util.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=19 | REGISTER_TAXONOMY_AS_CERTIFIER |
| LocationValidatorAgent | `agentic_core/L5_safety/reasoning/location_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=7 | REGISTER_TAXONOMY_AS_CERTIFIER |
| MetaLearningAgent | `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py` | L1 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | plan/advisory only | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; execution_profile_registry; git_grep_agentic_core_files=12 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| NamingAgent | `agentic_core/L5_safety/reasoning/NamingAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=19 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| NervousSystemAgent | `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| NeuralAutoImmuneAgent | `agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ObservabilityProbeExecutorAgent | `agentic_core/L6_observability/reasoning/observability_probe_executor.py` | L6 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | completed-run observe only — no current-run rescue | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| OrchestrationHandshakeAgent | `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | KEEP_AS_UTILITY |
| PascalSovereigntyAgent | `agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | REGISTER_TAXONOMY_AS_CERTIFIER |
| PerformanceAnalystAgentSimple | `agentic_core/L6_observability/utils/engines/PerformanceAnalystAgentSimple.py` | L6 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | completed-run observe only — no current-run rescue | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| PolicyNeuralAutoImmuneAgent | `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| PreCommitSovereignAgent | `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | NO — L0 base in L5 folder | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| PredictiveCostAuditorAgent | `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RedisSovereignAgent | `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | L2 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | bounded execution (product spine uses apps_* L2 recipe, not these classes) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=12 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RedSentinelAgent | `agentic_core/L5_safety/reasoning/RedSentinelAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=2 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RedTeamAgent | `agentic_core/L5_safety/reasoning/RedTeamAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RegressionOracleAgent | `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ReportLocationAgent | `agentic_core/L5_safety/reasoning/ReportLocationAgent.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| ResourceManagerAgent | `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RiskAssessorAgent | `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| RootCustomsAgent | `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` | L0 | `SHIM_OR_DEAD_LEGACY` | NO | delegates to root_customs_util (deterministic routing rules) | deprecated shim; no independent authority envelope | NO (L0 util is canonical) | none — product spine uses run_request_intake/check_route_gates, not this class | NO (DEAD_OR_LEGACY) | none | shim docstring; util replacement | ARCHIVE_OR_DELETE_SHIM |
| RootHygieneHealerAgent | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| RootHygieneValidatorAgent | `agentic_core/L5_safety/reasoning/root_hygiene_validator.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | NO | rule-based validation / classification | validate-only; dispatches via HEALER_REGISTRY without local act loop | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | REGISTER_TAXONOMY_AS_CERTIFIER |
| SafetyDetectorAgent | `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SafetyExecutorAgent | `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SafetyInspectorAgent | `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SecurityManagerAgent | `agentic_core/L5_safety/reasoning/SecurityManagerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SelfUpdatingSafetyEngineAgent | `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SemanticGatekeeperAgent | `agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SovereignActionPlaneAgent | `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SovereignBaseAgent | `agentic_core/base_agents/SovereignBaseAgent.py` | base | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| SovereignMCPGateway | `agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py` | L2 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | bounded execution (product spine uses apps_* L2 recipe, not these classes) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=7 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SovereignRAGManager | `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | knowledge | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | RAG/retrieval-adjacent (C0/L4 binding by proof only) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SprawlInspectorAgent | `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SSOTFolderCleanupAgent | `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py` | L0 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | route/intake (not L2 exec, not X3, not UWG) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StateManagementAgent | `agentic_core/L3_orchestration/reasoning/StateManagementAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | none detected | passive/telemetry-only surface | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | KEEP_AS_UTILITY |
| StrategicRecommendationAgent | `agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py` | L1 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | plan/advisory only | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StrategyCoordinatorAgent | `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StrategyScenarioSimulatorAgent | `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=1 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StructuralEngineerAgent | `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StructuralValidatorAgent | `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | L5 | `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=9 | REGISTER_TAXONOMY_AS_CERTIFIER |
| StructuredEngineAgent | `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | L2 | `UTILITY_OR_WRAPPER` | NO | contract/protocol or adapter stub | none | N/A | L2 contract wrapper or base/protocol | NO (STATIC_ONLY) | none | wrapper/base naming convention | KEEP_AS_UTILITY |
| StructureEnforcerAgent | `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=12 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| StructureHealerAgent | `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` | L5 | `HEALER_OR_DEV_AGENT` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=7 | KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH |
| SubAtomicAgent | `agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=13 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SubatomicHopAgent | `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | KEEP_AS_UTILITY |
| SubAtomicRegistryAgent | `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | L2 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | LLM API + prompts | execute/heal/run-style methods present | YES | bounded execution (product spine uses apps_* L2 recipe, not these classes) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=8 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| SystemArchitectAgent | `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; execution_profile_registry; git_grep_agentic_core_files=7 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| TerritoryChangeHandlerAgent | `agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| TestGeneratorAgent | `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| ToolsmithAgent | `agentic_core/L2_execution/reasoning/ToolsmithAgent.py` | L2 | `UTILITY_OR_WRAPPER` | NO | deterministic policy/heuristic reasoning | analysis without autonomous act | YES | bounded execution (product spine uses apps_* L2 recipe, not these classes) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=6 | KEEP_AS_UTILITY |
| TypeHintFixerAgent | `agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| TypeMechanicAgent | `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=5 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| UnifiedAgent | `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py` | L3 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | deterministic policy/heuristic reasoning | execute/heal/run-style methods present | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=14 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| UnusedCleanupAgent | `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py` | L5 | `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | YES | AST / deterministic code analysis | execute/heal/run-style methods present | YES | governance/heal certification — not route/X3/UWG/L4 write/L6 learn | NO (REGISTRY_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=3 | UPDATE_TAXONOMY_OFF_SPINE_ROLE |
| DagRuntimeInspector | `agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py` | L3 | `UTILITY_OR_WRAPPER` | NO | none detected | passive/telemetry-only surface | YES | workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional) | NO (STATIC_ONLY) | none | AGENT_TAXONOMY_MAP; git_grep_agentic_core_files=4 | KEEP_AS_UTILITY |

## Layer-by-layer findings
### L0 (2 candidates, 1 true agents)

- **RootCustomsAgent** — `SHIM_OR_DEAD_LEGACY`; true_agent=NO; E2E=NO (DEAD_OR_LEGACY)
- **SSOTFolderCleanupAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)

### L1 (3 candidates, 3 true agents)

- **ASTValidatorAgent** — `GOVERNANCE_CERTIFIER_OR_VALIDATOR`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **MetaLearningAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **StrategicRecommendationAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)

### L2 (12 candidates, 4 true agents)

- **EmbeddingSovereignAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **L2EmbeddingSovereignAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **L2ExecutionAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **L2RedisSovereignAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **L2SovereignMCPGatewayAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **L2StructuredEngineAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **L2SubAtomicRegistryAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **RedisSovereignAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- … and 4 more (see table)

### L3 (19 candidates, 12 true agents)

- **CoverageAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **DagEngineAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **DAGMutatorAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **DagRuntimeInspector** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **DomainPlannerAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **FeasibilityAnalystAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **FissionManagerAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **GravityStateAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)
- … and 11 more (see table)

### L5 (77 candidates, 64 true agents)

- **AdversarialProbeAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **AdversarialRedTeamerAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **ArchitectureGovernorAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **ArchitectureGovernorValidatorAgent** — `GOVERNANCE_CERTIFIER_OR_VALIDATOR`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **AutonomousThreatEvolutionAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **AutonomyGuardianAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **BenchmarkingAgent** — `GOVERNANCE_CERTIFIER_OR_VALIDATOR`; true_agent=NO; E2E=NO (STATIC_ONLY)
- **BootstrapAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- … and 69 more (see table)

### L6 (2 candidates, 2 true agents)

- **ObservabilityProbeExecutorAgent** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)
- **PerformanceAnalystAgentSimple** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)

### base (1 candidates, 0 true agents)

- **SovereignBaseAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)

### knowledge (1 candidates, 1 true agents)

- **SovereignRAGManager** — `TRUE_AGENT_NOT_ON_PRODUCT_SPINE`; true_agent=YES; E2E=NO (REGISTRY_ONLY)

### other (1 candidates, 0 true agents)

- **ITieredAgent** — `UTILITY_OR_WRAPPER`; true_agent=NO; E2E=NO (STATIC_ONLY)

## Runtime proof appendix

### Commands

```bash
python docs/reports/agent_inventory/_generate_runtime_assessment.py
# attempted:
python -c "... run_integrated_single_action_spine(..., _test_mode=True) ..."
```

- Generator exit: **0** (this script)
- Spine run exit: **0**

### Artifacts inspected
- [`agentic_core_how_trace.json`](artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_how_trace.json)
- [`agentic_core_l7_route_family_coverage.json`](artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_l7_route_family_coverage.json)
- [`agentic_core_spine_proof.json`](artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_spine_proof.json)
- [`c0_bypass_receipt.json`](artifacts/reports/agent_inventory/_spine_proof_run/c0_bypass_receipt.json)
- [`exit_review_packet.json`](artifacts/reports/agent_inventory/_spine_proof_run/exit_review_packet.json)
- [`integrated_runtime_artifact_manifest.json`](artifacts/reports/agent_inventory/_spine_proof_run/integrated_runtime_artifact_manifest.json)
- [`l1_plan_contract.json`](artifacts/reports/agent_inventory/_spine_proof_run/l1_plan_contract.json)
- [`l3_bypass_receipt.json`](artifacts/reports/agent_inventory/_spine_proof_run/l3_bypass_receipt.json)
- [`r4_c0_bypass_receipt.json`](artifacts/reports/agent_inventory/_spine_proof_run/r4_c0_bypass_receipt.json)
- [`r4_identity_receipt.json`](artifacts/reports/agent_inventory/_spine_proof_run/r4_identity_receipt.json)
- [`r4_run_manifest.json`](artifacts/reports/agent_inventory/_spine_proof_run/r4_run_manifest.json)
- [`route_contract.json`](artifacts/reports/agent_inventory/_spine_proof_run/route_contract.json)
- [`runtime_exhaust_bundle.json`](artifacts/reports/agent_inventory/_spine_proof_run/runtime_exhaust_bundle.json)
- [`runtime_identity_envelope.json`](artifacts/reports/agent_inventory/_spine_proof_run/runtime_identity_envelope.json)
- [`runtime_trace_snapshot.json`](artifacts/reports/agent_inventory/_spine_proof_run/runtime_trace_snapshot.json)
- [`terminal_ret_packet.json`](artifacts/reports/agent_inventory/_spine_proof_run/terminal_ret_packet.json)
- [`validated_request.json`](artifacts/reports/agent_inventory/_spine_proof_run/validated_request.json)
- [`x3_disposition_receipt.json`](artifacts/reports/agent_inventory/_spine_proof_run/x3_disposition_receipt.json)

### Acceptable proof not found

- No in-repo `agentic_core_spine_proof.json` with per-agent invocation records
- No OTEL span bundle in repo tying class names to canonical product spine run
- `tools/certification/agentic_core_e2e` scenarios: **not_implemented** (no `run_scenario` hook)

## Fix plan (by inventory role)

Rollup is **taxonomy/inventory cleanup only** — not a mandate to wire every class to the product spine or bulk-relabel as `NOT_AGENT`.

### `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` (74)

- Typical action: `UPDATE_TAXONOMY_OFF_SPINE_ROLE`

- AdversarialProbeAgent
- AdversarialRedTeamerAgent
- ArchitectureGovernorAgent
- AutonomousThreatEvolutionAgent
- AutonomyGuardianAgent
- BootstrapAgent
- BoundaryTestingAgent
- ChaosEngineeringAgent
- CodeDeduplicationAgent
- CodeEnforcerAgent
- CognitiveDispositionAgent
- ComplexityAnalyzerAgent
- … +62 more

### `GOVERNANCE_CERTIFIER_OR_VALIDATOR` (20)

- Typical action: `REGISTER_TAXONOMY_AS_CERTIFIER`

- ASTValidatorAgent
- ArchitectureGovernorValidatorAgent
- BenchmarkingAgent
- CodeDetectorAgent
- CodeFormatterAgent
- CodeJanitorAgent
- CodeValidatorAgent
- CostGovernorAgent
- FileClassificationHealerAgent
- FileClassificationValidatorAgent
- FilesystemSSOTValidatorAgent
- GravityLeakValidatorAgent
- … +8 more

### `HEALER_OR_DEV_AGENT` (6)

- Typical action: `KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH`

- CodeHealerAgent
- GovernanceAgent
- GravityLeakRepairAgent
- ReportLocationAgent
- RootHygieneHealerAgent
- StructureHealerAgent

### `UTILITY_OR_WRAPPER` (17)

- Typical action: `KEEP_AS_UTILITY`

- CoverageAgent
- DagRuntimeInspector
- GravityStateAgent
- IOrchestratorAgent
- ITieredAgent
- L2EmbeddingSovereignAgent
- L2ExecutionAgent
- L2RedisSovereignAgent
- L2SovereignMCPGatewayAgent
- L2StructuredEngineAgent
- L2SubAtomicRegistryAgent
- OrchestrationHandshakeAgent
- … +5 more

### `SHIM_OR_DEAD_LEGACY` (1)

- Typical action: `ARCHIVE_OR_DELETE_SHIM`

- RootCustomsAgent
