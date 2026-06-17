# Plan: exec-summary-rc-structural-repair-f4a8c2

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: In Progress
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: none
LAST_UPDATED: 2026-05-27
NOTION_PAGE_ID: 36d27693-f55c-8131-b67c-fc0aa960d9dc

PLAN_CREATED: slug=exec-summary-rc-structural-repair-f4a8c2 path=.claude/plans/exec-summary-rc-structural-repair-f4a8c2.md status=Not Started

---

## Objective

Fix the **structural root causes** behind `executive_summary` X3_REVIEW_JUDGE_SOFT_FAIL, not
symptom patches (text prohibitions). Four mechanical flaws identified from artifact evidence:

| Root Cause | Evidence | Symptom |
|---|---|---|
| **RC-A** | E0 `exec_summary_pos_svp_it_strategy_001` S1 = "...regulatory lineage, and **commercialization**..."; model copies verbatim | S1 thesis-body gap: "commercialization" uncovered in S2-S6 |
| **RC-B** | `fact_quant_hpc_003.preferred_c0_display_text` = "FSA-chartered quantitative foundation, built through..." — noun phrase + participial, NO main verb | S4 grammatical fragment; Gemini scores 2.0 |
| **RC-C** | `fact_engineering_platform_002` claim text = "Built and applied software dependency graph..." — past-tense active; when assigned to S6 position | S6 backward-looking tool description; "thin_S6_forward_synthesis" |
| **RC-D** | No inter-sentence connective tissue required; each S2-S6 maps 1:1 to one fact | Achievement stack; judges flag "no through-line" |

Evidence artifacts:
- `x1d_anthropic_claude_provider_parse_result_20260527_175950_959.json`: Claude 3.4, THESIS_BODY_GAP
- `x1d_gemini_pro_provider_parse_result_20260527_175907_104.json`: Gemini 2.0, S4 fragment + S6 recap
- `claim_ledger.json`: S6 = `fact_engineering_platform_002` = "Built and applied..."
- `claim_proof_split_policy.py:91-106`: `preferred_c0_display_text` = noun phrase fragment

---

## Parent Plan Chain

- `exec-summary-anthropic-surgical-regen-f3c8d2` → COMPLETE
- `exec-summary-brown-gap-hardening-b9e4c1` → COMPLETE
- `exec-summary-bro-svp-rca-e3a1f2` → COMPLETE (W1-W3 certified; W4 partial — deferred)
- **`exec-summary-rc-structural-repair-f4a8c2`** → this plan

---

## Wave Plan

### W1 — Fix E0 example S1 (RC-A)

**File:** `apps_rg/prompt_assembly/examples/executive_summary_examples.yaml`

Replace S1 of `exec_summary_pos_svp_it_strategy_001` from:
```
Enterprise technology leader who unifies governed data platforms, regulatory lineage,
and commercialization into one IT strategy and innovation agenda for decentralized
regulated enterprises.
```
To framing that uses "IT governance and digital innovation agenda" — no "commercialization"
thread unless it is ONLY present via a conditional annotation.

The model pattern-matches the example sentence structure directly, overriding annotation
prose constraints. Removing "commercialization" from the example S1 eliminates the source
of the contamination at root.

**Success:** No new Brown SVP run S1 contains "commercialization" unless `fact_engineering_platform_001` or `fact_engineering_platform_002` carries a commercial outcome.

---

### W2 — Fix fact_quant_hpc_003 fragment + add X2 gate (RC-B)

**Files:**
- `apps_rg/fact_inventory/claim_proof_split_policy.py` — fix `preferred_c0_display_text`
- `apps_rg/runtime/validators/executive_summary_x2.py` — new gate `check_exec_summary_no_sentence_fragment`
- `apps_rg/runtime/sections/executive_summary_x2_x1d_contract.py` — register gate ID
- `apps_rg/runtime/sections/executive_summary_synthesis_monotonic.py` — add to monotonic set

