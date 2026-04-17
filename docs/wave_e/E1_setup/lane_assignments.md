# Lane Assignment Matrix — Wave E1

**Authority:** Chat 1 / integration lead, E1-Setup run.
**Scope:** Assigns primary and secondary ownership of the minted Family set (F01..F12) to the four E1 sub-waves.

## Operating Rules (binding)

1. **Only Chat 1 / integration lead may mint new Family IDs in this run.**
2. **Other lanes may reserve atom ID ranges only for already-minted Family IDs** (F01..F12 as listed in `family_seed_registry.md`).
3. **Proposed new family workflow.** If a lane believes a new Family is genuinely required, it MUST:
   - Add a `proposed_new_family` block to its own `README.md` with title, intent, rationale, and the existing Family it would otherwise stretch.
   - **Stop short of minting the ID.**
   - Surface a HITL request to the integration lead.

## Lane Directory Map

| Lane | Sub-wave directory |
|---|---|
| E1a_family_spine | `docs/wave_e/E1a_family_spine/` |
| E1b_atoms | `docs/wave_e/E1b_atoms/` |
| E1c_authority_scope | `docs/wave_e/E1c_authority_scope/` |
| E1d_interactions | `docs/wave_e/E1d_interactions/` |

## Ownership Matrix

| Family | E1a (family spine) | E1b (atoms) | E1c (authority scope) | E1d (interactions) |
|---|---|---|---|---|
| F01 Request Intake + Envelope Check | primary | primary | secondary | — |
| F02 L1 Reasoning + Plan Generation | primary | primary | secondary | primary |
| F03 L0 Route Decision + Switching | primary | primary | secondary | primary |
| F04 C0 Context Assembly + Grounding | primary | primary | secondary | primary |
| F05 L3 Orchestration | primary | primary | secondary | primary |
| F06 L2 Task Execution | primary | primary | secondary | primary |
| F07 L2 Heal / Retry / Recovery | primary | primary | secondary | — |
| F08 Runtime Exit Control + Evaluation Spine | primary | primary | **primary** | primary |
| F09 Universal Write Gate | primary | primary | **primary** | primary |
| F10 L4 Durable Archive / State Authority | primary | primary | **primary** | — |
| F11 L5 Policy / Safety Authority | primary | primary | **primary** | primary |
| F12 L6 Observability + Future-Run Learning | primary | primary | **primary** | primary |

## Lane Responsibilities

### E1a_family_spine — primary owner F01..F12
- Produce `proposals/families.yaml` with Family records for all 12 IDs.
- Records MUST match `family_seed_registry.md` titles and intents verbatim unless HITL-approved.
- All families have `status: DRAFT` (integration pass promotes to `ACTIVE`).
- Produce a README with ready-for-integration declaration.

### E1b_atoms — primary owner F01..F12
- Produce `proposals/atoms.yaml` with RequirementAtom records for each family.
- One normative claim per atom; split if in doubt.
- Every `NORMATIVE` atom MUST cite ≥1 authority source of rank ≤ ARCHITECTURAL (source records may be produced by E1c; E1b may cite them by ID).
- Unsupported claims MUST be `UNRESOLVED` or `WEAK_EVIDENCE`, never faked `NORMATIVE`.
- Reserve atom ID ranges in `docs/wave_e/00_schema/id_allocations.log` **before** publishing atom YAML.
- Produce per-family scorecards `SCORE-F<NN>-E1b.yaml`.

### E1c_authority_scope — primary owner F08..F12, secondary support F01..F07
- Produce `proposals/sources.yaml` with SourceAuthorityRecord entries.
- Confirm or refine `owning_layer` for F01, F04, F08 (marked "confirm in E1c scope review" in the registry).
- For F08..F12, exhaustively map authority sources (rules, ADRs, external standards).
- For F01..F07, provide source coverage sufficient for E1b's `NORMATIVE` atoms to bind.
- Produce per-family scorecards `SCORE-F<NN>-E1c.yaml` for primary-owned families.

### E1d_interactions — primary owner F02..F06, F08..F09, F11..F12
- Produce `proposals/edges.yaml` with InteractionEdge records.
- Every edge between a layer-boundary concern and the Write Gate (F09), Policy (F11), or Observability (F12) MUST be explicit.
- Edge kinds from the frozen enum only (`REQUIRES`, `FORBIDS`, `IMPLIES`, `CONFLICTS_WITH`, `REFINES`, `SUPERSEDES`, `DEPENDS_ON`, `CONDITIONAL_ON`, `CO_REQUIRES`).
- Interactions are first-class records, never prose comments.
- Produce per-family scorecards `SCORE-F<NN>-E1d.yaml` for primary-owned families.

## Cross-Lane Handoffs

- **E1a → E1b:** families published as `DRAFT` give E1b a valid `family_id` target for atoms.
- **E1c → E1b:** source records give E1b `SRC-*` IDs to cite in `authority_binding`.
- **E1b → E1d:** atoms published as `DRAFT` give E1d valid `source_atom_id` / `target_atom_id` endpoints.
- **All lanes → integration pass:** promotion `DRAFT` → `ACTIVE` happens only in the integration pass, never in a sub-wave.

## Exclusions Ownership

- Exclusions (`OOS-*`) may be authored by any lane that encounters an explicitly out-of-scope claim.
- The most important pre-known exclusion: **L6 MUST NOT influence current-run decisions** (F12). This exclusion SHOULD be authored by either E1b (as part of F12 atoms) or E1c (as part of F12 authority scope). Coordinate via integration pass if duplicated.

## Ambiguities Resolved

- Directory names are final: `E1a_family_spine`, `E1b_atoms`, `E1c_authority_scope`, `E1d_interactions`.
- Family set is frozen for this run at F01..F12.
- Atom IDs are reserved per family by whichever lane publishes first (E1b is expected).
- Scorecards per lane are scoped to that lane's **primary**-owned families; secondary-support work does not produce scorecards to avoid double-counting.
