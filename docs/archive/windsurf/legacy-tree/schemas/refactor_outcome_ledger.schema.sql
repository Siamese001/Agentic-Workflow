-- =====================================================================
-- Refactor-Outcome Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures predicted vs actual outcomes of every refactoring wave.
-- event_kind values: "wave_prediction" | "wave_outcome" | "rollback_detected"
--
-- prediction_json shape:
--   {
--     "plan_slug": "<name>-<6hex>",
--     "wave_id": "W1.1",
--     "predicted_p0_delta": int,
--     "predicted_p1_delta": int,
--     "predicted_p2_delta": int,
--     "predicted_files_touched": int,
--     "predicted_tests_added": int,
--     "archetype": "CENTRAL_DEPENDENCY" | "ORCHESTRATOR" | "STATE_NODE" | "SAFETY_GATEKEEPER"
--   }
--
-- outcome_json shape:
--   {
--     "actual_p0_delta": int,
--     "actual_p1_delta": int,
--     "actual_p2_delta": int,
--     "actual_files_touched": int,
--     "actual_tests_added": int,
--     "rollback_within_7d": bool,
--     "guardian_residue": int,
--     "commit_sha_range": "<start>..<end>"
--   }
--
-- score_band values: "correct" | "partial" | "miss" | "rollback"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_refactor_outcome_kind
    ON events(event_kind)
    WHERE event_kind IN ('wave_prediction','wave_outcome','rollback_detected');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (102, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'refactor_outcome: wave prediction vs actual ledger v1');
