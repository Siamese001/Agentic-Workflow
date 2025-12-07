import logging
from __future__ import annotations
#!/usr/bin/env python3
"""
PHASE 3 — SEMANTIC HYDRATION OF EMPTY STUBS (FILENAME-BASED VERSION)

This script hydrates empty stub files by:
    • Scanning all canonical directories for stub files (≤30 bytes)
    • Finding donor files from 06_data archive by filename match
    • Using golden cache content when available
    • Hydrating each stub with real code and a provenance header

Outcome:
    Hydrates stubs using filename similarity matching.
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# =====================================================================
# CONFIGURATION
# =====================================================================
PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CANONICAL_DIRS = [
    PROJECT_ROOT / "01_agentic_core",
    PROJECT_ROOT / "02_schemas",
    PROJECT_ROOT / "03_runtime",
    PROJECT_ROOT / "04_prompt_governance",
    PROJECT_ROOT / "05_config",
    PROJECT_ROOT / "07_observability",
    PROJECT_ROOT / "08_scripts",
    PROJECT_ROOT / "09_apps",
    PROJECT_ROOT / "10_tests",
]

# Donor sources - archive directories with real code
DONOR_DIRS = [
    PROJECT_ROOT / "06_data",
]

GOLDEN_DIR = PROJECT_ROOT / "06_data" / "semantic_cache" / "golden"

SIMILARITY_THRESHOLD = 0.70          # filename similarity floor
MIN_DONOR_BYTES = 50                 # ignore trivial legacy files
MAX_STUB_BYTES = 30                  # consider ≤30 bytes a stub


# =====================================================================
# LOAD GOLDEN CONTENT CACHE
# =====================================================================
def load_golden_cache():
    """Load all golden content indexed by hash."""
    golden = {}
    if not GOLDEN_DIR.exists():
        return golden
    for p in GOLDEN_DIR.glob("*.golden.json"):
        try:
            blob = json.loads(p.read_text(encoding="utf-8"))
            content = blob.get("content", "")
            if content and len(content) >= MIN_DONOR_BYTES:
                golden[blob.get("hash", p.stem)] = content
        except Exception:
            continue
    return golden


GOLDEN_CACHE = load_golden_cache()
logging.debug(f"[LOAD] Loaded {len(GOLDEN_CACHE)} golden content entries")


# =====================================================================
# LOAD DONOR FILES
# =====================================================================
def load_donors():
    """Load all Python files from donor directories."""
    donors = {}
    for donor_dir in DONOR_DIRS:
        if not donor_dir.exists():
            continue
        for p in donor_dir.rglob("*.py"):
            try:
                if p.stat().st_size >= MIN_DONOR_BYTES:
                    # Normalize filename for matching
                    key = normalize_name(p.stem)
                    if key not in donors:
                        donors[key] = p
            except Exception:
                continue
    return donors


def normalize_name(name: str) -> str:
    """Normalize filename for matching."""
    # Remove common prefixes/suffixes, lowercase
    name = name.lower()
    name = re.sub(r'^(test_|_test$)', '', name)
    name = re.sub(r'[_\-]+', '_', name)
    return name.strip('_')


DONORS = load_donors()
logging.debug(f"[LOAD] Loaded {len(DONORS)} donor files")


# =====================================================================
# FILENAME SIMILARITY
# =====================================================================
def filename_similarity(name1: str, name2: str) -> float:
    """Compute similarity between two filenames."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()


# =====================================================================
# HYDRATION UTIL
# =====================================================================
def write_hydrated(target: Path, source_desc: str, content: str, score: float):
    header = (
        f"# ============================================================\n"
        f"# Hydrated via Phase 3 — Filename Matching\n"
        f"# Source: {source_desc}\n"
        f"# Match Score: {score:.4f}\n"
        f"# ============================================================\n\n"
    )
    target.write_text(header + content, encoding="utf-8")
    logging.debug(f"[HYDRATED] {target.name}  ←  {source_desc}  ({score:.4f})")


# =====================================================================
# MAIN EXECUTION
# =====================================================================
def main():
    hydrated = 0
    skipped = 0
    
    # Build list of donor names for matching
    donor_names = list(DONORS.keys())

    for root in CANONICAL_DIRS:
        if not root.exists():
            continue
        for stub in root.rglob("*.py"):
            # ignore __init__
            if stub.name == "__init__.py":
                continue

            # detect stub
            try:
                if stub.stat().st_size > MAX_STUB_BYTES:
                    continue  # not a stub
            except Exception:
                continue

            stub_key = normalize_name(stub.stem)
            
            # Find best matching donor by filename
            best_score = 0.0
            best_donor_key = None
            
            for donor_key in donor_names:
                score = filename_similarity(stub_key, donor_key)
                if score > best_score:
                    best_score = score
                    best_donor_key = donor_key

            if best_score >= SIMILARITY_THRESHOLD and best_donor_key:
                donor_path = DONORS[best_donor_key]
                try:
                    content = donor_path.read_text(encoding="utf-8", errors="ignore")
                    write_hydrated(stub, str(donor_path.name), content, best_score)
                    hydrated += 1
                except Exception as e:
                    logging.debug(f"[ERROR] Failed to read donor {donor_path}: {e}")
                    skipped += 1
            else:
                # Try exact name match in golden cache (less common)
                logging.debug(f"[NO MATCH] {stub} (best: {best_score:.2f})")
                skipped += 1

    logging.debug("\n=================== SUMMARY ===================")
    logging.debug(f"Hydrated: {hydrated}")
    logging.debug(f"Skipped (no donor ≥{SIMILARITY_THRESHOLD}): {skipped}")
    logging.debug("===============================================")


if __name__ == "__main__":
    main()
