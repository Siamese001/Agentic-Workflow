# H1 — Blocker Breakdown

wave: H1
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## Mandatory production-blocking set

| blocker_id | source_wave | why_it_blocks_h_production | weakens_pilot_trust | exact_closure_condition | minimum_evidence_for_closure | likely_owner | likely_remediation_type | can_parallelize | downstream_effect_on_card_families |
|---|---|---|---|---|---|---|---|---|---|
| B7-G3-05 | G3 | unresolved gateway-level resilience mismatch undermines production reliability claims for runtime reasoning surfaces | medium | gateway resilience contract is explicitly normalized and enforced to agreed minimum (gateway-level or equivalent formally accepted posture) | updated gateway resilience policy/spec, test evidence for failure-handling path, residual register closed | provider/gateway owner | resilience_hardening | yes (after ownership baselines are clear) | pipeline, state-machine, violation, failure-domain cards |
| B7-G4-03 | G4 | canonical memory state is ambiguous across multiple SQLite candidates | low (if excluded in pilot) | one canonical memory store designated and enforced; alternate stores classified and bounded | canonical-state ADR/decision record, config binding proof, runtime read-path evidence | storage/config owner + runtime owner | canonical_state_decision | yes (paired with B7-G6-03) | storage/control-plane, pipeline, violation cards |
| B7-G6-03 | G6 | same canonical memory-state ambiguity as G4, explicitly carried as blocker | low | same closure as B7-G4-03, with G6 blocker closed | G6/G7 residual closure updates + same evidence bundle as above | storage/config owner + runtime owner | canonical_state_decision | yes (paired with B7-G4-03) | storage/control-plane, pipeline cards |
| B7-G2b-06 | G2b/G4b | egress guard disable path lacks auditable governance trail; production trust posture weakened | low-medium | auditable egress-guard override controls with traceability and policy constraints | governance control spec, audit log schema/evidence, control test results | governance owner + provider/gateway owner | governance_hardening | yes | violation, storage/control-plane, failure-domain cards |
| DISABLE_RUNTIME_MUTATION_GUARD | G4b | mutation-guard bypass posture can invalidate governance-trust assumptions for production cards | medium | bypass is constrained, audited, and policy-governed with explicit operational contract | bypass governance policy, audit records, enforcement test suite evidence | governance owner + runtime owner | governance_hardening | yes | violation, storage/control-plane, pipeline cards |
| B7-G6-01 | G6 | L_CONTRACTS dead/unwired status leaves contract-authority ambiguity unresolved | low (if excluded in pilot) | contract surface explicitly dispositioned (canonical/adopted, archived, or declared non-authoritative) | architecture decision record + import/usage evidence + residual closure entry | architecture owner | contract_authority_resolution | no (dependency for B7-G6-02 clarity) | symbol, path, pipeline, state-machine cards |
| B7-G6-02 | G6 | duplicate execution-trace ownership creates conflicting authoritative contract semantics | medium | single authoritative execution-trace contract owner designated and duplicate surface dispositioned | ownership decision record, reference mapping, residual closure update | architecture owner + runtime owner | contract_authority_resolution | partially (after B7-G6-01 stance set) | pipeline, state-machine, violation cards |
| B7-G6-04 | G6 | large unresolved taxonomy bucket prevents production-safe broad card packaging | low (if pilot subset constrained) | unresolved bucket reduced to production-safe classified subsets or bounded deferred taxonomy with strict exclusion rules | taxonomy decomposition report, classification coverage metrics, acceptance register update | taxonomy owner | taxonomy_closure | yes | symbol, hotspot, violation, pipeline cards |
| B7-G6-05 | G6/G7 | mixed ownership boundary not fully formalized for production trust guarantees | medium | ownership classes formalized per-surface with no unresolved mixed-control ambiguity in production scope | ownership matrix closure evidence, per-surface owner tags, residual closure update | architecture owner + runtime owner + governance owner | ownership_formalization | no (foundation dependency) | all families, especially storage/control-plane and failure-domain |

## Secondary residuals (defer/accept/watch)

| residual | classification | handling posture |
|---|---|---|
| B7-G3-04 partial replay topology | defer/watch | keep excluded from production card scope; track for later replay-depth wave |
| B7-G3-06 partial system_learning topology | defer/watch | exclude system_learning-deep production claims until topology completion |
| REDIS_URL / REDIS_* default ambiguity | watch | maintain explicit caveat in control-plane metadata until normalized |
| provider/model selector layering ambiguity | watch | keep runtime-routing caveats and avoid over-claiming deterministic routing |
| SOVEREIGN_AUTO_APPROVE / ARCHIVE_BATCH_ACCEPT override posture | accept-with-guard | keep as governance watch with strict policy visibility |
| G5 opaque restart semantics | accept/watch | retain operational ambiguity labels in failure-domain/ownership cards |
