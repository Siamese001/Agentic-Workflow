# apps_rg Prompt Assembly — SSOT Gap Analysis

**Generated:** 2026-05-23  
**Scope:** `apps_rg/prompt_assembly/` + W9 section PA compile path (`apps_rg/runtime/sections/*_pa.py`)  
**Machine audit:** [prompt_assembly_ssot_gap_audit.json](../../artifacts/apps_rg/plans/prompt_assembly_ssot_gap_audit.json)  
**Execution plan:** [.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md](../../.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md)  
**Notion (Plans DB):** [apps-rg-pa-ssot-gap-b8e4f1](https://www.notion.so/apps-rg-pa-ssot-gap-b8e4f1-36927693f55c81ffa6c5d48b02e86e43)

---

## Executive summary

Prompt assembly has **strong structural governance** (BOM, registry, compiler, contract tests) but **weak compile-time SSOT binding** between declarative artifacts and what the model actually sees. The highest-impact gap is **dual E0 authority** on executive summary: BOM points at `examples/executive_summary_examples.yaml`, while live compile injects **compressed inline stubs** from the section template. The same **orphaned examples file** pattern affects competencies and unify lanes. Governance tests prove files **exist**; they do not prove **wired equivalence**.

**Gap count (automated, post-close):** 4 · **P0:** 0 · **Remaining:** PA-DUAL-CONTRACT-TREES (accepted)

**Compile proof:** [pa_e0_compile_proof_receipt.json](../../artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json)

---

## Inventory (what exists today)

| Layer | Path | Role |
|-------|------|------|
| BOM | [prompt_bom.yaml](../../apps_rg/prompt_assembly/prompt_bom.yaml) | 8-slot authority model; exec-summary `gold_examples_path` |
| Registry | [prompt_registry.yaml](../../apps_rg/prompt_assembly/prompt_registry.yaml) | Template catalog (E3/E4/E5 + W9 section templates) |
| Templates | [templates/](../../apps_rg/prompt_assembly/templates/) | 24 YAML slot-body packs |
| Examples | [examples/](../../apps_rg/prompt_assembly/examples/) | 3 multishot YAML files (exec, competencies, unify) |
| Section contracts (E3) | [section_contracts/](../../apps_rg/prompt_assembly/section_contracts/) | Legacy section contracts |
| Section contracts (W9) | [section_prompt_contracts/](../../apps_rg/prompt_assembly/section_prompt_contracts/) | Runtime lane contracts + pinned hashes |
| Core law | [pa_core_law_v1.yaml](../../apps_rg/prompt_assembly/pa_core_law_v1.yaml) | Shared PA truth/targeting contracts |
| Compiler | [compiler.py](../../apps_rg/prompt_assembly/compiler.py) | Assembles `PromptAssemblyInput` → artifact |
| Runtime PA | [runtime/sections/*_pa.py](../../apps_rg/runtime/sections/) | Per-lane slot load + `e0_examples=slots.get("E0")` |

**W9 live lanes (7):** executive_summary, headline, competencies, unify_bullets, unify_narrative, ibm_bullets, ibm_narrative

---

## Gap catalog

### G1 — Dual E0 authority (executive_summary) — **P0**

| Authority | Location | What model sees |
|-----------|----------|-----------------|
| A (declared SSOT) | BOM `gold_examples_path` → [executive_summary_examples.yaml](../../apps_rg/prompt_assembly/examples/executive_summary_examples.yaml) | 4–5 sentence dense gold (`after` field) — **not wired** |
| B (live compile) | [executive_summary.generate_scratch_v1.yaml](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) `slot_bodies.E0` | 2–3 sentence stubs for same example IDs |

**Wiring:** [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py) line 469: `e0_examples=slots.get("E0")`. Loader `load_executive_summary_example_after()` exists but is **not** used on compile path.

**Symptom:** S0/I0/U0 say “4 or 5 sentences”; E0 teaches shorter paragraphs; models imitate few-shot shape. X2 validates **output** sentence count, not **prompt** exemplar shape.

**Proof:** Shared IDs with divergent body length: `exec_summary_gold_base_resume_001` — inline 3 sentences vs YAML 4 sentences (measured 2026-05-23).

---

### G2 — Orphaned examples YAML (competencies, unify) — **P1**

| Section | Examples file | Inline E0 in template | Compile wiring |
|---------|---------------|----------------------|----------------|
| competencies | [competencies_examples.yaml](../../apps_rg/prompt_assembly/examples/competencies_examples.yaml) (5 examples) | May live in [competency_selector_v2.pa_slots.yaml](../../apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml) | `competencies_pa.py` → template slots only |
| unify_bullets / unify_narrative | [unify_examples.yaml](../../apps_rg/prompt_assembly/examples/unify_examples.yaml) (5 examples) | Separate per template | `unify_*_pa.py` → template slots only |

W10.5 tests assert examples **parse** and have pos/neg rows; **no test** asserts examples YAML content == compiled E0.

---

### G3 — BOM vs registry E0 requirement mismatch — **P2**

- [prompt_bom.yaml](../../apps_rg/prompt_assembly/prompt_bom.yaml): `E0` in `required_slots`
- [prompt_registry.yaml](../../apps_rg/prompt_assembly/prompt_registry.yaml): all W9 section templates list `E0` under `optional_slots`

Risk: compliance checks against BOM pass structurally while registry allows E0-less compile configs.

---

### G4 — Dual contract trees — **P2**

- `section_contracts/` — referenced by E3 templates in registry
- `section_prompt_contracts/` — referenced by W9 runtime lanes ([pa_lane_refs.yaml](../../tests/_core_contract/fixtures/apps_rg_binding_package/pa_lane_refs.yaml))

Both are active SSOT for overlapping concepts (executive_summary, competencies, unify). Drift risk when editing one tree only.

---

### G5 — Template shell vs section template indirection — **P2**

[executive_summary.contract.yaml](../../apps_rg/prompt_assembly/section_prompt_contracts/executive_summary.contract.yaml):

- `apps_rg_prompt_template_ref` → section YAML (content SSOT)
- `pa_template_ref: strategic_tailor_v1` → compiler shell (slot order wrapper)

Correct by design, but easy to edit shell slots thinking they are narrative SSOT.

---

### G6 — Token budget vs exemplar fidelity — **P2**

- BOM `compilation_constraints.max_total_tokens: 4000`
- [test_exec_summary_prompt_drift_ratchet.py](../../tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py): static slots must stay `< 7500` tokens

Pressure to keep **inline E0 stubs** small conflicts with **full gold** in examples YAML. No policy for “hydrate from YAML with budget trim” vs “duplicate stubs.”

---

### G7 — Output gates ≠ prompt SSOT — **P2**

X2 gates (e.g. `x2_exec_summary_sentence_count_4_5`) validate **model output**. They do not detect **prompt-side** E0/S0 contradiction. Lane can show `x2_all_pass` while compiled prompt still carries weak few-shot shape.

---

### G8 — Stale PA contract doc paths — **P3**

[apps_rg_pa_prompt_contract.md](../guides/apps_rg_pa_prompt_contract.md) references missing files:

- `rg_prompt_profile.yaml`
- `rg_style_profile.yaml`
- `rg_evidence_profile.yaml`

---

### G9 — No cross-lane E0 hydration module — **P2**

Every `*_pa.py` independently does `slots.get("E0")`. No shared `apps_rg/prompt_assembly/e0_hydration.py` (or equivalent) to:

1. Resolve BOM/examples path per section
2. Build `<many_shot_examples>` from YAML SSOT
3. Fail closed on ID/body drift vs template

---

### G10 — Legacy L2 `pa_context_bridge` — **P3**

[pa_context_bridge.py](../../apps_rg/l2_recipe/pa_context_bridge.py) still renders template `slot_bodies.E0` for package-driven L2 — same pattern as section PA. Any E0 fix must cover **both** entry paths.

---

## W9 lane matrix (automated)

| Lane | Examples YAML | Inline E0 IDs | Shared IDs | Dual-authority risk |
|------|---------------|---------------|------------|---------------------|
| executive_summary | Yes (12) | 4 positives | 3 | **Yes (P0)** |
| headline | No | 0 | 0 | No (inline-only) |
| competencies | Yes (5) | 0 on main template | 0 | **Yes (P1)** |
| unify_bullets | Yes (5) | 0 | 0 | **Yes (P1)** |
| unify_narrative | Yes (5) | 0 | 0 | **Yes (P1)** |
| ibm_bullets | No | 0 | 0 | No |
| ibm_narrative | No | 0 | 0 | No |

---

## What governance already catches

| Check | Location | Catches | Misses |
|-------|----------|---------|--------|
| BOM 8-slot presence | [test_apps_rg_pa_governance.py](../../tests/_apps_contract/test_apps_rg_pa_governance.py) | Registry refs, hashes | E0 body wiring |
| W10.5 signal hardening | [test_w10_5_pa_signal_hardening.py](../../tests/_apps_contract/test_w10_5_pa_signal_hardening.py) | YAML exists, pos/neg | Compile hydration |
| Exec summary drift ratchet | [test_exec_summary_prompt_drift_ratchet.py](../../tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py) | X2 IDs not in I0/R0, token budget | E0 vs S0 sentence parity |
| Examples gold metadata | [test_exec_summary_pa_compiled_prompt.py](../../tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py) | Gold row in YAML file | Inline vs YAML body |
| Prompt template authority X2 | [executive_summary_x2.py](../../apps_rg/runtime/validators/executive_summary_x2.py) | Artifact template ref | E0 content |
| Core G10 | [g10_prompt_assembly.py](../../agentic_core/L5_safety/runtime_gates/g10_prompt_assembly.py) | Slot order, budget | App exemplar SSOT |

**agentic_core** is not the right owner for G1–G2; fixes belong in **apps_rg** PA + contract tests.

---

## Recommended remediation order

1. **W0** — Author-Gate: single E0 SSOT strategy (hydrate-from-YAML vs delete inline vs generate-at-build).
2. **W1** — P0 executive_summary: wire `build_executive_summary_assembly_input()` to examples YAML; add `test_e0_compile_matches_examples_ssot`.
3. **W2** — P1 competencies + unify: same hydration helper + lane tests.
4. **W3** — Align BOM/registry E0 requiredness; document shell vs section template roles.
5. **W4** — CI gate: `python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py` fails on `dual_authority_risk` for any ACTIVE lane.
6. **W5** — Refresh [apps_rg_pa_prompt_contract.md](../guides/apps_rg_pa_prompt_contract.md); reconcile dual contract trees or add cross-ref lint.

---

## Commands

```bash
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
```

Regenerates [prompt_assembly_ssot_gap_audit.json](../../artifacts/apps_rg/plans/prompt_assembly_ssot_gap_audit.json).

---

## Related work

- [proof_pool_c0_ssot_gap_review_plan.md](proof_pool_c0_ssot_gap_review_plan.md) — C0/FEC proof pool (orthogonal)
- [apps-rg-proof-pool-c0-ssot-a7f3e2.md](../../.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md) — active proof-pool plan
- Conversation root cause: dual E0 authority (BOM examples vs inline template)
