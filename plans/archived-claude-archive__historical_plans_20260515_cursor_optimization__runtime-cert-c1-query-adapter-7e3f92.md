---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-c1-query-adapter-7e3f92.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-c1-query-adapter-7e3f92.md'
source_sha256: e22d5348397640fc3c588ab6ba7a91c63a3b4fbeb374c5b7f6d6da726990a7e0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase C.1 Plan — Read-Only Runtime ADG Query Adapter

**Status**: DESIGN PLAN — documentation only. No Python implementation.
No emitter change. No scanner change. No CI gate. No app certified.
**Plan version**: v1 (2026-04-30, initial)
**Parent plan**: `docs/plans/runtime_cert_phase_c_trace_collector_plan.md` (v2)
**Predecessor phases**: A, B.1, B.2, B.3, B.4, B.5 (all complete)
**Approved Author-Gate decisions**: AG-C-1 through AG-C-9 (see parent plan §0)

---

## 1. Purpose and non-goals

### 1.1 Purpose

Phase C.1 specifies a **read-only query adapter** — a thin Python module
(`tools/runtime_cert/runtime_adg_query_adapter.py`) that:

1. Accepts an existing `RuntimeADGSnapshot` or a path to a persisted
   runtime-ADG SQLite file as its only source of truth.
2. Yields `RuntimeADGNode` instances filtered by `trace_id`, `app_name`
   attribute, and/or a time-window pair (`started_after_ms`, `ended_before_ms`).
3. Converts each `RuntimeADGNode` into the **18-field Phase C trace row**
   (`dict[str, Any]`) defined in the parent plan §3.1, applying documented
   defaults for fields that cannot be derived from the node alone.
4. Exposes a snapshot-loading helper that wraps `create_runtime_adg_snapshot`
   for callers that need to build a `RuntimeADGSnapshot` from raw span dicts
   (e.g., test fixtures).

The adapter is the **foundation layer** for all of C.2–C.7. It emits no
spans, mutates no state, and performs no certification evaluation.

### 1.2 Hard non-goals

| Non-goal | Reason |
|---|---|
| No Python implementation in this plan | This is a planning document only. Code lands in a separate, scoped Author-Gate session. |
| No certification evaluation | `runtime_certification_status` is always `NOT_CERTIFIED` in Phase C. Writing any other value is a Phase C bug (AG-C-8 invariant). |
| No parallel storage | `system_learning/runtime_adg/` remains the SSOT. C.1 reads that store; it does not create a new one (AG-C-2). |
| No scanner classification changes | Phase F only. The adapter never calls or modifies `tools/analysis/apps_spine_coverage.py` (AG-C-4). |
| No emitter changes | The adapter is a pure consumer. It does not add, rename, or patch any OTel emitter (AG-C-5). |
| No app behavior changes | The adapter reads persisted or in-memory snapshot data; it cannot affect a running app. |
| No CI gate | Phase E only. C.1 ships no new gate in `ops_scripts/ci/`. |
| No live smoke | C.6 is the first live-trace phase. C.1 tests use synthetic fixtures only. |
| No schema migration | The 18-field row schema (AG-C-3) is frozen. C.1 does not extend or alter it. |

---

## 2. Inputs and existing surfaces

### 2.1 `RuntimeADGQuery` (`tools/adg/runtime_query.py`)

The existing production query facade. Key facts for C.1:

| Aspect | Detail |
|---|---|
| Thread safety | Per-call read-only SQLite connections (`uri=True&mode=ro&immutable=1`) — safe to call from any thread |
| Constructor | `RuntimeADGQuery(sqlite_path: Path | str | None = None)` — resolves to the newest `artifacts/adg/adg_indexed_*.sqlite` if `sqlite_path` is `None` |
| Provenance | `.snapshot_id` (stem of the SQLite path, e.g. `adg_indexed_04242026_0721`), `.snapshot_path` (str), `.provenance() -> dict` |
| Error contract | Never raises on malformed input; returns an empty envelope with an `"error"` key |
| `__adg_consumer_mode__` | `"inventory"` — C.1 must declare `__adg_consumer_mode__ = "runtime_cert_read"` per ADR-079 |

