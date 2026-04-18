# H0 — Card Family Design

wave: H0
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## Status enum

- `safe_now`
- `safe_for_pilot_only`
- `wait_for_blocker_resolution`

## Card family evaluation

| card_family | status | source_of_truth | projection_inputs | minimum_metadata | known_instability_risks | best_first_use_case |
|---|---|---|---|---|---|---|
| symbol cards | safe_now | ADG node/edge graph + G1 inventories | ADG nodes (`symbols` layer), `component_inventory.yaml`, G7 traceability | symbol_id, file_path, layer, inbound/outbound refs, confidence, snapshot_id | low if sourced from ADG exact graph only | architecture Q&A symbol grounding |
| path cards | safe_now | ADG structural paths + G2 canonical walk | ADG fan-in/fan-out, `canonical_request_walk.md`, `whole_system_runtime_map.md` | path_id, src, dst, relation_chain, layer_crossings, snapshot_id | medium for dynamic dispatch paths | impact-analysis and dependency walk explanations |
| violation cards | safe_for_pilot_only | G2/G3/G4/G4b/G7 violation and residual docs | `boundary_violations.md`, `open_blockers_and_acceptance.md`, `final_gap_register.md` | violation_id, category, severity, owner, residual_status, evidence_refs | medium-high: posture can change as blockers close | governance review and residual triage assistants |
| hotspot cards | safe_now | ADG centrality/chokepoint evidence + G2 bridge findings | ADG chokepoint metrics, `import_edge_matrix.md`, runtime map | hotspot_id, metric_type, value, path, rationale, snapshot_id | low-medium (recomputed each snapshot) | C0 assembly prioritization and risk-aware navigation |
| pipeline cards | safe_for_pilot_only | G3 pipeline catalogue + G7 integrated map | `pipeline_catalogue.yaml`, `state_machines.md`, G7 map | pipeline_id, triggers, stages, outputs, partial_flag, owner | medium-high due partial replay/system_learning and naming residuals | app runtime explainability for pilot apps |
| state-machine cards | safe_for_pilot_only | G3 state machine docs | `state_machines.md`, `trigger_matrix.md` | sm_id, states, transitions, invariants, unresolved_notes | medium where non-canonical naming or partial topology exists | failure-mode explanations for eval/healing flows |
| storage/control-plane cards | wait_for_blocker_resolution | G4 storage + G4b knobs + G7 ownership/residual set | `storage_catalogue.yaml`, `config_knob_catalogue.yaml`, ownership matrix | store_id/knob_id, authority_plane, owner, risk_level, canonical_state_flag | high: memory canonical-state ambiguity and governance bypass posture | production runbooks after blocker closure |
| failure-domain cards | safe_now | G5 failure domains + G7 ownership and blockers | `failure_domains.md`, `whole_system_runtime_map.md`, `open_blockers_and_acceptance.md` | fd_id, blast_radius, dependencies, owner_class, residual_links | low-medium in mixed-control zones | operator-facing incident triage assistant |

## Family-level inclusion policy for H pilot

Included in pilot:

- symbol cards
- path cards
- hotspot cards
- failure-domain cards
- restricted pipeline/state-machine cards (non-partial and clearly canonical segments only)

Excluded from pilot:

- storage/control-plane cards as canonical production truth cards
- replay/system_learning deep cards
- any card asserting resolved ownership/canonical-state where blockers remain open

## Family-level production prerequisites

Before production enablement of full family set:

- close memory canonical-state blockers (`B7-G4-03`, `B7-G6-03`)
- close ownership formalization blocker (`B7-G6-05`)
- resolve contract-authority blockers (`B7-G6-01`, `B7-G6-02`)
- remediate governance trust blockers (`B7-G2b-06`, mutation-guard bypass posture)
