# PA — Requirement Traceability Matrix (live runtime-evidence)

This file is the discoverable pointer from inside the PA doctrine folder
to the live, regenerated requirement-traceability matrix.

## Live matrix (regenerated each run)

- **Human report**: `docs/reports/prompt-assembly/runtime_evidence.md`
- **Machine sidecar (JSON)**: `tools/prompt_assembly/_runtime_evidence.json`

Both files are produced by the runtime-evidence harness:

```
python tools/prompt_assembly/runtime_evidence.py
```

The harness exits non-zero (and CI fails) if any requirement row is FAIL.
A passing run prints `VERDICT: PROVEN` with `N PASS / 0 FAIL`.

## What the matrix covers

Every row in every category below is generated against the actually-loaded
runtime objects in `agentic_core/prompt_governance/prompt_assembly/` and
the live PA pipeline. Categories marked **(harden-pass)** were added to
close the open scope around PA.8, parent doctrine, per-child forbidden
blocks, child MUST NOT clauses, and parser edge hardening.

| Category | What it proves |
|---|---|
| `STATUS_SET` | Every doctrine `PA_*` status name resolves to a member of the runtime `PAStatus` enum, and the per-stage `STAGE_TO_STATUSES` partition matches each `STATUS VALUES` block in PA.0..PA.7 |
| `STATUS_PARTITION_COMPLETE` | Every runtime `PAStatus` member is claimed by at least one stage; cross-stage statuses match the documented set |
| `DOCTRINE_DRIFT` | The `STATUS VALUES` parsed live from each `.md` file equals the runtime per-stage status partition (closes the SSOT-drift loophole) |
| `MUST_EMIT` | Every `MUST EMIT` field in each PA.0..PA.7 doctrine file is present (directly or via documented alias) in the constructed receipt envelope |
| `MUST_NOT_FENCE` | The PA package exposes NO public callable whose name implies retrieve / execute / route / call_provider / approve_output / mutate_l4 / commit_state |
| `FORBID_RD` | The parent doctrine's forbidden runtime-disposition set lives in `FORBIDDEN_DISPOSITIONS` and forbidden execution-verb set lives in `FORBIDDEN_EXECUTION_VERBS` |
| `FORBID_DEEP` | A receipt containing a forbidden token at any depth (root, nested dict, list element, deeply nested) is rejected by `assert_no_forbidden` |
| `FORBID_FALSE_POSITIVE` | Substring lookalikes (`allowance`, `denylist`) that are NOT exact forbidden tokens do NOT trigger rejection |
| `INVARIANT` | Each of the 12 cross-child invariants (PA.I1..PA.I12) has a constructive runtime check |
| `SLOT_MAP` | The canonical 10-slot map (S0/D0/I0/E0/C0/M0/U0/Y0/H0/R0) and authority-rank ordering can be constructed and is preserved |
| `NEGATIVE_PATH` | Every doctrine gap status is reachable through a negative-path runtime fixture |
| `DETERMINISM` | PA.I9/PA.I10: same BOM + slots + trimming + secret produce identical canonical bytes / hash / signature on repeated runs |
| `AGGREGATION` | `aggregate_doctrine_status` over a list of stage receipts collapses to the documented worst-case status |
| `PARSER_ROBUSTNESS` | The doctrine parser handles edge-case `.md` inputs (missing section, blank file, repeated heading, non-bullet noise, section terminated by next heading) |
| `E2E` | The full PA.0 → PA.7 pipeline runs end-to-end on a happy-path fixture and emits every required receipt with `dispatch_allowed = True` |
| `PIPELINE_NEG` | The pipeline correctly publishes a non-`PA_READY` aggregate status and refuses dispatch when input is incomplete; negative-path receipts contain ZERO forbidden tokens |
| `PARENT_VOCAB` **(harden-pass)** | Every status name in the parent doctrine's `STATUS VOCABULARY` block is a member of `PAStatus` AND is claimed by at least one stage's `STAGE_TO_STATUSES` partition |
| `CHILD_FORBID_DOCTRINE` **(harden-pass)** | For every PA.0..PA.7 child, the `FORBIDDEN OUTPUTS FROM THIS CHILD` block (a) parses non-empty, (b) is a subset of the parent master forbidden set, and (c) inherits every parent forbidden token (no silent drop) |
| `MUST_NOT_DOCTRINE` **(harden-pass)** | Every `MUST NOT` keyword in each PA.0..PA.7 child maps to at least one member of the parent's forbidden disposition / execution-verb set via the documented keyword → forbidden-token table |
| `PA8_RULES` **(harden-pass)** | Every PA.8 `RULES` keyword (C0 / R0 / Provider / Token) has a corresponding runtime artefact (function or type) on the PA package surface |
| `PA8_TESTS` **(harden-pass)** | Every PA.8 `TEST REQUIREMENTS` test name is present in the PA test corpus (literal name OR documented functional equivalent), with the corpus being PA test files + PA doctrine markdowns + their basenames |
| `PA8_CONTRACTS` **(harden-pass)** | Every PA.8 `CONTRACTS TO IMPLEMENT` field token (e.g. `proof_id`, `slot_hashes`, `provider_render_hash`) is absorbed by either a PA package symbol or a key in the recursively-walked PA.0..PA.7 receipt envelope |
| `PARSER_EDGE_HARDENING` **(harden-pass)** | The doctrine parser handles 7 additional encoding/whitespace/marker edge cases (UTF-8 BOM, trailing-colon heading, tab-indented bullets, asterisk markers, unicode bullet U+2022, lookalike heading mid-prose, heading without underline, CSV-style forbidden bullet split) |

## CI signal

The pytest wrapper at
`tests/unit/agentic_core/prompt_governance/prompt_assembly/test_runtime_evidence_harness.py`
parametrises every category and fails CI if any row is FAIL. All 23
categories above are exercised through the same parametrize block, so
adding a new category to the harness automatically extends CI coverage
with no test changes.

Two sibling tests close the SSOT-drift loophole at the doctrine layer:

- `test_doctrine_parser_finds_all_eight_stages` — every `PA.0..PA.7`
  doctrine `.md` file must yield ≥1 `STATUS VALUES` and ≥1 `MUST EMIT`
  bullet (heading rename / file move detection).
- `test_doctrine_status_values_resolve_to_PAStatus` — every parsed
  `STATUS` name must be a member of the runtime `PAStatus` enum.

## Related anchors

- Parent doctrine: `Prompt_Assembly.md` (this folder)
- Authority red-team child: `PA.8_Authority_RedTeam_Slot_Verification.md` (this folder)
- Cross-folder traceability: `../00X_Requirements_Traceability_and_No_Loss_Map.md`
- E2E proof harness: `../99_End_to_End_Runtime_Proof_and_Acceptance/`
- Runtime modules under test: `agentic_core/prompt_governance/prompt_assembly/`