**C.1 does NOT use `RuntimeADGQuery` directly** — the adapter targets the
`RuntimeADGSnapshot` / `RuntimeADGNode` shape (in-memory, test-friendly),
not the SQLite-indexed static ADG. `RuntimeADGQuery` wraps the *static*
code-structure ADG; the runtime-trace snapshots live under
`system_learning/runtime_adg/`. The two stores are distinct per parent plan §2
and constitutional §23-e. The adapter will reference `RuntimeADGQuery`'s
`_open_readonly` pattern as a model for any future SQLite reads against
*runtime* snapshot files, but the primary source is `RuntimeADGSnapshot`.

### 2.2 `RuntimeADGNode` and `RuntimeADGSnapshot`
(`system_learning/runtime_adg/snapshot.py`)

| Symbol | Fields relevant to C.1 |
|---|---|
| `RuntimeADGNode` | `node_id` (span ID), `name` (span name), `kind`, `layer`, `component`, `started_at_utc` (Unix ms), `duration_ms`, `status` (`ok`/`error`), `attributes_json` (compact sorted JSON string) |
| `RuntimeADGSnapshot` | `snapshot_id` (SHA-256 hex), `trace_id` (OTel trace ID), `mission`, `started_at_utc`, `ended_at_utc`, `nodes: tuple[RuntimeADGNode, ...]`, `edges: tuple[RuntimeADGEdge, ...]`, `snapshot_hash` |
| `create_runtime_adg_snapshot(...)` | Factory that sorts nodes/edges and computes the SHA-256 `snapshot_id`. C.1 exposes a test-helper wrapper around this. |
| `attributes_to_json(attrs: dict) -> str` | Serialises a span-attrs dict to compact sorted JSON. C.1 uses this in its snapshot-builder helper. |

`attributes_json` is a **string** — the adapter must call `json.loads()`
before reading any attribute. This is a known risk (parent plan §11 R2)
and is handled at the adapter boundary.

### 2.3 Phase C 18-field row schema (parent plan §3.1)

The frozen schema (AG-C-3) that C.1 partially populates. See §4 of this
plan for the field-by-field mapping.

### 2.4 Phase B.2 `ContractSpanBinding`
(`system_learning/runtime_adg/app_route_contracts.py`)

The per-app contract objects whose `normalized_cert_alias` and
`accepted_span_name_patterns` / `accepted_emitter_files` fields drive
C.2's mapping precedence (parent plan §4). C.1 does **not** perform
contract resolution — that is C.2's responsibility. C.1 simply carries
the raw `span_name`, `attributes`, and `evidence_source` forward so C.2
has everything it needs.

### 2.5 Phase B.5 `NegativeControlResult`
(`tools/runtime_cert/negative_controls.py`)

Defensive row accessors in `negative_controls.py` (`_row_str`,
`_row_list`, etc.) expect top-level OR nested `attributes` fields in each
row. C.1 must preserve both the flat top-level fields and the nested
`attributes` dict to remain compatible.

---

## 3. Proposed target file and API

### 3.1 Target file

```
tools/runtime_cert/runtime_adg_query_adapter.py
```

Rationale: sibling to `tools/runtime_cert/negative_controls.py` (Phase B.5).
The `tools/runtime_cert/` package is the correct SSOT for runtime cert
helpers (per `ssot-folder-enforcement.md` — utility helpers land in
`tools/<domain>/`).

### 3.2 Module-level declarations

```python
"""Read-only runtime ADG query adapter — Phase C.1.

Converts RuntimeADGNode instances from a RuntimeADGSnapshot into
the Phase C 18-field trace row shape defined in
docs/plans/runtime_cert_phase_c_trace_collector_plan.md §3.1.

What this module does NOT do
----------------------------
- Does NOT certify apps (runtime_certification_status is always NOT_CERTIFIED).
- Does NOT write to any store.
- Does NOT modify any emitter.
- Does NOT run scanner classification.
- Does NOT perform contract resolution (that is Phase C.2).
"""

__adg_consumer_mode__ = "runtime_cert_read"
```

### 3.3 Public dataclass — `PhaseC1Row`

A typed wrapper around the 18-field dict defined in parent plan §3.1.
The dataclass exists to make field names discoverable and to allow
`asdict()` serialisation. All fields have defaults consistent with the
"fail-closed" defaults described in §5 of this plan.

