# AG-RGGOV-6 Classification Report: apps_rg/config/agent_spec_config.py

**Plan:** apps-rg-declarative-ingress-only-spinal-governance-c8b3e1  
**Decision:** AG-RGGOV-6 = DECLARATIVE_PROFILE_ONLY  
**Date:** 2026-05-09  
**File Analyzed:** `apps_rg/config/agent_spec_config.py` (410 lines)

---

## Executive Summary

`agent_spec_config.py` is **severely contaminated** with runtime authority patterns:
- **172+ OTEL/lifecycle trace emission calls** (lines 71-232)
- **Orchestration topology schemas** defining execution graphs and agent dispatch
- **Legacy HOP runner configurations** with temperature, retry loops, iteration limits
- **Cross-imports from `agentic_core.runtime.contracts`**

**Verdict:** 85-90% of this file must be **quarantined**. Only static stylistic constraints and output schema definitions are eligible for declarative profile migration.

---

## 1. Field Classification Table

| Symbol | Current Purpose | Static Declarative? | Runtime Authority Smell? | Target Destination | Action |
|--------|-----------------|--------------------|--------------------------|-------------------|--------|
| **OTEL IMPORTS (lines 17-60, 74-97)** | Import 50+ `_emit_*` lifecycle trace functions | ❌ NO | ✅ YES — Core runtime contract emission | `agentic_core/L6_observability/` or delete | **QUARANTINE** |
| `_emit_applies_guardrail` (line 71) | Emits P0 guardrail span | ❌ NO | ✅ YES — Runtime trace emission | `agentic_core/L6_observability/` | **QUARANTINE** |
| `_emit_reads_policy_state` (line 72) | Emits P0 policy read span | ❌ NO | ✅ YES — Runtime trace emission | `agentic_core/L6_observability/` | **QUARANTINE** |
| `_emit_snapshots_state` (line 73) | Emits P0 state snapshot span | ❌ NO | ✅ YES — Runtime trace emission | `agentic_core/L6_observability/` | **QUARANTINE** |
| **100+ metric/observability emissions (lines 99-232)** | Emit P1-P4 spans for metrics, incidents, learning, routing | ❌ NO | ✅ YES — Runtime telemetry | `agentic_core/L6_observability/` or delete | **QUARANTINE** |
| **Pipeline Constants (lines 61-69)** | Import `BATCH_SIZE`, `BUFFER_SIZE`, `MAX_DEPTH`, etc. | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — Values may be runtime-stateful | Review per-usage | **EVALUATE** |
| `AgentSpec` (lines 243-251) | Pydantic model: agent name, module_path, inputs, outputs, timeout, criticality | ❌ NO | ✅ YES — Runtime agent topology definition | `agentic_core/L3_orchestration/` | **QUARANTINE** |
| `OrchestrationTopology` (lines 254-279) | Pydantic model: execution graph, phases, agents registry | ❌ NO | ✅ YES — MAJOR runtime orchestration authority | `agentic_core/L3_orchestration/` | **QUARANTINE** |
| `OrchestrationTopology.validate_agents_exist` (lines 264-279) | Validator ensuring phase agents exist in registry | ❌ NO | ✅ YES — Runtime validation with trace emission | `agentic_core/L3_orchestration/` | **QUARANTINE** |
| `ClerkExtractionConfig.metrics_patterns` (line 290-292) | Regex patterns for metrics extraction | ✅ YES | ❌ NO — Static extraction rules | `rg_evidence_profile.yaml` | **MIGRATE** |
| `ClerkExtractionConfig.min_bullets_per_section` (line 293) | Minimum bullet count constraint | ✅ YES | ❌ NO — Static output constraint | `rg_output_schema.json` | **MIGRATE** |
| `ClerkExtractionConfig.max_bullets_per_section` (line 294) | Maximum bullet count constraint | ✅ YES | ❌ NO — Static output constraint | `rg_output_schema.json` | **MIGRATE** |
| `EnrichmentConfig.forbidden_phrases` (lines 300-307) | List of prohibited phrases | ✅ YES | ❌ NO — Static style constraint | `rg_style_profile.yaml` | **MIGRATE** |
| `EnrichmentConfig.duplicate_threshold` (line 309) | Similarity threshold for dedup | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — May influence runtime dedup algo | `rg_evidence_profile.yaml` with annotation | **MIGRATE WITH FLAG** |
| `EnrichmentConfig.power_verbs` (lines 310-322) | Approved action verbs list | ✅ YES | ❌ NO — Static style vocabulary | `rg_style_profile.yaml` | **MIGRATE** |
| `GenerationConfig.base_temperatures` (lines 329-331) | Model temperature per section | ❌ NO | ✅ YES — Runtime model parameter | Core Prompt Assembly | **QUARANTINE** |
| `GenerationConfig.max_section_words` (lines 332-334) | Word count limits | ✅ YES | ❌ NO — Static output constraint | `rg_output_schema.json` | **MIGRATE** |
| `GenerationConfig.n_candidates` (line 335) | Number of candidates to generate | ❌ NO | ✅ YES — Runtime generation behavior | Core Prompt Assembly | **QUARANTINE** |
| `ValidationConfig.severity_threshold` (line 341) | Validation severity level | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — May gate exit behavior | `rg_evidence_profile.yaml` with annotation | **MIGRATE WITH FLAG** |
| `ValidationConfig.rule_categories` (lines 342-344) | Categories to validate | ✅ YES | ❌ NO — Static validation scope | `rg_evidence_profile.yaml` | **MIGRATE** |
| `ValidationConfig.min_quality_score` (line 345) | Minimum quality threshold | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — May gate exit behavior | `rg_evidence_profile.yaml` with annotation | **MIGRATE WITH FLAG** |
| `GateConfig.factual_failure_rules` (lines 351-353) | Rules for factual failure | ❌ NO | ✅ YES — Runtime gate logic | `agentic_core/L5_safety/` | **QUARANTINE** |
| `GateConfig.max_factual_loops` (line 354) | Max retry loops for facts | ❌ NO | ✅ YES — Runtime retry behavior | `agentic_core/L5_safety/` | **QUARANTINE** |
| `GateConfig.max_creative_retries` (line 355) | Max retries for creative | ❌ NO | ✅ YES — Runtime retry behavior | `agentic_core/L5_safety/` | **QUARANTINE** |
| `GateConfig.pass_threshold` (line 356) | Score threshold to pass | ❌ NO | ✅ YES — Runtime gate threshold | `agentic_core/L5_safety/` | **QUARANTINE** |
| `RefinementConfig.optimization_targets` (lines 362-364) | Targets for refinement | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — May drive runtime optimization | `rg_capability_profile.yaml` | **MIGRATE WITH REVIEW** |
| `RefinementConfig.max_iterations` (line 365) | Max refinement iterations | ❌ NO | ✅ YES — Runtime iteration limit | Core L2 Execution | **QUARANTINE** |
| `QAReportConfig.report_sections` (lines 371-378) | Report section names | ✅ YES | ❌ NO — Static output schema | `rg_output_schema.json` | **MIGRATE** |
| `QAReportConfig.output_directory` (line 379) | Directory for QA reports | ❌ NO | ✅ YES — Runtime file system write | Core L4 State or delete | **QUARANTINE** |
| `QAReportConfig.scoring_weights` (lines 380-387) | Dimension weights for scoring | ⚠️ PARTIAL | ⚠️ CONTEXTUAL — May influence runtime judge | `rg_evidence_profile.yaml` with annotation | **MIGRATE WITH FLAG** |
| `OrchestratorConfig.global_step_limit` (line 393) | Max steps in orchestration | ❌ NO | ✅ YES — Runtime step limit | `agentic_core/L3_orchestration/` | **QUARANTINE** |
| `OrchestratorConfig.max_retry_iterations` (line 394) | Max retries overall | ❌ NO | ✅ YES — Runtime retry behavior | `agentic_core/L3_orchestration/` | **QUARANTINE** |
| `OrchestratorConfig.checkpoint_enabled` (line 395) | Enable checkpointing | ❌ NO | ✅ YES — Runtime persistence behavior | `agentic_core/L4_state/` | **QUARANTINE** |
| `OrchestratorConfig.trace_persistence` (line 396) | Enable trace persistence | ❌ NO | ✅ YES — Runtime observability behavior | `agentic_core/L6_observability/` | **QUARANTINE** |
| `RGAgentSpecs` (lines 399-410) | Root config combining all HOP specs | ❌ NO | ✅ YES — Container for all above | N/A — container | **DECOMPOSE** |
| `PromptReceptionSpec` (imported) | Base class for prompt handling | ❌ NO | ✅ YES — Runtime prompt contract | `agentic_core/L1_cognition/` | **QUARANTINE** |

