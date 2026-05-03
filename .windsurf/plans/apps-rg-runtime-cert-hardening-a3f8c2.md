# apps_rg Runtime Certification & Quality Hardening

- **Plan slug**: `apps-rg-runtime-cert-hardening-a3f8c2`
- **Tier**: T3 (cross-layer — touches `apps_rg/`, `apps_shared/spine_emission/`, `agentic_core/runtime/entrypoints/`, `agentic_core/L5_safety/hitl/`, `tools/cert/apps_e2e/`, `certification/apps_evidence_assertions.jsonl`)
- **Status**: Completed (W1-W7 executed 2026-05-03; follow-up W8 activation plan apps-rg-deferred-activation-w8-a7f4d9 also Completed; gaps tracked in apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4)
- **Authored from**: live-run RCA against `artifacts/apps_rg/runs/20260503_135650/` (Blend360 SVP Agentic Transformation run) + 2026-05-03 spine-certification audit + 2026-05-03 agentic_core infrastructure inventory.
- **Revision history**:
  - v1 2026-05-03 — 8 gaps, 7 waves (quality/HITL/cert-wiring focus)
  - v2 2026-05-03 — 17 gaps, 10 waves (added 9 spine-contract gaps from audit; assumed they needed building)
  - **v3 2026-05-03 (CURRENT)** — **8 gaps closed, 8 reframed as wiring**; 7 waves, ~60K tokens. Cross-check of `agentic_core/` confirmed all canonical infrastructure already exists (route_contract_v15 with SINGLE_STEP/R4, l2_v4_contracts with E1–E5, G01–G29 runtime gates, Exit v6 pipeline, integrated_single_action_run entrypoint, spine_proof_bundle). `apps_shared/spine_emission/` is a **standalone pydantic shortcut with ZERO imports of agentic_core**. The 9 "spine-contract gaps" are one problem: **apps_rg bypasses the agentic_core runtime via `apps_shared.spine_emission.governed_run`**. Fix = thin-adapter refactor, not new emitters.

---

## 1. Goal

Bring an `apps_rg --target-company X --target-role Y` invocation from **"smoke pass"** to **conclusive runtime certification** by (a) fixing the immediate HITL signal + provenance contradiction, (b) formalizing the 2026-05-03 calibration drift through retroactive Author-Gate, (c) **refactoring `apps_shared/spine_emission/` from a parallel shortcut into a thin adapter over `agentic_core/runtime/entrypoints/`**, and (d) then producing a Fort Knox signoff whose evidence refs cite the real agentic_core receipts.

### The eight closure gaps (consolidated)

1. `run_report.status='HUMAN_REVIEW'` is not propagated to spine receipts (`ExitReviewPacket.x3_disposition='EXIT_OK'` contradicts it).
2. `provenance_report.valid=false` (`no_master_bullets`) goes unresolved at runtime.
3. apps_rg's HITL is an advisory JSON field, not the agentic_core blocking `HITLApprovalGate` (`router_l5_hitl`, ADR-023).
4. OTEL trace has only 3 app-level spans; no per-HOP/per-section/per-LLM detail AND no spine-level spans (U0, L1, L0, L3_bypass, L2_E1..E5, Exit_X1..X3, L6_handoff, runtime_gates).
5. Seven narrative-judge thresholds were relaxed during the 2026-05-03 calibration session without Author-Gate packets.
6. `_SENIORITY_SKIP` / `DEFAULT_BUZZWORDS` hard-coded in code rather than declared in config.
7. apps_e2e Fort Knox arm (constitutional §32) has never been invoked for apps_rg — no `APPS-REQ-RG-*` signoff exists.
8. Post-run unsealed artifacts (`Amit_Ayer_Resume_fixed.docx`) sit outside `runtime_exhaust_bundle.json::artifact_sha256_map`.

### The **one** architectural gap that generates audit findings G11–G19