```python
@dataclass
class PhaseC1Row:
    # Identity
    app_name: str                       # required — "apps_*"
    route_shape: str                    # required — one of 4 RouteShape values
    trace_id: str                       # required — OTel trace id
    span_id: str                        # required — OTel span id (= node_id)
    parent_span_id: str | None          # None for root spans

    # Span metadata
    span_name: str                      # raw RuntimeADGNode.name
    timestamp: int                      # RuntimeADGNode.started_at_utc (Unix ms)

    # Contract resolution (populated by C.2 — C.1 leaves as None)
    contract_name: str | None = None
    normalized_cert_alias: str | None = None

    # App-level provenance (C.1 populates if derivable from snapshot attrs)
    manifest_hash: str = ""             # 64-char hex; empty = not yet resolved
    static_runtime_mode: str = ""       # scanner field; populated by C.3-C.5

    # Certification status — INVARIANT: always NOT_CERTIFIED in Phase C
    runtime_certification_status: str = "NOT_CERTIFIED"

    # Optional identifiers (populated post-hardening)
    artifact_id: str | None = None      # also called contract_id in some attrs
    contract_id: str | None = None
    source_path: str | None = None      # code.filepath OTel attribute

    # Nested attributes (parsed from attributes_json)
    attributes: dict = field(default_factory=dict)

    # Provenance
    evidence_source: str = ""           # "runtime_adg.snapshot.<snapshot_id>"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict compatible with B.5 row accessors."""
        ...
```

> **Invariant**: the `runtime_certification_status` field default is
> `"NOT_CERTIFIED"` and the adapter must raise `ValueError` if any caller
> attempts to construct a `PhaseC1Row` with a different value (test
> `test_phase_c1_row_rejects_non_not_certified`).

### 3.4 Public functions

| Function signature | Purpose |
|---|---|
| `node_to_row(node: RuntimeADGNode, *, snapshot_id: str, trace_id: str, app_name: str = "", route_shape: str = "") -> PhaseC1Row` | Core conversion. Parses `attributes_json`, extracts known flat fields, applies defaults. Returns a `PhaseC1Row` with `contract_name=None` and `normalized_cert_alias=None` — those are C.2's job. |
| `iter_rows_from_snapshot(snapshot: RuntimeADGSnapshot, *, app_name: str = "", route_shape: str = "", started_after_ms: int = 0, ended_before_ms: int = 0) -> Iterator[PhaseC1Row]` | Iterates over `snapshot.nodes`, applies time-window filter if provided, calls `node_to_row` for each. Yields `PhaseC1Row` instances. |
| `iter_rows_for_trace(snapshot: RuntimeADGSnapshot, trace_id: str, *, app_name: str = "", route_shape: str = "") -> Iterator[PhaseC1Row]` | Convenience wrapper: filters nodes whose `attributes["trace_id"]` or the snapshot-level `trace_id` matches. Delegates to `iter_rows_from_snapshot` with identity filter. |
| `build_test_snapshot(trace_id: str, nodes: list[dict], *, mission: str = "test", started_at_utc: int = 0, ended_at_utc: int = 1) -> RuntimeADGSnapshot` | Test-only factory. Converts raw node dicts to `RuntimeADGNode` instances via `attributes_to_json`, then calls `create_runtime_adg_snapshot`. **Not intended for production paths.** |
| `extract_attributes(node: RuntimeADGNode) -> dict[str, Any]` | Parses `node.attributes_json` via `json.loads()`. Returns `{}` on `json.JSONDecodeError`. Never raises. Normalises attribute values to `str | int | float | bool | None | list | dict`. |

### 3.5 Constants

```python
NOT_CERTIFIED: str = "NOT_CERTIFIED"          # the only valid Phase C cert status
EVIDENCE_SOURCE_PREFIX: str = "runtime_adg.snapshot."

VALID_ROUTE_SHAPES: frozenset[str] = frozenset({
    "R3_grounded_read",
    "R3R4_grounded_write",
    "build_time_compiler",
    "formal_exception",
})

PHASE_C1_SCHEMA_VERSION: str = "1.0"  # bump if 18-field schema changes (AG-C-3)
```

---

## 4. 18-field row mapping

Each field in `PhaseC1Row` is derived as follows. "Fail-closed default"
is the value applied when the source is absent or malformed.

