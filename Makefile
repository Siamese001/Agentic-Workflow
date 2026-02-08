# Makefile for Agentic-Workflow test targets
# ============================================

.PHONY: test-unit-min-deps test-integration help

help:
	@echo "Available targets:"
	@echo "  test-unit-min-deps    Run unit tests that require no optional deps (pydantic/redis/requests)"
	@echo "  test-integration      Run integration tests (requires pydantic redis requests)"
	@echo "  test-decorators       Run decorator enforcement tests only"

# Run unit_min_deps tests (no optional deps required)
# These tests are AST-based and import-safe
test-unit-min-deps:
	python -m pytest tests/unit/agentic_core/base_agents/test_decorator_shim_contract.py \
		tests/unit/agentic_core/mixins/test_inspection_capability_structure.py \
		tests/unit/agentic_core/mixins/test_inspection_policy_governance.py \
		-m unit_min_deps -q

# Run decorator enforcement tests only
test-decorators:
	python -m pytest tests/unit/agentic_core/base_agents/test_decorator_shim_contract.py -v

# Run integration tests (requires: pip install pydantic redis requests)
# If deps are missing, tests will FAIL with clear message (not skip)
test-integration:
	INTEGRATION_FULL_DEPS_REQUIRED=1 python -m pytest tests/integration/agentic_core/test_inspector_agents_runtime.py \
		-m integration_full_deps -v

# Install integration test dependencies
install-integration-deps:
	pip install pydantic redis requests
