# Qwen vLLM 14B Healing — Unified Plan (Routing Scorecard Hardening Merged)

Complete plan for (1) per-agent classification + diff report [DONE], and
(2) hardened deterministic->Qwen->Gemini routing with gateway monopoly,
anti-flap, audit logging, replay protection, and kill-switch enforcement.

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

## Implementation Phases

| Phase | Scope | Files | Deps |
|---|---|---|---|
| A | Complete — no action needed | — | — |
| B | Router hardening (5 targeted edits) | `agentic_core/L0_routing/scripts/execute_ssot.py` | — |
| C | Anti-flap module | `agentic_core/L2_execution/healers/routing_anti_flap.py` (new) | Phase B digest fields |
| D | Gateway monopoly CI | `ops_scripts/ci/check_gateway_monopoly.py` + `.github/workflows/gateway-monopoly-check.yml` (new) | — |
| E | Acceptance tests | `tests/agentic_core/L0_routing/test_routing_scorecard.py` (new) | Phases B + C |

**Total**: 1 edit + 4 new files. No existing agent source files modified.

---

## File Change Summary

| File | Action |
|---|---|
| `agentic_core/L0_routing/scripts/execute_ssot.py` | Edit — extend `RoutingDecision` with 6 audit fields; update `_decide()` digest formula; add B.4 overrides (OVERRIDE_TRIVIAL_DETERMINISTIC, OVERRIDE_DET_COV_PREFERRED); add replay guard in arbiter; add kill-switch post-gate |
| `agentic_core/L2_execution/healers/routing_anti_flap.py` | New — `failure_signature_hash`, anti-flap TTL cache, `check_anti_flap()` |
| `ops_scripts/ci/check_gateway_monopoly.py` | New — AST provider import scanner |
| `.github/workflows/gateway-monopoly-check.yml` | New — CI workflow (push/PR) |
| `tests/agentic_core/L0_routing/test_routing_scorecard.py` | New — H.1-H.8 acceptance tests |
