# Live Qwen X2 — Wave 2 (headline, unify narrative, competencies)

**STATUS: PARTIAL** — Wave-2 scoped sections reach **X2 PASS** on latest **REAL_LLM** bundles; headline remains **X3 judge soft-fail**; unify narrative proof depends on unify bullets (Wave 3).

## After (latest REAL_LLM)

| Section | Run | X2 | X3 | PQ |
|---------|-----|----|----|-----|
| headline | `headline_20260518_225908` | PASS | X3_REVIEW_JUDGE_SOFT_FAIL | PASS |
| competencies | `competencies_20260518_225908` | PASS | X3_ALLOW | PASS (`proof_eligible`) |
| unify_narrative | `unify_narrative_20260518_231059` | PASS | X3_ALLOW | PASS |

## Fixes (no gate weakening)

- **Headline:** deterministic word-count expand to 10–13 words (`headline_lane`).
- **Competencies:** allowlist typo repair, `c0_proof_blob`-aligned coerce, keyword-stuffing term drop (`competencies_dispatch`).
- **Unify narrative:** claim `source_fact_id` remap, briefing themes default (`unify_narrative_lane`); upstream bullets + ledger pool stamp (`proof_pool_resolver`).

JSON: `live_qwen_x2_wave2_headline_unify_competencies.json`
