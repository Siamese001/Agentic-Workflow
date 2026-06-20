# ADG three-bucket weekly audit runbook (ADR-079)

**Purpose:** Keep daily ADG regen fast while still measuring static/runtime/registry alignment on a controlled cadence.

## Daily (default hot path)

```bash
python -m tools.generate.generate_full_adg
```

Expect log line `three_bucket=OFF`. This path does **not** refresh `THREE_BUCKET_GAP_REPORT.json`.

## Weekly or pre-release (opt-in audit)

```bash
python tools/otel/seed_synthetic_traces.py --prefer-registry-overlap
ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py
python ops_scripts/ci/check_three_bucket_gap_thresholds.py
```

On Windows, registry lift uses [safe_repo_scan.py](tools/adg/safe_repo_scan.py) (patched into consumer resolvers) so junction dirs like `.venv/lib64` do not abort the walk.

## CI certification (`adg-ci-gates.yml`)

`python tools/adg/run_full_adg_audit.py --mode certification` sets `ADG_CERTIFICATION_MODE=1`, `ADG_THREE_BUCKET=1`, and `ADG_THREE_BUCKET_SIGN=1` for Stage-1 only. Default developer regen (`python -m tools.generate.generate_full_adg`) remains `three_bucket=OFF`.

Or regen + audit in one invocation:

```bash
python -m tools.generate.generate_full_adg --three-bucket
```

## Stale report guard

Gap JSON and CI gate stdout include:

- `source_snapshot_sha256` — digest of the sqlite audited
- `generated_at` — report timestamp
- `READ_EXISTING_REPORT` — gate line tying threshold check to report identity

Re-run audit after every snapshot regen you intend to certify against.

## What this is not

- Not a substitute for full ADG release certification
- Not `ADG_CERTIFIED` strict mode
- Not mandatory on every `generate_full_adg` run

See [ADR-079](../architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md) and plan [adg-three-bucket-pipeline-redesign-c8e4f1.md](../../.codex/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md).
