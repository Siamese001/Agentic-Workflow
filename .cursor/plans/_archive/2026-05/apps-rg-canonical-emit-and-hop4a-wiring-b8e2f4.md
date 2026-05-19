# apps_rg Canonical Emit + HOP-4A Wiring + Headline Architecture

- **Plan slug**: `apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4`
- **Parent plan**: `apps-rg-deferred-activation-w8-a7f4d9` (Completed 2026-05-03)
- **Grandparent plan**: `apps-rg-runtime-cert-hardening-a3f8c2` (Completed 2026-05-03)
- **Tier**: T3 (cross-layer — L2 runtime emit + L0 pipeline wiring + architectural decision)
- **Status**: Completed (2026-05-03)
- **Authored from**: W10/P6.1 live investigation findings 2026-05-03
- **Investigation source**: `.cursor/state/apps-rg-w10-p61-investigation-findings.md`

## 1. Goal

Close the three architectural gaps surfaced by running `main_canonical()` and inspecting run artifacts. These are implementation gaps, not deferrals — the W4-W6 scaffold established the boundary; this plan lands the actual emitter, the missing pipeline HOP, and resolves the static-vs-dynamic headline question.

## 2. Gaps Discovered in W10/P6.1 Live Run

| Gap | Evidence | Severity |
|-----|----------|----------|
| **G1: Canonical receipt emitter stub** | `apps_shared/spine_emission/adapter.py:308` — `_emit_receipts()` is debug-log only | HIGH — blocks all 8 Fort Knox APPS-REQ-RG-* PASS claims |
| **G2: HOP-4A-HEADLINE not wired** | Module `apps_rg/integrations/hops/headline_ensemble.py` exists; absent from `run_report.checkpoints` | MEDIUM — LLM ensemble is dead code |
| **G3: Static owner.headline architectural decision** | `apps_shared/data/master_resume.json` contains byte-identical headline across 20+ runs; no adaptation per target role | LOW — design question, not a bug |

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| **W1** | P1.1, P1.2, P1.3 | Canonical receipt emitter — implement `_emit_receipts()` canonical path | ~18k | 🟡 Draft |
| **W2** | P2.1, P2.2 | HOP-4A-HEADLINE wiring into `generate_resume.main()` | ~8k | 🟡 Draft |
| **W3** | P3.1 | Author-Gate: static vs dynamic owner.headline architecture decision | ~4k | 🟡 Draft |
| **W4** | P4.1, P4.2 | End-to-end live verification — re-run `main_canonical()`, confirm 8/8 PASS proof producer, HITL fail-closed trip | ~6k | 🟡 Draft |

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1.1** | Implement `AdapterGovernedRun._emit_receipts()` canonical path | `apps_shared/spine_emission/adapter.py` | Need to produce 8 canonical receipts using `agentic_core.runtime.entrypoints.integrated_single_action_run` semantics | ~8k | 🟡 |
| **P1.2** | Wire `set_run_dir()` during adapter init so HITL bridge gets populated `run_dir` | `apps_shared/spine_emission/adapter.py`, `apps_rg/__main__.py` | Currently `gr.run_dir=None` in `main_canonical()` → AG-RG-012 fail-closed inert | ~5k | 🟡 |
| **P1.3** | Write tests asserting 8 receipts emitted for `prefer_canonical=True` runs | `tests/_apps_contract/test_w1_canonical_emit.py` (new) | Must test against fixture run_dir not live LLM | ~5k | 🟡 |
| **P2.1** | Insert HOP-4A-HEADLINE call into `apps_rg/scripts/generate_resume.py` main sequence | `apps_rg/scripts/generate_resume.py`, possibly `apps_rg/reasoning/resume_orchestrator.py` | Must place after HOP-2.5-JD-FACETS (has facets) and before HOP-5-ATS (consumes headline) | ~5k | 🟡 |
| **P2.2** | Route HOP-4A output to `executive_summary` (NOT owner.headline — see W3 decision) | `apps_rg/scripts/generate_resume.py`, possibly output assembler | Needs decision from W3.P1 first | ~3k | 🟡 |
| **P3.1** | Author-Gate AG-RG-013: static vs dynamic `owner.headline` | ADR under `docs/architecture/adr/` | Options: (A) keep static brand, (B) LLM-generate per target, (C) hybrid with `owner.headline_variant` map | ~4k | 🟡 |
| **P4.1** | Live `main_canonical()` run with all three gaps closed | (runtime only) | Produces artifacts in `artifacts/apps_rg/runs/<ts>/` with all 8 receipts | ~3k | 🟡 |
| **P4.2** | Run `apps_rg_proof_producer.py`; target ≥6/8 PASS | `tools/cert/apps_e2e/apps_rg_proof_producer.py` (runtime only) | PASS threshold: route_contract, l2_execution, exit_review, gate_verdicts required; others best-effort | ~3k | 🟡 |

