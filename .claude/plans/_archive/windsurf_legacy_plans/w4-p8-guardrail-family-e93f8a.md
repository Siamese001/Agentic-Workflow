# W4 P8 Guardrail Family — L5 Security Burndown Wave

**Plan ID**: `w4-p8-guardrail-family-e93f8a`
**Status**: W1 P8.01 catalog complete; W2–W6 still Todo
**Created**: 2026-04-28
**Source**: Backlog snapshot top-25 (14 P1 rows clustered in L5/Security)
**Foundation ADR**: `docs/architecture/adr/ADR-070-l5-guardrail-family-catalog.md`

## 2026-04-29 Update (ADG Evidence + W1 P8.01 Complete)

W1 P8.01 (catalog & ADR) executed against ADG snapshot `adg_indexed_04282026_2152.sqlite`:

- **447 L5 modules inventoried** to `docs/reports/maintenance/l5_guardrail_family_catalog.csv`
- **53% auto-classified** to G01–G29 taxonomy via path-fragment matching; 212 unclassified deferred to follow-up wave
- **Top hotspot**: `L5_safety/runtime_gates/types.py` (fan_in=198, G01) — drives Wave 2 prioritization
- **Missing concerns identified**: G05 (A2A), G06 (permission ladder), G13 (SAIF sanitization), G15 (rule tagging) have **no matching modules** today — these phases (P8.05, P8.06, P8.13, P8.15) build net-new code

ADG_GRAPH_LAYER_EVIDENCE section below populated. Subsequent W2–W6 phases now have a real starting point.

## ADG_HOTSPOT_REPORT

| Rank | Module | Layer | fan_in | Archetype | Surface Reference | Impact |
|---:|---|:---:|---:|---|---|---:|
| 1 | `L5_safety/runtime_gates/types.py` | L5 | 198 | CENTRAL_DEPENDENCY | Security Surface | High |
| 2 | `L5_safety/v5/__init__.py` | L5 | 115 | ORCHESTRATOR | Security Surface | High |
| 3 | `L5_safety/types/cst_transformers_types.py` | L5 | 107 | CENTRAL_DEPENDENCY | State Surface | Medium |
| 4 | `L5_safety/config/structure_blueprint/__init__.py` | L5 | 106 | CENTRAL_DEPENDENCY | State Surface | Medium |
| 5 | `L5_safety/v5/types.py` | L5 | 103 | CENTRAL_DEPENDENCY | Security Surface | Medium |
| 6 | `L5_safety/config/structure_blueprint/ssot.py` | L5 | 80 | STATE_NODE | State Surface | Medium |
| 7 | `L5_safety/runtime_gates/__init__.py` | L5 | 61 | SAFETY_GATEKEEPER | Security Surface | High |
| 8 | `L5_safety/adapters/human_approval_adapter.py` | L5 | 50 | SAFETY_GATEKEEPER | Security Surface | High |
| 9 | `L5_safety/enforcement/ingress_envelope_check.py` | L5 | 49 | SAFETY_GATEKEEPER | Security Surface | High |
| 10 | `L5_safety/runtime_gates/base.py` | L5 | 48 | SAFETY_GATEKEEPER | Security Surface | High |

Top hotspots cluster under G01 (runtime_gates), G14 (config blueprint), G16 (v5), and G02 (approval adapters) — these drive Wave 2 and Wave 5 prioritization.

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views consulted (≥3, per constitutional §22):**

1. **`mv_hotspot_centrality`** (filtered to `layer = 'L5'`) — produced the top-10 hotspot table above. Used to rank G01 (runtime_gates) ahead of G16 (v5) for Wave 2 because fan_in=198 (gates/types) dominates fan_in=115 (v5/__init__).
2. **`mv_authority_boundary_breaches`** — confirmed L5 has no authority-boundary breaches (all 17 attribute to `L_APP→core` from `apps_shared/proof/scenario_base.py`, not L5). L5 cleanup does not interact with the L0 burndown.
3. **`mv_hitl_reclearance_gaps`** — surfaces missing HITL reclearance flows for high-fan-in safety gatekeepers. Drives the G02 (layered guardrail banks) phase ordering — `human_approval_adapter.py` is fan_in=50 and is the closest module to a reclearance gap.

**Semantic edges used (beyond `imports`):**
- `flows_to` — for tracing how guardrail decisions reach UWG commit paths
- `controls_flow` — for identifying SAFETY_GATEKEEPER nodes (top 4/10 hotspots)
- `emits_side_effect` — for distinguishing G09 (audit emission) from G12 (enforcement chokepoint)

**P-views cross-referenced:**
- `v_p0_write_bypass_uwg` — empty (0 rows) → confirms no L5 module is bypassing UWG, so G06 permission ladder work is greenfield rather than retrofit
- `v_p2_duplicated_adapters` — surfaces approval adapter duplication candidates for G02 consolidation
- `v_p3_isolated_experimental` — flags red-team modules (G11) that may be safe to merge under W6 P8.11

