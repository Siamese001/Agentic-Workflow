# ADG Gap Analysis for LLM-as-Judge Implementation

**Date**: 2026-03-17
**ADG Artifact**: `adg_indexed_03162026_2358.sqlite`
**Scope**: What does the ADG capture today, what can it already support for LLM-as-Judge, and what's missing?

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


## Executive Summary

The ADG is a **deeply instrumented static analysis artifact** with 69,291 nodes, 499,376 edges across 98 distinct relation types, and near-perfect edge metadata coverage (100% `source_file`, 100% `symbol`, 98.7% `line_no`). It already provides the structural foundation for an LLM-as-Judge across **10 evaluation planes**. However, it has **zero runtime data**, **no evaluation rubrics**, and **no verdict history** — the three pillars an LLM-as-Judge needs beyond static graph topology.

### What the ADG CAN judge today (static plane — strong)

| PLANE | EDGE TYPES | VERDICT POTENTIAL |
|-------|-----------|-------------------|
| Architectural compliance | `belongs_to_layer`, `violates` | Which modules break layer gravity rules |
| Write governance | `writes_to`, `writes_through`, `execution_terminates_at_uwg` | Whether writes route through UWG |
| Prompt provenance | `generates_prompt`, `consumes_prompt`, `prompt_template_used_by`, `instruction_injection_source` | Prompt chain-of-custody auditing |
| Security surface | `accesses_credential`, `reads_secret`, `invokes_eval`, `external_http_call`, `invokes_importlib` | Risk surface identification |
| Determinism compliance | `uses_wall_clock`, `uses_uuid`, `uses_random`, `seeds_rng`, `patches_time` | Non-determinism site inventory |
| Anti-pattern detection | `antipattern` (1,596 edges), `dead_imports`, `unreachable_after_raise` | Code quality violations with file:line |
| Governance wiring | `applies_guardrail`, `records_execution_trace`, `signs_execution_trace`, etc. | Per-module governance completeness |
| Agent orchestration | `agent_executes_agent`, `orchestrates_workflow`, `dispatches_healing_run` | Multi-agent flow analysis |
| Test coverage | `covers` (9,944 edges mapping 2,896 test modules → 2,337 targets) | Which modules have test coverage |
| Dependency analysis | `imports` (276K), `calls` (19K), `reads_from` (72K) | Impact radius, dependency chains |

### What the ADG CANNOT judge today (gaps)

| GAP # | CATEGORY | DESCRIPTION |
|-------|----------|-------------|
| G1 | **Runtime data** | No runtime execution traces, latencies, error rates, or actual call frequencies |
| G2 | **Evaluation rubrics** | No scoring criteria, thresholds, or pass/fail definitions stored in ADG |
| G3 | **Verdict history** | No prior judge verdicts, no trend analysis, no regression detection |
| G4 | **Source code content** | ADG knows *which* file:line has an edge but stores no actual code text |
| G5 | **Semantic understanding** | Edges are syntactic (AST-based) — no semantic meaning of what code *does* |
| G6 | **Cross-module transaction boundaries** | No representation of multi-module transaction scopes |
| G7 | **Configuration values** | `reads_config`/`reads_env` edges exist but actual config values are not stored |
| G8 | **Temporal evolution** | No diff between ADG versions; judge can't assess "did this get better or worse?" |

---

## Section 1 — ADG Data Model

### 1.1 SQLite Schema

**`nodes` table** (69,291 rows):

| COLUMN | TYPE | COMPLETENESS | DESCRIPTION |
|--------|------|-------------|-------------|
| `id` | INTEGER PK | 100% | Unique node identifier |
| `adg_name` | TEXT | 100% | Canonical name (`ADG::Module::path` or `ADG::Symbol::name`) |
| `entity_type` | TEXT | 100% | `module`, `symbol`, `prompt_slot`, `provider`, `seam`, `layer`, `gateway`, `prompt_template` |
| `layer` | TEXT | 100% | L0–L6, L_APP, L_OPS, L_PG, L_RUNTIME, L_SHARED, L_SL, L_TEST, L_TOOLS, L_UNKNOWN |
| `identity_kind` | TEXT | 99.98% | `repo_module`, `external_module`, `inferred_symbol`, `unresolved_import`, etc. |
| `confidence` | TEXT | 99.98% | `HIGH` (55,346), `MEDIUM` (13,447), `LOW` (483) |
| `resolved_path` | TEXT | varies | Physical file path for repo modules; empty for externals |

