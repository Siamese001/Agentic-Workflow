# apps_lic X1D Repair Loop Hardening

PLAN_CREATED: slug=apps-lic-x1d-repair-loop-hardening-490f55 path=.claude/plans/apps-lic-x1d-repair-loop-hardening-490f55.md status=Completed

Status: Completed - W5 main live gate accepted 2026-06-10  
Created: 2026-06-09  
Worktree: `C:\Git\apps_lic`  
Branch: `apps_lic`  
Primary gate: 4 per company, 12 total, full live E2E (`run_post_w7_live_12_archetype_matrix.py`)

## Objective

Harden the production W5/X1D judge-feedback repair loop used by the live apps_lic canonical dispatch path until the main 12-row full live E2E gate clears without weakening X1D, X2, routing, no-send, no-L4-write, or proof-bundle requirements.

## RCA Summary

The failed live 12-row gate isolated the blocker to the production X1D judge-feedback repair loop, not the live harness:

- `.env` was loaded from `C:\Git\Agentic-Workflow-FRESH\.env`.
- Live Claude X1D was enabled.
- Qwen/vLLM provider mode was required.
- All 12 canonical runtime rows executed.
- All 12 proof bundles were parseable.
- All routes were `INMAIL` / `linkedin_inmail`.
- No-send, no-L4-write, and no-connector-post assertions remained present.
- X2 passed for all 12 rows.
- Required X1D judges were present; no missing judge condition was observed.
- The manifest exists as `spine_run_manifest.json`.

The live harness is doing its job. Eight rows reached `X1D_REVIEW_REQUIRED` with concrete live judge feedback and `required_repairs`. Regeneration was attempted for all eight red rows, but seven exhausted the repair budget and one produced the same text as its parent. The repair path is too patch-like for multi-issue live judge failures and needs deterministic sanitation, clean rebuild behavior, stronger issue-to-repair mapping, and a second repair iteration for SC-3 / multi-judge rows.

## Scope

In scope:

- `apps_lic/engines/x1d_judge_feedback_regeneration.py`
- `apps_lic/engines/whole_message_generation.py`
- `apps_lic/config/domain_contract/whole_message_generation.v1.yaml`
- `apps_lic/runtime/bindings/w5_validation_exit_binding.py`
- `tests/apps_lic/test_x1d_judge_feedback_regeneration.py`
- `tests/apps_lic/test_w5_validation_exit_canonical_wireup.py`
- Targeted regression tests for the live failure modes.

Out of scope:

- Changing the main live E2E gate shape away from 4 per company / 12 total.
- Treating the 15-row company soak as the primary gate.
- Weakening X1D thresholds, X2 validation, route policy, no-send, no-L4-write, or proof-bundle contracts.
- Broad C0, targeting, source-normalization, or harness rewrites.

## Status Tables

### Wave Progress

| Wave | Name | Status | Exit Evidence |
| --- | --- | --- | --- |
| W0 | Evidence Lock and Fixtures | Completed | `tests/apps_lic/fixtures/x1d_repair_loop_live_12_red_rows.json` and `tests/apps_lic/test_x1d_repair_loop_w0_fixtures.py` |
| W1 | Repair Intent Normalization and Sanitizer | Completed | `tests/apps_lic/test_x1d_judge_feedback_regeneration.py` covers normalized directives, terminal `Amit`, duplicate bridge, repeated role title, budget, and required claims |
| W2 | Clean Rebuild Repair Candidate Path | Completed | Clean rebuild path prevents same-as-parent repairs and replaces patchy duplicate-signature repairs with canonical-input candidates |
| W3 | Two-Iteration SC-3 / Multi-Judge Policy | Completed | SC-3 and multi-judge repair can use two attempts under the hard cap; SC-2 single-judge remains one attempt |
| W4 | Receipt Observability | Completed | W5 receipts and manifests expose repair effectiveness, resolved/unresolved issue IDs, and sanitizer status |
| W5 | Verification | Completed | Local W0-W5 gate passed with `34 passed, 4 warnings`; main 12-row live E2E retry20 passed with `acceptance_passed=true` and `quality_violation_count=0` |

