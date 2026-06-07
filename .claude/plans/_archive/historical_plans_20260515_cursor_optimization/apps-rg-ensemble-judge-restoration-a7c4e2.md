---
plan_id: apps-rg-ensemble-judge-restoration-a7c4e2
plan_type: refactor
status: ARCHIVED_SUPERSEDED
archived_at: "2026-05-11T09:40:00Z"
archived_reason: "Superseded by apps_rg zip-based full-spine implementation audit."
superseded_by: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2
active_authority: false
preserve_for: "historical reference and implementation detail only"
do_not_execute_directly: true
next_authority: ".windsurf/plans/apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2.md"
---

> **ARCHIVAL NOTICE (2026-05-11)**
>
> This plan is **ARCHIVED_SUPERSEDED**. It is no longer the active sequencing authority for `apps_rg` implementation work.
>
> - **Reason**: Superseded by a zip-based apps_rg full-spine implementation audit that determines the true next implementation unit across U0, L1, L0, C0, PA, L3, L2, Exit, runtime gates, judges, L6, UWG, tests, and receipts.
> - **Waves 1, 2, 2.5**: Completed and their artifacts remain valid.
> - **Waves 3–8**: NOT executed under this plan. May be referenced as implementation detail by the successor plan.
> - **Do not execute directly**: Any future implementation must be sequenced by the new zip-based full-spine audit plan.
> - **Receipt**: `artifacts/apps_rg/apps_rg_w3_plus_archival_receipt.json`

# Restore apps_rg Per-Section Ensemble + Judge Pipeline

Restore the quarantined per-section ensemble generation and multi-judge selection behavior for `apps_rg` resume generation through the agentic core spine, preserving the normal L0 cache hierarchy and using registry-resolved managed workflow dispatch.

---

## Context (SCQA)

- **Situation** — `apps_rg` pipeline currently produces resumes via a single monolithic Qwen LLM call in L2. The old standalone pipeline had 7 per-section HOPs, each generating 3 candidates at different temperatures, gating each candidate with quality checks, and selecting a winner via a multi-provider judge jury. That code was quarantined under AG-RGGOV-8 (ingress-only governance) but preserved in `apps_rg/integrations/hops/` and `apps_rg/integrations/gates/per_cand_resume_gates.py`.
- **Complication** — The quarantine correctly moved runtime execution authority to core, but core never implemented the ensemble+judge replacement. The monolithic call produces lower-quality resumes: no per-section length control, no candidate competition, no quality gates, no judge selection.
- **Question** — How do we restore per-section ensemble+judge quality while keeping `agentic_core` app-agnostic and `apps_rg` ingress-only?
- **Answer** — Add a generic ENSEMBLE_MODEL lane to core L2 (executes one bounded node at a time), a generic workflow runner to L3 (sequences section nodes from a manifest), and a registry-resolved workflow dispatch path to L0 (evaluated only after R1A/R1B/R5 cache checks miss). `apps_rg` supplies the manifest, prompt variants, gate configs, judge rubrics, and provider profiles as declarative config — never runtime authority.

---

## Architecture — Correct Pipeline Flow

**Runtime path (current run, produces user-visible output):**
```
U0 → L1 (work-shape hints)
  → L0: R1A actual exact cache lookup → hit? → return cached result
  → L0: R1B actual semantic cache lookup → hit? → return cached result
  → L0: R5 fallback check → hit? → return fallback
  → L0: R1A/R1B/R5 all MISS (cache-miss receipts in RouteContract evidence)
  → L0: evaluate execution_form from L1 work-shape hints
  → L0: if MANAGED_WORKFLOW → deterministic registry resolution (fail closed if 0 or >1)
  → C0 evidence retrieval → FinalEvidenceContract
  → PA prompt assembly
  → L3 sequences section nodes from resolved manifest
  → L2 executes each section node through generic ENSEMBLE_MODEL lane
  → L3 merges sealed section artifacts into SealedWorkflowPackage
  → Exit performs final evaluation
  → Exit emits exactly one X3DispositionReceipt (X3D_ALLOW_FINISH)
  → User-visible resume returned
```

**Post-runtime learning/writeback path (after run boundary, never blocks user output):**
```
RuntimeExhaustBundle (captures route, sealed result, evidence, disposition refs)
  → L6 writeback_proposer evaluates policies
  → Creates FutureRunPromotionRequest(s) — inert proposals, not writes
  → UWG admits or blocks each request independently
  → L4 stores only admitted records (R1A cache, R1B semantic cache, C0 evidence artifacts, index)
  → Future L0 can hit R1A/R1B; future C0 can reuse cached evidence
```

**Ownership boundary:**
- `agentic_core` owns: ManagedWorkflowSpec, workflow registry resolver, L3 workflow runner, generic L2 ENSEMBLE_MODEL lane, CandidateArtifact schema, candidate gate runner, judge interface, EnsembleSelectionReceipt, OTEL/replay/receipts
- `apps_rg` owns: workflow manifest, section list, prompt variants, resume gates, judge rubrics, provider profiles, merge rules, final resume schema, legacy HOP adapters during migration

---

## Hard Constraints

