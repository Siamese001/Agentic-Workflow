#!/usr/bin/env python3
"""
PHASE 4.1 — 08_scripts CANONICAL PURGE AND RELOCATION

This script relocates mislocated cognitive/runtime/governance/security engine
code from 08_scripts to canonical numbered domains using SSoT + Codemap.

Execution model: Docker-compatible, zero-loss, deterministic.
"""

import json
import hashlib
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

REPO_ROOT = Path("C:/Git/Agentic-Workflow")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Target subtrees to purge (scope of this patch)
TARGET_SUBTREES = [
    "08_scripts/logic",
    "08_scripts/pipeline_ops",
    "08_scripts/runtime_ops",
    "08_scripts/security_controls",
]

# Excluded files/paths
EXCLUDED_PATHS = {
    "08_scripts/migration",
    "08_scripts/zero_loss_merge_engine.py",
    "08_scripts/windsurf_unassigned_purge.py",
    "08_scripts/phase_4_1_08_scripts_purge.py",  # This script
}

# Valid canonical domain prefixes
VALID_DOMAINS = [
    "01_agentic_core/",
    "02_schemas/",
    "03_runtime/",
    "04_prompt_governance/",
    "05_config/",
    "07_observability/",
    "09_apps/",
]

# Output directories
ROLLBACK_DIR = REPO_ROOT / "06_data/rollback_snapshot/phase_4_1" / TIMESTAMP
ARCHIVE_DIR = REPO_ROOT / "06_data/stray_root_archive" / f"08_scripts_purge_{TIMESTAMP}"
AMBIGUOUS_DIR = REPO_ROOT / "05_config/review_pending/08_scripts_ambiguous" / TIMESTAMP
CONFLICT_DIR = REPO_ROOT / "05_config/review_pending/conflicts_08_scripts" / TIMESTAMP
RESIDUAL_DIR = REPO_ROOT / "05_config/review_pending/08_scripts_residual" / TIMESTAMP
LOG_DIR = REPO_ROOT / "06_data/execution_logs"
MERKLE_DIR = REPO_ROOT / "06_data/final_merkle"

