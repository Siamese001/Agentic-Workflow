# Master Hardening Consolidation Plan

Synthesizes all 14 source plans, a live AST audit of `apps_rg`/`apps_lic`, and a critical review of false-confidence failure modes into four execution phases: Phase 0 = architecture reality check before anything else; Phase 1 = agentic_core forensic/observability gaps (A–G); Phase 2 = apps_rg/apps_lic live audit results; Phase 3 = apps_rg/apps_lic gap fixes.

---

## Critical Design Principle: "DONE" ≠ "Runtime Enforced"

**All items marked complete below are verified as committed code.** They are NOT verified as runtime-enforced. Each Phase 1 gap fix must also produce a runtime invariant test + negative control + CI enforcement triple. Phase 0 is the pre-flight that validates all prior "DONE" claims.

---

## Already Complete (code exists in repo — runtime enforcement unverified until Phase 0)

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

---

---

# PHASE 0 — Architecture Reality Check (Pre-Flight Gates)

**Run before any code changes. Unblocks Phases 1–3 with evidence, not assumptions.**

---

## Gate A — Runtime Enforcement Verification

Every item in the "Already Complete" table must have a corresponding runtime invariant test that:
1. Exercises the live code path (not just imports)
2. Has a **negative control**: tamper the condition and assert the system **fails hard**, not silently

Priority list (highest risk of dead wiring first):

| Item | Invariant test | Negative control |
|------|---------------|-----------------|
| Semantic cache → Redis backend | `assert cache.backend.__class__.__name__ == "RedisCache"` | Disable Redis → assert `pytest.fail` or `RuntimeError`, not silent fallback to LRU |
| Meta-learning bus consumer drains bus | Publish 3 events → assert `store.get_rate()` updated | Monkey-patch consumer as no-op → assert `drain_and_apply` raises or logs `ERROR` |
| `response_text` captured in `InvocationRecord` | Invoke adapter → assert `record.response_text != ""` | Patch provider to return empty string → assert `InvocationRecord.response_text == ""` triggers `ValueError` |
| Mutation ledger records writes | Call `write_text()` → assert ledger file non-empty | Call `write_text()` without calling `set_mutation_ledger_path()` first → assert ledger is empty AND an `ERROR` log fires |
| Qwen threshold immutable | `assert HEALING_CONFIDENCE_X == 0.80` | Monkey-patch the constant → assert `validate_threshold_immutability()` raises `AssertionError` |

**New CI gate:** `tests/invariants/test_runtime_enforcement.py` — all 5 invariant+negative pairs above. This file must never be skipped.

---

## Gate B — Test Integrity Guardrail

"Zero pytest skips" is necessary but not sufficient. The following patterns hide failures silently:

- `try: ... except Exception: pass` inside test bodies
- Test functions that return without any `assert` statement
- `@pytest.mark.xfail` without `strict=True`
- Fixtures that swallow import errors and return `None`

**New CI script:** `ops_scripts/ci/check_test_integrity.py`

AST-walk all `tests/**/*.py`:
1. Flag any `except` block inside a test function body that has no `raise` and no `pytest.fail`
2. Flag any test function whose body contains zero `assert` statements and no `pytest.raises` context
3. Flag any `@pytest.mark.xfail` without `strict=True`
4. Hard-fail CI if any violations found outside a `# guardian: allow-...` whitelist

**Acceptance:** `python ops_scripts/ci/check_test_integrity.py` exits 0 on clean run.

---

## Gate C — Architecture Drift Scan

Architecture diagrams and layer documentation must match runtime wiring. Current risk: the codebase has 2257 baseline-suppressed anti-pattern violations (source: `ops_scripts/hooks/landmine_baseline.txt`). **Baseline-suppressing violations is the same failure mode as baseline-ignoring test skips** — it hides real problems.

### C1 — Landmine Triage (the 2257)

The current `check_anti_patterns.py` baseline approach allows 2257 violations to exist silently. This must change:

1. Run `python ops_scripts/ci/check_anti_patterns.py` with `--write-baseline` disabled
2. Generate a **classified triage report** grouping violations by: `silent_swallower`, `type_erasure`, `path_fragility`, `magic_configuration`
3. For each category, define a remediation tier:
   - **Tier 1 (fix immediately):** `silent_swallower` in production code paths (not `# guardian: allow-silent-swallower`)
   - **Tier 2 (fix within Phase 1/3):** `type_erasure`, `path_fragility` in L0-L3 layers
   - **Tier 3 (document and defer):** `magic_configuration` with config source annotation
