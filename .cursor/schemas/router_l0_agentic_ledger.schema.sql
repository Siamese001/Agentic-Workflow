-- =====================================================================
-- Router L0/agentic Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every AgenticRouter.route() decision from
-- agentic_core/L0_routing/reasoning/agentic_router.py. Constitutional §29
-- non-matrix L0 router (audit row 2 of audit-identified non-matrix routers).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "<target_name>",  -- chosen route target
--     "fingerprint":         "<sha256-12hex>", -- per cell {intent, n_targets}
--     "cell": { "intent": "...", "n_targets": int },
--     "predicted_p_success": float,   -- = classifier confidence
--     "eu_score":            float,   -- = confidence - min_confidence (positive=above threshold)
--     "intent":              "<intent>",
--     "min_confidence":      float,
--     "had_classifier":      bool,
--     "fallback_to_keywords": bool
--   }
--
-- outcome_json shape (bound after handler dispatch):
--   {
--     "success":     bool,    -- True iff decision.error is None
--     "latency_ms":  int,
--     "error":       string|null
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l0_agentic_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l0_agentic_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (116, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l0_agentic: AgenticRouter closed-loop §29 non-matrix v1');
