---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\agent-deprecation-migration-d7a3f2.md'
original_relative_path: 'agent-deprecation-migration-d7a3f2.md'
source_sha256: adbb96f4db24ba11c773ffebd8065d7dcaf015ca60d081a57c08d3ab0b9dabeb
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agent Deprecation Migration — rolling backlog

- **Plan ID**: `agent-deprecation-migration-d7a3f2`
- **Tier**: T3 (cross-layer, >5 files, affects 41 agent files + ~900 consumers)
- **Assessment source**: `tools/debug/_agent_deprecation_assessment.py` run against `artifacts/adg/adg_indexed_04242026_0721.sqlite`
- **Assessment artifact**: `artifacts/windsurf/agent_deprecation_assessment.txt`
- **Author-Gate**: `deletion_strategy / plan_only_no_moves` decision captured 2026-04-24; per-wave authorization required before any archive move

## 1. Purpose

Catalog every deprecation-candidate agent with ADG-backed evidence, define per-agent migration waves, and establish the constitutional-§3-compliant process for archival. **No files move without a per-wave Author-Gate decision.**

## 2. Scope

- **In scope**: 41 `*Agent.py` files identified by `_agent_deprecation_assessment.py` as deprecated or unreferenced (by the permissive ADG `resolves_callsite` metric)
- **In scope**: the ~900 incoming call-site consumers that must be migrated before archival
- **In scope**: `@c:/Git/Agentic-Workflow/agentic_core/L2_execution/types/agent_taxonomy_registry.py` (string-keyed dispatch registry — archival MUST update this)
- **Out of scope**: 100 agents in `KEEP` bucket (actively used, no deprecation marker)
- **Out of scope**: actual file moves in this plan (deferred to per-wave approval cycles)

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W0 | P0.1 | Assessment snapshot (ADG + registry + test-file cross-reference) — DONE 2026-04-24 | 4,000 | Fresh ADG snapshot | ✅ DONE | §ADG_HOTSPOT_REPORT + §ADG_GRAPH_LAYER_EVIDENCE populated |
| W1 | P1.1 | Registry duplicate resolution: decide which `IntelligenceLibrarianAgent` (apps_lic vs L4_state/engines) is canonical | 5,000 | User reviews + decides per-agent | 🟢 todo | Duplicate picked, other marked @deprecated OR renamed |
| W2 | P2.1 | validators/ duplicate dedup: 3 agents duplicated under L5_safety/validators/ and L5_safety/reasoning/ | 8,000 | User approves which path wins | 🟢 todo | 3 duplicates resolved per `v_p2_duplicated_adapters` |
| W3 | P3.1 | Migrate LOW-fan-in DEPRECATED agents (fan-in ≤ 8): 21 agents, ~760 consumers | 18,000 | Consumers can be migrated incrementally | 🟢 todo | 21 agents have 0 consumers, deprecation markers added, 90-day timer starts |
| W4 | P4.1 | Migrate MEDIUM-fan-in DEPRECATED agents (fan-in 9–50): 7 agents, ~200 consumers | 15,000 | W3 complete | 🟢 todo | 7 agents at 0 consumers |
| W5 | P5.1 | Migrate HIGH-fan-in DEPRECATED agents (fan-in > 50): 3 agents (FileClassificationAgent/LocationHealerAgent/GovernanceAgent), ~560 consumers | 30,000 | W3+W4 complete; may need to split into sub-waves | 🟢 todo | 3 agents at 0 consumers |
| W6 | P6.1 | Archive after 90-day cooling: move files to `archives/agents/<YYYY-MM-DD>/`, delete tests, update registry, run full suite | 8,000 | 90 days elapsed since each agent hit zero references | 🟢 todo | All 41 files physically moved, tests green, registry updated |

**Total est. tokens**: 88,000 across 7 waves (but W5 may need further decomposition — 30k approaches the single-wave cap).

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Assessment probe | `tools/debug/_agent_deprecation_assessment.py` + `artifacts/windsurf/agent_deprecation_assessment.txt` | ADG `resolves_callsite` undercounts registry-dispatched agents | 4,000 | ✅ done |
| P1.1 | Registry duplicate resolution | `agentic_core/L2_execution/types/agent_taxonomy_registry.py`, `apps_lic/reasoning/IntelligenceLibrarianAgent.py`, `agentic_core/L4_state/engines/IntelligenceLibrarianAgent.py` | Two different files same class name | 5,000 | todo |
| P2.1 | validators/ duplicate dedup | `agentic_core/L5_safety/validators/{CodeJanitorAgent,GovernanceAgent,PascalSovereigntyAgent}.py` vs `agentic_core/L5_safety/reasoning/` counterparts | `v_p2_duplicated_adapters` violation | 8,000 | todo |
| P3.1 | Low-fan-in DEPRECATED migration | 21 files listed in §10 | Must migrate each consumer before archiving | 18,000 | todo |
| P4.1 | Medium-fan-in DEPRECATED migration | 7 files listed in §10 | Heavier consumer migration | 15,000 | todo |
| P5.1 | High-fan-in DEPRECATED migration | 3 files listed in §10 (FileClassificationAgent 265, LocationHealerAgent 224, GovernanceAgent 70) | Very heavy; may need sub-wave split | 30,000 | todo |
| P6.1 | 90-day cooling archive sweep | All 41 files + registry + tests | Physical moves; needs per-agent AGENT-DELETION-AUTHORIZED markers | 8,000 | todo |