4. Shrink the baseline by Tier 1 violations before Phase 1 begins
5. CI rule: baseline may only shrink, never grow (enforce via `wc -l` comparison in CI)

**New file:** `docs/reports/plans/landmine_triage_report.md` — category × file × line table

### C2 — Gateway Bypass Scan

AST scan for LLM provider calls outside `SovereignLLMGateway`:

**New CI script:** `ops_scripts/ci/check_llm_sdk_imports.py` (may already exist — verify)
- Patterns to flag: `import google.generativeai`, `import openai` (direct), `import anthropic` (direct)
- Exception: files with `# guardian: allow-direct-sdk` annotation
- Hard-fail CI if any new violations outside annotation

**Current known violation:** `apps_rg/tools/ResumeGenerator.py:268` (fixed in Phase 3.1)

### C3 — Mutation Exclusivity Proof

UWG (`write_gateway.py`) must be the **sole mutation broker**. Any direct filesystem write outside it is an untracked mutation.

**New CI script:** `ops_scripts/ci/check_layer_write_sovereignty.py` (may already exist — verify and extend)

Patterns to flag in production code (not tests, not scripts):
- `open(... "w")` / `open(... "wb")` / `Path(...).write_text()` / `Path(...).write_bytes()` outside `write_gateway.py`
- `import requests` / `import httpx` outside designated network boundary files
- `import psycopg2` / `import sqlalchemy` outside designated DB boundary

**Findings so far:** 3 files use `import requests/httpx/psycopg2`: `ToolsmithAgent.py`, `sovereign_healing_engine_enforcer.py`, `cst_healer_mixin.py` — classify and address in triage.

### C4 — Observability Liveness Guarantees

The architecture depends on L6 telemetry, evaluation spine, and meta-learning bus signals. If any of these fail silently, routing decisions degrade invisibly.

**Required:** Every telemetry channel must emit a structured heartbeat event on startup/periodic interval.

**New invariant tests** in `tests/invariants/test_observability_liveness.py`:
```python
def test_drift_detector_emits_on_check():
    detector = DriftDetector(inject_clock=FakeClock())
    detector.check(context_hash="abc123")
    assert detector.last_emission_timestamp is not None

def test_retrieval_drift_monitor_emits_snapshot():
    monitor = RetrievalDriftMonitor()
    monitor.check_alerts()
    assert monitor.last_snapshot_timestamp is not None
```

CI: missing telemetry emission → test failure, not silent pass.

### C5 — AI-Checking-AI Structural Risk

The current AI-checking-AI design has `JudgeEvaluator`, `ReflectionEngine`, `ConstitutionalReviewerAgent` all producing verdicts that feed back into routing. **This is AI verifying AI** — a structural risk where model bias can self-reinforce.

**Required hardening:**
1. Any AI-check verdict with `confidence < 0.7` must set `human_enqueued = True` in the audit record
2. Human-enqueued verdicts must NOT feed back into routing until reviewed
3. Add a `HumanReviewQueue` stub in `agentic_core/L5_safety/audit/human_review_queue.py` with `enqueue(record)` and `pending_count()` methods
4. CI assertion: `pending_count() > 50` → CI warning (not hard fail, but visible)
5. `JudgeEvaluator` must have a deterministic pre-filter before LLM invocation that blocks structurally invalid inputs without calling the model at all

---

---

# PHASE 1 — agentic_core Forensic & Observability Gaps (GAP-A through GAP-G)

**Each fix must also produce the Gate A triple: runtime invariant test + negative control + CI enforcement.**

---

## GAP-A — CRITICAL: `run_manifest.json` and `artifact_integrity.json` never emitted

`_write_run_manifest_json()` and `_write_artifact_integrity_json()` defined but never called in heal pipeline.

**Fix:** Wire both calls in `_run_heal_pipeline()` — manifest at start, integrity as final step.

**Runtime invariant:** `test_heal_produces_run_manifest()` — assert file exists with correct `trace_id`.
**Negative control:** Comment out the call → test fails immediately.

---

## GAP-B — CRITICAL: `set_mutation_ledger_path()` never called in heal pipeline

`_MUTATION_LEDGER_PATH` is `None` throughout every heal run — all ledger appends are no-ops.

**Fix:** Call `set_mutation_ledger_path(output_dir / "mutation_ledger.jsonl", trace_id)` at start of `_run_heal_pipeline()` before Phase 2.

