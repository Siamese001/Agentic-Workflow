# L2 / Qwen prompt trace RCA — Claude failures (`exec_summary_20260525_002352`)

**Run:** [exec_summary_20260525_002352](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352)  
**Parent:** [exec_summary_cert_loop_debug_rca_20260525.md](exec_summary_cert_loop_debug_rca_20260525.md)

---

## Trace chain (generation only)

```text
apps_rg/__main__.py --section executive_summary
  → executive_summary_lane.py
      → build_executive_summary_composition_plan()     # C0 brushstrokes + six_sentence_arc
      → compile_executive_summary_prompt()           # PA: template + U0 + composition block
      → call_qwen_vllm(messages=compiled_prompt)     # L2 author
      → normalize + X2 + judges
```

| Stage | SSOT file | Artifact |
|-------|-----------|----------|
| Template I0/S0/E0 | [executive_summary.generate_scratch_v1.yaml](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) | slots in compiled prompt |
| PA compile | [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py) | [compiled_prompt.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/compiled_prompt.txt) |
| Composition | [executive_summary_composition.py](../../apps_rg/runtime/sections/executive_summary_composition.py) | [executive_summary_composition_plan.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/executive_summary_composition_plan.json) |
| SVP arc SSOT | [executive_summary_synthesis_contract.py](../../apps_rg/runtime/sections/executive_summary_synthesis_contract.py) | injected in U0 + composition_plan |
| Qwen call | [section_qwen_slice.py](../../apps_rg/runtime/providers/section_qwen_slice.py) | [provider_request.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/provider_request.json), [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/provider_response.json) |
| Output | — | [resume_display_text.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/resume_display_text.txt), [claim_ledger.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/claim_ledger.json) |

**Qwen:** `Qwen/Qwen2.5-32B-Instruct-AWQ`, `temperature=0.45`, single **system** message (~13k tokens), `max_tokens=2048`.

---

## Sentence ↔ claim_ledger ↔ brushstroke (what L2 actually wrote)

| # | `resume_display_text` (abridged) | `claim_ledger` facts | Planned arc (U0) | Claude dimension hit |
|---|----------------------------------|----------------------|------------------|----------------------|
| S1 | Technology strategy executive… platform… **$22M / 20% / 8→28** | `fact_engineering_platform_001` (+ metrics from 006/002 in prose) | B1 thesis only | executive_signal (overloaded opener) |
| S2 | **Building on that direction**, Basel/CCAR… 40% | `fact_governance_003` | B2 platform_arc | synthesis (sequential glue) |
| S3 | **Monolithic** risk… HPC… 40% | `fact_quant_hpc_001` | B2 scale_operating_model | synthesis |
| S4 | **Advanced quantitative**… **AWS and Databricks certifications** | `fact_certs_001`, `fact_quant_hpc_003` | B4 commercial — **no cert labels** | synthesis + **violates I0 credential_policy** |
| S5 | **These efforts culminate**… measurable business outcomes | 001 + 003 recycle | B4 enterprise_capstone | synthesis + ats_alignment |
| S6 | (same sentence as S5 in 6-sentence split) | — | forward-looking capstone | synthesis |

**Pattern:** Qwen treated **one brushstroke / one fact cluster per sentence** (`Building on` / `Monolithic` / `Advanced` / `culminate`) despite I0 `anti-inventory` and E0 `exec_summary_pos_svp_it_strategy_001` showing **woven** six-sentence arc.

---

## Prompt said X — model did Y

### 1. Integrated arc (I0 + U0 + composition_plan)

**Prompt (multiple slots):**

- I0 `north_star_synthesis_contract`: weave causal arc, anti-inventory S3–S5, no checklist.
- I0 `sentence_arc_contract` + U0 `six_sentence_arc`: S3 connective scale/innovation; S6 forward capstone, no thin recap.
- `STRATEGY_EXECUTIVE_SYNTHESIS` in jd_block: EA/interop/innovation emphasis; S6 forward-looking.
- E0 `exec_summary_pos_svp_it_strategy_001`: six-sentence **integrated** SVP example.

**L2 output:** Chronological **achievement stack** with transitional openers (`Building on`, `Monolithic`, `Advanced`, `culminate`).

**Failure link:** `executive_signal`, `synthesis_quality` (Claude codes: `achievement_inventory_*`, `sequential_recap_*`, `generic_closing_sentence`).

---

### 2. No credential dump (I0 + S5 arc + X2 gate)

**Prompt:**

- I0 `credential_policy_v1` + `composition_heuristics`: do not mention AWS/Databricks/FSA/cert inventories in `resume_display_text`.
- S5 arc: no cert/AWS/FSA labels.
- E0 `exec_summary_neg_credential_dump_001`.

**L2 output (S4):** `…supported by AWS and Databricks certifications` citing `fact_certs_001`.

**Failure link:** Direct **prompt contradiction** — X2 `x2_exec_summary_no_credential_dump` still **passed** (likely implied-credibility / single-clause interpretation). Claude still penalizes prose quality.

**L2 cause:** C0 lists `fact_certs_001` in **B4_business_role_fit** `required_fact_ids`; brushstroke goal = “credibility outcomes.” Qwen satisfies brushstroke coverage by **naming** certs.

