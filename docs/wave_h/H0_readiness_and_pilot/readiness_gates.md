# H0 — Readiness Gates

wave: H0
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 1. Gate categories

- **Pilot-start gates**: minimum conditions to begin bounded H pilot.
- **Production-start gates**: mandatory conditions to begin full H implementation.

## 2. Pilot-start gates (must all pass)

| gate_id | gate | pass_criteria | evidence_source |
|---|---|---|---|
| H0-PG-01 | ADG health and snapshot consistency | `adg_health` healthy; snapshot path/timestamp recorded in all H0 artifacts | ADG MCP health/status + H0 headers |
| H0-PG-02 | G7 integrated baseline stability | all six G7 artifacts present and internally consistent | `docs/wave_g/G7_integrated_runtime_map/*` |
| H0-PG-03 | residual classification complete | mandatory residual set classified into `blocks_h_pilot` / `blocks_h_production` / `does_not_block_h` | `go_no_go_matrix.md` |
| H0-PG-04 | pilot scope bounded and non-production | pilot limited to 1–2 app use cases, limited card families, no production dependency | `pilot_scope.md` |
| H0-PG-05 | card-family instability controls | each pilot card family defines instability risk and fallback behavior | `card_family_design.md` |
| H0-PG-06 | governance-safe posture | pilot excludes policy-sensitive canonical claims tied to unresolved blockers | `card_family_design.md`, `go_no_go_matrix.md` |

## 3. Production-start gates (must all pass)

| gate_id | gate | pass_criteria | blocker_mapping |
|---|---|---|---|
| H0-PR-01 | canonical-state closure | memory canonical-state ambiguity resolved | `B7-G4-03`, `B7-G6-03` |
| H0-PR-02 | ownership formalization closure | mixed repo/operator/external ownership boundaries formalized at production granularity | `B7-G6-05` |
| H0-PR-03 | contract-authority closure | dead/unwired contract surface and duplicate execution-trace ownership resolved | `B7-G6-01`, `B7-G6-02` |
| H0-PR-04 | governance-trust closure | egress guard audit gap and runtime mutation-guard bypass posture remediated and auditable | `B7-G2b-06`, `DISABLE_RUNTIME_MUTATION_GUARD` |
| H0-PR-05 | taxonomy closure for production packaging | large unresolved taxonomy bucket reduced to production-safe labeling posture | `B7-G6-04` |
| H0-PR-06 | resilience minimum for production Q&A/impact workflows | gateway-level resilience mismatch dispositioned to acceptable production standard | `B7-G3-05` |

## 4. Residual impact classification for H gates

| residual_or_issue | classification | gate_impact |
|---|---|---|
| B7-G3-04 partial replay topology | does_not_block_h | pilot ok if replay cards excluded; production replay family deferred |
| B7-G3-05 gateway-level resilience mismatch | blocks_h_production | requires production resilience posture alignment |
| B7-G3-06 partial system_learning topology | does_not_block_h | pilot ok if system_learning cards excluded |
| B7-G4-03 memory SQLite triplet ambiguity | blocks_h_production | blocks canonical-state claims |
| B7-G2b-06 egress guard audit gap | blocks_h_production | blocks governance-trust production gate |
| DISABLE_RUNTIME_MUTATION_GUARD bypass posture | blocks_h_production | blocks governance-trust production gate |
| B7-G6-01 L_CONTRACTS dead/unwired status | blocks_h_production | blocks contract-authority production gate |
| B7-G6-02 duplicate execution-trace ownership | blocks_h_production | blocks contract-authority production gate |
| B7-G6-03 memory canonical-state decision | blocks_h_production | same as canonical-state closure |
| B7-G6-04 role=other taxonomy bucket | blocks_h_production | blocks production-safe broad packaging |
| B7-G6-05 ownership formalization completion | blocks_h_production | blocks ownership clarity production gate |

## 5. Gate decision summary

- **Pilot start**: PASSABLE now (with bounded scope and exclusions).
- **Production start**: NO-GO until production blockers close.
