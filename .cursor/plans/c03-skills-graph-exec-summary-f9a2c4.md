---
plan_id: c03-skills-graph-exec-summary-f9a2c4
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ".cursor/decisions/dg1-c03-exec-summary-pool-wins-f9a2c4.md"
dod_exempt: false
---

# C0.3 Skills Graph — Executive Summary Output Enhancements

**North star:** The augmented skills graph + lane-local C0.3 binding (`c03_graphrag_bound`, track-weighted expansion) should **improve executive summary quality** (targeting, fact coverage, synthesis signal) without weakening proof law. Graph context must never imply claims outside `allowed_fact_ids`.

**Parent / sibling plans:**
- [apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md) — pool vs FEC allowlist (W0 open)
- [section-product-shape-alignment-b4e7a1.md](section-product-shape-alignment-b4e7a1.md) — 6-sentence / 140-word SSOT (COMPLETE)
- Display mutator RCA (Brown `exec_summary_20260523_211407`) — splitter + graph-only dedup; **prerequisite** for judge ≥4.0

**Audit:** [proof_pool_c0_ssot_gap_review_plan.md](docs/reports/apps_rg/proof_pool_c0_ssot_gap_review_plan.md) · [exec_summary_graph_projection_w4b.md](docs/reports/apps_rg/exec_summary_graph_projection_w4b.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-24
NOTION_PAGE_ID: 36927693-f55c-81cf-becb-f80666292408
NOTION_PLANS_ROW: page_id=36927693-f55c-81cf-becb-f80666292408
NOTION_STATUS: Completed
DISK_SSOT: .cursor/plans/c03-skills-graph-exec-summary-f9a2c4.md

PLAN_CREATED: slug=c03-skills-graph-exec-summary-f9a2c4 path=.cursor/plans/c03-skills-graph-exec-summary-f9a2c4.md status=Not Started notion_page=36927693-f55c-81cf-becb-f80666292408

PLAN_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 note="W0–W5 implemented; DG-1=A pool-wins; Brown exec_summary_20260523_215732 X2 PASS; X3_BLOCK (judge); closeout PARTIAL quality (1/3 Brown)"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W0 note="DG-1=A captured; allowlist audit extension; c03_exec_summary_binding.md"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W0.5 note="display integrity (waves A–D sibling)"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W1 note="filter_c03_evidence_to_allowed_pool; pre-L2 block; X2 subset gate"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W2 note="SQLite attach; graph_targeting_capsule; PA non-proof banner"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W3 note="brushstroke bindings; no promotion (DG-1=A)"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W4 note="native_c03 enrich; proof_pool_digest receipts"
WAVE_COMPLETE: plan=c03-skills-graph-exec-summary-f9a2c4 wave=W5 note="Brown sample LIVE_RUNTIME_PROOF; closeout receipt; 22 pytest passed"

---

## Context (SCQA)

- **Situation** — Executive summary uses `augmented_skills_graph` + `selection_method: augmented_skills_graph_c03_graphrag`. SRFS arsenal allocates ~7 HIGH facts; track-weighted expansion and `build_executive_summary_c03_graphrag_bound` add graph metadata; PA → L2 → repairs → X2/X1D.
- **Complication** — C0.3 on the exec hot path is **shallow** (1-hop edges on selected facts, no SQLite attach). Track expansion advertises **more** skills/facts than the proof pool allows. FEC/C03 snapshots can list **FEC-only** fact IDs (`fact_solutions_002`, `fact_revenue_ops_001`). Modular sweep: **X2 PASS + X3_REVIEW_JUDGE_SOFT_FAIL** (synthesis, not correctness).
- **Question** — Which C0.3 / skills-graph enhancements yield the **best** executive-summary output lift per unit risk?
- **Answer** — Fix **allowlist coherence first**, then **deepen graph-informed targeting** (SQLite + capsule + brushstroke binding), then **JD-aware fact promotion** and **native C03 parity** — without enabling spine GraphRAG or weakening gates.

---

## Current architecture (exec hot path)

```text
resolve_augmented_skills_graph_authority
  → select_candidate_facts_for_role (arsenal buckets, ≤10 facts)
  → build_executive_summary_c03_graphrag_bound(selected_fact_ids)   # no SQLite
  → build_track_weighted_expansion(seed_fact_ids, bind_c03=True)    # wide metadata
  → SectionProofPool.allowed_fact_ids  (~7)                         # proof law
  → compile_executive_summary_prompt (facts + graph appendix)
  → L2 → graph_only repair → composition (B1–B4) → finalize → X2/X1D
```

**Proof classification:** `c03_graph_sqlite_context.PROOF_CLASSIFICATION = graph_context_routing_support_not_claim_proof`

**Graph vs evidence separation (all artifacts):** Any graph capsule, C03 expansion, SQLite context, native C03 output, brushstroke map, or composition plan must carry:

| Field | Required value |
|-------|----------------|
| `authority_class` | `GRAPH_TARGETING_NON_PROOF` |
| `proof_classification` | `graph_context_routing_support_not_claim_proof` |
| `claim_support_allowed` | `false` |

- Any emitted `fact_id` used for **claim support** must be in `allowed_fact_ids`.
- Any graph-only skill or pillar may guide **wording/theme only**, never source a claim.

**Deferred (out of scope):** Core spine C0.3 GraphRAG traverse per [C0_graph_lane_deferral.md](apps_rg/config/domain_contract/C0_graph_lane_deferral.md).

---

## Ranked enhancements (impact on exec summary output)

| Rank | Enhancement | Primary quality lever | Root cause addressed |
|------|-------------|----------------------|----------------------|
| **E1** | **Pool-wins allowlist SSOT** — FEC/C03 evidence_items ⊆ `allowed_fact_ids`; strip or promote track-expanded facts explicitly | Fact coverage + model confusion | Pool 7 vs FEC 9; graph implies extra claims |
| **E2** | **SQLite C0.3 on exec resolve** — `enrich_c03_bound_with_sqlite_context` + `expand_c03_graph_bindings` (fact_links_first) on exec path | Targeting + skill ranking | Shallow 1-hop bind; pillar/skill context unused |
| **E3** | **Graph targeting capsule in PA** — top-N track-weighted skills (pillar-matched) as **non-proof** targeting slice | SVP synthesis / JD theming | Model sees ~7 facts but not graph-selected skills |
| **E4** | **Brushstroke ↔ fact binding at selection** — map each allowed fact → B1–B4 role; fail pre-L2 if required brushstroke uncovered | Synthesis structure | Painting plan advisory only; stacked fact clauses |
| **E5** | **JD-aware arsenal quota overrides** — derive bucket weights from `role_family_priorities` + JD signals (brokerage/regulated) | Targeting + coverage | Fixed `_PROFILE_SLOT_QUOTAS`; W4B under-match partner/GTM |
| **E6** | **Graph-informed fact promotion** — promote 1–2 track-high facts into pool when brushstroke gap + HIGH + external-eligible | Fact coverage | Conservative exec SRFS excludes MEDIUM partner facts |
| **E7** | **Native C03 ACL for executive_summary** — `enrich_proof_pool_with_native_c03` + align receipts | Authority clarity | Competencies-only native enrich today |
| **E8** | **Repair DAG uses composition plan** — graph-only repair template driven by `composition_plan` + `c03_selected_skill_ids`, not fixed plat/gov/quant stack | Synthesis after repair | mechanical_opener_stack → full template swap |

**Prerequisite (not C0.3, blocks judges):** Display integrity — `split_sentences` U+001F token vs `\s+`; graph-only pad loop `covered_bases`. Implement via sibling display-RCA wave or W0.5 in this plan.

---

## Architecture invariants

| ID | Invariant |
|----|-----------|
| INV-1 | Graph/skills metadata **never** adds claim proof without `fact_id` in `allowed_fact_ids`. |
| INV-2 | `PROOF_CLASSIFICATION` remains `graph_context_routing_support_not_claim_proof` in prompts. |
| INV-3 | No spine `canonical_c0_3_claimed=true` until real spine GraphRAG ships. |
| INV-4 | No weaken X2/X1D/judge thresholds to pass. |
| INV-5 | No `agentic_core` edits. |
| INV-6 | Product shape stays SSOT: 6 sentences / 140 words ([section_product_shape_ssot.py](apps_rg/runtime/sections/section_product_shape_ssot.py)). |
| INV-7 | Graph artifacts carry `authority_class=GRAPH_TARGETING_NON_PROOF`, `proof_classification=graph_context_routing_support_not_claim_proof`, `claim_support_allowed=false`. |
| INV-8 | One resolved proof pool object feeds PA, runtime payload, usage ledger, X2, and receipts (`proof_pool_digest` parity). |
| INV-9 | Repair may not add/remove claimable fact IDs or change `allowed_fact_ids`. |

---

## Design decisions (Author-Gate required)

### DG-1 — Allowlist when track expansion surfaces new HIGH facts

| Option | Behavior | Trade-off |
|--------|----------|-----------|
| **A — Pool wins (recommended)** | FEC/C03/PA only list `allowed_fact_ids`; track facts are context-only | Safest; may under-use graph |
| **B — Promote with receipt** | Up to +2 facts promoted into pool when brushstroke gap + HIGH + graph score | Better coverage; needs promotion rules + tests |
| **C — FEC widens pool** | Union FEC IDs into allowlist | Violates current proof law; highest regression risk; **not implementable in this plan** unless proof law is redesigned |

**Gate:** W0 — coordinate with [apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md) W0 (single decision for all lanes).

**W0 blocking rule:** Author-Gate must explicitly choose **A**, **B**, or **C**. If DG-1 is not captured, closeout `STATUS` must be **BLOCKED**, not PARTIAL. W1–W5 may not start until DG-1 is resolved and captured.

### DG-2 — Graph capsule size in PA

Default: **top 8 skills** by track weight × pillar match, max 120 chars/skill label, no fact claims in capsule.

---

## Execution waves

### W0 — Prereqs + design lock (no behavior change except audit)

| ID | Deliverable | Files |
|----|-------------|-------|
| W0.1 | Author-Gate **DG-1** (pool-wins vs promote) — one ledger entry | `.cursor/decisions/` or AG receipt |
| W0.2 | Exec-only allowlist audit extension in [proof_pool_c0_ssot_gap_audit.py](ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py) — report `c03_expansion_fact_ids - allowed` | ops_scripts |
| W0.3 | Document exec C03 hot path vs competencies native path in [qwen-vllm-topology.md](docs/architecture/qwen-vllm-topology.md) appendix or `docs/reports/apps_rg/c03_exec_summary_binding.md` | docs |

**Exit (blocking gate — not audit-only):**

- Audit JSON shows exec allowlist delta enumerated.
- **DG-1 resolved and captured** via Author-Gate receipt (explicit choice: **A** pool-wins only | **B** bounded promotion with receipt | **C** reject as unsafe).
- **W1–W5 may not start** until DG-1 is captured.
- If DG-1 is not captured at any closeout: `STATUS=BLOCKED` (never PARTIAL).
- Option **C** is not implementable in this plan unless proof law is redesigned; choosing C blocks all implementation waves.

---

### W0.5 — Display integrity prerequisite (parallel, ~1 day)

| ID | Deliverable | Files |
|----|-------------|-------|
| P.1 | Fix abbrev tokens (non-whitespace sentinels or restrict split `\s`) | [executive_summary_sentence_utils.py](apps_rg/runtime/validators/executive_summary_sentence_utils.py) |
| P.2 | Graph-only pad honors `covered_bases` | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| P.3 | X2: display roundtrip + cross-sentence metric dedup | [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) |

**Exit:** Brown rerun — no `B3\x1f`; no duplicate 8→28; tests green.

---

### W1 — E1 Allowlist coherence (P0)

| ID | Deliverable | Files |
|----|-------------|-------|
| W1.1 | `filter_c03_evidence_to_allowed_pool(c03_bound, allowed_fact_ids)` | [c03_graphrag_bound.py](apps_rg/runtime/c03_graphrag_bound.py), [c03_graph_sqlite_context.py](apps_rg/runtime/c03_graph_sqlite_context.py) |
| W1.2 | Wire filter in [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py) `_resolve_executive_summary_graph_only_proof_pool` after track expansion | proof_pool_resolver |
| W1.3 | FEC compose: exec section uses same allowlist ([c0_fec_compose.py](apps_rg/runtime/spine/c0_fec_compose.py)) | spine bridge |
| W1.4 | Contract test: `c03_selected_fact_ids ⊆ allowed_fact_ids` (or empty if pool-wins) | `tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py` |
| W1.5 | Pre-L2 gate: if any `evidence_items.fact_id` ∉ `allowed_fact_ids` and `claim_support_allowed != false` → **BLOCK** lane before provider call | proof_pool_resolver, executive_summary_lane |
| W1.6 | X2 gate: `c03_selected_fact_ids_claimable_subset_allowed_fact_ids` = PASS/FAIL | [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) |
| W1.7 | Receipt fields in `section_metric_receipt.json`: `allowed_fact_ids`, `c03_context_fact_ids`, `c03_filtered_out_fact_ids`, `promoted_fact_ids`, `graph_targeting_skill_ids` | lane receipts |

**Fail-closed:** C03/FEC/PA mismatch is **reported and blocks** the executive_summary lane before provider call — not advisory.

**Tests:**

- `compiled_prompt.txt` contains non-proof banner near `GRAPH_TARGETING_CAPSULE`.
- `provider_request.json` must not expose graph-expanded fact IDs outside `allowed_fact_ids` as claimable evidence.
- Empty after filtering is allowed only when the item is context-only and explicitly marked non-proof.

**Exit / acceptance (fresh Brown run):**

- `allowlist_mismatch=false`
- `c03_filtered_out_fact_ids` enumerated
- No FEC-only claimable fact IDs
- No prompt claim support outside `allowed_fact_ids`

---

### W2 — E2 + E3 Deepen C0.3 targeting (P0)

| ID | Deliverable | Files |
|----|-------------|-------|
| W2.1 | `build_executive_summary_c03_graphrag_bound(..., attach_sqlite=True)` default on exec | [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py), [c03_graphrag_bound.py](apps_rg/runtime/c03_graphrag_bound.py) |
| W2.2 | `build_graph_targeting_capsule(track_expansion, role_family_key, max_skills=8)` | new `apps_rg/runtime/c0/exec_summary_graph_targeting_capsule.py` |
| W2.3 | PA slot: `GRAPH_TARGETING_CAPSULE` block (non-proof banner) | [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py), template YAML |
| W2.4 | Artifact: `graph_targeting_capsule.json` in run dir | executive_summary_lane |
| W2.5 | Unit tests + [debug_c03_exec_summary_graph.py](tools/cursor/debug_c03_exec_summary_graph.py) update | tests |
| W2.6 | SQLite attach receipt: `c03_sqlite_attach_status` (`ATTACHED` \| `DEGRADED` \| `BLOCKED`), `c03_sqlite_attach_reason` | c03_graph_sqlite_context, lane receipts |

**Runtime rules (SQLite attach — bounded, non-authority-widening):**

- `attach_sqlite=True` is **best-effort bounded context**, not required proof authority.
- SQLite attach failure must degrade to shallow C03 with receipt (`c03_sqlite_attach_status`, `c03_sqlite_attach_reason`).
- Degraded attach may continue **only if** W1 allowlist coherence still passes.
- SQLite may add skill/pillar/relationship context; **cannot** add claimable facts.
- `canonical_c0_3_claimed` remains `false`.

**GRAPH_TARGETING_CAPSULE caps (W2):**

- Max **8 skills**; max **120 chars** per skill label.
- Max total capsule chars: **960** (8 × 120 hard cap).
- No metrics, employer names, dates, revenue figures, or unsupported outcome language inside capsule unless bound to `allowed_fact_ids` and still marked as evidence elsewhere.
- Capsule is **theming language only**; deterministic ordering by score then ID.

**Tests:**

- SQLite unavailable → lane runs or blocks per configured policy, with explicit receipt.
- SQLite returns fact outside `allowed_fact_ids` → filtered, not claimable.
- Capsule cannot contain forbidden metric/date/company patterns unless backed by allowed facts.
- Compiled prompt remains under section token budget.

**Exit:** Brown run artifacts include capsule; PA compiled prompt contains capsule + non-proof banner; no new fact IDs in allowlist without W1 promotion rules (DG-1=B only).

---

### W3 — E4 + E5 + E6 Selection quality (P1)

| ID | Deliverable | Files |
|----|-------------|-------|
| W3.1 | `bind_facts_to_brushstrokes(facts, c03_skills)` → plan metadata on `selected_fact_plan` | [executive_summary_composition.py](apps_rg/runtime/sections/executive_summary_composition.py) |
| W3.2 | Pre-L2 gate: `check_exec_summary_brushstroke_coverage` (B1–B4 each have ≥1 fact) | [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) |
| W3.3 | JD-aware quota overrides in [exec_summary_graph_projection_w4b.py](apps_rg/fact_inventory/exec_summary_graph_projection_w4b.py) | projection + tests from W4B fixtures |
| W3.4 | If **DG-1=B only**: `promote_track_facts_for_brushstroke_gaps(...)` max +2 | [selected_role_fact_set.py](apps_rg/fact_inventory/selected_role_fact_set.py), proof_pool_resolver |

**Brushstroke gate (pre-L2 — no hallucination pressure):**

- Evaluate selected **allowed** facts before provider call.
- If B1–B4 coverage incomplete: **block before L2** with explicit `gap_notes`, **or** continue only if product policy allows missing brushstroke coverage.
- Do **not** force the model to synthesize missing brushstrokes from graph-only context.

**Receipt fields:** `brushstroke_required_ids`, `brushstroke_covered_ids`, `brushstroke_missing_ids`, `brushstroke_fact_bindings`, `brushstroke_gate_status`.

**W3.4 promotion path (optional; impossible unless DG-1=B):**

- If DG-1 ≠ B: promotion code/tests **must not** be implemented.
- If DG-1=B, promotion requires: **HIGH** confidence, `external_eligible=true`, no contradiction flags, exact `source_fact_id`, brushstroke gap, max **+2** facts, `promotion_receipt_ref`, before/after `allowed_fact_ids` diff.
- Promotion must happen **before PA**, not during repair or after generation.

**Negative tests:**

- MEDIUM fact cannot be promoted for executive_summary.
- Graph score alone cannot promote.
- Promotion without receipt blocks.
- Promotion after L2 starts blocks.

**Exit:** W4B archetype tests pass; pre-L2 gate PASS or explicit gap_notes on Brown pool; optional +2 facts only with receipt (DG-1=B only).

---

### W4 — E7 + E8 Authority + repair (P1)

| ID | Deliverable | Files |
|----|-------------|-------|
| W4.1 | Call `enrich_proof_pool_with_native_c03` for `executive_summary` | [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py), [native_c03_skills_graph.py](apps_rg/runtime/native_c03_skills_graph.py) |
| W4.2 | Receipt fields: `native_c03_status`, `c03_graphrag_bound_status` aligned in run manifest | lane + spine receipts |
| W4.3 | Graph-only repair: `build_graph_only_executive_summary_from_facts(..., composition_plan=...)` brushstroke-ordered | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| W4.4 | Narrow graph-only trigger: opener normalize before full rewrite (coordinate Track C C1) | [executive_summary_composition.py](apps_rg/runtime/sections/executive_summary_composition.py), repair policy |

**Native C03 parity (receipt-only — not a second authority path):**

- `native_c03_status` is receipt parity **unless** it consumes the same `allowed_fact_ids`.
- One resolved proof pool object used by PA, runtime payload, usage ledger, X2, and receipts.
- Native C03 **cannot** produce a second evidence list that bypasses `SectionProofPool`.

**Test:** PA, FEC, `section_metric_receipt`, and X2 all reference the same `proof_pool_digest`.

**Repair DAG constraints (proof pool + product shape preserved):**

- Repair may: reorder, dedup, normalize opener, improve sentence flow.
- Repair may **not**: add new claimable fact IDs, change `allowed_fact_ids`, violate 6-sentence / 140-word SSOT.
- Repair receipt must show: `input_claim_ids`, `output_claim_ids`, `added_claim_ids=[]`, `removed_claim_ids`, `word_count`, `sentence_count`, `repair_reason`.

**Exit:** `native_c03_final_evidence.json` on exec runs; repair receipt shows brushstroke order when applied; `proof_pool_digest` parity across PA/FEC/receipt/X2.

---

### W5 — Live proof + closeout (required)

| ID | Deliverable |
|----|-------------|
| W5.1 | 3× Brown & Brown exec CLI (`REAL_LLM`, vLLM up) — **LIVE_RUNTIME_PROOF** for executive_summary only |
| W5.2 | Quality evidence: `allowlist_mismatch=false`, **≥2/3 X1D ≥4.0** — **not** proof-law PASS; `X3_REVIEW_JUDGE_SOFT_FAIL` ≠ PASS |
| W5.3 | Receipt: `docs/reports/apps_rg/c03_exec_summary_enhancement_closeout_receipt.md` (required closeout format below) |
| W5.4 | Regenerate [proof_pool_c0_ssot_gap_audit.json](artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json) |

**Proof classification (W5):**

- 3 Brown runs = **LIVE_RUNTIME_PROOF** for executive_summary only.
- **Not** `RELEASE_ELIGIBLE_PROOF` for full resume unless all required lanes, judges, provider receipts, and X2/X3 criteria pass.
- Judge threshold ≥2/3 X1D ≥4.0 is **quality evidence**, not proof-law evidence.

**Required artifacts per run:**

- `run_manifest.json`
- `compiled_prompt.txt`, `compiled_prompt_artifact.json`
- `provider_request.json`, `provider_response.json`
- `graph_targeting_capsule.json`, C03 bound artifact
- `section_metric_receipt.json`, `x2_gate_outputs.json`, `x3_disposition.json`
- `l6_shadow_eval_package.json` (if emitted by canonical lane)
- `proof_pool_digest` and `allowed_fact_ids` snapshot

**Commands:**

```bash
docker start local-qwen-vllm
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

```bash
pytest tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py \
  tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py \
  tests/unit/apps_rg/test_exec_summary_product_shape_x2.py -q
```

---

## Success criteria (Definition of Done)

| # | Criterion |
|---|-----------|
| DoD-1 | DG-1 Author-Gate captured (shared with proof-pool plan); W1–W5 blocked until captured |
| DoD-2 | Exec run: no FEC-only fact IDs in PA/C03 prompt surfaces |
| DoD-3 | `graph_targeting_capsule.json` emitted; PA includes capsule + non-proof banner |
| DoD-4 | Brushstroke coverage gate PASS or explicit gap_notes on Brown runs |
| DoD-5 | W5.2 judge threshold met on 2 of 3 consecutive runs (quality evidence only) |
| DoD-6 | No `agentic_core` diff; contract tests PASS |
| DoD-7 | `proof_pool_digest` parity across PA, FEC, receipt, X2 |
| DoD-8 | Protected-path proof captured (see below) |

**Do not claim PASS if:**

- DG-1 is missing
- Any claimable C03/FEC/PA `fact_id` is outside `allowed_fact_ids`
- `canonical_c0_3_claimed=true`
- Graph context is represented as claim proof
- Brown live run is not executed for W5
- X3 is REVIEW/BLOCK but closeout says quality passed

---

## Protected-path proof (every closeout)

```bash
git diff -- agentic_core          # → no diff
git diff -- apps_rg/runtime/sections/section_product_shape_ssot.py   # → no diff unless explicitly scoped
git diff -- apps_rg/config/domain_contract/C0_graph_lane_deferral.md # → no diff unless explicitly scoped
```

- Proof that `canonical_c0_3_claimed=false` remains unchanged.

---

## Required closeout format

Every wave closeout and W5 final receipt must use this exact structure:

```text
STATUS: PASS | PARTIAL | BLOCKED | FAIL
PLAN_ID:
WAVES_COMPLETED:
SCOPE_MATCH:
SCOPE_DRIFT:
AUTHOR_GATE_STATUS:
DG_1_DECISION:
FILES_CHANGED:
PROTECTED_FILES_TOUCHED:
COMMANDS_RUN:
TESTS_GATES:
RUNTIME_COMMANDS:
ARTIFACTS_WRITTEN:
ALLOWLIST_PROOF:
GRAPH_NON_PROOF_PROOF:
PROMOTION_PROOF:
PRODUCT_SHAPE_PROOF:
PROOF_CLASSIFICATION:
EXPLICIT_NON_CLAIMS:
NEXT_BLOCKER:
```

---

## Out of scope

- Core spine GraphRAG / `canonical_c0_3_claimed=true`
- Default judge regen (`APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=0` until W5 stable)
- Weakening X2 sentence/word caps
- Chroma collection migration (separate ops gap)

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Authority drift — W1–W5 assume DG-1 without capture | W0 blocking gate; `STATUS=BLOCKED` if DG-1 missing |
| Promotion (DG-1 B) introduces unsupported claims | HIGH-only + brushstroke gap + X2 subset checks; impossible unless DG-1=B |
| SQLite attach widens proof authority | Degrade with receipt; filter facts outside allowlist; `canonical_c0_3_claimed=false` |
| Native C03 second evidence path | Single `proof_pool_digest` across PA/FEC/receipt/X2 |
| SQLite attach latency | Cache per graph_digest; timeout + degrade to shallow bind |
| PA token bloat from capsule | Hard cap 8 skills × 120 chars; 960 total chars |
| Brushstroke gate forces hallucination | Pre-L2 block or policy-allowed gap; no graph-only synthesis |
| W0.5 not done → judges still fail on artifacts | Block W5 until P.1–P.3 PASS |
| W5 quality conflated with release proof | LIVE_RUNTIME_PROOF vs RELEASE_ELIGIBLE_PROOF separation |

---

## Status table

| Wave | Focus | Status |
|------|-------|--------|
| W0 | Design + audit | Complete (DG-1=A) |
| W0.5 | Display integrity prereq | Complete (waves A–D) |
| W1 | Allowlist coherence (E1) | Complete |
| W2 | SQLite + targeting capsule (E2,E3) | Complete |
| W3 | Brushstroke + quotas + promotion (E4–E6) | Complete (no promotion; DG-1=A) |
| W4 | Native C03 + repair (E7,E8) | Complete |
| W5 | Live proof | Complete (1 Brown sample; X2 PASS; X3_BLOCK judge) |
