---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\p3.2_apps-rg-l0-critical-gaps-remediation-a3f8e1.md'
original_relative_path: '_archive\\2026-05\\p3.2_apps-rg-l0-critical-gaps-remediation-a3f8e1.md'
source_sha256: d971adfb1d778503a1f02c3b2d9ff0fcf797cbc804dee17fa7cb0fc6827e006d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: "apps_rg L0 Critical Gaps Remediation — HARDENED"
description: "Hardened mission-critical L0 gap fixes: typed gate receipts, generic core fields, ref-based provider model, canonical route family vocabulary, staged shim cleanup"
plan_type: scoped_refactor
created: 2026-05-13
hardened: 2026-05-13
status: Not Started
dod_exempt: false
---

> [!IMPORTANT]
> PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER
> MASTER_PLAN_REF: .cursor/plans/apps-rg-master-governed-runtime-hardening.md
> DISPOSITION: MERGED_INTO_MASTER_WITH_CORE_SPLIT
> SUPERSEDED_BY_PHASES: Phase 5 and Phase 7
> RETAINED_SCOPE:
> - canonical route profile path
> - fail-closed route loader
> - route_family/execution_form/allowed_next_stage
> - typed gate receipts
> - no fake PASS
> - cache bypass for personalized drafts
> - provider_model_requirement_ref handoff
> MOVED_SCOPE:
> - generic RouteContract fields move to Phase 5/core-enabling work
> - apps_rg local L0 wiring moves to Phase 7
> DEFERRED_SCOPE:
> - terminal RET hardening unless R5 actively emitted
> CONFLICTS_RESOLVED:
> - L0 remains route owner; L1 hints are advisory only

## Portfolio Consolidation Notes
This plan has been merged into the master consolidation with core-enabling work split:
- Phase 5 (Core): Generic RouteContract field additions
- Phase 7 (Master): apps_rg-local L0 route wiring and typed gate receipts

---

# apps_rg L0 Critical Gaps Remediation — HARDENED

**Bottom line:** The real apps_rg L0 runtime gaps collapse to **5 mission-critical gaps** with **strict architectural boundaries**: no app-specific fields in core contracts, no fake PASS gate strings, no hardcoded model constants, staged shim cleanup with proof.

## Core Architectural Constraints (Non-Negotiable)

1. **L0 may not manufacture PASS** — PASS requires gate-required facts present and checked; missing inputs → UNKNOWN/FAIL, never PASS.
2. **agentic_core stays generic** — No resume-specific enums, no app literals in L0 routing. Generic fields only: `work_shape`, `task_shape`, `route_profile_ref`.
3. **Ref-based resolution** — Provider/model requirements flow through `provider_model_requirement_ref` → governed registry → concrete model. No hardcoded Qwen strings in contracts.
4. **Canonical route families** — Spine route families (R3R4_MANAGED_WORKFLOW, etc.) in RouteContract; app-specific routing reasons live in app-owned profiles.
5. **Proof before deferral** — Semantic cache deferral requires test proving R1B disabled for personalized drafts.

## Problem Statement

Per audit `apps-rg-l0-audit-2026-05-13`, apps_rg L0 has these **true runtime gaps**:

1. **L0 gate verdicts are placeholders/UNKNOWN** — `route_gate_refs` contains `"G07:UNKNOWN:0.0"`. Governance requires real GateVerdict or TEMPORARY_THIN_ADAPTER typed receipt, never manufactured PASS.
2. **Route profile path inconsistent** — L0 references stale `apps_rg/profiles/rg_route_profile.yaml`. Canonical path is `apps_rg/config/domain_contract/route_profiles.yaml`.
3. **Route decision logic hardcoded** — `APPS_RG_ROUTE_FAMILY` constant in code, not from profile.
4. **`execution_form` not populated** — Empty string breaks dispatch routing decisions.
5. **Cache bypass for personalized drafts not enforced** — Hardcoded eligibility ignores personalization flag.
6. **Work shape not represented** — L0 needs generic `work_shape`/`task_shape` fields to distinguish full resume vs section regenerate.
7. **Provider model hardcoded in PA** — Should be `provider_model_requirement_ref` in RouteContract, resolved through registry.
8. **Core has legacy apps_rg shim** — `agentic_core/L0_routing/apps_rg_l0_binding.py` needs staged deprecation with caller proof.

