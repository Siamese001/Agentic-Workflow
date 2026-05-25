# Executive Summary — L2 (Qwen) vs X1D (Judges) Input Parity RCA

**Date:** 2026-05-25  
**Evidence run:** [exec_summary_20260525_002352](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352)  
**Prior smoking-gun:** [exec_summary_l2_qwen_prompt_trace_rca_20260525.md](exec_summary_l2_qwen_prompt_trace_rca_20260525.md)  
**Remediation plan:** [.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md](../../.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md)

---

## Executive answer: “Why isn’t U0 the single boundary?”

**U0 is only the user-task slice.** `apps_rg` compiles **three different prompt surfaces** from overlapping but non-identical inputs:

| Surface | Builder | What the model sees |
|---------|---------|---------------------|
| **L2 generator** | `compile_executive_summary_prompt()` → `strategic_tailor_v1` shell | S0, D0, **I0**, **E0**, Y0, C0, JD block, **U0 + product_patch**, composition plan, SRFS blocks, graph guards, R0 |
| **X1D judges** | `build_executive_summary_judge_packet()` → `render_judge_prompt_from_packet()` | GRADE_ONLY instruction, **GRAPH_ONLY rubric**, **subset** `deterministic_gate_summary`, allowed_fact_packet, targeting_context, **candidate only** |
| **Judge regen (L2 retry)** | `build_judge_remediation_user_message()` appended to prior `messages` | Judge findings + dimension lines + composition arc — **not** full I0/E0/SRFS |

Targeting JD/briefing **can** match (parity receipt `parity_match: true` on the reference run). **Instructional and enforcement surfaces still diverge** — that is why Qwen and judges behave like they read different specs.

```text
runtime_payload (facts, jd, briefing, composition_plan)
        │
        ├─► PA compile ──► compiled_prompt.txt ──► Qwen L2
        │
        └─► JudgePacket ──► render_judge_prompt ──► Gemini / GPT / Claude X1D
                ▲
                └── never receives E0, I0, S0, composition_plan, SRFS oneshot
```

---

## Prior findings (smoking guns — retained)

1. **E0 gold_base teaches mechanism inventory** that I0 and negative E0 forbid; SVP positive example is last in compile order (`e0_examples.py`).
2. **B4 requires `fact_certs_001`** while I0 forbids AWS/Databricks/FSA names; X2 credential gate passes at 2 markers; judges still penalize synthesis.
3. **STRATEGY / S3 arc pushes Brown EA/interop** with no matching proof facts; judges grade ATS on full JD while L2 proof law blocks JD-as-proof.
4. **X2 passes inventory-shaped prose**; judges apply residual `synthesis_quality` / `executive_signal` anyway.

---

## Additional divergence scenarios (new)

### A. Intentional GRADE_ONLY separation (by design, still causes drift)

| # | L2 (Qwen) | X1D (judges) | Effect |
|---|-----------|--------------|--------|
| A1 | Full **I0** (`proof_law_v1`, `credential_policy_v1`, `composition_heuristics`, anti-inventory) | **No I0** — only short `GRADE_ONLY_INSTRUCTION` | Generator gets detailed proof/style law; judges get rubric summary only |
| A2 | **E0** many-shot (`build_executive_summary_e0`, 4 positives + negatives) | **No E0** | Qwen told “match E0 band”; judges never see gold/negative examples |
| A3 | **SRFS** oneshot + forbidden phrase contract + `SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR` in template lineage | Rubric mentions SRFS only in retired-criteria negation | Style SSOT split across three authorities |
| A4 | **`format_composition_plan_for_pa`** (brushstrokes, `required_fact_ids`, six_sentence_arc) | Rubric: “not a fixed S1–S5 checklist” + optional `evidence_utilization` | L2 **mandates** brushstroke facts; judges penalize “bullet stack” on same output |
| A5 | **`format_graph_only_quality_guardrails_block`** + input authority appendix | Not in judge packet | Extra generation-only constraints |
| A6 | **R0** JSON schema in PA shell | `REQUIRED_JUDGE_OUTPUT_SCHEMA` + dimension_verdicts block | Different output contracts |
| A7 | **S0/D0/Y0** voice slots | Shared compact `build_x1d_judge_system_prompt` only | Provider system prompts align; **user** prompts do not |

**Code anchors:** `executive_summary_pa.py` (`build_executive_summary_assembly_input`, `compile_executive_summary_prompt`); `executive_summary_judge_packet.py` (`render_judge_prompt_from_packet`, `packet_forbids_generator_prompt_reuse`); `executive_summary_x1d.py` (`use_grade_only_packet` → never reuse `compiled_prompt` as judge user message).

---

### B. Timing and snapshot mismatches (bugs / footguns)

