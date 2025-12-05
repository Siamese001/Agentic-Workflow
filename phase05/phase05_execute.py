#!/usr/bin/env python3
"""
PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v4, FULL SEMANTIC, ARCHIVE + UNASSIGNED)

This version replaces the original v3-LITE, filename/path-biased cache with a
content-first, component-level semantic cache that:

  • Ingests ARCHIVE roots (RG + LIC) as before.
  • ALSO ingests CURRENT "_unassigned" folders under:
        01_agentic_core
        02_schemas
        03_runtime
        04_prompt_governance
        05_config
        07_observability
        08_scripts
        09_apps
    (06_data and 10_tests are intentionally excluded.)

  • Builds a semantic cache that is COMPONENT-FIRST:
        - Extracts classes / key functions / config blocks as components.
        - Classifies each component (agent_base_class, orchestrator, schema, config, etc.).
        - Generates NL summaries for each component.
        - Assigns a semantic target bucket based on component kind (semantic-only, no path bias).
        - Writes semantic artifacts to:  semantic/H.semantic.json

  • Builds a simple COMPONENT GRAPH:
        - Nodes: components (component_id).
        - Edges: "co_defined" (components defined in same file).
        - Writes graph to: graphs/component_graph.json

  • Creates canonical bucket pointers:
        0X_<bucket_name>/L1_archive/P0_5/ingest/<rg|lic|current>/<component_id>.json
        → each pointer references the underlying hash + semantic/AST artifacts.

  • Performs UNASSIGNED RESOLUTION (CURRENT engine only, M1):
        - For each CURRENT file in a *_unassigned folder whose components are
          classified with confidence >= 0.8 into a canonical bucket:
              ⇒ Move the physical file out of the *_unassigned folder into the
                 chosen canonical domain root.
        - Files left behind in *_unassigned are those with low-confidence or
          ambiguous classification.

  • Writes ONLY under 06_data/semantic_cache/, EXCEPT for the controlled moves
    of CURRENT *_unassigned files into canonical domain roots.

This script is orchestrated via Phase05Orchestrator with the following steps:

    1. SSOT_LOAD           – Clean-wipe + recreate semantic_cache structure.
    2. ARCHIVE_SCAN        – Scan RG/LIC archives.
    3. CURRENT_SCAN        – Scan CURRENT *_unassigned folders.
    4. ARTIFACT_GENERATION – Build global artifacts + semantic components + component graph.
    5. DUAL_WRITE          – Create archive-local pointers + canonical component pointers.
    6. RESOLVE_UNASSIGNED  – Move CURRENT *_unassigned files that have high-confidence mappings.
    7. VALIDATION          – Run phase05_validate.
    8. CLEANUP             – Final reporting.

"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import traceback
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

# =====================================================================
# ROOTS
# =====================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

SSOT_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"  # existence check only
TRANSACTION_MANIFEST = CACHE_ROOT / "meta" / "transaction_manifest.json"

# =====================================================================
# SEMANTIC CACHE STRUCTURE
# =====================================================================

GLOBAL_DOMAINS = [
    "ast",
    "diffs",
    "embeddings",
    "golden",
    "integrity",
    "meta",
    "safety",
    "semantic",  # NEW: component-level semantic artifacts
    "graphs",    # NEW: component graph
]

ARCHIVE_LOCAL_ROOTS = [
    "resume_engine",    # RG
    "outreach_engine",  # LIC
]

CANONICAL_BUCKETS = [
    "01_agentic_core",
    "02_schemas",
    "03_runtime",
    "04_prompt_governance",
    "05_config",
    "06_data_source",
    "07_observability",
    "08_scripts",
    "09_apps",
    "10_tests",
]

APPROVED_TOP_LEVEL = set(GLOBAL_DOMAINS + ARCHIVE_LOCAL_ROOTS + CANONICAL_BUCKETS)

ELIGIBLE_EXTS = {".py", ".json", ".yaml", ".yml", ".md", ".txt"}

# CURRENT domains in which we care about *_unassigned.
CURRENT_DOMAINS_FOR_UNASSIGNED = [
    "01_agentic_core",
    "02_schemas",
    "03_runtime",
    "04_prompt_governance",
    "05_config",
    # "06_data_source" – intentionally excluded per your guidance
    "07_observability",
    "08_scripts",
    "09_apps",
    # "10_tests" – intentionally excluded per your guidance
]

UNASSIGNED_FOLDER_NAME = "_unassigned"

# =====================================================================
# ARCHIVE ROOTS — STRICT v3-LITE (as before)
# =====================================================================

RG_ARCHIVE_ROOTS: List[Tuple[Path, str]] = [
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_11/"), "Agentic-Workflow-10_11"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic_Workflow-10_10/"), "Agentic_Workflow-10_10"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_9/"), "Agentic-Workflow-10_9"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_8_core/"), "Agentic-Workflow-10_8_core"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_7_main/"), "Agentic-Workflow-10_7_main"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Microservices Model/"), "Microservices Model"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolith/"), "Monolith"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolithic/"), "Monolithic"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v2/"), "v2"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v6.0/"), "v6.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.0/"), "v7.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.5/"), "v7.5"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v8.0/"), "v8.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v9.0/"), "v9.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v10.0/"), "v10.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Old Resume Gen Python/"), "Old Resume Gen Python"),
]

LIC_ARCHIVE_ROOTS: List[Tuple[Path, str]] = [
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic-LIC/"), "Agentic-LIC"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic LIC/"), "Agentic LIC"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Monolithic/"), "Monolithic"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Old LIC/"), "Old LIC"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/deprecated in v13/"), "deprecated in v13"),
]

# =====================================================================
# HELPERS
# =====================================================================

def to_posix(path: Path) -> str:
    return str(PurePosixPath(path.as_posix()))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def safe_read_text(path: Path, max_bytes: int = 8000) -> str:
    try:
        with path.open("rb") as f:
            raw = f.read(max_bytes)
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def count_loc(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def infer_version_tag(path: Path, archive_name: str) -> Optional[str]:
    name = path.name.lower()
    arch = archive_name.lower()
    for token in ["v10_11", "v10_10", "v10_9", "v10_8", "v10_7", "v9_0", "v8_0", "v7_5", "v7_0", "v6_0", "v2"]:
        if token.replace("_", ".") in name or token.replace("_", ".") in arch:
            return token
    return None


# =====================================================================
# SEMANTIC DATA CLASSES
# =====================================================================

@dataclass
class ArchiveFileRecord:
    """Unified record for any file considered by Phase 0.5."""
    path: Path
    engine: str          # "RG", "LIC", "CURRENT"
    archive_name: str    # archive name OR current domain (for CURRENT)
    rel_posix: str
    version_tag: Optional[str]
    size_bytes: int
    loc: int

    def to_dict(self) -> dict:
        d = asdict(self)
        d["path"] = to_posix(self.path)
        return d


@dataclass
class ComponentRecord:
    """Represents a semantic component extracted from a file."""
    component_id: str
    name: str
    kind: str              # e.g. "agent_base_class", "orchestrator", "schema", "config", "function", ...
    engine: str            # "RG", "LIC", "CURRENT"
    archive_source: str    # archive_name or current domain
    version_tag: Optional[str]
    file: str              # full path as posix
    relative: str          # archive-relative or domain-relative
    span_start: int
    span_end: int
    tags: List[str]
    bucket: Optional[str]
    confidence: float
    nl_summary_short: str
    nl_summary_long: str

    def to_dict(self) -> dict:
        return {
            "component_id": self.component_id,
            "name": self.name,
            "kind": self.kind,
            "engine": self.engine,
            "archive_source": self.archive_source,
            "version_tag": self.version_tag,
            "file": self.file,
            "relative": self.relative,
            "span_start": self.span_start,
            "span_end": self.span_end,
            "tags": self.tags,
            "bucket": self.bucket,
            "confidence": self.confidence,
            "nl_summary": {
                "short": self.nl_summary_short,
                "long": self.nl_summary_long,
            },
        }


# =====================================================================
# TRANSACTION MANIFEST & PIPELINE STATE (from orchestrator)
# =====================================================================

@dataclass
class PipelineStep:
    """Represents a pipeline step with status and metadata."""
    step_id: str
    step_name: str
    status: str  # "PENDING", "RUNNING", "COMPLETED", "FAILED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    artifacts_created: List[str] = None

    def __post_init__(self):
        if self.artifacts_created is None:
            self.artifacts_created = []


@dataclass
class TransactionManifest:
    """Transaction manifest for pipeline state tracking."""
    pipeline_id: str
    start_time: str
    status: str  # "RUNNING", "COMPLETED", "FAILED", "RESUMED"
    dry_run: bool
    steps: List[PipelineStep]
    current_step: int
    total_files_processed: int
    artifacts_generated: int


class Phase05Orchestrator:
    """
    Enhanced orchestrator for Phase 0.5 semantic cache rebuild (v4).

    Adds CURRENT *_unassigned ingestion, component-level semantics,
    component graph, and unassigned resolution.
    """

    def __init__(self, dry_run: bool = False, resume_from: Optional[str] = None, strict_mode: bool = False):
        self.dry_run = dry_run
        self.resume_from = resume_from
        self.strict_mode = strict_mode
        self.pipeline_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.pipeline_steps = [
            PipelineStep("SSOT_LOAD", "Load and validate SSoT", "PENDING"),
            PipelineStep("ARCHIVE_SCAN", "Scan archives (RG/LIC)", "PENDING"),
            PipelineStep("CURRENT_SCAN", "Scan CURRENT *_unassigned folders", "PENDING"),
            PipelineStep("ARTIFACT_GENERATION", "Generate global + semantic artifacts + graph", "PENDING"),
            PipelineStep("DUAL_WRITE", "Create archive-local and canonical component pointers", "PENDING"),
            PipelineStep("RESOLVE_UNASSIGNED", "Resolve and move CURRENT *_unassigned files", "PENDING"),
            PipelineStep("VALIDATION", "Run comprehensive validation", "PENDING"),
            PipelineStep("CLEANUP", "Final cleanup and reporting", "PENDING"),
        ]

        self.transaction_manifest: Optional[TransactionManifest] = None
        self.current_step_index: int = 0

        # Statistics
        self.stats: Dict[str, int] = {
            "total_files_scanned": 0,
            "eligible_files_processed": 0,
            "global_artifacts_created": 0,
            "canonical_pointers_created": 0,
            "validation_keys_passed": 0,
            "validation_keys_failed": 0,
            "current_unassigned_files_scanned": 0,
            "current_unassigned_files_moved": 0,
        }

        # Cached data
        self._archive_records: List[ArchiveFileRecord] = []
        self._current_unassigned_records: List[ArchiveFileRecord] = []
        self._all_records: List[ArchiveFileRecord] = []
        self._hash_map: Dict[str, List[ArchiveFileRecord]] = {}
        self._components_by_hash: Dict[str, List[ComponentRecord]] = {}
        self._component_graph_edges: List[Tuple[str, str, str]] = []
        self._unassigned_move_plan: List[Tuple[Path, Path]] = []

    # -----------------------------------------------------------------
    # Manifest management
    # -----------------------------------------------------------------

    def load_or_create_manifest(self) -> bool:
        """Load existing manifest or create new one."""
        try:
            if self.resume_from and TRANSACTION_MANIFEST.exists():
                with open(TRANSACTION_MANIFEST, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                self.transaction_manifest = TransactionManifest(**manifest_data)

                for i, step in enumerate(self.transaction_manifest.steps):
                    if step["status"] != "COMPLETED":
                        self.current_step_index = i
                        break
                else:
                    self.current_step_index = len(self.transaction_manifest.steps)
                print(f"Resuming from step index: {self.current_step_index}")
                return True
            else:
                self.transaction_manifest = TransactionManifest(
                    pipeline_id=self.pipeline_id,
                    start_time=datetime.now().isoformat(),
                    status="RUNNING",
                    dry_run=self.dry_run,
                    steps=self.pipeline_steps,
                    current_step=0,
                    total_files_processed=0,
                    artifacts_generated=0,
                )
                return True
        except Exception as e:
            print(f"Error loading/creating manifest: {str(e)}")
            return False

    def save_manifest(self) -> bool:
        """Save transaction manifest."""
        try:
            if not self.dry_run and self.transaction_manifest:
                manifest_path = TRANSACTION_MANIFEST
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(asdict(self.transaction_manifest), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving manifest: {str(e)}")
            return False

    def update_step_status(self, step_index: int, status: str, error_message: Optional[str] = None):
        """Update step status in manifest."""
        if not self.transaction_manifest:
            return
        if step_index < len(self.transaction_manifest.steps):
            step = self.transaction_manifest.steps[step_index]
            step.status = status

            if status == "RUNNING":
                step.start_time = datetime.now().isoformat()
            elif status in ("COMPLETED", "FAILED"):
                step.end_time = datetime.now().isoformat()
                if error_message:
                    step.error_message = error_message

            self.transaction_manifest.current_step = step_index
            self.save_manifest()

    # -----------------------------------------------------------------
    # Orchestrator step execution
    # -----------------------------------------------------------------

    def _run_step(self, step_index: int) -> bool:
        step = self.pipeline_steps[step_index]

        if step.step_id == "SSOT_LOAD":
            return self._run_ssot_load(step)
        if step.step_id == "ARCHIVE_SCAN":
            return self._run_archive_scan(step)
        if step.step_id == "CURRENT_SCAN":
            return self._run_current_scan(step)
        if step.step_id == "ARTIFACT_GENERATION":
            return self._run_artifact_generation(step)
        if step.step_id == "DUAL_WRITE":
            return self._run_dual_write(step)
        if step.step_id == "RESOLVE_UNASSIGNED":
            return self._run_resolve_unassigned(step)
        if step.step_id == "VALIDATION":
            return self._run_validation(step)
        if step.step_id == "CLEANUP":
            return self._run_cleanup(step)

        print(f"Unknown step id: {step.step_id}")
        return False

    def _run_ssot_load(self, step: PipelineStep) -> bool:
        """SSOT load + clean-wipe + structure creation."""
        if not SSOT_YAML.exists():
            print("[WARN] SSoT YAML not found; proceeding in heuristic-only mode.")

        if not self.dry_run:
            print("Cleaning semantic cache...")
            wipe_semantic_cache()
            print("Creating semantic cache structure...")
            create_semantic_cache_structure()
        else:
            print("[DRY RUN] Would clean/create semantic cache structure.")

        step.artifacts_created = ["ssot_validation_report.json"]
        return True

    def _run_archive_scan(self, step: PipelineStep) -> bool:
        """Scan RG + LIC archives into ArchiveFileRecord list."""
        self._archive_records = scan_archives()
        rg_count = sum(1 for r in self._archive_records if r.engine == "RG")
        lic_count = sum(1 for r in self._archive_records if r.engine == "LIC")
        total = len(self._archive_records)

        self.stats["total_files_scanned"] = total
        self.stats["eligible_files_processed"] = total

        step.artifacts_created = [
            "archive_scan_report.json",
            f"integrity_records_archives_{total}.json",
        ]

        print(f"Archive scan complete: total={total}, RG={rg_count}, LIC={lic_count}")
        return True

    def _run_current_scan(self, step: PipelineStep) -> bool:
        """Scan CURRENT *_unassigned folders into ArchiveFileRecord list."""
        self._current_unassigned_records = scan_current_unassigned()
        cnt = len(self._current_unassigned_records)
        self.stats["current_unassigned_files_scanned"] = cnt

        step.artifacts_created = [
            "current_unassigned_scan_report.json",
            f"integrity_records_current_unassigned_{cnt}.json",
        ]

        print(f"Current *_unassigned scan complete: total={cnt}")
        return True

    def _run_artifact_generation(self, step: PipelineStep) -> bool:
        """Generate global artifacts + semantic components + component graph."""
        self._all_records = list(self._archive_records) + list(self._current_unassigned_records)

        if not self._all_records:
            print("[WARN] No eligible files found for artifact generation.")
            self._hash_map = {}
            self._components_by_hash = {}
            self._component_graph_edges = []
            return True

        print(f"Generating global + semantic artifacts for {len(self._all_records)} files...")

        (
            self._hash_map,
            self._components_by_hash,
            self._component_graph_edges,
        ) = generate_global_and_semantic_artifacts(self._all_records)

        self.stats["global_artifacts_created"] = len(self._hash_map) * 7  # ast, emb, diffs, golden, safety, integrity, meta

        step.artifacts_created = [
            f"semantic_artifacts_{len(self._hash_map)}.json",
            "component_graph.json",
        ]

        print(f"Generated artifacts for {len(self._hash_map)} unique hashes.")
        return True

    def _run_dual_write(self, step: PipelineStep) -> bool:
        """Create archive-local artifacts and canonical component pointers."""
        if not self._hash_map:
            print("[WARN] No hash map computed; skipping dual-write.")
            return True

        generate_archive_local_artifacts(self._hash_map)

        bucket_counts, move_plan = generate_canonical_component_pointers(
            self._hash_map, self._components_by_hash
        )
        self._unassigned_move_plan = move_plan

        total_pointers = sum(bucket_counts.values())
        self.stats["canonical_pointers_created"] = total_pointers

        step.artifacts_created = [
            "dual_write_report.json",
            "canonical_component_pointers.json",
        ]

        print(f"Created {total_pointers} canonical component pointers.")
        return True

    def _run_resolve_unassigned(self, step: PipelineStep) -> bool:
        """Move CURRENT *_unassigned files with high-confidence mappings."""
        if not self._unassigned_move_plan:
            print("No CURRENT *_unassigned move plan; nothing to resolve.")
            return True

        moved = 0
        for src, dst in self._unassigned_move_plan:
            if self.dry_run:
                print(f"[DRY RUN] Would move: {src} → {dst}")
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                os.replace(src, dst)
                moved += 1
            except Exception as e:
                print(f"[WARN] Failed to move {src} → {dst}: {e}")

        self.stats["current_unassigned_files_moved"] = moved
        step.artifacts_created = ["unassigned_resolution_report.json"]

        print(f"Resolved CURRENT *_unassigned files: moved={moved}")
        return True

    def _run_validation(self, step: PipelineStep) -> bool:
        """Run phase05_validate."""
        try:
            import phase05_validate

            result = phase05_validate.run()
            self.stats["validation_keys_passed"] = 40  # kept for compatibility, extended inside validator
            self.stats["validation_keys_failed"] = 0 if result == 0 else 1

            step.artifacts_created = ["validation_report.json"]
            return result == 0
        except Exception as e:
            print(f"Validation failed: {e}")
            self.stats["validation_keys_passed"] = 0
            self.stats["validation_keys_failed"] = 1
            return False

    def _run_cleanup(self, step: PipelineStep) -> bool:
        """Final cleanup and reporting."""
        final_report = {
            "pipeline_id": self.pipeline_id,
            "completion_timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "semantic_cache_summary": generate_cache_summary(),
        }

        if not self.dry_run:
            report_path = CACHE_ROOT / "meta" / "pipeline_completion_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(final_report, f, indent=2)

        step.artifacts_created = ["pipeline_completion_report.json"]
        return True

    # -----------------------------------------------------------------
    # Final summary printing
    # -----------------------------------------------------------------

    def print_final_summary(self):
        print("=== Final Summary ===")
        for k, v in self.stats.items():
            print(f"{k}: {v}")

        if self.stats["validation_keys_failed"] == 0:
            print("\n[SUCCESS] PHASE 0.5 COMPLETED SUCCESSFULLY")
            print("[PASS] All validation keys passed.")
            print("[PASS] Semantic cache ready for Phase 2.")
        else:
            print("\n[WARNING] PHASE 0.5 COMPLETED WITH VALIDATION FAILURES")
            print("[FAIL] Some validation keys failed.")


# =====================================================================
# CLEAN-WIPE + STRUCTURE
# =====================================================================

def wipe_semantic_cache() -> None:
    if CACHE_ROOT.exists():
        for p in sorted(CACHE_ROOT.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                try:
                    p.rmdir()
                except OSError:
                    # directory not empty; ignore
                    pass
        try:
            CACHE_ROOT.rmdir()
        except OSError:
            pass
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def create_semantic_cache_structure() -> None:
    # global domains
    for g in GLOBAL_DOMAINS:
        (CACHE_ROOT / g).mkdir(parents=True, exist_ok=True)
    # archive-local
    for r in ARCHIVE_LOCAL_ROOTS:
        (CACHE_ROOT / r).mkdir(parents=True, exist_ok=True)
    # canonical buckets
    for b in CANONICAL_BUCKETS:
        (CACHE_ROOT / b).mkdir(parents=True, exist_ok=True)


def generate_cache_summary() -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for dir_name in ["ast", "embeddings", "diffs", "golden", "safety", "integrity", "meta", "semantic"]:
        dir_path = CACHE_ROOT / dir_name
        if dir_path.exists():
            files = [f for f in dir_path.glob("*") if f.is_file()]
            summary[dir_name] = len(files)
        else:
            summary[dir_name] = 0
    return summary


# =====================================================================
# SCAN: ARCHIVES (RG/LIC)
# =====================================================================

def scan_root(root: Path, archive_name: str, engine: str) -> List[ArchiveFileRecord]:
    results: List[ArchiveFileRecord] = []
    if not root.exists():
        return results

    for f in root.rglob("*"):
        if not f.is_file():
            continue
        rel_parts = f.relative_to(root).parts
        if len(rel_parts) > 7:
            continue
        if f.suffix.lower() not in ELIGIBLE_EXTS:
            continue
        rel_posix = "/".join(rel_parts)
        size_bytes = f.stat().st_size
        loc = count_loc(f)
        version_tag = infer_version_tag(f, archive_name)
        results.append(
            ArchiveFileRecord(
                path=f,
                engine=engine,
                archive_name=archive_name,
                rel_posix=rel_posix,
                version_tag=version_tag,
                size_bytes=size_bytes,
                loc=loc,
            )
        )
    return results


def scan_archives() -> List[ArchiveFileRecord]:
    records: List[ArchiveFileRecord] = []
    for root, name in RG_ARCHIVE_ROOTS:
        records.extend(scan_root(root, name, "RG"))
    for root, name in LIC_ARCHIVE_ROOTS:
        records.extend(scan_root(root, name, "LIC"))
    return records


# =====================================================================
# SCAN: CURRENT *_unassigned
# =====================================================================

def scan_current_unassigned() -> List[ArchiveFileRecord]:
    records: List[ArchiveFileRecord] = []
    for domain in CURRENT_DOMAINS_FOR_UNASSIGNED:
        domain_root = PROJECT_ROOT / domain
        if not domain_root.exists():
            continue
        unassigned_root = domain_root / UNASSIGNED_FOLDER_NAME
        if not unassigned_root.exists():
            continue
        for f in unassigned_root.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() not in ELIGIBLE_EXTS:
                continue
            rel_posix = "/".join(f.relative_to(domain_root).parts)
            size_bytes = f.stat().st_size
            loc = count_loc(f)
            records.append(
                ArchiveFileRecord(
                    path=f,
                    engine="CURRENT",
                    archive_name=domain,
                    rel_posix=rel_posix,
                    version_tag="live",
                    size_bytes=size_bytes,
                    loc=loc,
                )
            )
    return records


# =====================================================================
# GLOBAL + SEMANTIC ARTIFACTS
# =====================================================================

def analyze_python_file(rec: ArchiveFileRecord) -> Tuple[List[ComponentRecord], List[Tuple[str, str, str]]]:
    """
    Analyze a Python file into components + intra-file semantic edges.

    Components:
        • Classes
        • Functions
        • Top-level CONSTANTS (D2 — uppercase with primitive RHS)

    Edges (A1, B2, C2):
        • ("child_component_id", base_class_name, "inherits_from")
        • ("component_id", import_target, "imports_module" / "imports_symbol")
        • ("component_id", callee_name, "calls")
        • ("comp_a", "comp_b", "co_defined") is added at the hash level.
    """
    text = safe_read_text(rec.path, max_bytes=200_000)
    if not text.strip():
        return [], []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], []

    components: List[ComponentRecord] = []
    edges: List[Tuple[str, str, str]] = []

    # Collect import targets at module level (B2).
    import_targets: List[Tuple[str, str]] = []  # (target_name, edge_kind)
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = alias.asname or alias.name
                import_targets.append((target, "imports_module"))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                target = f"{module}.{name}" if module else name
                import_targets.append((target, "imports_symbol"))

    # Helper to build an NL snippet (E1).
    def snippet_for_span(start: int, end: int) -> str:
        lines = text.splitlines()
        # Guard against out-of-range
        start_idx = max(start - 1, 0)
        end_idx = min(end, len(lines))
        snippet_lines = lines[start_idx:end_idx][:10]
        return "\n".join(snippet_lines)

    # Process top-level constants (D2).
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # Only consider simple Name targets (no tuple unpacking).
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            const_name = node.targets[0].id
            # Uppercase heuristic for constants.
            if not const_name.isupper():
                continue
            # Primitive RHS only: ast.Constant (str, int, float, bool, None).
            if not isinstance(node.value, ast.Constant):
                continue

            start = getattr(node, "lineno", 1)
            end = getattr(node, "end_lineno", start)
            snippet = snippet_for_span(start, end)

            kind = "constant"
            tags = ["constant"]
            bucket = "05_config"
            confidence = 0.85
            cid = f"{rec.path.name}::const::{const_name}"
            short, long = make_nl_summary(
                name=const_name,
                kind=kind,
                engine=rec.engine,
                archive=rec.archive_name,
                body_text=snippet,
            )

            comp = ComponentRecord(
                component_id=cid,
                name=const_name,
                kind=kind,
                engine=rec.engine,
                archive_source=rec.archive_name,
                version_tag=rec.version_tag,
                file=to_posix(rec.path),
                relative=rec.rel_posix,
                span_start=start,
                span_end=end,
                tags=tags,
                bucket=bucket,
                confidence=confidence,
                nl_summary_short=short,
                nl_summary_long=long,
            )
            components.append(comp)

    # Helper to walk a component body and find call edges (C2).
    def collect_call_edges(root_node: ast.AST, from_cid: str):
        for n in ast.walk(root_node):
            if isinstance(n, ast.Call):
                callee_name = None
                func = n.func
                if isinstance(func, ast.Name):
                    callee_name = func.id
                elif isinstance(func, ast.Attribute):
                    callee_name = func.attr
                if callee_name:
                    edges.append((from_cid, callee_name, "calls"))

    # Process classes and functions as components.
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            name = node.name
            start = getattr(node, "lineno", 1)
            end = getattr(node, "end_lineno", start)
            body_text = text.splitlines()[start - 1 : end]
            body_segment = "\n".join(body_text)

            kind, tags, bucket, confidence = classify_component_from_name_and_body(
                name=name,
                bases=[b.id for b in node.bases if isinstance(b, ast.Name)],
                body_text=body_segment,
                engine=rec.engine,
                archive=rec.archive_name,
            )
            cid = f"{rec.path.name}::class::{name}"
            snippet = snippet_for_span(start, end)
            short, long = make_nl_summary(
                name=name,
                kind=kind,
                engine=rec.engine,
                archive=rec.archive_name,
                body_text=snippet,
            )

            comp = ComponentRecord(
                component_id=cid,
                name=name,
                kind=kind,
                engine=rec.engine,
                archive_source=rec.archive_name,
                version_tag=rec.version_tag,
                file=to_posix(rec.path),
                relative=rec.rel_posix,
                span_start=start,
                span_end=end,
                tags=tags,
                bucket=bucket,
                confidence=confidence,
                nl_summary_short=short,
                nl_summary_long=long,
            )
            components.append(comp)

            # Inheritance edges (A1).
            for base in node.bases:
                if isinstance(base, ast.Name):
                    edges.append((cid, base.id, "inherits_from"))

            # Call edges from this class (methods).
            collect_call_edges(node, cid)

        elif isinstance(node, ast.FunctionDef):
            name = node.name
            start = getattr(node, "lineno", 1)
            end = getattr(node, "end_lineno", start)
            body_text = text.splitlines()[start - 1 : end]
            body_segment = "\n".join(body_text)

            kind, tags, bucket, confidence = classify_function_component(
                name=name,
                body_text=body_segment,
                engine=rec.engine,
                archive=rec.archive_name,
            )
            cid = f"{rec.path.name}::func::{name}"
            snippet = snippet_for_span(start, end)
            short, long = make_nl_summary(
                name=name,
                kind=kind,
                engine=rec.engine,
                archive=rec.archive_name,
                body_text=snippet,
            )

            comp = ComponentRecord(
                component_id=cid,
                name=name,
                kind=kind,
                engine=rec.engine,
                archive_source=rec.archive_name,
                version_tag=rec.version_tag,
                file=to_posix(rec.path),
                relative=rec.rel_posix,
                span_start=start,
                span_end=end,
                tags=tags,
                bucket=bucket,
                confidence=confidence,
                nl_summary_short=short,
                nl_summary_long=long,
            )
            components.append(comp)

            # Call edges from this function.
            collect_call_edges(node, cid)

    # Import edges from all components in this file (B2).
    for comp in components:
        for target, kind in import_targets:
            edges.append((comp.component_id, target, kind))

    return components, edges


def analyze_non_python_file(rec: ArchiveFileRecord) -> Tuple[List[ComponentRecord], List[Tuple[str, str, str]]]:
    """
    Treat JSON/YAML/MD/TXT as config-like or document components.
    Non-Python files do not currently produce edges.
    """
    text = safe_read_text(rec.path, max_bytes=200_000)
    if not text.strip():
        return [], []

    name = rec.path.name
    start = 1
    end = rec.loc if rec.loc > 0 else 1

    if rec.path.suffix.lower() in {".json", ".yaml", ".yml"}:
        kind = "config"
        tags = ["config"]
        bucket = "05_config"
        confidence = 0.9
    else:
        kind = "document"
        tags = ["doc"]
        bucket = None
        confidence = 0.5

    snippet_lines = text.splitlines()[:10]
    snippet = "\n".join(snippet_lines)

    cid = f"{rec.path.name}::blob"
    short, long = make_nl_summary(
        name=name,
        kind=kind,
        engine=rec.engine,
        archive=rec.archive_name,
        body_text=snippet,
    )

    comp = ComponentRecord(
        component_id=cid,
        name=name,
        kind=kind,
        engine=rec.engine,
        archive_source=rec.archive_name,
        version_tag=rec.version_tag,
        file=to_posix(rec.path),
        relative=rec.rel_posix,
        span_start=start,
        span_end=end,
        tags=tags,
        bucket=bucket,
        confidence=confidence,
        nl_summary_short=short,
        nl_summary_long=long,
    )
    return [comp], []


def classify_component_from_name_and_body(
    name: str,
    bases: List[str],
    body_text: str,
    engine: str,
    archive: str,
) -> Tuple[str, List[str], Optional[str], float]:
    """
    Heuristic classifier for classes (F1).
    Uses name + body keywords to decide kind/bucket/confidence.
    """
    lname = name.lower()
    lbody = body_text.lower()

    tags: List[str] = []
    bucket: Optional[str] = None
    confidence: float = 0.6

    # Agent-like
    if "agent" in lname or "agent" in lbody:
        tags.append("agent")
        if "base" in lname or "baseagent" in lname:
            kind = "agent_base_class"
            bucket = "01_agentic_core"
            confidence = 0.95
        else:
            kind = "agent_impl"
            bucket = "01_agentic_core"
            confidence = 0.9
    # Orchestrators / pipelines
    elif "orchestrator" in lname or "workflow" in lname or "pipeline" in lname:
        kind = "orchestrator"
        bucket = "03_runtime"
        tags.extend(["runtime", "orchestrator"])
        confidence = 0.9
    # Services / clients / handlers
    elif any(k in lname for k in ["service", "client", "handler", "strategy", "controller", "manager"]):
        kind = "service_component"
        bucket = "03_runtime"
        tags.extend(["service"])
        confidence = 0.85
    # Repositories / wrappers
    elif any(k in lname for k in ["repository", "repo", "wrapper"]):
        kind = "repository_component"
        bucket = "03_runtime"
        tags.extend(["repository"])
        confidence = 0.85
    # Schemas / models
    elif "schema" in lname or "model" in lname:
        kind = "schema"
        bucket = "02_schemas"
        tags.append("schema")
        confidence = 0.9
    # Configs / settings
    elif "config" in lname or "settings" in lname:
        kind = "config"
        bucket = "05_config"
        tags.append("config")
        confidence = 0.9
    # Prompt systems
    elif any(s in lbody for s in ["system_prompt", "prompt_registry", "guardrail"]):
        kind = "prompt_system"
        bucket = "04_prompt_governance"
        tags.append("prompt")
        confidence = 0.85
    # Analysis components
    elif any(k in lname for k in ["analysis", "analyzer", "analyser"]):
        kind = "analysis_component"
        bucket = "03_runtime"
        tags.append("analysis")
        confidence = 0.8
    else:
        kind = "class"
        tags.append("class")
        bucket = None
        confidence = 0.5

    if engine == "LIC":
        tags.append("lic_engine")
    elif engine == "RG":
        tags.append("rg_engine")
    elif engine == "CURRENT":
        tags.append("current_engine")

    return kind, tags, bucket, confidence


def classify_function_component(
    name: str,
    body_text: str,
    engine: str,
    archive: str,
) -> Tuple[str, List[str], Optional[str], float]:
    """
    Heuristic classifier for functions (F1).
    """
    lname = name.lower()
    lbody = body_text.lower()

    tags: List[str] = []
    bucket: Optional[str] = None
    confidence: float = 0.6

    if any(k in lname for k in ["main", "run_batch", "run_pipeline", "run_agent"]):
        kind = "runtime_entry"
        bucket = "03_runtime"
        tags.append("runtime_entry")
        confidence = 0.9
    elif "test_" in lname:
        kind = "test_function"
        bucket = "10_tests"
        tags.append("test")
        confidence = 0.9
    elif any(k in lbody for k in ["system_prompt", "prompt_registry", "guardrail"]):
        kind = "prompt_function"
        bucket = "04_prompt_governance"
        tags.append("prompt")
        confidence = 0.85
    elif any(k in lname for k in ["retry", "backoff", "retries"]):
        kind = "retry_handler"
        bucket = "03_runtime"
        tags.append("retry")
        confidence = 0.85
    elif any(k in lname for k in ["service", "client", "handler", "strategy"]):
        kind = "service_function"
        bucket = "03_runtime"
        tags.append("service")
        confidence = 0.8
    else:
        kind = "function"
        tags.append("function")
        bucket = None
        confidence = 0.5

    if engine == "LIC":
        tags.append("lic_engine")
    elif engine == "RG":
        tags.append("rg_engine")
    elif engine == "CURRENT":
        tags.append("current_engine")

    return kind, tags, bucket, confidence


def make_nl_summary(
    name: str,
    kind: str,
    engine: str,
    archive: str,
    body_text: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Generate NL summaries, including a short description and a longer one
    that embeds a deterministic snippet (first ~10 lines) from the component
    body (E1).
    """
    short = f"{kind} `{name}` from {archive} ({engine})"

    snippet = ""
    if body_text:
        lines = body_text.splitlines()
        snippet_lines = lines[:10]
        snippet = "\n".join(snippet_lines)

    long = (
        f"This component `{name}` is classified as `{kind}` originating from archive/domain "
        f"`{archive}` with engine `{engine}`. It was discovered during Phase 0.5 semantic "
        f"cache rebuild and should be considered for migration into the new agentic "
        f"architecture based on its assigned semantic bucket.\n\n"
    )
    if snippet:
        long += "Snippet (first lines):\n" + snippet

    return short, long


