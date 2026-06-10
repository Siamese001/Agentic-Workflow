# Eval Harness W2 Whole-Spine Replay

Plan: `eval-harness-adg-mcp-open-replan-9c1f2a`  
Wave: `W2`  
Implementation worktree: `C:\Git\eval-harness`  
Branch: `eval-harness`  
Result: `DONE_WITH_W1_MCP_CAVEAT`

## Scope

W2 implemented the first whole-spine replay harness surface without editing `agentic_core`.

Files added in the eval worktree:

- `tools/eval/whole_spine_replay.py`
- `tests/unit/tools/eval/test_whole_spine_replay.py`

Core Author-Gate was not consumed because W2 stayed in eval tooling and tests only. The plan-level Author-Gate requirement still applies before any future `agentic_core` contract change.

## W2.1 Schema

Scenario JSON now supports pinned replay identity:

- `scenario_id`
- `provider_mode`
- `expected_receipt_class`
- `inputs.jd`
- `inputs.briefing`
- `inputs.policies[]`
- `command[]`
- `runtime_receipt_path`
- optional `cwd`

The runner hashes JD, briefing, every policy file, and the canonical input bundle with SHA-256.

Receipt schema: `whole_spine_replay_receipt.v1`.

Key receipt fields:

- scenario and provider identity
- expected and actual runtime receipt class
- input bundle SHA-256
- executed command and cwd
- command exit code and duration
- runtime receipt path, presence, and SHA-256
- stdout/stderr SHA-256
- reason codes
- baseline comparison result

## W2.2 Runner

`tools/eval/whole_spine_replay.py` executes the scenario command with `subprocess.run(..., shell=False)`.

The command is the runtime-spine seam. The harness does not reclassify stored labels or grade stale outcomes. A passing replay requires:

- command exit code `0`
- runtime receipt file exists
- runtime receipt JSON is an object
- runtime receipt class matches `expected_receipt_class`
- runtime receipt `provider_mode`, when present, matches the scenario provider mode

## W2.3 Baseline Gate

The optional `--baseline` JSON file compares candidate output against frozen scenario expectations. A mismatch in configured fields returns `BASELINE_REGRESSION` and causes a failed replay even if the absolute command result otherwise passes.

Supported compared fields:

- `input_bundle_sha256`
- `runtime_receipt_class`
- `runtime_receipt_sha256`
- `provider_mode`
- `expected_receipt_class`

## Verification

Commands run from `C:\Git\eval-harness`:

- `python -m pytest -p pytest_timeout tests/unit/tools/eval/test_whole_spine_replay.py -q`
  - Result: `3 passed`
- `python -m py_compile tools/eval/run_capability_regression.py tools/eval/whole_spine_replay.py`
  - Result: passed
- `python tools/eval/whole_spine_replay.py --help`
  - Result: passed

## Residual Caveat

W1 remains blocked for direct Codex ADG MCP calls: `mcp__adg_sqlite.adg_health` still returns `Transport closed`. W2 did not require ADG MCP to implement the eval-side runner, but promotion binding in later waves must continue to treat the missing direct MCP transport as unresolved.
