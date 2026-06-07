-- =====================================================================
-- Router L0/bandit Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every NamespaceBandit.choose() routing decision and its paired
-- update() outcome from agentic_core/L0_routing/reasoning/namespace_bandit.py.
-- Constitutional §29 row #1.
--
-- The bandit already maintains in-memory Beta-Bernoulli posteriors. This
-- ledger adds DURABLE per-decision telemetry so:
--  - posteriors can be reconstructed/audited across process restarts
--  - cross-router calibration (L6/promo, L6/regret) can attribute outcomes
--    to specific (namespace, route) cells
--  - Author-Gate decisions about admissibility lists have evidence
--
-- prediction_json shape (event_kind="route_decision"):
--   {
--     "decision_id":         "<uuid4-hex>",
--     "selected":            "<route>",                  -- chosen route arm
--     "fingerprint":         "<sha256-12hex>",           -- per cell {namespace}
--     "cell": { "namespace": "<ns>", "admissible": ["..."] },
--     "predicted_p_success": float,    -- posterior mean at choose() time
--     "eu_score":            float,    -- Thompson-sampled value at choose()
--     "posterior_alpha":     float,    -- pre-update alpha for chosen arm
--     "posterior_beta":      float     -- pre-update beta for chosen arm
--   }
--
-- outcome_json shape (bound when update(success=...) is called):
--   {
--     "success":               bool,
--     "latency_ms":            int,
--     "posterior_alpha_after": float,
--     "posterior_beta_after":  float
--   }
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_router_l0_bandit_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision');

CREATE INDEX IF NOT EXISTS idx_router_l0_bandit_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (114, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l0_bandit: NamespaceBandit closed-loop §29 row #1 v1');
