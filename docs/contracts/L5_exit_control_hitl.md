# L5 ⇄ L3 Contract — Runtime HITL Exit Control

- **Contract ID:** `L5_exit_control_hitl`
- **Status:** DRAFT
- **Date:** 2026-04-21
- **Peers:** L3 orchestration, L5 safety (cross-cutting policy plane)
- **ADR:** `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
- **Plan:** `.windsurf/plans/runtime-hitl-exit-control-c4e7b3.md`
- **Not coupled to:** developer-loop harness, `.windsurf/` artifacts, guardian exemptions

---

## 1. Scope

Defines the boundary, call shapes, invariants, and observability requirements between:

- **L3 orchestration** — runs production agents, produces sealed L2 artifacts, dispatches
  exit-control disposition, invokes the Universal Write Gate (UWG)
- **L5 safety** — policy authority for escalation classification, approver-pool resolution,
  timeout + fallback semantics, adapter binding

This contract governs only the **runtime** path at v30 step [5]. It does not govern
developer-loop gating, IDE approvals, or any `.windsurf/` behavior.

---

## 2. Invariants

| # | Invariant |
|---|-----------|
| I1 | L3 never decides escalation *class* or *approver pool* — L5 is sole authority |
| I2 | L5 never writes to L4 directly — all writes flow UWG |
| I3 | Every ESCALATE_HITL dispatch produces exactly one `hitl.escalate` OTel span |
| I4 | Every escalation terminates with exactly one of: `hitl.approved`, `hitl.denied`, `hitl.timeout` (no silent drops) |
| I5 | On timeout, fallback is applied per L5 policy class — default DENY when policy unspecified |
| I6 | Policy snapshot version is bound to the escalation record at dispatch time (not resolution time) |
| I7 | Runtime HITL ledger is distinct from developer `decision_ledger.db` (no shared table, no shared row) |
| I8 | Guardrail enforcement runs before exit-control; escalation only reached on guardrail-pass (serial, not parallel) |
| I9 | Suspension affects only the specific run (keyed by `run_id`); other runs continue unaffected |
| I10 | Approver identity is bound to the identity-provider subject (no anonymous approvals) |

---

## 3. Call Shapes

### 3.1 L3 → L5: classify escalation

```python
# agentic_core.L5_safety.exit_control.hitl_policy
def classify_escalation_class(
    envelope: SealedFolder,
    policy_snapshot: str,        # e.g. "runtime_hitl_policy.yaml@<sha>"
) -> EscalationClass | None:
    """Return escalation class, or None if no escalation required.

    None → caller must proceed with its other exit-control logic (DENY | COMMIT).
    Non-None → caller MUST dispatch via hitl_escalator.
    """
```

`EscalationClass` ∈ {`financial`, `safety`, `regulated`, `novel_context`,
`low_confidence`, `policy_override`} — enumerated in
`agentic_core/L5_safety/exit_control/hitl_classes.py`.

### 3.2 L3 → L5: resolve approver pool

```python
def resolve_approver_pool(
    esc_class: EscalationClass,
    tenant: str,
    ts: datetime,
) -> ApproverPool:
    """Return adapter binding + pool members + timeout + fallback."""
```

```python
@dataclass(frozen=True)
class ApproverPool:
    adapter: str                  # "notion" | "slack" | "orkes" | "email_magic_link"
    members: list[ApproverRef]    # identity-provider subject IDs
    timeout_s: int
    fallback: FallbackAction      # DENY | ESCALATE_TO_POOL_B
    fallback_pool: Optional["ApproverPool"]
```

### 3.3 L3 → L5: dispatch escalation

```python
# agentic_core.L3_orchestration.exit_control.exit_controller
def dispatch_escalation(
    run_id: str,
    trace_id: str,
    envelope: SealedFolder,
    esc_class: EscalationClass,
    pool: ApproverPool,
    policy_snapshot: str,
) -> PendingEscalation:
    """Enqueue via adapter; persist ledger record; emit hitl.escalate span;
    suspend the run keyed by run_id. Returns a handle for later resume.
    """
```

### 3.4 Adapter → L3: resume

```python
# Callback path — adapter delivers decision asynchronously
def on_approver_decision(
    run_id: str,
    decision: Decision,           # APPROVED | DENIED
    approver_id: str,
    rationale: str | None,
) -> None:
    """Resume the suspended run, emit terminal span, route through exit_controller
    to UWG (on APPROVED) or DENY/REROUTE (on DENIED).
    """
```

### 3.5 Scheduler → L3: timeout

```python
def on_escalation_timeout(run_id: str) -> None:
    """Apply fallback from ApproverPool. Emit hitl.timeout span.
    If fallback_pool is set, re-dispatch; else route to DENY.
    """