**Root cause:** `apps_shared/spine_emission/` is a 3-file pydantic shortcut (`contracts.py`, `context.py`, `otel_trace.py`) built to satisfy the apps_e2e auditability harness's file-existence checks. It has **zero imports of `agentic_core`**. It rolled its own `ExecutionForm` enum (includes non-canonical `DETERMINISTIC_PIPELINE`), its own `X3Disposition` (missing X3A..X3G), its own `L2ExecutionReceipt` (no E1..E5), its own `RouteContract` (no `route_digest` / `hmac_sig` / `policy_hash` / `blueprint_hash` / `capability_token_ref` / `sandbox_envelope_ref` / `replay_key`). Meanwhile `agentic_core` has the full canonical machinery:

| Canonical type | Already at |
|---|---|
| `RouteContractV15` (SINGLE_STEP, R4_SINGLE_ACTION, deterministic_route_digest, HMAC, policy_hash, blueprint_hash) | `agentic_core/L0_routing/types/route_contract_v15.py` |
| `WorkOrderInputs` / `PrepOutput` / `ValidationOutput` / `ExecOutput` (E1–E5) | `agentic_core/L2_execution/types/l2_v4_contracts.py` |
| G01–G29 runtime gates (29 modules, including g24_determinism_replay, g26_exit_disposition, g28_audit_trace_completeness, g29_learning_firewall) | `agentic_core/L5_safety/runtime_gates/g0*.py` through `g29_*.py` |
| Exit X1/X2/X3 pipeline (v6) | `agentic_core/L3_orchestration/exit_eval/v6/{pipeline,x1_gates,x2_matrix,x3_dispositions}.py` |
| R4_SINGLE_ACTION integrated runtime entrypoint (produces sealed_l2_artifact.json + tool_authorization_receipt.json) | `agentic_core/runtime/entrypoints/integrated_single_action_run.py` |
| Spine proof bundle (no-bypass proof construct) | `agentic_core/runtime/artifacts/spine_proof_bundle.py` |
| L5 governance context (authority/policy/capability/sandbox types) | `agentic_core/L5_safety/types/l5_governance_context.py` |

**Fix:** refactor `apps_shared/spine_emission/` into a thin adapter that re-exports `agentic_core` canonical types and delegates `governed_run` to `agentic_core.runtime.entrypoints.integrated_single_action_run.run_integrated_single_action`. No new emitters. No new schemas. Just **wiring**.

Scope impact: the adapter refactor affects all 8 apps that use `apps_shared.spine_emission` (`apps_qna`, `apps_rg`, `apps_eval`, `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_underwriting_ai`). Handled via additive migration (new types alongside, migrate app-by-app, deprecate old shortcut) — apps_rg is the pilot; other apps migrate in a follow-on plan.

## 2. Closure criteria (Definition of Done)

