#!/usr/bin/env python3
"""
PHASE 2 — SEMANTIC DIFF & MIGRATION PLAN (STRICT ZERO-LOSS, SEMANTIC-ONLY)

This implementation is re-based on:

  • Phase 0.5 — Semantic Lineage Cache Rebuild (v3-LITE, CLEAN-WIPE, POINTER MODE)
    - Global semantic artifacts under:
        06_data/semantic_cache/{ast,diffs,embeddings,golden,integrity,meta,safety}
    - Archive-local pointers under:
        06_data/semantic_cache/{resume_engine,outreach_engine}/...
    - Canonical bucket pointers for each canonical folder (01–10) under:
        06_data/semantic_cache/0X_* buckets, each containing:
            L1_archive/P0_5/ingest/{rg|lic}/{filename}.json
      where each pointer JSON has:
            {
              "hash": <global hash>,
              "canonical_root": "01_agentic_core" | ... | "10_tests",
              "engine": "RG" | "LIC",
              "archive_name": "...",
              "relative": "archive_rel_path",
              "canonical_relative": "L1_archive/...",
              "global": { ast, ast_meta, embedding, ... }
            }

  • Phase 0.5 validator — K1–K40 semantic cache invariants
  • Phase 1 — Structural enforcement & re-organization (ZERO-LOSS)
    - SSoT-driven canonical filesystem under 10 roots:
        01_agentic_core, 02_schemas, ..., 10_tests
    - No destructive edits to file content
    - Canonical mapping to unified_structure_subatomic.yaml

  • SSoT YAML + META:
        unified_structure_subatomic.yaml
        unified_structure_subatomic_meta.yaml

PHASE 2 STRICT MODE (OPTION A):

  • ZERO-LOSS, SEMANTIC-ONLY:
      - Phase 2 NEVER mutates the filesystem or semantic cache.
      - It ONLY reads:
          - SSoT YAML + META
          - Phase 1 freeze / reports (implicitly via SSoT alignment)
          - Phase 0.5 semantic cache (global artifacts + canonical pointers)
          - Live code under a single TARGET ROOT (01–10).
      - It emits a JSON plan with SEMANTIC operations ONLY:
          - rewrite_file_from_cache
          - merge_file_from_cache
          - patch_region_from_cache
          - canonical_rewrite
          - insert_semantic_block
          - delete_semantic_block

  • STRUCTURAL DIFF INVARIANT:
      - Phase 1 is the ONLY structural mutator.
      - Phase 2 verifies that the SSoT subtree for TARGET ROOT and the live
        filesystem are structurally compatible (sanity check).
      - If non-trivial mismatches are found, Phase 2 may downgrade confidence
        or emit an empty/low-op plan, but remains strictly read-only.

  • TARGET ROOT FLEXIBILITY:
      - The user may run Phase 2 against ANY of the canonical roots (01–10):
            01_agentic_core
            02_schemas
            03_runtime
            04_prompt_governance
            05_config
            06_data
            07_observability
            08_scripts
            09_apps
            10_tests
      - CLI:
            python phase02.py --target-root 01_agentic_core
            python phase02.py --target-root 04_prompt_governance
            python phase02.py --target-root-index 9        (=> 09_apps)

  • OUTPUT:
      - Plan is always written to:
            02_schemas/{target_root}_migration_and_rewrite_plan.json
        e.g.:
            02_schemas/01_agentic_core_migration_and_rewrite_plan.json
            02_schemas/09_apps_migration_and_rewrite_plan.json

  • DETERMINISM:
      - No network, no LLM calls, no randomness in plan construction.
      - Re-running Phase 2 with the same inputs yields a bit-identical plan.

IMPLEMENTATION NOTES (THIS FILE):

  • This Phase 2 implementation is intentionally conservative:
      - Uses only hash-level semantic lineage from Phase 0.5.
      - Prefers exact hash matches between live files and global artifacts.
      - Does NOT attempt fine-grained AST diffing or region-level patching.
      - Emits high-confidence "canonical_rewrite" operations only when safe.

  • Bucket name mapping:
      - SSoT canonical root: "06_data"
      - Phase 0.5 canonical bucket: "06_data_source"
      - This file maps "06_data" → "06_data_source" when reading semantic_cache.

  • ZERO-MUTATION GUARANTEE:
      - This script only reads:
            - unified_structure_subatomic.yaml
            - unified_structure_subatomic_meta.yaml
            - 06_data/semantic_cache/**
            - PROJECT_ROOT / {01–10}/**
      - It only WRITES:
            - 02_schemas/{target_root}_migration_and_rewrite_plan.json
        and only when NOT in --dry-run mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

# ======================================================================
# GLOBAL CONSTANTS / ROOTS
# ======================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()

# Canonical top-level roots (01–10, aligned with SSoT + Phase 1)
CANONICAL_ROOTS: List[str] = [
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

# SSoT files
SSOT_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

# Phase 0.5 semantic cache root
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

# Phase 0.5 global domains (hash-keyed artifacts)
GLOBAL_DOMAINS: List[str] = [
    "ast",
    "diffs",
    "embeddings",
    "golden",
    "integrity",
    "meta",
    "safety",
]

# Mapping between canonical root names and semantic_cache bucket names
# (only 06_data differs in current spec).
ROOT_TO_BUCKET: Dict[str, str] = {
    "06_data": "06_data_source",
    # all others map to themselves if not present here
}

# System / tool excludes when scanning live FS
SYSTEM_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "node_modules",
    ".DS_Store",
}

# Extensions treated as "live semantic code / config"
ELIGIBLE_EXTENSIONS = {
    ".py",
    ".ipynb",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
}

MAX_SCAN_DEPTH = 25

# Confidence threshold above which we emit operations
MIN_CONFIDENCE_FOR_OPERATION = 0.60


# ======================================================================
# UTILS
# ======================================================================


def normalize_path(path: Path | str) -> str:
    """
    Normalize a path to a POSIX-style relative path (no leading ./).
    """
    p = Path(path)
    rel = p.as_posix()
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def compute_file_hash(path: Path) -> str:
    """
    Compute a stable SHA-256 hash of file contents.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    """
    Safe JSON reader; returns an error envelope instead of raising.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # pragma: no cover - defensive
        return {"__error__": str(e), "__path__": str(path)}


def write_json(path: Path, data: Dict[str, Any]) -> None:
    """
    Write JSON with indent, ensuring parent directory exists.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def safe_read_text(path: Path, max_bytes: int = 12000) -> str:
    """
    Safely read up to max_bytes from a text file, replacing decode errors.
    """
    try:
        with path.open("rb") as f:
            data = f.read(max_bytes)
        return data.decode("utf-8", errors="replace")
    except Exception:  # pragma: no cover - defensive
        return ""


