---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agent_healing_capabilities_readable.md'
original_relative_path: 'agent_healing_capabilities_readable.md'
source_sha256: 780d53aed9ff3bf669cf7691abbeea200b40698524d6d5270f2a4effc482af35
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agent Qwen & Gemini-2.5-pro Capability Map

## How LLM invocation works (two paths)

```
PATH 1: @standard_heal decorator  (54 agents)
        -> HealEscalationPolicy.decide(confidence)
               confidence > 0.75   -> LOCAL_AGENT  (no LLM, deterministic)
               confidence 0.50-0.75 -> QWEN_VLLM   -> Qwen2.5-7B-Instruct (vLLM)
               confidence < 0.50   -> GEMINI_2_5_PRO -> gemini-2.5-pro

PATH 2: direct self.llm_generate() call  (3 agents)
        -> CognitiveDispositionAgent  provider=google, model=gemini-3-flash-preview
        -> FissionManagerAgent        provider=google, model=gemini-2.5-pro
        -> StructuredEngineAgent      provider=google, model=gemini-3-flash-preview
```

**Column definitions:**

| Column | Meaning |
|--------|---------|
| `Mechanism` | How the agent reaches the LLM |
| `Qwen` | Can invoke Qwen2.5-7B-Instruct (medium-confidence path via tier router) |
| `Gemini-2.5-pro` | Can invoke gemini-2.5-pro (low-confidence path OR direct call) |
| `Gemini-flash` | Can invoke gemini-3-flash-preview (direct call only) |

---

## L5 — Safety (36 of 69 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| AdversarialProbeAgent | @standard_heal | YES | YES | NO |
| AdversarialRedTeamerAgent | @standard_heal | YES | YES | NO |
| ArchitectureGovernorAgent | @standard_heal | YES | YES | NO |
| AutonomousThreatEvolutionAgent | @standard_heal | YES | YES | NO |
| BenchmarkingAgent | @standard_heal | YES | YES | NO |
| BootstrapAgent | @standard_heal | YES | YES | NO |
| BoundaryTestingAgent | @standard_heal | YES | YES | NO |
| ChaosEngineeringAgent | @standard_heal | YES | YES | NO |
| CodeDetectorAgent | @standard_heal | YES | YES | NO |
| CodeEnforcerAgent | @standard_heal | YES | YES | NO |
| CodeHealerAgent | @standard_heal | YES | YES | NO |
| CodeValidatorAgent | @standard_heal | YES | YES | NO |
| **CognitiveDispositionAgent** | @standard_heal + direct llm_generate | YES | YES | YES |
| ComplexityAnalyzerAgent | @standard_heal | YES | YES | NO |
| ConstitutionalReviewerAgent | @standard_heal | YES | YES | NO |
| CostGovernorAgent | @standard_heal | YES | YES | NO |
| DependencyPruningAgent | @standard_heal | YES | YES | NO |
| DocstringComplianceAgent | @standard_heal | YES | YES | NO |
| FileClassificationAgent | @standard_heal | YES | YES | NO |
| GitHygieneAgent | @standard_heal | YES | YES | NO |
| HierarchyAgent | @standard_heal | YES | YES | NO |
| HygieneGuardianAgent | @standard_heal | YES | YES | NO |
| IntegrityGateExecutorAgent | @standard_heal | YES | YES | NO |
| InterfaceBoundaryAgent | @standard_heal | YES | YES | NO |
| PolicyNeuralAutoImmuneAgent | @standard_heal | YES | YES | NO |
| PredictiveCostAuditorAgent | @standard_heal | YES | YES | NO |
| RedSentinelAgent | @standard_heal | YES | YES | NO |
| RedTeamAgent | @standard_heal | YES | YES | NO |
| RegressionOracleAgent | @standard_heal | YES | YES | NO |
| RootHygieneAgent | @standard_heal | YES | YES | NO |
| SelfUpdatingSafetyEngineAgent | @standard_heal | YES | YES | NO |
| SovereignActionPlaneAgent | @standard_heal | YES | YES | NO |
| SprawlInspectorAgent | @standard_heal | YES | YES | NO |
| StructureHealerAgent | @standard_heal | YES | YES | NO |
| TestGeneratorAgent | @standard_heal | YES | YES | NO |
| TypeHintFixerAgent | @standard_heal | YES | YES | NO |
| AutonomyGuardianAgent | none | NO | NO | NO |
| CodeDeduplicationAgent | none | NO | NO | NO |
| CodeFormatterAgent | none | NO | NO | NO |
| CredentialScannerAgent | none | NO | NO | NO |
| DDDAlignmentAgent | none | NO | NO | NO |
| DocumentationAgent | none | NO | NO | NO |
| DuplicateCodeDetectorAgent | none | NO | NO | NO |
| DynamicSealAgent | none | NO | NO | NO |
| FilesystemSSOTReconcilerAgent | none | NO | NO | NO |
| GenerativeGuardAgent | none | NO | NO | NO |
| GospelSyncAgent | none | NO | NO | NO |
| GovernanceAgent | none | NO | NO | NO |
| GravityLeakRepairAgent | none | NO | NO | NO |
| L5SafetyExerciserAgent | none | NO | NO | NO |
| LocationAgent | none | NO | NO | NO |
| LocationHealerAgent | none | NO | NO | NO |
| LocationValidatorAgent | none | NO | NO | NO |
| NamingAgent | none | NO | NO | NO |
| NeuralAutoImmuneAgent | none | NO | NO | NO |
| PreCommitSovereignAgent | none | NO | NO | NO |
| ReportLocationAgent | none | NO | NO | NO |
| ResourceManagerAgent | none | NO | NO | NO |
| SafetyDetectorAgent | none | NO | NO | NO |
| SafetyExecutorAgent | none | NO | NO | NO |
| SafetyInspectorAgent | none | NO | NO | NO |
| SecurityManagerAgent | none | NO | NO | NO |
| StructuralEngineerAgent | none | NO | NO | NO |
| StructuralValidatorAgent | none | NO | NO | NO |
| StructureEnforcerAgent | none | NO | NO | NO |
| SystemArchitectAgent | none | NO | NO | NO |
| TerritoryChangeHandlerAgent | none | NO | NO | NO |
| TypeMechanicAgent | none | NO | NO | NO |
| UnusedCleanupAgent | none | NO | NO | NO |

