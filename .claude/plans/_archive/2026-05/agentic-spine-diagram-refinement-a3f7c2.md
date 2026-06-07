---
plan_id: agentic-spine-diagram-refinement-a3f7c2
plan_type: audit
---

# Agentic Spine Diagram Refinement — Sub-Stage Accuracy & L7 HowTrace Fidelity

Extend the agentic spine diagram with accurate sub-categories for every layer (X1, X2, L2 execute, C0 grounding, L5 inline safety) and wire L7 HowTrace to emit per-sub-stage telemetry.

---

## Context (SCQA)

- **Situation** — The agentic spine pipeline runs end-to-end (U0 → L1 → L0 → C0 → L3 → L2 → X1/X2/X3 → L4 → L5 → L6 → L7). A HowTrace JSON artifact is emitted at L7, but it records only flat stage-level entries. The current spine diagram likewise shows only single-node stages for X1 (exit gate), X2, C0 grounding, and L2 execute.

- **Complication** — Sub-stage detail is missing in three places: (1) the diagram does not reflect the 10 X1 gates (X1A–X1J), the 5-step L2 execute sequence, or the 6-step C0 grounding chain; (2) L7 HowTrace is flat and cannot answer "which sub-stage failed / took the most time?"; (3) the semantic cache writeback (D2 learn) is not wired in the R4 entrypoint, so intent vectors are never persisted and future D2 hits are impossible.

- **Question** — How do we extend the spine diagram, L7 HowTrace schema, and cache writeback so that every sub-stage is visible, auditable, and correctly reflected in telemetry?

- **Answer** — Add sub-stage nodes to the diagram, extend the HowTrace schema with a `sub_stages` array per stage entry, instrument each sub-stage boundary with a span/record call, and wire D2 `learn()` after every successful L2 execute.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py` | All 10 X1 gate definitions (X1A–X1J) | ✅ |
| `agentic_core/L2_execution/` (entrypoints + sub-executors) | L2 execute 5-step sequence | ✅ |
| `agentic_core/L0_routing/reasoning/route_gates.py` | D1/D2 cache lookup path | ✅ |
| `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | D2 learn / writeback logic | ✅ |
| `agentic_core/L4_state/cache/gptcache_client.py` | ChromaDB embedding client (intent vector source) | ✅ |
| `agentic_core/L1_cognition/bridges/u0_to_l1_plan.py` | L1 deterministic bridge (no LLM in R4) | ✅ |
| `agentic_core/L5_safety/enforcement/hitl_gate.py` | L5 inline guardrail pattern | ✅ |
| `artifacts/apps_rg/runs/r4_72afb54f/agentic_core_how_trace.json` | Current flat HowTrace output (confirmed gap) | ✅ |
| `.cursor/templates/execution-plan-template.md` | Plan format | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Diagram sub-stage nodes added | Spine diagram only (docs / ASCII / Mermaid) | A | ~8K 🟢 | ✅ DONE |
| Wave 2 | HowTrace schema extended + sub-stage instrumentation | L7 HowTrace JSON schema + stage boundary calls | B | ~20K 🟢 | ✅ DONE |
| Wave 3 | D2 cache writeback wired | R4 entrypoint + semantic_cache_manager learn() | C | ~12K 🟢 | ✅ DONE |
| Wave 4 | Verification — HowTrace artifact re-run shows sub-stage rows | Run R4 + inspect new HowTrace artifact | D | ~6K 🟢 | ✅ DONE |
| Wave 5 | apps_research → apps_rg L3 orchestration wiring | L3 step adapter + apps_rg __main__ dispatch fix | E | ~18K 🟢 | ✅ DONE |

**Total: ~64K tokens across 5 waves, all GREEN**

---

## Out Of Scope