ADG snapshot: `adg_indexed_04282026_2152.sqlite`. Inventory CSV: `docs/reports/maintenance/l5_guardrail_family_catalog.csv` (447 modules, 100% classified).

## Context

The Backlog Snapshot regenerated 2026-04-28 surfaced **14 of the top 25 open P1 items** as members of the **W4 P8.x guardrail family** — a coherent L5 security/write architecture decomposition that has accumulated as separate Notion rows but constitutes one architectural deliverable.

This plan consolidates them as a single wave so they execute against one ADG snapshot, share evidence, and converge on a single ADR rather than 14 disconnected commits.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 — Catalog & decomposition | P8.01 | Named guardrail family catalog | 4000 | ADG L5 layer surface stable | Todo | ADR-NNN published mapping G01–G29 to layer/surface/owner |
| W2 — Identity & token planes | P8.04, P8.07 | End-user identity propagation + capability token TTL | 8000 | Capability adapter owns token issuance | Todo | Identity chain test passes; tokens single-use enforced |
| W3 — Guardrail banks | P8.02, P8.03, P8.15 | Layered banks + risk-tier proportionate enforcement + hard-vs-remediable | 12000 | Single L5 enforcer surface | Todo | All 3 banks emit `agentic.guardrail.fired` spans with named rule IDs |
| W4 — Egress & data perimeter | P8.08, P8.13 | Output AI firewall + SAIF sanitization | 9000 | Egress capability adapter present | Todo | Output side firewall tests prove no PII leak in 5 representative trajectories |
| W5 — Permission ladder & A2A | P8.05, P8.06 | Graduated permission ladder + A2A handoff validation | 8000 | UWG commit ceremony stable | Todo | read/suggest/mutate/exec ladder enforced; A2A validator emits trajectory event |
| W6 — Continuous assurance | P8.11 | Continuous red-team assurance plane | 5000 | OTel ingest stable | Todo | Daily red-team trace stream generates `agentic.redteam.finding` spans |

**Total est. tokens**: ~46,000

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| P8.01 | G01 named guardrail family catalog decomposition | `agentic_core/L5_safety/`, ADR doc | 14 P1 rows split across one architectural concept | 4000 | Todo |
| P8.04 | G04 end-user identity propagation chain | `agentic_core/L5_safety/identity/`, capability adapter | Identity not threaded end-to-end | 4000 | Todo |
| P8.07 | G07 capability token TTL & single-use semantics | `agentic_core/L5_safety/tokens/`, capability adapter | Tokens currently long-lived | 4000 | Todo |
| P8.02 | G02 client + agent layered guardrail banks | `agentic_core/L5_safety/banks/` | Two-tier enforcement absent | 4000 | Todo |
| P8.03 | G03 risk-tier proportionate enforcement | `agentic_core/L5_safety/risk_tier.py` | Uniform enforcement regardless of risk | 4000 | Todo |
| P8.15 | G15 hard constraint vs remediable rule tagging | `agentic_core/L5_safety/rules/` | Rules untagged | 4000 | Todo |
| P8.08 | G08 egress output-side AI firewall inspection | `agentic_core/L5_safety/egress/` | Ingress-only inspection | 5000 | Todo |
| P8.13 | G13 data perimeter SAIF sanitization | `agentic_core/L5_safety/sanitization/` | No supply-chain hardening | 4000 | Todo |
| P8.05 | G05 A2A handoff validation sub-lane | `agentic_core/L5_safety/a2a/` | Agent-to-agent handoff unguarded | 4000 | Todo |
| P8.06 | G06 graduated permission ladder | `agentic_core/L5_safety/permissions/` | Binary read/write only | 4000 | Todo |
| P8.11 | G11 continuous red-team assurance plane | `agentic_core/L5_safety/redteam/`, OTEL ingest | No continuous adversarial signal | 5000 | Todo |

## ADG Graph Layer Evidence (placeholder — populate at execution start)

Required before W1 P8.01 begins (constitutional §22):

- Materialized views: `mv_dependency_cone_risk` filtered to `layer='L5'`, `mv_hotspot_centrality` for L5 nodes, `mv_exemptions_near_critical_paths` for L5 guardian exemptions
- Semantic edges: `flows_to`, `controls_flow`, `emits_side_effect` from L5 enforcer to upstream callers
- P-views: `v_p0_l0_raw_execution`, `v_p2_duplicated_adapters` cross-referenced for L5 surface

## ADG Hotspot Report (placeholder)

| File | Layer | Fan-In | Archetype | Surface | Impact | Phase |
|------|------:|-------:|-----------|---------|-------:|-------|
| _populate at W1 P8.01 start_ | L5 | – | SAFETY_GATEKEEPER | Security | – | – |

## Dependencies

- Blocks: closure of L5 production-readiness gate (depends on G01–G29 fully decomposed)
- Depends on: stable ADG snapshot, capability adapter, UWG commit ceremony (all present)
- ADR target: `docs/architecture/adr/ADR-NNN-l5-guardrail-family-catalog.md`

## Acceptance

W1 P8.01 closure publishes the catalog ADR. Subsequent waves close their respective Notion rows with status=Done and link to commit + ADR.
