# Write-Governance Advisory Note

**Status**: Advisory — documentation-only  
**Lane**: Lane C (`repo_canonical`)  
**Wave**: D7.1 (WC-G04 closeout)  
**Date**: 2026-04-16  
**Authority**: `invalid_for_normative_use=True` — repo-internal current-state record, **not** a requirement source  
**Applies to**: the agentic_core write path as of Wave C / early Wave D

> This note records the **current** write-governance posture in this repository. It does not prescribe new behaviour, does not modify any module, and does not reopen any Wave B or Wave C decision. It exists so the `repo_evidence` collection has a single retrievable anchor for the write-governance question; it pairs with the existing hardening specs (which describe the target-state daemon) without duplicating them.

---

## 1. Purpose and Non-Goals

**Purpose.** Provide one canonical Lane C entry that answers the question *"what is the write-governance posture of this codebase right now?"* in a single short document, so retrieval against `repo_evidence` can ground on an explicit statement rather than inferring from scattered modules.

**Non-goals.**
- No new requirements.
- No runtime or code change.
- No reopening of F25-int adjudication.
- No move of ownership between layers.
- No new anti-pattern and no change to any existing governance gate.
- No external URL — this is a repo-internal lens on the codebase as it stands.

---

## 2. Current Posture (as represented in the repo today)

The repository implements write governance as an **in-process enforcement chain**, assembled from five cooperating modules. Every mutation is expected to pass through this chain; there is no separate host daemon in the current tree.

### 2.1 The in-process chain

| Role | Module (current repo path) | Layer |
|------|----------------------------|-------|
| Single write authority | `agentic_core/L2_execution/enforcement/UniversalWriteGateway.py` | L2 |
| Guardrail admission check | `agentic_core/L2_execution/enforcement/guardrail_gate.py` | L2 |
| Mixin that binds arbitrary writers to the authority | `agentic_core/L2_execution/enforcement/write_governor_mixin.py` | L2 |
| Promotion-path write gate (L4-bound writes) | `agentic_core/L4_state/enforcement/promotion_write_gateway.py` | L4 |
| Ledger / clerk for durable mutation records | `agentic_core/L4_state/enforcement/uwg_clerk.py` | L4 |
| Thin interface surface used by callers | `agentic_core/interfaces/write_gateway.py` (+ `write_gateway_shim.py`) | shared |

**Posture summary.** Writes enter through the L2 `UniversalWriteGateway`, which validates the instruction against a `GuardrailGate` admission check, records a `MutationRecord` on commit, and supports a `replay_mode` path for deterministic simulation. L4 provides `promotion_write_gateway.py` for writes that cross the L2→L4 boundary and `uwg_clerk.py` for the ledger. All of these run inside the same Python process as the rest of `agentic_core`.

### 2.2 Observable invariants the chain already enforces

The following are observable in the current code and do not require any D7.1 change:

- **Single write authority.** Mutations outside the `UniversalWriteGateway` path are rejected by the guardrail chokepoint (`execution_guardrail_chokepoint.py`) and by the L5 global mutation validators.
- **Determinism hooks.** Each mutation carries a `mutation_hash` derived from `(actor_id, run_id, operation, path, data_hash)`; the record is designed to be replayable.
- **Replay mode.** The gateway supports a `replay_mode` flag that prevents real side-effects while preserving the audit envelope.
- **L5 safety checks.** `global_mutation_validator.py` and the hierarchy healers read the mutation records to detect violations.
- **Normative-lane isolation at retrieval time.** The `evidence_shaper` filter keeps Lane C (this document included) out of `ext_authority`-only normative responses by the `invalid_for_normative_use=True` flag set by the ingestion pipeline.

---

## 3. Delta Between Current Posture and the Hardening Target State

For completeness, the hardening specs in the repository already describe a target state where write governance runs as an **independent host-level daemon** (see `docs/specs/hardening/UWG_ISOLATION_SPEC.md`). That target state is **not** the current posture. The relevant deltas, stated only so Lane C retrieval can answer "does the repo claim that today?" without ambiguity:

| Dimension | Current (this note) | Target (hardening spec) |
|-----------|--------------------|-------------------------|
| Deployment | In-process library inside `agentic_core` | Independent daemon on a local socket |
| Lifecycle coupling | Tied to the host Python process | Independent start / stop / version |
| Boundary enforcement | Module-level guardrail chokepoint | Process-level IPC boundary + signed traces |
| Mutation trace signing | Deterministic hash over instruction fields | Signed `ExecutionTrace` verified by daemon |
| Policy storage | Python module + config dicts | Separate `policy_store` on the daemon side |

This table is descriptive only. It does **not** commit to moving from current to target posture in any specific wave. That decision belongs to a future ADR.

---

## 4. Interaction with Wave C and Wave D Decisions

- **Wave C §2d (evidence_shaper.py frozen)** — unaffected. This note does not change the shaper, the `allowed_collections` default, or the `LOW_NORMATIVE_COVERAGE` signal.
- **Wave C §2c (query_router.py frozen)** — unaffected. The domain mappings are not changed; architecture-domain queries continue to route to `repo_evidence`.
- **Wave D5 (LOW_NORMATIVE_COVERAGE consumer)** — the D5.1 consumer and D5.2 integration read this document solely through the `repo_evidence` retrieval path; the advisory adds one more chunk to that path's surface area but does not introduce any new route or signal.
- **Wave D7 (this slice)** — closes WC-G04 as an advisory. The gap is not "do daemonization"; the gap is "surface the current posture so retrieval can cite it". That is what this note does.

---

## 5. What This Note Is Not

- **Not an ADR.** ADRs live under `docs/architecture/adr/` and record approved decisions. This note records an **observed** state.
- **Not a requirement.** Requirements live in `docs/requirements/normative_requirements_spec.md` (Lane C, `invalid_for_normative_use=True`). Lane C content cannot be used to answer normative target-state questions.
- **Not a migration plan.** Any move toward the daemon posture described in the hardening specs requires a separate ADR, a separate wave, and its own HITL packet.
- **Not a replacement** for `UWG_ISOLATION_SPEC.md`, `AUTHORITY_HIERARCHY_INVARIANTS.md`, or any existing architecture document.

---

## 6. Retrieval Expectations

This document is ingested into `repo_evidence` with:

- `source_band = repo_canonical`
- `authority_tier = T4_repo_canonical`
- `invalid_for_normative_use = True`
- `source_type = local`
- `topic_bucket = arch_standards`
- `doc_family = architecture`
- `collapse_group = repo_architecture`
- `source_url` — repo-relative path only

It is expected to surface for queries such as "what is the current write-governance posture?", "how are mutations recorded today?", "is UWG a daemon in the repo?" and to **not** surface for `ext_authority`-only normative queries.

---

*Wave D7.1 advisory note. Frozen at this version. Any subsequent revision requires a new ingestion digest.*
