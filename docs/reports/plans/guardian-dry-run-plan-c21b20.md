# Guardian Scripts Dry Run Plan

Perform a comprehensive dry run of all guardian scripts in the tests/guardian directory and generate a detailed report of findings without making any code changes.

## Scope

1. **Guardian Test Discovery**: Identify all test files in tests/guardian/ directory
2. **Script Execution**: Run guardian tests in dry-run mode to collect results
3. **Registry Analysis**: Execute the main guardian aggregator script
4. **Report Generation**: Create comprehensive findings report

## Execution Steps

### Phase 1: Discovery and Inventory
- List all guardian test files and their purposes
- Review guardian registry configuration
- Identify available guardian runner scripts

### Phase 2: Dry Run Execution
- Run pytest on tests/guardian/ directory in collection mode only
- Execute the main guardian aggregator (run_all_guardians.py) with --dry-run flag if available
- Capture all outputs, errors, and warnings

### Phase 3: Analysis and Reporting
- Analyze test collection results
- Document any import errors or missing dependencies
- Summarize guardian coverage and capabilities
- Generate comprehensive report with findings

## Expected Deliverables

- Inventory of all guardian tests and scripts
- Execution results (success/failure status for each)
- Analysis of any issues or blockers
- Recommendations for improvements

## Constraints

- No code modifications will be made
- Read-only execution only
- Report will be saved to docs/reports/plans/ as per constitutional rules
