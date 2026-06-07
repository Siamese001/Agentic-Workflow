-- =====================================================================
-- Router L0/path Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every PathRouter.route_with_confidence() decision from
-- agentic_core/L0_routing/reasoning/path_router.py. Constitutional §29
-- non-matrix L0 router (audit row 1 of audit-identified non-matrix routers).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "A" | "B" | "C" | "D" | "R5",  -- chosen path
--     "fingerprint":         "<sha256-12hex>",  -- per cell {threshold, payload_class}
--     "cell": { "threshold": float, "payload_class": "..." },
--     "predicted_p_success": float,   -- = confidence input
--     "eu_score":            float,   -- = confidence - threshold (positive=proceed margin)
--     "abstain":             bool,    -- True iff R5 was chosen
--     "reason":              "<plan_abstain reason string>"
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l0_path_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l0_path_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (115, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l0_path: PathRouter closed-loop §29 non-matrix v1');
