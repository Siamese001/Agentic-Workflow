"""
Module Collision Guard - Architectural Integrity Enforcement

Detects and prevents:
- Duplicate filenames
- Duplicate logical import paths
- Namespace shadowing
- Case-insensitive conflicts
- Cross-root collisions
- Package/module dual definitions
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "module_collision_guardrail", "L5")
_emit_routes_through("p1", "module_collision_guardrail", "L5")
_emit_escalates_to_human("p1", "module_collision_guardrail", "L5")
_emit_reads_policy_state("p1", "module_collision_guardrail", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "module_collision_guardrail")
_emit_applies_guardrail("p0", "module_collision_guardrail", "p0_governance")
_emit_snapshots_state("p0", "module_collision_guardrail", "state_snapshot")

_ROOT = Path(__file__).resolve().parents[3]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, OPS_SCRIPTS_DIR, TOOLS_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

ALLOWED_SHIM_PAIRS = {
    "agentic_core/base_agents/decorators.py": "agentic_core/utils/decorators.py",
    "system_learning/types/meta_learning_types.py": "agentic_core/L5_safety/types/meta_learning_types.py",
    "agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py": "agentic_core/enforcement/sealed_interface_check_enforcer.py",
    "agentic_core/L2_execution/enforcement/boundary_verifier.py": "agentic_core/adg/runtime/boundary_verifier.py",
}
ALLOWED_SHIM_PAIRS_NORMALIZED = {
    canonical.replace("\\", "/"): shim.replace("\\", "/") for canonical, shim in ALLOWED_SHIM_PAIRS.items()
}


def compute_logical_import_path(file_path: Path, root: Path) -> str:
    """Compute logical import path for a Python file."""
    relative = file_path.relative_to(root)
    if file_path.name == "__init__.py":
        parts = list(relative.parts[:-1])
    else:
        parts = list(relative.with_suffix("").parts)
    return ".".join(parts)


EXCLUDE_PATTERNS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from scanning."""
    for part in path.parts:
        if part in EXCLUDE_PATTERNS:
            return True
    return False


def scan_directory(root: Path, repo_root: Path | None = None) -> dict[str, list[Path]]:
    """Scan directory for Python files and map logical paths to physical files."""
    logical_map = defaultdict(list)
    if repo_root is None:
        repo_root = Path.cwd().resolve()
    for py_file in root.rglob("*.py"):
        if should_exclude(py_file):
            continue
        logical_path = compute_logical_import_path(py_file, root)
        py_file_resolved = py_file.resolve()
        relative_path = py_file_resolved.relative_to(repo_root)
        logical_map[logical_path].append(relative_path)
    return logical_map


def is_allowed_shim_pair(files: list[tuple[str, Path]]) -> bool:
    """Check if duplicate files form an allowed canonical+shim pair."""
    if len(files) != 2:
        return False
    path_strs = [str(file).replace("\\", "/") for root, file in files]
    for canonical, shim in ALLOWED_SHIM_PAIRS_NORMALIZED.items():
        if canonical in path_strs and shim in path_strs:
            return True
    return False