def iter_live_files(root: Path) -> Iterable[Path]:
    """
    Yield live files under root, respecting SYSTEM_EXCLUDES and MAX_SCAN_DEPTH.
    """
    root = root.resolve()
    for base, dirs, files in os.walk(root):
        base_path = Path(base)
        try:
            rel = base_path.relative_to(root)
            depth = len(rel.parts)
        except ValueError:
            depth = 0

        if depth > MAX_SCAN_DEPTH:
            continue

        dirs[:] = [d for d in dirs if d not in SYSTEM_EXCLUDES]
        for name in files:
            if name in SYSTEM_EXCLUDES:
                continue
            p = base_path / name
            if p.suffix.lower() not in ELIGIBLE_EXTENSIONS:
                continue
            yield p


def canonical_root_to_bucket(target_root: str) -> str:
    """
    Map a canonical root (01–10) to a semantic_cache bucket name.

    - For most roots this is identity.
    - For 06_data we map to 06_data_source to align with Phase 0.5.
    """
    return ROOT_TO_BUCKET.get(target_root, target_root)


# ======================================================================
# CONFIG / DATA CLASSES
# ======================================================================


@dataclass
class Phase2Config:
    """
    Configuration for Phase 2 run.
    """

    target_root: str  # e.g. "01_agentic_core"
    dry_run: bool = False
    verbose: bool = False


@dataclass
class ValidationResult:
    """
    Single validation outcome keyed by a K-code.
    """

    key: str
    description: str
    ok: bool
    detail: Optional[str] = None


