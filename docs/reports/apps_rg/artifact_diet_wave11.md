# apps_rg Artifact Diet Wave 11

## Scope

Wave 11 adds a non-destructive artifact diet for runtime proof manifests.
Section lanes may keep verbose debug files on disk, but downstream consumers now
get a compact proof-oriented link set.

## Delivered

- `apps_rg/runtime/artifact_diet.py`
  - classifies artifacts as `proof_core`, `proof_optional`, `diagnostic_heavy`, or `diagnostic_other`
  - exports `compact_artifact_links()`
  - exports `build_artifact_diet_receipt()`
- `apps_rg/runtime/runtime_proof_layout.py`
  - preserves legacy `artifact_links`
  - adds `artifact_links_compact`
  - adds `artifact_diet`

## Diet Policy

Compact links keep proof surfaces such as:

- `l2_output.json`
- `x2_gate_outputs.json`
- `x3_disposition.json`
- `section_input_usage_ledger.json`
- `canonical_claim_ledger_v2.json`
- `runtime_exhaust_bundle.json`

Verbose diagnostics remain on disk but are omitted from compact links:

- `provider_response.json`
- `compiled_prompt.txt`
- `command_output.txt`
- `parsed_output.json`
- `prompt_selection_trace.json`

## Guardrails

- No artifact files are deleted.
- Legacy `artifact_links` remain unchanged for compatibility.
- Compact links are additive and safe for package consumers to adopt gradually.