---

## L4 — State (4 of 5 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| CheckpointManagerAgent | @standard_heal | YES | YES | NO |
| GravityStateAgent | @standard_heal | YES | YES | NO |
| PineconeSovereignAgent | @standard_heal | YES | YES | NO |
| RedisSovereignAgent | @standard_heal | YES | YES | NO |
| CachedStateLedgerAgent | none | NO | NO | NO |

---

## L3 — Orchestration (9 of 13 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| CoverageAgent | @standard_heal | YES | YES | NO |
| DAGMutatorAgent | @standard_heal | YES | YES | NO |
| DagEngineAgent | @standard_heal | YES | YES | NO |
| DomainPlannerAgent | @standard_heal | YES | YES | NO |
| **FissionManagerAgent** | direct llm_generate(gemini-2.5-pro) | NO | YES | NO |
| OrchestrationHandshakeAgent | @standard_heal | YES | YES | NO |
| SemanticGatekeeperAgent | @standard_heal | YES | YES | NO |
| StateManagementAgent | @standard_heal | YES | YES | NO |
| SubAtomicAgent | @standard_heal | YES | YES | NO |
| SubatomicHopAgent | @standard_heal | YES | YES | NO |
| DagRuntimeInspectorAgent | none | NO | NO | NO |
| NervousSystemAgent | none | NO | NO | NO |
| UnifiedAgent | none | NO | NO | NO |

---

## L2 — Execution (3 of 5 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| EmbeddingSovereignAgent | @standard_heal | YES | YES | NO |
| **StructuredEngineAgent** | direct llm_generate(gemini-flash) | NO | NO | YES |
| SubAtomicRegistryAgent | @standard_heal | YES | YES | NO |
| ToolsmithAgent | @standard_heal | YES | YES | NO |
| SovereignMCPGatewayAgent | none | NO | NO | NO |

---

## L1 — Cognition (2 of 3 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| ASTValidatorAgent | @standard_heal | YES | YES | NO |
| StrategicRecommendationAgent | @standard_heal | YES | YES | NO |
| MetaLearningAgent | none | NO | NO | NO |

---

## L0 — Routing (0 of 2 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| RootCustomsAgent | none | NO | NO | NO |
| SSOTFolderCleanupAgent | none | NO | NO | NO |

---

## L6 — Observability (0 of 1 wired)

| Agent | Mechanism | Qwen | Gemini-2.5-pro | Gemini-flash |
|-------|-----------|------|----------------|--------------|
| ObservabilityProbeExecutor | none | NO | NO | NO |

---

## Summary

| Metric | Count | % of 97 |
|--------|-------|---------|
| **Can call Qwen** (medium-confidence via @standard_heal) | **54** | **56%** |
| **Can call Gemini-2.5-pro** (low-confidence via @standard_heal OR direct) | **55** | **57%** |
| Can call Gemini-flash (direct only) | 2 | 2% |
| Wired via @standard_heal | 54 | 56% |
| Wired via direct llm_generate() | 3 | 3% |
| No LLM capability | 42 | 43% |

### The 3 direct llm_generate() callers

| Agent | Layer | Model called | Trigger |
|-------|-------|-------------|---------|
| CognitiveDispositionAgent | L5 | gemini-3-flash-preview | `provider="google"` in heal logic |
| FissionManagerAgent | L3 | **gemini-2.5-pro** | `model=os.getenv("GEMINI_PRO_MODEL")` |
| StructuredEngineAgent | L2 | gemini-3-flash-preview | `model=os.getenv("GEMINI_MODEL")` |

### The @standard_heal confidence gate (applies to all 54)

All 54 `@standard_heal` agents route through `decide_heal_escalation()` in
`agentic_core/L5_safety/types/heal_policy_types.py`. LLM is only activated when
`HEAL_POLICY_MODEL_ESCALATION=1` env var is set AND confidence falls below 0.75.
At runtime with default env: **all 54 resolve deterministically (no LLM)**. LLM
escalation is opt-in per deployment.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

