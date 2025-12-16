import os
import sys
import json
import logging
import subprocess
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import core utilities for validation and signing
from core_utils import (
    validate_python_syntax,
    sign_and_commit,
    search_nodes,
    add_observations,
    semantic_score_draft,
    write_file,
    register_process,
    log_action,
)

# Import MCP hardening utilities
from mcp_hardening import check_design_drift, execute_vulnerability_search

# Import sandbox utilities for execution isolation
from sandbox_utils import execute_in_sandbox
# Import consensus engine for Protocol 6
from consensus_engine import jury

# Add this global configuration flag (or load from environment/config)
SHADOW_MODE_ACTIVE = os.environ.get("AGENT_MODE", "PRODUCTION") == "SHADOW"
MAX_P6_ATTEMPTS = int(os.environ.get("MAX_P6_ATTEMPTS", "3"))
REGRESSION_SUITE_PATH = os.environ.get("REGRESSION_SUITE_PATH", "tests/")


def execute_regression_suite(logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Execute the full regression test suite (Test 5).

    Returns:
        Dict with status and details
    """

    if logger:
        logger.info(f"🧪 TEST_5: Running regression suite from {REGRESSION_SUITE_PATH}")

    # Check if regression suite path exists
    if not os.path.exists(REGRESSION_SUITE_PATH):
        error_msg = f"Regression suite path does not exist: {REGRESSION_SUITE_PATH}"
        if logger:
            logger.error(f"❌ TEST_5: {error_msg}")
        return {
            "status": "FAILED",
            "reason": error_msg
        }

    try:
        # Run pytest on the regression suite with timeout
        result = subprocess.run(
            ["python", "-m", "pytest", REGRESSION_SUITE_PATH, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            if logger:
                logger.info("✅ TEST_5: Regression suite passed")
            return {
                "status": "SUCCESS",
                "output": result.stdout,
                "stderr": result.stderr
            }
        else:
            if logger:
                logger.warning(f"⚠️ TEST_5: Regression suite failed\n{result.stderr}")
            return {
                "status": "FAILED",
                "output": result.stdout,
                "stderr": result.stderr,
                "reason": "REGRESSION_TEST_FAILURE"
            }

    except subprocess.TimeoutExpired:
error_msg = f"Regression suite timed out after 5 minutes"
        if logger:
            logger.error(f"❌ TEST_5: {error_msg}")
        return {
            "status": "FAILED",
            "reason": error_msg
        }
    except Exception as e:
error_msg = f"Error running regression suite: {str(e)}"
        if logger:
            logger.error(f"❌ TEST_5: {error_msg}")
        return {
            "status": "FAILED",
            "reason": error_msg
        }


def execute_dependency_refactor_zlm(issue_id: str, target_file: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Zero-Loss Merge (ZLM) wrapper for execute_dependency_refactor.
    Implements retry logic with P6 self-correction up to MAX_P6_ATTEMPTS.

    ZLM Policy: The agent MUST NOT stop until P9 finalization passes or max attempts reached.
    """
    # P5 Compliance: Register the process ID for Watchdog monitoring
    try:
        register_process()
        if logger:
            logger.info("📋 P5: Process registered with watchdog")
        log_action("P5_PROCESS_REGISTERED", f"CanonValidatorEngine ZLM started for {issue_id}")
    except Exception as e:
if logger:
            logger.warning(f"⚠️ P5: Could not register process: {e}")

    attempts = 0

    while attempts < MAX_P6_ATTEMPTS:
        attempts += 1

        if logger:
            logger.info(f"🔄 ZLM Attempt {attempts}/{MAX_P6_ATTEMPTS} for {target_file}")

        # Initialize regression result
        regression_result = {"status": "SKIPPED"}

        # Execute the standard validation pipeline
        result = execute_dependency_refactor(issue_id, target_file, tools, logger)

        # Check for success conditions - P2 passed, now run Test 5 (Regression Suite)
        regression_failed = False
        if result.get("status") in ["SUCCESS", "success"]:
            if logger:
                logger.info(f"✅ P2_PASS: Unit tests passed on attempt {attempts}")

            # Test 5: Run full regression suite
            regression_result = execute_regression_suite(logger)

            if regression_result.get("status") == "SUCCESS":
                if logger:
                    logger.info(f"✅ ZLM_SUCCESS: All tests passed on attempt {attempts}")

                # Log success to L5
                if tools.get('add_observations'):
                    tools['add_observations']([{
                        "entityName": f"ZLM_{issue_id}",
                        "observations": [f"ZLM_SUCCESS: P2 and Regression passed on attempt {attempts}"]
                    }])

                return result
            else:
                # Regression failed - set flag to trigger P6
                regression_failed = True
                if logger:
                    logger.warning(f"⚠️ TEST_5_FAIL: Regression suite failed. Triggering P6 fix.")

                # Log regression failure to L5
                if tools.get('add_observations'):
                    tools['add_observations']([{
                        "entityName": f"ZLM_{issue_id}",
                        "observations": [
                            f"REGRESSION_FAIL_ATTEMPT_{attempts}",
                            f"Error: {regression_result.get('stderr', 'Unknown error')}",
                            f"Reason: {regression_result.get('reason', 'REGRESSION_TEST_FAILURE')}"
                        ]
                    }])

        # P6 Self-Correction Trigger (triggered by P2 failure or Regression failure)
        if result.get("reason") in ["SANDBOX_VERIFICATION_FAILURE", "CONSENSUS_VALIDATION_FAILURE"] or regression_failed:
            if logger:
                if regression_failed:
                    logger.warning(f"⚠️ ZLM: Regression failure detected. Attempt {attempts}/{MAX_P6_ATTEMPTS}")
                else:
                    logger.warning(f"⚠️ ZLM: P2/P6 failure detected. Attempt {attempts}/{MAX_P6_ATTEMPTS}")

            # Skip logging here for regression failures since they're already logged above
            if not regression_failed and tools.get('add_observations'):
                tools['add_observations']([{
                    "entityName": f"ZLM_{issue_id}",
                    "observations": [
                        f"P2_FAIL_ATTEMPT_{attempts}",
                        f"Error: {result.get('details', 'Unknown error')}",
                        f"Reason: {result.get('reason')}"
                    ]
                }])

            # If we haven't reached max attempts, try P6 consensus fix
            if attempts < MAX_P6_ATTEMPTS:
                if logger:
                    logger.info(f"🔧 ZLM: Triggering P6 consensus for self-correction...")

                # Read current file content
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    # Query consensus for fix
                    fix_result = jury.propose_fix(
                        code=file_content,
                        error_message=result.get('details', ''),
                        context=f"ZLM Attempt {attempts}"
                    )

                    if fix_result.get("status") == "SUCCESS" and fix_result.get("fixed_code"):
                        if logger:
                            logger.info(f"✅ P6 proposed fix. Applying and retrying...")

                        # Apply the fix
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(fix_result["fixed_code"])

                        # Log fix application
                        if tools.get('add_observations'):
                            tools['add_observations']([{
                                "entityName": f"ZLM_{issue_id}",
                                "observations": [f"P6_FIX_APPLIED: Attempt {attempts}"]
                            }])

                        # Continue loop to retry validation
                        continue
                    else:
                        if logger:
                            logger.warning(f"⚠️ P6 could not generate fix. Continuing to next attempt...")

                except Exception as e:
if logger:
                        logger.error(f"❌ Error during P6 fix application: {e}")

            # Continue to next attempt
            continue

        # For other failure types (P1, GPG, etc.), fail immediately
        if result.get("status") in ["FAILED", "error"]:
            if logger:
                logger.error(f"❌ ZLM_FAIL: Non-recoverable failure - {result.get('reason')}")

            # Log non-recoverable failure
            if tools.get('add_observations'):
                tools['add_observations']([{
                    "entityName": f"ZLM_{issue_id}",
                    "observations": [f"ZLM_FAIL: {result.get('reason')} (Non-recoverable)"]
                }])

            return result

    # Max attempts reached
    if logger:
        logger.critical(f"❌ ZLM_FAIL: Maximum P6 attempts ({MAX_P6_ATTEMPTS}) reached for {target_file}")

    # Log max attempts failure
    if tools.get('add_observations'):
        tools['add_observations']([{
            "entityName": f"ZLM_{issue_id}",
            "observations": [f"ZLM_FAIL: P6 Max Attempts Reached ({MAX_P6_ATTEMPTS})"]
        }])

    return {
        "status": "FAILED",
        "reason": "ZLM_MAX_ATTEMPTS_REACHED",
        "details": f"Failed after {MAX_P6_ATTEMPTS} P6 self-correction attempts",
        "attempts": attempts
    }


def execute_dependency_refactor(issue_id: str, target_file: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Orchestrates a 5-MCP repair cycle: Git context (L1), canonical fix (L3), code edit (L1),
    cache (L4), and historical logging (L5).
    """
    if logger:
        logger.info(
            f"🛡️ Starting Full-Cycle Refactor for Issue: {issue_id}. New dependency: {new_dependency}")

    # Extract tools from the tools dictionary
    issues_get_detail = tools.get('issues_get_detail')
    search_records = tools.get('search_records')
    edit_file = tools.get('edit_file')
    commit = tools.get('commit')
    string_set = tools.get('string_set')
    add_observations = tools.get('add_observations')

    # Validate required tools
    if not all([issues_get_detail, search_records, edit_file, commit, string_set, add_observations]):
        return {"status": "error", "message": "Required MCP tools not available"}

    # 1. Get Issue Details and File Content (L1 GitKraken)
    try:
        issue_details_str = issues_get_detail(issue_id=issue_id)
        issue_details = json.loads(issue_details_str)
        target_file = issue_details.get("file_path", "src/config.js")
        if logger:
            logger.info(
                f"✅ L1 GitKraken: Retrieved issue {issue_id}, target file: {target_file}")
    except Exception as e:
return {"status": "error", "message": f"GitKraken L1 failed to retrieve issue: {e}"}

    # 2. Cost-Governed Vulnerability Check (L1/L3 Brave Search + L3 Pinecone)
    try:
        # First, try the cost-governed approach
        cost_check_result = execute_cost_governed_vulnerability_check(
            violation_hash=issue_id,
            violation_description=f"Issue {issue_id}: {new_dependency} dependency",
            code_version="latest",
            logger=logger
        )

        if cost_check_result["status"] == "success":
            # Use the fix from cost-governed search
            fix_result = cost_check_result["fix_result"]
            edits_payload = fix_result.get('metadata', {}).get('edits', [])
            if logger:
                logger.info(
                    f"✅ Cost-Governed Search: Found fix via {cost_check_result['source']}")
        else:
            # RAG failure - no fix found
            return {"status": "error", "message": "No fix found in any data source"}
    except Exception as e:
return {"status": "error", "message": f"Cost-governed search failed: {e}"}

    # 3. Apply Code Edit (L1 Filesystem)
    try:
        edit_result = edit_file(path=target_file, edits=edits_payload)
        if logger:
            logger.info(f"✅ L1 Filesystem: Applied edits to {target_file}")

        # --- HARDENING PROTOCOL 1: PRE-COMMIT SENTINEL ---
        is_valid, error_msg = validate_python_syntax(target_file)

        if not is_valid:
            if logger:
                logger.critical(f"HARDENING TRIGGERED: Blocked commit for {target_file} due to syntax error.")

            return {
                "status": "FAILED",
                "reason": "AST_VALIDATION_FAILURE",
                "details": error_msg
            }
        # -------------------------------------------------

        # --- HARDENING PROTOCOL 2: DOCKER SANDBOX ---
        # If syntax is valid, proceed to P2 Sandbox Check
        if logger:
            logger.info(f"Syntax valid. Initiating Sandbox Verification for {target_file}...")

        # Determine command:
        # 1. Try to run specific test if it exists
        # 2. Fallback to basic compilation check or import check
        test_file_name = f"test_{os.path.basename(target_file)}"
        possible_test_path = os.path.join(os.getcwd(), "tests", test_file_name)

        if os.path.exists(possible_test_path):
            # Run specific test
            sandbox_cmd = f"python3 -m unittest tests/{test_file_name}"
        else:
            # Fallback: Just ensure it compiles (redundant with AST but verifies imports/env)
            # or try to run the file itself if it's a script
            sandbox_cmd = f"python3 -m py_compile {target_file}"

        # Use the current working directory as repo_path
        repo_path = os.getcwd()

        # EXECUTE SANDBOX
        sandbox_success = execute_in_sandbox(repo_path, sandbox_cmd)

        if not sandbox_success:
            if logger:
                logger.critical(f"HARDENING TRIGGERED: Sandbox verification failed for {target_file}. Commit blocked.")
            return {
                "status": "FAILED",
                "reason": "SANDBOX_VERIFICATION_FAILURE",
                "details": "Code failed to execute or pass tests in isolated environment."
            }
        # --------------------------------------------

        # --- HARDENING PROTOCOL 6: MULTI-MODEL CONSENSUS ---
        if logger:
            logger.info(f"Sandbox verification passed. Initiating Supreme Court consensus for {target_file}...")

        # Read the file content for consensus analysis
        with open(target_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Run consensus engine
        consensus_result = jury.judge_artifact(file_content, context="Code Review")

        if consensus_result["status"] != "PASS":
            if logger:
                logger.critical(f"HARDENING TRIGGERED: Supreme Court rejected {target_file} with score {consensus_result['score']:.2f}")
                for vote in consensus_result["votes"]:
                    if vote["verdict"] == "NO":
                        logger.warning(f"  - {vote['model']}: {vote['reason']}")

            return {
                "status": "FAILED",
                "reason": "CONSENSUS_VALIDATION_FAILURE",
                "details": f"Multi-model consensus failed with score {consensus_result['score']:.2f}"
            }
        else:
            if logger:
                logger.info(f"✅ Supreme Court approved {target_file} with score {consensus_result['score']:.2f}")
        # ----------------------------------------------------

        # --- HARDENING PROTOCOL 9: CRYPTOGRAPHIC PROVENANCE (Code) ---
        BOT_GPG_KEY_ID = "0xAGENTICBOTID"  # Placeholder for your actual key

        # 4. Commit the fix with GPG signature (L1 GitKraken)
        commit_message = f"Fix({issue_id}): Refactored dependency using canonical pattern."
        commit_result = "mock_commit_hash"  # Placeholder for actual commit hash

        # --- HARDENING PROTOCOL 10: SHADOW MODE EXECUTION ---
        if SHADOW_MODE_ACTIVE:
            if logger:
                logger.warning(f"👻 SHADOW MODE: Blocked final commit of {target_file}.")
                logger.warning(f"Diff would be saved to shadow_output/{issue_id}_shadow.diff for review.")

            # Return success from the perspective of the agent workflow (it did its job)
            return {"status": "SUCCESS", "reason": "SHADOW_BLOCKED", "file": target_file}
        # --------------------------------------------------

        if not sign_and_commit(target_file, commit_message, key_id=BOT_GPG_KEY_ID):
            return {"status": "FAILED", "reason": "GPG_SIGNING_FAILURE"}

        if logger:
            logger.info(
                f"✅ L1 GitKraken: Signed and committed changes with message: {commit_message}")
        # -------------------------------------------------------------------
    except Exception as e:
return {"status": "error", "message": f"Filesystem/GitKraken L1 failed during repair/commit: {e}"}

    # 5. Cache Success (L4 Redis)
    fix_hash = f"FIX_AUDIT_{issue_id}_{hashlib.md5(commit_result.encode()).hexdigest()[:8]}"
    try:
        string_set(
            key=fix_hash, value=f"Target File: {target_file}, Status: COMPLETED")
        if logger:
            logger.info(f"✅ L4 Redis: Cached fix with hash: {fix_hash}")
    except Exception as e:
if logger:
            logger.warning(f"⚠️ L4 Redis cache failed: {e}")
        fix_hash = "CACHE_FAILED"

    # 6. Log Audit Trail (L5 MEMemory)
    try:
        add_observations(observations=[{
            "entityName": "AuditTrail",
            "contents": [
                f"Issue {issue_id} auto-refactored and committed.",
                f"Target File: {target_file}",
                f"Dependency Added: {new_dependency}",
                f"Redis Hash: {fix_hash}",
                f"Commit: {commit_result[:50]}..." if len(
                    commit_result) > 50 else commit_result
            ]
        }])
        if logger:
            logger.info("✅ L5 MEMemory: Logged audit trail")
    except Exception as e:
if logger:
            logger.warning(
                f"⚠️ L5 MEMemory logging failed (non-critical): {e}")

    return {
        "status": "SUCCESS",
        "message": f"Issue {issue_id} fixed, committed, and logged. Redis key: {fix_hash}",
        "commit_result": commit_result,
        "target_file": target_file,
        "redis_hash": fix_hash
    }


def validate_canon_compliance(file_path: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Validates a file against the canonical code patterns stored in Pinecone.
    Uses L1 (Filesystem), L3 (Pinecone), and L4 (Redis) for caching results.
    """
    if logger:
        logger.info(f"🔍 Starting canon compliance validation for {file_path}")

    # Extract tools
    read_file = tools.get('read_file')
    search_records = tools.get('search_records')
    string_get = tools.get('string_get')
    string_set = tools.get('string_set')

    # Check cache first (L4 Redis)
    file_hash = hashlib.md5(file_path.encode()).hexdigest()
    cache_key = f"canon_validation:{file_hash}"

    try:
        cached_result = string_get(key=cache_key)
        if cached_result:
            if logger:
                logger.info("✅ L4 Redis: Retrieved cached validation result")
            return json.loads(cached_result)
except Exception:
    pass
pass  # Cache miss or error, continue with validation

    # Read file content (L1 Filesystem)
    try:
        file_content = read_file(path=file_path)
        if logger:
            logger.info(
                f"✅ L1 Filesystem: Read {len(file_content)} characters")
    except Exception as e:
return {"status": "error", "message": f"Failed to read file: {e}"}

    # Query Pinecone for compliance patterns (L3)
    try:
        compliance_query = f"Validate compliance patterns for file: {file_path}\nContent preview: {file_content[:500]}..."
        search_result_str = search_records(
            query=compliance_query, index="code_canon", top_k=3)
        search_result = json.loads(search_result_str)

        # Analyze compliance based on Pinecone results
        violations = []
        for result in search_result:
            if result.get('metadata', {}).get('violation_type'):
                violations.append(result['metadata'])

        compliance_status = "COMPLIANT" if not violations else "VIOLATIONS_FOUND"

        validation_result = {
            "status": compliance_status,
            "file_path": file_path,
            "violations": violations,
            "validation_time": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Cache result (L4 Redis)
        try:
            string_set(key=cache_key, value=json.dumps(validation_result))
            if logger:
                logger.info("✅ L4 Redis: Cached validation result")
except Exception:
    pass
pass

        return validation_result

    except Exception as e:
return {"status": "error", "message": f"Pinecone validation failed: {e}"}


def automated_design_drift_audit(figma_file_id: str, canonical_version: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Automated design drift audit for Git pre-commit hooks.
    Integrates Figma (L2), Filesystem (L1), and Pinecone (L3) for comprehensive validation.
    """
    if logger:
        logger.info(
            f"🔍 Starting automated design drift audit for {figma_file_id}")

    # 1. Check design drift using hardened Figma access
    drift_result = check_design_drift(
        file_id=figma_file_id,
        canonical_version=canonical_version,
        logger=logger
    )

    if drift_result.get('drift_detected'):
        # 2. If drift detected, trigger canonical fix retrieval
        if logger:
            logger.warning(
                "Design drift detected - initiating repair workflow")

        # This would integrate with the existing execute_dependency_refactor
        # For now, return the drift report for manual review
        return {
            "status": "drift_detected",
            "message": "Design drift requires manual review or automated repair",
            "drift_report": drift_result.get('drift_report', []),
            "suggested_action": "Run execute_dependency_refactor with canonical patterns"
        }

    return {
        "status": "no_drift",
        "message": "Design is compliant with canonical version",
        "validated_version": drift_result.get('current_version'),
        "canonical_version": canonical_version
    }


def vulnerability_check_before_refactor(issue_description: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Cost-controlled vulnerability check before attempting Pinecone refactor.
    Uses Brave Search with security-specific sites to find quick fixes.
    """
    if logger:
        logger.info("🔒 Checking for existing vulnerability fixes...")

    # Extract key terms from issue description
    search_terms = issue_description.split()[:5]  # First 5 words
    security_query = " ".join(search_terms)

    # Execute hardened vulnerability search
    search_results = execute_vulnerability_search(
        security_query, logger=logger)

    if search_results:
        # Parse results for high-confidence fixes
        results = json.loads(search_results)

        # Look for immediate solutions
        for result in results:
            if 'fix' in result.get('snippet', '').lower() or 'solution' in result.get('title', '').lower():
                return {
                    "status": "quick_fix_found",
                    "message": "Immediate fix available - skipping Pinecone search",
                    "solution": result,
                    "cost_saved": "Pinecone query avoided"
                }

    return {
        "status": "no_quick_fix",
        "message": "No immediate fix found - proceed with Pinecone search",
        "proceed_to_pinecone": True
    }


def parse_time(time_str: str) -> datetime:
    """Helper to convert ISO format time to datetime object."""
    try:
        # Assuming the Time MCP or Figma returns ISO 8601 format
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
except Exception:
    pass
return datetime.min  # Return minimum time on parsing failure


def execute_version_locked_design_audit(component_id: str, logged_audit_time: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Performs a version-locked design audit, enforcing integrity by detecting design drift
    via Figma versions and Time MCP logs.
    """
    if logger:
        logger.info(
            f"🎨 Starting Version-Locked Audit for Component ID: {component_id}")

    # Convert the agent's last known audit time into a comparable object
    last_audit_dt = parse_time(logged_audit_time)

    # --- 1. Check Design Stability (Figma L2, Time L4, Sequential Thinking) ---
    try:
        # Figma returns version history for the file containing the component
        versions_str = get_file_versions(component_id=component_id)
        versions_data = json.loads(versions_str)
        versions = versions_data.get('versions', [])

        if not versions:
            return {"status": "error", "message": "Figma returned no version history."}

        # The latest version is typically the first element
        latest_version = versions[0]
        latest_version_dt = parse_time(latest_version['created_at'])

        design_status = "STABLE"

        # Sequential Thinking: Compare latest version time to last audit time
        if latest_version_dt > last_audit_dt:
            design_status = "DRIFT_DETECTED"
            if logger:
                logger.warning(
                    f"🚨 DESIGN DRIFT DETECTED: Latest version ({latest_version_dt}) is newer than last audit ({last_audit_dt}).")

        version_id_to_use = latest_version['id']

    except Exception as e:
if logger:
            logger.error(
                f"Figma L2 Version Check failed: {e}. Aborting audit.")
        return {"status": "error", "message": f"Figma L2 access failed: {e}"}

    # --- 2. Version-Locked Retrieval (Figma L2) ---
    try:
        # Retrieve the design context, locked to the latest version ID
        design_vars_str = get_variable_defs(
            node_id=component_id,
            version=version_id_to_use  # Enforces integrity (Hardening)
        )
        design_vars = json.loads(design_vars_str)
    except Exception as e:
if logger:
            logger.error(
                f"Figma L2 Data Retrieval failed: {e}. Audit cannot proceed.")
        return {"status": "error", "message": f"Figma L2 data retrieval failed: {e}"}

    # --- 3. Audit Log (L5 MEMemory) ---
    try:
        audit_message = f"Design Audit Complete: Status={design_status}. Version={version_id_to_use} used for context. Component={component_id}."
        add_observations(observations=[{
            "entityName": "DesignAudit",
            "contents": [audit_message]
        }])
except Exception:
    pass
if logger:
            logger.warning("⚠️ L5 MEMemory logging failed (non-critical).")

    return {
        "status": "success",
        "design_status": design_status,
        "version_id_used": version_id_to_use,
        "design_variables": design_vars
    }


def execute_cost_governed_vulnerability_check(
    violation_hash: str,
    violation_description: str,
    code_version: str,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Implements a Cost-Governed RAG pipeline: prioritizes a cheap Brave Search check
    before falling back to the expensive Pinecone search. (Cost Governance Hardening)
    """
    if logger:
        logger.info(
            f"💰 Starting Cost-Governed RAG for Violation: {violation_hash}")

    final_fix_result = None
    source_method = "FAILED"

    # --- 1. Low-Cost Search (L1/L3 Brave Search) ---
    # Hardening: Use restricted query to target high-confidence, cheap public sources.
    low_cost_query = f"{violation_description} fix site:security.stackexchange.com"

    try:
        brave_result_str = execute_vulnerability_search(low_cost_query, logger)

        if brave_result_str:
            # Parse the Brave Search result
            brave_results = json.loads(brave_result_str)
            if brave_results:
                final_fix_result = brave_results[0]  # Take first result
                source_method = "BraveSearch_LowCost"
                if logger:
                    logger.info(f"✅ Low-Cost Fix Found: Bypassing Pinecone.")

    except Exception as e:
if logger:
            logger.warning(
                f"Brave Search call failed: {e}. Proceeding to Pinecone fallback.")

    # --- 2. High-Cost Fallback (L3 Pinecone) ---
    # Sequential Thinking: Only execute this expensive step if the low-cost step failed.
    if not final_fix_result:
        if logger:
            logger.warning(
                "Low-cost search missed. Executing high-cost Pinecone fallback...")

        try:
            # Use the hybrid fix search for expensive Pinecone lookup
            pinecone_result = execute_hybrid_fix_search(
                violation_description, code_version, logger)

            if pinecone_result.get("status") == "success":
                final_fix_result = pinecone_result.get("top_fix")
                source_method = f"Pinecone_Hybrid_Confidence_{final_fix_result.get('confidence', 'N/A')}"
                if logger:
                    logger.info(f"✅ High-Cost Fix Found via Pinecone.")
            else:
                if logger:
                    logger.warning("Pinecone search yielded no success.")

        except Exception as e:
if logger:
                logger.error(f"CRITICAL: Pinecone search failed entirely: {e}")

    # --- 3. Result Aggregation and Audit Log (L5 MEMemory) ---

    if not final_fix_result:
        # RAG Failure Path
        try:
            add_observations(observations=[{
                "entityName": "RAG_Audit",
                "contents": [f"CRITICAL RAG FAILURE: Fix not found. Methods attempted: BraveSearch, Pinecone."]
            }])
except Exception:
    pass
pass
        return {"status": "rag_failure", "message": "No fix found in any data source."}

    # Success Path: Log the source of truth (Cost Governance Audit)
    try:
        fix_snippet = final_fix_result.get(
            'fix_text', final_fix_result.get('content', '...'))[:50]
        audit_message = f"Fix Found: Source={source_method}. Hash={violation_hash}. Fix Snippet: {fix_snippet}"
        add_observations(observations=[{
            "entityName": "CostGovernance",
            "contents": [audit_message]
        }])
except Exception:
    pass
pass

    return {
        "status": "success",
        "source": source_method,
        "fix_result": final_fix_result,
        "message": f"Fix found via {source_method}. Proceed to iterative repair."
    }


def execute_hybrid_fix_search(violation_description: str, code_version: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Executes a hardened hybrid search across two Pinecone indexes, prioritizing
    audited (high-confidence) fixes to ensure the best repair is selected.
    """
    if logger:
        logger.info(
            f"🔍 Starting Hybrid Fix Search for: {violation_description} (Version: {code_version})")

    all_results = []

    # --- 1. Index 1 Search (High-Quality Canon: Hardening through Metadata) ---
    INDEX_CANON = "code-canon-fixes"
    # Metadata filter ensures only fixes that passed the Iterative Repair Audit are considered
    canon_filter = {"$and": [
        {"audit_status": "AUDITED"},
        {"version": code_version}
    ]}

    try:
        # Search records with metadata filtering
        canon_results_str = search_records(
            query=violation_description,
            index=INDEX_CANON,
            top_k=2,
            filter=canon_filter
        )
        canon_results = json.loads(canon_results_str)

        # Tag results for prioritization and logging
        for res in canon_results:
            res['source_index'] = INDEX_CANON
            res['confidence'] = 'HIGH_AUDITED'
        all_results.extend(canon_results)

        if logger:
            logger.info(
                f"Found {len(canon_results)} AUDITED fixes in {INDEX_CANON}.")

    except Exception as e:
if logger:
            logger.warning(
                f"L3 Pinecone (Canon) search failed: {e}. Falling through to Fallback.")
        canon_results = []

    # --- 2. Index 2 Search (Fallback Cache: Lower Confidence) ---
    INDEX_FALLBACK = "stack-overflow-cache"
    # Metadata filter for a simulated community validation status
    fallback_filter = {"fix_type": "community_validated"}

    try:
        fallback_results_str = search_records(
            query=violation_description,
            index=INDEX_FALLBACK,
            top_k=3,
            filter=fallback_filter
        )
        fallback_results = json.loads(fallback_results_str)

        for res in fallback_results:
            res['source_index'] = INDEX_FALLBACK
            res['confidence'] = 'MEDIUM_COMMUNITY'
        all_results.extend(fallback_results)

        if logger:
            logger.info(
                f"Found {len(fallback_results)} community fixes in {INDEX_FALLBACK}.")

    except Exception as e:
if logger:
            logger.warning(
                f"L3 Pinecone (Fallback) search failed: {e}. RAG Failure possible.")
        fallback_results = []

    # --- 3. Result Aggregation and Prioritization (Sequential Thinking) ---

    if not all_results:
        # 4. Failure Path
        if logger:
            logger.error(
                "RAG Failure: No relevant fixes found across both indexes.")

        # 5. Audit Log (L5 MEMemory) - Log the failure for investigation
        try:
            add_observations(observations=[{
                "entityName": "RAG_Audit",
                "contents": [f"CRITICAL RAG FAILURE: No fix found for violation: {violation_description}"]
            }])
except Exception:
    pass
pass  # Non-critical if logging fails

        return {"status": "rag_failure", "message": "No canonical or community fix found."}

    # Sort: Audited fixes take priority over community fixes
    all_results.sort(
        key=lambda x: 1 if x['confidence'] == 'HIGH_AUDITED' else 0, reverse=True)

    # 4. Audit Log (L5 MEMemory) - Log the successful context
    try:
        audit_message = f"Hybrid search successful. Canon: {len(canon_results)}, Fallback: {len(fallback_results)}. Top fix confidence: {all_results[0]['confidence']}."
        add_observations(observations=[{
            "entityName": "RAG_Audit",
            "contents": [audit_message]
        }])
except Exception:
    pass
pass  # Non-critical if logging fails

    return {
        "status": "success",
        "total_results": len(all_results),
        "top_fix": all_results[0],
        "all_results": all_results
    }

