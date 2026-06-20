---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-runtime-gate-catalog-c4d7e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-runtime-gate-catalog-c4d7e1.md'
source_sha256: 85b3b6d8894b7423cdb54347b4d7aa9fd3bfa8cc0c7f8eda7bcfe0e3eda6659b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-runtime-gate-catalog-c4d7e1
plan_type: refactor
---

# Register apps_rg Resume-Generation Gates into the Fused agentic_core RuntimeGateEngine

Register 30 resume-generation gates and online judge outputs into the unified agentic_core RuntimeGateEngine, closing the structural gap where PER-CAND candidate verdicts were not enforced before POST-ENS artifact mutation. This is NOT a second app-local gate pipeline — apps_rg contributes a gate pack; agentic_core executes and enforces the gate pipeline.

---

## Context (SCQA)

**Situation**: apps_rg generates resumes via a multi-hop narrative pipeline. The `narrative_judge_scorer` provides PER-CAND scoring, ensemble selects a winner, and the exec_summary RCA exposed a critical structural defect: a 73-vs-122 word under-length candidate had `accepted=False` from the PER-CAND gate, but `winner.text` was written to `resume_data` anyway because POST-ENS acceptance/write admission was missing.

**Complication**: The current architecture allows apps_rg to write directly to `resume_data` without centralized gate authority. This creates a parallel enforcement risk: app-specific gates may drift from core gate semantics, bypasses may proliferate, and write-boundary violations may leak into exported resumes. The existing pattern of app-local `post_ens_guard.py` files repeats authority rather than delegating it.

**Question**: How do we close the write-boundary gap while ensuring apps_rg does NOT own a separate runtime gate authority layer, and all gate execution flows through the agentic_core RuntimeGateEngine?

**Answer**: Establish a **fused runtime gate pipeline**:
1. **agentic_core owns** runtime gate authority, GateVerdict schema, GateBundle aggregation, write admission, fail-closed semantics, receipts, observability, and Exit handoff
2. **apps_rg owns** resume-specific gate definitions, thresholds, source mappings, online judge rubrics, ATS/voice/credential/export rules, and domain config
3. **No direct write rule**: `resume_data` mutation requires `WriteAdmissionReceipt.writeable=true` from agentic_core
4. **Candidate inertness law**: PER-CAND outputs are candidate artifacts only; rejected candidates never mutate writeable state
5. **Online judges** run inside runtime gates but do NOT authorize writes directly — RuntimeGateEngine normalizes JudgeVerdict into GateBundle

---

## Ownership Model

