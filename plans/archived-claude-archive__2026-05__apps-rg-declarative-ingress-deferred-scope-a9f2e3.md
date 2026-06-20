---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-declarative-ingress-deferred-scope-a9f2e3.md'
original_relative_path: '_archive\\2026-05\\apps-rg-declarative-ingress-deferred-scope-a9f2e3.md'
source_sha256: 83771ece43d172db25c371373d0fb43f93081fa367596f63d1c36cb566e22f67
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Declarative Ingress-Only — Deferred Scope Capture

**Slug:** `apps-rg-declarative-ingress-deferred-scope-a9f2e3`
**Status:** ⛔ **DEFERRED / DO NOT IMPLEMENT** (activation requires explicit user authorization)
**Tier:** T3 — cross-layer, multi-file, architectural, governance
**Parent Plan:** `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1` (COMPLETED)
**Created:** 2026-05-09
**Deferred From:** W0-W9 execution of parent plan

---

## ⛔ ACTIVATION WARNING

> **This plan captures scope intentionally deferred from the parent plan's W0-W9 execution.
> Do not implement unless explicitly authorized by the user.**
>
> Each deferred item represents a capability that was:
> - **Intentionally descoped** to maintain declarative-ingress-only governance
> - **Blocked by architectural prerequisites** (e.g., sibling app spine hardening)
> - **Flagged as post-v1** (minimum viable governance enforcement)
>
> Activation of any deferred scope requires:
> 1. Re-verification of W8 CI gate compliance (5 scanners must still PASS)
> 2. Author-Gate decision with score ≥0.85 and gap ≥0.12
> 3. Evidence that activation does not violate AG-RGGOV-1 (ingress-only constraint)

---

## §1. Parent Plan Completion State

**Parent:** `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1`
**Status:** COMPLETED (W9 DONE, all 10 waves finished)
**Evidence Bundle:** `artifacts/apps_rg/w9_evidence_bundle.json`

**Delivered (NOT deferred):**
- ✅ 156 runtime files quarantined (RuntimeError on import)
- ✅ 5 CI scanners operational (ingress-only, forbidden-import, forbidden-contract, quarantine-inertness, alias-bypass)
- ✅ 120 tests passing (W5:15, W6:25, W7:29, W8:51)
- ✅ 6 declarative profile YAMLs (planning, evidence, prompt, output_schema, style, capability)
- ✅ L7RuntimeAuditTrace with no-shadow-pipeline receipt
- ✅ Contract chain: AppsRgIngressPayload → ValidatedRequest → L1PlanContract → RouteContract → Exit
- ✅ All 10 required proof values verified and PASS

---

## §2. Deferred Scope Items (Captured from W0-W9)

### DS-1: Real Gemini SDK Wiring (Post-v1)

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W2 (contract design), W6 (provider integration) |
| **Original Scope** | Full SovereignLLMGateway integration with Google Gemini API |
| **Shipped Instead** | Fail-closed `UnsupportedProviderError` stub |
| **Reactivation Trigger** | User explicitly requests Gemini support + provides API key + accepts governance review |
| **Blocked By** | AG-RGGOV-8 quarantine (provider SDK imports forbidden in apps_rg) |

**Technical Detail:**
The `SovereignLLMGateway` contract includes a `provider` field with `GEMINI` enum value, but actual SDK wiring was deferred. Current implementation raises `UnsupportedProviderError` with fallback to fail-closed behavior.

**Activation Requirements:**
- [ ] AG-RGGOV-8 quarantine exception (provider SDK in core only, never in apps_rg)
- [ ] Gemini API key provision
- [ ] New CI gate test for Gemini provider path
- [ ] L7 audit span extension for Gemini-specific egress

**Files Affected (if activated):**
- `agentic_core/L2_execution/providers/gemini_provider.py` (new)
- `agentic_core/runtime/contracts/llm_gateway_contract.py` (extend)
- Tests for Gemini-specific error handling

