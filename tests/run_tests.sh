#!/bin/bash
# Task: T5.4.2, T5.4.3 - Test Runner Script
# Spec Reference: phase5-spec.md Section 8 (Timeline & Task Breakdown)
# Constitution: constitution.md v5.0 Section 10 (Validation Criteria)
#
# Comprehensive test runner for Phase 5 integration and E2E tests.
# Runs all tests with proper configuration and generates reports.
#
# Version: 1.0
# Date: 2026-02-15

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$TEST_DIR")"
REPORT_DIR="$TEST_DIR/reports"
COVERAGE_DIR="$TEST_DIR/coverage"

# Create report directories
mkdir -p "$REPORT_DIR"
mkdir -p "$COVERAGE_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 5 Test Suite Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${YELLOW}>>> $1${NC}"
    echo ""
}

# Function to check service health
check_service() {
    local service_name=$1
    local health_url=$2

    echo -n "Checking $service_name... "
    if curl -s -f "$health_url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Not available${NC}"
        return 1
    fi
}

# Check prerequisites
print_section "Checking Prerequisites"

SERVICES_OK=true

check_service "Backend API" "http://localhost:8000/health" || SERVICES_OK=false
check_service "Reminder Worker" "http://localhost:5001/health" || SERVICES_OK=false
check_service "Dapr Sidecar" "http://localhost:3500/v1.0/healthz" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo ""
    echo -e "${RED}ERROR: Required services are not running!${NC}"
    echo "Please start all services before running tests:"
    echo "  - Backend API (port 8000)"
    echo "  - Reminder Worker (port 5001)"
    echo "  - Dapr Sidecar (port 3500)"
    echo "  - Frontend (port 3000) - for E2E tests"
    exit 1
fi

echo ""
echo -e "${GREEN}All services are healthy!${NC}"

# Parse command line arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

# Run tests based on type
case "$TEST_TYPE" in
    integration)
        print_section "Running Integration Tests Only"
        pytest "$TEST_DIR/integration" \
            -v \
            --tb=short \
            --html="$REPORT_DIR/integration-report.html" \
            --self-contained-html \
            --cov="$PROJECT_ROOT/agents/backend" \
            --cov-report=html:"$COVERAGE_DIR/integration" \
            --cov-report=term-missing \
            --junit-xml="$REPORT_DIR/integration-junit.xml" \
            $VERBOSE
        ;;

    e2e)
        print_section "Running E2E Tests Only"

        # Check if frontend is running
        check_service "Frontend" "http://localhost:3000" || {
            echo -e "${RED}ERROR: Frontend is not running on port 3000${NC}"
            exit 1
        }

        pytest "$TEST_DIR/e2e" \
            -v \
            --tb=short \
            --html="$REPORT_DIR/e2e-report.html" \
            --self-contained-html \
            --headed \
            --slowmo=100 \
            --video=retain-on-failure \
            --screenshot=only-on-failure \
            --junit-xml="$REPORT_DIR/e2e-junit.xml" \
            $VERBOSE
        ;;

    kafka)
        print_section "Running Kafka/Dapr Pub/Sub Tests"
        pytest "$TEST_DIR/integration/test_kafka_dapr_pubsub.py" \
            -v \
            --tb=short \
            --html="$REPORT_DIR/kafka-report.html" \
            --self-contained-html \
            $VERBOSE
        ;;

    jobs)
        print_section "Running Dapr Jobs API Tests"
        pytest "$TEST_DIR/integration/test_dapr_jobs_api.py" \
            -v \
            --tb=short \
            --html="$REPORT_DIR/jobs-report.html" \
            --self-contained-html \
            $VERBOSE
        ;;

    state)
        print_section "Running Dapr State Store Tests"
        pytest "$TEST_DIR/integration/test_dapr_state_store.py" \
            -v \
            --tb=short \
            --html="$REPORT_DIR/state-report.html" \
            --self-contained-html \
            $VERBOSE
        ;;

    smoke)
        print_section "Running Smoke Tests (Quick Validation)"
        pytest "$TEST_DIR" \
            -v \
            -m "not slow" \
            --tb=short \
            --maxfail=3 \
            $VERBOSE
        ;;

    all)
        print_section "Running All Tests (Integration + E2E)"

        # Check if frontend is running for E2E tests
        if ! check_service "Frontend" "http://localhost:3000"; then
            echo -e "${YELLOW}WARNING: Frontend not running, skipping E2E tests${NC}"
            TEST_DIRS="$TEST_DIR/integration"
        else
            TEST_DIRS="$TEST_DIR/integration $TEST_DIR/e2e"
        fi

        pytest $TEST_DIRS \
            -v \
            --tb=short \
            --html="$REPORT_DIR/full-report.html" \
            --self-contained-html \
            --cov="$PROJECT_ROOT/agents/backend" \
            --cov-report=html:"$COVERAGE_DIR/full" \
            --cov-report=term-missing \
            --junit-xml="$REPORT_DIR/full-junit.xml" \
            $VERBOSE
        ;;

    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [test_type] [verbose]"
        echo ""
        echo "Test types:"
        echo "  all          - Run all tests (default)"
        echo "  integration  - Run integration tests only"
        echo "  e2e          - Run E2E tests only"
        echo "  kafka        - Run Kafka/Dapr Pub/Sub tests"
        echo "  jobs         - Run Dapr Jobs API tests"
        echo "  state        - Run Dapr State Store tests"
        echo "  smoke        - Run quick smoke tests"
        echo ""
        echo "Verbose flag:"
        echo "  -vv          - Very verbose output"
        echo "  -s           - Show print statements"
        echo ""
        exit 1
        ;;
esac

# Check test results
TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}========================================${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed!${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo ""

# Display report locations
print_section "Test Reports Generated"
echo "HTML Report:     $REPORT_DIR/"
echo "Coverage Report: $COVERAGE_DIR/"
echo "JUnit XML:       $REPORT_DIR/"
echo ""

# Open HTML report in browser (optional)
if command -v xdg-open > /dev/null 2>&1; then
    echo "Opening HTML report in browser..."
    xdg-open "$REPORT_DIR/${TEST_TYPE}-report.html" 2>/dev/null || true
elif command -v open > /dev/null 2>&1; then
    echo "Opening HTML report in browser..."
    open "$REPORT_DIR/${TEST_TYPE}-report.html" 2>/dev/null || true
fi

exit $TEST_EXIT_CODE