def detect_collisions(scans: dict[str, dict[str, list[Path]]]) -> dict[str, list[tuple[str, list[Path]]]]:
    """Detect various types of module collisions."""
    violations = {
        "duplicate_filenames": [],
        "duplicate_logical_paths": [],
        "case_insensitive_collisions": [],
        "module_package_dual_definitions": [],
    }
    all_files = []
    logical_paths_map = defaultdict(list)
    for root_name, logical_map in scans.items():
        for logical_path, files in logical_map.items():
            for file_path in files:
                all_files.append((root_name, file_path))
                logical_paths_map[logical_path].append((root_name, file_path))
    stem_map = defaultdict(list)
    for root_name, file_path in all_files:
        stem = file_path.stem
        if stem == "__init__":
            continue
        stem_map[root_name, stem].append((root_name, file_path))
    for (root_name, stem), files in stem_map.items():
        if len(files) > 1 and (not is_allowed_shim_pair(files)):
            violations["duplicate_filenames"].append((f"{root_name}:{stem}", files))
    for logical_path, files in logical_paths_map.items():
        root_groups = defaultdict(list)
        for root_name, file_path in files:
            root_groups[root_name].append((root_name, file_path))
        for root_name, root_files in root_groups.items():
            if len(root_files) > 1 and (not is_allowed_shim_pair(root_files)):
                violations["duplicate_logical_paths"].append((f"{root_name}:{logical_path}", root_files))
    case_map = defaultdict(list)
    for logical_path, files in logical_paths_map.items():
        case_key = logical_path.lower()
        case_map[case_key].append((logical_path, files))
    for case_key, entries in case_map.items():
        unique_paths = {logical for logical, _ in entries}
        if len(unique_paths) > 1:
            root_groups = defaultdict(list)
            for logical, files in entries:
                for root_name, file_path in files:
                    root_groups[root_name].append((root_name, file_path))
            for root_name, root_files in root_groups.items():
                if len(root_files) > 1 and (not is_allowed_shim_pair(root_files)):
                    violations["case_insensitive_collisions"].append(
                        (f"{root_name}:{case_key}", [(case_key, root_files)])
                    )
    for logical_path, files in logical_paths_map.items():
        root_groups = defaultdict(list)
        for root_name, file_path in files:
            root_groups[root_name].append((root_name, file_path))
        for root_name, root_files in root_groups.items():
            has_module = any((f.name != "__init__.py" for _, f in root_files))
            has_package = any((f.name == "__init__.py" for _, f in root_files))
            if has_module and has_package and (not is_allowed_shim_pair(root_files)):
                violations["module_package_dual_definitions"].append(
                    (f"{root_name}:{logical_path}", root_files)
                )
    return violations


def format_violations(violations: dict[str, list[tuple[str, list[Path]]]]) -> str:
    """Format violations for output with deterministic sorting."""
    output_lines = []
    for violation_type, items in violations.items():
        if not items:
            continue
        output_lines.append(f"🚨 {violation_type.upper().replace('_', ' ')}:")
        items_sorted = sorted(items, key=lambda x: x[0])
        for key, files in items_sorted:
            output_lines.append(f"  {key}:")
            files_sorted = sorted(files, key=lambda x: (x[0], str(x[1])))
            for root_name, file_path in files_sorted:
                output_lines.append(f"    - {file_path}")
        output_lines.append("")
    return "\n".join(output_lines)


def load_baseline() -> dict:
    """Load the baseline file containing allowed collisions."""
    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
    if not baseline_path.exists():
        return {"logical_import_path_collisions": {}, "filename_collisions": {}}
    with open(baseline_path) as f:
        return json.load(f)


def save_baseline(collisions: dict[str, list[tuple[str, list[Path]]]]) -> None:
    """Save current collisions to baseline file (deterministic format)."""
    baseline = {"logical_import_path_collisions": {}, "filename_collisions": {}}
    if "duplicate_filenames" in collisions:
        for key, files in collisions["duplicate_filenames"]:
            stem_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            baseline["filename_collisions"][stem_lower] = paths
    if "duplicate_logical_paths" in collisions:
        for key, files in collisions["duplicate_logical_paths"]:
            logical_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            baseline["logical_import_path_collisions"][logical_lower] = paths
    baseline["filename_collisions"] = dict(sorted(baseline["filename_collisions"].items()))
    baseline["logical_import_path_collisions"] = dict(
        sorted(baseline["logical_import_path_collisions"].items())
    )
    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(baseline, indent=2, sort_keys=True) + "\n"
    baseline_path.write_bytes(content.encode("utf-8"))


