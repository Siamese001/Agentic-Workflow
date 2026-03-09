# Master Hardening Consolidation Plan

Synthesizes all 14 source plans, a live AST audit of `apps_rg`/`apps_lic`, a critical review of false-confidence failure modes, and a healing pathway unblock analysis into four execution phases: Phase 0 = architecture reality check; Phase 1 = agentic_core forensic/observability gaps (A–G); Phase 2 = apps_rg/apps_lic live audit results; Phase 3 = apps_rg/apps_lic gap fixes + healing pathway unblock.

---

## Critical Design Principle: "DONE" ≠ "Runtime Enforced"

All items marked complete are verified as committed code, NOT as runtime-enforced. Each Phase 1 gap fix must also produce a runtime invariant test + negative control + CI enforcement triple. Phase 0 validates all prior "DONE" claims.

---

## Already Complete (code exists — runtime enforcement unverified until Phase 0)

| Item | Evidence |
|------|----------|
| Silent swallowers phases 1-3 (19 fixes) | `silent_swallower_phases1-3_validation.md` |
| V15 SSOT entrypoint false FROZEN label | commit `ba302ef6d` |
| Semantic cache Redis hardening | `semantic-cache-redis-hardening-final.md` |
| Hybrid RAG/BM25 + ASTAwareTokenizer | commit `f9225f145` |
| Agentic RAG hardening | commit `474ff6447` |
| Meta-learning bus (`bus_consumer` + `healing_success_rate_store`) | commit `c9d54fa5d` |
| Evaluation & drift tracking | commit `0973a6498` |
| High-risk cross-cutting gaps | commit `0340a86b2` |
| AI-checking-AI Phase 1-8 + Phase 10 (AST CI) | commit `f0f9fc54c` |
| Qwen/Gemini `response_text` capture | both adapters capture `response_text` |
| Threshold SSOT (0.80/0.50) | `qwen_meta_learning.py` imports `healing_tier_config.py` |
| `policy_hash` from file | reads `v15_policy_pack.json` at runtime |
| Mutation ledger (`write_gateway.py`) | `set_mutation_ledger_path`, `_append_ledger_entry` implemented |
| `pre_validation.json` + `post_validation.json` called in heal path | lines 8291, 8339 of `execute_ssot.py` |
| Zero pytest skips | commit `73eafb144` |
| Redis → `pytest.fail` + CI workflow | commit `cbde2a287` |
| `apps_rg` and `apps_lic` in `SOVEREIGN_TERRITORIES` | `_constants.py` lines 925, 941 — both territories defined with full subfolder maps |

---

---

# PHASE 0 — Architecture Reality Check (Pre-Flight Gates)

**Run before any code changes. Unblocks Phases 1–3 with evidence, not assumptions.**

---

## Gate A — Runtime Enforcement Verification

Every "Already Complete" item must have a runtime invariant test + negative control + CI enforcement triple.

| Item | Invariant test | Negative control |
|------|---------------|-----------------|
| Semantic cache → Redis backend | `assert cache.backend.__class__.__name__ == "RedisCache"` | Disable Redis → assert `RuntimeError`, not silent LRU fallback |
| Meta-learning bus consumer drains bus | Publish 3 events → assert `store.get_rate()` updated | No-op consumer → assert `drain_and_apply` raises or logs `ERROR` |
| `response_text` captured in `InvocationRecord` | Invoke adapter → assert `record.response_text != ""` | Empty provider response → assert `ValueError` not silent empty string |
| Mutation ledger records writes | `write_text()` → assert ledger non-empty | Call without `set_mutation_ledger_path()` → assert ledger empty AND `ERROR` logged |
| Qwen threshold immutable | `assert HEALING_CONFIDENCE_X == 0.80` | Monkey-patch constant → assert `validate_threshold_immutability()` raises |

**New CI gate:** `tests/invariants/test_runtime_enforcement.py` — 5 invariant+negative pairs; never skippable.

---

## Gate B — Test Integrity Guardrail

"Zero pytest skips" is necessary but not sufficient. Silent failure modes:
- `try: ... except Exception: pass` inside test bodies
- Test functions with zero `assert` statements
- `@pytest.mark.xfail` without `strict=True`
- Fixtures that swallow import errors and return `None`

**New CI script:** `ops_scripts/ci/check_test_integrity.py` — AST-walk `tests/**/*.py`:
1. Flag `except` block in test body with no `raise` or `pytest.fail`
2. Flag test function with zero `assert` / `pytest.raises`
3. Flag `@pytest.mark.xfail` without `strict=True`
4. Hard-fail CI on any violation outside `# guardian: allow-...`

