# W4 P8 Guardrail Family — L5 Security Burndown Wave

**Plan ID**: `w4-p8-guardrail-family-e93f8a`
**Status**: Todo
**Created**: 2026-04-28
**Source**: Backlog snapshot top-25 (14 P1 rows clustered in L5/Security)

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
