# G7 — Open Blockers and Acceptance

wave: G7
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## 1. Disposition model

- `resolved_in_g7`
- `accepted_residual_in_g`
- `open_blocker_post_g7`

## 2. G3 residuals (required carry-forward)

| residual_id | g7_disposition | owner | effect_on_whole_system_map_trust | blocks_wave_h_implementation | notes |
|---|---|---|---|---|---|
| B7-G3-01 | accepted_residual_in_g | eval/runtime governance owner | low-medium (naming ambiguity) | no | non-canonical eval spine naming remains potentially misleading |
| B7-G3-02 | accepted_residual_in_g | APP-RG + APP-EXEC owners | medium (bootstrap side-effect behavior) | no | kept visible as special-case startup shims |
| B7-G3-03 | accepted_residual_in_g | observability + architecture owners | medium (L6 observer-role purity) | no | does not invalidate runtime map but weakens strict role purity |
| B7-G3-04 | open_blocker_post_g7 | replay pipeline owner | medium-high (partial topology) | yes | replay topology completeness required for deterministic replay claims |
| B7-G3-05 | open_blocker_post_g7 | gateway/provider resilience owner | high (resilience mismatch) | yes | gateway-level circuit-breaker posture unresolved |
| B7-G3-06 | open_blocker_post_g7 | system_learning owner | medium-high (partial topology) | yes | incomplete system_learning topology constrains hard guarantees |

## 3. G4 residuals (required carry-forward)

| residual_id | class | owner | acceptance_rationale | visible_in_whole_system_runtime_map | blocks_wave_h_implementation |
|---|---|---|---|---|---|
| B7-G4-01 | hygiene-only | ADG/tooling owner | retention policy is ops hygiene, map remains correct | yes | no |
| B7-G4-02 | hygiene-only | ADG/tooling owner | legacy archive is vestigial and explicit | yes | no |
| B7-G4-03 | topology-blocking | memory owner + config owner | multiple candidate canonical memory stores break single-source clarity | yes | yes |
| B7-G4-04 | hygiene-only | cache/storage owner | orphan namespace does not define canonical runtime behavior | yes | no |
| B7-G4-05 | hygiene-only | vector/storage owner | vestigial artefact registry kept explicit | yes | no |
| B7-G4-06 | Wave-H-neutral | L4/write-sovereignty owner | direct mkdir/write bypass question remains policy interpretation gap | yes | no |
| B7-G4-07 | Wave-H-neutral | infra operator + cache owners | no TTL/eviction posture is operational risk but map correctness preserved | yes | no |

## 4. G4b residuals and operationalized risks (required carry-forward)

| residual_or_risk | control_plane_residual_only | affects_runtime_map_correctness | blocks_wave_h_implementation | must_appear_in_ownership_matrix_or_gap_register | disposition |
|---|---|---|---|---|---|
| B7-G2b-06 (`EGRESS_GUARD_DISABLED` audit gap) | yes | yes (trust posture) | yes | both | open_blocker_post_g7 |
| `DISABLE_RUNTIME_MUTATION_GUARD` bypass posture | yes | yes (write-governance trust) | yes | both | open_blocker_post_g7 |
| `SOVEREIGN_AUTO_APPROVE` / `ARCHIVE_BATCH_ACCEPT` override posture | yes | yes (governance trust) | no (if controlled) | both | accepted_residual_in_g |
| `MEMORY_DB` dual-plane ambiguity | no | yes | yes | both | open_blocker_post_g7 |
| `REDIS_URL` / `REDIS_*` multi-reader default ambiguity | yes | medium | no | gap register | accepted_residual_in_g |
| provider/model selector default-layering ambiguity | yes | medium | no | gap register | accepted_residual_in_g |

## 5. G5 residuals (required carry-forward)

| residual_or_issue | g7_disposition | owner | affects_wave_h_timing |
|---|---|---|---|
| opaque restart semantics (GitKraken/deepwiki/external-tool-owned) | accepted_residual_in_g | operator + external tool owners | no |
| mixed repo-managed vs operator-managed boundary zones | open_blocker_post_g7 (formalization incomplete) | runtime map owner | yes |
| dual-plane runtime ambiguity (MCP subprocess vs in-process) | accepted_residual_in_g | tooling + architecture owners | no |
| process-schema extension beyond minimal G0 contract | resolved_in_g7 (documented and stabilized) | G5/G7 map owner | no |
| unknown `restart_mode_if_known` values retained honestly | accepted_residual_in_g | respective process owners | no |

## 6. G6 blocker-class carry-forward (required)

| residual_id | g7_status | owner | acceptance_rationale | blocks_wave_h_implementation |
|---|---|---|---|---|
| B7-G6-01 | open_blocker_post_g7 | architecture + traceability owners | L_CONTRACTS dead/unwired status still unresolved | yes |
| B7-G6-02 | open_blocker_post_g7 | L2/L3 + traceability owners | duplicate execution-trace contract ownership still unresolved | yes |
| B7-G6-03 | open_blocker_post_g7 | memory + config owners | canonical-state memory store still unresolved | yes |
| B7-G6-04 | open_blocker_post_g7 | taxonomy owner | 337-module residual bucket still unresolved | yes |
| B7-G6-05 | open_blocker_post_g7 | runtime map owner | ownership formalization incomplete for mixed-control zones | yes |

## 7. Specific issues explicitly addressed

| issue | addressed_in_g7 | where |
|---|---|---|
| `agentic_core/L_CONTRACTS/` dead/unwired status | yes (left open) | this file §6, map `G7-RS-11` |
| duplicate execution-trace type surfaces | yes (left open) | this file §6, map `G7-RS-11` |
| memory SQLite triplet ambiguity | yes (left open) | this file §§3/4/6, map `G7-RS-04` |
| 337-module `role=other` residual bucket | yes (left open) | this file §6, map `G7-RS-02` |
| ownership-boundary formalization | yes (partially resolved, still open blocker) | this file §§5/6, ownership matrix |
| special-case startup shims/facades | yes (accepted residual) | this file §2, map `G7-RS-01` |
| declared-not-wired stubs | yes (accepted residual) | map `G7-RS-09`; final gap register |
| orphan/vestigial stores/namespaces | yes (accepted residual) | this file §3; final gap register |
| partial replay/system_learning surfaces | yes (open blockers) | this file §2 |
| gateway-level resilience mismatch | yes (open blocker) | this file §2 (`B7-G3-05`) |
| control-plane bypass posture | yes | this file §4 |
