---
plan_id: apps-rg-hop4a-authority-and-judging-c3d7e1
plan_type: refactor
---

# apps_rg HOP-4A Authority + Judging Quality

Close two deferred follow-ups from `apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4`: resolve the field-authority conflict between HOP-4A and HOP-4B over `executive_summary` (AG-RG-014), and land a calibrated LLM rubric judge so HOP-4A ensemble results actually clear acceptance.

---

## Context (SCQA)

- **Situation** — AG-RG-013 (resolved 2026-05-03, option C) preserved `owner.headline` as a static brand line. HOP-4A (`headline_ensemble.py`) now runs and persists its output as `headline_candidate.json`. HOP-4B (`exec_summary_ensemble.py`) owns `executive_summary` and writes it unconditionally. Both HOPs operate in the same `narrative_pass.py` pipeline. No LLM rubric judge exists for HOP-4A (`executive_positioning_judge.py` is `IS_STUB=True`).
- **Complication** — AG-RG-014 is open: HOP-4A's winner text is stored as a side-artifact but never surfaces in the rendered resume output. Additionally, in the live run no HOP-4A candidate cleared acceptance — the ensemble judge stub returns `GRADER_UNKNOWN_SENTINEL`, causing every run to fail-closed or skip the acceptance gate silently.
- **Question** — Where does HOP-4A's winner text belong in the rendered resume, and does the judge need to be real before the output is trusted?
- **Answer** — Author-Gate AG-RG-014 to decide field authority (headline_variant field vs executive_summary prefix vs separate section); then implement a real `executive_positioning_judge` rubric scoring HOP-4A winners so the acceptance gate is no longer silently bypassed.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/scripts/narrative_pass.py` lines 219–277 | HOP-4A + HOP-4B wiring and field assignment | ✅ Read |
| `apps_rg/integrations/hops/headline_ensemble.py` | HOP-4A prompt variants and acceptance threshold | 🔲 |
| `apps_rg/integrations/hops/exec_summary_ensemble.py` | HOP-4B field assignment to `executive_summary` | 🔲 |
| `apps_rg/engines/judges/executive_positioning_judge.py` | Current stub — `IS_STUB=True`, `GRADER_UNKNOWN_SENTINEL` | 🔲 |
| `apps_rg/outputs/docx_exporter.py` | Which resume fields get rendered to DOCX | 🔲 |
| `agentic_core/L4_state/contracts/app_domain.py` | `GRADER_TYPE_VOCAB`, `ScoreDimension` schema | 🔲 |
| `tests/_apps_contract/test_w2_hop4a_wiring.py` | Existing wiring contract — regression guard | 🔲 |
| `tests/_apps_contract/test_w2_ag_rg_013.py` | Existing static-preservation contract — regression guard | 🔲 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| **W1** | P1.1, P1.2 | Author-Gate AG-RG-014: field-authority decision + wire HOP-4A output to chosen field | ~10k | 🔲 TODO |
| **W2** | P2.1, P2.2, P2.3 | Implement real `executive_positioning_judge` rubric; land acceptance-gate tests | ~18k | 🔲 TODO |
| **W3** | P3.1, P3.2 | End-to-end live run: HOP-4A winner surfaces in rendered output; judge clears ≥1 candidate | ~6k | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1.1** | Author-Gate AG-RG-014 — HOP-4A field authority | `narrative_pass.py`, ADR | Options: (A) `headline_variant`, (B) `executive_summary` prefix, (C) separate `targeted_headline` field | ~5k | 🔲 TODO |
| **P1.2** | Wire HOP-4A winner to the resolved target field | `apps_rg/scripts/narrative_pass.py`, `apps_rg/outputs/docx_exporter.py` | Must not regress `test_w2_ag_rg_013` static-preservation invariant | ~5k | 🔲 TODO |
| **P2.1** | Implement `executive_positioning_judge` rubric | `apps_rg/engines/judges/executive_positioning_judge.py` | Replace stub; implement `grade()` with real dimension scoring (role_alignment, differentiation, brand_voice) | ~8k | 🔲 TODO |
| **P2.2** | Wire judge into HOP-4A acceptance gate | `apps_rg/integrations/hops/headline_ensemble.py` | Ensure `run_ensemble` invokes `executive_positioning_judge.grade()` and fails HOP-4A on low score | ~5k | 🔲 TODO |
| **P2.3** | Contract tests: judge scoring + acceptance gate | `tests/_apps_contract/test_w2_hop4a_judging.py` (new) | Mock LLM; assert rubric dimensions populated; assert low-score triggers rejection | ~5k | 🔲 TODO |
| **P3.1** | Live run: confirm HOP-4A winner surfaces in rendered output | (runtime only) | Must see targeted headline in DOCX or JSON output | ~3k | 🔲 TODO |
| **P3.2** | Run proof producer; confirm no regression on 8/8 receipts | (runtime only) | `apps_rg_proof_producer.py --run-dir ...` | ~3k | 🔲 TODO |

---

## Gap Register

**GAP-1: HOP-4A winner is a side-artifact only (AG-RG-014 open)**
- `head_res.winner.text` is written to `headline_candidate.json` but never assigned to any `resume_data` field.
- The rendered DOCX and final JSON output never include the role-tailored headline.
- Impact: HOP-4A ensemble is computationally active but functionally invisible in the output artifact.

**GAP-2: `executive_positioning_judge` is a stub**
- `apps_rg/engines/judges/executive_positioning_judge.py` exports `IS_STUB=True` and returns `GRADER_UNKNOWN_SENTINEL`.
- HOP-4A acceptance gate silently bypasses scoring → every ensemble run reports unknown quality.
- Impact: No candidate ever "clears" — the pipeline is running blind.

---

## Execution Plan

### Phase 1 — AG-RG-014 Field Authority Decision + Wiring

**Scope**: Present Author-Gate options, capture decision, wire HOP-4A winner to target field.

**Options for AG-RG-014**:
- **(A) `targeted_headline` field** — new field in `resume_data`; rendered as a separate block above `executive_summary` in DOCX; clean separation from static brand line.
- **(B) Prepend to `executive_summary`** — HOP-4A winner text is prepended to HOP-4B output as a sub-heading; one combined field; minimal DOCX change.
- **(C) `headline_variant` map** — `resume_data["headline_variant"][target_company]` keyed by target; supports multi-company accumulation; most flexible but requires DOCX exporter change.

**Acceptance**: `narrative_pass.py` assigns `head_res.winner.text` to the resolved field; `test_w2_ag_rg_013` still passes (static `owner.headline` unchanged).

### Phase 2 — Real Executive Positioning Judge

**Scope**: Replace stub with functional rubric; wire into ensemble acceptance gate.

**Judge dimensions** (proposed):
- `role_alignment` — does the headline contain target_role tokens? (0.0–1.0)
- `differentiation` — distinct from generic templates? scored by keyword overlap with pain_points.
- `brand_voice` — consistent with `seed_text` (static brand line) tone?

**Acceptance gate**: `run_ensemble` calls `executive_positioning_judge.grade(winner_text, context)` and rejects candidates below `min_score` threshold (configurable, default 0.65).

**Commands**:
```bash
python -m pytest tests/_apps_contract/test_w2_hop4a_judging.py -v
python -m pytest tests/_apps_contract/ -v --tb=short
```

**Acceptance**: `IS_STUB=False`; `grade()` returns populated `ScoreDimension` list; mock test asserts low-score rejection; zero regressions on prior contract tests.

### Phase 3 — Live Verification

**Scope**: Confirm end-to-end rendering and proof producer.

**Commands**:
```bash
python -c "from apps_rg.__main__ import main_canonical; main_canonical()" \
    --target-company Blend360 --target-role "SVP, Agentic Transformation"
