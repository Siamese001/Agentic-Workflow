# Augmented skills graph — validation receipt (Wave 2)

**STATUS: PARTIAL**

## What shipped

- New module `apps_rg/fact_inventory/augmented_skills_graph.py` (loads W4A arsenal ledger, emits `source_authority` / `skills_source_type` / `graph_ref` / `graph_digest` / `graph_version`).
- Proof-pool resolver merges skills authority on SRFS, candidate-ledger, and base-resume fallback paths.
- Usage ledger + INPUT_AUTHORITY prompts distinguish **candidate fact ledger (claims)** vs **augmented skills graph (skills/competency)**.
- Contract tests: `tests/_apps_contract/test_apps_rg_augmented_skills_graph_source_authority.py` (31 tests, all passing).

## Negative controls

| Case | Result |
|------|--------|
| Missing `APPS_RG_AUGMENTED_SKILLS_GRAPH_PATH` | `skills_source_authority_status=BLOCKED` |
| Prompt when blocked | Explicit “do not treat broad_skills_ledger … as skills SSOT” |
| Skills fallback to candidate ledger | **Not observed** |

## Open gaps (PARTIAL)

- `proof_source` string remains `broad_skills_ledger` for X2 claim-pool compatibility.
- Competencies `verified_skill_inventory` not yet fed from graph skill rows.
- Older runtime proof bundles under `artifacts/apps_rg/runtime_proofs/` still show legacy labels until re-run.

See `augmented_skills_graph_section_source_validation.json` for command-level test counts.
