# C0 Policy Rectification — Single Authoritative Contract Path

**Status**: Not Started  
**Notion Page**: https://www.notion.so/c0-policy-rectification-f7b2a9-35a27693f55c81b3aaebcf61b7661395  
**Created**: 2026-05-08

---

## 1. Goal

Rectify the C0 run/bypass decision path so there is exactly one authoritative contract path and no duplicated or hardcoded C0 eligibility logic.

---

## 2. Architectural Decision

| Layer | Authority | Responsibility |
|-------|-----------|----------------|
| **L1** | Advisory | Declare semantic grounding need (advisory fields only) |
| **L0** | **Frozen Authority** | Freeze C0 policy into `RouteContract.c0_policy` |
| **C0** | Obedience | Obey `RouteContract.c0_policy`, perform only eligibility checks |
| **R4/L3/Entrypoints** | None | No hardcoded C0 bypass decisions |
| **PA** | Enforcement | Require `FinalEvidenceContract` or explicit `C0BypassReceipt` |

**Key Constraints**:
- Do NOT make L1 the sole runtime authority
- Do NOT let route-name prefixes decide C0 behavior
- Do NOT let R4 bypass C0 by hardcoded reason strings
- Do NOT create a parallel C0 decision mechanism

---

## 3. Target Shape

### 3.1 RouteContract.c0_policy Field

```python
@dataclass(frozen=True)
class C0Policy:
    grounding_required: bool
    c0_mode: Literal[
        "RETRIEVE_REQUIRED",
        "BYPASS_PRELOADED_CONTEXT",
        "BYPASS_CACHE_RETURN",
        "BYPASS_FALLBACK",
        "NOT_REQUIRED",
    ]
    decision_source: Literal[
        "L1_PLAN_DERIVED",
        "L0_ROUTE_TOPOLOGY",
        "CACHE_TERMINAL",
        "FALLBACK_TERMINAL",
        "PRELOADED_CONTEXT",
    ]
    evidence_contract_required: bool
    bypass_reason: str | None = None
    preloaded_context_ref: str | None = None
    support_target: str | None = None
```

Add to `RouteContract`:
```python
c0_policy: C0Policy | None = None
```

---

## 4. Refactor L1 C0 Preflight Logic

**File**: `agentic_core/L1_cognition/c0_context/preflight.py`

**Current Issues**:
- Emits runtime C0 eligibility decisions
- Whitelists route IDs (`R3_GROUNDED`, etc.)
- Decides whether C0 may run

**Changes**:
1. Rename semantics to advisory grounding analysis
2. Remove runtime preflight behavior
3. Remove route ID whitelisting
4. Emit only advisory fields:
   - `grounding_required` (L1 opinion)
   - `support_expectation`
   - `support_target`
   - `grounding_reason_codes`

**Constraint**: L1 must NOT decide whether C0 may run.

---

## 5. Refactor L0 C0 Policy Construction

**File**: `agentic_core/L0_routing/c0_retrieval/preflight.py` (or new L0 policy builder)

**Responsibilities**:
1. Consume `L1PlanContract.grounding_required` and selected route topology
2. Emit exactly one `RouteContract` with `c0_policy` populated
3. Route IDs can inform policy construction, but downstream C0 must not inspect route-name prefixes

**Mapping**:

| Route Topology | L1 grounding_required | c0_mode | decision_source |
|----------------|----------------------|---------|-----------------|
| R1_* cache | any | BYPASS_CACHE_RETURN | CACHE_TERMINAL |
| R5_* fallback | any | BYPASS_FALLBACK | FALLBACK_TERMINAL |
| R4_SINGLE_ACTION | False | BYPASS_PRELOADED_CONTEXT | PRELOADED_CONTEXT |
| R4_SINGLE_ACTION | True | RETRIEVE_REQUIRED | L1_PLAN_DERIVED |
| R3R4_MANAGED | varies | per-step policy | L0_ROUTE_TOPOLOGY |

**Replace** checks like:
```python
if route.route_id.startswith("R1_") or route.route_id.startswith("R5_"):
```

With explicit:
```python
if route.c0_policy.c0_mode in ("BYPASS_CACHE_RETURN", "BYPASS_FALLBACK"):
```

---

## 6. Refactor C0 Preflight