## W0 - Evidence Lock and Fixtures

Status: Completed 2026-06-09

Capture the failed live 12-row evidence as immutable regression context:

- Preserve row IDs, stop reasons, X1D issue IDs, required repairs, parent message, repair candidate, and final decision for the eight red rows.
- Add or update fixtures so tests can exercise the observed failure modes without needing live providers.
- Confirm the 15-row secondary soak remains useful corroborating evidence, but not the main acceptance gate.

Exit criteria:

- Completed: fixture represents seven `repair_budget_exhausted` rows and one `repair_same_as_parent` row.
- Completed: fixture covers AIG, Citi, and Neo4j red rows from the failed main gate.
- Completed: fixture preserves source artifact paths, parent/repair candidate digests, failed judge IDs, issue IDs, required repairs, X2 pass status, X1D review status, and missing-judge emptiness.
- Completed: fixture marks the 15-row company validation as secondary soak evidence, not the primary gate.

## W1 - Repair Intent Normalization and Sanitizer

Status: Completed 2026-06-09

Strengthen repair generation around explicit judge directives:

- Normalize X1D judge feedback into actionable repair intents.
- Map each required repair to an issue ID and expected textual effect.
- Sanitize candidate output before rejudging:
  - exactly one terminal `Amit`
  - no duplicate bridge sentence
  - no repeated role title
  - under InMail budget
  - requested claim IDs surfaced when X1D asks for evidence.

Exit criteria:

- Completed: normalized `X1DNormalizedRepairIntent` maps judge IDs, issue IDs, required repairs, intent classes, and required claim IDs.
- Completed: repair candidates are sanitized before W5 rejudges them.
- Completed: sanitizer enforces a single terminal `Amit`, bridge dedupe, repeated-role-title cleanup, budget compliance, and required claim surfacing.
- Completed: sanitizer returns an explicit `X1DRepairCandidateSanitizationResult` instead of silently accepting bad candidate text.

## W2 - Clean Rebuild Repair Candidate Path

Status: Completed 2026-06-09

Add a clean rebuild path for cases where small patches are unlikely to satisfy live judge feedback:

- Use canonical contact, company, source, route, claim, and policy inputs.
- Recompose the message around judge-required repairs instead of applying narrow textual substitutions.
- Detect same-text or near-same-text repairs before consuming the final repair attempt.
- Preserve all existing W5/X2/X1D validation contracts.

Exit criteria:

- Completed: same-as-parent Qwen repair output is converted into a clean rebuilt repair candidate before the loop reaches the same-text stop check.
- Completed: patchy duplicate-signature repairs trigger clean rebuild from canonical request, target, role, proof, length, and judge directive inputs.
- Completed: clean rebuild avoids repeated exact role-title mentions and keeps required commercial/runtime proof surfaced inside budget.

## W3 - Two-Iteration SC-3 / Multi-Judge Policy

Status: Completed 2026-06-09

Align the repair budget with the already bounded hard cap:

- Allow two repair iterations for SC-3 / multi-judge X1D failures.
- Keep the global hard cap at two.
- Do not increase budget for simple failures that should resolve in one repair.
- Make the policy visible in YAML and runtime policy code.

Exit criteria:

- Completed: `whole_message_generation` SC-3 policy advertises `repair_budget=2`.
- Completed: reasoning-intensity receipts advertise `validation_repair_passes=2` for SC-3.
- Completed: YAML policy mirrors set SC-3 repair/validation passes to 2.
- Completed: repair loop still hard-caps at 2 and elevates multi-judge failures to a two-iteration window.
- Completed: tests prove SC-3 repair can use the second iteration, SC-2 single-judge repair remains one iteration, and multi-judge failure resolves to a two-iteration window.