---

## Gate C — Architecture Drift Scan

### C1 — Landmine Triage (2257 baseline violations)

The `check_anti_patterns.py` baseline suppresses 2257 violations. Baseline-suppression = silent failure. Remediation tiers:
- **Tier 1 (fix before Phase 1):** `silent_swallower` in production paths not annotated `# guardian: allow-silent-swallower`
- **Tier 2 (fix within Phase 1/3):** `type_erasure`, `path_fragility` in L0-L3 layers
- **Tier 3 (document and defer):** `magic_configuration` with config source annotation

CI rule: **baseline may only shrink** — hard-fail if `landmine_baseline.txt` line count increases.
New artifact: `docs/reports/plans/landmine_triage_report.md`

### C2 — Gateway Bypass Scan

CI AST scan: flag `import google.generativeai`, direct `import openai`, direct `import anthropic` outside `# guardian: allow-direct-sdk`.
Known violation: `apps_rg/tools/ResumeGenerator.py:268` (fixed in Phase 3.1).

### C3 — Mutation Exclusivity Proof

CI scan for direct filesystem writes outside `write_gateway.py`: `open(..., "w")`, `Path.write_text()`, `Path.write_bytes()` in production code. Existing findings: `ToolsmithAgent.py`, `sovereign_healing_engine_enforcer.py`, `cst_healer_mixin.py` use `import requests/httpx/psycopg2` — classify in triage.

### C4 — Observability Liveness Guarantees

Every telemetry channel must emit on startup/check:
```python
def test_drift_detector_emits_on_check():
    detector = DriftDetector(inject_clock=FakeClock())
    detector.check(context_hash="abc123")
    assert detector.last_emission_timestamp is not None
```
New: `tests/invariants/test_observability_liveness.py`

### C5 — AI-Checking-AI Structural Risk

`confidence < 0.7` → `human_enqueued = True` in audit record; human-enqueued verdicts blocked from routing until reviewed. New: `HumanReviewQueue` stub in `agentic_core/L5_safety/audit/human_review_queue.py`. `JudgeEvaluator` must have deterministic pre-filter before LLM invocation.

---

---

# PHASE 1 — agentic_core Forensic & Observability Gaps (GAP-A through GAP-G)

*Each fix includes the Gate A triple: runtime invariant test + negative control + CI enforcement.*

---

## GAP-A — CRITICAL: `run_manifest.json` + `artifact_integrity.json` never emitted

**Fix:** Wire `_write_run_manifest_json()` at start + `_write_artifact_integrity_json()` as final step of `_run_heal_pipeline()`.
**Invariant:** `test_heal_produces_run_manifest()` — file exists with correct `trace_id`.
**Negative control:** Remove call → test fails immediately.

---

## GAP-B — CRITICAL: `set_mutation_ledger_path()` never called

**Fix:** Call `set_mutation_ledger_path(output_dir / "mutation_ledger.jsonl", trace_id)` at start of `_run_heal_pipeline()` before Phase 2 mutations.
**Invariant:** `test_heal_ledger_non_empty_on_commit_run()` — ledger non-empty after write.
**Negative control:** Pass `None` → ledger empty after write AND `ERROR` logged.

---

## GAP-C — HIGH: AI-check Unified Audit Trail (Phase 9) not implemented

**Fix:** `agentic_core/L5_safety/audit/ai_check_audit.py` (thread-safe JSONL emitter) + `human_review_queue.py` stub. Wire into 5 AI-check components. Schema: `{timestamp_utc, component, model_id, input_hash, verdict, confidence, human_enqueued, trace_id}`.
CI: zero entries with `confidence < 0.5 AND human_enqueued == false`.

---

## GAP-D — HIGH: apps_* output schema enforcement incomplete

*(Full enforcement via Phase 3.5 after Phase 2 audit.)*

---

## GAP-E — MEDIUM: `L4MetaPriorProvider` not wired into dispatcher

**Fix:** Create `system_learning/ports/l4_meta_prior_provider.py`; inject into `healing_tier_dispatcher._dispatch()`; sync bus → store after dispatch.
**Invariant:** Seeded store → routing selects `LOCAL_AGENT` for borderline input.

---

## GAP-F — MEDIUM: DriftRegistry unified timeline

**Fix:** Verify or create `drift_registry.py`; wire 3 drift sources; persist to `drift_timeline.jsonl`.

---

## GAP-G — MEDIUM: RAGAS-style metrics

