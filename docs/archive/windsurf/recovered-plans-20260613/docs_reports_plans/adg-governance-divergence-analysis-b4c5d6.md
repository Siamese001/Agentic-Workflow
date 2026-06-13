# ADG vs governance_hardening Branch Divergence Analysis

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary
The branches diverged at commit `1597b1138` on March 8, 2026, representing two parallel development tracks:
- **ADG**: Focused on pre-commit hooks and test governance enforcement
- **governance_hardening**: Focused on ADG feature enhancements (snapshots, diff, ownership, confidence, repair)

## Divergence Point
**Common ancestor**: `1597b1138` - "feat: Eliminate silent swallower anti-pattern - 640→0 violations"

## ADG Branch Changes (9 commits ahead)
**Focus**: Pre-commit governance and test enforcement

### Key Commits:
1. `2e8819646` - **Pre-commit hook for zero-skip policy**
   - Added T3a-skip hook in `.pre-commit-config.yaml`
   - Enforces zero-skip policy for UNIT_STRICT lane
   - Blocks commits with new pytest.skip() calls

2. `507a2f70b` - **Eliminate 81 skipped tests**
   - Removed all skipped tests in UNIT_STRICT lane
   - Enforced zero-skip governance

3. `588b1b49e` - **Harden Windsurf rules and CI gates**
   - Enhanced governance rules §15–§22
   - Strengthened CI enforcement

4. `94aba663f` - **ADG acceptance slice**
   - guardian-scope --file functionality
   - execute_ssot pre-run artifact integration

5. `73cf7a987` - **Complete ADG hardening**
   - CLI integration + comprehensive test coverage
   - 96.8% pass rate achievement

## governance_hardening Branch Changes (5 commits ahead)
**Focus**: ADG feature enhancements and analysis capabilities

### Key Commits:
1. `73ff02b94` - **Enhancements 6-10** (Major feature addition)
   - **snapshot.py**: CanonicalSnapshot with deterministic graph_hash
   - **diff.py**: GraphDiff comparing ADG(t-1) vs ADG(t)
   - **ownership.py**: OwnershipRegistry with blast_radius_report()
   - **confidence.py**: EdgeConfidence scoring (0.0-1.0)
   - **repair.py**: RepairRoute for violation routing
   - **75 new tests** in test_adg_enhancements_6_10.py

2. `d21842ec2` - **Resolve gaps 1-5**
   - G4 call graph integration
   - GT test traceability
   - GV layer violations detection
   - GG governance plane

3. `ea26ef38a` - **Fix ADG build**
   - Comprehensive dependency graph generation

4. `78ba9c827` - **ADG anti-pattern burndown**
   - 72 violations suppressed to 0 new

5. `e82ab8b1c` - **Phase 1-2 Anti-Pattern Burndown**
   - 1862→0 violations eliminated

## Impact Analysis

### Complementary Work
Both branches are **enhancing the ADG system** but from different angles:
- **ADG branch**: Governance enforcement and test compliance
- **governance_hardening**: Feature capabilities and analysis tools

### No Conflicts Detected
The changes appear to be **non-conflicting**:
- ADG branch: Pre-commit hooks, test policies, CI gates
- governance_hardening: New analysis modules, enhanced capabilities

### Integration Strategy
**Recommended approach**: Merge governance_hardening into ADG

#### Rationale:
1. **ADG has more recent commits** (March 10 18:17 vs 20:16)
2. **ADG includes governance hardening** that governance_hardening lacks
3. **governance_hardening adds new features** that complement ADG's governance focus
4. **Both branches target the same ADG system enhancement**

#### Merge Plan:
```bash
# On ADG branch
git checkout ADG
git merge governance_hardening
# Resolve any minor conflicts (unlikely)
# Test combined functionality
# Push merged result
```

## Next Steps
1. **Immediate**: Merge governance_hardening into ADG branch
2. **Validation**: Run full test suite to ensure compatibility
3. **Cleanup**: Delete governance_hardening after successful merge
4. **Documentation**: Update ADG documentation with new enhancements

## Risk Assessment
- **Low risk**: Changes are complementary and non-overlapping
- **Test coverage**: Both branches have comprehensive test coverage
- **Rollback**: Both branches have backup tags available

## Files Changed Summary
- **ADG branch**: 51 files, primarily CI/governance configuration
- **governance_hardening**: 8 files, primarily new ADG analysis modules
- **Combined**: Enhanced ADG system with both governance enforcement and advanced analysis capabilities

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

