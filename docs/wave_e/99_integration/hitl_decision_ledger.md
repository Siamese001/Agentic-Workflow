# Wave E1 Integration — HITL Decision Ledger

Stable-ID record of every non-trivial merge decision made during the E1 integration pass. Each entry follows a fixed shape so future waves can audit the provenance of the canonical graph.

---

## HITL-INT-001 — Last-writer-wins for E1c atom patches

**Subject:** E1c re-published F04.01, F04.04, F08.05 with identical IDs to E1b versions. Resolution policy needed.
**Options:**
- (a) Reject E1c's patches; keep E1b versions.
- (b) **Apply E1c versions; discard E1b (last-writer-wins).** ← Chosen.
- (c) Merge field-by-field (ad-hoc).
**Decision:** (b). Confidence: 0.92.
**Rationale:** E1c's role per contract is to patch atoms where scope/authority changes; the schema doesn't model partial patches so full-record overlay is the honest merge. Option (c) would introduce ad-hoc merge logic not described in the schema.
**Impact:** F04.01 promoted from UNRESOLVED to ACTIVE; F04.04 from UNRESOLVED to ACTIVE WEAK_EVIDENCE; F08.05 from NORMATIVE to ACTIVE WEAK_EVIDENCE.

## HITL-INT-002 — Drop self-referential `supersedes` field on E1c patches

**Subject:** E1c's patched atoms carry `supersedes: <own_id>`. Schema's `supersedes` field is for cross-ID replacement, not same-ID patches.
**Options:**
- (a) **Drop the `supersedes` field in canonical output.** ← Chosen.
- (b) Keep the self-reference (misuses the schema).
- (c) Rename the superseded atom (violates ID immutability).
**Decision:** (a). Confidence: 0.95.
**Rationale:** Self-referential supersedes is semantically meaningless and confuses downstream consumers. The last-writer-wins merge policy (HITL-INT-001) already captures the supersession relationship.

## HITL-INT-003 — F07 family authority_class correction (OPERATIONAL → CONSTITUTIONAL)