---

## 2. YAML/Profile Mapping

### 2.1 rg_planning_profile.yaml (New — Planning Constraints)

```yaml
# Static planning parameters migrated from agent_spec_config.py
# These constraints guide L1 planning but do not control runtime behavior

planning_constraints:
  max_sections: 7  # Derived from QAReportConfig.report_sections length
  
output_structure:
  required_sections:
    - executive_summary
    - quality_metrics
    - validation_results
    - recommendations
  
# Note: n_candidates, temperature, retry_iterations are NOT here
# Those are runtime parameters controlled by core Prompt Assembly
```

### 2.2 rg_evidence_profile.yaml (Evidence & Validation Rules)

```yaml
# Migrated from ClerkExtractionConfig, ValidationConfig, QAReportConfig

extraction_rules:
  metrics_patterns:
    - "\\$\\d+\\.?\\d*[MBK]\\+?"
    - "\\d+\\.?\\d*%"
    - "\\d{1,3}(?:,\\d{3})+"
  
validation_scope:
  rule_categories:
    - grammar
    - formatting
    - content_quality
    - ats_compatibility
  
quality_thresholds:
  # These are TARGETS, not runtime gates
  # Core Exit uses these as advisory targets, not hard thresholds
  min_quality_score: 0.7  # MIGRATE_WITH_FLAG: advisory target only
  severity_target: WARNING  # MIGRATE_WITH_FLAG: advisory classification
  
scoring_dimensions:
    # MIGRATE_WITH_FLAG: weights are advisory for judge calibration
    content_quality: 0.30
    ats_compatibility: 0.25
    keyword_match: 0.25
    formatting: 0.20
```

