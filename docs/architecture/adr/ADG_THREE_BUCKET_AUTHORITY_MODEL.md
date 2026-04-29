# ADG Three-Bucket Authority Model

**Status**: Phase 1 (Foundation) — landed 2026-04-29
**Certification**: ADG_NOT_CERTIFIED (W2/W3/W4/W5 outstanding)
**SSOT**: `agentic_core/adg/artifact/edge_authority.py`

## Why this exists

Prior to this work, the ADG generator emitted **unqualified edges** — every
import edge had the same shape regardless of whether the target resolved on
disk, was a literal-string `importlib.import_module` site, was a third-party
package, was a test-file edge, or originated from runtime telemetry. The
2026-04-28 commits added a single-axis `authority` enum (6 values) which
caught the most egregious case (broken targets), but left several classes of
authority confusion unaddressed:

* No distinction between "code can reference X" (static) and "X actually ran"
  (runtime).
* No representation for "configuration declares X is wired" (registry).
* No way for downstream consumers to declare which mode of evidence they
  consume.
* Materialized views silently accepted unresolved edges as inputs.

The 2026-04-29 directive — "ADG must become the certified graph authority for
all repo graph claims, but ADG must not pretend that a single AST scan is the
whole truth" — required widening to a three-bucket model.

## The three buckets

### Bucket A: STATIC GRAPH

> What the code **can** reference based on static source inspection.

Evidence sources: `ast.Import`, `ast.ImportFrom`, relative imports,
`importlib.import_module(literal)` / `__import__(literal)` /
`find_spec(literal)`, type-checking-only imports, test-only imports,
optional `try/except` imports, external package references.

Edge kinds (open list — populated as needed):
`STATIC_IMPORT`, `STATIC_FROM_IMPORT`, `RELATIVE_IMPORT`,
`DYNAMIC_IMPORT_LITERAL`, `DYNAMIC_IMPORT_PARTIAL`,
`DYNAMIC_IMPORT_UNRESOLVED`, `CALL_GRAPH_STATIC`,
`TYPE_CHECKING_REFERENCE`, `TEST_ONLY_REFERENCE`,
`EXTERNAL_PACKAGE_REFERENCE`, `OPTIONAL_IMPORT`,
`UNKNOWN_STATIC_REFERENCE`.

Resolution statuses (closed enum):
`VERIFIED_MODULE`, `VERIFIED_SYMBOL`, `UNRESOLVED_MODULE`,
`UNRESOLVED_SYMBOL`, `UNRESOLVED_DYNAMIC`, `PARTIAL`, `NOT_CHECKED`,
`NOT_APPLICABLE`, `UNKNOWN`.

**Authority law**:
* verified production internal reference → `AUTHORITATIVE`
* missing module/symbol → `RISK_SIGNAL_ONLY`
* dynamic unresolved → `UNKNOWN_NOT_PROOF`
* type-checking-only → `EXCLUDED_TYPE_ONLY` (W4)
* test-only → `EXCLUDED_TEST_ONLY`
* external package → `EXTERNAL_ONLY`
* optional dependency → `NON_AUTHORITATIVE_HINT` (W4)

### Bucket B: RUNTIME GRAPH

> What **actually happened** during execution.

Evidence sources: OpenTelemetry traces, span parent/child relationships,
tool-call traces, model-call receipts, MCP call logs, runtime graph
snapshots, sealed L2 artifacts, ExitReviewPacket traces.

Edge kinds: `RUNTIME_OBSERVED`, `CALL_GRAPH_RUNTIME`, `TOOL_CALL_RUNTIME`,
`MODEL_CALL_RUNTIME`, `CONNECTOR_CALL_RUNTIME`, `MCP_CALL_RUNTIME`,
`ROUTE_STEP_RUNTIME`, `WORKFLOW_EDGE_RUNTIME`, `IMPORT_LOAD_RUNTIME`,
`EXIT_DISPOSITION_RUNTIME`, `UWG_COMMIT_RUNTIME`, `L6_EVAL_RUNTIME`.

Resolution statuses: `VERIFIED_RUNTIME`, `VERIFIED_TRACE`,
`VERIFIED_RECEIPT`, `PARTIAL_TRACE`, `MISSING_TRACE`, `NOT_APPLICABLE`,
`UNKNOWN`.

