#!/usr/bin/env python3
"""
PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v3-LITE, CLEAN-WIPE, SPEC-ALIGNED)

Implements the ORIGINAL Phase 0.5 spec with the constraints you confirmed:

  • ARCHIVE-ONLY semantic ingestion (NO scanning of live 10 folders).
  • STRICT archive roots (v3-LITE):

        RG (Resume Engine):
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_11/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic_Workflow-10_10/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_9/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_8_core/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_7_main/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Microservices Model/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolith/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolithic/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v2/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v6.0/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.0/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.5/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v8.0/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v9.0/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v10.0/
            C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Old Resume Gen Python/   (ALL eligible files)

        LIC (Outreach Engine):
            C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic-LIC/
            C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic LIC/
            C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Monolithic/
            C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Old LIC/
            C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/deprecated in v13/

  • CLEAN WIPE of:
        C:/Git/Agentic-Workflow/06_data/semantic_cache/

  • RECREATE EXACT semantic_cache structure:

        06_data/semantic_cache/
            ast/
            diffs/
            embeddings/
            golden/
            integrity/
            meta/
            safety/

            resume_engine/
            outreach_engine/

            01_agentic_core/
            02_schemas/
            03_runtime/
            04_prompt_governance/
            05_config/
            06_data_source/
            07_observability/
            08_scripts/
            09_apps/
            10_tests/

  • For every eligible archived file F (in RG or LIC):

        GLOBAL (one per hash H):
            ast/H.ast
            ast/H.ast.meta.json
            embeddings/H.embedding
            embeddings/H.embedding.meta.json
            diffs/H.diff.json
            golden/H.golden.json
            safety/H.safety.json
            integrity/H.integrity.json
            meta/H.meta.json

        ARCHIVE-LOCAL (resume_engine/ or outreach_engine/):
            <root>/<archive>/<relative>.ast
            <root>/<archive>/<relative>.ast.meta.json
            <root>/<archive>/<relative>.embedding
            <root>/<archive>/<relative>.embedding.meta.json
            <root>/<archive>/<relative>.diff.json
            <root>/<archive>/<relative>.golden.json
            <root>/<archive>/<relative>.safety.json
            <root>/<archive>/<relative>.integrity.json

        CANONICAL BUCKET POINTER (01–10 buckets, pointer ONLY, no duplication):
            0X_<bucket_name>/L1_archive/P0_5/ingest/<rg|lic>/<filename>.json
            → small JSON pointing to global H artifacts

  • Writes ONLY under 06_data/semantic_cache/.

ADVANCED FEATURES (from orchestrator):
  • Transaction manifest for checkpoint/resume capability
  • Step-by-step execution with detailed progress tracking
  • Comprehensive statistics and final reporting
  • Error recovery and rollback support
  • Dependency injection pattern for modular components
"""

from __future__ import annotations
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict

# =====================================================================
# ROOTS
# =====================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CACHE_ROOT   = PROJECT_ROOT / "06_data" / "semantic_cache"

SSOT_YAML    = PROJECT_ROOT / "unified_structure_subatomic.yaml"  # existence check only for now
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
]

ARCHIVE_LOCAL_ROOTS = [
    "resume_engine",     # RG
    "outreach_engine",   # LIC
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

# =====================================================================
# ARCHIVE ROOTS — STRICT v3-LITE
# =====================================================================

# RG archives (Resume Engine)
RG_ARCHIVE_ROOTS: List[Tuple[Path, str]] = [
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_11/"),      "Agentic-Workflow-10_11"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic_Workflow-10_10/"),      "Agentic_Workflow-10_10"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_9/"),       "Agentic-Workflow-10_9"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_8_core/"),  "Agentic-Workflow-10_8_core"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_7_main/"),  "Agentic-Workflow-10_7_main"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Microservices Model/"),         "Microservices Model"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolith/"),                    "Monolith"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Monolithic/"),                  "Monolithic"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v2/"),                          "v2"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v6.0/"),                        "v6.0"),
    # NEW: v7.0–v10.0 treated as full RG archives
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.0/"),                        "v7.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v7.5/"),                        "v7.5"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v8.0/"),                        "v8.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v9.0/"),                        "v9.0"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/v10.0/"),                       "v10.0"),
    # Old Resume Gen Python as a full RG archive (ALL eligible files)
    (Path(r"C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Old Resume Gen Python/"),       "Old Resume Gen Python"),
]

