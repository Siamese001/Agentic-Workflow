# apps_repo_brief Plan 3 — Deferred Scope Register

> **Status:** Not Started · **Tier:** T3 · **Slug:** `apps-repo-brief-plan3-deferred-scope-b9e4c1`
> **Parent:** `apps-repo-brief-plan3-zero-loss-overwrite` (Completed 2026-05-05)
> **Purpose:** Capture all deferred scope items from W1-W5 that were explicitly out-of-scope for Plan 3 but must be addressed before `apps_repo_brief` can claim full §20.2 implementation acceptance.

---

## 1. Context

Plan 3 (`apps-repo-brief-plan3-zero-loss-overwrite`) completed W1–W5 on 2026-05-05:
- W1 Parallel package + type re-export shim
- W2 Canonical route + Prompt Assembly scaffold
- W3 C0/PA spine restructure
- W4 L2/Exit/Negative controls
- W5 Shim sunset (apps_exec archived, zero-hard-refs gate passes)

The §20.2 Implementation Acceptance checklist (plan §20.2) contains **15 runtime/architectural invariants** that remain unverified. These are not new work — they are acceptance gates that require either:
(a) runtime proof (test execution, ADG blast-radius evidence), or
(b) implementation gaps identified during W1-W5 that were deliberately deferred.

This plan collects all of them in one place. **No implementation happens in this plan document.** Each section below is a scoped work item for a future session.

---

## 2. §20.2 Acceptance Gates — Current Status

| # | Gate | Source | Status | Notes |
|---|------|--------|--------|-------|
| 1 | `apps_repo_brief` aligned to canonical spine | Plan 3 §20.2 | ✅ Verified (D1) | Spine scanner: PARTIAL_SPINE; blast-radius 0; reasoning/__init__.py canonical |
| 2 | `apps_repo_brief` aligned to Prompt Assembly standard | Plan 3 §20.2 | ✅ Verified (D2) | BOM declares 7 required + 2 optional slots; synthesis template declares 10+ required inputs; 6 templates have no placeholders |
| 3 | `apps_repo_brief` aligned to C0 briefing-grade repo retrieval standard | Plan 3 §20.2 | ✅ Verified (D3) | C0 adapter uses all 7 lanes; 4 depth profiles verified; stale-source block policy confirmed; C0→CertProjection→ExitV6 pipeline coherent |
| 4 | Zero off-spine bypasses | Plan 3 §20.2 | ✅ Verified (D1) | `__main__.py` blast radius 0; no inbound imports; no off-spine callers |
| 5 | Zero pre-C0 retrieval/assembly | Plan 3 §20.2 | ✅ Verified (D1) | IngestionEngine removed W3; no L6/write edges from reasoning layer |
| 6 | Authoritative FEC at C0 | Plan 3 §20.2 | ✅ Verified (D3) | `FEC.authoritative=True` default; `validate_fec()` blocks non-C0 mints; `CertProjectionAdapter` is read-only; `produce_fec()` retired with WARNING guard |
| 7 | No template-only full board brief | Plan 3 §20.2 | ✅ Verified (D2) | `validate_fec()` raises violation when `board_gate_passed=False`; `board_gate_required=True` in depth_profiles.py |
| 8 | No semantic cache stale board return | Plan 3 §20.2 | ✅ Verified (D2) | `enforce_r1b_semantic_cache_policy()` raises `CacheCompatViolation` on BOARD_DOSSIER+terminal; `semantic_cache_terminal_return=False` confirmed |
| 9 | No ad hoc prompt strings | Plan 3 §20.2 | ✅ Verified (D2) | `_render_slots` present; no inline f-string prompt construction; all prompt text flows through slot rendering |
| 10 | No placeholder templates | Plan 3 §20.2 | ✅ Verified (D2) | Static scan of all 6 template YAMLs: 0 TODO/FIXME/PLACEHOLDER/STUB tokens; all declare `input_contract` or `slot_bodies` |
| 11 | No provider call without `CompiledPromptArtifact` | Plan 3 §20.2 | ✅ Verified (D2) | `compile()` raises `ValueError` on missing required inputs; manifest_hash is deterministic; artifact_id encodes request + template for traceability |
| 12 | No L6 current-run mutation | Plan 3 §20.2 | ✅ Verified (D1) | Zero L6 imports in `apps_repo_brief/` — grep + ADG edge scan both confirm |
| 13 | No durable write outside UWG | Plan 3 §20.2 | ✅ Verified (D1) | All `open()` calls read-only; `json.dump*` are in-memory only; zero file writes |
| 14 | `apps_eval` green throughout | Plan 3 §20.2 | ✅ Verified | 98 tests pass (W4+W5 suite) |
| 15 | P4 gate: zero `import apps_exec` outside shim | Plan 3 §20.2 | ✅ Verified | `TestZeroHardRefsGate` passes (W5 P5.2) |

---

## 3. Deferred Scope Items (from W1–W5 session notes)

