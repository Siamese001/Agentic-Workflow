-- =====================================================================
-- Prompt-Classifier Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures tier prediction (T0/T1/T2/T3) vs actual scope at response end.
-- event_kind values: "tier_prediction" | "tier_outcome" | "tier_flip"
--
-- prediction_json shape:
--   {
--     "predicted_tier": "T0" | "T1" | "T2" | "T3",
--     "signals_matched": ["structured_reasoning", "adg_health", ...],
--     "prompt_hash": "sha256:..."
--   }
--
-- outcome_json shape:
--   {
--     "actual_tier": "T0" | "T1" | "T2" | "T3",
--     "files_edited": int,
--     "lines_changed": int,
--     "layers_touched": ["L0","L2","L4"],
--     "sr_packet_emitted": bool,
--     "tier_flipped_mid_session": bool
--   }
--
-- score_band values: "correct" | "under_classified" | "over_classified"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_prompt_classifier_kind
    ON events(event_kind)
    WHERE event_kind IN ('tier_prediction','tier_outcome','tier_flip');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (103, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'prompt_classifier: tier prediction accuracy ledger v1');