**Subject:** Schema rule "Family's authority_class MUST be the MINIMUM rank across atoms' bindings". F07 had OPERATIONAL (rank 5) but F07.04 binds SRC-RULE-001 (rank 1). E1c flagged and recommended ARCHITECTURAL.
**Options:**
- (a) Keep OPERATIONAL, emit a WARNING (ignores the schema rule).
- (b) Correct to ARCHITECTURAL per E1c's pragmatic recommendation.
- (c) **Correct to CONSTITUTIONAL per the strict schema rule computation.** ← Chosen.
- (d) Reclassify F07.04 to a higher-class binding set (doesn't help; SRC-RULE-001 is already rank 1).
**Decision:** (c). Confidence: 0.78.
**Rationale:** The schema rule is unambiguous ("MUST be the MINIMUM rank"). Option (b) would be a negotiated comfort choice that ignores the rule text. Option (a) would leave canonical output schema-invalid. If CONSTITUTIONAL feels too strong for F07's operational nature, the right remedy is to reconsider whether F07.04 should cite SRC-RULE-001 at all — not to downgrade the family class.
**Impact:** F07.authority_class = CONSTITUTIONAL in canonical families.yaml with `notes:` explaining the correction. All four F07 atoms unaffected.

## HITL-INT-004 — SRC-ADR-EXIT placeholder mapping

**Subject:** Six atoms cite SRC-ADR-EXIT; E1c could not materialize a real source for the exit spine.
**Options:**
- (a) Fabricate an SRC-ADR record with a speculative locator.
- (b) **Map to SRC-INT-003 (governing-semantics frontmatter); retain evidence_class per atom as E1c determined.** ← Chosen.
- (c) Mark all six atoms UNRESOLVED.
**Decision:** (b). Confidence: 0.88.
**Rationale:** (a) violates "locator MUST be resolvable". (c) throws away real content; the atoms' claims are valid even if the dedicated source doesn't exist. (b) is the honest compromise: ARCHITECTURAL-rank binding is maintained, WEAK_EVIDENCE flag makes the weakness visible, and a future wave can upgrade when the exit-spine ADR lands.
**Impact:** F08.01/03/04 and F09.05 retain WEAK_EVIDENCE; F08.02 retains NORMATIVE (had SRC-RULE-001 already); F08.05 is patched to WEAK_EVIDENCE per E1c.

## HITL-INT-005 — Promotion of WEAK_EVIDENCE atoms to ACTIVE

**Subject:** Whether WEAK_EVIDENCE atoms can be promoted to ACTIVE status.
**Options:**
- (a) Block WEAK_EVIDENCE atoms at DRAFT; only NORMATIVE promotes to ACTIVE.
- (b) **Allow WEAK_EVIDENCE atoms to be ACTIVE (claim in force, but support thin).** ← Chosen.
**Decision:** (b). Confidence: 0.84.
**Rationale:** Schema has no rule forbidding WEAK_EVIDENCE from being ACTIVE. The scoring rubric explicitly reduces coverage when WEAK atoms exist, which only makes sense if WEAK atoms can still be in-force. Option (a) would strand 15 atoms in DRAFT indefinitely even though their claims are sound. WEAK_EVIDENCE is a "thin-support" signal for future reinforcement, not a freeze.
**Impact:** All 15 WEAK_EVIDENCE atoms promoted to ACTIVE. They continue to count against coverage_score.

## HITL-INT-006 — Authority-binding deduplication after SRC mapping

**Subject:** Mapping SRC-ADR-L* → SRC-INT-003 produces duplicate entries in some atoms' `authority_binding` lists.
**Options:**
- (a) Keep duplicates (schema has no explicit uniqueness rule on the list).
- (b) **Deduplicate, preserving first-occurrence order.** ← Chosen.
**Decision:** (b). Confidence: 0.96.
**Rationale:** Duplicates convey no additional authority weight and pollute the canonical output. Deduplication is a non-semantic normalization.

## HITL-INT-007 — OOS-001 / OOS-002 non-deduplication

**Subject:** OOS-001 and OOS-002 both forbid L6 current-run influence, on different targets (L0 vs. L2 heal/retry).
**Options:**
- (a) Merge into one OOS with broader scope.
- (b) **Keep both; they have disjoint scope_statements.** ← Chosen.
**Decision:** (b). Confidence: 0.93.
**Rationale:** Distinct target surfaces (route decision vs. recovery path) warrant distinct exclusion records. Merging would reduce diagnostic value.

## HITL-INT-008 — OOS-003 as NOT_YET_DECIDED vs. OUT_OF_CHARTER

**Subject:** The C0-layer alternative was explicitly deferred rather than charter-rejected.
**Options:**
- (a) Reclassify as OUT_OF_CHARTER (simpler, less maintenance).
- (b) **Keep as NOT_YET_DECIDED with revisit_trigger.** ← Chosen (carried from E1c).
**Decision:** (b). Confidence: 0.90.
**Rationale:** The schema gives the option; NOT_YET_DECIDED is the honest classification. A concrete revisit_trigger is already published.

## HITL-INT-009 — Global coverage score not rounded up

**Subject:** Global score is 0.7413793... Contract rule: "if blockers remain, coverage_score must not be rounded up."
**Options:**
- (a) **Report 0.74 (or 0.741 for higher precision), do NOT round up to 0.75.** ← Chosen.
- (b) Round to 0.75 (would flip RED → YELLOW).
**Decision:** (a). Confidence: 1.00.
**Rationale:** Contract rule is explicit. Integrity requires honest reporting.

## HITL-INT-010 — Canonical v1 publishable with RED global coverage

**Subject:** Does RED global coverage block publication of canonical v1?
**Options:**
- (a) Block publication; require coverage work before canonical v1 ships.
- (b) **Publish canonical v1 with RED; document gaps for Wave F+.** ← Chosen.
**Decision:** (b). Confidence: 0.87.
**Rationale:** The canonical graph is schema-valid, internally consistent, and has no orphans, duplicates, or placeholder IDs. RED indicates missing ARCHITECTURAL sources (a known, documented gap), not structural incorrectness. Blocking publication would strand 58 valid ACTIVE atoms and 23 valid ACTIVE edges because three families need additional sources. The honest path is to publish with full transparency.
