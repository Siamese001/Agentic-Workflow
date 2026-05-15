# Cursor Runtime Seam Template

## Objective

Patch or verify exactly one runtime seam.

## Immutable constraints

- Do not edit `agentic_core` unless explicitly authorized.
- Do not change registries, v1 prompts, global gates, or broad runtime paths unless explicitly authorized.
- Do not mark PASS without completed commands and tests/gates.

## Allowed files

- `<path>`

## Commands

```bash
<exact command>
<exact test or gate>
```

## Required final response

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
FILES_CHANGED:
- path
COMMANDS_RUN:
- command -> result
TESTS_GATES:
- command -> result
ARTIFACTS:
- path or NONE
NOTES:
- caveat
```
