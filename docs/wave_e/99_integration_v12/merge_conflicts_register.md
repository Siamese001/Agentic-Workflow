# Canonical v1.2 Merge Conflicts Register

**Integration Wave:** F2 (Source Authoring for Remaining RED Families)
**Integration Date:** 2026-04-16

## Summary

No merge conflicts occurred during the F2 integration pass. All F2 proposals were compatible with canonical v1.1, and the merge executed cleanly without requiring conflict resolution.

## Conflict Resolution Log

| Conflict ID | Entity Type | Conflict Description | Resolution | Resolution Type |
|-------------|-------------|---------------------|------------|-----------------|
| N/A | N/A | No conflicts | N/A | N/A |

## Compatibility Checks

### Families
- **v1.1 families:** 12
- **F2 proposals:** 0 (empty)
- **Conflicts:** None
- **Resolution:** N/A (no changes proposed)

### Atoms
- **v1.1 atoms:** 59
- **F2 proposals:** 10 patches (no new atoms)
- **Conflicts:** None
- **Resolution:** All patches applied cleanly; no ID collisions

### Edges
- **v1.1 edges:** 26
- **F2 proposals:** 0 (empty)
- **Conflicts:** None
- **Resolution:** N/A (no changes proposed)
- **Note:** 2 edges had evidence_class upgraded automatically due to atom endpoint upgrades (not a conflict)

### Exclusions
- **v1.1 exclusions:** 3
- **F2 proposals:** 0 (empty)
- **Conflicts:** None
- **Resolution:** N/A (no changes proposed)

### Sources
- **v1.1 sources:** 6
- **F2 proposals:** 6 new sources
- **Conflicts:** None
- **Resolution:** All 6 new source IDs (SRC-ADR-001 through SRC-ADR-006) are unique and do not collide with existing sources

## ID Collision Check

| ID Space | v1.1 IDs | F2 Proposed IDs | Collisions | Resolution |
|----------|----------|-----------------|------------|------------|
| Family IDs | F01–F12 | None | 0 | N/A |
| Atom IDs | F01.01–F12.09 | None (patches only) | 0 | N/A |
| Edge IDs | INT-F01.03-F11.01-01 through INT-F12.08-F08.03-01 | None | 0 | N/A |
| Source IDs | SRC-RULE-001, SRC-RULE-002, SRC-INT-001–004 | SRC-ADR-001–006 | 0 | N/A |
| Exclusion IDs | OOS-001, OOS-002, OOS-003 | None | 0 | N/A |

**Result:** No ID collisions detected.

## Schema Compatibility

| Check | Result | Details |
|-------|--------|---------|
| F2 proposal field names match schema | PASS | All fields are from frozen schema |
| F2 proposal enum values match schema | PASS | All enum values are from frozen schema |
| F2 proposal ID formats match schema | PASS | All IDs match frozen ID conventions |
| F2 proposal entity types match schema | PASS | Only Family, Atom, Edge, Source, Exclusion types used |

## Reference Compatibility

| Check | Result | Details |
|-------|--------|---------|
| F2 atom family_id references | PASS | All family_id values reference existing families |
| F2 source authority_binding references | PASS | All source IDs in authority_binding exist in v1.1 or F2 proposals |
| F2 edge source_atom_id references | PASS | N/A (no new edges proposed) |
| F2 edge target_atom_id references | PASS | N/A (no new edges proposed) |
| F2 exclusion related_atoms references | PASS | N/A (no new exclusions proposed) |

## Conclusion

The F2 integration pass executed without any merge conflicts. All F2 proposals were compatible with canonical v1.1, and the merge was deterministic and clean. No conflict resolution was required.
