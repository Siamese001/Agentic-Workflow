#!/usr/bin/env python3
"""
Zero-Loss Merge: _unassigned → 10 Canonical Folders

Routes all files from _unassigned/ to the appropriate canonical folders:
  01_agentic_core, 02_schemas, 03_runtime, 04_prompt_governance, 05_config,
  06_data, 07_observability, 08_scripts, 09_apps, 10_tests

Routing Rules (based on filename patterns and content analysis):
1. *_observability_* → 07_observability
2. *_scripts_* → 08_scripts
3. *_safety_*, *_compliance_*, *_ethics_* → 01_agentic_core/L5_safety
4. *_execution_*, *_runtime_* → 03_runtime
5. *_config_*, *_settings_*, *_registry_* → 05_config
6. *_schema_*, *_validation_*, *_model_* → 02_schemas
7. *_prompt_*, *_template_* → 04_prompt_governance
8. *_test_*, test_* → 10_tests
9. Resume engine content (v5.*, RAG, JD*) → 09_apps/apps_rg
10. Personalization/outreach content → 09_apps/apps_lic
11. Remaining → 06_data/_unassigned_archive

Execution: Run from repo root inside Docker container.
"""

import os
import re
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# Configuration
REPO_ROOT = Path(__file__).resolve().parents[1]
UNASSIGNED_ROOT = REPO_ROOT / "_unassigned"
MANIFEST_PATH = REPO_ROOT / "06_data" / "unassigned_merge_manifest.json"

# Target folders
TARGETS = {
    "01_agentic_core": REPO_ROOT / "01_agentic_core",
    "02_schemas": REPO_ROOT / "02_schemas",
    "03_runtime": REPO_ROOT / "03_runtime",
    "04_prompt_governance": REPO_ROOT / "04_prompt_governance",
    "05_config": REPO_ROOT / "05_config",
    "06_data": REPO_ROOT / "06_data",
    "07_observability": REPO_ROOT / "07_observability",
    "08_scripts": REPO_ROOT / "08_scripts",
    "09_apps": REPO_ROOT / "09_apps",
    "10_tests": REPO_ROOT / "10_tests",
}


@dataclass
class FileRouting:
    """Routing decision for a single file."""
    source_path: Path
    target_folder: str
    target_subpath: str
    reason: str
    content_hash: str
    file_size: int


@dataclass
class MergeManifest:
    """Complete merge manifest for audit trail."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_files: int = 0
    routed_files: int = 0
    routings: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)


def compute_hash(filepath: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def analyze_content(filepath: Path) -> Dict[str, any]:
    """Analyze file content to determine routing hints."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(5000)
    except Exception:
        return {"type": "binary", "hints": []}
    
    hints = []
    
    # Resume engine indicators
    if any(x in content for x in ["Resume Generation Engine", "v5.", "JDAlignment", "RAG", "MASTER_RESUME"]):
        hints.append("resume_engine")
    
    # Observability indicators
    if any(x in content for x in ["telemetry", "metrics", "logging", "tracing", "span", "exporter"]):
        hints.append("observability")
    
    # Safety indicators
    if any(x in content for x in ["safety", "compliance", "ethics", "pii", "redaction", "toxicity"]):
        hints.append("safety")
    
    # Test indicators
    if any(x in content for x in ["def test_", "pytest", "unittest", "assert ", "mock"]):
        hints.append("test")
    
    # L2 execution indicators
    if any(x in content for x in ["ExecutionAgent", "L2 Execution", "executor", "PlanObject"]):
        hints.append("execution")
    
    # Schema/model indicators
    if any(x in content for x in ["@dataclass", "BaseModel", "TypedDict", "Schema"]):
        hints.append("schema")
    
    # Config indicators
    if any(x in content for x in ["CONFIG", "settings", "registry", "environment"]):
        hints.append("config")
    
    # Script/utility indicators
    if any(x in content for x in ["if __name__", "argparse", "click", "main()"]):
        hints.append("script")
    
    return {"type": "python" if filepath.suffix == ".py" else "other", "hints": hints}


