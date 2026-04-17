# Canonical v1.2 Coverage Report

**Integration Wave:** F2 (Source Authoring for Remaining RED Families)
**Integration Date:** 2026-04-16
**Previous Version:** v1.1

## Executive Summary

Global coverage improved from **0.776 YELLOW** to **0.931 GREEN**, a +0.155 delta. Nine atoms were upgraded from WEAK_EVIDENCE to NORMATIVE, and two edges were upgraded accordingly. F08 moved from RED 0.20 to GREEN 1.00 (full closure), F07 moved from RED 0.25 to YELLOW 0.75 (partial closure), and F01, F03, F09 all flipped from YELLOW to GREEN. F04 remains RED 0.25 unchanged.

## Global Coverage Metrics

| Metric | v1.1 | v1.2 | Delta |
|--------|------|------|-------|
| Total atoms | 59 | 59 | 0 |
| NORMATIVE atoms | 45 | 54 | +9 |
| WEAK_EVIDENCE atoms | 13 | 4 | -9 |
| EXCLUDED atoms | 1 | 1 | 0 |
| Coverage score | 0.776 | 0.931 | +0.155 |
| Bucket | YELLOW | GREEN | FLIP |

## Family-Level Coverage

| Family | Title | v1.1 Score | v1.2 Score | v1.1 Bucket | v1.2 Bucket | Atoms (N/W/E) | Delta |
|--------|-------|------------|------------|-------------|-------------|---------------|-------|
| F01 | Request Intake | 0.83 | 1.00 | YELLOW | GREEN | 6/0/0 | +0.17 |
| F02 | L1 Reasoning | 1.00 | 1.00 | GREEN | GREEN | 5/0/0 | 0.00 |
| F03 | L0 Route | 0.75 | 1.00 | YELLOW | GREEN | 4/0/0 | +0.25 |
| F04 | Context Assembly | 0.25 | 0.25 | RED | RED | 1/3/0 | 0.00 |
| F05 | L3 Orchestration | 0.75 | 0.75 | YELLOW | YELLOW | 3/1/0 | 0.00 |
| F06 | L2 Task Execution | 1.00 | 1.00 | GREEN | GREEN | 5/0/0 | 0.00 |
| F07 | Heal/Retry/Recovery | 0.25 | 0.75 | RED | YELLOW | 3/1/0 | +0.50 |
| F08 | Exit Spine | 0.20 | 1.00 | RED | GREEN | 5/0/0 | +0.80 |
| F09 | Universal Write Gate | 0.80 | 1.00 | YELLOW | GREEN | 5/0/0 | +0.20 |
| F10 | L4 Durable Archive | 1.00 | 1.00 | GREEN | GREEN | 3/0/0 | 0.00 |
| F11 | L5 Policy/Safety | 1.00 | 1.00 | GREEN | GREEN | 7/0/0 | 0.00 |
| F12 | L6 Observability | 1.00 | 1.00 | GREEN | GREEN | 7/0/1 | 0.00 |

**Legend:** N = NORMATIVE, W = WEAK_EVIDENCE, E = EXCLUDED

## Bucket Distribution

| Bucket | v1.1 Count | v1.2 Count | Families |
|--------|------------|------------|---------|
| GREEN | 5 | 9 | F01, F02, F03, F06, F08, F09, F10, F11, F12 |
| YELLOW | 4 | 2 | F05, F07 |
| RED | 3 | 1 | F04 only |

## Atom-Level Changes

### Upgraded WEAK → NORMATIVE (9 atoms)

| Atom | Family | v1.1 Evidence | v1.2 Evidence | Source(s) Added |
|------|--------|---------------|---------------|-----------------|
| F01.06 | F01 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-004 (L0_DECOMPOSITION_SPEC) |
| F03.04 | F03 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-004 (L0_DECOMPOSITION_SPEC) |
| F07.01 | F07 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-002 (HEALER_RETRY_HARDENING_SPEC) |
| F07.02 | F07 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-002 (HEALER_RETRY_HARDENING_SPEC) |
| F08.01 | F08 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-003 (eval_pipeline_acceptance) |
| F08.03 | F08 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-003 (eval_pipeline_acceptance) |
| F08.04 | F08 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-003 (eval_pipeline_acceptance) |
| F08.05 | F08 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-003 (eval_pipeline_acceptance) |
| F09.05 | F09 | WEAK_EVIDENCE | NORMATIVE | SRC-ADR-003 (eval_pipeline_acceptance) |

