# H1 — Owner Matrix

wave: H1
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## Required owner classes

- architecture owner
- runtime owner
- governance owner
- storage/config owner
- provider/gateway owner
- taxonomy owner

## Blocker-to-owner mapping

| blocker_id | architecture_owner | runtime_owner | governance_owner | storage_config_owner | provider_gateway_owner | taxonomy_owner | primary_accountable_owner |
|---|---|---|---|---|---|---|---|
| B7-G3-05 | advisory | supporting | supporting | n/a | primary | n/a | provider/gateway owner |
| B7-G4-03 / B7-G6-03 | supporting | supporting | advisory | primary | n/a | n/a | storage/config owner |
| B7-G2b-06 | advisory | supporting | primary | n/a | supporting | n/a | governance owner |
| DISABLE_RUNTIME_MUTATION_GUARD | supporting | supporting | primary | n/a | n/a | n/a | governance owner |
| B7-G6-01 | primary | supporting | advisory | n/a | n/a | n/a | architecture owner |
| B7-G6-02 | primary | supporting | advisory | n/a | n/a | n/a | architecture owner |
| B7-G6-04 | advisory | supporting | advisory | n/a | n/a | primary | taxonomy owner |
| B7-G6-05 | primary | supporting | supporting | n/a | supporting | advisory | architecture owner |

## Owner collaboration rules

1. Primary accountable owner signs closure recommendation.
2. Supporting owners provide evidence in their control plane/domain.
3. Advisory owners validate cross-domain side effects.
4. Any owner disagreement keeps blocker open until resolved.
