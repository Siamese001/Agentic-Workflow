-- =====================================================================
-- Hotspot-vs-Defect Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Weekly join of mv_hotspot_centrality top-N vs actual 30-day defect/churn.
-- event_kind values: "hotspot_prediction" | "defect_join" | "coefficient_proposal"
--
-- prediction_json shape:
--   {
--     "adg_snapshot_id": "adg_indexed_MMDDYYYY_HHMM",
--     "predicted_rank": int,
--     "impact_score": float,
--     "layer": "L0".."L6",
--     "archetype": "CENTRAL_DEPENDENCY" | ...,
--     "node_id": int
--   }
--
-- outcome_json shape (written by weekly joiner):
--   {
--     "actual_defect_count_30d": int,
--     "actual_churn_30d": int,
--     "sc_ap_additions_30d": int,
--     "was_refactored": bool,
--     "rank_delta": int   -- predicted_rank - rank_by_defects
--   }
--
-- score_band values: "confirmed" | "over_predicted" | "under_predicted"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_hotspot_defect_kind
    ON events(event_kind)
    WHERE event_kind IN ('hotspot_prediction','defect_join','coefficient_proposal');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (105, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'hotspot_defect: rank vs defect-density ledger v1');
