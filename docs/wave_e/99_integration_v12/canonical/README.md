# Canonical Requirement Graph v1.2

**Integration Wave:** F2 (Source Authoring for Remaining RED Families)
**Integration Date:** 2026-04-16
**Previous Version:** v1.1 (Wave F1 Integration)
**Next Version:** TBD

## Summary

Canonical v1.2 merges the F2 source-discovery and atom-upgrade proposals onto canonical v1.1. F2 registered six existing repo documents as SourceAuthorityRecords and upgraded nine atoms from WEAK_EVIDENCE to NORMATIVE where those sources truly support the claim. No schema drift occurred.

## Key Changes from v1.1

### Global Coverage
- **v1.1:** 0.776 YELLOW (45 NORMATIVE + 13 WEAK_EVIDENCE + 1 EXCLUDED = 59 atoms)
- **v1.2:** 0.931 GREEN (54 NORMATIVE + 4 WEAK_EVIDENCE + 1 EXCLUDED = 59 atoms)
- **Delta:** +0.155, bucket flip YELLOW → GREEN

### Family Bucket Changes

| Family | v1.1 Bucket | v1.2 Bucket | Reason |
|--------|-------------|-------------|--------|
| F01 | YELLOW | GREEN | F01.06 upgraded NORMATIVE via SRC-ADR-004 |
| F03 | YELLOW | GREEN | F03.04 upgraded NORMATIVE via SRC-ADR-004 |
| F04 | RED | RED | No change (F04.04 added supplementary binding only) |
| F07 | RED | YELLOW | F07.01, F07.02 upgraded NORMATIVE via SRC-ADR-002; F07.03 stays WEAK |
| F08 | RED | GREEN | F08.01, F08.03, F08.04, F08.05 upgraded NORMATIVE via SRC-ADR-003 |
| F09 | YELLOW | GREEN | F09.05 upgraded NORMATIVE via SRC-ADR-003 |

### Bucket Distribution

| Bucket | v1.1 Count | v1.2 Count | Families |
|--------|------------|------------|---------|
| GREEN | 5 | 9 | F01, F02, F03, F06, F08, F09, F10, F11, F12 |
| YELLOW | 4 | 2 | F05, F07 |
| RED | 3 | 1 | F04 only |

## Source Authority Records Added

Six new SourceAuthorityRecords were added by F2 (all pre-existing repo documents, no new authoring):

| ID | Title | Authority Class | Rank | Notes |
|----|-------|----------------|------|-------|
| SRC-ADR-001 | ADR-F25-int - Confidence-Scored Tiered Healing Dispatch Routing | ADVISORY | 6 | invalid_for_normative_use=True; ADVISORY supplement only |
| SRC-ADR-002 | Healer Retry Hardening Specification | ARCHITECTURAL | 4 | Supports F07.01, F07.02 |
| SRC-ADR-003 | Evaluation Pipeline Release Acceptance - Exit Control Gate | ARCHITECTURAL | 4 | Supports F08.01, F08.03, F08.04, F08.05, F09.05 |
| SRC-ADR-004 | L0 Decomposition Specification (L0a/L0b/L0c) | ARCHITECTURAL | 4 | Supports F01.06, F03.04 |
| SRC-ADR-005 | Replay Determinism Rules | ARCHITECTURAL | 4 | Supplementary for F04.04 |
| SRC-ADR-006 | Authority Hierarchy Invariants | ARCHITECTURAL | 4 | Supplementary for multiple families |

Total sources in v1.2: 12 (6 from v1 + 6 from F2)

## Atom Patches Applied

Ten atom patches were merged from F2 (9 NORMATIVE upgrades + 1 supplementary binding):

| Atom | v1.1 Evidence | v1.2 Evidence | Source(s) |
|------|---------------|---------------|-----------|
| F01.06 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-004 |
| F03.04 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-004 |
| F07.01 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-002 |
| F07.02 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-002 |
| F07.03 | WEAK_EVIDENCE | WEAK_EVIDENCE | SRC-INT-003, SRC-ADR-001 (ADVISORY only) |
| F08.01 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-003 |
| F08.03 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-003 |
| F08.04 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-003 |
| F08.05 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-003 |
| F09.05 | WEAK_EVIDENCE | NORMATIVE | SRC-INT-003, SRC-ADR-003 |
| F04.04 | WEAK_EVIDENCE | WEAK_EVIDENCE | SRC-INT-003, SRC-ADR-005 (supplementary) |

## Edges Updated

Two edges had their evidence_class upgraded from WEAK_EVIDENCE to NORMATIVE due to atom endpoint upgrades:

| Edge ID | v1.1 Evidence | v1.2 Evidence | Reason |
|---------|---------------|---------------|--------|
| INT-F08.04-F09.01-01 | WEAK_EVIDENCE | NORMATIVE | F08.04 upgraded NORMATIVE |
| INT-F09.05-F08.04-01 | WEAK_EVIDENCE | NORMATIVE | F09.05 upgraded NORMATIVE |

## Unchanged Artifacts

- **Families:** No new families, no family patches (families.yaml identical to v1.1)
- **Exclusions:** No new exclusions, no exclusion changes (exclusions.yaml identical to v1.1)
- **Interaction edges:** No new edges added (edges.yaml has same 26 edges as v1.1, with 2 evidence_class upgrades)

## Remaining Blockers

| ID | Blocker | Family Impact | Required Action |
|----|---------|---------------|-----------------|
| B3 | Context-assembly ADR | F04 RED 0.25 | Author dedicated ADR specifying attribution, no-private-substitute, idempotence. Highest remaining impact. |
| B2-partial | Normative escalation-target ADR | F07.03 WEAK | Promote healing_dispatch_routing_adr to normative via HITL, or author new ADR naming L3 as escalation target. |
| B6 | L3 orchestration charter ADR | F05.04 WEAK | Author L3 charter explicitly defining dispatch role. |
| B7 | 6 deferred interaction candidates (C1, C2, C3, C4, C6, C9) | Graph completeness | Downstream atoms / edge-kind patches required. |

## Validation Status

All F2 proposals passed schema validation:
- All SRC IDs match pattern `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`
- All locators are resolvable in-repo
- Every NORMATIVE upgrade cites ≥1 ARCHITECTURAL-rank source
- ADVISORY source (SRC-ADR-001) correctly NOT used to support NORMATIVE evidence_class
- No orphan family, atom, or edge references
- No duplicate IDs
- No advisory-only source used as sole support for NORMATIVE atom

## Integration QA Results

- **No orphan family references:** ✓
- **No orphan atom references:** ✓
- **No orphan edge endpoints:** ✓
- **No duplicate IDs:** ✓
- **No duplicate semantic atoms with same family_id + claim:** ✓
- **Every ACTIVE NORMATIVE atom has at least one valid authority binding:** ✓
- **Every EXCLUDED atom references a real OOS record:** ✓
- **No placeholder SRC IDs in canonical v1.2:** ✓
- **No advisory-only source used as sole support for NORMATIVE atom:** ✓
- **No sidecar markdown content copied into canonical schema fields:** ✓
- **No writes outside docs/wave_e/99_integration_v12/:** ✓

## Publishable?

**YES.** Canonical v1.2 is schema-valid, graph-integrity-verified, and ready for publication. The integration pass merged all F2 proposals without schema drift and documented all unresolved issues honestly.