**`edges` table** (499,376 rows):

| COLUMN | TYPE | COMPLETENESS | DESCRIPTION |
|--------|------|-------------|-------------|
| `id` | INTEGER PK | 100% | Unique edge identifier |
| `src_id` | INTEGER FK→nodes | 100% | Source node |
| `dst_id` | INTEGER FK→nodes | 100% | Target node |
| `relation_type` | TEXT | 100% | 98 distinct types (see Section 2) |
| `edge_kind` | TEXT | **100%** | Semantic classification of the edge mechanism |
| `source_file` | TEXT | **100%** | File where the edge was detected |
| `line_no` | INTEGER | **98.7%** | Line number of the detection site |
| `symbol` | TEXT | **100%** | Fully-qualified symbol involved |

**`meta` table**:

| KEY | VALUE |
|-----|-------|
| `schema_version` | 4.0.0 |
| `scanner_digest` | `6996445d...` |
| `artifact_digest` | `1c833f52...` |
| `total_nodes` | 69,291 |
| `total_edges` | 499,376 |

### 1.2 Snapshot JSON

The `adg_snapshot_*.json` file provides aggregated views:

| FIELD | CONTENTS |
|-------|----------|
| `by_layer` | Module count per layer (16 layers) |
| `counts` | `module_count`, `symbol_count`, `total_entities`, `total_relations`, `orphan_module_count`, `unresolved_count`, `layer_violation_count` |
| `graph_plane_counts` | Per-relation-type edge count (98 entries) |
| `identity_health` | Confidence distribution, identity_kind distribution, unresolved_import_count |
| `blind_spots` | `dynamic_import_count: 0`, `parse_failure_count: 0`, `star_import_count: 9` |
| `top_fan_out_hotspots` | Top 20 modules by outgoing edge count |
| `top_fan_in_hotspots` | Currently empty |

### 1.3 Node Entity Types

| ENTITY TYPE | COUNT | JUDGE ROLE |
|-------------|-------|------------|
| `symbol` | 60,518 | Function/class-level targets for fine-grained judging |
| `module` | 8,603 | **Primary evaluation targets** (8,603 repo + external) |
| `prompt_slot` | 49 | Prompt injection surface audit (S0/D0/I0/C0/U0 slots) |
| `provider` | 15 | External LLM provider bindings (OpenAI, Anthropic, Google, etc.) |
| `seam` | 7 | Architectural seam points (canonical truth, layer emission, learning) |
| `layer` | 4 | Layer sentinel nodes |
| `gateway` | 3 | Write gateways (UWG, SovereignLLMGateway, EmbeddingSovereignAgent) |
| `prompt_template` | 3 | Named prompt templates (CONSTITUTION, input_jd, k1_hyde_generation) |

### 1.4 Node Identity Health

| IDENTITY KIND | COUNT | CONFIDENCE | MEANING |
|---------------|-------|------------|---------|
| `repo_module` | 10,834 | HIGH | Files in the repository — primary judge targets |
| `external_module` | 44,381 | HIGH | Third-party packages (numpy, openai, etc.) |
| `inferred_symbol` | 13,445 | MEDIUM | Symbols resolved by type inference |
| `unresolved_import` | 483 | LOW | Import resolution failures — judge blind spots |
| `package_container` | 59 | HIGH | Package `__init__` groupings |

---

## Section 2 — Complete Relation Type Inventory (98 types)

### 2.1 Dependency & Structure Plane

