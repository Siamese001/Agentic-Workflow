#!/usr/bin/env python3
"""
Zero-Loss Merge: All _unassigned folders under 01-10 roots.

Scans all _unassigned folders and routes files to canonical locations
within their parent root folder.

Routing Rules per Root:
- 02_schemas: JSON files -> root, Python -> logic/validation
- 03_runtime: -> runtime_ops or pipeline_ops based on content
- 04_prompt_governance: -> templates or logic
- 05_config: -> logic/settings
- 07_observability: -> logic/* based on file type
- 08_scripts: -> utilities or migration
- 09_apps: -> apps_rg, apps_lic, or shared based on content
"""

import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "06_data" / "unassigned_all_merge_manifest.json"

# Root folders to scan
ROOT_FOLDERS = [
    "agentic_core",
    "schemas",
    "runtime",
    "prompt_governance",
    "config",
    "06_data",
    "observability",
    "scripts",
    "09_apps",
    "tests",
]


@dataclass
class MergeManifest:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_files: int = 0
    routed_files: int = 0
    routings: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)


def compute_hash(filepath: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def analyze_content(filepath: Path) -> Dict:
    """Analyze file content for routing hints."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(5000)
    except (ValueError, TypeError, KeyError):
        return {"type": "binary", "hints": []}

    hints = []

    # Resume engine
    if any(x in content for x in ["Resume", "JD", "bullet", "skill", "competenc"]):
        hints.append("resume_engine")

    # Personalization/outreach
    if any(x in content for x in ["personalization", "recipient", "engagement", "outreach"]):
        hints.append("outreach_engine")

    # Observability
    if any(x in content for x in ["telemetry", "metrics", "logging", "tracing", "span"]):
        hints.append("observability")

    # Safety
    if any(x in content for x in ["safety", "compliance", "ethics", "pii"]):
        hints.append("safety")

    # Schema/validation
    if any(x in content for x in ["schema", "validation", "model", "dataclass"]):
        hints.append("schema")

    return {"type": filepath.suffix, "hints": hints}


def route_file_in_root(filepath: Path, root_name: str, parent_folder: str) -> Tuple[str, str]:
    """
    Route a file within its root folder.
    Returns: (target_subpath, reason)
    """
    filename = filepath.name
    name_lower = filename.lower()
    analysis = analyze_content(filepath)
    hints = analysis.get("hints", [])

    # === 02_schemas ===
    if root_name == "schemas":
        if filepath.suffix == ".json":
            if "migration" in name_lower or "plan" in name_lower:
                return f"migration_plans/{filename}", "schema_migration_plan"
            if "freeze" in name_lower or "report" in name_lower:
                return f"reports/{filename}", "schema_report"
            if "status" in name_lower:
                return f"status/{filename}", "schema_status"
            return filename, "schema_root_json"
        return f"logic/validation/{filename}", "schema_validation"

    # === 03_runtime ===
    if root_name == "runtime":
        if "pipeline" in name_lower or "orchestrat" in name_lower:
            return f"pipeline_ops/{filename}", "runtime_pipeline"
        if "execution" in name_lower or "runtime" in name_lower:
            return f"runtime_ops/{filename}", "runtime_execution"
        return f"logic/{filename}", "runtime_logic"

    # === 04_prompt_governance ===
    if root_name == "prompt_governance":
        if "template" in name_lower or "prompt" in name_lower:
            return f"templates/{filename}", "prompt_template"
        return f"logic/{filename}", "prompt_logic"

    # === 05_config ===
    if root_name == "config":
        if "setting" in name_lower or "config" in name_lower:
            return f"logic/settings/{filename}", "config_settings"
        return f"logic/{filename}", "config_logic"

    # === 07_observability ===
    if root_name == "observability":
        if filepath.suffix == ".json":
            if "freeze" in name_lower or "report" in name_lower:
                return filename, "observability_report"
            return f"data/{filename}", "observability_data"

        # Python files
        if any(x in name_lower for x in ["logger", "log_", "logging"]):
            return f"logic/logging/{filename}", "observability_logging"
        if any(x in name_lower for x in ["trace", "span", "exporter", "propagator"]):
            return f"logic/tracing/{filename}", "observability_tracing"
        if any(x in name_lower for x in ["metric", "histogram", "collector", "sampler"]):
            return f"logic/metrics/{filename}", "observability_metrics"
        if any(x in name_lower for x in ["formatter", "adapter"]):
            return f"logic/formatters/{filename}", "observability_formatter"
        if any(x in name_lower for x in ["audit", "store"]):
            return f"logic/audit/{filename}", "observability_audit"
        if any(x in name_lower for x in ["inspector", "profiler", "verifier", "checker"]):
            return f"logic/inspection/{filename}", "observability_inspection"
        return f"logic/standard/{filename}", "observability_general"

    # === 08_scripts ===
    if root_name == "scripts":
        if filepath.suffix == ".json":
            if "freeze" in name_lower or "report" in name_lower:
                return filename, "scripts_report"
            return f"data/{filename}", "scripts_data"

        if any(x in name_lower for x in ["phase", "migration", "pipeline"]):
            return f"migration/{filename}", "scripts_migration"
        return f"utilities/{filename}", "scripts_utility"

    # === 09_apps ===
    if root_name == "09_apps":
        if filepath.suffix == ".json":
            if "freeze" in name_lower or "report" in name_lower:
                return filename, "apps_report"
            return f"data/{filename}", "apps_data"

        # Route based on parent folder hint
        if parent_folder == "apps_unknown":
            # Resume engine patterns
            if "resume_engine" in hints or any(x in name_lower for x in ["skill", "bullet", "experience", "jd_"]):
                return f"apps_rg/logic/{filename}", "apps_rg_logic"
            # Personalization patterns
            if "outreach_engine" in hints or any(x in name_lower for x in ["personalization", "recipient", "engagement", "template"]):
                return f"apps_lic/logic/{filename}", "apps_lic_logic"
            # Scoring patterns
            if any(x in name_lower for x in ["score", "rank", "weight", "calibrate", "compute", "normalize"]):
                return f"apps_rg/scoring/{filename}", "apps_rg_scoring"
            # Content generation
            if any(x in name_lower for x in ["content", "format", "generate", "build", "create"]):
                return f"apps_lic/generation/{filename}", "apps_lic_generation"
            # API/provider
            if any(x in name_lower for x in ["api", "call", "fetch", "provider"]):
                return f"shared/api/{filename}", "apps_shared_api"
            # Safety
            if any(x in name_lower for x in ["safety", "compliance", "risk", "assess"]):
                return f"shared/safety/{filename}", "apps_shared_safety"
            # Default
            return f"shared/utils/{filename}", "apps_shared_utils"

        return f"shared/{filename}", "apps_shared"

    # === Default fallback ===
    return f"logic/{filename}", "default_logic"


def find_unassigned_folders() -> List[Tuple[Path, str]]:
    """Find all _unassigned folders under root folders (excluding archives)."""
    results = []

    # Exclusion patterns
    exclude_patterns = [
        "phase3_snapshots",
        "dedup_archive",
        "unassigned_archive",
        "merged_",
        "sweep",
        "rollback",
        "backup",
    ]

    for root_name in ROOT_FOLDERS:
        root_path = REPO_ROOT / root_name
        if not root_path.exists():
            continue

        for unassigned in root_path.rglob("_unassigned"):
            path_str = str(unassigned)
            if unassigned.is_dir() and not any(excl in path_str for excl in exclude_patterns):
                results.append((unassigned, root_name))

    return results


def execute_merge(dry_run: bool = False) -> MergeManifest:
    """Execute the merge operation."""
    manifest = MergeManifest()

    unassigned_folders = find_unassigned_folders()
    print(f"Found {len(unassigned_folders)} _unassigned folders to process")

    for unassigned_path, root_name in unassigned_folders:
        print(f"\n=== Processing {unassigned_path.relative_to(REPO_ROOT)} ===")

        root_path = REPO_ROOT / root_name

        for filepath in unassigned_path.rglob("*"):
            if not filepath.is_file():
                continue

            manifest.total_files += 1
            filename = filepath.name
            parent_folder = filepath.parent.name if filepath.parent != unassigned_path else ""

            try:
                # Get routing decision
                target_subpath, reason = route_file_in_root(filepath, root_name, parent_folder)
                target_path = root_path / target_subpath

                # Compute hash
                content_hash = compute_hash(filepath)
                file_size = filepath.stat().st_size

                manifest.routings.append({
                    "source": str(filepath.relative_to(REPO_ROOT)),
                    "target": str(target_path.relative_to(REPO_ROOT)),
                    "reason": reason,
                    "hash": content_hash,
                    "size": file_size,
                })

                if not dry_run:
                    # Create target directory
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(str(filepath), str(target_path))

                    manifest.routed_files += 1
                else:
                    manifest.routed_files += 1
                    print(f"  [DRY-RUN] {filename} -> {target_subpath}")

            except (ValueError, TypeError, KeyError) as e:
                manifest.errors.append({
                    "source": str(filepath),
                    "error": str(e),
                })

    # Clean up empty _unassigned folders
    if not dry_run:
        for unassigned_path, _ in unassigned_folders:
            try:
                                for dirpath in sorted(unassigned_path.rglob("*"), key=lambda p: len(str(p)), reverse=True):
                    if dirpath.is_dir() and not any(dirpath.iterdir()):
                        dirpath.rmdir()

                                if unassigned_path.exists() and not any(unassigned_path.iterdir()):
                    unassigned_path.rmdir()
                    print(f"  Removed empty: {unassigned_path.relative_to(REPO_ROOT)}")
            except (ValueError, TypeError, KeyError) as e:
                manifest.errors.append({
                    "source": str(unassigned_path),
                    "error": f"Cleanup failed: {e}",
                })

    # Save manifest
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump({
            "timestamp": manifest.timestamp,
            "total_files": manifest.total_files,
            "routed_files": manifest.routed_files,
            "error_count": len(manifest.errors),
            "routings": manifest.routings,
            "errors": manifest.errors,
        }, f, indent=2)

    return manifest


def print_summary(manifest: MergeManifest):
    """Print merge summary."""
    print("\n" + "=" * 60)
    print("MERGE SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {manifest.timestamp}")
    print(f"Total files: {manifest.total_files}")
    print(f"Routed files: {manifest.routed_files}")
    print(f"Errors: {len(manifest.errors)}")

    # Group by target root
    by_root = defaultdict(int)
    for r in manifest.routings:
        root = r["target"].split("/")[0] if "/" in r["target"] else r["target"].split("\\")[0]
        by_root[root] += 1

    print("\nFiles per root folder:")
    for root, count in sorted(by_root.items()):
        print(f"  {root}: {count}")

    if manifest.errors:
        print("\nErrors:")
        for err in manifest.errors[:5]:
            print(f"  {err['source']}: {err['error']}")

    print(f"\nManifest saved to: {MANIFEST_PATH}")


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No files will be moved")
        print("=" * 60)

    manifest = execute_merge(dry_run=dry_run)
    print_summary(manifest)

    if not dry_run and manifest.routed_files == manifest.total_files and not manifest.errors:
        print("\n[OK] All files routed successfully!")
