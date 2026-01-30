#!/bin/bash
# =============================================================================
# Guardian Runner - Zero-Trust Architectural Health Check
# =============================================================================
# This script runs ONLY the guardian tests and fails with exit code 1 if ANY
# structural violation is found.
#
# USAGE:
#   ./run_guardian.sh           # Run all guardian tests
#   ./run_guardian.sh --verbose # Run with verbose output
#   ./run_guardian.sh --quick   # Run only critical tests
#
# EXIT CODES:
#   0 - All guardian tests passed
#   1 - Structural violations detected
#   2 - Test execution error
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GUARDIAN_DIR="tests/guardian"
REPORT_FILE="guardian_report.txt"
VERBOSE=false
QUICK=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --quick|-q)
            QUICK=true
            shift
            ;;
        --help|-h)
            echo "Guardian Runner - Zero-Trust Architectural Health Check"
            echo ""
            echo "Usage: ./run_guardian.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Run with verbose output"
            echo "  --quick, -q      Run only critical tests"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 2
            ;;
    esac
done

# Header
echo "========================================"
echo -e "${BLUE}GUARDIAN LAYER - ZERO-TRUST ARCHITECTURE${NC}"
echo "========================================"
echo ""
echo "Starting architectural health check..."
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check if guardian directory exists
if [ ! -d "$GUARDIAN_DIR" ]; then
    echo -e "${RED}ERROR: Guardian directory not found: $GUARDIAN_DIR${NC}"
    exit 2
fi

# Build pytest command
PYTEST_CMD="python -m pytest $GUARDIAN_DIR -m guardian"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v --tb=long"
else
    PYTEST_CMD="$PYTEST_CMD --tb=short"
fi

if [ "$QUICK" = true ]; then
    # Quick mode: only run critical tests
    PYTEST_CMD="$PYTEST_CMD -k 'constitutional or forbidden or diamond'"
fi

# Add output capture
PYTEST_CMD="$PYTEST_CMD --capture=no"

echo "Running: $PYTEST_CMD"
echo ""
echo "========================================"
echo -e "${YELLOW}PHASE 1: MRO & Inheritance Hardening${NC}"
echo "========================================"

# Run the tests and capture exit code
set +e
$PYTEST_CMD 2>&1 | tee guardian_temp_output.txt
PYTEST_EXIT_CODE=${PIPESTATUS[0]}
set -e

# Generate summary
echo ""
echo "========================================"
echo -e "${BLUE}GUARDIAN STATUS SUMMARY${NC}"
echo "========================================"

# Count results from output
PASSED=$(grep -c "PASSED\|passed" guardian_temp_output.txt 2>/dev/null || echo "0")
FAILED=$(grep -c "FAILED\|failed" guardian_temp_output.txt 2>/dev/null || echo "0")
ERRORS=$(grep -c "ERROR\|error" guardian_temp_output.txt 2>/dev/null || echo "0")
WARNINGS=$(grep -c "TECH DEBT\|WARNING" guardian_temp_output.txt 2>/dev/null || echo "0")

echo ""
echo "Test Results:"
echo "  Passed:   $PASSED"
echo "  Failed:   $FAILED"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS (Tech Debt)"
echo ""

# Generate violations table
echo "========================================"
echo "VIOLATIONS FOUND"
echo "========================================"

# Extract violation categories
MRO_VIOLATIONS=$(grep -c "MRO\|Diamond\|Mixin" guardian_temp_output.txt 2>/dev/null || echo "0")
IMPORT_VIOLATIONS=$(grep -c "Import\|Ghost\|Circular" guardian_temp_output.txt 2>/dev/null || echo "0")
SSOT_VIOLATIONS=$(grep -c "SSOT\|Blueprint\|Orphan" guardian_temp_output.txt 2>/dev/null || echo "0")
NAMING_VIOLATIONS=$(grep -c "Naming\|Convention" guardian_temp_output.txt 2>/dev/null || echo "0")
SUBATOMIC_VIOLATIONS=$(grep -c "Subatomic\|STRUCTURAL DEBT" guardian_temp_output.txt 2>/dev/null || echo "0")

printf "| %-25s | %-10s |\n" "Category" "Count"
printf "|%-27s|%-12s|\n" "---------------------------" "------------"
printf "| %-25s | %-10s |\n" "MRO & Inheritance" "$MRO_VIOLATIONS"
printf "| %-25s | %-10s |\n" "Import Safety" "$IMPORT_VIOLATIONS"
printf "| %-25s | %-10s |\n" "SSOT Alignment" "$SSOT_VIOLATIONS"
printf "| %-25s | %-10s |\n" "Naming Conventions" "$NAMING_VIOLATIONS"
printf "| %-25s | %-10s |\n" "Subatomic Compliance" "$SUBATOMIC_VIOLATIONS"
echo ""

# Final status
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================"
    echo "GUARDIAN STATUS: ✅ PASS"
    echo "========================================${NC}"
    echo ""
    echo "All architectural integrity checks passed!"
    echo "The codebase maintains structural integrity."
else
    echo -e "${RED}========================================"
    echo "GUARDIAN STATUS: ❌ FAIL"
    echo "========================================${NC}"
    echo ""
    echo "Architectural violations detected!"
    echo "Please review the output above and remediate issues."
    echo ""
    echo "Recommended Actions:"
    echo "  1. Review failed tests in detail"
    echo "  2. Check TECH DEBT items for known issues"
    echo "  3. Fix critical violations before merging"
fi

# Save report
{
    echo "GUARDIAN ARCHITECTURAL HEALTH REPORT"
    echo "====================================="
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Exit Status: $PYTEST_EXIT_CODE"
    echo ""
    echo "SUMMARY:"
    echo "  Passed: $PASSED"
    echo "  Failed: $FAILED"
    echo "  Errors: $ERRORS"
    echo "  Warnings: $WARNINGS"
    echo ""
    echo "VIOLATIONS BY CATEGORY:"
    echo "  MRO & Inheritance: $MRO_VIOLATIONS"
    echo "  Import Safety: $IMPORT_VIOLATIONS"
    echo "  SSOT Alignment: $SSOT_VIOLATIONS"
    echo "  Naming Conventions: $NAMING_VIOLATIONS"
    echo "  Subatomic Compliance: $SUBATOMIC_VIOLATIONS"
    echo ""
    echo "DETAILED OUTPUT:"
    echo "----------------"
    cat guardian_temp_output.txt
} > "$REPORT_FILE"

echo ""
echo "Report saved to: $REPORT_FILE"
echo "========================================"

# Cleanup
rm -f guardian_temp_output.txt

# Exit with pytest exit code
exit $PYTEST_EXIT_CODE
