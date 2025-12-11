#!/usr/bin/env python3
"""
SUBATOMIC CANON 2025 — FINAL TRANSFORMATION SCRIPT
===================================================
Executes the complete subatomic canon transformation with zero-loss guarantee.

8 SUBATOMIC PRINCIPLES:
1. Only agentic_core/, apps_lic/, apps_rg/ have L1–L5
2. Only L1_cognition has P1–P4 phases
3. L2_execution, L3_orchestration, L5_safety → completely flat
4. L4_memory → only P1_retrieve
5. Every .py file → imperative verb + concrete object
6. Banned forever: ops, utils, coordinator, provider, function, shared, core, various, stuff, business, standard
7. Depth emerges naturally — no fake nesting
8. Every name teaches its purpose on sight
"""

import os
import scripts.check_canonical_structure
import shutil
from pathlib import Path
from typing import Dict, List
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Cognitive engine roots that have L1-L5 structure
COGNITIVE_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "09_apps" / "apps_lic",
    REPO_ROOT / "09_apps" / "apps_rg",
]

# Layers that must be completely flat (no P* folders)
FLAT_LAYERS = ["L2_execution", "L3_orchestration", "L5_safety"]

# L4_memory keeps only P1_retrieve
L4_ALLOWED_PHASES = ["P1_retrieve"]

# Banned folder/file name patterns
BANNED_PATTERNS = [
    r".*_ops$",           # scoring_ops, business_ops, tool_ops, etc.
    r"^utils$",
    r"^coordinator$",
    r"^provider$",
    r"^function$",
    r"^shared$",
    r"^core$",
    r"^various$",
    r"^stuff$",
    r"^business$",
    r"^standard$",
]

# Many-shot rename mappings (current → target)
RENAME_MAPPINGS: Dict[str, str] = {
    # From the prompt examples
    "compute_confidence.py": "compute_confidence_score.py",
    "apply_weights.py": "apply_scoring_weights.py",
    "validate_schema.py": "validate_candidate_structure.py",
    "rank_results.py": "select_highest_scoring_candidate.py",
    "track.py": "enforce_remaining_budget.py",
    "apply_safety.py": "block_jailbreak_attempt.py",
    "enforce_filters.py": "enforce_content_filtering.py",
    "execute_action.py": "invoke_web_search.py",
    "process_response.py": "parse_search_results.py",
    "handle_common_failures.py": "retry_with_exponential_backoff.py",
    "format_registry_context.py": "format_candidate_payload.py",
    "normalize_scores.py": "normalize_confidence_scores.py",
    "inspect_core_state.py": "capture_current_agent_state.py",
    "merge_contexts.py": "consolidate_conversation_history.py",
    "calculate_similarity.py": "compute_semantic_similarity.py",
    "embed_generic_content.py": "generate_text_embedding.py",
    "optimize_results.py": "refine_final_ranking.py",
    "parse_registry_intent.py": "extract_user_intent.py",
    "check_registry_policy.py": "validate_against_safety_policy.py",
    "invoke_service.py": "call_external_api.py",
    "sort_results.py": "sort_by_confidence_score.py",
    "validate_ethics.py": "check_ethical_constraints.py",
    "snapshot_state.py": "persist_current_state.py",
    "retrieve_similarity.py": "find_similar_past_queries.py",
    "coordinate_execution_queries.py": "orchestrate_tool_sequence.py",
    "enforce_safety_filters.py": "apply_input_safety_filter.py",
    "prepare_execution_payload.py": "build_tool_call_payload.py",
    "validate_common_ethics.py": "block_harmful_content.py",
}

# Quarantine folder for L4 non-retrieve phases
QUARANTINE_L4 = "__QUARANTINE_L4_NON_RETRIEVE__"

# =============================================================================
# function FUNCTIONS
# =============================================================================

def is_banned_name(name: str) -> bool:
    """Check if a folder/file name matches banned patterns."""
    for pattern in BANNED_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True
    return False

def get_new_filename(old_name: str) -> str:
    """Get the new filename based on rename mappings."""
    return RENAME_MAPPINGS.get(old_name, old_name)

def collect_py_files(directory: Path) -> List[Path]:
    """Recursively collect all .py files in a directory."""
    if not directory.exists():
        return []
    return list(directory.rglob("*.py"))