| RELATION TYPE | EDGES | FILES | EDGE_KIND | JUDGE USE |
|---------------|-------|-------|-----------|-----------|
| `imports` | 276,560 | 3,070+ | `import`, `lazy_import`, `optional_import` | Dependency chains, impact radius |
| `exports` | 38,408 | 3,050+ | `export` | API surface analysis |
| `calls` | 19,735 | 1,948 | `call` | Execution flow, hotspot detection |
| `decorated_by` | 17,128 | 3,043 | `decorator` | Decorator governance |
| `covers` | 9,944 | 2,896→2,337 | `import` | Test coverage mapping |
| `belongs_to_layer` | 6,323 | 3,059 | `layer_membership` | Layer assignment verification |
| `dead_imports` | 4,797 | 1,523 | `dead_import` | Code hygiene |
| `implements` | 2,261 | 834 | `unresolved`, `external` | Interface implementation |
| `instantiates` | 775 | 458 | `composition` | Object creation patterns |

### 2.2 Data Flow Plane

| RELATION TYPE | EDGES | FILES | JUDGE USE |
|---------------|-------|-------|-----------|
| `reads_from` | 72,783 | 2,898 | State consumption tracking (type_annotation edges) |
| `writes_to` | 5,119 | 1,314 | State mutation tracking |
| `reads_through` | 2,439 | 681 | Governance read path |
| `writes_through` | 2,153 | 750 | Governance write path |
| `reads_env` | 6,851 | 3,048 | Environment variable access |
| `reads_config` | 95 | 33 | Configuration reads |
| `reads_runtime_state` | 12,559 | 3,045 | Runtime state access (includes ~12K instrumentation leak) |
| `reads_policy_state` | 10,770 | 3,027 | Policy state access (includes ~8.9K instrumentation leak) |
| `reads_secret` | 151 | 71 | Secret/credential reads |
| `freezes_context` | 5 | 3 | Context freeze operations |
| `unfreezes_context` | 2 | 2 | Context unfreeze operations |

### 2.3 Governance & Compliance Plane

| RELATION TYPE | EDGES | SRC FILES | COVERAGE of 8,603 REPO MODULES |
|---------------|-------|-----------|-------------------------------|
| `applies_guardrail` | 173 | 69 | 0.8% |
| `records_execution_trace` | 325 | 202 | 2.3% |
| `signs_execution_trace` | 133 | 61 | 0.7% |
| `emits_determinism_digest` | 167 | 130 | 1.5% |
| `emits_replay_key` | 21 | 8 | 0.1% |
| `validated_by_safety_plane` | 549 | 264 | 3.1% |
| `validated_by_registry` | 12 | 9 | — |
| `validated_by_llm_gateway` | 30 | 14 | — |
| `snapshots_state` | 194 | 60 | 0.7% |
| `execution_terminates_at_uwg` | 60 | 15 | 0.2% |
| `references_policy_hash` | 230 | 99 | 1.2% |
| `observes_policy_state` | 85 | 34 | 0.4% |
| `guards_replay` | 29 | 7 | 0.1% |
| `gated_by_confidence` | 29 | 3 | — |
| `emits_metric_event` | 219 | — | — |
| `reads_governed_config` | 28 | 10 | — |
| `verifies_boundary` | 33 | 7 | — |
| `verifies_policy` | 11 | 5 | — |
| `validates_blast_radius` | 19 | 5 | — |
| `validates_config_schema` | 6 | 2 | — |

**Key observation**: Governance edge coverage is **very sparse** (0.1%–3.1% of repo modules). This is the #1 convergence blocker per the convergence gap analysis (138 modules missing `emits_determinism_digest`/`records_execution_trace`).

### 2.4 Security & Risk Plane

| RELATION TYPE | EDGES | FILES | JUDGE USE |
|---------------|-------|-------|-----------|
| `accesses_credential` | 376 | 165 | Credential access surface |
| `reads_secret` | 151 | 71 | Secret vault reads |
| `invokes_eval` | 546 | 249 | `eval()`/`exec()` call sites (includes `re.compile`) |
| `invokes_getattr_dynamic` | 539 | 207 | Dynamic dispatch (`getattr`/`setattr`/`delattr`) |
| `invokes_importlib` | 170 | 83 | Dynamic module loading |
| `external_http_call` | 6 | 5 | HTTP egress points |
| `instruction_injection_source` | 2 | 1 | Prompt injection vectors |
| `enters_sandbox` | 39 | 16 | Sandbox entry points |
| `uses_random` | 59 | 36 | RNG usage (non-determinism) |
| `seeds_rng` | 14 | 11 | RNG seeding |
| `patches_time` | 32 | 18 | Time patching for determinism |

