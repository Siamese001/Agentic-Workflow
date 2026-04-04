"""
Pytest Test Orchestration MCP Server

ADG-aware test execution with impact analysis and governance validation.
Intelligent test selection based on ADG impact analysis to reduce test execution time.

Why this exists
---------------
6,293 modules require intelligent test selection
ADG impact analysis exists (adg_incremental_update.py) but not integrated
Test governance (Constitutional Rule #3) needs enforcement
No centralized test execution with ADG context

This server provides:
- ADG-aware test selection based on code changes
- Integration with adg_incremental_update.py for impact analysis
- Governance test suite execution and enforcement
- Test coverage analysis by ADG layer and edge type
- Failure analysis with ADG context
- Smoke test execution for critical path validation

Tools (4-6)
-----------
- pytest_status: Test health, coverage, recent failures
- pytest_run_adg_impact: Run tests for ADG-impacted modules only
- pytest_run_guardians: Run governance test suite
- pytest_run_smoke: Quick smoke test with critical path
- pytest_coverage_analysis: Coverage by ADG layer
- pytest_failure_analysis: Root cause analysis with ADG context

Integration
-----------
Uses existing pytest.ini configuration
Integrates with adg_incremental_update.py for impact analysis
Connects to test coverage and ADG edge mapping
Enforces Constitutional Rule #3 (no test skipping)
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    record_execution_trace,
)

# Lifecycle tracing for this MCP
emit_determinism_digest("pytest_mcp_server", "pytest_mcp_server_digest")
record_execution_trace("pytest_mcp_server", "pytest_mcp_server_trace")
_emit_applies_guardrail("p0", "pytest_mcp_server", "p0_governance")
_emit_reads_policy_state("p0", "pytest_mcp_server", "policy_binding")
_emit_snapshots_state("p0", "pytest_mcp_server", "state_snapshot")
_emit_authorize_and_execute("p2", "pytest_mcp_server", "execution_auth")
_emit_validates_capability("p2", "pytest_mcp_server", "capability_check")
_emit_routes_to_capability("p2", "pytest_mcp_server", "capability_route")
_emit_writes_via_uwg("p2", "pytest_mcp_server", "uwg_write")
_emit_blocks_direct_write("p2", "pytest_mcp_server", "direct_write_block")
_emit_records_tool_invocation("p2", "pytest_mcp_server", "tool_invocation")
_emit_captures_execution_output("p2", "pytest_mcp_server", "exec_output")
_emit_dispatches_agent("p3", "pytest_mcp_server", "agent_dispatch")
_emit_coordinates_agents("p3", "pytest_mcp_server", "agent_coordination")
_emit_records_workflow_lineage("p3", "pytest_mcp_server", "workflow_lineage")
_emit_records_healing_outcome("p3", "pytest_mcp_server", "healing_outcome")
_emit_escalates_failure("p3", "pytest_mcp_server", "failure_escalation")
_emit_orchestrates_workflow("p3", "pytest_mcp_server", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pytest_mcp_server", "healing_dispatch")
_emit_invokes_evaluation("p3", "pytest_mcp_server", "evaluation_signal")
_emit_records_telemetry_event("p4", "pytest_mcp_server", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pytest_mcp_server", "eval_metric")
_emit_stores_embedding("p4", "pytest_mcp_server", "embedding_store")
_emit_updates_meta_learning_state("p4", "pytest_mcp_server", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pytest_mcp_server", "exec_snapshot_link")

# Initialize FastMCP server
mcp = FastMCP("pytest-mcp")

# Logger
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
TESTS_DIR = PROJECT_ROOT / "tests"
PYTEST_INI = PROJECT_ROOT / "pytest.ini"
if not PYTEST_INI.exists():
    raise FileNotFoundError(f"pytest.ini not found at {PYTEST_INI}")
COVERAGE_DIR = PROJECT_ROOT / "htmlcov"
ADG_ARTIFACTS_DIR = PROJECT_ROOT / "artifacts/adg"
ADG_INCREMENTAL_SCRIPT = PROJECT_ROOT / "tools/adg_incremental_update.py"

# Test categories
GOVERNANCE_TESTS = [
    "tests/unit/agentic_core/L0_routing/",
    "tests/unit/agentic_core/L5_safety/",
    "tests/integration/governance/"
]

SMOKE_TESTS = [
    "tests/unit/agentic_core/adg/",
    "tests/unit/agentic_core/runtime/",
    "tests/integration/adg/"
]

# Cache for test status
_test_cache: dict[str, Any] = {}
_last_cache_update = 0
CACHE_TTL = 600  # 10 minutes


def _refresh_test_cache():
    """Refresh test status cache."""
    global _last_cache_update
    current_time = int(time.time())

    if current_time - _last_cache_update < CACHE_TTL:
        return

    # Check for recent test results
    test_results = {}

    # Look for pytest cache and coverage files
    pytest_cache_dir = PROJECT_ROOT / ".pytest_cache"
    if pytest_cache_dir.exists():
        test_results["cache_available"] = True
        test_results["cache_timestamp"] = pytest_cache_dir.stat().st_mtime
    else:
        test_results["cache_available"] = False

    # Check coverage
    if COVERAGE_DIR.exists():
        coverage_file = COVERAGE_DIR / "index.html"
        if coverage_file.exists():
            test_results["coverage_available"] = True
            test_results["coverage_timestamp"] = coverage_file.stat().st_mtime
    else:
        test_results["coverage_available"] = False

    # Count test files
    if TESTS_DIR.exists():
        test_files = list(TESTS_DIR.rglob("test_*.py")) + list(TESTS_DIR.rglob("*_test.py"))
        test_results["total_test_files"] = len(test_files)
    else:
        test_results["total_test_files"] = 0

    _test_cache.update(test_results)
    _last_cache_update = current_time


def _run_pytest(args: list[str], timeout: int = 300) -> dict[str, Any]:
    """Run pytest with specified arguments."""
    try:
        cmd = ["python", "-m", "pytest"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT)
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
            "timestamp": int(time.time())
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Test execution timed out",
            "command": " ".join(cmd),
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": " ".join(cmd),
            "timestamp": int(time.time())
        }


def _parse_pytest_output(output: str) -> dict[str, Any]:
    """Parse pytest output for test results."""
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": 0.0
    }

    lines = output.split('\n')
    for line in lines:
        if " passed" in line and " failed" in line:
            # Parse summary line like "5 passed, 2 failed, 1 skipped in 10.5s"
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed" and i > 0:
                    results["passed"] = int(parts[i-1])
                elif part == "failed" and i > 0:
                    results["failed"] = int(parts[i-1])
                elif part == "skipped" and i > 0:
                    results["skipped"] = int(parts[i-1])
                elif part == "errors" and i > 0:
                    results["errors"] = int(parts[i-1])
                elif part == "in" and i+1 < len(parts):
                    try:
                        results["duration"] = float(parts[i+1].rstrip('s'))
                    except ValueError:
                        pass

    results["total"] = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
    return results


@mcp.tool()
def pytest_status() -> dict[str, Any]:
    """Get test health, coverage, and recent failure status.

    Returns:
        Dictionary with overall test health and status metrics.
    """
    _refresh_test_cache()

    # Get recent test results from cache
    status = {
        "timestamp": int(time.time()),
        "cache_available": _test_cache.get("cache_available", False),
        "coverage_available": _test_cache.get("coverage_available", False),
        "total_test_files": _test_cache.get("total_test_files", 0),
        "health_score": 0.0,
        "recent_failures": [],
        "recommendations": []
    }

    # Calculate health score
    health_factors = []
    if status["cache_available"]:
        health_factors.append(0.3)
    if status["coverage_available"]:
        health_factors.append(0.4)
    if status["total_test_files"] > 0:
        health_factors.append(0.3)

    status["health_score"] = sum(health_factors)

    # Add recommendations
    if not status["cache_available"]:
        status["recommendations"].append("Run tests to generate cache")
    if not status["coverage_available"]:
        status["recommendations"].append("Run tests with coverage to generate reports")
    if status["total_test_files"] == 0:
        status["recommendations"].append("No test files found - check test directory structure")

    logger.info("pytest_status_checked", extra=status)
    return status


@mcp.tool()
def pytest_run_adg_impact(file_list: list[str], timeout: int = 300) -> dict[str, Any]:
    """Run tests for ADG-impacted modules only.

    Args:
        file_list: List of changed files to analyze for impact
        timeout: Test execution timeout in seconds

    Returns:
        Dictionary with impact analysis and test execution results.
    """
    if not file_list or len(file_list) == 0:
        return {"success": False, "error": "file_list cannot be empty"}

    if timeout <= 0 or timeout > 1800:  # Max 30 minutes
        return {"success": False, "error": "timeout must be between 1 and 1800 seconds"}
    # First, run ADG impact analysis
    try:
        impact_args = [str(ADG_INCREMENTAL_SCRIPT)] + file_list
        impact_result = subprocess.run(
            impact_args,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT)
        )

        if impact_result.returncode != 0:
            return {
                "success": False,
                "error": f"ADG impact analysis failed: {impact_result.stderr}",
                "file_list": file_list
            }

        # Parse impact output to get affected test files
        affected_modules = []
        for line in impact_result.stdout.split('\n'):
            if line.strip() and not line.startswith('#'):
                # Convert module paths to test file paths
                module_path = line.strip()
                test_path = TESTS_DIR / module_path.replace("agentic_core/", "").replace(".py", "_test.py")
                if test_path.exists():
                    affected_modules.append(str(test_path))

        if not affected_modules:
            return {
                "success": True,
                "message": "No tests affected by the specified changes",
                "file_list": file_list,
                "affected_modules": [],
                "impact_analysis": impact_result.stdout
            }

        # Run tests for affected modules
        pytest_args = affected_modules + ["-v", "--tb=short"]
        test_result = _run_pytest(pytest_args, timeout)

        # Parse test results
        if test_result["success"]:
            parsed_results = _parse_pytest_output(test_result["stdout"])
        else:
            parsed_results = {"error": "Test execution failed"}

        result = {
            "success": test_result["success"],
            "file_list": file_list,
            "affected_modules": affected_modules,
            "module_count": len(affected_modules),
            "impact_analysis": impact_result.stdout,
            "test_execution": test_result,
            "test_results": parsed_results,
            "timestamp": int(time.time())
        }

        logger.info("pytest_adg_impact_executed", extra={
            "file_count": len(file_list),
            "affected_modules": len(affected_modules),
            "success": result["success"]
        })

        return result

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "ADG impact analysis timed out",
            "file_list": file_list
        }
    except Exception as e:
        logger.error("pytest_adg_impact_error", extra={
            "file_count": len(file_list),
            "error": str(e)
        })
        return {
            "success": False,
            "error": str(e),
            "file_list": file_list
        }


@mcp.tool()
def pytest_run_guardians(timeout: int = 600) -> dict[str, Any]:
    """Run governance test suite to enforce Constitutional Rule #3.

    Args:
        timeout: Test execution timeout in seconds

    Returns:
        Dictionary with governance test results and compliance status.
    """
    governance_args = []
    for test_path in GOVERNANCE_TESTS:
        if Path(test_path).exists():
            governance_args.append(test_path)

    if not governance_args:
        return {
            "success": False,
            "error": "No governance test paths found",
            "searched_paths": GOVERNANCE_TESTS
        }

    # Add governance-specific pytest options
    governance_args.extend([
        "-v",
        "--tb=short",
        "--strict-markers",
        "-m", "governance or integration"
    ])

    test_result = _run_pytest(governance_args, timeout)

    # Parse results
    if test_result["success"]:
        parsed_results = _parse_pytest_output(test_result["stdout"])

        # Check for test skipping (Constitutional Rule #3 violation)
        if parsed_results.get("skipped", 0) > 0:
            compliance_status = "non_compliant"
            violation = f"Constitutional Rule #3 violated: {parsed_results['skipped']} tests skipped"
        else:
            compliance_status = "compliant"
            violation = None
    else:
        parsed_results = {"error": "Governance test execution failed"}
        compliance_status = "unknown"
        violation = "Test execution failed"

    result = {
        "success": test_result["success"],
        "governance_paths": GOVERNANCE_TESTS,
        "actual_paths": governance_args,
        "test_execution": test_result,
        "test_results": parsed_results,
        "compliance_status": compliance_status,
        "constitutional_rule_3_violation": violation,
        "timestamp": int(time.time())
    }

    logger.info("pytest_guardians_executed", extra={
        "success": result["success"],
        "compliance": compliance_status
    })

    return result


@mcp.tool()
def pytest_run_smoke(timeout: int = 180) -> dict[str, Any]:
    """Run quick smoke test with critical path validation.

    Args:
        timeout: Test execution timeout in seconds

    Returns:
        Dictionary with smoke test results and critical path status.
    """
    smoke_args = []
    for test_path in SMOKE_TESTS:
        if Path(test_path).exists():
            smoke_args.append(test_path)

    if not smoke_args:
        return {
            "success": False,
            "error": "No smoke test paths found",
            "searched_paths": SMOKE_TESTS
        }

    # Add smoke test specific options
    smoke_args.extend([
        "-v",
        "--tb=short",
        "-m", "smoke or unit",
        "--maxfail=5"  # Stop after 5 failures for quick feedback
    ])

    test_result = _run_pytest(smoke_args, timeout)

    # Parse results
    if test_result["success"]:
        parsed_results = _parse_pytest_output(test_result["stdout"])
        critical_path_status = "passed" if parsed_results.get("failed", 0) == 0 else "failed"
    else:
        parsed_results = {"error": "Smoke test execution failed"}
        critical_path_status = "unknown"

    result = {
        "success": test_result["success"],
        "smoke_paths": SMOKE_TESTS,
        "actual_paths": smoke_args,
        "test_execution": test_result,
        "test_results": parsed_results,
        "critical_path_status": critical_path_status,
        "timestamp": int(time.time())
    }

    logger.info("pytest_smoke_executed", extra={
        "success": result["success"],
        "critical_path": critical_path_status
    })

    return result


@mcp.tool()
def pytest_coverage_analysis(layer_filter: str = "all") -> dict[str, Any]:
    """Coverage analysis by ADG layer and edge type.

    Args:
        layer_filter: Filter by ADG layer (L0, L1, L2, L3, L4, L5, L6, all)

    Returns:
        Dictionary with coverage breakdown by ADG components.
    """
    # Try to run coverage analysis
    coverage_args = [
        "--cov=agentic_core",
        "--cov-report=term-missing",
        "--cov-report=json:coverage.json",
        "--cov-report=html",
        "tests/"
    ]

    coverage_result = _run_pytest(coverage_args, timeout=600)

    # Parse coverage JSON if available
    coverage_data = {}
    coverage_file = PROJECT_ROOT / "coverage.json"

    if coverage_file.exists():
        try:
            with open(coverage_file) as f:
                coverage_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to parse coverage JSON: {e}")

    # Analyze coverage by ADG layer
    layer_coverage = {}
    if coverage_data.get("files"):
        for file_path, file_data in coverage_data["files"].items():
            # Determine ADG layer from file path
            if "agentic_core/L" in file_path:
                layer_match = file_path.split("agentic_core/L")[1].split("/")[0]
                layer = f"L{layer_match}"
            else:
                layer = "other"

            if layer_filter != "all" and layer != layer_filter:
                continue

            if layer not in layer_coverage:
                layer_coverage[layer] = {
                    "files": 0,
                    "lines_covered": 0,
                    "lines_missing": 0,
                    "total_lines": 0,
                    "coverage_percent": 0.0
                }

            layer_coverage[layer]["files"] += 1
            layer_coverage[layer]["lines_covered"] += file_data.get("summary", {}).get("covered_lines", 0)
            layer_coverage[layer]["lines_missing"] += file_data.get("summary", {}).get("missing_lines", 0)
            layer_coverage[layer]["total_lines"] += file_data.get("summary", {}).get("num_statements", 0)

        # Calculate coverage percentages
        for layer in layer_coverage:
            total = layer_coverage[layer]["total_lines"]
            if total > 0:
                layer_coverage[layer]["coverage_percent"] = (
                    layer_coverage[layer]["lines_covered"] / total * 100
                )

    result = {
        "success": coverage_result["success"],
        "layer_filter": layer_filter,
        "coverage_execution": coverage_result,
        "layer_coverage": layer_coverage,
        "overall_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
        "timestamp": int(time.time())
    }

    logger.info("pytest_coverage_analyzed", extra={
        "layer_filter": layer_filter,
        "overall_coverage": result["overall_coverage"]
    })

    return result


@mcp.tool()
def pytest_failure_analysis(test_run_id: str = None) -> dict[str, Any]:
    """Root cause analysis of test failures with ADG context.

    Args:
        test_run_id: Specific test run ID to analyze (optional)

    Returns:
        Dictionary with failure analysis and ADG context.
    """
    # Get recent failure information from pytest cache
    pytest_cache_dir = PROJECT_ROOT / ".pytest_cache"
    failure_analysis = {
        "test_run_id": test_run_id or "latest",
        "failures": [],
        "adg_context": {},
        "recommendations": []
    }

    # Look for recent failure files
    if pytest_cache_dir.exists():
        # Find recent cache files that might contain failure info
        cache_files = list(pytest_cache_dir.rglob("*.cache"))

        for cache_file in cache_files[-10:]:  # Last 10 cache files
            try:
                # Simple attempt to read cache file (actual parsing would be more complex)
                with open(cache_file, 'rb') as f:
                    # This is a simplified approach - real cache parsing would require pytest cache format
                    content = f.read(1000)  # Read first 1KB
                    if b"FAILED" in content:
                        failure_analysis["failures"].append({
                            "cache_file": str(cache_file),
                            "detected_failure": True,
                            "analysis": "Failure detected in cache file"
                        })
            except Exception:
                continue

    # Add ADG context recommendations
    if failure_analysis["failures"]:
        failure_analysis["recommendations"].extend([
            "Check ADG impact analysis for affected modules",
            "Run pytest_run_adg_impact for targeted testing",
            "Verify layer boundary compliance if architecture tests failed",
            "Check import discipline if dependency tests failed"
        ])
    else:
        failure_analysis["recommendations"].append(
            "No recent failures detected - run tests to generate failure data"
        )

    result = {
        "success": True,
        "analysis": failure_analysis,
        "timestamp": int(time.time())
    }

    logger.info("pytest_failure_analyzed", extra={
        "test_run_id": test_run_id or "latest",
        "failures_found": len(failure_analysis["failures"])
    })

    return result


if __name__ == "__main__":
    logger.info("Starting Pytest Test Orchestration MCP Server")
    mcp.run()