## Wave Structure (Hardened: W0-W6)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1-P0.3 | Baseline verification: imports, paths, gate API existence | ~800 | No code changes; establish current state proof | Not Started | CI passes; no new imports from core shim; gate API surface identified |
| W1 | P1.1-P1.3 | Canonical route profile resolution + fail-closed loader | ~1,500 | route_profiles.yaml schema stable | Not Started | Profile loads from canonical path; missing profile fails closed |
| W2 | P2.1-P2.3 | RouteContract scoped field population: canonical route_family, execution_form, allowed_next_stage | ~1,800 | W1 stable; RouteContract fields defined | Not Started | `route_family=R3R4_MANAGED_WORKFLOW`, `execution_form=MANAGED_WORKFLOW` for full resume |
| W3 | P3.1-P3.3 | GateVerdict integration or TEMPORARY_THIN_ADAPTER RouteGateReceipt | ~1,500 | Gate machinery exists or typed temp available | Not Started | Gate refs typed; no UNKNOWN on clean runs; no fake PASS |
| W4 | P4.1-P4.2 | Declarative cache bypass + personalized draft cache tests | ~1,200 | W2 stable | Not Started | `personalization_required=True` → r1a=False, r1b=False |
| W5 | P5.1-P5.2 | Provider/model requirement ref handoff to PA/L2 | ~1,000 | Provider registry exists | Not Started | PA consumes from RouteContract, not hardcoded constant |
| W6 | P6.1-P6.3 | Shim deprecation/quarantine + CI app-agnostic proof | ~1,200 | W1-W5 stable; zero callers proven | Not Started | Shim deprecated; CI gate blocks new core imports |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Verify no new imports from core shim | `agentic_core/L0_routing/apps_rg_l0_binding.py` import graph | Hidden callers block removal | ~300 | Not Started |
| P0.2 | Verify gate API surface exists | `agentic_core/L5_safety/types/exit_disposition_types.py` or equivalent | Need real GateVerdict or temp adapter | ~300 | Not Started |
| P0.3 | Baseline CI check for app literals in core L0 | `ops_scripts/ci/check_l0_app_agnostic.py` (W6 gate, early version) | No automated proof currently | ~200 | Not Started |
| P1.1 | **DECISION: Canonical route profile** — `apps_rg/config/domain_contract/route_profiles.yaml` is canonical | `l0_binding.py` | Stale path `apps_rg/profiles/rg_route_profile.yaml` must fail CI | ~400 | Not Started |
| P1.2 | Fail-closed profile loader | `l0_binding.py` + `route_profiles.yaml` | Missing/malformed profile must raise, not fallback | ~600 | Not Started |
| P1.3 | Add work_shape/task_shape to L1PlanContract (generic core fields) | `agentic_core/runtime/contracts/l1_plan_contract.py` | Must be generic, not resume-specific | ~500 | Not Started |
| P2.1 | Populate canonical route_family | `l0_binding.py` + RouteContract | Must use spine families (R3R4_MANAGED_WORKFLOW), not app names | ~600 | Not Started |
| P2.2 | Populate execution_form | `l0_binding.py` + RouteContract | MANAGED_WORKFLOW for full resume | ~600 | Not Started |
| P2.3 | Populate allowed_next_stage | `l0_binding.py` + RouteContract | L3 for managed workflow | ~600 | Not Started |
| P3.1 | Define TEMPORARY_THIN_ADAPTER RouteGateReceipt if no real GateVerdict | `agentic_core/runtime/contracts/route_gate_receipt.py` | Typed, not strings; marked temporary | ~500 | Not Started |
| P3.2 | Implement _evaluate_route_gates with strict PASS rules | `l0_binding.py` | PASS only with facts present; missing → UNKNOWN/FAIL | ~600 | Not Started |
| P3.3 | G20 budget gate: PASS only with budget profile present and checked | `l0_binding.py` | No PASS merely because "checked even if not enforced" | ~400 | Not Started |
| P4.1 | Move hardcoded cache logic to profile | `route_profiles.yaml` + `l0_binding.py` | Personalization flag drives eligibility | ~600 | Not Started |
| P4.2 | Test: personalization_required=True disables R1A and R1B | `tests/_apps_contract/test_l0_cache_bypass.py` | Proof before deferral | ~600 | Not Started |
| P5.1 | Add provider_model_requirement_ref to RouteContract | `agentic_core/runtime/contracts/route_contract.py` | Ref-based, not raw model string | ~400 | Not Started |
| P5.2 | Update PA to consume ref from RouteContract | `apps_rg/runtime/bindings/pa_binding.py` | TEMPORARY_COMPATIBILITY_FALLBACK marked if needed | ~600 | Not Started |
| P6.1 | Import graph search for core shim callers | Global search | Must prove zero callers before removal | ~400 | Not Started |
| P6.2 | Stage 1: Replace any caller imports with apps_rg.runtime.bindings.l0_binding | All files with imports | Redirect to app-owned binding | ~400 | Not Started |
| P6.3 | Stage 2: Mark shim deprecated/quarantined | `agentic_core/L0_routing/apps_rg_l0_binding.py` | Warning + pointer to new location | ~400 | Not Started |