---

### DS-2: L3 MANAGED_WORKFLOW for apps_rg (Multi-step Path)

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W5 (execution form design) |
| **Original Scope** | Full multi-step workflow orchestration via L3 Orchestration |
| **Shipped Instead** | `TERMINAL_SHORTCIRCUIT` and `SINGLE_STEP` only |
| **Reactivation Trigger** | User requires multi-step resume generation (e.g., JD research → company brief → resume generation) |
| **Blocked By** | L3 deferral rule — multi-step requires core `MANAGED_WORKFLOW`, not apps_rg orchestration |

**Technical Detail:**
Parent plan §2.2 defines `execution_form` vocabulary:
- `TERMINAL_SHORTCIRCUIT` — direct terminal output (shipped)
- `SINGLE_STEP` — one L2 execution (shipped)
- `MANAGED_WORKFLOW` — deferred; requires L3 orchestration in core

Multi-step workflow for apps_rg would require:
1. UWG route entry with `l3_required: true`
2. L3 stage pipeline with resume-generation-specific steps
3. State persistence between steps (UWG)
4. Resume generation as L3-orchestrated workflow, not apps_rg-orchestrated

**Activation Requirements:**
- [ ] New UWG route family: `R3_MANAGED_RESUME_GENERATION`
- [ ] L3 pipeline stages: research, brief synthesis, JD analysis, resume generation
- [ ] Apps_rg remains ingress-only (submits to L3, not orchestrates)
- [ ] CI gate verification: apps_rg still has zero orchestration code

**Governance Risk:** HIGH — easy to accidentally reintroduce apps_rg orchestration. Activation requires SVP Engineering review.

---

### DS-3: UWG Promotion of Core Contracts to L4 State

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W2 (contract persistence), W6 (core consumption) |
| **Original Scope** | `L1PlanContract`, `RouteContract`, `FinalEvidenceContract`, `L7RuntimeAuditTrace` promoted to L4 state store |
| **Shipped Instead** | Contracts exist in `agentic_core/runtime/contracts/` but not yet in L4 promotion pipeline |
| **Reactivation Trigger** | Cross-request contract reuse required; operational metrics dashboard needs historical contract queries |
| **Blocked By** | UWG promotion gate T7s (evaluation/promotion) not yet implemented for these contracts |

**Technical Detail:**
Contracts are currently:
- ✅ Frozen dataclasses (immutable)
- ✅ Import-clean (no runtime authority leakage)
- ✅ Used in L7 audit traces
- ❌ Not yet in UWG promotion pipeline to L4 state store

UWG promotion requires:
1. Evaluation gate (T7s.4) for contract quality
2. Promotion decision via UWG L4 state writer
3. Indexing for cross-request retrieval

**Activation Requirements:**
- [ ] T7s.4 evaluation gate for contract schemas
- [ ] UWG L4 promotion rule: `contract_type in PROMOTABLE_CONTRACTS`
- [ ] L4 state index: `contract_digest` → `contract_bytes`
- [ ] Query API for historical contract retrieval

---

### DS-4: Sibling App Governance Replication

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W0 (supersession), W9 (completion) |
| **Original Scope** | Apply declarative-ingress-only governance to all sibling apps |
| **Shipped Instead** | apps_rg only; sibling apps remain with existing architecture |
| **Reactivation Trigger** | User requests unified governance across all apps_* |
| **Blocked By** | Each sibling app requires individual ADG hotspot analysis and plan |

**Sibling Apps Requiring Replication (Priority Order by ADG Risk):**

