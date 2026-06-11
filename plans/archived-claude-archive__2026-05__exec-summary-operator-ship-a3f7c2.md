---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-operator-ship-a3f7c2.md'
original_relative_path: '_archive\\2026-05\\exec-summary-operator-ship-a3f7c2.md'
source_sha256: 1a8766e9215c7473c2d0bcb663c757b56c62a5cd9995384c0397bf39800d9abf
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-operator-ship-a3f7c2
plan_type: product
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary — Operator Ship & Simplification

**North star:** One CLI run with explicit targeting (`python -m apps_rg --section executive_summary …`) must have a **clear, documented outcome**: either a **shippable draft** (rules-clean prose you can paste) or **certified ALLOW** (all judges pass). No more “X2 PASS + exit 1 + twelve env flags.”

**Related (do not duplicate):** [`section-product-shape-alignment-b4e7a1.md`](section-product-shape-alignment-b4e7a1.md) hardened **shape SSOT** (6 sentences / 140 words). This plan fixes **operator semantics, repair policy, and overfit complexity** — not sentence-count literals.

> **plan_id discipline:** `exec-summary-operator-ship-a3f7c2` ↔ file stem ↔ markers `plan=exec-summary-operator-ship-a3f7c2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-24
W5_RECEIPT: [exec_summary_operator_ship_exec_summary_20260524_001344_receipt.md](docs/reports/apps_rg/exec_summary_operator_ship_exec_summary_20260524_001344_receipt.md)
W5_RUN_ID: exec_summary_20260524_001344
W5_TIER_ACHIEVED: minimum_ship
W5_CERTIFIED_RUN_BEST: exec_summary_20260524_125852 (2/3 judges PASS; Claude 3.4 FAIL — residual synthesis)
DEFERRED_SCOPE: certified_3_of_3_model_backed_pass → backlog (Claude calibration + OpenAI quota); not required for plan PASS
PLAN_COMPLETE: plan=exec-summary-operator-ship-a3f7c2 note="W0–W5 minimum ship PASS; certified tier deferred"

NOTION_PAGE_ID: 36a27693-f55c-81ab-8c4a-e867ea5f5bfe
NOTION_PLAN_URL: https://www.notion.so/exec-summary-operator-ship-a3f7c2-36a27693f55c81ab8c4ae867ea5f5bfe
PLAN_CREATED: slug=exec-summary-operator-ship-a3f7c2 path=.cursor/plans/exec-summary-operator-ship-a3f7c2.md status=Not Started notion_page=36a27693-f55c-81ab-8c4a-e867ea5f5bfe

OPERATOR_GUIDE: [executive_summary_operator_guide.md](docs/apps_rg/executive_summary_operator_guide.md)

---

## Context (SCQA)

- **Situation** — Executive summary lane enforces strict X2 (deterministic) and unanimous X3 (three LLM judges). Pre-X2 synthesis regen is **on** by default; post-X2 judge regen is **off** unless `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1`. Tests **encode** `product_quality_status=PASS` + `X3_REVIEW_JUDGE_SOFT_FAIL` + `exit 1` as correct.
- **Complication** — Real runs (Brown & Brown SVP) pass X2, score 2/3 on judges, exit **1**. Operators optimized prompts/gates while the **certification bar** and **default repair** stayed misaligned. Multiple overlapping repair paths (synthesis regen, post-X2 refresh, judge regen, soft-judge-only rerun, L6 shadow) with no single story.
- **Question** — How do we ship exec summary without more gate creep?
- **Answer** — **Two-tier success model**, **one post-judge repair default on product runs**, **operator outcome matrix as contract tests**, and **prune/document** redundant paths — not more X2 gates.

---

## Product Decisions (lock in W0 — Author-Gate if policy fork)

| ID | Decision | Recommendation |
|----|----------|----------------|
| PD-1 | **Draft vs certified** | **DRAFT_READY** = `REAL_LLM` + X2 PASS → CLI **exit 0**, artifact usable, `proof_eligible=false`. **CERTIFIED** = `X3_ALLOW` + all judges pass → `proof_eligible=true`. |
| PD-2 | **Judge quorum** | Keep **3/3 for CERTIFIED** (proof). Do **not** add 2/3 ALLOW without explicit ADR — reduces overfit risk but weakens proof story. |
| PD-3 | **Default judge regen** | `judge_regeneration_enabled()` **true when** `product_fail_closed_runtime()` (live `python -m apps_rg --section executive_summary`). Env `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=0` remains opt-out. |
| PD-4 | **2/3 + solitary soft-fail** | When X2 PASS and exactly **one** soft-fail judge with synthesis/executive_signal tags → **one** bounded Qwen regen (already partially fixed in trigger order; wire + test). |
| PD-5 | **Exit code authority** | `process_exit_code` follows **DRAFT_READY**, not CERTIFIED alone. `PRODUCT_STATUS` / `X3_JSON` remain authoritative for proof. |
| PD-6 | **No new X2 narrative gates** | Narrative quality = judges + **one** post-judge regen prompt ([`executive_summary_synthesis_contract.py`](apps_rg/runtime/sections/executive_summary_synthesis_contract.py)). Stop adding deterministic proxies for “Claude likes it.” |

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | Do **not** weaken X2 gates or fixtures to force PASS. |
| INV-2 | Do **not** edit `agentic_core`. |
| INV-3 | SSOT shape: 6 sentences / max 140 words — [`section_product_shape_ssot.py`](apps_rg/runtime/sections/section_product_shape_ssot.py) + [`executive_summary_x2.py`](apps_rg/runtime/validators/executive_summary_x2.py). |
| INV-4 | JD/briefing = targeting only; `jd_used_as_proof=false` always. |
| INV-5 | At most **two** LLM repair loops on product path: (A) pre-X2 synthesis, (B) post-X2 judge remediation (max 1 attempt). |
| INV-6 | L6 shadow = **future-run signal only**; never mutates current run or exit code. |
| INV-7 | Operator outcome matrix tests are **release gates** for this plan (not optional docs). |

---

## Target Operator Model (after plan)

```text
python -m apps_rg --section executive_summary --target-company … --target-role … --jd … --manual-brief …

  → Qwen draft
  → [A] synthesis regen if X2 shape fails     (default ON)
  → X2
  → judges (3×)
  → [B] judge regen if not CERTIFIED-ready    (default ON on product path)
       └─ max 1 Qwen pass using synthesis contract + judge feedback
  → re-X2 + re-judge soft fails
  → X3

  Exit 0  if DRAFT_READY (REAL_LLM + X2 PASS)
  Exit 0  if CERTIFIED (X3_ALLOW) — same or stricter; proof_eligible when ALLOW
  Exit 1  only if REAL_LLM failed OR X2 FAIL OR generation BLOCKED
