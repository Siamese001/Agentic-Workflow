---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\resume-100-done-7b3e90.md'
original_relative_path: 'resume-100-done-7b3e90.md'
source_sha256: ad139db346411c3c9873979fa2db5e9510e4944652561ccbce55b2637d3cde6d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Resume 100% Done — Live Bundle Certification to X3 ALLOW

**Plan slug:** resume-100-done-7b3e90
**Status:** PARTIAL — unify_bullets X3_ALLOW; binding architecture fixed live; remaining sections judge-bound or content-quality-bound (see runtime_bundle_certification.md)
**Owner loop:** Cursor L2 executor (apps_rg)
**Provider:** qwen_vllm live (Qwen2.5-32B-Instruct-AWQ @ localhost:8000) — confirmed reachable.

## Goal

Drive every apps_rg resume section to **live X3 ALLOW** under canonical CLI runtime proof, or an
honest **PARTIAL** with a precisely-named judge-bound residual where ALLOW depends on external
X1D judges (openai/gemini/anthropic) scoring at/above threshold.

Sections in scope: `headline`, `competencies`, `unify_bullets`, `unify_narrative`,
`ibm_bullets`, `ibm_narrative`.

## Canonical inputs (resolved)

- Target: **AIG — VP, Global Head of Agentic AI Solutions**
- `--jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt`
- `--manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md`
- `--provider qwen_vllm`
- (the `apps_rg/config/default_*` files are blocked DEFAULT_SSOT placeholders — not usable for proof)

## Immutable constraints

- No `agentic_core` edits. No weakening of X2/X3. No bypassing preflight. No mock/provider seams.
- No base resume / archive / E0 prose as generated output. JD/briefing = targeting only.
- No HOLD/disputed metric promotion. LIVE_RUNTIME_PROOF only when CLI artifacts exist + qwen live.

## Confirmed runtime state (this wave, May 28 + Jun 6 recon)

| Section | Live run | X3 | Blocking gates / cause |
|---|---|---|---|
| headline | ✅ `headline_20260528_191444` | X3_BLOCK | new positioning **binding gates** fail (bundle_id/skill/source_fact required-in-output) + `x2_headline_xyz_literal_grounding` + decisive judge openai_chatgpt |
| ibm_bullets | ✅ `ibm_bullets_20260528_191805` | X3_BLOCK | `x2_ibm_metric_anchor_bullet_ownership`, `x2_ibm_metric_outcome_id_required_when_has_metric`, `x2_bullet_technical_specificity_floor` + decisive judges gemini/openai (binding gate PASSED) |
| competencies | ⚠️ interrupted (C0 only) | — | needs rerun |
| unify_bullets | ❌ not run this wave | — | — |
| unify_narrative | ❌ not run this wave | — | — |
| ibm_narrative | ❌ not run this wave | — | — |

## Root-cause: headline/Unify binding gates

The headline/Unify C0 packs instruct the model to bind to bundles, but the section **output schema**
has no field for the model to record `*_bundle_id` / `graph_skill_node_ids`, and the binding gate
reads those from the model output. IBM passes because the IBM prompt instructs the model to echo
the binding into `change_log` and the IBM output schema carries it. The model **does** emit
`claim_ledger[].source_fact_ids`, which equal the bundles' `linked_source_fact_ids`.

**DECISION POINT (Author-Gate, architecture_choice):** how to make the binding gate satisfiable
at runtime without weakening it —
- **A. Prompt-echo (IBM-aligned):** add binding fields to the headline/Unify output schema + PA
  instruction so the model echoes `*_bundle_id` + `graph_skill_node_ids`; gate reads them (as today).
- **B. Derive-from-cited-facts:** gate resolves bound bundle_id + graph_skill_node_ids by intersecting
  the model's emitted `source_fact_ids` with each bundle's `linked_source_fact_ids`; fail if no cited
  fact maps to any bundle (stronger: verifies facts are bundle-linked rather than trusting self-declared IDs).

## Phases

- **P1 — Binding-gate fix** (headline + unify_bullets + unify_narrative), per Author-Gate decision; unit-test the gate both ways (pass/fail).
- **P2 — Headline → ALLOW:** rerun live; resolve `x2_headline_xyz_literal_grounding`; triage judge result.
- **P3 — Unify bullets + narrative:** rerun live to X2 PASS; triage.
- **P4 — IBM bullets + narrative:** address `metric_anchor` / `metric_outcome_id` / `technical_specificity` gates (prompt/evidence tuning, no metric promotion); rerun live; triage.
- **P5 — Competencies:** rerun live to completion; triage.
- **P6 — Pre-existing failure triage + regression:** the 5 known failing tests; `compileall apps_rg`; targeted bundle/role-episode suites; `git diff --name-only agentic_core/` empty.
- **P7 — Reports + closeout:** `docs/reports/apps_rg/runtime_bundle_certification.{md,json}`; honest per-section PASS/PARTIAL/BLOCKED.

## Acceptance (honest)

- Each section: live CLI executed, artifacts exist, X2 result recorded.
- ALLOW where deterministic gates pass AND all configured model-backed judges pass.
- PARTIAL where X2 passes but judges score below threshold or a key is unavailable — named explicitly.
- No agentic_core diff; no weakened gate; no HOLD metric; no base/archive/E0 hydration.

## Judge-bound ceiling (named risk)

X3 ALLOW requires every configured X1D judge (openai/gemini/anthropic) to model-backed-pass. This is
partly external (API keys + scoring). "100% ALLOW" across all six is therefore not deterministically
guaranteed; the plan drives all controllable gates to PASS and classifies any judge-bound residual honestly.