def route_file(filepath: Path, filename: str, parent_folder: str = "") -> Tuple[str, str, str]:
    """
    Determine target folder and subpath for a file.
    Returns: (target_folder, target_subpath, reason)
    """
    name_lower = filename.lower()
    analysis = analyze_content(filepath)
    hints = analysis.get("hints", [])
    
    # PRIORITY RULE 0: apps_unknown folder → 09_apps (application-level code)
    if parent_folder == "apps_unknown":
        # Resume engine patterns
        if "resume_engine" in hints or any(x in name_lower for x in ["jd", "resume", "bullet", "skill", "competenc"]):
            return "09_apps", f"apps_rg/logic/{filename}", "apps_rg_resume_pattern"
        # Personalization/outreach patterns
        if any(x in name_lower for x in ["personalization", "recipient", "engagement", "outreach", "template"]):
            return "09_apps", f"apps_lic/logic/{filename}", "apps_lic_outreach_pattern"
        # Scoring/ranking patterns → apps_rg (resume scoring)
        if any(x in name_lower for x in ["score", "rank", "weight", "calibrate", "compute", "normalize"]):
            return "09_apps", f"apps_rg/scoring/{filename}", "apps_rg_scoring_pattern"
        # Content/formatting patterns → apps_lic (content generation)
        if any(x in name_lower for x in ["content", "format", "generate", "build", "create"]):
            return "09_apps", f"apps_lic/generation/{filename}", "apps_lic_generation_pattern"
        # API/service patterns → apps shared
        if any(x in name_lower for x in ["api", "call", "fetch", "service"]):
            return "09_apps", f"shared/api/{filename}", "apps_shared_api_pattern"
        # Safety/compliance patterns within apps
        if any(x in name_lower for x in ["safety", "compliance", "risk", "assess"]):
            return "09_apps", f"shared/safety/{filename}", "apps_shared_safety_pattern"
        # Default for apps_unknown
        return "09_apps", f"shared/utils/{filename}", "apps_shared_utils_pattern"
    
    # PRIORITY RULE 0.5: support_nomatch folder → infrastructure code
    if parent_folder == "support_nomatch":
        # Logging infrastructure
        if any(x in name_lower for x in ["logger", "log_", "logging"]):
            return "07_observability", f"logic/logging/{filename}", "support_logging_pattern"
        # Tracing infrastructure
        if any(x in name_lower for x in ["trace", "span", "exporter", "propagator", "jaeger", "otlp", "opentelemetry"]):
            return "07_observability", f"logic/tracing/{filename}", "support_tracing_pattern"
        # Metrics infrastructure
        if any(x in name_lower for x in ["metric", "histogram", "collector", "sampler"]):
            return "07_observability", f"logic/metrics/{filename}", "support_metrics_pattern"
        # Formatter/adapter infrastructure
        if any(x in name_lower for x in ["formatter", "adapter", "json_"]):
            return "07_observability", f"logic/formatters/{filename}", "support_formatter_pattern"
        # Audit/store infrastructure
        if any(x in name_lower for x in ["audit", "store", "sqlite", "file_"]):
            return "06_data", f"cache_ops/audit/{filename}", "support_audit_pattern"
        # Pipeline/phase scripts
        if any(x in name_lower for x in ["phase", "pipeline", "run_", "freeze"]):
            return "08_scripts", f"migration/{filename}", "support_migration_pattern"
        # Verification/inspection
        if any(x in name_lower for x in ["verifier", "inspector", "checker", "profiler"]):
            return "07_observability", f"logic/inspection/{filename}", "support_inspection_pattern"
        # PII/redaction → safety
        if any(x in name_lower for x in ["pii", "redaction"]):
            return "01_agentic_core", f"L5_safety/pii/{filename}", "support_pii_pattern"
        # Config/settings
        if any(x in name_lower for x in ["config", "setting"]):
            return "05_config", f"logic/settings/{filename}", "support_config_pattern"
        # Scripts patterns (explicit)
        if "_scripts_" in name_lower:
            return "08_scripts", f"utilities/{filename}", "support_scripts_pattern"
        # Observability patterns (explicit)
        if "_observability_" in name_lower:
            return "07_observability", f"logic/general/{filename}", "support_observability_pattern"
        # Runtime/execution patterns
        if any(x in name_lower for x in ["runtime", "execution", "snapshot"]):
            return "03_runtime", f"runtime_ops/support/{filename}", "support_runtime_pattern"
        # Default for support_nomatch → observability (most are infra)
        return "07_observability", f"logic/support/{filename}", "support_default_pattern"
    
    # Rule 1: Observability patterns (explicit _observability_ in name)
    if "_observability_" in name_lower:
        if "log" in name_lower or "logger" in name_lower:
            return "07_observability", f"logic/logging/{filename}", "observability_logging_pattern"
        if "metric" in name_lower or "histogram" in name_lower:
            return "07_observability", f"logic/metrics/{filename}", "observability_metrics_pattern"
        if "trace" in name_lower or "span" in name_lower or "exporter" in name_lower:
            return "07_observability", f"logic/tracing/{filename}", "observability_tracing_pattern"
        if "sampler" in name_lower or "collector" in name_lower:
            return "07_observability", f"logic/sampling/{filename}", "observability_sampling_pattern"
        return "07_observability", f"logic/general/{filename}", "observability_general_pattern"
    
    # Rule 2: Scripts patterns
    if "_scripts_" in name_lower or "script" in hints:
        if "phase" in name_lower:
            return "08_scripts", f"migration/{filename}", "scripts_phase_pattern"
        if "pipeline" in name_lower:
            return "08_scripts", f"pipeline_ops/{filename}", "scripts_pipeline_pattern"
        return "08_scripts", f"utilities/{filename}", "scripts_utility_pattern"
    
    # Rule 3: Safety patterns → L5_safety
    if any(x in name_lower for x in ["_safety_", "_compliance_", "_ethics_", "pii", "redaction"]) or "safety" in hints:
        return "01_agentic_core", f"L5_safety/guardrails/{filename}", "safety_guardrails_pattern"
    
    # Rule 4: Execution/runtime patterns
    if any(x in name_lower for x in ["_execution_", "_runtime_", "executor"]) or "execution" in hints:
        return "03_runtime", f"runtime_ops/execution/{filename}", "runtime_execution_pattern"
    
    # Rule 5: Config patterns
    if any(x in name_lower for x in ["_config_", "_settings_", "_registry_"]) or "config" in hints:
        return "05_config", f"logic/settings/{filename}", "config_settings_pattern"
    
    # Rule 6: Schema/validation patterns
    if any(x in name_lower for x in ["_schema_", "_validation_", "_model_"]) or "schema" in hints:
        return "02_schemas", f"logic/validation/{filename}", "schema_validation_pattern"
    
    # Rule 7: Prompt/template patterns
    if any(x in name_lower for x in ["_prompt_", "_template_", "governance"]):
        return "04_prompt_governance", f"templates/{filename}", "prompt_template_pattern"
    
    # Rule 8: Test patterns
    if name_lower.startswith("test_") or "_test_" in name_lower or "test" in hints:
        return "10_tests", f"unit/unassigned/{filename}", "test_pattern"
    
    # Rule 9: Resume engine content → apps_rg
    if "resume_engine" in hints or any(x in name_lower for x in ["jd_", "resume_", "rag_", "bullet"]):
        return "09_apps", f"apps_rg/logic/{filename}", "resume_engine_pattern"
    
    # Rule 10: Personalization/outreach → apps_lic
    if any(x in name_lower for x in ["personalization", "outreach", "recipient", "engagement"]):
        return "09_apps", f"apps_lic/logic/{filename}", "outreach_engine_pattern"
    
    # Rule 11: Formatters, adapters, exporters → observability
    if any(x in name_lower for x in ["formatter", "adapter", "exporter", "propagator"]):
        return "07_observability", f"logic/adapters/{filename}", "observability_adapter_pattern"
    
    # Rule 12: Inspectors, profilers, checkers → observability
    if any(x in name_lower for x in ["inspector", "profiler", "checker", "verifier"]):
        return "07_observability", f"logic/inspection/{filename}", "observability_inspection_pattern"
    
    # Rule 13: Store, cache patterns → data
    if any(x in name_lower for x in ["store", "cache", "audit"]):
        return "06_data", f"cache_ops/{filename}", "data_cache_pattern"
    
    # Rule 14: Coordinate, orchestrate, manage patterns
    if any(x in name_lower for x in ["coordinate", "orchestrate", "manage", "planning"]):
        return "03_runtime", f"pipeline_ops/orchestration/{filename}", "runtime_orchestration_pattern"
    
    # Rule 15: Compute, calculate, normalize, score patterns
    if any(x in name_lower for x in ["compute_", "calculate_", "normalize_", "score_", "weight_"]):
        return "01_agentic_core", f"L2_execution/scoring/{filename}", "agentic_scoring_pattern"
    
    # Rule 16: Enforce, validate, check patterns
    if any(x in name_lower for x in ["enforce_", "validate_", "check_"]):
        return "01_agentic_core", f"L5_safety/validation/{filename}", "agentic_validation_pattern"
    
    # Rule 17: Format, serialize, prepare patterns
    if any(x in name_lower for x in ["format_", "serialize_", "prepare_"]):
        return "03_runtime", f"runtime_ops/formatting/{filename}", "runtime_formatting_pattern"
    
    # Rule 18: Fetch, retrieve, query patterns
    if any(x in name_lower for x in ["fetch_", "retrieve_", "query_", "get_"]):
        return "01_agentic_core", f"L1_cognition/retrieval/{filename}", "agentic_retrieval_pattern"
    
    # Rule 19: Update, track patterns
    if any(x in name_lower for x in ["update_", "track_"]):
        return "01_agentic_core", f"L4_memory/state/{filename}", "agentic_memory_pattern"
    
    # Rule 20: Diagnose, inspect, assess patterns
    if any(x in name_lower for x in ["diagnose_", "inspect_", "assess_"]):
        return "07_observability", f"logic/diagnostics/{filename}", "observability_diagnostics_pattern"
    
    # Rule 21: Build, create, generate patterns
    if any(x in name_lower for x in ["build_", "create_", "generate_"]):
        return "01_agentic_core", f"L2_execution/generation/{filename}", "agentic_generation_pattern"
    
    # Rule 22: Implement, handle, apply patterns
    if any(x in name_lower for x in ["implement_", "handle_", "apply_"]):
        return "03_runtime", f"runtime_ops/handlers/{filename}", "runtime_handler_pattern"
    
    # Rule 23: Evaluate, rank, sort, order patterns
    if any(x in name_lower for x in ["evaluate_", "rank_", "sort_", "order_", "prioritize_"]):
        return "01_agentic_core", f"L2_execution/ranking/{filename}", "agentic_ranking_pattern"
    
    # Rule 24: Match, find, search patterns
    if any(x in name_lower for x in ["match_", "find_", "search_"]):
        return "01_agentic_core", f"L1_cognition/search/{filename}", "agentic_search_pattern"
    
    # Rule 25: Parse, extract, load patterns
    if any(x in name_lower for x in ["parse_", "extract_", "load_"]):
        return "03_runtime", f"runtime_ops/parsing/{filename}", "runtime_parsing_pattern"
    
    # Rule 26: Call, invoke, dispatch patterns
    if any(x in name_lower for x in ["call_", "invoke_", "dispatch_"]):
        return "03_runtime", f"runtime_ops/invocation/{filename}", "runtime_invocation_pattern"
    
    # Fallback: Archive in 06_data
    return "06_data", f"_unassigned_archive/{filename}", "fallback_archive"