1. No `if app == "apps_rg"` in core execution logic.
2. No resume section names in core execution logic.
3. No Qwen, Anthropic, OpenAI, or Gemini hardcoding in core.
4. No NarrativeJudgeScorer hardcoding in core.
5. No direct CLI → L2 bypass.
6. No L2 → user output bypass.
7. Exit emits exactly one X3DispositionReceipt (X3D_ALLOW_FINISH for success). Exit must never write cache, vector store, or evidence directly — that is a current-runtime defect to remove. Exit has no role in writeback.
8. UWG remains the only durable write path. L6 writeback_proposer creates inert FutureRunPromotionRequests post-runtime — UWG admits or blocks — L4 performs durable storage.
9. L3 owns multi-hop sequencing. L2 executes one bounded node at a time.
10. R1A/R1B/R5 cache checks happen BEFORE managed workflow evaluation.
11. Managed workflow selection is NOT automatic from app_context — it requires work-shape hint evaluation + registry resolution.
12. Fail closed if: zero workflows resolve, multiple resolve, registry digest mismatch, manifest references unregistered lane, ENSEMBLE_MODEL lacks required gate/judge profile, all candidates fail deterministic gates with no repair policy.
13. L0 reads cache only. L0 must not write cache.
14. L2 must not write cache. L3 must not write cache.
15. Cache writeback (R1A exact, R1B semantic) happens only through L6 writeback_proposer → FutureRunPromotionRequest → UWG → L4 (post-runtime, never during current run).
16. Cache writeback must never happen before Exit clears the final result.
17. UWG is the only durable write path for cache records, C0 evidence artifacts, and index metadata.
18. C0 may retrieve and emit FinalEvidenceContract but must not write L4 directly or silently create durable briefing state.
19. Missing briefing does not justify bypassing C0 or direct apps_rg local retrieval outside the spine.
20. Retrieved text remains data only and must not become instruction.
21. C0 evidence writeback stores reusable support artifacts, not authoritative business truth. Authority review is required before any retrieved content becomes durable truth.
22. In generic core contracts, use `app_context` or `owner_ref` — never `app_id` — to avoid implying app-specific branching.
23. The current Exit defect (direct Redis semantic cache write, direct Chroma collection write) MUST be removed as Wave 8 prerequisite. This is not a pattern to preserve.
24. User-visible resume output returns with X3D_ALLOW_FINISH. Cache/evidence writeback is a completely separate post-runtime path: RuntimeExhaustBundle → L6 writeback_proposer → FutureRunPromotionRequest → UWG → L4. Exit has zero involvement in writeback. No mixing of runtime output and durable writes.
25. If managed workflow registry resolution or manifest loading fails AFTER L0 selected MANAGED_WORKFLOW, the run fails closed (RouteRejected / Exit failure). No silent fallback to SINGLE_STEP.
26. R1A actual cache lookup must complete (not just eligibility markers) before L0/dispatch can enter L3. R1B actual cache lookup must complete before L3 entry. Cache-miss receipts must be present in RouteContract evidence before MANAGED_WORKFLOW proceeds.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/integrations/hops/` (quarantined code) | Original prompt variants, ensemble structure, meta-prompt defense | ✅ Read |
| `apps_rg/integrations/gates/per_cand_resume_gates.py` | Original per-candidate quality gates (10+ gates) | ✅ Read |
| `agentic_core/L3_orchestration/managed_workflow_router.py` | Existing ManagedWorkflowEngine scaffold | ✅ Read |
| `agentic_core/L3_orchestration/exit_eval/judges/` | Existing judge adapters (Qwen/Anthropic/OpenAI/Gemini) | ✅ Read |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | Current monolithic L2 execution | ✅ Read |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | Current L0 with R1A/R1B/R3/R4 cache eligibility | ✅ Read |
| `agentic_core/L1_cognition/apps_rg_l1_binding.py` | Current L1 plan contract emission | ✅ Read |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | Current dispatch chain (U0→L1→L0→C0→PA→L2→Exit) | ✅ Read |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens | Status |
|-------|--------|-------|------------|---------|--------|
| Wave 1 | Core contracts + schemas | Generic ensemble/workflow/judge/receipt types | A | ~30K | ✅ DONE |
| Wave 2 | L0 work-shape evaluation + registry | Cache-first routing, work-shape hints from L1, registry resolver | B | ~25K | ✅ DONE |
| Wave 2.5 | U0 RuntimeCustomizationPackage reconciliation | 24-field package on contract, schema, field map; U0 flow-through verified | B+ | ~15K | ✅ DONE |
| Wave 3 | L3 workflow runner | Generic managed-workflow orchestrator for section-based flows | C | ~30K | 🔲 TODO |
| Wave 4 | L2 ENSEMBLE_MODEL lane | Generic per-node multi-candidate generation + gating + judging | D | ~40K | � TODO |
| Wave 5 | apps_rg manifest + config | Section definitions, prompt variants, gate configs, judge rubrics, provider profiles | E | ~30K | � TODO |
| Wave 6 | Dispatch rewiring + Exit | Dispatch branches on execution_form, exit merges sections → X3 | F | ~25K | � TODO |
| Wave 7 | Tests + parity verification | Parity, anti-regression, E2E, fail-closed | G | ~20K | � TODO |
| Wave 8 | Cache + C0 governed writeback | R1A/R1B cache writeback via Exit→UWG→L4; C0 evidence writeback via Exit→UWG→L4 | H | ~30K | � TODO |

**Total: ~230K tokens across 8 waves, all GREEN**

---

## Out Of Scope

- Modifying any other `apps_*` pipeline routing (unless they explicitly register a managed workflow)
- Adding new cloud LLM provider adapters beyond existing (Anthropic/OpenAI/Qwen/Gemini judges)
- Healing tiers / reroute logic for failed judges
- Modifying the `apps_rg` CLI/wizard interface
- R1A/R1B/R5 cache read-path implementation changes (read path is unchanged; governed writeback path is IN scope)
- UWG admission policy authoring (UWG writeback contracts and flow are in scope; admission logic itself is a separate plan)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | CandidateArtifact + EnsembleSelectionReceipt | `agentic_core/runtime/contracts/ensemble_types.py` | Greenfield | ~8K | 🔲 TODO |
| 1.2 | ManagedWorkflowSpec + SectionNode | `agentic_core/runtime/contracts/workflow_manifest_types.py` | Generic, no app names | ~8K | 🔲 TODO |
| 1.3 | JudgeResult + JudgeJuryResult + CandidateGateResult | `agentic_core/runtime/contracts/judge_types.py` | Reuse existing JudgeResponse shape | ~8K | 🔲 TODO |
| 1.4 | SealedSectionArtifact + SealedWorkflowPackage | `agentic_core/runtime/contracts/sealed_workflow_types.py` | Container for per-section seals | ~6K | 🔲 TODO |
| 2.1 | L1 work-shape hints on L1PlanContract | `agentic_core/L1_cognition/apps_rg_l1_binding.py`, `agentic_core/runtime/contracts/l1_plan_contract.py` | Add hint fields | ~8K | 🔲 TODO |
| 2.2 | L0 cache-first + shape evaluation | `agentic_core/L0_routing/apps_rg_l0_binding.py` | R1A/R1B/R5 before shape decision | ~10K | 🔲 TODO |
| 2.3 | Workflow registry resolver | `agentic_core/L3_orchestration/workflow_registry.py` | Deterministic resolution, fail-closed | ~7K | 🔲 TODO |
| 3.1 | L3 ManagedWorkflowRunner | `agentic_core/L3_orchestration/managed_workflow_runner.py` | Sequences nodes, collects seals, merges | ~18K | 🔲 TODO |
| 3.2 | L3 section merge engine | `agentic_core/L3_orchestration/section_merge_engine.py` | App-supplied merge strategy | ~12K | 🔲 TODO |
| 4.1 | L2 ENSEMBLE_MODEL lane | `agentic_core/L2_execution/ensemble_lane.py` | Multi-candidate gen, provider-profile dispatch | ~18K | 🔲 TODO |
| 4.2 | Candidate gate runner | `agentic_core/L2_execution/candidate_gate_runner.py` | Gate registry, fail-closed on all-fail | ~10K | 🔲 TODO |
| 4.3 | Judge jury runner | `agentic_core/L2_execution/judge_jury_runner.py` | Multi-provider scoring, selection policy | ~12K | 🔲 TODO |
| 5.1 | apps_rg workflow manifest YAML | `apps_rg/config/workflow_manifest.yaml` | Section list + ordering + profiles | ~5K | 🔲 TODO |
| 5.2 | apps_rg prompt variant configs | `apps_rg/config/section_prompts/` (7 files) | Port from quarantine | ~15K | 🔲 TODO |
| 5.3 | apps_rg per-candidate gate configs + functions | `apps_rg/config/candidate_gates.yaml`, `apps_rg/gates/per_candidate.py` | Pure functions | ~8K | 🔲 TODO |
| 5.4 | apps_rg judge rubric configs | `apps_rg/config/judge_rubrics/` (4 files) | Scoring dimensions | ~5K | 🔲 TODO |
| 5.5 | apps_rg provider profiles | `apps_rg/config/provider_profiles.yaml` | Generator + judge provider configs | ~3K | 🔲 TODO |
| 6.1 | Dispatch branch on execution_form | `agentic_core/runtime/entry/apps_rg_dispatch.py` | MANAGED_WORKFLOW → L3 path | ~10K | 🔲 TODO |
| 6.2 | Exit merge + final evaluation | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | SealedWorkflowPackage → X3 | ~10K | 🔲 TODO |
| 6.3 | RouteContract extension | `agentic_core/runtime/contracts/route_contract.py` | workflow_ref field | ~5K | 🔲 TODO |
| 7.1 | Parity tests | `tests/_apps_contract/test_apps_rg_ensemble_parity.py` | Section quality parity | ~8K | 🔲 TODO |
| 7.2 | Anti-regression tests | `tests/_apps_contract/test_other_apps_unaffected.py` | No route contamination | ~5K | 🔲 TODO |
| 7.3 | Fail-closed tests | `tests/_apps_contract/test_managed_workflow_fail_closed.py` | Registry failures | ~5K | 🔲 TODO |
| 7.4 | Integration smoke test | `tests/_apps_contract/test_apps_rg_managed_workflow_e2e.py` | Full pipeline E2E | ~5K | 🔲 TODO |
| 7.5 | Cache writeback separation tests | `tests/_apps_contract/test_cache_writeback_uwg_only.py` | L0 read vs Exit→UWG write | ~5K | 🔲 TODO |
| 7.6 | C0 writeback separation tests | `tests/_apps_contract/test_c0_writeback_uwg_only.py` | C0 retrieve-only vs Exit→UWG writeback | ~5K | 🔲 TODO |
| 8.1 | R1A/R1B CacheCommitRequest contract | `agentic_core/runtime/contracts/cache_commit_types.py` | X3C shape for cache writeback | ~8K | 🔲 TODO |
| 8.2 | C0 EvidenceCommitRequest contract | `agentic_core/runtime/contracts/evidence_commit_types.py` | X3C shape for C0 writeback | ~6K | 🔲 TODO |
| 8.3 | Exit cache/C0 commit emission | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Emit X3C CommitRequests alongside X3 | ~10K | 🔲 TODO |
| 8.4 | apps_rg cache/freshness policy | `apps_rg/config/cache_writeback_policy.yaml`, `apps_rg/config/c0_writeback_policy.yaml` | TTL, freshness, eligibility | ~6K | 🔲 TODO |

---

## Gap Register

**GAP-1: L1PlanContract lacks work-shape hints**
- L1 currently emits `grounding_required`, `model_generation_required`, `write_authority_present` — no multi-step or ensemble hints.
- Impact: Must add `multiple_work_units_hint`, `merge_required_hint`, `per_unit_quality_selection_hint`, `candidate_generation_expected_hint` to L1PlanContract.

**GAP-2: L0 does not evaluate execution_form from L1 hints**
- L0 currently hardcodes `execution_form = "single_step"` (or `"managed_workflow"` only via env var opt-in).
- Impact: Must add deterministic shape rules that evaluate L1 hints ONLY after R1A/R1B/R5 cache checks miss.

**GAP-3: No workflow registry resolver**
- `managed_workflow_router.py` has a `ManagedWorkflowEngine` with in-memory workflow registration but no deterministic multi-field resolution (app_context + task_class + capability + policy_hash + registry_digest).
- Impact: Need a proper registry resolver that fails closed on zero/multiple matches or digest mismatch.

**GAP-4: L2 has no generic ENSEMBLE_MODEL lane**
- `apps_rg_l2_binding.py` makes one LLM call via vLLM and returns one SealedL2Artifact.
- Impact: Need a lane that generates N candidates via provider profile, gates them, judges them, selects winner, seals — all for one bounded section node.

**GAP-5: No SealedWorkflowPackage contract**
- Current pipeline produces one `SealedL2Artifact` for the whole resume. Multi-section needs a container.
- Impact: New contract type required.

**GAP-6: RouteContract lacks workflow_ref field**
- L0 currently emits `execution_form` but not a concrete workflow reference resolved from registry.
- Impact: Must add `workflow_ref` field populated by registry resolution.

**GAP-7: No governed cache writeback path**
- Pipeline has no mechanism for Exit to request cache writeback after successful completion. L0 reads cache; nothing writes it back.
- Impact: Must add `R1ACacheCommitRequest` and `R1BSemanticCacheCommitRequest` contracts, Exit emission logic, and UWG→L4 writeback flow. L0/L2/L3 must remain read-only.

**GAP-8: No governed C0 evidence writeback path**
- C0 retrieves and emits `FinalEvidenceContract` but has no path to write reusable evidence artifacts (briefing packets, citation maps, embedding indices) back to durable storage.
- Impact: Must add `C0EvidenceCommitRequest` contract, Exit emission logic, and UWG→L4 writeback flow. C0 must remain retrieve-only.

---

## Execution Plan

### Wave 1 — Core Contracts + Schemas (all generic, no app names)

**Phase 1.1 — CandidateArtifact + EnsembleSelectionReceipt**

New file: `agentic_core/runtime/contracts/ensemble_types.py`

```python
@dataclass(frozen=True)
class CandidateArtifact:
    candidate_id: str
    node_id: str          # section node this candidate belongs to
    variant_ref: str      # prompt variant that produced this candidate
    text: str
    temperature: float
    provider_profile: str # registry key — NOT a model name
    generation_timestamp: str
    generation_digest: str
    gate_results: tuple[CandidateGateResult, ...]
    gates_passed: bool
    judge_results: tuple[JudgeResult, ...]
    final_score: float
    selection_rank: int

