# Guardian Test Framework: Design Options & Recommendations

Guardian tests should operate as **pure reporting instruments** that track architectural health without blocking development, with optional agent-driven remediation for systematic fixes.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

### What Guardian Tests Do Now
- **Comprehensive validation** of SSOT structure, import safety, code quality, MRO integrity
- **Pure reporting** - no thresholds, no failures, just metrics tracking
- **Technical debt visibility** - violations are logged but don't block commits
- **Separation from pre-commit** - fast essential checks in pre-commit (<5s), comprehensive analysis in Guardian

### Guardian Test Categories
1. **SSOT Structure** (`test_comprehensive_structure.py`)
   - File placement validation (25 violations detected)
   - Package completeness (384 missing `__init__.py`)
   - Forbidden directory usage
   - Test file placement (578 misplaced)

2. **Code Quality** (`test_code_quality_metrics.py`)
   - File size/monolith detection
   - Cyclomatic complexity
   - Documentation coverage
   - Import organization

3. **Import Safety** (`test_import_safety.py`)
   - Ghost imports (512 detected)
   - Circular dependencies
   - Gravity leaks (300 detected)
   - Import waterfall violations (10 detected)

4. **MRO Integrity** (`test_mro_integrity.py`)
   - Diamond of Death detection
   - Inheritance conflicts

## Design Options

### Option 1: Pure Reporting (Current Implementation)
**Description:** Guardian tests run and generate reports showing pass/fail counts and violation details without any remediation.

**Pros:**
- ✅ Zero friction - never blocks development
- ✅ Clear visibility into technical debt
- ✅ Fast execution - just detection
- ✅ Developers maintain full control
- ✅ Easy to understand and maintain

**Cons:**
- ❌ Violations accumulate over time
- ❌ No automated cleanup
- ❌ Requires manual triage and fixing
- ❌ Technical debt can grow unchecked

**Use Cases:**
- CI/CD dashboards showing health trends
- Weekly/monthly architectural reviews
- Technical debt tracking and prioritization
- Compliance reporting

**Implementation Status:** ✅ **COMPLETE** (as of current session)

---

### Option 2: Manual Remediation with Scripts
**Description:** Guardian tests report violations + provide standalone scripts for common fixes (no agents).

**Pros:**
- ✅ Predictable, deterministic fixes
- ✅ No AI/LLM dependencies
- ✅ Fast execution
- ✅ Easy to review and audit
- ✅ Can be run selectively

**Cons:**
- ❌ Limited to pattern-based fixes
- ❌ Requires script maintenance
- ❌ Can't handle complex refactoring
- ❌ Still requires human decision-making

**Example Scripts:**
```python
# scripts/fix_missing_init_files.py
# scripts/move_misplaced_tests.py
# scripts/fix_import_order.py
# scripts/split_monolith_files.py
```

**Implementation Effort:** Medium (2-)

---

### Option 3: Agent-Driven Remediation (Autonomous)
**Description:** Guardian tests detect violations → Agents automatically fix them using existing healing infrastructure.

**Pros:**
- ✅ Fully autonomous - zero human intervention
- ✅ Handles complex refactoring
- ✅ Leverages existing `SovereignHealingEngine`
- ✅ Can learn from patterns
- ✅ Scales to entire codebase

**Cons:**
- ❌ Unpredictable changes
- ❌ Requires extensive testing
- ❌ Risk of breaking working code
- ❌ Hard to audit/review changes
- ❌ LLM costs for large-scale fixes

**Architecture:**
```
Guardian Test → Violation Report → HealingAgent → SovereignHealingEngine → MCP (Filesystem/Git)
```

**Existing Infrastructure:**
- `SovereignHealingEngine` - transactional healing with rollback
- `HealingTransaction` - backup/restore capability
- MCP clients - filesystem and git operations
- Healing strategies for different violation types

**Implementation Effort:** High (1-)

---

### Option 4: Hybrid - Reporting + Selective Agent Remediation
**Description:** Guardian tests report all violations. Agents fix only **safe, deterministic** violations (e.g., missing `__init__.py`, import order). Complex issues remain manual.

**Pros:**
- ✅ Best of both worlds
- ✅ Automated cleanup of mechanical issues
- ✅ Human oversight for complex changes
- ✅ Gradual automation - start small
- ✅ Configurable per violation type

**Cons:**
- ❌ More complex architecture
- ❌ Requires violation categorization
- ❌ Partial automation may confuse users

**Violation Categories:**
- **Auto-fixable:** Missing `__init__.py`, import order, trailing whitespace
- **Agent-assisted:** File moves, simple refactoring
- **Manual-only:** Complex refactoring, architectural changes