### 2.5 Anti-Pattern Plane

| EDGE_KIND | COUNT | SAMPLE |
|-----------|-------|--------|
| `retry_without_backoff` | 880 | `for_retry` at file:line with no exponential backoff |
| `silent_exception_swallow` | 623 | `except:bare` — bare except clauses |
| `global_state_mutation` | 85 | Module-level variable mutation |
| `blocking_call_in_async` | 8 | Sync calls in async context |
| `star_import` | 9 | `from module import *` |

**Anti-pattern edges are richly annotated**: every one has `source_file`, `line_no`, `symbol`, and `edge_kind`. A judge can produce precise file:line:evidence citations.

Sample anti-pattern verdict data:
```
file=agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py
line=218, sym=for_retry, kind=retry_without_backoff
src=ADG::Module::agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py
dst=ADG::Symbol::retry_without_backoff
```

### 2.6 Prompt & LLM Plane

| RELATION TYPE | EDGES | FILES | JUDGE USE |
|---------------|-------|-------|-----------|
| `generates_prompt` | 215 | 11 | Prompt generation sites |
| `consumes_prompt` | 9 | 6 | Prompt consumption sites |
| `prompt_template_used_by` | 45 | 13 | Template→consumer mapping |
| `scores_groundedness` | 40 | 3 | Groundedness evaluation sites |
| `transcripts_response` | 13 | 7 | Response transcription |
| `invokes_provider` | 14 | 10 | LLM provider invocations |
| `builds_dpo_batch` | 43 | 10 | DPO preference learning |
| `produces_preference_pair` | 13 | 5 | Preference pair generation |
| `embeds_into` | 23 | 17 | Embedding pipeline entry |
| `retrieves_via` | 52 | 23 | Retrieval pipeline entry |
| `chunks_into` | 1 | 1 | Document chunking |
| `instruction_injection_source` | 2 | 1 | D0 injection vectors |

**Prompt slot authority model**: The schema defines 5 prompt slot types (S0, D0, I0, C0, U0) with authority ordering rules. 49 `prompt_slot` nodes are detected. A judge can verify whether prompt assembly respects the authority hierarchy.

### 2.7 Orchestration & Healing Plane

| RELATION TYPE | EDGES | FILES | JUDGE USE |
|---------------|-------|-------|-----------|
| `agent_executes_agent` | 112 | 24 | Multi-agent dispatch chains |
| `orchestrates_workflow` | 29 | 3 | Workflow orchestration sites |
| `orchestrates_healing` | 73 | 46 | Healing orchestration |
| `dispatches_healing_run` | 71 | 12 | Healing dispatch |
| `escalates_to_human` | 15 | 6 | HITL escalation points |
| `requires_human_review` | 5 | 5 | Human review gates |
| `routes_through` | 673 | 175 | Governance routing |
| `routes_path` | 183 | 35 | Execution path routing |
| `pulls_context` | 358 | 134 | JIT context retrieval |
| `forces_stall` | 9 | 4 | Execution stall forcing |
| `reenters_safety` | 3 | 2 | Safety re-entry gates |
| `vigilance_reroute` | 7 | 3 | Vigilance rerouting |

### 2.8 Layer Violation Plane

790 `violates` edges exist, each annotating a specific layer gravity violation:
```
file=agentic_core/L0_routing/__init__.py
line=62, sym=L0->L_RUNTIME, kind=import
```

The schema defines `ALLOWED_LAYER_EDGES` (a frozenset of 80+ valid layer→layer pairs) and `LAYER_AUTHORITY_FORBIDDEN` (per-layer forbidden relation types). A judge can systematically evaluate every import against these rules.

---