**Authority law**:
* runtime edge with `trace_id`/`run_id`/`span_id` evidence →
  `AUTHORITATIVE_RUNTIME`
* runtime edge with sealed artifact receipt → `AUTHORITATIVE_RUNTIME`
* runtime edge with incomplete trace → `PARTIAL` or `RISK_SIGNAL_ONLY`
* runtime claim without trace or receipt → `UNKNOWN_NOT_PROOF`

**MUST NOT**: infer runtime behavior from static imports alone; merge
runtime-observed edges into static edges without labels.

### Bucket C: REGISTRY GRAPH

> What configuration / registry / declared system wiring says is **allowed,
> available, or connected**.

Evidence sources: agent registry (`apps_*/config/agent_specs.json`), tool
registry, prompt registry, MCP connector registry
(`.windsurf/mcp_config.json`), route registry, capability registry,
sandbox registry, YAML/JSON plugin maps, L4 policy/blueprint state.

Edge kinds: `REGISTRY_DECLARED`, `AGENT_TOOL_ALLOWED`,
`AGENT_MODEL_ALLOWED`, `AGENT_CONNECTOR_ALLOWED`, `ROUTE_AGENT_ALLOWED`,
`ROUTE_TOOL_ALLOWED`, `PROMPT_SLOT_DECLARED`, `MCP_CONNECTOR_DECLARED`,
`CAPABILITY_SCOPE_DECLARED`, `SANDBOX_SCOPE_DECLARED`, `CONFIG_REFERENCE`,
`PLUGIN_REFERENCE`, `MODEL_REFERENCE`, `TOOL_REFERENCE`,
`CONNECTOR_REFERENCE`, `PROMPT_REFERENCE`, `UNKNOWN_REGISTRY_REFERENCE`.

Resolution statuses: `VERIFIED_REGISTRY`, `VERIFIED_CONFIG`,
`UNRESOLVED_REGISTRY`, `STALE_REGISTRY`, `MISMATCHED_REGISTRY`,
`SUBSTITUTED_REGISTRY`, `NOT_APPLICABLE`, `UNKNOWN`.

**Authority law**:
* declaration matches active registry digest → `AUTHORITATIVE_REGISTRY`
* declaration with missing target → `RISK_SIGNAL_ONLY`
* stale or mismatched declaration → `RISK_SIGNAL_ONLY`
* declaration outside active policy → `NON_AUTHORITATIVE_HINT`
* unknown config reference → `UNKNOWN_NOT_PROOF`

**MUST NOT**: pretend registry-declared edges are static imports; pretend
registry permission means runtime execution happened.

## Authority law (the only place downstream consumers may check)

```python
from agentic_core.adg.artifact.edge_authority import (
    is_proof, is_risk, is_inventory_only, PROOF_STATUSES, RISK_STATUSES,
    INVENTORY_ONLY_STATUSES,
)

# Three subsets that partition ALL_AUTHORITY_STATUSES:
PROOF_STATUSES         # = {AUTHORITATIVE, AUTHORITATIVE_RUNTIME, AUTHORITATIVE_REGISTRY}
RISK_STATUSES          # = {RISK_SIGNAL_ONLY, UNKNOWN_NOT_PROOF, PARTIAL}
INVENTORY_ONLY_STATUSES # = {EXCLUDED_TEST_ONLY, EXCLUDED_TYPE_ONLY, EXTERNAL_ONLY, NON_AUTHORITATIVE_HINT}
```

Only `PROOF_STATUSES` may be used as proof. Everything else is **not proof**.

## The three canonical views

### proof_view

```sql
CREATE VIEW proof_view AS
SELECT * FROM edges
WHERE authority_status IN ('AUTHORITATIVE', 'AUTHORITATIVE_RUNTIME', 'AUTHORITATIVE_REGISTRY');
```

Used by: governance proof, layer-boundary proof, forbidden-dependency proof,
certified hotspot/chokepoint claims, refactor-impact claims, coverage
adequacy claims.

Excludes: unresolved, unknown, partial, test-only, type-only, external,
non-authoritative hints, risk signals.

### risk_view

```sql
CREATE VIEW risk_view AS
SELECT * FROM edges
WHERE authority_status IN ('RISK_SIGNAL_ONLY', 'UNKNOWN_NOT_PROOF', 'PARTIAL');
```