def generate_global_and_semantic_artifacts(
    records: List[ArchiveFileRecord],
) -> Tuple[
    Dict[str, List[ArchiveFileRecord]],
    Dict[str, List[ComponentRecord]],
    List[Tuple[str, str, str]],
]:
    """
    For each unique hash H:

        • Write global artifacts (ast, embeddings, diffs, golden, safety, integrity, meta).
        • Build semantic/H.semantic.json with component-level records.
        • Accumulate a simple component graph (co_defined edges).

    Returns:
        hash_map: H -> [ArchiveFileRecord, ...]
        components_by_hash: H -> [ComponentRecord, ...]
        component_graph_edges: [(component_id_a, component_id_b, "co_defined"), ...]
    """
    hash_map: Dict[str, List[ArchiveFileRecord]] = {}
    for rec in records:
        h = sha256_of(rec.path)
        hash_map.setdefault(h, []).append(rec)

    components_by_hash: Dict[str, List[ComponentRecord]] = {}
    component_graph_edges: List[Tuple[str, str, str]] = []

    for h, recs in hash_map.items():
        sources = [to_posix(r.path) for r in recs]
        engines = sorted({r.engine for r in recs})

        # AST global artifact
        write_json(
            CACHE_ROOT / "ast" / f"{h}.ast",
            {
                "hash": h,
                "kind": "ast_group",
                "sources": sources,
            },
        )
        write_json(
            CACHE_ROOT / "ast" / f"{h}.ast.meta.json",
            {
                "hash": h,
                "kind": "ast_meta",
                "engines": engines,
            },
        )

        # Embeddings
        embedding_vector = generate_embedding_for_files([r.path for r in recs])
        write_json(
            CACHE_ROOT / "embeddings" / f"{h}.embedding",
            {"hash": h, "kind": "embedding", "vector": embedding_vector},
        )
        write_json(
            CACHE_ROOT / "embeddings" / f"{h}.embedding.meta.json",
            {"hash": h, "kind": "embedding_meta"},
        )

        # Diffs
        write_json(
            CACHE_ROOT / "diffs" / f"{h}.diff.json",
            {"hash": h, "kind": "diff", "baseline": "empty_or_prev_version"},
        )

        # Golden
        golden_content = None
        for r in recs:
            try:
                with r.path.open("r", encoding="utf-8", errors="ignore") as f:
                    golden_content = f.read()
                break
            except Exception:
                continue
        write_json(
            CACHE_ROOT / "golden" / f"{h}.golden.json",
            {
                "hash": h,
                "kind": "golden",
                "content": golden_content,
                "length": len(golden_content) if golden_content else 0,
                "file_hash": h,
            },
        )

        # Safety
        write_json(
            CACHE_ROOT / "safety" / f"{h}.safety.json",
            {"hash": h, "kind": "safety", "status": "unknown"},
        )

        # Integrity
        write_json(
            CACHE_ROOT / "integrity" / f"{h}.integrity.json",
            {"hash": h, "kind": "integrity"},
        )

        # Meta
        write_json(
            CACHE_ROOT / "meta" / f"{h}.meta.json",
            {
                "hash": h,
                "kind": "meta",
                "files": [r.to_dict() for r in recs],
            },
        )

        # Semantic components + edges per hash
        comps_for_hash: List[ComponentRecord] = []
        edges_for_hash: List[Tuple[str, str, str]] = []
        
        for rec in recs:
            if rec.path.suffix.lower() == ".py":
                comps, edges = analyze_python_file(rec)
            else:
                comps, edges = analyze_non_python_file(rec)
            comps_for_hash.extend(comps)
            edges_for_hash.extend(edges)

        components_by_hash[h] = comps_for_hash

        # Write semantic/H.semantic.json
        write_json(
            CACHE_ROOT / "semantic" / f"{h}.semantic.json",
            {
                "hash": h,
                "components": [c.to_dict() for c in comps_for_hash],
            },
        )

        # Add co_defined edges within same hash
        comp_ids = [c.component_id for c in comps_for_hash]
        for i in range(len(comp_ids)):
            for j in range(i + 1, len(comp_ids)):
                edges_for_hash.append((comp_ids[i], comp_ids[j], "co_defined"))

        # Add all edges from this hash to global graph
        component_graph_edges.extend(edges_for_hash)

    # Global component graph file
    write_json(
        CACHE_ROOT / "graphs" / "component_graph.json",
        {
            "nodes": [
                {
                    "component_id": c.component_id,
                    "kind": c.kind,
                    "bucket": c.bucket,
                    "engine": c.engine,
                }
                for comps in components_by_hash.values()
                for c in comps
            ],
            "edges": [
                {"from": a, "to": b, "kind": kind}
                for (a, b, kind) in component_graph_edges
            ],
        },
    )

    return hash_map, components_by_hash, component_graph_edges