@dataclass(frozen=True)
class EnsembleSelectionReceipt:
    node_id: str
    winner_candidate_id: str
    winner_digest: str
    selection_policy: str
    selection_reason: str
    candidate_count: int
    passed_gate_count: int
    judged_count: int
    all_candidates_digest: str  # hash over all candidate digests
    receipt_timestamp: str
```

**Acceptance**: Types importable, JSON-serializable, zero app-specific names.

---

**Phase 1.2 — ManagedWorkflowSpec + SectionNode**

New file: `agentic_core/runtime/contracts/workflow_manifest_types.py`

```python
@dataclass(frozen=True)
class SectionNode:
    node_id: str
    node_type: str        # "ensemble_generate" | "passthrough" | "merge"
    tier: str             # "critical" | "medium" | "low"
    depends_on: tuple[str, ...] = ()
    candidate_count: int = 3
    generator_profile: str = ""     # provider-profile registry key
    temperature_profile: tuple[float, ...] = ()
    prompt_variant_refs: tuple[str, ...] = ()
    candidate_gate_profile: str = "" # gate config ref
    judge_profile: str = ""          # judge rubric ref
    selection_policy: str = "highest_mean"
    archive_policy: str = "all_candidates"

@dataclass(frozen=True)
class ManagedWorkflowSpec:
    manifest_id: str
    app_id: str
    task_class: str
    sections: tuple[SectionNode, ...]
    merge_strategy: str          # "sequential_concat" | "schema_assembly"
    final_gate_profile: str = ""
    registry_digest: str = ""    # sha256 of manifest bytes for tamper detection
    schema_version: str = "1.0"
```

**Acceptance**: Manifest loadable from YAML, typed, frozen, no app-specific names in field types.

---

**Phase 1.3 — JudgeResult + JudgeJuryResult + CandidateGateResult**

New file: `agentic_core/runtime/contracts/judge_types.py`

```python
@dataclass(frozen=True)
class JudgeResult:
    judge_id: str           # provider-profile registry key — NOT a provider name
    score: float            # 0.0 – 1.0
    reasoning: str
    latency_ms: int
    abstained: bool = False
    error: str = ""

@dataclass(frozen=True)
class JudgeJuryResult:
    node_id: str
    candidate_id: str
    judge_results: tuple[JudgeResult, ...]
    mean_score: float
    consensus: bool
    selection_policy_applied: str

@dataclass(frozen=True)
class CandidateGateResult:
    gate_id: str
    passed: bool
    reason: str
    params_used: Mapping[str, Any] = field(default_factory=dict)
```

**Acceptance**: All contracts importable, zero provider names.

---

**Phase 1.4 — SealedSectionArtifact + SealedWorkflowPackage**

New file: `agentic_core/runtime/contracts/sealed_workflow_types.py`

```python
@dataclass(frozen=True)
class SealedSectionArtifact:
    node_id: str
    winner_text: str
    winner_digest: str
    ensemble_receipt_digest: str
    sealed_at: str
    l5_certification_ref: str

@dataclass(frozen=True)
class SealedWorkflowPackage:
    package_id: str
    run_id: str
    trace_id: str
    app_id: str
    workflow_ref: str
    sections: tuple[SealedSectionArtifact, ...]
    package_digest: str
    merge_strategy: str
    sealed_at: str
    l5_certification_ref: str
```

**Acceptance**: All contracts importable, JSON-serializable.

---

### Wave 2 — L0 Work-Shape Evaluation + Registry

**Phase 2.1 — L1 work-shape hints**

Modify: `agentic_core/runtime/contracts/l1_plan_contract.py`
- Add optional hint fields to `L1PlanContract`:
  - `multiple_work_units_hint: bool = False`
  - `merge_required_hint: bool = False`
  - `per_unit_quality_selection_hint: bool = False`
  - `candidate_generation_expected_hint: bool = False`

Modify: `agentic_core/L1_cognition/apps_rg_l1_binding.py`
- Set all four hints to `True` for `task_class="resume_generation"` when generation_mode is not validation-only.
- These are HINTS, not directives — L0 evaluates them.

**Acceptance**: L1PlanContract carries work-shape hints. No routing authority in L1.

---

**Phase 2.2 — L0 cache-first + shape evaluation**

Modify: `agentic_core/L0_routing/apps_rg_l0_binding.py`

Correct ordering inside `l0_route_apps_rg()`:

```
1. Compute cache_eligibility (R1A, R1B, R3, R4) — unchanged
2. If R1A eligible → set execution_form = "cache_hit_r1a" → return early
3. If R1B eligible → set execution_form = "cache_hit_r1b" → return early
4. If R5 fallback eligible → set execution_form = "cache_hit_r5" → return early
5. All terminal routes MISS → evaluate work-shape hints from L1PlanContract:
   - If multiple_work_units_hint AND candidate_generation_expected_hint:
     execution_form = "managed_workflow"
   - Else: execution_form = "single_step"
