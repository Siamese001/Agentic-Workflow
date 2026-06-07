---
name: fortknox-evidence
description: Runtime-certification evidence discipline — hostile verifier, atomic assertions, compiler-is-the-only-status-authority, mutation-rejection pairing, positive-control canary. Invoke for any task mentioning certification, runtime certification, signoff, evidence, attestation, proof bundle, `RTC-REQ-*`, `compile_requirement_signoff.py`, `verify_final_requirement_signoff_bundle.py`, or.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: evidence_discipline
---
# Fort Knox Evidence Skill

In-house certification-evidence discipline. No upstream MCP surface — the integrity comes from deterministic scripts, schemas, and hashes.

**Parent rule:** `.claude/rules/fortknox-certification-discipline.md`
**Dual-track SSOT:** `docs/architecture/adr/ADR-103-fortknox-runtime-dual-track.md` (certification vs runtime proof)
**Runtime template:** `docs/reports/runtime_cert/README.md`
**Constitutional tie-in:** §32
**Author-Gate trigger:** `certification_claim` (author-gate-decision-points.md §1.11)

## When To Invoke

| User intent | Use this skill? |
|---|---|
| Claim a requirement is `SIGNED_OFF` | ✅ Yes — REQUIRED (run compiler + verifier first) |
| Add or modify atomic assertions | ✅ Yes — REQUIRED (schema + emitter-path rules) |
| Author a positive-control fixture | ✅ Yes — use `tools/cert/build_positive_control_fixture.py` as template |
| Diagnose a `trust_level == FAILED` | ✅ Yes — consult the failed-check list in the report |
| Regenerate the mutation-rejection bundle | ✅ Yes — pairs with compiler bundle, never folded in |
| Generic test failure unrelated to certification | ❌ No — use `testing-framework` skill |

## Hard Rules

1. **Never hand-edit** `artifacts/certification/final_requirement_signoff_report.json`. It is a compiler output. Re-run `tools/cert/compile_requirement_signoff.py` instead.
2. **Never bypass** the atomic-assertion schema. Every row must match `config/certification/schemas/evidence_assertion.schema.json` — one `req_id` + one `control` + one artifact-backed fact.
3. **Never fold** the mutation runner into the compiler output path. They are distinct trust roots by design (separation of duties).
4. **Always run as a pair** — `compile_requirement_signoff.py` + `verify_final_requirement_signoff_bundle.py` — when claiming any signoff status.
5. **Build positive controls before broadening scope.** A broken compiler that rejects everything is indistinguishable from a rigorous one without the canary.
6. **Assertion IDs are hex only.** `ASRT-<16–64 lowercase hex>` per schema pattern. Human-readable names are rejected.
7. **Pointers must resolve to req-scoped dicts.** `/per_req/<req_id>/<control>` — never a scalar at the root, never a substring match on a list.
8. **Emitter paths are allowlisted.** `tools/cert/*.py`, `scripts/verify_*_gate.py`, `scripts/verify_rtc_*.py`. Runtime paths (`agentic_core/*`, `apps_*/*`, `system_learning/*`) MUST NOT emit assertions.

## Canonical Workflow

### To claim a requirement is signed off

```bash
# 1. Regenerate report from atomic assertions.
python tools/cert/compile_requirement_signoff.py

# 2. Independent bundle verifier (MUST pass).
python ops_scripts/ci/verify_final_requirement_signoff_bundle.py

# 3. Adversarial mutation bundle (MUST reject all).
python ops_scripts/ci/generate_mutation_rejection_report.py

# 4. Read the report — status field is authoritative.
python -c "import json,pathlib; r=json.loads(pathlib.Path('artifacts/certification/final_requirement_signoff_report.json').read_text()); print(r.get('trust_level'), list((r.get('per_requirement') or {}).keys())[:5])"
```

### To add a new positive-control fixture

1. Copy `tools/cert/build_positive_control_fixture.py` — do not invent a new emitter pattern.
2. Fixture MUST produce a row-specific artifact with per-control pointers at `/per_req/<req_id>/<control>`.
3. Each emitted assertion's `assertion_id` = `"ASRT-" + sha256(f"{req_id}|{control}|{artifact_sha256}|{pointer}").hexdigest()[:40]`.
4. Commit the fixture with a deterministic filename including the `req_id` so git history is inspectable.
5. Re-run the canonical workflow. Confirm the new row lands as `SIGNED_OFF` in the report.

### To diagnose `trust_level == FAILED`

1. Read the report's `failed_checks` array — it names the specific validator rule (10-check validator).
2. For each failed check, read the referenced artifact at `artifact_path` and verify sha256 matches `artifact_sha256`.
3. If the artifact drifted: regenerate it (re-run the emitter). If the schema drifted: check the producer allowlist.
4. Do NOT edit the report to mask the failure — the gate will still block commit.

## Forbidden Patterns

- ❌ `"all_pass": true` as top-level proof — must be per-control `"assertion_result": "PASS"`
- ❌ `"linked_req_ids": [RTC-REQ-001, RTC-REQ-002]` as the only req_id reference
- ❌ `assertion_id: "signoff-gate-001"` — human-readable names rejected
- ❌ Pointer `/status` or `/trust_level` — scalar at root, not row-specific
- ❌ Emitter path `agentic_core/.../verifier.py` — runtime code must not emit
- ❌ Running mutation runner against the real `final_requirement_signoff_report.json` — use the pure validator function in a sandbox
- ❌ Caching `row_digest` / `merkle_root` anywhere except the report + sha256 sidecar

## Deterministic Gates (context)

| Gate | Purpose |
|---|---|
| `ops_scripts/ci/check_fortknox_clean_bundle.py` | Compiler + verifier agree; `trust_level != FAILED` |
| `ops_scripts/ci/check_fortknox_mutation_rejection.py` | All mutations rejected; clean bundle unchanged |
| `ops_scripts/ci/check_fortknox_positive_control.py` | `RTC-REQ-001` remains `SIGNED_OFF` |
| `.cursor/scripts/pre_write_fortknox_guard.py` | Blocks direct report edits (exit 2) |
| `.cursor/scripts/post_cursor_agent_fortknox_integrity_audit.py` | Retroactive claim-without-compiler detection |
| `.github/workflows/fortknox-nightly.yml` | Nightly regression scan + issue filing |

## Bypass

`FORTKNOX_DISCIPLINE_BYPASS=1` — logs a bypass row across all gates. Use only for scripted batch runs during compiler refactoring, schema evolution, or acknowledged exploratory sessions.

## References

- Path SSOT: `tools/cert/cert_paths.py`
- Schema SSOT: `config/certification/schemas/evidence_assertion.schema.json`
- Compiler: `tools/cert/compile_requirement_signoff.py`
- Bundle verifier: `ops_scripts/ci/verify_final_requirement_signoff_bundle.py`
- Mutation runner: `ops_scripts/ci/generate_mutation_rejection_report.py`
- Positive-control template: `tools/cert/build_positive_control_fixture.py`
- Rule: `.claude/rules/fortknox-certification-discipline.md`
- Author-Gate trigger: `.claude/rules/author-gate-decision-points.md` §1.11
