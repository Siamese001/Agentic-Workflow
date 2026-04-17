# Canonical v1.2 HITL Decision Ledger

**Integration Wave:** F2 (Source Authoring for Remaining RED Families)
**Integration Date:** 2026-04-16

## Summary

No HITL decisions were required during the F2 integration pass. All F2 proposals passed schema validation and contract checks automatically. The integration pass merged all ten atom patches and six new SourceAuthorityRecords without ambiguity or conflicts.

## Decision Log

| Decision ID | Topic | Decision | Rationale | Date |
|-------------|-------|----------|-----------|------|
| N/A | None | N/A | No HITL decisions required | N/A |

## Key Integration Decisions (Automated)

The following decisions were made programmatically during integration, without requiring HITL:

### 1. SRC-ADR-001 Discipline
**Decision:** Accept SRC-ADR-001 as ADVISORY with `invalid_for_normative_use=True` marker; bind it to F07.03 as supplementary only; do not allow it to promote any atom to NORMATIVE.
**Rationale:** The source explicitly carries `invalid_for_normative_use=True` and is described as repo-internal architecture only. F2 respected this marker by keeping F07.03 at WEAK_EVIDENCE despite the binding.

### 2. F04.04 Supplementary Binding
**Decision:** Accept SRC-ADR-005 as supplementary binding for F04.04, but keep F04.04 at WEAK_EVIDENCE.
**Rationale:** REPLAY_DETERMINISM_RULES mandates deterministic replay for mutations but does not explicitly state context-assembly idempotence. The binding is adjacent but not direct, so the atom correctly remains WEAK_EVIDENCE.

### 3. No New Families, Edges, or Exclusions
**Decision:** Accept F2's empty proposals for families.yaml, edges.yaml, and exclusions.yaml.
**Rationale:** F2's scope was source authoring and atom patching only. No new families, edges, or exclusions were proposed or needed.

### 4. Edge Evidence Class Upgrades
**Decision:** Upgrade evidence_class for INT-F08.04-F09.01-01 and INT-F09.05-F08.04-01 from WEAK_EVIDENCE to NORMATIVE.
**Rationale:** Both edges have endpoints (F08.04, F09.05) that were upgraded to NORMATIVE in this integration pass. The edge evidence follows the weaker endpoint, so upgrading to NORMATIVE is correct.

## Blockers Logged (No HITL Required)

The following blockers were logged in scorecards but did not require HITL decisions:

| Blocker ID | Description | Status |
|------------|-------------|--------|
| B3 | Context-assembly ADR required for F04 | Carried forward; requires later wave |
| B2-partial | Normative escalation-target ADR for F07.03 | Carried forward; requires later wave or HITL de-advisory |
| B6 | L3 orchestration charter ADR | Carried forward; requires later wave |
| B7 | 6 deferred interaction candidates | Carried forward; requires later wave |

## Validation of No Fabrication

The integration pass verified that F2 did not fabricate any sources:
- All 6 new SRC-ADR sources are pre-existing repo documents
- F2 authored zero new repo documents
- Locators were verified to resolve in-repo during F2 source authoring phase

## Conclusion

The F2 integration pass was straightforward with no HITL decisions required. All proposals were schema-valid, bounded, and honestly constrained. The integration pass executed the merge deterministically and documented all unresolved issues.
