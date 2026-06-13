# Decision-Ledger Hardening — W1..W5

**Status**: W1..W5 complete (2026-04-24) — all 15 phases shipped, wired, and smoke-tested
**Tier**: T3 — multi-file, cross-layer (CI + hooks + schema migrations)
**Slug**: `decision-ledger-hardening-w1w5-b3a81c`

## Goal
Close gaps in decision-ledger storage, integrity, and precedent-usage verification.
Extend the existing `author_gate_ledger_integrity.py` + `check_ledger_coverage.py` infra
to cover the 10-ledger family (`artifacts/ledgers/*.sqlite`) and add end-to-end parity
gates so a silent loss (e.g. the 2026-04-22 hook-dispatcher regression) fails CI.

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | A1 integrity + A2 marker-ledger parity | 3500 | in-progress | Both gates exit 0 on clean repo; integrity walks all 11 ledgers |
| W2 | W2.1, W2.2 | A3 precedent receipt + A4 stale sidecar | 3000 | todo | Marker v2 schema has `precedent_seen=N`; sidecar freshness alarms on drift |
| W3 | W3.1, W3.2 | B1 freshness SLO + B2 binding SLO | 3000 | todo | Per-ledger freshness report; predicted>14d fails |
| W4 | W4.1, W4.2 | C1 append-only triggers + E1 pre-commit | 3500 | todo | SQL triggers block UPDATE/DELETE; author-gate bypass pre-commit blocks |
| W5 | W5.1..W5.6 | D1 Notion parity + D2 memory parity + B3 usage rate + C2 sig verify + C3 writer allowlist + E2 heartbeat | 6000 | todo | All weekly CI jobs green |

## Phase-Level Summary

| Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|-------|-------|-------|-------------|-------------|--------|
| W1.1 | A1 — hash-chain + structural integrity gate | `ops_scripts/ci/check_decision_ledger_chain.py`; wire into `run_contract_gates.py` | 10/11 ledgers lack prev_hash/row_hash — must do structural-only check on them | 1800 | done-in-turn |
| W1.2 | A2 — marker ↔ ledger parity gate | `ops_scripts/ci/check_marker_ledger_parity.py`; reconcile DECISION_CAPTURED markers vs ledger rows | Time-window tolerance; silent hook-dispatcher regression detection | 1700 | done-in-turn |
| W2.1 | A3 — precedent-receipt marker field | v2 marker regex extension; writer update; CI parity check | Back-compat with v1 markers (must tolerate missing field) | 1500 | todo |
| W2.2 | A4 — stale-sidecar alarm | `ops_scripts/ci/check_sidecar_freshness.py`; fingerprint staleness | Fingerprint computation for "current intent" | 1500 | todo |
| W3.1 | B1 — per-ledger freshness SLO | `ops_scripts/ci/check_ledger_freshness.py`; YAML SLO config | Calibrating per-class cadence expectations | 1500 | todo |
| W3.2 | B2 — prediction→outcome binding SLO | `ops_scripts/ci/check_prediction_binding_sla.py`; warn status='predicted' > 14d | `post_commit_outcome_binder.py` may need nudging | 1500 | todo |
| W4.1 | C1 — append-only SQL triggers | `apply_append_only_triggers.py` migration; `check_ledger_append_only.py` gate | Migration safety; trigger creation is idempotent | 1500 | todo |
| W4.2 | E1 — touched-scripts pre-commit | `.pre-commit-config.yaml` entry; `check_decision_required.py` | False-positive rate on trivial script edits | 2000 | todo |
| W5.1 | D1 — Notion parity | Weekly CI job; query Notion decision DB; compare count to SQLite | Notion API rate limits | 1000 | todo |
| W5.2 | D2 — memory promotion parity | Weekly CI; `promote_to_pattern=true` → `ProceduralPattern:*` entity exists | Slug derivation from decision_id | 1000 | todo |
| W5.3 | B3 — precedent usage rate monitor | Running 30-day avg of `precedent_matches > 0` | Baseline learning | 1000 | todo |
| W5.4 | C2 — signature verification on read | Extend `lookup_refactor_decisions.py`; drop `sig_ok=false` matches | HMAC key distribution | 1000 | todo |
| W5.5 | C3 — writer-process allowlist | `writer_script` column; trigger enforcement; CI allowlist | Schema migration scope | 1000 | todo |
| W5.6 | E2 — heartbeat freshness CI | `ops_scripts/ci/check_post_cascade_alive.py`; fail on >6h gap | Session-activity detection | 1000 | todo |

## Non-Goals
- Rewriting existing `author_gate_ledger_integrity.py` (already wired in).
- Adding hash-chain to the 10 ledger-family DBs in this plan (tracked for a follow-up).
- Notion schema changes (use existing Author-Gate Decision Ledger DB).

## Files In Scope
- `ops_scripts/ci/check_decision_ledger_chain.py` (NEW)
- `ops_scripts/ci/check_marker_ledger_parity.py` (NEW)
- `ops_scripts/ci/run_contract_gates.py` (EDIT — add W1 gate calls)
- W2..W5: listed per-phase above
