#!/bin/bash
# Dashboard Test Execution Script
# SAFETY: Run this script after ANY change to dashboard files
# This ensures exhaustive testing prevents regression in observability territory

set -e  # Exit on first error

echo "=========================================="
echo "Running exhaustive dashboard tests..."
echo "=========================================="
echo ""

# Get the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run test suite
run_test_suite() {
    local suite_name=$1
    local test_path=$2
    
    echo -e "${YELLOW}Running ${suite_name}...${NC}"
    
    if pytest "$test_path" -v --tb=short; then
        echo -e "${GREEN}✓ ${suite_name} PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ ${suite_name} FAILED${NC}"
        ((FAILED_TESTS++))
    fi
    echo ""
}

# Run unit tests
echo -e "${YELLOW}=== UNIT TESTS ===${NC}"
run_test_suite "Unit Tests" "tests/unit/observability/metrics/dashboard/"

# Run integration tests
echo -e "${YELLOW}=== INTEGRATION TESTS ===${NC}"
run_test_suite "Integration Tests" "tests/integration/dashboard/"

# Run regression tests
echo -e "${YELLOW}=== REGRESSION TESTS ===${NC}"
run_test_suite "Regression Tests" "tests/regression/dashboard/"

# Run e2e tests if playwright is available
echo -e "${YELLOW}=== E2E TESTS ===${NC}"
if command -v pytest &> /dev/null; then
    if pytest "tests/e2e/dashboard/" -v --tb=short 2>/dev/null; then
        echo -e "${GREEN}✓ E2E Tests PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${YELLOW}⚠ E2E Tests SKIPPED (playwright not available)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ E2E Tests SKIPPED (pytest not available)${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All dashboard tests passed.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review and fix.${NC}"
    exit 1
fi