### Supplementary Binding (1 atom)

| Atom | Family | v1.1 Evidence | v1.2 Evidence | Source(s) Added |
|------|--------|---------------|---------------|-----------------|
| F04.04 | F04 | WEAK_EVIDENCE | WEAK_EVIDENCE | SRC-ADR-005 (REPLAY_DETERMINISM_RULES) - adjacent but not direct |

### Unchanged WEAK (4 atoms)

| Atom | Family | Evidence | Reason |
|------|--------|----------|--------|
| F04.02 | F04 | WEAK_EVIDENCE | No source canonicalizes context attribution |
| F04.03 | F04 | WEAK_EVIDENCE | No source canonicalizes no-private-substitute |
| F05.04 | F05 | WEAK_EVIDENCE | No L3 charter ADR naming dispatch role |
| F07.03 | F07 | WEAK_EVIDENCE | SRC-ADR-001 is ADVISORY with invalid_for_normative_use=True |

## Edge-Level Changes

Two edges had evidence_class upgraded from WEAK_EVIDENCE to NORMATIVE due to atom endpoint upgrades:

| Edge ID | v1.1 Evidence | v1.2 Evidence | Reason |
|---------|---------------|---------------|--------|
| INT-F08.04-F09.01-01 | WEAK_EVIDENCE | NORMATIVE | F08.04 upgraded NORMATIVE |
| INT-F09.05-F08.04-01 | WEAK_EVIDENCE | NORMATIVE | F09.05 upgraded NORMATIVE |

## Source Authority Records Added

Six new SourceAuthorityRecords added by F2 (all pre-existing repo documents):

| ID | Title | Authority Class | Rank | Supports Atoms |
|----|-------|----------------|------|----------------|
| SRC-ADR-001 | ADR-F25-int - Healing Dispatch Routing | ADVISORY | 6 | F07.03 (supplementary only) |
| SRC-ADR-002 | Healer Retry Hardening Spec | ARCHITECTURAL | 4 | F07.01, F07.02 |
| SRC-ADR-003 | Evaluation Pipeline Acceptance | ARCHITECTURAL | 4 | F08.01, F08.03, F08.04, F08.05, F09.05 |
| SRC-ADR-004 | L0 Decomposition Spec | ARCHITECTURAL | 4 | F01.06, F03.04 |
| SRC-ADR-005 | Replay Determinism Rules | ARCHITECTURAL | 4 | F04.04 (supplementary), F03.04 |
| SRC-ADR-006 | Authority Hierarchy Invariants | ARCHITECTURAL | 4 | Multiple families (supplementary) |

Total sources in v1.2: 12 (6 from v1 + 6 from F2)

## Remaining Blockers by Family

### F04 (RED 0.25) - Blocker B3
- **Missing:** Context-assembly ADR canonicalizing attribution (F04.02), no-private-substitute (F04.03), idempotence (F04.04)
- **Impact:** F04 remains sole RED family; highest remaining blocker
- **Required:** Author dedicated context-assembly ADR

### F07 (YELLOW 0.75) - Blocker B2-partial
- **Missing:** Normative escalation-target ADR for F07.03
- **Impact:** F07.03 stays WEAK, preventing full GREEN
- **Required:** Promote healing_dispatch_routing_adr to normative via HITL, or author new ADR

### F05 (YELLOW 0.75) - Blocker B6
- **Missing:** L3 orchestration charter ADR
- **Impact:** F05.04 stays WEAK
- **Required:** Author L3 charter explicitly defining dispatch role

### Graph Completeness - Blocker B7
- **Missing:** 6 deferred interaction candidates (C1, C2, C3, C4, C6, C9)
- **Impact:** Graph completeness
- **Required:** Downstream atoms / edge-kind patches

## Conclusion

F2 integration achieved material progress: global coverage flipped YELLOW → GREEN, three RED families (F01, F03, F08) closed to GREEN, and F07 moved RED → YELLOW. The exit-spine source (SRC-ADR-003) and healer-retry spec (SRC-ADR-002) were discovered in the repo, resolving what prior waves treated as "missing ADR" blockers. F04 remains the sole RED family, awaiting a context-assembly ADR.
