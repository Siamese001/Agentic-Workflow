---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pipeline-deferred-e9f2a4.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pipeline-deferred-e9f2a4.md'
source_sha256: c48fd6bef1085ab8fc534b6b639e4ebb99dd094acf89f51bf96ada57aa560839
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-pipeline-deferred-e9f2a4
plan_type: refactor
parent_plan: apps-rg-runtime-wiring-completion-d4e8a1
---

# apps_rg Pipeline — Deferred Scope

Successor plan capturing all scope explicitly deferred during `apps-rg-runtime-wiring-completion-d4e8a1` so the parent plan could close cleanly with a working live LLM E2E. Each row below was a verification-vs-deferral entry tracked by the parent plan's DoD section.

---

## Context (SCQA)

- **Situation** — Parent plan `apps-rg-runtime-wiring-completion-d4e8a1` shipped a fully operational `python -m apps_rg` pipeline: 7 layer bindings (U0→L1→L0→C0→PA→L2→Exit), real Qwen 32B AWQ inference (~21s), cryptographic provenance chain, fail-soft fallback, and 3 new CI gates (APPS-IMPORT/APPS-DRYRUN/PLAN-DOD). Notion `35b27693-f55c-8161-aa25-dcb20efcdf3b` Completed 2026-05-09.
- **Complication** — To keep the parent plan focused on "first working end-to-end pipeline + DoD discipline", twelve capability/quality items were intentionally deferred. They were tracked in the parent's Verification-vs-Deferral table and in memory `bf13593c-65f1-4541-83c9-13ef837eb2b7`. Without a successor plan, those items become invisible.
- **Question** — How do we land the deferred capability/quality items in priority order without re-opening the parent plan?
- **Answer** — One T2/T3 plan with 4 waves, each addressing a coherent slice of deferred scope, prioritized by impact: capability tests first (close the test-theater gap), then variant routing + retrieval quality, then ecosystem cleanup (test fixes + DoD backlog), then optional observability/orchestration.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Parent plan `.windsurf/plans/apps-rg-runtime-wiring-completion-d4e8a1.md` | source of deferred items (RCA §2, Verification-vs-Deferral) | 🔲 |
| Memory entity `bf13593c-65f1-4541-83c9-13ef837eb2b7` | session-end deferred-scope inventory | 🔲 |
| `tests/_apps_contract/test_apps_rg_*.py` (24 files) | classify negative-pattern vs capability per W1.P2 audit | 🔲 |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | binding chain to assert capabilities against | 🔲 |
| `apps_rg/config/domain_contract/route_profiles.yaml` | variant routing options (default / executive / short_form) | 🔲 |
| `artifacts/ci/plan_dod_gate.json` | 301-plan DoD backlog inventory | 🔲 |

---

## 1. Deferred Items Inventory (from parent plan)