## Files In Scope

**Primary (read+modify):**
- `apps_rg/runtime/bindings/l0_binding.py`
- `apps_rg/runtime/bindings/l1_binding.py`
- `apps_rg/runtime/bindings/pa_binding.py`
- `apps_rg/config/domain_contract/route_profiles.yaml`
- `agentic_core/runtime/contracts/route_contract.py`
- `agentic_core/runtime/contracts/l1_plan_contract.py`
- `agentic_core/runtime/contracts/route_gate_receipt.py` (new, TEMPORARY_THIN_ADAPTER)

**Secondary (read-only context):**
- `agentic_core/L0_routing/apps_rg_l0_binding.py` (legacy shim — staged deprecation)
- `agentic_core/L5_safety/types/exit_disposition_types.py` (GateVerdict pattern)

**CI/Tests (new files):**
- `ops_scripts/ci/check_l0_app_agnostic.py`
- `tests/_apps_contract/test_l0_gate_verdicts.py`
- `tests/_apps_contract/test_l0_execution_form.py`
- `tests/_apps_contract/test_l0_cache_bypass.py`
- `tests/_apps_contract/test_l0_canonical_profile_path.py`

## Definition of Done (Hardened)

| DoD ID | Criterion | Verification Method | Owner |
|--------|-----------|---------------------|-------|
| DoD-1 | Canonical route profile path is `apps_rg/config/domain_contract/route_profiles.yaml` | `test_l0_canonical_profile_path.py` asserts path; stale path absent | Cursor Agent |
| DoD-2 | Full resume generation emits `route_family=R3R4_MANAGED_WORKFLOW`, `execution_form=MANAGED_WORKFLOW`, `allowed_next_stage=L3` | Unit test `test_l0_execution_form.py` | Cursor Agent |
| DoD-3 | `grounding_required=true` when evidence/JD required (full resume) | Test: JD present → grounding_required=True | Cursor Agent |
| DoD-4 | Gate refs are typed (RouteGateReceipt or GateVerdict), not raw strings | `test_l0_gate_verdicts.py` asserts isinstance | Cursor Agent |
| DoD-5 | Gate verdicts are not UNKNOWN on clean dry-run; no fake PASS (facts required) | Test: clean run → all gates PASS or explicit; missing facts → UNKNOWN/FAIL | Cursor Agent |
| DoD-6 | G20 only PASS with budget profile present and route in bounds; else UNKNOWN/FAIL per policy | Test: no budget profile → G20=UNKNOWN or policy-driven FAIL | Cursor Agent |
| DoD-7 | Default full-resume dry-run has `personalization_required=true` → `r1a_exact=False`, `r1b_semantic=False` | `test_l0_cache_bypass.py` | Cursor Agent |
| DoD-8 | PA consumes `provider_model_requirement_ref` from RouteContract; TEMPORARY_COMPATIBILITY_FALLBACK marked if hardcoded constant used | Integration test + code inspection | Cursor Agent |
| DoD-9 | agentic_core has no active apps_rg route implementation; no app literals in L0 | `check_l0_app_agnostic.py` passes | Cursor Agent |
| DoD-10 | Core shim deprecated with warning; no new imports allowed | CI gate + import graph proof | Cursor Agent |
| DoD-11 | Smoke run: `python -m apps_rg --dry-run` exits 0 with fully populated RouteContract | Manual + CI verification | User/Cursor Agent |

