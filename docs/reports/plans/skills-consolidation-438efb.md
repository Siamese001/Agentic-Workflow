# Skills Consolidation Plan — 32 → 5 Canonical Skills

Consolidate 32 redundant skill directories into 5 canonical consolidated skills per SVP Engineering principles (operational simplicity, archival over deletion), archive replaced skills to `tools/archive/`, and update all references.

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1.1-P1.4 | Archive replaced skills, create directory structure | 45,000 | No active processes accessing skills | 🟢 GREEN | 27 skills archived, manifest created |
| Wave 2 | P2.1-P2.3 | Update RULES_INDEX.md to 5 consolidated skills | 25,000 | RULES_INDEX.md is current | 🟢 GREEN | Index shows only 5 canonical skills |
| Wave 3 | P3.1-P3.4 | Update .windsurfrules skill references | 35,000 | No other pending .windsurfrules edits | 🟢 GREEN | All refs point to consolidated skills |
| Wave 4 | P4.1-P4.3 | Create ADR, validate CI gates, final verification | 28,000 | CI gates use skill names not paths | 🟢 GREEN | CI passes, ADR created, 0 regressions |

**Total: 133,000 tokens across 4 waves, all GREEN** (Budget: 223,000 safe cap)

---

## Gap Register

**GAP-1: Consolidated skills claim to replace individual skills but both exist**
- 5 consolidated skills claim to replace 27 individual skills
- Creates confusion about which skill to invoke
- Risk of inconsistent enforcement across sessions

**GAP-2: Filename casing inconsistency**
- `skill.md` vs `SKILL.md` (e.g., `scope-guard/SKILL.md` vs `dedup-guard/skill.md`)
- Violates deterministic file naming conventions

**GAP-3: RULES_INDEX.md documents 15 skills but 32 directories exist**
- Documentation drift between actual state and intended state
- Creates ambiguity for maintenance and onboarding

**GAP-4: .windsurfrules references non-canonical skills**
- References `dependency-graph-analysis` but `graph-analysis` is the consolidated skill
- May cause skill invocation failures

---

## Execution Plan

### Wave 1 — Archive Replaced Skills

**Scope**: Archive 27 individual skills being consolidated while preserving history.

**Phase 1.1 — Create Archive Structure**
```bash
# Create archive directory for skills
mkdir -p tools/archive/.windsurf/skills/
mkdir -p tools/archive/.windsurf/skills/manifests/
```

**Phase 1.2 — Copy Individual Skills to Archive**
Copy these 27 skills to `tools/archive/.windsurf/skills/`:
- `agent-deletion-guard/`
- `artifact-management/` (consolidated into artifact-management)
- `boundary-enforcement/` (consolidated)
- `ci-grep-ban/`
- `ci-guardian-comments/`
- `ci-hollow-file/`
- `ci-integration/`
- `ci-layer-sovereignty/`
- `ci-schema-validation/`
- `dedup-guard/`
- `dependency-graph-analysis/`
- `evidence-bundle/`
- `graph-analysis/` (keep as canonical)
- `guardian-exemption-validator/`
- `hitl-decision-validator/`
- `import-hygiene/`
- `layer-boundary-guard/`
- `mcp-tool-verify/`
- `operational-gates/` (keep as canonical)
- `performance-monitor/`
- `plan-validation/`
- `powershell-guard/`
- `pre-write-orchestrator/`
- `progress-display/`
- `pytest-integrity/`
- `redis-hitl-gate/`
- `repair-gate-validator/`
- `rollback-gate/`
- `scope-guard/`
- `script-sprawl-guard/`
- `shim-discipline/`
- `skill-status-dashboard/`
- `ssot-write-gate/`
- `test-rigor-enforcement/`
- `testing-framework/` (keep as canonical)

**Phase 1.3 — Create Archive Manifest**
Create `tools/archive/.windsurf/skills/manifests/consolidation-archive-20260403.json` documenting:
- Archived skills list with original paths
- Consolidated skill mapping (which consolidated skill replaces which archived skills)
- Rationale per SVP Engineering principles
- Restoration procedure

**Phase 1.4 — Verify Archive Integrity**
```bash
# Verify all archived skills copied correctly
ls -la tools/archive/.windsurf/skills/ | wc -l
# Should show 27 skill directories + manifests/

# Verify manifest JSON is valid
python -c "import json; json.load(open('tools/archive/.windsurf/skills/manifests/consolidation-archive-20260403.json'))"
```

