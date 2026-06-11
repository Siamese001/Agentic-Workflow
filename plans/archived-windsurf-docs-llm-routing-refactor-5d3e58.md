---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-refactor-5d3e58.md'
original_relative_path: 'llm-routing-refactor-5d3e58.md'
source_sha256: e5e16c1efc167f12a577f2580cd8aeca0a995213b9ed0a8208621206d0b281c3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing Consolidation: Single Canonical Path for All Agents

Consolidate the two conflicting LLM invocation patterns into one canonical design where high-intensity agents automatically route to Qwen or Gemini-2.5-pro via the tier router, and low-intensity agents skip LLM entirely.

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


## The Problem: Two Competing Patterns

### Pattern A — `@standard_heal` decorator (54 agents)
- Wired to the `L2.3 HealingTierRouter` which correctly routes: **LOCAL → Qwen → Gemini-2.5-pro**
- But **LLM is globally disabled** unless `HEAL_POLICY_MODEL_ESCALATION=1` is set
- The `_task_complexity` and `_confidence` inputs default to `5` and `0.75` — meaning nearly every call lands in the HIGH tier (no LLM) even when escalation is on

### Pattern B — direct `self.llm_generate()` (3 agents)
- Hardcoded model strings, no confidence gate, no retry logic, no tier routing
- Bypasses the entire `HealingTierRouter` / `dispatch_healing` infrastructure
- Inconsistent: `FissionManagerAgent` always calls gemini-2.5-pro; others call flash

### Pattern C — 43 agents with no LLM wiring at all
- Some should have LLM capability (they do complex reasoning), some legitimately don't need it

---

## Root Causes

1. **`HEAL_POLICY_MODEL_ESCALATION` is an all-or-nothing global flag** — no per-agent control
2. **`_task_complexity` defaults to 5**, which is the judicious gate threshold — LLM barely fires
3. **No concept of "agent reasoning intensity"** baked into the agent class — the decorator can't distinguish `FissionManagerAgent` from `BootstrapAgent`
4. **Direct callers bypass the router entirely** — no retry logic, no tier fallback, no auditability

---

## Recommended Final Design

### Single principle: ALL LLM calls go through `dispatch_healing()` in `healing_tier_dispatcher.py`

```
Agent.heal_repository() / heal() / direct reasoning
    └── @standard_heal  OR  HeaLCallMixin.call_llm()
            └── decide_heal_escalation()   ← policy gate
                    └── dispatch_healing()  ← SINGLE choke point
                            ├── LOCAL_AGENT   (confidence >= 0.75)
                            ├── QWEN_VLLM     (0.40 <= confidence < 0.75)
                            └── GEMINI_2_5_PRO (confidence < 0.40 OR retries >= max)
```

No agent ever calls `self.llm_generate()` directly for reasoning that should be tiered.

---

## Implementation Plan (5 steps)

### Step 1 — Add `AGENT_REASONING_CLASS` to `SovereignBaseAgent`

Add a class-level attribute that every agent can override. This replaces the global env flag for per-agent control.

```python
# SovereignBaseAgent
AGENT_REASONING_CLASS: str = "LOW"  # "LOW" | "HIGH"
```

- **HIGH agents** (FissionManager, CognitiveDisposition, StructuredEngine, + any L3 orchestrators, L5 threat agents): `task_complexity = 9`, `_confidence` from actual score
- **LOW agents** (BootstrapAgent, NamingAgent, simple validators, etc.): `task_complexity = 3`, stay deterministic

This feeds directly into `HealEscalationInputs.task_complexity` in `@standard_heal`, so no other code changes are needed for the routing logic itself.

**Files:** `agentic_core/base_agents/SovereignBaseAgent.py`

---

### Step 2 — Replace `HEAL_POLICY_MODEL_ESCALATION` global flag with per-class opt-in

Instead of one env var controlling all 97 agents, add:

```python
# decorators_util.py standard_heal wrapper
enable_llm = (
    _select_reasoning_tier_enabled()          # global override still works
    or getattr(self, "AGENT_REASONING_CLASS", "LOW") == "HIGH"
)
```