## Section 3 — What an LLM-as-Judge CAN Do Today (no ADG changes needed)

### 3.1 Judge-Ready Evaluation Dimensions

**Dimension 1: Architectural Compliance Judging**
- **Evidence**: `belongs_to_layer` + `violates` edges
- **Question**: "Does module X import only from allowed layers?"
- **Verdict**: Compare `violates` edges against `ALLOWED_LAYER_EDGES` rules. 790 violations already detected.
- **Confidence**: HIGH — deterministic, AST-backed

**Dimension 2: Anti-Pattern Judging**
- **Evidence**: `antipattern` edges (1,596) with `edge_kind` taxonomy (retry_without_backoff, silent_exception_swallow, global_state_mutation, blocking_call_in_async)
- **Question**: "Does module X have code quality violations?"
- **Verdict**: Direct — every edge has file:line:symbol. Judge can produce precise citations.
- **Confidence**: HIGH — deterministic, AST-backed

**Dimension 3: Write Governance Judging**
- **Evidence**: `writes_to`, `writes_through`, `execution_terminates_at_uwg`, `L1_WRITE_ALLOWLIST`
- **Question**: "Do all write operations route through the Universal Write Gateway?"
- **Verdict**: Modules with `writes_to` but without `writes_through` or `execution_terminates_at_uwg` edges are UWG bypass candidates.
- **Confidence**: MEDIUM — depends on edge completeness

**Dimension 4: Security Surface Judging**
- **Evidence**: `accesses_credential`, `reads_secret`, `invokes_eval`, `external_http_call`, `instruction_injection_source`
- **Question**: "What is the security attack surface of module X?"
- **Verdict**: Inventory all security-risk edges per module with file:line evidence.
- **Confidence**: HIGH for direct detections; LOW for indirect/transitive risks

**Dimension 5: Test Coverage Judging**
- **Evidence**: `covers` edges (9,944 edges, 2,896 test→2,337 target modules)
- **Question**: "Is module X tested?"
- **Verdict**: Check if target module appears as `dst_id` in `covers` edges.
- **Confidence**: MEDIUM — static import-based coverage, not runtime execution coverage

**Dimension 6: Determinism Compliance Judging**
- **Evidence**: `uses_wall_clock`, `uses_random`, `uses_uuid`, `seeds_rng`, `patches_time`, `guards_replay`, `emits_determinism_digest`, `emits_replay_key`
- **Question**: "Does module X use non-deterministic operations, and are they properly guarded?"
- **Verdict**: Modules with `uses_wall_clock`/`uses_random`/`uses_uuid` WITHOUT corresponding `seeds_rng`/`patches_time`/`guards_replay` are determinism risks.
- **Confidence**: HIGH — well-defined, AST-backed

**Dimension 7: Dependency Impact Judging**
- **Evidence**: `imports`, `calls`, fan-in/fan-out hotspots
- **Question**: "What is the blast radius of changing module X?"
- **Verdict**: Transitive closure of `imports`/`calls` edges from X gives impact set.
- **Confidence**: HIGH — import graph is complete

**Dimension 8: Prompt Chain-of-Custody Judging**
- **Evidence**: `generates_prompt`, `consumes_prompt`, `prompt_template_used_by`, `instruction_injection_source`, prompt slot nodes
- **Question**: "Does the prompt assembly chain for module X follow the authority hierarchy?"
- **Verdict**: Trace prompt flow from template→slot→consumer and verify authority ordering.
- **Confidence**: MEDIUM — depends on prompt detection completeness (215 generation sites detected)

**Dimension 9: Governance Wiring Completeness Judging**
- **Evidence**: All governance edges per module vs. expected governance dimensions
- **Question**: "Does module X have complete governance wiring?"
- **Verdict**: Build per-module governance profile and compare against required dimensions.
- **Confidence**: HIGH for presence checks; question is what the *required* set should be

**Dimension 10: Dead Code / Import Hygiene Judging**
- **Evidence**: `dead_imports` (4,797), `unreachable_after_raise` (388)
- **Question**: "Does module X have dead code or unused imports?"
- **Verdict**: Direct — edges have file:line:symbol evidence.
- **Confidence**: HIGH — deterministic, AST-backed

