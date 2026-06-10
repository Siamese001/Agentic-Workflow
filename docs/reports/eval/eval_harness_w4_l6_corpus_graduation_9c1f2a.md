# Eval Harness W4 L6 Corpus Graduation

Plan: `eval-harness-adg-mcp-open-replan-9c1f2a`  
Wave: `W4`  
Implementation worktree: `C:\Git\eval-harness`  
Branch: `eval-harness`  
Result: `DONE_WITH_W1_MCP_CAVEAT`

## Scope

W4 added an eval-side L6 exhaust-to-corpus graduation contract without editing `agentic_core`.

Files added in the eval worktree:

- `tools/eval/l6_corpus_graduation.py`
- `data/eval/l6_corpus/known_failure_seeds.json`
- `tests/unit/tools/eval/test_l6_corpus_graduation.py`

Core Author-Gate was not consumed because W4 stayed in eval tooling, fixtures, and tests only. The plan-level Author-Gate requirement still applies before any future `agentic_core` contract change.

## W4.1 Staged Candidates

`tools/eval/l6_corpus_graduation.py stage` converts an L6 runtime exhaust package into staged corpus candidates only when the package includes:

- `trace_refs`
- `gate_refs`
- `judge_refs`
- `exit_disposition_ref`
- `created_after_exit=true`
- `current_run_closed=true`
- `no_l6_current_run_mutation_assertion=true`
- no claim that L6 can change X3 or Exit disposition

Candidates without a scenario seed or failure family are blocked.

## W4.2 Review And Graduation

The tool creates blind review packets that exclude judge scores, provider identity, and runtime verdict override fields.

Graduation requires:

- candidate status `STAGED`
- required reviewer approval quorum
- deterministic replay receipt with `passed=true`
- no baseline regression
- replay scenario ID matching the staged scenario seed

No direct auto-promotion path was added.

## W4.3 Known Failure Seeds

`data/eval/l6_corpus/known_failure_seeds.json` seeds three known failure families:

- token truncation
- zero judge rows
- decimal false-positive / `99.99` handling

These are staged as scenario seeds, not golden corpus rows. They still require review and replay before graduation.

## Verification

Commands run from `C:\Git\eval-harness`:

- `python -m pytest -p pytest_timeout tests/unit/tools/eval/test_l6_corpus_graduation.py -q`
  - Result: `7 passed`
- `python -m py_compile tools/eval/l6_corpus_graduation.py`
  - Result: passed
- `python tools/eval/l6_corpus_graduation.py stage --exhaust <temp-exhaust.json>`
  - Result: passed; emitted a staged `decimal_false_positive` candidate

## Residual Caveat

W1 remains blocked for direct Codex ADG MCP calls. W4 did not require ADG MCP to implement the eval-side graduation contract, but W5 promotion binding must continue to treat direct ADG MCP transport as unresolved.
