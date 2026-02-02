from __future__ import annotations

"""
One-Off Bulk Hierarchy Healer - Eternal Depth 4 Alignment
"""
import shutil
import sys
from datetime import datetime
from typing import Any

dry_run: Any = False
target_root: Any = "agentic_core"
primary_partition_only: Any = True
current_file: Any = Path(__file__).resolve()
project_root: Any = next((p for p in current_file.parents if (p / ".env").exists()), None)
if not project_root:
    print("[!] Project root not found (.env Missing).")
    sys.exit(1)
sys.path.insert(0, str(project_root))
try:
    from agentic_core.L5_safety.validators.structure_blueprint_config import CORE_SUBFOLDER_MAP
except ImportError:
    print("[!] Critical Failure: Cannot find CORE_SUBFOLDER_MAP in structure_blueprint.py")
    sys.exit(1)


def log_move(file_name: Any, src: Any, dst: Any) -> Any:
    """Brief description of functionality and purpose."""
    audit_log: Any = project_root / "mission_audit.csv"
    timestamp: Any = datetime.now().isoformat()
    log_entry: Any = f"{timestamp},{file_name},HIERARCHY_HEAL,{src},{dst},Bulk Alignment\n"
    with open(audit_log, "a") as f:
        f.write(log_entry)
    print(f"   [LOG] {file_name} moved to {dst}")


def main() -> Any:
    """Brief description of functionality and purpose."""
    target_dir: Any = project_root / TARGET_ROOT
    # Absolute Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    python_files: Any = list(get_python_files(target_dir))
    print(f"--- SOVEREIGN HEALING START: {TARGET_ROOT} ---")
    print(f"Mode: {('DRY RUN' if DRY_RUN else 'EXECUTION')}")
    output_file: Any = project_root / "hierarchy_heal_dry_run.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== BULK HIERARCHY HEAL ===\n")
        f.write(f"Target: {TARGET_ROOT}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"configuration: DRY_RUN = {DRY_RUN}\n\n")
        for file_path in python_files:
            rel: Any = file_path.relative_to(project_root)
            parts: Any = rel.parts
            if len(parts) < 3 or not parts[1].startswith("L"):
                continue
            layer: Any = parts[1]
            allowed_partitions: Any = CORE_SUBFOLDER_MAP.get(layer, [])
            if not allowed_partitions:
                continue
            primary: Any = allowed_partitions[0]
            is_depth_2: Any = len(parts) == 3
            is_wrong_partition: Any = len(parts) == 4 and parts[2] not in allowed_partitions
            if is_depth_2 or is_wrong_partition:
                dest_dir: Any = project_root / TARGET_ROOT / layer / primary
                dest_path: Any = dest_dir / file_path.name
                if dest_path.exists():
                    log_entry: Any = f"[CONFLICT] {rel} >> {dest_path.relative_to(project_root)} (already exists)\n"
                    print(
                        f"   [!] CONFLICT: {file_path.name} already exists in {primary}. Skipping."
                    )
                    f.write(log_entry)
                    continue
                log_entry: Any = f"[MOVE] {rel} >> {dest_path.relative_to(project_root)}\n"
                print(f"   [MOVE] {rel} >> {dest_path.relative_to(project_root)}")
                f.write(log_entry)
                if not DRY_RUN:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                    log_move(file_path.name, "/".join(parts[:-1]), f"{layer}/{primary}")
        f.write("\n=== SUMMARY ===\n")
        f.write(f"Total Python files scanned: {len(python_files)}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"DRY_RUN = {DRY_RUN}\n")
    if DRY_RUN:
        print(f"\n[DRY RUN COMPLETE] Output saved to: {output_file}")
        print("Set DRY_RUN = False in the script to execute moves")
    else:
        print(f"\n[EXECUTION COMPLETE] All moves executed. Output saved to: {output_file}")
    if not dry_run:
        print("\n--- INITIATING AUTO-CLEANUP ---")
        legacy_partitions: Any = [
            "P1_core",
            "P1_domain",
            "P1_interfaces",
            "P2_domain",
            "P3_aggregation",
            "P5_meta",
            "boundaries",
            "discovery",
            "identity",
            "inference",
            "planning",
            "planning_logic",
            "mcp",
            "sandbox",
            "tools",
            "P2_tools",
            "P3_engines",
            "P4_agents",
            "P5_healing",
            "event_bus",
            "framework",
            "handoff_logic",
            "health",
            "P5_workflow",
            "protocol",
            "security",
            "training",
            "automation",
            "migrations",
            "cache",
            "checkpoints",
            "filesystem",
            "memory",
            "persistence_layer",
            "S1_store",
            "semantic",
            "session_manager",
            "vector",
            "P1_red_team",
            "P4_security",
            "audit_logs",
            "gravity",
            "policy",
            "validators",
        ]
        for layer_folder in target_dir.iterdir():
            if not layer_folder.is_dir() or not layer_folder.name.startswith("L"):
                continue
            for legacy in legacy_partitions:
                legacy_path: Any = layer_folder / legacy
                if legacy_path.exists():
                    remaining: Any = [
                        f
                        for f in legacy_path.iterdir()
                        if f.name != "__pycache__" and f.name != "__init__.py"
                    ]
                    if not remaining:
                        try:
                            shutil.rmtree(legacy_path)
                            print(
                                f"   [CLEAN] Purged legacy folder: {legacy_path.relative_to(project_root)}"
                            )
                        except Exception as e:
                            print(f"   [!] Could not purge {legacy}: {e}")
    print("\n" + "=" * 70)
    print(f"[COMPLETE] Bulk hierarchy healing for {TARGET_ROOT}")
    if DRY_RUN:
        print("Status: PREVIEW MODE - No files were moved")
    else:
        print("Status: EXECUTED - Files moved and legacy folders cleaned")
    print("=" * 70)


if __name__ == "__main__":
    main()
