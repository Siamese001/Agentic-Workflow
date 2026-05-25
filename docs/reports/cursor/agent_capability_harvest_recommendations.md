# Agent Capability Harvest — Recommendations (Executive)

**Date:** 2026-05-25  
**Model:** [agent_capability_decision_model.md](agent_capability_decision_model.md)  
**Matrix:** [agent_capability_decision_matrix.json](agent_capability_decision_matrix.json) (118 rows)  
**Plan:** [agent-capability-spine-harvest-e8f4a2.md](../../.cursor/plans/agent-capability-spine-harvest-e8f4a2.md)

---

## Bottom line

The 118 `*Agent` classes are **not** missing from the product spine because of a wiring bug. W3 live proof and import-closure trace show **0/118** in spine closure and **0** artifact-proven runtime invocation. The valuable question is not "how do we mount agents on the spine?" but **which algorithms deserve extraction** into engines, profiles, judge panel adapters, or CI — and which shells should be deleted.

**Recommended posture:** Harvest **6** capabilities now (Tier A), pilot **2** judge panel adapters (Tier B), delete **16** dead/orphan shells (Tier D), and treat **66** as CI/Ops sidecars unless a product owner revives them with ADR + proof.

---

## Strategic recommendations (ordered)

### R1 — Do not reinstate agent classes on the product spine

ADR-088 and W3 evidence stand. Any future "agent leverage" must use P2–P5 patterns (engine, profile, panel adapter, app callable). P1 (`SPINE_FUNCTION_EXTENSION` with `*Agent` classes) requires explicit ADR amendment and live `invoked_class` proof.

### R2 — Execute Tier A harvest (6 agents → 3 spine touchpoints)

| Touchpoint | Agents | Action |
|------------|--------|--------|
| **L0 route gates** | `SemanticGatekeeperAgent`, `AutonomyGuardianAgent`, `SSOTFolderCleanupAgent` | Extract policy functions into `route_gates` / gate profiles; remove agent constructors from hot path |
| **C0 retrieval profile** | `EmbeddingSovereignAgent`, `SovereignRAGManager`, `RedisSovereignAgent` | Bind embedding/cache/RAG policy to U0 profile + existing semantic cache manager; delete sovereign agent entrypoints |

**Proof:** Unit tests on gate util + profile loader; spine import graph still has **0** `*Agent` modules.

### R3 — Judge panel pilot (7 candidates → 2 pilots)

Candidates: `AdversarialProbeAgent`, `AdversarialRedTeamerAgent`, `SafetyInspectorAgent`, `RedTeamAgent`, `GenerativeGuardAgent`, `ConstitutionalReviewerAgent`, `BoundaryTestingAgent`.

**Pilot:** Convert rubric checks from **two** lowest fan-in agents into `JudgeProviderAdapter` implementations under `agentic_core/runtime/judges/panel/`. Wire via `apps_rg` x1d panel bridge only — not L5 class mount.

**Proof:** Real provider panel run with adapter IDs in `x1d_llm_judge_outputs.json` manifest.

### R4 — FCA deprecation wave (conditional on user ops)

`FileClassificationHealerAgent` / monolith `FileClassificationAgent.py` are **Tier D** for the class shell; `file_classification/*` rules move to **P7** CI (ADG + structure blueprint).

**Blocker:** Confirm no production dependency on manual heal scripts. If scripts still run weekly, keep P7 sidecar until CI parity, then P9 delete shell.

### R5 — Orphan burndown (12 + shims)

Delete or archive all `ORPHAN_NO_REF` modules and `RootCustomsAgent` shim per deferred plan W4. ADG fan-in check before each delete.

### R6 — Integrity gate generalization (1 apps_rg reference)

`IntegrityGateExecutorAgent` is the only apps_rg typing reference. Generalize to `runtime/gates/integrity_gate_executor.py` util; apps inject via profile/validator — **P4**, not spine agent.

### R7 — Managed workflow fork (7 agents)

DAG/orchestration agents (`DomainPlannerAgent`, `DagEngineAgent`, `UnifiedAgent`, etc.) map to **P6**. **Default:** archive unless product roadmap commits to `MANAGED_WORKFLOW` spine branch. Do not merge into integrated single-action spine without ADR.

### R8 — Keep Tier C as documented CI inventory (76)

No bulk delete. Tag in matrix as `P7_CI_OPS` with burndown priority from ADG hotspot report. Reduces surprise when ops scripts import L5 heal agents.

---

## What NOT to do

| Anti-pattern | Why |
|--------------|-----|
| "Wire agents into spine for discoverability" | Violates ADR-088; confuses taxonomy with runtime |
| Keep 5k-line FCA because "we might need it" | Logic lives in subpackage + ADG; shell adds maintenance |
| Move L5 heal agents to L2 "to use them" | Wrong layer gravity; use P7 or extract pure utils |
| Bulk delete Tier C without importer check | 76 rows include ops_script consumers |

---

## Wave mapping (see plan)

| Wave | Deliverable |
|------|-------------|
| W0 | Model + matrix published (this session) |
| W1 | Tier D deletes + ADR-089 harvest charter |
| W2 | Tier A L0 + C0 extracts |
| W3 | Judge panel 2-adapter pilot |
| W4 | FCA extract + shell delete (gated) |
| W5 | Matrix regen + `ARTIFACT_PROVEN=0` re-proof |

---

## Metrics to track

| Metric | Baseline | Target after W5 |
|--------|----------|-----------------|
| Spine closure `*Agent` modules | 0 | 0 |
| `ARTIFACT_PROVEN` agent invocations | 0 | 0 |
| Tier A agents still as classes | 6 | 0 (logic in P2/P3) |
| ORPHAN_NO_REF modules | 12 | 0 |
| Monolith LOC (FCA) | ~5700 | 0 (archived) |
