-- =====================================================================
-- Router L1/c0 Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every L1 RetrievalRouter routing decision in
-- agentic_core/L1_cognition/reasoning/retrieval_router.py. Closed-loop
-- evidence per constitutional §29 row #3 (L1/c0).
--
-- See plan: .cursor/plans/closed-loop-router-fleet-rollout-d8f2a3.md
-- See rule: .cursor/rules/closed-loop-router-enforcement.md (row #3 L1/c0)
--
-- event_kind values:
--   "route_decision"  -- router chose a retrieval plan; outcome may bind later
--   "slo_miss"        -- post-hoc detection of an SLO violation; bound onto
--                        the original decision via late-binding
--
-- prediction_json shape (event_kind="route_decision"):
--   {
--     "decision_id":     "<uuid4-hex>",
--     "selected":        "<dim_tier>",            -- e.g. "tier_a", "tier_b", "tier_c"
--     "fingerprint":     "<sha256-12hex>",        -- per cell {intent_class, slo, allowed_tiers, ...}
--     "cell": {
--       "intent_class":  "CODE_LOCATOR" | "PROSE_FACTUAL" | ... ,
--       "slo":           "fast" | "standard" | "thorough",
--       "has_filters":   bool,
--       "compound":      bool
--     },
--     "predicted_p_success":  float,       -- prob the plan WILL fit SLO
--     "eu_score":             float,
--     "trace_id":             "<id>",
--     "route_id":             "L1/c0",
--     "plan": {                            -- the full plan_dict from RetrievalRouter
--       "query_transform":   "...",
--       "reranker_mode":     "...",
--       "reflective":        bool,
--       "dim_tier":          "...",
--       "collections":       ["..."],
--       "hydration_mode":    "...",
--       "implied_budget_ms": int,
--       "downgrades":        ["..."]
--     }
--   }
--
-- outcome_json shape:
--   {
--     "success":           bool,           -- did the plan satisfy SLO at runtime
--     "latency_ms":        int,            -- actual end-to-end retrieval latency
--     "implied_budget_ms": int,            -- echo of plan budget at decision time
--     "slo_budget_ms":     int,            -- the SLO floor
--     "results_returned":  int,            -- non-zero indicates retrieval served something
--     "downgraded":        bool            -- did plan_dict undergo downgrades
--   }
--
-- score_band values:
--   "tp"  -- predicted-success AND succeeded
--   "fp"  -- predicted-success AND failed (over-confidence)
--   "tn"  -- predicted-fail   AND failed
--   "fn"  -- predicted-fail   AND succeeded (under-confidence)
--   "unbound" -- outcome not yet attached
-- =====================================================================

-- Indexes specific to L1/c0 router queries
CREATE INDEX IF NOT EXISTS idx_router_l1_c0_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision','slo_miss');

CREATE INDEX IF NOT EXISTS idx_router_l1_c0_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision','slo_miss');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (111, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l1_c0: RetrievalRouter closed-loop §29 ledger v1');
