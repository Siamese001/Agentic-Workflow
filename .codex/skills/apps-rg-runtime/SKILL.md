---
name: apps-rg-runtime
description: Procedure for running the apps_rg resume-generation pipeline and reporting results — interactive-input discipline, mandatory post-run evidence rendering, and the layman-first executive-summary response shape. Invoke when the user asks to run apps_rg, `python -m apps_rg`, generate a resume, explain an apps_rg run, or show a run summary.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: during_work
  enforcement_type: tool_routing
---

# apps_rg Runtime & Reporting

This skill is the procedural companion to the always-on apps_rg rules. It exists because an
apps_rg run produces rich JSON evidence the user cannot see without rendering it, and because the
wizard — not Claude Code — owns the run inputs. Skipping the renderer or pre-filling inputs are the
two most common, most damaging mistakes; this skill prevents both.

**Sibling skills:** See the `plan-location.md` rule for plan-file placement; `boundary-enforcement` for
core/app separation, `artifact-management` for generic evidence capture. This skill is specifically
the apps_rg *run + report* loop.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| "run apps_rg" / `python -m apps_rg` without all inputs in the same turn | Issue ONE prompt requesting ALL missing inputs at once (template below); do not pre-fill flags |
| User names company + role + JD + briefing in the same turn | Run with those flags; source resume is static — resolve from the configured/most-recent path |
| Run finished (exit 0 or not) / "show me the run summary" / "how did the resume go" | Confirm mandatory `01_BCG_executive_output.md`, `02_output_bisect.md`, `02_section_lane_summary_table.md`, `03_L7_audit_ability_output.md`, and `APPS_RG_MANDATORY_RUN_OUTPUT.json` exist, invoke `python tools/apps_rg/render_run_summary.py [<run_dir>]`, and surface the decision RCA, causal attempt bisect, plus renderer markdown |
| `--section executive_summary` run | Lead with the 3-sentence layman block, then technical detail |

## Hard Routing Rules (do not violate)

| Rule | Why |
|---|---|
| Never pre-fill `--target-company`/`--target-role`/`--jd`/`--manual-brief` from inferred or prior-turn context | The in-app wizard owns these (`apps-rg-interactive-discipline.md`, constitutional §6/§18) |
| One single-prompt request for all missing inputs — no multi-turn back-and-forth | Same rule; minimizes round-trips |
| After ANY run, render `render_run_summary.py` output inline before claiming success | `apps-rg-post-run-summary.md` — "exit 0" without the table is at most PARTIAL |
| Failure/aborted runs MUST still emit and surface mandatory BCG + run ledger from the canonical run | Missing terminal artifacts are a hard failure; never repair or backfill them after exit |
| Fresh E2E run directories come only from `FRESH_E2E_ARTIFACT_DIR` / `e2e_launcher_result.json` | Modification-time discovery can bind evidence from a different run |
| Failure comparison uses the pinned baseline contract | A moving "latest passing" baseline makes the first divergence non-reproducible |
| The initial run closeout must answer "what ran, what did not, which judges ran, why retries worked or failed, and where prior/current first diverged" | Mandatory `02_output_bisect.md`, `02_section_lane_summary_table.md`, plus `APPS_RG_MANDATORY_RUN_OUTPUT.json` are the SSOT surfaces for that operator evidence |
| Every RCA required fix MUST be a 3-5 bullet implementation plan aimed at the core root cause | Single-line actions and symptom fixes are not operator-ready |
| Every RCA finding MUST include causal allocation tied to the actual root cause | Broad buckets are invalid unless each row names the concrete causal mechanism, evidence, work share, and retry recoverability |
| executive_summary response leads with exactly 3 layman sentences, no jargon | `apps-rg-executive-summary-response.md` |

## Standard Procedure

1. **Resolve inputs.** Source resume is static (most-recent `*_resume*.json|docx` under `ops_scripts/apps_rg/`). If company/role/JD/briefing are missing, issue the single-prompt template:
   ```
   To run apps_rg, please provide in your next message:
   1. Target: company, role, and level
   2. Job description — file path OR paste text
   3. Research briefing — file path, OR "auto-internal", OR "auto-tavily", OR "skip"
   ```
2. **Run** `python -m apps_rg ...` exactly as scoped — no added flags when the user typed a bare invocation.
3. **Locate the run dir** — use the explicit run directory returned by the invocation. For `--fresh-e2e`, require exactly one `FRESH_E2E_ARTIFACT_DIR` line and the matching `e2e_launcher_result.json`; never scan by modification time.
4. **Validate mandatory outputs** — verify these files exist in the exact run dir: `e2e_stage_ledger.json`, `01_BCG_executive_output.md`, `02_output_bisect.md`, `02_section_lane_summary_table.md`, `03_L7_audit_ability_output.md`, `APPS_RG_MANDATORY_RUN_OUTPUT.json`. Any missing file is a deterministic hard failure. Do not generate, regenerate, repair, or backfill it after the canonical run exits.
5. **Render evidence** — `python tools/apps_rg/render_run_summary.py [<run_dir>]`; paste the full markdown inline under `## apps_rg Runtime Evidence`. Do not paraphrase or truncate.
6. **Shape the response** — lead with the BCG executive answer and the mandatory run-ledger facts (sections, judges, blockers). Render the output bisect immediately after the BCG: every generation/repair/retry, scoped gate result, judge result or `JUDGES_NOT_REACHED`, first observed divergence, first causally relevant divergence, and ingestion-to-outcome lineage. Each RCA finding must include `root_cause`, causal allocation (`dominant_cause`, retry recoverability, and root-cause-linked allocation rows), plus a 3-5 bullet implementation plan that changes the producer/parser/validator contract causing the failure; do not present symptom-only rerun, prompt tweak, or threshold-relaxation actions as required fixes. For executive_summary, use the mandatory 3-sentence layperson explanation first, then the full attempt, gate, judge, and causal tables plus the repo-work proof floor.

## Forbidden Patterns

- ❌ Reporting "the pipeline succeeded" / "exit 0" without rendering the summary table (`apps-rg-post-run-summary.md`).
- ❌ Reporting a failed run as only "it failed" without a BCG RCA and mandatory section/judge ledger.
- ❌ Reporting RCA required fixes as one-line actions, rerun instructions, prompt-only changes, or gate-threshold changes instead of a 3-5 bullet root-cause implementation plan.
- ❌ Reporting causal allocation as generic buckets ("graph", "gates", "retries") without a concrete `root_cause_link`, evidence refs, work share, and required work.
- ❌ Hand-summarizing the run JSON instead of invoking the renderer (content-drift / hallucination risk).
- ❌ Pre-filling wizard flags from session memory or stale `apps_rg/scripts/*.json` files.
- ❌ Starting the executive_summary response with `X3_BLOCK`, a digest, or a gate-failure list.
- ❌ Skipping the renderer on a failed/aborted run "to save space".
- ❌ Selecting a fresh E2E run by latest modification time or sibling-directory scan.
- ❌ Running a mandatory-output generator after exit to make a failed run appear complete.

## References

- Renderer (required tool): `tools/apps_rg/render_run_summary.py`
- Rules: `.codex/rules/apps-rg-post-run-summary.md`, `apps-rg-interactive-discipline.md`, `apps-rg-executive-summary-response.md`, `apps-rg-execution-bias.md`
- Operator guide: `docs/apps_rg/executive_summary_operator_guide.md`
- Single backlog: `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md` (Master Gap Inventory)
- Sibling skills: `boundary-enforcement`, `artifact-management` · plan placement → `plan-location.md` rule
- Constitutional rules: §6, §18 (interactive discipline)