| Concern | Owner | Location |
|---|---|---|
| Runtime gate authority | agentic_core | `agentic_core/runtime_gates/` |
| GateVerdict / GateBundle schemas | agentic_core | `agentic_core/runtime_gates/definitions.py` |
| WriteAdmissionReceipt | agentic_core | `agentic_core/runtime_gates/write_admission.py` |
| Write admission guard (winner acceptance) | agentic_core | `agentic_core/runtime_gates/builtins/candidate_acceptance_guard.py` |
| Non-bypassable core gates | agentic_core | `agentic_core/runtime_gates/builtins/` |
| RuntimeGateEngine entrypoint | agentic_core | `agentic_core/runtime_gates/engine.py` |
| apps_rg gate pack (definitions, thresholds) | apps_rg | `apps_rg/integrations/gates/` |
| apps_rg online judge configs | apps_rg | `apps_rg/config/domain_contract/` |
| Resume-specific gate implementations | apps_rg | `apps_rg/integrations/gates/*_resume_gates.py` |
| Domain contracts (GateDefinition dataclass) | agentic_core | `agentic_core/L4_state/contracts/app_domain.py` |
| Harness parity gate | ops_scripts/ci | `ops_scripts/ci/check_app_domain_harness_parity.py` |

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/integrations/hops/_ensemble_runner.py` | ensemble selection, winner acceptance | ✅ Verified |
| `apps_rg/scripts/narrative_pass.py` | where winner writes happen, needs POST-ENS guard | ✅ Verified |
| `apps_rg/integrations/length_budget.py` | LengthBudget.fits() for gates | ✅ Verified |
| `apps_rg/integrations/hops/narrative_judge_scorer.py` | scoring patterns to harden | 🔲 TO READ |
| `apps_rg/__main__.py` | cross_company_contamination pattern | ✅ Verified |
| ADG: agentic_core runtime_gates module | blast radius, existing abstractions | 🔲 ADG Query |

---

## Wave Structure (Reordered)

| Wave | Metric | Scope | Status |
|---|---|---|---|
| Wave 0 — Fused Runtime Gate Authority Foundation | 6 core contracts, 1 engine entrypoint | GateVerdict, GateBundle, WriteAdmissionReceipt, RuntimeGateEngine, apps_rg adapter | 🔲 TODO |
| Wave 1 — P0 Write-Boundary Fix | 3 gates, structural fix | POST-ENS write admission guard, length_parity strict, re_roll loop | 🔲 TODO |
| Wave 2 — Online Judge Contract Binding | 4 contracts, 1 adapter | JudgeVerdict schema, runtime binding, normalization to GateBundle | 🔲 TODO |
| Wave 3 — Input/Replay Integrity & Anti-Contamination | 3 gates | prompt_assembly_sha, master_resume_sha_pinned, cross_company_contamination | 🔲 TODO |
| Wave 4 — Anti-Fabrication & Credential Integrity | 4 gates | provenance_required, figure_citation, tenure_accuracy, degree_certification | 🔲 TODO |
| Wave 5 — Resume Domain PER-CAND Gates | 6 gates | length, quantified outcomes, target company, forbidden filler, sentence, archetype | 🔲 TODO |
| Wave 6 — POST-NARR Coherence & ATS | 5 gates | keyword coverage, claim uniqueness, cross-section consistency, bullet count, role chronology | 🔲 TODO |
| Wave 7 — PRE-EXPORT Artifact Gate | 1 gate | docx_render_no_orphan | 🔲 TODO |
| Wave 8 — CI / ADG / RUNBOOK Integration | 3 deliverables | Gate registration, harness parity, documentation | 🔲 TODO |

**Total: ~40K tokens across 9 waves**

---

## Out Of Scope

- **LLM-self-judge passes** — existing heuristic scoring sufficient; second LLM pass adds latency + nondeterminism
- **Reading-grade-level gates** — too brittle, varies by domain vocabulary
- **Sentiment analysis** — resumes are intentionally upbeat; gates fire without signal
- **Offline judge calibration, drift analysis, false positive/negative analysis** — belongs in separate L6 companion plan: `apps-rg-judge-reliability-and-calibration`
- **Judge rubric redesign or threshold tuning** — L6 observability work, not runtime gate authority
- **Human-labeled holdout scoring** — evaluation harness work, not runtime enforcement
- **apps_rg CLI wizard changes** — plan focuses on pipeline gates, not UX
- **DOCX renderer rewrite** — gate validates output, doesn't change renderer
- **New LLM-judge implementations** — runtime gates normalize existing judge outputs only

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W0.P1 | Core contracts: GateDefinition, GateVerdict, JudgeVerdict | `agentic_core/runtime_gates/definitions.py` | GAP-1: no unified verdict schema | ~4K | 🔲 TODO |
| W0.P2 | GateBundle aggregation | `agentic_core/runtime_gates/gate_bundle.py` | GAP-2: no bundle abstraction | ~3K | 🔲 TODO |
| W0.P3 | WriteAdmissionReceipt & WriteAdmissionGuard | `agentic_core/runtime_gates/write_admission.py` | GAP-3: no write authority | ~4K | 🔲 TODO |
| W0.P4 | RuntimeGateEngine entrypoint | `agentic_core/runtime_gates/engine.py` | GAP-4: no fused execution path | ~5K | 🔲 TODO |
| W0.P5 | apps_rg gate registry adapter | `apps_rg/integrations/gates/registry.py` | GAP-5: app-to-core binding | ~3K | 🔲 TODO |
| W0.P6 | Candidate inertness law enforcement | `narrative_pass.py` refactor | GAP-6: direct write pattern | ~4K | 🔲 TODO |
| W1.P1 | Candidate acceptance guard (core-owned) | `agentic_core/runtime_gates/builtins/candidate_acceptance_guard.py` | GAP-7: write-before-abort race | ~3K | 🔲 TODO |
| W1.P2 | length_parity_strict for all sections | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-8: tolerance 0.45→0.15 | ~3K | 🔲 TODO |
| W1.P3 | length_re_roll_loop generalization | `_ensemble_runner.py` | GAP-9: retry only for exec_summary | ~2K | 🔲 TODO |
| W2.P1 | JudgeVerdict schema & runtime contract | `agentic_core/runtime_gates/definitions.py` | GAP-10: no judge integration | ~3K | 🔲 TODO |
| W2.P2 | Online judge normalization adapter | `agentic_core/runtime_gates/judge_adapter.py` | GAP-11: judge→gate mapping | ~3K | 🔲 TODO |
| W2.P3 | Judge evidence attachment | `GateBundle.evidence_refs` | GAP-12: missing provenance | ~2K | 🔲 TODO |
| W2.P4 | Malformed judge verdict handling | `RuntimeGateEngine` | GAP-13: bypass risk | ~2K | 🔲 TODO |
| W3.P1 | prompt_assembly_sha | `agentic_core/runtime_gates/builtins/prompt_sha_gate.py` | GAP-14: replay/debuggability | ~2K | 🔲 TODO |
| W3.P2 | master_resume_sha_pinned | `agentic_core/runtime_gates/builtins/input_snapshot_gate.py` | GAP-15: concurrent edit detection | ~2K | 🔲 TODO |
| W3.P3 | cross_company_contamination (core gate) | `agentic_core/runtime_gates/builtins/contamination_gate.py` | GAP-16: reframe to core | ~2K | 🔲 TODO |
| W4.P1 | provenance_required | `apps_rg/integrations/gates/post_ens_resume_gates.py` | GAP-17: flag not validated | ~3K | 🔲 TODO |
| W4.P2 | figure_citation_verification | `apps_rg/integrations/gates/post_ens_resume_gates.py` | GAP-18: numeric claims unchecked | ~3K | 🔲 TODO |
| W4.P3 | tenure_accuracy | `apps_rg/integrations/gates/post_ens_resume_gates.py` | GAP-19: prose vs computed mismatch | ~2K | 🔲 TODO |
| W4.P4 | degree_certification_unchanged | `apps_rg/integrations/gates/pre_export_resume_gates.py` | GAP-20: credential hallucination | ~2K | 🔲 TODO |
| W5.P1 | length_parity_strict (PER-CAND enforcement) | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-21: drift prevention | ~2K | 🔲 TODO |
| W5.P2 | quantified_outcome_count | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-22: content density | ~2K | 🔲 TODO |
| W5.P3 | target_company_name_absence | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-23: anti-flattery | ~1K | 🔲 TODO |
| W5.P4 | forbidden_filler_strict | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-24: soft→hard gate | ~2K | 🔲 TODO |
| W5.P5 | sentence gates (count, max_length) | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-25: ATS readability | ~2K | 🔲 TODO |
| W5.P6 | archetype_lead | `apps_rg/integrations/gates/per_cand_resume_gates.py` | GAP-26: drift from archetype | ~1K | 🔲 TODO |
| W6.P1 | jd_keyword_coverage_min | `apps_rg/integrations/gates/post_narr_resume_gates.py` | GAP-27: reported not gated | ~2K | 🔲 TODO |
| W6.P2 | claim_uniqueness | `apps_rg/integrations/gates/post_narr_resume_gates.py` | GAP-28: recycled numbers | ~2K | 🔲 TODO |
| W6.P3 | cross_section_consistency | `apps_rg/integrations/gates/post_narr_resume_gates.py` | GAP-29: 3-different-people | ~3K | 🔲 TODO |
| W6.P4 | bullet_count_per_role | `apps_rg/integrations/gates/post_narr_resume_gates.py` | GAP-30: sparse bullets | ~1K | 🔲 TODO |
| W6.P5 | role_chronology | `apps_rg/integrations/gates/post_narr_resume_gates.py` | GAP-31: date violations | ~2K | 🔲 TODO |
| W7.P1 | docx_render_no_orphan | `apps_rg/integrations/gates/pre_export_resume_gates.py` | GAP-32: empty sections leak | ~2K | 🔲 TODO |
| W8.P1 | Gate registration in app_domain | `agentic_core/L4_state/contracts/app_domain.py` | GAP-33: contract parity | ~3K | 🔲 TODO |
| W8.P2 | Harness parity gate extension | `ops_scripts/ci/check_app_domain_harness_parity.py` | GAP-34: CI enforcement | ~2K | 🔲 TODO |
| W8.P3 | RUNBOOK.md update | `apps_rg/RUNBOOK.md` | GAP-35: documentation | ~1K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1 to GAP-35**: See Phase-Level Summary above for all numbered gaps.

**Structural Gap (unnumbered)**: The current `narrative_pass.py` pattern allows direct mutation:
```python
winner = run_ensemble(...)
resume_data["executive_summary"] = winner.text  # ❌ Direct write without gate authority
_abort_if_critical(winner)
```
This must be replaced with the RuntimeGateEngine pattern where `writeable=true` is required.

---

## Proposed File Layout

```
agentic_core/runtime_gates/
  __init__.py
  engine.py                    # RuntimeGateEngine entrypoint
  definitions.py               # GateDefinition, GateVerdict, JudgeVerdict dataclasses
  gate_bundle.py               # GateBundle aggregation
  write_admission.py           # WriteAdmissionReceipt, WriteAdmissionGuard
  receipts.py                  # Receipt emission to outcome ledger
  builtins/
    __init__.py
    candidate_acceptance_guard.py   # Non-bypassable: winner acceptance
    prompt_sha_gate.py              # Non-bypassable: prompt assembly SHA
    input_snapshot_gate.py          # Non-bypassable: master resume SHA
    contamination_gate.py           # Non-bypassable: cross-company
    provenance_contract_gate.py     # Non-bypassable: provenance for quantified claims