```

**Stdout must say explicitly:** `DRAFT_READY: true|false`, `CERTIFIED: true|false`, `PROOF_ELIGIBLE: …` — not only `PRODUCT_QUALITY_STATUS` vs `PROCESS_EXIT_CODE`.

---

## Execution Waves

| Wave | Focus | P0 |
|------|-------|-----|
| **W0** | Lock PD-1–PD-6 (Author-Gate packet if 2/3 ALLOW debated) | Yes |
| **W1** | Operator outcome module + CLI exit semantics + stdout | Yes |
| **W2** | Default judge regen on product path + 2/3 solitary regen + lane wiring | Yes |
| **W3** | Operator outcome contract tests (matrix) | Yes |
| **W4** | De-complexify: repair policy doc, env surface, retire dead SRFS repair flags | P1 |
| **W5** | Live Brown & Brown proof + receipt | Required |

---

## W0 — Product lock (½ day)

**Deliverables**

- [ ] This plan’s PD-1–PD-6 accepted (or ADR note in plan if 2/3 ALLOW chosen instead).
- [ ] One-paragraph **Operator README** stub: `docs/apps_rg/executive_summary_operator_guide.md` (draft vs certified, env opt-outs only).

**Author-Gate:** Required if changing proof contract (PD-1/PD-2/PD-5).

---

## W1 — Two-tier success + CLI exit (1–2 days)

### W1.1 Operator disposition helper

**New:** `apps_rg/runtime/sections/executive_summary_operator_disposition.py`

```python
# derive from existing artifacts — no new gates
draft_ready = runtime_generation_status == "REAL_LLM" and product_quality_status == "PASS"
certified = x3_code == "X3_ALLOW" and x3.pass_
proof_eligible = certified and all_judges_model_backed_pass
cli_exit = 0 if draft_ready and not generation_blocked else 1
# product_fail_closed: optional cli_exit=1 if not certified — DECIDE in W0 (recommend exit 0 on draft_ready)
```

### W1.2 Wire CLI report

**Edit:**

- [`apps_rg/runtime/section_cli_execution_report.py`](apps_rg/runtime/section_cli_execution_report.py) (or equivalent builder used by exec summary lane)
- [`apps_rg/runtime/sections/executive_summary_lane.py`](apps_rg/runtime/sections/executive_summary_lane.py) — set `process_exit_code` from operator helper, not raw `x3.pass_` alone
- [`apps_rg/__main__.py`](apps_rg/__main__.py) section path if exit is finalized there

**Fields to add to persisted `cli_section_execution_report.json`:**

- `draft_ready`, `certified`, `proof_eligible`, `disposition_tier` (`draft` | `certified` | `failed`)

### W1.3 Deprecate confusing composite status

- Keep `COMMAND_PASS_PRODUCT_REVIEW_OR_BLOCK` for plumbing but add **`OPERATOR_STATUS`** line: `DRAFT_READY` | `CERTIFIED` | `FAILED`.
- Document: `PRODUCT_QUALITY_STATUS` = X2 only; `PRODUCT_STATUS` = X3 code.

**Tests**

- Update [`tests/_apps_contract/test_exec_summary_cli.py`](tests/_apps_contract/test_exec_summary_cli.py): scenario X2 PASS + `X3_REVIEW_JUDGE_SOFT_FAIL` → **`process_exit_code == 0`** when `draft_ready` (product path).
- Keep test that `PRODUCT_STATUS` still shows soft-fail X3.

---

## W2 — Repair policy defaults (1 day)

### W2.1 Product-default judge regen

**Edit:** [`apps_rg/runtime/sections/executive_summary_repair_policy.py`](apps_rg/runtime/sections/executive_summary_repair_policy.py)

```python
def judge_regeneration_enabled() -> bool:
    if not RELEASE_JUDGE_REGENERATION_ENABLED:
        return False
    if os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "").strip().lower() in ("0", "false", "no", "off"):
        return False
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime
    if product_fail_closed_runtime():
        return True  # default ON for live section CLI
    return _truthy_env(os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "0"))