**Runtime invariant:** `test_heal_ledger_non_empty_on_commit_run()` — after a heal run that writes at least one file, assert `mutation_ledger.jsonl` line count > 0.
**Negative control:** Call `set_mutation_ledger_path(None)` → assert ledger file empty after write → Gate A fires.

---

## GAP-C — HIGH: AI-check Unified Audit Trail (Phase 9) not implemented

`agentic_core/L5_safety/audit/` directory does not exist.

**Fix:**
- `ai_check_audit.py` — thread-safe singleton JSONL emitter
- Schema: `{timestamp_utc, component, model_id, input_hash, verdict, confidence, human_enqueued, trace_id}`
- `human_review_queue.py` — stub queue for low-confidence verdicts (`confidence < 0.7`)
- Wire into 5 AI-check components + emit `human_enqueued=True` when below threshold
- CI: assert zero entries with `confidence < 0.5 AND human_enqueued == false`
- Guardian test: `tests/guardian/test_ai_check_audit_schema.py`

---

## GAP-D — HIGH: apps_* output schema enforcement not verified

`check_apps_output_contract.py` only enforces `AGENT_ID` — does not enforce `{intent_delta, tool_requests, state_diff_proposal}`.

*(Full fix is in Phase 3.5 after the live audit in Phase 2.)*

---

## GAP-E — MEDIUM: `L4MetaPriorProvider` not wired into dispatcher

Dispatcher defaults `meta_prior_provider=None` — historical success-rate data invisible to routing.

**Fix:** Create `system_learning/ports/l4_meta_prior_provider.py`; lazy-inject into `healing_tier_dispatcher._dispatch()`; sync bus → store after dispatch.

**Runtime invariant:** Seed store with `syntax_error` rate=0.95 → assert routing selects `LOCAL_AGENT` for borderline confidence input.
**Negative control:** Remove injection → assert routing selects `GEMINI` (neutral prior wins) → test detects regression.

---

## GAP-F — MEDIUM: DriftRegistry unified timeline unverified

Three siloed drift systems may not feed a single `DriftRegistry`.

**Fix:** Verify or create `agentic_core/L6_observability/engines/drift_registry.py`; wire all 3 sources; persist to `L4_state/stores/drift_timeline.jsonl`.

**Observability liveness:** Covered by Phase 0 Gate C4 invariant tests.

---

## GAP-G — MEDIUM: RAGAS-style metrics unverified

Four deterministic metrics needed in `agentic_core/evaluation/metrics/`.

**Fix:** `FaithfulnessMetric`, `AnswerRelevancyMetric`, `ContextPrecisionMetric`, `GroundednessMetric` — all deterministic (cosine/precision@k, no LLM). Wire into `OfflineEvaluationRunner`.

**Invariant:** Identical inputs → identical scores across 3 calls (determinism test).

---

### Phase 1 Acceptance Criteria

- `execute_ssot --heal` produces all 7 artifacts; all share same `trace_id`; `mutation_ledger.jsonl` non-empty
- `agentic_core/L5_safety/audit/` exists; guardian test passes; `human_review_queue.py` stub present
- `L4MetaPriorProvider` routing test passes with seeded data
- `DriftRegistry.query()` returns entries from all 3 sources
- All 4 RAGAS metrics produce deterministic scores
- `tests/invariants/test_runtime_enforcement.py` passes (all 5 Gate A invariant+negative pairs)

---

---

# PHASE 2 — Live AST Audit: apps_rg and apps_lic Gap Analysis

*Results of the live code walkthrough. Implementation is in Phase 3.*

---

## apps_rg Gaps

### RG-GAP-01 — CRITICAL: Direct Gemini SDK call in `ResumeGenerator`
**File:** `apps_rg/tools/ResumeGenerator.py:268`
```python
import google.generativeai as genai
model = genai.GenerativeModel("gemini-1.5-flash")  # bypasses SovereignLLMGateway
```
Also imports from `runtime.shared.multi_provider_clients` (legacy namespace).

### RG-GAP-02 — HIGH: `HardenedGeminiExecutor` not implemented; Google path silently skipped
**File:** `apps_rg/types/AllProvidersDownError.py:77-79`
`HardenedRouter._initialize_executors()` logs a warning for Google and skips executor creation — all Gemini calls via the router have no hardened executor.

### RG-GAP-03 — HIGH: `RgHealingOrchestrator.run()` entirely stubbed
**File:** `apps_rg/reasoning/RgHealingOrchestrator.py`
Every cycle returns `{"status": "skipped", "reason": "HealingCycle not implemented"}`. `SignalRouterAgent` commented out. `RgReflectionAgent` execution is `pass`. Orchestrator always emits `success=False`.

