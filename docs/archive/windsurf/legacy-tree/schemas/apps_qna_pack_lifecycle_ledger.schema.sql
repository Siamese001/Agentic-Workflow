-- =====================================================================
-- apps_qna pack-lifecycle Ledger — extends ledger_base.schema.sql
-- =====================================================================
-- Captures every interview-pack build / lint / self-eval event from the
-- apps_qna domain.  Provides the durable record surface that W4 routers
-- (NamespaceBandit for route selection, paste-set bandit, Wilson CI
-- promotion gates) and W5 system_learning consume for cross-interview
-- transfer and flywheel promotion per constitutional §29.
--
-- event_kind values
--   "pack_build"          : a card pack was generated (W1.3 OTel-paired)
--   "pack_lint"           : lint pass executed (success / failure with reasons)
--   "pack_self_eval"      : self-eval comparison emitted (with prior pack)
--   "route_select"        : W4.1 NamespaceBandit chose a likely_questions route
--   "paste_set_select"    : W4.2 paste-set composition decision
--   "promote_decision"    : W4.3 Wilson CI verdict (promote / rollback)
--   "interview_outcome"   : W5 cross-interview transfer signal (post-rehearsal)
--
-- prediction_json shape (event_kind="pack_build"):
--   {
--     "interview_slug": str,
--     "interviewer": str | null,
--     "card_count": int,
--     "routes_covered": [str, ...],
--     "paste_set_size": int,
--     "paste_exceeds_chatgpt_limit": bool,
--     "template_set_version": str,
--     "builder_version": str
--   }
--
-- prediction_json shape (event_kind="route_select"):
--   {
--     "namespace": "apps_qna_likely_questions",
--     "candidate_routes": [str, ...],
--     "selected_route": str,
--     "posterior_alpha": float,
--     "posterior_beta": float,
--     "thompson_sample": float
--   }
--
-- prediction_json shape (event_kind="promote_decision"):
--   {
--     "candidate": str,
--     "baseline": str,
--     "wilson_lower": float,    -- must be ≥ 0.60 for promote
--     "z_score": float,         -- must be ≥ 1.96 for promote
--     "uplift": float,          -- must be > 0 for promote
--     "n_each_arm": int,        -- must be ≥ 30 for promote
--     "verdict": "promote" | "rollback" | "insufficient_evidence"
--   }
--
-- outcome_json shape (event_kind="pack_build", bound at lint/self-eval time):
--   {
--     "lint_passed": bool,
--     "lint_violations": [str, ...] | null,
--     "self_eval_drift": {"word_delta": int, "card_delta": int} | null
--   }
--
-- outcome_json shape (event_kind="route_select", bound post-rehearsal):
--   {
--     "actually_asked": bool,    -- did the interviewer probe this route?
--     "card_landed": bool        -- did the bound card resolve the answer?
--   }
--
-- score_band values
--   "pack_build":          "clean" | "lint_failed" | "self_eval_drift"
--   "route_select":         "hit"   | "miss"
--   "promote_decision":     "promote" | "rollback" | "insufficient_evidence"
-- =====================================================================

-- Indexes specific to apps_qna pack-lifecycle queries.
CREATE INDEX IF NOT EXISTS idx_apps_qna_kind_band
    ON events(event_kind, score_band)
    WHERE event_kind IN (
        'pack_build', 'pack_lint', 'pack_self_eval',
        'route_select', 'paste_set_select',
        'promote_decision', 'interview_outcome'
    );

-- Frequently-filtered context for cross-interview lookups.
CREATE INDEX IF NOT EXISTS idx_apps_qna_repo_area_kind
    ON events(repo_area, event_kind)
    WHERE event_kind IN (
        'pack_build', 'route_select', 'paste_set_select'
    );

-- Documented JSON schema version for this ledger.
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (114, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'apps_qna_pack_lifecycle: pack build / route-select / promotion v1');
