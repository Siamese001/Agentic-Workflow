# Augmented skills graph — section source audit (Wave 1)

**Verdict: PARTIAL** — skills/competency authority is wired to `master_skills_arsenal_ledger.json` (augmented W4A graph) on all seven canonical sections via shared proof-pool metadata and INPUT_AUTHORITY prompts. Claim-evidence substrate still uses the candidate fact ledger under the legacy runtime label `broad_skills_ledger` (explicitly non-authoritative for skills).

## Canonical mapping

| Concept | Path / module |
|---------|----------------|
| Augmented skills graph artifact | `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` |
| Authority loader | `apps_rg/fact_inventory/augmented_skills_graph.py` |
| Legacy candidate fact ledger | `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json` |
| Shared resolver | `apps_rg/runtime/proof_pool_resolver.py` |

## Section matrix

| Section | Lane | PA | Resolver | Skills authority | Legacy ledger in receipts | Verdict |
|---------|------|----|-----------|------------------|---------------------------|---------|
| headline | `headline_lane.py` | `headline_pa.py` | `proof_pool_resolver` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |
| executive_summary | `executive_summary_lane.py` | `executive_summary_pa.py` | resolver + `exec_summary_srfs_arsenal` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |
| competencies | `competencies_lane.py` | `competencies_pa.py` | `proof_pool_resolver` | augmented_skills_graph | verified_skill_inventory scaffolding | PARTIAL |
| unify_bullets | `unify_bullets_lane.py` | `unify_bullets_pa.py` | `proof_pool_resolver` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |
| unify_narrative | `unify_narrative_lane.py` | `unify_narrative_pa.py` | `proof_pool_resolver` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |
| ibm_bullets | `ibm_bullets_lane.py` | `ibm_bullets_pa.py` | `proof_pool_resolver` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |
| ibm_narrative | `ibm_narrative_lane.py` | `ibm_narrative_pa.py` | `proof_pool_resolver` | augmented_skills_graph | broad_skills_ledger (claim only) | PARTIAL |

## Findings

1. **No pre-existing `augmented_skills_graph` symbol** — audit started with zero matches; SSOT is the W4A arsenal ledger file.
2. **`broad_skills_ledger` misnomer** — loads `candidate_fact_ledger`, not the graph. Now marked `broad_skills_ledger_skills_authority: false` in proof-pool metadata.
3. **Arsenal graph was already used** for executive-summary ranking via `exec_summary_srfs_arsenal`; other sections lacked explicit skills-authority metadata until Wave 2 wiring.
4. **Prompts** — INPUT_AUTHORITY uses “CANDIDATE FACT LEDGER” for claims and “AUGMENTED SKILLS GRAPH” for skills/competency authority.
5. **Negative control** — missing graph → `skills_source_authority_status: BLOCKED`; claim pool may still resolve; skills do not fall back to candidate ledger.

## Legacy reference classification

| Reference | Class |
|-----------|--------|
| `broad_skills_ledger` proof_source / X2 validators | DEPRECATED_NON_AUTHORITY (claim evidence) |
| `master_candidate_skills_fact_ledger` | DEPRECATED_NON_AUTHORITY (`legacy_skills_ledger_ref`) |
| `verified_skill_inventory` in competency template | DEPRECATED_NON_AUTHORITY (organizational scaffolding) |
| `master_skills_arsenal_ledger` / W4A graph | **Augmented graph SSOT** |
| Arsenal unit tests | TEST_FIXTURE_ONLY |

Machine-readable matrix: `augmented_skills_graph_section_source_audit.json`.