6. If managed_workflow → resolve workflow_ref via registry:
   (app_context + task_class + capability + execution_form + policy_hash + registry_digest_set)
   → must resolve exactly one workflow
   → fail closed on zero, multiple, or digest mismatch
7. Emit RouteContract with execution_form and workflow_ref
```

Note: R1A/R1B/R5 "eligibility" today marks which cache tiers to check — actual cache lookup happens at dispatch time. The key correction is that `execution_form` is decided AFTER the cache eligibility markers are set, not before. The dispatch checks the actual caches using these markers before proceeding to L3/L2.

**Acceptance**: L0 never selects MANAGED_WORKFLOW before cache check completion. Workflow ref resolved deterministically. Fail-closed on ambiguity.

---

**Phase 2.3 — Workflow registry resolver**

New file: `agentic_core/L3_orchestration/workflow_registry.py`

```python
class WorkflowRegistry:
    def resolve(
        self,
        app_context: str,
        task_class: str,
        capability: str,
        execution_form: str,
        policy_hash: str,
    ) -> ResolvedWorkflow:
        """Deterministic resolution. Fail-closed.

        Raises:
            WorkflowResolutionError if zero, multiple, or digest mismatch.
        """

    def register(self, manifest_path: Path) -> str:
        """Register a manifest. Returns registry_digest."""

    def validate_manifest(self, spec: ManagedWorkflowSpec) -> list[str]:
        """Return list of validation errors. Empty = valid.

        Checks:
        - All SectionNode.generator_profile exist in provider registry
        - All SectionNode.candidate_gate_profile exist in gate registry
        - All SectionNode.judge_profile exist in judge rubric registry
        - No unregistered lane references
        """
```

**Acceptance**: Registry loads manifests from app config dirs. Resolution is deterministic and fail-closed.

---

### Wave 3 — L3 Workflow Runner

**Phase 3.1 — L3 ManagedWorkflowRunner**

New file: `agentic_core/L3_orchestration/managed_workflow_runner.py`

L3 sequences the managed workflow. L2 executes each section node through a generic ENSEMBLE_MODEL lane.

Responsibilities:
- Receive resolved `ManagedWorkflowSpec` + route + evidence from dispatch
- Topologically sort sections on `depends_on`
- For each section node: call L2 ENSEMBLE_MODEL lane → receive `SealedSectionArtifact`
- If a section fails and tier="critical" → fail the workflow
- If a section fails and tier="medium"/"low" → skip, log warning
- Collect `SealedSectionArtifact` per section
- Call merge engine to produce `SealedWorkflowPackage`
- Emit OTEL spans per section: `l3.workflow.section.{node_id}`
- Persist intermediate results to run directory
- GENERIC — reads config from the spec, never checks section names

**Acceptance**: Runner sequences N sections from any manifest.

---

**Phase 3.2 — Section merge engine**

New file: `agentic_core/L3_orchestration/section_merge_engine.py`

Responsibilities:
- Accept `tuple[SealedSectionArtifact, ...]` + `merge_strategy`
- `merge_strategy` is a registry key resolved from app config (e.g., `"schema_assembly"`)
- The merge function itself is app-supplied (registered by apps_rg at load time)
- Core provides the runner framework; app provides the implementation
- Core validates: all expected sections present, no duplicate node_ids, digest integrity

**Acceptance**: Merge produces `SealedWorkflowPackage` without app-specific logic in core.

---

### Wave 4 — L2 ENSEMBLE_MODEL Lane

**Phase 4.1 — ENSEMBLE_MODEL lane**

New file: `agentic_core/L2_execution/ensemble_lane.py`

L2 executes one bounded section node at a time:

1. Receive `SectionNode` config + compiled prompt + evidence
2. For each `(prompt_variant_ref, temperature)` pair:
   - Build prompt from variant template + evidence
   - Call LLM via `generator_profile` registry key (dispatches to configured endpoint)
   - Produce `CandidateArtifact`
3. Return all `CandidateArtifact`s
4. Provider-profile dispatch is registry-driven, not hardcoded
5. Timeout + retry per existing L2 discipline
6. OTEL spans: `l2.ensemble.generate.{node_id}.{variant_ref}`

**Acceptance**: Generates N candidates for one node. Zero app-specific logic.

---

**Phase 4.2 — Candidate gate runner**

New file: `agentic_core/L2_execution/candidate_gate_runner.py`

Responsibilities:
- Accept `list[CandidateArtifact]` + `candidate_gate_profile` ref
- Load gate config from registry (config path comes from app, not hardcoded)
- Gate functions registered by apps at load time — pure `(text, context, params) -> CandidateGateResult`
- Run each gate against each candidate, mark `gates_passed`
- **Fail-closed**: if ALL candidates fail deterministic gates AND no repair policy → raise `AllCandidatesGatedError`
- Meta-prompt defense is just another registered gate

**Acceptance**: Gates filter candidates. All-fail raises. Zero app-specific logic.

---

**Phase 4.3 — Judge jury runner**

New file: `agentic_core/L2_execution/judge_jury_runner.py`

Responsibilities:
- Accept passed candidates + `judge_profile` ref
- Load judge rubric from registry (config path from app)
- Call judge providers specified in rubric `judge_providers` list (registry keys, not provider names)
- Each provider scores each candidate 0.0–1.0 with reasoning
- Apply `selection_policy` from rubric:
  - `"highest_mean"` — mean score across judges
  - `"consensus"` — majority agreement on top candidate
  - `"best_of_n"` — highest single score wins
- Return `EnsembleSelectionReceipt` + winner
- **Fallback**: if cloud judges fail, use `fallback_provider` from rubric (also a registry key)
- Fallback is explicit, registry-bound, and observable (OTEL span marks fallback)
- OTEL spans: `l2.judge.{judge_id}.{node_id}`

**Acceptance**: Jury selects winner. Zero hardcoded provider names.

---

### Wave 5 — apps_rg Manifest + Config

**Phase 5.1 — Workflow manifest YAML**

New file: `apps_rg/config/workflow_manifest.yaml`

Contains section pipeline definition with 7 sections (headline, exec_summary, competencies, unify_bullets, ibm_bullets, ey_bullets, insurtech_bullets). Each section specifies candidate_count, generator_profile (registry key), temperature_profile, prompt_variant_refs, candidate_gate_profile, judge_profile, selection_policy, archive_policy.

Critical sections: candidate_count=3. Medium sections: candidate_count=1.

**Acceptance**: YAML parses into valid `ManagedWorkflowSpec`. All profile refs resolve in registries.

---

**Phase 5.2 — Prompt variant configs**

New directory: `apps_rg/config/section_prompts/` — 7 YAML files porting prompt templates from quarantined code. Each contains variant_id, system_prompt, user_template (with placeholders), word_budget, style_constraint.

**Acceptance**: All prompt configs loadable. No runtime code in apps_rg.

---

**Phase 5.3 — Per-candidate gate configs + functions**

New file: `apps_rg/config/candidate_gates.yaml` — gate definitions per section type.
New file: `apps_rg/gates/__init__.py`
New file: `apps_rg/gates/per_candidate.py` — pure gate functions `(text, context, params) -> CandidateGateResult`. Registered with core's gate registry at app load time.

Gate functions are pure — no imports from L5/L2/L3 internals. They ARE the domain logic that stays in apps_rg.

**Acceptance**: Gate config parseable. Gate functions importable and testable in isolation.

---

**Phase 5.4 — Judge rubric configs**

New directory: `apps_rg/config/judge_rubrics/` — 4 YAML files (headline, exec_summary, competencies, bullet). Each specifies scoring dimensions, weights, judge_providers (registry keys), fallback_provider (registry key), consensus_threshold.

**Acceptance**: Rubrics loadable. Map to existing judge adapter interface via registry keys.

---

**Phase 5.5 — Provider profiles**

New file: `apps_rg/config/provider_profiles.yaml`

Maps registry keys to concrete provider configs:
```yaml
profiles:
  qwen_local:
    provider_type: vllm
    endpoint: http://localhost:8000/v1/chat/completions
    model: Qwen/Qwen2.5-32B-Instruct-AWQ
    max_tokens: 4096
    timeout_s: 60

  anthropic_judge:
    provider_type: anthropic
    model: claude-sonnet-4-20250514
    max_tokens: 1024
    timeout_s: 30
    api_key_env: ANTHROPIC_API_KEY

  openai_judge:
    provider_type: openai
    model: gpt-4o
    max_tokens: 1024
    timeout_s: 30
    api_key_env: OPENAI_API_KEY

  google_judge:
    provider_type: google
    model: gemini-2.5-flash
    max_tokens: 1024
    timeout_s: 30
    api_key_env: GOOGLE_API_KEY
