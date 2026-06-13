# Diagram vs Code Drift Report

**Date**: 2026-02-11
**Method**: Visual analysis of 5 architecture PNGs cross-referenced against current codebase
**Diagrams analyzed**: Exec Summary vF2, L0 Drilldown, L2 Pipeline v2, L5 Safety, L6 Observability

---

## Executive Summary

Your diagrams are **V15 vintage** (pre-consolidation, pre-LCD, pre-kernel). The codebase has undergone 5-6 major structural sessions since these were created. **Every diagram has significant drift.** The Exec Summary is ~70% accurate, layer drilldowns are ~50-60% accurate.

---

## Diagram 1: Exec Summary vF2 (Main Control Flow)

### What the diagram shows correctly
- L0-L6 layer topology and flow direction
- L5 Guardian as validation gate with Pass/Escalate/HIL decision
- L2 as Symmetric Validator-Healer Pipe
- L3 Human Review Gate with approval queue
- L4 Knowledge System (Semantic + Episodic memory)
- Artifact taxonomy (RESULT, AGGREGATE, INCIDENT, HEALING_PLAN)
- "No direct writes from L0" constraint

### What's MISSING (added in last 5-6 sessions)

| Missing Element | What exists in code now |
|---|---|
| **Classification Kernel** | `agentic_core/core/classification_kernel.py` — zero-dep SSOT with 19-priority queue, LRU cache, 68 contract tests |
| **6 Canonical Executors** | HOPPipelineExecutor, RGValidationExecutor, LICValidationExecutor, ObservabilityProbeExecutor, RGStrategyExecutor, InspectorExecutor |
| **Agent count reduction** | 190 → 149 agents (19 retirements, 28 merge shims) |
| **LCD+ Canonical Skeleton** | apps_* folders restructured to 6-folder standard (config/types/reasoning/engines/validators/utils) |
| **Blueprint Enforcement Engine** | 6-module enforcement suite (territory_diff, leaf_node, volatile_rules, mixin_ast, blueprint_hash, cross_layer) |
| **Phantom Baseline System** | Non-growing debt contract with 29 locked phantoms |
| **AI-Checking-AI Remediation** | 4 heuristic violations replaced with 8 deterministic Guardian tests |
| **Guardian-to-L6 Contract** | GuardianResult schema, correlation ID, POSIX paths, performance ceilings |
| **CI Governance Gates** | 4 CI workflows: ssot_verify, ssot-kernel-guardrail, guardian-tests, agent-sprawl-check |
| **Dependency Governance** | 57 packages in 4 buckets (core/dev/infra/sdks), import allowlist |
| **Control Plane** | Entire structural governance layer underpinning L0-L6 |

### What's STALE (diagram shows things that changed)

| Diagram Shows | Current Reality |
|---|---|
| Generic "Guardian (Validation Gate)" | Guardian now has **deterministic tests only** — no heuristic AI validation |
| L2 generic "Applies Approved Fix Only" | L2 now powered by **6 canonical executors** with parameterized dispatch |
| No mention of LCD structure | All apps_* folders restructured, 13 dissolved folders, ~130 import fixes |
| No mention of classification | Classification Kernel is the foundation — every layer imports it |

---

## Diagram 2: L5 Safety (Governance & Safety Drilldown)

### What's correct
- Budget Guard (Token/Cost Checks) — still exists
- Guardian (Validation Gate) — still exists
- Artifact Guard concept — still exists
- Policy Update Mechanism — still exists
- Flow: L0 → L5 → L2/L3

### What's MISSING

| Missing Element | Current Code |
|---|---|
| **FileClassificationAgent (FCA)** | Core L5 agent — delegates to classification_kernel, handles compound suffix resolution |
| **InspectorExecutor** | Replaced 3 inspector agents (DagRuntime, SignatureVerifier, TokenBudgetInspector) |
| **AI-Checking-AI remediation** | AutonomyGuardianAgent, SovereignCanonAuditor, ArchitectureGovernor, Phase5Validator — all now deterministic |
| **Structure Blueprint enforcement** | `structure_blueprint/enforcement/` with 6 modules, SHA-256 hash lock |
| **Compound suffix detection** | `_detect_filename_tag_conflicts()` — 49 regex patterns, 92 files renamed |
| **SSOT Guardrail** | `ssot_guardrail.py` — AST-based shadow classification blocker |
| **Shim Structural Lock** | AST enforcement: shims may only contain imports + `__all__` + docstring |

### What's STALE

| Diagram Shows | Current Reality |
|---|---|
| "Guardrail Guard" as separate box | Guardrail is now part of Blueprint Enforcement engine |
| "Safe State Emulation" | No longer a distinct component — subsumed by `_simulate_verify.py` |
| "Policy Guard (Static, Budget, Safety)" generic | Now split into deterministic modules with explicit enforcement contracts |
| "Permission Adapter (No New Adapters)" | Adapters reclassified — no longer hardcoded to enforcement/, inherit placement from wrapped component |
| Generic "Artifact Guard" | Now governed by Guardian-to-L6 contract with explicit schema |

---

## Diagram 3: L2 Pipeline v2 (Schema-Aligned Pipeline)

