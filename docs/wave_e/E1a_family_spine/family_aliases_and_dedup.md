# Wave E1a — Family Aliases and Deduplication

**Scope:** Catalog the alias / title variants considered during E1a, record which were collapsed into the canonical title, and confirm that no two Families express the same normative claim.

## Alias Collapses (seed registry → canonical title)

| Seed title (family_seed_registry.md) | Canonical title (proposals/families.yaml) | Alias collapses / notes |
|---|---|---|
| F01 Request Intake + Envelope Check | Request Intake and Envelope Check | Replaced "+" connector with "and"; did not split into two families (see family_risk_flags.md for atom-split flag). |
| F02 L1 Reasoning + Plan Generation | L1 Reasoning and Plan Generation | Treated reasoning and plan generation as one family because plan generation is the terminal artifact of L1 reasoning; splitting would create an artificial boundary. |
| F03 L0 Route Decision + Switching | L0 Route Decision and Switching | "Route switching" is the act of committing a decision; kept as one family. |
| F04 C0 Context Assembly + Grounding | Context Assembly and Grounding | Dropped the "C0" prefix from the title because `C0` is not a valid owning_layer enum value and using it would imply a layer the schema does not define. See family_risk_flags.md. |
| F05 L3 Orchestration | L3 Orchestration | Unchanged. |
| F06 L2 Task Execution | L2 Task Execution | Unchanged. |
| F07 L2 Heal / Retry / Recovery | L2 Heal, Retry, and Recovery | Replaced slash-list with comma-list for readability; did not split. |
| F08 Runtime Exit Control + Evaluation Spine | Runtime Exit Control and Evaluation Spine | Kept bundled; flagged for atom-split by E1b. |
| F09 Universal Write Gate | Universal Write Gate | Unchanged. |
| F10 L4 Durable Archive / State Authority | L4 Durable Archive and State Authority | "Durable archive" and "state authority" refer to the same layer from two vantage points (storage surface vs. authority); kept as one family. |
| F11 L5 Policy / Safety Authority | L5 Policy and Safety Authority | Policy and safety are the same authority from two vantage points at L5. |
| F12 L6 Observability + Future-Run Learning | L6 Observability and Future-Run Learning | Kept bundled; flagged for atom-split by E1b (observe vs. feed-forward). |

## No Duplicate Families

Cross-checked all twelve intents pairwise. No two families share a normative claim:

- F09 (Write Gate) and F10 (L4 State) are adjacent but distinct: F09 governs the write path; F10 governs the state's authoritativeness and the no-shadow rule.
- F06 (Task Execution) and F07 (Heal/Retry/Recovery) are adjacent but distinct: F06 covers the success path; F07 covers the recovery path and the re-planning escalation.
- F08 (Exit Spine) and F11 (L5 Policy) share L5 involvement but have different normative subjects: F08 is "where termination decisions flow through"; F11 is "who is the policy authority."
- F04 (Context) and F02 (Reasoning) are adjacent but distinct: F04 covers the assembly/grounding contract; F02 covers the reasoning and plan generation that consume the context.

## Candidates Considered and Rejected

Two seed concepts were evaluated for separation into their own family but intentionally kept bundled in E1a and instead flagged for E1b atom-split:

- **F01 → F01a "Intake" + F01b "Envelope Check"**: rejected because the normative claim ("admission is predicated on envelope validation") becomes awkward to state as a cross-family edge when it is more natural as two atoms inside F01.
- **F12 → F12a "Observability" + F12b "Future-Run Learning"**: rejected because the L6-MUST-NOT-influence-current-run constraint spans both concerns; splitting would duplicate that exclusion.

E1b should capture the internal distinction via separate atoms within the same family, not by requesting new Family IDs.

## No `proposed_new_family` Entries

E1a identified no new family that would justify a HITL request to the integration lead. All twelve minted IDs cover the concerns encountered during spine normalization.
