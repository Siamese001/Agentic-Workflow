-- =====================================================================
-- Router L4/uwg Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every DurableWriteGateway.commit() decision from
-- agentic_core/L4_state/uwg/durable_write_gateway.py. Constitutional §29
-- matrix row #7 (L4/uwg).
--
-- prediction_json shape:
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "commit" | "blocked",
--     "fingerprint":         "<sha256-12hex>",   -- per cell {source_surface, blast_radius}
--     "cell": { "source_surface": "...", "blast_radius": "..." },
--     "predicted_p_success": float,    -- = 1.0 when validation expected pass else 0.5
--     "eu_score":            float,    -- = 1.0 when committed, 0.0 when blocked
--     "validation_status":   "PASS" | "FAIL",
--     "block_stage":         "validation" | "lock_contention" | "",
--     "n_state_diffs":       int,
--     "n_target_surfaces":   int,
--     "tenant_id":           "..."
--   }
--
-- outcome_json shape:
--   {
--     "success":             bool,    -- True iff commit_receipt is not None
--     "latency_ms":          int,
--     "commit_receipt_id":   "..." | null,
--     "blocked_receipt_id":  "..." | null,
--     "n_refresh_receipts":  int,
--     "snapshot_after":      "..." | null
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l4_uwg_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l4_uwg_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (118, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l4_uwg: DurableWriteGateway closed-loop §29 row #7 v1');