---

## Section 4 — Implementation Gaps for LLM-as-Judge

### G1: No Runtime Execution Data (CRITICAL)

**What's missing**: The ADG is purely static (AST-based). It has zero information about:
- Whether a `calls` edge is actually executed at runtime
- Call frequencies, latencies, error rates
- Runtime exception traces
- Actual LLM provider response times/costs
- Memory consumption per module

**Why it matters**: A judge evaluating "Is module X healthy?" needs both structural correctness (ADG has this) AND runtime behavior (ADG does not). A module can be perfectly wired but failing 50% of the time at runtime.

**What would need to change**:
- Add runtime telemetry collection (OpenTelemetry spans or similar)
- Store runtime edges alongside static edges (new table or separate artifact)
- New relation types: `runtime_calls` (with frequency/latency), `runtime_errors`, `runtime_latency_p99`

### G2: No Evaluation Rubrics or Scoring Criteria (CRITICAL)

**What's missing**: The ADG stores *facts* (edges exist or don't), but there are no:
- Scoring rubrics (e.g., "a module MUST have `applies_guardrail` if it has `writes_to`")
- Pass/fail thresholds
- Severity classifications per violation type
- Weighted scoring models

**Why it matters**: A judge needs both evidence (ADG has this) AND criteria to judge against. Currently the criteria are implicit in the convergence gap analysis and `.windsurfrules`, but they're not structured data a judge can programmatically consume.

**What would need to change**:
- Define a `rubrics` table or JSON artifact: `{dimension, rule_id, condition, severity, threshold}`
- Example rubric: `{dim: "write_governance", rule: "WG-001", condition: "module has writes_to AND NOT writes_through AND NOT execution_terminates_at_uwg", severity: "HIGH", verdict: "FAIL"}`
- This is the most impactful gap to close — it turns the ADG from a fact store into a judgeable evidence substrate

### G3: No Verdict History or Trend Tracking (HIGH)

**What's missing**: No record of prior judge evaluations:
- No verdict timestamps
- No trend analysis ("module X went from PASS to FAIL between ADG v1 and v2")
- No regression detection across ADG rebuilds

**Why it matters**: A judge system needs to detect *regressions* — things that were passing and now aren't. Without history, every evaluation is a fresh assessment with no temporal context.

**What would need to change**:
- New `verdicts` table: `{module_path, dimension, verdict, score, evidence_hash, adg_timestamp}`
- Diff engine between ADG versions (currently `artifact_digest` changes but no structured diff)

### G4: No Source Code Content (HIGH)

**What's missing**: The ADG records that "file X, line 47 calls symbol Y" but does NOT store the actual source code. The judge knows *that* an edge exists but can't read *what the code does*.

**Why it matters**: For nuanced verdicts (e.g., "Is this `eval()` call safe?"), the judge needs to see the actual code. The `invokes_eval` edge for `re.compile` is very different from `eval(user_input)`.

**What would NOT need to change in ADG**:
- Source code is on disk — the judge just needs a tool to read it (a source retrieval function, not an ADG schema change)
- The ADG already provides file:line coordinates — combine with filesystem read

### G5: No Semantic Understanding (MEDIUM)

**What's missing**: All edges are syntactic/structural — the ADG doesn't capture:
- What a function *does* (its purpose, its contracts)
- Whether a test *meaningfully* covers the behavior it imports
- Whether a `calls` edge represents a critical path or a fallback/logging path

**Why it matters**: A judge saying "module X has test coverage" (via `covers` edges) cannot distinguish between a thorough integration test and a trivial smoke test that imports the module but barely exercises it.

**What could change**:
- This is fundamentally an LLM analysis task, not an ADG schema task
- The judge itself would provide semantic understanding by reading source code (G4) and interpreting the edges
- Optional: Add a `semantic_role` column to edges if pre-classification is desired

### G6: No Cross-Module Transaction Boundaries (MEDIUM)