python tools/cert/apps_e2e/apps_rg_proof_producer.py \
    --run-dir artifacts/apps_rg/runs/<ts> \
    --out-dir artifacts/certification/apps_rg_proofs
```

**Acceptance**: HOP-4A winner text appears in rendered DOCX/JSON under resolved field; proof producer ≥6/8 PASS; no new FAIL receipts vs baseline.

---

## Out Of Scope

- Other HOP judges (HOP-4B exec summary judge, HOP-4C competencies judge) — separate plan
- Multi-company `headline_variant` accumulation beyond the single active run
- Migrating other apps to the `executive_positioning_judge` pattern
- HOP-4A prompt tuning or new prompt variants — quality improvement separate from wiring

---

## Author-Gate Seeds

```
AG_QUEUE_SEED: plan=apps-rg-hop4a-authority-and-judging-c3d7e1 id=AG-RG-014 depends_on= title=HOP-4A winner field authority (targeted_headline vs exec_summary prefix vs headline_variant map)
```

---

## Success Criteria

- [ ] AG-RG-014 answered: HOP-4A winner field resolved and wired
- [ ] `head_res.winner.text` appears in rendered DOCX/JSON under the resolved field
- [ ] `executive_positioning_judge.IS_STUB == False`
- [ ] `grade()` returns populated dimensions; mock test passes
- [ ] Low-score HOP-4A candidate is rejected, not silently bypassed
- [ ] `test_w2_ag_rg_013` passes (static `owner.headline` invariant preserved)
- [ ] `test_w2_hop4a_wiring` passes (regression)
- [ ] All `tests/_apps_contract/` pass (zero regressions)
- [ ] Proof producer ≥6/8 PASS on live run

---

## Dependencies

- **P1.2 depends on P1.1** — wiring target field requires AG-RG-014 decision
- **P2.2 depends on P2.1** — wiring judge requires judge implementation
- **W3 depends on W1, W2** — live verification requires all gaps closed

---

## Parent Plan

`apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4` (Completed 2026-05-03) — this plan closes the two deferred follow-ups seeded as AG-RG-014 and HOP-4A judging quality.