```text
composition_plan B4: required_fact_ids = [fact_certs_001, fact_quant_hpc_001, fact_quant_hpc_003]
C0 EVIDENCE_FACTS: fact_certs_001: Holds AWS Certified ML Engineer...
I0: Do not mention certifications ... in resume_display_text   ← conflict
```

---

### 3. ATS / Brown EA · interoperability · post-merger (JD + briefing)

**Prompt:**

- JD_TEXT + BRIEFING (capped): federated architecture, Accession integration, API-first ecosystem, innovation incubation.
- `SVP_JD_EMPHASIS_THEMES`: federated/post-merger, EA governance, innovation incubation.
- S3 guidance: “federated architecture” as **connective prose** (targeting vocabulary).

**Proof pool (C0):** No fact_id for brokerage, federated EA, post-merger integration, or interoperability — only platform/governance/quant/certs/scale.

**GRAPH_TARGETING_CAPSULE** (in compiled prompt): pillars skew **GTM presales** (`p2 gtm_*`), not EA/interop facts.

**L2 output:** Generic regulated-enterprise / platform language; no substantive Accession/interop/incubation weave.

**Failure link:** `ats_alignment_without_keyword_stuffing` — `weak_alignment_to_ea_interoperability_innovation_themes`. **Not fixable by prompt wording alone** without proof facts or accepting JD-shaped **emphasis** without substance (Claude wants more than surface AI/platform terms).

---

### 4. S1 thesis vs metrics (arc B1)

**Prompt:** S1 = thesis only; S5 = one metric clause.

**L2 output:** S1 bundles platform + **$22M / 20% margin / 8→28** (`fact_engineering_platform_006`, `fact_exec_002`).

**Failure link:** Reads as **inventory lead-in**; weakens executive_signal before S2 “Building on.”

**L2 cause:** B1 `required_fact_ids` includes `fact_engineering_platform_006` (heavy metrics); Qwen front-loads commercial proof.

---

### 5. Mechanism / outcome framing in C0

**C0 lines:**

- `fact_engineering_platform_001`: long mechanism list in fact text + `OUTCOME_FRAMING_REQUIRED` / `max_mechanism_terms=2`.
- Qwen S1 compresses to “operationalizing governed agentic AI platforms…” but S2–S4 still read as **separate wins**.

**Failure link:** Competes with I0 `anti-stacking` / `max two mechanism terms` — model defaults to **fact order**, not E0 gold narrative.

---

## Regen path (judge → Qwen) — why L2 did not self-correct

| Step | Artifact | What happened |
|------|----------|----------------|
| Trigger | `judge_remediation_trigger.json` | `solitary_severe_soft_fail` (Claude only); regen enabled |
| Regen prompt | Same thread + `build_judge_remediation_user_message()` | Adds `DIMENSION_VERDICTS` + synthesis/jd_emphasis lines from Claude findings |
| Cycles 1–2 | `judge_remediation_cycles.json` | Regen draft **failed X2** (`first_person`, `inferred_bridge`, `source_sensitive_phrases`) → **reverted** |
| Cycle 3 | same | `accepted: true`, `all_judges_pass: false` |

**Trace-back:** Regen **did** surface Claude’s dimension failures to Qwen, but **committed text stayed** initial generation; regen drafts could not stay X2-green while applying ATS/synthesis fixes.

---

## Root causes at L2 (ranked)

| # | Cause | Layer |
|---|--------|--------|
| 1 | **Brushstroke-per-sentence execution** — Qwen maps B1→S1, B2→S2–S3, B3→S4, B4→S5–S6 sequentially | L2 behavior vs I0/E0 |
| 2 | **B4 + `fact_certs_001` in C0** conflicts with credential_policy / S5 arc | Composition + C0 selection |
| 3 | **Metrics on 006 in B1** inflate S1 | `bind_facts_to_brushstrokes` / fact classification |
| 4 | **JD/briefing EA/interop themes without proof facts** — ATS gap is structural | C0 pool + targeting law |
| 5 | **GRAPH_TARGETING_CAPSULE GTM-heavy** — weak steer toward Brown briefing themes | [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py) product_patch |
| 6 | **Regen reverted on X2** — judge hints never shipped | [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) regen revert |

---

## Smallest L2-facing fixes

1. **Composition:** Move `fact_certs_001` out of required B4 display binding (implied credibility only per I0); put 006 metrics in S5 brushstroke only, not B1.
2. **PA / U0:** Add hard rule: “Do not use Building on / Monolithic / Advanced / These efforts culminate as sentence openers; follow E0 `exec_summary_pos_svp_it_strategy_001` sentence shape exactly.”
3. **C0:** Add or select one **interop/EA-adjacent** allowed fact (or explicit `gap_notes` + S3 targeting-only clause template) so ATS alignment is evidence-backed not hallucinated.
4. **Regen:** Fix post-regen X2 revert so Claude-targeted `DIMENSION_VERDICTS` can land without `first_person` / bridge violations.

---

## Files to inspect in Cursor

1. [compiled_prompt.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/compiled_prompt.txt) — full Qwen system prompt  
2. [executive_summary_composition_plan.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/executive_summary_composition_plan.json) — brushstroke → fact pressure  
3. [claim_ledger.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/claim_ledger.json) — sentence/fact mapping  
4. [x1d_dimension_matrix.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/x1d_dimension_matrix.json) — Claude vs OpenAI dimension split  
