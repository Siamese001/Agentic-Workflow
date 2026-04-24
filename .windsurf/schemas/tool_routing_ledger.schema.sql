-- =====================================================================
-- Tool-Routing Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every retrieval-class tool call Cascade makes.
-- event_kind values: "retrieval_tool_choice" | "routing_violation" | "fallback_recovery"
--
-- prediction_json shape:
--   {
--     "query_features": {
--       "mentions_import": bool,
--       "targets_symbol": bool,
--       "targets_allcaps": bool,
--       "asks_blast_radius": bool,
--       "asks_layer": bool,
--       "is_literal_search": bool
--     },
--     "chosen_tool": "mcp1_adg_edge_fanin" | "grep_search" | "mcp4_read_text_file" | ...,
--     "routing_reason": "decision_tree_rule_3" | "operator_override" | "degraded_fallback"
--   }
--
-- outcome_json shape:
--   {
--     "backend_used": "redis_cache" | "sqlite" | "degraded_grep",
--     "result_count": int,
--     "classification_correct": bool,   -- was chosen tool actually optimal post-hoc?
--     "fallback_triggered": bool
--   }
--
-- score_band values: "correct" | "miss" | "degraded"
-- =====================================================================

-- Indexes specific to tool-routing queries
CREATE INDEX IF NOT EXISTS idx_tool_routing_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('retrieval_tool_choice','routing_violation','fallback_recovery');

-- Documented JSON schema version for this ledger
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (101, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'tool_routing: retrieval-tool choice ledger v1');
