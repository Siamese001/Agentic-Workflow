# apps_rg C0.3 resume graph W1-W6 boundary

Date: 2026-07-13

Plan: `apps-rg-c03-resume-graph-hardening-9f3c2a`

Implementation commit: `059b3951e8dee62cc9efae57f5fd8285dce48ae5`

## Durable decisions

- Canonical graph JSON remains authoritative; generated SQLite is a runtime/query projection only.
- C0.3 applies authority gates before targeting, records terminal decisions for each bounded candidate,
  and traverses the full bounded sibling frontier before applying caps.
- One deterministic whole-resume allocation is frozen before generation for all 11 claim-bearing lanes.
  Its sample digest is `47a0bbaf8828a532e5577f0d871915e50cb3fbc2981419436bde47dc655cddd3`.
- The current-run allocation contains 30 canonical-visible and 17 derived narrative assignments. It
  enforces zero skill-ID, metric-outcome-ID, and normalized metric-signature reuse and does not write
  durable graph state.
- Before X3, each final visible claim must bind to its allocated skill, fact, path, edges, citation, and
  exact metric value/unit. Orphans, causal cross-root merges, metric drift, and signed digest drift fail
  closed; the post-generation gate never repairs signed upstream artifacts.

## Verification and boundary

- W1-W5: 38 focused tests passed; 12 X3 integration tests passed; graph hardening validation, compilation,
  and whitespace checks passed. Temporary import-only stubs outside the repository were used for locally
  absent optional `openai` and `chromadb` imports; real graph JSON and SQLite data remained under test.
- W0's frozen ADG authority map constrained structural edits because live ADG transport was unavailable.
- W6 is `BLOCKED`: its configured human-labeled dataset is absent, the semantic grader is pending, and the
  benchmark is scoreless. `proof_confidence_calibrated` therefore remains `UNKNOWN`, which is non-PASS.
- Per the plan stop condition and v40 L6 doctrine, W7-W9 are not started. Resumption requires an authorized
  frozen labeled set (at least 40 samples unless the plan is formally revised), release-holdout permission,
  and blinded resume-coach review. L6 evidence is post-run and may influence future runs only.

Evidence:

- `docs/reports/apps_rg/c03_resume_graph_w1_w5_closeout.json`
- `docs/reports/apps_rg/c03_resume_graph_w6_blocker.json`
- `docs/reports/codex/codex_apps_rg_c03_resume_graph_w1_w6_receipt.json`