## W4 - Receipt Observability

Status: Completed 2026-06-09

Make repair-loop receipts sufficient for future RCA:

- Add `x1d_repair_effective`.
- Add `x1d_repair_resolved_issue_ids`.
- Add `x1d_repair_unresolved_issue_ids`.
- Add `repair_candidate_sanitization_passed`.
- Keep existing canonical dispatch and proof-bundle fields intact.

Exit criteria:

- Completed: regeneration attempt packets expose `x1d_repair_effective`, `x1d_repair_resolved_issue_ids`, `x1d_repair_unresolved_issue_ids`, and `repair_candidate_sanitization_passed`.
- Completed: regeneration result packets roll those fields up across attempts.
- Completed: W5 validation-exit receipts project the rollup fields at payload top level.
- Completed: canonical spine manifests project the same fields with `w5_` prefixes.
- Completed: focused W5 canonical wireup tests verify the new receipt and manifest fields.

## W5 - Verification

Status: Completed 2026-06-10

### W5 Finish Scope

In scope:

- Harden only the apps_lic W5 X1D judge-feedback repair loop used by the live spine.
- Add C-level editorial issue-family dispatch for the stable retry16 red rows.
- Add deterministic C-level clean-rebuild copy and subject-line composition for AIG and Citi.
- Add fixture-backed tests using retry16 unresolved issue IDs, final drafts, stop reasons, and attempt receipts.
- Re-run the local W0-W5 gate and the primary 4-per-company / 12-row live E2E gate.

Out of scope:

- Do not change env lookup beyond using the user-provided `C:/Users/amita/env/.env` for verification.
- Do not change the live harness acceptance contract.
- Do not weaken X1D, X2, no-send, proof-bundle, unsupported-claim, or route gates.
- Do not increase the global repair hard cap beyond 2.
- Do not treat the 15-row company soak as a replacement for the 12-row main full E2E gate.

Completion boundary:

- W5 is complete only when the primary 12-row live E2E gate reports `acceptance_passed=true` and `quality_violation_count=0`.
- If the live gate still fails, W5 remains open and the plan must capture the new root cause with artifact paths.

Run focused and live verification:

1. Focused tests with plugin autoload disabled and `pytest_timeout` explicitly enabled:

   ```bash
   python -m pytest -p pytest_timeout tests/apps_lic/test_x1d_judge_feedback_regeneration.py tests/apps_lic/test_w5_validation_exit_canonical_wireup.py tests/apps_lic/test_post_w7_live_12_archetype_matrix.py -q
   ```

2. Main full live E2E gate:

   ```bash
   python scripts/apps_lic/run_post_w7_live_12_archetype_matrix.py --clean --env-file C:/Users/amita/env/.env --output-dir artifacts/apps_lic/live_e2e_codex_20260610/w5_main_full_e2e_12_archetype_matrix_retry20
   ```

Acceptance criteria:

- `canonical_runtime_rows=12`.
- `parseable_proof_bundle_count=12`.
- `live_claude_x1d_enabled=true`.
- `provider_mode=live_qwen_vllm_required`.
- No missing required X1D judges.
- X2 remains passing.
- `quality_violation_count=0`.
- `acceptance_passed=true`, or any remaining review-required row is explicitly policy-expected and not attributable to repair-loop failure.

Observed 2026-06-09:

- Completed: compile check for `apps_lic/engines/x1d_judge_feedback_regeneration.py`.
- Completed: local W0-W5 gate passed with `31 passed, 4 warnings`.
- Completed: main live 12-row gate executed with live Qwen and live Claude X1D using `C:/Git/Agentic-Workflow-FRESH/.env`.
- Open: live acceptance did not pass. Best observed run was `artifacts/apps_lic/live_e2e_codex_20260609/w5_main_full_e2e_12_archetype_matrix_retry3` with `draft_visible_count=10`, `quality_violation_count=2`, and remaining rows `citi_brian_saluzzo` and `neo4j_firat_tekiner`.
- RCA: W5 repair receipts now prove the live loop is invoking two effective, sanitized attempts when the first attempt resolves prior issues and exposes new unresolved issue IDs. The remaining failures are within the actual spine repair path, not the live harness: second-attempt deterministic repair can still produce same-as-parent output for newly surfaced judge issues, and broader content-expansion experiments regressed live quality.