```

**Acceptance**: Provider profiles loadable. Core dispatches to providers via these configs without hardcoding names.

---

### Wave 6 — Dispatch Rewiring + Exit

**Phase 6.1 — Dispatch branch on execution_form**

Modify: `agentic_core/runtime/entry/apps_rg_dispatch.py`

After L0 (route computed) and C0 (evidence gathered):
- Check `route.execution_form`
- If `"managed_workflow"`:
  - Resolve manifest via `WorkflowRegistry.resolve()` using `route.workflow_ref`
  - Call `ManagedWorkflowRunner.execute(spec, route, fec, validated_request, run_dir)`
  - Receive `SealedWorkflowPackage`
  - Pass to Exit binding
- If `"single_step"` or any `"cache_hit_*"`: keep existing monolithic path (backward compat)
- OTEL span: `dispatch.execution_form.{execution_form}`

**Acceptance**: Dispatch routes to L3 managed workflow path when execution_form=managed_workflow. Old path preserved.

---

**Phase 6.2 — Exit merge + final evaluation**

Modify: `agentic_core/runtime/exit/apps_rg_exit_binding.py`

- Accept either `SealedL2Artifact` (old single-step path) or `SealedWorkflowPackage` (new path)
- For workflow package: delegate to app-supplied merge function to assemble sections into final output
- Run final resume-level evaluation (existing exit_eval judges)
- Emit exactly one `X3DispositionReceipt` (X3D_ALLOW_FINISH for success)
- Save `generated_resume.json` + per-section archives + ensemble receipts to run directory (local stage-output, not durable writeback)
- Exit must NOT write Redis semantic cache or Chroma collections directly — remove current defect
- Cache/evidence writeback handled separately by RuntimeExhaustBundle/L6 → UWG → L4 (Wave 8)

**Acceptance**: Exit produces identical output schema regardless of execution path. Exactly one X3DispositionReceipt. Zero direct cache/vector writes from Exit.

---

**Phase 6.3 — RouteContract extension**

Modify: `agentic_core/runtime/contracts/route_contract.py`

Add optional field: `workflow_ref: str = ""` — populated by L0 when execution_form=managed_workflow, empty otherwise.

**Acceptance**: RouteContract backward-compatible (default empty string).

---

### Wave 7 — Tests + Parity Verification

**Phase 7.1 — Parity tests**

New file: `tests/_apps_contract/test_apps_rg_ensemble_parity.py`
- Headline: 8-11 words, pipe format
- Exec summary: best-practice sentence count, 3rd-person, ≥2 quantified outcomes
- Competencies: exactly 6 categories
- Bullet sections: match base resume bullet count
- Meta-prompt defense rejects clarification questions
- Forbidden buzzwords rejected
- Uses `APPS_RG_L2_FORCE_STUB=1` with canned candidate sets for deterministic testing

---

**Phase 7.2 — Anti-regression tests**

New file: `tests/_apps_contract/test_other_apps_unaffected.py`
- Assert no MANAGED_WORKFLOW routing for non-apps_rg tasks
- Assert WorkflowRegistry returns None for unregistered apps
- Assert gate registry isolation (apps_rg gates not globally active)
- Other apps_* dispatch paths unchanged

---

**Phase 7.3 — Fail-closed tests**

New file: `tests/_apps_contract/test_managed_workflow_fail_closed.py`
- Zero workflows resolve → error
- Multiple workflows resolve → error
- Registry digest mismatch → error
- Manifest references unregistered lane → error
- ENSEMBLE_MODEL lacks required gate profile → error
- All candidates fail deterministic gates, no repair policy → `AllCandidatesGatedError`
- All cloud judges fail, fallback works → success with fallback OTEL marker

---

**Phase 7.4 — Integration smoke test**

New file: `tests/_apps_contract/test_apps_rg_managed_workflow_e2e.py`
- Run `python -m apps_rg` with MANAGED_WORKFLOW path
- Assert 7 section artifacts in run directory
- Assert per-section ensemble archives + receipts present
- Assert `generated_resume.json` contains all 7 sections
- Assert total pipeline time < 3 minutes
- Assert exactly one X3 disposition emitted

---

**Phase 7.5 — Cache writeback separation tests**

New file: `tests/_apps_contract/test_cache_writeback_uwg_only.py`
- Assert L0 can read R1A/R1B cache records (read path)
- Assert L0 never writes cache (no write methods exposed)
- Assert L2 never writes cache
- Assert L3 never writes cache
- Assert L6 writeback_proposer creates `FutureRunPromotionRequest` with `R1APromotionPayload` only after successful X3D_ALLOW_FINISH
- Assert `R1APromotionPayload` contains all required fields (request_digest, normalized_payload_digest, app_context, task_class, route_id, workflow_ref, policy_hash, blueprint_hash, registry_digest_set, prompt/profile digest, output_schema_digest, final_response_ref, final_response_digest, exit_disposition_ref, replay_key, trace_root, created_at, ttl/freshness profile)
- Assert `R1BPromotionPayload` contains all required fields (semantic_embedding_ref, intent_vec_ref, app_context, task_class, capability, compatible_output_schema_digest, policy_hash, registry_digest_set, evidence_support_compatibility, workflow_ref, final_response_ref, final_response_digest, semantic_cache_threshold_profile, freshness_profile, replay_key, trace_root, exit_disposition_ref)
- Assert L6 writeback_proposer does not propose when Exit disposition is failure
- Assert future identical request hits R1A after UWG-admitted writeback

---

**Phase 7.6 — C0 writeback separation tests**

New file: `tests/_apps_contract/test_c0_writeback_uwg_only.py`
- Assert C0 emits FinalEvidenceContract (retrieve only)
- Assert C0 never writes to L4 directly
- Assert C0 never silently creates durable briefing state
- Assert L6 writeback_proposer creates `FutureRunPromotionRequest` with `C0EvidencePromotionPayload` only when evidence is reusable + policy allows
- Assert `C0EvidencePromotionPayload` contains all required fields (evidence_contract_ref, source_ids, source_versions, acl_freshness_receipts, contradiction_report, support_status, evidence_digest, citation_map, policy_hash, registry_digest_set, replay_key, trace_root, exit_disposition_ref, uwg_receipt)
- Assert missing briefing still invokes C0 normally (grounding_required=true path)
- Assert no direct apps_rg local retrieval outside the spine when briefing is missing

---

### Wave 8 — Cache + C0 Governed Writeback

**Phase 8.1 — FutureRunPromotionRequest + R1A/R1B payloads**

New file: `agentic_core/runtime/contracts/future_run_promotion_types.py`

```python
@dataclass(frozen=True)
class FutureRunPromotionRequest:
    """Inert post-runtime promotion proposal.

    Created by L6 writeback_proposer ONLY after successful X3D_ALLOW_FINISH.
    Contains payload + metadata. Has no authority — UWG admits or blocks.
    """
    promotion_type: str = ""  # r1a_exact_cache | r1b_semantic_cache | c0_evidence | index_refresh
    run_id: str = ""
    disposition_ref: str = ""
    trace_root: str = ""
    created_at: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    payload_ref: str = ""  # ref to typed payload below