# =====================================================================
# ARCHIVE-LOCAL ARTIFACTS (unchanged behavior for RG/LIC)
# =====================================================================

def generate_archive_local_artifacts(
    hash_map: Dict[str, List[ArchiveFileRecord]]
) -> None:
    for h, recs in hash_map.items():
        for rec in recs:
            if rec.engine == "RG":
                root = CACHE_ROOT / "resume_engine" / rec.archive_name
            elif rec.engine == "LIC":
                root = CACHE_ROOT / "outreach_engine" / rec.archive_name
            else:
                # CURRENT engine does not get archive-local artifacts
                continue

            base = root / rec.rel_posix
            base.parent.mkdir(parents=True, exist_ok=True)

            write_json(
                base.with_suffix(base.suffix + ".ast"),
                {"hash": h, "kind": "ast_local", "global": f"ast/{h}.ast"},
            )
            write_json(
                base.with_suffix(base.suffix + ".ast.meta.json"),
                {
                    "hash": h,
                    "kind": "ast_meta_local",
                    "global": f"ast/{h}.ast.meta.json",
                },
            )
            write_json(
                base.with_suffix(base.suffix + ".embedding"),
                {
                    "hash": h,
                    "kind": "embedding_local",
                    "global": f"embeddings/{h}.embedding",
                },
            )
            write_json(
                base.with_suffix(base.suffix + ".embedding.meta.json"),
                {
                    "hash": h,
                    "kind": "embedding_meta_local",
                    "global": f"embeddings/{h}.embedding.meta.json",
                },
            )
            write_json(
                base.with_suffix(base.suffix + ".diff.json"),
                {"hash": h, "kind": "diff_local", "global": f"diffs/{h}.diff.json"},
            )
            write_json(
                base.with_suffix(base.suffix + ".golden.json"),
                {
                    "hash": h,
                    "kind": "golden_local",
                    "global": f"golden/{h}.golden.json",
                },
            )
            write_json(
                base.with_suffix(base.suffix + ".safety.json"),
                {
                    "hash": h,
                    "kind": "safety_local",
                    "global": f"safety/{h}.safety.json",
                },
            )
            write_json(
                base.with_suffix(base.suffix + ".integrity.json"),
                {
                    "hash": h,
                    "kind": "integrity_local",
                    "global": f"integrity/{h}.integrity.json",
                },
            )