HIGH-class agents auto-enable LLM. LOW-class agents still require the env var (safe default).

**Files:** `agentic_core/utils/decorators_util.py`

---

### Step 3 — Migrate the 3 direct `llm_generate()` callers to `dispatch_healing()`

Replace ad-hoc `await self.llm_generate(provider="google", model=...)` calls with:

```python
# Before (FissionManagerAgent)
response = await self.llm_generate(prompt, provider="google",
    model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"), ...)

# After
from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing
from agentic_core.L2_execution.healers.healing_tier_types import HealingInput
healing_input = HealingInput(failure_type="orchestration_plan", ...)
decision, record = dispatch_healing(healing_input, config, agent_name=self.__class__.__name__)
```

This gives them retry logic, tier fallback, audit logging, and budget caps automatically.

**Files:**
- `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py`
- `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py`
- `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py`

---

### Step 4 — Mark the 43 "unwired" agents appropriately

Audit the 43 agents with no LLM wiring. Classify each:

| Category | Action | Estimate |
|----------|--------|----------|
| Simple rule-based agents (NamingAgent, BootstrapAgent, etc.) | Set `AGENT_REASONING_CLASS = "LOW"` explicitly, document as intentional | ~35 agents |
| Complex agents that should have LLM but don't (SystemArchitectAgent, GravityLeakRepairAgent, etc.) | Set `AGENT_REASONING_CLASS = "HIGH"` and add `@standard_heal` | ~8 agents |

**Files:** Individual agent files — no logic changes, just class attribute + decorator

---

### Step 5 — Add `AGENT_REASONING_CLASS` enforcement to CI

Add a lightweight AST-based CI check:

```python
# ops_scripts/ci/check_agent_reasoning_class.py
# Fails if any *Agent.py in L3/L5 is missing AGENT_REASONING_CLASS declaration
```

Prevents regression where new agents are added without explicitly choosing HIGH or LOW.

**Files:** `ops_scripts/ci/check_agent_reasoning_class.py`, `.github/workflows/`

---

## What Changes vs. What Stays the Same

| Component | Change |
|-----------|--------|
| `healing_tier_dispatcher.py` | **No change** — already correct |
| `healing_tier_router.py` | **No change** — already correct |
| `HealingTierConfig` | **No change** — thresholds stay |
| `@standard_heal` | Small change: Step 2 (per-class enable_llm) |
| `SovereignBaseAgent` | Small change: Step 1 (add class attribute) |
| 3 direct-LLM agents | Refactor: Step 3 (migrate to dispatch_healing) |
| 43 unwired agents | Classify only: Step 4 (attribute + optional decorator) |
| CI | New check: Step 5 |

---

## Non-Goals

- Do NOT change `HealingTierRouter` scoring weights
- Do NOT remove `HEAL_POLICY_MODEL_ESCALATION` env var (keep as global override)
- Do NOT wire the `HEALER_REGISTRY` (separate concern)
- Do NOT touch `apps_lic` or `apps_rg`

---

## Scope (N = files)

| Step | Files | N |
|------|-------|---|
| 1 | `SovereignBaseAgent.py` | 1 |
| 2 | `decorators_util.py` | 1 |
| 3 | `FissionManagerAgent.py`, `StructuredEngineAgent.py`, `CognitiveDispositionAgent.py` | 3 |
| 4 | ~43 agent files (attribute only, no logic) | ~43 |
| 5 | 1 CI script + 1 workflow | 2 |
| **Total** | | **~50** |

Step 4 is mechanical (single-line additions). Steps 1–3 are the only code-logic changes.

---

## Clarifying Questions

1. **Should HIGH agents always enable LLM**, or should it remain opt-in even for them (env var still required)?
2. **Step 3 scope**: Is `FissionManagerAgent` the only one that needs real LLM output back (not just a heal signal)? The `dispatch_healing()` path currently returns an `InvocationRecord`, not the LLM response body — the migration needs to wire the response back to the caller.
3. **Step 4**: Do you want to audit all 43 agents together in one PR, or only wire the ~8 that genuinely need HIGH reasoning?

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

