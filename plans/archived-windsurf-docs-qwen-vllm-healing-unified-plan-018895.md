---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\qwen-vllm-healing-unified-plan-018895.md'
original_relative_path: 'qwen-vllm-healing-unified-plan-018895.md'
source_sha256: aa5ef562501a7cb19d804d17a4122ba27b5cb96121d3dc437c978967ef66e676
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Qwen vLLM 14B Healing — Unified Plan v2 (L2 Four-Phase Decomposition Added)

Extends the routing scorecard hardening plan with a mandatory four-phase (pre-commit / validation / execution / healing) refactor for every L2 execution agent, mirroring the pattern already established in `execute_ssot.py` for its 10 L5 agents.

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


## Status Snapshot

| Component | State |
|---|---|
| Per-agent classification report | **DONE** — `docs/reports/plans/qwen_vllm_healing_recommendations.md` |
| `generate_qwen_healing_report.py` | **DONE** — `ops_scripts/general/` |
| `FailureType` / `RoutingTier` enums | **DONE** — `execute_ssot.py` ~L501 |
| `RoutingInputs` / `RoutingDecision` dataclasses | **DONE** — `execute_ssot.py` |
| `compute_routing_decision()` pure function | **DONE** — `execute_ssot.py` ~L613 |
| `_get_qwen_vllm_arbiter()` WSL subprocess seam | **DONE** — `execute_ssot.py` |
| `_route_decision()` factor derivation bridge | **DONE** — `execute_ssot.py` |
| BMG cosine path (`BMG_EMBEDDINGS_ENABLED`) | **DONE** — `execute_ssot.py` + `healing_tier_config.py` |
| `healing_tier_router.py` (X/Y band) | **DONE** — `L2_execution/healers/` |
| `qwen_vllm_inference.py` (WSL subprocess worker) | **DONE** — `L2_execution/healers/` |
| **Gateway monopoly AST CI scan** | **MISSING** |
| **`failure_signature_hash` anti-flap** | **MISSING** |
| **`RoutingDecision` full audit fields** | **PARTIAL** — missing `score_raw`, `score_effective`, `override_applied`, `failure_signature_hash`, `router_version_hash` |
| **Replay mode blocks live inference in arbiter** | **MISSING** — GATE_0_REPLAY routes DET but arbiter subprocess call is unguarded |
| **Tier kill-switches (`QWEN_ENABLED` / `GEMINI_ENABLED`)** | **PARTIAL** — `QWEN_VLLM_ENABLED` startup check exists; `GEMINI_ENABLED` missing; no post-routing gate |
| **Hard overrides B.4** (trivial-det; det-cov preferred) | **MISSING** |
| **Routing acceptance tests H.1-H.8** | **MISSING** |
| **L2 agent four-phase decomposition** | **MISSING** — all 7 L2 agents lack explicit phase structure |

---

## Confirmed Parameters

| Parameter | Value |
|---|---|
| vLLM endpoint | `http://localhost:8000/v1` (running, OpenAI-compat) |
| WSL inference worker | `/home/amita/venvs/vllm/bin/python qwen_vllm_inference.py` |
| Model | `Qwen2.5-14B-Instruct-AWQ` (RTX 5090) |
| BMG index | `canon-healing-patterns` (dim=1536, cosine) |
| GPU cost | **OUT OF SCOPE** |

---

## Part 1 — Agent Classification (Complete)

**186 agents** scanned — 67 QWEN_VLLM / 118 DETERMINISTIC / 1 HYBRID / 51 BMG.
Report: `docs/reports/plans/qwen_vllm_healing_recommendations.md` (209 KB, 4169 lines).
Generator: `ops_scripts/general/generate_qwen_healing_report.py`.

Classification criteria unchanged — see report for full tables and diffs.

**Use Qwen vLLM 14B when ANY of:**
1. `heal()`/`execute()`/`act()` requires semantic judgment on prose or intent
2. Agent generates free-form content (docstrings, test bodies, messages, resume sections)
3. Multi-file cross-cutting repair needs contextual understanding
4. Novel/ambiguous violations not reducible to a fixed rule set
5. Agent performs strategy selection or reflection across past outcomes

**Keep Deterministic when ALL of:**
1. Violation is structurally enumerable (path match, AST node)
2. Repair is a fixed action (file move, import fix, counter increment)
3. Safety-critical path requiring auditability (PII, pre-commit, credential)
4. Output is a scalar/boolean

