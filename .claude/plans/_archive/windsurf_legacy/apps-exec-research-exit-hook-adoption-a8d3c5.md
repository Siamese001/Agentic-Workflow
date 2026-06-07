# apps_exec + apps_research Exit-Hook Adoption

**Slug:** `apps-exec-research-exit-hook-adoption-a8d3c5`
**Created:** 2026-05-03
**Status:** Completed
**Completed:** 2026-05-03
**Owner:** Cursor Agent
**Pattern source:** `.windsurf/plans/apps-rfp-c0-fec-producer-wiring-b9d4f1.md` (Completed) — apps_rfp carries the canonical `_build_exit_receipts` + `maybe_invoke_exit_eval` + cert_route_registry.yaml shape to copy.
**Parent plans:**
- `.windsurf/plans/apps-exec-c0-fec-producer-wiring-c2e8a5.md` (Completed)
- `.windsurf/plans/apps-research-c0-fec-producer-wiring-e7a2c3.md` (Completed)

## 1. Problem Statement

apps_exec and apps_research now have real FEC producers registered (plans above, Completed 2026-05-03). Their `__main__.py` cert paths compute FEC via `resolve_fec("apps_<name>", run_ctx)` but **neither app invokes `maybe_invoke_exit_eval`** — the v6 Exit pipeline does not execute on their cert runs, so the app-specific rubric never scores.

Without exit-hook adoption, the FEC producer is computed-and-discarded. This plan wires the hook so FEC flows end-to-end into Exit-rubric scoring, matching apps_qna / apps_rfp / apps_underwriting_ai.

## 2. Goals

For **each** of apps_exec and apps_research:

- `config/cert_route_registry.yaml` — route entry with `invoke_exit_eval: true` + `rubric_output_map` (copy apps_rfp shape).
- `__main__.py` — load cert route entry via `_load_cert_route_entry(registry_path)` helper; build receipts via `_build_exit_receipts(cert_route_entry)` that calls `resolve_fec` into `final_evidence_contract`; call `maybe_invoke_exit_eval(receipts, cert_route_entry)` before exiting `governed_run`.
- `EmissionConfig.route_registry_path` updated if not already pointing at `cert_route_registry.yaml`.
- 5+ contract tests per app covering: cert-route entry load, receipts shape with populated FEC, Exit hook invocation path, fail-soft on missing rubric map, fail-soft on registry parse error.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Rewriting app engines (no changes to `engines/`, `integrations/`).
- New rubric dims.
- Calibration of any LLM judge.
- Changes to the 3 apps that already adopted the hook.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | apps_exec exit-hook adoption | ~8k | ✅ Done | 7 tests pass; 430/430 suite green |
| W2 | W2.P1–W2.P3 | apps_research exit-hook adoption | ~8k | ✅ Done | 7 tests pass; 430/430 suite green |

## Verification Evidence

- Both apps had exit-hook scaffolding (`_load_cert_route_entry`, `_build_exit_receipts(entry, fec)`, `_maybe_run_exit_hook(fec)`) already in place from `apps-runtime-domain-enforcement-a7e9d4`; this plan wired FEC resolution + hook invocation into `_run_live_cert`.
- `cert_route_registry.yaml` already present for both apps with `invoke_exit_eval: true` + valid `rubric_output_map_path`.
- W1.P2 + W2.P2: `_run_live_cert` now calls `resolve_fec(...)` fail-soft then `_maybe_run_exit_hook(_fec)` inside `governed_run`.
- W1.P3 + W2.P3: `tests/_apps_contract/test_apps_exec_exit_hook.py` (7 tests), `tests/_apps_contract/test_apps_research_exit_hook.py` (7 tests) — registry presence, invoke_exit_eval=true invariant, rubric_output_map on-disk check, FEC flow through `_build_exit_receipts`, None-FEC fail-soft, and `_maybe_run_exit_hook` no-raise on any input.
- Cross-test fix: `test_import_registers_producer` in apps_exec / apps_research FEC tests now uses `importlib.reload(apps_<name>.cert)` to force re-execution of `register_producer` side-effect — xdist + sibling `__main__.py` imports caused sys.modules cache races.
- Full `tests/_apps_contract/` suite: **430 passed, 0 regressions** (baseline 400 → +14 new exit-hook tests + 16 already landed from prior FEC plans; prior sum was 400).

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | apps_exec cert_route_registry | `apps_exec/config/cert_route_registry.yaml` (new or update) | Need rubric_output_map matching apps_exec eval_rubrics.yaml dim ids | 3k | ⏳ Todo |
| W1.P2 | apps_exec __main__.py hook wiring | `apps_exec/__main__.py` (edit) | Registry path in EmissionConfig may need update; governed_run exit-order semantics | 3k | ⏳ Todo |
| W1.P3 | apps_exec contract tests | `tests/_apps_contract/test_apps_exec_exit_hook.py` (new) | Receipts-shape fixture setup | 2k | ⏳ Todo |
| W2.P1 | apps_research cert_route_registry | `apps_research/config/cert_route_registry.yaml` (new or update) | research eval_rubrics has `context_recall` / `context_precision` / `answer_relevancy` tracked-only dims — copy apps_rfp zero-weight pattern | 3k | ⏳ Todo |
| W2.P2 | apps_research __main__.py hook wiring | `apps_research/__main__.py` (edit) | Same shape as apps_exec W1.P2 | 3k | ⏳ Todo |
| W2.P3 | apps_research contract tests | `tests/_apps_contract/test_apps_research_exit_hook.py` (new) | Hop citation attribute access in receipts mapper | 2k | ⏳ Todo |

## 6. Pattern Source (apps_rfp — canonical shape)

```python
# apps_rfp/__main__.py pattern to replicate:
cert_route_entry = _load_cert_route_entry(registry_path)
with governed_run(cfg, cli_args=argv) as gr:
    ...  # spans
    _maybe_run_exit_hook()  # builds receipts (FEC included), invokes hook
```

`_build_exit_receipts(cert_route_entry)` returns a dict with
`final_evidence_contract=_build_fec_for_receipts()` (calls `resolve_fec`).

## 7. Deliverables

- Exit hook invoked on cert runs for apps_exec + apps_research
- 5+ new tests per app covering hook plumbing and FEC flow-through
- `tests/_apps_contract/` remains green (target: 410+ tests passed)

## 8. Non-Goals Fence

- No rubric dim changes.
- No changes to FEC producer modules (already Completed).
- No changes to apps_qna / apps_rfp / apps_underwriting_ai hooks.

## 9. Governance

- Constitutional §6: deterministic pattern replication from apps_rfp.
- Fail-soft throughout: registry-load / receipt-build / hook-invoke failures must never break the cert bundle.
- §24 deferred-scope: captured via DEFERRED_SCOPE marker emitted 2026-05-03.