**Explicitly NOT REQUIRED (Future Hardening):**
- risk_tier, capability_ceiling — NOT_APPLICABLE for current apps_rg paths
- filesystem_scope, network_scope, write_scope — NOT_APPLICABLE unless L0 gains those authorities
- Terminal RET handling — defer until R5 actively emitted
- Semantic cache compatibility proof — deferral acceptable ONLY if DoD-7 proves R1B disabled for personalized drafts (see P4.2).

## Wave Execution (Hardened)

### W0 — Baseline Verification (No Code Changes)

**P0.1: Verify No New Imports from Core Shim**
- Run global import graph search for `agentic_core.L0_routing.apps_rg_l0_binding`
- Document all callers; if any exist, they must be migrated in W6

**P0.2: Verify Gate API Surface**
- Search for canonical 00C/runtime `GateVerdict` implementation (belongs to runtime gate machinery, not L5)
- Note: L5 certification refs may be *consumed by* runtime gates for verification; L5 does not *emit* GateVerdict
- If 00C `GateVerdict` exists: use directly
- If unavailable: use generic `TEMPORARY_THIN_ADAPTER RouteGateReceipt` only until canonical 00C integration exists

**P0.3: Baseline CI Check**
- Early version of `check_l0_app_agnostic.py`: scans for app literals, reports current state
- No enforcement yet; establishes baseline

### W1 — Canonical Route Profile + Fail-Closed Loader

**P1.1: CANONICAL PATH DECISION — FINAL**

**DECISION:** `apps_rg/config/domain_contract/route_profiles.yaml` is the **canonical** route profile.

- `apps_rg/profiles/rg_route_profile.yaml` **must not be created**.
- Any stale reference to `apps_rg/profiles/rg_route_profile.yaml` **must fail CI**.
- Update `l0_binding.py:_ROUTE_PROFILE_RELPATH` to canonical path.

**P1.2: Fail-Closed Profile Loader**

```python
def _load_route_profile(repo_root: Path) -> dict:
    path = repo_root / _ROUTE_PROFILE_RELPATH  # canonical
    if not path.exists():
        raise RouteProfileNotFoundError(f"Canonical route profile missing: {path}")
    profile = yaml.safe_load(path.read_text())
    if not _validate_profile_schema(profile):
        raise RouteProfileSchemaError("Route profile schema mismatch")
    return profile
```

**P1.3: Generic Work Shape Fields in L1PlanContract**

Add to `agentic_core/runtime/contracts/l1_plan_contract.py`:

```python
work_shape: str  # generic; apps_rg profile defines values like "full_resume_generation"
task_shape: str  # generic; apps_rg profile defines "section_regeneration", "bullet_regeneration"
route_profile_ref: str  # ref to app-owned route profile
```

**NOT in core:** No `full_resume`, `section_regenerate`, `bullet_regenerate` enum values. Those are app-owned profile values.

### W2 — RouteContract Field Population (Canonical Vocabulary)

**P2.1: Populate Canonical route_family**

For full resume generation with grounding:
- `route_family = RouteFamily.R3R4_MANAGED_WORKFLOW` (canonical spine value)
- `route_reason = "full_resume_generation"` (app-owned profile reason, stored separately if needed)

For section regeneration:
- `route_family = RouteFamily.R3_SIMPLE_GROUNDED_READ` or `R4_SINGLE_ACTION`
- `route_reason = "section_regeneration"`

