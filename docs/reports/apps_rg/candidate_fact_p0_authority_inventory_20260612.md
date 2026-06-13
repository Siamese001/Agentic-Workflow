# Candidate Fact P0 Authority Inventory

Plan: `typed-edge-role-facet-guardrails-a6f3d2`
Date: 2026-06-12

## Result

`candidate_fact` and SRFS are deprecated as runtime authority before W1.
Remaining references are allowed only as lineage, compatibility aliases, fact-vector substrate labels, historical tests, or tombstones.

## Searches

- `rg -n "candidate_fact|CandidateFact|SRFS|SelectedRoleFactSet" apps_rg tests -g "!*.pyc"`
- `rg -n "candidate_facts_as_proof: true|candidate_facts_as_proof is True|candidate_facts_may_prove_claim\(fact_bound=True\) is True|effective_claim_proof\(fact_bound=True\) is True" apps_rg tests`

## Allowed References

| Pattern | Classification | Notes |
|---|---|---|
| `candidate_fact_id` | Lineage alias | May remain when it points to GraphDB-backed facts and cannot admit or rank claims. |
| `ledger_candidate_fact_id` | Compatibility alias | Used to preserve historical joins; not authority. |
| `candidate_fact_ledger` in fact-vector ingest/bootstrap tests | Substrate/source label | Allowed until W2 `fact_ledger` cleanup, provided traversal does not read it as skills or proof authority. |
| `SelectedRoleFactSet` and SRFS tombstones | Retired surface | Imports must fail closed with the retirement error. |
| Prompt/example mentions of candidate facts | Historical prompt artifact | Not closure evidence and not allowed to satisfy W3-W5 hardening by prompt wording alone. |

## Blocked Authority Paths

| Path | P0 Enforcement |
|---|---|
| Metadata flags such as `candidate_fact_ledger_used_as_authority` or `candidate_facts_as_proof` | `BLOCKED_CANDIDATE_FACT_AUTHORITY` from `assert_candidate_fact_authority_deprecated`. |
| Source authority fields set to `candidate_fact`, `candidate_fact_ledger`, `selected_role_fact_set`, or `srfs` | `BLOCKED_CANDIDATE_FACT_AUTHORITY`. |
| `selection_method` values using candidate-fact ledger or SRFS selection | `BLOCKED_CANDIDATE_FACT_AUTHORITY`. |
| Candidate-fact claim substrate without GraphDB claim authority | `BLOCKED_CANDIDATE_FACT_AUTHORITY`. |
| Section config declaring candidate facts as proof | Runtime parser forces `candidate_facts_as_proof=False`; YAML now declares false and `candidate_fact_lineage_allowed=true`. |

## Compatibility Map

| Field | Allowed Meaning After P0 | Not Allowed |
|---|---|---|
| `candidate_fact_id` | Historical fact/node lineage id for GraphDB-authorized facts | Selecting, proving, ranking, weighting, or backfilling claims. |
| `candidate_fact_ledger` | Transitional source/substrate label before W2 `fact_ledger` cleanup | Skills SSOT, metric SSOT, proof authority, claim authority, or section eligibility authority. |
| `selected_role_fact_set` / `srfs` | Retired/tombstoned label in compatibility tests or historical artifacts | Runtime authority or selection source. |

## Verification

Focused P0 gate:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -o "addopts=--strict-markers --strict-config --tb=short --continue-on-collection-errors --import-mode=importlib" tests/unit/apps_rg/runtime/sections/test_section_spec_wave6.py tests/unit/apps_rg/test_candidate_fact_deprecation_p0.py tests/unit/apps_rg/test_graph_skills_authority_separation.py tests/unit/apps_rg/test_selected_role_fact_set_retirement_guard.py tests/_apps_contract/test_apps_rg_augmented_skills_graph_source_authority.py
```

Result: 47 passed, 3 warnings.

Note: the override removes `--timeout=180` from `pytest.ini` because `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` prevents the timeout plugin from registering the option in this Codex environment.