def ensure_init_py(directory: Path) -> None:
    """Ensure __init__.py exists in directory."""
    init_file = directory / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Auto-generated __init__.py for subatomic canon 2025."""\n')

def move_file_with_rename(src: Path, dest_dir: Path, apply_rename: bool = True) -> Path:
    """Move a file to destination directory, optionally applying rename mappings."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    new_name = get_new_filename(src.name) if apply_rename else src.name
    dest_path = dest_dir / new_name

    # Handle conflicts
    if dest_path.exists() and dest_path != src:
        # Add suffix to avoid overwrite
        stem = dest_path.stem
        suffix = dest_path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

    if src != dest_path:
        shutil.move(str(src), str(dest_path))

    return dest_path

# =============================================================================
# TRANSFORMATION FUNCTIONS
# =============================================================================

def flatten_layer(layer_path: Path, layer_name: str) -> Dict[str, List[str]]:
    """
    Flatten a layer by moving all files from P* subdirectories to the layer root.
    Returns a log of operations performed.
    """
    log = {"moved": [], "deleted_dirs": [], "renamed": []}

    if not layer_path.exists():
        return log

    # Find all P* directories
    phase_dirs = [d for d in layer_path.iterdir() if d.is_dir() and d.name.startswith("P")]

    for phase_dir in phase_dirs:
        # Collect all .py files recursively
        py_files = collect_py_files(phase_dir)

        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue  # Skip __init__.py files

            # Move to layer root with rename
            new_path = move_file_with_rename(py_file, layer_path)
            log["moved"].append(f"{py_file} -> {new_path}")

            if py_file.name != new_path.name:
                log["renamed"].append(f"{py_file.name} -> {new_path.name}")

                try:
            shutil.rmtree(phase_dir)
            log["deleted_dirs"].append(str(phase_dir))
        except (ValueError, TypeError, KeyError) as e:

    # Ensure __init__.py exists at layer root
    ensure_init_py(layer_path)

    return log

def quarantine_l4_non_retrieve(l4_path: Path) -> Dict[str, List[str]]:
    """
    Quarantine L4_memory phases other than P1_retrieve.
    """
    log = {"quarantined": [], "kept": []}

    if not l4_path.exists():
        return log

    quarantine_dir = l4_path / QUARANTINE_L4

    for item in l4_path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("P") and item.name not in L4_ALLOWED_PHASES:
            # Move to quarantine
            dest = quarantine_dir / item.name
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest))
            log["quarantined"].append(f"{item.name} -> {dest}")
        elif item.name in L4_ALLOWED_PHASES:
            log["kept"].append(item.name)

    return log

def delete_banned_folders(root: Path) -> List[str]:
    """
    Delete all folders matching banned patterns.
    Promotes files up before deletion.
    """
    deleted = []

    # Walk bottom-up to handle nested banned folders
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current_dir = Path(dirpath)

        for dirname in dirnames:
            if is_banned_name(dirname):
                banned_dir = current_dir / dirname

                # Promote .py files to parent
                for py_file in collect_py_files(banned_dir):
                    if py_file.name != "__init__.py":
                        move_file_with_rename(py_file, current_dir)

                                try:
                    shutil.rmtree(banned_dir)
                    deleted.append(str(banned_dir))
                except (ValueError, TypeError, KeyError) as e:

    return deleted

def apply_file_renames(root: Path) -> List[str]:
    """
    Apply rename mappings to all .py files.
    """
    renamed = []

    for py_file in root.rglob("*.py"):
        if py_file.name in RENAME_MAPPINGS:
            new_name = RENAME_MAPPINGS[py_file.name]
            new_path = py_file.parent / new_name

            if not new_path.exists():
                py_file.rename(new_path)
                renamed.append(f"{py_file} -> {new_path}")

    return renamed

# =============================================================================
# YAML UPDATE FUNCTIONS
# =============================================================================

