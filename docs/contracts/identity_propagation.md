# Identity Propagation Contract — L5 v4

**Scope**: Defines how the **invoking principal** is chained through agent layers, MCP connectors, A2A handoffs, and backend tool calls — so every side effect is attributable to a specific end user identity rather than a broad service account.

**Covers gaps**: G-04 (end-user identity propagation), G-05 (A2A handoff governance).

**Sources**:
- Google *SAIF* + *Cloud CISO 2025 SAIF guidance* → "agents must propagate the actual user's identity and permissions to every backend tool they touch"
- Google *Agent Development Kit* → front-end auth → identity propagation → MCP auth → A2A auth → IAM
- Anthropic *Framework* → MCP connector allowlists, enterprise admin scoping
- OpenAI *handoff_description* pattern → specialist-to-specialist transfer with retained context

---

## 1. The Invariant

> **SAIF Principle 3**: *"Any actions taken by AI agents on a user's behalf should be properly controlled and permissioned, and agents should be instructed to propagate the actual user's identity and permissions to every backend tool they touch."*

**L5 Invariant**: Every `capability_token` carries a `principal_chain`. Every downstream L3/L2/tool invocation MUST carry that chain unaltered (append-only on handoff). A call without a valid principal_chain is REJECTED.

---

## 2. Principal Chain Structure

```yaml
principal_chain:
  invoking_user: str            # authenticated human (or system principal) at front door
  invoking_user_kind: enum      # { human, automation, system }
  auth_method: str              # how the invoker authenticated
  auth_issued_at: iso8601
  auth_expires_at: iso8601

  agent_id: str                 # registry-known agent currently executing
  agent_registry_digest: sha256

  parent_agent_id: str | null   # non-null on A2A handoff; chain extends
  handoff_history: [            # append-only audit of transfers
    {
      from_agent_id: str,
      to_agent_id: str,
      handoff_description: str,
      at: iso8601,
      reason: str,
      scope_delta: { added: [str], removed: [str] }
    }
  ]

  delegation_depth: int         # len(handoff_history); capped by risk_tier_band
  scope_tag: str                # context compartment (G-09)
  scopes: [str]                 # effective permission scopes in chain
```

---

## 3. Propagation Rules

### 3.1 Front-door authentication (invoker)
- The invoking principal authenticates via the front-door auth mechanism (local user session, API key, OAuth, etc.).
- L5 G2 resolves the principal and seeds the chain at `delegation_depth=0`.
- `invoking_user` is immutable for the chain's lifetime.

### 3.2 Agent execution
- Each agent inherits `principal_chain` from its entry point.
- Agents MAY NOT swap `invoking_user`.
- Agents MAY narrow `scopes` (drop only); they MAY NOT widen.

### 3.3 A2A handoff (G-05)
When agent A hands off to agent B:
1. B is looked up in Agent Registry; its allowed-model/mode are verified.
2. `handoff_description` is required and recorded.
3. `parent_agent_id = A.agent_id`; `agent_id = B.agent_id`.
4. `delegation_depth += 1`; rejected if > band cap (LOW=3, MODERATE=2, HIGH=1).
5. `scope_delta` is computed: B's effective scopes = A's scopes ∩ B's registry-declared scopes, optionally minus explicit `scope_delta.removed`.
6. Handoff Validation sub-lane (F-15) runs before B executes.

### 3.4 Tool invocation
- Each tool call from an agent MUST pass `principal_chain` to the tool layer.
- Tool-side authorization:
  - For Google Cloud / external IaaS tools: propagate as IAM context (SAIF pattern).
  - For MCP connectors: include chain in the MCP request envelope; MCP server enforces `connector_allowlist` match + principal authorization.
  - For internal tools: chain is logged, not authorized (internal trust boundary already closed).
- Tool output carries back any mutation attribution; Audit Plane correlates by `token_id` + `principal_chain.invoking_user`.

### 3.5 MCP Connector layer
- MCP Connector Registry (see Registries expansion, G-12) pins `allowed_principals` per connector entry.
- Enterprise admin can:
  - Allowlist which connectors a given `invoking_user` role may attach.
  - Grant one-time (per `token_id`) vs permanent (per principal) access.
- Per-call flow: token → MCP client → connector checks (token valid, principal allowed, connector in `connector_allowlist`) → dispatch.

### 3.6 A2A protocol (future / external agent-to-agent)
- When an agent invokes an external agent (A2A protocol), the chain is serialized into the A2A envelope.
- Receiving agent's L5 (if governed) re-validates the chain at its own G1 entry.
- Cross-boundary chain truncation is forbidden; receiving L5 either accepts the full chain or REJECTS the request.

---

## 4. Ban on Broad Service Accounts

Per SAIF explicit recommendation:

> *"We strongly advise against using service accounts that have broad access."*

**Prohibited patterns** (L5 will REJECT):
- Generic `agent_service_account` identities without a bound `invoking_user`.
- Tools that internally substitute their own identity for the caller's.
- MCP connectors that ignore `principal_chain` and use their own OAuth token.
- Multi-tenant side effects authorized by "agent did it" without user attribution.

**Exception path**: automation principals (`invoking_user_kind: automation`) are allowed but MUST be:
- Registered in Agent Registry with `execution_mode: automation`
- Scoped narrowly (no `external` rung unless explicitly granted)
- Audited with the same rigor as human principals

---

## 5. Identity Propagation Matrix

| Surface | Propagation Mechanism | Enforcement Point |
|---|---|---|
| Front-door invocation | Session / API key / OAuth | G2 Identity Propagation |
| Agent → sub-agent (A2A in-process) | `principal_chain` append | Handoff Validation (F-15) |
| Agent → MCP connector | MCP envelope extension | MCP client + connector registry |
| Agent → external HTTP tool (SAIF) | IAM / OIDC token exchange bound to `invoking_user` | Tool Registry + Policy Chokepoint |
| Agent → external agent (A2A protocol) | A2A envelope extension | Remote L5 G1 + local Handoff Validation |
| Agent → LLM provider | Gateway carries chain in audit metadata (provider is egress, not a principal consumer) | LLM Gateway audit log |
| Agent → internal DB / UWG state | `principal_chain` logged; write attribution | Write Gateway (UWG) |

---

## 6. Forensic Reconstruction

Every mutation in the system MUST be reconstructable to its originating `invoking_user` via:

1. `audit_log` → `token_id`
2. `token_id` → `capability_token.principal_chain`
3. `principal_chain.invoking_user` + `handoff_history`

This is the minimum bar for SAIF + NIST AI RMF attestation. The Audit / Forensic Plane (see `calibration_assurance_planes.md`) owns the reconstruction verifier.

---

## 7. Open Question (parent plan §10.3)

The parent plan flagged: *"Is end-user principal even meaningful in this single-operator workspace, or should propagation only model agent-chain principals?"*

**Recommended posture (not yet ratified)**:
- Even in single-operator mode, propagate the operator as `invoking_user` so future multi-user deployment is a no-op.
- Agent-chain principals compose *after* the invoker slot, never replace it.
- Automation / scheduled invocations use `invoking_user_kind: automation` with a designated automation principal ID.

This makes the contract deployment-invariant.

---

## 8. Out of Scope

- Concrete OIDC / IAM / OAuth flow wiring.
- MCP A2A protocol header spec (tracking external A2A standard evolution).
- Cryptographic binding of chain (signing / attestation).
- Implementation — spawned by per-gap plans.