Used by: cleanup backlog, risk triage, graph-quality improvement,
missing-instrumentation detection, dependency-uncertainty analysis.

Output MUST be labeled as risk, not proof.

### inventory_view

```sql
CREATE VIEW inventory_view AS
SELECT * FROM edges;
```

Used by: debugging, audits, migrations, graph exploration, before/after
comparison.

Output MUST be labeled as inventory, not proof.

## Schema fields (per-edge)

Beyond the existing edge schema, every edge MUST carry:

| Field | Type | Purpose |
|---|---|---|
| `bucket` | `static \| runtime \| registry` | Which authority axis governs this edge |
| `resolution_status` | enum (per bucket) | What the resolver determined |
| `authority_status` | enum (10 values) | What downstream consumers may claim |
| `evidence_refs` | JSON array | Pointers to source AST node, run/trace/span ids, registry digest, etc. |

Plus the existing `authority` column (legacy single-axis enum) is kept as a
back-compat alias and derived from the triplet at backfill time.

## Mapping from legacy `authority` (2026-04-28) → triplet (2026-04-29)

| Legacy `authority` | New `bucket` | New `resolution_status` | New `authority_status` |
|---|---|---|---|
| `verified` | `static` | `VERIFIED_MODULE` | `AUTHORITATIVE` |
| `unresolved` | `static` | `UNRESOLVED_MODULE` | `RISK_SIGNAL_ONLY` |
| `dynamic` | `static` | `UNRESOLVED_DYNAMIC` | `UNKNOWN_NOT_PROOF` |
| `external` | `static` | `NOT_APPLICABLE` | `EXTERNAL_ONLY` |
| `test_only` | `static` | `VERIFIED_MODULE` | `EXCLUDED_TEST_ONLY` |
| `runtime_observed` | `runtime` | `VERIFIED_RUNTIME` | `AUTHORITATIVE_RUNTIME` |

Tests assert this mapping is bijective and that the SQL backfill agrees with
the Python classifier.

## What CAN be claimed from each bucket

| Claim type | Required bucket | Required authority_status |
|---|---|---|
| "Module X imports module Y in production" | static | AUTHORITATIVE |
| "X is a hotspot" | static | AUTHORITATIVE only |
| "X has no callers" (zero-fan-in) | static | AUTHORITATIVE only — unresolved/dynamic/external excluded |
| "Tool T was actually called" | runtime | AUTHORITATIVE_RUNTIME |
| "Agent A ran in this run" | runtime | AUTHORITATIVE_RUNTIME |
| "Healing chain executed" | runtime | AUTHORITATIVE_RUNTIME |
| "Agent A is configured to use tool T" | registry | AUTHORITATIVE_REGISTRY |
| "MCP connector M is declared" | registry | AUTHORITATIVE_REGISTRY |
| "X is broken" (cleanup backlog) | static | RISK_SIGNAL_ONLY |

## What CANNOT be claimed

* Runtime behavior cannot be inferred from static imports.
* Registry permission does not imply runtime execution.
* Static dependency does not imply registry permission.
* Unresolved/unknown/partial edges cannot inflate proof claims.
* Test-only / type-only / external edges cannot drive production hotspot
  reports.

## SSOTDecisionRecord (cross-bucket reconciliation primitive — W2)

When a claim requires reconciling evidence across all three buckets, the
answer is a **`SSOTDecisionRecord`** (`agentic_core/adg/artifact/ssot_decision_record.py`).

### Question answered

> "For this exact run, under this exact policy and registry snapshot, did
> the thing exist (static), was it allowed (registry), did it happen
> (runtime), and was the result sealed?"

### 8-cell decision matrix

The matrix is the cross-product of three axes, each derived from one
ADG bucket:

| FOUND | ALLOWED | USED | Outcome | Severity |
|:---:|:---:|:---:|---|---|
| ✓ | ✓ | ✓ | `VALID_USE` | gold |
| ✓ | ✓ | ✗ | `ALLOWED_NOT_USED` | benign |
| ✓ | ✗ | ✓ | `POLICY_BYPASS` | **INCIDENT** |
| ✓ | ✗ | ✗ | `BLOCKED_UNUSED` | benign |
| ✗ | ✓ | ✓ | `HIDDEN_PATH` | **INTEGRITY** |
| ✗ | ✓ | ✗ | `REGISTRY_DRIFT` | hygiene |
| ✗ | ✗ | ✓ | `SEVERE_BYPASS` | **CRITICAL** |
| ✗ | ✗ | ✗ | `CLEAN_ABSENCE` | benign |

