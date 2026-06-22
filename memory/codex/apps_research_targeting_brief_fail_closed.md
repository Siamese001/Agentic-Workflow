# ProceduralPattern:AppsResearchTargetingBriefFailClosed

- INVARIANT: apps_research must not emit or hand off synthetic targeting briefs to apps_rg; missing grounded company_brief_text is a product failure, not a fallback opportunity.
- scope: apps_research CLI, apps_research targeting brief artifacts, generic L2 package-driven executor, apps_rg manual-brief handoff.
- enforcement: tests/unit/apps_research/test_cli_apps_rg_targeting_brief.py; tests/_apps_contract/test_apps_research_ag9_spine.py; tests/_apps_contract/test_w6_l2_package_driven_execution.py.
- canonical_pattern: run `python -m apps_research --target-company <company> --target-role <role> --jd <jd-path>`; only run apps_rg when the fresh run prints `artifact=<...briefing.md>`.
- do_not_do: do not reuse stale populated apps_research artifacts after a fresh run fails, and do not treat `--dry-run` as product evidence.
- discovered: 2026-06-21, validated: 2026-06-21.
