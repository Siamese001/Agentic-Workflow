# apps_rg Lean-Core Architecture Contract

> **Plan Reference:** `apps_rg_lean_core_binding_a1b2c3`  
> **Status:** ACTIVE  
> **Effective Date:** 2026-06-07  
> **Last Updated:** 2026-06-07

---

## Purpose

This document establishes the architectural binding law for apps_rg as part of the Lean-Core Spine Contract Binding + Authority Collapse refactor. It defines what apps_rg owns, what it does not own, and the rules for binding to the spine contract layer.

---

## Mental Model

### BAD BINDING (Deprecated)
```
apps_rg is hard-wired to agentic_core imports and concrete implementation internals.
```

### GOOD BINDING (Target)
```
apps_rg is bound to the spine contract.

agentic_core is one runtime implementation of the spine.
apps_rg speaks the spine contract cleanly.
apps_rg does not become a sub-platform or reimplement the spine.
```

---

## Binding Law

### 1. apps_rg binds to spine contracts, not agentic_core implementation.

All production imports of spine functionality must route through `apps_rg.runtime.spine_contracts`. Concrete agentic_core runtime internals are **FORBIDDEN** in production code.

**Allowed:**
```python
from apps_rg.runtime.spine_contracts import ValidatedRequest, RouteContract
```

**Forbidden:**
```python
from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import ...
from agentic_core.runtime.judges.panel import ...
from agentic_core.L2_execution import ...
```

**Temporary Exception:**
- `apps_rg/runtime/spine_contracts.py` may re-export existing contract classes while contracts still live under agentic_core.
- No other apps_rg production module may import those contract classes directly.

**Long-term Target:**
Neutral shared contract package (e.g., `apps_shared/spine_contracts` or `agentic_spine_contracts`) that both apps_rg and agentic_core depend on.

---

### 2. Graph is mandatory for apps_rg product value.

- C0.3 graph context must be emitted for all active generation routes
- Graph traversal policy must be present in route contracts
- Graph skills proof pool must be active for relevant sections
- Role-family projection uses graph topology
- Phase changes use graph-traversal reasoning

**Non-Negotiable:** Graph capabilities are not optional. They are core to apps_rg's value proposition.

---

### 3. Sections remain independently runnable.

- Section CLI entrypoints must function without full-run orchestration
- Section debugging capability is preserved
- SectionRunner consolidates lifecycle, not eliminates independent execution
- Each section can be generated, validated, and debugged in isolation

---

### 4. Candidate facts prove claims.

- No JD or briefing text may be used as candidate claim proof
- All claims must reference verified fact IDs from candidate graph
- Fact IDs are validated against candidate_facts graph
- Claims without supporting facts are flagged, not silently accepted

**Product Rule:** If a claim cannot be traced to a candidate fact ID, it is marked as unsupported.

---

### 5. Graph supports role/phase/skill routing unless fact-bound.

- Role-family projection uses graph topology
- Phase changes use graph-traversal reasoning
- Skills graph drives competency selection
- When facts are explicit, they override graph inference
- Graph never overrides explicit candidate facts

---

### 6. JD and briefing are targeting only.

- JD text informs positioning, never proves candidate claims
- Briefing informs strategic targeting, never proves candidate claims
- Both are inputs to the generation process, not evidence in the proof pool
- Claims sourced only from JD/briefing without fact support are rejected

---

### 7. One authority per decision.

| Stage | Authority | Responsibility |
|-------|-----------|----------------|
| U0 | Structure Validation | Validate input structure, stamp identity, reject missing required inputs |
| L1 | Deterministic Planning | Plan generation without evidence retrieval, route hints are advisory only |
| L0 | Deterministic Routing | One cheapest safe route, no retrieval, no model call |
| C0 | Evidence Resolution | Candidate facts prove claims, graph supports routing unless fact-bound |
| PA | Prompt Assembly | One compiler, one artifact shape, canonical slot order |
| L2 | Model Execution | All model calls through ProviderGatewayPort |
| Exit | Disposition Aggregation | X1 checkout, X2 aggregation, X3 exactly one disposition |