@dataclass(frozen=True)
class R1APromotionPayload:
    """Payload for R1A exact cache promotion.

    Created by L6 writeback_proposer post-runtime.
    Consumed by UWG → L4 for governed cache storage.
    """
    commit_type: str = "r1a_exact_cache"
    request_digest: str = ""
    normalized_payload_digest: str = ""
    app_context: str = ""
    task_class: str = ""
    route_id: str = ""
    workflow_ref: str = ""             # populated if managed_workflow was used
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: str = ""
    prompt_profile_digest: str = ""
    output_schema_digest: str = ""
    final_response_ref: str = ""
    final_response_digest: str = ""
    exit_disposition_ref: str = ""
    replay_key: str = ""
    trace_root: str = ""
    created_at: str = ""
    ttl_seconds: int = 0
    freshness_profile: str = ""        # registry key for TTL/staleness rules

@dataclass(frozen=True)
class R1BPromotionPayload:
    """Payload for R1B semantic cache promotion.

    Created by L6 writeback_proposer post-runtime.
    Consumed by UWG → L4 for governed semantic cache storage.
    """
    commit_type: str = "r1b_semantic_cache"
    semantic_embedding_ref: str = ""
    intent_vec_ref: str = ""
    app_context: str = ""
    task_class: str = ""
    capability: str = ""
    compatible_output_schema_digest: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    evidence_support_compatibility: str = ""  # metadata about evidence/support compat
    workflow_ref: str = ""             # populated if managed_workflow was used
    final_response_ref: str = ""
    final_response_digest: str = ""
    semantic_cache_threshold_profile: str = ""  # registry key
    freshness_profile: str = ""        # registry key for TTL/staleness rules
    replay_key: str = ""
    trace_root: str = ""
    exit_disposition_ref: str = ""
```

**Acceptance**: All contracts importable, frozen, JSON-serializable. Zero app-specific names. `FutureRunPromotionRequest` is the envelope; typed payloads carry domain-neutral data.

---

**Phase 8.2 — C0EvidencePromotionPayload + IndexRefreshPayload**

Same file: `agentic_core/runtime/contracts/future_run_promotion_types.py` (continued)

```python
@dataclass(frozen=True)
class C0EvidencePromotionPayload:
    """Payload for C0 evidence/briefing writeback promotion.

    Created by L6 writeback_proposer post-runtime when
    evidence packet is reusable and writeback policy allows.
    Consumed by UWG → L4 for governed evidence storage.
    Stores reusable support artifacts, NOT authoritative business truth.
    """
    commit_type: str = "c0_evidence_writeback"
    evidence_contract_ref: str = ""    # ref to FinalEvidenceContract
    source_ids: tuple[str, ...] = ()
    source_versions: tuple[str, ...] = ()
    acl_freshness_receipts: tuple[str, ...] = ()
    contradiction_report: str = ""
    support_status: str = ""           # e.g. "sufficient", "partial", "insufficient"
    evidence_digest: str = ""
    citation_map: str = ""             # serialized citation map ref
    policy_hash: str = ""
    registry_digest_set: str = ""
    replay_key: str = ""
    trace_root: str = ""
    exit_disposition_ref: str = ""
    uwg_receipt: str = ""              # populated by UWG after admission

    # Writeback candidates (optional, policy-driven)
    generated_briefing_packet_ref: str = ""
    normalized_evidence_bundle_ref: str = ""
    source_lineage_map_ref: str = ""
    retrieval_query_profile_ref: str = ""
    evidence_support_profile_ref: str = ""
    reusable_context_packet_ref: str = ""
    app_read_surface_metadata_ref: str = ""
    embedding_index_refresh_ref: str = ""
```

**Acceptance**: Contract importable, frozen, JSON-serializable. Zero app-specific names.

---

**Phase 8.3 — Post-runtime writeback proposer (L6)**

New file: `agentic_core/runtime/exhaust/writeback_proposer.py`

**Model: Runtime path is clean. Writeback is a separate post-runtime learning path.**

After the runtime path completes (Exit emits X3D_ALLOW_FINISH, resume returned to user), the RuntimeExhaustBundle is closed and handed to L6:

1. RuntimeExhaustBundle contains: RouteContract (with cache-miss receipts), SealedWorkflowPackage ref, FinalEvidenceContract ref, X3DispositionReceipt ref, run_id, timestamps
2. L6 `writeback_proposer` evaluates app-supplied policies (`cache_writeback_policy.yaml`, `c0_writeback_policy.yaml`)
3. If cacheable and policy allows:
   - Build `FutureRunPromotionRequest` for R1A exact cache (route hash, sealed output, disposition ref, TTL)
   - Build `FutureRunPromotionRequest` for R1B semantic cache (embedding ref, threshold profile)
4. If evidence is reusable and policy allows:
   - Build `FutureRunPromotionRequest` for C0 evidence artifact (FEC ref, source IDs, digests, citation map)
   - Build `FutureRunPromotionRequest` for index refresh if applicable
5. All `FutureRunPromotionRequest`s are inert proposals — they contain data, not authority
6. Proposals submitted to UWG for admission validation
7. UWG admits or blocks each request independently
8. L4 stores only admitted records
9. **Never** propose writeback when Exit disposition was failure/error
10. OTEL spans: `l6.writeback_propose.r1a`, `l6.writeback_propose.r1b`, `l6.writeback_propose.c0`, `l6.writeback_propose.index`

Flow:
```
RuntimeExhaustBundle closed (post-run boundary)
→ L6 writeback_proposer loads policies
→ evaluates eligibility from bundle evidence
→ creates inert FutureRunPromotionRequest(s)
→ submits to UWG
→ UWG admits or blocks
→ L4 stores admitted records
→ future L0 can hit R1A/R1B; future C0 can reuse cached evidence
```

**What is NOT allowed:**
- Exit writing cache/vector store directly (current defect to remove)
- Exit depositing commit requests or writeback proposals of any kind
- Any writeback blocking the user-visible output
- L6 writing to L4 directly (must go through UWG)
- Proposing writeback for failed runs

**Acceptance**: Runtime path completes and user gets resume without any writeback involvement. Writeback proposals are post-runtime only. FutureRunPromotionRequests are inert data. UWG is the sole admission gate.

---

**Phase 8.4 — apps_rg cache/freshness policy configs**

New file: `apps_rg/config/cache_writeback_policy.yaml`
```yaml
r1a_exact:
  enabled: true
  ttl_seconds: 604800           # 7 days
  freshness_profile: resume_exact_7d
  eligible_task_classes: [resume_generation]
  eligible_exit_statuses: [success]

r1b_semantic:
  enabled: true
  freshness_profile: resume_semantic_30d
  semantic_cache_threshold_profile: resume_semantic_v1
  eligible_task_classes: [resume_generation]
  eligible_exit_statuses: [success]
  require_evidence_support: true
```

New file: `apps_rg/config/c0_writeback_policy.yaml`
```yaml
evidence_writeback:
  enabled: true
  eligible_support_statuses: [sufficient, partial]
  require_no_contradictions: true
  reusable_artifact_types:
    - generated_briefing_packet
    - normalized_evidence_bundle
    - citation_map
    - source_lineage_map
    - retrieval_query_profile
    - reusable_context_packet
  freshness_profile: evidence_14d
  eligible_exit_statuses: [success]
