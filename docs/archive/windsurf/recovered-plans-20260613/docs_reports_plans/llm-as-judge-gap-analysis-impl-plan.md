# LLM-as-Judge: Gap Analysis & Implementation Plan

**Date**: 2026-03-17
**Scope**: Complete gap analysis of the LLM-as-Judge system — existing infrastructure, data sources, missing capabilities, architecture design, rubrics, and phased implementation roadmap.
**Separation Note**: This document is the **LLM-as-Judge system** plan. ADG serves as one data input (see `adg-llm-judge-gap-analysis.md` for ADG-specific gaps).

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Existing Judge/Evaluation Infrastructure Inventory](#2-existing-judgeevaluation-infrastructure-inventory)
3. [Data Sources Available to the Judge](#3-data-sources-available-to-the-judge)
4. [Evaluation Dimensions the LLM-as-Judge Must Cover](#4-evaluation-dimensions)
5. [Gap Analysis: What Exists vs What's Needed](#5-gap-analysis)
6. [LLM-as-Judge Architecture Design](#6-architecture-design)
7. [Evaluation Rubrics & Scoring Framework](#7-rubrics--scoring-framework)
8. [Phased Implementation Roadmap](#8-phased-implementation-roadmap)
9. [Risk Analysis & Mitigations](#9-risk-analysis--mitigations)

---

## 1. Executive Summary

The codebase has **extensive but fragmented** evaluation infrastructure across 6 subsystems. There are two judge implementations (`GeminiJudge`, `JudgeEvaluator`), four RAGAS-style metrics, a reasoning evaluation pipeline, an L6 observability evaluation system, and an `apps_eval` evaluation lab with scorecards, regression detection, and quality gates.

**However, no unified LLM-as-Judge system exists.** The current components are isolated, use different type systems, have no shared rubric format, and lack the ability to consume structured data from the ADG, Redis, or source files as evidence inputs.

### Key Findings

| AREA | STATUS | VERDICT |
|------|--------|---------|
| Judge protocol & types | Two incompatible systems exist | **FRAGMENTED** |
| Evaluation metrics (RAGAS) | 4 metrics implemented, deterministic | **FUNCTIONAL** |
| Reasoning evaluation | Full pipeline with 5 dimensions, orphan guards | **FUNCTIONAL** |
| L6 evaluation signal routing | Integrator with subscribe/publish pattern | **FUNCTIONAL** |
| Evaluation lab (apps_eval) | Scorecard, regression, gates — no LLM judge wiring | **PARTIAL** |
| ADG as evidence source | 8,606 nodes, 502K edges, 98 relation types via Redis | **READY** |
| Source code retrieval for judge | ADG has file:line coords but no code reader for judge | **MISSING** |
| Unified rubric format | No shared rubric schema across subsystems | **MISSING** |
| Verdict persistence & history | In-memory stores only, no durable storage | **MISSING** |
| Multi-source evidence assembly | No component assembles ADG + source + runtime into judge context | **MISSING** |
| LLM provider abstraction for judge | Only GeminiJudge exists (Gemini-specific) | **PARTIAL** |

### What Needs to Be Built

1. **Evidence Assembly Layer** — Collects ADG data, source code, runtime telemetry, and config into structured judge context
2. **Unified Judge Protocol** — Single protocol that all judge implementations conform to
3. **Rubric Engine** — Configurable rubric definitions that drive evaluation criteria
4. **Verdict Store** — Persistent storage for judge verdicts with trend/regression analysis
5. **Judge Orchestrator** — Coordinates multi-dimension evaluation runs across evidence sources
6. **Provider Abstraction** — Support multiple LLM backends (Gemini, GPT-4, Claude, local models)

---

## 2. Existing Judge/Evaluation Infrastructure Inventory

### 2.1 Judge Implementations

#### A. `agentic_core/evaluation/judges/llm_judge.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`LLMJudge` protocol** | `evaluate(query, answer, context) → JudgeScore` — async protocol |
| **`JudgeScore` dataclass** | `faithfulness`, `answer_relevancy`, `context_precision`, `groundedness` (4 float scores) |
| **`GeminiJudge`** | Production judge using `google.generativeai` Gemini API. Fixed RAG rubric prompt. |
| **`NullJudge`** | CI stub returning 1.0 scores. |
| **Rubric** | Hardcoded prompt template scoring 4 RAG dimensions on 0.0–1.0 scale |
| **Lifecycle tracing** | Full `_emit_*` instrumentation for governance/telemetry |
| **Limitations** | Single-provider (Gemini only), fixed rubric, no evidence assembly, no verdict persistence |

#### B. `apps_shared/types/judge_evaluator_types.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`JudgmentCriterion` enum** | 7 criteria: accuracy, completeness, relevance, coherence, factuality, safety, helpfulness |
| **`JudgmentScore` enum** | 5 levels: excellent (1.0), good (0.75), adequate (0.5), poor (0.25), unacceptable (0.0) |
| **`JudgeVerdict` dataclass** | `criterion`, `score`, `reasoning`, `evidence`, `suggestions`, `metadata` |
| **`JudgeEvaluationResult` dataclass** | Multiple verdicts, overall score, pass/fail, evaluator_id |
| **`JudgeEvaluator` class** | Async `evaluate()` with LLM-based or heuristic mode. Parses structured LLM responses. |
| **Limitations** | No ADG integration, no evidence assembly, no persistence, separate type system from `LLMJudge` |

### 2.2 Evaluation Metrics

#### `agentic_core/evaluation/metrics/`

| FILE | COMPONENTS | TYPE |
|------|-----------|------|
| `base.py` | `EvaluationMetric` ABC, `RetrievalMetric`, `GenerationMetric`, `ClassificationMetric` | Abstract bases |
| `ragas_metrics.py` | `FaithfulnessMetric`, `AnswerRelevancyMetric`, `ContextPrecisionMetric`, `GroundednessMetric` | Deterministic, BGE-cosine |
| `classification.py` | Classification metrics (ConfusionMatrix) | Deterministic |
| `f1_score.py` | F1 score metric | Deterministic |

**Observation**: RAGAS metrics are deterministic (no LLM calls), use BGE embeddings, and are well-designed. They complement rather than replace LLM-as-Judge.

#### Evaluation Datasets

| DATASET | PURPOSE | SIZE |
|---------|---------|------|
| `rag_eval_set.json` | RAG retrieval evaluation | ~10 examples |
| `safety_eval_set.json` | Safety compliance evaluation | ~10 examples |
| `hallucination_eval_set.json` | Hallucination detection | ~10 examples |
| `groundedness_eval_set.json` | Groundedness evaluation | ~10 examples |
| `classification_eval_set.json` | Classification evaluation | ~10 examples |

### 2.3 Reasoning Evaluation Pipeline

#### `agentic_core/L1_cognition/evaluation/reasoning_evaluation.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`ReasoningEvaluationRecord`** | 12-field immutable artifact per evaluated reasoning step |
| **`ReasoningEvaluationRubric`** | 5 dimensions: relevance, consistency, policy_compliance, coherence, actionability |
| **`ReasoningEvaluationOutcome`** | PASS, FAIL, INCONCLUSIVE, NEEDS_REVIEW, ESCALATE |
| **`evaluate_reasoning_step()`** | Mandatory entrypoint with orphan guard (no eval without trace binding) |
| **`ComparativeReasoningEvaluation`** | Side-by-side candidate comparison (5 fields) |
| **`ReasoningEvaluationStore`** | In-memory queryable store (by run_id, trace_id, outcome) |
| **Strengths** | Strong spec compliance, orphan guards, hash-based provenance, comparative eval support |
| **Limitations** | In-memory only (no persistence), no LLM-based scoring, no ADG integration |

### 2.4 L6 Observability Evaluation System

#### `agentic_core/L6_observability/evaluation/evaluation_record.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`EvaluationRecord`** | 10-field immutable artifact, policy-sensitive evaluation support |
| **`EvaluationStage`** | 5 stages: REASONING_TRACE, EXECUTION_TRACE, ROUTING_TRACE, STATE_MUTATION_TRACE, FINAL_OUTCOME_TRACE |
| **`evaluate_and_attach()`** | Mandatory entrypoint binding eval to trace lineage |
| **`EvaluationIndex`** | Queryable in-memory store |
| **`OrphanEvaluationError`** | Orphan eval protection |

#### `agentic_core/L6_observability/evaluation/evaluation_signal_integrator.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`EvaluationSignalIntegrator`** | Routes eval signals from L6 → L1/L2 via pub/sub |
| **`EvalSignalKind`** | QUALITY_SCORE, LATENCY, ACCURACY, SAFETY_VERDICT, HALLUCINATION_FLAG, COST |
| **`EvalSignal`** | Frozen dataclass with trace_id, source_module, target_layer, kind, score |
| **Strengths** | Proper feedback loop architecture, layer-aware routing |
| **Limitations** | No LLM judge integration, no ADG evidence consumption |

### 2.5 Evaluation Lab (apps_eval)

| FILE | COMPONENT | PURPOSE |
|------|-----------|---------|
| `types/eval_types.py` | `EvalRequest`, `EvalResult`, `ScenarioResult`, `SuiteResult`, `ScorecardRow`, `RegressionRecord`, `EvalRunSummary` | Domain types |
| `engines/scorecard_engine.py` | `ScorecardEngine` | Weighted scorecard computation (6 default dimensions) |
| `engines/regression_detector.py` | `RegressionDetector` | Baseline comparison, regression flagging |
| `engines/scenario_runner.py` | Scenario execution against benchmark suites | Suite runner |
| `validators/eval_gate_validator.py` | `EvalGateValidator` | Quality gates (min score, regression, timeout) |
| `spine/eval_spine_adapter.py` | `EvalSpineAdapter` | CID-based spine integration |
| `reasoning/EvalOrchestrator.py` | Eval orchestrator | Pipeline coordinator |

**Strengths**: Complete evaluation pipeline (scenario → suite → scorecard → regression → gate). Deterministic scoring.
**Limitations**: No LLM judge in the pipeline. Scorecard dimensions are hardcoded. No ADG evidence.

### 2.6 Runtime Evaluation Spine

#### `agentic_core/adg/runtime/eval_spine.py`

| COMPONENT | DETAILS |
|-----------|---------|
| **`EvalMetricResult`** | Runtime metric with name, value, threshold, pass/fail |
| **`DriftAlert`** | Drift detection between metrics |
| **`PreferencePair` / `DPOBatch`** | DPO preference learning support |
| **`OptimizationProposal`** | Staged optimization proposals |
| **Purpose** | Runtime metric collection, drift detection, DPO batch building |
| **Relevance to Judge** | Provides runtime signals the judge can consume, but no direct integration |

---

## 3. Data Sources Available to the Judge

### 3.1 ADG SQLite Database

| ATTRIBUTE | VALUE |
|-----------|-------|
| **Location** | `artifacts/adg/adg_indexed_*.sqlite` |
| **Current** | `adg_indexed_03172026_0002.sqlite` |
| **Nodes** | 8,606 |
| **Edges** | 502,935 across 98 relation types |
| **Entity types** | module, symbol, prompt_slot, provider, seam, layer, gateway, prompt_template |
| **Edge metadata** | 100% source_file, 100% symbol, 98.7% line_no |
| **What it provides** | Static dependency graph, architectural compliance data, anti-pattern violations, governance wiring, security surface, test coverage mapping, prompt chain-of-custody |

### 3.2 ADG Redis Hot Cache

| ATTRIBUTE | VALUE |
|-----------|-------|
| **URL** | `redis://localhost:6379/0` |
| **Access** | MCP tools: `adg_node`, `adg_edge_fanout`, `adg_edge_fanin`, `adg_nodes_by_layer`, `adg_violations`, `adg_snapshot`, `adg_meta`, `adg_status` |
| **Data types** | Nodes as HASHes, edges as SETs, violations as LISTs, snapshot as STRING |
| **Freshness** | `adg_status` / `adg_assert_fresh` check ingestion vs SQLite mtime |
| **What it provides** | Fast graph queries without SQLite overhead. Real-time node/edge lookups. Layer-based filtering. |

### 3.3 Source Code Files (Filesystem)

| ATTRIBUTE | VALUE |
|-----------|-------|
| **Root** | `c:\Git\Agentic-Workflow\` |
| **Total modules** | ~3,000+ Python files |
| **Access** | Filesystem read at ADG-provided file:line coordinates |
| **What it provides** | Actual code context for nuanced verdicts. ADG gives coordinates; filesystem gives content. |
| **Gap** | No structured source retrieval tool exists for the judge. Must be built. |

### 3.4 Evaluation Datasets

| DATASET | FILE | PURPOSE |
|---------|------|---------|
| RAG eval | `agentic_core/evaluation/datasets/rag_eval_set.json` | RAG quality benchmarks |
| Safety eval | `agentic_core/evaluation/datasets/safety_eval_set.json` | Safety compliance tests |
| Hallucination eval | `agentic_core/evaluation/datasets/hallucination_eval_set.json` | Hallucination detection |
| Groundedness eval | `agentic_core/evaluation/datasets/groundedness_eval_set.json` | Grounding verification |
| Classification eval | `agentic_core/evaluation/datasets/classification_eval_set.json` | Classification accuracy |

### 3.5 Configuration & Policy Data

| SOURCE | LOCATION | CONTENTS |
|--------|----------|----------|
| ADG schema | `agentic_core/adg/schema.py` | Entity types, relation types, allowed layer edges, forbidden relations, governance frozensets |
| `.windsurfrules` | `.windsurf/rules/.windsurfrules` | Constitutional rules, coding standards, testing requirements |
| `pyproject.toml` | Root | Project dependencies, tool configs |
| Agent spec configs | `apps_*/config/agent_spec_config.py` | Per-app agent specifications |
| Structure blueprint | `agentic_core/L5_safety/config/structure_blueprint_config.py` | SSOT territory definitions |

### 3.6 Runtime Telemetry (Partial)

| SOURCE | STATUS | CONTENTS |
|--------|--------|----------|
| Lifecycle trace emitters | EMITTED but not collected | `_emit_*` calls throughout codebase |
| Execution trace store | In-memory only | Active trace context |
| Eval signal integrator | Functional but ephemeral | Layer-targeted eval signals |
| EvalSpine | Functional | Runtime metrics, drift alerts |

### 3.7 Knowledge Graph (MCP Memory)

| SOURCE | STATUS | CONTENTS |
|--------|--------|----------|
| Persistent memory | Available via MCP | Entity/observation/relation graph |
| ADG context import | Available | Layer structure, project context |
| Session context | Available | Cross-session learning |

---

## 4. Evaluation Dimensions the LLM-as-Judge Must Cover

### 4.1 Dimension Taxonomy

The LLM-as-Judge must evaluate across **four planes**, each containing multiple dimensions:

#### Plane A: Code Quality & Architecture (ADG-backed)

| DIM ID | DIMENSION | DATA SOURCE | CURRENT STATUS |
|--------|-----------|-------------|----------------|
| A1 | **Architectural compliance** | ADG `belongs_to_layer` + `violates` | READY — 790 violations detected |
| A2 | **Anti-pattern detection** | ADG `antipattern` edges (1,596) | READY — file:line evidence |
| A3 | **Dead code / import hygiene** | ADG `dead_imports` (4,797) | READY — deterministic |
| A4 | **Dependency impact / blast radius** | ADG `imports` + `calls` fan-out | READY — graph traversal |
| A5 | **Test coverage completeness** | ADG `covers` edges (9,944) | PARTIAL — import-based, not behavioral |
| A6 | **Code complexity hotspots** | ADG fan-out scores | READY — top hotspots identified |

#### Plane B: Governance & Compliance (ADG + Policy-backed)

| DIM ID | DIMENSION | DATA SOURCE | CURRENT STATUS |
|--------|-----------|-------------|----------------|
| B1 | **Write governance (UWG)** | ADG `writes_to`, `writes_through`, `execution_terminates_at_uwg` | PARTIAL — rubrics needed |
| B2 | **Determinism compliance** | ADG `uses_wall_clock`, `uses_random`, `seeds_rng`, `guards_replay` | READY |
| B3 | **Governance wiring completeness** | ADG governance edges per module | PARTIAL — rubrics needed |
| B4 | **Security surface** | ADG `accesses_credential`, `reads_secret`, `invokes_eval`, `external_http_call` | READY |
| B5 | **Prompt chain-of-custody** | ADG prompt edges + slot nodes | PARTIAL — source code needed |
| B6 | **Layer boundary enforcement** | ADG `violates` + allowed layer edges | READY |
| B7 | **Policy compliance** | `.windsurfrules` + ADG evidence | MISSING — policy parser needed |

#### Plane C: Agent & Output Quality (LLM-evaluated)

| DIM ID | DIMENSION | DATA SOURCE | CURRENT STATUS |
|--------|-----------|-------------|----------------|
| C1 | **Answer faithfulness** | Agent output + context | FUNCTIONAL — RAGAS metric + GeminiJudge |
| C2 | **Answer relevancy** | Agent output + query | FUNCTIONAL — RAGAS metric |
| C3 | **Context precision** | Retrieved docs + ground truth | FUNCTIONAL — RAGAS metric |
| C4 | **Groundedness** | Agent output + context | FUNCTIONAL — RAGAS metric |
| C5 | **Safety compliance** | Agent output + safety dataset | PARTIAL — dataset exists, no judge wiring |
| C6 | **Hallucination detection** | Agent output + context | PARTIAL — dataset exists, no judge wiring |
| C7 | **Reasoning quality** | Reasoning traces | FUNCTIONAL — 5 dimensions in reasoning eval |
| C8 | **Coherence & helpfulness** | Agent output | PARTIAL — JudgeEvaluator types exist |

#### Plane D: System Health & Runtime (Telemetry-backed)

| DIM ID | DIMENSION | DATA SOURCE | CURRENT STATUS |
|--------|-----------|-------------|----------------|
| D1 | **Latency compliance** | EvalSignalIntegrator LATENCY signals | PARTIAL — signal type exists |
| D2 | **Error rate monitoring** | Runtime exceptions | MISSING — no collection |
| D3 | **Cost efficiency** | LLM provider costs | MISSING — no collection |
| D4 | **Regression detection** | RegressionDetector baselines | FUNCTIONAL — deterministic |
| D5 | **Drift detection** | EvalSpine DriftAlert | FUNCTIONAL — threshold-based |

---

## 5. Gap Analysis: What Exists vs What's Needed

### 5.1 Critical Gaps (Must Fix)

#### GAP-J1: No Unified Judge Protocol

**Exists**: Two incompatible judge interfaces:
- `LLMJudge.evaluate(query, answer, context) → JudgeScore` (4 RAG scores)
- `JudgeEvaluator.evaluate(input, criteria, context) → JudgeEvaluationResult` (7 criteria)

**Needed**: Single `JudgeProtocol` that:
- Accepts structured evidence (ADG data + source code + runtime signals)
- Supports configurable rubrics (not hardcoded prompts)
- Returns a standardized `JudgeVerdict` with provenance
- Can be backed by any LLM provider

**Impact**: Without this, every new evaluation dimension requires a custom judge implementation.

#### GAP-J2: No Evidence Assembly Layer

**Exists**: ADG data in SQLite/Redis. Source code on disk. Runtime signals in memory. No component brings them together.

**Needed**: `EvidenceAssembler` that:
- Queries ADG for relevant edges/nodes given a target module or dimension
- Reads source code at ADG-provided file:line coordinates
- Collects runtime signals from EvalSpine / EvalSignalIntegrator
- Packages all evidence into a structured `EvidenceBundle` for judge consumption

**Impact**: This is the #1 architectural gap. Without it, the judge has no structured input.

#### GAP-J3: No Rubric Engine

**Exists**: Hardcoded rubric in `GeminiJudge` prompt. 5 reasoning rubric dimensions in `ReasoningEvaluationRubric`. 6 scorecard dimensions in `ScorecardEngine`. All incompatible.

**Needed**: `RubricEngine` that:
- Loads rubric definitions from a canonical `rubrics.json` or `rubrics` table
- Maps dimensions to evidence requirements (which ADG edges, which source, which runtime signals)
- Supports severity levels, thresholds, and conditional applicability
- Generates LLM prompts from rubric definitions (template-driven, not hardcoded)

**Impact**: Without configurable rubrics, adding new evaluation dimensions requires code changes.

#### GAP-J4: No Verdict Persistence

**Exists**: `ReasoningEvaluationStore` and `EvaluationIndex` are in-memory singletons. Lost on process exit.

**Needed**: `VerdictStore` backed by SQLite (or similar) that:
- Persists all judge verdicts with timestamps and ADG artifact digests
- Supports trend queries ("show me module X's scores over time")
- Enables regression detection across ADG rebuilds
- Stores evidence hashes for reproducibility

**Impact**: Without persistence, no historical analysis, no trend detection, no regression alerting.

### 5.2 High Gaps (Should Fix)

#### GAP-J5: No Source Code Retrieval Tool for Judge

**Exists**: ADG provides `source_file` and `line_no` for every edge. No utility function reads the actual code.

**Needed**: `SourceRetriever` utility:
```
get_source_context(file_path, line_no, window=10) → str
get_function_body(file_path, symbol_name) → str
get_class_definition(file_path, class_name) → str
```

**Impact**: Without source code, LLM-as-Judge can only see graph topology, not code semantics.

#### GAP-J6: No Multi-Provider LLM Abstraction

**Exists**: `GeminiJudge` is Gemini-specific. `JudgeEvaluator` uses a generic `llm_client` parameter but no provider registry.

**Needed**: `JudgeProviderRegistry` supporting:
- Gemini (existing)
- GPT-4 / GPT-4o
- Claude 3.5 Sonnet
- Local models (Ollama, vLLM)
- Model-specific prompt formatting
- Cost tracking per evaluation

**Impact**: Single-provider dependency creates vendor lock-in and cost constraints.

#### GAP-J7: No Judge Orchestrator

**Exists**: `EvalOrchestrator` in apps_eval runs scenario-based evaluation. No orchestrator for multi-dimension LLM judging.

**Needed**: `JudgeOrchestrator` that:
- Accepts a target (module, PR, agent output, full system)
- Selects applicable rubrics based on target type
- Dispatches evidence assembly per dimension
- Runs judge evaluations (potentially in parallel)
- Aggregates verdicts into a scorecard
- Feeds results to regression detector and verdict store

**Impact**: Without orchestration, each evaluation run requires manual coordination.

### 5.3 Medium Gaps (Nice to Have)

#### GAP-J8: No ADG Diff for Temporal Analysis

**Exists**: `artifact_digest` changes between ADG rebuilds. No structured diff tool.

**Needed**: `ADGDiffEngine` comparing two SQLite artifacts → added/removed edges by type.

#### GAP-J9: No Comparative Judge Mode

**Exists**: `ComparativeReasoningEvaluation` supports A/B comparison for reasoning traces.

**Needed**: Generalize to any evaluation dimension (e.g., compare two implementations, two prompt templates, two agent configurations).

#### GAP-J10: No Human-in-the-Loop Escalation for Uncertain Verdicts

**Exists**: `NEEDS_REVIEW` and `ESCALATE` outcomes exist in reasoning evaluation. `escalates_to_human` ADG edge type exists (15 edges).

**Needed**: Judge escalation path that routes low-confidence verdicts to human reviewers with evidence bundles.

---

## 6. LLM-as-Judge Architecture Design

### 6.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       JUDGE ORCHESTRATOR                            │
│  Target → Rubric Selection → Evidence Assembly → Judge Dispatch →   │
│  Verdict Aggregation → Scorecard → Regression Check → Persist       │
└────────┬────────────────┬──────────────────┬───────────────┬────────┘
         │                │                  │               │
    ┌────▼────┐    ┌──────▼──────┐    ┌──────▼──────┐  ┌────▼─────┐
    │ RUBRIC  │    │  EVIDENCE   │    │   JUDGE     │  │ VERDICT  │
    │ ENGINE  │    │  ASSEMBLER  │    │  PROVIDER   │  │  STORE   │
    │         │    │             │    │  REGISTRY   │  │          │
    │ rubrics │    │ ADG queries │    │ Gemini      │  │ SQLite   │
    │ .json   │    │ Source read │    │ GPT-4       │  │ verdicts │
    │ thresholds│  │ Runtime sig │    │ Claude      │  │ trends   │
    │ severity │   │ Config data │    │ Local       │  │ history  │
    └─────────┘    └──────┬──────┘    └─────────────┘  └──────────┘
                          │
              ┌───────────┼───────────────┐
              │           │               │
        ┌─────▼────┐ ┌───▼─────┐  ┌──────▼──────┐
        │   ADG    │ │ SOURCE  │  │  RUNTIME    │
        │  REDIS   │ │ READER  │  │  TELEMETRY  │
        │  CACHE   │ │         │  │  (future)   │
        │          │ │ file:ln │  │             │
        │ 8.6K nd  │ │ funcs   │  │ EvalSpine   │
        │ 503K ed  │ │ classes │  │ Signals     │
        └──────────┘ └─────────┘  └─────────────┘
```

### 6.2 Component Specifications

#### 6.2.1 JudgeOrchestrator

**Location**: `agentic_core/evaluation/judges/judge_orchestrator.py`

```python
class JudgeOrchestrator:
    """Coordinates multi-dimension LLM-as-Judge evaluation runs."""

    def __init__(
        self,
        rubric_engine: RubricEngine,
        evidence_assembler: EvidenceAssembler,
        provider_registry: JudgeProviderRegistry,
        verdict_store: VerdictStore,
    ) -> None: ...

    async def evaluate_module(self, module_path: str) -> JudgeReport: ...
    async def evaluate_pr(self, changed_files: list[str]) -> JudgeReport: ...
    async def evaluate_agent_output(self, output: AgentOutput) -> JudgeReport: ...
    async def evaluate_system(self) -> JudgeReport: ...
```

**Responsibilities**:
- Accept evaluation targets (module, PR, agent output, full system)
- Select applicable rubrics based on target type and module role
- Dispatch evidence assembly per applicable dimension
- Run judge evaluations via provider registry
- Aggregate verdicts into `JudgeReport` with scorecard
- Feed results to verdict store and regression detector

#### 6.2.2 EvidenceAssembler

**Location**: `agentic_core/evaluation/judges/evidence_assembler.py`

```python
@dataclass(frozen=True)
class EvidenceBundle:
    target: str                          # Module path or evaluation target
    adg_evidence: dict[str, Any]         # ADG edges, nodes, violations
    source_snippets: list[SourceSnippet] # Relevant code at file:line
    runtime_signals: list[EvalSignal]    # Runtime telemetry (if available)
    config_context: dict[str, Any]       # Relevant configuration
    adg_digest: str                      # ADG artifact digest for provenance

class EvidenceAssembler:
    """Assembles evidence bundles from multiple data sources."""

    def __init__(
        self,
        adg_client: ADGClient,         # Redis or SQLite
        source_reader: SourceRetriever,
        runtime_collector: RuntimeCollector | None = None,
    ) -> None: ...

    def assemble(self, target: str, dimensions: list[str]) -> EvidenceBundle: ...
```

**Data Flow**:
1. Query ADG Redis for target module's edges (fan-in, fan-out, violations, governance)
2. For each relevant edge, read source code at file:line via SourceRetriever
3. Collect runtime signals if available
4. Package into `EvidenceBundle` with ADG digest for provenance

#### 6.2.3 RubricEngine

**Location**: `agentic_core/evaluation/judges/rubric_engine.py`

```python
@dataclass(frozen=True)
class RubricDefinition:
    rubric_id: str
    dimension: str
    applies_to: dict[str, Any]    # module_role, layer, entity_type conditions
    evidence_requirements: list[str]  # ADG edge types needed
    scoring_criteria: list[ScoringCriterion]
    severity: str                  # CRITICAL, HIGH, MEDIUM, LOW
    prompt_template: str           # LLM judge prompt template
    deterministic_check: str | None  # Optional deterministic pre-check

class RubricEngine:
    """Loads and selects applicable rubrics for evaluation targets."""

    def __init__(self, rubric_path: str = "artifacts/judge/rubrics.json") -> None: ...
    def select_rubrics(self, target: str, module_meta: dict) -> list[RubricDefinition]: ...
    def render_prompt(self, rubric: RubricDefinition, evidence: EvidenceBundle) -> str: ...
```

#### 6.2.4 JudgeProviderRegistry

**Location**: `agentic_core/evaluation/judges/provider_registry.py`

```python
class JudgeProvider(Protocol):
    """Unified protocol for all LLM judge backends."""
    async def judge(self, prompt: str, rubric_id: str) -> RawJudgeResponse: ...
    @property
    def provider_id(self) -> str: ...
    @property
    def cost_per_eval(self) -> float: ...

class JudgeProviderRegistry:
    def register(self, provider: JudgeProvider) -> None: ...
    def get(self, provider_id: str) -> JudgeProvider: ...
    def get_default(self) -> JudgeProvider: ...
```

#### 6.2.5 VerdictStore

**Location**: `agentic_core/evaluation/judges/verdict_store.py`

```python
class VerdictStore:
    """Persistent SQLite-backed verdict storage."""

    def __init__(self, db_path: str = "artifacts/judge/verdicts.sqlite") -> None: ...
    def store(self, verdict: JudgeVerdict) -> None: ...
    def query_by_module(self, module_path: str) -> list[JudgeVerdict]: ...
    def query_by_dimension(self, dimension: str) -> list[JudgeVerdict]: ...
    def trend(self, module_path: str, dimension: str, n: int = 10) -> list[float]: ...
    def regressions(self, current_digest: str, previous_digest: str) -> list[RegressionRecord]: ...
```

**Schema**:
```sql
CREATE TABLE verdicts (
    verdict_id TEXT PRIMARY KEY,
    module_path TEXT NOT NULL,
    dimension TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    score REAL NOT NULL,
    outcome TEXT NOT NULL,          -- PASS, FAIL, WARN, NEEDS_REVIEW
    evidence_hash TEXT NOT NULL,
    reasoning TEXT,
    adg_digest TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(module_path, dimension, rubric_id, adg_digest)
);

CREATE TABLE verdict_evidence (
    verdict_id TEXT REFERENCES verdicts(verdict_id),
    evidence_type TEXT NOT NULL,    -- adg_edge, source_snippet, runtime_signal
    evidence_key TEXT NOT NULL,
    evidence_value TEXT NOT NULL
);

CREATE INDEX idx_verdicts_module ON verdicts(module_path);
CREATE INDEX idx_verdicts_dimension ON verdicts(dimension);
CREATE INDEX idx_verdicts_digest ON verdicts(adg_digest);
```

#### 6.2.6 SourceRetriever

**Location**: `agentic_core/evaluation/judges/source_retriever.py`

```python
@dataclass(frozen=True)
class SourceSnippet:
    file_path: str
    start_line: int
    end_line: int
    content: str
    symbol: str | None = None

class SourceRetriever:
    """Reads source code at ADG-provided coordinates."""

    def __init__(self, repo_root: str) -> None: ...
    def get_context(self, file_path: str, line_no: int, window: int = 10) -> SourceSnippet: ...
    def get_function(self, file_path: str, function_name: str) -> SourceSnippet: ...
    def get_class(self, file_path: str, class_name: str) -> SourceSnippet: ...
```

### 6.3 Data Flow

```
1. User/CI triggers: evaluate_module("agentic_core/L2_execution/providers.py")

2. JudgeOrchestrator:
   a. Query ADG for module metadata (layer, entity_type, role)
   b. RubricEngine.select_rubrics() → [arch_compliance, write_gov, determinism, security, ...]
   c. For each rubric:
      i.   EvidenceAssembler.assemble(module, rubric.evidence_requirements) → EvidenceBundle
      ii.  Deterministic pre-check if rubric has one (skip LLM if deterministic verdict)
      iii. RubricEngine.render_prompt(rubric, evidence) → LLM prompt
      iv.  JudgeProvider.judge(prompt) → RawJudgeResponse
      v.   Parse response into JudgeVerdict
   d. Aggregate verdicts → JudgeReport (scorecard, overall score, regressions)
   e. VerdictStore.store(verdicts)
   f. Return JudgeReport

3. Output: Structured report with per-dimension verdicts, evidence citations, and trend data
```

### 6.4 Integration Points

| INTEGRATION | HOW |
|-------------|-----|
| **ADG Redis** | `EvidenceAssembler` uses MCP tools (`adg_node`, `adg_edge_fanout`, `adg_edge_fanin`, `adg_violations`) |
| **ADG SQLite** | Direct SQLite queries for bulk analysis (full-system evaluations) |
| **apps_eval** | `ScorecardEngine` receives judge verdicts as additional scorecard dimensions |
| **EvalSignalIntegrator** | Judge verdicts feed back as `EvalSignal(kind=QUALITY_SCORE)` to L1/L2 |
| **ReasoningEvaluation** | Judge evaluates reasoning traces using `evaluate_reasoning_step_from_trace()` |
| **CI Pipeline** | Judge runs as gate in `adg-ci-gates.yml` workflow |
| **Knowledge Graph** | Persistent memory stores verdict summaries for cross-session context |

---

## 7. Rubrics & Scoring Framework

### 7.1 Rubric Format

```json
{
  "rubric_id": "ARCH-001",
  "dimension": "architectural_compliance",
  "display_name": "Layer Gravity Compliance",
  "description": "Verifies module imports only from allowed layers per ALLOWED_LAYER_EDGES",
  "applies_to": {
    "entity_type": ["module"],
    "layer": ["L0", "L1", "L2", "L3", "L4", "L5", "L6"],
    "exclude_layer": ["L_TEST", "L_TOOLS"]
  },
  "evidence_requirements": [
    {"type": "adg_edge", "relation": "belongs_to_layer"},
    {"type": "adg_edge", "relation": "violates"},
    {"type": "adg_edge", "relation": "imports"}
  ],
  "deterministic_check": "count(violates edges) == 0",
  "scoring": {
    "method": "deterministic",
    "score_formula": "1.0 - (violation_count / total_import_count)",
    "pass_threshold": 1.0,
    "warn_threshold": 0.95
  },
  "severity": "CRITICAL",
  "prompt_template": null
}
```

### 7.2 Scoring Methods

| METHOD | DESCRIPTION | WHEN USED |
|--------|-------------|-----------|
| **Deterministic** | Formula-based, no LLM call | Anti-patterns, layer violations, dead imports, coverage counts |
| **LLM-Pointwise** | Single LLM call scores one target | Security assessment, prompt chain audit, code quality |
| **LLM-Pairwise** | LLM compares two candidates | Before/after refactoring, A/B testing |
| **LLM-Reference** | LLM scores against gold standard | Agent output quality, faithfulness |
| **Hybrid** | Deterministic pre-filter + LLM for borderline cases | Write governance, governance wiring |

### 7.3 Proposed Rubric Catalog (Initial Set)

#### Plane A: Code Quality (Deterministic)

| RUBRIC ID | DIMENSION | METHOD | PASS THRESHOLD |
|-----------|-----------|--------|----------------|
| ARCH-001 | Layer gravity compliance | Deterministic | 1.0 (zero violations) |
| QUAL-001 | Anti-pattern count | Deterministic | 0 critical anti-patterns |
| QUAL-002 | Dead import ratio | Deterministic | < 5% dead imports |
| DEP-001 | Fan-out complexity | Deterministic | Fan-out < 200 |
| COV-001 | Test coverage presence | Deterministic | ≥ 1 `covers` edge |

#### Plane B: Governance (Hybrid — Deterministic + LLM)

| RUBRIC ID | DIMENSION | METHOD | PASS THRESHOLD |
|-----------|-----------|--------|----------------|
| GOV-001 | Write governance compliance | Hybrid | writes_to → must have writes_through or uwg |
| GOV-002 | Determinism guard presence | Deterministic | uses_random → must have seeds_rng |
| GOV-003 | Governance wiring completeness | LLM-Pointwise | Module role-specific governance expectations |
| SEC-001 | Security risk assessment | LLM-Pointwise | Score ≥ 0.7 on security rubric |
| SEC-002 | Credential exposure | Deterministic | No hardcoded secrets in source |
| PROMPT-001 | Prompt authority chain | LLM-Pointwise | Authority hierarchy respected |

#### Plane C: Agent Output Quality (LLM-evaluated)

| RUBRIC ID | DIMENSION | METHOD | PASS THRESHOLD |
|-----------|-----------|--------|----------------|
| RAG-001 | Faithfulness | LLM-Reference | ≥ 0.75 |
| RAG-002 | Answer relevancy | LLM-Reference | ≥ 0.70 |
| RAG-003 | Context precision | Deterministic | ≥ 0.60 |
| RAG-004 | Groundedness | LLM-Reference | ≥ 0.75 |
| SAFE-001 | Safety compliance | LLM-Pointwise | No safety violations |
| HALL-001 | Hallucination detection | LLM-Pointwise | Hallucination score < 0.2 |
| REASON-001 | Reasoning quality | LLM-Pointwise | 5 dimensions ≥ 0.7 each |

#### Plane D: System Health (Deterministic)

| RUBRIC ID | DIMENSION | METHOD | PASS THRESHOLD |
|-----------|-----------|--------|----------------|
| PERF-001 | Latency compliance | Deterministic | p99 < 30s |
| REG-001 | Score regression | Deterministic | Δ > -0.05 from baseline |

### 7.4 Scorecard Weighting

| PLANE | WEIGHT | RATIONALE |
|-------|--------|-----------|
| A: Code Quality | 25% | Foundation — must be structurally sound |
| B: Governance | 30% | Highest weight — governance is constitutional requirement |
| C: Agent Output Quality | 30% | Core value delivery |
| D: System Health | 15% | Operational concern, lower weight |

### 7.5 Verdict Output Format

```json
{
  "verdict_id": "vd-a1b2c3d4e5f6",
  "target": "agentic_core/L2_execution/providers.py",
  "dimension": "write_governance",
  "rubric_id": "GOV-001",
  "outcome": "FAIL",
  "score": 0.40,
  "reasoning": "Module has 3 writes_to edges but no writes_through or execution_terminates_at_uwg edge. Writes bypass UWG governance.",
  "evidence": [
    {"type": "adg_edge", "relation": "writes_to", "dst": "state_registry", "line": 142},
    {"type": "source_snippet", "file": "providers.py", "lines": "140-145", "content": "..."}
  ],
  "suggestions": ["Add UWG routing for write operations at lines 142, 167, 203"],
  "severity": "HIGH",
  "adg_digest": "917a5b88f28cb626",
  "provider_id": "gemini-1.5-pro",
  "created_at": "2026-03-17T00:15:00Z"
}
```

---

## 8. Phased Implementation Roadmap

### Phase 0: Foundation (Week 1–2) — Unblocks everything

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| Define unified `JudgeVerdict` type | `agentic_core/evaluation/judges/types.py` | P0 |
| Define `JudgeProtocol` | Protocol class in `types.py` | P0 |
| Build `SourceRetriever` | `agentic_core/evaluation/judges/source_retriever.py` | P0 |
| Build `VerdictStore` (SQLite) | `agentic_core/evaluation/judges/verdict_store.py` | P0 |
| Create rubric JSON format & 5 initial rubrics | `artifacts/judge/rubrics.json` | P0 |

**Acceptance**: SourceRetriever reads code at ADG coordinates. VerdictStore persists and queries verdicts. Types are importable.

### Phase 1: Evidence Assembly + Deterministic Judges (Week 3–4)

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| Build `EvidenceAssembler` with ADG + source integration | `evidence_assembler.py` | P0 |
| Build `RubricEngine` loading from JSON | `rubric_engine.py` | P0 |
| Implement deterministic judges for Plane A (ARCH-001, QUAL-001, QUAL-002, DEP-001, COV-001) | Deterministic verdict functions | P0 |
| Implement deterministic judges for GOV-002, SEC-002 | Deterministic verdict functions | P1 |
| Tests for all deterministic judges | `tests/evaluation/test_deterministic_judges.py` | P0 |

**Acceptance**: `evaluate_module("some/module.py")` returns deterministic verdicts for 7+ rubrics with ADG-backed evidence. All verdicts persisted to VerdictStore.

### Phase 2: LLM Judge Integration (Week 5–6)

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| Build `JudgeProviderRegistry` | `provider_registry.py` | P0 |
| Adapt `GeminiJudge` to `JudgeProvider` protocol | Refactor existing code | P1 |
| Add GPT-4 provider | New provider class | P1 |
| Implement LLM-Pointwise judges for GOV-001, GOV-003, SEC-001, PROMPT-001 | LLM judge functions | P0 |
| Implement LLM-Reference judges for RAG-001 through RAG-004 | LLM judge functions | P1 |
| Build prompt template system | Template rendering in `RubricEngine` | P0 |

**Acceptance**: LLM judges produce structured verdicts for governance and quality dimensions. Provider switching works. Cost tracking per evaluation.

### Phase 3: Judge Orchestrator + Scorecard (Week 7–8)

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| Build `JudgeOrchestrator` | `judge_orchestrator.py` | P0 |
| Integrate with `ScorecardEngine` | Extended scorecard with judge dimensions | P1 |
| Integrate with `RegressionDetector` | Cross-ADG-version regression | P1 |
| Build `JudgeReport` output format (JSON + Markdown) | Report generation | P1 |
| Wire to `EvalSignalIntegrator` for feedback loop | Signal routing | P2 |

**Acceptance**: `JudgeOrchestrator.evaluate_module()` runs full pipeline, produces scorecard, detects regressions, persists all verdicts.

### Phase 4: CI Integration + Scaling (Week 9–10)

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| CI gate: judge runs on PR-changed files | `.github/workflows/judge-ci.yml` | P0 |
| CLI entrypoint | `python -m agentic_core.evaluation.judges --target <path>` | P1 |
| Batch evaluation (full system) | System-wide report generation | P1 |
| Performance optimization (parallel judge calls) | Async batch judging | P2 |
| Dashboard / report viewer | Markdown report generation | P2 |

**Acceptance**: CI gate blocks PRs that fail critical rubrics. Full-system evaluation runs < .

### Phase 5: Advanced Features (Week 11+)

| TASK | DELIVERABLE | PRIORITY |
|------|-------------|----------|
| ADG diff engine for temporal analysis | `adg_diff.py` | P1 |
| Comparative judge mode (A/B evaluation) | Pairwise comparison support | P2 |
| HITL escalation for uncertain verdicts | Escalation workflow | P2 |
| Runtime telemetry integration | OpenTelemetry → judge evidence | P2 |
| Self-improving rubrics (DPO feedback) | Meta-learning integration | P3 |
| Knowledge graph verdict persistence | MCP memory integration | P3 |

---

## 9. Risk Analysis & Mitigations

| RISK | LIKELIHOOD | IMPACT | MITIGATION |
|------|-----------|--------|------------|
| LLM judge hallucinations (false verdicts) | HIGH | HIGH | Deterministic pre-checks filter obvious cases. LLM only for nuanced analysis. Evidence citation requirement. |
| Cost explosion from LLM calls | MEDIUM | MEDIUM | Deterministic judges first (free). LLM judge caching. Budget limits per evaluation run. |
| ADG staleness producing wrong evidence | MEDIUM | HIGH | Always check `adg_status` freshness. Reject stale cache. Include ADG digest in every verdict. |
| Rubric drift (rubrics become outdated) | MEDIUM | MEDIUM | Rubric versioning. Review cycle. Regression detection catches outdated thresholds. |
| Over-engineering (building too much before validating) | HIGH | MEDIUM | Phase 0 delivers value immediately (deterministic judges). Each phase is independently useful. |
| Performance (full-system evaluation too slow) | LOW | MEDIUM | Parallel judge calls. Deterministic pre-filtering. Cache verdicts by (module, ADG digest). |
| Type system fragmentation (yet another type system) | MEDIUM | LOW | Phase 0 explicitly unifies types. Deprecation path for old `JudgeScore` and `JudgeEvaluator`. |

---

## Appendix A: File Inventory of Existing Infrastructure

| FILE | KEY COMPONENTS | LAYER |
|------|---------------|-------|
| `agentic_core/evaluation/judges/llm_judge.py` | `LLMJudge`, `GeminiJudge`, `NullJudge`, `JudgeScore` | Core |
| `apps_shared/types/judge_evaluator_types.py` | `JudgeEvaluator`, `JudgeVerdict`, `JudgmentCriterion` | Shared |
| `agentic_core/evaluation/metrics/base.py` | `EvaluationMetric`, `RetrievalMetric`, `GenerationMetric` | Core |
| `agentic_core/evaluation/metrics/ragas_metrics.py` | RAGAS metrics (Faithfulness, Relevancy, Precision, Groundedness) | Core |
| `agentic_core/L1_cognition/evaluation/reasoning_evaluation.py` | `ReasoningEvaluationRecord`, `evaluate_reasoning_step()` | L1 |
| `agentic_core/L6_observability/evaluation/evaluation_record.py` | `EvaluationRecord`, `evaluate_and_attach()` | L6 |
| `agentic_core/L6_observability/evaluation/evaluation_signal_integrator.py` | `EvaluationSignalIntegrator`, `EvalSignal` | L6 |
| `agentic_core/adg/runtime/eval_spine.py` | `EvalSpine`, `DriftAlert`, `DPOBatch` | ADG Runtime |
| `apps_eval/engines/scorecard_engine.py` | `ScorecardEngine`, weighted scorecard | apps_eval |
| `apps_eval/engines/regression_detector.py` | `RegressionDetector`, baseline comparison | apps_eval |
| `apps_eval/validators/eval_gate_validator.py` | `EvalGateValidator`, quality gates | apps_eval |
| `apps_eval/types/eval_types.py` | `EvalRequest`, `EvalResult`, `ScorecardRow` | apps_eval |
| `agentic_core/adg/schema.py` | Entity types, relation types, governance frozensets | ADG |
| `tools/adg/adg_mcp_server.py` | Redis MCP tools for ADG queries | Tools |
| `tools/adg/adg_redis_ingest.py` | SQLite → Redis ingestion | Tools |

## Appendix B: ADG Edge Types Most Relevant to Judge

| RELATION TYPE | EDGES | PRIMARY JUDGE USE |
|---------------|-------|-------------------|
| `imports` | 276,560 | Dependency analysis, impact radius |
| `reads_from` | 72,783 | State consumption tracking |
| `covers` | 9,944 | Test coverage mapping |
| `belongs_to_layer` | 6,323 | Layer assignment verification |
| `writes_to` | 5,119 | Write governance auditing |
| `dead_imports` | 4,797 | Code hygiene |
| `antipattern` | 1,596 | Code quality violations |
| `violates` | 790 | Layer gravity violations |
| `routes_through` | 673 | Governance routing verification |
| `invokes_eval` | 546 | Security surface (eval/exec calls) |
| `accesses_credential` | 376 | Credential access surface |
| `records_execution_trace` | 325 | Governance wiring |
| `generates_prompt` | 215 | Prompt chain-of-custody |
| `applies_guardrail` | 173 | Guardrail coverage |
| `reads_secret` | 151 | Secret access surface |
| `signs_execution_trace` | 133 | Trace signing coverage |
| `agent_executes_agent` | 112 | Multi-agent flow |

---

**End of Report**

*This plan should be reviewed and approved before Phase 0 implementation begins. The existing `adg-llm-judge-gap-analysis.md` remains the canonical reference for ADG-specific data gaps.*

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