Observed 2026-06-10:

- Completed: ADG health checked healthy before W5 continuation.
- Completed: env file corrected to `C:/Users/amita/env/.env` after `C:/Git/Agentic-Workflow-FRESH/.env` was found absent.
- Completed: compile check for `apps_lic/engines/x1d_judge_feedback_regeneration.py`.
- Completed: focused repair-loop tests passed with `21 passed, 4 warnings`.
- Completed: local W0-W5 gate passed with `34 passed, 4 warnings`.
- Completed: main live 12-row gate executed repeatedly with live Qwen and live Claude X1D using `C:/Users/amita/env/.env`.
- Completed: retry20 main live 12-row gate passed at `artifacts/apps_lic/live_e2e_codex_20260610/w5_main_full_e2e_12_archetype_matrix_retry20`.
- Completed: retry20 reported `canonical_runtime_rows=12`, `parseable_proof_bundle_count=12`, `live_claude_x1d_enabled=true`, `provider_mode=live_qwen_vllm_required`, `draft_visible_count=12`, `review_or_block_count=0`, `quality_violation_count=0`, and `acceptance_passed=true`.
- Completed: AIG, Citi, and Neo4j each cleared all four archetype rows.
- RCA closure: root cause was limited to hardening the live spine W5 repair loop for C-level editorial issue-family dispatch, deterministic AIG/Citi clean-rebuild composition, same-parent fallback behavior, and over-broad claim carry-forward. No additional root cause was found in env loading, the live harness, X2, no-send/no-L4-write policy, proof-bundle parsing, provider mode, missing judges, or the 12-row gate contract.

## W5 Finish RCA - 2026-06-10

### What Is Not The Root Cause

- Not env loading: latest valid runs load `C:/Users/amita/env/.env` and set `live_claude_x1d_enabled=true`.
- Not the live harness: canonical row count, proof-bundle parsing, provider mode, route/no-send assertions, and live X1D execution all run.
- Not X2: remaining failures are X1D review rows after X2 has passed.
- Not missing W5 receipt observability: attempts expose effectiveness, resolved issue IDs, unresolved issue IDs, sanitizer status, and final stop reason.
- Not insufficient repair invocation: remaining rows show repair attempts are triggered, effective on prior issues, and rejudged.

### Root Causes

1. C-level acceptance is an editorial-strategy problem, not just a repair-loop plumbing problem.

   The loop now invokes bounded repair correctly, but the remaining rows are judged on executive sharpness: specific trigger insight, recipient-role fit, proof-context bridge, subject specificity, and CTA confidence. The existing deterministic repair templates can satisfy structural issues but do not reliably produce C-level executive judgment.

2. Repair intent normalization is too coarse for late-stage live judge feedback.

   Live judge issue IDs such as `cta_pressure_test_phrasing_is_overused_in_cold_outreach`, `value_bridge_sentence_is_dense_and_reads_as_generic_platform_pitch`, and `governance_foundation_sentence_reads_as_defensive_credential_framing` collapse into broad intents like `cta`, `trigger_hook`, or `claim_surface`. That loses the specific edit required on attempt 2, so the rebuilt candidate can be same-as-parent or only cosmetically different.

3. The clean rebuild path is static and company-template driven.

   The current rebuild uses company-specific strings for AIG/Citi/Neo4j. This creates whack-a-mole behavior: one live run clears Neo4j and exposes AIG/Citi, another clears a Citi row and exposes a different C-level phrasing critique. The template does not compose from a semantic editorial model with named trigger, role-owner signal, proof bridge, and CTA strategy.

