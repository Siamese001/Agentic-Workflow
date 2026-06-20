-- =====================================================================
-- Progress-ETA Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures ProgressReporter predicted ETA vs actual duration.
-- event_kind values: "eta_predicted" | "eta_realized"
--
-- prediction_json shape (at ProgressReporter.__init__):
--   {
--     "operation_name": str,
--     "predicted_total": int,
--     "predicted_eta_s": float,
--     "caller_location": "file:line"
--   }
--
-- outcome_json shape (at ProgressReporter.done()):
--   {
--     "actual_duration_s": float,
--     "actual_items_processed": int,
--     "overrun_ratio": float,        -- actual / predicted
--     "failed": bool
--   }
--
-- score_band values: "accurate" (|overrun-1|<0.2) | "slow" (overrun>1.2) | "fast" (overrun<0.8)
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_progress_eta_kind
    ON events(event_kind)
    WHERE event_kind IN ('eta_predicted','eta_realized');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (108, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'progress_eta: predicted vs actual progress duration v1');