| ID | Item | Source | Severity |
|---|---|---|---|
| DS-1 | Capability tests for apps_rg pipeline (close test theater gap from RCA §2.2) | Parent W1.P2 | High |
| DS-2 | 4 broken pre-existing apps_rg tests (test theater, quarantine import, stale R4 expectations) | Parent W4.P2 regression check | High |
| DS-3 | L0 routing variant selection (executive / short_form vs default-only) | Parent W3.P3 routing rationale | Medium |
| DS-4 | C0 PDF parsing for manual brief (currently path-reference only) | Parent W3.P4 C0 binding | Medium |
| DS-5 | C0 real retrieval system integration (semantic chunking, similarity search) | Parent W3.P4 stub | Medium |
| DS-6 | OTel span emission for apps_rg dispatch chain | Not in parent; infrastructure exists | Medium |
| DS-7 | Provenance chain assertions in tests (compilation_hash matching) | Parent W3 cross-stage chain | Medium |
| DS-8 | 301-plan DoD backlog cleanup (PLAN-DOD advisory baseline) | Parent W6 first-run output | Low |
| DS-9 | L2 binding via SovereignLLMGateway (vs direct urllib) — circuit breaker/metrics | Parent W5 alternative | Low |
| DS-10 | L3 managed-workflow path enablement | Parent §3 non-goal; route profile allows | Low |
| DS-11 | Full 24-test classification audit (negative-pattern vs capability) | Parent W1.P2 deferred | Low |
| DS-12 | Token-budget logic for FEC inlining (currently 6000-char cap) | Parent W3.P4 PA stub | Low |

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2, P1.3 | Capability tests + broken-test cleanup (DS-1, DS-2, DS-7, DS-11) | ~12k | Test framework unchanged; quarantine policy stable | Not Started | 7 capability tests pass (one per binding); 4 broken tests fixed-or-deleted with explicit ADR; provenance-chain assertions pass; W1.P2 audit doc published |
| W2 | P2.1, P2.2 | Routing + retrieval quality (DS-3, DS-4, DS-5, DS-12) | ~14k | route_profiles.yaml stable; pypdf available | Not Started | Executive variant fires for target_level=EXECUTIVE; manual brief PDF parsed into evidence items; C0 chunking landed; FEC token budget configurable |
| W3 | P3.1, P3.2 | Observability + gateway routing (DS-6, DS-9) | ~10k | OTEL infra unchanged; SovereignLLMGateway stable | Not Started | Per-stage OTEL spans emitted; SovereignLLMGateway path optional via env var |
| W4 | P4.1, P4.2 | Backlog cleanup (DS-8, DS-10) | ~8k | DoD backlog tractable; L3 DAG infra optional | Not Started | DoD backlog under 100 (or `dod_exempt:true` set on legitimate exemptions); L3 path opt-in via route_profiles |

Total: ~44k tokens, 9 phases, 4 waves.

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Capability test suite | `tests/_apps_contract/test_apps_rg_pipeline_capability.py` (NEW) | Must instantiate real bindings; force-stub L2 via env var | ~5k | Not Started |
| P1.2 | Broken test cleanup | `tests/_apps_contract/test_apps_rg_{main_is_thin_core_shim,fail_closed,fec_producer,legacy_cleanup}.py` | Some tests reference old R4-runner shape; some import quarantined modules; ADR needed for delete-vs-fix decision | ~4k | Not Started |
| P1.3 | Provenance-chain assertions | `tests/_apps_contract/test_apps_rg_provenance_chain.py` (NEW) | Must run live OR force-stub mode | ~3k | Not Started |
| P2.1 | L0 variant routing | `agentic_core/L0_routing/apps_rg_l0_binding.py` + `agentic_core/runtime/contracts/l1_plan_contract.py` (target_level field?) | Decide: extend L1Plan with target_level or pass envelope to L0; minor architectural choice | ~5k | Not Started |
| P2.2 | C0 PDF parsing + retrieval | `agentic_core/runtime/c0/apps_rg_c0_binding.py` + new pypdf dep | pypdf adds dep; need text-extraction fail-soft; chunking strategy decision | ~9k | Not Started |
| P3.1 | OTEL spans for dispatch chain | `agentic_core/runtime/entry/apps_rg_dispatch.py` (instrument try/except blocks) | Existing OTEL bridge available; per-stage span name conventions | ~5k | Not Started |
| P3.2 | Optional SovereignLLMGateway path | `agentic_core/L2_execution/apps_rg_l2_binding.py` (opt-in env var) | Gateway is heavier; default stays on direct urllib | ~5k | Not Started |
| P4.1 | DoD backlog cleanup | `.windsurf/plans/*.md` (301 files) | Mostly mechanical: add `dod_exempt: true` to RCA/doc plans; add real DoD to active plans | ~5k | Not Started |
| P4.2 | L3 managed-workflow opt-in | `agentic_core/L0_routing/apps_rg_l0_binding.py` + L3 binding (NEW) | Route profile permits but binding doesn't exist; large architectural addition | ~3k | Not Started |

---

## 4. Definition of Done