Where:
- **FOUND** = `static_refs` is non-empty (proof the thing exists in the codebase)
- **NOT FOUND** = `static_refs` is empty
- **ALLOWED** = `registry_refs` is non-empty AND every ref is `AUTHORITATIVE_REGISTRY`
- **BLOCKED** = `registry_refs` is empty OR any ref is stale/mismatched/unresolved
- **USED** = `runtime_refs` is non-empty AND at least one ref is `AUTHORITATIVE_RUNTIME`
- **NOT USED** = `runtime_refs` is empty OR no ref is authoritative

### Required fields (per spec Section 2)

```python
@dataclass(frozen=True)
class SSOTDecisionRecord:
    # Required scalar identifiers
    request_id:          str
    run_id:              str
    trace_id:            str
    route_contract_id:   str
    policy_hash:         str
    blueprint_hash:      str
    # Required bucket evidence
    registry_digest_set: tuple[str, ...]
    static_refs:         tuple[str, ...]
    runtime_refs:        tuple[str, ...]
    registry_refs:       tuple[str, ...]
    # Required determinism / signing
    replay_key:          str   # SHA-256 over (request_id, run_id, route, policy)
    manifest_hash:       str   # SHA-256 over sorted bucket evidence + hashes
    hmac_sig:            str   # HMAC-SHA256(manifest_hash, secret)
    outcome:             str   # one of the 8 matrix cells
    # Optional context refs
    evidence_contract_ref:  str | None = None
    prompt_artifact_ref:    str | None = None
    sealed_l2_artifact_ref: str | None = None
    exit_review_packet_ref: str | None = None
    x3_disposition:         str | None = None
    uwg_commit_receipt_ref: str | None = None
```

### Construction

The canonical path is `SSOTDecisionRecord.build(...)` which:

1. Computes `outcome` via the reconciler from `static_refs` / `runtime_refs` / `registry_refs`
2. Computes deterministic `manifest_hash` over sorted bucket evidence
3. Computes `replay_key` from `(request_id, run_id, route_contract_id, policy_hash)`
4. Computes `hmac_sig` via HMAC-SHA256 with secret from `ADG_SSOT_HMAC_KEY`
5. Returns a frozen dataclass instance

```python
rec = SSOTDecisionRecord.build(
    request_id="req-001",
    run_id="run-001",
    trace_id="trace-001",
    route_contract_id="route-001",
    policy_hash="policy-abc",
    blueprint_hash="blueprint-def",
    registry_digest_set=["digest-1"],
    static_refs=["edge:42"],
    runtime_refs=["edge:99"],
    registry_refs=["edge:55"],
)
# rec.outcome = "VALID_USE"
# rec.manifest_hash, rec.replay_key, rec.hmac_sig populated
```

### Persistence

Schema lives in `ssot_decision_records` table (created in same backfill
transaction as the three views). Indexes on `run_id`, `trace_id`,
`request_id`, `outcome`, `replay_key`, `manifest_hash` for forensic
queries.

### Tamper evidence

`manifest_hash` is SHA-256 over the JSON-canonicalized constituent
evidence (sorted refs, normalized order). Any later mutation of the
record's bucket evidence produces a different hash. `hmac_sig` provides
the secondary signature so a tampered record cannot pass authenticity
verification.

### Consumer rule