**Add BMG (`canon-healing-patterns`)** when past healing pattern recall is core,
or agent already connects to Pinecone/EmbeddingSovereignAgent/DeepBrainHarvester.

---

## Part 2 — Routing Scorecard Hardening

### A. Architectural Invariants (Non-Negotiable)

**A.1 Gateway Monopoly**
- `compute_routing_decision()` returns **symbolic** `model_id` only (already true).
- `_get_qwen_vllm_arbiter()` and `healing_provider_adapters.py` are the ONLY approved
  seams that bind symbolic model_id to a concrete provider call.
- Any direct `vllm` / `openai` / `google.generativeai` import **outside** allowlisted
  files = **HARD FAIL** (AST CI scan — Phase D).
- Allowlist: `L2_execution/healers/qwen_vllm_inference.py`,
  `L2_execution/healers/healing_provider_adapters.py`, `tests/**`.

**A.2 Externalized vLLM Boundary**
- vLLM runs as separate WSL process (already implemented via subprocess).
- Replay mode MUST deny the subprocess call — arbiter must raise before `subprocess.run()`.

**A.3 Control-Plane Determinism**
- Determinism = routing decisions + artifacts + logs. Not identical token streams.
- Digest must bind: `chosen_tier`, symbolic `model_id`, `score_effective`, `gate_applied`,
  `override_applied`, `failure_signature_hash`, `router_version_hash`.
- Timestamps excluded from digest; allowed as non-digest audit fields.

---

### B. Routing Scorecard

#### B.0 Pre-Gates — already implemented in `compute_routing_decision()`

| Gate | Condition | Route | Impl |
|---|---|---|---|
| GATE_0_REPLAY | `replay_mode=True` | DETERMINISTIC | Done (arbiter enforcement gap — see E) |
| GATE_1_RETRY | `retry_count >= 3` | Gemini/fail-closed | Done |
| GATE_2a | `structural_class AND det_cov` | DETERMINISTIC | Done |
| GATE_2b | `structural_class AND NOT det_cov` | Gemini/fail-closed | Done |
| GATE_3_MECH | `B=3, A=0, C<=1, playbook, det_cov` | DETERMINISTIC | Done |

#### B.1 Score Inputs (0-3 each; embeddings are informational-only / C0)

- C = Complexity, B = Blast-radius, A = Ambiguity/Autonomy-risk
- N = Novelty, F = Failure-cost, L = Latency (tie-breaker only)
- P = playbook_match (bool), D = deterministic_coverage (bool)

#### B.2 Score Formula — already implemented

```
S  = 3C + 4B + 3A + 2N + 4F
S' = max(0, S - 4)  if playbook_match else S
```

#### B.3 Thresholds — already implemented

```
S' <= 13        -> DETERMINISTIC
14 <= S' <= 26  -> Qwen
S' >= 27        -> Gemini
```

#### B.4 Hard Overrides — PARTIAL (two missing)

Currently implemented: `(B=3 OR F=3) AND (C>=2 OR A>=1)` -> Gemini; latency tie-breaker.

**Missing — add after threshold routing, before latency tie-breaker:**

1. `C=0 AND A=0 AND B<=1 AND F<=1` -> force DETERMINISTIC
   Gate name: `OVERRIDE_TRIVIAL_DETERMINISTIC`
   Rationale: trivially simple change — no LLM value-add.

2. `det_cov=True AND A<=1 AND C<=1` AND `tier_raw==QWEN` -> prefer DETERMINISTIC
   Gate name: `OVERRIDE_DET_COV_PREFERRED`
   Skip if `structural_class=True` (already handled by Gate 2a).

#### B.5 Qwen-Disallowed Classes — already complete in `_QWEN_DISALLOWED`

```
{IMPORT_BOUNDARY_VIOLATION, LAYER_VIOLATION, GATEWAY_BYPASS,
 SIGNATURE_VERIFY, DETERMINISM_DIGEST, POLICY_HASH,
 SCANNER_CI_GUARD, UNSIGNED_INGRESS, KILL_SWITCH_BYPASS,
 SCHEMA_REQUIRED_FIELDS_MISSING}
```

