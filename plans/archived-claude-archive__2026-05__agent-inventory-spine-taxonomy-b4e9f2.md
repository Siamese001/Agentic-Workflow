---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\agent-inventory-spine-taxonomy-b4e9f2.md'
original_relative_path: '_archive\\2026-05\\agent-inventory-spine-taxonomy-b4e9f2.md'
source_sha256: 24aa9c0551f7f07c8efadf336222033f4d8517f3a808056041d7659353e9a834
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: agent-inventory-spine-taxonomy-b4e9f2
plan_type: governance
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# Agent Inventory — Product Spine Truth & Taxonomy Cleanup

**North star:** Align documentation, taxonomy, and proof contracts with the **function-based canonical product spine**. No `*Agent` class may be described as product-spine-invoked without artifact proof. Inventory/taxonomy work is a **separate track** from spine truth — not “wire all agents OR bulk NOT_AGENT.”

**Evidence base (PARTIAL):**
- [Runtime assessment MD](../docs/reports/agentic_core_agent_inventory_runtime_assessment.md)
- [Runtime assessment JSON](../docs/reports/agentic_core_agent_inventory_runtime_assessment.json)
- [Generator](../docs/reports/agent_inventory/_generate_runtime_assessment.py)
- Spine harness artifacts: [\_spine_proof_run/](../artifacts/reports/agent_inventory/_spine_proof_run/)

**Architecture conclusion (frozen for this plan):** The canonical E2E product spine is a **governed functional pipeline**, not a class-agent execution graph. `AGENT_TAXONOMY_MAP` is metadata — not the product runtime graph.

