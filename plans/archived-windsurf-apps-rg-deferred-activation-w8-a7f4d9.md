---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-deferred-activation-w8-a7f4d9.md'
original_relative_path: 'apps-rg-deferred-activation-w8-a7f4d9.md'
source_sha256: 4bdf8e9574938626e07fd9d944cbc482a8d8fcdfb07047901803a642b3615144
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Deferred Activation & Follow-On Work

- **Plan slug**: `apps-rg-deferred-activation-w8-a7f4d9`
- **Parent plan**: `apps-rg-runtime-cert-hardening-a3f8c2` (W1-W7 completed 2026-05-03)
- **Tier**: T2 (activation of skeletons + deferred Author-Gate decisions)
- **Status**: Completed
- **Authored from**: W6 completion checkpoint; AG-RG-011/012 pending; P6.1 deferred.

## 1. Goal

Activate the W3-W6 skeleton implementations by resolving pending Author-Gate decisions and executing deferred scope that requires live LLM runs or operator environment configuration.

### Deferred from parent plan

| ID | Source | Description | Blocker |
|----|--------|-------------|---------|
| AG-RG-011 | W6.P2 | Post-run patch policy (forbid / re-seal-helper / per-tool-allowlist) | User decision pending |
| AG-RG-012 | W6.P3 | HITL blocking behavior (cli-stdin-pause / fail-closed / async-callback) | User decision pending |
| P6.1 | W6 | Headline ensemble SVP inclusion (revert SENIORITY_SKIP) | Live LLM runs |

### New scope (emerged from W4-W6 implementation)

- **Live integration test**: Run `python -m apps_rg --target-company "TestCorp" --target-role "Test Role"` via `main_canonical()` entrypoint to verify V15 RouteContract emission
- **Proof producer activation**: After live run, verify `apps_rg_proof_producer.py` generates PASS assertions for APPS-REQ-RG-001..008
- **Fort Knox signoff**: Run `scripts/compile_apps_e2e_signoff.py` with apps_rg evidence

## 2. Closure criteria

- [ ] **D1.** AG-RG-011 decided and `reseal_artifact()` policy activated (or CI gate enforcing forbid)
- [ ] **D2.** AG-RG-012 decided and `hitl_bridge.evaluate_hitl()` blocking behavior wired to `apps_rg/__main__.py`
- [ ] **D3.** P6.1 live run produces headline with organic seniority token (no SENIORITY_SKIP)
- [ ] **D4.** Live `main_canonical()` run emits all 8 canonical receipts (route_contract.json, l2_execution_receipt.json, exit_review_packet.json, gate_verdicts.json, spine_proof_bundle.json, replay_comparison.json, ats_coverage_report.json, provenance_report.json)
- [ ] **D5.** Proof producer reports ≥6 of 8 PASS (baseline for iterative improvement)
- [ ] **D6.** Notion parent plan `apps-rg-runtime-cert-hardening-a3f8c2` marked Completed

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| **W8** | P8.1, P8.2 | Author-Gate decision execution (AG-RG-011, AG-RG-012) | ~4k | 🟡 Draft |
| **W9** | P9.1 | P6.1 headline ensemble live run & prompt iteration | ~6k | 🟡 Draft |
| **W10** | P10.1, P10.2 | Live integration run + proof producer verification | ~5k | 🟡 Draft |

## 4. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens |
|----------|-------|-------|-------------|-------------|
| **P8.1** | Execute AG-RG-011 decision | `apps_shared/spine_emission/reseal.py` policy activation + CI gate if forbid chosen | Requires user selection | ~2k |
| **P8.2** | Execute AG-RG-012 decision | `apps_rg/__main__.py` HITL blocking wiring + environment check | Requires user selection | ~2k |
| **P9.1** | Headline ensemble SVP inclusion | `apps_rg/integrations/hops/headline_ensemble.py` prompt engineering | Live LLM iteration | ~6k |
| **P10.1** | Live `main_canonical()` run | Execute apps_rg via new entrypoint, capture all 8 receipts | Runtime debugging | ~3k |
| **P10.2** | Proof producer verification | Run `apps_rg_proof_producer.py`, verify PASS count, fix gaps | Receipt schema alignment | ~2k |

## 5. Files to modify (from W1-W7 skeletons)

- `apps_rg/__main__.py` - Wire `evaluate_hitl()` blocking behavior per AG-RG-012
- `apps_shared/spine_emission/reseal.py` - Activate policy per AG-RG-011
- `apps_rg/integrations/hops/headline_ensemble.py` - Remove SENIORITY_SKIP, iterate prompt
- `certification/apps_evidence_assertions.jsonl` - Append APPS-REQ-RG-* rows after live run

## 6. Dependencies

- Parent plan W1-W7 completion (skeletons exist)
- User decisions on AG-RG-011, AG-RG-012
- Live LLM environment (local Qwen 1.5B or API key for remote)

## 7. Non-goals

- No new schema definitions (use existing v15, v4, Exit v6)
- No new runtime gates (use existing G01-G29)
- No changes to other 7 apps (apps_rg-only pilot per AG-RG-007)
- No Fort Knox compiler changes (use existing `compile_apps_e2e_signoff.py`)

## 8. Risk register

| Risk | Mitigation |
|------|------------|
| Live run fails to emit canonical receipts | Debug W4 adapter wiring; fallback to legacy `main()` |
| Headline ensemble iteration exceeds token budget | Cap at 3 prompt variants; document best-effort |
| AG decisions delayed | Plan can park; skeletons are backward-compatible |

## 9. Author-Gate queue (inherited)

Pending from parent plan:
- `AG-RG-011`: Post-run patch policy — transferred to this plan
- `AG-RG-012`: HITL blocking behavior — transferred to this plan

New seeds:
```
AG_QUEUE_SEED: plan=apps-rg-deferred-activation-w8-a7f4d9 id=AG-RG-DEF-001 depends_on= title=P8.1-reseal-policy-activation
AG_QUEUE_SEED: plan=apps-rg-deferred-activation-w8-a7f4d9 id=AG-RG-DEF-002 depends_on= title=P8.2-hitl-blocking-behavior-activation
AG_QUEUE_SEED: plan=apps-rg-deferred-activation-w8-a7f4d9 id=AG-RG-DEF-003 depends_on= title=P9.1-seniority-skip-removal-strategy
```