**Implementation Effort:** Medium-High ()

---

### Option 5: Interactive Remediation (User-Guided)
**Description:** Guardian tests run → Show violations → User selects which to fix → Agent applies fixes with approval.

**Pros:**
- ✅ User maintains control
- ✅ Can leverage agent intelligence
- ✅ Learn from user decisions
- ✅ Gradual trust building

**Cons:**
- ❌ Requires UI/CLI interaction
- ❌ Not fully automated
- ❌ Slower than autonomous

**Implementation Effort:** High ()

---

## Recommended Design: **Option 4 - Hybrid Approach**

### Why Hybrid is Best

1. **Pragmatic Balance**
   - Automate the boring, mechanical fixes (80% of violations)
   - Keep human oversight for architectural decisions (20% of violations)
   - Reduce technical debt without risk

2. **Leverages Existing Infrastructure**
   - `SovereignHealingEngine` already exists
   - Guardian tests already categorize violations
   - MCP clients handle file operations safely

3. **Incremental Adoption**
   - Start with safest fixes (missing `__init__.py`)
   - Gradually expand to more complex fixes
   - Build confidence over time

4. **Risk Mitigation**
   - Transactional healing with rollback
   - Git integration for easy revert
   - Dry-run mode for testing
   - Configurable per violation type

### Implementation Plan

#### Phase 1: Safe Auto-Fixes (Week 1)
**Target Violations:**
- Missing `__init__.py` files (384 instances)
- Import order violations
- Trailing whitespace
- Redundant import aliases

**Implementation:**
```python
# agentic_core/L0_maintenance/scripts/guardian_healer.py
class GuardianHealingStrategy:
    SAFE_AUTO_FIX_CATEGORIES = [
        "missing_init_files",
        "import_order",
        "whitespace"
    ]

    async def heal_guardian_violations(self, report: dict):
        for violation in report['violations']:
            if violation['category'] in self.SAFE_AUTO_FIX_CATEGORIES:
                await self.apply_fix(violation)
```

#### Phase 2: Agent-Assisted Fixes (Week 2)
**Target Violations:**
- Misplaced test files (578 instances)
- File moves to correct territories
- Simple refactoring

**Implementation:**
- Use LLM for context-aware decisions
- Require human approval for moves
- Generate PR with detailed explanation

#### Phase 3: Monitoring & Metrics (Week 3)
**Deliverables:**
- Dashboard showing fix success rates
- Technical debt reduction metrics
- Violation trend analysis
- Cost tracking (LLM usage)

### Configuration Example

```yaml
# .guardian_config.yaml
remediation:
  mode: hybrid  # pure_reporting | manual_scripts | agent_autonomous | hybrid | interactive

  auto_fix:
    enabled: true
    categories:
      - missing_init_files
      - import_order
      - whitespace
    max_fixes_per_run: 50
    require_approval: false

  agent_assisted:
    enabled: true
    categories:
      - misplaced_tests
      - file_moves
    require_approval: true
    create_pr: true

  manual_only:
    categories:
      - monolith_splitting
      - circular_dependencies
      - mro_violations
```

### Success Metrics

**Short-term (1 month):**
- 80% reduction in missing `__init__.py` files
- 50% reduction in import order violations
- Zero breaking changes from auto-fixes

**Long-term (3 months):**
- 60% reduction in total violations
- <5% manual intervention rate
- Positive developer feedback

### Risk Mitigation

1. **Dry-run mode** - Test fixes without applying
2. **Rollback capability** - Revert any fix instantly
3. **Git integration** - Every fix is a commit
4. **Approval gates** - Human review for risky changes
5. **Gradual rollout** - Start with 10% of violations

## Alternative Recommendation: Start with Option 1

If the team prefers **maximum safety** and **zero automation risk**, keep Option 1 (Pure Reporting) and add:

1. **Weekly review meetings** to triage violations
2. **Manual fix sprints** to reduce technical debt
3. **Violation trend dashboards** to track progress
4. **Documentation** on how to fix each violation type

This approach has **zero risk** but requires **more human effort**.

## Conclusion

**Recommended:** Option 4 (Hybrid) provides the best balance of automation, safety, and pragmatism. It leverages existing infrastructure, reduces technical debt systematically, and maintains human oversight for critical decisions.

**Alternative:** Option 1 (Pure Reporting) if the team values maximum control and is willing to invest manual effort in remediation.

**Not Recommended:** Option 3 (Full Autonomous) is too risky without extensive testing and validation infrastructure.

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