def execute_merge(dry_run: bool = False) -> MergeManifest:
    """Execute the merge operation."""
    manifest = MergeManifest()
    
    if not UNASSIGNED_ROOT.exists():
        print(f"ERROR: {UNASSIGNED_ROOT} does not exist")
        return manifest
    
    # Collect all files
    all_files = list(UNASSIGNED_ROOT.rglob("*"))
    files_to_route = [f for f in all_files if f.is_file()]
    manifest.total_files = len(files_to_route)
    
    print(f"Found {manifest.total_files} files to route")
    
    for filepath in files_to_route:
        filename = filepath.name
        
        try:
            # Get routing decision (pass parent folder for context)
            parent_folder = filepath.parent.name if filepath.parent != UNASSIGNED_ROOT else ""
            target_folder, target_subpath, reason = route_file(filepath, filename, parent_folder)
            
            # Compute hash for verification
            content_hash = compute_hash(filepath)
            file_size = filepath.stat().st_size
            
            # Build target path
            target_base = TARGETS.get(target_folder, TARGETS["06_data"])
            target_path = target_base / target_subpath
            
            routing = FileRouting(
                source_path=filepath,
                target_folder=target_folder,
                target_subpath=target_subpath,
                reason=reason,
                content_hash=content_hash,
                file_size=file_size,
            )
            
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
                
                # Copy file (preserve original for safety)
                shutil.copy2(filepath, target_path)
                
                # Verify copy
                if compute_hash(target_path) == content_hash:
                    manifest.routed_files += 1
                else:
                    manifest.errors.append({
                        "source": str(filepath),
                        "error": "Hash mismatch after copy",
                    })
            else:
                manifest.routed_files += 1
                print(f"  [DRY-RUN] {filepath.name} → {target_folder}/{target_subpath}")
                
        except Exception as e:
            manifest.errors.append({
                "source": str(filepath),
                "error": str(e),
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
    
    # Group by target folder
    by_folder = {}
    for r in manifest.routings:
        folder = r["target"].split("/")[0]
        by_folder[folder] = by_folder.get(folder, 0) + 1
    
    print("\nFiles per target folder:")
    for folder, count in sorted(by_folder.items()):
        print(f"  {folder}: {count}")
    
    if manifest.errors:
        print("\nErrors:")
        for err in manifest.errors[:10]:
            print(f"  {err['source']}: {err['error']}")
        if len(manifest.errors) > 10:
            print(f"  ... and {len(manifest.errors) - 10} more")
    
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
        print("You may now safely delete _unassigned/ after verification.")
    elif dry_run:
        print("\n[OK] Dry run complete. Run without --dry-run to execute.")