### RG-GAP-04 — MEDIUM: `AgentExecutor` routes LLM calls via `Provider` abstraction, not `SovereignLLMGateway`
**File:** `apps_rg/utils/agent_executor_util.py`
`_execute_openai`, `_execute_anthropic`, `_execute_google` dispatch directly via `apps_shared.Provider.get_client()` — bypassing gateway audit logging, `allowed_models` enforcement, and circuit breakers.

### RG-GAP-05 — MEDIUM: No output contract on reasoning agents
No `intent_delta`, `tool_requests`, `state_diff_proposal` in any `apps_rg/reasoning/` return value.

### RG-GAP-06 — LOW: Near-zero test coverage for reasoning agents
`tests/unit/apps_rg/engines/` contains only a `utils/` subdirectory — no engine-level or reasoning-agent tests.

---

## apps_lic Gaps

### LIC-GAP-01 — CRITICAL: `control_plane.py` entirely commented out (LEGACY)
**File:** `apps_lic/engines/control_plane.py`
The safety control plane (PII scrubbing, bias detection, constitutional review) is 100% commented out with no active replacement. All LIC messages skip input/output safety evaluation.

### LIC-GAP-02 — HIGH: All 9 HOP stage handlers are stubs
**File:** `apps_lic/engines/hop_stage_registry.py`
Every stage returns `{"stage": N, "status": "processed", "context": context}` — no actual domain logic for profile analysis, generation, validation, or gate decision.

### LIC-GAP-03 — HIGH: `GeminiLLMClient._MODEL = "gemini-pro"` — stale model ID
**File:** `apps_lic/tools/GeminiLLMClient.py:13`
Client correctly delegates to `SovereignLLMGateway` but uses wrong model string.

### LIC-GAP-04 — MEDIUM: No output contract on reasoning agents
Same as RG-GAP-05 for LIC domain.

### LIC-GAP-05 — MEDIUM: Zero test coverage
`tests/unit/apps_lic/` does not exist.

---

---

# PHASE 3 — apps_rg and apps_lic Gap Fixes

---

## 3.1 — Fix RG-GAP-01: Replace direct Gemini SDK call in `ResumeGenerator`

Replace `_generate_with_gemini()` with `SovereignLLMGateway` delegation (same pattern as `GeminiLLMClient`). Fix legacy import namespace.

**Gate A triple:** `test_resume_generator_uses_gateway()` asserts no `google.generativeai` import at module level; negative control: restore direct import → import-time AST check in CI fails.

---

## 3.2 — Fix RG-GAP-02: Wire `HardenedGeminiExecutor` into `HardenedRouter`

Create `apps_rg/engines/hardened_gemini_executor.py` wrapping `SovereignLLMGateway`. Wire into `HardenedRouter._initialize_executors()` for `Provider.GOOGLE`.

**Gate A triple:** `test_hardened_router_google_executor_present()` asserts `Provider.GOOGLE` key exists in `router.executors`; negative control: remove wiring → router raises `AllProvidersDownError` for Google tier.

---

## 3.3 — Fix RG-GAP-03: Implement minimal `HealingCycle` and wire `RgReflectionAgent`

Implement `HealingCycle.execute(strategy) -> dict` with `{converged, passed_agents, failed_agents, rollback_triggered}`. Wire `RgReflectionAgent.execute()` instead of `pass`.

**Gate A triple:** `test_rg_healing_orchestrator_runs_cycle()` asserts `result["success"]` on seeded converging context; negative control: stub `HealingCycle` to return empty dict → orchestrator raises `KeyError`, not silent `success=False`.

---

## 3.4 — Fix RG-GAP-04: Route `AgentExecutor` through `SovereignLLMGateway`

Replace direct provider dispatch in `agent_executor_util.py` with a single `_execute_via_gateway()` using `GenerationRequest`. Retain Instructor structured-output path as a special case only.

**Gate A triple:** `test_agent_executor_routes_via_gateway()` mocks `SovereignLLMGateway.route_generation` and asserts it is called; negative control: bypass gateway → mock not called → assertion fires.

---

## 3.5 — Fix RG-GAP-05 + LIC-GAP-04: Implement and enforce output contract

Create `apps_shared/types/reasoning_output.py` with frozen `ReasoningOutput(intent_delta, tool_requests, state_diff_proposal)`. Extend `check_apps_output_contract.py` to flag reasoning agents not returning this schema. Update agents incrementally.

