# H0 — Projection Pipeline Plan (Design Only)

wave: H0
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## 1. Purpose

Define the non-implementation projection plan for converting Wave G curated runtime truth into stability-labeled semantic cards for Wave H pilot.

This plan is scoping-only and does not execute projection, ingestion, or runtime writes.

## 2. Projection stages

| stage_id | stage | intent | output |
|---|---|---|---|
| H0-PP-01 | Source freeze and snapshot pin | bind all projection logic to one ADG snapshot + signed-off G artifacts | source manifest |
| H0-PP-02 | Surface extraction | extract runtime surfaces, ownership classes, pipelines, failure domains, residual links | normalized surface rows |
| H0-PP-03 | Family shaping | map normalized rows into card family templates with required metadata | card candidate records |
| H0-PP-04 | Stability labeling | label each card as canonical, special_case, or unresolved based on G7/G6 residual links | stability-tagged candidates |
| H0-PP-05 | Traceability annotation | add Wave F atom/edge links only when directly supported | traceability-enriched candidates |
| H0-PP-06 | Pilot filter | include only `safe_now` + allowed `safe_for_pilot_only` families | pilot candidate subset |
| H0-PP-07 | Gate report generation | produce pilot go/no-go evidence against readiness gates | gate evidence bundle |

## 3. Projection input contracts

Primary source groups:

- Structural truth: ADG snapshot (`04182026_0858`)
- Runtime topology and ownership: G5 + G7
- Storage/control-plane context: G4 + G4b
- Pipeline/state machine context: G3
- Residual and blocker posture: G6 + G7 registers
- Wave F traceability target IDs: v1.4 canonical atom/edge sets

## 4. Metadata contract for projected cards

Minimum cross-family metadata:

- `card_id`
- `card_family`
- `source_refs`
- `snapshot_id`
- `stability_status` (`canonical`, `special_case`, `unresolved`)
- `ownership_class` (`repo-managed`, `operator-managed`, `external-tool-owned`, `mixed-control`)
- `residual_links`
- `traceability_links` (Wave F atom/edge IDs when directly supportable)
- `pilot_eligibility` (`yes`/`no`)

## 5. Instability and safety controls

- Do not project unresolved blocker facts as canonical.
- Require explicit residual-link metadata when source artifact marks unresolved/partial posture.
- Exclude family segments tied to production-blocking residuals from pilot set.
- Maintain reversible pilot posture: no production dependency and no write-path coupling.

## 6. Pilot-to-production transition hooks

Production projection start must be gated by:

- canonical-state closure
- ownership formalization closure
- governance trust closure
- contract-authority closure

See `readiness_gates.md` and `go_no_go_matrix.md` for exact go/no-go conditions.
