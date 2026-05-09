# W1 Implementation Plan — exec-summary length-parity remediation

## Files to Modify

1. **apps_rg/integrations/gates/per_cand_resume_gates.py**
   - Add asymmetric tolerance support to `length_parity_strict_gate`
   - Add `structural_slot_coverage_gate` (4 slots: archetype, quantified_outcomes, engagement_model, value_thesis)
   - Add `unsupported_appended_claim_gate` for repaired candidates
   - Update `per_cand_quality_composite_gate` to wire quantified_outcome_count for exec_summary

2. **apps_rg/integrations/hops/exec_summary_ensemble.py**
   - Rewrite all 6 prompt builders to use 4-sentence structural slots (sentence-count primary)
   - Set asymmetric tolerance: target=122, below=0.10, above=0.25 → [110, 153]
   - Import and use new gates from per_cand_resume_gates
   - Implement candidate-local repair loop (80-109 words, only if non-length gates pass)
   - Deterministic expansion using marquee_outcomes with provenance
   - Remove the retry-round approach (P99-140) - replaced by candidate-local repair

3. **apps_rg/integrations/hops/_ensemble_runner.py**
   - Extend Candidate dataclass to capture repair telemetry
   - Extend _archive_candidates to write enhanced scorecard with original/repaired word counts

4. **apps_rg/integrations/length_budget.py**
   - Add asymmetric tolerance support to LengthBudget dataclass

5. **tests/_apps_contract/test_w5_per_cand_gates.py**
   - Add tests for asymmetric tolerance
   - Add tests for structural_slot_coverage_gate
   - Add tests for unsupported_appended_claim_gate

6. **tests/_apps_contract/test_exec_summary_length_parity_remediation.py** (new file)
   - Test candidates at 68, 72, 76 words fail
   - Test candidate at 109 words can be repaired
   - Test candidate at 110 words passes without repair
   - Test candidate at 153 words passes
   - Test candidate at 154 words fails
   - Test candidate below 80 words does not get repaired
   - Test repair requires provenance-backed source
   - Test scorecard captures repair telemetry

## Implementation Order

1. Update length_budget.py with asymmetric support
2. Update per_cand_resume_gates.py with new gates and asymmetric tolerance
3. Update exec_summary_ensemble.py with new prompts and repair logic
4. Update _ensemble_runner.py with telemetry capture
5. Write tests

## Key Design Decisions

- **Sentence-count primary**: Exactly 4 sentences, each with content role. No "25-35 words per sentence" hard requirement.
- **Asymmetric tolerance**: -10%/+25% for exec_summary only (target 122 → [110, 153]). Bullets stay symmetric ±15%.
- **Candidate-local repair**: Each candidate evaluated independently. If non-length gates pass and word_count in [80, 109], append one provenance-backed marquee outcome.
- **Provenance**: Appended sentences must carry provenance refs. No invented claims.
- **Quality gates prevent padding**: quantified_outcome_count and structural_slot_coverage gates run before and after repair.
- **Scorecard telemetry**: Track original_word_count, repaired_word_count, repair_applied, repair_reason_code, appended_sentence_source_refs[].
