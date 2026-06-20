---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-spine-hardening-7e3b9c.md'
original_relative_path: '_archive\\2026-05\\apps-rg-spine-hardening-7e3b9c.md'
source_sha256: 3aa6346d635bf2b8fe5c792df4c0684d9aeeba6aa61c9ae779c212f8782f1c53
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Spine Hardening — Boundary Correction (T3)

**Slug:** `apps-rg-spine-hardening-7e3b9c`
**Status:** Completed
**Tier:** T3
**Closed:** 2026-05-09
**Type:** Boundary correction + best-practice hardening
**Owner:** Cursor Agent
**Authored:** 2026-05-09

> Harden apps_rg prompt-injection architecture and documentation so it follows the canonical agentic_core spine. Non-renaming, non-parallel-system, behavior-preserving.

## ADG Provenance

```
ADG Provenance: backend=sqlite+redis, snapshot=adg_indexed_05052026_0722.sqlite
Health: status=ok, mode=full, schema_version=1.0
Nodes: 140743, Edges: 863353, graph_projection: available, stale=false
```

## 1. Goal

Make these 11 spine invariants true and test-backed in apps_rg:

1. L1 plans (does NOT assemble provider-ready prompts)
2. L0 routes (does NOT emit PromptBOM/CompiledPromptArtifact)
3. C0 retrieves evidence (data only, never instruction)
4. PA composes and defends the prompt packet (sole authority over CompiledPromptArtifact)
5. Runtime Gates emit live GateVerdict records
6. L5 emits governance certification evidence (NOT runtime disposition)
7. L2 executes the signed compiled artifact
8. L3 only orchestrates managed-workflow step contracts (BYPASSED for apps_rg per spine_manifest)
9. Exit emits exactly one X3 disposition
10. UWG is the only durable write path
11. L6 evaluates only completed-run exhaust

## 2. Non-Goals (will NOT do)

- Rename `agentic_core/L0_routing/reasoning/assembly_stage.py` → PA namespace (deferred — see DEFERRED_SCOPE).
- Rewrite `prompt_governance/` taxonomy.
- Build a parallel prompt system.
- Cross-app spine corrections in `apps_qna`, `apps_research`, `apps_underwriting_ai`.
- Move major folders.

## 3. ADG_HOTSPOT_REPORT

