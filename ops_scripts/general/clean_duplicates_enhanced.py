from __future__ import annotations

import argparse

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

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

logging.basicConfig(level=logging.INFO, format="%(message)s")
Logger = logging.getLogger(__name__)


def aggressive_cleanup():
    """More aggressive cleanup targeting additional patterns"""
    purged_count = 0
    for item in os.listdir("."):
        # guardian: allow-path-string
        if os.path.isdir(item) and item.startswith("test_repo"):
            try:
                shutil.rmtree(item)
                Logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.error(f"❌ Failed to delete directory {item}: {e}")
    temp_patterns = SOVEREIGN_EXCLUDED_FOLDERS
    for pattern in temp_patterns:
        pass
    from pathlib import Path

    from agentic_core.utils.ssot_discovery_validator import get_python_files

    search_path = Path(pattern.split("**")[0] if "**" in pattern else ".")
    for file in [str(f) for f in get_python_files(search_path)]:
        try:
            os.remove(file)
            Logger.info(f"🗑️ Purged temp file: {file}")
            purged_count += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.error(f"❌ Failed to delete {file}: {e}")
    for root, dirs, _files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                Logger.info(f"🗑️ PURGED DIRECTORY: {pycache_path}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:
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
    for root, _dirs, files in os.walk("/app"):
        for file in files:
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
    except OSError:
        return None


def extract_functions(filepath):
    """Extract function definitions from a Python file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        functions = []
        for node in ast.walk(tree):
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
                    }
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
    aggressive=False, organize=False, merge_logic=False, merge_to=None, silos=None, exclude=None
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
    for item in os.listdir("."):
        # guardian: allow-path-string
        if os.path.isdir(item) and item.startswith("test_repo_1765"):
            try:
                shutil.rmtree(item)
                Logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.error(f"❌ Failed to delete directory {item}: {e}")
    for root, _dirs, files in os.walk("."):
        for file in files:
            file_path = Path(root) / file
            if "_clean.py" in file or file == "test_report.html":
                try:
                    os.remove(file_path)
                    Logger.info(f"🗑️ Purged File: {file_path}")
                    purged_count += 1
                # guardian: allow-silent-swallow
                except Exception as e:
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
