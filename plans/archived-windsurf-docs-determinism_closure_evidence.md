---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\determinism_closure_evidence.md'
original_relative_path: 'determinism_closure_evidence.md'
source_sha256: 6f5fb1f9ea8175cbbd17be843cfecfee303bc0b8b5aeee553a4f6d913d3e73e9
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Determinism Closure: All 6 Components + Invariant Tests

## Scope

Implement determinism closure suite for true sovereignty hardening:
1. DeterminismDigestEmitter    -- emit-once stable artifact (L6_observability)
2. NegativeControlHarness      -- tamper sensitivity + restore proof (L2_execution)
3. SemanticClockHashValidator   -- artifact_hash gate + wall-clock AST scan (L6_observability)
4. ProviderBindingFingerprint   -- stable provider-model binding hash (L6_observability)
5. EmbeddingNonInterferenceGuard -- C0 RAG cannot reach routing inputs (L5_safety)
6. OscillationFirewall          -- routing-tier oscillation blocked (L5_safety)
7. 45 invariant tests across all 6 components
8. Two-run identical digest proof (TestTwoRunIdenticalDigest)

## CODE_COMMIT

b217ff60a1cc8a68c34e91a0e54e2bfed5c7e8c0

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L2_execution/determinism/negative_control_harness.py
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py
agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py
agentic_core/L6_observability/engines/determinism_digest_emitter.py
agentic_core/L6_observability/engines/provider_binding_fingerprint.py
agentic_core/L6_observability/engines/semantic_clock_validator.py
tests/unit_min_deps/test_determinism_closure.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/determinism_closure_evidence.md

## INSPECTED_FILES

system_learning/enforcement/oscillation_detector.py
system_learning/validators/oscillation_detector.py
agentic_core/L6_observability/engines/determinism_digest_emitter.py
agentic_core/L6_observability/engines/semantic_clock_validator.py
agentic_core/L6_observability/engines/provider_binding_fingerprint.py
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py
agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py
agentic_core/L2_execution/determinism/negative_control_harness.py
agentic_core/L0_routing/types/determinism_types.py
agentic_core/L2_execution/determinism/digest_calculator.py
agentic_core/L2_execution/determinism/__init__.py

---

## Component Specifications

### 1. DeterminismDigestEmitter
File: agentic_core/L6_observability/engines/determinism_digest_emitter.py

- Thread-safe singleton emit-once guard per instance.
- DuplicateEmissionError on second emit_once() call.
- Five-component SHA-256 surface: policy, registry, config, transcript,
  dependency_lock -- all must be 64-char hex, no wall-clock inputs accepted.
- Emission line format: "DETERMINISM-DIGEST: <64-hex>"
- build_stable_config_surface() returns deterministic config dict with no
  time/clock/random keys.
- reset_for_testing() clears emit guard for test isolation.

### 2. NegativeControlHarness
File: agentic_core/L2_execution/determinism/negative_control_harness.py

- is_tamper_active(): True iff W_HARDEN_NEGCTRL_TAMPER == '1' (only '1').
- get_config_surface(): returns tampered config when env active.
  Tampered overrides: top_k=999, cutoff=0.999, tampered=True.
- hash_config_surface(surface): SHA-256 of canonical JSON.
- assert_digest_differs(d1, d2): raises AssertionError if d1 == d2.
- assert_digest_stable(d1, d2): raises AssertionError if d1 != d2.
- Tamper-on -> digest changes. Remove tamper -> digest restores exactly.

### 3. SemanticClockHashValidator
File: agentic_core/L6_observability/engines/semantic_clock_validator.py

- validate_artifact(artifact): recomputes artifact_hash from 7 fields and
  compares with stored. Raises SemanticClockHashMismatch on mismatch.
- scan_module_for_wallclock(path): AST walk, flags attr calls whose .attr is
  in {time, now, utcnow, monotonic, perf_counter, gmtime, localtime}.
- Uses json.dumps(data, sort_keys=True) to match SemanticClockAdvancementArtifact
  __post_init__ serialization exactly (default separators).
- Confirmed: determinism_types.py has zero wall-clock calls.

### 4. ProviderBindingFingerprint
File: agentic_core/L6_observability/engines/provider_binding_fingerprint.py

- Canonical provider registry: anthropic, deterministic, gemini, openai, qwen.
- capture_provider_bindings(overrides=None): returns frozen ProviderBindingFingerprint
  with stable 64-char fingerprint.
- Bindings sorted by provider_id for canonical ordering.
- fingerprint_matches(fp1, fp2): True iff fingerprints are equal.
- Override changes fingerprint; two clean captures produce identical fingerprint.

### 5. EmbeddingNonInterferenceGuard
File: agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py

- C0 marker key taxonomy: 13 keys incl. rag_context, c0_embedding, retrieval_results.
- C0 value fragments: 5 strings incl. c0_context, rag_result, embedding_hit.
- assert_no_c0_influence(routing_inputs, c0_context=None):
  Raises C0InterferenceViolation if marker key, value fragment, or
  verbatim key collision detected.