**Fix:** Four deterministic metrics in `evaluation/metrics/`. Wire into `OfflineEvaluationRunner`.
**Invariant:** Identical inputs → identical scores across 3 calls.

---

---

# PHASE 2 — Live AST Audit: apps_rg and apps_lic Gap Analysis

*Gap register only — implementation in Phase 3.*

## apps_rg Gaps

| Gap | Severity | Finding |
|-----|----------|---------|
| **RG-GAP-01** | CRITICAL | `ResumeGenerator.py:268` — direct `google.generativeai` SDK, bypasses `SovereignLLMGateway` |
| **RG-GAP-02** | HIGH | `AllProvidersDownError.py:77` — `HardenedGeminiExecutor` not implemented; Google path silently skipped |
| **RG-GAP-03** | HIGH | `RgHealingOrchestrator.run()` fully stubbed — every cycle returns `{"status": "skipped"}` |
| **RG-GAP-04** | MEDIUM | `agent_executor_util.py` — `_execute_openai/anthropic/google` bypass `SovereignLLMGateway` |
| **RG-GAP-05** | MEDIUM | No `intent_delta`/`tool_requests`/`state_diff_proposal` output contract on reasoning agents |
| **RG-GAP-06** | LOW | No engine-level or reasoning-agent tests in `tests/unit/apps_rg/` |

## apps_lic Gaps

| Gap | Severity | Finding |
|-----|----------|---------|
| **LIC-GAP-01** | CRITICAL | `control_plane.py` 100% commented out — safety control plane non-functional |
| **LIC-GAP-02** | HIGH | All 9 HOP stage handlers in `hop_stage_registry.py` are stubs |
| **LIC-GAP-03** | HIGH | `GeminiLLMClient._MODEL = "gemini-pro"` — stale model ID |
| **LIC-GAP-04** | MEDIUM | No output contract on LIC reasoning agents |
| **LIC-GAP-05** | MEDIUM | `tests/unit/apps_lic/` does not exist |

---

---

# PHASE 3 — apps_rg and apps_lic Gap Fixes + Healing Pathway Unblock

---

## 3.0 — HEAL-UNBLOCK: Remove all artificial blockers from the healing pathway

When `--heal` is invoked, the healing pathway must activate across ALL SSOT-registered territories — including `apps_rg` and `apps_lic` — without artificial gates. Four blockers identified:

---

### HEAL-GAP-01 — CRITICAL: `load_agents()` never discovers apps_rg/apps_lic agents

**File:** `agentic_core/L0_routing/scripts/execute_ssot.py`

```python
# CURRENT (agents never discovered)
search_paths = [
    project_root / AGENTIC_CORE_DIR,
    # Add other apps_* folders if needed, e.g., apps_private  ← comment, not code
]

# FIX
search_paths = [
    project_root / AGENTIC_CORE_DIR,
    project_root / APPS_RG_DIR,
    project_root / APPS_LIC_DIR,
]
```

`apps_rg` and `apps_lic` ARE in `SOVEREIGN_TERRITORIES` and ARE in the territory sweep — but `load_agents()` only walks `agentic_core/`. Any healing agent in apps_rg/apps_lic is invisible to the discovery pipeline.

**Gate A triple:**
- `test_load_agents_discovers_apps_rg_agents()` — assert `"RgHealingOrchestrator"` or similar key exists in returned dict
- Negative control: revert `search_paths` to `[AGENTIC_CORE_DIR]` → assert apps_rg agents missing from dict

---

### HEAL-GAP-02 — HIGH: All apps_* `heal_repository()` default `dry_run=True` — no execution

**Files:** `apps_rg/engines/base_rg_engine.py:54`, `RgHealingOrchestrator.py:166`, `RgResumeOrchestrator.py:80`, `ProactiveAgent.py:95`, `ContentQualityAgent.py:246`, and all LIC equivalents.

Every apps_* `heal_repository(self, dry_run: bool = True, ...)` defaults to scan-only mode. The main pipeline does pass `dry_run=False, execute=True` when it calls known agents directly — but agents discovered via `load_agents()` are dispatched through `LegacyAgentAdapter` which also defaults to dry_run.

**Fix:** Change default signature to `dry_run: bool = False` in all apps_* `heal_repository()` methods to match the agentic_core convention. Document that the caller is responsible for passing `dry_run=True` when scan-only is desired.

**Gate A triple:**
- `test_rg_healing_orchestrator_default_not_dry_run()` — instantiate and assert `heal_repository.__defaults__` first arg is `False`
- Negative control: revert to `dry_run=True` default → test asserts fails → CI blocks

---