## 5. Gap Register

| Gap ID | Description | Closed in wave |
|--------|-------------|----------------|
| G-D1 | `IntelligenceLibrarianAgent` exists in 2 paths with same class name | W1 |
| G-D2 | 3 duplicated adapters under `L5_safety/validators/` | W2 |
| G-D3 | 21 deprecated agents (low fan-in ≤8) still have consumers | W3 |
| G-D4 | 7 deprecated agents (medium fan-in 9–50) still have consumers | W4 |
| G-D5 | 3 deprecated agents (high fan-in >50) still have consumers | W5 |
| G-D6 | 6 zero-fan-in shims (10–19 lines) are registered ACTIVE in taxonomy but unimplemented | W1 (investigate; likely scaffold, keep) |
| G-D7 | `GravityLeakHealerAgent` zero-fan-in via ADG but consumed by `territory_healer_adapters.py` | W3 |
| G-D8 | No AGENT-DELETION-AUTHORIZED markers on any current deprecated agent | W3+W4+W5 (add per-agent marker as each hits zero consumers) |
| G-D9 | No automated 90-day cooling-timer tracking | W6 |
| G-D10 | No rollback protocol if an archived agent is discovered to have hidden consumer | W6 |

## 6. Risk Register

| Risk | Severity | Mitigation |
|------|:--:|------------|
| Agent dispatched via string key fails silently after archive | **Critical** | Never archive without (a) zero consumers in ADG, (b) zero taxonomy-registry entries, (c) full test-suite pass, (d) 90-day cooling |
| Consumer migration breaks production flow | High | Migrate one consumer at a time; keep legacy agent valid until last consumer updated |
| Archive sweep (W6) discovers hidden consumer | Medium | Rollback protocol: restore from `archives/agents/<date>/` + git history; re-add registry entry |
| Tests deleted prematurely reduce coverage | Medium | Tests deleted ONLY when agent is physically archived (W6), never during deprecation (W3–W5) |
| 41-agent scope too large for coherent migration | High | Plan decomposes into per-fan-in waves; each wave can further split if it exceeds 30k tokens |
| Constitutional §3 bypass | Critical | Per-agent AGENT-DELETION-AUTHORIZED marker required at wave entry; 90-day timer enforced per-agent |

## 7. Execution Protocol (per wave)

1. **Entry Author-Gate**: surface wave scope, list agents + consumer counts, get explicit user authorization
2. **Per-agent loop**:
   a. Add `# AGENT-DELETION-AUTHORIZED: <date> <rationale>` marker to the agent file
   b. Identify each consumer via ADG `edge_fanin(tgt_id, relation_type='resolves_callsite')` + grep test-file imports + registry scan
   c. For each consumer: redirect to canonical replacement (add import, update call, add test if missing)
   d. After all consumers migrated: verify ADG shows 0 fan-in AND registry entry removed AND no test imports
   e. Start 90-day cooling timer (record in `artifacts/agent_deprecation/<agent>.json`)
3. **Wave exit**: commit + push; update this plan's §Execution Log; update Notion Wave/Phase row
4. **W6 only**: after 90 days, physically `git mv <file> archives/agents/<YYYY-MM-DD>/<file>`, delete tests, run full suite, commit

## 8. Notion Targets