**What's missing**: No representation of:
- Multi-module transaction scopes (begin→commit→rollback)
- Distributed operation boundaries
- Eventual consistency windows

**Why it matters**: A judge evaluating "Is this multi-agent workflow safe?" needs to understand transaction boundaries, not just individual edges.

**What could change**:
- New entity type: `transaction_scope` with edges `begins_transaction`, `commits_transaction`, `participates_in_transaction`
- This requires semantic analysis beyond AST scanning

### G7: No Configuration Values (LOW)

**What's missing**: `reads_config` (95 edges) and `reads_env` (6,851 edges) tell us *which* modules read configuration, but not *what values* they read or whether those values are valid.

**Why it matters**: A judge evaluating configuration compliance needs to know whether `REDIS_URL` is set, not just that `os.environ.get("REDIS_URL")` is called.

**What could change**: Configuration values are runtime data (G1 overlap) — this would be addressed by runtime telemetry rather than ADG schema changes.

### G8: No Temporal ADG Evolution (LOW)

**What's missing**: No structured diff between ADG versions. The `artifact_digest` and `scanner_digest` change, but there's no "these 47 edges were added, these 12 were removed."

**Why it matters**: A judge evaluating a PR or code change needs to see the *delta* in the ADG, not the full graph.

**What could change**:
- Add an `adg_diff` tool that compares two SQLite files and produces structured diff
- Store edge/node deltas per commit (ties into `commit_sha` meta field, currently empty)

---

## Section 5 — ADG Structural Observations Relevant to Judge Design

### 5.1 Fan-Out Hotspots (most complex modules — highest judge scrutiny)

| FAN-OUT | MODULE |
|---------|--------|
| 1,235 | `apps_shared/types/sovereign_severity_types.py` |
| 1,104 | `agentic_core/L0_routing/scripts/execute_ssot.py` |
| 1,058 | `agentic_core/adg/extraction/static_scanner.py` |
| 756 | `tests/architecture/test_adg_branches_and_robustness.py` |
| 678 | `tests/adg/test_adg_g7_g16_completeness_accuracy.py` |

### 5.2 Fan-In Hotspots (most depended-upon — highest impact)

All top 15 fan-in nodes are symbols in `agentic_core/runtime/lifecycle_trace_contract.py` with 4,594–5,548 incoming edges each. This is the `_emit_*` instrumentation infrastructure — every module calls these emitters.

### 5.3 Governance Coverage Gap

Only **0.1%–3.1%** of repo modules have governance edges. This is by design (governance edges only appear on modules that actually call governance functions), but it means a judge applying governance rubrics will find most modules "not covered" unless the rubric accounts for module roles.

**Implication for judge design**: The rubric must classify modules into roles (agent, engine, config, test, utility) and apply different governance expectations per role. The ADG's `entity_type` and `layer` fields support this classification.

### 5.4 Instrumentation Edge Leakage

~27,000 edges in `reads_runtime_state`, `reads_policy_state`, and `reads_env` are instrumentation leakage — they're emitted by `_emit_*` calls, not by actual runtime state reads. These have deterministic counts and don't affect core governance edges, but a judge must be aware that these three relation types have inflated counts.

### 5.5 Blind Spots

| BLIND SPOT | COUNT | JUDGE IMPACT |
|-----------|-------|-------------|
| Unresolved imports | 483 | Edges to these nodes are LOW confidence — judge should flag but not fail |
| Star imports | 9 | Imported symbols are invisible to AST — judge has incomplete view |
| Dynamic imports | 0 | Not a current concern |
| Parse failures | 0 | All files parseable |

---

## Section 6 — Convergence Gap Interaction

The convergence gap analysis (`convergence_gap_analysis_03162026_2101.md`) identifies **138 modules** missing `emits_determinism_digest` and/or `records_execution_trace` as the sole convergence blocker.

An LLM-as-Judge system built on the ADG would directly serve convergence closure:

