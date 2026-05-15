-- =====================================================================
-- Router L6/promo Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every promotion-gate verdict from
-- agentic_core/L6_observability/promotion_gates.promotion_decision(). §29 row #9.
--
-- prediction_json shape:
--   {
--     "decision_id":     "<uuid4-hex>",
--     "selected":        "promote" | "reject",
--     "fingerprint":     "<sha256-12hex>",       -- per cell {min_n_each_arm, z}
--     "cell": { "min_n_each_arm": int, "z": float },
--     "predicted_p_success": float,              -- = candidate Wilson lower bound
--     "eu_score":            float,              -- = (candidate.lower - baseline.upper)
--     "candidate_successes": int,
--     "candidate_n":         int,
--     "baseline_successes":  int,
--     "baseline_n":          int,
--     "candidate_lower":     float,
--     "candidate_upper":     float,
--     "baseline_lower":      float,
--     "baseline_upper":      float,
--     "promote":             bool,
--     "verdict_reason":      "<short string from PromotionVerdict.reason>"
--   }
--
-- outcome_json shape (bound when post-promotion canary completes):
--   {
--     "success":              bool,    -- did the promoted candidate avoid rollback?
--     "latency_ms":           int,
--     "rolled_back":          bool,
--     "rollback_reason":      string|null
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l6_promo_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision','rollback_event');

CREATE INDEX IF NOT EXISTS idx_router_l6_promo_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision','rollback_event');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (112, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l6_promo: promotion_decision closed-loop §29 row #9 v1');