> **plan_id discipline:** `agent-inventory-spine-taxonomy-b4e9f2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
PLAN_HARDENING: applied_2026-05-25 assessment_hardening_v2_taxonomy_axes
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-25
PLAN_COMPLETE: YES
NOTION_STATUS: Completed
EXECUTION_APPROVED: false
FOLLOW_UP_PLAN: agent-inventory-deferred-followup-c2a8f1
DEFERRED_REGISTER: docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md
CLOSEOUT_RECEIPT: docs/reports/cursor/agent_inventory_spine_taxonomy_closeout_receipt.md

NOTION_PAGE_ID: 36b27693-f55c-81d3-b7a7-d9b54d461f83
NOTION_PLAN_URL: https://www.notion.so/agent-inventory-spine-taxonomy-b4e9f2-36b27693f55c81d3b7a7d9b54d461f83

PLAN_CREATED: slug=agent-inventory-spine-taxonomy-b4e9f2 path=.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md status=Not Started notion_page=36b27693-f55c-81d3-b7a7-d9b54d461f83

---

## Context (SCQA)

- **Situation** — AST scan found **118** `*Agent` candidates in `agentic_core`; **31** registered in `AGENT_TAXONOMY_MAP`; mock-L2 spine harness proves **stage/function** flow (`U0_INTAKE` … `L6_RUNTIME_EXHAUST`) with `producer_component` on `integrated_single_action_spine_run`.
- **Complication** — **0** candidates are artifact-proven as product-spine-invoked; taxonomy and class names are routinely misread as runtime invocation; **56** heuristic true-agents lack taxonomy rows; L5/healing classes must not be collapsed to `NOT_AGENT` by default.
- **Question** — How do we make spine truth and agent inventory **legible and enforceable** without falsely wiring every `*Agent` into the product path?
- **Answer** — Two parallel decisions: (1) lock product-spine truth to **functions + acceptance invariant**; (2) extend taxonomy as an **inventory/control surface** with **four orthogonal axes** — registration must never imply product-spine participation.

---

## Taxonomy axes (orthogonal — W1 schema)

Every `AgentTaxonomyEntry` (or equivalent row) MUST carry **four separate fields**. None may be inferred from another.

| Field | Allowed values | Meaning |
|-------|----------------|---------|
| `agenthood_status` | `TRUE_AGENT` · `NOT_AGENT` · `WRAPPER_ONLY` · `SHIM_OR_DEAD_LEGACY` | Reasoning + autonomy classification (heuristic at registration time) |
| `inventory_role` | `PRODUCT_SPINE_FUNCTION` · `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` · `GOVERNANCE_CERTIFIER_OR_VALIDATOR` · `HEALER_OR_DEV_AGENT` · `UTILITY_OR_WRAPPER` · `SHIM_OR_DEAD_LEGACY` | Governance/inventory placement — **not** runtime routing |
| `product_spine_invocation_status` | `ARTIFACT_PROVEN` · `NOT_ARTIFACT_PROVEN` | Whether a **runtime artifact** proves selection/invocation on the canonical product spine |
| `runtime_proof_class` | `LIVE_RUNTIME_PROOF` · `REPLAY_RUNTIME_PROOF` · `TEST_RUNTIME_PROOF` · `MOCK_ONLY_PROOF` · `NONE` | Quality tier of the cited proof (if any) |

**W1 registration defaults (mandatory for all new rows, including the ~56 gap fill):**

| Field | Default at registration | Rationale |
|-------|-------------------------|-----------|
| `product_spine_invocation_status` | `NOT_ARTIFACT_PROVEN` | No row added in W1 may claim spine invocation |
| `runtime_proof_class` | `NONE` | Registration is inventory metadata, not runtime proof |
| `inventory_role` | Per assessment (never `PRODUCT_SPINE_FUNCTION` for `*Agent` classes) | Functions live on spine table, not `*Agent` AST rows |
| `agenthood_status` | Per assessment heuristic | Independent of spine invocation |

`PRODUCT_SPINE_FUNCTION` is reserved for **named spine functions** (e.g. `run_integrated_single_action_spine`) if modeled in taxonomy at all — not for bulk `*Agent` class registration.

---

## Two decisions (non-equivalent)

### Decision 1 — Product spine truth

| Invariant | Target |
|-----------|--------|
| E2E invoked `*Agent` class count | **0** until artifact proves otherwise |
| Taxonomy registration ⇒ invocation | **Forbidden claim** |
| Class name / inheritance ⇒ invocation | **Forbidden claim** |
| HOW / spine proof scope | Stage/function only |

Canonical spine functions (not classes):

| Function | Module |
|----------|--------|
| `run_integrated_single_action_spine` | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` |
| `run_request_intake` | `agentic_core/L0_routing/intake/pipeline.py` |
| `validated_request_to_plan_contract` | `agentic_core/L1_cognition/bridges/u0_to_l1_plan.py` |
| `check_route_gates` | `agentic_core/L0_routing/reasoning/route_gates.py` |
| `resolve_l2_recipe` | `agentic_core/runtime/l2_recipe_resolver.py` |
| `ExitEvalPipeline.run` | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` |

### Decision 2 — Inventory / taxonomy cleanup

Separate four axes on every candidate (maps 1:1 to taxonomy fields above):

1. `agenthood_status` — agent vs wrapper vs shim
2. Taxonomy registration — **inventory/control only**
3. `product_spine_invocation_status` — artifact-only; default `NOT_ARTIFACT_PROVEN`
4. `runtime_proof_class` — proof tier; default `NONE` at registration

**Inventory roles** (from assessment):

| Role | Count (2026-05-25) | Typical action |
|------|-------------------:|----------------|
| `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | 74 | Register with `inventory_role` only; `product_spine_invocation_status=NOT_ARTIFACT_PROVEN` |
| `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | 20 | Same; never imply route/X3/UWG ownership via registration |
| `HEALER_OR_DEV_AGENT` | 6 | Same; document dev/healing path separately |
| `UTILITY_OR_WRAPPER` | 17 | `agenthood_status=WRAPPER_ONLY` or `NOT_AGENT` as appropriate |
| `SHIM_OR_DEAD_LEGACY` | 1 | W2 archive (`RootCustomsAgent`) |

**Explicitly forbidden:**

- Treating Decision 2 as “wire agent identity into HOW **or** reclassify all L5 as NOT_AGENT/archive.”
- **“Register 56 off-spine gaps” implying product-spine participation** — registration fills inventory rows only; it does **not** add classes to the runtime execution graph.

---

## Acceptance invariants

### A1 — Product-spine invoked (runtime claim)

No `agentic_core` class may be described as **product-spine invoked** unless an E2E artifact contains at least one of:

- class name
- module path
- registry selected agent id
- execution profile id bound to that class
- OTEL span naming that class/module
- receipt producer/consumer/executor naming that class/module

**Baseline:** 0/118 satisfy today. W1 must not advance this count without a cited artifact path on the entry.

### A2 — Taxonomy registration (inventory claim)

**No taxonomy registration may be interpreted as E2E invocation.**

- Adding or updating an `AGENT_TAXONOMY_MAP` row is **inventory/control metadata only**.
- Forbidden inference: taxonomy key present → product-spine participant; import fan-in → invoked; static call path in spine source → invoked.
- Any future `product_spine_invocation_status=ARTIFACT_PROVEN` **must** cite `spine_proof_ref` (or equivalent) pointing to a runtime artifact that contains **class name, module path, registry selected agent id, execution profile id, OTEL span naming, or receipt producer/consumer/executor** for that class — not merely the taxonomy key, import graph, or grep hit.
- W1 bulk registration MUST set `product_spine_invocation_status=NOT_ARTIFACT_PROVEN` and `runtime_proof_class=NONE` unless an existing artifact already satisfies A1 (baseline: none).

---

## NON_CLAIMS (plan scope boundary)

- This plan does **not** assert `*Agent` classes are unused everywhere.
- Assessment proves **not artifact-proven** on the canonical spine run inspected.
- Mock L2 harness proves **path shape** only — not live product model/tool execution.
- [`agentic_core/L6_system_learning/snapshot/__init__.py`](../agentic_core/L6_system_learning/snapshot/__init__.py) shim is **report-generation only** — not architecture proof.

---

## Out Of Scope

- Wiring all 118 `*Agent` classes into `run_integrated_single_action_spine`
- Bulk `NOT_AGENT` / delete-by-default for L5/healing
- `apps_*` recipe or L2 step changes (L2 remains `resolve_l2_recipe` → app callables)
- Live production E2E with real models (W3 only — **no backfill from mock harness**)
- Using mock `_spine_proof_run/` artifacts to set `ARTIFACT_PROVEN` or upgrade `runtime_proof_class` in W0–W2
- Renaming every `*Agent` file in one wave (separate burndown if desired)

---

## Status Tables

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W0 | W0.0–W0.2 | Canon docs + acceptance invariant ADR | ~40K | Assessment accepted as PARTIAL baseline | ✅ DONE | ADR-088 + LAYER.md + rule + [W0 receipt](../docs/reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md) |
| W1 | W1.0–W1.2 | Four-axis taxonomy + inventory-only gap fill | ~80K | Registration ≠ spine participation | ✅ DONE | 118 agentic_core rows; 0 ARTIFACT_PROVEN; [W1 receipt](../docs/reports/cursor/agent_inventory_spine_taxonomy_w1_receipt.md) |
| W2 | W2.0–W2.2 | Misplacement + shim archive + L6 harness doc | ~40K | L6 snapshot preserved report-only | ✅ DONE | [W2 receipt](../docs/reports/cursor/agent_inventory_spine_taxonomy_w2_receipt.md) |
| W3 | W3.0 | Live spine proof (optional) | ~60K | Provider keys + apps_rg lane available | 🔲 DEFERRED | Real L2 run; class identity fields if approved |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W0.0 | Spine truth ADR | `docs/architecture/adr/ADR-088-*.md`, `agentic_core/runtime/LAYER.md` | Taxonomy misread as runtime graph | ~15K | ✅ DONE |
| W0.1 | Acceptance invariant in docs | `.cursor/rules/`, assessment cross-link | False PASS on class invocation | ~12K | ✅ DONE |
| W0.2 | W0 receipt | `docs/reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md` | PARTIAL baseline tracked | ~8K | ✅ DONE |
| W1.0 | Taxonomy schema: four orthogonal axes | `agent_taxonomy_spine_axes.py`, registry merge | Registration misread as invocation | ~25K | ✅ DONE |
| W1.1 | Inventory-only gap fill (118 rows) | `data/agentic_core_w1_spine_axes.json` | NOT_ARTIFACT_PROVEN / NONE defaults | ~40K | ✅ DONE |
| W1.2 | CI: A1 + A2 invariants | `check_agent_taxonomy_spine_invariants.py`, pytest | Taxonomy key ≠ invoked | ~15K | ✅ DONE |
| W2.0 | Archive `RootCustomsAgent` shim | `archives/agents/2026-05-25/` | Orphan body re-defined class at import | ~10K | ✅ DONE |
| W2.1 | Layer misplacement ledger | `docs/reports/cursor/` | SemanticGatekeeper, Bootstrap, etc. | ~8K | ✅ DONE |
| W2.2 | L6 snapshot shim (preserve, report-only) | `L6_system_learning/snapshot/__init__.py` | Must not be arch evidence | ~5K | ✅ DONE |
| W3.0 | Live E2E class-identity emit (optional) | spine proof bundle, OTEL | Mock L2 only today | ~60K | 🔲 DEFERRED |

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Canon + invariant docs | ✅ DONE | — | ADR-088, LAYER, rule, receipt |
| W1 | Taxonomy inventory roles | ✅ DONE | 13 pytest | 118-row inventory merge |
| W2 | Shim + misplacement | ✅ DONE | 12 pytest | orphan archived, ledger |
| W3 | Live proof (optional) | 🔲 DEFERRED | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.0 | Spine truth ADR | ✅ DONE |
| W0.1 | Acceptance invariant docs | ✅ DONE |
| W0.2 | W0 receipt | ✅ DONE |
| W1.0 | Taxonomy schema extension | ✅ DONE |
| W1.1 | Off-spine registration pass | ✅ DONE |
| W1.2 | CI taxonomy/spine claim gate | ✅ DONE |
| W2.0 | RootCustomsAgent archive | ✅ DONE |
| W2.1 | Misplacement ledger | ✅ DONE |
| W2.2 | L6 snapshot shim documented (preserve) | ✅ DONE |
| W3.0 | Live E2E proof | 🔲 DEFERRED |

---

## Wave 0 — Canon & acceptance invariant

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

WAVE_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=0 note="+ADR-088, invariants ref, LAYER.md, rule, W0 receipt, assessment link"

**Phases:**
- **W0.0** — Publish ADR (mandatory statements below) | ~15K | PHASE_STATUS: TODO
- **W0.1** — Propagate A1 + A2 invariants to docs / rule cross-ref | ~12K | PHASE_STATUS: TODO
- **W0.2** — Emit `docs/reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md` | ~8K | PHASE_STATUS: TODO

**W0.0 ADR mandatory statements (verbatim intent):**

1. The **current canonical product spine is function/stage based** (`run_integrated_single_action_spine`, intake, route gates, L1 bridge, L2 recipe resolver, Exit pipeline).
2. The **taxonomy registry is an inventory/control surface**, not the runtime execution graph.
3. Runtime graph claims require a **runtime receipt** that proves selection/invocation (A1 fields) — not taxonomy presence, import, or static call path.
4. Registration and `product_spine_invocation_status` are **orthogonal** (A2).

**Acceptance:**
- ADR states Decision 1 and Decision 2 as non-equivalent
- ADR includes the four mandatory statements above
- NON_CLAIMS copied verbatim into ADR or linked assessment section
- No new claim that any `*Agent` is product-spine-invoked

---

## Wave 1 — Four-axis taxonomy (inventory-only registration)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

WAVE_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=1 note="+118 agentic_core inventory rows, 4 axes, 0 ARTIFACT_PROVEN, 13 pytest PASS"

**Phases:**
- **W1.0** — Extend `AgentTaxonomyEntry` with `agenthood_status`, `inventory_role`, `product_spine_invocation_status`, `runtime_proof_class` (+ optional `spine_proof_ref` when proven) | ~25K | PHASE_STATUS: TODO
- **W1.1** — Inventory-only gap fill (~56 rows): set `product_spine_invocation_status=NOT_ARTIFACT_PROVEN`, `runtime_proof_class=NONE`; map `inventory_role` from assessment — **no** `PRODUCT_SPINE_FUNCTION` on `*Agent` classes | ~40K | PHASE_STATUS: TODO
- **W1.2** — CI gate: enforce A1 (runtime claims) + A2 (registration ≠ invocation); reject `ARTIFACT_PROVEN` without `spine_proof_ref` | ~15K | PHASE_STATUS: TODO

**Acceptance:**
- Every new/updated row has all four axes populated; no default inference between axes
- `AGENT_TAXONOMY_MAP` count ≥ 87 for heuristic true-agents (or explicit exclusion list with reason)
- **Zero** rows with `product_spine_invocation_status=ARTIFACT_PROVEN` after W1 (baseline unchanged until W3)
- **Zero** rows with `runtime_proof_class=MOCK_ONLY_PROOF` used to satisfy A1 in W0–W2
- CI fails if docs/tests equate taxonomy registration with E2E invocation
- `python -m pytest tests/agentic_core/L2_execution/test_agent_taxonomy_registry.py -q` PASS (create if missing)

**Author-Gate:** Required before W1.0 schema edit (`architecture_choice` + `refactor_scope`).

**Forbidden in W1:** Copying mock harness artifacts (`artifacts/reports/agent_inventory/_spine_proof_run/`) into `spine_proof_ref` to flip invocation status.

---

## Wave 2 — Shim archive & misplacement ledger

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

WAVE_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=2 note="+orphan body archived, thin shim 163 lines, misplacement ledger, L6 harness preserved"

**Phases:**
- **W2.0** — Archive/delete `RootCustomsAgent` shim; callers → `root_customs_util` | ~10K | PHASE_STATUS: TODO
- **W2.1** — Document static misplacements (`SemanticGatekeeperAgent`, `BootstrapAgent`, `PreCommitSovereignAgent`) — move deferred | ~8K | PHASE_STATUS: TODO
- **W2.2** — Document L6 snapshot shim as **report-generation-only** (preserve; do not delete as “dead legacy”) | ~5K | PHASE_STATUS: TODO

**Acceptance:**
- No import of `RootCustomsAgent` in `agentic_core` spine chain modules
- Misplacement ledger linked from assessment MD
- [`agentic_core/L6_system_learning/snapshot/__init__.py`](../agentic_core/L6_system_learning/snapshot/__init__.py) remains with docstring: **harness/report generation only — not architecture evidence**; W2 must **not** treat it as spine proof or delete it in the same bucket as `RootCustomsAgent`

---

## Wave 3 — Live spine proof

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: EXECUTED
CHECKPOINT: D

**Phases:**
- **W3.0** — Run `run_integrated_single_action_spine` without mock L2; evaluate whether to add optional `invoked_class` / `executor_module` fields to HOW trace | ~60K | PHASE_STATUS: DONE

**Closeout (2026-05-25):** Live run via [run_w3_live_spine_proof.py](../tools/governance/run_w3_live_spine_proof.py) → [w3_live_spine_proof_report.json](../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json). `a1_invoked_agent_classes=0`; Decision 1 **defer** → [agent_inventory_w3_class_identity_evaluation.md](../docs/reports/cursor/agent_inventory_w3_class_identity_evaluation.md). Receipt: [agent_inventory_spine_taxonomy_w3_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w3_receipt.md) (**PARTIAL** — L2 modular lane fault, not mock).

**Unblock criteria:**
- User approves emitting class identity on spine (Decision 1 scope expansion)
- Live `apps_rg` lane green with real provider

**W3 hardening (non-negotiable):**

- **Do not backfill W3 claims from the mock harness.** Artifacts under `_spine_proof_run/` (`_test_mode=True`, mock L2) may inform W0–W2 path-shape documentation only.
- W3 may set `product_spine_invocation_status=ARTIFACT_PROVEN` only after a **live** run with `runtime_proof_class` ∈ `{LIVE_RUNTIME_PROOF, REPLAY_RUNTIME_PROOF}` and a valid `spine_proof_ref`.
- Mock-only runs remain `MOCK_ONLY_PROOF` and **must not** satisfy A1 or flip taxonomy invocation status.

---

## Gap Register

**GAP-1: Taxonomy/runtime graph confusion**
- 31 registered names imply runtime ownership; assessment shows 0 artifact-proven spine invocation
- Fix: W0 ADR + W1 `inventory_role`

**GAP-2: 56 unregistered true-agents**
- Heuristic agents lack taxonomy metadata for governance routing
- Fix: W1.1 inventory-only registration (four axes; `NOT_ARTIFACT_PROVEN` / `NONE` defaults)

**GAP-3: Mock-only spine proof**
- Harness proves functions; mock `_spine_proof_run/` remains path-shape only
- Fix: W3 live run (`_w3_live_spine_proof_run/`) — 0 `*Agent` in artifacts; full green `python -m apps_rg` still separate gate

**GAP-4: Layer misplacements**
- Safety/routing agents in wrong package paths
- Fix: W2.1 ledger; physical move = future plan

---

## Definition of Done

DoD-1: Spine truth ADR published and linked from assessment
- Evidence: [ADR-088-product-spine-function-truth.md](../docs/architecture/adr/ADR-088-product-spine-function-truth.md); linked from [assessment MD](../docs/reports/agentic_core_agent_inventory_runtime_assessment.md)
- Status: DONE (W0)

DoD-2: Taxonomy carries all four axes on every registered `agentic_core` agent
- Evidence: registry introspection shows `agenthood_status`, `inventory_role`, `product_spine_invocation_status`, `runtime_proof_class` on each entry; W1 ends with zero `ARTIFACT_PROVEN`
- Status: DONE (W1)

DoD-3: CI enforces A1 + A2 (registration ≠ invocation; `ARTIFACT_PROVEN` requires `spine_proof_ref`)
- Evidence: `pytest tests/governance/test_agent_spine_invocation_claims.py -q` → 0 failed (or equivalent gate)
- Status: DONE (W1)

DoD-4: Assessment regenerated; E2E invoked class count still 0 unless W3 executed
- Evidence: `python docs/reports/agent_inventory/_generate_runtime_assessment.py` exit 0; JSON `invoked_e2e_yes` documented; W3 live report linked
- Status: DONE (W3 — `invoked_e2e_yes` remains 0)

DoD-5: W0 receipt + Notion plan Status reflects wave progress
- Evidence: [agent_inventory_spine_taxonomy_w0_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md); Notion Plans row updated manually if needed
- Status: DONE (W0 receipt); Notion sync optional

### Verification vs deferral

| Item | Verify in W0–W2 | Deferred |
|------|-----------------|----------|
| Function-based spine canon | ✅ | — |
| Inventory role taxonomy | ✅ | — |
| Live L2/model spine run | W3 live runner (PARTIAL — lane fault) | Full green `python -m apps_rg` |
| Optional class identity in HOW | W3 eval: defer | Future plan if approved |
| Physical layer moves | — | Future plan |

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=3 gap="Emit class identity on canonical spine" impact="high — changes proof contract"
AUTHORIZATION_DECISION: plan=agent-inventory-spine-taxonomy-b4e9f2 decision=DEFERRED authorized_by=user decisive_reason="Assessment explicitly separates spine truth from taxonomy; class identity emit is optional future work"
```