### What's correct
- L2.1 Validator Agent (pre-side-effect) concept
- L2.2 Healer Agent (post-failure/rollback) concept
- Artifact emission through Guardian
- AGGREGATE/RESULT/INCIDENT artifact types

### What's MISSING

| Missing Element | Current Code |
|---|---|
| **6 Canonical Executors** | The "Healer Agent" is now 6 parameterized executors handling different domains |
| **HOPPipelineExecutor** | 9 HOP stage agents consolidated into 1 with stage registry |
| **Wave Model** | Bounded mutation with blast-radius control (max actions per wave, confidence thresholds) |
| **Consolidation shims** | 28 merge shims providing backward compatibility |
| **Agent count governance** | Sprawl check CI gate preventing count > ceiling |

### What's STALE

| Diagram Shows | Current Reality |
|---|---|
| Single monolithic "L2.2 Healer Agent" | Now dispatched through 6 specialized executors |
| No mention of blast radius | Blast radius tracked per agent (max=9 for HOPPipelineExecutor) |
| No mention of rollback model | Wave model includes per-wave rollback with byte-for-byte snapshot restore |

---

## Diagram 4: L0 Core Logic & Routing (Drilldown)

### What's correct
- Router Election concept
- Contextual Router / Policy Config Manager / Policy Enforcer trio
- Connection to Knowledge Graph
- Flow to L2 and Metrics Dashboard

### What's MISSING

| Missing Element | Current Code |
|---|---|
| **LCD+ Canonical Skeleton** | L0 now enforces 6-folder standard for all apps_* |
| **Classification Kernel delegation** | `discovery_util.py` delegates to kernel for agent detection |
| **full_agent_discovery.py** | Uses `classification_cache_context()` for batch operations |
| **Leaf Node enforcement** | `allow_root_py=False` prevents loose .py files in certain directories |

### What's STALE

| Diagram Shows | Current Reality |
|---|---|
| "Permission Adapter (No New Adapters)" | Adapter classification fixed — no longer forced to enforcement/ |
| No mention of LCD structure | L0 is the primary enforcer of LCD+ skeleton |
| Generic "Policy Config Manager" | Now backed by immutable `MappingProxyType` + `frozenset` configs |

---

## Diagram 5: L6 Observability (Drilldown)

### What's correct
- Multi-modal Ingestion (Logs, Telemetry, API)
- Real-Time Stream Processing
- Signal Correlation & Deduplication
- Response Handler concept
- Connection to L5 and L2

### What's MISSING

| Missing Element | Current Code |
|---|---|
| **ObservabilityProbeExecutor** | Consolidated 6 obs agents into 1 parameterized executor |
| **Guardian-to-L6 Contract** | `GuardianResult` schema with correlation ID, max runtime, artifact size limits |
| **guardian_{id}.json artifacts** | Structured, L6-ingestible guardian results |
| **Telemetry-to-enforcement link** | L6 now consumes enforcement_report.json from blueprint enforcement |

### What's STALE

| Diagram Shows | Current Reality |
|---|---|
| "Model Trigger Heuristics" in Signal Correlation | Heuristics being replaced per §33 (Heuristic Replacement Mandate) |
| 6 separate observability agents implied | Now 1 ObservabilityProbeExecutor with probe_type dispatch |
| "Self-Healing Trigger" from Response Handler → L2 | Self-healing now bounded by wave model, not direct trigger |

---

## Recommended Diagram Updates (Priority Order)

| Priority | Diagram | Effort | Impact |
|---|---|---|---|
| **P0** | Exec Summary vF2 → v3 | Medium | Add Control Plane section, update L2 with executors, add CI badge |
| **P1** | L5 Safety | High | Major rework — add FCA, classification kernel, blueprint enforcement, AI-checking-AI |
| **P2** | L2 Pipeline v2 → v3 | Medium | Replace monolithic healer with 6 executors, add wave model |
| **P3** | L6 Observability | Low | Add ObservabilityProbeExecutor, Guardian-to-L6 contract |
| **P4** | L0 Core Logic | Low | Add LCD+ skeleton, classification kernel delegation |
| **NEW** | PNG 1-5 from figma_5png doc | High | 5 entirely new diagrams already specced in `figma_5png_architectural_diagrams.md` |

---

## How to Use Figma MCP Going Forward

### Current limitation
Your diagrams are local PNGs, not in Figma. The Figma MCP needs live Figma URLs to extract structured data.

### Recommended workflow
1. **Upload your updated diagrams to Figma** (use the "Untitled" file or create a new one)
2. **Organize into pages**: one Figma page per layer (L0-L6) + Exec Summary + Control Plane
3. **Add designer comments** on elements that need code verification
4. Then I can use:
   - `get_figma_data` → extract structured component data → cross-reference against codebase
   - `process_design_comments` → convert your annotations into actionable code tasks
   - `download_design_assets` → keep repo PNGs in sync with Figma source

### The Plugin script already exists
`docs/reports/plans/figma-flowchart-plugin.js` can auto-generate the v2 Exec Summary in Figma — that gives you a starting point to build from.

---

*Generated 2026-02-11. Cross-referenced against: agent_discovery_full.json, structure_blueprint, classification_kernel.py, consolidation artifacts, and 5 architecture PNGs.*

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