## 5. Dependencies

- **W2 depends on W3.P1** — HOP-4A-HEADLINE routing target depends on the static-vs-dynamic decision
- **W4 depends on W1, W2, W3** — live verification requires all gaps closed
- **W1 is independent** — canonical emit can land before HOP-4A decision

## 6. Author-Gate Seeds

```
AG_QUEUE_SEED: plan=apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4 id=AG-RG-013 depends_on= title=static vs dynamic owner.headline architecture
AG_QUEUE_SEED: plan=apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4 id=AG-RG-014 depends_on=AG-RG-013 title=HOP-4A-HEADLINE target field (owner.headline vs executive_summary vs both)
```

## 7. Closure Criteria

- [ ] G1: `_emit_receipts()` canonical path emits all 8 receipt files; tested via fixture
- [ ] G2: HOP-4A-HEADLINE appears in `run_report.checkpoints`; headline reflects target_role tokens
- [ ] G3: ADR authored, AG-RG-013 and AG-RG-014 answered
- [ ] W4: Live run produces ≥6/8 PASS from proof producer
- [ ] HITL bridge trips fail-closed when `status=HUMAN_REVIEW` (AG-RG-012 end-to-end)
- [ ] Zero regression on `tests/_apps_contract/test_w{3,4,5,6}_*.py` (19 tests)
- [ ] Zero regression on `tests/unit/apps_rg/` (38 tests)

## 8. Non-Goals

- Not migrating other 7 apps (apps_qna, apps_lic, apps_rfp, apps_exec, apps_research, apps_underwriting_ai, apps_eval) to canonical emit — follow-on plan
- Not changing `agentic_core.runtime.entrypoints` internals — consume as-is
- Not writing real LLM judge implementations (NO_UNIMPL_JUDGES backlog) — separate plan
- Not resolving `provenance_report.reason=no_master_bullets` — pre-existing, orthogonal

## 9. Success Signal

**Single command golden path:**
```bash
python -c "from apps_rg.__main__ import main_canonical; main_canonical()" \
    --target-company Blend360 --target-role "SVP, Agentic Transformation"
# then
python tools/cert/apps_e2e/apps_rg_proof_producer.py \
    --run-dir artifacts/apps_rg/runs/<ts> \
    --out-dir artifacts/certification/apps_rg_proofs
# expect: PASS ≥6, NOT_VERIFIED ≤2
```

And the generated resume's headline-bearing field (per W3 decision) contains `SVP` + `Agentic Transformation` tokens organically.

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `agentic_core.runtime.entrypoints.integrated_single_action_run` API drift | Medium | High | Pin to current contract in P1.1; add import-smoke test |
| HOP-4A insertion breaks HOP-5-ATS coverage scoring | Medium | Medium | P2.1 runs existing ATS coverage assertions before merge |
| W3 decision is A (keep static) — P2.2 becomes no-op | High | Low | Plan budget already accounts; P2.2 early-exit clean |
| Live run flaky due to LLM nondeterminism | Low | Medium | W4.P2 threshold is ≥6/8, not 8/8 |
