# Issue #343 reachability decision for Apps Research → Apps RG certification

**Decision date:** 2026-07-13
**Decision:** Track separately; do not expand issue #550's critical path.

## Scope

Wave 6 of the Apps Research → Apps RG E2E hardening work requires a
reachability decision for
`apps_rg/runtime/validators/verb_canonicalizer_validator.py`. The question is
whether that module is reachable from the certified Apps RG C0, PA, or L2
product path.

## Static evidence

Repository-wide symbol and import searches found only:

1. the module itself;
2. the legacy L5 compatibility shim at
   `agentic_core/L5_safety/validators/verb_canonicalizer_validator.py`; and
3. its isolated unit test at
   `tests/unit/apps_rg/runtime/validators/test_verb_canonicalizer_validator.py`.

No Apps RG C0, PA, L2, whole-run, section-run, Exit, or mandatory-output
module imports or invokes `VerbCanonicalizer`, `canonicalize`, or
`check_for_forbidden_verbs`.

The module is visibly defective (its methods are module-level, refer to
nonexistent public constant names, and append to an undefined `canonical`
variable), but static source reachability does not place it on the issue #550
product path.

## Limits of this decision

The repository-readiness check could not query the live ADG service in this
workspace, so this is a static source/import/symbol decision, not a claim of
graph-certified unreachability. Any future ADG edge, runtime registry entry,
dynamic import, or explicit C0/PA/L2 caller invalidates this decision and must
reopen the critical-path assessment.

## Required follow-up

- Keep issue #343 open or repair it in a separate change.
- Do not treat the existing expected-failure behavior as product validation.
- Add the module to issue #550 only if a concrete C0/PA/L2 reachability edge is
  established.
