# Wave E1d — Interaction Candidates

**Scope:** Catalog every interaction candidate considered during Pass A. Candidates that point at stable atom IDs became schema-valid edges in `proposals/edges.yaml`. Candidates whose endpoints are not yet stable remain here as sidecar analysis (per contract: "keep candidates in sidecar analysis and README blockers").

---

## 1. Emitted Edges (23) — summary

Organized by the dominant flow direction. Full records in `proposals/edges.yaml`.

**Admission chain**
- `INT-F01.03-F11.01-01` REQUIRES — intake consumes L5 policy
- `INT-F02.01-F01.05-01` DEPENDS_ON — reasoning awaits admission

**Reasoning / routing separation (refinements)**
- `INT-F05.02-F02.02-01`, `INT-F06.03-F02.02-01` REFINES — non-L1-no-plan refined per layer
- `INT-F05.03-F03.02-01`, `INT-F06.04-F03.02-01` REFINES — non-L0-no-route refined per layer

**Orchestration plane**
- `INT-F05.01-F02.03-01` REQUIRES — L3 orchestrates L1 plan
- `INT-F05.04-F06.01-01` REQUIRES — L3 dispatches to L2

**Execution plane**
- `INT-F06.02-F03.01-01` REQUIRES — L2 uses L0 route

**Write Gate monopoly**
- `INT-F06.05-F09.01-01` REQUIRES — L2 mutations via gate
- `INT-F07.04-F09.01-01` REQUIRES — heal/retry via gate
- `INT-F10.03-F09.01-01` REQUIRES — L4 writes via gate

**Recovery chain**
- `INT-F07.03-F02.01-01` CONDITIONAL_ON — re-plan on unrecoverable failure
- `INT-F07.03-F05.01-01` REQUIRES — escalation via L3

**Exit spine**
- `INT-F08.02-F11.05-01` REQUIRES — spine applies L5 exit policy
- `INT-F08.04-F09.01-01` REQUIRES — spine signals gate
- `INT-F09.04-F11.04-01` REQUIRES — gate rejects missing policy signal
- `INT-F09.05-F08.04-01` REQUIRES — gate rejects missing exit signal

**Policy implications**
- `INT-F11.07-F09.01-01` IMPLIES — L5 no-mutate implies gate monopoly

**L6 no-current-run-influence (FORBIDS)**
- `INT-F12.02-F03.01-01` FORBIDS — L6 ↛ L0
- `INT-F12.02-F11.01-01` FORBIDS — L6 ↛ L5
- `INT-F12.03-F09.01-01` FORBIDS — L6 ↛ gate

**Future-run feed-forward**
- `INT-F12.05-F02.01-01` DEPENDS_ON — future L1 consumes L6 artifacts

---

## 2. Candidates NOT Emitted (endpoints not yet stable)

| # | Candidate relationship | Reason not emitted | Suggested target wave |
|---|---|---|---|
| C1 | Intake reason-code (`F01.06`) feeds L6 learning (observability). | F01.06 and F12 atoms are stable, but there is no atom that says "L6 MUST catalog admission rejections". The consumer atom does not yet exist. | Wave F or a follow-up E-phase that extends F12 with a consumer atom. |
| C2 | Context grounding (F04) binds L5 policy (e.g., "context MUST NOT include unauthorized sources"). | No F11 atom currently restricts context content; would require a new F11 atom. | Wave F, possibly preceded by an E1a revision to F11. |
| C3 | Heal/retry (`F07.01`/`F07.02`) bounded by L5 policy (e.g., retry budget is policy-set). | No F11 atom explicitly binds heal/retry; closest is F11.03 (L5 binds L2 execution) which is arguable. | A future F11 atom "L5 MUST set retry budgets" would enable `INT-F07.02-F11.?-01 REQUIRES`. |
| C4 | Context attribution (`F04.02`) feeds audit trail / evaluation spine. | No atom exists for an audit-trail surface inside F08 or elsewhere. | Wave F. |
| C5 | Exit spine (F08) produces L6 observation material (successful termination events observed for future learning). | Requires a new F12 atom `"L6 MUST observe F08 outcomes"`. | A future F12 atom, then edge becomes `INT-F12.?-F08.03-01 DEPENDS_ON`. |
| C6 | Route decision (`F03.01`) records rationale consumed by F04 (context) for subsequent steps. | Would require a new F04 atom or a new F03 atom. | Wave F. |
| C7 | `F02.04` (L1 MUST NOT execute) implies F05 or F06 executes. Already implicit; edge to what target? No clean target atom. | The existing F02.04 is self-contained. No edge needed — the implication is captured by the complementary atoms' existence. | No action. |
| C8 | CONFLICTS_WITH candidates. The candidate pair `F07.03` ("surface to L3 for re-planning") vs. `F05.02` ("L3 MUST NOT plan") looks like a conflict but is not: F07.03's "for re-planning" is a downstream goal, not a claim that L3 plans. The actual planning is L1's (F02.01). No CONFLICTS_WITH edge emitted. | Not a real conflict. | No action; note for integration pass. |
| C9 | CO_REQUIRES BIDIRECTIONAL candidates. `F09.04` (gate rejects missing policy) and `F11.04` (L5 binds gate) are mutually necessary. Could be `CO_REQUIRES` BIDIRECTIONAL. | Chose to encode as single DIRECTED `REQUIRES` from F09.04 to F11.04 for simplicity; the reverse REQUIRES is implicit in F11.04's own claim. | Integration pass may promote to BIDIRECTIONAL if a verification tool benefits. |

---

## 3. Edges Ruled Out as Mis-typed

- `INT-F12.02-F03.01-01 FORBIDS` is the chosen encoding. Considered and rejected: `CONFLICTS_WITH` (schema validation requires one endpoint status to be `UNRESOLVED` or `DEPRECATED`; both are `DRAFT`), `IMPLIES` (wrong direction of meaning).
- The L3-to-L1 re-planning edge is CONDITIONAL_ON rather than plain DEPENDS_ON because the dependency only activates on unrecoverable-failure classification.

---

## 4. Self-Check of Schema Constraints for Emitted Edges

- [x] All 23 edges have unique `(source_atom_id, target_atom_id, edge_kind)` triples.
- [x] No edge has `source_atom_id == target_atom_id`.
- [x] All endpoints exist in E1b's atoms.yaml.
- [x] No BIDIRECTIONAL edges used (conservative choice; see C9).
- [x] The single `CONDITIONAL_ON` edge (`INT-F07.03-F02.01-01`) has a non-empty `condition`.
- [x] No edge has status `ACTIVE`.
- [x] All edges have `evidence_class` + `authority_binding` (including WEAK_EVIDENCE edges).

---

## 5. Total Counts

- **Emitted edges:** 23.
- **Candidates not emitted:** 9 (C1..C9; most require new atom IDs in Wave F).
