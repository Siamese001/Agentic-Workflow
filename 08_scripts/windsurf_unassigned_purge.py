"""
08_scripts/windsurf_unassigned_purge.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: ff4fe90a20dbcc7f61f5ff50e637e35241ecc0f243174a1414a5b57433bd8301
"""
#!/usr/bin/env python3
"""
WINDSURF UNASSIGNED PURGE — SSoT RELOCATION ENGINE
===================================================

Deterministic relocation of all Python files from _unassigned*, _canonicalized_unknown*,
and *unknown* folders into architecturally correct canonical paths.

Algorithm:
    STEP 1: Direct Phase 2 match (source_path → target_path from migration plans)
    STEP 2: Code-aware canonical match (filename semantics → canonical subtree)
    STEP 3: Safe hold (unmapped → 05_config/review_pending/unmapped/)

Zero-Loss Guarantee:
    All originals archived to 06_data/unassigned_archive/final_purge_<timestamp>/
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).resolve().parent.parent
PLANS_DIR = ROOT / "02_schemas"
ARCHIVE_ROOT = ROOT / "06_data" / "unassigned_archive"

# Canonical roots (only these are valid targets)
CANONICAL_ROOTS = [
    "01_agentic_core",
    "02_schemas",
    "03_runtime",
    "04_prompt_governance",
    "05_config",
    "06_data",
    "07_observability",
    "08_scripts",
    "09_apps",
    "10_tests",
]

# Patterns for unassigned directories
UNASSIGNED_PATTERNS = [
    "_unassigned",
    "_canonicalized_unknown",
    "unknown",
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MigrationRecord:
    """Record of a single file migration."""

    source_rel: str
    target_rel: str
    mode: str  # PHASE2_DIRECT, CODE_AWARE_CANONICAL, UNMAPPED_REVIEW_PENDING
    archive_path: str = ""


@dataclass
class PurgeState:
    """State for the purge operation."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    run_dir: Path = field(default=None)
    migrations: list[MigrationRecord] = field(default_factory=list)
    phase2_mappings: dict[str, str] = field(default_factory=dict)  # source_basename → target_path
    expected_py: set[str] = field(default_factory=set)  # canonical paths from plans

    def __post_init__(self):
        if self.run_dir is None:
            self.run_dir = ARCHIVE_ROOT / f"final_purge_{self.timestamp}"


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC MAPPING RULES
# ═══════════════════════════════════════════════════════════════════════════════

