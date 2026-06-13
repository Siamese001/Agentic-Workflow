# Behavioral Learning Ultra Diff for .windsurfrules

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Plan to synthesize learnings from last 12 chats into rule improvements.

### Key Behavioral Patterns Identified:

**1. Evidence Contradiction Prevention**
- Pattern: Claims vs reality mismatches in evidence files
- Learning: Wave 2.3 claimed "pre-commit run --all-files passes" but actual output showed failures
- Rule Gap: No explicit rule requiring evidence verification before claims

**2. Scope Decontamination Discipline**
- Pattern: Unrelated files getting modified in scoped phases
- Learning: Phase 2.4 had to revert 13 unrelated files, keep only 7 prompt_gov files
- Rule Gap: Scope expansion detection exists but remediation process not codified

**3. Hard-Coded Bypass Anti-Patterns**
- Pattern: Temporary workarounds becoming permanent
- Learning: Phase 10 used hard-coded reference_strings whitelist, losing enforcement value
- Rule Gap: No rule prohibiting hard-coded bypasses in invariant tests

**4. Evidence File Location Violations**
- Pattern: Plans saved outside SSOT-approved locations
- Learning: RCA showed plans going to C:\Users\amita\.windsurf\plans instead of docs/reports/plans/
- Rule Gap: System guidance conflicts with constitutional rules

**5. Post-Commit Evidence Integrity**
- Pattern: Evidence files claiming success without verification
- Learning: Multiple phases required remediation when evidence didn't match reality
- Rule Gap: No rule requiring post-commit evidence verification

**6. Test Suite Isolation Requirements**
- Pattern: Test failures blocking unrelated work
- Learning: apps_rg test collection errors prevented Phase 10 completion
- Rule Gap: No rule for test suite impact isolation

### Ultra Diff Proposed:

**Add Rule §35: Evidence Contradiction Zero Tolerance**
- All evidence file claims MUST be verified with actual command outputs
- Any mismatch between claimed and actual results → IMMEDIATE FAIL
- Evidence files must contain raw outputs, not summaries

**Add Rule §36: Scope Decontamination Protocol**
- Before any phase commit, verify git diff --name-only matches declared scope
- If unrelated files present: MUST run decontamination protocol
- Document all reverted files with justification

**Add Rule §37: Hard-Coded Bypass Prohibition**
- Invariant tests MUST NOT use hard-coded whitelists or bypasses
- Temporary workarounds MUST have explicit expiration dates
- All bypasses MUST be documented in phase evidence with removal plan

**Add Rule §38: Evidence File SSOT Compliance**
- ALL plans, evidence, reports MUST go to docs/reports/plans/
- System guidance that conflicts with .windsurfrules MUST be ignored
- Files outside SSOT locations → constitutional violation

**Add Rule §39: Post-Commit Verification Mandate**
- After every commit, run verification suite
- Evidence file MUST include post-commit status
- Any post-commit failures require immediate remediation

**Add Rule §40: Test Impact Isolation**
- Test failures must not block unrelated structural work
- Create test isolation protocol for collection/import errors
- Document test suite status separate from phase acceptance

**Strengthen Rule §5A: Scope Budget Gate**
- Add explicit decontamination steps when scope expands
- Require scope justification file for any expansion
- Add scope violation tracking in evidence

**Strengthen Rule §16A: Evidence File Lock**
- Require evidence file pre-commit verification
- Add evidence contradiction detection
- Mandate raw output inclusion for all claims

### Implementation Approach:

1. Add new rules §35-§40 after existing §34
2. Strengthen existing rules with new behavioral constraints
3. Add evidence verification checklist to §16A
4. Update phase template to include scope decontamination steps

### Expected Impact:

- Prevent evidence contradictions like Wave 2.3
- Eliminate scope violations like Phase 10
- Prevent hard-coded bypasses in invariants
- Ensure SSOT compliance for all artifacts
- Improve post-commit verification discipline
- Isolate test failures from structural work

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

