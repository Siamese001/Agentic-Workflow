-- =====================================================================
-- MCP-Invocation Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every mcp*_ tool call: latency, retries, hang attribution.
-- event_kind values: "mcp_call" | "mcp_retry" | "mcp_hang_bypass" | "mcp_serialization_violation"
--
-- prediction_json shape:
--   {
--     "server_id": "adg_sqlite" | "memory" | "notion" | ...,
--     "tool_name": "adg_edge_fanin",
--     "payload_bytes": int,
--     "expected_latency_ms": int    -- rolling p50 at call time
--   }
--
-- outcome_json shape:
--   {
--     "actual_latency_ms": int,
--     "retries": int,
--     "hang_bypass_triggered": bool,
--     "response_bytes": int,
--     "error_class": null | "TimeoutError" | "JSONDecodeError" | ...
--   }
--
-- score_band values: "fast" (p50), "slow" (p95), "hang" | "error"
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_mcp_invocation_kind
    ON events(event_kind)
    WHERE event_kind IN ('mcp_call','mcp_retry','mcp_hang_bypass','mcp_serialization_violation');

CREATE INDEX IF NOT EXISTS idx_mcp_latency ON events(score_band, latency_ms);

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (104, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'mcp_invocation: per-MCP-call telemetry ledger v1');