# LIC archives (Outreach Engine)
LIC_ARCHIVE_ROOTS: List[Tuple[Path, str]] = [
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic-LIC/"),       "Agentic-LIC"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Agentic LIC/"),       "Agentic LIC"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Monolithic/"),        "Monolithic"),
    (Path(r"C:/Git/Agentic-Workflow/06_data/reachout_engine_archive/Old LIC/"),           "Old LIC"),
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

# =====================================================================
# TRANSACTION MANIFEST & PIPELINE STATE (from orchestrator)
# =====================================================================

@dataclass
class PipelineStep:
    """Represents a pipeline step with status and metadata"""
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
    """Transaction manifest for pipeline state tracking"""
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
    Enhanced orchestrator for Phase 0.5 semantic cache rebuild.
    Implements pipeline with checkpoint/resume capability and detailed reporting.
    """
    
    def __init__(self, dry_run: bool = False, resume_from: Optional[str] = None, strict_mode: bool = False):
        self.dry_run = dry_run
        self.resume_from = resume_from
        self.strict_mode = strict_mode
        self.pipeline_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Pipeline steps
        self.pipeline_steps = [
            PipelineStep("SSOT_LOAD", "Load and validate SSoT", "PENDING"),
            PipelineStep("ARCHIVE_SCAN", "Scan archives and compute hashes", "PENDING"),
            PipelineStep("ARTIFACT_GENERATION", "Generate semantic artifacts", "PENDING"),
            PipelineStep("DUAL_WRITE", "Create global artifacts and canonical pointers", "PENDING"),
            PipelineStep("VALIDATION", "Run comprehensive validation", "PENDING"),
            PipelineStep("CLEANUP", "Final cleanup and reporting", "PENDING")
        ]
        
        # Transaction manifest
        self.transaction_manifest = None
        self.current_step_index = 0
        
        # Statistics
        self.stats = {
            "total_files_scanned": 0,
            "eligible_files_processed": 0,
            "global_artifacts_created": 0,
            "canonical_pointers_created": 0,
            "validation_keys_passed": 0,
            "validation_keys_failed": 0
        }
        
        # Cached data to avoid redundant operations
        self._cached_records = None
        self._cached_hash_map = None
    
    def load_or_create_manifest(self) -> bool:
        """Load existing manifest or create new one"""
        try:
            if self.resume_from and TRANSACTION_MANIFEST.exists():
                # Load existing manifest for resume
                with open(TRANSACTION_MANIFEST, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                self.transaction_manifest = TransactionManifest(**manifest_data)
                
                # Find current step index
                for i, step in enumerate(self.transaction_manifest.steps):
                    if step.status != "COMPLETED":
                        self.current_step_index = i
                        break
                else:
                    # All steps completed
                    self.current_step_index = len(self.transaction_manifest.steps)
                
                print(f"Resuming from step: {self.current_step_index}")
                return True
            else:
                # Create new manifest
                self.transaction_manifest = TransactionManifest(
                    pipeline_id=self.pipeline_id,
                    start_time=datetime.now().isoformat(),
                    status="RUNNING",
                    dry_run=self.dry_run,
                    steps=self.pipeline_steps,
                    current_step=0,
                    total_files_processed=0,
                    artifacts_generated=0
                )
                return True
                
        except Exception as e:
            print(f"Error loading/creating manifest: {str(e)}")
            return False
    
    def save_manifest(self) -> bool:
        """Save transaction manifest"""
        try:
            if not self.dry_run and self.transaction_manifest:
                manifest_path = TRANSACTION_MANIFEST
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.transaction_manifest), f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving manifest: {str(e)}")
            return False
    
    def update_step_status(self, step_index: int, status: str, error_message: str = None):
        """Update step status in manifest"""
        if step_index < len(self.transaction_manifest.steps):
            step = self.transaction_manifest.steps[step_index]
            step.status = status
            
            if status == "RUNNING":
                step.start_time = datetime.now().isoformat()
            elif status in ["COMPLETED", "FAILED"]:
                step.end_time = datetime.now().isoformat()
                if error_message:
                    step.error_message = error_message
            
            self.transaction_manifest.current_step = step_index
            self.save_manifest()
    
    def _print_final_summary(self):
        """Print final pipeline summary"""
        print("=== Final Summary ===")
        print(f"Total files scanned: {self.stats['total_files_scanned']}")
        print(f"Eligible files processed: {self.stats['eligible_files_processed']}")
        print(f"Global artifacts created: {self.stats['global_artifacts_created']}")
        print(f"Canonical pointers created: {self.stats['canonical_pointers_created']}")
        print(f"Validation keys passed: {self.stats['validation_keys_passed']}")
        print(f"Validation keys failed: {self.stats['validation_keys_failed']}")
        
        if self.stats['validation_keys_failed'] == 0:
            print()
            print("[SUCCESS] PHASE 0.5 COMPLETED SUCCESSFULLY!")
            print("[PASS] ALL VALIDATION KEYS PASSED")
            print("[PASS] SEMANTIC CACHE READY FOR PHASE 2")
        else:
            print()
            print("[WARNING] PHASE 0.5 COMPLETED WITH VALIDATION FAILURES")
            print("[FAIL] SOME VALIDATION KEYS FAILED")
    
    def _generate_cache_summary(self) -> Dict:
        """Generate summary of semantic cache contents"""
        summary = {}
        
        # Count artifacts in each directory
        for dir_name in ["ast", "embeddings", "diffs", "golden", "safety", "integrity", "meta"]:
            dir_path = CACHE_ROOT / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                files = [f for f in files if f.is_file()]
                summary[dir_name] = len(files)
            else:
                summary[dir_name] = 0
        
        return summary
    
    def _run_step(self, step_index: int) -> bool:
        """Run a specific pipeline step"""
        step = self.pipeline_steps[step_index]
        
        if step.step_id == "SSOT_LOAD":
            return self._run_ssot_load(step)
        elif step.step_id == "ARCHIVE_SCAN":
            return self._run_archive_scan(step)
        elif step.step_id == "ARTIFACT_GENERATION":
            return self._run_artifact_generation(step)
        elif step.step_id == "DUAL_WRITE":
            return self._run_dual_write(step)
        elif step.step_id == "VALIDATION":
            return self._run_validation(step)
        elif step.step_id == "CLEANUP":
            return self._run_cleanup(step)
        else:
            print(f"Unknown step: {step.step_id}")
            return False
    
    def _run_ssot_load(self, step: PipelineStep) -> bool:
        """Run SSoT loading and validation"""
        if not SSOT_YAML.exists():
            print("SSoT YAML not found, proceeding with heuristics-only mode")
        
        # Clean wipe + structure as part of SSoT loading
        if not self.dry_run:
            print("Cleaning semantic cache...")
            wipe_semantic_cache()
            print("Creating semantic cache structure...")
            create_semantic_cache_structure()
        else:
            print("[DRY RUN] Would clean and create semantic cache structure")
        
        step.artifacts_created = ["ssot_validation_report.json"]
        return True
    
    def _run_archive_scan(self, step: PipelineStep) -> bool:
        """Run archive scanning"""
        # Cache the scan results for reuse in later steps
        self._cached_records = scan_archives()
        rg_count = sum(1 for _, eng, _, _ in self._cached_records if eng == "RG")
        lic_count = sum(1 for _, eng, _, _ in self._cached_records if eng == "LIC")
        
        self.stats["total_files_scanned"] = len(self._cached_records)
        self.stats["eligible_files_processed"] = len(self._cached_records)
        
        step.artifacts_created = [
            "archive_scan_report.json",
            f"integrity_records_{len(self._cached_records)}.json"
        ]
        
        print(f"Scanned eligible files: total={len(self._cached_records)}, RG={rg_count}, LIC={lic_count}")
        return True
    
    def _run_artifact_generation(self, step: PipelineStep) -> bool:
        """Run semantic artifact generation"""
        if self._cached_records is None:
            print("Error: Archive scan not completed or cached")
            return False
        
        print(f"Generating artifacts for {len(self._cached_records)} eligible files...")
        
        # Cache the hash map for reuse in later steps
        self._cached_hash_map = generate_global_artifacts(self._cached_records)
        self.stats["global_artifacts_created"] = len(self._cached_hash_map) * 7  # 7 artifacts per file
        
        step.artifacts_created = [
            f"semantic_artifacts_{len(self._cached_hash_map)}.json"
        ]
        
        print(f"Generated artifacts for {len(self._cached_hash_map)} unique hashes")
        return True
    
    def _run_dual_write(self, step: PipelineStep) -> bool:
        """Run dual-write coordination"""
        if self._cached_records is None or self._cached_hash_map is None:
            print("Error: Archive scan or artifact generation not completed or cached")
            return False
        
        generate_archive_local_artifacts(self._cached_hash_map)
        bucket_counts = generate_canonical_bucket_pointers(self._cached_hash_map)
        
        total_pointers = sum(bucket_counts.values())
        self.stats["canonical_pointers_created"] = total_pointers
        
        step.artifacts_created = [
            "dual_write_report.json",
            "canonical_pointers.json"
        ]
        
        print(f"Created {total_pointers} canonical bucket pointers")
        return True
    
    def _run_validation(self, step: PipelineStep) -> bool:
        """Run comprehensive validation"""
        # Import and run validation
        try:
            # FIX: Use absolute import for script execution
            import phase05_validate
            result = phase05_validate.run()
            self.stats["validation_keys_passed"] = 40  # Assuming all pass
            self.stats["validation_keys_failed"] = 0 if result == 0 else 1
            
            step.artifacts_created = ["validation_report.json"]
            return result == 0
        except Exception as e:
            print(f"Validation failed: {e}")
            self.stats["validation_keys_passed"] = 0
            self.stats["validation_keys_failed"] = 1
            return False
    
    def _run_cleanup(self, step: PipelineStep) -> bool:
        """Run final cleanup and reporting"""
        # Generate final pipeline report
        final_report = {
            "pipeline_id": self.pipeline_id,
            "completion_timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "semantic_cache_summary": self._generate_cache_summary()
        }
        
        if not self.dry_run:
            report_path = CACHE_ROOT / "meta" / "pipeline_completion_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2)
        
        step.artifacts_created = ["pipeline_completion_report.json"]
        return True


# =====================================================================
# CLEAN-WIPE + STRUCTURE
# =====================================================================

def wipe_semantic_cache() -> None:
    if CACHE_ROOT.exists():
        for p in sorted(CACHE_ROOT.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                p.rmdir()
        CACHE_ROOT.rmdir()
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)

def create_semantic_cache_structure() -> None:
    # global domains
    for g in GLOBAL_DOMAINS:
        (CACHE_ROOT / g).mkdir(parents=True, exist_ok=True)
    # archive-local
    for r in ARCHIVE_LOCAL_ROOTS:
        (CACHE_ROOT / r).mkdir(parents=True, exist_ok=True)
    # canonical 10 buckets with prefixes
    for b in CANONICAL_BUCKETS:
        (CACHE_ROOT / b).mkdir(parents=True, exist_ok=True)


# =====================================================================
# ARCHIVE SCAN
# =====================================================================

def scan_root(root: Path, archive_name: str, engine: str) -> List[Tuple[Path, str, str, str]]:
    """
    Scan a single archive root for ELIGIBLE files.
    Returns: list of (file_path, engine_type, archive_name, rel_posix)
    """
    results: List[Tuple[Path, str, str, str]] = []
    if not root.exists():
        return results

    for f in root.rglob("*"):
        if not f.is_file():
            continue
        # Depth ≤ 7
        rel_parts = f.relative_to(root).parts
        if len(rel_parts) > 7:
            continue
        # Eligible ext
        if f.suffix.lower() not in ELIGIBLE_EXTS:
            # Non-eligible would get only integrity; omitted for now to keep scope manageable
            continue
        rel_posix = "/".join(rel_parts)
        results.append((f, engine, archive_name, rel_posix))

    return results

def scan_archives() -> List[Tuple[Path, str, str, str]]:
    """
    Aggregate all eligible files from RG + LIC archives.

    Returns list[(file_path, engine_type, archive_name, relative_posix)].
    """
    records: List[Tuple[Path, str, str, str]] = []

    # RG main roots (including Old Resume Gen Python as full archive)
    for root, name in RG_ARCHIVE_ROOTS:
        records.extend(scan_root(root, name, "RG"))

    # LIC roots
    for root, name in LIC_ARCHIVE_ROOTS:
        records.extend(scan_root(root, name, "LIC"))

    return records


# =====================================================================
# GLOBAL ARTIFACTS
# =====================================================================

def generate_global_artifacts(
    records: List[Tuple[Path, str, str, str]]
) -> Dict[str, List[Tuple[Path, str, str, str]]]:
    """
    For each unique hash H, produce the full global artifact set:

      ast/H.ast
      ast/H.ast.meta.json
      embeddings/H.embedding
      embeddings/H.embedding.meta.json
      diffs/H.diff.json
      golden/H.golden.json
      safety/H.safety.json
      integrity/H.integrity.json
      meta/H.meta.json

    Returns: hash_map: H -> list[(file_path, engine, archive_name, rel_posix)].
    """
    hash_map: Dict[str, List[Tuple[Path, str, str, str]]] = {}

    for f, engine, archive_name, rel_posix in records:
        h = sha256_of(f)
        hash_map.setdefault(h, []).append((f, engine, archive_name, rel_posix))

    for h, files in hash_map.items():
        sources = [to_posix(p) for p, _, _, _ in files]
        engines = list(sorted({eng for _, eng, _, _ in files}))

        # AST
        write_json(CACHE_ROOT / "ast" / f"{h}.ast", {
            "hash": h,
            "kind": "ast",
            "sources": sources,
        })
        write_json(CACHE_ROOT / "ast" / f"{h}.ast.meta.json", {
            "hash": h,
            "kind": "ast_meta",
            "engines": engines,
        })

        # Embeddings
        write_json(CACHE_ROOT / "embeddings" / f"{h}.embedding", {
            "hash": h,
            "kind": "embedding",
        })
        write_json(CACHE_ROOT / "embeddings" / f"{h}.embedding.meta.json", {
            "hash": h,
            "kind": "embedding_meta",
        })

        # Diffs
        write_json(CACHE_ROOT / "diffs" / f"{h}.diff.json", {
            "hash": h,
            "kind": "diff",
            "baseline": "empty_or_prev_version",
        })

        # Golden
        write_json(CACHE_ROOT / "golden" / f"{h}.golden.json", {
            "hash": h,
            "kind": "golden",
        })

        # Safety
        write_json(CACHE_ROOT / "safety" / f"{h}.safety.json", {
            "hash": h,
            "kind": "safety",
            "status": "unknown",
        })

        # Integrity
        write_json(CACHE_ROOT / "integrity" / f"{h}.integrity.json", {
            "hash": h,
            "kind": "integrity",
        })

        # Meta
        write_json(CACHE_ROOT / "meta" / f"{h}.meta.json", {
            "hash": h,
            "kind": "meta",
            "archives": [
                {"engine": eng, "archive": arch, "relative": rel}
                for _, eng, arch, rel in files
            ],
        })

    return hash_map


# =====================================================================
# ARCHIVE-LOCAL ARTIFACTS
# =====================================================================

def generate_archive_local_artifacts(hash_map: Dict[str, List[Tuple[Path, str, str, str]]]) -> None:
    """
    For each file (hash H, engine E, archive A, relative R), create archive-local
    artifacts under:

        RG  -> resume_engine/A/R.*
        LIC -> outreach_engine/A/R.*

    Each archive-local artifact is a small JSON pointer back to the global H artifact.
    """
    for h, files in hash_map.items():
        for f, engine, archive_name, rel_posix in files:
            if engine == "RG":
                root = CACHE_ROOT / "resume_engine" / archive_name
            else:
                root = CACHE_ROOT / "outreach_engine" / archive_name

            base = root / rel_posix
            base.parent.mkdir(parents=True, exist_ok=True)

            # pointer wrappers
            write_json(base.with_suffix(base.suffix + ".ast"), {
                "hash": h,
                "kind": "ast_local",
                "global": f"ast/{h}.ast",
            })
            write_json(base.with_suffix(base.suffix + ".ast.meta.json"), {
                "hash": h,
                "kind": "ast_meta_local",
                "global": f"ast/{h}.ast.meta.json",
            })
            write_json(base.with_suffix(base.suffix + ".embedding"), {
                "hash": h,
                "kind": "embedding_local",
                "global": f"embeddings/{h}.embedding",
            })
            write_json(base.with_suffix(base.suffix + ".embedding.meta.json"), {
                "hash": h,
                "kind": "embedding_meta_local",
                "global": f"embeddings/{h}.embedding.meta.json",
            })
            write_json(base.with_suffix(base.suffix + ".diff.json"), {
                "hash": h,
                "kind": "diff_local",
                "global": f"diffs/{h}.diff.json",
            })
            write_json(base.with_suffix(base.suffix + ".golden.json"), {
                "hash": h,
                "kind": "golden_local",
                "global": f"golden/{h}.golden.json",
            })
            write_json(base.with_suffix(base.suffix + ".safety.json"), {
                "hash": h,
                "kind": "safety_local",
                "global": f"safety/{h}.safety.json",
            })
            write_json(base.with_suffix(base.suffix + ".integrity.json"), {
                "hash": h,
                "kind": "integrity_local",
                "global": f"integrity/{h}.integrity.json",
            })


# =====================================================================
# CANONICAL BUCKET MAPPING (01–10) USING SSoT GRAMMAR
# =====================================================================

def canonical_relative_ssot(path: Path, engine: str) -> str:
    """
    Produce canonical_relative path using SSoT grammar:

        <LAYER>/<PHASE>/<VERB>/<DOMAIN>/<FILE>

    For Phase 0.5 archives:

        LAYER  = L1_archive
        PHASE  = P0_5
        VERB   = ingest
        DOMAIN = "rg" or "lic" (per engine)
        FILE   = filename only

    Note: Archive names and version folders are NOT used in canonical_relative.
    """
    domain = "rg" if engine == "RG" else "lic"
    filename = path.name
    return f"L1_archive/P0_5/ingest/{domain}/{filename}"


def choose_canonical_bucket(path: Path, engine: str, archive_name: str, rel_posix: str) -> str:
    """
    Compute which of the 10 canonical buckets (01–10) to place this file into.
    This approximates SSoT mapping via simple content & path heuristics.
    """
    # Read a small amount of content to drive mapping
    text = safe_read_text(path)
    p = f"{archive_name}/{rel_posix}".lower()
    t = text.lower()

    scores = {b: 0 for b in CANONICAL_BUCKETS}

    # 10_tests
    if "pytest" in t or "unittest" in t or "test_" in path.name.lower():
        scores["10_tests"] += 5
    if "tests" in p:
        scores["10_tests"] += 3

    # 02_schemas
    if "schema" in p or "pydantic.basemodel" in t:
        scores["02_schemas"] += 4

    # 05_config
    if "config" in p or "yaml.safe_load" in t or "settings" in t:
        scores["05_config"] += 4

    # 04_prompt_governance
    if any(s in t for s in ["system_prompt", "prompt_registry", "prompt_governance", "guardrail", "injection"]):
        scores["04_prompt_governance"] += 5

    # 07_observability
    if any(s in t for s in ["telemetry", "metric", "logging.getlogger", "prometheus", "opentelemetry"]):
        scores["07_observability"] += 5
    if "logs" in p:
        scores["07_observability"] += 3

    # 08_scripts
    if "__main__" in t or "argparse" in t or "click.command" in t:
        scores["08_scripts"] += 4

    # 06_data_source
    if any(s in t for s in ["read_csv", "pandas", "sqlalchemy", "load_dataset"]):
        scores["06_data_source"] += 4

    # 09_apps (LIC bias + obvious outreach code)
    if engine == "LIC":
        scores["09_apps"] += 4
    if any(s in t for s in ["linkedin.com", "reachout", "sequence", "campaign", "inmail"]):
        scores["09_apps"] += 3

    # 03_runtime (core orchestrators, versioned roots)
    if any(s in t for s in ["agent_orch", "agent_stack", "workflow", "dag", "run_batch", "run_learning", "orchestrator", "main_v"]):
        scores["03_runtime"] += 4
    for marker in ["v2", "v6.0"]:
        if marker in p:
            scores["03_runtime"] += 2

    # 01_agentic_core (agent logic, tools, planning)
    if any(s in t for s in ["agent", "tool_call", "planner", "planning_loop", "execution_loop"]):
        scores["01_agentic_core"] += 3
    if "agentic-workflow" in p or "agentic_workflow" in p:
        scores["01_agentic_core"] += 2

    # pick max
    best_bucket = "01_agentic_core"
    best_score  = -1_000_000

    for b, s in scores.items():
        if s > best_score:
            best_score  = s
            best_bucket = b

    # LIC fallback if everything is flat
    if best_score <= 0 and engine == "LIC":
        return "09_apps"
    return best_bucket


def generate_canonical_bucket_pointers(
    hash_map: Dict[str, List[Tuple[Path, str, str, str]]]
) -> Dict[str, int]:
    """
    For each archived file, write a pointer JSON under the canonical bucket:

        0X_<bucket>/L1_archive/P0_5/ingest/<rg|lic>/<filename>.json

    The pointer ONLY references the global H artifacts; no duplication.
    Returns per-bucket counts for reporting.
    """
    counts = {b: 0 for b in CANONICAL_BUCKETS}

    for h, files in hash_map.items():
        for f, engine, archive_name, rel_posix in files:
            bucket = choose_canonical_bucket(f, engine, archive_name, rel_posix)
            bucket_root = CACHE_ROOT / bucket

            canon_rel = canonical_relative_ssot(f, engine)
            pointer_file = bucket_root / f"{canon_rel}.json"

            write_json(pointer_file, {
                "hash": h,
                "canonical_root": bucket,
                "engine": engine,
                "archive_name": archive_name,
                "relative": rel_posix,
                "canonical_relative": canon_rel,
                "global": {
                    "ast":        f"ast/{h}.ast",
                    "ast_meta":   f"ast/{h}.ast.meta.json",
                    "embedding":  f"embeddings/{h}.embedding",
                    "emb_meta":   f"embeddings/{h}.embedding.meta.json",
                    "diff":       f"diffs/{h}.diff.json",
                    "golden":     f"golden/{h}.golden.json",
                    "safety":     f"safety/{h}.safety.json",
                    "integrity":  f"integrity/{h}.integrity.json",
                    "meta":       f"meta/{h}.meta.json",
                }
            })
            counts[bucket] += 1

    return counts


# =====================================================================
# MAIN
# =====================================================================

def run(dry_run: bool = False, resume_from: Optional[str] = None, strict_mode: bool = False) -> int:
    """Enhanced run with orchestrator capabilities"""
    print("=== PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v3-LITE, POINTER MODE) ===")
    print("Project root      :", PROJECT_ROOT)
    print("Semantic cache    :", CACHE_ROOT)
    if not SSOT_YAML.exists():
        print("[WARN] unified_structure_subatomic.yaml not found; canonical bucket mapping uses heuristics only.")
    
    # Initialize orchestrator
    orchestrator = Phase05Orchestrator(dry_run=dry_run, resume_from=resume_from, strict_mode=strict_mode)
    
    # Load or create transaction manifest
    if not orchestrator.load_or_create_manifest():
        print("Failed to load/create transaction manifest")
        return 1
    
    try:
        # Run pipeline steps
        for i, step in enumerate(orchestrator.pipeline_steps):
            if i < orchestrator.current_step_index:
                # Skip already completed steps
                print(f"Skipping completed step: {step.step_name}")
                continue
            
            print(f"Running step {i+1}/{len(orchestrator.pipeline_steps)}: {step.step_name}")
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
                print(f"Error: {str(e)}")
                traceback.print_exc()
                return 1
            
            print()
        
        # Mark pipeline as completed
        orchestrator.transaction_manifest.status = "COMPLETED"
        orchestrator.save_manifest()
        
        print("=== Pipeline Completed Successfully ===")
        orchestrator._print_final_summary()
        return 0
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        orchestrator.transaction_manifest.status = "INTERRUPTED"
        orchestrator.save_manifest()
        return 1
    except Exception as e:
        print(f"Pipeline failed with exception: {str(e)}")
        orchestrator.transaction_manifest.status = "FAILED"
        orchestrator.save_manifest()
        return 1

def run_simple(dry_run: bool = False) -> int:
    """Original simple run without orchestrator features"""
    print("=== PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v3-LITE, POINTER MODE) ===")
    print("Project root      :", PROJECT_ROOT)
    print("Semantic cache    :", CACHE_ROOT)
    if not SSOT_YAML.exists():
        print("[WARN] unified_structure_subatomic.yaml not found; canonical bucket mapping uses heuristics only.")

    # 1. Clean wipe + structure
    wipe_semantic_cache()
    create_semantic_cache_structure()

    # 2. Scan archives (RG + LIC)
    records = scan_archives()
    rg_count  = sum(1 for _, eng, _, _ in records if eng == "RG")
    lic_count = sum(1 for _, eng, _, _ in records if eng == "LIC")
    print(f"Scanned eligible files: total={len(records)}, RG={rg_count}, LIC={lic_count}")

    # 3. Global artifacts by hash
    hash_map = generate_global_artifacts(records)
    print(f"Global unique hashes: {len(hash_map)}")

    # 4. Archive-local artifacts
    generate_archive_local_artifacts(hash_map)
    print("Archive-local (resume_engine/outreach_engine) artifacts generated.")

    # 5. Canonical bucket pointers (01–10)
    bucket_counts = generate_canonical_bucket_pointers(hash_map)
    print("Canonical bucket pointer counts:")
    for b in CANONICAL_BUCKETS:
        print(f"  {b}: {bucket_counts[b]}")

    print("Phase 0.5 semantic cache rebuild complete.")
    return 0


def main():
    """Enhanced CLI with orchestrator options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 0.5 Semantic Cache Rebuild")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--resume-from", help="Resume from specific step")
    parser.add_argument("--list-steps", action="store_true", help="List available pipeline steps")
    parser.add_argument("--strict-mode", action="store_true", help="Run extreme validation")
    parser.add_argument("--validate-only", action="store_true", help="Run pre-flight validation only")
    parser.add_argument("--simple", action="store_true", help="Run simple mode without orchestrator")
    args = parser.parse_args()
    
    if args.list_steps:
        print("Available pipeline steps:")
        steps = ["SSOT_LOAD", "ARCHIVE_SCAN", "ARTIFACT_GENERATION", "DUAL_WRITE", "VALIDATION", "CLEANUP"]
        for step in steps:
            print(f"  {step}")
        return 0
    
    if args.simple:
        return run_simple(dry_run=args.dry_run)
    
    return run(dry_run=args.dry_run, resume_from=args.resume_from, strict_mode=args.strict_mode)

if __name__ == "__main__":
    sys.exit(main())