Any claim that mixes evidence from two or more buckets (e.g. "tool T was
configured AND was actually called") MUST emit an SSOTDecisionRecord
rather than infer from one bucket alone. Single-bucket claims continue
to use `proof_view` directly.

## ADG certification

A snapshot is **ADG_CERTIFIED** when ALL of the following hold:

1. No edge missing `bucket`
2. No edge missing `resolution_status`
3. No edge missing `authority_status`
4. No edge missing `evidence_refs` (or with empty array when not applicable)
5. No edge missing `snapshot_id`
6. No `AUTHORITATIVE*` edge missing proof evidence
7. Static-graph tests pass
8. Runtime-separation tests pass (where fixtures exist)
9. Registry tests pass (where registries exist)
10. Every downstream consumer declares mode (proof/risk/inventory)
11. No proof report consumes risk or inventory edges as proof
12. Deterministic regeneration from same inputs produces same digest and
    same authority counts

**Current status**: ADG_NOT_CERTIFIED.

Reason: criteria 4 (evidence_refs not yet populated for static edges in W1
— still NULL after triplet backfill), 8 (runtime resolver — W2 deferred),
9 (registry resolver — W3 deferred), 10 (consumer audit — W4 deferred),
11 (CI gate that asserts mode — W4 deferred), 12 (deterministic-digest
test — W5 deferred).

## Phase plan

| Wave | Phase | Status |
|---|---|---|
| W1 | Foundation: schema + triplet backfill + 3 views + tests + deliverables | **Landed 2026-04-29** |
| W2 | Runtime hardening: lift `tools/generate/generate_runtime_adg.py` outputs into bucket=runtime with run_id/trace_id evidence_refs | Deferred |
| W3 | Registry resolvers: agent_specs / MCP config / tool registry / prompt slots → bucket=registry with registry_digest evidence_refs | Deferred |
| W4 | Consumer audit: every ADG consumer declares proof/risk/inventory mode; CI gate fails on missing mode | Deferred |
| W5 | Certification gate: ADG_CERTIFIED check; deterministic-digest test; graduation of bucket/resolution_status/authority_status from NULLABLE to NOT NULL | Deferred |

## Tests added

* `tests/unit/agentic_core/adg/artifact/test_three_bucket_authority.py` — 33
  unit tests across `TestClosedEnums`, `TestAuthorityLaw`,
  `TestLegacyMapping`, `TestTripletClassifier`, `TestSQLTripletBackfill`,
  `TestThreeViews`, `TestEndToEnd`.
* `tests/unit/agentic_core/adg/artifact/test_edge_authority.py` — 43
  pre-existing tests preserved.

Total: **76 unit tests passing**.

## Commands & evidence

```
python -m pytest tests/unit/agentic_core/adg/artifact/test_three_bucket_authority.py \
                 tests/unit/agentic_core/adg/artifact/test_edge_authority.py
# 76 passed, 25 warnings in 5.11s

python tools/adg/audit_three_bucket_counts.py
# total_edges=725903 across snapshot adg_indexed_04292026_0533.sqlite
# proof_count=199989 risk_count=14580 inventory_only_count=511334
```

## Distribution on the latest snapshot (projected — not yet shipped)

| Authority status | Count | Share |
|---|---:|---:|
| AUTHORITATIVE | 199,989 | 27.55% |
| EXTERNAL_ONLY | 349,174 | 48.10% |
| EXCLUDED_TEST_ONLY | 162,160 | 22.34% |
| RISK_SIGNAL_ONLY | 14,483 | 2.00% |
| UNKNOWN_NOT_PROOF | 97 | 0.01% |
| AUTHORITATIVE_RUNTIME | 0 | 0% (W2) |
| AUTHORITATIVE_REGISTRY | 0 | 0% (W3) |
| PARTIAL | 0 | 0% (W4 — symbol-level resolver) |
| EXCLUDED_TYPE_ONLY | 0 | 0% (W4 — TYPE_CHECKING detection) |
| NON_AUTHORITATIVE_HINT | 0 | 0% (W4 — optional-import detection) |

Bucket distribution: 100% static, 0% runtime, 0% registry. The runtime and
registry buckets are real — but populating them is W2/W3 work.

## References

* Plan: `.windsurf/plans/adg-three-bucket-authority-model-7e2a91.md`
* SSOT: `agentic_core/adg/artifact/edge_authority.py`
* Schema: `agentic_core/adg/artifact/ArtifactPaths.py`, `multi_writer.py`
* Final-stage backfill: `tools/generate/generate_full_adg.py`
* Tests: `tests/unit/agentic_core/adg/artifact/test_three_bucket_authority.py`
* Prior ADR (legacy single-axis): `docs/architecture/adr/ADG_EDGE_AUTHORITY_AXIS.md`
* Constitutional §22 (ADG graph-layer primary), §23 (canonical invariants)
