-- Phase D.3 cert-decision ledger DDL — per ADR-080 §6 and
-- plan `.windsurf/plans/runtime-cert-d3-cert-decision-ledger-85989c.md`.
--
-- This DDL is intentionally NOT registered in
-- `tools/ledgers/schema_registry.py` `LEDGER_REGISTRY`. Cert-decision
-- ledgers are domain data (one SQLite file per app), not intelligence
-- ledger audit events. Consequently `tools/ledgers/apply_schema.py`
-- (which iterates `LEDGER_REGISTRY` — verified 2026-05-01) will never
-- auto-apply this DDL. It is applied by
-- `tools.runtime_cert.decisions.cert_decision_ledger.ensure_cert_decision_ledger`
-- at first use.
--
-- File layout: `artifacts/ledgers/cert_decision_<app_name>.sqlite`.
--
-- CHECK constraints on the two status columns enforce the ADR-080
-- Phase D invariant AT THE PERSISTENCE LAYER, in addition to D.1's
-- `CertificationDecisionRecord.__post_init__`. Belt-and-suspenders:
-- if a tamperer issues `UPDATE ... SET runtime_certification_status_after
-- = 'RUNTIME_CERTIFIED'` directly against the SQLite file, the constraint
-- rejects the write. If the in-file `record_json` blob is mutated, D.1
-- re-validation on read rejects it.
--
-- Phase D does NOT certify any app. A `verdict = 'certify'` row still
-- carries `runtime_certification_status_after = 'NOT_CERTIFIED'` here;
-- scanner promotion to `RUNTIME_CERTIFIED` is Phase F (out of scope).

CREATE TABLE IF NOT EXISTS cert_decisions (
    decision_id                          TEXT    PRIMARY KEY,
    generated_at_utc                     TEXT    NOT NULL,
    app_name                             TEXT    NOT NULL,
    route_shape                          TEXT    NOT NULL,
    manifest_hash                        TEXT    NOT NULL,
    evidence_kind                        TEXT    NOT NULL,
    closeout_report_id                   TEXT    NOT NULL,
    closeout_report_hash                 TEXT    NOT NULL,
    trace_observed_n                     INTEGER NOT NULL,
    trace_observed_success_n             INTEGER NOT NULL,
    evidence_rate                        REAL    NOT NULL,
    wilson_lower                         REAL    NOT NULL,
    z_score                              REAL    NOT NULL,
    uplift                               REAL    NOT NULL,
    verdict                              TEXT    NOT NULL,
    failure_reasons_json                 TEXT    NOT NULL,
    next_review_utc                      TEXT    NOT NULL,
    runtime_certification_status_before  TEXT    NOT NULL
        CHECK (runtime_certification_status_before = 'NOT_CERTIFIED'),
    runtime_certification_status_after   TEXT    NOT NULL
        CHECK (runtime_certification_status_after  = 'NOT_CERTIFIED'),
    record_json                          TEXT    NOT NULL,
    inserted_at_utc                      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cert_decisions_app_manifest
    ON cert_decisions (app_name, manifest_hash);

CREATE INDEX IF NOT EXISTS idx_cert_decisions_closeout_report_hash
    ON cert_decisions (closeout_report_hash);

CREATE INDEX IF NOT EXISTS idx_cert_decisions_generated_at_utc
    ON cert_decisions (generated_at_utc);
