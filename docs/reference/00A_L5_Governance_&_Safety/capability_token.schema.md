# L5 Capability Token — v4 Schema & Lifecycle

**Scope**: Defines the `capability_token` structure bound at CERTIFY, consumed by L3 orchestration and L2 execution, and verified by L5 exit-control before any external action or state mutation.

**Covers gaps**: G-06 (graduated permission model), G-07 (TTL + single-use semantics), G-09 (context boundary scope), G-19 (plan digest transparency).

**Sources**:
- Anthropic *Framework for Safe & Trustworthy Agents* → read-only default, explicit mutation approval, persistent grants
- Anthropic *MCP* → one-time vs permanent connector grants
- Google *SAIF* → identity propagation, per-tool authorization scopes
- OpenAI *Governed Agents Cookbook* → Agent/Tool/Prompt registry-bound scoping
- Internal: ADR-023 (runtime HITL exit-control), ADR-044 (request intake envelope hardening)

---

## 1. Schema (v4)

```yaml
capability_token:
  # --- Identity & provenance -----------------------------------------
  token_id: str                      # UUIDv7; unique per CERTIFY
  issued_at: iso8601
  issuer: "L5_governance_plane"
  policy_version: semver             # SSOT policy package version
  compliance_hash: sha256            # pins the rule set + thresholds
  registry_digest: sha256            # pins all 4 registries at issue time

  # --- Scope ---------------------------------------------------------
  principal_chain:                   # see identity_propagation.md
    invoking_user: str
    agent_id: str
    parent_agent_id: str | null      # populated on A2A handoff
    delegation_depth: int            # 0 for direct invocation
    scope_tag: str                   # context compartment id (G-09)

  # --- Risk posture --------------------------------------------------
  risk_tier_band: LOW | MODERATE | HIGH
  hard_constraints_active: [str]     # list of rule IDs with hard_constraint=true

  # --- Permission ladder (G-06) -------------------------------------
  permission_ladder_entry:
    enum: [ read, suggest, mutate, external ]
    # read     : inspection, analysis, no side effects
    # suggest  : propose edits, render diffs, no apply
    # mutate   : apply changes inside trusted surface (repo, local state)
    # external : irreversible / external side-effect actions
  step_up_required_for: [str]        # actions that need step-up HITL

  # --- TTL / single-use (G-07) --------------------------------------
  ttl_seconds: int                   # band-derived cap
  expires_at: iso8601
  single_use: bool                   # true for HIGH band; token invalid after 1 execution
  persistent_grant_ref: str | null   # ref to enterprise-admin pre-grant, if any

  # --- Connector / tool authorization --------------------------------
  connector_allowlist: [connector_id]  # from MCP Connector Registry
  tool_allowlist: [tool_id]            # from Tool Registry
  grant_mode:
    enum: [ one_time, permanent, sessioned ]

  # --- Plan transparency (G-19) -------------------------------------
  plan_digest: sha256                # hash of the agent's declared plan
  plan_stream_endpoint: str | null   # live todo-stream for HITL mid-flight inspection

  # --- Sandbox binding ----------------------------------------------
  sandbox_envelope_ref: str          # links to sandbox_envelope record

  # --- Audit wiring --------------------------------------------------
  audit_log_ref: str
  replay_envelope_ref: str
  standards_fingerprint:             # (G-16)
    nist_ai_rmf: str
    iso_42001: str
    cosai_baseline: str
    sector_overlays: [str]           # HIPAA | SOX | GDPR | ...

  # --- Revocation ----------------------------------------------------
  revoked: bool
  revoked_at: iso8601 | null
  revocation_reason: str | null
```

---

## 2. Permission Ladder (G-06)

Inspired by Anthropic's Claude Code read-only-by-default pattern.

| Rung | Description | Band cap | Typical actions |
|---|---|---|---|
| `read` | Inspection only | LOW → any | File reads, ADG queries, searches |
| `suggest` | Propose changes, render diffs, no apply | LOW → any | Generate patch, dry-run, preview |
| `mutate` | Apply inside trusted surface | MODERATE+ | Write repo file, memory graph update, Notion row post |
| `external` | Irreversible / external side-effect | HIGH only | HTTP POST/DELETE, deploy, notify, cancel subscription |