| # | Field | Primary source | Fail-closed default | Notes |
|:---:|---|---|---|---|
| 1 | `app_name` | Caller-supplied `app_name` kwarg OR `attributes["app_name"]` | `""` (empty string) | C.1 never infers `app_name` from file paths; that would be fragile. Callers (C.3/C.4/C.5) must supply it. |
| 2 | `route_shape` | Caller-supplied `route_shape` kwarg OR `attributes["route_shape"]` | `""` | Same as `app_name` — caller supplies from the app's `spine_manifest.yaml`. |
| 3 | `trace_id` | `snapshot.trace_id` (snapshot-level) | `""` | If per-node `attributes["trace_id"]` is present and differs from `snapshot.trace_id`, log a warning; use the snapshot-level value (it is the primary key). |
| 4 | `span_id` | `node.node_id` | `""` | Direct field access — no derivation needed. |
| 5 | `parent_span_id` | `attributes.get("parent_span_id")` OR `attributes.get("parent_id")` | `None` | Both attribute keys are probed to absorb minor naming drift. |
| 6 | `span_name` | `node.name` | `""` | Raw emitter name — preserved verbatim for C.2 pattern matching. |
| 7 | `timestamp` | `node.started_at_utc` | `0` | Unix milliseconds. |
| 8 | `contract_name` | **Not set by C.1** — left as `None` | `None` | C.2 trace-row normaliser populates this via the §4 mapping precedence (parent plan). |
| 9 | `normalized_cert_alias` | **Not set by C.1** — left as `None` | `None` | C.2 populates via `ContractSpanBinding.normalized_cert_alias`. |
| 10 | `manifest_hash` | `attributes.get("manifest_hash")` | `""` (empty) | If absent at C.1 time, `manifest_hash` remains `""`. C.3/C.4/C.5 may back-fill from `compute_manifest_hash_for_app(app_name)` at the extractor level. C.1 does not call that function. |
| 11 | `static_runtime_mode` | **Not set by C.1** — left as `""` | `""` | C.3/C.4/C.5 extractors consult the scanner output (read-only) and back-fill this field. C.1 does not read scanner output. |
| 12 | `runtime_certification_status` | **Hardcoded** `"NOT_CERTIFIED"` | `"NOT_CERTIFIED"` | AG-C-8 invariant. Any attempt to set another value is rejected by `PhaseC1Row.__post_init__`. |
| 13 | `artifact_id` | `attributes.get("artifact_id")` OR `attributes.get("contract_id")` | `None` | Both keys probed in order. First non-empty string wins. |
| 14 | `contract_id` | `attributes.get("contract_id")` | `None` | Separate from `artifact_id` in case both are present and differ. If equal to `artifact_id`, the field is still populated independently. |
| 15 | `source_path` | `attributes.get("code.filepath")` OR `attributes.get("source_path")` | `None` | Required by CC-SHARED-03 discrimination in B.5. |
| 16 | `attributes` | `json.loads(node.attributes_json)` | `{}` | `JSONDecodeError` → `{}`, warning logged. The full parsed dict is preserved for downstream helpers. |
| 17 | `evidence_source` | `f"runtime_adg.snapshot.{snapshot_id}"` | Constructed from `snapshot_id` — never empty when snapshot_id is available | Provides audit trail per parent plan §3.1. |
| 18 | *(envelope — not a row field)* | `PhaseC1Row.to_dict()` produces a flat dict; envelope wrapping is C.3/C.4/C.5's job | — | The row schema has 17 data fields + 1 provenance field (`evidence_source`) = 18 fields total. The envelope (`snapshot_id`, `gap_report`, etc.) is C.3-level. |

> **Note on field count**: the parent plan §3.1 lists 15 named fields
> (including `artifact_id / contract_id` as one joint entry and
> `source_path / file_path` as one joint entry). This plan treats each
> alias pair as two distinct `PhaseC1Row` fields (`artifact_id` and
> `contract_id`; `source_path` only — `file_path` is an alias resolved at
> read time). The total comes to 17 data fields + `evidence_source` = 18.
> The schema version constant `PHASE_C1_SCHEMA_VERSION = "1.0"` freezes
> this count.

---

## 5. Fail-closed handling

### 5.1 `attributes_json` parse failure