```

### W2.2 Solitary 2/3 regen (verify)

- Confirm [`evaluate_judge_remediation_trigger`](apps_rg/runtime/sections/executive_summary_judge_remediation.py) allows `solitary_severe` when `pass_count >= 2` (fix landed; add regression test if missing).
- **`soft_judge_only_rerun`:** run when regen skipped **only if** env `APPS_RG_EXEC_SUMMARY_SOFT_JUDGE_RERUN=1` OR fold into judge regen path — **avoid silent same-text re-score as primary fix** (low yield).

### W2.3 Post-X2 judge refresh

- **Default stays ON** but add receipt flag `rescore_only=true` — document in operator guide: does not rewrite prose.
- Optional W4: skip refresh when all judges already pass (micro-optimization).

**Tests**

- `test_judge_regen_enabled_by_default_on_product_fail_closed`
- Extend [`test_executive_summary_synthesis_contract.py`](tests/unit/apps_rg/test_executive_summary_synthesis_contract.py) solitary 2/3 case

---

## W3 — Operator outcome matrix (contract tests) (1 day)

**New:** `tests/_apps_contract/test_executive_summary_operator_outcomes.py`

| Case | X2 | Judges | Judge regen | Expect `draft_ready` | Expect `certified` | Expect exit (product) |
|------|----|--------|-------------|----------------------|--------------------|------------------------|
| Happy certified | PASS | 3/3 pass | n/a | true | true | 0 |
| **Shippable draft** | PASS | 2/3 soft | off | true | false | **0** |
| Rules fail | FAIL | any | any | false | false | 1 |
| Gen blocked | PASS | n/a | n/a | false | false | 1 |
| 0/3 + regen on | PASS | 0/3 → regen → 3/3 | on | true | true | 0 |

Implementation: **mocked** `aggregate_x3` + lane disposition helper + patch `judge_regeneration_enabled` — no live APIs in CI.

**Anti-regression:** Test must **fail** if code reverts to `exit 1` on X2 PASS + soft-fail only.

---

## W4 — Simplification & de-overfit (1–2 days, P1)

### Remove operator-facing complexity

| Item | Action |
|------|--------|
| SRFS LLM repair flags | Already off — **delete** dead branches or quarantine under `archives/` per apps taxonomy |
| Env flag sprawl | Publish **single table** in operator guide: 3 flags that matter (`JUDGE_REGEN` opt-out, `SYNTHESIS_REGEN` opt-out, `SOFT_JUDGE_RERUN` optional) |
| `executive_summary_synthesis_contract.py` | **Keep** — SSOT for SVP arc; inject in PA, regen, judge message only |
| Multiple regen receipts | Collapse to `repair_summary.json` with ordered attempts (A synthesis, B judge) |

### Prompt / judge calibration (no new X2)

- Ensure E0 positive for SVP is [`exec_summary_pos_svp_it_strategy_001`](apps_rg/prompt_assembly/examples/executive_summary_examples.yaml) in compile path for strategy titles.
- Judge rubric: already updated for S3–S6 — **parity test** vs synthesis contract strings.

### Complexity budget

- Run [`apps-rg-complexity-test-radar`](apps-rg-complexity-test-radar-605dcc.md) baseline before/after; **fail W4** if `executive_summary_lane.py` grows without deleting equivalent lines elsewhere.

---

## W5 — Live proof (required for plan PASS)

**Command (product path, no test harness):**

```powershell
python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Acceptance (either is plan PASS):**