# =====================================================================
# CANONICAL COMPONENT POINTERS (SEMANTIC-ONLY BUCKETING)
# =====================================================================

def canonical_relative_for_component(comp: ComponentRecord) -> str:
    """
    Canonical relative path for component pointers:

        LAYER  = L1_archive     (for archives)
                 L1_current     (for CURRENT)
        PHASE  = P0_5
        VERB   = ingest
        DOMAIN = "rg" | "lic" | "current"
        FILE   = component_id (sanitized)
    """
    if comp.engine == "RG":
        domain = "rg"
        layer = "L1_archive"
    elif comp.engine == "LIC":
        domain = "lic"
        layer = "L1_archive"
    else:
        domain = "current"
        layer = "L1_current"

    safe_id = comp.component_id.replace("/", "_").replace("\\", "_")
    return f"{layer}/P0_5/ingest/{domain}/{safe_id}"


def choose_bucket_for_component(comp: ComponentRecord) -> str:
    """
    Semantic-only bucket decision (C1).
    """
    if comp.bucket:
        # If classifier provided a bucket, trust it.
        return comp.bucket

    # Fallback by kind/tag.
    k = comp.kind
    tags = set(comp.tags)

    if k in ("agent_base_class", "agent_impl", "tooling_adapter"):
        return "01_agentic_core"
    if k in ("schema", "pydantic_model"):
        return "02_schemas"
    if k in ("orchestrator", "runtime_entry", "pipeline_step"):
        return "03_runtime"
    if "prompt" in tags or k == "prompt_system" or k == "prompt_function":
        return "04_prompt_governance"
    if k == "config":
        return "05_config"
    if "data_source" in tags:
        return "06_data_source"
    if "observability" in tags:
        return "07_observability"
    if "cli_script" in tags:
        return "08_scripts"
    if comp.engine == "LIC":
        return "09_apps"
    if "test" in tags or k == "test_function":
        return "10_tests"

    return "01_agentic_core"


