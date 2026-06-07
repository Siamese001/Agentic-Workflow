-- =====================================================================
-- Memory-Recall Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Tracks which mem_recall_session_start entities actually informed the session.
-- event_kind values: "entity_recalled" | "entity_referenced" | "recall_hit_rate"
--
-- prediction_json shape (at session start):
--   {
--     "entity_name": str,
--     "entity_type": "ProceduralPattern" | "ProjectContext" | "ArchitecturalInvariant" | ...,
--     "observation_count": int,
--     "last_updated": "ISO-8601",
--     "session_id": str
--   }
--
-- outcome_json shape (at session end):
--   {
--     "referenced_in_response": bool,
--     "referenced_in_tool_args": bool,
--     "semantic_match_score": float,   -- vector_db similarity to session text
--     "reference_count": int
--   }
--
-- score_band values: "hit" | "partial" | "miss"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_memory_recall_kind
    ON events(event_kind)
    WHERE event_kind IN ('entity_recalled','entity_referenced','recall_hit_rate');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (109, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'memory_recall: recalled entity vs session-reference hit rate v1');