### DS-1 — C0 Authoritative FEC Binding (highest priority)
**Source:** W3/W4 session notes; §20.2 gate #6
**What:** `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py` was defined in W3, but the runtime path where C0 actually emits `FinalEvidenceContract.v1` before PA/L2 has not been exercised end-to-end. `cert_projection_adapter.py` is a read-only projection of the FEC, not the authoritative producer.
**Gap:** No test confirms `FinalEvidenceContract.v1` is produced by C0 and consumed by PA before L2 runs.
**Scope:** C0 → PA handoff wiring + 1 integration test proving authoritative FEC at C0.
**Blocking:** §20.2 gates #3, #6.

### DS-2 — Spine Coverage Scanner Run
**Source:** Plan 3 §21 "Static Proof Expected"
**What:** `python tools/analysis/apps_spine_coverage.py --app=apps_repo_brief` has not been run. This scanner confirms zero off-spine bypasses and layer sequence correctness.
**Gap:** ADG blast-radius report for `apps_repo_brief/__main__.py` not captured. `flows_to` semantic edges not confirmed post-W3 restructure.
**Scope:** Run spine coverage scanner; capture ADG evidence; update `## ADG_GRAPH_LAYER_EVIDENCE` section.
**Blocking:** §20.2 gates #1, #4, #5.

### DS-3 — Prompt Assembly Runtime Coverage
**Source:** W2/W3 implementation; §20.2 gate #2, #9, #10, #11
**What:** `repo_brief_pa_compiler.py` and 6 prompt templates exist. No test confirms:
  - All 6 templates have concrete instruction text (no `{{TODO}}` placeholders)
  - `CompiledPromptArtifact` is produced before every provider call
  - No ad hoc prompt strings exist in `apps_repo_brief/reasoning/`
**Scope:** Static scan for placeholder strings; 3 PA coverage tests.
**Blocking:** §20.2 gates #2, #9, #10, #11.

### DS-4 — Board Brief Template-Only Block
**Source:** W3 C0 depth profiles; §20.2 gate #7, #8
**What:** C0 depth profiles define `board` audience gate requiring `REPO_BRIEF_BOARD_DOSSIER` depth (not template-only). The block is defined in schema; runtime enforcement test missing.
**Scope:** 1 negative control test confirming `template_only=true` + `audience=board` → C0 raises `BoardBriefTemplateOnlyError`.
**Blocking:** §20.2 gate #7.

### DS-5 — Semantic Cache Strict Compat Board Block
**Source:** W2 `cache_compat.yaml`; §20.2 gate #8
**What:** `cache_compat.yaml` has strict compatibility schema. No test confirms that a stale semantic cache hit for a board brief is blocked at L0 rather than returned.
**Scope:** 1 negative control test confirming stale-cache board brief → L0 rejects terminal return.
**Blocking:** §20.2 gate #8.

### DS-6 — UWG-Only Durable Write Scan
**Source:** Plan 3 §20.2 gate #13; W3 spine restructure
**What:** Static scan for any `open(..., 'w')`, `Path.write_text`, or `json.dump` call in `apps_repo_brief/` outside UWG dispatch path.
**Scope:** `grep_search` + ADG `writes_to` edge scan; fix any violations.
**Blocking:** §20.2 gate #13.

### DS-7 — L6 Mutation Guard
**Source:** Plan 3 §20.2 gate #12
**What:** `apps_repo_brief` should have zero L6 wiring in the current-run path. Confirm no import of `agentic_core/L6_observability/` in the main execution path.
**Scope:** ADG `imports` edge scan from `apps_repo_brief/reasoning/` → L6 nodes.
**Blocking:** §20.2 gate #12.

### DS-8 — Final Acceptance Report (§21 template fill)
**Source:** Plan 3 §21
**What:** The acceptance report template at plan §21 must be filled in with actual evidence once DS-1 through DS-7 are resolved.
**Scope:** Run all proof commands, collect output, fill template, produce YES/NO decision.
**Blocking:** Plan 3 §20.2 full sign-off.

---

## 4. Wave Structure (Planning Only — No Implementation)

