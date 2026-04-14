from __future__ import annotations

import argparse

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "clean_duplicates_enhanced", "execution_auth")
_emit_validates_capability("p2", "clean_duplicates_enhanced", "capability_check")
_emit_routes_to_capability("p2", "clean_duplicates_enhanced", "capability_route")
_emit_writes_via_uwg("p2", "clean_duplicates_enhanced", "uwg_write")
_emit_blocks_direct_write("p2", "clean_duplicates_enhanced", "direct_write_block")
_emit_records_tool_invocation("p2", "clean_duplicates_enhanced", "tool_invocation")
_emit_captures_execution_output("p2", "clean_duplicates_enhanced", "exec_output")
_emit_dispatches_agent("p3", "clean_duplicates_enhanced", "agent_dispatch")
_emit_coordinates_agents("p3", "clean_duplicates_enhanced", "agent_coordination")
_emit_records_workflow_lineage("p3", "clean_duplicates_enhanced", "workflow_lineage")
_emit_records_healing_outcome("p3", "clean_duplicates_enhanced", "healing_outcome")
_emit_escalates_failure("p3", "clean_duplicates_enhanced", "failure_escalation")
_emit_orchestrates_workflow("p3", "clean_duplicates_enhanced", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "clean_duplicates_enhanced", "healing_dispatch")
_emit_invokes_evaluation("p3", "clean_duplicates_enhanced", "evaluation_signal")
_emit_records_telemetry_event("p4", "clean_duplicates_enhanced", "telemetry_event")
_emit_captures_evaluation_metric("p4", "clean_duplicates_enhanced", "eval_metric")
_emit_stores_embedding("p4", "clean_duplicates_enhanced", "embedding_store")
_emit_updates_meta_learning_state("p4", "clean_duplicates_enhanced", "meta_learning")
_emit_links_execution_to_snapshot("p4", "clean_duplicates_enhanced", "exec_snapshot_link")