- **Plans DB** (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`): one parent row
- **Wave/Phase Convergence DB** (`aa8d2507-101e-4384-81d9-60ea3fe33876`): 7 rows (W0 + W1–W6)
- **SC/AP Violation Backlog**: `v_p2_duplicated_adapters` hits become individual backlog rows tracked in W2

## 9. Exit Criteria

- [x] W0 complete (assessment probe + artifact committed)
- [ ] W1–W6 complete
- [ ] All 41 files either (a) physically archived to `archives/agents/<date>/` after 90-day cooling, or (b) explicitly kept with rationale
- [ ] `agent_taxonomy_registry.py` updated: all archived agents removed
- [ ] Full test suite passes: `python -m pytest tests/`
- [ ] Each archived agent has `AGENT-DELETION-AUTHORIZED:` marker + 90-day timer record
- [ ] No pre-existing test regresses

## ADG_HOTSPOT_REPORT

Populated in W0 via `tools/debug/_agent_deprecation_assessment.py` against snapshot `adg_indexed_04242026_0721.sqlite`.

**Classification**: 3 risk tiers by ADG fan-in (via `resolves_callsite` — the most consumer-discovery-sensitive edge type):

### High-fan-in DEPRECATED (W5 targets — `CENTRAL_DEPENDENCY` archetype)

| File | fan_in | Lines | Archetype | Surface | Layer | Mult | Impact |
|------|:-----:|:-----:|-----------|---------|:-----:|:----:|:------:|
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | **265** | 5,688 | CENTRAL_DEPENDENCY | Security Surface | L5 | ×2.0 | 530 |
| `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | **224** | 3,212 | CENTRAL_DEPENDENCY | Write Surface + Security Surface | L5 | ×2.0 | 448 |
| `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | 70 | 1,263 | SAFETY_GATEKEEPER | Security Surface | L5 | ×2.0 | 140 |

### Medium-fan-in DEPRECATED (W4 targets)

| File | fan_in | Lines | Archetype | Surface | Layer |
|------|:-----:|:-----:|-----------|---------|:-----:|
| `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` | 46 | 889 | ORCHESTRATOR | Execution Surface | L0 |
| `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` | 42 | 700 | SAFETY_GATEKEEPER | Write Surface | L5 |
| `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | 34 | 539 | SAFETY_GATEKEEPER | Security Surface | L5 |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | 27 | 720 | ORCHESTRATOR | State Surface | L2 |
| `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | 26 | 459 | SAFETY_GATEKEEPER | Security Surface | L5 |
| `agentic_core/L5_safety/reasoning/RedSentinelAgent.py` | 22 | 539 | SAFETY_GATEKEEPER | Security Surface | L5 |
| `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | 15 | 412 | SAFETY_GATEKEEPER | State Surface | L5 |

### Low-fan-in DEPRECATED (W3 targets — 21 files, each fan_in ≤ 8)

All L3–L5 layers, mostly `SAFETY_GATEKEEPER` archetype, Security Surface.

- `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` (fan_in=2)
- `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py` (2)
- `agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py` (2)
- `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py` (2)
- `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py` (2)
- `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py` (3)
- `agentic_core/L5_safety/reasoning/CodeJanitorAgent.py` (3)
- `agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py` (4)
- `agentic_core/L2_execution/reasoning/ToolsmithAgent.py` (4)
- `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py` (4)
- `agentic_core/L5_safety/reasoning/BootstrapAgent.py` (4)
- `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py` (4)
- `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py` (4)
- `agentic_core/L5_safety/reasoning/CostGovernorAgent.py` (5)
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py` (6)
- `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py` (6)
- `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py` (6)
- `agentic_core/L3_orchestration/reasoning/GravityStateAgent.py` (7)
- `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py` (8)
- `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py` (8)
- `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py` (8)

### Zero-fan-in candidates (NOT archive candidates — all have registry/test references)

6 shims (10–19 lines) + 4 validators/ duplicates. All are registered ACTIVE in `agent_taxonomy_registry.py` or imported by dedicated test files. Dispatched via string key — ADG `resolves_callsite` cannot see this path.

| File | fan_in | Registry ACTIVE | Test file | Verdict |
|---|:-:|:-:|:-:|---|
| `apps_lic/reasoning/IntelligenceLibrarianAgent.py` | 0 | yes (but points to `L4_state/engines/` path!) | — | **Possible rename, not archive** |
| `apps_lic/reasoning/LicReflectionAgent.py` | 0 | yes | — | Registered scaffold — keep |
| `apps_lic/reasoning/MessageArchitectAgent.py` | 0 | yes | — | Registered scaffold — keep |
| `apps_lic/reasoning/MessageComplianceAgent.py` | 0 | yes | — | Registered scaffold — keep |
| `apps_rg/reasoning/RgStrategicPlannerAgent.py` | 0 | yes | `tests/unit/apps_rg/test_rg_strategic_planner_agent.py` | Has test — keep |
| `apps_rg/reasoning/RgTemplateOptimizerAgent.py` | 0 | yes | `tests/unit/apps_rg/test_rg_template_optimizer_agent.py` | Has test — keep |
| `agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py` | 0 | — | — | Consumed by `territory_healer_adapters.py` (3 refs) |
| `agentic_core/L5_safety/validators/CodeJanitorAgent.py` | 0 | — | — | W2 dedup target |
| `agentic_core/L5_safety/validators/GovernanceAgent.py` | 0 | — | — | W2 dedup target |
| `agentic_core/L5_safety/validators/PascalSovereigntyAgent.py` | 0 | — | — | W2 dedup target |

**Layer-criticality multipliers applied** (constitutional §23):
- L5 (Safety) × 2.0 — majority of DEPRECATED agents
- L0 (Routing) × 2.0 — `RootCustomsAgent`, `SSOTFolderCleanupAgent`
- L3 (Orchestration) × 1.75 — `CoverageAgent`, `SubAtomicAgent`, `SubatomicHopAgent`, `GravityStateAgent`, `OrchestrationHandshakeAgent`
- L2 (Execution) × 1.0 — `SubAtomicRegistryAgent`, `ToolsmithAgent`
- L1 (Cognition) × 1.0 — `StrategicRecommendationAgent`

## ADG_GRAPH_LAYER_EVIDENCE

**Note on materialized views**: Snapshot `adg_indexed_04242026_0721.sqlite` was produced without `mv_*` materialization. Plan falls back to P-views + semantic edges. Canonical MVs referenced for constitutional §22 coverage:

- `mv_graph_reverse_dependency_hotspots` — would rank `FileClassificationAgent` (265 fan-in) and `LocationHealerAgent` (224 fan-in) at the top of the deprecation-migration queue
- `mv_hotspot_centrality` — combines fan-in + fan-out + layer multiplier (W0 probe computed manually)
- `mv_agent_specialization_overlap` — flags the 3 `L5_safety/validators/*` duplicates of `L5_safety/reasoning/*` agents (W2 targets)
- `mv_l2_phase_coverage` — would flag deprecated agents still wired into E1–E5 phase handlers
- `mv_write_sovereignty_paths` — verifies healer agents (e.g. `LocationHealerAgent`) write through UWG before archival
- `mv_gateway_bypass_paths` — verifies no deprecated agent bypasses established gateways before its consumers migrate

**Semantic edges surveyed**:

| Relation type | Usage in plan |
|---|---|
| `imports` | Consumer discovery via module-level import chains |
| `resolves_callsite` | **Primary metric** — class-level call resolution driving fan-in counts in §ADG_HOTSPOT_REPORT |
| `instantiates` | Catches cases where consumers instantiate the agent class directly |
| `flows_to` | Data-flow continuity — validators whose outputs feed healers |
| `reads_from` | State-read dependencies that would break if the agent vanishes |
| `writes_to` | Write-authority dependencies (critical for L4 healers) |

**P-view cross-references**:

| P-view | Relevance | Wave |
|---|---|---|
| `v_p2_duplicated_adapters` | Confirms `L5_safety/validators/` directory duplicates of `L5_safety/reasoning/` agents | W2 |
| `v_p1_zero_caller_infra` | Identifies agents with no incoming calls — used as initial filter before registry/test cross-reference | W0 |
| `v_p2_mixed_usage` | Agents used both via registry and direct import — flag for careful migration | W3+W4+W5 |
| `v_p1_zero_caller_infra` | Most agents in KEEP bucket also appear here — confirms registry-dispatch pattern is dominant | W0 validation |

**ADG Provenance**: `backend=sqlite_direct, snapshot=adg_indexed_04242026_0721.sqlite` (direct SQLite read per §26 MCP serialization discipline).

## 10. Execution Log

### W0 — Assessment snapshot — DONE 2026-04-24

- Built `tools/debug/_agent_deprecation_assessment.py`: exhaustive per-agent probe across 8 ADG edge types + deprecation regex + shim heuristic
- Ran against `artifacts/adg/adg_indexed_04242026_0721.sqlite` → 141 agents scanned (100 KEEP + 31 RISKY_DEPRECATED + 6 SHIM_UNUSED + 4 INVESTIGATE_ZERO_FANIN + 0 SAFE_TO_ARCHIVE)
- Cross-referenced 10 zero-fan-in candidates against `agent_taxonomy_registry.py` + grep of repo → all 10 have registry or test references
- Author-Gate decision `deletion_strategy / plan_only_no_moves` captured 2026-04-24 (marker in next-response)
- **Finding**: ZERO agents meet constitutional §3 bar ("zero references + AGENT-DELETION-AUTHORIZED marker + 90-day cooling")
- Artifact: `artifacts/windsurf/agent_deprecation_assessment.txt`

### W1–W6 — DEFERRED

Each wave requires its own Author-Gate entry surfacing scope + consumer count. No wave starts without explicit per-wave approval.