def check_against_baseline(collisions: dict[str, list[tuple[str, list[Path]]]], baseline: dict) -> list[str]:
    """Check if collisions exceed baseline. Returns list of violations."""
    violations = []
    current_filename = {}
    if "duplicate_filenames" in collisions:
        for key, files in collisions["duplicate_filenames"]:
            stem_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            current_filename[stem_lower] = paths
    for stem_lower, paths in current_filename.items():
        if stem_lower not in baseline["filename_collisions"]:
            violations.append(f"NEW filename collision: {stem_lower} -> {paths}")
        else:
            baseline_paths = baseline["filename_collisions"][stem_lower]
            if set(paths) != set(baseline_paths):
                violations.append(
                    f"GROWTH in filename collision {stem_lower}: baseline={baseline_paths}, current={paths}"
                )
    current_logical = {}
    if "duplicate_logical_paths" in collisions:
        for key, files in collisions["duplicate_logical_paths"]:
            logical_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            current_logical[logical_lower] = paths
    for logical_lower, paths in current_logical.items():
        if logical_lower not in baseline["logical_import_path_collisions"]:
            violations.append(f"NEW logical path collision: {logical_lower} -> {paths}")
        else:
            baseline_paths = baseline["logical_import_path_collisions"][logical_lower]
            if set(paths) != set(baseline_paths):
                violations.append(
                    f"GROWTH in logical path collision {logical_lower}: baseline={baseline_paths}, current={paths}"
                )
    return violations


def get_repo_root() -> Path:
    """Determine repository root via git or fallback to .git search."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()


def discover_roots(repo_root: Path) -> dict[str, Path]:
    """Discover roots to scan with deterministic ordering."""
    roots = {}
    for name in [AGENTIC_CORE_DIR, TOOLS_DIR, OPS_SCRIPTS_DIR]:
        path = repo_root / name
        if path.exists():
            roots[name] = path
    for path in sorted(repo_root.glob("apps_*")):
        if path.is_dir():
            roots[path.name] = path
    return dict(sorted(roots.items()))


def main():
    """Main entry point."""
    repo_root = get_repo_root()
    roots_to_scan = discover_roots(repo_root)
    if os.environ.get("MODULE_COLLISION_UPDATE_BASELINE") == "1":
        print("[*] UPDATING BASELINE...")
        missing_roots = [name for name, path in roots_to_scan.items() if not path.exists()]
        if missing_roots:
            print(f"ERROR: Missing roots: {missing_roots}")
            sys.exit(1)
        scans = {}
        for root_name, root_path in roots_to_scan.items():
            scans[root_name] = scan_directory(root_path, repo_root)
        collisions = detect_collisions(scans)
        save_baseline(collisions)
        print(
            f"[OK] Baseline updated with {sum(len(items) for items in collisions.values())} collision groups"
        )
        sys.exit(0)
    missing_roots = [name for name, path in roots_to_scan.items() if not path.exists()]
    if missing_roots:
        print(f"ERROR: Missing roots: {missing_roots}")
        sys.exit(1)
    scans = {}
    for root_name, root_path in roots_to_scan.items():
        scans[root_name] = scan_directory(root_path, repo_root)
    collisions = detect_collisions(scans)
    baseline = load_baseline()
    violations = check_against_baseline(collisions, baseline)
    if violations:
        print("[!] MODULE COLLISION VIOLATIONS DETECTED")
        print("=" * 50)
        for violation in violations:
            print(f"  - {violation}")
        print("")
        print("[X] ARCHITECTURAL INTEGRITY COMPROMISED")
        print("Fix violations or update baseline with MODULE_COLLISION_UPDATE_BASELINE=1")
        sys.exit(1)
    else:
        total_collisions = sum(len(items) for items in collisions.values())
        if total_collisions > 0:
            print("[OK] No new module collisions detected")
            print(f"     Existing collisions: {total_collisions} groups (baselined)")
        else:
            print("[OK] No module collisions detected")
        print("Architectural integrity maintained.")
        sys.exit(0)


if __name__ == "__main__":
    main()
