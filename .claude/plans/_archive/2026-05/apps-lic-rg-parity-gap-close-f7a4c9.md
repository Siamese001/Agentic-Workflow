---
plan_id: apps-lic-rg-parity-gap-close-f7a4c9
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_lic → apps_rg golden-state parity (gap analysis rollout)

Close governed-runtime proof gaps for `apps_lic` identified in `apps_lic_vs_apps_rg_gap_analysis.md` (archive audit), prioritized W0-first: unblock monorepo runtime, then SSOT contracts, real L2, canonical gates/Exit, evidence chain, and L6/X1D/99 proof.

> **plan_id discipline**: Filename stem matches `plan_id`. Markers use `plan=apps-lic-rg-parity-gap-close-f7a4c9`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-15

---

## Context (SCQA)

- **Situation** — An external/uploaded `apps_lic` archive shows substantial domain assets (U0 adapter, profiles, FEC bridge, PA compiler, managed workflow, judges scaffolding) but was audited **without** `agentic_core`, `apps_rg`, `tests/_apps_contract`, or CI scripts.
- **Complication** — Integrated runtime smoke fails (`No module named 'agentic_core'`); ingress, route SSOT, L2, gates, Exit/X3, C0 proof, judges, L6 chain, and contract tests are not yet golden-state certified.
- **Question** — How do we systematically close parity gaps **in the full monorepo** while preserving architecture law (apps own ingress/profiles; core stays generic)?
- **Answer** — Execute in waves: prove runtime spine end-to-end, collapse route policy SSOT, harden L2 and gate/Exit receipts, strengthen evidence/PA proofs, then X1D/L6/99 closure with contract gates—deferring core renames unless a boundary audit confirms leakage.

---

## Source Document

Secondary SSOT for findings (user-supplied audit path):

- Original narrative: user-local `Downloads/apps_lic_vs_apps_rg_gap_analysis.md`; derived register IDs **LIC-GAP-001** … **013** preserved below.

---

## Status Tables

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1–P1.3 | Runtime unblock + U0 ingress binding | ~25K | Full repo checkout; secrets for any live judges deferred | 🔲 TODO | `python -m apps_lic ...` exit 0; `ValidatedRequest` carries `AppsLicIngressContractV1` |
| W2 | P2.1–P2.2 | L0 route policy single SSOT | ~12K | Product agrees briefing-only stance | 🔲 TODO | One canonical route family; stale R3/briefing quarantined or removed |
| W3 | P3.1–P3.3 | L2 real adapters + UWG negatives | ~35K | Provider gateway available or honest BLOCK | 🔲 TODO | Real sealed artifact or sealed rejection; no synthetic receipt; no rogue CommitRequest |
| W4 | P4.1–P4.2 | 00C gates + Exit X3 | ~20K | apps_rg patterns reusable as reference | 🔲 TODO | `GateMeshResult` visible at Exit; exactly one canonical X3 |
| W5 | P5.1–P5.2 | C0/FEC + PA hardening | ~18K | apps_research path defined as SSOT for evidence vs direct C0 | 🔲 TODO | Evidence ledger + citations/ACL/freshness proof or explicit partial |
| W6 | P6.1–P6.3 | X1D/L6/99 + contract tests | ~25K | Human labels optional for early merge | 🔲 TODO | `RuntimeExhaustBundle`→`CompletedEvalRecord`→inert proposal; `_apps_contract` tests added |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Monorepo runtime smoke | `apps_lic/__main__.py`, env/PYTHONPATH, spine entry | Archive vs HEAD drift | ~6K | 🔲 TODO |
| P1.2 | U0 ingress bridge | `runtime/u0/*`, `contracts/*`, `profile_builder.py` | `AppsRgIngressPayload` vs `AppsLicIngressContractV1` | ~10K | 🔲 TODO |
| P1.3 | Runtime proof bundle capture | artifact dir, OTEL/trace refs | Proof bundle discipline | ~9K | 🔲 TODO |
| P2.1 | Route SSOT collapse | `l0_policy.yaml`, `route_profiles.yaml`, domain_contract route JSON | Contradictory R3/briefing | ~8K | 🔲 TODO |
| P2.2 | Cache/route tests | profiles + tests | Final-draft bypass vs R1 | ~4K | 🔲 TODO |
| P3.1 | L2 validation depth | `integrations/lic_l2_step_adapters.py` | TODO pass-throughs | ~15K | 🔲 TODO |
| P3.2 | Provider + seal | gateway, schema validation | Synthetic receipt removal | ~12K | 🔲 TODO |
| P3.3 | UWG/Commit clarity | adapters + capability profiles | Ambiguous draft commit comment | ~8K | 🔲 TODO |
| P4.1 | Gate receipts | gate profiles vs runtime GateMesh | UNKNOWN must not PASS | ~10K | 🔲 TODO |
| P4.2 | Exit/X3 mapping | `exit_profile*`, disposition mapping | App-local APPROVED/REJECTED vs X3A–X3E | ~10K | 🔲 TODO |
| P5.1 | FEC/C0 proof | `fec_producer.py`, `apps_research_bridge.py`, `c0_graph_adapter.py` | CONFIG_PREPARED_ONLY graph | ~10K | 🔲 TODO |
| P5.2 | PA unresolved placeholders | `lic_pa_compiler.py`, templates | Weak rejection proof | ~8K | 🔲 TODO |
| P6.1 | Judges + calibration | `evals/*`, `judges/*` | Empty human labels | ~10K | 🔲 TODO |
| P6.2 | L6 completed-run chain | learning profiles + observer wiring | Missing exhaust/eval records | ~10K | 🔲 TODO |
| P6.3 | CI contract surface | `tests/_apps_contract/`, selective pytest | Archive had no tests | ~5K | 🔲 TODO |

