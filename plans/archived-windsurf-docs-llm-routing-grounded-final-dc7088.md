---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-grounded-final-dc7088.md'
original_relative_path: 'llm-routing-grounded-final-dc7088.md'
source_sha256: 4abe964ccfa84ea13bf42b49bb58bd9e5b0b4e8693093722dd924a6132b4c2f5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing: Grounded Final Plan Based on Actual Repo Code

Implement LLM routing hardening based on what actually exists in the codebase — extending real infrastructure rather than aspirational abstractions.

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


## What Already Exists (Do NOT Recreate)

| Component | Location | Status |
|-----------|----------|--------|
| `FailureSignal` + `to_healing_input()` | `healing_tier_types.py` | COMPLETE |
| `InvocationRecord` (immutable) | `healing_tier_dispatcher.py` | COMPLETE |
| `dispatch_healing()` choke point | `healing_tier_dispatcher.py` | COMPLETE |
| `route_healing_tier()` single choke | `healing_tier_router.py` | COMPLETE |
| `FAILURE_CLASS_PRIORS` rubric | `healing_tier_router.py` | COMPLETE |
| `HealingTierConfig` (frozen, X/Y bands) | `healing_tier_config.py` | COMPLETE |
| `HealSeamBypassError` + capability token | `heal_llm_seam.py` | COMPLETE |
| `HealBudgetCaps` + context counters | `heal_llm_seam.py` | COMPLETE |
| `HealTelemetryRecord` + `policy_hash` | `heal_llm_seam.py` | COMPLETE |
| `ReplayBundle` + `canonical_bytes()` | `L4_state/types/replay_bundle_types.py` | COMPLETE |
| `active_config_hashes` dict in replay | `replay_bundle.py` | COMPLETE |
| `@standard_heal` seam enforcement | `decorators_util.py` | COMPLETE |

---

## What Is MISSING (Actual Gaps to Fill)

| Gap | Impact | Priority |
|-----|--------|----------|
| `invoke_qwen_vllm()` / `invoke_gemini()` are **stubs** | No actual LLM calls anywhere | CRITICAL |
| `call_llm()` does not exist in `MCPOperationMixin` | apps_rg engines silently broken | CRITICAL |
| No `ReasoningClass` enum — binary HIGH/LOW only | Coarse routing | HIGH |
| `HEAL_POLICY_MODEL_ESCALATION` is global env var | Cannot classify per-agent | HIGH |
| `HealingTierConfig` thresholds are static constants | Not read from L4 state | MEDIUM |
| No `healing_config_hash` in `ReplayBundle.active_config_hashes` | Config not replay-anchored | MEDIUM |
| No AST-based CI ban on model literals / temp outside gateway | Drift re-entry risk | MEDIUM |
| No agent classification scan with objective rubric | Guessing which agents need LLM | HIGH |
| No generation path (only healing path exists) | apps_rg production calls unrouted | HIGH |

---

## Phase 0 — Agent Classification Scan

Use the **existing** `FAILURE_CLASS_PRIORS` rubric to derive objective classification criteria:

```
syntax_error prior=0.90   → DETERMINISTIC (local agent handles)
import_cycle prior=0.70   → DETERMINISTIC
naming_violation prior=0.85 → DETERMINISTIC
location_violation prior=0.65 → DETERMINISTIC
structure_violation prior=0.60 → DETERMINISTIC (marginal LLM benefit)
gravity_leak prior=0.55   → LLM candidate
integrity_gate_failure prior=0.50 → LLM candidate
test_failure prior=0.45   → LLM candidate
runtime_error prior=0.35  → LLM required
unknown prior=0.30        → LLM required
```

### Classification rubric (objective, AST-based scan)
For each agent, AST-scan for:

| Signal | Weight | Interpretation |
|--------|--------|----------------|
| `heal_violations()` cyclomatic complexity > 8 | +2 | Complex logic |
| Cross-agent imports in heal method | +2 | Non-local reasoning |
| `failure_type` in `["test_failure","runtime_error","unknown"]` | +2 | Low-prior class |
| `blast_radius_estimate > 0.5` in call site | +1 | Wide impact |
| `retry_count` referenced in heal logic | +1 | Already failing |