These always route DETERMINISTIC (if det_cov) or Gemini (if not), never Qwen.

---

### C. Escalation Dampening / Anti-Flap — MISSING

**New module**: `agentic_core/L2_execution/healers/routing_anti_flap.py`

**`failure_signature_hash` definition:**
```
SHA256(
    failure_type
    + "|" + "|".join(sorted(affected_paths))
    + "|" + stack_excerpt[:200]
    + "|" + "|".join(sorted(governance_surface_tags))
)[:16]
```
- Stable across retries for same logical failure.
- Excludes: timestamps, PIDs, memory addresses.

**Rules:**
1. Per `(trace_id, failure_signature_hash)` — Qwen max 2 attempts:
   - attempt 1 -> QWEN allowed
   - attempt 2 -> QWEN allowed
   - attempt 3+ -> force GEMINI (`ANTI_FLAP_ESCALATION`)
2. After Gemini escalation: 10-min cooldown blocks Qwen re-entry for same
   `failure_signature_hash`.
3. Gate 1 (`retry_count >= 3`) covers the global hard override independently.

**Storage**: in-process TTL dict. Redis is an optional future seam for multi-process.
**Integration**: called by `_route_decision()` in `execute_ssot.py` after Gate 1,
before Gate 2.

---

### D. `RoutingDecision` Audit Record — PARTIAL (extend existing dataclass)

**Add fields to existing `RoutingDecision`:**
```python
score_raw: int = 0
score_effective: int = 0
override_applied: str = ""
failure_signature_hash: str = ""
router_version_hash: str = ""
trace_id: str = ""
```

**Update `_decide()` inner function digest formula:**
```
SHA256(
    tier | model_id | score_effective | gate_applied | override_applied
    | failure_signature_hash | router_version_hash
)[:16]
```
Timestamp excluded from digest; allowed in `as_log_line()` as non-digest field.

**`_ROUTER_VERSION_HASH`** = module-level constant, computed once at import:
```python
import hashlib, inspect
_ROUTER_VERSION_HASH = hashlib.sha256(
    inspect.getsource(compute_routing_decision).encode()
).hexdigest()[:16]
```

**Full `RouteDecision` log record fields (bound into determinism digest):**
```
trace_id, failure_signature_hash, replay_mode, failure_type,
factors: {C,B,A,N,F,L,playbook_match,deterministic_coverage,structural_class},
score_raw, score_effective, gate_applied, override_applied,
chosen_tier, chosen_model_id (symbolic), retry_count,
timestamp (non-digest field only)
```

---

### E. Replay Mode Enforcement in Arbiter — MISSING

`GATE_0_REPLAY` routes to DETERMINISTIC but `_get_qwen_vllm_arbiter()` does not
check `replay_mode` before calling `subprocess.run()`.

**Add to inner `_arbiter()` function inside `_get_qwen_vllm_arbiter()`:**
```python
def _arbiter(agent_name, confidence, violation_types, territory,
             *, replay_mode=False):
    if replay_mode:
        raise RuntimeError(
            "REPLAY_MODE: live Qwen inference blocked. "
            "Provide transcripted response or deterministic stub."
        )
    # ... existing subprocess.run() call unchanged ...
```
Apply the same guard to any Gemini invocation path in `healing_provider_adapters.py`.

---

### F. Kill-Switch Hardening — PARTIAL

Currently: `QWEN_VLLM_ENABLED` startup check in `validate_qwen_startup_state()`.
Missing: `GEMINI_ENABLED`; no post-routing gate that logs the decision.

**Add post-routing kill-switch gate inside `compute_routing_decision()`,
after all pre-gates + threshold + overrides, before `_decide()`:**
```python
def _qwen_enabled() -> bool:
    import os; return os.getenv("QWEN_ENABLED", "true").lower() == "true"

def _gemini_enabled() -> bool:
    import os; return os.getenv("GEMINI_ENABLED", "true").lower() == "true"

if tier_raw == RoutingTier.QWEN and not _qwen_enabled():
    tier_raw = (RoutingTier.GEMINI
                if not inputs.provider_prohibited_gemini
                else RoutingTier.FAIL_CLOSED)
    gate_raw = "KILL_SWITCH_QWEN_DISABLED"

if tier_raw == RoutingTier.GEMINI and not _gemini_enabled():
    tier_raw = RoutingTier.FAIL_CLOSED
    gate_raw = "KILL_SWITCH_GEMINI_DISABLED"
```
Silent fallback is **forbidden** — `gate_applied` in `RoutingDecision` must reflect
the kill-switch gate name.