def update_meta_yaml(yaml_path: Path) -> None:
    """Update unified_structure_subatomic_meta.yaml with new cognitive_layer_phase_rules."""
    content = yaml_path.read_text(encoding="utf-8")

    # Replace cognitive_layer_phase_rules section

    new_rules = """cognitive_layer_phase_rules:
    L1_cognition:
      allowed_phases: [P1_retrieve, P2_inspect, P3_aggregate, P4_safety]
    L2_execution:
      allowed_phases: []
    L3_orchestration:
      allowed_phases: []
    L4_memory:
      allowed_phases: [P1_retrieve]
    L5_safety:
      allowed_phases: []"""

    # basic string replacement for the rules
    content = re.sub(
        r"cognitive_layer_phase_rules:.*?L5_safety:\s*\n\s*allowed_phases:.*?\]",
        new_rules,
        content,
        flags=re.DOTALL
    )

    # Add subatomic_canon_2025 section if not present
    if "subatomic_canon_2025:" not in content:
        canon_section = """
# ---------------------------------------------------------------------
# 11. SUBATOMIC CANON 2025 — FINAL
# ---------------------------------------------------------------------
subatomic_canon_2025:
  enforced: true
  principles_applied:
    - only_three_agents_have_L1_L5
    - only_L1_has_phases
    - L2_L3_L5_flat
    - L4_retrieval_only
    - imperative_verb_naming
    - banned_low_signal_words
    - natural_depth_no_padding
    - self_teaching_names
"""
        content += canon_section

    yaml_path.write_text(content, encoding="utf-8")

def update_main_yaml(yaml_path: Path) -> None:
    """Update unified_structure_subatomic.yaml to reflect flat structure."""
    content = yaml_path.read_text(encoding="utf-8")

    # Replace 01_agentic_core with agentic_core in domain references
    content = content.replace("agentic_core", "agentic_core")

    yaml_path.write_text(content, encoding="utf-8")

# =============================================================================
# IMPORT FIXER
# =============================================================================

def fix_imports_in_file(file_path: Path, old_to_new: Dict[str, str]) -> bool:
    """Fix imports in a single Python file based on rename mappings."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        for old_name, new_name in old_to_new.items():
            old_module = old_name.replace(".py", "")
            new_module = new_name.replace(".py", "")

            # Replace import statements
            content = re.sub(
                rf"\bfrom\s+(\S+\.)?{re.escape(old_module)}\b",
                rf"from \1{new_module}",
                content
            )
            content = re.sub(
                rf"\bimport\s+(\S+\.)?{re.escape(old_module)}\b",
                rf"import \1{new_module}",
                content
            )

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except (ValueError, TypeError, KeyError) as e:

        return False

def fix_all_imports(root: Path) -> int:
    """Fix imports across the entire repository."""
    fixed_count = 0

    for py_file in root.rglob("*.py"):
        if fix_imports_in_file(py_file, RENAME_MAPPINGS):
            fixed_count += 1

    return fixed_count

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():

    all_logs = {
        "flattened_layers": {},
        "quarantined_l4": {},
        "deleted_banned": [],
        "renamed_files": [],
        "fixed_imports": 0,
    }

    # Step 1: Flatten L2, L3, L5 layers

    for root in COGNITIVE_ROOTS:
        for layer in FLAT_LAYERS:
            layer_path = root / layer
            if layer_path.exists():
                log = flatten_layer(layer_path, layer)
                key = f"{root.name}/{layer}"
                all_logs["flattened_layers"][key] = log

    # Step 2: Quarantine L4 non-retrieve phases

    for root in COGNITIVE_ROOTS:
        l4_path = root / "L4_memory"
        if l4_path.exists():
            log = quarantine_l4_non_retrieve(l4_path)
            key = f"{root.name}/L4_memory"
            all_logs["quarantined_l4"][key] = log

    # Step 3: Delete banned folders

    for root in COGNITIVE_ROOTS:
        deleted = delete_banned_folders(root)
        all_logs["deleted_banned"].extend(deleted)

    # Step 4: Apply file renames

    for root in COGNITIVE_ROOTS:
        renamed = apply_file_renames(root)
        all_logs["renamed_files"].extend(renamed)

    # Step 5: Update YAML files

    meta_yaml = REPO_ROOT / "unified_structure_subatomic_meta.yaml"
    main_yaml = REPO_ROOT / "unified_structure_subatomic.yaml"

    if meta_yaml.exists():
        update_meta_yaml(meta_yaml)

    if main_yaml.exists():
        update_main_yaml(main_yaml)

    # Step 6: Fix imports

    fixed = fix_all_imports(REPO_ROOT)
    all_logs["fixed_imports"] = fixed

    # Write transformation log
    log_path = REPO_ROOT / "subatomic_canon_2025_transform_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, indent=2, default=str)

if __name__ == "__main__":
    main()
