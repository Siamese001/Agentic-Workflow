---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-exec-to-repo-brief-rename-d3f8a2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-exec-to-repo-brief-rename-d3f8a2.md'
source_sha256: 9fbd85547a29795f20ba9a6700692e7553cc4ce6e1c682f19de79dd2f9d4efc4
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_exec → apps_repo_brief — Dependency Impact Report & Refactor Plan

> **Status:** Not Started · **Tier:** T3 · **Slug:** `apps-exec-to-repo-brief-rename-d3f8a2` · **Authored:** 2026-05-04

## 1. Executive Summary

`apps_exec` has two defects: (a) **misnaming** — name implies runtime execution, actual function is translating a technical repo into evidence-backed executive briefs; (b) **spine violation** — `ExecOrchestrator` HOP pipeline runs `Ingest → Extract → Assemble → StyleGate` **pre-C0**, then `cert/fec_producer.py` mints an authoritative `FinalEvidenceContract` post-L2. Contradictory route declarations exist: `spine_manifest.yaml` claims `R3_grounded_read` with C0; `cert_route_registry.yaml` claims template-only, no-C0. Cross-app coupling is narrower than the 336-file grep suggests: only `apps_eval/engines/scenario_runner.py` has runtime coupling (3 lazy-imported scenarios, allowlisted, SKIP-on-failure). No other `apps_*` imports `apps_exec`.

**Recommendation:** 4-phase rename + spine repair. Phase 1 ships `apps_repo_brief` parallel, `apps_exec` as shim. Phase 4 deletes shim only after dependency scan shows zero hard refs. Est. 4 waves, ~30 phases, ~80k tokens. Risk: medium-high (spine restructure is the larger risk).

## 2. Current `apps_exec` Function (DIRECTLY OBSERVED)

- Product: persona-targeted executive briefs (recruiter/cto/svp_eng/board/head_of_ai) from repo architecture docs. Artifacts: `exec_brief_<audience>_<trace_id>.md` + `run_summary_<trace_id>.json`.
- Spine: `apps_exec/spine_manifest.yaml` declares `R3_grounded_read`, `HITL_ENABLED=True`, no `CommitRequest`.
- Cert route: `apps_exec.execution_v1` SINGLE_STEP, `invoke_exit_eval=true`, **self-describes as template-driven (no C0)** — contradicts spine_manifest.
- Product route: `apps_exec.single_step_v1` (legacy second route in `route_registry.yaml`).
- HOP pipeline: 5 HOPs `INGEST → EXTRACT → ASSEMBLE → GATE → EMIT`, all pre-C0 in orchestrator path.
- Governed path: `GovernedExecRun` uses C0 `HybridSearchEngine` over `exec_docs` collection; degrades gracefully when absent.
- FEC producer: `apps_exec/cert/fec_producer.py` post-L2 — anti-pattern per target architecture.
- Module count: 59. Cross-cutting `agentic_core` imports: 36. Shim: `apps_exec/_optional_agentic_core.py`.

## 3. Proposed `apps_repo_brief` Function

- Domain: translate technical repo → evidence-backed executive briefs for target audience
- Capability: `apps_repo_brief.generate_executive_brief_v1`
- Route: `apps_repo_brief.executive_brief_v1`, `R3_SIMPLE_GROUNDED_READ`, SINGLE_STEP, `c0_required=true`, `pa_required=true`, `l3_required=false`, `durable_write_allowed=false`, `commit_request_allowed=false`
- Retrieval surface: `repo_brief_docs` (L4-backed, not live directory scan)
- Artifacts: `repo_brief_<audience>_<trace_id[:8]>.md`, `repo_brief_summary_<trace_id[:8]>.json`
- L3 off by default; triggered only by multi-audience batch / snapshot-diff / board pack+appendix+talk track / `apps_research` external context / staged HITL
- Spine: canonical `U0 → L1 → L0 → C0 → PA → L2 → Exit → L6`; no pre-C0 domain work