---

### G. Gateway Monopoly AST CI Scan — MISSING

**New script**: `ops_scripts/ci/check_gateway_monopoly.py`

Algorithm (AST-based, no regex):
1. Walk `.py` files under `agentic_core/`, `apps_lic/`, `apps_rg/`,
   `apps_shared/`, `system_learning/`, `tools/`.
2. `ast.parse()` each file; inspect all `Import` and `ImportFrom` nodes.
3. Flag imports of provider modules: `vllm`, `openai`, `google.generativeai`,
   `anthropic`.
4. **Allowlist** (exact repo-relative paths):
   - `agentic_core/L2_execution/healers/qwen_vllm_inference.py`
   - `agentic_core/L2_execution/healers/healing_provider_adapters.py`
   - All paths under `tests/`
5. Violation -> print `FAIL: <file>:<line> direct provider import outside gateway seam`
   -> `sys.exit(1)`.

**New workflow**: `.github/workflows/gateway-monopoly-check.yml`
Triggers on push/PR to any branch.

---

### H. Acceptance Tests — MISSING

**New file**: `tests/agentic_core/L0_routing/test_routing_scorecard.py`

All cases call `compute_routing_decision()` directly (pure function, no mocking).
Anti-flap tests use in-process TTL cache with no external side-effects.

```
H.1 Pre-Gates
  structural + det_cov -> DETERMINISTIC (GATE_2_STRUCTURAL_DET_COV)
  structural + no det_cov + gemini_ok -> GEMINI
  structural + no det_cov + gemini_prohibited -> FAIL_CLOSED
  replay_mode=True -> DETERMINISTIC (GATE_0_REPLAY)
  retry_count=3 -> GEMINI/FAIL_CLOSED (GATE_1_RETRY_OVERRIDE)
  B=3, A=0, C=1, playbook, det_cov -> DETERMINISTIC (GATE_3_CRITICAL_SURFACE_MECH)

H.2 Qwen-Disallowed Classes (parametrized over _QWEN_DISALLOWED members)
  tier != QWEN for all disallowed failure types
  det_cov=True -> DETERMINISTIC; det_cov=False -> GEMINI/FAIL_CLOSED

H.3 Score + Thresholds
  S_eff 0,13 -> DET;  S_eff 14,26 -> QWEN;  S_eff 27,max -> GEMINI
  playbook dampener: S=17 + playbook -> S_eff=13 -> DET

H.4 Hard Overrides B.4
  C=0, A=0, B=1, F=1 -> DETERMINISTIC (OVERRIDE_TRIVIAL_DETERMINISTIC)
  det_cov=True, A=1, C=1, S_eff=20 -> DETERMINISTIC (OVERRIDE_DET_COV_PREFERRED)

H.5 Anti-Flap
  Same (trace_id, sig_hash): attempt 1->QWEN, 2->QWEN, 3->GEMINI (ANTI_FLAP_ESCALATION)
  Post-escalation cooldown: Qwen re-entry blocked within cooldown window

H.6 Determinism Binding
  Two identical RoutingInputs -> identical determinism_digest
  Digest contains tier, model_id, score_effective, failure_signature_hash (not timestamp)
  Changing any digest field -> digest changes

H.7 Kill-Switches
  QWEN_ENABLED=false + score->Qwen -> GEMINI or FAIL_CLOSED (not silent)
  gate_applied contains "KILL_SWITCH_QWEN_DISABLED"
  GEMINI_ENABLED=false + Gemini required -> FAIL_CLOSED + "KILL_SWITCH_GEMINI_DISABLED"

H.8 Gateway Monopoly (static)
  check_gateway_monopoly.py: import vllm in non-allowlisted file -> exit(1)
  import vllm in qwen_vllm_inference.py -> exit(0) (allowlisted)
```

---

## Implementation Phases (Updated)

