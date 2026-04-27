# apps_proof — Threat Model and Coverage Matrix

> **Scope**: this document is the apps_proof harness's reviewer checklist. It
> exists because of audit-pass-1 BUG #1 (anti-tamper invariant claimed
> beyond enforced scope) and BUG #6 (artifact files referenced in the
> inventory but not hash-verified). The combined RCA root-causes are
> RC-3 (trust boundaries undrawn) and RC-4 (anti-tamper scope unenumerated).
>
> **Limitation**: passing every line in this matrix only proves the
> apps_proof harness is internally consistent. It does NOT prove
> compliance with the broader docs/reference architecture requirements.
> See `tools/proof/req_compiler.py` and the requirements-evidence matrix
> at `artifacts/runtime/req_evidence/latest/requirements_matrix.md` for
> the full architectural compliance gate.

## 1. Trust boundaries

Every field that crosses a boundary must declare its required validation.

| Field | Crossing | Trust state after | Required validation | Validator owner |
|---|---|---|---|---|
| `packet.app_id` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | NEVER use to derive on-disk paths; treat as content only | `validators.validate_artifact_inventory` (BUG #1 fix) |
| `packet.scenario_id` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | NEVER use to derive on-disk paths; pass trusted path explicitly | `validators.validate_artifact_inventory` |
| `packet.packet_hash` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | recompute from canonical body; compare; reject mismatch | `verify_packet_hash` |
| `ContractRecord.payload_path` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | exists check + non-empty + (in W2) content_hash recomputation | `validators.validate_artifact_inventory` |
| `ArtifactRecord.path` + `content_hash` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | walk inventory, recompute sha256_of_file, compare hash (BUG #6 fix) | `validators.validate_artifact_inventory` |
| `SpanRecord.parent_span_id` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | every parent_span_id MUST reference an emitted span_id | `validators.validate_trace_tree` |
| `SpanRecord.trace_id` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | non-None AND consistent across all spans (BUG #2 fix) | `validators.validate_trace_tree` |
| `SpanRecord.layer` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | must respect canonical sequence U0 → ... → L6 → customizer | `validators.validate_trace_tree` |
| `Contract.task_spec / route_id / etc.` | in-memory → JSON write → JSON read | post-disk = attacker-influenced | re-run scenario deterministically; compare timestamp-stripped content | `validators.validate_replay` |
| `sandbox_writer.artifact_id` | function arg → Path.__truediv__ | UNTRUSTED at API surface | allowlist `[A-Za-z0-9._-]`, reject `..`, leading `.`, length > 128 (BUG #8 fix) | `sandbox_writer._validate_artifact_id` |
| `request_uwg_commit.artifact_id` | function arg → Path.__truediv__ | UNTRUSTED at API surface | same allowlist as sandbox_writer | `sandbox_writer._validate_artifact_id` |
| `app_id` (from CLI `--apps` flag) | argv → SQL LIKE pattern | UNTRUSTED | scenarios.SCENARIOS membership check (registered apps only) | `proof_runner.main` |
| Bypass query result `unresolved` | sqlite query → in-memory | sentinel-poisoned (-1 on error) | clamp to `max(int(total), 0)` before summing (BUG #3 fix) | `adg_queries.run_bypass_queries` |
| Customizer-emitted exceptions | function call → caller frame | broad (sandbox_writer can raise OSError, ImportError, KeyError) | catch (RuntimeError, ValueError, TypeError, AttributeError, ImportError, OSError, KeyError); emit FAIL span (BUG #4 fix) | `scenario_base.run_app_scenario` |
| W3 reload `packet_dict["app_id"]` | json.loads → dict access | malformed JSON / missing keys | wrap in try/except (JSONDecodeError, KeyError, TypeError, ValueError); fall through to validator_exception (BUG #9, #10 fix) | `proof_runner.main` |

## 2. Tamper × validator coverage matrix

For each tamper class, declare which validator catches it AND the expected
fail_reason substring. A "no" cell that should be "yes" is a defense gap;
a "yes" cell with no expected_fail_reason is a wrong-mechanism risk.

| Tamper | Inventory | Trace | Replay | Write sovereignty | Expected fail_reason |
|---|:---:|:---:|:---:|:---:|---|
| Mutate `packet_hash` field | ✅ | — | — | — | `hash mismatch` |
| Mutate `app_id` without rehash | ✅ | — | — | — | `hash mismatch` (after BUG #1 fix) |
| Delete trace inventory file | ✅ | (n/a if file gone) | — | — | `inventory missing` |
| Empty trace inventory file | ✅ | — | — | — | `inventory empty` |
| Set all root parent_span_ids to non-None | — | ✅ | — | — | `expected exactly 1 root` |
| Orphan parent_span_id | — | ✅ | — | — | `missing parent` |
| Inconsistent trace_id across spans | — | ✅ | — | — | `inconsistent trace_id values` |
| All-None trace_id (BUG #2) | — | ✅ | — | — | `span(s) missing trace_id` |
| Layer order swap | — | ✅ | — | — | `appears after later layer` |
| Mutate L1PlanContract.task_spec | — | — | ✅ | — | `L1PlanContract: content hash drift` |
| Inject field into RouteContract | — | — | ✅ | — | `RouteContract: content hash drift` |
| Remove route_id from RouteContract | — | — | ✅ | — | `RouteContract: content hash drift` |
| Remove `packet_hash` field entirely | ✅ | — | — | — | `no packet_hash field` |
| Mutate sandbox artifact content (BUG #6) | ✅ | — | — | — | `artifact content_hash drift` |
| Delete sandbox artifact file (BUG #6) | ✅ | — | — | — | `artifact file missing` |
| `apps_*` direct infra import | — | — | — | ✅ | `direct infra writes bypass UWG` |
| `apps_*` write outside UWG | — | — | — | ✅ | `P0 write-bypass-UWG violations` |
| Recompute hash after mutation (T13 — DOCUMENTED LIMITATION) | ❌ documented | — | (would catch via volatile fields) | — | (no fail — defense-in-depth probe) |

## 3. What this matrix does NOT cover

The harness's `caught=True` (verdict) and `reason_match=True` (mechanism)
together prove the LISTED tampers are caught. The following gaps remain
by design:

- **Dynamic content tamper inside spans/gates beyond span tree well-formedness** — e.g. mutating `span.attrs.route_id` would not be caught (no validator hashes span content). Mitigation: the trace tree validator catches structural anomalies; the replay validator catches contract drift; span attrs are advisory.
- **Symlink + file replacement attacks on Windows** — sha256_of_file follows the file at the path; a symlink pointing elsewhere isn't detected as a tamper. Out of scope; harness assumes filesystem integrity.
- **Concurrent mutation during validation** — validate_replay re-runs the scenario; if an attacker mutates during the second run, racy outcomes possible. Out of scope; harness assumes single-writer invariant during validation.
- **Determinism of upstream IntakePipeline metadata** — wall-clock timestamps and runtime UUIDs are stripped by `_strip_volatile`. By design, mutating those volatile fields is NOT a tamper.

## 4. Reviewer checklist (use before merging changes to apps_shared/proof/)

For each change to apps_shared/proof/* answer YES/NO:

1. Does this introduce a new field that crosses a trust boundary? If YES, add a row to §1.
2. Does this change a validator's claimed scope (catches new tampers, drops some)? If YES, update §2.
3. Does this add a new negative control? If YES, declare its `expected_fail_reason` in `CONTROLS` AND add a row to §2.
4. Does this add a public API surface that takes a string used in a `Path.__truediv__`? If YES, add allowlist validation (precedent: `_validate_artifact_id`).
5. Does this catch broad exceptions inside a validator? If YES, narrow to specific types (use `except Exception` ONLY at the outer multi-app iteration boundary, where it MUST log full stack to artifact log).
6. Does this read a JSON file that came from disk? If YES, validate `isinstance(parsed, dict)` (or whatever shape) before indexing.

## 5. Scope transfer to docs/reference

This matrix is local to apps_proof. The same boundary-table + coverage-
matrix pattern MUST be applied across the broader L0..L6 reference
architecture. The 12 reference directories that need this treatment:

```
docs/reference/00A_L5_Governance_Safety/
docs/reference/00B_L4_State_Archive_and_UWG/
docs/reference/00C_Runtime_Gates_Current_Run_Mesh/
docs/reference/01_Request_Intake/
docs/reference/02_L1_Reasoning_Plan/
docs/reference/03_L0_Route_Decision_and_L3_Orchestration/
docs/reference/03A_C0_Context_Engine/
docs/reference/03B_PA_Prompt_Assembly/
docs/reference/04_L2_Execute/
docs/reference/05_Exit_Evaluation_and_Control/
docs/reference/06_L6_Shadow_Evaluation_System_Learning/
docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/
```

The mechanical bridge from those requirements to runtime evidence is the
**requirements-to-runtime evidence compiler** at
`tools/proof/req_compiler.py`. Each requirement extracted from the above
gets a row in the runtime-evidence matrix with status:

```
PASS | PARTIAL | MISSING | DOC_ONLY | MOCK_ONLY | FAKE | UNVERIFIED | NOT_APPLICABLE
```

Release-grade compliance requires:
1. apps_proof harness `--mode full` exits 0 (this matrix ALL green)
2. requirements-evidence matrix has zero rows in
   `{MISSING, DOC_ONLY, MOCK_ONLY, FAKE, UNVERIFIED}` (excluding `NOT_APPLICABLE`)

Either alone is insufficient. Both together = release-eligible.