- Changing the routing logic of X1–X3 gates (diagram labels only, no logic change)
- Adding new guardrail rules to L5 safety
- Modifying C0 grounding retrieval strategy
- Retraining or swapping the BGE-M3 embedding model
- Any change to L6 runtime exhaust or learning ledger schema
- ADR authoring (observational plan only)
- Modifying `apps_research` internals (adapter wraps its public interface only)
- Changing `apps_lic` → `apps_research` path (out of scope; only apps_rg path addressed)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Spine diagram — X1 sub-gates (X1A–X1J) | docs/diagrams or inline ASCII | GAP-1 | ~4K | ✅ DONE |
| 1.2 | Spine diagram — L2 execute 5-step + C0 6-step + X2 sub-stages | docs/diagrams or inline ASCII | GAP-2 | ~4K | ✅ DONE |
| 2.1 | HowTrace schema: add `sub_stages` array to stage entry | `agentic_core/L7_*/how_trace*.py` or schema JSON | GAP-3 | ~10K | ✅ DONE |
| 2.2 | Instrument sub-stage boundaries in X1, L2, C0 | `x1_gates.py`, L2 executors, C0 grounding steps | GAP-3 | ~10K | ✅ DONE |
| 3.1 | Wire D2 `learn()` call in R4 entrypoint after successful L2 | R4 entrypoint + `semantic_cache_manager.py` | GAP-4 | ~12K | ✅ DONE |
| 4.1 | Re-run R4; verify HowTrace artifact has sub-stage rows + D2 learn logged | Artifact inspection | — | ~6K | ✅ DONE |
| 5.1 | Fix `apps_rg/__main__.py`: `R3R4_MANAGED` → enter L3 orchestration (not `sys.exit`) | `apps_rg/__main__.py` | GAP-8 | ~8K | ✅ DONE |
| 5.2 | Register L3 step adapter for `apps_research` with full spine envelope | New file: `apps_shared/adapters/research_l3_adapter.py` | GAP-9 | ~10K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: X1 exit gate sub-stages missing from spine diagram**
- The diagram shows a single "X1" node. The actual implementation runs 10 checks: X1A (schema), X1B (confidence), X1C (hallucination), X1D (tool contract), X1E (citation), X1F (latency), X1G (cost), X1H (safety), X1I (rubric bound), X1J (HITL escalation).
- Impact: reviewers cannot trace which gate caused a fail verdict from the diagram alone.

**GAP-2: L2 execute 5-step sequence and C0 6-step grounding chain not reflected**
- L2 execute sub-stages: (1) plan decomposition, (2) tool dispatch, (3) result aggregation, (4) self-critique, (5) output assembly. C0 sub-stages: (1) query normalization, (2) embedding lookup, (3) D1 exact cache probe, (4) D2 semantic cache probe, (5) retrieval augmentation, (6) grounding context assembly.
- Impact: latency and failure attribution is impossible without sub-stage breakdown.

**GAP-3: L7 HowTrace emits flat stage-level entries only**
- Confirmed by inspecting `artifacts/apps_rg/runs/r4_72afb54f/agentic_core_how_trace.json` — no `sub_stages` key present in any stage record.
- Impact: post-run audit cannot determine which sub-stage consumed tokens, triggered a retry, or produced an error.

**GAP-4: D2 semantic cache `learn()` never called in R4 entrypoint**
- `semantic_cache_manager.py` has a `learn(query, response, embedding)` method. The R4 entrypoint calls `recall()` but omits the paired `learn()` after a successful execution.
- Impact: the intent vector corpus never grows; every subsequent run is a D2 cache miss regardless of semantic similarity.

**GAP-5: `apps_qna` product mode (default `build`) runs OUTSIDE the spine**
- `apps_qna/__main__.py` default path calls `run_qna.main()` → `spine_handoff.build_pack_via_spine()`. This emits only a `ValidatedRequest` envelope — no L0 route check, no L2 execution receipt, no Exit eval (X1/X2/X3), no L6 exhaust, no L7 HowTrace.
- The cert mode (`--apps-e2e-live`) IS fully wired via `apps_shared.spine_emission.governed_run`. The live interview mode (`--interview`) is partially wired.
- Impact: the spine diagram shows `apps_qna` as spine-connected but the normal product path is only partially connected (intake validation only). GAP between diagram and reality.

**GAP-6: `apps_research` has no spine wiring**
- No imports of `agentic_core` L-layer components found in `apps_research/`. It runs as a standalone pipeline with no U0 intake, no L0 routing, no Exit eval, no L7 audit.
- Impact: research pipeline is invisible to the spine — no HowTrace, no exit disposition, no cache keys fed back to D1/D2.