| Phase | Scope | Files | Deps |
|---|---|---|---|
| A | Complete | — | — |
| B | Router hardening | `execute_ssot.py` (1 edit) | — |
| C | Anti-flap module | `routing_anti_flap.py` (new) | Phase B |
| D | Gateway monopoly CI | `check_gateway_monopoly.py` + workflow (2 new) | — |
| E | Routing acceptance tests | `test_routing_scorecard.py` (new) | Phases B + C |
| F | L2 four-phase refactor | 7 agent edits | Phase B (`_route_decision`) |
| G | L2 phase acceptance tests | `test_l2_agent_phases.py` (new) | Phase F |

**Total**: 8 edits + 5 new files. No L5/L0/apps_* agent source files modified.

---

## Part 3 — L2 Execution Agent Four-Phase Decomposition

### Reference Pattern (from `execute_ssot.py` L5 agents)

`execute_ssot.py` runs its 10 L5 agents across four named phases per territory:

| Phase | Function | Role |
|---|---|---|
| 1 — Discovery | `execute_phase1_discovery()` | Scan / detect violations; no writes |
| 2 — Reconciliation | `execute_phase2_reconciliation()` | Write / apply fixes; gated by decision engine |
| 3 — Validation | `execute_phase3_validation()` / `execute_phase3_architectural_validation()` | Post-heal AST checks; produces remaining-violations |
| 4 — Healing | `execute_phase4_healing()` | Governor + deeper repair on residual violations |

The same four phases must be implemented in every L2 execution agent's `heal_repository()` as explicit, named internal methods. This makes the healing lifecycle uniform, testable, and routeable via the SSOT scorecard.

---

### Phase Contract per Agent

Each L2 agent must expose (as methods or documented internal blocks):

```
pre_commit_checks(self) -> list[str]
    - Pure read-only validation before any state change
    - Checks: env keys, connectivity, config invariants, API key presence
    - Returns: list of error strings (empty = pass)
    - Routing: DETERMINISTIC always (no LLM)
    - Must NOT write files, update indexes, or mutate state

validate(self, dry_run=True) -> dict[str, int]
    - Full scan: detect all violations/misconfigurations
    - Returns: {violations: N, warnings: N}
    - Routing: DETERMINISTIC (structural) or Qwen (semantic content check)
    - Populates self._pending_violations for execution phase
    - Must NOT apply fixes

execute(self, ctx: HealContext) -> dict[str, int]
    - Apply fixes for violations found in validate()
    - Gated by AutonomousDecisionEngine.should_proceed_with_healing()
    - Routing decision logged via _route_decision() -> RoutingDecision
    - Returns: {fixed: N, errors: N, skipped: N}
    - Writes only via UniversalWriteGateway / write_gateway seam

heal(self, violation: dict) -> dict
    - Handle a single residual violation post-execution
    - Called by Phase 4 governor for any unfixed items from execute()
    - Routing: per violation failure_type via compute_routing_decision()
    - Returns canonical dict: {status, details, artifacts, errors}
```

`heal_repository()` becomes the orchestrator that calls these four methods in order,
with the decision engine gating execution and healing phases.

---

### L2 Agent Breakdown

#### `EmbeddingSovereignAgent`
**Current state**: `heal_repository()` is a flat monolith; `heal()` returns `skipped`.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert `GOOGLE_API_KEY`, `OPENAI_API_KEY` present; assert Redis reachable (ping); assert `EXPECTED_DIMENSIONS` config valid |
| **validation** | Scan each configured provider: dimension mismatch check, cache round-trip test; return `{violations: N}` |
| **execution** | Fix cache key prefix collisions if detected; re-initialize `_bge_m3_model` if stale; log `RoutingDecision` (DETERMINISTIC for config fixes, QWEN for semantic embedding policy review) |
| **healing** | Handle `EMBEDDING_DIM_MISMATCH`, `PROVIDER_UNREACHABLE`, `CACHE_MISS_RATE_EXCEEDED` violation types; route via `compute_routing_decision()` |

**Routing tier**: DETERMINISTIC (config/env) / QWEN (embedding policy advice)

---

#### `PineconeSovereignAgent`
**Current state**: Has rich scan logic; `heal_repository()` not shown — likely flat.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert `PINECONE_API_KEY`; assert index `canon-healing-patterns` exists and is ready (status=`Ready`); assert dimension=1536; assert cloud/region match env |
| **validation** | Check index stats (vector count vs expected floor); verify namespace existence; validate metadata schema on sample vectors |
| **execution** | Re-create index if missing (with gate: B=3 / high blast-radius → Gemini required); upsert missing namespace; fix metadata schema drift |
| **healing** | Handle `INDEX_NOT_FOUND`, `DIMENSION_MISMATCH`, `NAMESPACE_MISSING`, `VECTOR_COUNT_BELOW_FLOOR`; structural index ops = DETERMINISTIC; semantic schema repair = Qwen |