```

**Acceptance**: Policy configs loadable. Exit reads policies to decide whether to emit commit requests.

---

## Rules

- No `if app == "apps_rg"` in core — config/registry dispatch only
- No resume section names in core execution logic
- No provider names hardcoded in core — registry keys only
- L3 owns multi-hop sequencing. L2 executes one bounded node at a time.
- R1A/R1B/R5 cache checks before managed workflow evaluation
- Workflow resolution is deterministic and fail-closed
- All new core files go in `agentic_core/` (L2, L3, contracts)
- All apps_rg config goes in `apps_rg/config/` — never `agentic_core/`
- Gate functions in `apps_rg/gates/` — pure, no imports from L5/L2/L3 internals
- Judges are evaluators/selectors, not authority expanders
- Cloud judge fallback is explicit, registry-bound, and observable
- OTEL spans for every section + candidate + judge call
- Existing monolithic path preserved behind execution_form check (rollback)
- **L0 reads cache only — never writes**
- **L2/L3 never write cache or evidence to L4**
- **Cache writeback flows exclusively through L6 writeback_proposer → FutureRunPromotionRequest → UWG → L4 (post-runtime)**
- **C0 evidence writeback flows exclusively through L6 writeback_proposer → FutureRunPromotionRequest → UWG → L4 (post-runtime)**
- **No cache or evidence writeback during the runtime path (user gets resume first, writeback is post-runtime)**
- **UWG is the sole admission gate for all durable writes (cache, evidence, index)**
- **Exit must not write Redis, Chroma, or any durable store directly (current defect to remove)**
- **C0 evidence writeback stores reusable support artifacts, not authoritative business truth**

---

## Per-Section Artifact Emission (each section node produces)

| Artifact | Schema | Emitted by |
|---|---|---|
| `CandidateArtifact` (N per node) | `ensemble_types.py` | L2 ENSEMBLE_MODEL lane |
| `CandidateGateResult` (per gate per candidate) | `judge_types.py` | L2 candidate gate runner |
| `JudgeResult` (per judge per candidate) | `judge_types.py` | L2 judge jury runner |
| `JudgeJuryResult` (per candidate) | `judge_types.py` | L2 judge jury runner |
| `EnsembleSelectionReceipt` (1 per node) | `ensemble_types.py` | L2 (post-selection) |
| `SealedSectionArtifact` (1 per node) | `sealed_workflow_types.py` | L2 (seals winner) |

L3 collects all `SealedSectionArtifact`s → `SealedWorkflowPackage`.
Exit produces one `X3DispositionReceipt`.

---

## Stage-Output Receipt Manifest (per managed workflow run)

Every managed workflow run saves these files in the run directory (`artifacts/apps_rg/runs/<ts>/`):

| # | File | Producer |
|---|---|---|
| 00 | `00_parse_envelope.json` | CLI/wizard |
| 01 | `01_U0_validated_request.json` | U0 |
| 02 | `02_L1_plan_contract.json` | L1 |
| 03 | `03_L0_route_contract.json` | L0 |
| 03a | `03a_R1A_cache_lookup_receipt.json` | L0 (actual R1A lookup result) |
| 03b | `03b_R1B_cache_lookup_receipt.json` | L0 (actual R1B lookup result) |
| 03c | `03c_R5_fallback_receipt.json` | L0 |
| 04 | `04_C0_evidence_contract.json` | C0 |
| 05 | `05_PA_compiled_prompt.json` | PA (if global prompt exists) |
| 06 | `06_L3_workflow_manifest_resolved.json` | L3 (resolved manifest) |
| 07 | `07_L3_to_L2_step_contract_<node>.json` | L3 (per section node) |
| 08 | `08_L2_candidate_artifacts_<node>.json` | L2 (per section node) |
| 09 | `09_L2_gate_results_<node>.json` | L2 (per section node) |
| 10 | `10_L2_judge_results_<node>.json` | L2 (per section node) |
| 11 | `11_L2_selection_receipt_<node>.json` | L2 (per section node) |
| 12 | `12_L2_sealed_section_<node>.json` | L2 (per section node) |
| 13 | `13_L3_sealed_workflow_package.json` | L3 |
| 14 | `14_Exit_disposition_receipt.json` | Exit |
| opt | `15_promotion_request_r1a.json` | L6 writeback_proposer (post-runtime, only if eligible) |
| opt | `15_promotion_request_r1b.json` | L6 writeback_proposer (post-runtime, only if eligible) |
| opt | `15_promotion_request_c0.json` | L6 writeback_proposer (post-runtime, only if eligible) |
| 99 | `99_runtime_exhaust_bundle.json` | RuntimeExhaustBundle |

---

## File Inventory

### New Core Files (agentic_core — generic, app-agnostic)

| File | Layer | Purpose |
|---|---|---|
| `agentic_core/runtime/contracts/ensemble_types.py` | Contracts | CandidateArtifact, EnsembleSelectionReceipt |
| `agentic_core/runtime/contracts/workflow_manifest_types.py` | Contracts | SectionNode, ManagedWorkflowSpec |
| `agentic_core/runtime/contracts/judge_types.py` | Contracts | JudgeResult, JudgeJuryResult, CandidateGateResult |
| `agentic_core/runtime/contracts/sealed_workflow_types.py` | Contracts | SealedSectionArtifact, SealedWorkflowPackage |
| `agentic_core/L3_orchestration/workflow_registry.py` | L3 | Manifest discovery + deterministic resolution |
| `agentic_core/L3_orchestration/managed_workflow_runner.py` | L3 | Generic section-based workflow orchestrator |
| `agentic_core/L3_orchestration/section_merge_engine.py` | L3 | App-supplied merge strategy execution |
| `agentic_core/L2_execution/ensemble_lane.py` | L2 | Generic ENSEMBLE_MODEL lane (one bounded node) |
| `agentic_core/L2_execution/candidate_gate_runner.py` | L2 | Per-candidate gate execution |
| `agentic_core/L2_execution/judge_jury_runner.py` | L2 | Multi-provider judge + selection |
| `agentic_core/runtime/contracts/future_run_promotion_types.py` | Contracts | FutureRunPromotionRequest, R1APromotionPayload, R1BPromotionPayload, C0EvidencePromotionPayload, IndexRefreshPayload |
| `agentic_core/runtime/exhaust/writeback_proposer.py` | L6/Exhaust | Post-output writeback proposal (Option A: RuntimeExhaustBundle → UWG) |

### New apps_rg Files (domain-specific config + gates)

| File | Purpose |
|---|---|
| `apps_rg/config/workflow_manifest.yaml` | Section pipeline definition |
| `apps_rg/config/provider_profiles.yaml` | Generator + judge provider configs |
| `apps_rg/config/candidate_gates.yaml` | Gate configuration per section |
| `apps_rg/config/section_prompts/headline.yaml` | Headline prompt variants |
| `apps_rg/config/section_prompts/exec_summary.yaml` | Exec summary prompt variants |
| `apps_rg/config/section_prompts/competencies.yaml` | Competencies prompt variants |
| `apps_rg/config/section_prompts/unify_bullets.yaml` | Unify bullet prompt variants |
| `apps_rg/config/section_prompts/ibm_bullets.yaml` | IBM bullet prompt variants |
| `apps_rg/config/section_prompts/ey_bullets.yaml` | EY bullet prompt variant |
| `apps_rg/config/section_prompts/insurtech_bullets.yaml` | InsurTech bullet prompt variant |
| `apps_rg/gates/__init__.py` | Gate module init |
| `apps_rg/gates/per_candidate.py` | Pure gate functions (ported from quarantine) |
| `apps_rg/config/judge_rubrics/headline_rubric.yaml` | Headline judge scoring rubric |
| `apps_rg/config/judge_rubrics/exec_summary_rubric.yaml` | Exec summary judge rubric |
| `apps_rg/config/judge_rubrics/competencies_rubric.yaml` | Competencies judge rubric |
| `apps_rg/config/judge_rubrics/bullet_rubric.yaml` | Bullet section judge rubric |
| `apps_rg/config/cache_writeback_policy.yaml` | R1A/R1B cache writeback TTL + eligibility |
| `apps_rg/config/c0_writeback_policy.yaml` | C0 evidence writeback eligibility + reusable artifact types |

### Modified Core Files

| File | Change |
|---|---|
| `agentic_core/runtime/contracts/l1_plan_contract.py` | Add 4 work-shape hint fields |
| `agentic_core/runtime/contracts/route_contract.py` | Add `workflow_ref` field |
| `agentic_core/L1_cognition/apps_rg_l1_binding.py` | Set work-shape hints for resume_generation |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | Cache-first + shape evaluation + registry resolution |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | Branch on execution_form → L3 path |
| `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Handle SealedWorkflowPackage merge, emit X3D_ALLOW_FINISH, deposit refs to RuntimeExhaustBundle. Remove current defect (direct Redis/Chroma writes). |