**GAP-7: R1B / D2 semantic cache gated behind `SEMANTIC_CACHE_D2_ENABLED=1` env flag (disabled by default)**
- `apps_rg/__main__.py` wraps both R1B recall and R1B store in `if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1"`. In all normal runs the D2 path is dead code.
- Impact: the spine diagram implies D2 semantic cache is an active layer; in practice it is opt-in and off by default for all apps.

**GAP-8: `apps_rg` treats `R3R4_MANAGED` as a stop signal instead of a dispatch signal**
- L0 prerequisite gate correctly returns `L0Route.R3R4_MANAGED` when briefing is missing/stale. But `apps_rg/__main__.py:296-303` reads this and calls `sys.exit(1)` telling the user to manually run `apps_research`.
- `R3R4_MANAGED` is defined as "enters L3 orchestration with ≥1 L2 steps" (`routing_artifact_types.py:433-435`). The intent is L3 dispatches apps_research as step 1, then apps_rg as step 2 — a single managed workflow.
- Impact: broken UX (2+ manual commands), no cross-step audit trail, no briefing quality gate before resume generation. The `R3R4_MANAGED` route exists in the type system but is dead code for this path.

**GAP-9: No L3 step adapter registered for `apps_research`**
- Even if `apps_rg/__main__.py` did enter L3 on `R3R4_MANAGED`, there is no registered L3 step adapter that invokes `apps_research` with a full spine envelope (U0→L1→L0→C0→L2→Exit).
- `apps_lic` has `apps_research_bridge.py` (direct import, no spine). `apps_rg` has `research_facade.py` (raw subprocess, no spine). Neither is an L3-registered adapter.
- Impact: L3 orchestration cannot dispatch `apps_research` as a managed workflow step. Cross-app dispatch is theoretical — the wiring doesn't exist.

---

## Execution Plan

### Phase 1.1 — Spine Diagram: X1 Sub-Gates
**Scope**: Add 10 labeled sub-gate nodes (X1A–X1J) under the X1 exit evaluation stage in the spine diagram.

**Acceptance**: Diagram clearly shows each gate label with its check type (schema / confidence / hallucination / tool contract / citation / latency / cost / safety / rubric / HITL).

### Phase 1.2 — Spine Diagram: L2 Execute + C0 Grounding + X2
**Scope**: Expand L2 execute to 5 sub-steps, C0 grounding to 6 sub-steps, and X2 to its constituent checks in the diagram.

**Acceptance**: Each expanded block is legible with step numbers and short labels.

### Phase 2.1 — HowTrace Schema Extension
**Scope**: Add `sub_stages: list[SubStageRecord]` to the HowTrace stage entry. `SubStageRecord` = `{name, start_ms, end_ms, status, meta}`.

**Commands**:
```bash
# Locate HowTrace schema/dataclass
grep -r "how_trace" agentic_core/ --include="*.py" -l
```

**Acceptance**: HowTrace JSON schema updated; existing stage records remain backward-compatible (sub_stages defaults to `[]`).

### Phase 2.2 — Instrument Sub-Stage Boundaries
**Scope**: Add `record_sub_stage()` calls at entry/exit of each X1 gate check, each L2 execute step, and each C0 grounding step.

**Acceptance**: A test run produces HowTrace with non-empty `sub_stages` arrays for X1, L2, and C0 stage entries.

### Phase 3.1 — Wire D2 Cache Writeback
**Scope**: In the R4 entrypoint, after successful L2 execute, call `semantic_cache_manager.learn(query=intent_text, response=output, embedding=intent_vector)`.

**Commands**:
```bash
# Confirm learn() signature
grep -n "def learn" agentic_core/L4_state/utils/memory/semantic_cache_manager.py
```

**Acceptance**: After one successful run, re-run with semantically similar query and confirm D2 `recall()` returns a hit (cache_hit=True, source=semantic).

### Phase 4.1 — Verification Run
**Scope**: Execute R4 end-to-end and inspect the new HowTrace artifact.

**Commands**:
```bash
# Run R4 (adjust args as needed)
python -m apps_rg
# Then inspect artifact
python -c "import json; d=json.load(open('artifacts/apps_rg/runs/<latest>/agentic_core_how_trace.json')); [print(s['stage'], len(s.get('sub_stages',[]))) for s in d]"
```