**P2.2: Populate execution_form**

| work_shape (from profile) | route_family | execution_form |
|---------------------------|--------------|----------------|
| `full_resume_generation` | R3R4_MANAGED_WORKFLOW | MANAGED_WORKFLOW |
| `section_regeneration` | R3_SIMPLE_GROUNDED_READ | SINGLE_STEP |
| `healing_validation` | R5_SEMANTIC_REFRESH | TERMINAL_SHORTCIRCUIT |

**P2.3: Populate allowed_next_stage**

- `MANAGED_WORKFLOW` → `allowed_next_stage = {L3}`
- `SINGLE_STEP` → `allowed_next_stage` is conditional:
  - If `grounding_required = true`: must begin with C0 → {C0, PA, L2} or {C0, L2} if no PA
  - If `grounding_required = true` and model generation required: flow is C0 → PA → L2
  - If `grounding_required = false` and model generation required: flow is PA → L2
  - If pure bounded action with no model prompt: flow is L2 directly
  - Grounded section regeneration must not skip C0
- `TERMINAL_SHORTCIRCUIT` → `allowed_next_stage = {Exit}`

### W3 — Typed Gate Verdicts (No Fake PASS)

**P3.1: TEMPORARY_THIN_ADAPTER RouteGateReceipt (if needed)**

If real `GateVerdict` machinery unavailable:

```python
@dataclass(frozen=True)
class RouteGateReceipt:
    """TEMPORARY_THIN_ADAPTER — Replace with canonical GateVerdict when available."""
    gate_id: str  # G07, G08, G10, G20
    verdict: Literal["PASS", "UNKNOWN", "FAIL", "WARN"]
    score: float  # 0.0-1.0
    reason: str
    facts_present: bool  # PASS requires facts_present=True
    required_facts: tuple[str, ...]  # What facts were required for this gate
```

**P3.2: _evaluate_route_gates with Strict PASS Rules**

```python
def _evaluate_route_gates(l1_plan, route_profile) -> tuple[RouteGateReceipt, ...]:
    receipts = []
    
    # G07: Route Selection
    route_family_derived = _derive_route_family(l1_plan, route_profile)
    facts_present = route_family_derived is not None
    if facts_present and route_family_derived != RouteFamily.UNKNOWN:
        g07 = RouteGateReceipt("G07", "PASS", 1.0, "Route family derived from profile", True, ("profile", "l1_plan"))
    elif not facts_present:
        g07 = RouteGateReceipt("G07", "UNKNOWN", 0.0, "Missing route profile or L1 plan", False, ("profile", "l1_plan"))
    else:
        g07 = RouteGateReceipt("G07", "FAIL", 0.0, "Unroutable input", True, ("profile", "l1_plan"))
    receipts.append(g07)
    
    # G08: Retrieval/Grounding
    grounding_required = _derive_grounding_required(l1_plan, route_profile)
    facts_present = grounding_required is not None
    # ... same pattern: PASS only if facts_present and valid
    
    # G10: Cache/Freshness
    cache_eligibility = _derive_cache_eligibility(l1_plan, route_profile)
    facts_present = personalization_flag_readable(l1_plan)
    # ...
    
    # G20: Cost/Latency/Budget
    budget_profile = route_profile.get("budget_constraints")
    route_within_budget = _check_route_within_budget(l1_plan, budget_profile)
    if budget_profile and route_within_budget is not None:
        g20 = RouteGateReceipt("G20", "PASS" if route_within_budget else "FAIL", 1.0 if route_within_budget else 0.0, "Budget checked", True, ("budget_profile",))
    elif budget_profile is None:
        g20 = RouteGateReceipt("G20", "UNKNOWN", 0.0, "No budget profile defined", False, ("budget_profile",))
    else:
        g20 = RouteGateReceipt("G20", "FAIL", 0.0, "Route exceeds budget or check failed", True, ("budget_profile",))
    receipts.append(g20)
    
    return tuple(receipts)
```

**P3.3: G20 Strict Rule**