> Mandatory per `.windsurf/rules/plan-location.md` §5 (added by parent plan W6).

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Capability tests pass with real bindings (no mocks) | `pytest tests/_apps_contract/test_apps_rg_pipeline_capability.py -v` shows 7+ passes | 🔲 |
| DoD-2 | `python -m apps_rg --target-company X --target-role Y --target-level EXECUTIVE ...` selects executive route variant in disposition | Inspect `route.route_id` in `final_output` for EXECUTIVE input — matches `rg.resume_generation.executive` | 🔲 |
| DoD-3 | Manual brief PDF parsed into FEC evidence_items with content_type='text' (not 'path_reference') | Check `final_output.fec.evidence_items` for brief: items have non-empty content + content_type='text' | 🔲 |
| DoD-4 | All 4 broken pre-existing tests fixed or explicitly deleted with ADR | `pytest tests/_apps_contract/test_apps_rg_*.py` shows 0 errors (excluding intentional skips) | 🔲 |
| DoD-5 | DoD backlog reduced from 301 to <100 plans missing DoD | `python ops_scripts/ci/check_plan_definition_of_done.py` reports <100 violations | 🔲 |
| DoD-6 | Per-stage OTEL spans visible in trace for one Brown & Brown live run | `otel_mcp.otel_trace(<trace_id>)` shows 7 child spans (U0/L1/L0/C0/PA/L2/Exit) | 🔲 |
| DoD-7 | Provenance chain assertions enforce digest matching across 5 boundaries | `pytest tests/_apps_contract/test_apps_rg_provenance_chain.py` shows 5+ assertion passes | 🔲 |

**Verification-vs-Deferral**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Real C0 semantic-chunking + similarity-search retrieval (DS-5 full) | Out of scope for this plan; depends on apps_qna c0 retrieval system that is itself in flux. P2.2 lands minimal text-chunking only. | Future plan if C0 retrieval becomes blocker |
| L3 DAG full implementation (DS-10) | Single-step path is sufficient for current resume_generation use cases. P4.2 lands the OPT-IN flag only; full DAG binding is deferred. | Future plan if multi-step resume flows become a requirement |

---

## 5. Files In Scope

| File | Action | Wave |
|---|---|---|
| `tests/_apps_contract/test_apps_rg_pipeline_capability.py` | NEW | W1 |
| `tests/_apps_contract/test_apps_rg_provenance_chain.py` | NEW | W1 |
| `tests/_apps_contract/test_apps_rg_main_is_thin_core_shim.py` | EDIT (test_main_passes_app_name expectation) | W1 |
| `tests/_apps_contract/test_apps_rg_fail_closed.py` | EDIT or DELETE (per ADR) | W1 |
| `tests/_apps_contract/test_apps_rg_fec_producer.py` | EDIT (skip on quarantine) or DELETE | W1 |
| `tests/_apps_contract/test_apps_rg_legacy_cleanup.py` | EDIT (skip on quarantine) or DELETE | W1 |
| `docs/architecture/adr/ADR-NNN-apps-rg-test-theater-cleanup.md` | NEW | W1 |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | EDIT (variant selection) | W2, W4 |
| `agentic_core/runtime/contracts/l1_plan_contract.py` | EDIT (add target_level?) | W2 |
| `agentic_core/runtime/c0/apps_rg_c0_binding.py` | EDIT (PDF parsing, chunking) | W2 |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | EDIT (OTEL spans) | W3 |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | EDIT (gateway opt-in) | W3 |
| `pyproject.toml` or `requirements.txt` | EDIT (pypdf dep) | W2 |
| `.windsurf/plans/*.md` (301 files) | EDIT (add DoD or `dod_exempt: true`) | W4 |

---

## 6. ADG_HOTSPOT_REPORT

> NOTE: this plan touches one new central node (`apps_rg_dispatch.py`) and reuses the 7 binding files which are already structurally well-bounded (no fan-in pollution). Hotspot report is therefore short.

| Node | Layer | Fan-in | Fan-out | Archetype | Surfaces | Multiplier | Impact |
|---|---|---|---|---|---|---|---|
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | L0/runtime | 1 (only `apps_rg/__main__.py`) | 7 (one per binding) | ORCHESTRATOR | Execution, Observability | 2.0 | Low |
| `agentic_core/runtime/c0/apps_rg_c0_binding.py` | L0/runtime | 1 (dispatch) | 4 (FEC + payload + path utilities) | STATE_NODE (evidence) | Execution, Observability | 2.0 | Low |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | L2 | 1 (dispatch) | 5 (urllib, health probe, prompt, sealed, model registry) | CENTRAL_DEPENDENCY (LLM call) | Execution, Security (egress) | 1.0 | Low |