```

---

## 4. Data Shapes

### 4.1 Runtime HITL ledger record

```json
{
  "event_id": "evt_<ulid>",
  "run_id": "run_<ulid>",
  "trace_id": "<w3c_trace_id>",
  "tenant": "<tenant_id>",
  "ts_dispatched": "<iso8601>",
  "ts_resolved": "<iso8601|null>",

  "esc_class": "financial|safety|regulated|novel_context|low_confidence|policy_override",
  "policy_snapshot": "runtime_hitl_policy.yaml@<sha>",
  "envelope_ref": "<immutable_pointer>",

  "pool": {
    "adapter": "notion|slack|orkes|email_magic_link",
    "members": ["<subject_id>", ...],
    "timeout_s": <int>,
    "fallback": "DENY|ESCALATE_TO_POOL_B"
  },

  "resolution": {
    "outcome": "APPROVED|DENIED|TIMEOUT",
    "approver_id": "<subject_id|null>",
    "rationale": "<free_text|null>",
    "latency_ms": <int>,
    "fallback_taken": "DENY|ESCALATE_TO_POOL_B|null"
  },

  "integrity": {
    "prev_hash": "<sha256>",
    "hash": "<sha256>",
    "sig_alg": "ed25519|none",
    "signature": "<b64|null>"
  }
}
```

### 4.2 OTel span attributes (mandatory)

| Span | Attributes |
|------|------------|
| `hitl.escalate` | `run_id`, `trace_id`, `esc_class`, `approver_pool.adapter`, `approver_pool.timeout_s`, `policy_snapshot` |
| `hitl.approved` | `run_id`, `trace_id`, `approver_id`, `latency_ms`, `rationale_len` |
| `hitl.denied` | `run_id`, `trace_id`, `approver_id`, `latency_ms`, `reason_code` |
| `hitl.timeout` | `run_id`, `trace_id`, `timeout_s`, `fallback_taken` |

Spans produced by `agentic_core/L3_orchestration/exit_control/exit_controller.py` using the
tracer from `tools/otel/otel_mcp_server.py` conventions. Ingest via existing
`otel_ingest_to_runtime_adg` path.

---

## 5. Non-Overlap With Other Systems

| System | Overlap | Delineation |
|--------|---------|-------------|
| Guardrail chokepoint (`execution_guardrail_chokepoint`) | Both gate writes | **Serial, not parallel.** Guardrail runs first (pre-L2-seal). Exit-control runs after seal. If guardrail blocks, no escalation. Not double-gating. |
| Developer harness (`.windsurf/` gates) | Both use "approval" language | Completely disjoint: different humans (developer vs end-user/SRE), different timing (IDE vs runtime), different state stores, different retention |
| Guardian exemptions (`anti-pattern-hitl-gate`) | Both are HITL-adjacent | Guardian exemptions are **source-code** comments for developer-loop anti-patterns. Runtime HITL escalates **runtime actions**. No shared path. |
| UWG | Both are write-control | Runtime HITL produces APPROVED escalations which enter UWG as normal commit requests. UWG authority unchanged. |
| Shadow eval (step [6]) | Both produce learning signals | Runtime HITL **feeds** step [6] via `runtime_hitl_consumer.py`. Drafts only; UWG gates promotion. |

---

## 6. Failure Modes & Handling

| Failure | Required behavior |
|---------|-------------------|
| Adapter enqueue fails | Retry with backoff (max 3); on final failure, fail-closed → DENY, emit `hitl.denied` with `reason_code=adapter_unreachable` |
| Ledger write fails | Spool to local queue (`artifacts/runtime/hitl_ledger_spool/`); proceed with escalation; reconcile asynchronously |
| Policy snapshot mismatch (YAML edited mid-flight) | Bind snapshot at dispatch; resolution uses same snapshot; fresh YAML applies only to new escalations |
| Approver responds after timeout | Log as `late_response` in ledger; do NOT override fallback (fallback is authoritative) |
| Concurrent approvals from pool | First decisive response wins; others logged as `late_response` |
| Orchestrator crash mid-suspend | On restart, reload suspended runs from ledger; reissue adapter poll; honor original timeout clock |

---

## 7. Versioning

This contract is versioned. Breaking changes require:

1. New ADR superseding ADR-023
2. Incremented version tag in this file
3. Migration plan for in-flight escalations (drain or re-dispatch under new contract)

Non-breaking additions (new span attributes, new escalation classes, new adapters) do not
require a new ADR; they require updating this file and the sibling plan.

**Version:** `1.0.0-draft`

---

## 8. Acceptance

Contract is accepted when:

- [ ] L3 orchestration owner reviews §3 call shapes + §6 failure modes
- [ ] L5 safety owner reviews §2 invariants + §4.1 policy snapshot semantics
- [ ] Compliance reviewer reviews §4.1 integrity block + §5 non-overlap
- [ ] Paired ADR-023 accepted
- [ ] Contract reflected in Notion ADR Registry row (link back to this file)
