# Parallel Phase-1 orchestration — closeout (W3–W4)

**Plan:** [apps-rg-parallel-section-orchestration-f2a8c4](../../.cursor/plans/apps-rg-parallel-section-orchestration-f2a8c4.md)

## Shipped (W3 wiring)

- `phase1_lane_inventory.json` receives parallel metadata when env/profile enables parallel mode.
- Opt-in: `APPS_RG_PARALLEL_PHASE1_LANES=1`, cap `APPS_RG_PHASE1_MAX_PARALLEL` (default 2).
- Unit proof: [test_phase1_parallel_dispatcher.py](../../tests/unit/apps_rg/test_phase1_parallel_dispatcher.py)

## Live whole-run smoke (W4)

**STATUS: BLOCKED** — requires live `qwen_vllm` + GPU; same constraint as `test_exec_summary_cli.py` (offline stub forbidden).

**Next command when provider available:**

```bash
set APPS_RG_PARALLEL_PHASE1_LANES=1
set APPS_RG_PHASE1_MAX_PARALLEL=2
python -m apps_rg --whole-run ...
```

Default product path remains **serial** (no env flag).
