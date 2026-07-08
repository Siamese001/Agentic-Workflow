# apps_rg L4 Best-Practices Hardening Closeout

Plan ID: `apps-rg-l4-best-practices-hardening`
Branch: `codex-apps-rg-l4-best-practices-hardening`

## Implemented

- R1B derived-index misses now fail closed with `fixture_store_consulted=false`.
- Fixture mirror writes on blocked R1B promotion are default-off.
- `UWGCommitReceipt` now carries L4 provenance fields directly.
- UWG validation rejects missing clearance proof, registry digest set, staged-diff mismatch, non-Exit source, and target-surface mismatch.
- Audit ledger appends now carry `prev_chain_hash` and `chain_hash`.
- R1B durable projection bundles and derived-index entries now point to commit and read-surface refresh receipts.
- CI gate `check_apps_rg_l4_best_practices.py` blocks the main regression classes.

## Baseline Failures

W0 captured pre-existing broad failures in
`artifacts/apps_rg/l4_best_practices/w0_baseline_manifest.json`.
The broad `run_contract_gates.py` failure is from plan graph-layer evidence
violations outside this implementation surface. The broad `pytest -k r1b`
collection errors are also outside the focused R1B/L4 changed files.

## Verification

Focused verification commands are recorded in the final turn summary. This
document intentionally does not claim full-repo green status because W0 proved
pre-existing broad failures.
