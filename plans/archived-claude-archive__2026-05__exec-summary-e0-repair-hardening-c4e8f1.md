---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\exec-summary-e0-repair-hardening-c4e8f1.md'
original_relative_path: '_archive\\2026-05\\exec-summary-e0-repair-hardening-c4e8f1.md'
source_sha256: a237729408acc5753ee86c6174c213cc4cdb5ae0c28d62f4bcc7101ccc6b5916
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-e0-repair-hardening-c4e8f1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
dod_exempt: false
parent_rca_run: exec_summary_20260523_153906
depends_on_plan: apps-rg-pa-ssot-gap-b8e4f1
depends_on_plan_status: COMPLETED
---

# Executive summary — repair monotonicity and X2 hardening (post PA SSOT)

Close the **remaining** Brown & Brown live failure chain after PA E0 convergence: **deterministic repair regression** (mechanism inventory + thin ledger), **synthesis regen / repair orchestration**, and **live runtime proof**. The **3-sentence initial L2** root cause (dual E0 authority) is **closed upstream** by [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md).

Target: canonical CLI produces **4–5 sentences**, **≥5 claim_ledger rows when pool≥6**, passes **`x2_exec_summary_sentence_count_4_5`**, **`x2_exec_summary_evidence_utilization`**, **`x2_exec_summary_no_mechanism_inventory`**, and **`X3_ALLOW`** (or honest BLOCK with no repair-induced regression).

> **plan_id:** `exec-summary-e0-repair-hardening-c4e8f1`  
> **Prerequisite (COMPLETED):** [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md) — E0 hydrate at compile via [`e0_examples.py`](apps_rg/prompt_assembly/e0_examples.py)  
> **Extends:** [exec-summary-graph-only-b5a963](exec-summary-graph-only-b5a963.md) (W10 repair — needs monotonic X2 guard)  
> **Pre-PA-SSOT RCA run:** [exec_summary_20260523_153906](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_153906)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W8
LAST_COMPLETED_WAVE: W8
LAST_UPDATED: 2026-05-23
INHERITED_FROM: apps-rg-pa-ssot-gap-b8e4f1 (W1–W5 COMPLETED 2026-05-23)
NOTION_PLANS_ROW: page_id=36927693-f55c-812c-9299-e92220d8a6e6 url=https://www.notion.so/exec-summary-e0-repair-hardening-c4e8f1-36927693f55c812c9299e92220d8a6e6

---

## Upstream completion (apps-rg-pa-ssot-gap-b8e4f1)

| Deliverable | Location | Relevance here |
|-------------|----------|----------------|
| `resolve_e0_for_section()` | [`e0_examples.py`](apps_rg/prompt_assembly/e0_examples.py) | Executive summary E0 from YAML, not template stubs |
| PA wiring | [`executive_summary_pa.py`](apps_rg/runtime/sections/executive_summary_pa.py) | `e0_examples=resolve_e0_for_section("executive_summary", …)` |
| Template | [`executive_summary.generate_scratch_v1.yaml`](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) | Inline positives removed; compile-time E0 |
| Contract tests | [`test_pa_e0_examples_ssot.py`](tests/_apps_contract/test_pa_e0_examples_ssot.py) | Gold ≥4 sentences; no template stub in compiled E0 |
| Compile proof | [`pa_e0_compile_proof_receipt.json`](artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json) | `yaml_gold_sentence_count: 4`, `pass: true` |
| CI ratchet | [`check_prompt_assembly_ssot.py`](ops_scripts/ci/check_prompt_assembly_ssot.py), [`verify_pa_e0_compile_proof.py`](ops_scripts/apps_rg/verify_pa_e0_compile_proof.py) | Contract gates |
| Docs | [`apps_rg_pa_prompt_contract.md`](docs/guides/apps_rg_pa_prompt_contract.md) | PA contract SSOT |

**Verify inherited E0 (no re-implementation):**

```bash
python ops_scripts/apps_rg/verify_pa_e0_compile_proof.py
python -m pytest tests/_apps_contract/test_pa_e0_examples_ssot.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py -q
```

---

## SR_INTAKE

**Objective:** Finish executive_summary **runtime** hardening: repair must be X2-monotonic; live Brown & Brown must PASS product gates after PA SSOT fixed compile-time E0.