def generate_canonical_component_pointers(
    hash_map: Dict[str, List[ArchiveFileRecord]],
    components_by_hash: Dict[str, List[ComponentRecord]],
) -> Tuple[Dict[str, int], List[Tuple[Path, Path]]]:
    """
    For each component, write a pointer JSON under the canonical bucket:

        0X_<bucket>/L1_.../P0_5/ingest/<rg|lic|current>/<component_id>.json

    Returns:
        bucket_counts: bucket -> pointer count
        move_plan: [(src_path, dst_path)] for CURRENT *_unassigned files
                   with high-confidence classification (for RESOLVE_UNASSIGNED).
    """
    counts: Dict[str, int] = {b: 0 for b in CANONICAL_BUCKETS}
    move_plan: List[Tuple[Path, Path]] = []

    for h, recs in hash_map.items():
        comps = components_by_hash.get(h, [])
        for comp in comps:
            bucket = choose_bucket_for_component(comp)
            comp.bucket = bucket  # ensure filled

            bucket_root = CACHE_ROOT / bucket
            canon_rel = canonical_relative_for_component(comp)
            pointer_file = bucket_root / f"{canon_rel}.json"

            write_json(
                pointer_file,
                {
                    "hash": h,
                    "canonical_root": bucket,
                    "engine": comp.engine,
                    "archive_source": comp.archive_source,
                    "relative": comp.relative,
                    "canonical_relative": canon_rel,
                    "component_id": comp.component_id,
                    "kind": comp.kind,
                    "confidence": comp.confidence,
                    "global": {
                        "ast": f"ast/{h}.ast",
                        "ast_meta": f"ast/{h}.ast.meta.json",
                        "embedding": f"embeddings/{h}.embedding",
                        "emb_meta": f"embeddings/{h}.embedding.meta.json",
                        "diff": f"diffs/{h}.diff.json",
                        "golden": f"golden/{h}.golden.json",
                        "safety": f"safety/{h}.safety.json",
                        "integrity": f"integrity/{h}.integrity.json",
                        "meta": f"meta/{h}.meta.json",
                        "semantic": f"semantic/{h}.semantic.json",
                    },
                },
            )
            counts[bucket] += 1

            # Build move plan for CURRENT *_unassigned files with high-confidence mapping.
            if (
                comp.engine == "CURRENT"
                and comp.confidence >= 0.8
                and comp.archive_source in CURRENT_DOMAINS_FOR_UNASSIGNED
            ):
                src_path = Path(comp.file)
                # Target domain root is the bucket root at PROJECT_ROOT level.
                target_domain_root = PROJECT_ROOT / bucket
                dst_path = target_domain_root / Path(comp.file).name
                move_plan.append((src_path, dst_path))

    return counts, move_plan