If `json.loads(node.attributes_json)` raises `JSONDecodeError`:
- `attributes` field is set to `{}`.
- A `WARNING`-level log message is emitted: `"C.1: attributes_json parse failure for span_id=%s: %s"`.
- The row is **still yielded** with `attributes={}` and all attribute-derived
  fields (`contract_name`, `parent_span_id`, `artifact_id`, `source_path`,
  etc.) set to their fail-closed defaults.
- The caller (C.3/C.4/C.5) can inspect `row["attributes"] == {}` as a signal
  that this span may need attribute hardening.

Rationale: silently dropping a span from the row set would create a
`TRACE_GAP` — arguably worse than yielding a partially-populated row.
The fail-closed status vocabulary (`TRACE_GAP`, `ATTRIBUTE_HARDENING_REQUIRED`)
is C.3's concern; C.1's job is to preserve as much information as possible.

### 5.2 Missing or non-string `app_name`

If the caller supplies `app_name=""` AND `attributes.get("app_name")` is
absent or not a string starting with `"apps_"`:
- `row.app_name` is set to `""`.
- A `DEBUG`-level log is emitted.
- The row is yielded. C.3/C.4/C.5 will detect `app_name=""` and treat the
  row as unresolvable (no contract match possible → `UNKNOWN_NEEDS_RUNTIME_RUN`).

### 5.3 Unknown or malformed `contract_name` in attributes

C.1 does **not** validate `contract_name` values extracted from
`attributes`. It simply reads `attributes.get("contract_name")` as a
string and stores it in `attributes` for C.2's inspection. C.2 owns
contract validation.

### 5.4 `CommitRequest` span preservation

C.1 does **not** filter out `CommitRequest` spans. It yields every node
in the snapshot without exception. The `FORBIDDEN_SPAN_VIOLATION` logic
is C.3/C.4's responsibility. Filtering at C.1 would make C.3 unable to
detect the violation.

### 5.5 Certification status invariant

`PhaseC1Row.__post_init__` (Python dataclass validation hook) raises
`ValueError` if `runtime_certification_status != "NOT_CERTIFIED"`.
This is the only place in Phase C where a programmatic invariant is
enforced — every other fail-closed status is a reporting label, not a
raised exception.

### 5.6 Empty snapshot

If `snapshot.nodes` is an empty tuple, `iter_rows_from_snapshot` yields
nothing. No exception is raised. Callers that need to distinguish
"snapshot existed but was empty" from "snapshot not found" should check
`snapshot.node_count() == 0` before calling.

### 5.7 Time-window filter

If `started_after_ms == 0` AND `ended_before_ms == 0` (the defaults),
no time filtering is applied — all nodes are yielded. If either bound
is non-zero, the filter condition is:

```
started_after_ms <= node.started_at_utc < ended_before_ms
```