**File**: `agentic_core/L0_routing/c0_retrieval/preflight.py` (C0.0 preflight)

**Changes**:
1. Read only `RouteContract.c0_policy` plus C0-owned eligibility inputs:
   - ACL/source scope
   - Source availability
   - Freshness
   - Budget
   - Origin trust
   - Graph permission

2. Do NOT recompute semantic need from L1
3. Do NOT inspect route-name prefixes to decide bypass
4. Emit:
   - `C0PreflightStatus` when retrieval is required
   - `C0BypassReceipt` when `c0_mode` is an allowed bypass mode

5. If `c0_mode=RETRIEVE_REQUIRED` and C0 cannot run, emit evidence gap or blocked preflight status, NOT a fake bypass.

---

## 7. Fix R4 Entrypoint Hardcoded Bypass

**File**: `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`

**Current Issue**:
```python
c0_receipt = build_c0_bypass_receipt(
    ...
    c0_bypass_reason="GROUNDING_NOT_REQUIRED",  # ← Hardcoded
)
```

**Changes**:
1. Remove hardcoded `c0_bypass_reason="GROUNDING_NOT_REQUIRED"`
2. Replace with `RouteContract.c0_policy`-driven behavior
3. If R4 uses preloaded context, bypass reason must be:
   ```python
   c0_mode="BYPASS_PRELOADED_CONTEXT"
   preloaded_context_ref="<ref>"
   ```
4. If R4 requires argument grounding, it must allow C0 retrieval before L2
5. R4 route type alone must NEVER imply grounding is unnecessary

---

## 8. Fix L3 Managed Workflow Behavior

**Requirement**: L3 step contracts must carry inherited or step-specific `c0_policy`

**Changes**:
1. Managed workflow may contain:
   - Steps that do not need grounding
   - Steps that use preloaded context
   - Steps that require fresh C0 retrieval

2. L3 must NOT make implicit C0 decisions outside the RouteContract or step contract
3. Each step's `c0_policy` is honored from the frozen contract

---

## 9. Fix Prompt Assembly Boundary

**Requirement**: PA must check the frozen `RouteContract.c0_policy`

**Changes**:
1. If `evidence_contract_required=true`, PA must require `FinalEvidenceContract`
2. If `evidence_contract_required=false` but `c0_mode` is bypass, PA must require `C0BypassReceipt`
3. PA must NOT silently proceed when C0 evidence was required but absent
4. PA must NOT convert bypass into evidence

---

## 10. Observability and Receipts

Add explicit OTEL/span or receipt fields:

| Field | Source | Purpose |
|-------|--------|---------|
| `l1_grounding_required` | L1PlanContract | Advisory signal |
| `route_c0_mode` | RouteContract.c0_policy | Frozen decision |
| `evidence_contract_required` | RouteContract.c0_policy | PA enforcement |
| `c0_preflight_status` | C0.0 output | Eligibility result |
| `c0_bypass_reason` | C0BypassReceipt | Typed bypass reason |
| `c0_policy_decision_source` | RouteContract.c0_policy | Traceability |

Every C0 bypass must be typed, replayable, and traceable.

---

## 11. Tests to Add or Update

1. **L1 grounding advisory does not authorize C0 by itself**
2. **L0 freezes c0_policy into RouteContract**
3. **C0 preflight obeys RouteContract.c0_policy and does not inspect route prefixes**
4. **R1/R5 terminal routes bypass via explicit c0_policy, not prefix checks**
5. **R4 with preloaded context emits BYPASS_PRELOADED_CONTEXT, not GROUNDING_NOT_REQUIRED**
6. **R4 with argument grounding requires C0 retrieval**
7. **PA fails closed when evidence_contract_required=true and FinalEvidenceContract is missing**
8. **PA accepts explicit C0BypassReceipt only when RouteContract.c0_policy allows bypass**
9. **L3 step-level c0_policy is honored in managed workflows**
10. **Negative test: hardcoded C0 bypass reason without RouteContract.c0_policy fails**

---

## 12. Anti-Pattern Scan

Search for and remove/quarantine:

| Pattern | Location | Replacement |
|---------|----------|-------------|
| `route_id.startswith("R1_")` | C0 preflight | `c0_policy.c0_mode == "BYPASS_CACHE_RETURN"` |
| `route_id.startswith("R5_")` | C0 preflight | `c0_policy.c0_mode == "BYPASS_FALLBACK"` |
| `route_id in {"R3_GROUNDED", ...}` | L1 preflight | Remove entirely |
| `hardcoded "GROUNDING_NOT_REQUIRED"` | R4 entrypoint | `c0_policy` with `BYPASS_PRELOADED_CONTEXT` |
| `c0_bypass_reason="..."` hardcoded | Any entrypoint | RouteContract-driven |
| Duplicate C0 preflight logic | Outside C0/L0 | Consolidate to single path |
| C0 decisions in R4/L3 | Entrypoints | Move to L0 policy construction |

---

## 13. Acceptance Criteria

- [ ] One canonical C0 policy path:
  ```
  L1 semantic grounding need
    -> L0 freezes RouteContract.c0_policy
    -> C0 preflight obeys c0_policy
    -> PA requires FinalEvidenceContract or C0BypassReceipt
  ```
- [ ] No route-name prefix checks remain inside C0 preflight for bypass decisions
- [ ] No hardcoded R4 C0 bypass remains
- [ ] Every C0 bypass has a typed reason and receipt
- [ ] Tests prove both retrieve-required and bypass paths
- [ ] Existing route behavior remains functionally compatible, but decision authority is now contract-driven and replayable

---

## 14. Files to Modify

| File | Changes |
|------|---------|
| `agentic_core/L0_routing/c0_retrieval/route_contract.py` | Add `C0Policy` dataclass and `c0_policy` field to `RouteContract` |
| `agentic_core/L0_routing/c0_retrieval/preflight.py` | Remove route-prefix checks, obey `RouteContract.c0_policy` |
| `agentic_core/L1_cognition/c0_context/preflight.py` | Remove runtime decisions, emit advisory fields only |
| `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` | Remove hardcoded bypass, use `c0_policy` |
| `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | Review and apply same pattern |
| `agentic_core/runtime/contracts/c0_bypass_receipt.py` | Ensure typed bypass reasons |
| `agentic_core/prompt_governance/prompt_assembly/pa4_validation.py` | Enforce evidence/bypass receipt requirement |
| Tests in `tests/agentic_core/L0_routing/c0_retrieval/` | Update to use `c0_policy` |
| Tests in `tests/_apps_contract/` | Add new test cases |

---

## 15. Non-Goals

- Do NOT refactor unrelated routing, retrieval, PA, L2, Exit, L5, L4, or L6 behavior
- Do NOT create new retrieval modes
- Do NOT create new route families
- Do NOT change C0's internal retrieval implementation
- Do NOT modify the UWG or spine contracts beyond C0 policy field

---

## 16. Uncertainty Areas

| Question | Investigation Needed |
|----------|---------------------|
| Does `agentic_core/L0_routing/doctrine/preflight.py` also need changes? | Review for C0-related logic |
| Are there other R4-like entrypoints with hardcoded bypass? | Search for `build_c0_bypass_receipt` calls |
| How does this affect existing test fixtures? | Identify fixtures with hardcoded bypass |
| Do we need migration for existing RouteContract instances? | Check backward compatibility requirements |

---

## 17. Wave Structure (Tentative)

| Wave | Focus | Files | Est. Tokens | Status |
|------|-------|-------|---------------|--------|
| W1 | Add C0Policy to RouteContract | route_contract.py | ~2k | Not Started |
| W2 | Refactor L1 preflight (advisory only) | L1/c0_context/preflight.py | ~3k | Not Started |
| W3 | Refactor L0 C0 policy construction | L0/c0_retrieval/preflight.py | ~4k | Not Started |
| W4 | Fix R4 hardcoded bypass | integrated_r4_*.py | ~2k | Not Started |
| W5 | Fix PA boundary enforcement | pa4_validation.py | ~2k | Not Started |
| W6 | Tests and verification | test files | ~4k | Not Started |

---

## 18. Related

- Memory: `6e7e9afe-46fc-4476-85f7-9e9e0729c1bb` (author-gate-deferred-scope)
- Memory: `78c557a4-e0a4-4cfd-92d8-d22c05a2d2fa` (Plans DB AI Summary)
- Rule: `.windsurf/rules/adg-canonical-invariants.md`
- Rule: `.windsurf/rules/plan-location.md`