**Wave 1 Acceptance**:
- [ ] 27 skills copied to archive
- [ ] Manifest created with consolidation mapping
- [ ] Archive integrity verified
- [ ] Git status shows only new archive entries

---

### Wave 2 — Update RULES_INDEX.md

**Scope**: Align RULES_INDEX.md with consolidated skill structure.

**Phase 2.1 — Update Skills Table**
Replace skills table (lines 27-45) with 5 consolidated skills:

| # | Skill | Layer | Timing | Type | CI Gate | Pre-commit Hook | Status |
|---|-------|-------|--------|------|---------|----------------|--------|
| 1 | **graph-analysis** | Windsurf | Before work | Behavioural + Structural | None | None | ENFORCED |
| 2 | **boundary-enforcement** | Pre-commit | After work | Structural | ADG GV edges | T2a, T4a | ENFORCED |
| 3 | **operational-gates** | Both | Before work | Behavioural + Structural | `check_rollback_checkpoints.py` | T3a-rollback | ENFORCED |
| 4 | **testing-framework** | Pre-commit | After work | Structural | `adg_ci_lane_gate.py` | T3a-skip | ENFORCED |
| 5 | **artifact-management** | Pre-commit | After work | Structural | `validate_report_location.py` | T3b | ENFORCED |

**Phase 2.2 — Add Consolidation Note**
Add section after skills table explaining consolidation:
```markdown
## Skill Consolidation (2026-04-03)

**Previous State**: 32 individual skill directories
**Current State**: 5 consolidated canonical skills
**Archived Skills**: 27 individual skills archived to `tools/archive/.windsurf/skills/`
**Rationale**: SVP Engineering principle — operational simplicity through reduced moving parts

**Consolidation Mapping**:
- `graph-analysis` ← `dependency-graph-analysis`, `scope-guard`, `dedup-guard`
- `boundary-enforcement` ← `layer-boundary-guard`, `import-hygiene`, `shim-discipline`
- `operational-gates` ← `rollback-gate`, `mcp-tool-verify`
- `testing-framework` ← `test-rigor-enforcement`, `pytest-integrity`
- `artifact-management` ← `evidence-bundle`, `ssot-write-gate`, `progress-display`
```

**Phase 2.3 — Update Coverage Summary**
Update coverage table (lines 175-184) to reflect 5 skills:
| Category | Total | Enforced | Partial | Missing |
|----------|-------|----------|---------|---------|
| Constitutional Rules | 5 | 5 | 0 | 0 |
| Skills | 5 | 5 | 0 | 0 |
| CI Gates | 41 | 41 | 0 | 0 |
| Pre-commit Hooks | 25+ | 25+ | 0 | 0 |

**Wave 2 Acceptance**:
- [ ] Skills table shows only 5 consolidated skills
- [ ] Consolidation note added with mapping
- [ ] Coverage summary updated
- [ ] No broken internal links

---

### Wave 3 — Update .windsurfrules References

**Scope**: Update all skill references in `.windsurfrules` to point to canonical consolidated skills.

**Phase 3.1 — Identify Current References**
Search for skill name references in `.windsurfrules`:
```bash
# Find all skill name references
grep -n "dependency-graph-analysis\|scope-guard\|dedup-guard\|layer-boundary-guard\|import-hygiene\|shim-discipline\|rollback-gate\|mcp-tool-verify\|test-rigor-enforcement\|pytest-integrity\|evidence-bundle\|ssot-write-gate\|progress-display" .windsurfrules
```

**Phase 3.2 — Update References to Canonical Names**
Replace occurrences:
- `dependency-graph-analysis` → `graph-analysis`
- `scope-guard` → `graph-analysis`
- `dedup-guard` → `graph-analysis`
- `layer-boundary-guard` → `boundary-enforcement`
- `import-hygiene` → `boundary-enforcement`
- `shim-discipline` → `boundary-enforcement`
- `rollback-gate` → `operational-gates`
- `mcp-tool-verify` → `operational-gates`
- `test-rigor-enforcement` → `testing-framework`
- `pytest-integrity` → `testing-framework`
- `evidence-bundle` → `artifact-management`
- `ssot-write-gate` → `artifact-management`
- `progress-display` → `artifact-management`

**Phase 3.3 — Verify No Orphaned References**
```bash
# Verify all references now point to canonical skills
grep -E "skill.*graph-analysis|skill.*boundary-enforcement|skill.*operational-gates|skill.*testing-framework|skill.*artifact-management" .windsurfrules
```