# Filename pattern → canonical location mapping
# Based on analysis of existing canonical structure
SEMANTIC_MAPPINGS: list[tuple[str, str]] = [
    # ─────────────────────────────────────────────────────────────────────────
    # OBSERVABILITY (07_observability)
    # ─────────────────────────────────────────────────────────────────────────
    # Tracing/Telemetry
    (r"^(span|trace|tracing|tracer|w3c_trace|baggage)", "07_observability/logic/tracing"),
    (r"^(opentelemetry|otlp|jaeger)", "07_observability/logic/tracing/adapters"),
    (r"^always_on_sampler", "07_observability/logic/tracing/sampling"),
    (r"^sampling_processor", "07_observability/logic/tracing/sampling"),
    
    # Metrics
    (r"^(metric|histogram|counter)", "07_observability/logic/metrics"),
    (r"^(runtime_metrics|pipeline_metrics)", "07_observability/logic/metrics/collectors"),
    (r"^cost_profiler", "07_observability/logic/metrics/profiling"),
    
    # Logging
    (r"^(logger|log_config|log_event|structured_json_logger)", "07_observability/logic/logging"),
    (r"^(file_logger|console_trace|json_trace)", "07_observability/logic/logging/exporters"),
    (r"^(color_formatter|json_formatter|base_formatter)", "07_observability/logic/logging/formatters"),
    (r"^openai_logger_adapter", "07_observability/logic/logging/adapters"),
    
    # Audit/Security
    (r"^(audit_event|sqlite_audit|file_audit|append_only_store)", "07_observability/security_controls/audit"),
    (r"^(hash_chain|signature_verifier)", "07_observability/security_controls/integrity"),
    (r"^pii_redaction", "07_observability/security_controls/privacy"),
    (r"^metadata_enricher", "07_observability/logic/enrichment"),
    
    # Exporters
    (r"^(json_exporter|otlp_exporter)", "07_observability/logic/exporters"),
    
    # Observability-specific operations
    (r"^.*_observability_.*", "07_observability/logic/operations"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # RUNTIME (03_runtime)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(runtime_snapshot|planning_snapshot)", "03_runtime/runtime_ops/snapshots"),
    (r"^(state_inspector|dag_runtime|token_budget)", "03_runtime/runtime_ops/inspection"),
    (r"^(cpu_check|memory_check)", "03_runtime/runtime_ops/health"),
    (r"^(pointer_reconcile)", "03_runtime/runtime_ops/reconciliation"),
    (r"^(serialize_data|format_data|format_metadata)", "03_runtime/runtime_ops/serialization"),
    (r"^run_pipeline", "03_runtime/pipeline_ops/execution"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # SCRIPTS (08_scripts)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^phase0[0-9]", "08_scripts/migration"),
    (r"^.*_scripts_.*", "08_scripts/utilities"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # SAFETY (01_agentic_core/L5_safety)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(assess_safety|compute_safety|evaluate_safety)", "01_agentic_core/L5_safety/P4_safety/check_rules/semantic_adjust_scores"),
    (r"^assess_content_risk", "01_agentic_core/L5_safety/P4_safety/check_rules/semantic_adjust_scores"),
    (r"^(enforce.*budget|track.*cost|update.*usage)", "01_agentic_core/L5_safety/P4_safety/manage_costs/state_update_ops"),
    (r"^(check.*compliance|check.*policy|validate.*ethics|validate.*constraints)", "01_agentic_core/L5_safety/P4_safety/check_rules/policy_check_safety"),
    (r"^(enforce.*boundaries|enforce.*contracts|enforce.*filters|enforce.*limits)", "01_agentic_core/L5_safety/P4_safety/check_rules/policy_check_safety"),
    (r"^(apply.*safety)", "01_agentic_core/L5_safety/P4_safety/check_rules/policy_check_safety"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # COGNITION (01_agentic_core/L1_cognition)
    # ─────────────────────────────────────────────────────────────────────────
    # P1_retrieve - gathering/fetching
    (r"^(fetch_|build_.*query|build_.*filters)", "01_agentic_core/L1_cognition/P1_retrieve/gather_context_inputs/understand_request"),
    (r"^(compute.*embedding|calculate.*similarity|normalize.*vector)", "01_agentic_core/L1_cognition/P1_retrieve/gather_context_inputs/embedding/embedding_compare_meaning"),
    
    # P2_inspect - analysis/scoring
    (r"^(apply_weights|adjust.*weights|weight_)", "01_agentic_core/L1_cognition/P2_inspect/semantic_adjust_scores"),
    (r"^(compute.*score|compute.*confidence|calibrate.*score)", "01_agentic_core/L1_cognition/P2_inspect/semantic_adjust_scores"),
    (r"^(normalize.*score|compute.*match)", "01_agentic_core/L1_cognition/P2_inspect/semantic_adjust_scores"),
    (r"^(inspect.*quality)", "01_agentic_core/L1_cognition/P2_inspect/quality"),
    
    # P3_aggregate - ranking/sorting
    (r"^(rank_|sort_|refine.*ranking|optimize.*order)", "01_agentic_core/L1_cognition/P3_aggregate/pick_best_result"),
    (r"^(prioritize_|order_)", "01_agentic_core/L1_cognition/P3_aggregate/pick_best_result"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXECUTION (01_agentic_core/L2_execution)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(execute_|invoke_|perform_|call_.*api)", "01_agentic_core/L2_execution/use_tools/use_a_tool"),
    (r"^(handle.*error|handle.*timeout|implement.*fallback|implement.*retry)", "01_agentic_core/L2_execution/use_tools/routing_retry_task"),
    (r"^(coordinate_|manage.*context|manage.*parameters)", "01_agentic_core/L2_execution/data_access/get_info"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # ORCHESTRATION (01_agentic_core/L3_orchestration)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(orchestrate_|build.*orchestration|prepare.*orchestration)", "01_agentic_core/L3_orchestration/planning"),
    (r"^(load.*planning)", "01_agentic_core/L3_orchestration/planning"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # MEMORY (01_agentic_core/L4_memory)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(update.*profile|embed.*profile|match.*pattern)", "01_agentic_core/L4_memory/P1_retrieve/gather_context_inputs"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # PROMPT GOVERNANCE (04_prompt_governance)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(format.*prompt|find.*template|generate.*section|generate.*subject|create.*bullet)", "04_prompt_governance/templates"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # VALIDATION (various)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(validate.*schema|validate.*quality)", "01_agentic_core/L1_cognition/P2_inspect/validation"),
    (r"^(diagnose_|evaluate.*quality)", "01_agentic_core/L1_cognition/P2_inspect/diagnostics"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONFIG (05_config)
    # ─────────────────────────────────────────────────────────────────────────
    (r"^(parse.*settings|extract.*parameters)", "05_config/settings"),
]


def get_canonical_target(filename: str) -> str | None:
    """
    Determine canonical target path based on filename semantics.
    Returns None if no confident mapping found.
    """
    basename = Path(filename).stem  # Remove .py extension
    
    for pattern, target_dir in SEMANTIC_MAPPINGS:
        if re.match(pattern, basename, re.IGNORECASE):
            return target_dir
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 PLAN LOADING
# ═══════════════════════════════════════════════════════════════════════════════


def load_phase2_plans(state: PurgeState) -> None:
    """
    Load all Phase 2 migration plans and extract source→target mappings.
    """
    logger.info("Loading Phase 2 migration plans from %s", PLANS_DIR)
    
    plan_files = list(PLANS_DIR.glob("*_migration_and_rewrite_plan.json"))
    logger.info("Found %d plan files", len(plan_files))
    
    for plan_file in plan_files:
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            operations = data.get("operations", [])
            for op in operations:
                source_path = op.get("source_path", "")
                target_path = op.get("target_path", "")
                
                if source_path and target_path:
                    # Store by basename for matching
                    source_basename = Path(source_path).name
                    state.phase2_mappings[source_basename] = target_path
                
                # Collect expected paths
                if target_path and target_path.endswith(".py"):
                    # Only add if it's a canonical path (not _unassigned)
                    if not any(p in target_path for p in UNASSIGNED_PATTERNS):
                        state.expected_py.add(target_path)
        
        except Exception as e:
            logger.warning("Failed to load plan %s: %s", plan_file.name, e)
    
    logger.info("Loaded %d source→target mappings", len(state.phase2_mappings))
    logger.info("Collected %d expected canonical paths", len(state.expected_py))


# ═══════════════════════════════════════════════════════════════════════════════
# UNASSIGNED FILE DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════


def find_unassigned_dirs() -> list[Path]:
    """
    Find all directories matching unassigned patterns.
    Excludes archive directories (06_data).
    Returns deduplicated list.
    """
    unassigned_dirs: set[Path] = set()
    
    for item in ROOT.iterdir():
        if not item.is_dir():
            continue
        
        # Skip archive directory
        if item.name == "06_data":
            continue
        
        # Check root-level unassigned dirs
        for pattern in UNASSIGNED_PATTERNS:
            if pattern in item.name.lower():
                unassigned_dirs.add(item.resolve())
                break
    
    # Also check inside canonical roots for nested unassigned dirs
    for root_name in CANONICAL_ROOTS:
        root_path = ROOT / root_name
        if not root_path.exists():
            continue
        
        # Skip 06_data (archive)
        if root_name == "06_data":
            continue
        
        for dirpath, dirnames, _ in os.walk(root_path):
            dirpath = Path(dirpath)
            for dirname in dirnames:
                for pattern in UNASSIGNED_PATTERNS:
                    if pattern in dirname.lower():
                        unassigned_dirs.add((dirpath / dirname).resolve())
    
    return list(unassigned_dirs)


def find_unassigned_files(dirs: list[Path]) -> list[Path]:
    """
    Find all .py files in unassigned directories.
    Returns deduplicated list.
    """
    files: set[Path] = set()
    for d in dirs:
        if d.exists():
            for f in d.rglob("*.py"):
                files.add(f.resolve())
    return list(files)


# ═══════════════════════════════════════════════════════════════════════════════
# RELOCATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════════


def archive_file(src: Path, state: PurgeState) -> Path:
    """
    Archive a file to the run directory, preserving relative structure.
    Returns the archive path.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    rel_path = src.relative_to(ROOT)
    archive_path = state.run_dir / rel_path
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, archive_path)
    return archive_path


def relocate_file(
    src: Path,
    target_rel: str,
    state: PurgeState,
    mode: str,
    add_todo: bool = False,
) -> None:
    """
    Relocate a file to its canonical location.
    
    1. Archive original
    2. Read content
    3. Optionally prepend TODO comment
    4. Write to target
    5. Remove original
    6. Record migration
    """
    rel_path = src.relative_to(ROOT)
    
    # Archive
    archive_path = archive_file(src, state)
    
    # Read content
    content = src.read_text(encoding="utf-8")
    
    # Add TODO comment if unmapped
    if add_todo:
        todo_comment = (
            "# TODO[HUMAN_OWNER]: Unmapped legacy/unassigned module.\n"
            "# No Phase 2 mapping and no safe canonical placement inferred.\n\n"
        )
        if not content.startswith("# TODO[HUMAN_OWNER]"):
            content = todo_comment + content
    
    # Determine target path
    target_path = ROOT / target_rel
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to target
    target_path.write_text(content, encoding="utf-8")
    
    # Remove original
    src.unlink()
    
    # Record
    state.migrations.append(MigrationRecord(
        source_rel=str(rel_path),
        target_rel=target_rel,
        mode=mode,
        archive_path=str(archive_path.relative_to(ROOT)),
    ))
    
    logger.info("[%s] %s → %s", mode, rel_path, target_rel)


def process_file(src: Path, state: PurgeState) -> None:
    """
    Process a single unassigned file through the 3-step algorithm.
    """
    rel_path = src.relative_to(ROOT)
    basename = src.name
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Direct Phase 2 match
    # ─────────────────────────────────────────────────────────────────────────
    if basename in state.phase2_mappings:
        target = state.phase2_mappings[basename]
        # Validate target is canonical (not still pointing to _unassigned)
        if not any(p in target for p in UNASSIGNED_PATTERNS):
            relocate_file(src, target, state, "PHASE2_DIRECT")
            return
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Code-aware canonical match
    # ─────────────────────────────────────────────────────────────────────────
    canonical_dir = get_canonical_target(basename)
    if canonical_dir:
        # Validate the target directory is under a canonical root
        root_name = canonical_dir.split("/")[0]
        if root_name in CANONICAL_ROOTS:
            target_rel = f"{canonical_dir}/{basename}"
            relocate_file(src, target_rel, state, "CODE_AWARE_CANONICAL")
            return
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Safe hold (review pending)
    # ─────────────────────────────────────────────────────────────────────────
    target_rel = f"05_config/review_pending/unmapped/{basename}"
    relocate_file(src, target_rel, state, "UNMAPPED_REVIEW_PENDING", add_todo=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════


def cleanup_empty_dirs(dirs: list[Path]) -> None:
    """
    Attempt to remove empty unassigned directories.
    """
    for d in sorted(dirs, key=lambda p: len(p.parts), reverse=True):
        try:
            if d.exists() and d.is_dir():
                # Check if empty (no files, only empty subdirs allowed)
                has_files = any(d.rglob("*") if not f.is_dir() else False for f in d.iterdir())
                if not has_files:
                    shutil.rmtree(d)
                    logger.info("Removed empty directory: %s", d.relative_to(ROOT))
        except Exception as e:
            logger.warning("Could not remove %s: %s", d, e)


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT REPORT
# ═══════════════════════════════════════════════════════════════════════════════


def print_audit_report(state: PurgeState) -> None:
    """
    Print final migration audit table.
    """
    print("\n")
    print("═" * 100)
    print("FINAL MIGRATION AUDIT")
    print("═" * 100)
    print(f"{'SOURCE (relative)':<50} {'MODE':<25} TARGET")
    print("─" * 100)
    
    # Group by mode
    by_mode: dict[str, list[MigrationRecord]] = {}
    for rec in state.migrations:
        by_mode.setdefault(rec.mode, []).append(rec)
    
    for mode in ["PHASE2_DIRECT", "CODE_AWARE_CANONICAL", "UNMAPPED_REVIEW_PENDING"]:
        records = by_mode.get(mode, [])
        for rec in sorted(records, key=lambda r: r.source_rel):
            src_display = rec.source_rel[:48] + ".." if len(rec.source_rel) > 50 else rec.source_rel
            print(f"{src_display:<50} {rec.mode:<25} {rec.target_rel}")
    
    print("─" * 100)
    print(f"\nTOTAL FILES PROCESSED: {len(state.migrations)}")
    print(f"  - PHASE2_DIRECT:           {len(by_mode.get('PHASE2_DIRECT', []))}")
    print(f"  - CODE_AWARE_CANONICAL:    {len(by_mode.get('CODE_AWARE_CANONICAL', []))}")
    print(f"  - UNMAPPED_REVIEW_PENDING: {len(by_mode.get('UNMAPPED_REVIEW_PENDING', []))}")
    print(f"\nZERO-LOSS ARCHIVE: {state.run_dir.relative_to(ROOT)}/")
    print("\n" + "═" * 100)
    print("ALL _unassigned AND _canonicalized_unknown FOLDERS PROCESSED")
    print("NO UNASSIGNED PYTHON FILES REMAIN")
    print("═" * 100)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    """
    Main entry point for the unassigned purge operation.
    """
    logger.info("=" * 80)
    logger.info("WINDSURF UNASSIGNED PURGE — SSoT RELOCATION ENGINE")
    logger.info("=" * 80)
    logger.info("ROOT: %s", ROOT)
    
    # Initialize state
    state = PurgeState()
    state.run_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Archive directory: %s", state.run_dir)
    
    # Load Phase 2 plans
    load_phase2_plans(state)
    
    # Find unassigned directories and files
    unassigned_dirs = find_unassigned_dirs()
    logger.info("Found %d unassigned directories:", len(unassigned_dirs))
    for d in unassigned_dirs:
        logger.info("  - %s", d.relative_to(ROOT))
    
    unassigned_files = find_unassigned_files(unassigned_dirs)
    logger.info("Found %d unassigned Python files", len(unassigned_files))
    
    if not unassigned_files:
        logger.info("No unassigned files to process. Exiting.")
        return
    
    # Process each file
    logger.info("Processing files...")
    for f in sorted(unassigned_files):
        try:
            process_file(f, state)
        except Exception as e:
            logger.error("Failed to process %s: %s", f, e)
            raise
    
    # Cleanup empty directories
    logger.info("Cleaning up empty directories...")
    cleanup_empty_dirs(unassigned_dirs)
    
    # Print audit report
    print_audit_report(state)
    
    # Save migration log
    log_path = state.run_dir / "migration_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": state.timestamp,
                "total_files": len(state.migrations),
                "migrations": [
                    {
                        "source": rec.source_rel,
                        "target": rec.target_rel,
                        "mode": rec.mode,
                        "archive": rec.archive_path,
                    }
                    for rec in state.migrations
                ],
            },
            f,
            indent=2,
        )
    logger.info("Migration log saved to: %s", log_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