### New Test Files

| File | Purpose |
|---|---|
| `tests/_apps_contract/test_apps_rg_ensemble_parity.py` | Section quality parity with old HOPs |
| `tests/_apps_contract/test_other_apps_unaffected.py` | Anti-regression for other apps |
| `tests/_apps_contract/test_managed_workflow_fail_closed.py` | Fail-closed scenarios |
| `tests/_apps_contract/test_apps_rg_managed_workflow_e2e.py` | Full E2E smoke test |
| `tests/_apps_contract/test_cache_writeback_uwg_only.py` | Cache writeback separation (L0 read vs Exit→UWG write) |
| `tests/_apps_contract/test_c0_writeback_uwg_only.py` | C0 writeback separation (C0 retrieve-only vs Exit→UWG writeback) |

---

## Rollback Strategy

1. Set `APPS_RG_EXECUTION_FORM=SINGLE_STEP` env var → L0 forces single_step → dispatch uses old monolithic path. This is the ONLY acceptable fallback path.
2. No destructive changes to existing monolithic pipeline (preserved in dispatch branch).
3. If manifest loading fails AFTER L0 selected MANAGED_WORKFLOW → RouteRejected / Exit failure. **No silent fallback to SINGLE_STEP.** The run fails closed with a descriptive error.
4. If registry resolution fails AFTER L0 selected MANAGED_WORKFLOW → fail closed with descriptive error (no silent degradation to wrong workflow).
5. Silent fallback is FORBIDDEN. Only explicit `APPS_RG_EXECUTION_FORM=SINGLE_STEP` env var reverts to old path.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| R1A/R1B/R5 precedes shape evaluation | Actual cache lookups (not just eligibility) complete before managed workflow | Test + code review |
| R1A actual lookup proof | R1A lookup receipt present in RouteContract evidence before MANAGED_WORKFLOW proceeds | RouteContract assertion in test |
| R1B actual lookup proof | R1B lookup receipt present in RouteContract evidence before MANAGED_WORKFLOW proceeds | RouteContract assertion in test |
| Cache-miss receipts | cache_miss_r1a + cache_miss_r1b present when MANAGED_WORKFLOW selected | RouteContract field assertion |
| Registry resolution | Exactly 1 workflow or fail closed | Fail-closed test suite |
| Section count | 7 sections generated independently | Count section artifacts in run dir |
| Candidate count (critical) | 3 per section | Count candidates in archive JSON |
| Gate filtering | ≥1 candidate rejected per section (adversarial) | Gate test with known-bad text |
| Judge scoring | Per rubric, multi-provider | JudgeJuryResult + EnsembleSelectionReceipt artifacts |
| Core app-agnostic | 0 resume section names in core execution logic | `grep` proof |
| Core provider-agnostic | 0 hardcoded provider names in core | `grep` proof |
| Other apps unaffected | 0 route changes for non-registered apps | Anti-regression test |
| Pipeline latency | < 3 minutes E2E | Timer in smoke test |
| X3 count | Exactly 1 X3DispositionReceipt per run | Exit binding assertion |
| No direct cache/vector write from Exit | Exit does not write Redis or Chroma directly | grep/mock proof: zero direct write calls in exit binding |
| Option A writeback | Resume returned to user before any writeback proposal | Timing assertion in E2E test |
| Stage-output receipts | All 14+ stage-output files present in run directory | File-count assertion on run dir |
| No silent fallback | Manifest/registry failure after MANAGED_WORKFLOW → error, not SINGLE_STEP | Fail-closed test |
| R1A cache writeback | Only through L6 writeback_proposer → UWG → L4 | Cache writeback separation test |
| R1B semantic cache writeback | Only through L6 writeback_proposer → UWG → L4 | Cache writeback separation test |
| L0 cache read/write separation | L0 reads only, never writes | Test proves no write methods on L0 |
| L2/L3 cache isolation | L2/L3 never write cache or evidence | Test proves no write paths |
| C0 evidence writeback | Only through L6 writeback_proposer → UWG → L4 | C0 writeback separation test |
| C0 retrieve-only discipline | C0 emits FEC but never writes L4 | Test proves no direct L4 access |
| Missing briefing → C0 invoked | No bypass of C0 when grounding required | Test with no briefing input |
| Future R1A hit after writeback | Identical request short-circuits via R1A | E2E two-request test |
| Future R1B hit after writeback | Semantically equivalent request short-circuits via R1B | E2E semantic-equiv test |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Per-section ensemble generates candidates and selects winner via judge jury | `pytest tests/_apps_contract/test_apps_rg_ensemble_parity.py -v` passes | 🔲 |
| DoD-2 | Smoke-run produces 7-section resume with per-section archives and receipts | `python -m apps_rg --target-company "Test" --target-role "SVP" --source-resume <path> --jd <path>` exits 0 and produces `artifacts/apps_rg/runs/<ts>/` with section archives | 🔲 |
| DoD-3 | All existing tests + new tests pass, zero regressions | `pytest tests/_apps_contract/ -v` shows 0 fail | 🔲 |
| DoD-4 | Other apps unaffected | `pytest tests/_apps_contract/test_other_apps_unaffected.py -v` passes | 🔲 |
| DoD-5 | Fail-closed on registry/resolution failures | `pytest tests/_apps_contract/test_managed_workflow_fail_closed.py -v` passes | 🔲 |
| DoD-6 | Core contains zero resume-specific or provider-specific logic | `grep -rn "headline\|exec_summary\|competencies\|ibm_bullets\|ey_bullets\|insurtech\|NarrativeJudgeScorer\|Qwen\|Anthropic\|OpenAI\|Gemini" agentic_core/` returns 0 matches (allowlist: tests, doc comments, registry fixture refs explicitly marked `# allowlist: provider-fixture`) | 🔲 |
| DoD-7 | R1A/R1B cache writeback works only through Exit → UWG → L4; L0/L2/L3 never write cache | `pytest tests/_apps_contract/test_cache_writeback_uwg_only.py -v` passes | 🔲 |
| DoD-8 | C0 evidence writeback works only through L6 writeback_proposer → UWG → L4; C0 retrieves only, never writes L4 directly | `pytest tests/_apps_contract/test_c0_writeback_uwg_only.py -v` passes | 🔲 |
| DoD-9 | Stage-output receipt manifest complete (14+ files per managed workflow run) | `python -m apps_rg ...` exits 0 and `ls artifacts/apps_rg/runs/<ts>/` shows all numbered stage outputs per manifest | 🔲 |
| DoD-10 | Current Exit defect (direct Redis/Chroma writes) removed | `grep -rn "redis\|chroma\|put_cache\|add_to_collection" agentic_core/runtime/exit/apps_rg_exit_binding.py` returns 0 matches | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Cloud judge cost optimization | Requires production traffic data | `NEXT_STEP:` marker |
| Healing tier for judge failures | Separate plan scope | `NEXT_STEP:` marker |
| UWG admission policy logic | Admission rules are a separate plan; this plan defines the commit contract shape + flow only | `NEXT_STEP:` marker |
| Legacy HOP adapter migration | Deferred until parity proven | `NEXT_STEP:` marker |

---

## Core Principle (preserved throughout implementation)

```
L0 reads and routes.
C0 retrieves and contracts evidence.
PA assembles.
L3 sequences.
L2 executes one bounded node.
Exit emits exactly one X3.
UWG is the only durable write gate.
L4 stores.
L6 learns only after the run boundary.
```

---

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
