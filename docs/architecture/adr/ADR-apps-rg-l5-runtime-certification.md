# ADR: apps_rg L5 Runtime Certification

Status: Accepted

Date: 2026-07-06

## Context

apps_rg had core L5 certification primitives and a governance profile, but governed runtime runs did not materialize one machine-checkable `L5CertificationPacket` before Exit authorization or cache proposal emission.

## Decision

apps_rg owns app-specific L5 runtime assembly under `apps_rg/runtime/l5`. Core L5 remains app-agnostic and provides typed contracts, packet production, and metadata-only egress certification.

Runtime flow:

1. Load `apps_rg/profiles/rg_l5_governance_profile.yaml`.
2. Build child certifier receipts for safety, authority context, origin trust, replay/audit, static governance, runtime binding, conditional HITL reclearance, and conditional provider egress.
3. Build typed metadata-only egress receipts when ProviderGateway is invoked.
4. Build exactly one `L5CertificationPacket` and attach packet ref, digest, and status to the sealed L2 artifact.
5. Exit blocks allow and cache proposals when packet evidence is missing, malformed, `L5_NOT_CERTIFIED`, or backed only by the legacy test placeholder ref.
6. Exit cache proposals carry the L5 packet digest into the UWG/L4 evidence sidecar.

## Non-Authorities

L5 certification does not emit `GateVerdict`, does not emit X3, does not route, retrieve, execute, write L4, write durable cache, or rescue the current run. Eval results do not waive runtime gates.

Exit and L2 do not commit durable state. Durable cache persistence remains Exit proposal to UWG admission to L4 evidence.

## Consequences

The runtime gains fail-closed, replayable L5 evidence without widening L5 authority. CI enforces cert refs, no authority widening, packet runtime wiring, and no direct durable cache bypass.
