# Testing Accelerators

Testing accelerators for ADG-based test optimization.

## Files

- **adg_test_accelerator.py**: Main testing accelerator (symlink to ../../adg_test_accelerator.py)
  - `gap`: Gap analysis - rank uncovered production modules by fan-in
  - `scope`: Scoped selection - emit test files covering changed files
  - `groups`: Parallel groups - partition tests for pytest-xdist
  - `report`: Full JSON report combining all analyses
  - `collection-safety`: Import safety analysis via ADG graph

- **adg_test_selector.py**: Smart test selection (symlink to ../../adg/adg_test_selector.py)
  - Selects tests based on ADG dependency graph
  - `--from-diff` mode for CI integration

## Usage

```bash
# Via unified CLI
python -m tools.adg.accelerators testing gap --top 20 --layer L5
python -m tools.adg.accelerators testing scope --changed agentic_core/L0_routing/config/path_constants.py
python -m tools.adg.accelerators testing groups --workers 4
python -m tools.adg.accelerators testing collection-safety --json out.json

# Direct usage
python tools/adg_test_accelerator.py gap --top 20
python tools/adg/adg_test_selector.py --from-diff
```

## Integration

CI workflow: `.github/workflows/adg-accelerators-ci.yml`
- Job: `testing-collection-safety`
- Job: `testing-gap-analysis`
- Job: `testing-scope`