**Constraints:**
- No `agentic_core` edits.
- Do not weaken X2/X1D gates or fixtures.
- Do not re-open PA SSOT design (hydrate-from-YAML is settled).
- `executive_summary.generate_scratch_v1.yaml` remains section slot SSOT; E0 content authority is `examples/executive_summary_examples.yaml` + `e0_examples.py`.

**Assumptions:**
- Qwen vLLM available for W7 live proof (or mark BLOCKED with env note).
- Pre-PA-SSOT artifact [exec_summary_20260523_153906](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_153906) remains historical baseline only; **W0 re-run required** post-merge.

**Tier:** T2/T3 (repair + lane + optional C0 + live proof)

---

## Root causes — status after PA SSOT

| ID | Problem | Status | Owner wave |
|----|---------|--------|------------|
| RC-E0-1 | Runtime E0 = 3-sentence inline stubs; YAML unused | **CLOSED** ([apps-rg-pa-ssot-gap](apps-rg-pa-ssot-gap-b8e4f1.md) W1) | — |
| RC-E0-2 | Model imitates 3-sentence many-shots | **MITIGATED** (compile E0 now 4+ sents); confirm on W0 live | W0, W7 |
| RC-TST-1 | Tests didn't prove E0/YAML parity | **CLOSED** (`test_pa_e0_examples_ssot.py`, CI proof) | — |
| RC-YAML-1 | Template line 1 non-comment | **CLOSED** (session + PA SSOT template pass) | — |
| RC-REP-1 | Repair hardcodes mechanism-inventory S1 | **OPEN** | W2 |
| RC-REP-2 | Repair emits 4 ledger rows when pool=7 | **OPEN** | W2 |
| RC-REP-3 | `detect_graph_only_synthesis_violations` ignores mechanism + utilization | **OPEN** | W2 |
| RC-REP-4 | Repair overwrites better regen candidate | **OPEN** | W3 |
| RC-RUN-1 | `coerce_resume_display_sentence_count_band` no-op | **ACCEPTED** (X2 enforces; no silent pad) | — |
| RC-C0-1 | 7-fact pool + optional certs → utilization pressure | **OPEN** (optional) | W4 |

---

## Wave status overview

| Wave | Focus | Status |
|------|--------|--------|
| **W1** | E0 SSOT / compile hydration | **DONE** (inherited [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md)) |
| **W0** | Post-PA-SSOT baseline + live re-run | **DONE** (compile proof; live optional per env) |
| **W2** | Prompt ratchet (U0 ledger floor, I0 cross-ref E0) | **DONE** |
| **W3** | Graph-only repair X2-monotonic | **DONE** |
| **W4** | Lane repair orchestration | **DONE** |
| **W5** | C0 / utilization policy (optional) | **DONE** |
| **W6** | Repair-focused test matrix + CI slice | **DONE** (67 passed) |
| **W7** | Live proof Brown & Brown | **DONE** ([exec_summary_20260523_164959](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_164959) — PRODUCT_QUALITY PASS; X3_REVIEW_JUDGE_SOFT_FAIL Track C) |
| **W8** | Closeout receipt | **DONE** |

---

## SR_PLAN — Waves

### W1 — E0 SSOT (inherited — no work)

**Completed by:** [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md) W1–W5 (2026-05-23).

**Do not duplicate:** `format_executive_summary_e0_slot_from_examples_yaml()` or new `test_executive_summary_e0_ssot.py` — use existing [`resolve_e0_for_section`](apps_rg/prompt_assembly/e0_examples.py) and [`test_pa_e0_examples_ssot.py`](tests/_apps_contract/test_pa_e0_examples_ssot.py).

**Regression guard (run in W6 CI slice):**

```bash
python ops_scripts/apps_rg/verify_pa_e0_compile_proof.py
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py   # expect p0_count: 0
```

---

### W0 — Post-PA-SSOT baseline (live + compile snapshot)

**Goal:** Confirm compile-time E0 is fixed; establish **new** runtime baseline for repair work.

**Steps:**
1. Run `verify_pa_e0_compile_proof.py` (expect `pass: true`).
2. Run Brown & Brown canonical CLI; record new `artifact_dir`.
3. In new run inspect:
   - `compiled_prompt.txt` — E0 positives from YAML (≥4 sentences); **no** legacy 3-sentence stub phrases.
   - `provider_response.json` — **target** 4–5 sentences on first call (may still be 3 if model ignores E0; documents residual risk).
   - `graph_only_generation_quality_repair.json` — whether repair still regresses X2.