---

## Related artifacts

| Artifact | Path |
|----------|------|
| Runtime assessment | [agentic_core_agent_inventory_runtime_assessment.md](../docs/reports/agentic_core_agent_inventory_runtime_assessment.md) |
| JSON export | [agentic_core_agent_inventory_runtime_assessment.json](../docs/reports/agentic_core_agent_inventory_runtime_assessment.json) |
| L6 snapshot shim (harness only) | [snapshot/__init__.py](../agentic_core/L6_system_learning/snapshot/__init__.py) |

---

## Plan closeout (2026-05-25)

**Status:** Completed on disk and Notion. All in-charter waves W0–W3 done.

**Transferred deferred scope** → [agent-inventory-deferred-followup-c2a8f1](agent-inventory-deferred-followup-c2a8f1.md) · register [agent_inventory_deferred_scope_register_20260525.md](../docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md)

| Deferred ID | Summary |
|-------------|---------|
| DS-1 | Full green integrated R4 (`python -m apps_rg` / `PYTEST_APPS_RG_INTEGRATED_LIVE`) |
| DS-2 | Optional class identity on HOW (product approval) |
| DS-3 | Physical misplacement moves |
| DS-4 | RootCustoms thin shim removal |
| DS-5 | A2 — no `ARTIFACT_PROVEN` without live/replay proof |

**Closeout receipt:** [agent_inventory_spine_taxonomy_closeout_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_closeout_receipt.md)

```
SCOPE_TRANSFER: from=agent-inventory-spine-taxonomy-b4e9f2 to=agent-inventory-deferred-followup-c2a8f1 items=DS-1,DS-2,DS-3,DS-4,DS-5
PLAN_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 note="W0-W3 DONE; deferred scope → c2a8f1; Notion Completed"
```

## Marker Quick Reference

```
WAVE_START: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=0
WAVE_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 wave=3 note="live proof PARTIAL; 0 ARTIFACT_PROVEN agents"
PLAN_COMPLETE: plan=agent-inventory-spine-taxonomy-b4e9f2 note="Closed; follow-up agent-inventory-deferred-followup-c2a8f1"
```