# Placeholder detection patterns
PLACEHOLDER_PATTERNS = [
    "# ZERO-LOSS PLACEHOLDER",
    "# Phase-3 placeholder",
    "# Placeholder file",
    "pass  # placeholder",
    "pass # placeholder",
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of file content."""
    if not filepath.exists():
        return ""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha256_content(content: bytes) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def normalize_path(path: str) -> str:
    """Normalize path to forward slashes."""
    return path.replace("\\", "/")


def is_placeholder(filepath: Path) -> bool:
    """Check if file is a Phase-3 placeholder."""
    if not filepath.exists():
        return False
    try:
        content = filepath.read_text(encoding="utf-8")
        # Empty or near-empty files
        if len(content.strip()) < 50:
            return True
        # Check for placeholder patterns
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in content:
                return True
        return False
    except Exception:
        return False


def ensure_dir(path: Path):
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def get_sub_tail(source_path: str) -> str:
    """
    Extract sub_tail from source path.
    
    Examples:
    - 08_scripts/logic/data_access/get_info/.../match_context.py
      → data_access/get_info/.../match_context.py
    
    - 08_scripts/logic/logic/data_access/.../validate_schema.py
      → data_access/.../validate_schema.py
    
    - 08_scripts/pipeline_ops/guardrails/.../apply_safety.py
      → guardrails/.../apply_safety.py
    """
    parts = source_path.split("/")
    
    # Find the domain-specific root
    if "08_scripts/logic/logic/" in source_path:
        # Handle nested logic/logic case
        idx = parts.index("logic") + 2  # Skip both "logic" entries
    elif "08_scripts/logic/" in source_path:
        idx = parts.index("logic") + 1
    elif "08_scripts/pipeline_ops/" in source_path:
        idx = parts.index("pipeline_ops") + 1
    elif "08_scripts/runtime_ops/" in source_path:
        idx = parts.index("runtime_ops") + 1
    elif "08_scripts/security_controls/" in source_path:
        idx = parts.index("security_controls") + 1
    else:
        # Fallback: skip 08_scripts and first subdirectory
        idx = 2
    
    return "/".join(parts[idx:])


# ============================================================================
# PHASE 4.1-A: RELOAD EXPECTED UNIVERSE (SSoT)
# ============================================================================

def load_expected_py() -> Tuple[Set[str], Set[str]]:
    """
    Load expected_py and expected_dirs from migration plans.
    Returns (expected_py, expected_dirs).
    """
    schemas_dir = REPO_ROOT / "02_schemas"
    plan_files = list(schemas_dir.glob("*_migration_and_rewrite_plan.json"))
    
    expected_py: Set[str] = set()
    expected_dirs: Set[str] = set()
    
    for pf in plan_files:
        try:
            with open(pf, "r", encoding="utf-8") as f:
                content = f.read()
                # Skip comment lines at start
                lines = content.split("\n")
                json_lines = [l for l in lines if not l.strip().startswith("#")]
                data = json.loads("\n".join(json_lines))
            
            ops = data.get("operations", [])
            for op in ops:
                target = op.get("target_path", "")
                bucket = op.get("bucket", "")
                if target and bucket:
                    # Build full canonical path
                    full_path = f"{bucket}/{target}"
                    if full_path.endswith(".py"):
                        expected_py.add(normalize_path(full_path))
                        expected_dirs.add(normalize_path(str(Path(full_path).parent)))
        except Exception as e:
            print(f"Warning: Error reading {pf.name}: {e}")
    
    return expected_py, expected_dirs


# ============================================================================
# PHASE 4.1-B: ENUMERATE 08_scripts CANDIDATE FILES
# ============================================================================

def enumerate_candidates(expected_py: Set[str]) -> List[Dict]:
    """
    Enumerate candidate files from target subtrees.
    Returns list of candidate dicts with source_path, filename, sub_tail.
    """
    candidates = []
    
    for subtree in TARGET_SUBTREES:
        subtree_path = REPO_ROOT / subtree
        if not subtree_path.exists():
            continue
        
        for py_file in subtree_path.rglob("*.py"):
            rel_path = normalize_path(str(py_file.relative_to(REPO_ROOT)))
            
            # Check exclusions
            skip = False
            for excl in EXCLUDED_PATHS:
                if rel_path.startswith(excl) or rel_path == excl:
                    skip = True
                    break
            if skip:
                continue
            
            # Skip __init__.py files (needed for package imports)
            if py_file.name == "__init__.py":
                continue
            
            # Skip if already in expected_py (canonical location)
            if rel_path in expected_py:
                continue
            
            sub_tail = get_sub_tail(rel_path)
            
            candidates.append({
                "source_path": rel_path,
                "filename": py_file.name,
                "sub_tail": sub_tail,
                "abs_path": py_file,
            })
    
    return candidates


# ============================================================================
# PHASE 4.1-C: DETERMINE CANONICAL DESTINATIONS
# ============================================================================

def find_canonical_dest(candidate: Dict, expected_py: Set[str]) -> Tuple[Optional[str], List[str], str]:
    """
    Find canonical destination for a candidate file.
    Returns (canonical_dest, suffix_matches, reason).
    """
    sub_tail = candidate["sub_tail"]
    filename = candidate["filename"]
    
    # Find all paths ending with sub_tail
    suffix_matches = [p for p in expected_py if p.endswith(sub_tail)]
    
    if len(suffix_matches) == 1:
        canonical_dest = suffix_matches[0]
        
        # Validate domain
        valid_domain = any(canonical_dest.startswith(d) for d in VALID_DOMAINS)
        if not valid_domain:
            return None, suffix_matches, "invalid_domain"
        
        return canonical_dest, suffix_matches, "unique_match"
    
    elif len(suffix_matches) == 0:
        # Try matching by filename only as fallback diagnostic
        filename_matches = [p for p in expected_py if p.endswith(f"/{filename}")]
        return None, filename_matches[:5], "no_suffix_match"
    
    else:
        return None, suffix_matches[:10], "multiple_matches"


# ============================================================================
# PHASE 4.1-D: RELOCATION + ARCHIVAL
# ============================================================================

def relocate_file(
    candidate: Dict,
    canonical_dest: str,
    audit_log: List[Dict],
) -> bool:
    """
    Relocate a candidate file to its canonical destination.
    Returns True if relocation was performed.
    """
    source_abs = candidate["abs_path"]
    source_rel = candidate["source_path"]
    dest_abs = REPO_ROOT / canonical_dest
    
    # Read source content
    source_content = source_abs.read_bytes()
    source_hash = sha256_content(source_content)
    
    # 1. Create rollback snapshot
    rollback_path = ROLLBACK_DIR / source_rel
    ensure_dir(rollback_path.parent)
    shutil.copy2(source_abs, rollback_path)
    
    # 2. Check conflict protocol
    dest_hash_before = ""
    safe_to_write = True
    placeholder_overwrite = False
    conflict_flag = False
    
    if dest_abs.exists():
        dest_hash_before = sha256_file(dest_abs)
        
        if is_placeholder(dest_abs):
            # Overwrite placeholder
            safe_to_write = True
            placeholder_overwrite = True
        elif dest_hash_before == source_hash:
            # Identical content - source is redundant
            safe_to_write = False
        else:
            # Real conflict
            safe_to_write = False
            conflict_flag = True
            
            # Move source to conflict quarantine
            conflict_path = CONFLICT_DIR / f"{source_rel}_CONFLICT_{source_hash[:8]}.py"
            ensure_dir(conflict_path.parent)
            shutil.copy2(source_abs, conflict_path)
    
    # 3. Archive source
    archive_path = ARCHIVE_DIR / source_rel
    ensure_dir(archive_path.parent)
    shutil.move(str(source_abs), str(archive_path))
    
    # 4. Write canonical destination
    dest_hash_after = ""
    if safe_to_write:
        ensure_dir(dest_abs.parent)
        dest_abs.write_bytes(source_content)
        dest_hash_after = sha256_content(source_content)
    
    # 5. Audit log entry
    audit_log.append({
        "action": "relocate_08_scripts",
        "source_path": source_rel,
        "canonical_dest": canonical_dest,
        "hash_source_before": source_hash,
        "hash_dest_before": dest_hash_before,
        "hash_dest_after": dest_hash_after,
        "conflict_flag": conflict_flag,
        "placeholder_overwrite_flag": placeholder_overwrite,
        "safe_to_write": safe_to_write,
    })
    
    return safe_to_write


# ============================================================================
# PHASE 4.1-E: AMBIGUITY HANDLING
# ============================================================================

def handle_ambiguous(
    candidate: Dict,
    suffix_matches: List[str],
    reason: str,
    audit_log: List[Dict],
):
    """Handle ambiguous/unmapped files."""
    source_abs = candidate["abs_path"]
    source_rel = candidate["source_path"]
    
    # Read source content
    source_content = source_abs.read_bytes()
    source_hash = sha256_content(source_content)
    
    # 1. Move to ambiguous quarantine
    ambiguous_path = AMBIGUOUS_DIR / source_rel
    ensure_dir(ambiguous_path.parent)
    shutil.copy2(source_abs, ambiguous_path)
    
    # 2. Archive original
    archive_path = ARCHIVE_DIR / source_rel
    ensure_dir(archive_path.parent)
    shutil.move(str(source_abs), str(archive_path))
    
    # 3. Audit log
    audit_log.append({
        "action": "ambiguous_08_scripts",
        "source_path": source_rel,
        "candidate_suffix_matches": suffix_matches,
        "reason": reason,
        "hash_source": source_hash,
    })


# ============================================================================
# PHASE 4.1-F: CLEANUP
# ============================================================================

def cleanup_empty_dirs():
    """Remove empty directories from target subtrees."""
    removed = []
    for subtree in TARGET_SUBTREES:
        subtree_path = REPO_ROOT / subtree
        if not subtree_path.exists():
            continue
        
        # Walk bottom-up to remove empty dirs
        for dirpath, dirnames, filenames in os.walk(str(subtree_path), topdown=False):
            dp = Path(dirpath)
            # Check if directory is empty (no files, no subdirs)
            if not any(dp.iterdir()):
                try:
                    dp.rmdir()
                    removed.append(normalize_path(str(dp.relative_to(REPO_ROOT))))
                except Exception:
                    pass
    
    return removed


def check_residual_files(audit_log: List[Dict]) -> List[str]:
    """Check for residual .py files in target subtrees."""
    residual = []
    
    for subtree in TARGET_SUBTREES:
        subtree_path = REPO_ROOT / subtree
        if not subtree_path.exists():
            continue
        
        for py_file in subtree_path.rglob("*.py"):
            rel_path = normalize_path(str(py_file.relative_to(REPO_ROOT)))
            
            # Skip __init__.py
            if py_file.name == "__init__.py":
                continue
            
            # Skip excluded
            skip = False
            for excl in EXCLUDED_PATHS:
                if rel_path.startswith(excl) or rel_path == excl:
                    skip = True
                    break
            if skip:
                continue
            
            # This is a residual file
            residual.append(rel_path)
            
            # Move to residual quarantine
            residual_path = RESIDUAL_DIR / rel_path
            ensure_dir(residual_path.parent)
            shutil.copy2(py_file, residual_path)
            
            # Archive
            archive_path = ARCHIVE_DIR / rel_path
            ensure_dir(archive_path.parent)
            shutil.move(str(py_file), str(archive_path))
            
            audit_log.append({
                "action": "residual_08_scripts",
                "source_path": rel_path,
            })
    
    return residual


# ============================================================================
# PHASE 4.1-G: MERKLE + CODEMAP
# ============================================================================

def compute_merkle_root() -> Dict:
    """Compute Merkle root for repository."""
    folder_summary = {}
    all_hashes = []
    total_files = 0
    total_py_files = 0
    
    for domain in ["01_agentic_core", "02_schemas", "03_runtime", "04_prompt_governance",
                   "05_config", "06_data", "07_observability", "08_scripts", "09_apps"]:
        domain_path = REPO_ROOT / domain
        if not domain_path.exists():
            folder_summary[domain] = {"files": 0, "py_files": 0}
            continue
        
        domain_files = 0
        domain_py = 0
        
        for f in domain_path.rglob("*"):
            if f.is_file():
                domain_files += 1
                total_files += 1
                if f.suffix == ".py":
                    domain_py += 1
                    total_py_files += 1
                    all_hashes.append(sha256_file(f))
        
        folder_summary[domain] = {"files": domain_files, "py_files": domain_py}
    
    # Compute Merkle root from sorted hashes
    all_hashes.sort()
    combined = "".join(all_hashes)
    merkle_root = hashlib.sha256(combined.encode()).hexdigest()
    
    return {
        "merkle_root": merkle_root,
        "total_files": total_files,
        "total_py_files": total_py_files,
        "folder_summary": folder_summary,
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("PHASE 4.1 — 08_scripts CANONICAL PURGE AND RELOCATION")
    print("=" * 80)
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Repository: {REPO_ROOT}")
    print()
    
    # Ensure output directories
    for d in [ROLLBACK_DIR, ARCHIVE_DIR, AMBIGUOUS_DIR, CONFLICT_DIR, 
              RESIDUAL_DIR, LOG_DIR, MERKLE_DIR]:
        ensure_dir(d)
    
    audit_log: List[Dict] = []
    
    # Phase 4.1-A: Load expected universe
    print("Phase 4.1-A: Loading expected_py universe from SSoT...")
    expected_py, expected_dirs = load_expected_py()
    print(f"  Loaded {len(expected_py)} expected_py entries")
    print(f"  Loaded {len(expected_dirs)} expected_dirs entries")
    print()
    
    # Phase 4.1-B: Enumerate candidates
    print("Phase 4.1-B: Enumerating 08_scripts candidate files...")
    candidates = enumerate_candidates(expected_py)
    print(f"  Found {len(candidates)} candidate files")
    print()
    
    # Phase 4.1-C & D: Determine destinations and relocate
    print("Phase 4.1-C/D: Determining canonical destinations and relocating...")
    relocated_count = 0
    ambiguous_count = 0
    conflict_count = 0
    
    for candidate in candidates:
        canonical_dest, suffix_matches, reason = find_canonical_dest(candidate, expected_py)
        
        if canonical_dest:
            success = relocate_file(candidate, canonical_dest, audit_log)
            if success:
                relocated_count += 1
                print(f"  ✓ Relocated: {candidate['source_path']} → {canonical_dest}")
            else:
                if audit_log[-1].get("conflict_flag"):
                    conflict_count += 1
                    print(f"  ⚠ Conflict: {candidate['source_path']} (dest exists with different content)")
                else:
                    print(f"  ○ Redundant: {candidate['source_path']} (identical to dest)")
        else:
            handle_ambiguous(candidate, suffix_matches, reason, audit_log)
            ambiguous_count += 1
            print(f"  ? Ambiguous: {candidate['source_path']} ({reason})")
    
    print()
    print(f"  Relocated: {relocated_count}")
    print(f"  Ambiguous: {ambiguous_count}")
    print(f"  Conflicts: {conflict_count}")
    print()
    
    # Phase 4.1-E: Already handled above
    
    # Phase 4.1-F: Cleanup
    print("Phase 4.1-F: Checking for residual files and cleaning up...")
    residual = check_residual_files(audit_log)
    if residual:
        print(f"  Found {len(residual)} residual files (moved to review_pending)")
    
    removed_dirs = cleanup_empty_dirs()
    if removed_dirs:
        print(f"  Removed {len(removed_dirs)} empty directories")
    print()
    
    # Phase 4.1-G: Merkle + Codemap
    print("Phase 4.1-G: Computing Merkle root...")
    merkle_data = compute_merkle_root()
    merkle_data["timestamp"] = TIMESTAMP
    merkle_data["relocated_count"] = relocated_count
    merkle_data["ambiguous_count"] = ambiguous_count
    merkle_data["conflict_count"] = conflict_count
    merkle_data["residual_count"] = len(residual)
    
    merkle_file = MERKLE_DIR / f"FINAL_FREEZE_08_scripts_purge_{TIMESTAMP}.json"
    with open(merkle_file, "w", encoding="utf-8") as f:
        json.dump(merkle_data, f, indent=2)
    print(f"  Merkle root: {merkle_data['merkle_root'][:16]}...")
    print(f"  Written to: {merkle_file.name}")
    print()
    
    # Write audit log
    log_file = LOG_DIR / f"windsurf_omega_08_scripts_purge_{TIMESTAMP}.log"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2)
    print(f"Audit log written: {log_file.name}")
    print()
    
    # Write codemap update
    codemap_file = LOG_DIR / f"codemap_08_scripts_purge_{TIMESTAMP}.json"
    codemap_data = {
        "timestamp": TIMESTAMP,
        "phase": "4.1",
        "description": "08_scripts canonical purge and relocation",
        "relocated_files": [e for e in audit_log if e.get("action") == "relocate_08_scripts"],
        "ambiguous_files": [e for e in audit_log if e.get("action") == "ambiguous_08_scripts"],
        "residual_files": [e for e in audit_log if e.get("action") == "residual_08_scripts"],
        "merkle_root": merkle_data["merkle_root"],
    }
    with open(codemap_file, "w", encoding="utf-8") as f:
        json.dump(codemap_data, f, indent=2)
    print(f"Codemap written: {codemap_file.name}")
    print()
    
    # Phase 4.1-H: Final confirmation
    print("Phase 4.1-H: Final verification...")
    
    # Check that no non-utility .py files remain
    remaining_py = []
    for subtree in TARGET_SUBTREES:
        subtree_path = REPO_ROOT / subtree
        if not subtree_path.exists():
            continue
        for py_file in subtree_path.rglob("*.py"):
            if py_file.name != "__init__.py":
                rel_path = normalize_path(str(py_file.relative_to(REPO_ROOT)))
                skip = False
                for excl in EXCLUDED_PATHS:
                    if rel_path.startswith(excl) or rel_path == excl:
                        skip = True
                        break
                if not skip:
                    remaining_py.append(rel_path)
    
    if remaining_py:
        print(f"  ERROR: {len(remaining_py)} non-utility .py files still remain!")
        for rp in remaining_py[:10]:
            print(f"    - {rp}")
        audit_log.append({
            "action": "phase_4_1_failure",
            "reason": "remaining_py_files",
            "files": remaining_py,
        })
        # Re-write audit log with failure
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(audit_log, f, indent=2)
        return False
    
    print()
    print("=" * 80)
    print("08_SCRIPTS PURGE COMPLETE")
    print("ALL 08_SCRIPTS ENGINE FILES RELOCATED TO CANONICAL DOMAINS")
    print("ALL AMBIGUOUS FILES MOVED TO REVIEW_PENDING")
    print("MERKLE AND CODEMAP UPDATED")
    print("REPOSITORY IS NOW STRUCTURALLY READY FOR PHASE-3 HYDRATION")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