### HEAL-GAP-03 — HIGH: Toggle `else False` fallback disables `use_cyclic_validation` when toggles not injected

**File:** `apps_rg/engines/resume_orchestrator_engine.py:113-116`

```python
# CURRENT — disables cyclic validation when toggles not injected
use_cyclic = (
    self.toggles.use_cyclic_validation
    if self.toggles and hasattr(self.toggles, "use_cyclic_validation")
    else False    # ← wrong: config default is True, engine overrides to False
)

# FIX — read from config when toggles not injected
from apps_rg.config.reasoning_toggles_config import RGReasoningToggles
_defaults = RGReasoningToggles()
use_cyclic = (
    self.toggles.use_cyclic_validation
    if self.toggles and hasattr(self.toggles, "use_cyclic_validation")
    else _defaults.use_cyclic_validation   # True per config
)
```

Same pattern applies to `use_persistent_tracing`.

**Gate A triple:**
- `test_orchestrator_uses_cyclic_validation_without_toggles()` — instantiate with `toggles=None` → assert `use_cyclic == True`
- Negative control: reinstate `else False` → assert cyclic loop never executes → test detects regression

---

### HEAL-GAP-04 — HIGH: `LicHealingOrchestrator._execute_healing()` is a stub

**File:** `apps_lic/reasoning/LicHealingOrchestrator.py`

`_execute_healing()` logs the incident and returns `{"healed": True, ...}` unconditionally without performing any real remediation. No domain agent is invoked.

**Fix:** Wire `_execute_healing()` to dispatch to the domain-appropriate agent based on `incident.type`:
- Structural violations → `ControlPlane.evaluate_input/output()`
- Schema/output contract violations → `HOPPipelineExecutor` re-run on failing stage
- LLM call violations → re-route via `SovereignLLMGateway` with corrected model ID

**Gate A triple:**
- `test_lic_healing_orchestrator_executes_real_healing()` — inject incident with `type="structural"` → assert `ControlPlane.evaluate_input` called (mock)
- Negative control: stub `_execute_healing` to return empty dict → test asserts missing `healed` key

---

### Phase 3.0 Acceptance Criteria

- `python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal` with no `--territory` flag discovers and calls at least one apps_rg agent and one apps_lic agent
- `load_agents()` output dict contains at least `RgHealingOrchestrator` and `LicHealingOrchestrator` keys
- All apps_* `heal_repository.__defaults__[0] == False`
- `ResumeOrchestratorEngine` with `toggles=None` runs the cyclic validation loop
- `LicHealingOrchestrator._execute_healing()` invokes a domain agent (not stub)

---

## 3.1 — Fix RG-GAP-01: Replace direct Gemini SDK call

Replace `_generate_with_gemini()` in `ResumeGenerator.py` with `SovereignLLMGateway` delegation. Fix legacy `runtime.shared` namespace import.
**Gate A:** `test_resume_generator_uses_gateway()` — assert no `google.generativeai` import; CI AST scan hard-fails on restoration.

---

## 3.2 — Fix RG-GAP-02: Wire `HardenedGeminiExecutor`

Create `apps_rg/engines/hardened_gemini_executor.py`. Wire into `HardenedRouter._initialize_executors()` for `Provider.GOOGLE`.
**Gate A:** `test_hardened_router_google_executor_present()` — assert key exists; negative: remove → `AllProvidersDownError`.

---

## 3.3 — Fix RG-GAP-03: Implement minimal `HealingCycle`

`HealingCycle.execute(strategy) -> {converged, passed_agents, failed_agents, rollback_triggered}`. Wire `RgReflectionAgent.execute()` replacing `pass`.
**Gate A:** `test_rg_healing_orchestrator_runs_cycle()` — seeded converging context → `success=True`; negative: stub returns `{}` → `KeyError` not silent.

---

## 3.4 — Fix RG-GAP-04: Route `AgentExecutor` through `SovereignLLMGateway`

Replace `_execute_openai/anthropic/google` in `agent_executor_util.py` with `_execute_via_gateway()`. Retain Instructor path only for structured output.
**Gate A:** Mock `SovereignLLMGateway.route_generation` → assert called; negative: bypass → mock not called.

---

## 3.5 — Fix RG-GAP-05 + LIC-GAP-04: Output contract scanner + schema

Create `apps_shared/types/reasoning_output.py` with frozen `ReasoningOutput(intent_delta, tool_requests, state_diff_proposal)`. Extend `check_apps_output_contract.py` to flag missing schema in reasoning agents.

---

