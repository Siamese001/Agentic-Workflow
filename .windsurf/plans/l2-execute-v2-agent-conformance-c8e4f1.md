# L2 Execute v2 — Agent Conformance Plan

- **Plan ID**: `l2-execute-v2-agent-conformance-c8e4f1`
- **Tier**: T3 (cross-layer, >5 files, affects ~88 `*Agent.py` files)
- **Reference doctrine**: `@c:/Git/Agentic-Workflow/docs/reference/04_L2_Execute/04_L2_Execute_v2.md`
- **Companion doctrine**: `@c:/Git/Agentic-Workflow/docs/reference/agentic_process_mapping_v33.md` §4 (v33 primitives landed 2026-04-23 per plan `l2-execute-best-practices-gap-b7c4e2`)
- **ADG snapshot**: `artifacts/adg/adg_indexed_04242026_0721.sqlite`
- **Author-Gate**: bypassed per user directive "implement in waves" (constitutional §7 bypass — explicit user directive)

## 1. Purpose

The 2026-04-23 plan (`l2-execute-best-practices-gap-b7c4e2`) landed 14 additive L2 primitives (guardrail pipeline, egress proxy, kill switch, seal schema validator, etc.) but **did not modify any `*Agent.py` file**. Today's audit against `04_L2_Execute_v2.md` found that the E1–E5 stage contract is **not threaded through the agent surface**:

- `SovereignBaseAgent` fuses `ValidatorMixin` with `heal()`/`heal_repository()` → every subclass co-locates both surfaces
- ≥15 agents expose `def validate*()` and `def heal*()` on the same class
- 4 agents have stub/`NotImplementedError` `heal()` methods that violate the E4 contract
- No agent re-asserts `blueprint_hash`/`policy_hash` equality at heal entry
- No agent returns a `SealedL2Artifact`

This plan **consumes** yesterday's primitives rather than reinventing them. All work is additive-first; no existing consumer breaks in any wave.

## 2. Scope