**Routing tier**: DETERMINISTIC (index ops) / QWEN (schema/metadata repair) / GEMINI (index recreation)

---

#### `RedisSovereignAgent`
**Current state**: Singleton with `operation_stats`; `heal_repository()` via `@standard_heal`.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert Redis connection pool healthy (ping); assert `REDIS_URL` / `REDIS_PASSWORD` present; assert TTL policy config valid |
| **validation** | Scan: connection pool exhaustion check; key expiry drift; memory ceiling check; `operation_stats` anomaly detection (hit-rate < threshold) |
| **execution** | Flush stale keys (TTL policy); rebuild connection pool if exhausted; reset `operation_stats` counters with audit log entry |
| **healing** | Handle `CONNECTION_POOL_EXHAUSTED`, `KEY_TTL_DRIFT`, `MEMORY_CEILING_EXCEEDED`; all DETERMINISTIC (numeric thresholds, no LLM value-add) |

**Routing tier**: DETERMINISTIC throughout (structural/numeric only)

> Note: `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` is a shim that delegates to `L4_state.reasoning.RedisSovereignAgent`. The four phases above apply to the canonical L4 version. The L2 shim must expose the same `pre_commit_checks()` / `validate()` / `execute()` / `heal()` interface and delegate.

---

#### `SovereignMCPGatewayAgent`
**Current state**: Singleton; `heal_repository()` not implemented (raises or absent).

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert MCP servers reachable (llm_route, kg, archive); assert connection pool not exhausted; assert `audit_log` rotation working |
| **validation** | Check `operation_stats["errors"]` rate; detect stale connections; validate LLM routing fallback chain integrity |
| **execution** | Reset error counters; evict stale pool connections; re-validate fallback model availability |
| **healing** | Handle `LLM_ROUTE_FAILURE`, `KG_QUERY_TIMEOUT`, `ARCHIVE_OP_FAILED`; DETERMINISTIC for connection resets; Qwen for LLM routing policy advice |

**Routing tier**: DETERMINISTIC (ops) / QWEN (routing policy)

---

#### `StructuredEngineAgent`
**Current state**: Only `generate_plan()` + stub `heal_repository()` that raises `NotImplementedError`.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert `GEMINI_MODEL` env var set; assert gateway seam (`SovereignLLMGateway`) importable; assert no direct provider import (AST self-check) |
| **validation** | Validate that `generate_plan()` output conforms to `AgentPlan` schema; detect empty `tool_calls` from last N runs |
| **execution** | Re-configure model if `GEMINI_MODEL` changed; purge invalid cached plans; log routing decision (QWEN for plan quality review) |
| **healing** | Handle `PLAN_SCHEMA_INVALID`, `EMPTY_TOOL_CALLS`, `GATEWAY_IMPORT_VIOLATION`; plan schema = Qwen; import violation = DETERMINISTIC |

**Routing tier**: QWEN (plan content) / DETERMINISTIC (config/import)

---

#### `SubAtomicRegistryAgent`
**Current state**: Rich AST scanner and registry; `heal_repository()` via `@standard_heal`.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert all entries in `UNIFIED_AGENT_MAPPING` are importable; assert no circular imports in mapped agents (AST cycle check); assert registry index file exists |
| **validation** | Scan: stale registry entries (class moved/renamed); missing `heal()` method on registered agents; duplicate canonical keys |
| **execution** | Remove stale entries; update moved class paths; write updated registry JSON via `write_gateway` |
| **healing** | Handle `STALE_REGISTRY_ENTRY`, `MISSING_HEAL_METHOD`, `DUPLICATE_KEY`, `CIRCULAR_IMPORT`; structural fixes = DETERMINISTIC; semantic dedup = Qwen |

**Routing tier**: DETERMINISTIC (path/key fixes) / QWEN (semantic dedup of near-duplicate agents)

---

