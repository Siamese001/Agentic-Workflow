# Guardian-to-L6 Ingestion Contract

Version: 1
Date: 2026-02-08

## Artifact Location

All guardian result artifacts MUST be written to:

```
docs/reports/guardian_artifacts/
```

This is the SSOT constant `GUARDIAN_ARTIFACT_DIR` in `guardian_contract.py`.

## Filename Pattern

```
guardian_{guardian_id}.json
```

Examples:

- `guardian_hygiene.json`
- `guardian_manifest_integrity.json`
- `combined_guardian_result.json`

This is the SSOT constant `GUARDIAN_ARTIFACT_PATTERN` in `guardian_contract.py`.

## Schema

Every artifact conforms to `GuardianResult.to_dict()` as defined in:

```
agentic_core/L0_maintenance/types/guardian_contract.py
```

Contract version: `CONTRACT_VERSION` (integer, currently 1).

## Required Fields

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `guardian_id` | str | yes | Stable identifier |
| `version` | int | yes | Contract version |
| `status` | str | yes | PASS, FAIL, ERROR |
| `summary` | str | yes | Human-readable summary |
| `checks` | list | yes | Ordered check entries |
| `artifacts` | list | yes | Emitted artifact refs |
| `metrics` | dict | yes | Numeric metrics |
| `remediation_hints` | list | yes | Fix suggestions |
| `timestamp` | str | no | ISO-8601 (injectable) |
| `correlation_id` | str | no | Deterministic if injected |

## Correlation Strategy

- `correlation_id` is optional but deterministic when injected via CLI `--correlation-id`.
- L6 ingestion should use `correlation_id` to group results from the same CI run.
- If absent, L6 should fall back to `timestamp` or filesystem mtime.

## Path Contract

- All paths in `artifacts[].path` are repo-relative POSIX.
- No absolute paths. Enforced by `normalize_repo_path()`.
- No backslashes. No `..` segments. No leading `/`.

## Compatibility

- Any change to `CONTRACT_SCHEMA_SNAPSHOT` keys requires `CONTRACT_VERSION` bump.
- L6 consumers must check `version` field and reject unknown versions.
- `check_schema_compatibility()` function available for programmatic validation.

## Performance Ceilings

- Max guardian runtime: 30,000 ms (`MAX_GUARDIAN_RUNTIME_MS`)
- Max artifact size: 512 KB (`MAX_ARTIFACT_SIZE_KB`)
- Max scan depth: 10 levels (`MAX_SCAN_DEPTH`)