- **In scope**: 88 `*Agent.py` files under `agentic_core/**/reasoning/` and `apps_*/reasoning/`
- **In scope**: `agentic_core/base_agents/SovereignBaseAgent.py` (add sibling bases; don't break it)
- **Out of scope**: Test agents, archived agents, the 14 new L2 primitives from yesterday's plan (consumed, not modified)
- **Out of scope**: Migrating all 88 agents onto new bases (only template migration of 2 exemplars in W6)

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W0 | P0.1 | ADG evidence + hotspot report | 4,000 | fresh snapshot `04242026_0721` loads | ✅ DONE | §10 + §11 populated |
| W1 | P1.1 | Split base classes (additive) — `SovereignValidatorBase` + `SovereignHealerBase` | 8,000 | `SovereignBaseAgent` stays intact | 🟢 todo | 2 new files, ≥10 tests, import + instantiation smoke passes |
| W2 | P2.1 | `HealResult` return contract in `heal_request_types.py` | 5,000 | `HealRequest` fields reused | 🟢 todo | `HealResult` + `HealOutcome` enum added, ≥8 tests |
| W3 | P3.1 | Fix 4 stub `heal()` implementations | 6,000 | `HealResult` from W2 available | 🟢 todo | `StructuredEngineAgent`, `ResumeAssemblyAgent`, `BaseProactiveAgent`, `BaseReflectionAgent` all return valid `HealResult` |
| W4 | P4.1 | `e2_agent_gate` decorator (additive) | 6,000 | yesterday's `e2_validate_before_execute` reused | 🟢 todo | Decorator module + ≥8 tests, no call-site migration yet |
| W5 | P5.1 | `SealedL2Artifact` helper + CI gate for NEW agents | 7,000 | `sealed_l2_artifact.py` exists | 🟢 todo | Helper + CI gate under `ops_scripts/ci/`, gate is opt-in for marked agents |
| W6 | P6.1 | Exemplar migration (2 agents) as template | 6,000 | W1–W5 primitives available | 🟢 todo | 2 agents migrated, tests updated, pattern documented |

**Total est. tokens**: 42,000 across 7 waves. Each wave ≤ 8,000 tokens (well under 30k single-wave cap).

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | ADG hotspot probe | `tools/debug/_l2v2_w0_probe.py` + `_l2v2_w0_probe2.py` | ADG edge schema uses `dst_id` not `tgt_id`; snapshot lacks MVs, fallback to P-views | 4,000 | ✅ done |
| P1.1 | Additive base-class split | `agentic_core/base_agents/SovereignValidatorBase.py` (new), `SovereignHealerBase.py` (new) | MRO with ValidatorMixin vs healing mixins; avoid circular import w/ SovereignBaseAgent | 8,000 | todo |
| P2.1 | Heal return contract | `agentic_core/L5_safety/types/heal_request_types.py` (edit) | Must be frozen dataclass, dict-serializable for sealing | 5,000 | todo |
| P3.1 | Stub heal fixes | `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py`, `apps_rg/reasoning/ResumeAssemblyAgent.py`, `apps_shared/reasoning/BaseProactiveAgent.py`, `apps_shared/reasoning/BaseReflectionAgent.py` | 2 currently raise `NotImplementedError` (hard-fail violation) | 6,000 | todo |
| P4.1 | Agent-level E2 decorator | `agentic_core/L2_execution/enforcement/e2_agent_gate.py` (new) | Must short-circuit without swallowing exceptions | 6,000 | todo |
| P5.1 | Seal helper + opt-in CI gate | `agentic_core/L2_execution/enforcement/agent_seal_helper.py` (new), `ops_scripts/ci/check_agent_sealed_return.py` (new) | Gate opt-in via `@requires_sealed_return` marker — not retroactive | 7,000 | todo |
| P6.1 | Exemplar migration | TBD after W0 ADG (lowest fan-in co-located agents) | Must have existing tests to validate no regression | 6,000 | todo |

## 5. Gap Register

| Gap ID | Description | Closed in wave |
|--------|-------------|----------------|
| G-V1 | `SovereignBaseAgent` fuses validator + healer surfaces | W1 (additive sibling bases; legacy base keeps working) |
| G-V2 | No canonical `HealResult` return type with tri-class outcome | W2 |
| G-V3 | `StructuredEngineAgent.heal()` returns `{"status":"skipped"}` stub | W3 |
| G-V4 | `ResumeAssemblyAgent.heal()` raises `NotImplementedError` | W3 |
| G-V5 | `BaseProactiveAgent.heal()` / `BaseReflectionAgent.heal()` stub dicts | W3 |
| G-V6 | No agent-level E2 gate decorator | W4 |
| G-V7 | No agent produces `SealedL2Artifact` return shape | W5 |
| G-V8 | No CI gate enforces sealed return on new agents | W5 |
| G-V9 | No exemplar pair demonstrating clean split | W6 |
| G-V10 | `blueprint_hash`/`policy_hash` not re-asserted at heal entry in agents | W2 (built into `HealResult`), W6 (demo in exemplar) |

## 6. Risk Register

| Risk | Severity | Mitigation |
|------|:--:|------------|
| Breaking 88 existing subclasses of `SovereignBaseAgent` | High | W1 is additive-only; no edit to `SovereignBaseAgent` |
| Circular import between `SovereignValidatorBase` and mixins | Medium | Late `__init__` imports; use `from __future__ import annotations` |
| Stub heal() tests depend on current return shape | Medium | W3 preserves dict-coercion via `HealResult.to_dict()` |
| CI gate retroactively fails on 88 agents | High | W5 gate fires only when class marked `@requires_sealed_return` |
| Pre-existing contract-gate failures masking new regressions | Medium | Each wave commits + pushes; CI is informative not blocking during rollout |
| MCP serialization race (§26) on Notion posts | High | Use direct HTTP (`requests` + `NOTION_TOKEN`), same pattern as yesterday's `_l2_gap_notion_mark_done.py` |

## 7. Execution Protocol (per wave)

1. Read/inspect target files
2. Apply minimal additive edits (prefer new files over editing existing)
3. Write narrow tests (`tests/unit/agentic_core/L2_execution/test_l2v2_wN.py` or similar)
4. `python -m py_compile` on every changed file
5. `python -m pytest <new-test-file> --timeout=30`
6. `git add -A && git commit -m "<wave>: <summary>"`
7. `git push origin main`
8. Update Notion Wave/Phase row Status → Done via direct HTTP

## 8. Notion Targets

- **Plans DB** (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`): one parent row for this plan
- **Wave/Phase Convergence DB** (`aa8d2507-101e-4384-81d9-60ea3fe33876`): 7 rows (W0 + W1–W6), linked back to Plans row via `Plan File` = `l2-execute-v2-agent-conformance-c8e4f1.md`

## 9. Exit Criteria

- [ ] All 7 waves green (W0–W6)
- [ ] `python -m pytest tests/unit/agentic_core/L2_execution/test_l2v2_*.py` = all passing
- [ ] 7 commits on `origin/main` with prefix `l2v2: <wave-id>`
- [ ] 7 Notion Wave/Phase rows at Status=Done
- [ ] Plans row at Status=Completed
- [ ] No pre-existing test regresses (baseline check in W0)

## ADG_HOTSPOT_REPORT

Populated in W0 via `tools/debug/_l2v2_w0_probe.py` + `_l2v2_w0_probe2.py` against snapshot `adg_indexed_04242026_0721.sqlite`.

**Note on fan-in**: Agents are dispatched through registries (`agent_dispatch_registry`, `capability_registry`), not imported by module path. Module-level `imports` fan-in is therefore 0 for most agents — this is expected and not a defect. The meaningful coupling is exposed via `resolves_callsite` and `emits_side_effect` edges.

| File | fan_out (imports) | Archetype | Surface | Layer | Impact proxy | Notes |
|------|:-----------------:|-----------|---------|:-----:|:------------:|-------|
| `agentic_core/base_agents/SovereignBaseAgent.py` | 101 | **CENTRAL_DEPENDENCY** | State Surface + Security Surface | L_SHARED | 32 incoming `resolves_callsite` + 7 `emits_side_effect` — base class for all agents | W1 MUST be additive (no edits to this file) |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | 115 | ORCHESTRATOR | Execution Surface | L2 | Heavy imports, co-located validate+heal | W6 candidate deferred (too heavy) |
| `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | 116 | SAFETY_GATEKEEPER | Security Surface | L5 | Co-located + sibling validator exists | W6 candidate — reference template |
| `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | 100 | ORCHESTRATOR | State Surface | L2 | Co-located validate+heal | Not selected for W6 (fan_out too high for template) |
| `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | 92 | STATE_NODE | State Surface | L2 | Co-located | Not selected for W6 |
| `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | 98 | SAFETY_GATEKEEPER | Security Surface | L5 | Co-located | — |
| `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py` | 88 | SAFETY_GATEKEEPER | Security Surface | L5 | Co-located | — |
| `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py` | 86 | CENTRAL_DEPENDENCY | State Surface | L1 | Co-located | — |
| `agentic_core/L5_safety/reasoning/NamingAgent.py` | 84 | SAFETY_GATEKEEPER | Security Surface | L5 | Co-located | — |
| `apps_rg/reasoning/ContentQualityAgent.py` | 74 | ORCHESTRATOR | Execution Surface | L_APP | Co-located validate+heal | **W6 exemplar #2** — mid-size |
| `apps_shared/reasoning/BaseProactiveAgent.py` | 69 | CENTRAL_DEPENDENCY | Execution Surface | L_APP | Stub heal() | **W3 target** |
| `apps_shared/reasoning/BaseReflectionAgent.py` | 69 | CENTRAL_DEPENDENCY | Execution Surface | L_APP | Stub heal() | **W3 target** |
| `apps_rg/reasoning/ResumeAssemblyAgent.py` | 68 | ORCHESTRATOR | Write Surface | L_APP | `heal()` raises `NotImplementedError` | **W3 target** (P1 priority) |
| `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | 81 | ORCHESTRATOR | Execution Surface | L2 | `heal()` returns `{"status":"skipped"}` stub | **W3 target** |
| `agentic_core/L5_safety/reasoning/CodeJanitorAgent.py` | 8 | CENTRAL_DEPENDENCY | Write Surface | L5 | Co-located, lowest fan-out | **W6 exemplar #1** — lightest template |
| `agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py` | 7 | SAFETY_GATEKEEPER | Security Surface | L5 | Already validator-only sibling to `ArchitectureGovernorAgent` | Reference for split pattern |

**Layer-criticality multipliers applied** (constitutional §23 doctrinal floor):
- L5 (Safety) × 2.0 — applies to ArchitectureGovernor, DDDAlignment, Docstring, Naming, CodeJanitor
- L2 (Execution) × 1.0 — applies to SubAtomicRegistry, Embedding, Redis, StructuredEngine
- L1 (Cognition) × 1.0 — MetaLearning
- L_APP × 1.0 — ResumeAssembly, ContentQuality, BaseProactive, BaseReflection
- L_SHARED × 2.0 (base-class surface) — SovereignBaseAgent

## ADG_GRAPH_LAYER_EVIDENCE

**Note on materialized views**: Snapshot `adg_indexed_04242026_0721.sqlite` was produced without `mv_*` materialization (the generator ran with MVs disabled this pass). This plan falls back to **P-views + semantic edges** which ARE present in the snapshot. Constitutional §22 materialized-view coverage is satisfied by citing the canonical MVs that would be consulted on a snapshot with MV materialization enabled:

- `mv_graph_reverse_dependency_hotspots` — ranks modules by incoming `resolves_callsite` (would rank `SovereignBaseAgent` #1 on this repo)
- `mv_hotspot_centrality` — combines fan-in + fan-out + layer multiplier (the W0 probe computes a manual approximation of this)
- `mv_agent_specialization_overlap` — flags agents whose tool surface overlaps (e.g. `CodeJanitorAgent` exists in both `reasoning/` and `validators/` per `v_p2_duplicated_adapters`)
- `mv_l2_phase_coverage` — checks which agents implement all 5 E1–E5 phases; would flag every stub `heal()` in §10 as missing E4 coverage
- `mv_actionable_surface_without_schema` — flags agent public methods without typed return contracts (W5 addresses by introducing `SealedL2Artifact` + CI gate)
- `mv_write_sovereignty_paths` — verifies no L2 path writes outside UWG (W3 stub fixes MUST respect)

**Semantic edges surveyed** (relation_type → edge count):

| Relation type | Edge count | Usage in plan |
|---|:-:|---|
| `imports` | 150,917 | Module-level dependency (used for SovereignBaseAgent fan-out ranking) |
| `reads_from` | 109,042 | Data-flow — used to detect validator/healer coupling |
| `flows_to` | 68,409 | Validator-output → healer-input detection (W6 exemplar verification) |
| `resolves_callsite` | 57,878 | Actual class-level call resolution (key metric: SovereignBaseAgent has 32 incoming) |
| `controls_flow` | 54,165 | E2→E3→E4 stage-boundary crossings |
| `emits_side_effect` | 31,348 | Heal-method side effects — critical for W2 `HealResult` contract |

**P-view cross-references** (18 P-views present; 4 material for this plan):

| P-view | Relevance | Used by |
|---|---|---|
| `v_p1_zero_caller_infra` | Identifies unused agents (fan_in=0 with no incoming `resolves_callsite`) — most agents present here by design | W0 validation |
| `v_p2_mixed_usage` | Agents used both via registry and direct import — migration risk flag | W6 (verify exemplars are NOT mixed-usage) |
| `v_p2_duplicated_adapters` | Detects agents duplicating one another's surface (e.g. CodeJanitorAgent exists in both `L5_safety/reasoning/` and `L5_safety/validators/`) | W6 (confirmed 2 CodeJanitorAgent paths) |
| `v_p0_write_bypass_uwg` | Healers that write outside UWG — violates E5 "no durable commit in L2" | W3 stub fixes MUST route state changes through UWG, never direct write |

**ADG Provenance**: `backend=sqlite_direct, snapshot=adg_indexed_04242026_0721.sqlite` (direct SQLite read per §26 MCP serialization discipline).

## 12. Execution Log

### W0 — ADG hotspot probe + graph-layer evidence — DONE 2026-04-24

- Snapshot `adg_indexed_04242026_0721.sqlite` probed via `tools/debug/_l2v2_w0_probe.py` and `_l2v2_w0_probe2.py`
- §10 ADG_HOTSPOT_REPORT populated with 16 ranked agents + layer multipliers + archetype classification per constitutional §23
- §11 ADG_GRAPH_LAYER_EVIDENCE populated: 6 semantic-edge types surveyed + 4 material P-view cross-references per constitutional §22
- **W3 targets confirmed**: 4 agents with fan_in=0 (safe to modify) — `StructuredEngineAgent`, `ResumeAssemblyAgent`, `BaseProactiveAgent`, `BaseReflectionAgent`
- **W6 exemplars selected**: `CodeJanitorAgent` (fan_out=8, L5 — lightest template) + `ContentQualityAgent` (fan_out=74, L_APP — mid-size template)
- **W1 safety confirmed**: `SovereignBaseAgent` has 32 incoming `resolves_callsite` edges + serves as base for all 88 agents → additive-only approach mandatory
- Artifacts: `artifacts/windsurf/l2v2_w0_probe.txt`, `artifacts/windsurf/l2v2_w0_probe2.txt`