| Tier | Criteria |
|------|----------|
| **Minimum ship** | `draft_ready=true`, `process_exit_code=0`, `resume_display_text` in artifacts, X2 all pass |
| **Certified** | Above + `x3_code=X3_ALLOW`, `proof_eligible=true` |

**Artifacts**

- `artifacts/apps_rg/runtime_proofs/executive_summary/real/<run_id>/`
- Receipt: `docs/reports/apps_rg/exec_summary_operator_ship_<run_id>_receipt.md` (links via receipt_links)

**If certified fails after W2:** capture `x1d_llm_judge_outputs.json` + one judge regen receipt; tune synthesis contract / regen prompt only — **no new X2 gates**.

---

## What we explicitly will NOT do

- Add X2 gates for “narrative synthesis,” “JD emphasis,” or “Claude score proxy.”
- Lower judge threshold below 4.0/5 to game ALLOW.
- Copy gold-example metrics into fixtures.
- Add fourth repair loop or L6 current-run mutation.
- Claim PASS from plan file update alone.

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Exit 0 on draft weakens proof story | `proof_eligible` stays false; stdout labels CERTIFIED vs DRAFT |
| Default judge regen increases cost/latency | Max 1 attempt; only when not certified after first judge pass |
| Tests encoded old exit semantics | W3 matrix + update `test_exec_summary_cli.py` |
| Still fails Claude after regen | W5 documents; optional PD-2 quorum ADR if regen insufficient |

---

## Acceptance Standard (plan complete)

- [x] W0 product decisions recorded (PD-1–PD-6; [executive_summary_operator_guide.md](docs/apps_rg/executive_summary_operator_guide.md))
- [x] W1: `draft_ready` / `certified` in CLI report + exit 0 on draft path (product)
- [x] W2: judge regen default on `product_fail_closed_runtime()`
- [x] W3: operator outcome matrix tests green in CI
- [x] W5: Brown & Brown live run meets **minimum ship** tier with receipt (`exec_summary_20260524_001344`)
- [x] No X2 gate weakening (diff review + existing contract suite green)
- [ ] **Certified tier (optional):** 3/3 `MODEL_BACKED_PASS` + `X3_ALLOW` — **not achieved** (best: `exec_summary_20260524_125852` = 2/3)

**Proof commands**

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/_apps_contract/test_executive_summary_operator_outcomes.py \
  tests/_apps_contract/test_exec_summary_cli.py \
  tests/unit/apps_rg/test_executive_summary_judge_remediation.py \
  tests/unit/apps_rg/test_executive_summary_synthesis_contract.py \
  -q
```

---

## File Touch List (summary)

| File | Wave |
|------|------|
| `apps_rg/runtime/sections/executive_summary_operator_disposition.py` | W1 NEW |
| `apps_rg/runtime/sections/executive_summary_repair_policy.py` | W2 |
| `apps_rg/runtime/sections/executive_summary_lane.py` | W1–W2 |
| `apps_rg/runtime/section_cli_execution_report.py` | W1 |
| `tests/_apps_contract/test_executive_summary_operator_outcomes.py` | W3 NEW |
| `tests/_apps_contract/test_exec_summary_cli.py` | W1 |
| `docs/apps_rg/executive_summary_operator_guide.md` | W0 NEW |
| `apps_rg/runtime/sections/executive_summary_synthesis_contract.py` | W4 (maintain) |

---

## Deferred (post-ship backlog)

- 2-of-3 judge quorum for CERTIFIED (needs ADR + calibration study)
- Resume package rollup: draft lane ALLOW for assembly while package stays REVIEW
- Auto-enable judge regen from L6 shadow on **next** run (config generation only)