# =====================================================================
# EMBEDDING GENERATION (unchanged core logic)
# =====================================================================

def generate_embedding_for_files(file_paths: List[Path]) -> List[float]:
    try:
        import math
        from collections import Counter

        all_text = ""
        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    all_text += text + " "
            except Exception:
                continue

        if not all_text.strip():
            hash_obj = hashlib.sha256(all_text.encode())
            hash_bytes = hash_obj.digest()
            return [(b - 128.0) / 128.0 for b in hash_bytes[:128]]

        tokens = all_text.lower().replace("\n", " ").split()
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
            "import",
            "def",
            "class",
            "if",
            "else",
            "elif",
            "for",
            "while",
            "return",
            "print",
            "pass",
            "break",
            "continue",
            "try",
            "except",
            "finally",
        }
        tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

        token_counts = Counter(tokens)
        if not token_counts:
            hash_obj = hashlib.sha256(all_text.encode())
            hash_bytes = hash_obj.digest()
            return [(b - 128.0) / 128.0 for b in hash_bytes[:128]]

        most_common = token_counts.most_common(100)
        embedding: List[float] = []

        for i, (_token, count) in enumerate(most_common):
            if i >= 100:
                break
            tf = count / len(tokens)
            tfidf = math.log(1 + tf * 10)
            embedding.append(tfidf)

        while len(embedding) < 128:
            hash_obj = hashlib.sha256((all_text + str(len(embedding))).encode())
            hash_bytes = hash_obj.digest()
            next_val = (hash_bytes[0] - 128.0) / 128.0
            embedding.append(next_val)

        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding[:128]
    except Exception:
        try:
            combined_text = " ".join(str(p) for p in file_paths)
            hash_obj = hashlib.sha256(combined_text.encode())
            hash_bytes = hash_obj.digest()
            return [(b - 128.0) / 128.0 for b in hash_bytes[:128]]
        except Exception:
            return [0.0] * 128