> Per constitutional §22 + `adg-graph-layer-enforcement.md`. Ranked by **PA-boundary impact** (not global centrality — none of apps_rg's files appear in the global top-20 `mv_hotspot_centrality`, which is expected for leaf-app code).

| Rank | Node | adg_name | Layer | Fan-In | Fan-Out | Archetype | 5-Surface | Impact |
|---|---|---|---|---|---|---|---|---|
| 1 | 3157 | `apps_rg/__main__.py` | L_APP | TBD-W1 | 11 (imports) | **ORCHESTRATOR** | Execution + Write | CRITICAL — entrypoint dispatching whole pipeline; line 45 imports `agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run` (the real PA chokepoint) |
| 2 | 33121 | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | L_RUNTIME | TBD-W1 | TBD-W1 | **CENTRAL_DEPENDENCY** | Execution + State + Observability | CRITICAL — actual PA hot path; imported by `apps_rg/__main__.py:45` |
| 3 | 3275 | `apps_rg/prompt_assembly/compiler.py` | L_APP | **0** | TBD-W1 | **CENTRAL_DEPENDENCY** (claimed) | Execution | ⚠️ **AMBIGUOUS** — `mv_graph_reverse_dependency_hotspots` shows zero `imports` fan-in. AGENTIC_SPINE.md claims this is CANONICAL_PA; either dead code or dynamically loaded. **W1 MUST resolve.** |
| 4 | apps_rg/integrations/* | (40 items) | L_APP | TBD-W1 | TBD-W1 | **CENTRAL_DEPENDENCY** | Execution + Egress | HIGH — provider bridges; primary suspect for `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS` |
| 5 | apps_rg/engines/* | (57 items) | L_APP | TBD-W1 | TBD-W1 | **ORCHESTRATOR** (HOP-level) | Execution | HIGH — bullet/narrative engines; primary suspect for `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` |
| 6 | 3155 | `apps_rg/L1_cognition/jd_planner.py` | L_APP | TBD-W1 | TBD-W1 | **CENTRAL_DEPENDENCY** (planning) | Execution | MEDIUM — must verify it emits planning metadata only, not provider-ready messages |
| 7 | apps_rg/scripts/narrative_pass.py | L_APP | TBD-W1 | TBD-W1 | **ORCHESTRATOR** (post-pipeline) | Execution + Egress | MEDIUM — narrative pass operates post-pipeline; risk of bypassing PA |

**Archetype legend:** `CENTRAL_DEPENDENCY` (high fan-in — bad pattern poisons many callers), `ORCHESTRATOR` (high fan-out / `flows_to` density — pattern hides chain failures).

**Layer multipliers note:** apps_rg is `L_APP`. Constitutional §23 multipliers (L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75) do not directly apply to L_APP. Impact ranking above uses **user §1 spine-role criticality** (PA, L2, L1, C0) as the dimension instead.

## 4. ADG_GRAPH_LAYER_EVIDENCE

> Per constitutional §22. ≥3 MVs + semantic edges + P-view cross-references.

### 4.1 Materialized views consulted (W0 + W1 plan)

| MV | W0 evidence | W1 deepening |
|---|---|---|
| `mv_hotspot_centrality` | ✅ Queried — top 20 contains zero apps_rg files (leaf-app, expected); top hotspot is `agentic_core/runtime/contracts/lifecycle_trace_contract.py` (fan_in=106726) — used universally by mixin instrumentation | Re-query scoped to `resolved_path LIKE 'apps_rg/%'` |
| `mv_graph_chokepoint_bridges` | ⏳ W1 | Identify the actual PA chokepoint between `apps_rg/__main__.py` and the runtime pipeline runner |
| `mv_graph_reverse_dependency_hotspots` | ✅ Indirectly — `apps_rg/prompt_assembly/compiler.py` has zero `imports` fan-in (suspicious) | Confirm whether it is dynamically loaded |
| `mv_graph_critical_path_blast_radius` | ✅ Queried — `prompt_assembly/compiler.py` blast_radius=0 (corroborates suspect-dead status) | Re-query for `__main__.py` and `integrated_r4_deterministic_pipeline_run.py` |
| `mv_dependency_cone_risk` | ⏳ W1 | Compute cone risk for the runtime pipeline runner (real PA path) |

### 4.2 Semantic edges to inspect in W1

| Relation | Source | Why |
|---|---|---|
| `flows_to` | `apps_rg/__main__.py` → ? | Trace data flow from CLI args (untrusted) into prompt slots — proves U0 airlock placement |
| `emits_side_effect` | `apps_rg/integrations/*` | Identify provider call sites (LLM egress) — must consume CompiledPromptArtifact, not raw strings |
| `controls_flow` | `apps_rg/reasoning/RgResumeOrchestrator.py` | Confirm orchestrator does not assemble — only dispatches HOPs |
| `resolves_callsite` | `apps_rg/__main__.py:45` → `run_integrated_r4_deterministic_pipeline` | Resolve where PA actually runs at runtime |
| `reads_from`/`writes_to` | `apps_rg/cache/r1a_adapter.py` | Confirm cache adapter does NOT reconstruct prompts on hit |

### 4.3 P-view cross-references

| P-view | Hypothesis | W1 query |
|---|---|---|
| `v_p0_*` | Layer breaks: any apps_rg file directly importing from L4/L5/L6 internals? | Filter rows where `src` LIKE `apps_rg/%` |
| `v_p1_*` | Mis-layered infra: `apps_rg/prompt_assembly/compiler.py` zero callers — is this a P1 zero-caller infra hit? | Likely yes |
| `v_p2_*` | Duplicated/dormant: confirm `apps_rg/prompt_assembly/compiler.py` is dormant (corroborates W0 ADG signal) | Confirms or denies dead-code status |
| `v_p3_*` | Isolated experimental: catch-all for orphaned files in apps_rg | Cross-check against W1 file inventory |

## 5. Two Prompt-Injection Concepts (definitive)

### 5A. Instructional prompt injection (governed composition)

Insertion of: goal · success criteria · task mode · scope · efficiency constraints · evidence binding · reasoning controls · safety rails · output schema · error format · minimality rules.

**Authority:** `agentic_core/mixins/instructional_injection_mixin.py` + YAML corpus (constitutional §_PA).
**Consumed only after:** L0 RouteContract + (C0 FinalEvidenceContract if grounded) + PA compiled artifact + L2 approved bounded work order.

### 5B. Prompt injection defense (boundary protection)

Detection / fencing / neutralization / quarantine / rejection of untrusted content trying to override: system instructions · developer instructions · policy · route · tool selection · provider/model · schema · output format · sandbox/capability scope · write authority · HITL requirements.

**Authority:** PA airlock layer (this plan W4) + `agentic_core/prompt_governance/security/`.

> **Required language (every doc updated by this plan):** "Instructional injection is a governed composition pattern. Prompt injection defense is a boundary protection pattern. They are related but not the same."

## 6. Slot Model (apps_rg PA contract)

Authority order, S0 highest:

| Slot | Content | Authority | Override-able by |
|---|---|---|---|
| S0 | System invariants | HIGHEST | nothing |
| D0 | Fences, scope limits, anti-injection controls | HIGHEST | nothing |
| I0 | Operating instructions, AgentSpec constraints | HIGH | nothing |
| E0 | Approved exemplars | MEDIUM | I0 |
| C0 | Verified evidence (JD, master resume, company brief) | DATA-ONLY | nothing (cannot introduce instructions) |
| M0 | Provider-safe control hints (no CoT disclosure) | MEDIUM | I0 |
| U0 | Neutralized user task intent | DATA-ONLY | cannot override S0/D0/I0/R0 |
| H0 | Bounded repair hints | LOW | cannot widen route/tool/model/schema/policy/evidence/capability/sandbox |
| R0 | Response schema binding | HIGHEST | nothing — cannot be overridden by user/retrieved/tool/model/human |

**Failure modes:**
- Mandatory S0/D0/I0/R0 or must-use C0 cannot fit budget → `PA_BUDGET_OVERFLOW` (fail closed).
- Silent drop of mandatory authority or must-use evidence → forbidden.

## 7. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | W1.P1, W1.P2 | ADG-driven boundary findings sweep across apps_rg | ~12k | ADG green; W0 done | ✅ DONE | `docs/reports/apps_rg/spine_boundary_findings_20260509_055000.md` exists; Tier-A/B/C/D/E classified |
| **W2** | W2.P1, W2.P2 | Doc rewrite: AGENTIC_SPINE.md + new PROMPT_BOUNDARY_CONTRACT.md + THREAT_MODEL.md correction | ~8k | W1 findings | ✅ DONE | All three docs include the canonical ownership table, two-injection-concepts language, dual PA topology section |
| **W3** | W3.P1, W3.P2, W3.P3 | PA boundary code: receipts, `pa_boundary_check()` helper, mixin guard | ~14k | W1 findings; W2 doc anchors | ✅ DONE | `_pa_boundary.py` helper created; receipts emitted at compiler/pa_local/anthropic_rag_entrypoint; 25 contract tests pass |
| **W4** | W4.P1, W4.P2, W4.P3, W4.P4 | Airlocks: U0, C0, tool/model output, HITL re-entry | ~16k | W3 receipts | ✅ DONE | 4 airlock modules implemented; 30 contract tests pass; receipts + audit trail emitted |
| **W5** | W5.P1, W5.P2 | Receipts + OTEL spans (user §10) | ~8k | W3+W4 hooks | ✅ DONE | `_otel_spans.py` helper added; 3 OTEL span types (`pa.airlock_security_pass`, `pa.injection_neutralization`, `pa.unsafe_payload_rejection`) emitted across all 4 airlocks; 15 OTEL contract tests pass |
| **W6** | W6.P1, W6.P2 | Anti-bypass scanner + CI gate registration | ~10k | W3 receipts present | ✅ DONE | `ops_scripts/ci/check_apps_rg_pa_boundary.py` AST scanner created and registered as PA-RG1 in `run_contract_gates.py`; advisory default, fail-closed via `APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1`, bypass via `APPS_RG_PA_BOUNDARY_BYPASS=1`; 7 scanner tests pass |

**Total est. tokens:** ~68k. Within 1M context budget.

**Notion deferral:** Per `notion-plan-wave-deferral.md`, `wave_execution_state.py start --plan apps-rg-spine-hardening-7e3b9c` runs at start of W1; all Notion writes batched at W6 completion.

## 8. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | ADG-driven file inventory | `apps_rg/**/*.py` | 18 dirs, 200+ files; need ADG-scoped queries not grep | ~6k | Not Started |
| W1.P2 | Findings classification | `docs/reports/apps_rg/spine_boundary_findings_<ts>.md` (NEW) | 9 violation classes; some files multi-class | ~6k | Not Started |
| W2.P1 | AGENTIC_SPINE.md rewrite | `apps_rg/AGENTIC_SPINE.md` | 271 lines; preserve route/cache/HOP detail; fix L0/L2/L3/L5 ownership | ~5k | Not Started |
| W2.P2 | New boundary docs | `apps_rg/PROMPT_BOUNDARY_CONTRACT.md` (NEW); update `THREAT_MODEL.md` | First-time spine contract doc; must use required language | ~3k | Not Started |
| W3.P1 | PA receipt emit sites | `apps_rg/prompt_assembly/compiler.py` (or its real successor); call sites in pipeline runner | Resolve W0 ambiguity first | ~5k | Not Started |
| W3.P2 | `pa_boundary_check()` helper | `apps_rg/prompt_assembly/_pa_boundary.py` (NEW) | Pure helper; idempotent; cited by every emit site | ~4k | Not Started |
| W3.P3 | Worker-side mixin guard | `apps_rg/engines/*.py` consumers; mixin entry helper | Mixin must not fire pre-compiled-artifact | ~5k | Not Started |
| W4.P1 | U0 airlock | `apps_rg/__main__.py` wizard path; `apps_rg/prompt_assembly/slot_mapper.py` | "Ignore previous instructions"-class regex; provider/model/schema-override patterns | ~4k | Not Started |
| W4.P2 | C0 evidence airlock | C0 slot in `slot_mapper.py`; JD/resume/brief loaders | Resumes/JDs are PRIME injection vector | ~5k | Not Started |
| W4.P3 | Tool/model output airlock | post-LLM response handlers in HOPs | Tool output cannot widen authority | ~4k | Not Started |
| W4.P4 | HITL re-entry airlock | `apps_rg/hitl/*` (5 files) | Per AGENTIC_SPINE.md HITL=False — verify or harden | ~3k | Not Started |
| W5.P1 | Receipt types + emit sites | `apps_rg/prompt_assembly/_pa_boundary.py`; receipt schema | 12 receipt types per user §10; deterministic digests | ~4k | Not Started |
| W5.P2 | OTEL spans | wrap PA boundary, slot composition, airlock pass, artifact emission, L2 consumption, mixin events | Use existing OTEL helpers from `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | ~4k | Not Started |
| W6.P1 | Scanner | `ops_scripts/ci/check_apps_rg_pa_boundary.py` (NEW) | AST-based: detect provider message arrays, hardcoded prompts, raw-string LLM calls, schema-only-as-prose, retrieved-content-as-instruction; UNKNOWN ≠ PASS | ~6k | Not Started |
| W6.P2 | CI gate registration | `ops_scripts/ci/run_contract_gates.py` (modify) | Advisory default; `APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1` strict; `APPS_RG_PA_BOUNDARY_BYPASS=1` bypass; fail-closed when bypass logged | ~4k | Not Started |

## 9. Files To Inspect (W1)

### Tier A — provider-ready prompt construction risk (CRITICAL)

1. `apps_rg/__main__.py` — entrypoint; CLI args + wizard captures untrusted text
2. `apps_rg/engines/` (57 items) — bullet/narrative/clerk/factcheck engines
3. `apps_rg/reasoning/RgResumeOrchestrator.py` + 19 siblings
4. `apps_rg/scripts/narrative_pass.py` + 33 sibling scripts
5. `apps_rg/integrations/` (40 items) — provider bridges (prime suspect)

### Tier B — L1/L0/C0 ownership drift

6. `apps_rg/L1_cognition/jd_planner.py`
7. `apps_rg/cache/r1a_adapter.py`, `cache/chunk_commit.py`
8. `apps_rg/cert/fec_producer.py`

### Tier C — PA layer self-audit

9. `apps_rg/prompt_assembly/` (17 items) — confirm or refute as canonical PA
10. `apps_rg/prompt_assembly/compiler.py` — resolve W0 ambiguity (dead vs dynamic)
11. `apps_rg/prompt_assembly/slot_mapper.py` — implement S0–R0 from §6
12. `apps_rg/prompt_assembly/provider_request.py` — provider rendering must be PA-internal

### Tier D — L3/L5 ownership language

13. `apps_rg/AGENTIC_SPINE.md` — confirmed needs §0/§8/§9 corrections
14. `apps_rg/spine_manifest.yaml` — verify L3 BYPASSED claim
15. `apps_rg/enforcement/` (2 items) — runtime-disposition language drift
16. `apps_rg/THREAT_MODEL.md` — must distinguish §5A vs §5B
17. `apps_rg/hitl/` (5 items) — verify HITL=False against runtime behavior

### Tier E — shared surface (read-only; §4 wrapper not move)

18. `agentic_core/L0_routing/reasoning/assembly_stage.py` — add PA-ownership contract comment + receipt
19. `agentic_core/L1_cognition/reasoning/prompt_envelope.py` — clarify PA-territory consumed via L1
20. `agentic_core/mixins/instructional_injection_mixin.py` — verify mixin pre-PA guard
21. `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` — **the real PA hot path** per W0 ADG

## 10. Likely Boundary Risks (pre-W1 hypothesis)

| # | Risk | Class | Confidence |
|---|---|---|---|
| R1 | `apps_rg/integrations/` direct provider calls with concatenated strings | `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS` | High |
| R2 | `apps_rg/engines/*` builds prompt strings via f-string before PA | `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` | High |
| R3 | JD/resume content inserted into authority slots without C0 fencing | `VIOLATION_RETRIEVED_CONTENT_AS_INSTRUCTION` | High |
| R4 | Wizard / `--manual-brief` user text not run through U0 airlock | `VIOLATION_USER_TEXT_AUTHORITY_PROMOTION` | High |
| R5 | `apps_rg/L1_cognition/jd_planner.py` may construct final provider messages | `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` | Medium |
| R6 | AGENTIC_SPINE.md line 46 places PA compilation inside L2 E1 | `WARNING_BOUNDARY_COMMENT_ONLY` | Confirmed |
| R7 | Schema instructions in narrative templates expressed only as prose | `VIOLATION_SCHEMA_ONLY_AS_PROSE` | Medium |
| R8 | THREAT_MODEL/RUNBOOK uses "L5 blocks the run" language | `VIOLATION_L5_AS_RUNTIME_DISPOSITION_OWNER` | Medium |
| R9 | `apps_rg/prompt_assembly/compiler.py` is dead code; AGENTIC_SPINE.md fictional CANONICAL_PA reference | `WARNING_BOUNDARY_COMMENT_ONLY` (doc) + needs W3 resolution | High (per W0 ADG fan-in=0) |

## 11. Author-Gate Decisions Foreseen

```
AG_QUEUE_SEED: plan=apps-rg-spine-hardening-7e3b9c id=AG-W3-COMPILER-RESOLUTION depends_on= title=Resolve apps_rg/prompt_assembly/compiler.py status (dead vs dynamic vs adopt-as-real-PA)
AG_QUEUE_SEED: plan=apps-rg-spine-hardening-7e3b9c id=AG-W4-AIRLOCK-STRICTNESS depends_on=AG-W3-COMPILER-RESOLUTION title=U0/C0 airlock strictness (block vs neutralize-and-log) for apps_rg JD/resume content
AG_QUEUE_SEED: plan=apps-rg-spine-hardening-7e3b9c id=AG-W6-SCANNER-COVERAGE depends_on=AG-W3-COMPILER-RESOLUTION title=Scanner coverage scope (apps_rg only vs apps_rg + shared PA surface)
```

User pre-decided execution scope (1A), scanner posture (2A advisory + fail-closed env var), shared-surface relabel (3A receipts only). Remaining AG decisions surface as wave findings demand.

## 12. Acceptance Condition

apps_rg accepted only when this separation is true and test-backed:

> L1 plans · L0 routes · C0 retrieves evidence · PA composes and defends the prompt · Runtime Gates emit live GateVerdicts · L5 certifies governance evidence · L2 executes the signed compiled artifact · L3 only orchestrates managed-workflow step contracts · Exit emits one X3 · UWG alone writes durable state · L6 learns only after the run.

## 13. Deferred Scope

```
DEFERRED_SCOPE: physically move agentic_core/L0_routing/reasoning/assembly_stage.py into agentic_core/prompt_governance/ PA namespace (separate T3 plan; risk-bounded; behavior preserved by §4 wrapper this plan)
DEFERRED_SCOPE: cross-app spine corrections in apps_qna apps_research apps_underwriting_ai apps_lic apps_rfp apps_exec
DEFERRED_SCOPE: rewrite agentic_core/prompt_governance/ taxonomy to align with PA/Runtime-Gates/L5-evidence split
DEFERRED_SCOPE: ADR registry update for the boundary correction (ADR-NNN apps_rg PA ownership ratification)
```

## 14. Plan Marker

```
PLAN_CREATED: slug=apps-rg-spine-hardening-7e3b9c path=.cursor/plans/apps-rg-spine-hardening-7e3b9c.md tier=T3 status=Not Started waves=6
```

## 15. AI Summary

- Target: apps_rg boundary correction across L1/L0/C0/PA/L2/L3/L5/UWG/L6
- Closes blurred ownership: PA owns prompt assembly (not L0), L5 emits evidence (not runtime disposition), L3 orchestrates only when MANAGED_WORKFLOW
- New files: `apps_rg/PROMPT_BOUNDARY_CONTRACT.md`, `apps_rg/prompt_assembly/_pa_boundary.py`, `ops_scripts/ci/check_apps_rg_pa_boundary.py`, `docs/reports/apps_rg/spine_boundary_findings_<ts>.md`
- Edit: `apps_rg/AGENTIC_SPINE.md` (rewrite ownership language); `apps_rg/THREAT_MODEL.md` (distinguish §5A vs §5B); receipts + OTEL spans across PA emit sites; airlock helpers in slot_mapper
- Pattern source: constitutional §22 + adg-graph-layer-enforcement + boundary-enforcement skill. 6 waves, ~68k tokens
- Non-goals: no folder renames; no parallel prompt system; no cross-app changes; no `prompt_governance/` rewrite
- Success: 8+ negative tests pass per user §11; anti-bypass scanner registered as advisory CI gate (NP3-style); zero `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS` in apps_rg