- **PASS** only if: budget profile exists AND route is within bounds
- **UNKNOWN** if: no budget profile defined
- **FAIL** if: budget profile exists but route exceeds bounds OR check failed

### W4 — Cache Bypass + Personalized Draft Proof

**P4.1: Declarative Cache Logic in Profile**

```yaml
# route_profiles.yaml
cache_eligibility_policy:
  r1a_exact:
    default: true
    override_when:
      personalization_required: false
  r1b_semantic:
    default: false  # Always false for resume generation
```

**P4.2: Test Proof Before Deferral**

For apps_rg final resume generation, `personalization_required` defaults to `true` unless explicitly proven otherwise via route profile policy.

```python
def test_personalization_disables_cache():
    # Default full-resume dry-run: personalization_required = true
    l1_plan = build_l1_plan()  # no explicit personalization flag = defaults to True for resume
    route = l0_route_apps_rg(l1_plan)
    assert route.cache_eligibility["r1a_exact"] is False
    assert route.cache_eligibility["r1b_semantic"] is False
    
def test_explicit_non_personalized_allows_r1a():
    # Only for non-final deterministic validation paths with explicit cache-safe policy
    l1_plan = build_l1_plan(personalization_required=False, cache_safe_policy=True)
    route = l0_route_apps_rg(l1_plan)
    assert route.cache_eligibility["r1a_exact"] is True  # Only allowed here
    assert route.cache_eligibility["r1b_semantic"] is False  # Always false for resume
```

If `test_personalization_disables_cache` passes, semantic cache compatibility proof is deferrable.

### W5 — Provider Model Ref Handoff

**P5.1: Add provider_model_requirement_ref to RouteContract**

```python
@dataclass(frozen=True)
class RouteContract:
    # ... existing fields
    provider_model_requirement_ref: str  # e.g., "model_lane::apps_rg::primary_generator"
```

**P5.2: PA Consumes Ref**

In `pa_binding.py`:

```python
def pa_compose_apps_rg(route: RouteContract, ...):
    # TEMPORARY_COMPATIBILITY_FALLBACK: Remove by 2026-06-01
    if not route.provider_model_requirement_ref:
        warnings.warn("TEMPORARY_COMPATIBILITY_FALLBACK: Using hardcoded model", DeprecationWarning)
        target_model = APPS_RG_TARGET_MODEL  # Hardcoded constant
    else:
        target_model = resolve_model_from_registry(route.provider_model_requirement_ref)
```

### W6 — Staged Shim Cleanup

**P6.1: Import Graph Search**

```bash
# Find all imports of the core shim
grep -r "from agentic_core.L0_routing.apps_rg_l0_binding import" --include="*.py" .
grep -r "import agentic_core.L0_routing.apps_rg_l0_binding" --include="*.py" .
```

**P6.2: Replace Caller Imports**

For each caller found:
- Replace: `from agentic_core.L0_routing.apps_rg_l0_binding import l0_route_apps_rg`
- With: `from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg`

**P6.3: Mark Shim Deprecated**

```python
# agentic_core/L0_routing/apps_rg_l0_binding.py
"""DEPRECATED — Moved to apps_rg.runtime.bindings.l0_binding.

Removal target: 2026-06-01
Migration: Replace imports with apps_rg.runtime.bindings.l0_binding.
"""
import warnings
warnings.warn(
    "DEPRECATED: agentic_core.L0_routing.apps_rg_l0_binding is obsolete. "
    "Use apps_rg.runtime.bindings.l0_binding. Removal target: 2026-06-01",
    DeprecationWarning,
    stacklevel=2
)
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
__all__ = ["l0_route_apps_rg"]
```

**CI Check:**

```python
# In check_l0_app_agnostic.py
if "agentic_core.L0_routing.apps_rg_l0_binding" in new_imports:
    raise L0AgnosticViolation("New imports from deprecated core shim forbidden")
```

## Verification-vs-Deferral (Hardened)

