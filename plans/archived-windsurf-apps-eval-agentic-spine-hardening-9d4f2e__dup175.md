---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-eval-agentic-spine-hardening-9d4f2e__dup175.md'
original_relative_path: 'apps-eval-agentic-spine-hardening-9d4f2e__dup175.md'
source_sha256: 2bb236256032902623b31de83b1cf4b54d6d3aaf1149f51ee35c6c9114028fc6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_eval Agentic Spine Hardening

> Zero-loss overwrite plan to harden apps_eval alignment to canonical agentic_core spine.

---

## Status

**Status**: Not Started  
**Plan File**: `apps-eval-agentic-spine-hardening-9d4f2e`  
**Target**: apps_eval Evaluation Lab  
**Pattern Source**: apps_exec/AGENTIC_SPINE.md, apps_rg/AGENTIC_SPINE.md, constitutional §22-30

---

## Objective

Closes spine hardening gap; aligns apps_eval to canonical agentic_core R4_DETERMINISTIC_EVAL_RUN. Enforces:
- Pure shim `__main__.py` (no business logic)
- Prompt Assembly judge standard (CompiledPromptArtifact)
- LocalEvalEvidenceContract (FEC producer)
- Cache-safety (exact + semantic)
- Exit exact-X3 standard (X3D/X3E only)

---

## Non-Goals (Explicitly Out of Scope)

- **No C0 retrieval** — scenarios are preloaded, not vector-retrieved
- **No L3 DAG** — execution stays within L2 E3 scenario loop
- **No static DAG terms** — evaluation is dynamic per-scenario
- **No direct L4** — all state changes via Exit → UWG → L4
- **No scenario mutation** — scenarios are read-only evaluation fixtures
- **No runtime HITL** — evaluation is deterministic/automated

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| P0 | P0.1 | Entrypoint purity audit — __main__.py shim verification | 2,000 | Current __main__.py exists | Not Started | Pure shim confirmed; no business logic |
| P1.5 | P1.5.1-P1.5.5 | Prompt Assembly templates — 5 canonical judge templates | 4,000 | PA system from apps_exec/AGENTIC_SPINE.md | Not Started | 5 templates + PromptBOM registry |
| W1 | W1.1-W1.3 | __main__.py pure shim — arg parse, L1 plan, L0 route binding | 3,000 | Entrypoint audit complete | Not Started | Shim delegates 100% to L1/L0 |
| W2 | W2.1-W2.4 | Local evidence contract — FEC producer + resolve_fec() | 4,000 | apps_qna FEC pattern exists | Not Started | FEC produces schema_version=1.0 |
| W3 | W3.1-W3.5 | L2 E1-E5 stages — PREP, VALID, EXEC, HEAL, SEAL | 8,000 | L2 execution scaffolding exists | Not Started | All 5 stages sealed-packet compliant |
| W4 | W4.1-W4.3 | Exit v6 wiring — X1, X2, exact X3 disposition | 4,000 | Exit v6 pipeline from apps_eval_doctrine | Not Started | X3D/X3E only; no X3B HITL |
| W5 | W5.1-W5.2 | Acceptance sweep — 84 governance tests + negative controls | 6,000 | All waves above complete | Not Started | 84 tests pass; negative controls fail closed |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Entrypoint purity audit | `__main__.py` | Current __main__ may have logic bleed | 2,000 | Not Started |
| P1.5.1 | PromptBOM registry scaffold | `prompt_assembly/registry.py` | PA module doesn't exist | 1,000 | Not Started |
| P1.5.2 | Judge template — correctness | `templates/judge_correctness.txt` | Assertion fencing standard | 600 | Not Started |
| P1.5.3 | Judge template — determinism | `templates/judge_determinism.txt` | Hash comparison prompt | 600 | Not Started |
| P1.5.4 | Judge template — governance | `templates/judge_governance.txt` | Policy compliance prompt | 600 | Not Started |
| P1.5.5 | Judge template — latency + richness | `templates/judge_{latency,richness}.txt` | Secondary dims | 1,200 | Not Started |
| W1.1 | Shim arg parse | `__main__.py` | U0 intake binding | 800 | Not Started |
| W1.2 | Shim L1 plan | `__main__.py` | EvalRun spec creation | 1,000 | Not Started |
| W1.3 | Shim L0 route binding | `__main__.py` | Route registry lookup | 1,200 | Not Started |
| W2.1 | FEC producer module | `cert/fec_producer.py` | New file | 1,000 | Not Started |
| W2.2 | FEC cert registration | `cert/__init__.py` | Side-effect registration | 600 | Not Started |
| W2.3 | Local evidence contract | `contracts/local_eval_evidence.py` | New contract class | 1,200 | Not Started |
| W2.4 | Integration wiring | `integrations/eval_ingress.py` | FEC resolution at entry | 1,200 | Not Started |
| W3.1 | E1 PREP stage | `engines/eval_prep.py` | Suite/scenario loading | 1,500 | Not Started |
| W3.2 | E2 VALID stage | `engines/eval_valid.py` | Schema + threshold validation | 1,500 | Not Started |
| W3.3 | E3 EXEC stage | `engines/scenario_runner.py` | Scenario loop sealed packets | 2,000 | Not Started |
| W3.4 | E4 HEAL stage | `engines/eval_heal.py` | Local repair (retry/skip) | 1,500 | Not Started |
| W3.5 | E5 SEAL stage | `engines/eval_seal.py` | Report + scorecard sealing | 1,500 | Not Started |
| W4.1 | Exit X1 checkout | `integrations/exit_adapter.py` | Provenance validation | 1,200 | Not Started |
| W4.2 | Exit X2 aggregation | `integrations/exit_adapter.py` | Gate violations rollup | 1,400 | Not Started |
| W4.3 | Exit X3 disposition | `integrations/exit_adapter.py` | X3D/X3E exact mapping | 1,400 | Not Started |
| W5.1 | Governance test suite | `tests/_apps_eval/governance/` | 84 tests new | 3,500 | Not Started |
| W5.2 | Negative controls | `tests/_apps_eval/negative/` | Fail-closed verification | 2,500 | Not Started |

