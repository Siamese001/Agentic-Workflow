# v1.4 Merge Conflicts Register

F4 integration pass. Base: canonical v1.3. Delta: F4 edge-evidence and exclusion-cleanup proposals.

## Conflict inventory

**Total non-trivial conflicts: 0.**

F4's proposal was narrow (8 edge evidence upgrades + 1 exclusion revision) and touched no entity that v1.3 had freshly stabilized. Every v1.3 record except the 8 affected edges and OOS-003 passes through unchanged.

## Minor merge decisions (trivial)

| # | Decision | Resolution |
|---|---|---|
| M-v14-01 | How to integrate F4 `edge_patches` against v1.3 `edges.yaml` | Pairwise replacement by edge `id`. Each of the 8 patched edges replaces the corresponding v1.3 record; `edge_kind`, `direction`, `status`, and `condition` preserved verbatim. Only `evidence_class` and `authority_binding` changed. |
| M-v14-02 | Preservation of CONDITIONAL_ON `condition` on INT-F07.03-F02.01-01 | Preserved verbatim: `"Unrecoverable L2 task failure detected."` — matches SRC-ADR-009 §3.1 definition. |
| M-v14-03 | Preservation of `authority_binding` additive history for upgraded edges | Edge patches replace the binding list, not append. F4's per-edge rationale justifies the replacement binding as a complete direct-support citation — not a supplementation of the v1.3 list. In every case the new binding is a superset (content-wise) of the v1.3 binding, or substitutes more-specific sources (e.g., INT-F12.05-F02.01-01 substitutes `SRC-RULE-001 + SRC-INT-001 + SRC-INT-004` for the prior `SRC-INT-002`, matching the edge's actual memory-lifecycle grounding). |
| M-v14-04 | OOS-003 `scope_statement`, `related_atoms`, `related_families` | Preserved verbatim from v1.3. Only `reason`, `decided_at_wave`, `decided_by`, `revisit_trigger`, and `notes` updated per F4 proposal. History is retained. |
| M-v14-05 | Whether F4's proposal sidecar `rationale:` fields on edges leak into canonical `edges.yaml` | **Rejected.** Canonical edges retain only schema-defined fields. F4 per-edge rationales stay in `F4_edge_exclusion_cleanup/proposals/edges.yaml` and `weak_edge_upgrade_matrix.md`. |
| M-v14-06 | No atom patches | F4's `proposals/atoms.yaml` is explicitly empty (`atom_patches: []`). v1.4 carries all 60 ACTIVE + 1 EXCLUDED atoms verbatim from v1.3. |
| M-v14-07 | No new sources | F4's `proposals/sources.yaml` is empty. All 15 v1.3 sources carry forward unchanged. |
| M-v14-08 | No family changes | F4's `proposals/families.yaml` is empty. All 12 families carry forward. |
| M-v14-09 | OOS-001 and OOS-002 carry forward unchanged | F4 proposed no patches to either. Per integration rule 7, neither was touched. |
| M-v14-10 | Scorecards | All 12 `SCORE-F<NN>-INTEGRATION.yaml` files carry forward with `produced_at_wave: v1.4` update only. No atom count, evidence distribution, or bucket changed from v1.3 at the per-family atom level. Edge counts within scorecards were not recorded per-family in v1.3 (edge coverage is tracked globally), so no scorecard `edge_count_total` or `weak_evidence_count` value changes. |

## Over-eagerness check

Per integration rule 4–5, the pass did not upgrade any edge merely because both endpoints are NORMATIVE. Only the 8 edges for which F4 produced an explicit patch were considered, and each patch's direct-support rationale was re-validated against the cited sources before acceptance:

- SRC-RULE-001, SRC-INT-001, SRC-INT-003 as cited for INT-F02.01-F01.05-01 → validated: F01.05's own claim states the ordering, and the cited sources collectively ground layer separation + admission-gate discipline.
- SRC-ADR-008 L3-I1 step 2 for INT-F05.04-F06.01-01 → validated: explicit dispatch invariant.
- SRC-ADR-008 L3-I3 + SRC-ADR-009 ESC-I1 for both F07.03 edges → validated: emitting + receiving halves of the re-plan contract.
- SRC-ADR-003 for INT-F08.04-F09.01-01 and INT-F09.05-F08.04-01 → validated: explicit spine-to-UWG binding via `GovernedHandoffAgent` and `evaluate_sealed()`.
- SRC-RULE-001 §17 + SRC-INT-001 + SRC-INT-004 for INT-F12.05-F02.01-01 → validated: constitutional memory-lifecycle mandate + AGENTS.md session-start recall.
- SRC-ADR-003 + SRC-INT-004 for INT-F12.08-F08.03-01 → validated: spine outcome recording + memory write-back.

No edge was accepted on endpoint-evidence grounds alone.

## Sources considered and NOT integrated

None. F4 proposed no new sources. No v1.3 source was re-classified.

## ADVISORY discipline

SRC-ADR-001 remains the only ADVISORY-class source in v1.4. It appears in `sources.yaml` with `authority_class: ADVISORY` and is bound to no atom and no edge. Validation confirms 0 occurrences of SRC-ADR-001 in any `authority_binding` in v1.4.

## Exclusion discipline

The OOS-003 revision targets `reason`, which is an enum field bound to the fixed set `{OUT_OF_CHARTER, DEFERRED, SUPERSEDED, UNSAFE, DUPLICATE, NOT_YET_DECIDED}`. `SUPERSEDED` is a valid member. The revision therefore does not introduce schema drift. Cross-enum rule "no ACTIVE atom cites any Exclusion as authority" is preserved: 0 ACTIVE atoms cite OOS-003 in v1.4.

## Outcome

v1.4 is a clean, bounded additive merge. Zero non-trivial conflicts. All merge actions were routine identity-matched replacements or verbatim carry-forwards.
