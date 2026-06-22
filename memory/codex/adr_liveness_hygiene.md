# ADR Liveness Hygiene

## ProceduralPattern:ADRLivenessHygiene

- ADR markdown is rationale/provenance only; current authority requires a live binding to a current gate, test, `.codex` rule/skill, config, runtime/code surface, or current plan.
- Use `python ops_scripts/ci/inventory_adr_liveness.py --json` to classify ADR-like files as `live_bound`, `noncanonical`, `historical_stale_marker`, or `unbound_review`.
- Use `python ops_scripts/ci/check_adr_hygiene.py --advisory` to report ADR namespace drift while allowing known duplicate ADR numbers and known legacy/generated noncanonical ADR-like files.
- Do not wire the liveness inventory into default full contract gates without reassessing runtime cost; it scans repo-wide inbound references and took roughly 30-40 seconds locally on 2026-06-22.
- Discovered: 2026-06-22; validated: 2026-06-22.