### 2.3 rg_prompt_profile.yaml (Style & Constraints)

```yaml
# Migrated from EnrichmentConfig

style_constraints:
  forbidden_phrases:
    - "responsible for"
    - "duties included"
    - "helped with"
    - "assisted with"
    - "worked on"
  
  preferred_verbs:
    - achieved
    - delivered
    - led
    - drove
    - established
    - transformed
    - accelerated
    - optimized
    - pioneered
    - spearheaded

content_constraints:
  # Advisory only — core may override based on context
  duplicate_similarity_threshold: 0.85  # MIGRATE_WITH_FLAG: advisory
```

### 2.4 rg_output_schema.json (Output Structure & Limits)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RG Output Schema",
  "description": "Static output constraints migrated from agent_spec_config.py",
  
  "constraints": {
    "bullets_per_section": {
      "min": 3,
      "max": 8
    },
    "section_word_limits": {
      "summary": 100,
      "experience_bullet": 30,
      "skills": 50
    }
  },
  
  "report_structure": {
    "required_sections": [
      "executive_summary",
      "quality_metrics",
      "validation_results",
      "recommendations"
    ]
  }
}
```

### 2.5 rg_style_profile.yaml (Stylistic Guidelines)

```yaml
# Migrated from EnrichmentConfig and style-related fields

voice_and_tone:
  # High-level stylistic targets (advisory)
  professional: true
  achievement_oriented: true
  metric_driven: true

vocabulary:
  power_verbs:
    - achieved
    - delivered
    - led
    - drove
    - established
    - transformed
    - accelerated
    - optimized
    - pioneered
    - spearheaded