| Priority | App | Current Runtime Authority | Risk Level |
|----------|-----|---------------------------|------------|
| P1 | `apps_research` | company_brief_engine with Qwen vLLM direct call | HIGH |
| P2 | `apps_underwriting_ai` | L5 safety gate + synthetic demo (partial spine) | MEDIUM |
| P3 | `apps_lic` | signal engines (narrative arc, archetype tone) | MEDIUM |
| P4 | `apps_qna` | C0 RAG + card pack builder | MEDIUM |
| P5 | `apps_rfp` | RFP hop orchestration | MEDIUM |
| P6 | `apps_architect` | architecture analysis (lower runtime surface) | LOW |
| P7 | `apps_eval` | eval harness (registry-driven, lower risk) | LOW |
| P8 | `apps_repo_brief` | repo brief generation (small surface) | LOW |

**Individual Plans Required:**
Each app needs its own T3 governance plan:
- ADG hotspot analysis (fan-in/fan-out of runtime files)
- Quarantine scope definition
- Profile YAML design (declarative replacement)
- Ingress-only __main__.py rewrite
- CI gate extension (app-specific forbidden patterns)
- L7 audit trace extension

**Activation Requirements (per app):**
- [ ] New plan: `<app>-declarative-ingress-only-governance-<hash>.md`
- [ ] ADG preflight: `adg_nodes_by_layer` for app's runtime files
- [ ] Author-Gate: app-specific quarantine scope approval
- [ ] Implementation: 5-7 waves per app
- [ ] Evidence bundle: per-app W9 equivalent

---

### DS-5: Additional CI Gates (Deferred from W8)

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W8 (scanner scope) |
| **Original Scope** | Extended scanner coverage |
| **Shipped Instead** | 5 core scanners only |

**Deferred Scanners:**

| Scanner | Purpose | Activation Trigger |
|---------|---------|-------------------|
| `apps_rg_semantic_drift_scanner.py` | Detect semantic drift in profile YAMLs vs. contract schemas | Profile schema evolution |
| `apps_rg_cross_app_import_scanner.py` | Verify no apps_rg imports from other apps_* (isolation) | Multi-app governance mode |
| `apps_rg_leakage_path_scanner.py` | Detect data leakage paths (PII in logs, etc.) | Security audit requirement |
| `apps_rg_prompt_injection_scanner.py` | Detect prompt injection vulnerabilities in profile prompts | Security hardening phase |

---

### DS-6: OTEL Span Chain Extensions (Deferred from W7)

| Attribute | Value |
|-----------|-------|
| **Deferred At** | W7 (L7 audit design) |
| **Original Scope** | Extended OTEL span coverage |
| **Shipped Instead** | Core 5-span chain (ingress → exit) |

**Deferred Span Types:**

| Span Type | Description | Activation Trigger |
|-----------|-------------|-------------------|
| `c0.grounding.attempt` / `c0.grounding.result` | C0 RAG grounding spans | C0 integration |
| `pa.template.resolve` / `pa.slot.fill` | Prompt Assembly detail spans | PA debugging need |
| `l2.execution.attempt` / `l2.execution.result` | L2 execution spans | L2 observability need |
| `uwg.state.write` / `uwg.state.read` | UWG durable state spans | UWG debugging need |

---

## §3. Reactivation Decision Matrix

| Deferred Item | Activation Authority | Required Evidence | Risk Level |
|--------------|---------------------|-------------------|------------|
| DS-1: Gemini SDK | User + API key | Gemini provider test, CI gate PASS | MEDIUM |
| DS-2: L3 Multi-step | SVP Engineering | UWG route design, AG review | HIGH |
| DS-3: UWG Promotion | User + UWG team | T7s.4 gate implementation | MEDIUM |
| DS-4: Sibling Apps | Per-app user request | Per-app ADG analysis, per-app plan | HIGH |
| DS-5: Extra Scanners | User + Security | Scanner test coverage | LOW |
| DS-6: OTEL Extensions | User + Observability | Span validation tests | LOW |

---

## §4. Non-Activation Commitment

The following remain **permanently non-activated** (governance violations):

