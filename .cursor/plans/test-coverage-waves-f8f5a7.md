---
plan_id: test-coverage-waves-f8f5a7
plan_type: infra
---

# Test Coverage Waves — Top 15 ADG-Driven Targets

Add structural-coverage tests for the 15 highest-leverage untested modules selected by ADG fan-in (blast radius) + fan-out (integration seams) + layer criticality (L0/L5 ×2.0, L3/L4 ×1.75 per `adg-canonical-invariants.md` §6).

ADG Provenance: backend=sqlite, snapshot=`adg_indexed_04242026_0558.sqlite.tmp` (5,577 modules, 150,152 import edges, 30,240 unresolved targets).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/rules/adg-canonical-invariants.md` §6 | Layer multipliers (L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75) | ✅ |
| `ops_scripts/verification/report_test_gaps_top15.py` | Fan-in + fan-out analyzer (built this session) | ✅ |
| `artifacts/test_gaps/top15_04252026_0114.{json,md}` | Top-15 ranked output | ✅ |
| ADG SQLite `nodes`/`edges` tables, `relation_type='imports'` | Structural truth for test-importer + prod fan-in/out | ✅ |
| `tests/unit/agentic_core/**` existing patterns | Style/scaffolding for new test files | 🔲 |

---

## ADG Hotspot Report (Top 15)

| Rank | Layer | Module | Test Imp | Fan-In | Fan-Out | Combined | Archetype |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | L0 | `agentic_core/L0_routing/config/__init__.py` | 0 | **120** | 3 | **8.09** | CENTRAL_DEPENDENCY |
| 2 | L5 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | 0 | 11 | 12 | **6.70** | ORCHESTRATOR |
| 3 | L5 | `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | 0 | 2 | **14** | **5.57** | SAFETY_GATEKEEPER |
| 4 | L5 | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` | 0 | 3 | 7 | **5.49** | SAFETY_GATEKEEPER |
| 5 | L0 | `agentic_core/L0_routing/reasoning/agentic_router.py` | 0 | 2 | 10 | **5.40** | ORCHESTRATOR |
| 6 | L5 | `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` | 0 | 2 | 9 | **5.35** | ORCHESTRATOR |
| 7 | L5 | `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | 0 | 3 | 5 | **5.34** | SAFETY_GATEKEEPER |
| 8 | L5 | `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | 0 | 1 | 13 | **5.18** | ORCHESTRATOR |
| 9 | L5 | `agentic_core/L5_safety/enforcement/verification_gate.py` | 0 | 3 | 3 | **5.13** | SAFETY_GATEKEEPER |
| 10 | L5 | `agentic_core/L5_safety/reasoning/NamingAgent.py` | 0 | 3 | 3 | **5.13** | SAFETY_GATEKEEPER |
| 11 | L4 | `agentic_core/L4_state/config/chroma_paths.py` | 0 | **18** | 0 | **5.04** | STATE_NODE |
| 12 | L0 | `agentic_core/L0_routing/types/shadow_routing_types.py` | 0 | 2 | 4 | **4.99** | CENTRAL_DEPENDENCY |
| 13 | L5 | `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py` | 0 | 3 | 2 | **4.98** | SAFETY_GATEKEEPER |
| 14 | L5 | `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` | 0 | 1 | 8 | **4.95** | ORCHESTRATOR |
| 15 | L3 | `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py` | 0 | 5 | 4 | **4.90** | ORCHESTRATOR |

**Surface intersections** (per ADG canonical invariants §3):
- **Security**: GovernanceAgent, verification_gate, StructuralValidatorAgent, CodeEnforcerAgent, L5SafetyExerciserAgent, NamingAgent (6)
- **Execution**: agentic_router, UnifiedAgent, SovereignActionPlaneAgent (3)
- **State**: chroma_paths, L0_routing/config/__init__.py (2)
- **Write**: hierarchy_healer, root_hygiene_healer, SystemArchitectAgent (3)
- **Observability**: shadow_routing_types (1)

All 15 intersect at least one ADG Surface — no isolated modules in this batch.

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| Wave 1 | Foundational L0/L4 (high fan-in roots) | Ranks 1, 11, 12 (`L0_routing/config/__init__.py`, `chroma_paths.py`, `shadow_routing_types.py`) | A | ~12K 🟢 |
| Wave 2 | L5 safety gatekeepers (validators + gates) | Ranks 7, 9, 10, 13 (`StructuralValidatorAgent`, `verification_gate`, `NamingAgent`, `CodeEnforcerAgent`) | B | ~16K 🟢 |
| Wave 3 | L5 orchestrators / healers | Ranks 2, 4, 6, 8, 14 (`hierarchy_healer`, `root_hygiene_healer`, `SystemArchitectAgent`, `SovereignActionPlaneAgent`, `L5SafetyExerciserAgent`) | C | ~22K 🟢 |
| Wave 4 | Routing/orchestration cores | Ranks 3, 5, 15 (`GovernanceAgent`, `agentic_router`, `UnifiedAgent`) | D | ~16K 🟢 |

**Total: ~66K tokens across 4 waves.**

Wave ordering rationale: foundational types and config (Wave 1) first because they have the highest fan-in (120, 18, 2) and are pure data — easy to test, unblock everything else. L5 gatekeepers (Wave 2) next because they are leaf-ish (low fan-out) and security-surface critical. Wave 3 tackles complex L5 orchestrators with substantial fan-out (mock-heavy). Wave 4 is the riskiest cluster — agent cores with the broadest surface area.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | L0 routing config tests | `tests/unit/agentic_core/L0_routing/config/test___init__.py` | GAP-1, fan-in=120 | ~4K | 🔲 TODO |
| 1.2 | L4 chroma_paths tests | `tests/unit/agentic_core/L4_state/config/test_chroma_paths.py` | GAP-1, fan-in=18 | ~4K | 🔲 TODO |
| 1.3 | L0 shadow_routing_types tests | `tests/unit/agentic_core/L0_routing/types/test_shadow_routing_types.py` | GAP-2 | ~4K | 🔲 TODO |
| 2.1 | StructuralValidatorAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_StructuralValidatorAgent.py` | GAP-3 | ~4K | 🔲 TODO |
| 2.2 | verification_gate tests | `tests/unit/agentic_core/L5_safety/enforcement/test_verification_gate.py` | GAP-3 | ~4K | 🔲 TODO |
| 2.3 | NamingAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_NamingAgent.py` | GAP-3 | ~4K | 🔲 TODO |
| 2.4 | CodeEnforcerAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_CodeEnforcerAgent.py` | GAP-3 | ~4K | 🔲 TODO |
| 3.1 | hierarchy_healer tests | `tests/unit/agentic_core/L5_safety/reasoning/test_hierarchy_healer.py` | GAP-4, fan-out=12 | ~5K | 🔲 TODO |
| 3.2 | root_hygiene_healer tests | `tests/unit/agentic_core/L5_safety/reasoning/test_root_hygiene_healer.py` | GAP-4 | ~4K | 🔲 TODO |
| 3.3 | SystemArchitectAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_SystemArchitectAgent.py` | GAP-4 | ~4K | 🔲 TODO |
| 3.4 | SovereignActionPlaneAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_SovereignActionPlaneAgent.py` | GAP-4, fan-out=13 | ~5K | 🔲 TODO |
| 3.5 | L5SafetyExerciserAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_L5SafetyExerciserAgent.py` | GAP-4 | ~4K | 🔲 TODO |
| 4.1 | GovernanceAgent tests | `tests/unit/agentic_core/L5_safety/reasoning/test_GovernanceAgent.py` | GAP-5, fan-out=14 | ~6K | 🔲 TODO |
| 4.2 | agentic_router tests | `tests/unit/agentic_core/L0_routing/reasoning/test_agentic_router.py` | GAP-5, fan-out=10 | ~5K | 🔲 TODO |
| 4.3 | UnifiedAgent tests | `tests/unit/agentic_core/L3_orchestration/reasoning/test_UnifiedAgent.py` | GAP-5 | ~5K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Foundational types/config untested but exported broadly.**
- `L0_routing/config/__init__.py` has 120 prod consumers — any breakage cascades through all routing code.
- `chroma_paths.py` has 18 consumers — vector store path resolution is silent failure surface.

**GAP-2: Type/contract modules lack import-shape tests.**
- `shadow_routing_types.py` is a contract surface — at minimum, structural import + dataclass instantiation tests prevent silent contract drift.

**GAP-3: L5 safety gatekeepers have zero tests despite enforcing security policy.**
- All 4 modules in Wave 2 sit on the Security ADG Surface. Per canonical invariants §3: "Swallowed checks = no safety."

**GAP-4: L5 orchestrators with high fan-out are integration black boxes.**
- 5 modules in Wave 3 each touch 7–13 downstream prod modules. Without integration tests, healing/orchestration failures are undetectable until they cascade.

**GAP-5: Layer L0/L3/L5 agent cores are unprotected against regression.**
- GovernanceAgent (fan-out=14), agentic_router (fan-out=10), UnifiedAgent (fan-out=4) are routing/governance cores. Constitutional rule §22: ADG graph layer is primary for refactoring — these untested cores block any safe refactor.

---

## Execution Plan

For every phase, the test scaffold follows this minimum-bar pattern (cheap to author, structurally meaningful):

1. **Importability** — `import <module>` succeeds (catches dependency cycles, missing exports).
2. **Public surface inventory** — `assert callable(getattr(<module>, <name>))` for every documented top-level symbol.
3. **Construction smoke** — for classes/agents: instantiate with minimal mocks; assert no exception.
4. **Per-method dispatch smoke** — for the 1–3 most-called public methods (identified via `adg_edge_fanin`), call with minimal valid input; assert return shape or no exception.
5. **Negative path** — at least one explicit error case (invalid input → expected exception class).

Higher-fan-out modules (Wave 3, Wave 4) get one additional **integration-style test** that mocks the immediate downstream collaborators (top 3 by frequency in `flows_to`/`calls` edges) and asserts the public method routes to them.

### Wave 1 — Foundational (Phases 1.1, 1.2, 1.3)

**Scope**: Pure data/config modules; small mocking surface.

**Commands**:
```bash
# After all 3 test files added:
python -m pytest tests/unit/agentic_core/L0_routing/config/test___init__.py \
                 tests/unit/agentic_core/L4_state/config/test_chroma_paths.py \
                 tests/unit/agentic_core/L0_routing/types/test_shadow_routing_types.py -v
```

**Acceptance**: All 3 test files exist, pytest passes, each module's `test_importers` count goes from 0 → ≥1 in next ADG regen.

### Wave 2 — L5 Safety Gatekeepers (Phases 2.1–2.4)

**Scope**: Pure-validator modules — small fan-out, security-critical.

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/test_StructuralValidatorAgent.py \
                 tests/unit/agentic_core/L5_safety/enforcement/test_verification_gate.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_NamingAgent.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_CodeEnforcerAgent.py -v
```

**Acceptance**: All 4 pass; each module covered by ≥1 test importer.

### Wave 3 — L5 Healers & Orchestrators (Phases 3.1–3.5)

**Scope**: High-fan-out modules — mock collaborators per `adg_edge_fanout(relation_type='calls')`.

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/test_hierarchy_healer.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_root_hygiene_healer.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_SystemArchitectAgent.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_SovereignActionPlaneAgent.py \
                 tests/unit/agentic_core/L5_safety/reasoning/test_L5SafetyExerciserAgent.py -v
```

**Acceptance**: All 5 pass; integration-style test exists for each (mocks top-3 downstream collaborators).

### Wave 4 — Routing & Orchestration Cores (Phases 4.1–4.3)

**Scope**: Heaviest modules — broadest surface, full integration discipline.

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/test_GovernanceAgent.py \
                 tests/unit/agentic_core/L0_routing/reasoning/test_agentic_router.py \
                 tests/unit/agentic_core/L3_orchestration/reasoning/test_UnifiedAgent.py -v
```

**Acceptance**: All 3 pass; agentic_router & UnifiedAgent get ≥2 dispatch tests each.

---

## Rules

- All new tests use `pytest`; no `unittest.TestCase` boilerplate.
- No `@pytest.mark.skip` and no `@pytest.mark.xfail` without `strict=True` (constitutional §1).
- Every catch in test setup uses specific exception types; no bare `except Exception` (constitutional §15).
- Subprocess in test fixtures: `subprocess.run(argv, shell=False, timeout=30)` only (constitutional §0, §14).
- Use existing fixtures from `tests/conftest.py` and `tests/conftest_factories.py` where possible — do not duplicate.
- After each wave: regenerate ADG (`python tools/generate_full_adg.py`), confirm `test_importers` count went 0 → ≥1 for the targeted modules, write back the score delta.

---

## Success Criteria

- [ ] All 15 modules go from `test_importers=0` to `test_importers≥1` in the next ADG snapshot.
- [ ] No new SC/AP P0/P1 violations introduced (run `adg_violations` after each wave).
- [ ] `pytest tests/unit/agentic_core/` passes with no new failures attributable to this plan.
- [ ] Per-wave commit ladder: one commit per wave, message format `wave-N-test-coverage: <files> (<+lines>)`.
- [ ] Coverage delta posted to Notion Wave/Phase Convergence (one row per wave) after Wave 4.

---

## Implementation Commands

```bash
# (already done) Generate top-15 report
python ops_scripts/verification/report_test_gaps_top15.py \
  --adg artifacts/adg/adg_indexed_04242026_0558.sqlite.tmp

# Wave 1 → 4 test execution per Execution Plan above

# After each wave: refresh ADG and verify coverage delta
python tools/generate_full_adg.py
python ops_scripts/verification/report_test_gaps_top15.py
```

---

## Rollback Strategy

If a wave introduces test failures or unexpected import cycles:
1. `git revert <wave-commit>` — each wave is one atomic commit.
2. Re-run `pytest tests/unit/agentic_core/<layer>` to confirm baseline restored.
3. Open a follow-up `NEXT_STEP:` marker if a single module needs special test infrastructure (e.g., async fixtures, OTel mocks).

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Modules covered | 15/15 | `report_test_gaps_top15.py` post-regen |
| L0 layer coverage | 42.7% → ≥45.0% | risk_weighted report by-layer table |
| L5 layer coverage | 12.3% → ≥14.5% | risk_weighted report by-layer table |
| Test pass rate | 100% | `pytest tests/unit/agentic_core` |
| New SC/AP P0/P1 | 0 | `adg_violations` snapshot diff |