Score >= 3 → LLM healing needed. Score < 3 → DETERMINISTIC.

Output: versioned JSON `artifacts/discovery/agent_reasoning_classification.json` with hash.

---

## Phase 1 — Production Invocation: Wire Real Providers

The `DefaultHealingProviderInvoker` stubs in `healing_tier_dispatcher.py` must be implemented.

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

```python
class DefaultHealingProviderInvoker:
    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        # Wire to SovereignLLMGateway with provider="qwen_vllm"
        # Enforce HealSeamBypassError if called outside @standard_heal
        # Log InvocationRecord to L4 outcome_sink

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        # Wire to SovereignLLMGateway with provider="google"
        # model=config.model_gemini_2_5_pro_id
        # temperature=0.0 (deterministic), replay_mode=True
```

**Constraint:** Both methods must emit `InvocationRecord` to `HealingOutcomeSink`. Already structured in dispatcher — just needs provider call wired in.

---

## Phase 2 — Fix apps_rg: Implement call_llm()

**File:** `agentic_core/mixins/mcp_operation_mixin.py`

```python
class MCPOperationMixin:
    async def call_llm(
        self,
        prompt: str,
        *,
        reasoning_class: ReasoningClass | None = None,
        trace_id: str | None = None,
    ) -> str:
        """Route to SovereignLLMGateway.route_generation(). No provider logic here."""
        # Does NOT call dispatch_healing() — this is production generation, not healing
        # Uses ReasoningClass to select tier from LLMRoutingPolicy
        # Enforces temperature=0.0 by default
        # Requires trace_id — generate from CIDRegistry if not provided
```

**Authority constraint:** `call_llm()` constructs only a typed request and delegates to gateway. It does NOT select model names or providers.

**Classification for apps_rg engines:**
- `BulletGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.LIGHT`
- `MessageGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC`

---

## Phase 3 — ReasoningClass Enum (Replaces String HIGH/LOW)

**New file:** `agentic_core/config/reasoning_class.py`

```python
class ReasoningClass(Enum):
    DETERMINISTIC = 0  # No LLM — deterministic rules only
    LIGHT = 1          # Qwen, temp=0 — fast generation/light healing
    STRATEGIC = 2      # Gemini-2.5-pro, temp=0 — complex reasoning
    ORCHESTRATOR = 3   # Gemini-2.5-pro, temp=0, higher token budget
    HEALER = 4         # Healing path only — routes through dispatch_healing()
```

**SovereignBaseAgent:**
```python
AGENT_REASONING_CLASS: ReasoningClass = ReasoningClass.DETERMINISTIC  # Conservative default
ALLOW_STOCHASTIC: bool = False  # Must be False unless L5-certified
```

**Gate:** If `ALLOW_STOCHASTIC=False` and `temperature > 0` anywhere — CI hard fail.

---

## Phase 4 — Generation Path (Separate from Healing)

Add `route_generation()` to `SovereignLLMGateway` as a **separate path** from `dispatch_healing()`.

```
Generation path (apps_rg, orchestrators):
  agent.call_llm(prompt)
    → MCPOperationMixin.call_llm()
    → SovereignLLMGateway.route_generation(ReasoningClass)
    → provider invoke (Qwen or Gemini, temp=0)
    → InvocationRecord emitted

Healing path (agentic_core healers):
  @standard_heal → decide_heal_escalation()
    → FailureSignal.to_healing_input()
    → dispatch_healing() [existing choke point]
    → route_healing_tier() [existing router]
    → DefaultHealingProviderInvoker [Phase 1 wires this]
```

These two paths MUST NOT cross. `dispatch_healing()` is NOT callable from generation agents.

---

## Phase 5 — Wire HealingTierConfig Hash into ReplayBundle

`ReplayBundle.active_config_hashes` already exists. Add healing config hash to it:

```python
active_config_hashes = {
    "healing_config": HealingTierConfig.content_hash(),   # ADD THIS
    "routing_policy": LLMRoutingPolicy.policy_hash(),     # ADD THIS
    ...existing entries...
}
```

