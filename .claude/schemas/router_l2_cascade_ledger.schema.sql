-- =====================================================================
-- Router L2/cascade Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every HealingRouter / ConfidenceAwareExecutor routing decision
-- in agentic_core/L2_execution/healers/. Closes constitutional §29 loop:
-- prediction → outcome → calibration → meta-learner.
--
-- See plan: .windsurf/plans/l2-cascade-router-closed-loop-wiring-c4d8a1.md
-- See rule: .windsurf/rules/closed-loop-router-enforcement.md (row #4)
--
-- event_kind values:
--   "route_decision"  — router chose a tier/provider; outcome may bind later
--   "route_outcome"   — late-arriving outcome (rare; usually bound on the
--                       same row via writer.bind_outcome rather than a new row)
--   "fallback_event"  — automatic Qwen→Flash demotion after health probe
--                       failure or dispatch error
--   "cost_demotion"   — Pro→Flash or Flash→Qwen demotion under budget pressure
--
-- prediction_json shape (event_kind="route_decision"):
--   {
--     "decision_id":     "<uuid4-hex>",        -- Cursor Agent marker decision_id
--     "tier":            "HIGH"|"MEDIUM"|"LOW"|"HITL",
--     "provider":        "deterministic"|"qwen"|"gemini_flash"|"gemini_pro"|"hitl",
--     "target_model":    "<model-id>",         -- e.g. Qwen/Qwen2.5-32B-Instruct-AWQ
--     "gate_applied":    "<gate-name>",        -- NO_OVERRIDE | GATE_1_RETRY_OVERRIDE | ...
--     "gemini_subtier":  ""|"FLASH"|"PRO",
--     "cost_demoted":    bool,
--     "fingerprint":     "<sha256-12hex>",     -- per cascade_calibrator.fingerprint
--     "predicted_p_success": float,            -- model's prior P(success | tier, cell)
--     "eu_score":        float,                -- Expected Utility used to choose tier
--     "confidence_input": float,               -- raw ConfidenceScore.score
--     "cost_budget_remaining_usd": float|null,
--     "app_name":        "<caller>",
--     "vllm_healthy":    bool|null             -- Qwen probe state at decision time
--   }
--
-- outcome_json shape (bound onto same row via writer.bind_outcome):
--   {
--     "success":           bool,
--     "tier_attempted":    "HIGH"|"MEDIUM"|"LOW",
--     "tier_used":         "HIGH"|"MEDIUM"|"LOW",       -- differs on cascade fallback
--     "fallback_reason":   ""|"qwen_health_probe_failed"|"qwen_unsuccessful:..."|...,
--     "model_used":        "<model-id>",
--     "latency_ms":        int,
--     "cost_usd_observed": float|null,
--     "error_code":        string|null,
--     "response_len_bytes": int|null,
--     "downstream_judge_score": float|null  -- when caller has post-hoc judge
--   }
--
-- score_band values:
--   "tp"  — predicted-success AND succeeded
--   "fp"  — predicted-success AND failed   (over-confidence; calibration miss)
--   "tn"  — predicted-fail   AND failed
--   "fn"  — predicted-fail   AND succeeded (under-confidence; calibration miss)
--   "unbound" — outcome not yet attached
--
-- score_numeric: Brier-component for the row = (predicted_p_success - actual)^2
--   where actual ∈ {0.0, 1.0}. Aggregating mean(score_numeric) over a band
--   yields the band's Brier score; lower is better-calibrated.
-- =====================================================================

-- Indexes specific to L2/cascade router queries
CREATE INDEX IF NOT EXISTS idx_router_l2_cascade_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN ('route_decision','route_outcome','fallback_event','cost_demotion');

-- Calibration scripts read by tier+provider+status for Wilson CI per band
CREATE INDEX IF NOT EXISTS idx_router_l2_cascade_status_kind
    ON events(status, event_kind)
    WHERE event_kind IN ('route_decision','route_outcome');

-- Documented JSON schema version for this ledger
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (110, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'router_l2_cascade: HealingRouter closed-loop §29 ledger v1');