---

## 3.6 — Fix LIC-GAP-01: Activate control plane via `GovernanceShieldAgent`

Rewrite `apps_lic/engines/control_plane.py` (active, not commented) with minimal `ControlPlane` delegating to `GovernanceShieldAgent.evaluate()`. Wire into `LicSpineAdapter` before/after `ExecutionOrchestrator.execute()`.

**Gate A triple:** `test_control_plane_evaluate_input_active()` asserts `ControlPlane().evaluate_input(pii_text)` returns `PolicyDecision` with `action != ALLOW`; negative control: comment out class → `ImportError` in `LicSpineAdapter` → CI fails at import time.

---

## 3.7 — Fix LIC-GAP-02: Implement real logic for HOP5, HOP6, HOP7

Priority order: HOP5 (generation → `OutreachMessageAgent`), HOP6 (validation chain), HOP7 (gate decision). Remaining stages in follow-on PR.

**Gate A triple per stage:** `test_hop5_returns_message_body()` asserts result contains `"message_body"` key with non-empty string; negative control: stub returns empty dict → assertion fires.

---

## 3.8 — Fix LIC-GAP-03: Update `GeminiLLMClient` model ID

```python
from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
_MODEL: str = HealingTierConfig().model_gemini_2_5_pro_id   # "gemini-2.5-pro"
```

**Gate A triple:** `test_gemini_llm_client_model_id()` asserts `GeminiLLMClient._MODEL == "gemini-2.5-pro"`; negative control: hardcode `"gemini-pro"` → assertion fails.

---

## 3.9 — Fix RG-GAP-06 + LIC-GAP-05: Baseline test suites

New test files (zero skips, each with at least one assertion):
- `tests/unit/apps_rg/reasoning/test_rg_healing_orchestrator.py`
- `tests/unit/apps_rg/tools/test_resume_generator_gateway.py`
- `tests/unit/apps_lic/reasoning/test_hop_pipeline_executor.py`
- `tests/unit/apps_lic/engines/test_control_plane.py`
- `tests/unit/apps_lic/tools/test_gemini_llm_client_model_id.py`

---

## Phase 3 Execution Order

| Step | Gap | Priority | Risk |
|------|-----|----------|------|
| 3.8 | LIC-GAP-03 (1-line model ID) | QUICK WIN | Zero |
| 3.1 | RG-GAP-01 (direct SDK → gateway) | CRITICAL | Low |
| 3.6 | LIC-GAP-01 (control_plane active) | CRITICAL | Medium |
| 3.2 | RG-GAP-02 (HardenedGeminiExecutor) | HIGH | Low |
| 3.7 | LIC-GAP-02 (HOP5/6/7 stages) | HIGH | Medium |
| 3.4 | RG-GAP-04 (AgentExecutor → gateway) | MEDIUM | Medium |
| 3.3 | RG-GAP-03 (HealingCycle implementation) | HIGH | High |
| 3.5 | Output contract scanner + schema | MEDIUM | Low |
| 3.9 | Test suites | LOW | Zero |

---

## Phase 3 Acceptance Criteria

- `grep -r "google.generativeai" apps_rg/` → zero results (CI enforced)
- `HardenedRouter` creates `HardenedGeminiExecutor` for `Provider.GOOGLE`
- `RgHealingOrchestrator.run()` returns `success=True` on seeded converging context
- `ControlPlane.evaluate_input(pii_content)` returns non-ALLOW `PolicyDecision`
- HOP5 stage returns message body (calls `OutreachMessageAgent`)
- `GeminiLLMClient._MODEL == "gemini-2.5-pro"`
- `check_apps_output_contract.py` exits 0 with extended 3-field schema check
- All 5 new test files pass with zero skips, zero assertion-less tests

---

## Hard Constraints (all phases)

- All LLM calls via `SovereignLLMGateway` — no direct `openai`, `anthropic`, `google.generativeai` SDK usage
- All writes via `write_gateway.py` — no direct `open(..., "w")` or `Path.write_text()` in production paths
- `ensure_ascii=True` on all JSONL output
- No wall-clock timestamps in determinism-sensitive paths (inject `now_iso`)
- Zero `pytest.skip()` / `pytest.importorskip()` in new or modified tests
- Zero assertion-less test functions (enforced by Gate B scanner)
- Baseline may only shrink: CI hard-fails if `landmine_baseline.txt` line count increases
- Plans saved to `docs/reports/plans/` only