**Ladder rules**:
- A token at rung `N` implicitly grants rungs `0..N` (monotone).
- Step-up to a higher rung requires either (a) HITL approval, or (b) a pre-existing `persistent_grant_ref`.
- `external` rung REQUIRES `single_use: true` unless bound to a persistent grant with enumerated `connector_allowlist`.

---

## 3. TTL / Single-Use (G-07)

| Band | `ttl_seconds` cap | `single_use` default |
|---|---:|:---:|
| LOW | 3600 (1h) | false |
| MODERATE | 900 (15m) | configurable |
| HIGH | 300 (5m) | **true** |

Persistent grants (Anthropic pattern) override these caps but MUST be:
- Registered in MCP Connector Registry or Tool Registry with `grant_mode: permanent`
- Tied to a specific `principal_chain.invoking_user`
- Scoped to specific `connector_allowlist` / `tool_allowlist`
- Revocable by enterprise admin at any time

---

## 4. Context Scope Tag (G-09)

`principal_chain.scope_tag` is a compartment identifier that:
- Is attached at G2 based on invoking context (task id, session id, or explicit compartment override).
- Is immutable for the token's lifetime.
- Gates cross-context information reads: tokens with scope_tag A cannot retrieve memory/cache entries marked scope_tag B unless an explicit cross-compartment grant exists.
- Enforced by F-16 Context Bleed Detector (`guardrail_families.md`).

---

## 5. Plan Digest + Stream (G-19)

- `plan_digest`: SHA-256 of the agent's declared to-do plan at CERTIFY time. Post-certification plan changes require re-entry through L5 (invalidate token, re-certify).
- `plan_stream_endpoint`: optional live stream of the agent's current step / next step for HITL mid-flight observation. Mirrors Anthropic Claude Code's real-time to-do checklist.

---

## 6. Lifecycle State Machine

```
        ┌────────────┐
   ─────► ISSUED     │  (CERTIFY stamp applied)
        └─────┬──────┘
              │ first use
              ▼
        ┌────────────┐
        │ IN_USE     │
        └─────┬──────┘
              │
    ┌─────────┼─────────┬──────────────┐
    │         │         │              │
    ▼         ▼         ▼              ▼
┌────────┐┌────────┐┌────────┐┌────────────────┐
│ EXPIRED││CONSUMED││REVOKED ││ STEP_UP_PENDING│
└────────┘└────────┘└────────┘└────────┬───────┘
  (ttl)   (single_use) (admin/         │
                        forensic)      │ HITL approve/deny
                                       ▼
                                 (re-issue or REJECT)
```

Any terminal state (EXPIRED / CONSUMED / REVOKED) requires re-entry through G1 for a new token.

---

## 7. Verification Contract

L5 exit-control (per ADR-023) MUST verify before any action:

1. `token_id` not in revocation list
2. `expires_at > now`
3. Action's required rung ≤ `permission_ladder_entry`
4. Action's connector / tool ∈ `connector_allowlist` / `tool_allowlist`
5. `single_use` not already consumed
6. `policy_version` matches active policy (or is within grace window)
7. `principal_chain.delegation_depth` ≤ band max (see `risk_tier_bands.md` §3)
8. `plan_digest` matches current declared plan (or step-up required)

Verification failure → REJECT; emit forensic event to Audit Plane.

---

## 8. Revocation

- Enterprise admin revocation: immediate, broadcast to L5 exit-control.
- Forensic revocation: triggered by Audit Plane on detected anomaly.
- Self-revocation: agent may surrender token (e.g., task complete).
- Revocation is terminal; a new token requires full L5 re-entry.

---

## 9. Out of Scope

- Concrete token serialization format (JWT? CBOR? — deferred).
- Signing / key management (deferred to security-hardening plane).
- Distributed revocation gossip protocol.
- Implementation — spawned by per-gap plans.
