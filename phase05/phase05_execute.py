#!/usr/bin/env python3
"""
PHASE 0.5 — SEMANTIC LINEAGE CACHE REBUILD (v3-LITE, CLEAN-WIPE, SPEC-ALIGNED)

Implements the ORIGINAL Phase 0.5 spec with the constraints you confirmed:

  • ARCHIVE-ONLY semantic ingestion (NO scanning of live 10 folders).
  • STRICT archive roots (v3-LITE):

        RG (Resume Engine):
            C:/Git/Resume Engine Archive/Agentic-Workflow-10_11/
            C:/Git/Resume Engine Archive/Agentic_Workflow-10_10/
            C:/Git/Resume Engine Archive/Agentic-Workflow-10_9/
            C:/Git/Resume Engine Archive/Agentic-Workflow-10_8_core/
            C:/Git/Resume Engine Archive/Agentic-Workflow-10_7_main/
            C:/Git/Resume Engine Archive/Microservices Model/
            C:/Git/Resume Engine Archive/Monolith/
            C:/Git/Resume Engine Archive/Monolithic/
            C:/Git/Resume Engine Archive/v2/
            C:/Git/Resume Engine Archive/v6.0/
            C:/Git/Resume Engine Archive/v7.0/
            C:/Git/Resume Engine Archive/v7.5/
            C:/Git/Resume Engine Archive/v8.0/
            C:/Git/Resume Engine Archive/v9.0/
            C:/Git/Resume Engine Archive/v10.0/
            C:/Git/Resume Engine Archive/Old Resume Gen Python/   (ALL eligible files)

        LIC (Outreach Engine):
            C:/Git/Reachout Engine Archive/Agentic-LIC/
            C:/Git/Reachout Engine Archive/Agentic LIC/
            C:/Git/Reachout Engine Archive/Monolithic/
            C:/Git/Reachout Engine Archive/Old LIC/
            C:/Git/Reachout Engine Archive/deprecated in v13/

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
"""

from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Dict, List, Tuple

# =====================================================================
# ROOTS
# =====================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CACHE_ROOT   = PROJECT_ROOT / "06_data" / "semantic_cache"

SSOT_YAML    = PROJECT_ROOT / "unified_structure_subatomic.yaml"  # existence check only for now

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
    (Path(r"C:/Git/Resume Engine Archive/Agentic-Workflow-10_11/"),      "Agentic-Workflow-10_11"),
    (Path(r"C:/Git/Resume Engine Archive/Agentic_Workflow-10_10/"),      "Agentic_Workflow-10_10"),
    (Path(r"C:/Git/Resume Engine Archive/Agentic-Workflow-10_9/"),       "Agentic-Workflow-10_9"),
    (Path(r"C:/Git/Resume Engine Archive/Agentic-Workflow-10_8_core/"),  "Agentic-Workflow-10_8_core"),
    (Path(r"C:/Git/Resume Engine Archive/Agentic-Workflow-10_7_main/"),  "Agentic-Workflow-10_7_main"),
    (Path(r"C:/Git/Resume Engine Archive/Microservices Model/"),         "Microservices Model"),
    (Path(r"C:/Git/Resume Engine Archive/Monolith/"),                    "Monolith"),
    (Path(r"C:/Git/Resume Engine Archive/Monolithic/"),                  "Monolithic"),
    (Path(r"C:/Git/Resume Engine Archive/v2/"),                          "v2"),
    (Path(r"C:/Git/Resume Engine Archive/v6.0/"),                        "v6.0"),
    # NEW: v7.0–v10.0 treated as full RG archives
    (Path(r"C:/Git/Resume Engine Archive/v7.0/"),                        "v7.0"),
    (Path(r"C:/Git/Resume Engine Archive/v7.5/"),                        "v7.5"),
    (Path(r"C:/Git/Resume Engine Archive/v8.0/"),                        "v8.0"),
    (Path(r"C:/Git/Resume Engine Archive/v9.0/"),                        "v9.0"),
    (Path(r"C:/Git/Resume Engine Archive/v10.0/"),                       "v10.0"),
    # Old Resume Gen Python as a full RG archive (ALL eligible files)
    (Path(r"C:/Git/Resume Engine Archive/Old Resume Gen Python/"),       "Old Resume Gen Python"),
]

# LIC archives (Outreach Engine)
LIC_ARCHIVE_ROOTS: List[Tuple[Path, str]] = [
    (Path(r"C:/Git/Reachout Engine Archive/Agentic-LIC/"),       "Agentic-LIC"),
    (Path(r"C:/Git/Reachout Engine Archive/Agentic LIC/"),       "Agentic LIC"),
    (Path(r"C:/Git/Reachout Engine Archive/Monolithic/"),        "Monolithic"),
    (Path(r"C:/Git/Reachout Engine Archive/Old LIC/"),           "Old LIC"),
    (Path(r"C:/Git/Reachout Engine Archive/deprecated in v13/"), "deprecated in v13"),
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
            pointer_dir  = bucket_root / canon_rel
            pointer_file = pointer_dir / f"{f.stem}{f.suffix}.json"

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

def run() -> int:
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


if __name__ == "__main__":
    raise SystemExit(run())
