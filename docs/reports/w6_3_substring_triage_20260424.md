# W6.3 C_SUBSTRING SSOT Triage — 20260424

Total sites classified: **91**

## Category breakdown

| Category | Count | Disposition |
|---|---:|---|
| EXEMPT_DOC | 32 | Already exempt (docstring) — no action |
| LOG_MESSAGE | 21 | Add to SSOT probe exemption allowlist |
| ARGPARSE_HELP | 17 | Documentation (argparse help/description) — no migration |
| ACCIDENTAL_CONCAT | 8 | Convert to f-string with constant interpolation |
| TEMPLATE | 5 | Convert to f-string with constant interpolation |
| RAISE_ARG | 4 | Exception diagnostic text — no migration |
| PROSE_OUTPUT | 3 | Prose output (lines/body/markdown) — no migration |
| REGEX_PATTERN | 1 | Regex pattern literal — migration would corrupt |

## Per-site detail

### ACCIDENTAL_CONCAT (8 sites)

- `tools/reports/audit_notion_backlog_coverage.py:157` lit=`.windsurf/plans`
  - context: `"Deterministic reconciliation of `.windsurf/plans/*.md` vs Notion Wave/Phase Convergence DB.",`
- `tools/retrieval/coverage_report.py:136` lit=`.windsurf/plans`
  - context: `"Per plan `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md`: "`
- `ops_scripts/calibration/ledger_weekly_report.py:93` lit=`.windsurf/plans`
  - context: `"Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`",`
- `ops_scripts/ci/check_hardcoded_exclusions.py:257` lit=`docs/reports`
  - context: `"Known hardcoded exclusion-set violations as of baseline freeze. "`
- `ops_scripts/ci/check_mcp_sync_integrity.py:83` lit=`.windsurf/scripts`
  - context: `issues.append("global MCP config drift detected; run 'python .windsurf/scripts/sync_mcp_config.py'")`
- `ops_scripts/ci/check_mcp_sync_integrity.py:66` lit=`.windsurf/scripts`
  - context: `"AGENTS.md MCP Quick Reference drift detected; run 'python .windsurf/scripts/sync_mcp_config.py'"`
- `ops_scripts/verification/report_risk_weighted_test_gaps.py:71` lit=`artifacts/adg`
  - context: `sys.exit("ERROR: no adg_indexed_*.sqlite snapshot found under artifacts/adg/")`
- `system_learning/engines/cross_repo_system_learning_import.py:108` lit=`docs/reports`
  - context: `"/docs/reports/plans/cross-repo-system-learning-incorporation-",`

### ARGPARSE_HELP (17 sites)

- `agentic_core/adg/client/cli.py:699` lit=`artifacts/adg`
  - context: `help="Write artifacts/adg/scan_manifest.json after scan (A1)",`
- `agentic_core/adg/client/cli.py:714` lit=`artifacts/adg`
  - context: `help="Output path for artifact JSON (default: artifacts/adg/adg_canonical_artifact.json)",`
- `agentic_core/adg/client/cli.py:798` lit=`artifacts/adg`
  - context: `help="Output directory (default: artifacts/adg)",`
- `tools/adg/adg_repair.py:273` lit=`artifacts/adg`
  - context: `help="ADG artifacts directory (default: artifacts/adg)",`
- `tools/adg/adg_repair.py:299` lit=`artifacts/adg`
  - context: `help="ADG artifacts directory (default: artifacts/adg)",`
- `tools/calibration/__main__.py:46` lit=`docs/reports`
  - context: `help="Write JSON report here. Defaults to docs/reports/calibration/<fixture>_sweep.json.",`
- `tools/generate/graph_projection.py:944` lit=`artifacts/adg`
  - context: `"Examples:\n"`
- `tools/migration/ssot_path_literal_migrator.py:324` lit=`artifacts/adg`
  - context: `help="restrict to one literal (repeatable). e.g. --only-literal artifacts/adg",`
- `tools/migration/ssot_prefix_path_migrator.py:321` lit=`artifacts/adg`
  - context: `help="restrict to one literal (repeatable). Default: artifacts/adg only.",`
- `tools/graphdb/agent_integration/cli.py:259` lit=`artifacts/adg`
  - context: `epilog="""`
- `ops_scripts/calibration/ledger_weekly_report.py:128` lit=`docs/reports`
  - context: `help="Override output path (default: docs/reports/calibration/<YYYY-Www>.md)",`
- `ops_scripts/calibration/weekly_refresh.py:262` lit=`docs/reports`
  - context: `"Destination path for the drift report. Defaults to "`
- `ops_scripts/ci/check_exception_contract.py:240` lit=`artifacts/adg`
  - context: `help="Path to ADG sqlite (default: latest in artifacts/adg/)",`
- `ops_scripts/ci/check_test_harness_coverage.py:190` lit=`artifacts/adg`
  - context: `help="Path to ADG sqlite (default: latest in artifacts/adg/)",`
- `ops_scripts/ci/executor_theater_gate.py:407` lit=`artifacts/adg`
  - context: `help="Path to adg_indexed_*.sqlite (default: latest in artifacts/adg/)",`
- `ops_scripts/maintenance/migrate_reports_to_ssot.py:67` lit=`docs/reports`
  - context: `parser = argparse.ArgumentParser(description="Migrate report files into docs/reports.")`
- `infrastructure/utils/adg_health.py:299` lit=`artifacts/adg`
  - context: `epilog="""`

### EXEMPT_DOC (32 sites)

- `agentic_core/adg/artifact/normalizer.py:285` lit=`artifacts/adg`
  - context: `"""Converts an ADGArtifact into compact NormalizedGraph form.`
- `agentic_core/adg/artifact/normalizer_config.py:292` lit=`artifacts/adg`
  - context: `"""Converts an ADGArtifact into compact NormalizedGraph form.`
- `agentic_core/adg/runtime/behavioral_index.py:356` lit=`artifacts/adg`
  - context: `"""Locate the most-recent ADG SQLite artifact under ``artifacts/adg/``.`
- `agentic_core/L3_orchestration/reasoning/engines/adg_integration.py:163` lit=`artifacts/adg`
  - context: `"""Initialize ADG query client.`
- `agentic_core/L5_safety/identity/__init__.py:1` lit=`.windsurf/plans`
  - context: `"""L5 Identity sub-package — front-door principal resolution (G-04, L5 v4).`
- `agentic_core/L5_safety/validators/report_location_validator.py:266` lit=`docs/reports`
  - context: `"""`
- `tools/adg/adg_ci_gate.py:190` lit=`artifacts/adg`
  - context: `"""Record current phase to artifacts/adg_current_phase.json."""`
- `tools/adg/_run_stub_archive.py:1` lit=`artifacts/adg`
  - context: `"""One-shot runner: execute the archive plan from stub_archive_candidates.json.`
- `tools/calibration/__main__.py:1` lit=`docs/reports`
  - context: `"""CLI for the threshold-sweep harness.`
- `tools/debug/_adg_cleanup_oneshot.py:1` lit=`artifacts/adg`
  - context: `"""One-shot ADG cleanup using the now-fixed archiver.`
- `tools/debug/_backlog_two_pass.py:205` lit=`artifacts/windsurf`
  - context: `"""Count entries in artifacts/windsurf/*violations*.jsonl matching pattern."""`
- `tools/debug/_runtime_adg_coverage_audit.py:1` lit=`.windsurf/plans`
  - context: `"""Runtime ADG coverage audit — read-only diagnostic.`
- `tools/debug/_w6_2bc_runner.py:1` lit=`artifacts/adg`
  - context: `"""W6.2b+c runner: apply prefix codemod for non-artifacts/adg literals."""`
- `tools/debug/_w6_2b_only.py:1` lit=`docs/reports`
  - context: `"""W6.2b: apply prefix codemod for docs/reports literal only."""`
- `tools/eval/audit_wave_b_target_state.py:1` lit=`docs/reports`
  - context: `"""Wave B external-only target-state audit + freeze gates.`
- `tools/generate/infra_wiring_views.py:1` lit=`docs/reports`
  - context: `"""Post-generation ADG enrichment: infrastructure wiring violation views.`
- `tools/retrieval/coverage_report.py:2` lit=`.windsurf/plans`
  - context: `"""ADG ↔ ChromaDB coverage report.`
- `tools/adg/repair/__init__.py:1` lit=`artifacts/adg`
  - context: `"""ADG Repair Orchestrator Package.`
- `tools/adg/shared_modules/path_resolver.py:1` lit=`artifacts/adg`
  - context: `"""Shared path resolver for ADG tools — eliminates hardcoded Windows paths.`
- `tools/adg/shared_modules/path_resolver.py:30` lit=`artifacts/adg`
  - context: `"""Return ADG artifacts directory (artifacts/adg).`
- `tools/adg/shared_modules/path_resolver.py:68` lit=`artifacts/adg`
  - context: `"""Return ADG reports directory (artifacts/adg/reports)."""`
- `tools/adg/shared_modules/path_resolver.py:73` lit=`artifacts/adg`
  - context: `"""Return ADG snapshots directory (artifacts/adg/snapshots)."""`
- `tools/adg/prompt_assembly/retrieval/adapters.py:53` lit=`artifacts/adg`
  - context: `"""Find the latest file matching a glob pattern in artifacts/adg/."""`
- `tools/generate/validation/gates.py:177` lit=`artifacts/adg`
  - context: `"""Block if HIGH-severity antipatterns INCREASED vs prior run (P1 non-regression ratchet).`
- `tools/generate/validation/gates.py:241` lit=`artifacts/adg`
  - context: `"""Enforce non-regression ratchet for MEDIUM-severity antipatterns (P2 non-regression ratchet).`
- `tools/ingestion/adg_cards/symbol_emitter.py:72` lit=`artifacts/adg`
  - context: `"""Yield ``SymbolCard`` objects from the given ADG snapshot.`
- `ops_scripts/ci/check_snapshot_has_mvs.py:100` lit=`artifacts/adg`
  - context: `"""Return the snapshot file to inspect.`
- `ops_scripts/ci/check_w6_ap_velocity_kpi.py:2` lit=`artifacts/windsurf`
  - context: `"""KPI H3 — anti-pattern velocity per 1k LOC (plan W6.5).`
- `ops_scripts/ci/check_w6_trace_theater_kpi.py:2` lit=`artifacts/windsurf`
  - context: `"""KPI E3 — trace-theater growth per layer (plan W6.4).`
- `ops_scripts/ci/executor_theater_gate.py:115` lit=`artifacts/adg`
  - context: `"""Find latest adg_indexed_*.sqlite in artifacts/adg/."""`
- `ops_scripts/maintenance/migrate_reports_to_ssot.py:1` lit=`docs/reports`
  - context: `"""Move report artifacts under docs/reports according to SSOT-style rules."""`
- `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_manifest.py:1` lit=`docs/reports`
  - context: `"""`

### LOG_MESSAGE (21 sites)

- `agentic_core/adg/runtime/behavioral_index.py:362` lit=`artifacts/adg`
  - context: `logger.debug("[ADGBehavioralIndex] artifacts/adg/ not found — degraded mode")`
- `tools/adg/adg_ci_gate.py:181` lit=`artifacts/adg`
  - context: `print("    → Trace import edges in artifacts/adg_semantic_graph.json")`
- `tools/adg/refactor_accelerator.py:42` lit=`artifacts/adg`
  - context: `print("[RA] ERROR: No adg_indexed_*.sqlite found in artifacts/adg/", file=sys.stderr)`
- `tools/adg/structural_outputs.py:34` lit=`artifacts/adg`
  - context: `print("[structural_outputs] ERROR: No adg_indexed_*.sqlite found in artifacts/adg/", file=sys.stderr)`
- `tools/debug/_wave_c_filter.py:43` lit=`artifacts/adg`
  - context: `print("rewrote artifacts/adg/wave_c_targets.txt")`
- `tools/generate/generate_final_compliance_report.py:430` lit=`docs/reports`
  - context: `print("   JSON: docs/reports/plans/final_architectural_compliance_report_03242026.json")`
- `tools/generate/generate_final_compliance_report.py:431` lit=`docs/reports`
  - context: `print("   Markdown: docs/reports/plans/final_architectural_compliance_report_03242026.md")`
- `tools/generate/generate_full_adg.py:565` lit=`.windsurf/plans`
  - context: `print("[ERROR] See wave plan: .windsurf/plans/burn-down-syntax-errors-wave-plan-20260406.md")`
- `tools/ingestion/ingest_code.py:608` lit=`artifacts/adg`
  - context: `"No ADG snapshot found under artifacts/adg/adg_indexed_*.sqlite; "`
- `tools/retrieval/coverage_report.py:153` lit=`artifacts/adg`
  - context: `print("ERROR: no ADG snapshot under artifacts/adg/; run tools/generate_full_adg.py first.")`
- `ops_scripts/calibration/hotspot_defect_join.py:152` lit=`artifacts/adg`
  - context: `print("[hotspot_defect_join] no ADG snapshot found under artifacts/adg/",`
- `ops_scripts/ci/check_expected_wiring.py:296` lit=`docs/reports`
  - context: `f"\n{len(total_errors)} wiring assertion(s) failed. "`
- `ops_scripts/ci/check_ledger_coverage.py:102` lit=`.windsurf/scripts`
  - context: `print("  Fix: run `python .windsurf/scripts/post_commit_outcome_binder.py "`
- `ops_scripts/ci/check_post_cursor_agent_payload.py:119` lit=`.windsurf/scripts`
  - context: `f"    {_REQUIRED_IMPORT}\n"`
- `ops_scripts/ci/executor_theater_gate.py:347` lit=`artifacts/adg`
  - context: `print("[EXECUTOR_THEATER_GATE] ERROR: No ADG SQLite found in artifacts/adg/")`
- `ops_scripts/maintenance/root_cleanup.py:95` lit=`docs/reports`
  - context: `print("\n[1/4] Moving audit files to docs/reports/audit...")`
- `ops_scripts/maintenance/root_cleanup.py:99` lit=`docs/reports`
  - context: `print("\n[2/4] Moving assessment files to docs/reports/assessments...")`
- `ops_scripts/ci/author_gate/check_ledger_integrity.py:44` lit=`.windsurf/scripts`
  - context: `f"{unsealed} unsealed row(s). Run: python .windsurf/scripts/"`
- `ops_scripts/ci/author_gate/check_ledger_schema.py:52` lit=`.windsurf/scripts`
  - context: `"[check_ledger_schema] FAIL — drift detected. Run: python .windsurf/scripts/apply_ledger_schema.py"`
- `ops_scripts/ci/author_gate/check_outcome_coverage.py:130` lit=`.windsurf/scripts`
  - context: `"\nRemediation: run `python .windsurf/scripts/post_commit_outcome_binder.py` "`
- `infrastructure/utils/adg_health.py:346` lit=`artifacts/adg`
  - context: `logger.error("Searched: artifacts/adg/adg_indexed_*.sqlite")`

### PROSE_OUTPUT (3 sites)

- `tools/debug/_runtime_adg_coverage_audit.py:197` lit=`.windsurf/plans`
  - context: `lines.append("**Plan**: `.windsurf/plans/runtime-adg-coverage-audit-4f7a21.md`")`
- `ops_scripts/calibration/weekly_refresh.py:184` lit=`.windsurf/plans`
  - context: `"Plan: `.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md` §W4.P2",`
- `ops_scripts/calibration/weekly_refresh.py:219` lit=`docs/reports`
  - context: `"**🔴 At least one threshold shows alert-level drift.** "`

### RAISE_ARG (4 sites)

- `tools/debug/_adg_p1_ranked.py:14` lit=`artifacts/adg`
  - context: `raise FileNotFoundError("No ADG snapshot found in artifacts/adg/")`
- `tools/diag/scan_adg_import_orphans.py:34` lit=`artifacts/adg`
  - context: `raise SystemExit("No ADG snapshot found in artifacts/adg/")`
- `tools/guardian/guardian_sweep.py:32` lit=`artifacts/adg`
  - context: `raise FileNotFoundError("No ADG SQLite found in artifacts/adg/")`
- `ops_scripts/ci/adg_gates/gate_base.py:170` lit=`artifacts/adg`
  - context: `raise RuntimeError("No ADG SQLite file found in artifacts/adg/")`

### REGEX_PATTERN (1 sites)

- `ops_scripts/ci/check_deferred_scope_markers.py:50` lit=`.windsurf/plans`
  - context: `PLAN_GLOB_RE = re.compile(r"^\.windsurf/plans/.+\.md$")`

### TEMPLATE (5 sites)

- `tools/ledgers/_bootstrap_skills.py:99` lit=`.windsurf/plans`
  - context: `- Schema: `.windsurf/schemas/{spec.schema_file}``
- `tools/reports/audit_notion_backlog_coverage.py:175` lit=`.windsurf/plans`
  - context: `lines.append(f"- `.windsurf/plans/{p}.md`")`
- `ops_scripts/ci/check_agents_md_sync.py:66` lit=`.windsurf/scripts`
  - context: `f"AGENTS.md: {status}; add the markers and run 'python .windsurf/scripts/sync_mcp_config.py'"`
- `ops_scripts/ci/check_agents_md_sync.py:76` lit=`.windsurf/scripts`
  - context: `f"AGENTS.md: '{marker}' autogen block drifted from SSOT; run "`
- `ops_scripts/ci/check_post_cursor_agent_payload.py:83` lit=`.windsurf/scripts`
  - context: `f"tool_info. Replace with `{_REQUIRED_IMPORT}` (see "`
