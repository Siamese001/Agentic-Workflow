# Author-Gate capture, outcome binding, and SLA

This runbook supports **Wave 5** operations for the developer-loop Author-Gate
learning stack (plan `author-gate-learning-harden-f4e8a2`).

## Scope

- **In scope:** SQLite ledger under `.cursor/state/refactor_decisions/`, capture
  hooks, `post_commit_outcome_binder`, weekly/join calibration artifacts.
- **Out of scope:** runtime production HITL in `agentic_core/L5_safety/`.

## SLAs (operator defaults)

| Signal | Target | Measurement |
|--------|--------|-------------|
| **Surfaced → bound** | Review within **7 calendar days** | `decisions.status = surfaced` and no `decision_outcomes.execution_completed = 1`, or bind older than 7 days since `decisions.created_at` |
| **Capture completeness** | No sustained growth in Author-Gate **v2 completeness** violations | `ops_scripts/ci/check_author_gate_v2_completeness.py` |
| **Ledger SSOT** | No CI failure on legacy-path writers | `ops_scripts/ci/check_refactor_decision_ledger_ssot.py` |

Adjust thresholds in your environment; the join report uses **7 days** for the
“surfaced but unbound” counter unless you change the script constant.

## Joined calibration report (W5.1)

Run:

```bash
python ops_scripts/calibration/author_gate_learning_join_report.py --days 7
```

Outputs:

- `docs/reports/calibration/ag_learning_join_<YYYY-Www>.json`
- `docs/reports/calibration/ag_learning_join_<YYYY-Www>.md`

## When outcomes are missing

1. Confirm the ledger file exists: `.cursor/state/refactor_decisions/refactor_decision_ledger.sqlite`.
2. Run the binder for recent commits (example):
   `python .cursor/scripts/post_commit_outcome_binder.py --lookback 20`
   (or the Windsurf mirror script if your hooks still reference it — DB target is the same SSOT path.)
3. Ensure **CI receipt** env vars are set if you rely on **high** bind confidence
   (`AG_BIND_*` — see `tools/refactor_decisions/bind_confidence.py`).
4. Re-run schema migration if columns are missing:
   `python .cursor/scripts/apply_ledger_schema.py`

## When capture / packets fail

1. Inspect hook violation logs under `artifacts/cursor/` and `artifacts/windsurf/`
   (e.g. `author_gate_*_violations.jsonl`, `ask_user_question_packet_violations.jsonl`).
2. Run contract gates locally: `python ops_scripts/ci/run_contract_gates.py` (subset
   as needed) to see which harness check failed.
3. For bypass usage review, open `artifacts/windsurf/governance_bypass_rollup_latest.json`
   (from W4 rollup).

## Escalation

- Persistent unbound **surfaced** rows above SLA: treat as **governance debt** —
  pause pattern promotion until bind health recovers (`promote_author_gate_patterns.py`
  already requires clean **high** binds).
- Suspected ledger corruption: run hash-chain gate
  `ops_scripts/ci/author_gate/check_ledger_integrity.py` and W4 anomaly detector
  `ops_scripts/ci/author_gate/detect_author_gate_ledger_anomalies.py`.