---

## Gap Register

**GAP-1**: Prompt Assembly system not yet present in apps_eval (pattern from apps_exec).  
**GAP-2**: FEC producer pattern needs replication from apps_qna (per-app cert module).  
**GAP-3**: Exit v6 integration may need adapter layer (eval has no runtime HITL).  
**GAP-4**: 84 governance tests = substantial test surface; may defer partial to follow-up plan.

---

## Deferred Scope (Do Not Implement — Capture for Future Plan)

1. **Real LLM-judge calibration** — Spearman ≥ 0.80 vs human labels (needs holdout corpus)
2. **Production eval-log mining** — PII redaction pipeline for production trace eval
3. **C0 scenario retrieval** — if scenarios ever need vector retrieval (currently preloaded)
4. **L3 DAG adoption** — if eval ever needs orchestration graph (currently R4_SINGLE_ACTION)
5. **Cross-app eval integration** — evaluating apps_* from apps_eval (currently internal agentic_core only)
6. **Eval harness parity gates** — AEH1-style gate for apps_eval itself (meta-evaluation)

---

## Acceptance Criteria

1. **84 governance tests pass** — entrypoint, PA, FEC, L2 stages, Exit wiring
2. **Negative controls fail closed** — 5+ tests verifying graceful degradation
3. **Pure shim verified** — __main__.py under 100 lines, 100% delegation
4. **FEC produces valid contract** — schema_version=1.0, template_only sufficiency
5. **Sealed packet compliance** — all L2 stages emit to E5, Exit produces exactly one X3
6. **Cache safety** — R1A exact hit + R1B semantic hit paths tested
7. **No X3B HITL** — eval remains deterministic, no runtime HITL dispositions

---

## Pattern References

- `apps_exec/AGENTIC_SPINE.md` — Prompt Assembly canonical pattern
- `apps_rg/AGENTIC_SPINE.md` — R4_SINGLE_ACTION deterministic execution
- `agentic_core/L3_orchestration/exit_eval/v6/apps_eval_doctrine.py` — FENCE_POSTS tuple
- `apps_qna/cert/fec_producer.py` — FEC producer replication pattern
- Constitutional §22-30 — Spine enforcement, closed-loop routing, SSOT discipline

---

## Files In Scope

### New Files (to create)
- `apps_eval/__main__.py` (overwrite — pure shim)
- `apps_eval/prompt_assembly/registry.py`
- `apps_eval/prompt_assembly/templates/*.txt` (5 templates)
- `apps_eval/cert/__init__.py`
- `apps_eval/cert/fec_producer.py`
- `apps_eval/contracts/local_eval_evidence.py`
- `apps_eval/engines/eval_prep.py`
- `apps_eval/engines/eval_valid.py`
- `apps_eval/engines/eval_heal.py`
- `apps_eval/engines/eval_seal.py`
- `apps_eval/integrations/eval_ingress.py`
- `apps_eval/integrations/exit_adapter.py`
- `tests/_apps_eval/governance/test_*.py` (21 files, 84 tests)
- `tests/_apps_eval/negative/test_*.py` (5 files, negative controls)

### Modified Files
- `apps_eval/engines/scenario_runner.py` (sealed packet compliance)
- `apps_eval/engines/base_eval_engine.py` (dim_scores standard)
- `apps_eval/config/eval_policies.yaml` (cache strategy annotation)

---

## Next Action

**Current Wave**: P0.1 — Entrypoint purity audit  
Begin by reading current `apps_eval/__main__.py` to assess logic bleed vs pure shim standard.