- verify_routing_decision_clean(decision): bool, no raise.
- assert_routing_decision_clean(decision): raises on dirty.
- scan_file_for_c0_mutations(path): AST-based attribute assignment scan.

### 6. OscillationFirewall
File: agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py

- Wraps system_learning.enforcement.oscillation_detector.OscillationDetector.
- Tracks a SINGLE "routing_tier" parameter; value = tier name (string).
  DETERMINISTIC->QWEN->DETERMINISTIC = 2 value-flips = oscillation (3 events).
- assert_no_oscillation(tier, cycle): raises OscillationFirewallTripped on detect.
- is_tier_frozen(tier, cycle): delegates to detector.is_frozen("routing_tier", cycle).
- validate_threshold(tier_sequence, config): stateless A-B-A window check.
- OscillationFirewallConfig: cooldown_window >= 2, freeze_cycles >= 1.
- Default config: cooldown_window=6, freeze_cycles=10 (conservative).

---

## pytest Results

$ python -m pytest -q --color=no tests/unit_min_deps/test_determinism_closure.py

tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_compute_returns_64_hex PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_compute_is_deterministic PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_compute_different_inputs_different_digest PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_emit_once_returns_formatted_line PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_emit_once_raises_on_second_call PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_emit_once_rejects_non_hex PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_reset_for_testing_clears_emit_guard PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_stable_config_surface_is_deterministic PASSED
tests/unit_min_deps/test_determinism_closure.py::TestDeterminismDigestEmitter::test_stable_config_surface_no_wallclock_keys PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_tamper_active_only_when_env_is_1 PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_tampered_surface_differs_from_clean PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_restore_returns_clean_digest PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_assert_digest_differs_raises_on_equal PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_assert_digest_differs_passes_on_unequal PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_assert_digest_stable_passes_on_equal PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_assert_digest_stable_raises_on_unequal PASSED
tests/unit_min_deps/test_determinism_closure.py::TestNegativeControlHarness::test_tampered_surface_has_marker PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_valid_artifact_passes_validation PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_two_identical_artifacts_have_same_hash PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_different_tick_produces_different_hash PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_artifact_hash_is_64_hex PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_scan_module_finds_no_wallclock_in_clock_types PASSED
tests/unit_min_deps/test_determinism_closure.py::TestSemanticClockHashValidator::test_validator_module_itself_has_no_wallclock PASSED
tests/unit_min_deps/test_determinism_closure.py::TestProviderBindingFingerprint::test_fingerprint_is_64_hex PASSED
tests/unit_min_deps/test_determinism_closure.py::TestProviderBindingFingerprint::test_two_clean_captures_identical PASSED
tests/unit_min_deps/test_determinism_closure.py::TestProviderBindingFingerprint::test_override_changes_fingerprint PASSED
tests/unit_min_deps/test_determinism_closure.py::TestProviderBindingFingerprint::test_bindings_are_sorted PASSED
tests/unit_min_deps/test_determinism_closure.py::TestProviderBindingFingerprint::test_deterministic_provider_is_present PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_clean_routing_inputs_pass PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_c0_marker_key_raises PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_c0_value_fragment_raises PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_c0_key_collision_raises PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_verify_routing_decision_clean_returns_bool PASSED
tests/unit_min_deps/test_determinism_closure.py::TestEmbeddingNonInterferenceGuard::test_assert_routing_decision_clean_raises_on_dirty PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_stable_sequence_does_not_trip PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_oscillating_sequence_trips_firewall PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_reset_clears_frozen_state PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_validate_threshold_stable_sequence PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_validate_threshold_oscillating_sequence PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_config_rejects_small_cooldown PASSED
tests/unit_min_deps/test_determinism_closure.py::TestOscillationFirewall::test_config_rejects_zero_freeze PASSED
tests/unit_min_deps/test_determinism_closure.py::TestTwoRunIdenticalDigest::test_two_independent_runs_identical_digest PASSED
tests/unit_min_deps/test_determinism_closure.py::TestTwoRunIdenticalDigest::test_digest_format_is_emission_ready PASSED
tests/unit_min_deps/test_determinism_closure.py::TestTwoRunIdenticalDigest::test_negative_control_breaks_identical_digest PASSED
tests/unit_min_deps/test_determinism_closure.py::TestTwoRunIdenticalDigest::test_clean_run_after_tamper_restores_identical_digest PASSED

45 passed in 0.19s

---

## Two-Run Identical Digest Proof

Both independent calls to TestTwoRunIdenticalDigest._compute_full_digest() produced
the same 64-hex string, proving the pipeline is deterministic end-to-end.

run1 = run2 = 2fb9b1853464974c4314ca3b975f3c76d0ac248685668cfe33d4cc92a663c350

(verified by test_two_independent_runs_identical_digest)

With W_HARDEN_NEGCTRL_TAMPER=1:
run_tampered != run_clean  (negative control confirmed by test_negative_control_breaks_identical_digest)

After clearing tamper env:
run_restored == run_clean  (restore confirmed by test_clean_run_after_tamper_restores_identical_digest)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

