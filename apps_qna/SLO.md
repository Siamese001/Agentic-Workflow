# apps_qna — SLO

`apps_qna` is an **offline builder + linter**. It has no runtime SLO in the
operational sense (no live traffic, no agent dispatch, no user-facing
latency).

The relevant service-level objectives are **build-time**:

| Metric | Target | Verification |
|---|---|---|
| Build time for an 18-card pack | < 5 seconds | `time python -m apps_qna --interview drew-clements ...` |
| Linter run on an 18-card pack | < 2 seconds | `time python -m apps_qna lint <pack>` |
| Memory ceiling | < 200 MB RSS | resource module assertion in test |
| Template render success rate | 100% under StrictUndefined for all valid inputs | `pytest apps_qna/tests/test_templates_render.py` |
| Linter false-positive rate | 0 on the valid_pack fixture | `pytest apps_qna/tests/test_validators.py::test_valid_pack_passes` |
| Linter false-negative rate | 0 on the 6 invalid_packs fixtures | `pytest apps_qna/tests/test_validators.py::test_invalid_packs_fail` |

## Determinism

Same inputs → byte-identical outputs (modulo `built_at` timestamp in the
manifest).

This is enforced by:

- All randomness banned. No `uuid4`, no `random`, no `datetime.now()` in
  template rendering. Only the `BuildMetadata.built_at` is allowed a real
  timestamp, and it is recorded in the manifest, not in any card.
- Jinja2 `keep_trailing_newline=True` and `lstrip_blocks=True` lock layout.
- File I/O uses LF line endings explicitly (no platform-default behavior).

## Failure modes and recovery

| Failure | Detection | Recovery |
|---|---|---|
| Missing required input field | pydantic ValidationError at config load | Fix YAML, re-run |
| Template references undefined variable | `jinja2.UndefinedError` | Fix template OR add field to types/Interview |
| Linter reports invariant violation | exit code 1 | Fix templates or route_registry.yaml |
| Output dir already populated | `FileExistsError` unless `--force` | `--force` to overwrite |

## Out of scope

- No queue, no worker pool, no concurrency.
- No retries — failures surface immediately, are deterministic.
- No telemetry — this module emits no spans, no metrics, no logs beyond
  stdlib `logging` to stderr.
