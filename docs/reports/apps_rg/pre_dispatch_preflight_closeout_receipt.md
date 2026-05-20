# Pre-dispatch fail-closed closeout — `python -m apps_rg`

## STATUS: PASS

## SCOPE_MATCH

Mandatory pre-dispatch gates on canonical `python -m apps_rg --section <lane>` for all seven section lanes: targeting inputs (JD + manual briefing) and Qwen/vLLM readiness before lane runtime or `canonical_dispatch`.

## FILES_CHANGED

- [pre_dispatch_preflight.py](apps_rg/runtime/pre_dispatch_preflight.py) — SSOT evaluator + receipt writer
- [__main__.py](apps_rg/__main__.py) — wire gates for every section lane; dry-run after preflight
- [test_apps_rg_pre_dispatch_preflight.py](tests/_apps_contract/test_apps_rg_pre_dispatch_preflight.py)
- [test_pre_dispatch_preflight.py](tests/unit/apps_rg/test_pre_dispatch_preflight.py)
- [test_apps_rg_section_cli_preflight.py](tests/_apps_contract/test_apps_rg_section_cli_preflight.py) — fresh fixture paths for vLLM test

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `pytest tests/_apps_contract/test_apps_rg_pre_dispatch_preflight.py tests/unit/apps_rg/test_pre_dispatch_preflight.py tests/_apps_contract/test_apps_rg_section_cli_preflight.py -o addopts= -q` | 0 |
| Stale default JD CLI negative (`headline`, default_jd + ci-probe brief) | 2 |
| Stale default briefing CLI negative | 2 |
| Qwen unreachable (`VLLM_BASE_URL=http://127.0.0.1:9/`, stub disabled) | 2 |
| Fresh fixtures + stub + `--dry-run` | 0 |

## TESTS_GATES

- 23 targeted pytest cases — **PASS**

## NEGATIVE_CONTROLS

- **Stale JD** — `jd_status=DEFAULT_BLOCKED`, `dispatch_started=false`, receipt [pre_dispatch_headline_20260520_085437.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085437.json)
- **Stale briefing** — `manual_brief_status=DEFAULT_BLOCKED`, receipt [pre_dispatch_headline_20260520_085438.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085438.json)
- **Qwen down** — exit 2 before dispatch; no lane artifacts
- **No silent mock fallback** — default provider resolution remains `qwen_vllm` / `DEV_DEFAULT_QWEN_VLLM`; `--provider mock` rejected

## POSITIVE_CONTROL

- Fresh [ci-probe-jd.txt](tests/_fixtures/ci-probe-jd.txt) + [ci-probe-briefing.txt](tests/_fixtures/ci-probe-briefing.txt), stub on, `--dry-run` → exit 0, `dispatch_started=true` in [pre_dispatch_headline_20260520_085441.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085441.json)

## ARTIFACTS_WRITTEN

- [pre_dispatch_headline_20260520_085437.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085437.json)
- [pre_dispatch_headline_20260520_085438.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085438.json)
- [pre_dispatch_headline_20260520_085441.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_headline_20260520_085441.json)
- [pre_dispatch_preflight_closeout_receipt.json](docs/reports/apps_rg/pre_dispatch_preflight_closeout_receipt.json)

## PROOF_CLASSIFICATION

Contract + canonical CLI preflight (not smoke/dispatch-only shim).

## EXPLICIT_NON_CLAIMS

- No live REAL_LLM proof run with healthy Docker Qwen in this session (positive path used `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1` + `--dry-run`).
- Full R4 run without `--section` is out of scope.
- R1A/R1B whole-run cache preflight unchanged.

## FORBIDDEN_FILES_TOUCHED

| Area | Touched |
|------|---------|
| agentic_core | **no** (no files in this task diff) |
| unrelated section prompts | **no** |
| unrelated dispatch/smoke paths | **no** |

## NEXT_BLOCKER

None for scoped pre-dispatch gates.