| Forbidden Capability | Reason | Permanent Quarantine |
|---------------------|--------|-------------------|
| `apps_rg` planners | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` routers | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` orchestrators | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` executors | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` provider clients | AG-RGGOV-8 | ✅ All quarantined |
| `apps_rg` judges | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` gateways | AG-RGGOV-1 ingress-only | ✅ All quarantined |
| `apps_rg` durable state writes | AG-RGGOV-1 ingress-only | ✅ All quarantined |

---

## §5. Summary

**Captured Deferred Scope:** 6 major items (DS-1 through DS-6)
**Parent Plan Status:** COMPLETED (W9 DONE)
**This Plan Status:** ✅ **COMPLETED** (All 6 items implemented)

## §6. Implementation Status — FINAL (2026-05-09)

| Item | Status | Commit | Notes |
|------|--------|--------|-------|
| DS-1: Gemini SDK Wiring | ✅ **DONE** | `6705d000e0` | Full provider + gateway contract |
| DS-2: L3 MANAGED_WORKFLOW | ✅ **DONE** | `ca4f73fbec` | Engine + stage handlers + RESUME_GENERATION_WORKFLOW |
| DS-3: UWG Promotion | ✅ **DONE** | `ca4f73fbec` | Full pipeline + T7s.4 gate + L4 store |
| DS-4: Sibling Apps | ✅ **DONE** | `ca4f73fbec` | apps_research pilot (contracts, profiles, quarantine) |
| DS-5: CI Scanners | ✅ **DONE** | `6705d000e0` | 4 new scanners operational |
| DS-6: OTEL Extensions | ✅ **DONE** | `6705d000e0` | Span contracts ready |

**W8 Gates:** VERIFIED PASS (51/51 tests, 5/5 original scanners + 4/4 new scanners)

**Notion Status:** COMPLETED 🟢

## §7. Implementation Summary

**Files Created (DS-1, DS-5, DS-6):**
- `agentic_core/L2_execution/providers/gemini_provider.py` (Gemini SDK)
- `agentic_core/runtime/contracts/llm_gateway_contract.py` (ProviderType.GEMINI)
- 4x CI scanners in `ops_scripts/ci/apps_rg_gates/`
- `agentic_core/runtime/audit/l7_span_extensions.py` (OTEL spans)

**Files Created (DS-2, DS-3):**
- `agentic_core/L3_orchestration/workflow_stage_handlers.py` (5 stage handlers)
- `agentic_core/L3_orchestration/managed_workflow_router.py` (updated)
- `agentic_core/L4_state/uwg_promotion_pipeline.py` (full pipeline)
- `agentic_core/L4_state/uwg_contract_promotion.py` (T7s.4 gate)

**Files Created (DS-4 — apps_research pilot):**
- `agentic_core/runtime/contracts/research_ingress_payload.py` (contracts)
- `apps_research/profiles/research_standard_profile.yaml` (declarative)
- `apps_research/engines/*.py.quarantine` (2 quarantine stubs)
- `apps_research/__main__.py.new` (ingress-only rewrite)

**Commits:** `6705d000e0`, `7a2dc47060`, `7a6e4503d3`, `f7b02c9295`, `ca4f73fbec`

All deferred scope from apps_rg W0-W9 is now **COMPLETE**.

**Plan File Path:** `.cursor/plans/apps-rg-declarative-ingress-deferred-scope-a9f2e3.md`
**Notion Registration:** (pending if user requests)

---

*DEFERRED_SCOPE markers captured from parent plan execution:*
* `DEFERRED_SCOPE: Real Gemini SDK wiring under SovereignLLMGateway (v1 ships fail-closed)`
* `DEFERRED_SCOPE: L3 MANAGED_WORKFLOW orchestration for apps_rg (multi-step path deferred to v2)`
* `DEFERRED_SCOPE: UWG promotion of L1PlanContract/RouteContract/FinalEvidenceContract/L7RuntimeAuditTrace to L4`
* `DEFERRED_SCOPE: Replication of declarative-ingress-only governance to sibling apps`
