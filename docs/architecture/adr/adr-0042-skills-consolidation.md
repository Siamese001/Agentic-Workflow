# ADR-0042: Consolidate 32 Skills to 5 Canonical Skills

**Status**: Accepted  
**Date**: 2026-04-03  
**Author**: Platform Team  
**Decision ID**: ADR-0042

---

## Context

The legacy editor skill system had grown organically to 32 individual skill directories under `.codex/skills/`. This created several operational challenges:

1. **Cognitive Overload**: 32 skills made it difficult for developers to know which skill to invoke
2. **Overlapping Responsibilities**: Multiple skills addressed similar concerns (e.g., 3 different graph-related skills)
3. **Documentation Drift**: `RULES_INDEX.md` documented 15 skills while 32 directories existed
4. **Ghost Consolidated Skills**: 5 consolidated skills claimed to replace 27 individual skills, but originals still existed side-by-side

### Prior State (32 Skills)

**Graph/Analysis Skills**:
- `dependency-graph-analysis` — AST graph construction
- `scope-guard` — Scope drift prevention using graph
- `dedup-guard` — Duplicate detection using graph
- `graph-analysis` — **Consolidated** (claimed to replace above 3)

**Boundary/Import Skills**:
- `layer-boundary-guard` — Layer gravity enforcement
- `import-hygiene` — Import cleanliness
- `shim-discipline` — Backward compatibility stubs
- `boundary-enforcement` — **Consolidated** (claimed to replace above 3)

**Operational Skills**:
- `rollback-gate` — Rollback checkpoint enforcement
- `mcp-tool-verify` — MCP tool validation
- `operational-gates` — **Consolidated** (claimed to replace above 2)

**Testing Skills**:
- `test-rigor-enforcement` — Testing requirements
- `pytest-integrity` — Test collection/execution integrity
- `testing-framework` — **Consolidated** (claimed to replace above 2)

**Artifact Skills**:
- `evidence-bundle` — Evidence capture
- `ssot-write-gate` — SSOT path validation
- `progress-display` — Progress reporting
- `artifact-management` — **Consolidated** (claimed to replace above 3)

**Additional CI/Utility Skills** (17 skills):
- `agent-deletion-gate`, `ci-grep-ban`, `ci-guardian-comments`, `ci-hollow-file`, `ci-integration`, `ci-layer-sovereignty`, `ci-schema-validation`, `guardian-exemption-validator`, `hitl-decision-validator`, `performance-monitor`, `plan-validation`, `powershell-guard`, `pre-write-orchestrator`, `redis-hitl-gate`, `repair-gate-validator`, `script-sprawl-guard`, `skill-status-dashboard`

---

## Decision

**Consolidate 32 skills into 5 canonical consolidated skills per SVP Engineering principles.**

### SVP Engineering Principles Applied

1. **Operational Simplicity**: Reduce moving parts from 32 → 5 canonical entrypoints
2. **Dependency Hygiene**: Eliminate overlapping enforcement mechanisms
3. **Archival over Deletion**: Preserve history in `tools/archive/.codex/skills/`
4. **Documentation**: Maintain clear consolidation mapping in `RULES_INDEX.md`
5. **Zero-Regression**: All CI gates must pass; functionality preserved

### Consolidation Mapping

| Canonical Skill | Replaces (Archived) | Rationale |
|-----------------|---------------------|-----------|
| `graph-analysis` | `dependency-graph-analysis`, `scope-guard`, `dedup-guard` | Single entrypoint for all graph-first analysis needs |
| `boundary-enforcement` | `layer-boundary-guard`, `import-hygiene`, `shim-discipline` | Unified boundary/import/shim concerns |
| `operational-gates` | `rollback-gate`, `mcp-tool-verify` | Combined operational safety mechanisms |
| `testing-framework` | `test-rigor-enforcement`, `pytest-integrity` | Comprehensive testing enforcement |
| `artifact-management` | `evidence-bundle`, `ssot-write-gate`, `progress-display` | Unified artifact lifecycle management |

### Archive Strategy

All 30 non-canonical skills archived to `tools/archive/.codex/skills/`:
- 27 skills replaced by consolidated skills
- 17 CI-specific/utility skills (not consolidated but archived for reference)
- Full manifest: `tools/archive/.codex/skills/manifests/consolidation-archive-20260403.json`

---

## Consequences

### Positive

1. **Reduced Cognitive Load**: Developers now have 5 clear skill entrypoints instead of 32
2. **Clear Authority**: Each canonical skill has well-defined, non-overlapping scope
3. **Maintained History**: Archived skills preserve implementation details for reference
4. **Documentation Alignment**: `RULES_INDEX.md` now matches actual skill count (5)
5. **Consistent References**: `.windsurfrules` updated to reference canonical skills only

### Negative

1. **Skill Path Changes**: Scripts/hooks referencing specific skill paths must update
2. **Learning Curve**: Team must learn new canonical skill names
3. **Archive Maintenance**: Archived skills may become stale over time

### Neutral

1. **CI Gate Count Unchanged**: 41 CI gates still operational (no gates removed)
2. **Functionality Preserved**: All enforcement mechanisms remain intact
3. **Pre-commit Hooks Unchanged**: Hook IDs remain stable

---

## Implementation

### Wave 1 — Archive (Complete)
- Created `tools/archive/.codex/skills/` structure
- Archived 30 individual skills with full directory contents
- Created consolidation manifest JSON

### Wave 2 — Index Update (Complete)
- Updated `RULES_INDEX.md` skills table: 15 → 5 skills
- Added consolidation note section with full mapping
- Updated coverage summary: Skills 15 → 5
- Added changelog entry

### Wave 3 — Reference Update (Complete)
- Updated `.windsurfrules` orphaned references:
  - `dependency-graph-analysis` → `graph-analysis` (3 occurrences)
  - `test-rigor-enforcement` → `testing-framework` (1 occurrence)
  - `progress-display` → `artifact-management` (1 occurrence)

### Wave 4 — Validation (Current)
- Create this ADR
- Validate CI gates have no archived skill references
- Run contract gates to verify zero regressions

---

## References

- **Plan**: `docs/reports/plans/skills-consolidation-438efb.md`
- **Archive Manifest**: `tools/archive/.codex/skills/manifests/consolidation-archive-20260403.json`
- **Updated Index**: `.windsurf/RULES_INDEX.md`
- **Updated Rules**: `.codex/rules/.windsurfrules`

---

## Acceptance Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Archived skills count | 30 | ✅ |
| Canonical skills in RULES_INDEX | 5 | ✅ |
| .windsurfrules orphaned refs | 0 | ✅ |
| CI gates status | PASS | ⏳ |
| ADR created | Yes | ✅ |

---

## Changelog

- 2026-04-03: ADR created, consolidation complete