avoid:
  passive_phrases:
    - "responsible for"
    - "duties included"
    - "helped with"
    - "assisted with"
    - "worked on"
```

### 2.6 rg_capability_profile.yaml (Capability Declarations)

```yaml
# Declarative capability metadata only
# Runtime capability execution lives in agentic_core

declared_capabilities:
  # Advisory list of what this profile package claims to support
  # Core validates against actual capability registry
  supported_formats:
    - ats_compatible_resume
    - executive_summary
    
  optimization_targets:  # MIGRATE_WITH_REVIEW
    # These are aspirational targets, not runtime directives
    - keyword_density
    - action_verb_strength
    - quantification_rate

# NO runtime configuration here:
# - No max_iterations (runtime L2 concern)
# - No step_limits (runtime L3 concern)
# - No retry counts (runtime L3/L5 concern)
# - No checkpoint settings (runtime L4 concern)
```

---

## 3. Runtime-Behavior Quarantine List

These symbols MUST be quarantined — they implement or configure runtime authority:

### 3.1 OTEL/Lifecycle Emissions (All Must Go)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| All `_emit_*` imports | 17-60, 74-97 | Trace emission runtime calls |
| All `_emit_*` invocations | 71-232 | 100+ runtime span emissions |
| `LayerSegment` import | 18 | Layer trace enumeration |

**Quarantine Target:** `archives/apps_rg/runtime_traces_20260509/`  
**Inertness:** Module should not import; if forced, `RuntimeError` on any emission call.

### 3.2 Orchestration & Topology (Major Runtime Authority)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| `AgentSpec` | 243-251 | Agent runtime topology definition |
| `OrchestrationTopology` | 254-279 | Execution graph, phase ordering |
| `validate_agents_exist` | 264-279 | Runtime validation with trace emission |

**Quarantine Target:** `archives/apps_rg/orchestration_config_20260509/`  
**Migration Path:** Core L3 already has equivalent topology management; no migration needed.

### 3.3 Model & Generation Parameters (Runtime Model Behavior)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| `GenerationConfig.base_temperatures` | 329-331 | Model temperature control |
| `GenerationConfig.n_candidates` | 335 | Candidate generation count |

**Quarantine Target:** Core L2 Execution (if needed) or delete.  
**Rationale:** Prompt Assembly in core owns model parameter selection.

### 3.4 Gate & Retry Configuration (L5 Safety Runtime)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| `GateConfig.factual_failure_rules` | 351-353 | Gate failure classification |
| `GateConfig.max_factual_loops` | 354 | Factual retry limit |
| `GateConfig.max_creative_retries` | 355 | Creative retry limit |
| `GateConfig.pass_threshold` | 356 | Gate pass threshold |

**Quarantine Target:** `agentic_core/L5_safety/gate_config.py` (core already owns)  
**Note:** These are already likely duplicated in core; verify before migration.

### 3.5 Orchestrator Runtime State (L3 Orchestration)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| `OrchestratorConfig.global_step_limit` | 393 | Step limit enforcement |
| `OrchestratorConfig.max_retry_iterations` | 394 | Retry behavior |
| `OrchestratorConfig.checkpoint_enabled` | 395 | Persistence behavior |
| `OrchestratorConfig.trace_persistence` | 396 | Observability behavior |

**Quarantine Target:** `agentic_core/L3_orchestration/runtime_limits.py`  
**Rationale:** Core L3 owns orchestration; these are runtime policy parameters.

### 3.6 Container Class (Decomposed)

| Symbol | Line(s) | Runtime Authority |
|--------|---------|-------------------|
| `RGAgentSpecs` | 399-410 | Combines all runtime configs |
| `PromptReceptionSpec` (imported) | — | Base runtime contract |

**Quarantine Target:** N/A (decomposed into parts above)  
**Note:** `RGAgentSpecs` serves no purpose after decomposition.

---

## 4. Profile Schema Updates Required

### 4.1 New Profile: `rg_planning_profile.yaml`

**Purpose:** Static planning constraints for L1 cognition  
**Fields:**
- `planning_constraints.max_sections`
- `output_structure.required_sections`

### 4.2 Updated: `rg_evidence_profile.yaml`

**Add Fields:**
```yaml
extraction_rules:
  metrics_patterns: [regex_list]
  
