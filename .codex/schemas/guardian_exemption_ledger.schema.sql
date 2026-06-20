-- =====================================================================
-- Guardian-Exemption Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Tracks every "# guardian: allow-*" exemption and its downstream defect attribution.
-- event_kind values: "exemption_created" | "rca_link" | "exemption_retired"
--
-- prediction_json shape (at exemption creation):
--   {
--     "exemption_type": "allow-broad-except" | "allow-shell-true" | "allow-no-timeout" | ...,
--     "file_path": str,
--     "line": int,
--     "justification": str,
--     "approver": str,
--     "layer": "L*"
--   }
--
-- outcome_json shape (written by RCA-linker):
--   {
--     "attributed_defects": [{"rca_id": str, "confidence": "direct"|"probable"|"weak"}],
--     "defect_count": int,
--     "last_attributed_at": "ISO-8601",
--     "retired_at": null | "ISO-8601"
--   }
--
-- score_band values: "clean" (zero defects) | "flagged" (≥1 probable) | "hot" (≥1 direct)
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_guardian_exemption_kind
    ON events(event_kind)
    WHERE event_kind IN ('exemption_created','rca_link','exemption_retired');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (107, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'guardian_exemption: exemption lifecycle + RCA attribution v1');
