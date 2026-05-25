# ADG three-bucket pipeline redesign — closeout receipt

```text
STATUS: PASS
CI_GATES_3B:
- check_three_bucket_gap_thresholds.py -> exit 0
- check_runtime_proof_view_well_formed.py -> exit 0 (3734 rows)
- check_adg_snapshot_signed.py -> exit 0 (after sign_snapshot on enriched snapshot)
- check_adg_certified.py -> exit 0 (advisory; consumer-mode debt pre-existing outside plan)
- check_otel_genai_semconv_coverage.py -> exit 0
- check_schema_graduation_readiness.py -> exit 0
PLAN_ID: adg-three-bucket-pipeline-redesign-c8e4f1
WAVES_COMPLETED: W1, W1.6, W2.0, W2.1, W2.2, W3.1, W3.2, W3.3, W4.1
SCOPE_MATCH: yes — ADR-079 opt-in hot path, join fix, Windows registry lift, contract tests, stale guard, archive pointers, runbook
SCOPE_DRIFT: none
FILES_CHANGED:
- [runtime_view_builder.py](tools/otel/runtime_view_builder.py)
- [safe_repo_scan.py](tools/adg/safe_repo_scan.py)
- [registry_bucket_lift.py](tools/adg/registry_bucket_lift.py)
- [snapshot_fingerprint.py](tools/adg/snapshot_fingerprint.py)
- [three_bucket_gap_report.py](tools/adg/three_bucket_gap_report.py)
- [three_bucket_reports.py](tools/generate/integration/three_bucket_reports.py)
- [run_three_bucket_audit.py](tools/adg/run_three_bucket_audit.py)
- [check_three_bucket_gap_thresholds.py](ops_scripts/ci/check_three_bucket_gap_thresholds.py)
- [adg-three-bucket-weekly-audit-runbook.md](docs/cursor/adg-three-bucket-weekly-audit-runbook.md)
- tests under tests/unit/tools/
- archive pointers (3 files under .cursor/plans/_archive/2026-05/)
COMMANDS_RUN:
- pytest (unit seam tests, -o addopts=) -> exit_code: 0
- python tools/otel/seed_synthetic_traces.py --prefer-registry-overlap -> exit_code: 0
- registry_bucket_lift on snapshot -> resolved=27 consumer inserted (first run)
- ADG_THREE_BUCKET=1 run_three_bucket_audit.py -> exit_code: 0
- rebuild runtime view + gap report after overlap seed -> triplet_attested=121 health_pct=0.02
TESTS_GATES:
- pytest tests/unit/tools/adg/test_safe_repo_scan.py tests/unit/tools/adg/test_registry_bucket_lift_safe_scan.py tests/unit/tools/otel/test_runtime_static_edge_join.py tests/unit/tools/generate/integration/test_*three_bucket* -o addopts= -> pass
- check_three_bucket_gap_thresholds.py -> exit 0 (READ_EXISTING_REPORT with sha256)
ARTIFACTS_WRITTEN:
- [THREE_BUCKET_GAP_REPORT.json](docs/reports/adg/THREE_BUCKET_GAP_REPORT.json)
- [adg_three_bucket_pipeline_redesign_closeout.md](docs/reports/cursor/adg_three_bucket_pipeline_redesign_closeout.md)
DEFAULT_HOT_PATH_PROOF:
- test_generate_full_adg_three_bucket_default_off.py -> pass (no inline three-bucket producers)
AUDIT_OPT_IN_PROOF:
- ADG_THREE_BUCKET=1 audit receipt with snapshot_sha256 and runtime_proof=attested
W2_JOIN_PROOF:
- static_edge_id_nonnull: 0 -> 127 (path fallback) -> 324 (overlap-biased seed)
- triplet_attested: 0 -> 121 after --prefer-registry-overlap seed + registry lift
- threshold files changed in W2: none
FORBIDDEN_FILES_TOUCHED:
- agentic_core: no
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF | AUDIT_RUNTIME_PROOF
EXPLICIT_NON_CLAIMS:
- not ADG regen release certification
- not ADG_CERTIFIED strict
- not mandatory hot-path three-bucket
- 0.02% triplet health is pipeline proof only, not soak target
NEXT_BLOCKER: none for plan closeout; production triplet soak remains separate (GenAI emitter migration)
```