### Wave Progress (hook-maintained compact view)

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Runtime + U0 | 🔲 TODO | — | — |
| W2 | Route SSOT | 🔲 TODO | — | — |
| W3 | L2 + UWG | 🔲 TODO | — | — |
| W4 | Gates + Exit | 🔲 TODO | — | — |
| W5 | C0 + PA | 🔲 TODO | — | — |
| W6 | X1D + L6 + 99 | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| P1.1 | Monorepo runtime smoke | 🔲 TODO |
| P1.2 | U0 ingress bridge | 🔲 TODO |
| P1.3 | Proof bundle capture | 🔲 TODO |
| P2.1 | Route SSOT collapse | 🔲 TODO |
| P2.2 | Cache/route tests | 🔲 TODO |
| P3.1 | L2 validation depth | 🔲 TODO |
| P3.2 | Provider + seal | 🔲 TODO |
| P3.3 | UWG/Commit clarity | 🔲 TODO |
| P4.1 | Gate receipts | 🔲 TODO |
| P4.2 | Exit/X3 mapping | 🔲 TODO |
| P5.1 | FEC/C0 proof | 🔲 TODO |
| P5.2 | PA hardening | 🔲 TODO |
| P6.1 | Judges + calibration | 🔲 TODO |
| P6.2 | L6 chain | 🔲 TODO |
| P6.3 | Contract tests | 🔲 TODO |

---

## Out Of Scope (this plan cycle)

- Broad `agentic_core` refactors (only file **CORE_GAP_CANDIDATES** after ADG/boundary audit user authorizes core work).
- Renaming shared types solely for cosmetics without leakage proof (`LIC-GAP-012`).
- Completing judge promotion without human/adjudicated labels (`LIC-GAP-009`).
- Implementing GraphRAG/C0 traversal while `CONFIG_PREPARED_ONLY`—must be explicit deferral unless product demands.

---

## Wave 1 — Runtime unblock + U0 parity

WAVE_ID: W1  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases**: P1.1 · P1.2 · P1.3  

**Acceptance**:

- LIC-GAP-001 cleared: CLI run with monorepo `PYTHONPATH`/`uv`/project venv emits non-failure spine or honest R5 with captured artifacts.
- LIC-GAP-002 cleared: ingress path conforms to `AppsLicIngressContractV1` before U0 adaptation.
- Proof directory lists `validated_request`, route decision, PA artifact reference, L2 outcome (success or bounded failure), Exit packet stub/progress toward X3 chain.

---

## Wave 2 — Route policy SSOT

WAVE_ID: W2  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: B

**Phases**: P2.1 · P2.2  

**Acceptance**:

- LIC-GAP-003 cleared: domain_contract route profile wins; YAML/static duplicates updated, quarantined, or flagged `deprecated` with CI guard if needed.
- Final personalized drafts bypass R1A/R1B per policy; governed cache only for allowed support artifacts.

---

## Wave 3 — L2 execution + sealing

WAVE_ID: W3  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: C

**Phases**: P3.1 · P3.2 · P3.3  

**Acceptance**:

- LIC-GAP-004 cleared: remove synthetic `_e5_l2_receipt` / `test_l2_receipt` class behaviors; validate manifest, claims, placeholders, send mode; real provider call or DOCUMENTED block.
- LIC-GAP-013 cleared: clarify CommitRequest semantics; negative tests forbid direct send/write off-spine paths.

---

## Wave 4 — Canonical gates + Exit X3

WAVE_ID: W4  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: D

**Phases**: P4.1 · P4.2  

**Acceptance**:

- LIC-GAP-005/006 cleared: adapters produce/consume canonical gate mesh receipts; UNKNOWN never PASS; Exit emits exactly one X3-compatible disposition + user-visible packet.

---

## Wave 5 — Evidence (C0/FEC) + PA

WAVE_ID: W5  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: E

**Phases**: P5.1 · P5.2  

**Acceptance**:

- LIC-GAP-007 cleared: FEC or research bridge proves citations/ACL/freshness/version; graph adapter either live or explicitly “not runtime-ready.”
- LIC-GAP-008 cleared: unresolved template placeholders cause hard rejection with tests.

---

## Wave 6 — X1D, L6, 99 bundle, CI

WAVE_ID: W6  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: F

**Phases**: P6.1 · P6.2 · P6.3  

**Acceptance**:

- LIC-GAP-009: deterministic judges wired; LLM judges remain non-promoted until labels exist (document expectation).
- LIC-GAP-010: completed-run-only L6 chain artifacts present (`RuntimeExhaustBundle` → `CompletedEvalRecord` → inert proposals).
- LIC-GAP-011: selective `pytest` under `tests/_apps_contract/` + app smoke scripted in CI or local gate doc.

---

## Gap Register

| ID | Severity | Classification | Finding | Proof / seam |
|----|----------:|----------------|-----------|---------------|
| LIC-GAP-001 | BLOCKER | REQUIRED_PARITY | No integrated runtime without core | Monorepo smoke + artifact bundle |
| LIC-GAP-002 | BLOCKER | REQUIRED_PARITY | U0 ingress shape mismatch suspicion | Ingress bridge + validated request artifact |
| LIC-GAP-003 | HIGH | REQUIRED_PARITY | Route SSOT contradiction | Profile collapse + route tests |
| LIC-GAP-004 | CRITICAL | REQUIRED_PARITY | L2 TODOs / synthetic seal | Real seal path + provider |
| LIC-GAP-005 | HIGH | REQUIRED_PARITY | Missing GateVerdict/GateMesh in archive audit | Wire canonical gate receipts |
| LIC-GAP-006 | HIGH | REQUIRED_PARITY | Exit vocab vs X3 | Mapping or native spine packet |
| LIC-GAP-007 | HIGH | DOMAIN_ADAPTATION | FEC bridge without live Golden C0 proof | Evidence contract + citations |
| LIC-GAP-008 | MEDIUM | DOMAIN_ADAPTATION | PA placeholder enforcement | Negative tests |
| LIC-GAP-009 | HIGH | DOMAIN_ADAPTATION | Judges blocked / unstubs | Labels + calibration gating |
| LIC-GAP-010 | HIGH | REQUIRED_PARITY | L6 chain absent | Completed-run ingest only |
| LIC-GAP-011 | HIGH | REQUIRED_PARITY | No tests in upload | Repo contract tests |
| LIC-GAP-012 | MEDIUM | CORE_GAP_CANDIDATE | `AppsRgIngressPayload` naming in apps_lic | ADG audit before any core rename |
| LIC-GAP-013 | HIGH | REQUIRED_PARITY | UWG/commit clarity | Negative controls + docs in Exit path |

---

## Definition of Done

| DoD | Criterion | Evidence command / artifact |
|-----|-----------|-----------------------------|
| DoD-1 | End-to-end `apps_lic` run exits 0 in monorepo with captured spine artifacts | `python -m apps_lic ...` + artifact dir listing |
| DoD-2 | Route/cache behavior matches finalized domain contract | Targeted pytest on route + cache bypass |
| DoD-3 | L2 produces non-synthetic sealed outcome or bounded failure | Unit/integration tests on `lic_l2_step_adapters` |
| DoD-4 | Gates + Exit: UNKNOWN never PASS; one X3 | Gate/exit pytest or runtime bundle fields |
| DoD-5 | Contract/regression subset green | `python -m pytest tests/_apps_contract/<selectors> -q` |
| DoD-6 | L6 only post-run; learning artifacts deterministic | pytest for exhaust → eval → proposal path |

### Verification vs deferral

| Topic | Verified in-repo | Deferred (explicit marker) |
|-------|------------------|-----------------------------|
| Full GraphRAG / C0 traverse | FEC + apps_research path | `c0_graph_adapter` CONFIG_ONLY until chartered |
| LLM judge promotion | Deterministic judges on path | Promotion until Spearman/human labels |
| Core type rename (`AppsRgIngressPayload`) | Boundary audit dossier | No core edits without charter |

---

## Scope Expansion Authorization

Use standard markers (`DISCOVERED_SCOPE`, `AUTHORIZATION_DECISION`, `SCOPE_EXPANSION`) if execution reveals CORE work or cross-app abstraction.

---

## Marker Quick Reference

```
WAVE_START: plan=apps-lic-rg-parity-gap-close-f7a4c9 wave=<N>
WAVE_COMPLETE: plan=apps-lic-rg-parity-gap-close-f7a4c9 wave=<N> note="<summary>"
PHASE_COMPLETE: plan=apps-lic-rg-parity-gap-close-f7a4c9 phase=<P#.>
PLAN_COMPLETE: plan=apps-lic-rg-parity-gap-close-f7a4c9 note="<final outcome>"
```

---

## Reviewer Notes (non-normative)

Cross-check all archive-only conclusions against **current repo HEAD** before execution (drift risk).
