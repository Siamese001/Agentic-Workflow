-- =====================================================================
-- Router L0/ensemble Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every EnsembleRouter.route() decision and its paired
-- update_outcome() outcome. Constitutional §29 non-matrix L0 router.
-- Replaces the in-memory MetaLearner state with durable backing so
-- ensemble learning survives process restarts.
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "<selected_agent>",
--     "fingerprint":         "<sha256-12hex>",   -- per cell {n_models, decision_strategy}
--     "cell": { "n_models": int, "decision_strategy": "..." },
--     "predicted_p_success": float,    -- = decision.confidence
--     "eu_score":            float,    -- = mean_confidence - std_confidence (margin)
--     "decision_strategy":   "weighted_voting" | "meta_learning" | "simple_voting",
--     "confidence":          float,
--     "uncertainty":         float,
--     "agent_agreement_score": float,
--     "n_base_models":       int
--   }
--
-- outcome_json shape:
--   {
--     "success":     bool,
--     "latency_ms":  int,
--     "meta_learner_target":    float,  -- 1.0 if success else 0.0
--     "model_weights_after": { "<model_name>": float, ... }
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l0_ensemble_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l0_ensemble_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (117, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l0_ensemble: EnsembleRouter durable meta-learner backing v1');