**Rule:** No stage takes authority from another stage.

---

### 8. Missing briefing fails closed.

- No apps_research delegation from apps_rg critical path
- No fallback briefing generation
- Clear product error on missing briefing

**Error Message:**
```
apps_rg requires an uploaded briefing artifact or authoritative briefing text; apps_research delegation is disabled.
```

**Active Generation Modes (require briefing):**
- strategic_tailor
- tailor_existing
- generate_scratch
- section_regen
- healing_fact_check

---

### 9. R1B semantic output reuse is opt-in only.

**Default:** OFF (R1B semantic cache disabled)

**Opt-in Activation:**
```bash
export APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
```

**Rules:**
- R1B never bypasses graph validation unless explicitly enabled
- When enabled, R1B hit must still pass graph digest verification
- Exact deterministic cache (R1A) remains enabled by default

**Rationale:** Prevent semantic cache from bypassing graph-grounded career reasoning.

---

### 10. LLM judges evaluate compact packets only; they do not repair.

**JudgePacket Shape:**
```python
{
    "section_id": "...",
    "target_company": "...",
    "target_role": "...",
    "display_text": "...",
    "claim_ledger": [...],
    "fact_abstracts": [...],
    "deterministic_gate_summary": {...},
    "rubric_ref": "...",
    "rubric_compact": "8-12 checks max"
}
```

**Constraints:**
- Judge input target: 2k-4k tokens
- Judge output target: <500 tokens JSON
- Attempts: 1 (default)
- No full prompt, JD, briefing, or chat thread in judge context

**Deterministic X2 First:**
- Hard deterministic gates enforce correctness before judge
- Judge only runs after X2 gates pass
- Judge evaluates quality, not correctness

---

### 11. Exit emits exactly one X3 for product-visible full runs.

- Section dispositions map to same Exit model
- No section-local final authority bypass
- Full run emits one coherent X3 disposition
- X3 options: ALLOW, REVIEW, BLOCK
- UNKNOWN is never PASS

---

### 12. UWG alone writes durable state.

- No durable writes from L2, L3, judges, or apps_rg runtime
- All state changes route through UWG
- Exit may emit disposition, but UWG writes the record
- L4 storage is UWG-orchestrated

---

### 13. L6 remains post-run only.

- L6 cannot rescue the current run
- L6 operates on completed run artifacts only
- L6 is offline shadow calibration and learning
- L6 never mutates in-progress runs
- L6 outputs inform future runs, not current run

---

## Product Ownership

### apps_rg OWNS (Product Logic)

- **Graph-grounded career arcs**: Resume narrative structured around career trajectory
- **Phase/role/skills graph projection**: Graph-driven role and phase mapping
- **Section specs**: Shape, constraints, validation rules per section
- **Proof-pool selection**: Which facts support which claims
- **JD/briefing targeting boundaries**: How targeting inputs inform (not prove) generation
- **Resume assembly**: Final resume composition from sections
- **Product-specific validators**: X2 validators for resume-specific correctness

### apps_rg does NOT OWN (Core Spine)

- Concrete agentic_core execution engines
- Core route engines
- Core L2 executors
- Core Exit pipelines
- UWG (Universal Write Guard)
- L4 (Storage Layer)
- L6 (Learning Layer - post-run only)
- Concrete core judge engines

---

## Import Architecture

### Production Code Import Rules

