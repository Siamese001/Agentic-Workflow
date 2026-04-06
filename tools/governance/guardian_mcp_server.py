"""
Guardian Governance MCP Server

Centralizes access to 17+ guardian scripts and governance agents.
Provides unified query and trigger interface for governance validations from Windsurf chat.

Why this exists
---------------
17+ guardian scripts in agentic_core/L0_routing/scripts/run_guardian_*.py
AutonomyGuardian/HygieneGuardian agents in L5_safety/reasoning/
No unified query interface for governance status
Manual script execution for governance validation

This server provides:
- Centralized guardian status and reporting
- On-demand guardian execution from chat
- Interface to L5_safety guardian agents
- Governance decision audit trail
- Automated healing trigger for failed guardians
- Sovereignty and hygiene manifest access

Tools (6-8)
-----------
- guardian_status: Which guardians passed/failed recently
- guardian_run: Execute specific guardian (e.g., hierarchy_compliance)
- guardian_report: Latest guardian execution results
- guardian_manifest: Sovereignty/hygiene manifest status
- guardian_healing: Trigger healing for failed guardians
- guardian_audit: Governance decision audit trail
- guardian_impact_analysis: Predict governance impact of changes
- guardian_registry: List all available guardians

Integration
-----------
Wraps existing agentic_core/L0_routing/scripts/run_guardian_*.py
Interfaces with L5_safety/reasoning/*GuardianAgent.py
Uses guardian_report.json and telemetry events
Connects to healing infrastructure for automated remediation
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
emit_determinism_digest("guardian_mcp_server", "guardian_mcp_server_digest")
record_execution_trace("guardian_mcp_server", "guardian_mcp_server_trace")
_emit_applies_guardrail("p0", "guardian_mcp_server", "p0_governance")
_emit_reads_policy_state("p0", "guardian_mcp_server", "policy_binding")
_emit_snapshots_state("p0", "guardian_mcp_server", "state_snapshot")
_emit_authorize_and_execute("p2", "guardian_mcp_server", "execution_auth")
_emit_validates_capability("p2", "guardian_mcp_server", "capability_check")
_emit_routes_to_capability("p2", "guardian_mcp_server", "capability_route")
_emit_writes_via_uwg("p2", "guardian_mcp_server", "uwg_write")
_emit_blocks_direct_write("p2", "guardian_mcp_server", "direct_write_block")
_emit_records_tool_invocation("p2", "guardian_mcp_server", "tool_invocation")
_emit_captures_execution_output("p2", "guardian_mcp_server", "exec_output")
_emit_dispatches_agent("p3", "guardian_mcp_server", "agent_dispatch")
_emit_coordinates_agents("p3", "guardian_mcp_server", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardian_mcp_server", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardian_mcp_server", "healing_outcome")
_emit_escalates_failure("p3", "guardian_mcp_server", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardian_mcp_server", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardian_mcp_server", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardian_mcp_server", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardian_mcp_server", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardian_mcp_server", "eval_metric")
_emit_stores_embedding("p4", "guardian_mcp_server", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardian_mcp_server", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardian_mcp_server", "exec_snapshot_link")

# Initialize FastMCP server
mcp = FastMCP("governance-mcp")

# Logger
logger = logging.getLogger(__name__)

# Configuration
GUARDIAN_SCRIPTS_DIR = Path("C:/Git/Agentic-Workflow/agentic_core/L0_routing/scripts")
GUARDIAN_REPORTS_DIR = Path("C:/Git/Agentic-Workflow/artifacts/governance")
GUARDIAN_AGENTS_DIR = Path("C:/Git/Agentic-Workflow/agentic_core/L5_safety/reasoning")

# Known guardian scripts
GUARDIAN_SCRIPTS = [
    "run_guardian_hierarchy_compliance.py",
    "run_guardian_layer_boundary.py",
    "run_guardian_sovereignty.py",
    "run_guardian_hygiene.py",
    "run_guardian_import_discipline.py",
    "run_guardian_ssot_compliance.py",
    "run_guardian_dependency_graph.py",
    "run_guardian_architectural_rules.py",
    "run_guardian_test_coverage.py",
    "run_guardian_performance.py",
    "run_guardian_security.py",
    "run_guardian_observability.py",
    "run_guardian_documentation.py",
    "run_guardian_deployment.py",
    "run_guardian_monitoring.py",
    "run_guardian_backup.py",
    "run_guardian_recovery.py"
]

# Cache for guardian status
_guardian_cache: dict[str, dict[str, Any]] = {}
_last_cache_update = 0
CACHE_TTL = 300  # 5 minutes


def _refresh_guardian_cache():
    """Refresh guardian status cache."""
    global _last_cache_update
    current_time = int(time.time())

    if current_time - _last_cache_update < CACHE_TTL:
        return

    # Scan for guardian reports
    for script in GUARDIAN_SCRIPTS:
        guardian_name = script.replace("run_guardian_", "").replace(".py", "")
        report_file = GUARDIAN_REPORTS_DIR / f"{guardian_name}_report.json"

        if report_file.exists():
            try:
                with open(report_file) as f:
                    report = json.load(f)

                _guardian_cache[guardian_name] = {
                    "name": guardian_name,
                    "script": script,
                    "status": report.get("status", "unknown"),
                    "last_run": report.get("timestamp", 0),
                    "summary": report.get("summary", ""),
                    "issues_found": report.get("issues_count", 0),
                    "report_file": str(report_file)
                }
            except Exception as e:
                logger.warning(f"Failed to load guardian report for {guardian_name}: {e}")
                _guardian_cache[guardian_name] = {
                    "name": guardian_name,
                    "script": script,
                    "status": "error",
                    "last_run": 0,
                    "summary": f"Failed to load report: {e}",
                    "issues_found": 0,
                    "report_file": str(report_file)
                }
        else:
            _guardian_cache[guardian_name] = {
                "name": guardian_name,
                "script": script,
                "status": "never_run",
                "last_run": 0,
                "summary": "No report available",
                "issues_found": 0,
                "report_file": str(report_file)
            }

    _last_cache_update = current_time


@mcp.tool()
def guardian_status() -> dict[str, Any]:
    """Get current status of all guardians (passed/failed/never_run).

    Returns:
        Dictionary with guardian status summary and detailed status list.
    """
    _refresh_guardian_cache()

    status_counts = {"passed": 0, "failed": 0, "never_run": 0, "error": 0, "unknown": 0}
    guardian_details = []

    for guardian_name, cache_entry in _guardian_cache.items():
        status = cache_entry["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        guardian_details.append({
            "name": guardian_name,
            "status": status,
            "last_run": cache_entry["last_run"],
            "issues_found": cache_entry["issues_found"],
            "summary": cache_entry["summary"]
        })

    result = {
        "timestamp": int(time.time()),
        "total_guardians": len(_guardian_cache),
        "status_counts": status_counts,
        "overall_health": status_counts["passed"] / max(len(_guardian_cache), 1),
        "guardians": guardian_details
    }

    logger.info("guardian_status_checked", extra=result)
    return result


@mcp.tool()
def guardian_run(guardian_name: str, force: bool = False, timeout: int = 300) -> dict[str, Any]:
    """Execute a specific guardian script.

    Args:
        guardian_name: Name of guardian (e.g., "hierarchy_compliance")
        force: Force re-run even if recently executed
        timeout: Execution timeout in seconds

    Returns:
        Dictionary with execution result and output.
    """
    if timeout <= 0 or timeout > 1800:  # Max 30 minutes
        return {"success": False, "error": "timeout must be between 1 and 1800 seconds"}

    if not guardian_name or not guardian_name.strip():
        return {"success": False, "error": "guardian_name cannot be empty"}

    if len(guardian_name) > 50:
        return {"success": False, "error": "guardian_name too long (max 50 characters)"}

    script_name = f"run_guardian_{guardian_name}.py"
    script_path = GUARDIAN_SCRIPTS_DIR / script_name

    if not script_path.exists():
        return {
            "success": False,
            "error": f"Guardian script not found: {script_name}",
            "guardian_name": guardian_name
        }

    # Check if recently run (unless forced)
    if not force:
        _refresh_guardian_cache()
        cache_entry = _guardian_cache.get(guardian_name, {})
        last_run = cache_entry.get("last_run", 0)
        if int(time.time()) - last_run < 60:  # Recently run
            return {
                "success": False,
                "error": f"Guardian {guardian_name} recently run (use force=True)",
                "guardian_name": guardian_name,
                "last_run": last_run
            }

    try:
        # Execute guardian script
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,  # Use provided timeout
            cwd="C:/Git/Agentic-Workflow"
        )

        execution_result = {
            "success": result.returncode == 0,
            "guardian_name": guardian_name,
            "script": script_name,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": int(time.time())
        }

        # Refresh cache after execution
        _refresh_guardian_cache()

        logger.info("guardian_run_executed", extra={
            "guardian_name": guardian_name,
            "success": execution_result["success"],
            "return_code": result.returncode
        })

        return execution_result

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Guardian {guardian_name} execution timed out",
            "guardian_name": guardian_name,
            "script": script_name
        }
    except Exception as e:
        logger.error("guardian_run_error", extra={
            "guardian_name": guardian_name,
            "error": str(e)
        })
        return {
            "success": False,
            "error": str(e),
            "guardian_name": guardian_name,
            "script": script_name
        }


@mcp.tool()
def guardian_report(guardian_name: str = None) -> dict[str, Any]:
    """Get latest guardian execution results.

    Args:
        guardian_name: Specific guardian name, or None for all guardians

    Returns:
        Dictionary with detailed guardian reports.
    """
    _refresh_guardian_cache()

    if guardian_name:
        if guardian_name not in _guardian_cache:
            return {
                "success": False,
                "error": f"Guardian not found: {guardian_name}"
            }

        cache_entry = _guardian_cache[guardian_name]
        report_file = Path(cache_entry["report_file"])

        if report_file.exists():
            try:
                with open(report_file) as f:
                    report = json.load(f)

                return {
                    "success": True,
                    "guardian_name": guardian_name,
                    "report": report
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to load report: {e}",
                    "guardian_name": guardian_name
                }
        else:
            return {
                "success": False,
                "error": f"No report file found for {guardian_name}",
                "guardian_name": guardian_name
            }
    else:
        # Return summary of all guardians
        reports = {}
        for name, cache_entry in _guardian_cache.items():
            reports[name] = {
                "status": cache_entry["status"],
                "last_run": cache_entry["last_run"],
                "summary": cache_entry["summary"],
                "issues_found": cache_entry["issues_found"]
            }

        return {
            "success": True,
            "guardian_count": len(reports),
            "reports": reports
        }


@mcp.tool()
def guardian_manifest() -> dict[str, Any]:
    """Get sovereignty and hygiene manifest status.

    Returns:
        Dictionary with manifest compliance status and details.
    """
    # Look for manifest files
    manifest_files = [
        "sovereignty_manifest.json",
        "hygiene_manifest.json",
        "architecture_manifest.json"
    ]

    manifests = {}
    for manifest_file in manifest_files:
        manifest_path = GUARDIAN_REPORTS_DIR / manifest_file
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifests[manifest_file.replace(".json", "")] = json.load(f)
            except Exception as e:
                manifests[manifest_file.replace(".json", "")] = {
                    "error": f"Failed to load: {e}"
                }

    # Calculate overall compliance
    total_compliance = 0
    compliance_count = 0

    for manifest_name, manifest_data in manifests.items():
        if isinstance(manifest_data, dict) and "compliance_score" in manifest_data:
            total_compliance += manifest_data["compliance_score"]
            compliance_count += 1

    overall_compliance = total_compliance / max(compliance_count, 1)

    result = {
        "timestamp": int(time.time()),
        "overall_compliance": overall_compliance,
        "manifest_count": len(manifests),
        "manifests": manifests,
        "status": "compliant" if overall_compliance >= 0.95 else "non_compliant"
    }

    logger.info("guardian_manifest_checked", extra=result)
    return result


@mcp.tool()
def guardian_healing(failure_id: str, healing_type: str = "automatic") -> dict[str, Any]:
    """Trigger healing for failed guardians.

    Args:
        failure_id: Guardian failure identifier or guardian name
        healing_type: Type of healing (automatic, manual, assisted)

    Returns:
        Dictionary with healing initiation result.
    """
    # Find the guardian with this failure
    _refresh_guardian_cache()
    target_guardian = None

    for guardian_name, cache_entry in _guardian_cache.items():
        if (guardian_name == failure_id or
            cache_entry.get("status") == "failed" or
            cache_entry.get("issues_found", 0) > 0):
            target_guardian = guardian_name
            break

    if not target_guardian:
        return {
            "success": False,
            "error": f"No failed guardian found for failure_id: {failure_id}. Available failed guardians: {list(_guardian_cache.keys())}",
            "failure_id": failure_id
        }

    try:
        # Trigger healing by re-running the guardian with analysis
        healing_result = guardian_run(target_guardian, force=True)

        healing_response = {
            "success": healing_result["success"],
            "failure_id": failure_id,
            "target_guardian": target_guardian,
            "healing_type": healing_type,
            "timestamp": int(time.time()),
            "execution_result": healing_result
        }

        # If healing succeeded, update cache
        if healing_result["success"]:
            _refresh_guardian_cache()

        logger.info("guardian_healing_triggered", extra={
            "failure_id": failure_id,
            "target_guardian": target_guardian,
            "success": healing_response["success"]
        })

        return healing_response

    except Exception as e:
        logger.error("guardian_healing_error", extra={
            "failure_id": failure_id,
            "error": str(e)
        })
        return {
            "success": False,
            "error": str(e),
            "failure_id": failure_id
        }


@mcp.tool()
def guardian_audit(time_window_hours: int = 24) -> dict[str, Any]:
    """Get governance decision audit trail.

    Args:
        time_window_hours: Time window for audit (default 24 hours)

    Returns:
        Dictionary with audit trail and governance decisions.
    """
    cutoff_time = int(time.time()) - (time_window_hours * 3600)

    audit_events = []

    # Collect recent guardian executions
    _refresh_guardian_cache()
    for guardian_name, cache_entry in _guardian_cache.items():
        if cache_entry.get("last_run", 0) >= cutoff_time:
            audit_events.append({
                "timestamp": cache_entry["last_run"],
                "event_type": "guardian_execution",
                "guardian_name": guardian_name,
                "status": cache_entry["status"],
                "issues_found": cache_entry["issues_found"],
                "summary": cache_entry["summary"]
            })

    # Sort by timestamp (most recent first)
    audit_events.sort(key=lambda x: x["timestamp"], reverse=True)

    # Calculate governance metrics
    total_executions = len(audit_events)
    failed_executions = len([e for e in audit_events if e["status"] == "failed"])
    total_issues = sum(e["issues_found"] for e in audit_events)

    result = {
        "time_window_hours": time_window_hours,
        "cutoff_time": cutoff_time,
        "total_executions": total_executions,
        "failed_executions": failed_executions,
        "success_rate": (total_executions - failed_executions) / max(total_executions, 1),
        "total_issues_found": total_issues,
        "audit_events": audit_events[:100],  # Limit to 100 most recent
        "governance_health": "healthy" if failed_executions == 0 else "degraded"
    }

    logger.info("guardian_audit_generated", extra=result)
    return result


@mcp.tool()
def guardian_impact_analysis(change_set: list[str]) -> dict[str, Any]:
    """Predict governance impact of proposed changes.

    Args:
        change_set: List of file paths that will be changed

    Returns:
        Dictionary with impact analysis and affected guardians.
    """
    # Simple impact analysis based on file paths
    affected_guardians = []
    impact_level = "low"

    for file_path in change_set:
        # Map file patterns to affected guardians
        if "agentic_core/L" in file_path and "routing" in file_path:
            affected_guardians.extend(["hierarchy_compliance", "layer_boundary"])
            impact_level = "high"
        elif "agentic_core/L5_safety" in file_path:
            affected_guardians.extend(["security", "sovereignty"])
            impact_level = "high"
        elif "test_" in file_path or "tests/" in file_path:
            affected_guardians.append("test_coverage")
            impact_level = "medium"
        elif "import" in file_path or "dependency" in file_path:
            affected_guardians.append("import_discipline")
            impact_level = "medium"
        elif "docs/" in file_path or "README" in file_path:
            affected_guardians.append("documentation")
            impact_level = "low"

    # Remove duplicates
    affected_guardians = list(set(affected_guardians))

    result = {
        "change_set": change_set,
        "affected_guardians": affected_guardians,
        "impact_level": impact_level,
        "guardian_count": len(affected_guardians),
        "recommendation": _get_impact_recommendation(impact_level),
        "timestamp": int(time.time())
    }

    logger.info("guardian_impact_analyzed", extra=result)
    return result


@mcp.tool()
def guardian_registry() -> dict[str, Any]:
    """List all available guardians with metadata.

    Returns:
        Dictionary with guardian registry and metadata.
    """
    registry = []

    for script in GUARDIAN_SCRIPTS:
        guardian_name = script.replace("run_guardian_", "").replace(".py", "")
        script_path = GUARDIAN_SCRIPTS_DIR / script

        # Get script metadata
        metadata = {
            "name": guardian_name,
            "script": script,
            "script_path": str(script_path),
            "exists": script_path.exists(),
            "category": _get_guardian_category(guardian_name),
            "description": _get_guardian_description(guardian_name),
            "typical_duration": _get_guardian_duration(guardian_name)
        }

        # Add current status if available
        _refresh_guardian_cache()
        if guardian_name in _guardian_cache:
            cache_entry = _guardian_cache[guardian_name]
            metadata.update({
                "current_status": cache_entry["status"],
                "last_run": cache_entry["last_run"],
                "issues_found": cache_entry["issues_found"]
            })

        registry.append(metadata)

    result = {
        "timestamp": int(time.time()),
        "total_guardians": len(registry),
        "guardians": registry,
        "categories": list(set(g["category"] for g in registry))
    }

    logger.info("guardian_registry_generated", extra=result)
    return result


# Helper functions

def _get_guardian_category(guardian_name: str) -> str:
    """Get guardian category based on name."""
    if "hierarchy" in guardian_name or "layer" in guardian_name:
        return "architecture"
    elif "security" in guardian_name or "sovereignty" in guardian_name:
        return "security"
    elif "test" in guardian_name:
        return "testing"
    elif "performance" in guardian_name or "monitoring" in guardian_name:
        return "operations"
    elif "import" in guardian_name or "dependency" in guardian_name:
        return "dependencies"
    elif "backup" in guardian_name or "recovery" in guardian_name:
        return "resilience"
    else:
        return "general"


def _get_guardian_description(guardian_name: str) -> str:
    """Get guardian description."""
    descriptions = {
        "hierarchy_compliance": "Validates architectural layer hierarchy compliance",
        "layer_boundary": "Enforces layer boundary rules and restrictions",
        "sovereignty": "Checks sovereign territory compliance",
        "hygiene": "Validates code hygiene and best practices",
        "import_discipline": "Enforces import discipline and rules",
        "ssot_compliance": "Validates Single Source of Truth compliance",
        "dependency_graph": "Analyzes dependency graph integrity",
        "architectural_rules": "Validates architectural rule compliance",
        "test_coverage": "Checks test coverage requirements",
        "performance": "Validates performance requirements",
        "security": "Security compliance and vulnerability checks",
        "observability": "Observability and monitoring compliance",
        "documentation": "Documentation completeness and accuracy",
        "deployment": "Deployment readiness and compliance",
        "monitoring": "Monitoring configuration and alerts",
        "backup": "Backup strategy and compliance",
        "recovery": "Recovery procedures and testing"
    }
    return descriptions.get(guardian_name, f"Guardian for {guardian_name}")


def _get_guardian_duration(guardian_name: str) -> str:
    """Get typical execution duration."""
    durations = {
        "hierarchy_compliance": "2-5 minutes",
        "layer_boundary": "1-3 minutes",
        "sovereignty": "1-2 minutes",
        "hygiene": "3-8 minutes",
        "import_discipline": "1-2 minutes",
        "ssot_compliance": "1-2 minutes",
        "dependency_graph": "5-15 minutes",
        "architectural_rules": "2-5 minutes",
        "test_coverage": "5-10 minutes",
        "performance": "3-8 minutes",
        "security": "5-20 minutes",
        "observability": "2-5 minutes",
        "documentation": "1-3 minutes",
        "deployment": "2-5 minutes",
        "monitoring": "1-2 minutes",
        "backup": "1-3 minutes",
        "recovery": "2-5 minutes"
    }
    return durations.get(guardian_name, "2-5 minutes")


def _get_impact_recommendation(impact_level: str) -> str:
    """Get recommendation based on impact level."""
    recommendations = {
        "low": "Changes are low risk, standard review process sufficient",
        "medium": "Changes may affect some guardians, run affected guardians before commit",
        "high": "High impact changes, run full guardian suite and review results carefully"
    }
    return recommendations.get(impact_level, "Unknown impact level")


if __name__ == "__main__":
    logger.info("Starting Guardian Governance MCP Server")
    mcp.run()