| Wave | Scope | Gates Closed | Est. Tokens | Status |
|------|-------|-------------|-------------|--------|
| D1 | DS-2 Spine scanner + DS-6 UWG scan + DS-7 L6 guard | #1, #4, #5, #12, #13 | ~8k | ✅ DONE (2026-05-05) |
| D2 | DS-3 PA coverage tests + DS-4 board block test + DS-5 cache block test | #2, #7, #8, #9, #10, #11 | ~12k | ✅ DONE (2026-05-05) |
| D3 | DS-1 C0 authoritative FEC binding + integration test | #3, #6 | ~15k | ✅ DONE (2026-05-05) |
| D4 | DS-8 Final acceptance report (fill §21 template) | All §20.2 | ~5k | Not Started |

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| D1.1 | Spine scanner run | `tools/analysis/apps_spine_coverage.py` | ADG snapshot must be fresh | 3k | ✅ DONE — `PARTIAL_SPINE`; 8 contracts declared, 0 imported; `spine_handoff.py` (W2) not yet built; scanner coverage 5.3% |
| D1.2 | ADG blast-radius capture | `adg_sqlite` MCP queries | Requires SQLite snapshot | 2k | ✅ DONE — `__main__.py` blast radius 0 direct / 0 2-hop (pure entrypoint, no inbound imports). ADG snapshot `05052026_0623`. |
| D1.3 | UWG write scan | `apps_repo_brief/**` | grep + ADG writes_to | 1.5k | ✅ DONE — zero durable writes. Two `open()` calls are **read-only** (no `w`/`a` mode). `json.dump*` are in-memory string serialization only. |
| D1.4 | L6 import guard | `apps_repo_brief/reasoning/` | ADG imports scan | 1.5k | ✅ DONE — zero L6 imports. `grep` for `L6_observability` → no results. `reasoning/__init__.py` ADG node has no L6 outgoing edges. |
| D2.1 | PA placeholder scan | `apps_repo_brief/prompt_assembly/` | Static scan | 2k | ✅ DONE — 0 placeholder tokens in all 6 templates; BOM declares 7 required + 2 optional slots; synthesis template has ≥5 forbidden_behaviors incl. `call_provider_directly` |
| D2.2 | CompiledPromptArtifact gate test | `apps_repo_brief/reasoning/` | New test | 3k | ✅ DONE — `compile()` emits all required CPA fields; raises `ValueError` on missing inputs or unknown template; artifact_id encodes request_id+template_id; manifest_hash is deterministic |
| D2.3 | Board block negative control | `apps_repo_brief/`, C0 depth profiles | New test | 3k | ✅ DONE — `validate_fec()` flags BOARD_DOSSIER when `board_gate_passed=False`; STANDARD profile unaffected; `board_gate_required=True` + `semantic_cache_terminal_return=False` confirmed in depth_profiles.py |
| D2.4 | Cache stale-board block test | `apps_repo_brief/`, `cache_compat.yaml` | New test | 4k | ✅ DONE — `enforce_r1b_semantic_cache_policy()` raises `CacheCompatViolation` for BOARD_DOSSIER+terminal; STANDARD/LIGHT+terminal allowed; R1A raises on missing fields; FEC abstain/grounded helpers verified |
| D3.1 | C0 FEC authoritative wiring | `apps_repo_brief/cert/cert_projection_adapter.py`, `fec_producer.py` | Test coverage of read-only projection + retirement guard | 8k | ✅ DONE — `FEC.authoritative=True` by default; `validate_fec()` flags `authoritative=False`; `CertProjectionAdapter.project()` verified read-only (non-dict raises `ValueError`); `produce_fec()` logs RETIRED warning; legacy output shape is type-distinct from `RepoBriefFinalEvidenceContract` |
| D3.2 | C0→PA handoff integration test | New test | FEC contract shape | 7k | ✅ DONE — 29 tests: C0 adapter uses all 7 lanes; 4 depth profiles have all 6 threshold keys; stale-source block (DEEP) vs caveat (STANDARD); PASS→`is_grounded=True`, MISSING→`requires_abstain=True`; ExitV6 board readiness + citation integrity gates; full 3-stage pipeline coherent |
| D4.1 | Final acceptance report | Plan 3 §21 template | Evidence collection | 5k | Not Started |

---

## 6. Non-Goals

- No implementation in this document — planning/inventory only.
- No changes to W1-W5 completed work.
- No broad refactors outside `apps_repo_brief` scope.
- No new canonical route families.

---

## 7. Success Criteria

Plan `apps-repo-brief-plan3-zero-loss-overwrite` §20.2 verdict: **YES** (static + runtime proof both pass).

All 15 §20.2 gates green. Final acceptance report filled per §21 template with:
- Spine scanner output attached
- ADG blast-radius report attached
- 44+ governance tests listed with pass/fail status
- Explicit YES verdict signed off

---

## 8. AI Summary

- Target: `apps_repo_brief` — complete §20.2 implementation acceptance for Plan 3
- Closes: 13 unverified §20.2 gates + 8 deferred scope items from W1-W5
- New files: acceptance report (`docs/reports/plans/apps-repo-brief-plan3-acceptance.md`), ~6 new tests (D2.2, D2.3, D2.4, D3.2)
- Edit: C0 FEC authoritative wiring (`repo_brief_final_contract.py`), C0→PA handoff
- Pattern source: `apps-repo-brief-plan3-zero-loss-overwrite` §20.2 + §21 template
- Non-goals: No new waves, no implementation in this document
- Success: YES verdict on all 15 §20.2 acceptance gates; final acceptance report complete

**PLAN_CREATED:** `.windsurf/plans/apps-repo-brief-plan3-deferred-scope-b9e4c1.md`
