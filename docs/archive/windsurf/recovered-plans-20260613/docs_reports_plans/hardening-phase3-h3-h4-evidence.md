# Hardening Phase 3: H3 + H4 Evidence

**Phase:** 3 / Wave 2
**Date:** 2026-02-18
**Branch:** adaptive_control
**Baseline:** ffbb3c860

---

## Objective

Implement H3 (provider-pinned LLM replay enforcement) and H4 (multivariate drift detection with ShiftReport schema).

## Scope Declaration

| File | Intent |
|---|---|
| `agentic_core/L2_execution/types/llm_replay_types.py` | New: ReplayBundle, ReplayMode, LLMReplayStrategy (H3) |
| `agentic_core/L5_safety/types/shift_report_types.py` | New: ShiftReport, CovariateShiftDetector, MMD+PSI (H4) |
| `tests/governance/test_llm_replay_enforcement.py` | New: 15 H3 governance tests |
| `tests/governance/test_shift_report.py` | New: 14 H4 governance tests |
| `docs/reports/plans/hardening-phase3-h3-h4-evidence.md` | This evidence file |

Planned impacted files: N=5

## H3: Provider-Pinned LLM Replay Enforcement

- `ReplayBundle` frozen dataclass with model_version, tokenizer_version, raw bytes, provider_checksum
- `ReplayMode` enum: RECORDED_OUTPUT (production default), DETERMINISTIC_INFERENCE (dev/test only)
- DETERMINISTIC_INFERENCE labeled NON_AUTHORITATIVE in all governance output
- `validate_production_mode()` rejects DETERMINISTIC_INFERENCE
- `LLMReplayStrategy` replays stored bytes or raises NotImplementedError for non-authoritative mode

### H3 Tests: 15 passed

```
TestReplayBundle: 6 tests (frozen, checksum sha256, deterministic, differs, verify pass/fail)
TestReplayModePolicy: 4 tests (production allows, dev allows, validate pass/reject)
TestGovernanceLabels: 4 tests (authoritative flags and labels)
TestLLMReplayStrategy: 3 tests (recorded output returns bytes, deterministic raises, labels)
```

## H4: Multivariate Drift Detection

- `ShiftReport` frozen dataclass with joint_shift, per_feature, mmd_score, psi_scores, sample_size_ok, timestamp
- `CovariateShiftDetector` with MMD (RBF kernel) + PSI (equal-width binning)
- Minimum sample guard: n < 30 skips detection
- Joint shift = MMD exceeds threshold OR any PSI exceeds threshold
- `ShiftReport.skipped()` factory for insufficient samples

### H4 Tests: 14 passed

```
TestShiftReportImmutability: 2 tests (frozen, timestamp set)
TestMinimumSampleGuard: 3 tests (constant=30, small skips, sufficient runs)
TestMMDDetection: 2 tests (identical no shift, shifted detected)
TestPSIDetection: 2 tests (per-feature flags, no drift low psi)
TestSkippedReport: 1 test (factory fields)
TestJointShiftLogic: 2 tests (mmd exceeds, psi exceeds)
```

## Full Governance Suite

```
python -m pytest tests/governance/ -q --tb=short

261 passed in 50.91s
```

Previous: 232 passed. Current: 261 passed (+29: 15 H3 + 14 H4).

## Acceptance

- [x] H3: 15/15 replay enforcement tests pass
- [x] H4: 14/14 shift report tests pass
- [x] Full governance suite: 261/261 pass
- [x] No regressions
- [x] Scope matches declaration (5 files)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