- **D1**. `apps_rg/__main__.py` propagates `run_report.status` → spine so `HUMAN_REVIEW` surfaces as `x3_disposition='X3B_ESCALATE_HITL'` with `failed_stages=['provenance']`. No more `EXIT_OK` ↔ `HUMAN_REVIEW` contradiction.
- **D2**. Root cause of `provenance_report.valid=false / reason=no_master_bullets` identified, documented in ADR, and either fixed or formally accepted with guardian exemption.
- **D3**. apps_rg calls `HITLApprovalGate.evaluate(...)` from `agentic_core/L5_safety/hitl/` when `status='HUMAN_REVIEW'` and emits `router_l5_hitl` ledger event per ADR-050.
- **D4**. OTEL trace tree contains ≥20 spans: spine-level (U0, L1, L0, L3_bypass, L2_E1..E5, Exit_X1..X3, L6_handoff, runtime_gates) **emitted by the agentic_core integrated runtime** + app-level (per HOP-4 section, per candidate, per LLM call) with `prompt_variant`, `model_used`, `composite_score`, `tokens_in`, `tokens_out`, `latency_ms`.
- **D5**. Seven 2026-05-03 calibration decisions formalized (revert+fix-prompt OR accept+ADR). No silent threshold drift.
- **D6**. `_SENIORITY_SKIP`, `DEFAULT_BUZZWORDS`, per-section gate caps live in YAML config.
- **D7**. `certification/apps_evidence_assertions.jsonl` contains `APPS-REQ-RG-*` rows citing **the real agentic_core receipts** (sealed_l2_artifact.json, gate_verdicts bundle, exit_review_packet with X1..X3, spine_proof_bundle) as evidence refs; `tools/cert/apps_e2e/apps_rg_proof_producer.py` exists; fresh signed bundle at `certification/apps/per_app_evidence/apps_rg/`.
- **D8**. Post-run sealing protocol: full pipeline re-run overwrites cleanly OR post-run patches go through re-seal helper updating `artifact_sha256_map`. No orphan files in sealed run dirs.
- **D-ADAPTER**. `apps_shared/spine_emission/` is refactored as a thin adapter: (a) `contracts.py` re-exports agentic_core canonical types (`RouteContractV15`, `L2V4` types, `ExitReviewPacket` from Exit v6, `GateVerdict` from runtime_gates); (b) `context.py::governed_run` delegates to `agentic_core.runtime.entrypoints.integrated_single_action_run.run_integrated_single_action` for `SINGLE_STEP` routes; (c) the thin old types stay as deprecated aliases with `DeprecationWarning` until the other 7 apps migrate (tracked in a follow-on plan). Verified: a fresh apps_rg run produces all of `route_contract.json`, `l2_execution_receipt.json` (with E1..E5), `exit_review_packet.json` (with X1..X3), `gate_verdicts.json`, `spine_proof_bundle.json`, `replay_comparison.json` — all populated with canonical agentic_core content.

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | P1.1, P1.2 | HITL signal propagation (cheap immediate fix — superseded by W6 later) | ~8k | `apps_shared.spine_emission` API stable until W4 refactor; orchestrator exposes `status` in `run_report.json` | 🟡 Draft | D1, D2 met |
| **W2** | P2.1, P2.2, P2.3 | Quality-gate recalibration retrofit (Author-Gate cluster) | ~14k | Local Qwen 1.5B is the binding generator | 🟡 Draft | D5, D6 met |
| **W3** | P3.1, P3.2, P3.3 | OTEL span tree depth — app-level (per-HOP, per-candidate, per-LLM) | ~10k | `governed_run.span()` is the canonical span entry point | 🟡 Draft | D4 (app-level portion) met |
| **W4** | P4.1, P4.2, P4.3, P4.4 | **`apps_shared/spine_emission/` → thin adapter over `agentic_core/runtime/entrypoints/`** | ~18k | `agentic_core.runtime.entrypoints.integrated_single_action_run` + `integrated_safe_reuse_run` are stable public APIs; `route_contract_v15`, `l2_v4_contracts`, Exit v6, runtime_gates, spine_proof_bundle are importable; other 7 apps can keep the deprecated shortcut path until their migration plan lands | 🟡 Draft | D-ADAPTER met; D4 spine-level spans emitted |
| **W5** | P5.1, P5.2, P5.3 | apps_e2e Fort Knox cert arm wiring (evidence refs = real agentic_core receipts from W4) | ~14k | Constitutional §32 arm is canonical; patterned after sibling app's canary `APPS-REQ-001` producer | 🟡 Draft | D7 met |
| **W6** | P6.1, P6.2, P6.3 | Output authenticity & DOCX fidelity + blocking HITL upgrade | ~14k | DOCX template `apps_shared/templates/svp_resume_template.docx` is canonical; `HITLApprovalGate.evaluate()` has stable public API; W4's replay_key available for reclearance audit | 🟡 Draft | D3, D8 met; ATS coverage ≥0.85 |
| **W7** | P7.1 | Retroactive Author-Gate record-keeping for the 2026-05-03 session | ~3k | `.windsurf/state/author_gate_queue/<slug>.jsonl` is the SSOT per §35 | 🟡 Draft | 7 missed decisions on record |

