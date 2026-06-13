# Prompt Governance Audit Report

**Date:** 2026-03-17
**ADG Database:** `adg_indexed_03172026_0002.sqlite`
**Scope:** `artifacts/adg/`, prompt governance infrastructure, injection coverage, tier-aware enrichment

---

## Executive Summary

Audited the prompt governance stack from ADG artifacts through assembly stage, slot contracts, injection symbols, agent registry, and reasoning tier enforcement. Found **7 critical gaps** and implemented **5 fixes** with **41 passing tests**.

---

## Gap Analysis

### Gap 1: D0 Injection Fence Coverage = 45.5%
- **Severity:** CRITICAL
- **Finding:** Only 5 of 11 prompt-generating files include D0 fences. `GovernedPayload.d0_injections` defaults to `""`, allowing assembly without injection fences.
- **Risk:** User prompts (U0) can influence system prompts (S0) without a D0 barrier.
- **Fix:** Added runtime warning in `GovernedPayload.__post_init__()` when S0+U0 present but D0 empty.

### Gap 2: 62/67 Agent Reasoning Files Have ZERO Prompt Governance Edges
- **Severity:** HIGH
- **Finding:** Only 5 agent files have any prompt-related ADG edges (`generates_prompt`, `consumes_prompt`, `instruction_injection_source`, `prompt_template_used_by`). The remaining 62 agents operate entirely outside prompt governance tracking.
- **Root Cause:** Most agents delegate to engine files (spine adapters, executors) where prompt assembly occurs. The agents themselves don't directly generate/consume prompts.
- **Fix:** Added detection to `identify_guardrail_gaps.py` for ongoing monitoring.

### Gap 3: ALL Agents in Registry Were `ReasoningIntensity.HIGH`
- **Severity:** HIGH
- **Finding:** Every agent in `AGENT_REGISTRY` was classified as `HIGH` reasoning. The `LOW` and `MEDIUM` tiers existed in the enum but were never assigned.
- **Fix:** Reclassified deterministic agents:
  - **LOW:** `location`, `file_classification`, `root_hygiene`, `tool_reliability_mixin`, `ssot_audit`
  - **MEDIUM:** `hierarchy`, `gravity_repair`
  - **HIGH:** `reconciler`, `arch_governor`, `system_architect`, `conversational_repair`, `cognitive_disposition`, `sovereign_base`, `mission_runner`, `orchestrator_engine`

### Gap 4: No Tier-Aware I0 Instructional Enrichment
- **Severity:** HIGH
- **Finding:** `AirlockAssembler.assemble()` accepts `i0_instructional` but no mechanism populates it based on reasoning tier. LOW-tier agents (1 branch, depth 1, no reflection) receive the same generic instruction as CRITICAL-tier agents.
- **Fix:** Created `agentic_core/prompt_governance/core/tier_instructional_enrichment.py`:
  - `TIER_ENRICHMENT_TABLE` with tier-specific constraints, guidance, and preambles
  - `enrich_i0_for_tier()` function to prepend tier-appropriate instructions
  - LOW tier: 5 constraints + 5 guidance items (explicit, prescriptive)
  - HIGH tier: 2 constraints (permissive)
  - CRITICAL tier: reflexion-enabled, extended budget

### Gap 5: High-Risk Operations Guardrail Coverage = 13.8%
- **Severity:** MEDIUM (existing — documented for tracking)
- **Finding:** 1,250 high-risk edges, only 173 guardrail edges. Key gaps:
  - `accesses_credential`: 96% gap (170/177 files)
  - `invokes_eval`: 99% gap (199/202 files)
  - `reads_secret`: 97% gap (35/36 files)
- **Status:** Pre-existing. Now tracked by enhanced `identify_guardrail_gaps.py`.

### Gap 6: `PROMPT_INJECTION_SYMBOLS` Too Narrow (7 → 17 symbols)
- **Severity:** MEDIUM
- **Finding:** Only covered `InstructionInjector`, `PromptInjector`, `D0Injector`, `inject_instruction`, `inject_d0`, `PromptAugmentor`, `InstructionOverride`. Missing coverage for context injection (C0), user override (U0), system override (S0), escalation, and hijacking.
- **Fix:** Added 10 symbols: `ContextInjector`, `C0Injector`, `inject_context`, `U0Override`, `SystemPromptOverride`, `PromptEscalator`, `inject_system`, `inject_u0`, `PromptHijacker`, `SlotOverride`.

### Gap 7: Only 2 `instruction_injection_source` Edges in Entire Codebase
- **Severity:** LOW
- **Finding:** Only `OutreachLearningAgent.py` emits this edge type. Scanner detection is working but the surface area is minimal.
- **Status:** Monitored by new `identify_guardrail_gaps.py` section.

---

## Files Modified

| File | Change |
|------|--------|
| `agentic_core/adg/schema.py` | Widened `PROMPT_INJECTION_SYMBOLS` (7 → 17) |
| `agentic_core/L0_routing/engines/assembly_stage.py` | Added D0 fence warning in `GovernedPayload.__post_init__()` |
| `agentic_core/agents/agent_registry.py` | Reclassified 7 agents to proper tiers (5 LOW, 2 MEDIUM) |
| `tools/adg/identify_guardrail_gaps.py` | Added Prompt Governance Gaps section |

## Files Created

| File | Purpose |
|------|---------|
| `agentic_core/prompt_governance/core/tier_instructional_enrichment.py` | Tier-aware I0 enrichment provider |
| `tests/unit/prompt_governance/__init__.py` | Test package init |
| `tests/unit/prompt_governance/test_tier_instructional_enrichment.py` | 20 tests for enrichment provider |
| `tests/unit/prompt_governance/test_prompt_governance_coverage.py` | 21 tests for symbols, registry, D0 |

## Evidence Files (cleanup candidates)

| File | Purpose |
|------|---------|
| `tools/evidence/_prompt_governance_audit.py` | Audit script (ADG query) |
| `tools/evidence/_prompt_governance_audit2.py` | Detail audit script (ADG query) |

---

## Test Results

**41 tests passed, 0 failed, 0 errors.**

```
tests/unit/prompt_governance/test_tier_instructional_enrichment.py    — 20 passed
tests/unit/prompt_governance/test_prompt_governance_coverage.py       — 21 passed
```

---

## Recommendations for Follow-Up

1. **Wire `enrich_i0_for_tier()` into spine adapters** — The enrichment provider exists but needs to be called during `_LicAssemblerAdapter.assemble()` and `_RgAssemblerAdapter.assemble()` when the agent's reasoning tier is available from the execution envelope.

2. **Increase D0 fence adoption** — Currently 45.5%. Target: 100% for all production prompt assembly paths. Add a CI gate that fails on new files generating S0+U0 without D0.

3. **Register app-level agents** — The `AGENT_REGISTRY` only has infrastructure agents. App-level agents (`ValidatorAgent`, `HOPPipelineExecutor`, etc.) should be registered with proper tier classification.

4. **ADG re-index after these changes** — Run `python tools/generate_full_adg.py` to pick up the widened `PROMPT_INJECTION_SYMBOLS` in the next scan.

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

