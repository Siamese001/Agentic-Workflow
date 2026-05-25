# Executive Summary — Operator Guide

> **Plan SSOT:** [.cursor/plans/exec-summary-operator-ship-a3f7c2.md](../.cursor/plans/exec-summary-operator-ship-a3f7c2.md)

## One command

```powershell
python -m apps_rg --section executive_summary `
  --target-company "<company>" `
  --target-role "<role>" `
  --jd <path-to-jd.txt> `
  --manual-brief <path-to-briefing.md>
```

## Two outcomes (operator-ship W1)

| Tier | Meaning | CLI |
|------|---------|-----|
| **DRAFT_READY** | `REAL_LLM` + X2 PASS (`PRODUCT_QUALITY_STATUS=PASS`) | **exit 0**, `proof_eligible=false` |
| **CERTIFIED** | `X3_ALLOW` + all judges ≥ 4.0/5 | **exit 0**, `proof_eligible=true` when manifest allows |

Stdout includes `OPERATOR_STATUS`, `DRAFT_READY`, `CERTIFIED`, `DISPOSITION_TIER` (see `cli_section_execution_report.json`).

- `PRODUCT_QUALITY_STATUS` = X2 only (deterministic rules).
- `PRODUCT_STATUS` = full X3 disposition (judges).
- Do not treat **exit 1** alone as “generation failed” when `OPERATOR_STATUS=DRAFT_READY`.

## Repair loops (simplified)

1. **Synthesis regen** — before judges; default **on** (`APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN`).
2. **Judge regen** — after judges when not certified; default **on** on product CLI. Up to **3 cycles** (Qwen rewrite → re-X2 → re-score soft-failed judges); stops early when all judges pass. If a judge-directed rewrite **fails X2**, one **X2-repair** pass runs (same machinery as pre-judge synthesis regen) instead of discarding the attempt. Opt-out: `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=0`. Cap: `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS` (default `3`, max `5`).

## Env flags that matter

| Variable | Default | Purpose |
|----------|---------|---------|
| `APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN` | on | Pre-X2 shape repair |
| `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN` | **on** (product path); `=0` opt-out | Post-judge Qwen rewrite loop |
| `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS` | `3` (max `5`) | Cycles until all judges pass or cap |
| `APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO` | ignored on product path | Dev/harness only |

## What we are not doing

- No new X2 gates for “narrative quality.”
- No lowering judge thresholds to force ALLOW.

## Default run summary (Cursor / operators)

**Always lead with exactly 3 short sentences** (~12-year-old reading level), then technical detail.

### Layman template (fill in per run)

1. **What happened:** The run finished and saved a draft under `artifacts/.../exec_summary_<timestamp>/` (or: it stopped early because …).
2. **Targeting fix:** The grader used the **same shortened briefing** the writer saw—not the full pasted research doc—so JD-fit scores are fair on that slice.
3. **Approved or not:** Say “approved for release” only on `X3_ALLOW` + certified judges; otherwise say **not approved** and one plain reason (e.g. “two judges scored the paragraph low,” “checklist ran before the log file existed”).

### Technical block (below the 3 sentences)

| Field | Where |
|-------|--------|
| Artifact dir | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_*` |
| Targeting parity | `targeting_context_parity_receipt.json` → `parity_match` |
| Product disposition | stdout `PRODUCT_X3_STATUS`, `x3_disposition.json` |
| Operator tier | `OPERATOR_STATUS`, `DRAFT_READY`, `CERTIFIED` in `cli_section_execution_report.json` |

Rule: [.cursor/rules/apps-rg-executive-summary-response.mdc](../.cursor/rules/apps-rg-executive-summary-response.mdc)

### Example layman (Brown run `exec_summary_20260524_233842`)

1. The run finished and wrote a real executive-summary draft plus all the proof files in the artifact folder.
2. The grader read the same shortened briefing as the writer (about 2,600 characters each)—not the full 15,000-character research paste—so the “unfair textbook” bug is fixed.
3. It’s still **not approved for release** because some automatic checklists failed (including ones that expect a usage log before it’s written) and Gemini and Claude scored the paragraph below the pass line.

## Input parity (L2 vs X1D)

U0 is only the task slice. Three prompt surfaces exist:

| Surface | Artifact | Contents |
|---------|----------|----------|
| L2 (Qwen) | `compiled_prompt.txt` | Full PA: I0, E0, composition plan, C0, JD/briefing, SRFS guards |
| X1D (judges) | `executive_summary_judge_packet_post_x2.json` | GRADE_ONLY rubric, generation law digest, X2 gate snapshot, candidate |
| Regen | `judge_remediation_cycles.json` | Judge feedback appended to prior messages |

Per-run contract manifest: `generation_grade_contract_manifest.json` (digests, E0 compile order, gate keys, `judge_excluded_by_design`).

Targeting parity (`targeting_context_parity_receipt.json`) proves JD/briefing bytes match — not full instructional parity. Judges run **after** structural X2 on `REAL_LLM` paths.

Plan: [.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md](../.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md)

## Debug: which rubric dimension failed?

After each judge pass, the run writes **`x1d_dimension_matrix.json`** next to `x1d_llm_judge_outputs.json`.

| File | Use |
|------|-----|
| `x1d_dimension_matrix.json` | Per-dimension pass/fail per judge + `consensus_fail` when ≥2 judges fail that dimension |
| `x1d_llm_judge_outputs.json` | Holistic score/pass per judge; each judge includes `dimension_verdicts` (8 keys) |
| `x2_gate_outputs.json` / packet `deterministic_gate_summary` | Hard structural/proof gates only |

**Read order:** X2 gates → dimension matrix → holistic judge pass count.

`dimension_verdicts_inferred: true` on a judge means the model omitted structured dimensions and the runtime inferred them from findings/flags (still useful, less authoritative than explicit model output).

**Regen hints:** When judge regen runs, Qwen receives a `DIMENSION_VERDICTS` block built from failed dimensions (see `executive_summary_judge_remediation.py`).

**Plan:** [.cursor/plans/exec-summary-x1d-dimension-verdicts-e8f4a2.md](../.cursor/plans/exec-summary-x1d-dimension-verdicts-e8f4a2.md)
