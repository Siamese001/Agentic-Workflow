# Output-Contract Registry

Registry for output contracts consumed by the Output-Contract Validator at
v33 §5 EXIT EVAL. See [ADR-039](../../docs/architecture/adr/ADR-039-output-contract-validator.md).

## Layout

```
config/contracts/
  <contract_id>.json         # contract metadata + kind-specific payload
```

Each contract file is self-describing:

```json
{
  "contract_id": "underwriting.decision_packet.v1",
  "kind": "json_schema",
  "version": 1,
  "schema_ref": "config/schemas/decision_packet.schema.json",
  "description": "Underwriting AI decision-packet output contract"
}
```

## Contract kinds (ADR-039 §2.1)

| kind | Required fields |
|---|---|
| `json_schema` | `schema_ref` → path to a JSON Schema 2020-12 file |
| `markdown_sections` | `required_sections` list (ordered); `optional_sections` list |
| `tool_result_envelope` | `envelope_version` integer |
| `proposal_template` | `template_ref` path; `app_domain` string |
| `text_constraints` | `max_chars`, `min_chars`, `regex_denylist`, `language` |
| `none` | (no fields) |

## Resolution

A request that declares `output_contract_ref: "<contract_id>"` resolves to
`config/contracts/<contract_id>.json`. Missing refs cause the validator to
emit `required_form_satisfied=false` with violation
`contract_ref_unresolved:<contract_id>`.

## Status

Scaffold only. Concrete contract files are added as apps declare them.
