-- =====================================================================
-- Deferred-Scope Calibration Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Tracks computed P-band at capture vs actual days-to-done on Wave/Phase rows.
-- event_kind values: "deferred_scope_capture" | "status_flip" | "band_drift"
--
-- prediction_json shape (at capture time):
--   {
--     "notion_row_id": "<uuid>",
--     "computed_p_band": "P1".."P5",
--     "impact_score": float,
--     "factors": {
--       "coverage_gap_pct": float,
--       "fan_in": int,
--       "layer": "L*",
--       "surface": "Security"|"Write"|"Execution"|"State"|"Observability"|"None"
--     },
--     "scorer_version": "v1" | "v2"
--   }
--
-- outcome_json shape (written by status-flip poller):
--   {
--     "final_status": "Done" | "In Progress" | "Dropped",
--     "days_to_done": int,
--     "was_reprioritized": bool,
--     "actual_p_band": "P1".."P5"   -- inferred from days_to_done distribution
--   }
--
-- score_band values: "aligned" | "drift" | "dropped"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_deferred_scope_kind
    ON events(event_kind)
    WHERE event_kind IN ('deferred_scope_capture','status_flip','band_drift');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (106, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'deferred_scope_calibration: P-band vs actual days-to-done v1');