## 3.6 — Fix LIC-GAP-01: Activate control plane via `GovernanceShieldAgent`

Rewrite `apps_lic/engines/control_plane.py` (active, not commented). `ControlPlane.evaluate_input/output()` delegates to `GovernanceShieldAgent.evaluate()`. Wire into `LicSpineAdapter` before/after `ExecutionOrchestrator.execute()`.
**Gate A:** `test_control_plane_evaluate_input_active()` — PII content → `PolicyAction != ALLOW`; negative: comment class → `ImportError` in `LicSpineAdapter`.

---

## 3.7 — Fix LIC-GAP-02: Implement HOP5, HOP6, HOP7 domain logic

HOP5 (generation → `OutreachMessageAgent`), HOP6 (validation chain), HOP7 (gate decision). Remaining stages in follow-on PR.
**Gate A:** `test_hop5_returns_message_body()` — result has non-empty `"message_body"`; negative: stub empty dict → assertion fires.

---

## 3.8 — Fix LIC-GAP-03: Update `GeminiLLMClient` model ID

```python
from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
_MODEL: str = HealingTierConfig().model_gemini_2_5_pro_id   # "gemini-2.5-pro"
```
**Gate A:** `test_gemini_llm_client_model_id()` — assert `_MODEL == "gemini-2.5-pro"`; negative: hardcode `"gemini-pro"` → fails.

---

## 3.9 — Baseline test suites

New files (zero skips, all assertions present):
- `tests/unit/apps_rg/reasoning/test_rg_healing_orchestrator.py`
- `tests/unit/apps_rg/tools/test_resume_generator_gateway.py`
- `tests/unit/apps_lic/reasoning/test_hop_pipeline_executor.py`
- `tests/unit/apps_lic/engines/test_control_plane.py`
- `tests/unit/apps_lic/tools/test_gemini_llm_client_model_id.py`

---

## Phase 3 Execution Order

| Step | What | Priority |
|------|------|----------|
| **3.0 / HEAL-GAP-01** | Add apps_rg/apps_lic to `load_agents()` search paths | CRITICAL |
| **3.0 / HEAL-GAP-02** | Flip `dry_run` default to `False` in all apps_* agents | HIGH |
| **3.0 / HEAL-GAP-03** | Fix toggle `else False` fallback | HIGH |
| **3.0 / HEAL-GAP-04** | Wire `_execute_healing()` to domain agents | HIGH |
| **3.8** | Model ID fix (1-liner) | QUICK WIN |
| **3.1** | Direct SDK → gateway | CRITICAL |
| **3.6** | control_plane rewrite | CRITICAL |
| **3.2** | `HardenedGeminiExecutor` | HIGH |
| **3.7** | HOP5/6/7 domain logic | HIGH |
| **3.4** | `AgentExecutor` → gateway | MEDIUM |
| **3.3** | `HealingCycle` implementation | HIGH |
| **3.5** | Output contract scanner | MEDIUM |
| **3.9** | Test suites | LOW |

---

## Global Acceptance Criteria

- `execute_ssot_entrypoint --heal` produces all 7 artifacts; `mutation_ledger.jsonl` non-empty; all share `trace_id`
- `load_agents()` discovers agents from `apps_rg` and `apps_lic`
- `grep -r "google.generativeai" apps_rg/` → zero results (CI enforced)
- `RgHealingOrchestrator.run()` returns `success=True` on seeded converging context
- `ControlPlane.evaluate_input(pii_content)` returns non-ALLOW `PolicyDecision`
- HOP5 stage returns non-empty `message_body`
- `GeminiLLMClient._MODEL == "gemini-2.5-pro"`
- All apps_* `heal_repository.__defaults__[0] == False`
- `ResumeOrchestratorEngine(toggles=None)` runs cyclic validation loop
- `check_apps_output_contract.py` exits 0 with 3-field schema check
- All 5 new test files pass: zero skips, zero assertion-less tests
- `check_test_integrity.py` exits 0 (Gate B)
- `landmine_baseline.txt` line count does not increase (Gate C1)

---

## Hard Constraints

- All LLM calls via `SovereignLLMGateway` — no direct SDK imports
- All writes via `write_gateway.py` — no direct `open(..., "w")` in production paths
- `ensure_ascii=True` on all JSONL output
- No wall-clock timestamps in determinism-sensitive paths (inject `now_iso`)
- Zero `pytest.skip()` / `pytest.importorskip()` in new or modified tests
- Zero assertion-less test functions (Gate B enforced)
- Baseline may only shrink (Gate C1 enforced)
- Plans saved to `docs/reports/plans/` only
