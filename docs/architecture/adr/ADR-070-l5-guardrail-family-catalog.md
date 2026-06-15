# ADR-070: L5 Guardrail Family Catalog (G01–G29 Taxonomy)

**Status**: Accepted (catalog implemented)
**Date**: 2026-04-29
**Deciders**: Architecture leads + L5 owners
**Plan**: `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md` (Wave 1, Phase P8.01)
**Source**: 14 P1 Notion rows in W4 P8.x decomposition
**ADG snapshot**: `artifacts/adg/adg_indexed_04282026_2152.sqlite`

**Current-state note (2026-06-15):** The catalog and guardrail-family skeletons landed; subsequent net-new guardrail families remain tracked as separate phases, not open status for this catalog ADR.

## Context

The Wave 4 P8.x decomposition surfaced 14 P1 backlog items addressing distinct guardrail concerns (G01–G29) that have no canonical mapping to existing L5 modules. The Backlog Snapshot top-25 showed 14 of 25 P1 items belonging to this single conceptual decomposition, indicating the family was previously undecomposed.

The ADG hot-cache scan of `agentic_core/L5_safety/` (447 modules excluding `__init__.py` and `types/`) shows the existing structure is organized by mechanism (`runtime_gates/`, `enforcement/`, `audit/`, `adapters/`, `v5/`, `config/`) rather than by guardrail concern. This ADR catalogs the existing structure against the G01–G29 taxonomy so subsequent W4 phases (P8.02–P8.15) can target specific concerns rather than scattered files.

## Decision

Adopt the G01–G29 guardrail family taxonomy as the canonical concern decomposition for L5. Each existing L5 module is assigned exactly one G-id by path-fragment classification; modules that fit multiple concerns are tagged by primary concern.

## Final Mapping (100% coverage as of 2026-04-29 W2 extension)

| G-id | Concern | Module count | Primary path fragment |
|------|---------|-------------:|------------------------|
| G01 | Named guardrail family catalog (runtime gates) | 41 | `runtime_gates/` |
| G02 | Layered guardrail banks (client + agent) | 8 | `ingress/`, `adapters/`, `approval/` |
| G03 | Risk-tier proportionate enforcement | 1 | `severity` |
| G04 | End-user identity propagation | 21 | `identity/` |
| G07 | Capability token TTL & single-use | 2 | `token/` |
| G08 | Egress output-side AI firewall | 4 | `egress/` |
| G09 | Audit emission (cross-cutting) | 15 | `audit/` |
| G10 | Policy plane | 7 | `policy/` |
| G11 | Continuous red-team assurance | 2 | `redteam/` |
| G12 | Enforcement chokepoint | 106 | `enforcement/` |
| G14 | Structure blueprint (config) | 11 | `blueprint/`, `config/` |
| G16 | v5 governance plane | 17 | `v5/` |
| G17 | Healer/Classifier reasoning agents | 80 | `L5_safety/reasoning/` |
| G18 | Safety utilities (file ops, dedup, gates) | 57 | `L5_safety/utils/` |
| G19 | Validators (location, truth, schema) | 49 | `L5_safety/validators/` |
| G20 | Exit-eval grading spine | 14 | `L5_safety/eval_spine/` |
| G21 | Internal contracts (vocab, status enums) | 11 | `L5_safety/contracts/` |
| G22 | Exit control HITL | 1 | `L5_safety/exit_control/` |

**Total: 447 modules — 100% classified.**

**Authoritative inventory CSV**: `docs/reports/maintenance/l5_guardrail_family_catalog.csv`

### Classification History

- **2026-04-29 W1**: 235/447 (53%) auto-classified via path-fragment matching
- **2026-04-29 W2**: 212 G-UNCLASSIFIED modules drained by extending taxonomy with G17–G22 (six new G-ids capturing the `reasoning/`, `utils/`, `validators/`, `eval_spine/`, `contracts/`, `exit_control/` buckets). Result: 447/447 (100%).

## What's Missing (driver of subsequent W4 phases)

| G-id | Concern | Status | Owning phase |
|------|---------|--------|--------------|
| G05 | A2A handoff validation | **No matching modules** | W5 P8.05 |
| G06 | Graduated permission ladder | **No matching modules** | W5 P8.06 |
| G13 | Data perimeter SAIF sanitization | **No matching modules** | W4 P8.13 |
| G15 | Hard-vs-remediable rule tagging | **No matching modules** | W3 P8.15 |

These four concerns lack any L5 module today — subsequent phases must build new modules under the existing layout, tagged with their G-id at file header.

## Hotspot Concentration

Top-10 L5 modules by fan-in (from `mv_hotspot_centrality`):

| fan_in | Module | Concern | Risk |
|-------:|--------|---------|------|
| 198 | `L5_safety/runtime_gates/types.py` | G01 | High (poisons all runtime gates) |
| 115 | `L5_safety/v5/__init__.py` | G16 | Medium |
| 107 | `L5_safety/types/cst_transformers_types.py` | G-UNCLASSIFIED | Medium |
| 106 | `L5_safety/config/structure_blueprint/__init__.py` | G14 | Medium |
| 103 | `L5_safety/v5/types.py` | G16 | Medium |
| 80 | `L5_safety/config/structure_blueprint/ssot.py` | G14 | Medium |
| 61 | `L5_safety/runtime_gates/__init__.py` | G01 | High |
| 50 | `L5_safety/adapters/human_approval_adapter.py` | G02 | High (HITL channel) |
| 49 | `L5_safety/enforcement/ingress_envelope_check.py` | G12 | Medium |
| 48 | `L5_safety/runtime_gates/base.py` | G01 | High |

Wave 1 closure cleans up G01 + G16 (highest fan-in). G05/G06/G13/G15 (the missing-concern phases) are net-new code so their fan-in baseline is 0.

## Consequences

### Positive

- 14 disconnected backlog items collapse into 1 ADR + 1 inventory CSV — coherent execution path.
- Each subsequent W4 phase (P8.02–P8.15) targets a specific G-id with a known starting fan-in.
- The G-UNCLASSIFIED bucket (212 modules) becomes a deferred scope item with priority ranked by hotspot fan-in.

### Negative

- Manual classification of 212 unclassified modules is required before full coverage; deferred to a follow-up wave.
- The G05/G06/G13/G15 concerns require net-new code — risk of architectural drift if their phases run without referencing this ADR.

### Reversibility

This ADR is a classification overlay, not a code change. Reversible by removing G-id annotations and the CSV. No structural commitment.

## Acceptance

- [x] CSV inventory written: `docs/reports/maintenance/l5_guardrail_family_catalog.csv`
- [ ] G-id annotations added to L5 module file headers (W2+ work, post-ADR ratification)
- [ ] G-UNCLASSIFIED 212 modules triaged in follow-up wave (deferred)

## References

- Plan: `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`
- Inventory: `docs/reports/maintenance/l5_guardrail_family_catalog.csv`
- ADG snapshot: `artifacts/adg/adg_indexed_04282026_2152.sqlite`
- Notion W4 P8.x rows: 14 P1 items (top-25 backlog snapshot 2026-04-29)
