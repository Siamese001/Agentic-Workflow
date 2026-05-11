---
dod_exempt: false
---
# apps_lic U0 Runtime Package Complete

**Plan ID:** apps-lic-u0-runtime-package-complete-f8e2a1  
**Status:** In Progress (W5+ remaining)  
**Created:** 2026-05-11  
**Tier:** T3 Architectural

## Objective
Implement or verify a complete apps_lic runtime customization package that enters through U0 and carries everything agentic_core needs to run apps_lic on the common agentic spine.

## Critical Framing
- **NOT** a blind file addition task
- Audit first, reuse existing implementation
- No duplicate concepts under new names
- No parallel apps_lic pipeline
- No copy of apps_rg resume-generation semantics
- Remove stale briefing-only/R3-only routing language

## Domain Definition
- **app_id:** apps_lic
- **task_class:** outreach_message
- **Domain:** outreach personalization / governed outreach draft generation
- **Normal posture:** read-only outreach draft generation and validation
- **Forbidden actions:** send email, LinkedIn message, SMS, connector send, auto-send, external HTTP post, ungoverned egress

## Final L0 Routing Law

apps_lic L0 must choose exactly one outcome:

### 1. R4_MANAGED_DRAFT
**Condition:** fresh, valid outreach context exists; no apps_research support needed  
**Path:** U0 → L1 → L0 → R4 task family → execution_form=MANAGED_WORKFLOW → L3 HOP draft workflow → L2 bounded steps → Exit clears final draft

### 2. R3R4_MANAGED_RESEARCH_THEN_DRAFT
**Condition:** fresh context missing/stale/incomplete; research authorized  
**Path:** U0 → L1 → L0 → R3R4 managed workflow → L3 apps_research support → L3 validates/builds context → L3 HOP draft workflow → L2 bounded steps → Exit clears final draft

### 3. R5_FALLBACK
**Condition:** no valid context; research not authorized; policy/consent/evidence/channel invalid  
**Path:** U0/L1/L0/L3/L2 failure → R5 terminal packet → Exit → bounded fail-closed / abstain / no-draft outcome

## Cache Rules
- **R1A exact cache:** BYPASS for final outreach draft reuse
- **R1B semantic cache:** BYPASS for final outreach draft reuse
- **Allowed cache uses:** verified company briefing, public company facts, retrieval manifests, consent/compliance evidence, approved prompt/profile refs, policy/rubric/threshold refs
- **Forbidden cache uses:** final outreach message, personalized opening, CTA, recipient-specific claim, consent-dependent language, channel-rendered final copy

## W0 Hardening Clarifications (Applied)

1. **L4 Write Path** — Changed from IMPLEMENTED to PARTIAL. Documentation-only claims insufficient; requires code/static scan verification.

2. **Cache Policy** — Changed from IMPLEMENTED to PARTIAL. Must explicitly prove R1A/R1B bypass for final drafts, not just semantic_cache_enabled=false.

3. **Forbidden Send Modes** — Changed from IMPLEMENTED to PARTIAL. Must cover all 7 modes (currently only validates 3: send_now, auto_send, connector_send). Missing: email_outbox_send, linkedin_send, sms_send, external_http_post.

4. **Route Drift** — Marked HIGHEST PRIORITY. Must replace old names (evidence_grounded_generation, ungrounded_generation, R3_grounded_read, briefing-only) with final L0 outcomes (R4_MANAGED_DRAFT, R3R4_MANAGED_RESEARCH_THEN_DRAFT, R5_FALLBACK).

5. **Final L0 Tree Structure** — Documented exactly:
   - Bypass R1A/R1B for final draft reuse
   - R4_MANAGED_DRAFT (fresh context) → MANAGED_WORKFLOW → L3 HOP → L2 → Exit
   - R3R4_MANAGED_RESEARCH_THEN_DRAFT (research authorized) → L3 apps_research support → L3 HOP → L2 → Exit
   - R5_FALLBACK (no valid context) → fail closed / no draft

6. **Briefing-Only Route** — Must be removed from apps_lic. Route to apps_research directly or fail closed with safe guidance.

