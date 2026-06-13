# Branch Cleanup Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State
- **Current branch**: governance_hardening
- **Local branches**: 4 (ADG, governance_hardening, main, and possibly others)
- **Remote branches**: 60+ stale branches on origin
- **Issue**: Massive branch sprawl making repository difficult to navigate

## Cleanup Strategy

### Phase 1: Identify Stale Branches
1. Check which branches are merged into main
2. Identify branches with no recent activity
3. Check for duplicate/similar branches

### Phase 2: Safe Removal Process
1. **Local cleanup**: Remove merged local branches (except main, governance_hardening)
2. **Remote cleanup**: Coordinate with team before removing remote branches
3. **Preservation**: Keep branches that might have ongoing work

### Phase 3: Prevention
1. Establish branch naming conventions
2. Set up automated branch cleanup policies
3. Regular maintenance schedule

## Immediate Safe Cleanup (March 11, 2026)

### Analysis Results
- **Total remote branches**: 60+
- **Current branch**: governance_hardening (most recent: March 10, 2026)
- **Main branch**: March 10, 2026
- **ADG branch**: March 10, 2026 (active work)

### Branch Categories by Age

#### SAFE TO DELETE (Completed phases, old test branches)
```bash
# Phase-completed branches (early Feb 2026)
git push origin --delete agentic-5.4-phase_2_done
git push origin --delete agentic-model-v5.4-phase2_completed
git push origin --delete agentic-model-v5.4-phase3

# Test branches (completed work)
git push origin --delete test-sprawl
git push origin --delete test_consolidation
git push origin --delete test_deprecation
git push origin --delete heal_testing
git push origin --delete heal-router-testing

# Old feature branches (Feb 2026)
git push origin --delete feature/chat-session-20250214
git push origin --delete feature/prompt-modularization
git push origin --delete fix/prompt-modules-clean

# Duplicate branches
git push origin --delete qwen_migration  # duplicate of Qwen_migration
git push origin --delete meta_learning  # duplicate of meta-learning
```

#### REVIEW BEFORE DELETE (May have ongoing work)
```bash
# Architecture branches - check if still needed
git push origin --delete L2-Architecture
git push origin --delete L3_orchestration
git push origin --delete L5-to-L2-signal

# Infrastructure - verify dependencies
git push origin --delete Redis
git push origin --delete vLLM
git push origin --delete vLLM_config

# SSOT variants - check which is canonical
git push origin --delete SSOT_cleanup
git push origin --delete new_execute_ssot
```

#### KEEP (Active/Recent work)
- main, governance_hardening, ADG (current work)
- SSOT, SSOT-Mixins (core architecture)
- guardian, guardian-heal-orch (security)
- windsurf-skills-workflows (recent: Feb 19)
- execute_ssot (recent: March 8)

### Execution Commands
```bash
# Step 1: Backup before deletion
git tag backup-20260311-pre-cleanup main
git push origin backup-20260311-pre-cleanup

# Step 2: Delete safe branches (run in batches)
git push origin --delete agentic-5.4-phase_2_done agentic-model-v5.4-phase2_completed agentic-model-v5.4-phase3

# Step 3: Clean up local tracking branches
git remote prune origin
```

## Branch Categories for Review

### High Priority - Likely Safe to Delete
- Phase-specific branches: agentic-5.4-phase_2_done, agentic-model-v5.4-phase2_completed
- Test branches: test-sprawl, test_consolidation, test_deprecation
- Old feature branches: feature/chat-session-20250214
- Duplicate branches: meta-learning, meta_learning

### Medium Priority - Review Before Delete
- Architecture branches: L2-Architecture, L3_orchestration, L5-to-L2-signal
- Enhancement branches: enhancements, file_classification_enhancements
- Infrastructure: infrastructure, Redis, vLLM

### Low Priority - Keep
- Current work: governance_hardening, main
- Active features: SSOT, SSOT-Mixins, guardian
- Recent work: windsurf-skills-workflows

## Safety Measures
1. **Backup**: Create backup tags before deletion
2. **Communication**: Announce cleanup to team
3. **Verification**: Check for any open PRs before deletion
4. **Rollback**: Keep reflog for recovery if needed

## Next Steps
1. Team approval for remote branch cleanup
2. Execute local cleanup immediately
3. Schedule remote cleanup for maintenance window
4. Implement prevention policies

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