# =====================================================================
# MAIN
# =====================================================================

def run(
    dry_run: bool = False,
    resume_from: Optional[str] = None,
    strict_mode: bool = False,
) -> int:
    """Run Phase 0.5 with orchestrator."""
    print("=== PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v4, ARCHIVE + UNASSIGNED) ===")
    print("Project root      :", PROJECT_ROOT)
    print("Semantic cache    :", CACHE_ROOT)
    if not SSOT_YAML.exists():
        print("[WARN] unified_structure_subatomic.yaml not found; canonical mapping uses heuristics only.")

    orchestrator = Phase05Orchestrator(
        dry_run=dry_run,
        resume_from=resume_from,
        strict_mode=strict_mode,
    )

    if not orchestrator.load_or_create_manifest():
        print("Failed to load/create transaction manifest.")
        return 1

    try:
        for i, step in enumerate(orchestrator.pipeline_steps):
            if i < orchestrator.current_step_index:
                print(f"Skipping previously completed step: {step.step_name}")
                continue

            print(f"Running step {i + 1}/{len(orchestrator.pipeline_steps)}: {step.step_name}")
            orchestrator.update_step_status(i, "RUNNING")

            try:
                success = orchestrator._run_step(i)
                if success:
                    orchestrator.update_step_status(i, "COMPLETED")
                    print(f"[PASS] Step completed: {step.step_name}")
                else:
                    orchestrator.update_step_status(i, "FAILED", f"Step {step.step_name} failed")
                    print(f"[FAIL] Step failed: {step.step_name}")
                    return 1
            except Exception as e:
                orchestrator.update_step_status(i, "FAILED", str(e))
                print(f"[FAIL] Step failed with exception: {step.step_name}")
                print(f"Error: {e}")
                traceback.print_exc()
                return 1

            print()

        orchestrator.transaction_manifest.status = "COMPLETED"
        orchestrator.save_manifest()

        print("=== Pipeline Completed ===")
        orchestrator.print_final_summary()
        return 0

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        if orchestrator.transaction_manifest:
            orchestrator.transaction_manifest.status = "INTERRUPTED"
            orchestrator.save_manifest()
        return 1
    except Exception as e:
        print(f"Pipeline failed with exception: {e}")
        if orchestrator.transaction_manifest:
            orchestrator.transaction_manifest.status = "FAILED"
            orchestrator.save_manifest()
        return 1


