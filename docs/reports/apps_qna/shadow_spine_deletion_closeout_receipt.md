# apps_qna shadow spine deletion — closeout receipt (final)

**Date:** 2026-05-20  
**Scope:** Tier A orphan/dead duplicate deletion + Tier B shadow spine removal + stale metadata cleanup. Tier C ADR-082 **out of scope**.

## STATUS: PASS

## ACCEPTED_SCOPE

- Tier A orphan/dead duplicate deletion complete (`qna_capability_registry.py`, `qna_l2_step_adapters.py`, `qna_exit_fec_producer.py` — confirmed deleted on disk; no live imports).
- Tier B shadow spine deletion complete (`live_interview_runtime.py` deleted; import raises `ModuleNotFoundError`).
- Canonical runtime proof: `python -m apps_qna build --interview default` → exit 0.
- Stale deleted-module metadata removed (`source_channel`, docstrings).
- Tier C ADR-082 migration not performed.

## FOLLOW_UP_CHECK (resolved)

**Issue:** Earlier receipt listed `qna_capability_registry.py` under `REMAINING_REFERENCES` as `STABLE_ROUTE_ID` while Tier A claimed the file was deleted.

**Root cause:** Sloppy wording. The file **still existed on disk** when the hardening receipt was written; only `live_interview_runtime.py` had been removed in that wave. Tier A deletions were applied in the final closeout pass.

**Verification (2026-05-20):**

| Check | Result |
|-------|--------|
| `test -f apps_qna/qna_capability_registry.py` | **nonzero** (file absent) |
| `test -f apps_qna/live_interview_runtime.py` | **nonzero** (file absent) |
| `rg qna_capability_registry` in `apps_qna` `tests` `ops_scripts` `*.py` | **no matches** |
| `rg live_interview_runtime` in same scope | **stable route IDs + negative-control tests only** (see below) |
| `git status --short` Tier A/B paths | `D` for all four deleted modules |

## FILES_CHANGED

### Deleted (Tier A — applied final pass)

- [qna_capability_registry.py](../../apps_qna/qna_capability_registry.py)
- [qna_l2_step_adapters.py](../../apps_qna/qna_l2_step_adapters.py)
- [qna_exit_fec_producer.py](../../apps_qna/qna_exit_fec_producer.py)

### Deleted (Tier B)

- [live_interview_runtime.py](../../apps_qna/live_interview_runtime.py)

### Modified (metadata / proof-enabling)

- [l2_binding.py](../../apps_qna/runtime/bindings/l2_binding.py)
- [__main__.py](../../apps_qna/__main__.py)
- [u0_intake.py](../../apps_qna/u0_intake.py)
- [profile_builder.py](../../apps_qna/runtime/profile_builder.py) — see [INCIDENTAL_RUNTIME_FIX](#incidental_runtime_fix)
- [test_w0_thin_slice.py](../../tests/apps_qna/test_w0_thin_slice.py)
- [test_apps_qna_entrypoint.py](../../tests/apps_qna/governance/test_apps_qna_entrypoint.py)

## INCIDENTAL_RUNTIME_FIX

- **File:** [profile_builder.py](../../apps_qna/runtime/profile_builder.py)
- **Change:** `briefing_artifact_ref=` → `manual_brief_path=` on `AppsRgIngressPayload`
- **Reason:** canonical live build proof (`python -m apps_qna build --interview default`) could not run otherwise (`parse_payload` returned `None`)
- **Non-claim:** no broader profile-builder refactor

## COMMANDS_RUN

| Command | Exit | Result |
|---------|------|--------|
| `test -f apps_qna/qna_capability_registry.py` | 1 | File absent (expected) |
| `test -f apps_qna/live_interview_runtime.py` | 1 | File absent (expected) |
| `rg "qna_capability_registry\|live_interview_runtime" apps_qna tests ops_scripts -g "*.py"` | 0 | See [REMAINING_REFERENCES](#remaining-references) |
| `git status --short` Tier A/B paths | 0 | Four `D` entries |
| `python -m pytest tests/_apps_contract/test_w1_qna_spine_migration.py tests/apps_qna/governance/ -q -o addopts=` | 0 | 63 passed |
| `python -m apps_qna build --interview default` | 0 | Live spine (AppIngressRunner) |
| `python -c "import apps_qna.live_interview_runtime"` | 1 | `ModuleNotFoundError` (expected) |
| `git diff -- apps_qna/router apps_qna/builder apps_qna/cert/fec_producer.py` | 0 | Empty |

## REMAINING_REFERENCES

| Location | Pattern | Classification |
|----------|---------|----------------|
| [l0_router.py](../../apps_qna/l0_router.py) | `live_interview_runtime_pack_v1` route IDs | **STABLE_ROUTE_ID** |
| [router/two_tier_router.py](../../apps_qna/router/two_tier_router.py) | route map keys (protected; unchanged) | **STABLE_ROUTE_ID** |
| [test_acceptance.py](../../tests/apps_qna/test_acceptance.py), [test_w0_thin_slice.py](../../tests/apps_qna/test_w0_thin_slice.py) | `route_id=...pack_v1` | **STABLE_ROUTE_ID** |
| [test_w1_qna_spine_migration.py](../../tests/_apps_contract/test_w1_qna_spine_migration.py) | forbidden-import asserts, section comments | **NEGATIVE_CONTROL_TEST** / **HISTORICAL_DOC_ONLY** |
| [test_apps_qna_entrypoint.py](../../tests/apps_qna/governance/test_apps_qna_entrypoint.py) | assert no shadow import in `__main__` | **NEGATIVE_CONTROL_TEST** |

**Not present:** `qna_capability_registry` in any `apps_qna` / `tests` / `ops_scripts` `*.py`.

## CANONICAL_RUNTIME_PROOF

- `python -m apps_qna build --interview default` → exit 0
- `import apps_qna.live_interview_runtime` → `ModuleNotFoundError`
- `source_channel` on intake path → `apps_qna.app_ingress_runner`

## PROOF_CLASSIFICATION

| Class | Claim |
|-------|-------|
| **CONTRACT_TEST_PROOF** | Yes — 63 pytest |
| **LIVE_RUNTIME_PROOF** | Yes — `python -m apps_qna build --interview default` |
| **CERT_RECEIPT_PROOF** | Not claimed (`--apps-e2e-live` not re-run; not misrepresented as runtime proof) |
| MOCK / STUB / DISPATCH / GREP / DOCS proof | **Not claimed** |

## PROTECTED_PATH_PROOF

`git diff -- apps_qna/router apps_qna/builder apps_qna/cert/fec_producer.py` → **empty**.

`agentic_core/**` may show **pre-existing unstaged** diffs from other sessions — not part of this wave.

## NON_CLAIMS

- No production certification beyond shadow-spine deletion.
- No taxonomy cleanup (Tier C `check_apps_folder_taxonomy` flags unchanged).
- No stub/fail-soft provider runtime certification.
- No ADR-082 migration.
- No broader `profile_builder` refactor (incidental kwarg fix only).