**Total estimated tokens: ~81k across 7 waves.** (Down from v2's ~117k.)

**Wave ordering / dependencies:**
- **W1 → W2 → W3**: natural quality/observability progression. W1 is the cheap immediate fix; W6.P3 supersedes it structurally.
- **W4**: the pivotal wave. Refactors the adapter. W4 output is the precondition for W5 (Fort Knox evidence refs cite real agentic_core receipts).
- **W5**: Fort Knox signoff — gated on W4 because `APPS-REQ-RG-*` evidence needs the real receipts W4 produces.
- **W6**: parallel-runnable with W5 once W4 lands. Blocking HITL (W6.P3) depends on W4's HITLApprovalGate wiring hook.
- **W7**: paperwork, runs any time.

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1.1** | Wire apps_rg `HUMAN_REVIEW` → spine `mark_stage('provenance','fail')` | `apps_rg/__main__.py`, `apps_rg/scripts/narrative_pass.py`, `apps_rg/engines/resume_orchestrator_engine.py` (read-only) | Identifying the callsite where `status` is known AFTER orchestrator finishes but BEFORE `governed_run.__exit__` fires | ~3k | 🟡 Draft |
| **P1.2** | RCA `provenance_report.valid=false / no_master_bullets` | `apps_rg/integrations/verbatim_provenance_gate.py`, master resume JSON loader, `apps_rg/scripts/generate_resume.py` | Real authenticity failure vs misconfigured fixture | ~5k | 🟡 Draft |
| **P2.1** | Emit retroactive Author-Gate packets for 7 calibration decisions | `.windsurf/state/author_gate_queue/apps-rg-runtime-cert-hardening-a3f8c2.jsonl` | Scored A/B/C/D options per decision; preserve rationale | ~4k | 🟡 Draft |
| **P2.2** | Resolve each calibration decision (revert+fix-prompt OR accept+ADR) | `apps_eval/config/rubrics/narrative_judge.yaml`, `apps_rg/integrations/anti_overfitting.py`, `apps_rg/integrations/hops/exec_summary_ensemble.py`, `apps_rg/integrations/hops/_role_bullet_runner.py`, `docs/architecture/adr/ADR-XXX-apps-rg-narrative-judge-calibration.md` (new) | Some thresholds defensibly relaxed for 1.5B model; others snap back. AG decision per-item. | ~7k | 🟡 Draft |
| **P2.3** | Move `_SENIORITY_SKIP` + `DEFAULT_BUZZWORDS` + per-section caps to YAML | `apps_rg/integrations/ats_coverage.py`, `apps_rg/integrations/anti_overfitting.py`, `apps_eval/config/rubrics/narrative_judge.yaml` (extension) or new `apps_rg/config/anti_overfitting_overrides.yaml` | SSOT location — extend narrative_judge.yaml OR new overlay (AG decision). | ~3k | 🟡 Draft |
| **P3.1** | Wrap each HOP-4 section in `gr.span("hop_4a_headline")` etc. | `apps_rg/scripts/narrative_pass.py::_run_narrative_pipeline` | Plumbing `gr` into a function that doesn't receive it | ~3k | 🟡 Draft |
| **P3.2** | Per-candidate child spans with `prompt_variant` + `composite_score` | `apps_rg/integrations/hops/_ensemble_runner.py`, `apps_rg/integrations/hops/_role_bullet_runner.py`, `apps_eval/engines/narrative_judge_scorer.py` | Cardinality ~60 spans; watch trace size | ~4k | 🟡 Draft |
| **P3.3** | Per-LLM-call spans with `model_used`, `tokens_in`, `tokens_out`, `latency_ms` | `apps_rg/integrations/hops/_llm_client.py` | Wrap each generator closure in span context manager | ~3k | 🟡 Draft |
| **P4.1** | **Re-export agentic_core canonical types from `apps_shared/spine_emission/contracts.py`** | `apps_shared/spine_emission/contracts.py`, `apps_shared/spine_emission/__init__.py` | Old `ExecutionForm` / `X3Disposition` / `L2ExecutionReceipt` / `RouteContract` / `ExitReviewPacket` stay as deprecated aliases emitting `DeprecationWarning`. New canonical exports: `RouteContractV15`, `ExecutionFormV15`, `WorkOrderInputs`, `PrepOutput`, `ValidationOutput`, `ExecOutput`, Exit v6 `ExitReviewPacket`, `GateVerdict`, `SpineProofBundle`. `__all__` lists both for one release cycle. | ~5k | 🟡 Draft |
| **P4.2** | **Delegate `governed_run` to `agentic_core.runtime.entrypoints.integrated_single_action_run`** for SINGLE_STEP routes | `apps_shared/spine_emission/context.py` | `governed_run` becomes a thin wrapper: builds an R4_SINGLE_ACTION call-spec, invokes `run_integrated_single_action`, captures its sealed_l2_artifact.json / tool_authorization_receipt.json / exit_review_packet.json / spine_proof_bundle.json / gate_verdicts.json, places them in the app's run_dir. `mark_stage` becomes a shim that feeds into the agentic_core span tree. **apps_rg is the pilot** — other apps keep the deprecated direct path until their migration plan lands. | ~6k | 🟡 Draft |
| **P4.3** | **Wire apps_rg `__main__.py` to use the new adapter path** — map `DETERMINISTIC_PIPELINE` → `SINGLE_STEP` | `apps_rg/__main__.py`, `apps_rg/config/cert_route_registry.yaml` (update execution_form) | `EmissionConfig(expected_execution_form='DETERMINISTIC_PIPELINE')` → `'SINGLE_STEP'`. The HOP pipeline becomes the L2 payload inside `run_integrated_single_action`. | ~4k | 🟡 Draft |
| **P4.4** | **Verify fresh apps_rg run emits canonical receipts** — diff against baseline `20260503_135650/` | `artifacts/apps_rg/runs/<new_ts>/`, verification script `tools/cert/apps_e2e/verify_apps_rg_receipts.py` (new) | Fresh run MUST contain: `route_contract.json` with `execution_form=SINGLE_STEP`, `route_digest`, `hmac_sig`, `policy_hash`, `blueprint_hash`, `replay_key`; `sealed_l2_artifact.json` with E1..E5; `exit_review_packet.json` with X1..X3 canonical; `gate_verdicts.json` with applicable G0x rows; `spine_proof_bundle.json`; ≥20 OTEL spans including spine-level. | ~3k | 🟡 Draft |
| **P5.1** | Define `APPS-REQ-RG-*` evidence assertions — reference the real agentic_core receipts emitted by W4 | `certification/apps_evidence_assertions.jsonl`, `certification/schemas/apps_evidence_assertion.schema.json` (verify shape) | Choose 8–12 claims: `APPS-REQ-RG-001-canonical-route-v15`, `-002-l2-e1-e5-sealed`, `-003-exit-x3-canonical`, `-004-runtime-gates-applicable-subset`, `-005-spine-proof-no-bypass`, `-006-replay-verdict-emitted`, `-007-ats-coverage-floor`, `-008-provenance-bound-to-master` | ~5k | 🟡 Draft |
| **P5.2** | Build `tools/cert/apps_e2e/apps_rg_proof_producer.py` | `tools/cert/apps_e2e/apps_rg_proof_producer.py` (new), `tools/cert/apps_e2e/_shared.py` (existing utility) | Pattern after canary `APPS-REQ-001` producer. Reads W4 receipts from `artifacts/apps_rg/runs/<latest>/`; emits per-claim JSON+sha256. | ~6k | 🟡 Draft |
| **P5.3** | Wire apps_rg into `compile_apps_e2e_signoff.py` + run signoff | `scripts/compile_apps_e2e_signoff.py`, `tools/certification/generate_apps_100pct_runtime_proof.py` | Verify CI gate `T7s.4` passes for apps_rg row | ~3k | 🟡 Draft |
| **P6.1** | Headline ensemble: natural SVP inclusion (revert SENIORITY_SKIP) | `apps_rg/integrations/hops/headline_ensemble.py`, `apps_rg/integrations/ats_coverage.py` | Prompt-engineering fix so ensemble produces headline with seniority token organically | ~4k | 🟡 Draft |
| **P6.2** | ATS coverage 0.73 → ≥0.85 + DOCX re-seal helper | `apps_rg/integrations/hops/exec_summary_ensemble.py`, `apps_rg/integrations/hops/competencies_ensemble.py`, `apps_rg/outputs/docx_exporter.py`, `apps_shared/spine_emission/context.py` (`reseal_artifact()` API) | Missing 7 terms + post-run patch policy (AG decision) | ~6k | 🟡 Draft |
| **P6.3** | **Blocking HITL via `HITLApprovalGate.evaluate(...)`** (supersedes W1.P1 cheap fix) | `apps_rg/__main__.py`, `agentic_core/L5_safety/hitl/__init__.py` (verify public API), `apps_rg/integrations/hitl_bridge.py` (new) | Uses W4's `replay_key` for reclearance audit. CLI fail-closed vs stdin-pause vs async-callback — AG decision. | ~4k | 🟡 Draft |
| **P7.1** | Retroactive AG packets for 7 missed 2026-05-03 calibration decisions | `.windsurf/state/author_gate_queue/apps-rg-runtime-cert-hardening-a3f8c2.jsonl` | Pure record-keeping | ~3k | 🟡 Draft |

## 5. Author-Gate decision points foreseen

Per §35 plan-time seeding.

AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-001 depends_on= title=W1.P2-provenance-rca-disposition (fix vs accept-with-ADR)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-002 depends_on=AG-RG-001 title=W2.P2-naturalness-threshold-final (revert-0.80 / accept-0.65 / two-tier)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-003 depends_on=AG-RG-002 title=W2.P2-composite-threshold-final (revert-0.85 / accept-0.60 / per-section-tier)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-004 depends_on=AG-RG-003 title=W2.P2-mirror-density-floor-final (restore-0.05 / keep-0.0 / make-adaptive)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-005 depends_on=AG-RG-004 title=W2.P2-length-tolerance-final (revert-0.15 / accept-relaxed / model-tier-aware)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-006 depends_on=AG-RG-005 title=W2.P3-config-ssot-location (extend-narrative_judge.yaml / new-apps_rg-overlay)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-007 depends_on= title=W4.P2-adapter-migration-strategy (big-bang / additive-deprecation / apps_rg-only-pilot)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-008 depends_on=AG-RG-007 title=W4.P3-route-family-mapping (SINGLE_STEP-via-R4_SINGLE_ACTION / custom-route-family)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-009 depends_on=AG-RG-008 title=W4.P2-c0-pa-handling-in-integrated-runtime (NOT_REQUIRED-receipt-from-integrated-runtime / treat-company-research-as-grounded)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-010 depends_on= title=W5.P1-apps-req-rg-claim-set (which-8-12-claims-to-ship)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-011 depends_on= title=W6.P2-post-run-patch-policy (forbid / re-seal-helper / per-tool-allowlist)
AG_QUEUE_SEED: plan=apps-rg-runtime-cert-hardening-a3f8c2 id=AG-RG-012 depends_on= title=W6.P3-hitl-blocking-behavior (cli-stdin-pause / fail-closed / async-callback)

## 6. Gap Register

| ID | Gap | Surfaced from | Resolution wave |
|----|-----|---------------|-----------------|
| G1 | EXIT_OK ↔ HUMAN_REVIEW contradiction in receipts | `run_report.json` vs `exit_review_packet.json` | W1 (symptom) + W4 (structural — Exit v6 pipeline emits canonical X3) |
| G2 | Provenance gate failure (`no_master_bullets`) goes silent at runtime | `run_report.provenance_report.valid=false` | W1 |
| G3 | Quality bar drift without Author-Gate (7 thresholds relaxed in one session) | Session edit history 2026-05-03 | W2, W7 |
| G4 | Hard-coded calibration constants (SENIORITY_SKIP, DEFAULT_BUZZWORDS) | `ats_coverage.py:167`, `anti_overfitting.py:DEFAULTS` | W2.P3 |
| G5 | OTEL trace too shallow (3 spans, no spine-level) | `otel_runtime_trace.json::span_count=3` | W3 (app-level) + W4 (spine-level emerges from integrated_single_action_run) |
| G6 | apps_e2e Fort Knox arm not invoked for apps_rg | `certification/apps_evidence_assertions.jsonl` grep | W5 |
| G7 | apps_rg HITL is advisory JSON field, not blocking gate | `resume_orchestrator_engine.py:374` vs `agentic_core/L5_safety/hitl/` | W6.P3 |
| G8 | Post-run patches produce orphan unsealed artifacts | `Amit_Ayer_Resume_fixed.docx` not in `artifact_sha256_map` | W6.P2 |
| G9 | Headline ensemble can't naturally include "SVP" | Session ats_coverage fix 2026-05-03 | W6.P1 |
| G10 | ATS organic coverage stuck at 0.73 (7 missing terms) | `run_report.jd_keyword_coverage.coverage=0.7308` | W6.P2 |
| **G11–G19 (consolidated)** | `apps_shared/spine_emission/` bypasses agentic_core — emits its own thin pydantic envelopes instead of delegating to canonical runtime entrypoints. Symptoms: non-canonical `execution_form`, missing route/L2/Exit/gate/replay/no-bypass fields, thin OTEL trace. | Cross-check of `apps_shared/spine_emission/*.py` (zero `agentic_core` imports) vs `agentic_core/runtime/entrypoints/integrated_single_action_run.py` (exists, produces canonical receipts). | **W4 (adapter refactor)** |

## 7. Out of scope (explicit non-goals)

- Migrating the OTHER 7 apps (`apps_qna`, `apps_eval`, `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_underwriting_ai`) off the deprecated `apps_shared.spine_emission` direct path. Those migrations get a follow-on plan that patterns after apps_rg's W4 here.
- Promoting apps_rg to `MANAGED_WORKFLOW`. W4 maps apps_rg to `SINGLE_STEP` / `R4_SINGLE_ACTION` which is the correct canonical form for a deterministic HOP pipeline.
- Building out L5 registries (authority/policy/blueprint/capability/sandbox) if they don't exist. If W4.P4 verification finds registry stubs, the receipts carry `STUB_PENDING_REGISTRY` refs — DEGRADED but signed. Separate plan builds registries.
- Switching local generator from Qwen 1.5B. Calibration (W2) produces thresholds matched to the current generator.
- Replacing python-docx with pandoc/LaTeX.
- Adding resume sections beyond the 8 in the SVP template.
- Multi-target-company batch runs.

## 8. Risks

- **R1**: W4 integrated-runtime delegation may surface that apps_rg's deterministic HOP pipeline doesn't fit cleanly into R4_SINGLE_ACTION's bounded-packet shape (pipeline has internal retries in HOP-4 ensembles). Mitigation: if fit is bad, fall back to `integrated_safe_reuse_run` OR emit a minimal R4_SINGLE_ACTION envelope that wraps the existing pipeline as a single deterministic L2 payload.
- **R2**: W4 may surface that `run_integrated_single_action` requires a `cap::deterministic_compute` capability token that doesn't exist for apps_rg. Mitigation: use the development surrogate in `TOOL_REGISTRY_RECORDS` or register a new apps_rg tool_id.
- **R3**: W2 Author-Gate decisions may keep all 7 relaxations (1.5B model's natural output range). W6 output-quality work becomes more important to compensate.
- **R4**: W6.P3 blocking HITL may break non-interactive CLI. Need fail-closed mode when no human available (AG decision).
- **R5**: W4 adapter refactor may break the other 7 apps if the deprecated aliases aren't wire-compatible. Mitigation: keep the old pydantic types as `DeprecationWarning` aliases for one full release cycle; all 8 apps' tests run in CI before cutover.
- **R6**: OTEL trace depth (W3 + W4 spine spans) may exceed collector batch limits. Bound trace size; sample at candidate level if needed.

## 9. Execution preconditions

Before starting Wave 1:
- [x] Plan registered in Notion Plans DB (page `35527693-f55c-81ad-92cc-d2cc1737b517`)
- [ ] `python tools/windsurf/wave_execution_state.py start --plan apps-rg-runtime-cert-hardening-a3f8c2` at W1 kickoff
- [ ] Local Qwen vLLM container running and healthy (preflight from this session's fail-fast fix)
- [ ] `artifacts/apps_rg/runs/20260503_135650/` retained as baseline for W4.P4 diff comparison

Before starting Wave 4 (adapter refactor):
- [ ] Verify `agentic_core.runtime.entrypoints.integrated_single_action_run.run_integrated_single_action` signature — public API
- [ ] Verify `agentic_core.L0_routing.types.route_contract_v15` — importable from apps_shared
- [ ] Verify `agentic_core.L2_execution.types.l2_v4_contracts` — importable
- [ ] All 8 apps' existing tests green before cutover (baseline)

Before starting Wave 5 (Fort Knox signoff):
- [ ] W4 D-ADAPTER verified: fresh apps_rg run produces canonical receipts (route+L2+Exit+gates+proof-bundle)

## 10. References

- **Constitutional rules**: §6 (Author-Gate), §32 (Fort Knox two arms), §35 (AG queue drain), §36 (plan registration), §25 (MCP serialization)
- **ADRs**: ADR-023 (HITL routing), ADR-050 (intelligence ledger family), ADR-070 (L5 guardrail family), ADR-080 (Phase D runtime cert)
- **Skills**: `author-gate-packet-builder`, `fortknox-evidence`, `boundary-enforcement`, `operational-gates`
- **Reference docs**: `docs/reference/00C_Runtime_Gates_Current_Run_Mesh/`, `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v15.md`, `docs/reference/04_L2_Execute/04_L2_Execute_v4.md`, `docs/reference/05_Exit_Evaluation_and_Control/05.5_Exit_Aggregation_and_X3_Disposition.md`
- **This-session forensics**:
  - `artifacts/apps_rg/runs/20260503_135650/` — baseline live run (12 of 13 hard-blocker gaps verified against actual files 2026-05-03)
  - `apps_shared/spine_emission/*.py` — verified ZERO imports of `agentic_core` (grep 2026-05-03)
  - `agentic_core/L0_routing/types/route_contract_v15.py`, `agentic_core/L2_execution/types/l2_v4_contracts.py`, `agentic_core/L5_safety/runtime_gates/g01..g29_*.py`, `agentic_core/runtime/entrypoints/integrated_single_action_run.py` — verified canonical infrastructure already exists (2026-05-03)
- **Architectural insight (v3 correction)**: The 9 "spine-contract gaps" (G11–G19 in v2) are NOT missing agentic_core capability — they are one wiring gap: `apps_shared/spine_emission/` is a parallel shortcut. v3 plan replaces 3 new-infrastructure waves (~40k tokens) with one adapter-refactor wave (~18k tokens).