4. Keep [exec_summary_20260523_153906](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_153906) as **pre-PA-SSOT** comparison only.

**Proof:**

```powershell
python ops_scripts/apps_rg/verify_pa_e0_compile_proof.py

python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Exit:** New baseline path documented; `CURRENT_WAVE` → W2.

---

### W2 — Prompt contract ratchet (template + I0 + U0)

**Goal:** Reinforce runtime output shape **without** re-touching E0 hydration.

**Steps:**
1. I0 `composition_heuristics`: one line — compiled E0 positives are 4–5 sentences from examples YAML; output must match that band (see [apps_rg_pa_prompt_contract.md](docs/guides/apps_rg_pa_prompt_contract.md)).
2. U0 task string ([executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)): **"claim_ledger: when ALLOWED_SOURCE_FACT_IDS count ≥6, emit ≥5 rows unless gap_notes explain omissions."**
3. SRFS block: keep pointer to E0; do not inject duplicate 3-sentence exemplar text.
4. Token budget: run [test_executive_summary_token_budget_contract.py](tests/_apps_contract/test_executive_summary_token_budget_contract.py) if U0/I0 grow.

**Tests:** Extend [test_executive_summary_prompt_ssot.py](tests/unit/apps_rg/test_executive_summary_prompt_ssot.py) for U0 ledger-floor language.

---

### W3 — Graph-only deterministic repair: X2-monotonic

**Goal:** Repair must not introduce mechanism inventory or drop ledger below utilization threshold.

**Implementation:** [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py)

1. **S1 rewrite** — thesis-led opener, **≤2 mechanism terms** (`is_mechanism_inventory_sentence`).
2. **Ledger depth** — when `len(plan_facts) >= 6`, emit **≥5** `claim_ledger` rows.
3. **`detect_graph_only_synthesis_violations`** — add `check_exec_summary_no_mechanism_inventory` + `check_exec_summary_evidence_utilization`.
4. **`apply_graph_only_generation_quality_repair`** — skip apply when repair regresses those gates (`skipped_x2_regression` in meta).

**Tests:** Expand [test_exec_summary_graph_only_quality.py](tests/unit/apps_rg/test_exec_summary_graph_only_quality.py).

**Proof:** `pytest tests/unit/apps_rg/test_exec_summary_graph_only_quality.py -q`

---

### W4 — Lane repair orchestration

**Goal:** Synthesis regen + graph repair compose without trading wins.

**Implementation:** [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)

1. Honor `graph_quality_meta.skipped_x2_regression` — do not `replaced_l2=True`.
2. Prefer `best_candidate` from synthesis regen when repair worsens mechanism/utilization vs regen output.
3. Keep `coerce_resume_display_sentence_count_band` as no-op (X2 remains authority).

**Tests:** `tests/unit/apps_rg/test_executive_summary_repair_orchestration.py` (new); re-run [test_executive_summary_synthesis_regen.py](tests/unit/apps_rg/test_executive_summary_synthesis_regen.py).

---

### W5 — C0 / utilization policy (optional)

**Goal:** Resolve cert-fact vs utilization tension without weakening gates.

**Options (Author-Gate if implementing both):**
- **A:** [c04_exec_summary_shaping.py](apps_rg/runtime/c0/c04_exec_summary_shaping.py) — `fact_certs_*` → `STRATUM_BACKGROUND`.
- **B:** Exclude `fact_certs_*` from utilization pool size in gate math only.

**Tests:** [test_exec_summary_graph_shaping.py](tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py), [test_executive_summary_evidence_utilization.py](tests/unit/apps_rg/test_executive_summary_evidence_utilization.py).

---

### W6 — Test + CI matrix (repair-focused; E0 via PA SSOT tests)

**Goal:** Ratchet **repair and runtime**; rely on PA SSOT plan for E0 drift.

**CI slice (minimum):**

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Inherited PA SSOT (do not skip)
python ops_scripts/apps_rg/verify_pa_e0_compile_proof.py
pytest tests/_apps_contract/test_pa_e0_examples_ssot.py `
  tests/_apps_contract/test_pa_section_contracts_w9.py -q

