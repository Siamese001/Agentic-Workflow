# Primary vs. Secondary Skill Analysis — apps_rg

## Scope

This analysis checks whether `apps_rg` currently has a primary/secondary **skill** distinction, separate from `link_class_by_fact` values on fact links.

## Findings

1. **There is no active `skill_class` field in the live skill rows.** A ledger scan found zero `skill_rows` with a `skill_class` key. The live distinction is therefore not encoded as a skill-level class.

2. **`primary` is used at the fact-link and graph-edge levels, not as a skill rank.** The live ledger uses `link_class_by_fact` to mark linked evidence as `"primary"`; the same scan found `primary` link-class values and no `secondary` link-class values. The ledger also has `primary_fact_id` metadata on some rows, and `graph_edges` use `"primary": true` for employment-to-track edges.

3. **Track-weighted scoring ignores primary/secondary fact classes.** In `build_track_weighted_expansion`, candidate score is computed from the resolved track weight and the row's `role_family_weights[role_family_key]`. The code filters for active/external-claim-eligible rows, matches row pillar to track, requires non-empty fact links, and then computes `score = w * (1.0 + rf_w)`. It does not inspect `link_class_by_fact`, `primary_fact_id`, or any `skill_class` field when ranking candidates.

4. **`primary` graph edges have a different meaning.** `_build_graph_indexes` uses `edge.get("primary") is True` on `employment_in_career_track` edges to record primary employment-track membership. That is routing/graph topology, not skill scoring.

## Recommendation

Reframe rather than add a new primary/secondary skill taxonomy. The current dynamic model already has clearer scoring axes: JD-inferred projection profile, pillar/track membership, and `role_family_weights`. If stronger evidence weighting is needed later, add an explicit, tested evidence-strength multiplier that consumes `link_class_by_fact` or `primary_fact_id`; do not introduce a separate `skill_class` unless there is a concrete scoring path and migration plan.

For the current PR, keep `link_class_by_fact` as evidence metadata and continue using pillar/role-family weights for skill selection. Treat any future `secondary` value as an evidence-link label until a scoring contract says otherwise.