apps_rg/integrations/gates/
  __init__.py
  registry.py                  # apps_rg gate pack registration adapter
  per_cand_resume_gates.py     # PER-CAND gates: length, filler, tone, etc.
  post_ens_resume_gates.py     # POST-ENS gates: provenance, citation, tenure
  post_narr_resume_gates.py    # POST-NARR gates: coherence, ATS, uniqueness
  pre_export_resume_gates.py   # PRE-EXPORT gates: credential, orphan check
  online_judges.py             # Online judge runtime binding

apps_rg/config/domain_contract/
  resume_gate_catalog.yaml     # 30-gate catalog with placements, severities
  threshold_profiles.yaml        # Per-profile thresholds (ATS, draft, strict)
  forbidden_terms.yaml           # Buzzword lists
  ats_keyword_policy.yaml        # Keyword coverage rules
  source_mapping.yaml            # Provenance source definitions
```

**Important**: Inspect existing runtime gate/core contracts first. Reuse existing modules where available. Avoid duplicate abstractions.

---

## Online Judge Runtime Contract

Online judges evaluate candidates inside runtime gates but do NOT authorize writes directly. The RuntimeGateEngine normalizes JudgeVerdict into GateVerdict/GateBundle.

### Required JudgeVerdict Fields

| Field | Type | Description |
|---|---|---|
| judge_id | str | Canonical judge identifier (e.g., "narrative_judge_scorer") |
| judge_version | str | Semver of judge implementation |
| rubric_version | str | Version of rubric applied |
| threshold_profile_id | str | Which threshold profile was active |
| gate_id | str | Runtime gate this judge feeds into |
| placement | str | PER-CAND, POST-ENS, POST-NARR, PRE-EXPORT |
| score | float | Normalized score 0.0-1.0 |
| accepted | bool | Candidate passed threshold |
| result | enum | PASS \| FAIL \| WARN \| UNKNOWN \| NOT_APPLICABLE |
| reason_codes | list[str] | Machine-readable failure reasons |
| evidence_refs | list[str] | References to source bullets, spans |
| deterministic_digest | str | Hash of inputs for reproducibility |

### Runtime Rules

1. **Online judges may evaluate candidates inside runtime gates**
2. **Online judges do NOT authorize writes** — only RuntimeGateEngine issues WriteAdmissionReceipt
3. **RuntimeGateEngine normalizes JudgeVerdict into GateVerdict/GateBundle**
4. **accepted=false blocks write for critical gates**
5. **malformed judge verdict blocks write for judge-required critical gates**
6. **missing judge_version/rubric_version/threshold_profile_id blocks write for judge-required critical gates**
7. **judge verdicts must be attached to GateBundle evidence_refs or evaluator_ref**
8. **UNKNOWN is never treated as PASS for critical gates**

### Out of Scope for This Plan

- Judge calibration (human-labeled holdout scoring)
- False positive / false negative analysis
- Judge drift over time detection
- Rubric redesign or threshold tuning
- Spearman correlation tracking

These belong in a separate L6 companion plan: **apps-rg-judge-reliability-and-calibration**.

---

## Execution Plan

### Wave 0 — Fused Runtime Gate Authority Foundation

**W0.P1 — Core contracts: GateDefinition, GateVerdict, JudgeVerdict**

Create `agentic_core/runtime_gates/definitions.py`:
- `GateDefinition`: id, placement, severity, bypassable, dependencies
- `GateVerdict`: gate_id, result (PASS/FAIL/WARN/UNKNOWN), reason, evidence, timestamp
- `JudgeVerdict`: all required fields from Online Judge Runtime Contract
- Enums: `GatePlacement`, `GateSeverity`, `GateResult`

**W0.P2 — GateBundle aggregation**

Create `agentic_core/runtime_gates/gate_bundle.py`:
- `GateBundle` dataclass: aggregates GateVerdicts across placements
- `aggregate()` method: determines overall PASS/FAIL/WARN/UNKNOWN
- `has_critical_failure()` method: true if any non-bypassable gate failed
- `evidence_refs` list for audit trail

**W0.P3 — WriteAdmissionReceipt & WriteAdmissionGuard**

Create `agentic_core/runtime_gates/write_admission.py`:
- `WriteAdmissionReceipt`: writeable (bool), gate_bundle_ref, timestamp, receipts_digest
- `WriteAdmissionGuard.evaluate()`: takes artifact, GateBundle → returns WriteAdmissionReceipt
- Non-bypassable: winner_acceptance_guard logic lives here

**W0.P4 — RuntimeGateEngine entrypoint**

Create `agentic_core/runtime_gates/engine.py`:
- `RuntimeGateEngine` class
- `evaluate(app_id, placement, artifact, context)` → GateBundle
- `register_gate_pack(app_id, gate_definitions, gate_callables)` → binds apps_rg gates
- `normalize_judge_verdict(judge_verdict)` → GateVerdict
- Executes gates in order, aggregates to GateBundle

**W0.P5 — apps_rg gate registry adapter**

Create `apps_rg/integrations/gates/registry.py`:
- `register_apps_rg_gate_pack()` function
- Loads gate definitions from `resume_gate_catalog.yaml`
- Binds gate callables from per_cand/post_ens/post_narr/pre_export modules
- Calls `RuntimeGateEngine.register_gate_pack()`

**W0.P6 — Candidate inertness law enforcement**

Modify `apps_rg/scripts/narrative_pass.py`:
- Replace direct `resume_data[...] = winner.text` pattern
- Insert RuntimeGateEngine.evaluate() before any mutation
- Require WriteAdmissionReceipt.writeable=true
- Emit sealed failure packet on rejection (not partial resume)

**Acceptance (Wave 0)**:
- [ ] Core contracts compile, no circular imports
- [ ] RuntimeGateEngine can register and execute a mock gate pack
- [ ] Unit test: `test_runtime_gate_engine_is_single_gate_execution_path`
- [ ] Unit test: `test_write_admission_guard_rejects_without_bundle`
- [ ] 0 regressions in existing apps_contract tests

---

### Wave 1 — P0 Write-Boundary Fix

**W1.P1 — Candidate acceptance guard (core-owned)**

Create `agentic_core/runtime_gates/builtins/candidate_acceptance_guard.py`:
- Non-bypassable core gate
- Input: artifact (winner), GateBundle
- Logic: if any PER-CAND gate returned FAIL for this artifact → FAIL
- Reason code: `candidate_rejected_by_per_cand_gate`
- This is the winner_acceptance_guard, but core-owned

**W1.P2 — length_parity_strict for all sections**

In `apps_rg/integrations/gates/per_cand_resume_gates.py`:
- Implement `length_parity_strict` gate
- Tolerance: 0.15 (configurable via threshold_profiles)
- Apply to: exec_summary, headline, competencies, role_bullets

**W1.P3 — length_re_roll_loop generalization**

Modify `apps_rg/integrations/hops/_ensemble_runner.py`:
- Extract retry logic to section-agnostic helper
- Config-driven: `critical_sections` list in config
- Max 1 retry per section with reinforced prompt

**Acceptance (Wave 1)**:
- [ ] `test_rejected_winner_never_mutates_resume_data`
- [ ] `test_unknown_verdict_never_mutates_resume_data`
- [ ] `test_write_admission_receipt_required_for_resume_data_mutation`
- [ ] `test_abort_after_gate_failure_does_not_emit_partial_resume`

---

### Wave 2 — Online Judge Contract Binding

**W2.P1 — JudgeVerdict schema & runtime contract**

Extend `agentic_core/runtime_gates/definitions.py`:
- Full JudgeVerdict dataclass with all required fields
- Validation: judge_version, rubric_version, threshold_profile_id required

**W2.P2 — Online judge normalization adapter**

Create `agentic_core/runtime_gates/judge_adapter.py`:
- `normalize_judge_verdict(judge_verdict: JudgeVerdict) -> GateVerdict`
- Maps score/accepted to PASS/FAIL/WARN/UNKNOWN
- Handles malformed verdict → UNKNOWN with reason

**W2.P3 — Judge evidence attachment**

Extend `agentic_core/runtime_gates/gate_bundle.py`:
- `evidence_refs` field: list of source bullet references
- `evaluator_ref`: which judge produced verdict
- Audit trail for provenance

**W2.P4 — Malformed judge verdict handling**

Extend `RuntimeGateEngine`:
- Detect missing required fields (judge_version, rubric_version, threshold_profile)
- Treat as UNKNOWN for critical gates → blocks write
- Log to outcome ledger with `malformed_judge_verdict` reason

**Acceptance (Wave 2)**:
- [ ] `test_judge_verdict_requires_judge_id`
- [ ] `test_judge_verdict_requires_rubric_version`
- [ ] `test_judge_verdict_requires_threshold_profile`
- [ ] `test_accepted_false_maps_to_fail_closed_for_critical_gate`
- [ ] `test_judge_warn_does_not_block_noncritical_gate`
- [ ] `test_malformed_judge_verdict_blocks_write`

---

### Wave 3 — Input/Replay Integrity & Anti-Contamination

**W3.P1 — prompt_assembly_sha**

Create `agentic_core/runtime_gates/builtins/prompt_sha_gate.py`:
- Non-bypassable
- Hash fully assembled prompt after template substitution
- Store in GateBundle evidence_refs

**W3.P2 — master_resume_sha_pinned**

Create `agentic_core/runtime_gates/builtins/input_snapshot_gate.py`:
- Non-bypassable
- Hash master_resume.json at pipeline start
- Abort if changed mid-run

**W3.P3 — cross_company_contamination (reframed as core gate)**

Create `agentic_core/runtime_gates/builtins/contamination_gate.py`:
- Migrate logic from `apps_rg/__main__.py:_assert_artifact_matches_company`
- Non-bypassable core gate
- Validate generated artifacts' `company` field matches `--target-company`

**Acceptance (Wave 3)**:
- [ ] All three gates execute in PRE-LLM or POST-NARR placement
- [ ] Cross-company contamination still detected, now core-enforced

---

### Wave 4 — Anti-Fabrication & Credential Integrity

**W4.P1 — provenance_required**

In `apps_rg/integrations/gates/post_ens_resume_gates.py`:
- Non-bypassable for quantified claims
- Validate `provenance_ok` flag AND `provenance_sources` list
- Sources must resolve to master_resume/JD/brief bullet

**W4.P2 — figure_citation_verification**

In `apps_rg/integrations/gates/post_ens_resume_gates.py`:
- Extract `%`, `$`, `×`, scale patterns
- Fuzzy-match to master_resume text
- Unmatched figures → FAIL with `unverified_claim` reason

**W4.P3 — tenure_accuracy**

In `apps_rg/integrations/gates/post_ens_resume_gates.py`:
- Extract "X+ years" patterns from exec_summary
- Compare to `_compute_years_of_experience(roles)` ±1 year

**W4.P4 — degree_certification_unchanged**

In `apps_rg/integrations/gates/pre_export_resume_gates.py`:
- Byte-level comparison of `education` and `certifications_and_credentials`
- Compare to SHA-pinned master_resume subset
- Any drift → FAIL (non-bypassable)

**Acceptance (Wave 4)**:
- [ ] Fabrication attempt (mocked) correctly rejected
- [ ] Credential drift blocked
- [ ] <50ms per gate performance

---

### Wave 5 — Resume Domain PER-CAND Gates

**W5.P1-W5.P6 — Length, quantified outcomes, anti-flattery, filler, sentences, archetype**

Implement in `apps_rg/integrations/gates/per_cand_resume_gates.py`:
1. `length_parity_strict` (PER-CAND enforcement)
2. `quantified_outcome_count` (≥2 numeric claims)
3. `target_company_name_absence` (anti-flattery)
4. `forbidden_filler_strict` (hardened from soft)
5. `sentence_count_strict` + `sentence_max_length`
6. `archetype_lead` (first sentence contains archetype)

All configurable via `threshold_profiles.yaml`.

---

### Wave 6 — POST-NARR Coherence & ATS

Implement in `apps_rg/integrations/gates/post_narr_resume_gates.py`:
- `jd_keyword_coverage_min` (≥80% JD must-have keywords)
- `claim_uniqueness` (no recycled numbers)
- `cross_section_consistency` (same archetype/tenure/outcomes)
- `bullet_count_per_role` (3-5 bullets)
- `role_chronology` (date-descending, gap detection)

---

### Wave 7 — PRE-EXPORT Artifact Gate

**W7.P1 — docx_render_no_orphan**

In `apps_rg/integrations/gates/pre_export_resume_gates.py`:
- Validate final DOCX has no empty sections
- Search for `{placeholder}`, `null`, `None`
- Reject render if orphans found

---

### Wave 8 — CI / ADG / RUNBOOK Integration

**W8.P1 — Gate registration in app_domain**

In `agentic_core/L4_state/contracts/app_domain.py`:
- Add `GateDefinition` dataclass
- Register all 30 gates with id, placement, severity

**W8.P2 — Harness parity gate extension**

In `ops_scripts/ci/check_app_domain_harness_parity.py`:
- Add `GATE_CATALOG_DEFINED` check
- Add `GATE_IMPLEMENTATION_EXISTS` check
- Advisory by default; fail-closed via env var

**W8.P3 — RUNBOOK.md update**

In `apps_rg/RUNBOOK.md`:
- Add "## Runtime Gate Catalog" section
- Table: Gate ID | Placement | Severity | Config Path
- Link to this plan

**Acceptance (Wave 8)**:
- [ ] All 30 gates registered in contract
- [ ] Harness parity gate passes
- [ ] RUNBOOK.md updated
- [ ] CI passes: `python ops_scripts/ci/run_contract_gates.py`

---

## Rules

### Ownership Discipline
- **agentic_core owns** runtime gate authority, schemas, write admission, non-bypassable core gates
- **apps_rg owns** domain gate definitions, thresholds, resume-specific rules, online judge configs
- **No apps_rg final authority**: apps_rg gates register into RuntimeGateEngine; apps_rg cannot independently authorize writes

### Candidate Inertness Law
- PER-CAND and POST-ENS outputs are **candidate artifacts only**
- Candidate text is **not writeable state**
- `winner.text` must **never** be copied directly into `resume_data`
- `resume_data` mutation is **forbidden** until POST-ENS emits `accepted_artifact=true` AND `WriteAdmissionReceipt.writeable=true`
- Rejected candidates may be logged, but **never** copied into `resume_data`, export payloads, cache, or final artifacts
- Exit receives only **accepted sealed artifacts** or sealed failure/retry/blocked packets

### Severity-Based Enforcement Matrix

| Gate Category | Default Enforcement | Configurable |
|---|---|---|
| Core safety/integrity gates (winner_acceptance, contamination, provenance) | **FAIL_CLOSED** | No |
| Write-boundary gates | **FAIL_CLOSED** | No |
| Provenance/credential/company-contamination | **FAIL_CLOSED** | No |
| Resume quality gates (length, filler, tone) | **WARN** or strict-configurable | Yes |
| ATS optimization gates | **FAIL** (production), **WARN** (draft) | Yes |
| Voice/polish gates | **WARN** unless strict profile | Yes |
| Coherence gates | **WARN** | Yes |

**UNKNOWN is never treated as PASS for critical gates.**

### Non-Bypassable Gates
The following gates are **non-bypassable** in CI and production:
- `candidate_acceptance_guard` (core-owned winner acceptance)
- `prompt_assembly_sha`
- `master_resume_sha_pinned`
- `cross_company_contamination`
- `provenance_required` (for quantified claims)
- `figure_citation_verification` (for numeric claims)
- `degree_certification_unchanged`
- `docx_render_no_orphan` (when placeholders/nulls exist)

### Layer Placement Discipline
- **PER-CAND**: `apps_rg/integrations/gates/per_cand_resume_gates.py`
- **POST-ENS**: `apps_rg/integrations/gates/post_ens_resume_gates.py` + core `candidate_acceptance_guard`
- **POST-NARR**: `apps_rg/integrations/gates/post_narr_resume_gates.py`
- **PRE-LLM**: `agentic_core/runtime_gates/builtins/prompt_sha_gate.py`, `input_snapshot_gate.py`
- **PRE-EXPORT**: `apps_rg/integrations/gates/pre_export_resume_gates.py`

### Reuse Patterns
- `LengthBudget.fits()` for length/sentence gates
- `_assert_artifact_matches_company` pattern migrated to core `contamination_gate`
- `narrative_judge_scorer` feeds JudgeVerdict to RuntimeGateEngine for normalization

### Outcome Ledger Integration
Every gate result emitted to `eval_harness_outcome` ledger per ADR-050.

---

## Success Criteria

- [ ] Wave 0 complete: RuntimeGateEngine, WriteAdmissionReceipt, core contracts operational
- [ ] P0 write-boundary fix: rejected winners never mutate resume_data
- [ ] All non-bypassable gates are core-owned and enforced
- [ ] apps_rg gate pack registers into RuntimeGateEngine; no independent write authority
- [ ] Online judge verdicts normalized through RuntimeGateEngine; no direct write authorization
- [ ] 30 gates cataloged in app_domain contract
- [ ] Zero regressions in existing apps_contract test suite (400+ tests)
- [ ] Harness parity gate reports all gates as `IMPLEMENTED`
- [ ] P0 mutation tests pass (6 tests)
- [ ] Online judge contract tests pass (5 tests)
- [ ] ADG/CI anti-bypass tests pass (3 tests)
- [ ] RUNBOOK.md documents fused gate pipeline for operators
- [ ] Performance: total gate overhead <200ms per resume generation

---

## Implementation Commands

```bash
# Pre-flight verification
python ops_scripts/ci/check_app_domain_harness_parity.py
python ops_scripts/ci/run_contract_gates.py

