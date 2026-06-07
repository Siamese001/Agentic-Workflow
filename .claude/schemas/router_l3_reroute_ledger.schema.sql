-- =====================================================================
-- Router L3/reroute Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every RerouteCeiling.attempt_reroute() decision from
-- agentic_core/L3_orchestration/exit_control/reroute_governance.py.
-- Constitutional §29 matrix row #6 (L3/reroute).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<request_id>",
--     "selected":            "allow" | "ceiling_exceeded",
--     "fingerprint":         "<sha256-12hex>",   -- per cell {max_reroutes}
--     "cell": { "max_reroutes": int },
--     "predicted_p_success": float,    -- = 1 - (count / max_reroutes), inverted
--     "eu_score":            float,    -- = max_reroutes - count (remaining headroom)
--     "request_id":          "...",
--     "current_count":       int,
--     "max_reroutes":        int
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l3_reroute_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l3_reroute_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (119, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l3_reroute: RerouteCeiling closed-loop §29 row #6 v1');