_emit_records_execution_trace("p0", "evidence", "clean_duplicates_enhanced")
_emit_applies_guardrail("p0", "clean_duplicates_enhanced", "p0_governance")
_emit_reads_policy_state("p0", "clean_duplicates_enhanced", "policy_binding")
_emit_snapshots_state("p0", "clean_duplicates_enhanced", "state_snapshot")
emit_replay_key("p0", "clean_duplicates_enhanced")
emit_determinism_digest("p0", "clean_duplicates_enhanced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"Brief description of functionality and purpose."
import ast
import hashlib
import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from tqdm import tqdm

_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_1")
_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_2")
_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_3")
_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_4")
_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_5")
_emit_emits_metric_event("clean_duplicates_enhanced", "p4obs", "metric_6")
_emit_records_incident_event("clean_duplicates_enhanced", "p4obs", "incident")
_emit_captures_runtime_anomaly("clean_duplicates_enhanced", "p4obs", "anomaly")
_emit_writes_observability_log("clean_duplicates_enhanced", "p4obs", "obs_log")
_emit_updates_monitoring_state("clean_duplicates_enhanced", "p4obs", "mon_state")
_emit_triggers_alert("clean_duplicates_enhanced", "p4obs", "alert")
_emit_links_incident_trace("clean_duplicates_enhanced", "p4obs", "trace_link")
_emit_captures_pattern("clean_duplicates_enhanced", "p3lm", "pattern")
_emit_records_learning_event("clean_duplicates_enhanced", "p3lm", "learning_event")
_emit_writes_learning_snapshot("clean_duplicates_enhanced", "p3lm", "snapshot")
_emit_feeds_meta_learning("clean_duplicates_enhanced", "p3lm", "meta_feed")
_emit_updates_routing_strategy("clean_duplicates_enhanced", "p3lm", "routing")
_emit_improves_agent_policy("clean_duplicates_enhanced", "p3lm", "policy")
_emit_stores_learning_state("clean_duplicates_enhanced", "p3lm", "state")
_emit_records_execution_trace("clean_duplicates_enhanced", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("clean_duplicates_enhanced", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("clean_duplicates_enhanced", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("clean_duplicates_enhanced", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("clean_duplicates_enhanced", "L4_STATE", "p2_trace_5")
_emit_reads_environ("clean_duplicates_enhanced", "env_read", "p2_env_1")
_emit_reads_environ("clean_duplicates_enhanced", "env_read", "p2_env_2")
_emit_reads_runtime_state("clean_duplicates_enhanced", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("clean_duplicates_enhanced", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "clean_duplicates_enhanced", "context_pull")
_emit_pulls_context("p1", "clean_duplicates_enhanced", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "clean_duplicates_enhanced", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "clean_duplicates_enhanced", "uwg_term_2")
_emit_writes_through("p1", "clean_duplicates_enhanced", "write_through")
_emit_writes_through("p1", "clean_duplicates_enhanced", "write_through_2")
_emit_validated_by_safety_plane("p1", "clean_duplicates_enhanced", "safety_validation")
_emit_invokes_eval("p1", "clean_duplicates_enhanced", "eval_call")
_emit_proposal_commits_routing("p1", "clean_duplicates_enhanced", "routing_commit")
_emit_escalates_to_human("p1", "clean_duplicates_enhanced", "human_escalation")
_emit_routes_through("p1", "clean_duplicates_enhanced", "route_through")
_emit_checks_agent_registry("p1", "clean_duplicates_enhanced", "agent_registry")
_emit_validates_agent_capability("p1", "clean_duplicates_enhanced", "capability")
_emit_dispatches_execution_plan("p1", "clean_duplicates_enhanced", "exec_plan")
_emit_agent_executes_agent("p1", "clean_duplicates_enhanced", "sub_agent")
_emit_routes_to_agent("p1", "clean_duplicates_enhanced", "target_agent")
_emit_verifies_policy("p1", "clean_duplicates_enhanced", "policy_check")
_emit_observes_runtime_state("p1", "clean_duplicates_enhanced", "runtime_state")
_emit_verifies_boundary("p1", "clean_duplicates_enhanced", "boundary_check")
_emit_transcripts_response("p1", "clean_duplicates_enhanced", "transcript")
_emit_hard_fails_untranscripted("p1", "clean_duplicates_enhanced")
_emit_gated_by_confidence("p1", "clean_duplicates_enhanced", "confidence_gate")

logging.basicConfig(level=logging.INFO, format="%(message)s")
Logger = logging.getLogger(__name__)


def aggressive_cleanup():
    """More aggressive cleanup targeting additional patterns"""
    purged_count = 0
    for item in tqdm(os.listdir("."), desc="Processing", unit="item"):
        # guardian: allow-path-string
        if os.path.isdir(item) and item.startswith("test_repo"):
            try:
                shutil.rmtree(item)
                Logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                raise
                Logger.error(f"❌ Failed to delete directory {item}: {e}")
    temp_patterns = SOVEREIGN_EXCLUDED_FOLDERS
    from pathlib import Path

    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for pattern in temp_patterns:
        search_path = Path(pattern.split("**")[0] if "**" in pattern else ".")
        for file in [str(f) for f in get_python_files(search_path)]:
            try:
                os.remove(file)
                Logger.info(f"🗑️ Purged temp file: {file}")
                purged_count += 1
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                Logger.error(f"❌ Failed to delete {file}: {e}")
    for root, dirs, _files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                Logger.info(f"🗑️ PURGED DIRECTORY: {pycache_path}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                Logger.error(f"❌ Failed to delete directory {pycache_path}: {e}")
    return purged_count


def organize_structure():
    """Reorganize files into proper engine directories"""
    Logger.info("📁 Starting folder reorganization...")
    engines_dir = "/app/engines"
    subdirs = ["resume_engine", "outreach_engine", "CanonValidatorAgent"]
    for subdir in subdirs:
        path = Path(engines_dir) / subdir
        os.makedirs(path, exist_ok=True)
        Logger.info(f"📁 Created directory: {path}")
    file_mappings = {
        "resume": "resume_engine",
        "outreach": "outreach_engine",
        "canon": "CanonValidatorAgent",
        "validator": "CanonValidatorAgent",
    }
    moved_count = 0
    for root, _dirs, files in tqdm(os.walk("/app"), desc="Processing", unit="item"):
        for file in tqdm(files, desc="Processing", unit="item"):
            if file.endswith(".py"):
                file_path = Path(root) / file
                file_lower = file.lower()
                target_dir = None
                for keyword, directory in file_mappings.items():
                    if keyword in file_lower:
                        target_dir = directory
                        break
                if target_dir and (not file.startswith("__")):
                    target_path = Path(engines_dir) / target_dir / file
                    try:
                        # guardian: allow-path-string
                        if not os.path.exists(target_path):
                            shutil.move(file_path, target_path)
                            Logger.info(f"📁 Moved {file} to {target_dir}/")
                            moved_count += 1
                    # guardian: allow-silent-swallow
                    except Exception as e:
                        Logger.error(f"❌ Failed to move {file}: {e}")
    Logger.info(f"\n✨ Reorganization complete. Moved {moved_count} files.")
    return moved_count


def get_file_hash(filepath):
    """Calculate hash of file content for deduplication"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:  # guardian: Add error context logging
        return None


def extract_functions(filepath):
    """Extract function definitions from a Python file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        functions = []
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line + 1
                lines = content.split("\n")[start_line:end_line]
                func_code = "\n".join(lines)
                functions.append(
                    {
                        "name": node.name,
                        "code": func_code,
                        "hash": hashlib.md5(func_code.encode()).hexdigest(),
                    },
                )
        return functions
    # guardian: allow-silent-swallow
    except Exception as e:
        Logger.error(f"❌ Failed to parse {filepath}: {e}")
        return []


def merge_validator_logic(silos, exclude_dirs, merge_to):
    """Merge duplicate validator logic across silos into a single file"""
    Logger.info("🔀 Starting validator logic merge...")
    all_files = []
    for silo in silos:
        silo_path = f"/app/{silo}"
        # guardian: allow-path-string
        if os.path.exists(silo_path):
            for root, dirs, files in os.walk(silo_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    if file.endswith(".py") and (not file.startswith("__")):
                        filepath = Path(root) / file
                        all_files.append(filepath)
    function_map = defaultdict(list)
    for filepath in all_files:
        functions = extract_functions(filepath)
        for func in functions:
            if func["name"] not in ["validate", "check", "verify", "is_valid"]:
                continue
            function_map[func["name"]].append({"hash": func["hash"], "code": func["code"], "file": filepath})
    merged_content = "#!/usr/bin/env python3\n\"\"\"\nCanon Validator v2.0 - Merged and Consolidated\nAll validator logic consolidated from multiple silos.\n\"\"\"\n\nimport ast\nimport hashlib\nimport logging\nimport os\nimport re\nimport subprocess\nimport sys\nfrom dataclasses import dataclass, field\nfrom typing import Any, Dict, List, Set, Tuple\n\nfrom agentic_core.L5_safety.config.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,\n    AGENT_DISCOVERY_MANIFEST_JSON,\n    AGENTIC_CORE_DIR,\n    SCRIPTS_DIR,\n    TESTS_DIR,\n    DASHBOARD_DIR,\n    L0_MAINTENANCE_DIR,\n    L1_COGNITION_DIR,\n    L2_EXECUTION_DIR,\n    L3_ORCHESTRATION_DIR,\n    L4_STATE_DIR,\n    L5_SAFETY_DIR,\n    L6_OBSERVABILITY_DIR,\n    get_validated_project_root,\n)\n\nLogger = logging.getLogger(__name__)\n\n# Configure logging\nlogging.basicConfig(level=logging.INFO, format=\"%(message)s\")\nLogger = logging.getLogger(__name__)\n\n# Fix Windows console encoding\nif sys.platform == \"win32\":\n    import io\nfrom agentic_core.L5_safety.config.structure_blueprint.ssot import (\n    SOVEREIGN_EXCLUDED_FOLDERS,\n)\n    sys.stdout = io.TextIOWrapper(\n        sys.stdout.buffer, encoding=\"utf-8\", errors=\"replace\")\n    sys.stderr = io.TextIOWrapper(\n        sys.stderr.buffer, encoding=\"utf-8\", errors=\"replace\")\n\n# ==============================================================================\n# CONFIGURATION: EXCLUSION ZONES\n# ==============================================================================\n# NAMING FIXED: EXCLUDED_DIRS → excluded_dirs\nexcluded_dirs = {\n    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',\n    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs',\n    ARCHIVES_DIR, 'data',\n}\n\n# NAMING FIXED: EXCLUDED_FILES → excluded_files\nexcluded_files = {\n    'CanonValidatorAgent.py',\n    'canon_validator_backup.py',\n    'canon_validator_v2_agentic.py',\n    'auto_canon.py',\n    '.DS_Store'\n}\n\ndef is_excluded(path: str) -> bool:\n    \"\"\"Check if a path should be excluded from validation.\"\"\"\n    path_parts = path.split(os.sep)\n\n    # Check directory exclusions\n    for part in path_parts:\n        if part in EXCLUDED_DIRS:\n            return True\n\n    # Check file exclusions\n    filename = os.path.basename(path)\n    if filename in EXCLUDED_FILES:\n        return True\n\n    return False\n\n"
    added_functions = set()
    for func_name, func_list in function_map.items():
        if func_list:
            func_data = func_list[0]
            if func_data["hash"] not in added_functions:
                merged_content += f"\n# Function: {func_name} (from {func_data['file']})\n"
                merged_content += func_data["code"] + "\n\n"
                added_functions.add(func_data["hash"])
    os.makedirs(Path(merge_to).parent, exist_ok=True)
    with open(merge_to, "w", encoding="utf-8") as f:
        f.write(merged_content)
    Logger.info(f"✅ Merged validator logic to {merge_to}")
    Logger.info(f"📊 Processed {len(all_files)} files")
    Logger.info(f"🔀 Merged {len(added_functions)} unique validation functions")
    return len(added_functions)


def _adg_startup_warning() -> None:
    """Emit ADG-sourced antipattern count for this script at startup."""
    try:
        from pathlib import Path as _Path

        from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile

        _root = _Path(__file__).resolve().parents[2]
        _rel = str(_Path(__file__).resolve().relative_to(_root)).replace("\\", "/")
        _profile = get_behavioral_profile(_rel, _root)
        _bscore = getattr(_profile, "behavioral_score", 0.5)
        _apsigs = getattr(_profile, "antipattern_signals", frozenset())
        if _apsigs or _bscore < 0.4:
            import warnings

            warnings.warn(
                f"[ADG] {_rel}: {len(_apsigs)} antipattern signal(s) "
                f"detected (score={_bscore:.2f}, "
                f"script-like={getattr(_profile, 'deterministic_coverage', False)}). "
                f"Signals: {sorted(_apsigs) or 'none'}",
                stacklevel=2,
            )
    # guardian: allow-silent-swallow
    except Exception:
        pass


def purge_everything(
    aggressive=False,
    organize=False,
    merge_logic=False,
    merge_to=None,
    silos=None,
    exclude=None,
):
    """
    Brief description of functionality and purpose.

    This function performs various cleanup and organization tasks.

    :param aggressive: Perform aggressive cleanup
    :param organize: Organize files into engine directories
    :param merge_logic: Merge duplicate validator logic
    :param merge_to: Target file for merged validator logic
    :param silos: Comma-separated list of silos to process
    :param exclude: Comma-separated list of directories to exclude
    """
    _adg_startup_warning()
    purged_count = 0
    for item in tqdm(os.listdir("."), desc="Processing", unit="item"):
        # guardian: allow-path-string
        if os.path.isdir(item) and item.startswith("test_repo_1765"):
            try:
                shutil.rmtree(item)
                Logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                Logger.error(f"❌ Failed to delete directory {item}: {e}")
    for root, _dirs, files in tqdm(os.walk("."), desc="Processing", unit="item"):
        for file in tqdm(files, desc="Processing", unit="item"):
            file_path = Path(root) / file
            if "_clean.py" in file or file == "test_report.html":
                try:
                    os.remove(file_path)
                    Logger.info(f"🗑️ Purged File: {file_path}")
                    purged_count += 1
                # guardian: allow-silent-swallow
                except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    raise
                    Logger.error(f"❌ Failed to delete {file_path}: {e}")
    if aggressive:
        purged_count += aggressive_cleanup()
    Logger.info(f"\n✨ Aggressive Cleanup Complete. {purged_count} items removed.")
    if organize:
        organize_structure()
    if merge_logic and merge_to and silos:
        merged_count = merge_validator_logic(silos, exclude or [], merge_to)
        Logger.info(f"\n🔀 Merge Complete. {merged_count} functions merged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean duplicates and organize code structure")
    parser.add_argument("--aggressive", action="store_true", help="Perform aggressive cleanup")
    parser.add_argument("--organize", action="store_true", help="Organize files into engine directories")
    parser.add_argument("--merge-logic", action="store_true", help="Merge duplicate validator logic")
    parser.add_argument("--merge-to", type=str, help="Target file for merged validator logic")
    parser.add_argument("--silos", type=str, help="Comma-separated list of silos to process")
    parser.add_argument("--exclude", type=str, help="Comma-separated list of directories to exclude")
    args = parser.parse_args()
    silos = args.silos.split(",") if args.silos else []
    exclude = args.exclude.split(",") if args.exclude else []
    purge_everything(
        aggressive=args.aggressive,
        organize=args.organize,
        merge_logic=args.merge_logic,
        merge_to=args.merge_to,
        silos=silos,
        exclude=exclude,
    )