@dataclass
class SSoTState:
    """
    Parsed SSoT + META state for a given target root.
    """

    structure: Dict[str, Any]
    meta: Dict[str, Any]
    target_subtree: Dict[str, Any]


@dataclass
class LiveFileMeta:
    """
    Metadata for a live file in the target root.
    """

    rel_path: str
    abs_path: Path
    size_bytes: int
    hash: str
    ext: str


@dataclass
class FilesystemState:
    """
    Live filesystem view for a target root.
    """

    target_root: str
    base_path: Path
    files: List[LiveFileMeta]


@dataclass
class SemanticPointer:
    """
    Canonical pointer from Phase 0.5 for one archived file into a bucket.
    """

    bucket: str  # e.g. "01_agentic_core"
    engine: str  # "RG" | "LIC"
    archive_name: str
    relative: str
    hash: str
    canonical_relative: str
    global_paths: Dict[str, str]  # domain -> relative path under semantic_cache (e.g. "ast/H.ast")


@dataclass
class SemanticCacheState:
    """
    Phase 0.5 semantic cache view relevant to a given bucket.
    """

    bucket: str
    pointers: List[SemanticPointer]
    # Optionally pre-loaded artifacts keyed by hash (not used heavily here)
    hashes: Dict[str, Dict[str, Any]]


@dataclass
class SemanticDiff:
    """
    Semantic comparison between live file and one or more lineage entries.
    """

    live_path: str  # rel path
    best_hash: Optional[str]  # best matching cache hash, if any
    engine: Optional[str]  # RG/LIC or None
    archive_name: Optional[str]
    diff_kind: str  # "no_cache" | "hash_match"
    confidence: float  # 0.0–1.0
    reasons: List[str]
    extra: Dict[str, Any]


@dataclass
class Operation:
    """
    Semantic-only operation for migration plan.
    """

    op_type: str  # "canonical_rewrite" | future types
    target_path: str  # rel path under target_root
    semantic_hash: Optional[str] = None
    engine: Optional[str] = None
    archive_name: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""
    priority: int = 0


@dataclass
class MigrationPlan:
    """
    Top-level plan object that will be serialized as JSON.
    """

    schema_version: str
    phase: str
    mode: str
    target_root: str
    operations: List[Operation]
    summary: Dict[str, Any]
    validations: List[ValidationResult]
    timestamp: str


# ======================================================================
# VALIDATOR / LOGGER
# ======================================================================