| From | To | Status |
|------|-----|--------|
| `apps_rg/*` | `apps_rg.runtime.spine_contracts` | ALLOWED |
| `apps_rg/*` | `agentic_core.runtime.contracts.*` | TEMPORARY (via facade only) |
| `apps_rg/*` | `agentic_core.runtime.entrypoints.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.runtime.entry.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.L0_routing.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.L1_cognition.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.L2_execution.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.runtime.exit.*` | **FORBIDDEN** |
| `apps_rg/*` | `agentic_core.runtime.judges.*` | **FORBIDDEN** (except via panel port) |
| `apps_rg/*` | `agentic_core.runtime.l6.*` | **FORBIDDEN** |
| `apps_rg/*` | `apps_research.*` | **FORBIDDEN** (quarantined) |

### Test Code Import Rules

Tests may import directly for mocking and integration testing, but should prefer:
- Test doubles that implement Protocol interfaces
- Mock facades that simulate contract behavior

---

## CI Enforcement

### test_apps_rg_spine_contract_binding.py

**Purpose:** Verify apps_rg production code has zero forbidden concrete agentic_core imports

**Trigger:** Every PR touching `apps_rg/`

**Behavior:**
- Walks all `apps_rg/*.py` files via AST
- Extracts import statements
- Fails if any forbidden import pattern matches

**Forbidden Patterns:**
- `agentic_core.runtime.entrypoints`
- `agentic_core.runtime.entry`
- `agentic_core.L0_routing`
- `agentic_core.L1_cognition`
- `agentic_core.L2_execution`
- `agentic_core.runtime.exit`
- `agentic_core.runtime.judges` (concrete)
- `agentic_core.runtime.l6`

**Exemptions:**
- `apps_rg/runtime/spine_contracts.py` (the facade itself)
- Test files (`tests/*`, `test_*.py`)
- Files explicitly listed in `EXEMPT_FILES`

**Failure Message:**
```
Forbidden concrete agentic_core imports detected:
  - apps_rg/runtime/orchestration.py: from agentic_core.runtime.entrypoints import ...

All production imports must route through apps_rg/runtime/spine_contracts.py
```

**Bypass:** `SPINE_CONTRACT_BINDING_BYPASS=1` (emergency only, requires CTO approval)

---

## Evolution Path

### Phase 1: Facade (Current)
- `spine_contracts.py` re-exports from `agentic_core.runtime.contracts`
- `ports.py` defines Protocol interfaces
- CI enforces import boundary

### Phase 2: Contract Package
- Extract `agentic_core.runtime.contracts` to `agentic_spine_contracts`
- Both `apps_rg` and `agentic_core` depend on `agentic_spine_contracts`
- Facade becomes pass-through or removed

### Phase 3: Runtime Port Injection
- `agentic_core` implements `SpineRuntimePort`, `ProviderGatewayPort`, etc.
- `apps_rg` receives port implementations via dependency injection
- No direct imports of concrete implementations

---

## Violations and Remediation

### Detecting Violations

```bash
# Run import boundary check
python -m pytest tests/architecture/test_apps_rg_spine_contract_binding.py -v

# Find current violations (before fix)
grep -r "from agentic_core.runtime" apps_rg --include="*.py" | grep -v test | grep -v spine_contracts
```

### Remediation Process

1. Identify the forbidden import
2. Determine the contract type needed
3. Add to `spine_contracts.py` if missing
4. Change import to use facade
5. Run CI check to verify
6. Document in wave completion notes

---

## References

- **Plan Document:** `.cursor/plans/apps_rg-lean-core-binding-a1b2c3.md`
- **Notion Plan:** `apps_rg_lean_core_binding_a1b2c3`
- **Architecture Tests:** `tests/architecture/test_apps_rg_spine_contract_binding.py`
- **Ports Definition:** `apps_rg/runtime/ports.py`
- **Contract Facade:** `apps_rg/runtime/spine_contracts.py`

---

## Amendment Process

To amend this binding law:

1. Propose amendment in plan document
2. Get approval from Architecture Lead
3. Update this document
4. Update CI guards if needed
5. Register amendment in Notion Plans DB
6. Notify all apps_rg contributors

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-06-07 | Initial binding law for lean-core refactor | Cursor Agent |