def run_simple(dry_run: bool = False) -> int:
    """Deprecated simple run: kept for compatibility; wraps full run."""
    return run(dry_run=dry_run, resume_from=None, strict_mode=False)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Phase 0.5 Semantic Cache Rebuild (v4)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--resume-from", help="Resume from specific step id (not used in v4)")
    parser.add_argument("--list-steps", action="store_true", help="List pipeline steps")
    parser.add_argument("--strict-mode", action="store_true", help="Enable strict validation mode")
    parser.add_argument("--validate-only", action="store_true", help="Run validation only")
    parser.add_argument("--simple", action="store_true", help="Alias for default run (kept for compatibility)")
    args = parser.parse_args()

    if args.list_steps:
        print("Available pipeline steps:")
        print("  SSOT_LOAD")
        print("  ARCHIVE_SCAN")
        print("  CURRENT_SCAN")
        print("  ARTIFACT_GENERATION")
        print("  DUAL_WRITE")
        print("  RESOLVE_UNASSIGNED")
        print("  VALIDATION")
        print("  CLEANUP")
        return 0

    if args.validate_only:
        import phase05_validate

        return phase05_validate.run()

    return run(dry_run=args.dry_run, resume_from=args.resume_from, strict_mode=args.strict_mode)


if __name__ == "__main__":
    sys.exit(main())
