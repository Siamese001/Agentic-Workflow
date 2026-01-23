"""
PHASE 2 REMEDIATION: COMPLEX CASES & SAFER UPDATES
--------------------------------------------------
Objective:
    1. Parse 'remediation_skipped.log'.
    2. Apply advanced heuristics for Phase 2 targets.
    3. execute `git mv`.
    4. Update imports using Tokenization (Zero-Risk of string corruption).
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Set

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
SKIPPED_LOG = ROOT_DIR / "remediation_skipped.log"

# Respect the Sovereign Quarantine list from conftest.py
QUARANTINED_DIRS = {
    "archives",
    ".sovereign_healing_backup",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}

# Expanded Action Verbs based on Phase 1 "Skipped" analysis
VERB_PATTERN = re.compile(
    r"^(Add|Collect|Compare|Coordinate|Guard|Deprecated|Phase|Sprint|Track|"
    r"Search|Retrieve|Request|Rank|Match|Migrate|Understand|Use|Tool|Titanium|"
    r"Test|Signal|Semantic|Sandbox|Runtime|Restore|Refine|Query|P[0-9]|Orchestrate|"
    r"Observability|Metacognition|Load|Legacy|Instructional|Infrastructure|"
    r"Hardened|Golden|Functional|Fix|Fetch|Execute|Event|Etl|Check|Brand|Batch|"
    r"Atomic|Archive|Analyze)(?=[A-Z0-9])"
)

# Expanded Protection: partial matches allowed
PROTECTED_SUBSTRINGS = (
    "Agent", "Orchestrator", "Validator", "Factory", "Registry", "Engine", 
    "Model", "Schema", "Config", "Exception", "Client", "Service", "Manager",
    "Router", "Fusion", "Pipeline", "Wrapper", "Adapter", "Context", "Architect"
)

def to_snake_case(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_project_file_map() -> dict:
    """Builds a map of {filename: Path} once to avoid repeated rglob calls."""
    print("[*] Mapping project files (ignoring quarantined dirs)...")
    file_map = {}
    for root, dirs, files in os.walk(ROOT_DIR):
        # In-place modification of dirs to skip quarantined ones
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]
        for f in files:
            if f.endswith(".py"):
                # Store only the first occurrence or handle duplicates if necessary
                if f not in file_map:
                    file_map[f] = Path(root) / f
    return file_map

def get_targets(file_map: dict) -> List[Path]:
    if not SKIPPED_LOG.exists(): return []
    with open(SKIPPED_LOG, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    files = []
    for line in lines:
        # Clean up Windsurf tags and log suffixes
        line = re.sub(r'\\s*', '', line)
        if ":" in line:
            fname = line.split(":")[0].strip()
        else:
            fname = line.split(" ")[0].strip()
            
        if fname in file_map:
            files.append(file_map[fname])
            
    return sorted(list(set(files)))

def update_imports_tokenized(renames: List[Tuple[Path, str]]):
    """
    Safely updates imports using scoped regex. 
    Only modifies lines that start with import/from statements.
    """
    print("\n[Phase 2] Updating Imports (Tokenized Safety)...")
    rename_map = {p.stem: Path(n).stem for p, n in renames}
    
    count = 0
    # We can reuse the file_map keys to find files to update
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]
        for file in files:
            if not file.endswith(".py"): continue
            path = Path(root) / file
            
            try:
                content_str = path.read_text(encoding='utf-8')
                if not any(old in content_str for old in rename_map):
                    continue

                lines = content_str.splitlines(keepends=True)
                new_lines = []
                file_modified = False
                
                for line in lines:
                    # Scoped Regex: Only modify lines that look like imports
                    if re.match(r"^\s*(import|from)\b", line):
                        for old, new in rename_map.items():
                            if re.search(rf"\b{old}\b", line):
                                line = re.sub(rf"\b{old}\b", new, line)
                                file_modified = True
                    new_lines.append(line)
                
                if file_modified:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    count += 1

            except Exception as e:
                pass
                
    print(f"  Modified {count} files.")

def main():
    file_map = get_project_file_map()
    print(f"[*] Starting Phase 2 Analysis...")
    targets = get_targets(file_map)
    print(f"[*] Loaded {len(targets)} candidates from skipped log.")
    
    rename_queue = []
    
    for file_path in targets:
        name = file_path.name
        stem = file_path.stem
        
        # Priority Rule: Protected Substring (Stronger than verb)
        # matches "CanonValidatorEngineZlm" because "Engine" is in it
        if any(sub in name for sub in PROTECTED_SUBSTRINGS):
            continue
            
        # Action Rule: Expanded Verb List
        if VERB_PATTERN.match(stem):
            new_name = to_snake_case(stem) + ".py"
            rename_queue.append((file_path, new_name))
            continue
            
        # Fallback: Files starting with "Test" or "Fix" not caught above
        if stem.startswith("Test") or stem.startswith("Fix"):
             new_name = to_snake_case(stem) + ".py"
             rename_queue.append((file_path, new_name))

    print(f"\n[Phase 2] Identifying {len(rename_queue)} actionable renames.")
    
    if not rename_queue:
        print("No actions found.")
        return

    print("\n[Phase 2] Executing Git Moves...")
    success = 0
    for old, new_name in rename_queue:
        new_path = old.parent / new_name
        if new_path.exists(): continue
        
        if os.system(f'git mv "{old}" "{new_path}"') == 0:
            print(f"  [OK] {old.name} -> {new_name}")
            success += 1
            
    if success > 0:
        update_imports_tokenized(rename_queue)

if __name__ == "__main__":
    main()