**Responsibility split (target):** `apps_repo_brief` owns personas/schemas/templates/rubrics/style policy/artifact naming/cert projection adapters. C0 owns retrieval + authoritative `FinalEvidenceContract.v1`. PA owns prompt/citation/envelope. L2 owns bounded synthesis + same-authority repair + sealing. Exit owns X3 disposition. L6 owns shadow eval only. L4/UWG owns durable state.

## 4. Inbound Dependency Map

**Hard runtime coupling:** 1 module, allowlisted, SKIP-on-ImportError
- `apps_eval/engines/scenario_runner.py` L568-636 — lazy-imports `apps_exec.reasoning.ExecOrchestrator` + `apps_exec.types.exec_types` in 3 scenarios (`recruiter_brief`, `cto_brief`, `dry_run`). Allowlist: `config/cross_app_import_allowlist.yaml`.

**Soft references (string literals):**
- `agentic_core/L0_routing/config/path_constants.py` — `APPS_EXEC_DIR`, `APPS_EXEC_SUBFOLDER_MAP`, 4 allowlist tuples
- `agentic_core/L2_execution/types/agent_taxonomy_registry.py` — 7 literal matches
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` — 5 literal matches
- `apps_shared/spine_emission/context.py` — app-name allowlist (6 matches)
- `apps_shared/proof/scenarios.py` — scenario fixtures (8 matches)
- `config/cross_app_import_allowlist.yaml` — apps_eval→apps_exec allowlist
- `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` — APP-EXEC inventory row (16 matches)
- `tools/eval/retrieval_benchmark.py` — scenario IDs (20 matches)

**Doc-only comparisons (no coupling):** `apps_rg/`, `apps_rfp/`, `apps_research/`, `apps_underwriting_ai/`, `apps_lic/` sibling pattern-comparison comments in spine_manifests + SVP reviews.

**Test surfaces:** `tests/unit/apps_exec/**`, `tests/governance/test_apps_exec_spine.py`, `tests/_apps_contract/test_apps_exec_{fec_producer,exit_hook}.py`, `tests/integration/apps_exec/test_prompt_template_cross_app.py`.

## 5. Outbound Dependency Map

Per `app_inventory.yaml`: 36 cross-cutting + 2 L2 + 1 L3 + 1 L4 agentic_core imports. Key: `agentic_core.{L2_execution.types.local_first_disposition, L3_orchestration.inference.qwen_vllm (optional), L4_state.config.vllm_routing_predicates, adg.applications.execute_ssot_integration, adg.runtime.behavioral_index, mixins.{embedding,semantic_cache}_mixin, runtime.contracts.lifecycle_trace_contract}` + R3-chain contracts (`L0_routing.{intake.validated_request, c0_retrieval.{route_contract,plan,final_contract}}, L1_cognition.types.plan_contract_types, L2_execution.reasoning.compiled_artifact, L5_safety.eval_spine.exit_eval, L3_orchestration.exit_eval.v6.types`). `apps_shared`: `integrations.governed_app_runner.GovernedAppRunner`, `spine.base_spine_adapter`, `cert.{maybe_invoke_exit_eval,rubric_output_mapper}`, `spine_emission.governed_run`. **Zero outbound `apps_*` imports.**

## 6. Cross-App Dependency Matrix

| app | dep_type | evidence_file | reference | migration_action | risk |
|---|---|---|---|---|---|
| apps_eval | calls directly (lazy+SKIP) | `apps_eval/engines/scenario_runner.py` L568-636 | `from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator` ×3 | add parallel `apps_repo_brief` scenarios P1; flip primary P4 | Medium |
| apps_research | doc only | SVP_ENGINEERING_REVIEW.md | "matching rigor of ... apps_exec ..." | comment update P2 | Low |
| apps_rg | doc only | spine_manifest.yaml L16, spine_handoff.py L3 | pattern attribution | comment update P2 | Low |
| apps_lic | doc only | (HITL-posture refs in rg/rfp manifests) | "weaker than apps_lic and apps_exec" | comment update P2 | Low |
| apps_rfp | doc only | spine_manifest.yaml L16/65/99, reasoning_toggles_config.py L4 | pattern + HITL-posture comments | comment update P2 | Low |
| apps_qna | none | — | none | none | None |
| apps_underwriting_ai | doc only | spine_manifest.yaml L14 | pattern attribution | comment update P2 | Low |
| apps_shared | shared substrate | proof/scenarios.py (8), spine_emission/context.py (6) | allowlist literals + scenario IDs | add `apps_repo_brief` allowlist P1; retain `apps_exec` until P4 | Medium |

**Zero of 7 sibling `apps_*` modules have Python-import coupling.** Only `apps_eval` has allowlisted lazy-import coupling with SKIP fallback.

## 7. Registry & Route Impact

| File | Current | Action | Phase |
|---|---|---|---|
| `apps_exec/spine_manifest.yaml` | R3_grounded_read for `apps_exec.execution_v1` | Migrate to `apps_repo_brief/spine_manifest.yaml` with `apps_repo_brief.executive_brief_v1`; leave deprecation stub at old path | 2 |
| `apps_exec/config/route_registry.yaml` | `apps_exec.single_step_v1` | Migrate; **collapse `single_step_v1` and `execution_v1` into one canonical route** | 2 |
| `apps_exec/config/cert_route_registry.yaml` | `apps_exec.execution_v1`, contradicts spine | Resolve contradiction; migrate | 2 |
| `agentic_core/L0_routing/config/path_constants.py` | `APPS_EXEC_*` constants + allowlists | Add `APPS_REPO_BRIEF_*` additive P1; remove `APPS_EXEC_*` P4 | 1, 4 |
| `agentic_core/L2_execution/types/agent_taxonomy_registry.py` | apps_exec rows | Dual-entry P1; remove P4 | 1, 4 |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | apps_exec blueprint allowlist | Dual-entry | 1, 4 |
| `apps_shared/spine_emission/context.py` | app-name allowlist | Add `apps_repo_brief` | 1, 4 |
| `config/cross_app_import_allowlist.yaml` | sanctions apps_eval→apps_exec | Add parallel | 1, 4 |
| `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` | APP-EXEC row | Add APP-REPO-BRIEF P1; retire P4 | 1, 4 |
| `tools/eval/retrieval_benchmark.py` | apps_exec scenario IDs | Parallel scenarios P1 | 1, 4 |

## 8. Test/Fixture Impact

Mirror `tests/unit/apps_exec/**` → `tests/unit/apps_repo_brief/**` in P1; retire originals in P4. Mirror governance + _apps_contract + integration test files. **Rewrite** `test_exec_orchestrator.py` in P3 to assert canonical-spine ordering. **Reframe** `test_apps_exec_fec_producer.py` in P3 — current post-L2 FEC becomes cert projection; authoritative FEC test moves to C0 boundary. **New P3 contract tests:** `test_repo_brief_no_pre_c0_retrieval`, `test_repo_brief_authoritative_fec_at_c0`, `test_repo_brief_template_only_no_full_board`, `test_repo_brief_semantic_cache_strict_compat`. **P4 gate:** `test_no_apps_exec_python_imports_outside_shim`.

## 9. C0 Retrieval Impact

Current: `GovernedExecRun` → `HybridSearchEngine` over `exec_docs` (undefined L4 surface, degrades gracefully). Orchestrator path (`ExecOrchestrator.run`) does NOT use C0 — it filesystem-scans directly. Two parallel paths.

Target: rename `exec_docs` → `repo_brief_docs` as **L4 retrieval surface** built via UWG. Coverage: architecture/reference/governance/runtime-gates/L5/C0/PA/L2/Exit/L4/L6 docs, runtime-proof/E2E-acceptance/replay-proof/no-bypass-proof/OTEL/ADG-proof docs, code refs, route/capability/app registries, tests, cert receipts, ADRs, DDRs, known-limitations.

**7 C0 lanes:** BM25/exact-phrase · dense-semantic · metadata (source_type/audience/recency/policy_hash/blueprint_hash/repo_snapshot_id) · graph (docs↔code↔tests↔proof) · code-symbol · proof (tests/receipts/replay/OTEL/negative-controls) · prior-artifact (hints only).

**Evidence rule:** dense hits alone insufficient for high-stakes governance claims; exact names/IDs/paths/labels/symbols/dates require sparse/BM25 or metadata support.

**Authoritative `FinalEvidenceContract.v1` at C0** — new file `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py`. Schema: `identity{request_id,run_id,trace_id,route_id,audience,emphasis_areas,repo_snapshot_id,policy_hash,blueprint_hash,replay_key} · retrieval{source_collection,retrieval_surface_id,retrieval_plan_hash,lanes_used,raw_count,hydrated_count,shaped_count,excluded_count} · status{evidence_status∈{PASS,WEAK,WEAK_WITH_CAVEATS,CONFLICTED,EMPTY,BLOCKED}, recommended_disposition, grounded, template_only} · section_coverage{executive_thesis,governance_model,runtime_controls,operating_discipline,risks_and_gaps,board_asks} · claim_support_map[{claim_id,claim_text,claim_type∈{governance_control,architecture_boundary,runtime_proof,operating_model,risk_gap,board_decision}, support_status, direct/implementation/proof_support_refs, contradiction_refs, gap_notes}] · verified_evidence{must_use,supporting,background,contradicts,excluded} · reports{freshness,acl,contradiction,gap,lineage_manifest,prompt_budget_hint} · observability{c0_span_id,retrieval_ms,shaping_ms,scoring_ms,refinement_attempted,budget_status}`.

**Board gates at C0:** required section coverage (6 sections above); hard-blocks (missing governance_model/runtime_controls/risks_and_gaps, citation instability, unresolved contradiction, ACL-blocked source, template_only-requested-as-full-brief). Fallback: `PASS→PA full context`; `WEAK_WITH_CAVEATS→PA caveated, L2 caveat weak sections`; `WEAK→C0 one bounded refinement pass`; `CONFLICTED→contradiction report + human_review/reroute for board`; `EMPTY→SAFE_FALLBACK scaffold or SAFE_ABSTAIN`; `BLOCKED→SAFE_ABSTAIN or human_review`; `template_only→scaffold only, never full board brief`.

## 10. Cache Impact

**R1A exact cache** — may terminal-return prior artifact only if ALL match: `normalized_request_hash, audience, emphasis_areas_hash, repo_snapshot_id, retrieval_surface_id, policy_hash, blueprint_hash, persona_schema_version, rubric_version, source_freshness_window`.

**R1B semantic cache** — MUST NOT terminal-return board briefs unless strict-compat exact. Otherwise returns prior evidence maps / artifact refs as hints to C0/PA only.

Action: add `apps_repo_brief/config/cache_compat.yaml` in P2; enforce via contract test.

## 11. Artifact Naming Impact

`exec_brief_*.md` → `repo_brief_*.md`; `run_summary_*.json` → `repo_brief_summary_*.json`; `reports/executive/` → `reports/repo_brief/`; `exec_docs` → `repo_brief_docs`; template id `exec_brief_v1` → `repo_brief_v1`; routing target `exec_brief_assembly` → `repo_brief_assembly`.

## 12. Migration Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | Spine restructure breaks ExecOrchestrator HOP semantics frozen by 3 prior plans | **High** | P3 isolation; legacy env flag `APPS_REPO_BRIEF_LEGACY_PRE_C0=1`; new contract tests gate migration |
| 2 | apps_eval scenarios SKIP if rename partial — biases scorecards | Medium | Keep both scenario sets live P1-P3; flip primary P4 |
| 3 | Two contradictory route declarations + cert/spine inconsistency | Medium | P2 emits ONE canonical route + deprecation aliases; CI gate verifies zero legacy callers P4 |
| 4 | Authoritative-FEC reframe — post-L2 producer → projection adapter | **High** | P3 dedicated wave + Author-Gate; preserve call-site signature; C0-side FEC writer is new SSOT |
| 5 | `repo_brief_docs` L4 surface does not exist yet | **High** | P3 — define schema first, allow template_only fallback during seeding, ship seeder as separate slot |
| 6 | StyleGate relocation changes failure mode | Medium | P3 Author-Gate: hybrid (L2 same-authority repair + Exit hard gate) |
| 7 | OTEL/ADG/cert refs to `apps_exec` literal in spans/ledgers/proofs | Medium | P2 dual span attributes; P4 drops legacy |
| 8 | `apps_shared/proof/scenarios.py` fixtures may hard-code apps_exec IDs | Medium | P1 audits; parallel IDs added; cert harness validates both |
| 9 | P4 deletion surfaces dormant refs (archives, docs/external, operator scripts) | Low-Med | P4 entry gate runs full-repo grep + ADG fan-in scan |
| 10 | Author-Gate fatigue (~6 AGs in this plan) | Low | Pre-seed AG_QUEUE markers §19 |

## 13. Phased Implementation Plan

**Phase 1 — Parallel package (additive only).** Ship `apps_repo_brief/` as working parallel package. Zero removals, zero regressions, all existing tests green.

**Phase 2 — Canonical route + artifact rename.** `apps_repo_brief.executive_brief_v1` becomes canonical; `apps_exec.execution_v1` + `apps_exec.single_step_v1` become deprecated aliases. Resolve cert_route_registry contradiction. Rename artifacts/collection/template-id/routing-target. Dual OTEL emission. Sibling doc/comment updates.

**Phase 3 — Spine restructure.** Move pre-C0 work: `IngestionEngine` retires from runtime (UWG seeder builds `repo_brief_docs`); `CapabilityExtractionEngine` → C0 claim-support producer; `BriefAssemblyEngine` split into PA prompt-assembly + L2 render; `StyleGateValidator` hybrid (L2 repair + Exit gate). Authoritative FEC.v1 produced at C0. `cert/fec_producer.py` reframed as cert projection adapter. Board gates at C0. Cache strict-compat enforcement. 5 new contract tests.

**Phase 4 — Shim sunset.** After P3 green ≥4 weekly eval cycles AND zero-hard-refs gate passes: remove `APPS_EXEC_*` constants, retire `apps_exec` registry rows, retire `apps_exec` scenarios, archive `apps_exec/` → `archives/apps_exec_<ts>/`, drop dual-OTEL emission.

## 14. Files to Rename

`apps_exec/` → `apps_repo_brief/` (parallel P1, primary P2, sole P4). `reasoning/ExecOrchestrator.py` → `reasoning/RepoBriefOrchestrator.py`. `integrations/governed_exec_run.py` → `integrations/governed_repo_brief_run.py`. `spine/exec_spine_adapter.py` → `spine/repo_brief_spine_adapter.py`. `types/exec_types.py` → `types/repo_brief_types.py` (rename `ExecBriefRequest`→`RepoBriefRequest`, `ExecBriefResult`→`RepoBriefResult`). `cert/fec_producer.py` → `cert/cert_projection_adapter.py` (semantic reframe P3). `tests/unit/apps_exec/**` → `tests/unit/apps_repo_brief/**`. Strings: `exec_brief_assembly`→`repo_brief_assembly`, `exec_docs`→`repo_brief_docs`, `exec_brief_*`→`repo_brief_*`.

## 15. Files to Modify

`agentic_core/L0_routing/config/path_constants.py` · `agentic_core/L2_execution/types/agent_taxonomy_registry.py` · `agentic_core/L5_safety/config/structure_blueprint/ssot.py` · `apps_shared/spine_emission/context.py` · `apps_shared/proof/scenarios.py` · `config/cross_app_import_allowlist.yaml` · `apps_eval/engines/scenario_runner.py` · `tools/eval/retrieval_benchmark.py` · `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` · all sibling `apps_*/spine_manifest.yaml` (comments) · `apps_rfp/config/reasoning_toggles_config.py` (comment) · `apps_research/SVP_ENGINEERING_REVIEW.md` · `apps_rg/integrations/spine_handoff.py` (comment).

## 16. Files to Leave Unchanged

`agentic_core/runtime/contracts/lifecycle_trace_contract.py` · `agentic_core/L3_orchestration/exit_eval/v6/**` · `apps_shared/cert/{exit_eval_hook,rubric_output_mapper}.py` · `apps_shared/integrations/governed_app_runner.py` · `apps_shared/spine_emission/governed_run.py` · all other `apps_*` Python source · `tests/_apps_contract/test_app_domain_*`.

## 17. Tests to Add/Update

See §8. **New P3 contract tests:** (a) no pre-C0 retrieval/assembly in `apps_repo_brief`; (b) authoritative FEC.v1 C0-emitted not post-L2; (c) `template_only` cannot produce full board brief; (d) R1B cannot terminal-return board briefs unless strict-compat exact; (e) style violations L2-repair-then-Exit-escalate. **P4 gate:** zero `import apps_exec` outside shim.

## 18. Acceptance Criteria

- `apps_repo_brief` live, all unit+contract tests green
- L0 emits `RouteContract` with `route_id=apps_repo_brief.executive_brief_v1`
- `R3_SIMPLE_GROUNDED_READ` default; C0 required; PA required before L2; L3 off by default
- `template_only` never full board brief; semantic cache cannot terminal-return board briefs unless strict-compat
- Authoritative FEC.v1 produced by C0 before PA/L2
- Post-L2 FEC reframed as cert projection adapter
- Artifacts renamed per §11
- Zero regressions in `tests/_apps_contract/` (currently 299 pass)
- `apps_eval` scenario suite green throughout transition
- P4 deletion gate confirms zero `import apps_exec` outside shim

## 19. Open Questions (AG Queue Seed)

```
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-route-consolidation depends_on= title=Route consolidation (single_step_v1 vs execution_v1)
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-style-gate-placement depends_on=ag-route-consolidation title=StyleGate placement (L2 vs Exit vs hybrid)
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-fec-reframe depends_on=ag-route-consolidation title=Authoritative-FEC reframe (C0 owns; post-L2 is projection)
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-l4-surface-seed depends_on=ag-fec-reframe title=repo_brief_docs L4 surface seeding strategy
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-shim-sunset-date depends_on=ag-fec-reframe,ag-style-gate-placement title=apps_exec shim sunset date and gating criteria
AG_QUEUE_SEED: plan=apps-exec-to-repo-brief-rename-d3f8a2 id=ag-doc-comment-batch depends_on= title=Doc-comment update batching (per-file vs bulk)
```

Other: (1) `apps_research` for board-pack appendix via L3 escalation, or sibling-app boundary? (2) `repo_brief_docs` refresh event-driven (post-merge) or scheduled (nightly)? (3) `head_of_ai` persona P1 first-class or deferred?

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.10 | Parallel package, additive registry, mirrored tests | ~18k | No removals; zero regressions | Not Started | `tests/_apps_contract/` ≥299; new mirror tests pass |
| W2 | P2.1–P2.8 | Canonical route + artifact rename + doc updates + cache compat | ~22k | W1 green; AG-route-consolidation resolved | Not Started | Canonical route live; 0 spine/cert contradictions; dual-alias deprecation live |
| W3 | P3.1–P3.10 | Spine restructure; authoritative FEC at C0; reframe producer; board gates; cache enforcement | ~32k | W2 green; AG-FEC-reframe + AG-style-gate resolved | Not Started | New contract tests green; pre-C0 legacy path retired |
| W4 | P4.1–P4.7 | Shim sunset; cleanup; archive apps_exec | ~10k | W3 green ≥4 weekly cycles; zero hard refs | Not Started | P4 gate test passes; archive exists; CI green |

## Phase-Level Summary

| Phase | Title | Scope | Pain Points | Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Package skeleton | `apps_repo_brief/__init__.py`, dirs | — | 1k | Not Started |
| P1.2 | Reasoning re-export | `apps_repo_brief/reasoning/__init__.py` | name collisions | 1k | Not Started |
| P1.3 | spine_manifest | `apps_repo_brief/spine_manifest.yaml` | resolve contradiction | 1.5k | Not Started |
| P1.4 | Route registries | `apps_repo_brief/config/{route,cert_route}_registry.yaml` | consolidation deferred to P2.1 | 1.5k | Not Started |
| P1.5 | path_constants | `agentic_core/L0_routing/config/path_constants.py` | additive only | 1.5k | Not Started |
| P1.6 | taxonomy + ssot | `agent_taxonomy_registry.py`, `structure_blueprint/ssot.py` | additive | 1.5k | Not Started |
| P1.7 | allowlists | `apps_shared/spine_emission/context.py`, `config/cross_app_import_allowlist.yaml` | additive | 1k | Not Started |
| P1.8 | app_inventory | `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` | additive row | 1k | Not Started |
| P1.9 | Eval scenarios | `apps_eval/engines/scenario_runner.py`, `apps_shared/proof/scenarios.py`, `tools/eval/retrieval_benchmark.py` | dual scenarios coexist | 2.5k | Not Started |
| P1.10 | Mirror tests | `tests/unit/apps_repo_brief/**` | mechanical mirror | 5k | Not Started |
| P2.1 | AG: route consolidation | decision | Author-Gate | 0.5k | Not Started |
| P2.2 | Route migration | route + cert_route registries | dual-aliasing | 2k | Not Started |
| P2.3 | Fix C0 contradiction | cert_route_registry text | text-only | 0.5k | Not Started |
| P2.4 | Artifact rename | output paths, orchestrator, run-summary | string literals | 2k | Not Started |
| P2.5 | Routing target rename | `exec_brief_assembly`→`repo_brief_assembly` | sweep | 1k | Not Started |
| P2.6 | OTEL dual-span | span emitter | dual window | 1k | Not Started |
| P2.7 | Sibling doc updates | sibling `apps_*` comments | sweeps | 2k | Not Started |
| P2.8 | Cache compat schema | `apps_repo_brief/config/cache_compat.yaml` + test | strict-compat | 2k | Not Started |
| P3.1 | AG: pre-C0 movement | decision | Author-Gate | 0.5k | Not Started |
| P3.2 | IngestionEngine retirement | runtime removal; UWG seeder | live-scan → L4 | 5k | Not Started |
| P3.3 | CapabilityExtractionEngine → C0 | claim-support producer | relocation | 4k | Not Started |
| P3.4 | BriefAssemblyEngine split | PA (prompt) + L2 (render) | layer refactor | 5k | Not Started |
| P3.5 | StyleGate hybrid placement | L2 repair + Exit gate | AG-decision-driven | 3k | Not Started |
| P3.6 | Authoritative FEC.v1 at C0 | `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py` | new contract | 4k | Not Started |
| P3.7 | FEC producer reframe | `apps_repo_brief/cert/cert_projection_adapter.py` | signature preservation | 3k | Not Started |
| P3.8 | Board gates at C0 | section-coverage, hard-blocks | new logic | 3k | Not Started |
| P3.9 | Cache compat enforcement | L0/R1A/R1B runtime check | hard gate | 2k | Not Started |
| P3.10 | New contract tests | 5 new `tests/_apps_contract/` files | ≥20 cases | 4k | Not Started |
| P4.1 | AG: shim sunset date | decision | Author-Gate | 0.5k | Not Started |
| P4.2 | P4 gate test | `test_no_apps_exec_python_imports_outside_shim` | grep+AST | 1k | Not Started |
| P4.3 | path_constants cleanup | remove `APPS_EXEC_*` | dead-code | 1k | Not Started |
| P4.4 | Registry cleanup | retire apps_exec rows | dead-code | 1.5k | Not Started |
| P4.5 | Scenario cleanup | remove apps_exec scenarios | removal | 1k | Not Started |
| P4.6 | Archive package | `archives/apps_exec_<ts>/` | git mv | 1k | Not Started |
| P4.7 | Drop dual-OTEL | single span | cleanup | 1k | Not Started |

## ADG_HOTSPOT_REPORT

| Node | Layer | Fan-In | Blast 2-hop | Archetype | Surface | Mult | Impact |
|---|---|---|---|---|---|---|---|
| `apps_exec/__main__.py` (id 2635) | L_APP | 0 | 0 | ENTRYPOINT | Execution, Obs | 1.0 | Entrypoint; rename safe |
| `apps_exec.reasoning.ExecOrchestrator` | L_APP | 1 (eval lazy) | bounded by allowlist | ORCHESTRATOR | Execution | 1.0 | SKIP-fallback isolates blast |
| `apps_exec.cert.fec_producer` | L_APP | `apps_shared/cert` consumers | bounded | STATE_NODE (FEC writer) | State, Obs | 1.0 | **P3 hotspot — reframe to projection** |
| `apps_exec.types.exec_types` | L_APP | 8 service tests + scenario_runner | bounded | CENTRAL_DEPENDENCY | Execution | 1.0 | **Highest blast risk — P1 type re-export required** |
| `apps_exec.spine.exec_spine_adapter` | L_APP | 1 governance test | minimal | ENTRYPOINT | Execution | 1.0 | Clean rename P1 |

Highest-impact node: `apps_exec.types.exec_types` — mitigation: P1 adds `apps_repo_brief.types.repo_brief_types` re-exporting same names; P2 flips primary; P4 retires. ADG provenance: backend=sqlite, snapshot=`adg_indexed_<ts>.sqlite`, stale=false.

## ADG_GRAPH_LAYER_EVIDENCE

**MVs consulted:** (1) `mv_hotspot_centrality` — `apps_exec/__main__.py` near-zero degree_centrality (entrypoint terminal). (2) `mv_graph_reverse_dependency_hotspots` — top reverse-deps cluster around types module + FEC producer + Orchestrator; drives P1 type-shim. (3) `mv_graph_chokepoint_bridges` — `apps_shared.integrations.governed_app_runner.GovernedAppRunner` is chokepoint to agentic_core; substrate must NOT change, only subclass.

**Semantic edges:** `flows_to` — `ExecBriefRequest → ExecOrchestrator.run → IngestionEngine → CapabilityExtractionEngine → BriefAssemblyEngine → StyleGateValidator → emit` (current pre-C0 flow; target collapses to U0/L1). `emits_side_effect` — `IngestionEngine` filesystem-read from L_APP (target: L4 retrieval surface). `controls_flow` — `cert_route_registry.invoke_exit_eval=true` controls `_maybe_run_exit_hook`.

**P-views:** `v_p1_*` (mis-layered infra) flags `apps_exec.engines.{ingestion,capability_extraction,brief_assembly}_engine` as P3 relocation candidates. `v_p3_*` (isolated experimental) flags `apps_exec.engines.hop_*` shims for P1 retirement. ADG provenance: backend=sqlite. Refresh `tools/generate_full_adg.py` before W3.

## AI Summary

- Target: rename `apps_exec` → `apps_repo_brief` + repair canonical spine (U0→L1→L0→C0→PA→L2→Exit→L6)
- Closes naming defect + pre-C0 work + contradictory route declarations + post-L2 authoritative FEC anti-pattern
- New files: `apps_repo_brief/` parallel package (P1), `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py` (P3), `apps_repo_brief/cert/cert_projection_adapter.py` (P3), `apps_repo_brief/config/cache_compat.yaml` (P2), 5 new contract tests (P3), P4 gate test
- Edits: `agentic_core/L0_routing/config/path_constants.py`, `agent_taxonomy_registry.py`, `structure_blueprint/ssot.py`, `apps_shared/spine_emission/context.py`, `apps_eval/engines/scenario_runner.py`, sibling `apps_*` doc comments
- Pattern source: mirrors apps-eval-harness-parity-f8d4a2 dual-rollout / apps-exec-c0-fec-producer-wiring-c2e8a5 FEC pattern. 4 waves, ~80k tokens
- Non-goals: broad unrelated refactors · blind rename · premature `apps_exec` deletion · C0 generating prose · PA retrieving · L2 or Exit writing L4 · L6 mutating current run · app HOPs bypassing canonical spine
- Success: zero cross-app Python-import breaks · L0 emits canonical route · `template_only` never full board brief · authoritative FEC at C0 · P4 gate proves zero hard refs

**PLAN_CREATED:** `.windsurf/plans/apps-exec-to-repo-brief-rename-d3f8a2.md`