| # | Issue | Evidence |
|---|--------|----------|
| B1 | **First X1D round runs before X2** | `executive_summary_lane.py`: `run_llm_judges` ~L2014, then `run_x2_gates` ~L2108 |
| B2 | **Pre-X2 `deterministic_gate_summary` has ~11 keys**; live X2 emits **~79 gates** | `build_deterministic_gate_summary` vs `x2_gate_outputs.json`; `JUDGE_PACKET_REQUIRED_GATE_KEYS` in `executive_summary_x2_x1d_contract.py` |
| B3 | **Synthesis / mechanical-opener X2 gates not in judge packet summary** | e.g. `x2_executive_summary_synthesis_quality` PASS in X2 but absent from `build_deterministic_gate_summary`; judges still fail `synthesis_quality` dimension |
| B4 | **Post-X2 refresh** rebuilds packet (`executive_summary_judge_packet_post_x2.json`) — soft rerun / regen paths must use post-X2 packet | `refresh_x1d_judges_after_full_x2`, `rerun_soft_failed_judges` (fixed when `x2_gates` passed) |
| B5 | **Regen uses truncated L2 `messages` + remediation block** — not a recompile from `runtime_payload` | `retry_qwen_for_judge_remediation` — fourth prompt surface |

---

### C. Conditional divergence (same run family, different runs)

| # | Trigger | L2 change | Judge change |
|---|---------|-----------|--------------|
| C1 | **Token budget trim** (`trim_executive_summary_prompt_content`) | May strip **E0**, **Y0**, compress **JD/briefing** in compiled prompt | Judge packet uses **frozen** `jd_text` / `briefing` from `generation_material` extract — **not** re-trimmed with L2 |
| C2 | **Evidence capsule** active | C0 replaced by capsule block in L2 | Judges still get full `allowed_fact_packet` list from pool |
| C3 | **`enrich_allowed_fact_packet_for_judges`** | C0 may omit metric derivative rows in display | Judges see **extra** derivative fact rows for grading |
| C4 | **Dual rubrics in repo** | I0 + product shape | Packet uses **`GRAPH_ONLY_GRADE_ONLY_RUBRIC`** only; `SRFS_GRADE_ONLY_RUBRIC` unused on packet path — SRFS dim-6 ATS language stricter in dead rubric |
| C5 | **Provider transport** | Qwen vLLM single stack | Gemini schema / OpenAI json_object / Anthropic token limits — same contract hash, different enforcement |

**C1 is the critical “something is fucked up” case when trim fires:** parity compares digests extracted from **post-trim** `compiled_prompt` vs **pre-trim frozen** bundle passed to judges — they can match on digest while **L2 lost E0/JD prose judges never had**.

On reference run `exec_summary_20260525_002352`, `trim_applied: false` ([token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/token_budget_receipt.json)) — C1 did not fire; A/B still explain 2/3 judges.

---

### D. Enforcement triple-stack (same output, three verdicts)

| Layer | Mechanism | Credential example | Mechanism-inventory example |
|-------|-----------|-------------------|----------------------------|
| L2 I0 | “Do not mention AWS, Databricks…” | Forbidden in prose | Anti comma-chain inventory |
| L2 composition | B4 `required_fact_ids` includes certs | **Required** weave | Arc pushes platform brushstroke |
| X2 | `no_credential_dump` (≥3 markers), `no_mechanism_inventory` (pattern) | **PASS** at 2 markers | **PASS** without comma-chain |
| X1D dim 6–8 | Residual quality + gate summary subset | Rubric: don’t soft-penalize if gate pass — **Claude still fails** | `executive_signal` / inventory findings |

---

### E. Other sections (pattern warning)

`targeting_context_lane_runtime_audit.py`: only **executive_summary** has `judge_packet_glob`. Headline, competencies, unify lanes audit **compiled_prompt** only — no judge packet parity lane. Any future judge packet there would repeat the same L2 vs X1D split unless unified at compile time.

---

## Why targeting parity ≠ prompt parity

[targeting_context_parity_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/targeting_context_parity_receipt.json) proves **JD + briefing bytes** match between generation material extract and judge packet. That is **necessary** but **not sufficient**:

- Parity does not include **E0, I0, composition_plan, SRFS, gate snapshots, or rubric text**.
- Parity digest is computed **after** compile; optional trim can change L2 JD embedding without updating judge inputs (C1).

---

## Recommended fix themes (see plan)

1. **Single generation–grade contract document** derived from one builder (or explicit diff manifest).
2. **E0 compile order / gold_base removal** for SVP lanes.
3. **Align B4 cert requirement with I0 + tighten X2 credential gate**.
4. **Expand `deterministic_gate_summary` to full post-X2 snapshot before any MODEL_BACKED judge call**; never grade on pre-X2 subset.
5. **Map rubric dimensions to X2 gate IDs** (synthesis_quality ↔ `x2_executive_summary_synthesis_quality`) in packet.
6. **Judge regen: recompile from `runtime_payload` or inject parity manifest**, not findings-only patch.
7. **CI: L2–X1D input manifest drift gate** (hashes of instructional blocks, gate key sets).

---

## Status

| Item | Status |
|------|--------|
| RCA complete | PASS (this document) |
| Plan on disk | PASS — [exec-summary-l2-x1d-input-parity-c4f8e1.md](../../.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md) |
| Notion registration | Run `tools/notion/plan_notion_sync_exec_summary_l2_x1d_input_parity.py` |