#### `ToolsmithAgent`
**Current state**: `heal_repository()` partially wired; seeds territory content; has `save_tool()`.

| Phase | What to implement |
|---|---|
| **pre-commit** | Assert `generated_tools/` directory writable; assert `write_gateway` importable; assert no `tool_spec` JSON schema violations in `tools/` |
| **validation** | Scan all registered `ToolSpec` for schema compliance; detect orphaned tool Python files (no matching spec); detect specs without implementations |
| **execution** | Write missing tool Python files via `save_tool()`; remove orphaned files; seed ghost territories via `seed_territory()` |
| **healing** | Handle `TOOL_SCHEMA_INVALID`, `ORPHANED_TOOL_FILE`, `MISSING_IMPLEMENTATION`, `GHOST_TERRITORY`; QWEN for generating missing implementations; DETERMINISTIC for file cleanup |

**Routing tier**: QWEN (tool code generation) / DETERMINISTIC (file ops, schema validation)

---

### Shared Implementation Pattern

All seven agents must follow this `heal_repository()` skeleton:

```python
def heal_repository(self, dry_run=True, execute=False,
                    depth=0, max_depth=3, _call_path=None) -> dict:
    # --- Cycle / depth guard (unchanged) ---
    ...

    # PHASE 1: PRE-COMMIT
    pre_errors = self.pre_commit_checks()
    if pre_errors:
        return {"errors": len(pre_errors), "pre_commit_failed": True,
                "messages": pre_errors}

    # PHASE 2: VALIDATION
    scan = self.validate(dry_run=True)
    if scan["violations"] == 0:
        return {"violations": 0, "fixed": 0, "errors": 0}

    if dry_run and not execute:
        return scan  # scan-only mode

    # PHASE 3: EXECUTION (gated by routing decision)
    ctx = HealContext(heal=execute, dry_run=dry_run, ...)
    result = self.execute(ctx)

    # PHASE 4: HEALING (residual violations)
    for v in self._pending_violations:
        if v not in result["fixed_violations"]:
            self.heal(v)

    return {**scan, **result}
```

---

### Routing Decision Integration per Phase

| Phase | Routing | Rationale |
|---|---|---|
| pre-commit | Always DETERMINISTIC | Pure env/config assertions — no LLM value |
| validation | DETERMINISTIC for structural; QWEN for semantic content checks | Schema presence is structural; content quality is semantic |
| execution | Per `_route_decision()` using violation's `FailureType` | Scorecard decides; kill-switches enforced here |
| healing | Per `compute_routing_decision(RoutingInputs(...))` for each violation | Each residual violation gets an independent scorecard decision |

---

### Acceptance Tests for L2 Phase Decomposition

**New file**: `tests/agentic_core/L2_execution/test_l2_agent_phases.py`

```
P.1 pre_commit_checks() — missing env var returns non-empty error list (each agent)
P.2 validate() — returns {violations: N} with no side effects (each agent, dry_run=True)
P.3 execute() with dry_run=True — returns scan result, no writes (each agent)
P.4 execute() with execute=True — applies exactly the fixes found in validate() (each agent)
P.5 heal() — each documented violation type returns canonical {status, details, artifacts, errors}
P.6 Routing decision logged — execute() emits RoutingDecision log line per violation
P.7 Pre-commit gate blocks execution — if pre_commit_checks() fails, heal_repository()
    returns early without calling validate() or execute()
P.8 Phase isolation — validate() called independently does not mutate agent state
```

---

## File Change Summary

| File | Action |
|---|---|
| `agentic_core/L0_routing/scripts/execute_ssot.py` | Edit — extend `RoutingDecision`; B.4 overrides; replay guard; kill-switch gate |
| `agentic_core/L2_execution/healers/routing_anti_flap.py` | New — anti-flap TTL cache |
| `ops_scripts/ci/check_gateway_monopoly.py` | New — AST provider import scanner |
| `.github/workflows/gateway-monopoly-check.yml` | New — CI workflow |
| `tests/agentic_core/L0_routing/test_routing_scorecard.py` | New — H.1-H.8 routing tests |
| `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | Edit — four phases |
| `agentic_core/L2_execution/reasoning/ToolsmithAgent.py` | Edit — four phases |
| `tests/agentic_core/L2_execution/test_l2_agent_phases.py` | New — P.1-P.8 phase tests |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

