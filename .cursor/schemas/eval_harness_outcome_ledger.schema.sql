-- =====================================================================
-- Eval-Harness-Outcome Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures one row per AppSpecificEvaluator.evaluate_from_packet call
-- from the v6 Exit pipeline. Closes the feedback loop for audit BLOCKER
-- #10 (domain telemetry) and feeds W5.P6 CI gate + future calibration.
--
-- Plan: .cursor/plans/apps-eval-harness-parity-f8d4a2.md W5.P7
-- Constitutional §29 (closed-loop router evidence) — this ledger is the
-- evidence surface for the apps_* eval harness itself.
--
-- event_kind values:
--   "app_eval_bound"    — bound app-specific eval executed (pass or fail)
--   "app_eval_unbound"  — route had no app-contract ref (pass-through)
--   "app_eval_error"    — evaluator raised; pipeline fell through to unbound
--
-- prediction_json shape (mandatory fields):
--   {
--     "bound": bool,                       -- True if route carried an app-contract ref
--     "app_id": "apps_rg" | ...,           -- empty string if unbound
--     "task_class": "resume_generation" | ...,
--     "rubric_ref": "aer::apps_rg::resume_generation::v1",
--     "threshold_profile_ref": "atp::apps_rg::resume_generation::v1",
--     "overall_score": 0.0..1.0,
--     "overall_pass_threshold": 0.0..1.0,
--     "hitl_policy": "none" | "required_on_low" | "required_always",
--     "dim_count": int,
--     "dim_fail_count": int,
--     "dim_unknown_count": int,
--     "fail_reasons": [str, ...]           -- copied from AppSpecificEvalResult
--   }
--
-- outcome_json shape (populated when X2 aggregate decision is known):
--   {
--     "disposition": "ALLOW" | "DENY" | "ESCALATE" | "ABSTAIN" | "RETRY",
--     "rationale": "hitl_required_on_low" | "app_specific_eval_failed" | ...,
--     "failed_gate_ids": [str, ...],
--     "reason_codes": [str, ...]
--   }
--
-- score_band values:
--   "pass"          — bound and passed
--   "deny"          — bound, failed, guardrail hard fail
--   "escalate"      — bound, failed, HITL routed
--   "unknown"       — bound but could not score (output missing dim_scores)
--   "unbound"       — not evaluated (no app contract ref on route)
--   "error"         — evaluator raised
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_eval_harness_kind
    ON events(event_kind)
    WHERE event_kind IN ('app_eval_bound','app_eval_unbound','app_eval_error');

CREATE INDEX IF NOT EXISTS idx_eval_harness_repo
    ON events(repo_area)
    WHERE event_kind IN ('app_eval_bound','app_eval_unbound','app_eval_error');

INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (121, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'eval_harness_outcome: per-run ASE result ledger v1 (plan apps-eval-harness-parity-f8d4a2 W5.P7)');