| CONVERGENCE CRITERION | HOW JUDGE USES ADG |
|-----------------------|---------------------|
| Delta-zero stability | Compare `artifact_digest` across rebuilds |
| High-risk gap closure | Query per-module governance edge profile, identify modules missing required dims |
| Canonical path closure | Trace `calls`→`routes_through`→`execution_terminates_at_uwg` chains |
| Replay determinism | Check `emits_determinism_digest`/`emits_replay_key` presence per module |
| Query answerability | Validate all judge queries return results |
| False-positive detection | Use `edge_kind` + `symbol` to distinguish real vs instrumentation edges |

---

## Section 7 — Prioritized Implementation Roadmap

### Phase 1: Evaluation Rubrics (unblocks G2) — **Highest ROI**

Define structured rubrics that turn ADG edges into pass/fail verdicts:

```
{
  "dimension": "write_governance",
  "rule_id": "WG-001",
  "applies_to": {"has_edge": "writes_to", "module_role": ["agent", "engine"]},
  "requires": {"any_edge": ["writes_through", "execution_terminates_at_uwg"]},
  "severity": "HIGH",
  "verdict_on_fail": "FAIL: Module writes state without UWG governance"
}
```

Store as `artifacts/judge/rubrics.json` or a new `rubrics` SQLite table.

### Phase 2: Source Code Bridge (unblocks G4)

Not an ADG change — a judge utility function:
```python
def get_source_context(file_path: str, line_no: int, window: int = 10) -> str:
    """Read source code around a specific file:line from ADG edge metadata."""
```

This closes the loop: ADG edge → file:line → actual code → LLM verdict.

### Phase 3: Verdict Storage (unblocks G3)

New `verdicts` table in a judge-specific SQLite:
```sql
CREATE TABLE verdicts (
    module_path TEXT, dimension TEXT, rule_id TEXT,
    verdict TEXT, score REAL, evidence TEXT,
    adg_timestamp TEXT, judge_timestamp TEXT
);
```

### Phase 4: Runtime Telemetry Integration (unblocks G1)

Extend ADG schema or create parallel artifact with runtime data:
- OpenTelemetry span export → `runtime_edges` table
- Join on `(source_file, symbol)` to correlate static and runtime edges

### Phase 5: ADG Diff Engine (unblocks G8)

Compare two SQLite ADG artifacts and produce structured delta:
- Added/removed nodes
- Added/removed edges by relation type
- Changed governance coverage percentages

---

## Section 8 — Summary Readiness Matrix

| JUDGE CAPABILITY | ADG READINESS | GAP | PHASE TO FIX |
|-----------------|---------------|-----|-------------|
| Evaluate architectural compliance | ✅ **READY** | — | — |
| Evaluate anti-pattern presence | ✅ **READY** | — | — |
| Evaluate dependency impact | ✅ **READY** | — | — |
| Evaluate dead code/imports | ✅ **READY** | — | — |
| Evaluate determinism compliance | ✅ **READY** | — | — |
| Evaluate security surface | ✅ **READY** | — | — |
| Evaluate layer violations | ✅ **READY** | — | — |
| Evaluate write governance | ⚠️ **PARTIAL** | Rubrics needed | Phase 1 |
| Evaluate governance wiring completeness | ⚠️ **PARTIAL** | Rubrics needed | Phase 1 |
| Evaluate prompt chain-of-custody | ⚠️ **PARTIAL** | Rubrics + source | Phase 1+2 |
| Evaluate test coverage quality | ⚠️ **PARTIAL** | Semantic understanding | Phase 2+5 |
| Produce file:line evidence citations | ⚠️ **PARTIAL** | Source code read | Phase 2 |
| Detect regressions across versions | ❌ **NOT READY** | Verdict history | Phase 3+5 |
| Evaluate runtime health | ❌ **NOT READY** | Runtime telemetry | Phase 4 |
| Evaluate configuration compliance | ❌ **NOT READY** | Runtime values | Phase 4 |
| Evaluate transaction safety | ❌ **NOT READY** | Transaction model | Future |

**Overall**: The ADG is **ready for 7 evaluation dimensions** today, **partially ready for 4 more** with rubrics + source code tooling, and **not ready for 5** that require runtime data or new schema extensions.

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

