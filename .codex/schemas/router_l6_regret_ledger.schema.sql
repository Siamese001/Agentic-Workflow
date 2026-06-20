-- =====================================================================
-- Router L6/regret Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every regret sample recorded via
-- agentic_core/L6_observability/regret_accounting.RegretLedger.record(). §29 row #10.
--
-- prediction_json shape (event_kind="route_decision"):
--   {
--     "decision_id":         "<RegretLedger sample's decision_id>",
--     "selected":            "<decision_layer>",        -- e.g. "L0", "L1", ...
--     "fingerprint":         "<sha256-12hex>",          -- per cell {decision_layer}
--     "cell": { "decision_layer": "L0..L6" },
--     "predicted_p_success": float,                     -- = chosen_reward in [0,1]
--     "eu_score":            float,                     -- = -regret (more negative = worse decision)
--     "chosen_reward":       float,
--     "best_alternative_reward": float,
--     "regret":              float                      -- non-negative
--   }
--
-- score_band semantics:
--   "tp" — predicted high reward AND received high reward (low regret)
--   "fp" — predicted high reward AND received low reward (chose poorly)
--   "tn" — predicted low reward AND received low reward
--   "fn" — predicted low reward AND received high reward
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l6_regret_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l6_regret_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (113, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l6_regret: RegretLedger.record closed-loop §29 row #10 v1');