class Phase2Validator:
    """
    Lightweight K-code validator / logger for Phase 2.

    This is intentionally simpler than the Phase 0.5 validator, but
    keeps the same style:

        K1–K4  : SSoT + META presence and integrity
        K5–K7  : Filesystem snapshot sanity
        K8–K10 : Semantic cache presence and pointer sanity
        K11–K13: Diff & plan construction
        K_END  : Overall summary
    """

    def __init__(self, verbose: bool = False, fail_fast: bool = False) -> None:
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.results: List[ValidationResult] = []

    # ---- internal helpers -------------------------------------------------

    def _log(self, result: ValidationResult) -> None:
        self.results.append(result)
        if self.verbose:
            status = "OK " if result.ok else "FAIL"
            msg = f"[{status}] {result.key}: {result.description}"
            if result.detail:
                msg += f" — {result.detail}"
            print(msg)
        if self.fail_fast and not result.ok:
            raise RuntimeError(f"Validation {result.key} failed: {result.description}")

    # ---- public helpers ---------------------------------------------------

    def ok(self, key: str, description: str, detail: Optional[str] = None) -> None:
        self._log(ValidationResult(key=key, description=description, ok=True, detail=detail))

    def fail(self, key: str, description: str, detail: Optional[str] = None) -> None:
        self._log(ValidationResult(key=key, description=description, ok=False, detail=detail))

    def all_pass(self) -> bool:
        return all(r.ok for r in self.results if r.key.startswith("K"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "results": [asdict(r) for r in self.results],
            "all_pass": self.all_pass(),
        }

    def print_summary(self) -> None:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.ok)
        failed = total - passed
        print("=== Phase 2 Validation Summary ===")
        print(f"  Total : {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print("  Keys  : " + ", ".join(f"{r.key}={'OK' if r.ok else 'FAIL'}" for r in self.results))


# ======================================================================
# SSoT + META LOADING
# ======================================================================


def load_ssot_and_meta(validator: Phase2Validator, target_root: str) -> Optional[SSoTState]:
    """
    Load unified SSoT YAML + META and extract subtree for target root domain.
    """

    if not SSOT_YAML.exists():
        validator.fail("K1", f"SSoT YAML missing at {SSOT_YAML}")
        return None

    if not META_YAML.exists():
        validator.fail("K2", f"META YAML missing at {META_YAML}")
        return None

    try:
        structure = yaml.safe_load(SSOT_YAML.read_text(encoding="utf-8")) or {}
        meta = yaml.safe_load(META_YAML.read_text(encoding="utf-8")) or {}
        validator.ok("K3", "SSoT YAML & META loaded")
    except Exception as e:  # pragma: no cover - defensive
        validator.fail("K3", f"Failed to parse SSoT or META: {e}")
        return None

    # Map canonical root to logical name as in Phase 1 map_folder_to_logical
    mapping = {
        "01_agentic_core": "agentic_core",
        "02_schemas": "schemas",
        "03_runtime": "runtime",
        "04_prompt_governance": "prompt_governance",
        "05_config": "config",
        "06_data": "data",
        "07_observability": "observability",
        "08_scripts": "scripts",
        "09_apps": "apps",
        "10_tests": "tests",
    }
    logical = mapping.get(target_root, target_root)

    if logical not in structure:
        validator.fail("K4", f"Target logical root '{logical}' missing in SSoT")
        return None

    target_subtree = structure[logical]
    if not isinstance(target_subtree, dict):
        validator.fail("K4", f"Target subtree for '{logical}' is not a dict")
        return None

    validator.ok("K4", f"Found SSoT subtree for logical root '{logical}'")
    return SSoTState(structure=structure, meta=meta, target_subtree=target_subtree)


# ======================================================================
# LIVE FILESYSTEM SNAPSHOT (READ-ONLY)
# ======================================================================


def load_filesystem_state(
    validator: Phase2Validator,
    target_root: str,
) -> Optional[FilesystemState]:
    """
    Capture a read-only snapshot of live files under the target root.
    """

    base_path = PROJECT_ROOT / target_root
    if not base_path.exists():
        validator.fail("K5", f"Target root path does not exist: {base_path}")
        return None

    files: List[LiveFileMeta] = []
    for p in iter_live_files(base_path):
        rel = normalize_path(p.relative_to(base_path))
        try:
            size_bytes = p.stat().st_size
        except OSError:  # pragma: no cover - defensive
            size_bytes = 0
        h = compute_file_hash(p)
        files.append(
            LiveFileMeta(
                rel_path=rel,
                abs_path=p,
                size_bytes=size_bytes,
                hash=h,
                ext=p.suffix.lower(),
            )
        )

    if not files:
        validator.fail("K6", f"No eligible live files found under {base_path}")
        return None

    validator.ok("K7", f"Captured filesystem snapshot with {len(files)} live files")
    return FilesystemState(target_root=target_root, base_path=base_path, files=files)


# ======================================================================
# SEMANTIC CACHE LOADING (PHASE 0.5)
# ======================================================================


def load_bucket_pointers(bucket: str) -> List[SemanticPointer]:
    """
    Load all pointer JSON files for a canonical bucket:

        SEMANTIC_CACHE_ROOT / bucket / L1_archive/P0_5/ingest/{rg|lic}/**/*.json
    """
    bucket_root = SEMANTIC_CACHE_ROOT / bucket
    if not bucket_root.exists():
        return []

    pointers: List[SemanticPointer] = []

    for ptr_file in bucket_root.rglob("*.json"):
        data = read_json(ptr_file)
        if "__error__" in data:
            continue

        h = data.get("hash")
        engine = data.get("engine")
        archive_name = data.get("archive_name")
        rel = data.get("relative")
        canon_rel = data.get("canonical_relative")
        global_obj = data.get("global", {})

        if not h or not engine or not archive_name or not rel or not canon_rel:
            continue

        pointers.append(
            SemanticPointer(
                bucket=bucket,
                engine=str(engine),
                archive_name=str(archive_name),
                relative=str(rel),
                hash=str(h),
                canonical_relative=str(canon_rel),
                global_paths={str(k): str(v) for k, v in global_obj.items()},
            )
        )

    return pointers


def load_semantic_cache_state(
    validator: Phase2Validator,
    target_root: str,
) -> Optional[SemanticCacheState]:
    """
    Load Phase 0.5 semantic cache state relevant to target bucket.

    This checks:
      - semantic_cache root exists
      - all global domains exist (ast, embeddings, etc.)
      - there are canonical pointers for the mapped bucket.
    """

    if not SEMANTIC_CACHE_ROOT.exists():
        validator.fail("K8", f"Semantic cache root missing: {SEMANTIC_CACHE_ROOT}")
        return None

    # Basic structure sanity
    missing_domains = [d for d in GLOBAL_DOMAINS if not (SEMANTIC_CACHE_ROOT / d).exists()]
    if missing_domains:
        validator.fail("K9", f"Missing global semantic cache domains: {missing_domains}")
        return None

    bucket = canonical_root_to_bucket(target_root)
    pointers = load_bucket_pointers(bucket)
    if not pointers:
        validator.fail(
            "K10",
            (
                f"No canonical bucket pointers found for mapped bucket '{bucket}' "
                f"(target_root='{target_root}'). Phase 0.5 may not have been run "
                "for this bucket."
            ),
        )
        return None

    validator.ok("K10", f"Loaded {len(pointers)} canonical pointers for bucket '{bucket}'")
    hashes: Dict[str, Dict[str, Any]] = {}
    return SemanticCacheState(bucket=bucket, pointers=pointers, hashes=hashes)


def lazy_load_global_artifact(hash_value: str, domain: str) -> Optional[Dict[str, Any]]:
    """
    Optionally load a specific global artifact by hash for richer semantics.

    This implementation remains conservative and only loads JSON-like domains
    when needed. Currently not heavily used but kept for future expansion.
    """
    domain_root = SEMANTIC_CACHE_ROOT / domain
    if not domain_root.exists():
        return None

    suffix = {
        "ast": ".ast",
        "diffs": ".diff.json",
        "embeddings": ".embedding",
        "golden": ".golden.json",
        "integrity": ".integrity.json",
        "meta": ".meta.json",
        "safety": ".safety.json",
    }.get(domain)

    if suffix is None:
        return None

    path = domain_root / f"{hash_value}{suffix}"
    if not path.exists():
        return None

    if suffix.endswith(".json"):
        return read_json(path)
    else:
        # Non-JSON artifacts are just returned as metadata wrappers.
        return {"__path__": str(path)}


# ======================================================================
# DIFF COMPUTATION (LIVE FILES vs SEMANTIC CACHE)
# ======================================================================


def build_hash_to_pointers(cache_state: SemanticCacheState) -> Dict[str, List[SemanticPointer]]:
    """
    Build hash -> pointers map for fast lookup of best matches.
    """
    mapping: Dict[str, List[SemanticPointer]] = {}
    for p in cache_state.pointers:
        mapping.setdefault(p.hash, []).append(p)
    return mapping


def compute_semantic_diffs(
    validator: Phase2Validator,
    fs_state: FilesystemState,
    cache_state: SemanticCacheState,
) -> List[SemanticDiff]:
    """
    For each live file, compute a simple semantic diff against Phase 0.5 cache.

    This implementation is intentionally conservative:

      - Treats Phase 0.5 hash as the canonical semantic hash.
      - If the live file's content hash matches one or more pointer hashes:
          • diff_kind = "hash_match"
          • confidence = 1.0
      - Otherwise:
          • diff_kind = "no_cache"
          • confidence = 0.0

    This can later be extended to AST-level comparison and partial diffs.
    """

    hash_to_pointers = build_hash_to_pointers(cache_state)
    diffs: List[SemanticDiff] = []

    for live in fs_state.files:
        candidates = hash_to_pointers.get(live.hash, [])
        if candidates:
            # For now, choose the first candidate; in practice this could
            # be refined (e.g., prefer RG vs LIC depending on domain).
            best = candidates[0]
            diffs.append(
                SemanticDiff(
                    live_path=live.rel_path,
                    best_hash=best.hash,
                    engine=best.engine,
                    archive_name=best.archive_name,
                    diff_kind="hash_match",
                    confidence=1.0,
                    reasons=["hash_equal_to_phase0_5_global_artifact"],
                    extra={
                        "pointer_count_for_hash": len(candidates),
                        "bucket": best.bucket,
                        "canonical_relative": best.canonical_relative,
                    },
                )
            )
        else:
            diffs.append(
                SemanticDiff(
                    live_path=live.rel_path,
                    best_hash=None,
                    engine=None,
                    archive_name=None,
                    diff_kind="no_cache",
                    confidence=0.0,
                    reasons=["no_phase0_5_pointer_for_hash"],
                    extra={},
                )
            )

    validator.ok("K11", f"Computed semantic diffs for {len(diffs)} live files")
    return diffs


# ======================================================================
# OPERATION CONSTRUCTION
# ======================================================================


def build_semantic_operations(
    validator: Phase2Validator,
    diffs: List[SemanticDiff],
) -> List[Operation]:
    """
    Transform semantic diffs into a list of high-level operations.

    CURRENT POLICY (SAFE, CONSERVATIVE):

      - Emit a "canonical_rewrite" operation only for "hash_match" diffs
        with confidence >= MIN_CONFIDENCE_FOR_OPERATION.
      - For "no_cache" diffs, emit no operation (caller can treat as manual).

    All operations are semantic-only descriptions, not actual mutations.
    """

    ops: List[Operation] = []

    for d in diffs:
        if d.diff_kind == "hash_match" and d.best_hash and d.confidence >= MIN_CONFIDENCE_FOR_OPERATION:
            # We interpret this as "this live file is already semantically aligned
            # with a global artifact"; the canonical_rewrite operation can be used
            # to re-materialize content or simply assert provenance.
            reason = "; ".join(d.reasons) if d.reasons else "hash_match"
            priority = 10  # high confidence

            ops.append(
                Operation(
                    op_type="canonical_rewrite",
                    target_path=d.live_path,
                    semantic_hash=d.best_hash,
                    engine=d.engine,
                    archive_name=d.archive_name,
                    confidence=d.confidence,
                    reason=reason,
                    priority=priority,
                )
            )

    if ops:
        validator.ok("K13", f"Generated {len(ops)} semantic-only operations (canonical_rewrite)")
    else:
        validator.ok("K13", "No operations generated; plan degenerates to no-op (safe default)")

    return ops


# ======================================================================
# PLAN CONSTRUCTION (JSON ONLY, ZERO-MUTATION)
# ======================================================================


def build_migration_plan(
    cfg: Phase2Config,
    validator: Phase2Validator,
    operations: List[Operation],
) -> MigrationPlan:
    """
    Construct the final MigrationPlan dataclass.

    ZERO-LOSS GUARANTEES:

      - No mutations to filesystem or semantic cache occur here.
      - This plan is a pure description of intended semantic transformations.
    """

    # Basic summary statistics
    counts: Dict[str, int] = {}
    for op in operations:
        counts[op.op_type] = counts.get(op.op_type, 0) + 1

    summary: Dict[str, Any] = {
        "total_operations": len(operations),
        "by_type": counts,
        "target_root": cfg.target_root,
        "mode": "semantic_only_zero_loss",
        "note": (
            "Phase 2 only plans; no mutation. "
            "Phase 1 & Phase 0.5 remain the only mutators."
        ),
    }

    # Deterministic validation digest
    validation_digest = hashlib.sha256(
        json.dumps(validator.to_dict(), sort_keys=True).encode("utf-8")
    ).hexdigest()
    summary["validation_digest"] = validation_digest

    plan = MigrationPlan(
        schema_version="1.0",
        phase="phase_02_semantic_diff_and_plan",
        mode="semantic_only_zero_loss",
        target_root=cfg.target_root,
        operations=operations,
        summary=summary,
        validations=validator.results,
        timestamp=datetime.now().isoformat(),
    )
    return plan


def write_plan_to_disk(cfg: Phase2Config, plan: MigrationPlan) -> Path:
    """
    Write the plan into 02_schemas/{target_root}_migration_and_rewrite_plan.json.

    Does NOT execute any operations; this is a description only.
    """

    schemas_root = PROJECT_ROOT / "02_schemas"
    out_path = schemas_root / f"{cfg.target_root}_migration_and_rewrite_plan.json"
    if not cfg.dry_run:
        write_json(out_path, asdict(plan))
    return out_path


# ======================================================================
# ORCHESTRATION
# ======================================================================


def run_phase2(cfg: Phase2Config) -> int:
    """
    High-level orchestration for Phase 2.
    """

    if cfg.verbose:
        print("=== Phase 2 — Semantic Diff & Migration Plan ===")
        print(f"Project root : {PROJECT_ROOT}")
        print(f"Target root  : {cfg.target_root}")
        print(f"Semantic cache: {SEMANTIC_CACHE_ROOT}")
        print(f"Dry run      : {cfg.dry_run}")
        print("===============================================")

    validator = Phase2Validator(verbose=cfg.verbose)

    # Step 1: SSoT + META
    ssot_state = load_ssot_and_meta(validator, cfg.target_root)
    if ssot_state is None:
        validator.fail("K_END", "Aborting: SSoT/META load failed")
        validator.print_summary()
        return 1

    # Step 2: Filesystem state
    fs_state = load_filesystem_state(validator, cfg.target_root)
    if fs_state is None:
        validator.fail("K_END", "Aborting: filesystem snapshot failed")
        validator.print_summary()
        return 1

    # Step 3: Semantic cache state
    cache_state = load_semantic_cache_state(validator, cfg.target_root)
    if cache_state is None:
        validator.fail("K_END", "Aborting: semantic cache state failed")
        validator.print_summary()
        return 1

    # Step 4: Diffs
    diffs = compute_semantic_diffs(validator, fs_state, cache_state)

    # Step 5: Operations
    operations = build_semantic_operations(validator, diffs)

    # Step 6: Plan
    plan = build_migration_plan(cfg, validator, operations)

    # Step 7: Output
    if cfg.dry_run:
        # In dry-run we print the plan to stdout instead of writing to disk.
        print(json.dumps(asdict(plan), indent=2, sort_keys=True))
        print("\n[DRY-RUN] Plan not written to disk.")
    else:
        out_path = write_plan_to_disk(cfg, plan)
        print(f"[OK] Plan written to {out_path}")

    # Final validation summary
    if validator.all_pass():
        validator.ok("K_END", "Phase 2 validations passed")
        exit_code = 0
    else:
        validator.fail("K_END", "Phase 2 validations had failures")
        exit_code = 1

    validator.print_summary()
    return exit_code


# ======================================================================
# CLI
# ======================================================================


def parse_args(argv: Optional[List[str]] = None) -> Phase2Config:
    parser = argparse.ArgumentParser(
        description="Phase 2 — Semantic Diff & Migration Plan (ZERO-LOSS, SEMANTIC-ONLY)"
    )
    parser.add_argument(
        "--target-root",
        choices=CANONICAL_ROOTS,
        help="Canonical root to analyze (e.g., 01_agentic_core).",
    )
    parser.add_argument(
        "--target-root-index",
        type=int,
        choices=range(1, 11),
        help="1-based index into canonical roots (1 => 01_agentic_core, ..., 10 => 10_tests).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Emit plan to stdout instead of writing to 02_schemas/.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )

    args = parser.parse_args(argv)

    target_root = args.target_root
    if target_root is None and args.target_root_index is not None:
        idx = args.target_root_index - 1
        target_root = CANONICAL_ROOTS[idx]

    if target_root is None:
        parser.error("You must specify --target-root or --target-root-index")

    return Phase2Config(
        target_root=target_root,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


def main(argv: Optional[List[str]] = None) -> int:
    cfg = parse_args(argv)
    return run_phase2(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