All three nodes have fan-in=1 (from dispatch only), so changes are scope-contained.

---

## 7. ADG_GRAPH_LAYER_EVIDENCE

| MV / Edge / View | Evidence | Relevance |
|---|---|---|
| `mv_hotspot_centrality` | `apps_rg_dispatch` node centrality is low (single in-edge from `apps_rg/__main__.py`) | Confirms scope-contained changes |
| `flows_to` semantic edges | dispatch → 7 bindings → 7 contract types | Verifies pipeline shape unchanged from parent plan |
| `emits_side_effect` | `apps_rg_l2_binding._post_chat_completion` is the only network egress in scope | Constrains W3 SovereignLLMGateway routing decision |
| `v_p2_safety_gatekeepers` | U0 binding (authority validation) is the safety gate; cannot be weakened by this plan | Constrains W2 routing changes |
| `resolves_callsite` | `is_qwen_available` resolves to `vllm_health_probe.probe()` | Confirms W3 OTEL instrumentation insertion point |

---

## 8. Non-Goals

- Full L3 managed-workflow DAG implementation (P4.2 lands opt-in flag only)
- Replacing direct urllib with mandatory SovereignLLMGateway routing (P3.2 lands opt-in only)
- Real C0 semantic-chunking + similarity-search (P2.2 lands text-chunking only)
- Re-litigating the parent plan's RCA findings or the ingress-only governance posture
- Restoring `apps_rg.cert` or `apps_rg.prompt_assembly` from quarantine (W4 quarantine is correct; broken tests that import them get fixed or deleted with ADR)
- New apps onboarding (apps_lic, apps_rfp, apps_research, apps_underwriting_ai) — those have their own plans

---

## 9. Dependencies + Sequencing

- W1 must land before W2 — capability tests serve as the regression-detection net for W2 routing/retrieval changes
- W2.P2 needs `pypdf` dep added; coordinate with infrastructure team if dep policy requires review
- W3.P1 OTEL instrumentation depends on existing `otel_lifecycle_bridge` API stability
- W4.P2 L3 opt-in flag is independent — can land in any order with W1-W3
- DoD backlog cleanup (W4.P1) is independent and can land in parallel with any wave

---

## 10. Rollback Strategy

Per-wave rollback is straightforward because each wave touches an isolated set of files (see §5). If a wave breaks the live pipeline:

1. `git revert <wave-commit-sha>` for the offending wave
2. Re-run `python ops_scripts/ci/check_apps_rg_dryrun.py` and `python -m apps_rg ... --target-company "Brown & Brown" ...` to verify pipeline still reaches `exit_status='success'`
3. The 3 W6 CI gates (APPS-IMPORT, APPS-DRYRUN, PLAN-DOD) catch regressions automatically

---

## 11. Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Test pass count | +7 capability + +5 provenance = +12 new passes vs baseline | `pytest tests/_apps_contract/ -k apps_rg` |
| Broken-test count | 0 (currently 4 broken from quarantine) | `pytest tests/_apps_contract/test_apps_rg_*.py` no errors |
| DoD backlog | <100 plans missing DoD (currently 301) | `python ops_scripts/ci/check_plan_definition_of_done.py` |
| OTEL coverage | 7 child spans visible in one live trace | `otel_mcp.otel_trace(<trace_id>)` from a live run |
| Live pipeline reachability | Brown & Brown invocation still exits 0 with execution_status='completed' | `python -m apps_rg --target-company "Brown & Brown" ...` |

---

## 12. Cascade Alignment Checks

- ADG-first: all routing decisions consult `agentic_core/L0_routing/apps_rg_l0_binding.py` and `route_profiles.yaml` before changing variant selection logic
- DoD-first: every wave has DoD rows in its own success criteria column above; plan template enforced
- Fail-soft preserved: W3.P2 SovereignLLMGateway routing must NOT remove the existing fail-soft fallback in `apps_rg_l2_binding.py`
- Scope-contained: parent plan's pattern (pure functions per binding, contract-typed boundaries) is invariant — this plan extends, never refactors