4. Local tests prove mechanics, not live judge convergence.

   Local W0-W5 tests prove repair invocation, sanitizer behavior, receipt projection, and selected phrase handling. They do not predict whether live Claude X1D will accept C-level executive copy. That is why local `33 passed` can coexist with live `10/12`.

5. The hard cap of two attempts is correct but requires an in-attempt fallback.

   W5 must not simply raise the repair budget. Instead, if the second attempt would be same-as-parent or leaves a known C-level issue family unresolved, the same attempt needs to switch to a different editorial rewrite strategy before returning the repair candidate.

### Finish Plan

W5 should finish via a narrow C-level editorial repair layer inside the existing W5 repair loop, not by weakening X1D or increasing the attempt cap.

1. Freeze the current plumbing as the baseline.

   - Keep dynamic one-follow-up behavior under hard cap 2.
   - Keep W5 receipt fields.
   - Keep sanitizer and proof/no-send/X2 contracts.
   - Stop broad company-copy patching unless it is driven by an issue-family dispatch table.

2. Add a C-level editorial issue-family classifier.

   Map live issue IDs into precise edit families:

   - `subject_specificity`: subject lacks trigger or recipient-role specificity.
   - `trigger_insight`: opening is generic or lacks named company trigger.
   - `proof_bridge`: metric/proof is dropped in without domain context.
   - `credential_dump`: proof sentence reads like resume recitation.
   - `cta_executive_sharpness`: CTA is generic, overused, or asks the recipient to do work.
   - `same_parent_risk`: second-attempt candidate fingerprint matches parent or prior repair.

3. Replace static C-level company templates with a small editorial composer.

   Compose C-level repair text from five fields:

   - named trigger: from `target_context.company_trigger` and `role_ownership_signal`
   - recipient authority: e.g. GCDO, CIO, CPO
   - company-specific operating tension
   - allowed proof bridge integrated into that tension
   - direct executive CTA that does not use banned generic phrases

4. Add deterministic C-level copy lint before W5 rejudge.

   For C-level trigger-based InMail, block or rewrite before live X1D when text contains:

   - generic CTAs: `brief executive exchange`, `pressure-test`, `worth a look`
   - standalone proof labels: `Commercial proof:`, `The governance foundation is`
   - generic bridge labels: `My fit is`, `My proof is`, `The measurable proof is`
   - subject lines without a named trigger or executive role signal
   - metric sentences that do not mention the company domain or operating context

5. Add retry16 fixture coverage for the two stable red rows.

   Fixture rows:

   - `aig_jim_young`
   - `citi_brian_saluzzo`

   The fixture should preserve final subject, final draft, unresolved issue IDs, stop reason, and attempt receipts from `artifacts/apps_lic/live_e2e_codex_20260610/w5_main_full_e2e_12_archetype_matrix_retry16`.

6. Add tests that fail for the root cause, not the symptoms.

   Tests should assert:

   - C-level editorial composer consumes specific issue families, not only broad intents.
   - second-attempt same-parent risk triggers an alternate editorial variant inside the same attempt.
   - generated C-level repairs avoid banned generic CTA/proof/bridge phrases.
   - AIG proof bridge ties `$22M`/margin proof to insurance workflow reuse or governed release.
   - Citi proof bridge ties governance/quant proof to Citi Sky operating controls without credential-dump phrasing.

7. Run acceptance in order.

   - Compile check.
   - Local W0-W5 gate.
   - Main 12-row live E2E with `--env-file C:/Users/amita/env/.env`.
   - Mark W5 complete only when `acceptance_passed=true` and `quality_violation_count=0`.

## Decision Record

The main full E2E gate is 4 contacts per company across three companies, for 12 total rows. The 15-row run remains a secondary company-soak validation and must not mask failures in the 12-row archetype matrix.