| Item | Verify Now | Defer |
|------|------------|-------|
| Canonical profile path | ✅ W1 test | ❌ |
| Canonical route_family/execution_form | ✅ W2 test | ❌ |
| Gate verdicts typed | ✅ W3 test | ❌ |
| Gate verdicts no UNKNOWN on clean run | ✅ W3 test | ❌ |
| G20 strict PASS rules | ✅ W3 test | ❌ |
| Personalization defaults true, disables cache | ✅ W4 test | ❌ (proof required before deferral) |
| Provider ref handoff | ✅ W5 integration test | ❌ |
| Shim cleanup staged | ✅ W6 import graph + CI | ❌ |
| Risk tier, capability ceiling | ❌ | ✅ NOT_APPLICABLE for current runs |
| Filesystem/network/write scope | ❌ | ✅ NOT_APPLICABLE for current runs |
| Terminal RET handling | ❌ | ✅ Future route coverage |

## Non-Goals (Explicitly Excluded)

1. **Moving L0 binding to agentic_core** — App-owned binding is correct; only cleanup shim in core.
2. **Resume-specific enums in core** — Core fields are generic (`work_shape`, `task_shape`); app profile owns values.
3. **Full RouteContract population** — Risk tier, capability ceiling, filesystem scope: NOT_APPLICABLE.
4. **Section regeneration feature** — Infrastructure only (generic work_shape field); actual feature deferred.
5. **Semantic cache compatibility** — Deferral requires W4 proof that R1B disabled for personalized drafts.
6. **C0 handoff verification** — C0 already checks `grounding_required`; additional verification is test hardening, not a gap.

## Risk Register (Hardened)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Real GateVerdict machinery unavailable | Medium | Medium | TEMPORARY_THIN_ADAPTER with explicit deprecation date |
| PA hardcoded constant not migrated | Low | High | CI gate for hardcoded strings; TEMPORARY_COMPATIBILITY_FALLBACK with warning |
| Legacy shim has hidden dynamic imports | Medium | High | Import graph search in W0; runtime import tracing if needed |
| Profile schema churn | Medium | Medium | Schema version check; fail-closed on mismatch |
| Generic work_shape field too abstract | Low | Low | App profile provides clear value mapping; L0 reads both |

## Rollback Plan

If any wave causes regression:

1. **W0-W1:** Revert to current `l0_binding.py`; profile changes are additive only.
2. **W2-W3:** Disable new field population; fallback to current behavior with UNKNOWN gates.
3. **W4-W6:** Revert specific phase; earlier waves remain stable.

## Related Plans & Precedents

- Parent audit: `apps-rg-l0-audit-2026-05-13` (gap report — this plan hardens that output)
- Runtime wiring: `apps-rg-runtime-wiring-completion-d4e8a1` (W3.P5 real LLM dispatch)
- Golden state: `apps-rg-golden-state-section-generation-a4f9e1` (section vs full distinction)

## Success Criteria (Hardened)

```bash
# Smoke run must produce hardened RouteContract
python -m apps_rg \
  --target-company "Test" \
  --target-role "Test Role" \
  --target-level "EXECUTIVE" \
  --jd "test" \
  --dry-run
```

Expected RouteContract:
- `route_profile_ref`: canonical path to `route_profiles.yaml`
- `work_shape`: `full_resume_generation` (from profile, not core enum)
- `route_family`: `R3R4_MANAGED_WORKFLOW` (canonical spine)
- `execution_form`: `MANAGED_WORKFLOW`
- `allowed_next_stage`: `L3`
- `grounding_required`: `true`
- `route_gate_refs`: typed receipts, all PASS on clean run
- `personalization_required`: `true` (default for final resume generation)
- `cache_eligibility`: `{"r1a_exact": false, "r1b_semantic": false}` (personalization disables both)
- `provider_model_requirement_ref`: `"model_lane::apps_rg::primary_generator"` (or equivalent)

All 11 DoD criteria met.

---

**PLAN_CREATED:** 2026-05-13  
**HARDENED:** 2026-05-13  
**WAVE_EXECUTION_STATE:** Not Started  
**NEXT_AUTHOR_GATE:** W0.P0.2 — Verify gate API surface (real GateVerdict vs TEMPORARY_THIN_ADAPTER)