# Wave 0: Core foundation tests
pytest tests/unit/runtime_gates/test_core_contracts.py -v
pytest tests/unit/runtime_gates/test_engine.py -v
pytest tests/unit/runtime_gates/test_write_admission.py -v

# P0 mutation tests
pytest tests/_apps_contract/test_p0_write_boundary_fix.py -v

# Online judge contract tests
pytest tests/_apps_contract/test_judge_runtime_contract.py -v

# ADG/CI anti-bypass tests
pytest tests/_apps_contract/test_runtime_gate_authority.py -v

# Full suite verification
pytest tests/_apps_contract/ -x --tb=short

# ADG verification (post-implementation)
python tools/generate_full_adg.py
python tools/adg/adg_redis_ingest.py
```

---

## Required Tests

### P0 Mutation Tests (Wave 1 Acceptance)
- `test_rejected_winner_never_mutates_resume_data`
- `test_unknown_verdict_never_mutates_resume_data`
- `test_malformed_judge_verdict_blocks_write`
- `test_missing_gate_bundle_blocks_write`
- `test_write_admission_receipt_required_for_resume_data_mutation`
- `test_abort_after_gate_failure_does_not_emit_partial_resume`

### Online Judge Contract Tests (Wave 2 Acceptance)
- `test_judge_verdict_requires_judge_id`
- `test_judge_verdict_requires_rubric_version`
- `test_judge_verdict_requires_threshold_profile`
- `test_accepted_false_maps_to_fail_closed_for_critical_gate`
- `test_judge_warn_does_not_block_noncritical_gate`

### ADG/CI Anti-Bypass Tests (Wave 0-1)
- `test_no_direct_resume_data_write_without_write_admission_guard`
- `test_apps_rg_gate_registry_has_no_final_authority`
- `test_runtime_gate_engine_is_single_gate_execution_path`

---

## ADG Hardening Rules

**No direct write to resume_data narrative fields** is allowed unless the write path passes through:
1. RuntimeGateEngine
2. GateBundle aggregation
3. WriteAdmissionGuard
4. WriteAdmissionReceipt.writeable=true

**Fields to scan in ADG**:
- `resume_data["executive_summary"]`
- `resume_data["core_competencies"]`
- `resume_data["professional_experience"]`
- Headline / title fields
- Export payload fields derived from generated narrative output

**CI gate**: `ops_scripts/ci/check_resume_data_mutation_paths.py` (new) — validates all resume_data mutations go through WriteAdmissionReceipt.

---

## Code-Shape Guidance for narrative_pass.py

Replace unsafe pattern:
```python
# ❌ BEFORE (unsafe)
winner = run_ensemble(...)
resume_data["executive_summary"] = winner.text
_abort_if_critical(winner)
```

With RuntimeGateEngine pattern:
```python
# ✅ AFTER (fused gate pipeline)
winner = run_ensemble(...)