**Acceptance**: Every X1, L2, C0 stage entry shows `sub_stages` count > 0; D2 learn log line present.

### Phase 5.1 — Fix `apps_rg/__main__.py`: `R3R4_MANAGED` → L3 orchestration
**Scope**: Replace the `sys.exit(1)` on `R3R4_MANAGED` with an L3 orchestration entry. When the L0 prerequisite gate returns `R3R4_MANAGED`, `apps_rg` must build a 2-step managed workflow plan (step 1: apps_research, step 2: apps_rg) and enter `agentic_core.L3_orchestration` instead of bailing out.

**Target behavior**:
```
L0 gate returns R3R4_MANAGED
  → build L1 plan: [apps_research(company_brief), apps_rg(resume_gen)]
  → enter L3 orchestration with plan
  → L3 dispatches step 1 (apps_research via adapter from Phase 5.2)
  → L3 dispatches step 2 (apps_rg L2 DAG, consuming step 1 output)
  → Exit V6 reviews both steps
  → L6/L7 seal
```

**Files**: `apps_rg/__main__.py` (lines ~285-303), possibly `apps_rg/integrations/spine_handoff.py`

**Acceptance**: Running `python -m apps_rg --target-company "Brown & Brown"` with no briefing on disk does NOT print "run apps_research first" and exit. Instead it runs apps_research as step 1, then apps_rg as step 2, in a single end-to-end invocation.

### Phase 5.2 — Register L3 step adapter for `apps_research`
**Scope**: Create `apps_shared/adapters/research_l3_adapter.py` — an L3-registered step adapter that wraps `apps_research` with a full spine envelope. The adapter must:
1. Accept a structured input (company name, JD path, depth)
2. Invoke `apps_research` via its public interface (not subprocess)
3. Emit U0_sub, L1_sub, L0_sub, C0, L2, Exit receipts for the sub-run
4. Return a structured output (CompanyBrief + artifact paths) to L3
5. Register itself in the L3 step adapter registry so the orchestrator can discover it

**Design constraint**: wraps `apps_research`'s public interface only — does not modify `apps_research` internals. Uses the same pattern as `apps_lic/integrations/apps_research_bridge.py` but adds the spine envelope layer.

**Files**: New: `apps_shared/adapters/research_l3_adapter.py`; may touch `agentic_core/L3_orchestration/` for adapter registration

**Acceptance**: L3 orchestrator can resolve `"apps_research"` as a step type and dispatch it. The sub-run produces `u0_intake_envelope.json`, `l2_execution_receipt.json`, `exit_review_packet.json`, and `company_research.json` under a timestamped run directory.

---

## Rules

- No changes to X1–X3 gate logic — diagram labels and instrumentation only.
- HowTrace `sub_stages` field MUST default to `[]` (backward-compatible).
- D2 learn call MUST be guarded: only on `status == "success"` to avoid poisoning cache with failed outputs.
- Do not modify C0 retrieval strategy or embedding model.

---

## Success Criteria

- [ ] Spine diagram reflects X1 (10 gates), L2 execute (5 steps), C0 grounding (6 steps), X2 sub-checks
- [ ] HowTrace artifact from a real R4 run contains `sub_stages` arrays with >0 entries for X1/L2/C0
- [ ] D2 semantic cache `learn()` is called after every successful L2 execute
- [ ] A second semantically-similar run produces a D2 cache hit
- [ ] No existing tests broken

---

## Rollback Strategy

If things go wrong:
1. HowTrace schema change is additive — revert `sub_stages` key; existing consumers see no change (key absent = `[]`).
2. D2 learn call — remove the single `learn()` call from R4 entrypoint; no data is deleted from ChromaDB on rollback.
3. Diagram changes are doc-only — revert to previous diagram file.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| HowTrace sub_stages populated | >0 entries for X1, L2, C0 | Inspect artifact JSON |
| D2 cache hit on repeat run | cache_hit=True, source=semantic | Log line in route_gates.py |
| Diagram sub-stage count | X1=10, L2=5, C0=6, X2≥2 | Visual review of diagram |
| Backward compatibility | Zero existing test failures | pytest tests/ |

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