A single non-zero bound is treated as a half-open window (e.g.,
`started_after_ms=T, ended_before_ms=0` means "all nodes that started
after T"). Malformed windows (e.g., `started_after_ms > ended_before_ms`)
log a `WARNING` and apply no filter (fail-open for time bounds only —
time filtering is a convenience feature, not a safety gate).

---

## 6. Test plan

All tests must pass with no live database, no live OTel exporter, and no
`agentic_core` process side-effects.

### 6.1 Target test file

```
tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py
```

### 6.2 Test fixture strategy

All tests use **synthetic `RuntimeADGNode` and `RuntimeADGSnapshot`
instances** constructed directly from `system_learning/runtime_adg/snapshot.py`
dataclasses. No SQLite file is opened. No `RuntimeADGQuery` (static ADG)
is imported.

Shared fixture factory (in `conftest.py` or at the top of the test file):

```python
def _make_node(
    node_id: str = "span-001",
    name: str = "orchestrator.execute",
    kind: str = "orchestrator",
    layer: str = "L3",
    component: str = "apps_research",
    started_at_utc: int = 1_700_000_000_000,
    duration_ms: float = 123.4,
    status: str = "ok",
    attrs: dict | None = None,
) -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=node_id,
        name=name,
        kind=kind,
        layer=layer,
        component=component,
        started_at_utc=started_at_utc,
        duration_ms=duration_ms,
        status=status,
        attributes_json=attributes_to_json(attrs or {}),
    )

def _make_snapshot(nodes, trace_id="trace-abc-123") -> RuntimeADGSnapshot:
    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission="test",
        started_at_utc=1_700_000_000_000,
        ended_at_utc=1_700_000_001_000,
        nodes=tuple(nodes),
        edges=(),
    )
```

### 6.3 Test cases

| # | Test name | What it proves |
|:---:|---|---|
| T1 | `test_node_to_row_basic_fields` | `span_id = node.node_id`, `span_name = node.name`, `timestamp = node.started_at_utc`, `evidence_source` starts with `EVIDENCE_SOURCE_PREFIX`. |
| T2 | `test_node_to_row_attrs_parsed` | `attributes` is a dict when `attributes_json` is valid JSON. |
| T3 | `test_node_to_row_attrs_malformed_json` | `attributes = {}` and no exception raised when `attributes_json` is malformed. |
| T4 | `test_node_to_row_parent_span_id_extracted` | `parent_span_id` is extracted from `attributes["parent_span_id"]`. |
| T5 | `test_node_to_row_parent_span_id_alias` | `parent_span_id` is extracted from `attributes["parent_id"]` when `parent_span_id` is absent. |
| T6 | `test_node_to_row_contract_name_is_none` | `contract_name is None` — C.1 never resolves contracts. |
| T7 | `test_node_to_row_normalized_cert_alias_is_none` | `normalized_cert_alias is None` — C.1 never resolves aliases. |
| T8 | `test_phase_c1_row_rejects_non_not_certified` | Constructing `PhaseC1Row(runtime_certification_status="RUNTIME_CERTIFIED", ...)` raises `ValueError`. |
| T9 | `test_iter_rows_from_snapshot_yields_all_nodes` | A 3-node snapshot yields 3 rows. |
| T10 | `test_iter_rows_from_snapshot_time_filter_lower_bound` | `started_after_ms` filters out older nodes. |
| T11 | `test_iter_rows_from_snapshot_time_filter_upper_bound` | `ended_before_ms` filters out newer nodes. |
| T12 | `test_iter_rows_from_snapshot_empty_snapshot` | Zero nodes → zero rows, no exception. |
| T13 | `test_iter_rows_for_trace_correct_trace_id` | Rows carry `snapshot.trace_id`, not a per-node attribute value. |
| T14 | `test_build_test_snapshot_roundtrip` | `build_test_snapshot` returns a valid `RuntimeADGSnapshot` with correct `snapshot_id`. |
| T15 | `test_evidence_source_includes_snapshot_id` | `evidence_source == f"runtime_adg.snapshot.{snapshot.snapshot_id}"`. |
| T16 | `test_app_name_from_kwarg` | Caller-supplied `app_name` takes precedence over `attributes["app_name"]`. |
| T17 | `test_app_name_from_attrs_fallback` | When `app_name=""` kwarg, `attributes["app_name"]` is used if present. |
| T18 | `test_manifest_hash_from_attrs` | `manifest_hash` is extracted from `attributes["manifest_hash"]` when present. |
| T19 | `test_manifest_hash_default_empty` | `manifest_hash == ""` when not in attributes. |
| T20 | `test_artifact_id_and_contract_id_independent` | Both fields are populated independently when attrs contain both keys. |
| T21 | `test_source_path_from_code_filepath` | `source_path` is populated from `attributes["code.filepath"]`. |
| T22 | `test_source_path_from_alias` | `source_path` populated from `attributes["source_path"]` when `code.filepath` absent. |
| T23 | `test_to_dict_serialisable` | `row.to_dict()` output passes `json.dumps()` without raising. |
| T24 | `test_to_dict_has_all_18_fields` | `len(row.to_dict()) == 18`. |
| T25 | `test_commit_request_span_preserved` | A node with `name="CommitRequest"` is yielded by `iter_rows_from_snapshot`; C.1 does not suppress it. |
| T26 | `test_malformed_time_window_no_filter` | `started_after_ms=9999, ended_before_ms=1` logs a warning and yields all nodes. |
| T27 | `test_phase_c1_schema_version_constant` | `PHASE_C1_SCHEMA_VERSION == "1.0"`. |
| T28 | `test_no_live_db_import` | `import tools.runtime_cert.runtime_adg_query_adapter` does not attempt to open any SQLite file or import `RuntimeADGQuery`. |
| T29 | `test_extract_attributes_returns_dict` | `extract_attributes(node)` always returns a `dict`. |
| T30 | `test_iter_rows_preserves_b5_accessor_compatibility` | Row produced by `node_to_row` satisfies B.5's `_row_str(row, "app_name")` and `_row_list(row, "attributes")` without raising. |

Target: ≥30 tests, all passing, zero live-DB dependencies.

---

## 7. Scope boundaries

The following operations are **explicitly forbidden** within Phase C.1:

| Forbidden action | Why |
|---|---|
| Calling `tools/analysis/apps_spine_coverage.py` | Scanner consultation is C.3/C.4/C.5 territory, not C.1. |
| Calling `compute_manifest_hash_for_app()` | Manifest resolution is C.3/C.4/C.5. C.1 only reads `manifest_hash` from attributes if already present. |
| Importing `RuntimeADGQuery` from `tools/adg/runtime_query.py` | The static ADG and the runtime snapshot store are distinct (constitutional §23-e). C.1 targets the runtime snapshot, not the static code graph. |
| Writing any output to disk | C.1 is a pure in-memory converter. |
| Raising any exception on malformed input (except `ValueError` for the cert-status invariant) | C.1 must be safe to call from any code path, including guardrails. All errors are logged and fail-closed defaults applied. |
| Performing contract resolution | C.2's responsibility. C.1 leaves `contract_name` and `normalized_cert_alias` as `None`. |
| Evaluating certification verdicts | Phase D's responsibility. |
| Adding a new CI gate | Phase E only. |
| Modifying any emitter | Phase C never modifies emitters (AG-C-5). |

---

## 8. Implementation estimate

This plan describes the **design only**. The implementation is a separate
Author-Gate session. Sizing estimate for context:

| Artifact | Estimated lines |
|---|---|
| `tools/runtime_cert/runtime_adg_query_adapter.py` | ~150 (module docstring ~30, `PhaseC1Row` dataclass ~40, 5 functions ~60, constants ~10, `__all__` ~5) |
| `tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py` | ~60 (fixture helpers ~15, 30 test cases ~45) |
| **Total** | **~210 lines** |

Optional (not blocking C.1 merge):
- Inline doc-note in `tools/runtime_cert/__init__.py` listing exported symbols.
- One-paragraph entry in `docs/reference/runtime_certification/contract_span_binding_matrix.md`
  linking to the adapter module.

---

## 9. Acceptance criteria

C.1 is **done** when ALL of the following hold:

1. `tools/runtime_cert/runtime_adg_query_adapter.py` exists and exports
   `PhaseC1Row`, `node_to_row`, `iter_rows_from_snapshot`,
   `iter_rows_for_trace`, `build_test_snapshot`, `extract_attributes`,
   `NOT_CERTIFIED`, `EVIDENCE_SOURCE_PREFIX`, `VALID_ROUTE_SHAPES`,
   `PHASE_C1_SCHEMA_VERSION`.
2. All 30 test cases in `tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py`
   pass with `pytest -x`.
3. No live SQLite file is opened during the test run (`test_no_live_db_import`
   passes cleanly under `RUNTIME_CERT_NO_DB=1` if that env-check is added).
4. `runtime_certification_status == "NOT_CERTIFIED"` in every row
   produced by the adapter (`test_phase_c1_row_rejects_non_not_certified`
   passes).
5. No emitter file, scanner file, CI gate file, or app file was modified.
6. `tools/analysis/apps_spine_coverage.py` is unchanged.
7. `tools/adg/runtime_query.py` is unchanged.
8. `system_learning/runtime_adg/snapshot.py` is unchanged.
9. Every `apps_*` app remains at `NOT_CERTIFIED` (class-level
   `runtime_certification_status` field unmodified).
10. **C.2 is gated on C.1 acceptance criteria all passing** — no C.2
    implementation begins until this list is satisfied (AG-C-9).

---

## 10. Stop conditions (C.1 blocked)

C.1 implementation is blocked if any of the following are discovered
during the implementation Author-Gate session:

| # | Condition | Recovery |
|:---:|---|---|
| B1 | `RuntimeADGNode` has been modified (new/removed fields) and the 18-field schema is no longer consistent | Amend this plan; re-run Author-Gate before writing code. |
| B2 | `system_learning/runtime_adg/snapshot.py::attributes_to_json` has changed to a non-JSON format | Update `extract_attributes` spec; amend this plan. |
| B3 | A Phase B.5 accessor (`_row_str`, `_row_list`) requires a field that C.1 does not produce | Add that field to `PhaseC1Row`; bump `PHASE_C1_SCHEMA_VERSION`; re-run Author-Gate on the schema change (AG-C-3 amendment). |
| B4 | The `tools/runtime_cert/` package does not exist or has been relocated | Verify `tools/runtime_cert/__init__.py` exists; unblock before proceeding. |
| B5 | A concurrent PR modifies the 18-field schema between plan approval and implementation start | Gate on schema-freeze confirmation; do not implement a stale schema. |

---

## 11. Final output summary

| Item | Value |
|---|---|
| **Plan path** | `.windsurf/plans/runtime-cert-c1-query-adapter-7e3f92.md` (this file) |
| **Files inspected for this plan** | `tools/adg/runtime_query.py`, `system_learning/runtime_adg/snapshot.py`, `tools/runtime_cert/negative_controls.py` (lines 1–60), `docs/plans/runtime_cert_phase_c_trace_collector_plan.md` (full) |
| **Proposed adapter module** | `tools/runtime_cert/runtime_adg_query_adapter.py` |
| **Proposed test file** | `tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py` |
| **Proposed public API** | `PhaseC1Row` (dataclass), `node_to_row`, `iter_rows_from_snapshot`, `iter_rows_for_trace`, `build_test_snapshot`, `extract_attributes`, + 4 constants |
| **Open questions** | See §11.1 below |
| **Files modified by this plan** | **0** — documentation only |
| **Apps affected by this plan** | **0** — read-only planning |
| **Runtime certification performed** | **NO.** No app has been certified. No `runtime_certification_status` other than `NOT_CERTIFIED` has been written or proposed anywhere in this plan. The `apps_*` cohort remains at its post-W14 state: 6 `APP_OVERLAY_STATIC_EVIDENCE`, 3 `FORMAL_EXCEPTION_STATIC_EVIDENCE`, 0 `RUNTIME_CERTIFIED`, 0 `FORMAL_EXCEPTION_VERIFIED`. |

### 11.1 Open questions

| # | Question | Impact | Resolution path |
|:---:|---|---|---|
| Q1 | Should `PhaseC1Row` use `dataclass(frozen=True)` (immutable) or a mutable dataclass? | Frozen is safer for concurrent consumers (C.3/C.4/C.5 may run in parallel per AG-C-9). Mutable is easier for C.2 to back-fill `contract_name`. | Resolve at implementation Author-Gate. Recommended: frozen, with C.2 producing a new row via `dataclasses.replace()`. |
| Q2 | Should `iter_rows_from_snapshot` accept a `RuntimeADGSnapshot` only, or also a `pathlib.Path` to a persisted snapshot file? | Adding a path-based overload would make C.6 smoke ergonomics simpler (load from file → iterate). But it adds I/O to what should be a pure converter. | Resolve at implementation Author-Gate. Recommended: path-based loading stays in a separate `load_snapshot_from_path(path)` helper; C.1's core functions remain pure. |
| Q3 | Does `PHASE_C1_SCHEMA_VERSION = "1.0"` need to be written into `PhaseC1Row.to_dict()` output? | Yes — it lets Phase D detect schema version mismatches across cached row sets. | Add `schema_version` as a 19th field in `to_dict()` output only (not in the dataclass itself, to avoid inflating the 18-field count). Resolve at implementation Author-Gate. |

---

## Provenance

| Item | Value |
|---|---|
| Plan version | **v1** (initial) |
| Generated | 2026-04-30 |
| Parent plan | `docs/plans/runtime_cert_phase_c_trace_collector_plan.md` v2 |
| Author-Gate status | All prerequisite decisions (AG-C-1…9) approved in parent plan §0. This plan does NOT authorize implementation — a separate Author-Gate session is required before any Python is written (per parent plan §0.3). |
| Files inspected | 4 |
| Files modified | 0 |
| Apps affected | 0 |
| Runtime certification performed | NO |