**Wave 3 Acceptance**:
- [ ] All 13 replaced skill names updated to canonical
- [ ] No orphaned references to archived skills
- [ ] `.windsurfrules` remains valid (no syntax issues)

---

### Wave 4 — Create ADR and Final Validation

**Scope**: Document consolidation rationale and validate no CI regressions.

**Phase 4.1 — Create Consolidation ADR**
Create `docs/architecture/adr/adr-0042-skills-consolidation.md`:
- Title: ADR-0042: Consolidate 32 Skills to 5 Canonical Skills
- Context: Skill sprawl, overlapping responsibilities
- Decision: Consolidate per SVP Engineering principles
- Consequences: Reduced cognitive load, clearer authority

**Phase 4.2 — Validate CI Gates**
Verify CI gates don't reference archived skill paths:
```bash
# Check CI gates for archived skill references
grep -r "dependency-graph-analysis\|scope-guard\|dedup-guard\|layer-boundary-guard\|import-hygiene\|shim-discipline\|rollback-gate\|mcp-tool-verify\|test-rigor-enforcement\|pytest-integrity\|evidence-bundle\|ssot-write-gate\|progress-display" ops_scripts/ci/ || echo "No archived skill references found"
```

**Phase 4.3 — Run CI Contract Gates**
```bash
# Run contract gates to verify no regressions
python ops_scripts/ci/run_contract_gates.py
```

**Wave 4 Acceptance**:
- [ ] ADR created with consolidation rationale
- [ ] CI gates pass (no regressions)
- [ ] No archived skill references in CI scripts
- [ ] Git status shows clean consolidation

---

## Rules

1. **Archival over deletion**: Move skills to archive, don't delete
2. **Preservation of history**: All skill content preserved in `tools/archive/`
3. **Reference integrity**: All internal references updated to canonical skills
4. **Zero-regression**: CI gates must pass before completion
5. **Documentation**: ADR required explaining consolidation rationale

---

## Rollback Strategy

If consolidation causes issues:

1. **Restore from archive**: Copy skills from `tools/archive/.windsurf/skills/` back to `.windsurf/skills/`
2. **Revert RULES_INDEX.md**: Restore original skills table with 15 entries
3. **Revert .windsurfrules**: Restore skill name references
4. **Verify restoration**: Run CI gates to confirm pre-consolidation state

Rollback command sequence:
```bash
# Emergency rollback
git checkout HEAD -- .windsurf/skills/
git checkout HEAD -- .windsurf/RULES_INDEX.md
git checkout HEAD -- .windsurf/rules/.windsurfrules
rm -rf tools/archive/.windsurf/skills/
python ops_scripts/ci/run_contract_gates.py
```

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| Archived skills count | 27 | `ls tools/archive/.windsurf/skills/ \| wc -l` |
| Canonical skills in RULES_INDEX | 5 | Count rows in skills table |
| .windsurfrules orphaned refs | 0 | `grep -c "dependency-graph-analysis\|scope-guard\|..." .windsurfrules` |
| CI gates status | PASS | `python ops_scripts/ci/run_contract_gates.py` exit code |
| ADR created | Yes | File exists at `docs/architecture/adr/adr-0042-skills-consolidation.md` |

---

## Token Estimation Summary

**Per-wave breakdown using ContextWindowEstimator:**

| Wave | System | User | Files | Diffs | Est. Input | Reserved | Safety | Total | Status |
|------|--------|------|-------|-------|------------|----------|--------|-------|--------|
| 1 | 2,000 | 3,000 | 35,000 | 5,000 | 45,000 | 12,000 | 8,000 | 65,000 | 🟢 |
| 2 | 2,000 | 2,000 | 18,000 | 3,000 | 25,000 | 12,000 | 8,000 | 45,000 | 🟢 |
| 3 | 2,000 | 3,000 | 25,000 | 5,000 | 35,000 | 12,000 | 8,000 | 55,000 | 🟢 |
| 4 | 2,000 | 3,000 | 20,000 | 3,000 | 28,000 | 12,000 | 8,000 | 48,000 | 🟢 |
| **Total** | | | | | **133,000** | **48,000** | **32,000** | **213,000** | 🟢 |

**Budget utilization**: 213,000 / 223,000 safe cap = **95.5%** (safe margin: 10,000 tokens)
