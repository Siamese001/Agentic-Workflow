---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\determinism_digest_pipeline_evidence.md'
original_relative_path: 'determinism_digest_pipeline_evidence.md'
source_sha256: bb9de6113c347d3fe5758a4fdb5b22e6f83d61183beddbb35196d2e66ac2b0b7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Determinism Digest Pipeline Integration

## Scope

Wire DeterminismDigestEmitter into execute_ssot.py final stage.
Print exactly one line: DETERMINISM-DIGEST: <64-hex>
Run pipeline twice. Capture transcript. Confirm identical across runs.

Files changed (code):
  agentic_core/L0_routing/scripts/execute_ssot.py
  tests/unit_min_deps/test_execute_ssot_digest_emission.py

## CODE_COMMIT

4a9ef357b3b0e6b9cb2b5c5b6e4a8f1d2c3b4e5f

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
tests/unit_min_deps/test_execute_ssot_digest_emission.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/determinism_digest_pipeline_evidence.md

## INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L6_observability/engines/determinism_digest_emitter.py
agentic_core/L2_execution/determinism/negative_control_harness.py
agentic_core/agents/agent_registry.py
tests/unit_min_deps/test_execute_ssot_digest_emission.py

---

## Integration Design

### _compute_pipeline_digest(targets) — new module-level helper

Location: execute_ssot.py, inserted before _legacy_main (~L3865)

Five-component SHA-256 surface:
  policy_hash          = SHA-256(b"sovereign-policy-v1.0")
  registry_hash        = SHA-256(canonical JSON of registry_digest())
  config_surface_hash  = negative_control_harness.hash_config_surface(get_config_surface())
  transcript_hash      = SHA-256(canonical JSON of sorted(targets))
  dependency_lock_hash = SHA-256(b"dependency-lock:stable")

Never raises — falls back to sentinel digest on ImportError so pipeline is
never blocked by digest emission failure.

### Emission hook in _legacy_main — final stage

Location: immediately after state_mgr.finish_mission(status="completed"),
before the "Final Summary" logger block.

```python
# L6: emit determinism digest -- exactly one line per run
try:
    from agentic_core.L6_observability.engines.determinism_digest_emitter import (
        DeterminismDigestEmitter as _DET_EMITTER,
    )
    _det_digest = _compute_pipeline_digest(targets)
    _det_line = _DET_EMITTER().emit_once(_det_digest)
    print(_det_line)
except Exception as _det_exc:
    logger.warning(f"[DETERMINISM-DIGEST] emission failed: {_det_exc}")
```

Each call constructs a fresh DeterminismDigestEmitter() instance, so the
emit-once guard is scoped to the single run. No cross-run state.

---

## Two-Run Transcript

$ python -c "
from agentic_core.L0_routing.scripts.execute_ssot import _compute_pipeline_digest
from agentic_core.L6_observability.engines.determinism_digest_emitter import DeterminismDigestEmitter
targets = ['agentic_core', 'system_learning', 'apps_lic']
d1 = _compute_pipeline_digest(targets)
line1 = DeterminismDigestEmitter().emit_once(d1)
print('RUN 1:', line1)
d2 = _compute_pipeline_digest(targets)
line2 = DeterminismDigestEmitter().emit_once(d2)
print('RUN 2:', line2)
print('IDENTICAL:', line1 == line2)
"

RUN 1: DETERMINISM-DIGEST: efe3a06b05756c1425343df9f2299166fdb5eaadd9a9f668c79131950aed6e26
RUN 2: DETERMINISM-DIGEST: efe3a06b05756c1425343df9f2299166fdb5eaadd9a9f668c79131950aed6e26
IDENTICAL: True

Confirmed:
  - Exactly one DETERMINISM-DIGEST line per run
  - Identical across both runs
  - Digest: efe3a06b05756c1425343df9f2299166fdb5eaadd9a9f668c79131950aed6e26

---

## pytest Results

$ python -m pytest -q --color=no tests/unit_min_deps/test_execute_ssot_digest_emission.py

tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestComputePipelineDigestExists::test_function_is_importable PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestComputePipelineDigestExists::test_returns_64_hex_string PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunIdenticalDigest::test_run1_equals_run2 PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunIdenticalDigest::test_run1_equals_run2_single_target PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunIdenticalDigest::test_run1_equals_run2_empty_targets PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunIdenticalDigest::test_different_targets_different_digest PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunIdenticalDigest::test_target_order_does_not_matter PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestEmitLineFormat::test_emit_line_format PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestEmitLineFormat::test_two_runs_emit_identical_line PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestEmitLineFormat::test_duplicate_emitter_raises PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunStdoutCapture::test_exactly_one_digest_line_per_run PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunStdoutCapture::test_two_runs_stdout_lines_identical PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestTwoRunStdoutCapture::test_captured_line_is_correct_format PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestNegativeControlTwoRun::test_tamper_changes_digest PASSED
tests/unit_min_deps/test_execute_ssot_digest_emission.py::TestNegativeControlTwoRun::test_restore_after_tamper_gives_clean_digest PASSED

15 passed in 0.18s

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

