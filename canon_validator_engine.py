import time
import json
import hashlib
from typing import Dict, Any, Optional

def execute_dependency_refactor(issue_id: str, new_dependency: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Orchestrates a 5-MCP repair cycle: Git context (L1), canonical fix (L3), code edit (L1), 
    cache (L4), and historical logging (L5).
    """
    if logger:
        logger.info(f"🛡️ Starting Full-Cycle Refactor for Issue: {issue_id}. New dependency: {new_dependency}")

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
            logger.info(f"✅ L1 GitKraken: Retrieved issue {issue_id}, target file: {target_file}")
    except Exception as e:
        return {"status": "error", "message": f"GitKraken L1 failed to retrieve issue: {e}"}

    # 2. Retrieve Canonical Refactor Pattern (L3 Pinecone)
    refactor_query = f"Canonical pattern for adding dependency {new_dependency} and fixing issue {issue_id} in {target_file}"
    try:
        search_result_str = search_records(query=refactor_query, index="code_canon", top_k=1)
        search_result = json.loads(search_result_str)
        # Assuming result contains the necessary 'edits' JSON structure
        edits_payload = search_result[0].get('metadata', {}).get('edits', [])
        if not edits_payload:
            return {"status": "error", "message": "No canonical refactor pattern found in Pinecone"}
        if logger:
            logger.info(f"✅ L3 Pinecone: Retrieved canonical refactor pattern with {len(edits_payload)} edits")
    except Exception as e:
        return {"status": "error", "message": f"Pinecone L3 failed: {e}"}

    # 3. Apply Code Edit (L1 Filesystem)
    try:
        edit_result = edit_file(path=target_file, edits=edits_payload)
        if logger:
            logger.info(f"✅ L1 Filesystem: Applied edits to {target_file}")
        
        # 4. Commit the fix (L1 GitKraken)
        commit_message = f"Fix({issue_id}): Refactored dependency using canonical pattern."
        commit_result = commit(path=target_file, message=commit_message)
        if logger:
            logger.info(f"✅ L1 GitKraken: Committed changes with message: {commit_message}")
    except Exception as e:
        return {"status": "error", "message": f"Filesystem/GitKraken L1 failed during repair/commit: {e}"}

    # 5. Cache Success (L4 Redis)
    fix_hash = f"FIX_AUDIT_{issue_id}_{hashlib.md5(commit_result.encode()).hexdigest()[:8]}"
    try:
        string_set(key=fix_hash, value=f"Target File: {target_file}, Status: COMPLETED")
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
                f"Commit: {commit_result[:50]}..." if len(commit_result) > 50 else commit_result
            ]
        }])
        if logger:
            logger.info("✅ L5 MEMemory: Logged audit trail")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ L5 MEMemory logging failed (non-critical): {e}")

    return {
        "status": "refactor_complete",
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
    except:
        pass  # Cache miss or error, continue with validation

    # Read file content (L1 Filesystem)
    try:
        file_content = read_file(path=file_path)
        if logger:
            logger.info(f"✅ L1 Filesystem: Read {len(file_content)} characters")
    except Exception as e:
        return {"status": "error", "message": f"Failed to read file: {e}"}

    # Query Pinecone for compliance patterns (L3)
    try:
        compliance_query = f"Validate compliance patterns for file: {file_path}\nContent preview: {file_content[:500]}..."
        search_result_str = search_records(query=compliance_query, index="code_canon", top_k=3)
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
        except:
            pass
        
        return validation_result
        
    except Exception as e:
        return {"status": "error", "message": f"Pinecone validation failed: {e}"}
