-- =====================================================================
-- Test-Selection Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- ADG-driven test triage: selection accuracy, regression coverage per change-set.
-- event_kind values: "triage_selection" | "test_run_outcome" | "missed_regression"
--
-- prediction_json shape:
--   {
--     "change_set_sha": str,
--     "changed_files": [str, ...],
--     "adg_selected_tests": [str, ...],
--     "selection_rationale": "fan_in" | "layer_critical" | "semantic_edge" | "full_suite",
--     "predicted_runtime_s": float
--   }
--
-- outcome_json shape:
--   {
--     "tests_passed": int,
--     "tests_failed": int,
--     "failed_tests": [str, ...],
--     "would_have_caught_regression_tests": [str, ...],   -- from later bisect or operator tag
--     "selection_precision": float,
--     "selection_recall": float,
--     "actual_runtime_s": float
--   }
--
-- score_band values: "clean" (no failures) | "caught" (failures caught by selection)
--                  | "missed" (regression in unselected test)
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_test_selection_kind
    ON events(event_kind)
    WHERE event_kind IN ('triage_selection','test_run_outcome','missed_regression');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (110, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'test_selection: ADG triage precision/recall ledger v1');