**W2a:** Change `preferred_c0_display_text` for `fact_quant_hpc_003` from noun phrase to
a complete SVO sentence: "Quantitative rigor established through FSA-chartered actuarial
work in capital modeling and portfolio stress analytics underpins regulated-risk delivery."

**W2b:** New gate `x2_exec_summary_no_sentence_fragment` checks each of the 6 sentences in
`resume_display_text` contains at least one finite verb (via regex: present/past tense verb
not in a non-main clause). Hard fail on fragment.

**Success:** S4 fragment no longer passes X2; `preferred_c0_display_text` is a complete sentence.

---

### W3 — Add forward projection display text for fact_engineering_platform_002 (RC-C)

**File:** `apps_rg/fact_inventory/claim_proof_split_policy.py`

Add `forward_projection_preferred_c0_display_text` for `fact_engineering_platform_002`:
```
"Software dependency graph intelligence enables accelerated legacy-system analysis,
exposes architecture chains, and improves transformation visibility across enterprise complexity."
```

Update `format_selected_facts_for_c0` (or equivalent) to prefer
`forward_projection_preferred_c0_display_text` when the fact is assigned to S6 position.

This changes the fact's C0 injection text from backward "Built and applied..." to forward
"enables...exposes...improves..." — making S6 structurally forward-pointing at source.

**Success:** S6 display text for the dependency graph fact reads with present-tense enabling
verbs, not past-tense application description.

---

### W4 — Connective tissue requirement in scratch template (RC-D)

**File:** `apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml`

Add explicit connective tissue rule to generation workflow:

> Each of S2–S5 MUST open with a thesis-referent connector that binds it to the prior
> sentence or the S1 thesis thread. Approved connectors: "Through [X]," "Building on
> that [X]," "That [X] discipline," "Against that [X] foundation." S2 opening with a
> bare proper noun or achievement verb (e.g. "Scaled ML...", "Directed large-scale...")
> is FORBIDDEN — it reads as an achievement bullet, not a synthesized executive arc.

**Success:** S3 no longer opens with bare "Scaled ML engineering organization...";
S4 no longer starts with the fragment; S5 connects to prior sentence context.

---

### W5 — Unit tests

**File:** `tests/unit/apps_rg/test_exec_summary_structural_repair_f4a8c2.py`

Tests:
1. `test_e0_example_s1_no_commercialization` — assert `exec_summary_pos_svp_it_strategy_001` S1 does not contain "commercialization"
2. `test_quant_hpc_003_preferred_display_has_main_verb` — assert `preferred_c0_display_text` for `fact_quant_hpc_003` passes fragment gate
3. `test_fragment_gate_detects_noun_phrase_fragment` — assert gate returns False for "FSA-chartered quantitative foundation, built through..."
4. `test_fragment_gate_passes_complete_sentences` — assert gate returns True for 6 complete sentences
5. `test_engineering_platform_002_forward_projection_present` — assert forward projection display text has present-tense enabling verb
6. `test_forward_projection_display_text_no_past_tense_opener` — assert "Built" / "Applied" not in S6 projection text
7. `test_connective_tissue_instruction_in_scratch_template` — assert template contains "thesis-referent connector"

---

### W6 — Brown SVP proof run

Command:
```
cd "c:\Git\Agentic-Workflow-FRESH" && python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md
```

Target: X3_ALLOW (exit 0). Accept PARTIAL if X3_REVIEW with X2 PASS + all judges ≥ 3.8 and no fragment finding.

---

## DEFERRED_SCOPE

`DEFERRED_SCOPE: plan=exec-summary-rc-structural-repair-f4a8c2 reason="Composition plan target_picture field contains 'commercialization' from briefing synthesis — structural fix requires changing how composition plan derives target_picture from briefing keywords. Large blast radius across composition plan builder." P-Band=P3`

`DEFERRED_SCOPE: plan=exec-summary-rc-structural-repair-f4a8c2 reason="Achievement stack RC-D fully addressed only with a claim_ledger inter-sentence dependency constraint (each ledger row references prior row's thesis thread). Requires claim_ledger schema change." P-Band=P3`