7. **W8 Test Approach** — Map existing tests first, add only missing executable tests. Final receipt separates: tests_reused, tests_added, tests_missing_but_deferred with reasons.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1-P0.6 | Audit current implementation | ~8k | ADG healthy, files readable | ✅ DONE | 45-item audit matrix complete (11 IMPLEMENTED, 7 PARTIAL, 24 MISSING, 3 DRIFTED). Hardening clarifications applied per user acceptance. |
| W1 | P1.1-P1.6 | RuntimeCustomizationPackageSection + 6 JSON configs | ~12k | W0 complete, route fields aligned to final L0 | ✅ DONE | Package exists with final route names only (R4/R3R4/R5)
| W2 | P2.1-P2.6 | L0 routing correction - HIGHEST PRIORITY | ~10k | W1 package with correct route fields | ✅ DONE | Old routes removed, R4/R3R4/R5 implemented, cache bypass proven |
| W3 | P3.1-P3.6 | Exit/L6 package consumption + static no-bypass scan | ~12k | W2 L0 routing complete | ✅ DONE | Exit consumes package, L6 future-run only, no-bypass proven |
| W3.5 | P3.7-P3.10 | Fail-closed exit profile, forbidden-send-modes contract-source, data-driven cache receipt, field-map MAPPED | ~6k | W3 complete | ✅ DONE | _load_exit_profile fail-closed; AppsLicExitProfileError; no hardcoded G-numbers; forbidden send modes from validated contract; cache receipt data-driven; 89/89 tests |
| W4 | P4.1-P4.4 | Schema regeneration & field-map coverage proof | ~6k | W3.5 complete | ✅ DONE | JSON schema from Pydantic; 233 pointers, 100% covered; silently_dropped=[]; 21 tests pass |
| W5 | P5.1-P5.4 | Integration wiring (runner, handoff) | ~10k | U0 adapter pattern exists | ✅ DONE | Package preserved through chain; stale R3_grounded_read removed |
| W6 | P6.1-P6.4 | L0 routing correction | ~8k | L0 routing code located | Not Started | Final routing model implemented |
| W7 | P7.1-P7.3 | Core profile resolution wiring | ~6k | Generic resolver pattern exists | Not Started | Exit/L6 consume refs generically |
| W8 | P8.1-P8.4 | Tests & negative controls | ~12k | Test patterns from apps_rg | Not Started | 81 tests pass |
| W9 | P9.1-P9.2 | Verification & receipt | ~4k | All prior waves green | Not Started | Receipt JSON written, tests green |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Read apps_lic ingress contract | 1 | Frozen model validation | 2k | ✅ DONE |
| P0.2 | Read apps_lic config files | 15+ | YAML consistency check | 2k | ✅ DONE |
| P0.3 | Inspect agentic_core U0/Exit/L6 | 5+ | Cross-layer contract chain | 2k | ✅ DONE |
| P0.4 | Check existing layer bindings | 3+ | Pattern reuse from apps_rg | 1k | ✅ DONE |
| P0.5 | Build audit matrix | 1 | 45 capability rows | 1k | ✅ DONE |
| P0.6 | W0 receipt & gap identification | 1 | Clear gap categorization | 1k | ✅ DONE |
| P1.1 | Add RuntimeCustomizationPackageSection dataclass | 1 | Strict frozen Pydantic, extra=forbid | 4k | ✅ DONE |
| P1.2 | Add ProfileRef dataclass (nested) | 1 | ref_id, path, digest, required | 2k | ✅ DONE |
| P1.3 | Add PolicySection dataclasses | 1 | Route, Write, ForbiddenSend, Consent | 3k | ✅ DONE |
| P1.4 | Add runtime_customization_package field to contract | 1 | Top-level field with all refs | 3k | ✅ DONE |
| P1.5 | Create 6 JSON config profile files | 6 | Aligned to final L0 model only | 2k | ✅ DONE |
| P1.6 | W1 verification receipt | 1 | Route fields use final names only | 1k | ✅ DONE |
| P2.1 | Remove old route families from L0 binding | 1 | evidence_grounded_generation, etc | 2k | ✅ DONE |
| P2.2 | Implement _derive_route_family for R4/R3R4/R5 | 1 | Context + auth detection | 2k | ✅ DONE |
| P2.3 | meta_feedback_profile.outreach_message.v1.json | 1 | L6 learning params | 2k | ✅ DONE |
| P2.4 | Implement cache bypass in L0 | 1 | final_draft_r1a_bypass flags | 2k | ✅ DONE |
| P2.5 | Add briefing-only fail-closed handling | 1 | Route to apps_research or R5 | 1k | ✅ DONE |
| P2.6 | W2 verification tests | 1 | Executable proof of all 7 behaviors | 1k | ✅ DONE |
| P3.1 | Exit binding consumes exit_profile_ref from package | 1 | Load required/conditional gates | 2k | ✅ DONE |
| P3.2 | Exit fail-closed on missing GateMeshResult/required gate | 1 | material UNKNOWN -> ESCALATE | 2k | ✅ DONE |
| P3.3 | G27 handling for read-only draft return | 1 | NOT_APPLICABLE with reason | 2k | ✅ DONE |
| P3.4 | RuntimeExhaustBundle carries profile refs + cache bypass | 1 | Bundle enrichment | 2k | ✅ DONE |
| P3.5 | L6 consumes bundle after current-run boundary | 1 | Future-run proposals only | 2k | ✅ DONE |
| P3.6 | Static scan: no L4 writes, no send path, no X3, no cache return | 1 | Narrow static analysis | 2k | ✅ DONE |
| P3.7 | Remove hardcoded G-number fallback from _load_exit_profile | 1 | Fail-closed on missing/malformed/digest-mismatch config | 2k | ✅ DONE |
| P3.8 | Add AppsLicExitProfileError; return profile_id/config_path/config_digest | 1 | Prove data came from config, not code | 1k | ✅ DONE |
| P3.9 | Forbidden send modes: remove pre-Pydantic hardcoded check; use validated contract as source | 1 | Post-validation check; re-raise ValidationError as E2 | 2k | ✅ DONE |
| P3.10 | Cache bypass receipt: fully data-driven from CacheBypassPolicy fields + config digest | 1 | No static strings as proof | 1k | ✅ DONE |
| P4.1 | Generate JSON Schema from AppsLicIngressContractV1.model_json_schema() | 1 | Write to artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json | 2k | ✅ DONE |
| P4.2 | Enumerate all 233 JSON pointers; verify field-map coverage 100% | 1 | silently_dropped=[] | 2k | ✅ DONE |
| P4.3 | Verify runtime_customization_package (126 ptrs) all MAPPED to app_payload.* | 1 | MAPPED/DERIVED/DEFERRED audit | 2k | ✅ DONE |
| P4.4 | Verify derived fields have explicit receipts (payload_digest, package_digest) | 1 | Explicit reason in field map | 1k | ✅ DONE |
| P5.1 | Wire lic_ingress_runner.py | 1 | Construct package in U0 payload | 3k | ✅ DONE |
| P5.2 | Wire spine_handoff.py | 1 | Preserve into ValidatedRequest | 3k | ✅ DONE |
| P5.3 | Compute/verify package_digest | 1 | Digest conventions | 2k | ✅ DONE (already in U0 adapter via W4) |
| P5.4 | Remove stale R3_grounded docs | 1 | Doc correction | 2k | ✅ DONE |
| P6.1 | Implement R4_MANAGED_DRAFT path | 1 | Fresh context → L3 HOP | 2k | Not Started |
| P6.2 | Implement R3R4_MANAGED_RESEARCH_THEN_DRAFT | 1 | Missing context → apps_research → HOP | 3k | Not Started |
| P6.3 | Implement R5_FALLBACK | 1 | Fail-closed / abstain | 2k | Not Started |
| P6.4 | Remove briefing-only route | 1 | Route to apps_research or fail | 1k | Not Started |
| P7.1 | Generic profile resolver (if missing) | 1 | Load by ref/path/digest | 2k | Not Started |
| P7.2 | Exit harness consume exit_profile_ref | 1 | Enforce declaratively | 2k | Not Started |
| P7.3 | L6 RuntimeExhaustBundle wiring | 1 | learning_profile_ref carried | 2k | Not Started |
| P8.1 | U0 package tests (16 tests) | 1 | Strict validation tests | 4k | Not Started |
| P8.2 | L0 route tests (12 tests) | 1 | Routing logic tests | 3k | Not Started |
| P8.3 | Exit/gate tests (17 tests) | 1 | Gate enforcement tests | 3k | Not Started |
| P8.4 | Negative controls (14 tests) | 1 | Fail-closed verification | 2k | Not Started |
| P9.1 | Run targeted test suite | 1 | pytest tests/_apps_contract/ | 2k | Not Started |
| P9.2 | Write receipt JSON | 1 | artifacts/apps_lic/...receipt.json | 2k | Not Started |

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|------------|
| DoD-1 | 45-item audit matrix completed | W0 receipt shows IMPLEMENTED/PARTIAL/MISSING/DRIFTED for all 45 capabilities |
| DoD-2 | 5 JSON config profiles added/verified | Files exist at apps_lic/config/domain_contract/*.outreach_message.v1.json |
| DoD-3 | RuntimeCustomizationPackageSection in Pydantic | Strict frozen model, extra=forbid, all nested sections present |
| DoD-4 | JSON schema regenerated from Pydantic | ✅ artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json — 233 pointers, 100% covered |
| DoD-5 | Field map covers all runtime_customization_package pointers | ✅ 126 rcp pointers covered; silently_dropped=[] |
| DoD-6 | lic_ingress_runner constructs complete package | Payload includes all required refs, digests, policies |
| DoD-7 | spine_handoff preserves package into ValidatedRequest | app_payload.runtime_customization_package accessible downstream |
| DoD-8 | L0 routing implements final model | R4_MANAGED_DRAFT, R3R4_MANAGED_RESEARCH_THEN_DRAFT, R5_FALLBACK only |
| DoD-9 | Briefing-only route removed from apps_lic | Routes to apps_research or fails closed |
| DoD-10 | Cache bypass for final draft enforced | R1A/R1B bypass for final outreach draft reuse |
| DoD-11 | Exit harness enforces apps_lic Exit profile | ✅ W3.5: fail-closed; gates loaded from config SSOT only; AppsLicExitProfileError on any failure |
| DoD-12 | 81 tests pass | tests/_apps_contract/test_apps_lic_*.py all green |
| DoD-13 | Receipt JSON written | artifacts/apps_lic/apps_lic_u0_complete_runtime_package_receipt.json exists |

## Verification vs Deferral

| Checkpoint | Verify Now | Defer |
|------------|------------|-------|
| W0 audit matrix | ✅ Complete before any edits | ❌ |
| Config JSON profiles | ✅ Add if missing | ❌ |
| Pydantic model strictness | ✅ Preserve frozen/extra=forbid | ❌ |
| Field map coverage | ✅ 100% pointer coverage | ❌ |
| L0 routing final model | ✅ Implement now | ❌ |
| Core generic profile resolver | ✅ Verify/create if missing | ❌ |
| 81 test implementations | ✅ Add missing tests | ❌ |
| Integration with apps_research C0 | ❌ | ➡️ Future plan if C0 wiring not ready |
| Real LLM judge calibration | ❌ | ➡️ Holdout-based calibration plan |
| Production holdout separation | ❌ | ➡️ Eval harness deferred work |

## Non-Goals (Explicitly Out of Scope)

1. **C0 FEC producer binding** — apps_lic may use apps_research as support step, but full C0 grounding is separate BLOCKER #4 work
2. **Real LLM judge implementations** — stubs acceptable; real logic needs holdout calibration
3. **Production-log mining** — deferred to observability plan
4. **Send connector implementation** — apps_lic is draft-only; sends are explicitly forbidden
5. **L4 direct write path** — must go through UWG only
6. **X3 emission from apps_lic** — Exit harness only
7. **L6 current-run rescue** — L6 is completed-run only per architecture

## Key Files Expected

### Config Deliverables
- `apps_lic/config/domain_contract/runtime_customization_package.outreach_message.v1.json`
- `apps_lic/config/domain_contract/runtime_gate_profile.outreach_message.v1.json`
- `apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json`
- `apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json`
- `apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json` (if needed)
- `apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json` (if needed)

### Contract Deliverables
- `apps_lic/contracts/apps_lic_ingress_contract_v1.py` — add RuntimeCustomizationPackageSection
- `apps_lic/contracts/apps_lic_ingress_contract.v1.schema.json` — regenerate from Pydantic
- `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml` — complete pointer coverage

### Integration Deliverables
- `apps_lic/integrations/lic_ingress_runner.py` — construct package
- `apps_lic/integrations/spine_handoff.py` — preserve package
- `agentic_core/runtime/u0/apps_lic_u0_adapter.py` — validate & preserve (if exists)

### Test Deliverables
- `tests/_apps_contract/test_apps_lic_u0_runtime_package.py` — 16 U0 tests
- `tests/_apps_contract/test_apps_lic_l0_routing.py` — 12 L0 tests
- `tests/_apps_contract/test_apps_lic_exit_gates.py` — 17 Exit/gate tests
- `tests/_apps_contract/test_apps_lic_negative_controls.py` — 14 negative tests

### Receipt Deliverable
- `artifacts/apps_lic/apps_lic_u0_complete_runtime_package_receipt.json`

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing apps_lic code has drifted from spec | Medium | High | W0 audit catches drift; reconcile rather than overwrite |
| Payload digest infrastructure missing | Low | Medium | Verify digest conventions exist; harden if partial |
| Generic profile resolver not yet in agentic_core | Low | High | Create if missing; follow apps_rg pattern |
| Field map silent drop of new fields | Medium | High | Explicit field map verification step |
| L0 routing conflict with existing briefing-only path | Medium | High | Author-Gate decision if removal is destructive |
| Strict Pydantic breaks existing tests | Low | Medium | Fix tests, not validation; preserve strictness |
| Cross-layer wiring complexity | Medium | Medium | Phase-by-phase verification; tests at each boundary |

## Gap Register

<!-- Deferred scope items captured during execution -->

### W3.5 Blocking Corrections (applied, closed)

| Item | Correction | Status |
|------|-----------|--------|
| Hardcoded G-number fallback in `_load_exit_profile` | Removed; raises `AppsLicExitProfileError` fail-closed | ✅ CLOSED |
| Pre-Pydantic `_REQUIRED_FORBIDDEN_SEND_MODES` constant | Removed; post-validation check uses `contract.forbidden_send_modes.modes` | ✅ CLOSED |
| Static cache bypass receipt strings | Replaced with data-driven `CacheBypassPolicy` field values + config digest | ✅ CLOSED |
| Field map `runtime_customization_package` entries showing DEFERRED | Changed to MAPPED with `app_payload` target | ✅ CLOSED |
| `payload_digest` field map missing DERIVED status | Added DERIVED with explicit adapter-computed digest receipt | ✅ CLOSED |

### W4 Completed Artefacts

| Artefact | Path |
|---------|------|
| Pydantic JSON Schema | `artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json` |
| Field-map coverage result | `artifacts/apps_lic/w4_field_map_coverage_result.json` |
| W4 verification tool | `tools/apps_lic/w4_schema_verify.py` |
| W4 tests (21) | `tests/_apps_contract/test_w4_apps_lic_schema_field_map_coverage.py` |
| W4 receipt | `apps_lic/contracts/w4_schema_field_map_receipt.md` |
| W3.5 receipt | `apps_lic/contracts/w3_5_boundary_receipt.md` |

## Notes

**Pattern to follow:** apps_rg runtime wiring (plan apps-rg-runtime-wiring-completion-d4e8a1) established the 7-layer binding pattern (U0/L1/L0/C0/PA/L2/Exit) as pure functions. Reuse this pattern for apps_lic where applicable.

**Critical invariant:** U0 carries the package only — does not execute judges, gates, evals, models, tools, sends, routing, orchestration, or learning.

**Route shape invariant:** Exactly one RouteContract emitted from L0; no briefing-only route; cache bypass for final drafts; R4_MANAGED_DRAFT calls L3 HOP orchestration (not direct L2).