This gives L4 cryptographic anchoring of the routing policy without inventing `InstructionPacket` or `VersionStore` (those don't exist).

---

## Phase 6 — Dynamic Thresholds from L4

`HealingTierConfig` currently uses hardcoded defaults. Wire to `_HISTORICAL_SUCCESS_RATES` (already in `healing_tier_router.py`) which is documented as "backed by L4 in production":

```python
def load_default_healing_tier_config() -> HealingTierConfig:
    # Read x/y thresholds from L4 state store instead of constants
    # _HISTORICAL_SUCCESS_RATES already structured for this
```

This satisfies the L6 meta-learning feedback loop without building OscillationDetector (which does not exist in the repo).

---

## Phase 7 — AST-Based CI Guards

**New file:** `ops_scripts/ci/check_llm_routing_compliance.py`

AST-based (not grep) checks:

```python
checks = [
    # Agents must declare AGENT_REASONING_CLASS
    "all_agents_have_reasoning_class",

    # Ban model string literals in agent files
    "no_model_literals_in_agents",      # "gemini-*", "qwen*", "gpt-*"

    # Ban direct llm_generate() outside LLMProviderMixin
    "no_direct_llm_generate_in_agents",

    # Ban temperature= keyword args outside gateway
    "no_temperature_kwarg_outside_gateway",

    # Ban provider imports (openai, anthropic, google.generativeai) in agents
    "no_provider_imports_in_agents",

    # Ban httpx/aiohttp in agent files
    "no_raw_http_clients_in_agents",

    # All dispatch_healing() calls must have trace_id
    "dispatch_healing_requires_trace_id",
]
```

---

## Implementation Sequence

**Critical ordering constraint: CI must be active before agent migration.**

1. Phase 0 — Run scan, produce `agent_reasoning_classification.json` with hash
2. Phase 3 — Add `ReasoningClass` enum (no agent changes yet)
3. Phase 7 — Deploy CI guards (catches any regression from Phase 4+)
4. Phase 1 — Wire real provider invocation in dispatcher stubs
5. Phase 2 — Implement `call_llm()` in `MCPOperationMixin`
6. Phase 4 — Add `route_generation()` to gateway
7. Phase 5 — Add config hashes to `ReplayBundle`
8. Phase 6 — Wire L4 dynamic thresholds
9. Apply `AGENT_REASONING_CLASS` classifications from Phase 0 scan

---

## Scope: Files to Change

| Phase | File | N |
|-------|------|---|
| 0 | New scan script (analysis only) | 1 |
| 1 | `healing_tier_dispatcher.py` | 1 |
| 2 | `mcp_operation_mixin.py` | 1 |
| 3 | New `reasoning_class.py`, `SovereignBaseAgent.py` | 2 |
| 4 | `SovereignLLMGateway.py` | 1 |
| 5 | `replay_bundle.py` | 1 |
| 6 | `healing_tier_config.py`, `healing_tier_router.py` | 2 |
| 7 | New CI script + workflow | 2 |
| Apply | ~30 agent files (classifications from scan) | ~30 |
| **Total** | | **~41** |

---

## What This Plan Explicitly Does NOT Build

These appear in the critique but do NOT exist in the repo — adding them is out of scope:

- `InstructionPacket` — not in codebase, aspirational
- `VersionStore` / `Activator` / `ApprovalGate` — not in codebase
- `OscillationDetector` / `DampeningValidators` — not in codebase
- HMAC signature on packets — not in codebase
- `ToolBudget(compute_ms, memory_mb)` — partial stub only

These belong to a future architectural phase, not this routing refactor.

---

## Success Criteria

1. Real LLM calls wired through `dispatch_healing()` (not stubs)
2. `call_llm()` functional in apps_rg engines
3. All agents classified with hashed artifact
4. `ReasoningClass` enum replaces string HIGH/LOW
5. Generation path separate from healing path
6. `HealingTierConfig` hash in `ReplayBundle.active_config_hashes`
7. CI blocks model literals, temperature kwargs, provider imports in agents
8. `FAILURE_CLASS_PRIORS` used as objective classification rubric

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

