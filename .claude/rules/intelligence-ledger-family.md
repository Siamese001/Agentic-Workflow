# Intelligence Ledger Family — stub

> On-demand (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. All ledger writes go through `tools.ledgers.hook_helpers.emit_ledger_event` (never raw `sqlite3`), fail-soft + idempotent; schema additive-only. Detail: [`ledger-consulter`](../skills/ledger-consulter/SKILL.md) skill, ADR-050. Enforced: `ops_scripts/ci/check_ledger_writer_contract.py`.
