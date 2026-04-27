-- =====================================================================
-- Router L5/hitl Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every HITLApprovalGate.evaluate() decision from
-- agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py.
-- Constitutional §29 matrix row #8 (L5/hitl).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "approve" | "modify" | "reject" | "return_to_l1" | "escalate" | "pending",
--     "fingerprint":         "<sha256-12hex>",   -- per cell {verdict_class}
--     "cell": { "verdict_class": "approved|modified|rejected|escalated" },
--     "predicted_p_success": float,    -- = 1.0 if approve, 0.5 if modify, 0.0 if reject/escalate
--     "eu_score":            float,    -- = -latency_ms / 1000 (faster = better)
--     "verdict":             "...",
--     "review_requested":    bool,
--     "latency_ms":          float,
--     "disposition":         "ALLOW|RETRY|DENY|REROUTE|ESCALATE",
--     "stop_condition_violated": bool
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l5_hitl_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l5_hitl_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (120, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l5_hitl: HITLApprovalGate closed-loop §29 row #8 v1');
