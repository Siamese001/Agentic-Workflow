-- =====================================================================
-- Router L3/sovereign_mcp Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every SovereignMcpRouter.resolve_violation() decision from
-- agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py.
-- Constitutional §29 non-matrix L3 router (final fleet-rollout router).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "<status>",       -- e.g. "l5_redteam", "l4_memory_recall", ...
--     "fingerprint":         "<sha256-12hex>", -- per cell {key_id_band, violation_class}
--     "cell": { "key_id_band": "L0|L1|L2|L3|L4|L5|other", "violation_class": "..." },
--     "predicted_p_success": float,    -- = 1.0 if authorized+initialized, else 0.0
--     "eu_score":            float,    -- = 1 if non-error status, 0 otherwise
--     "key_id":              int,
--     "file_path":           "...",
--     "violation_desc":      "...",
--     "tool":                "..." | null,    -- tool used by chosen branch
--     "authorized":          bool,
--     "initialized":         bool
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l3_sovereign_mcp_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l3_sovereign_mcp_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (121, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l3_sovereign_mcp: SovereignMcpRouter closed-loop §29 non-matrix v1');