# This plan's scope
pytest tests/unit/apps_rg/test_exec_summary_graph_only_quality.py `
  tests/unit/apps_rg/test_executive_summary_evidence_utilization.py `
  tests/unit/apps_rg/test_executive_summary_prompt_ssot.py `
  tests/unit/apps_rg/test_executive_summary_repair_orchestration.py `
  tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py `
  tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py `
  tests/_apps_contract/test_exec_summary_section_pipeline.py -q
```

**New tests (this plan only):**
- `tests/unit/apps_rg/test_executive_summary_repair_orchestration.py`
- Optional: `tests/_apps_contract/test_exec_summary_post_repair_x2_shape.py` — compile + unit repair gates, not duplicate `test_pa_e0_examples_ssot.py`

**Not needed:** `test_executive_summary_e0_ssot.py` (superseded by `test_pa_e0_examples_ssot.py`).

---

### W7 — Live proof (Brown & Brown)

**Goal:** Runtime PASS after W2–W4 (and W5 if taken).

**Expect (vs pre-PA-SSOT run):**
| Check | Pre-PA-SSOT (153906) | Post-fix target |
|-------|----------------------|-----------------|
| Compiled E0 | 3-sentence stubs | ≥4 sentences (CI proof) |
| Initial `provider_response` | 3 sentences | 4–5 sentences |
| `x2_exec_summary_no_mechanism_inventory` | FAIL (repair) | PASS |
| `x2_exec_summary_evidence_utilization` | FAIL (4 rows) | PASS |
| `PRODUCT_STATUS` | X3_BLOCK | ALLOW |

**Receipt:** [executive_summary_e0_repair_hardening_receipt.md](docs/reports/apps_rg/executive_summary_e0_repair_hardening_receipt.md)

---

### W8 — Closeout

1. `PLAN_STATUS: COMPLETED`, `LAST_COMPLETED_WAVE: W8`.
2. Cross-link [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md) as prerequisite.
3. C0 proof-pool work remains [apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md) if needed.

---

## Verification matrix (SR_VERIFY)

| Check | Gate / artifact | Pass criterion |
|-------|-----------------|----------------|
| E0 compile SSOT | [pa_e0_compile_proof_receipt.json](artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json) | `pass: true` (inherited) |
| E0 drift CI | `prompt_assembly_ssot_gap_audit.py` | `p0_count: 0` |
| Initial L2 shape | `provider_response.json` (post W0) | 4–5 sentences |
| Mechanism inventory | `x2_exec_summary_no_mechanism_inventory` | PASS |
| Evidence weave | `x2_exec_summary_evidence_utilization` | PASS when pool≥6 |
| Sentence band | `x2_exec_summary_sentence_count_4_5` | PASS |
| Repair monotonic | `graph_only_generation_quality_repair.json` | No X2 regression on apply |
| Product | `x3_disposition.json` | ALLOW (Brown & Brown) |

---

## Files touched (remaining scope only)

| File | Waves |
|------|-------|
| [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py) | W2 (U0/I0 text only) |
| [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) | W3 |
| [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) | W4 |
| [c04_exec_summary_shaping.py](apps_rg/runtime/c0/c04_exec_summary_shaping.py) | W5 (optional) |
| `tests/unit/apps_rg/test_executive_summary_repair_orchestration.py` | W4/W6 (new) |

**Already changed (PA SSOT plan — do not re-edit unless regression):**
- [e0_examples.py](apps_rg/prompt_assembly/e0_examples.py)
- [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/examples/executive_summary_examples.yaml) path via hydration
- [prompt_bom.yaml](apps_rg/prompt_assembly/prompt_bom.yaml), [prompt_registry.yaml](apps_rg/prompt_assembly/prompt_registry.yaml)
- [test_pa_e0_examples_ssot.py](tests/_apps_contract/test_pa_e0_examples_ssot.py)

---

## SR_APPROVAL

**Status:** Ready for execution on **W0, W2–W8** (W1 closed upstream).

Reply `SR_APPROVAL: approved` to start at **W0** (post-PA-SSOT baseline), or `SR_APPROVAL: W2-W7` to skip baseline and implement repair waves only.

---

## Deferred

- Re-implementing E0 hydration (owned by [apps-rg-pa-ssot-gap-b8e4f1](apps-rg-pa-ssot-gap-b8e4f1.md)).
- L1 `sentence_band` advisory field.
- Changing `EVIDENCE_UTIL_MIN_LEDGER_ROWS_WHEN_POOL_LARGE` threshold before W3/W5 fixes land.
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