validation_scope:
  rule_categories: [string_list]
  
quality_thresholds:
  min_quality_score: float  # FLAG: advisory target
  severity_target: string   # FLAG: advisory classification
  
scoring_dimensions:
  [dimension]: weight_float  # FLAG: advisory for judge calibration
```

### 4.3 Updated: `rg_output_schema.json`

**Add Constraints:**
```json
{
  "constraints": {
    "bullets_per_section": { "min": int, "max": int },
    "section_word_limits": { "section": int }
  },
  "report_structure": {
    "required_sections": [string_list]
  }
}
```

### 4.4 Updated: `rg_prompt_profile.yaml`

**Add Fields:**
```yaml
style_constraints:
  forbidden_phrases: [string_list]
  
content_constraints:
  duplicate_similarity_threshold: float  # FLAG: advisory
```

### 4.5 Updated: `rg_style_profile.yaml`

**Add Fields:**
```yaml
vocabulary:
  power_verbs: [string_list]
  avoid:
    passive_phrases: [string_list]
```

### 4.6 Updated: `rg_capability_profile.yaml`

**Add Fields:**
```yaml
declared_capabilities:
  supported_formats: [string_list]
  optimization_targets: [string_list]  # REVIEW: aspirational only
```

---

## 5. Unresolved Ambiguities (AG_QUEUE_SEED)

### AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-6a depends_on=AG-RGGOV-6 title=Duplicate threshold behavioral semantics

`EnrichmentConfig.duplicate_threshold` (0.85) controls similarity for deduplication.  
**Question:** Is this an advisory target (core may approximate) or exact runtime requirement?  
**Impact:** If exact, needs core implementation. If advisory, stays in profile with `approximate: true` flag.

### AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-6b depends_on=AG-RGGOV-6 title=Quality score threshold semantics

`ValidationConfig.min_quality_score` (0.7) and `GateConfig.pass_threshold` (0.8) are close.  
**Question:** Is 0.7 a "target" and 0.8 a "gate"? Or is 0.7 the pre-gate floor?  
**Impact:** If distinct thresholds, both need semantic clarification. If redundant, pick one.

### AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-6c depends_on=AG-RGGOV-6 title=Scoring weights runtime binding

`QAReportConfig.scoring_weights` sum to 1.0 (0.3+0.25+0.25+0.2).  
**Question:** Does core judge use these weights exactly, or as hints?  
**Impact:** If exact, core needs weighted scoring implementation. If hints, profile annotation suffices.

### AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-6d depends_on=AG-RGGOV-6 title=Power verbs enforcement level

`EnrichmentConfig.power_verbs` is a preferred list.  
**Question:** Is this a hard constraint (reject non-list verbs) or advisory (prefer when appropriate)?  
**Impact:** Hard constraint needs validation logic in core. Advisory is style guide only.

---

## 6. Action Summary

| Action Category | Count | Destination |
|----------------|-------|-------------|
| **MIGRATE** (clean static) | 15 fields | `apps_rg/profiles/*.yaml` |
| **MIGRATE_WITH_FLAG** (ambiguous) | 5 fields | `apps_rg/profiles/*.yaml` + core review |
| **MIGRATE_WITH_REVIEW** (needs decision) | 1 field | `rg_capability_profile.yaml` + AG-RGGOV-6a/b/c/d |
| **QUARANTINE** (runtime authority) | 25+ symbols | `archives/apps_rg/` or `agentic_core/` |
| **DELETE** (redundant) | ~172 emission calls | Remove entirely |

**W3 Planning Block Status:** AG-RGGOV-6 classification complete.  
**Recommendation:** Resolve AG-RGGOV-6a through AG-RGGOV-6d before finalizing profile schemas, then proceed with field migration and quarantine.

---

**DECISION_CAPTURED:** AG-RGGOV-6 field classification delivered. W3 planning block resolved pending ambiguity decisions.
