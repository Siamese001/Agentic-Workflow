# Wave F2 - Authored Source Index

**Important finding:** F2 did NOT author any new repo documents. All six new SourceAuthorityRecord proposals register **existing** canonical documents that were already in the repo before F2 began.

Prior waves (F1 in particular) treated F08/F07/F04 as "missing-ADR" blockers. That was a documentation-discovery failure, not an authoring failure. The real sources exist under `docs/architecture/`, `docs/specs/hardening/`, and `docs/contracts/`.

---

## Registered (existing) documents

| SRC ID | Locator | Status on disk | authority_class | Normative for F2? |
|---|---|---|---|---|
| SRC-ADR-001 | `docs/architecture/healing_dispatch_routing_adr.md` | Pre-existing, dated 2026-04-16 | ADVISORY (rank 6) | ❌ invalid_for_normative_use=True |
| SRC-ADR-002 | `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` | Pre-existing | ARCHITECTURAL (rank 4) | ✅ NORMATIVE |
| SRC-ADR-003 | `docs/architecture/eval_pipeline_acceptance.md` | Pre-existing, ACCEPTED 2026-04-13, 135/135 tests passing | ARCHITECTURAL (rank 4) | ✅ NORMATIVE |
| SRC-ADR-004 | `docs/specs/hardening/L0_DECOMPOSITION_SPEC.md` | Pre-existing | ARCHITECTURAL (rank 4) | ✅ NORMATIVE |
| SRC-ADR-005 | `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md` | Pre-existing | ARCHITECTURAL (rank 4) | ✅ NORMATIVE |
| SRC-ADR-006 | `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` | Pre-existing | ARCHITECTURAL (rank 4) | ✅ NORMATIVE |

## Candidate documents considered and NOT registered

| Document | Reason not registered |
|---|---|
| `docs/architecture/write_governance_note.md` | Explicitly labeled `invalid_for_normative_use=True`. Does not add NORMATIVE support beyond what SRC-ADR-003 already provides via GovernedHandoffAgent. |
| `docs/requirements/normative_requirements_spec.md` | Scope is retrieval/routing (AGEN-0100 abstain, AGEN-0101 hybrid search, etc.), not agentic workflow context assembly. Does not cleanly support F04. |
| `docs/specs/hardening/UWG_ISOLATION_SPEC.md` | Supports F09 UWG claims, but F09 is already GREEN in v1.1 except F09.05, which SRC-ADR-003 covers more directly. Reserved for later waves if F09 needs additional support. |
| `docs/specs/hardening/L6_DRIFT_SAFEGUARDS_SPEC.md` | F12 is already GREEN post-F1. No atom benefits from adding. |
| `docs/specs/hardening/POLICY_EPOCH_SPEC.md` | Not read in detail; F11 is already GREEN. Reserved. |
| `docs/contracts/guardian_to_L6.md` | Covers guardian artifact contract, ingestion into L6. Adjacent to F12.07/F12.08 but those are already NORMATIVE post-F1. |

## Why no new documents were authored

The F2 contract permits authoring new ADRs or rules **"if needed"** under `docs/adr/`, `docs/rules/`, or `docs/architecture/`, but also explicitly forbids fabrication. For the three remaining WEAK atoms (F04.02, F04.03, F04.04 attribution/idempotence; F05.04 L3 dispatch; F07.03 escalation target), authoring brand-new ADRs without:

1. HITL approval
2. Implementation backing
3. Demonstrable project posture

would be fabrication. The existing repo has no equivalent of these three in canonical form, so F2 declined to author speculative ADRs and instead carries them forward as explicit blockers.

## Locator resolvability check

Each registered locator was verified:

| Locator | Resolves? | Notes |
|---|---|---|
| `docs/architecture/healing_dispatch_routing_adr.md` | ✅ | File read in F2 session |
| `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` | ✅ | File read in F2 session |
| `docs/architecture/eval_pipeline_acceptance.md` | ✅ | File read in F2 session, RELEASE ACCEPTED marker confirmed |
| `docs/specs/hardening/L0_DECOMPOSITION_SPEC.md` | ✅ | File read in F2 session |
| `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md` | ✅ | File read in F2 session |
| `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` | ✅ | File read in F2 session |

All six are real, resolvable, internally consistent documents in the current repo state.
