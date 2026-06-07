-- =====================================================================
-- Ask-User-Question Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures enriched_choice_builder decisions surfaced via ask_user_question.
-- event_kind values: "enriched_choice" | "data_collection" | "test_fixture"
--
-- prediction_json shape:
--   {
--     "question": str,
--     "option_count": int,
--     "recommended_index": int | null,
--     "confidence_source": "explicit" | "heuristic_default",
--     "confidence_score": float,
--     "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
--     "telemetry_context": str
--   }
--
-- outcome_json shape:
--   {
--     "selected_index": int | null,
--     "matched_recommendation": bool,
--     "override": bool
--   }
--
-- score_band values: "aligned" (selected==recommended) | "override" (selected!=recommended) | "pending" (no selection yet)
-- =====================================================================

-- Indexes specific to ask_user_question queries
CREATE INDEX IF NOT EXISTS idx_auq_context_band
    ON events(repo_area, score_band)
    WHERE event_kind IN ('enriched_choice','data_collection','test_fixture');

CREATE INDEX IF NOT EXISTS idx_auq_confidence
    ON events(score_numeric)
    WHERE event_kind IN ('enriched_choice','data_collection','test_fixture');

-- Documented JSON schema version for this ledger
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (101, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'ask_user_question: enriched choice decision ledger v1');