gate_bundle = runtime_gate_engine.evaluate(
    app_id="apps_rg",
    placement="POST_ENS",
    artifact=winner,
    context=run_context,
)

write_receipt = write_admission_guard.evaluate(
    artifact=winner,
    gate_bundle=gate_bundle,
)

if not write_receipt.writeable:
    return sealed_failure_packet(write_receipt)

accepted = AcceptedArtifact.from_candidate(winner, write_receipt)
resume_data["executive_summary"] = accepted.text
```

**Preserve existing style and imports** — the invariant matters: `resume_data` mutation must be dominated by `WriteAdmissionReceipt.writeable=true`.

---

## Rollback Strategy

If critical regression detected:

1. **Profile-level rollback**: Switch from `production` to `draft` profile in `threshold_profiles.yaml` — quality gates downgrade from FAIL to WARN (no code change)
2. **Gate-level disable**: Set specific gate to `severity: WARN` in `resume_gate_catalog.yaml` (config only)
3. **Code-level rollback**: Revert specific wave commits while keeping RuntimeGateEngine foundation
4. **Full rollback**: Revert to pre-plan commit; resume generation falls back to existing soft-scoring behavior

### Emergency Bypass Policy

- **NO `WINNER_ACCEPTANCE_BYPASS`** — core invariant gates are non-bypassable
- **`GATE_ENFORCEMENT_BYPASS=1`** — local-dev only; does NOT bypass non-bypassable core gates
- Any profile-based downgrade emits `bypass_receipt` to outcome ledger with `downgrade_from=FAIL to=WARN reason=profile_switch`
- Production requires explicit operator action to downgrade; cannot happen via config drift

---

## Acceptance Criteria (Detailed)

| Metric | Target | Verification |
|---|---|---|
| RuntimeGateEngine operational | Core contracts compile, engine executes | Unit tests pass |
| WriteAdmissionReceipt required | 100% of resume_data mutations | ADG scan + CI gate |
| P0 write-boundary fix | 6/6 mutation tests pass | pytest |
| Online judge contract | 5/5 judge tests pass | pytest |
| ADG anti-bypass | 3/3 authority tests pass | pytest |
| Non-bypassable gates | 8/8 core-owned | Code review |
| Total gates cataloged | 30/30 | Contract + harness parity |
| Test coverage | ≥85% new code | pytest --cov |
| Performance overhead | <200ms | cProfile |
| Regression count | 0 | Full apps_contract suite |

---

## Cascade Alignment Checks

- ADG query for `agentic_core/runtime_gates` existing abstractions before W0
- ADG scan for direct `resume_data[...] = ` mutations in apps_rg
- Skill retrieval: `graph-analysis` for dependency tracing, `adg-sqlite` for hotspot analysis
- Author-Gate decisions documented at: gate severity calibration (W0), online judge contract (W2), bypass policy
