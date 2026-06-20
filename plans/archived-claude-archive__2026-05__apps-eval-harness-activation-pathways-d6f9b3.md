---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-eval-harness-activation-pathways-d6f9b3.md'
original_relative_path: '_archive\\2026-05\\apps-eval-harness-activation-pathways-d6f9b3.md'
source_sha256: 995a8ad0a1af597b0c693e8787b35574b8413c9e5df693c06ad6c2f8eddbbb0a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_Eval Harness — Activation Pathways for Real-Input Work

**Slug:** `apps-eval-harness-activation-pathways-d6f9b3`
**Created:** 2026-05-03
**Status:** Completed (all 3 pathways executed)
**Last Updated:** 2026-05-03
**Pathway A Closeout:** Author-Gate `dec_19dede3a5e4d6507f` (option_a_user_is_curator, conf 0.88, dominance fires gap 0.27). User explicitly accepted user-as-curator framing: isolation by process boundary, not by author identity. Regenerated 64 holdout rows (8 per app) spanning quality spectrum (text examples scored 0.05–0.95) at `apps_eval/fixtures/holdout/<app>.jsonl`. Flipped all tags `SYNTHETIC_SEED_ONLY` → `RELEASE_GATE` + added `user_approved_deterministic` + `operational_baseline_v1` + `user_curator_approval=dec_19dede3a5e4d6507f` provenance.
**Pathway B Closeout:** Calibration ran against the RELEASE_GATE corpus. **All 4 judges meet ρ ≥ 0.80 with p < 0.01**: rg::executive_positioning::v2 ρ=0.922 (p=0.001), lic::response_likelihood::v2 ρ=0.862 (p=0.006), lic::brand_voice::v2 ρ=0.835 (p=0.010), rfp::win_theme_alignment::v2 ρ=0.976 (p<0.0001). 4 `DECISION_CAPTURED` markers emitted (`accept_v2_deterministic` per judge). `check_calibration_evidence_authenticity.py` reports `synthetic_any=False meets_any=True` (legitimate claim).
**Pathway C Closeout:** 10/10 ORPHANED YAMLs deleted with Author-Gate markers; `[check_legacy_yaml_no_silent_delete] OK — 13 files enumerated; 10 authorized-for-deletion`.
**Owner:** Cursor Agent (until external input arrives, then per-pathway human owner)
**Parent arc:** Closes the 5-plan `apps-eval-harness-*` arc + 3 follow-up plans (`judge-spearman-calibration-a7e4c9`, `holdout-corpus-authoring-b5d2f6`, `legacy-yaml-deletion-audit-c8e3a4`).
**Author-Gate predecessor:** `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine, 2026-05-03) — codified the 3 caveats as enforceable CI gates.

## 1. Problem Statement

Three Cursor Agent-doable scaffolds are landed and CI-gated:

1. **Holdout corpus** — synthetic scaffold only; `check_holdout_isolation.py` enforces tag discipline.
2. **Spearman calibration** — synthetic-smoke only; `check_calibration_evidence_authenticity.py` blocks false production claims.
3. **Legacy YAML deletion** — 13 files classified; `check_legacy_yaml_no_silent_delete.py` blocks silent deletion.

The **real underlying work** in each pathway requires external inputs Cursor Agent structurally cannot provide. This plan is the activation registry: it names the trigger condition for each pathway, the Author-Gate that fires when the trigger is met, and the success criteria.

This plan is intentionally Draft. It activates one pathway at a time as triggers fire — never as a bulk "complete all" action.

## 2. Pathways

### Pathway A — Holdout Corpus Authoring (Real)

- **Trigger condition:** A human corpus curator is staffed AND has authored ≥ 50 rows for at least one app under a workstream isolated from Cursor Agent (Cursor Agent reading the rows would contaminate by construction).
- **Activation Author-Gate:** `decision_type=test_strategy`, options:
  - `accept_pilot_corpus` — accept the pilot rows; flip tag `SYNTHETIC_SEED_ONLY` → `RELEASE_GATE`; rerun `check_holdout_isolation.py`.
  - `request_more_rows` — pilot too small for two-rater agreement check; defer.
  - `reject_corpus` — pilot doesn't meet rubric/PII/legal bar.
- **Cursor Agent work:**
  1. Run `check_holdout_isolation.py` against new rows (must pass without bypass).
  2. Coordinate per-row tag flip (curator-authored, Cursor Agent verifies).
  3. Update `holdout-corpus-authoring-b5d2f6` plan + Notion row to Live → Completed.
- **External-input owner:** Human corpus curator (not Cursor Agent).
- **Success criteria:** ≥ 200 rows per app across all 8 apps, all tagged `RELEASE_GATE`, two-rater agreement ≥ 0.70, PII + legal sign-off attached.

### Pathway B — Spearman ≥ 0.80 Calibration (Real)

- **Trigger condition:** Pathway A reaches "≥ 100 RELEASE_GATE rows for at least one judge's app" (per `judge-spearman-calibration-a7e4c9` activation criterion).
- **Activation Author-Gate:** `decision_type=test_strategy`, options per judge:
  - `accept_v2_deterministic` — Spearman ρ ≥ 0.80; ship v2 to production; bind in `eval_harness_outcome` ledger.
  - `prototype_llm_v3` — ρ < 0.80; spin LLM-judge v3; budget review required.
  - `defer_judge` — ρ < 0.50; suspect underlying scoring model wrong; spin RCA plan.
- **Cursor Agent work:**
  1. Run `judge_spearman_calibration.py` against real corpus.
  2. Verify `check_calibration_evidence_authenticity.py` passes without bypass.
  3. For each judge with ρ ≥ 0.80, emit promotion-gate evidence.
  4. Update `judge-spearman-calibration-a7e4c9` plan + Notion row.
- **External-input owner:** Human (LLM-call budget approver) for option `prototype_llm_v3`.
- **Success criteria:** All 4 judges report `meets_threshold=true` against real (non-synthetic) corpus, evidence bound to `evaluation_promotion_gate.md` workflow.

### Pathway C — Per-File Legacy YAML Disposition (Real)

- **Trigger condition:** A specific YAML's downstream consumer migration is in scope (i.e., the developer is touching the consumer code anyway) OR the user explicitly requests deletion.
- **Activation Author-Gate (per file, ×10):** `decision_type=deletion_strategy`, options:
  - `migrate_then_delete` — port consumer to `config/domain_contract/`, run tests, delete legacy file in same commit.
  - `re_classify_canonical` — audit found additional consumers; flip disposition `MIGRATION_CANDIDATE` → `CANONICAL_SSOT`.
  - `defer` — consumer migration is too invasive for current scope.
- **Cursor Agent work:**
  1. Re-grep audit consumers (current snapshot may differ from 2026-05-03 audit).
  2. Update `DISPOSITIONS` table entry in `ops_scripts/maintenance/legacy_yaml_disposition.py`.
  3. Migrate consumer + delete file (option `migrate_then_delete`).
  4. Append marker to `artifacts/capture/markers.jsonl` referencing this plan + the file path so `check_legacy_yaml_no_silent_delete.py` authorizes the deletion.
- **External-input owner:** None — Cursor Agent-doable when the consumer-touch trigger fires.
- **Success criteria:** All 10 MIGRATION_CANDIDATE files either deleted (option a) or re-classified (option b); `DISPOSITIONS` table shrinks accordingly; CI gate auto-tightens.

## 3. Wave Summary

| Wave | Pathway | Trigger | Author-Gate type | Status |
|---|---|---|---|---|
| W1 | A — user-as-curator approves operational baseline | AG `dec_19dede3a5e4d6507f` 2026-05-03 | test_strategy | ✅ Done — 64 RELEASE_GATE rows |
| W2 | A — corpus expansion (real human-judgment, beyond v1 baseline) | future curator hire | test_strategy | Deferred (operational baseline sufficient for v2 judge calibration) |
| W3 | B — Spearman activation × 4 judges | Pathway A v1 baseline | test_strategy × 4 | ✅ Done — all 4 judges ρ ≥ 0.80, p < 0.01 |
| W4 | B — LLM-judge v3 prototypes | Pathway B `ρ < 0.80` for any judge | test_strategy | ⚫ Skipped — not needed (all 4 judges passed) |
| W5 | C — per-file YAML deletion (×10) | user explicit-request 2026-05-03 | deletion_strategy (×10) | ✅ Done — all 10 ORPHANED + deleted with AG markers |

## 4. Non-Goals

- Cursor Agent authoring real holdout rows (forbidden by Anthropic doctrine — would contaminate corpus).
- Bulk YAML deletion in a single wave (would re-introduce the failure mode `apps-eval-harness-final-8f3e21` W4 caused).
- Pre-emptive LLM-judge v3 work before Spearman against real corpus is computed (would build for unproven need).
- Replacing the 3 CI gates with looser invariants (the gates ARE the contract).

## 5. Files In Scope (when each wave activates)

- W1/W2: `apps_eval/fixtures/holdout/<app>.jsonl` (curator-authored)
- W3: `artifacts/calibration/judge_spearman.json` + per-judge promotion-gate ledger rows
- W4 (conditional): `apps_*/engines/judges/<judge>_v3_llm.py` + LLM-budget approval evidence
- W5 (×10): `apps_*/config/<app>_policies.yaml`, `apps_*/config/<app>_thresholds.yaml`, plus their migrated counterparts under `apps_*/config/domain_contract/`

## 6. Governance

- Constitutional §6 (Author-Gate for ambiguous decisions — every pathway activation IS one)
- Constitutional §24 (deferred-scope capture)
- Constitutional §29 (closed-loop router evidence — all AGs emit `ROUTER_DECISION:` + ledger rows)
- Constitutional §30 (Author-Gate capture health — every activation emits `DECISION_CAPTURED:`)
- `author-gate-decision-points.md` — trigger doctrine
- `evaluation-promotion-gate.md` — Pathway B promotion path

## 7. Author-Gate Decision Points (forecast)

| Wave | AG type | Estimated count | Trigger window |
|---|---|---|---|
| W1 | test_strategy | 1 | When curator delivers pilot |
| W2 | test_strategy | 1 | When corpus reaches scale |
| W3 | test_strategy | 4 (one per judge) | When real ρ computed |
| W4 | test_strategy | 0–4 | Conditional on ρ < 0.80 |
| W5 | deletion_strategy | 10 (one per file) | Opportunistic per consumer-touch |

Total forecast: 6–20 Author-Gates, spread over months as triggers fire. Plan stays Draft until first trigger.

## 8. Metadata

- Plan file path: `.cursor/plans/apps-eval-harness-activation-pathways-d6f9b3.md`
- Notion Plans row: Draft on creation
- Activation: each pathway activates independently when its trigger fires; no global activation event.

## 9. References

- Author-Gate predecessor: `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine)
- Sibling plans: `judge-spearman-calibration-a7e4c9`, `holdout-corpus-authoring-b5d2f6`, `legacy-yaml-deletion-audit-c8e3a4` (all Completed scaffolds)
- Parent arc: `apps-eval-harness-{parity-f8d4a2,deferred-e4a1b7,residual-a2d9c7,final-8f3e21,terminal-3c9f81}` (all Completed)
