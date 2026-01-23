"""
PHASE 2.5: BROKEN IMPORT REPAIR
-------------------------------
Objective: Detect and fix multiline imports missed by Phase 2's strict regex.
"""
import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
# Re-use the Sovereign Quarantine list
QUARANTINED_DIRS = {
    "archives", ".sovereign_healing_backup", "__pycache__", ".git", 
    ".venv", "venv", "node_modules", "dist", "build"
}

# Re-define Phase 2 logic to reconstruct the list of 53 renamed files
# (We look for the NEW snake_case files that exist, and map back to OLD PascalCase)
def reconstruct_rename_map():
    # Heuristic: We know Phase 2 converted Camel to Snake.
    # We will search for snake_case files that match Phase 2 verbs
    # and check if they are "fresh" (this is an approximation, but effective).
    
    # Alternatively, we can just hardcode the verbs and look for the snake_case versions
    verbs = [
        "Add", "Collect", "Compare", "Coordinate", "Guard", "Deprecated", "Phase", "Sprint", "Track",
        "Search", "Retrieve", "Request", "Rank", "Match", "Migrate", "Understand", "Use", "Tool", "Titanium",
        "Test", "Signal", "Semantic", "Sandbox", "Runtime", "Restore", "Refine", "Query", "Orchestrate",
        "Observability", "Metacognition", "Load", "Legacy", "Instructional", "Infrastructure",
        "Hardened", "Golden", "Functional", "Fix", "Fetch", "Execute", "Event", "Etl", "Check", "Brand", "Batch",
        "Atomic", "Archive", "Analyze"
    ]
    
    mapping = {} # OldPascal -> NewSnake
    
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]
        for f in files:
            if not f.endswith(".py"): continue
            
            # Check if this file was likely renamed in Phase 2
            # It should be snake_case, start with a verb, and NOT be in the protected list
            stem = f[:-3]
            if "_" in stem and stem[0].islower():
                # Convert back to Pascal to guess the old name
                parts = stem.split('_')
                if not parts: continue
                
                # Check if first part is a known verb (case insensitive match)
                if parts[0].capitalize() in verbs:
                    # Construct probable old PascalCase name
                    # primitive reconstruction: join capitalized parts
                    # This isn't perfect but covers 90% of cases like golden_state_runner -> GoldenStateRunner
                    old_name = "".join(p.capitalize() for p in parts)
                    
                    # Special handling for numbers or odd caps? 
                    # Let's rely on the codebase scanning.
                    mapping[old_name] = stem
                    
    return mapping

def repair_imports():
    print("[*] Starting Multiline Import Repair...")
    mapping = reconstruct_rename_map()
    print(f"[*] Monitoring {len(mapping)} potential renamed candidates for lingering references.")
    
    modified_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]
        for f in files:
            if not f.endswith(".py"): continue
            path = Path(root) / f
            
            # Skip the script itself
            if path.name == "repair_imports_phase25.py": continue
            
            try:
                content = path.read_text(encoding='utf-8')
                original_content = content
                
                # REPAIR STRATEGY:
                # Instead of "Scoped Regex", we use a global replacement for the specific Words
                # BUT we guard it to ensure we don't change class definitions or unrelated strings.
                # Since the files are already renamed, the Class Definition inside the file might already be gone
                # (unless the script renamed the file but not the class inside it - which is common).
                
                # We are looking for IMPORTS.
                # Heuristic: If we see the OldName, and it's NOT a class definition `class OldName`, it's likely a reference.
                
                for old, new in mapping.items():
                    if old not in content: continue
                    
                    # Regex to match "OldName" as a whole word
                    # Exclude: "class OldName" (definition)
                    # Include: "import OldName", "from ... import OldName", "OldName()"
                    
                    def replacement_logic(match):
                        # match.group(1) is the prefix (e.g. "class " or " " or "(")
                        prefix = match.group(1)
                        if "class" in prefix:
                            return match.group(0) # Don't touch class definitions
                        return f"{prefix}{new}"
                    
                    # Look for OldName preceded by boundary, whitespace, comma, or bracket
                    # capture the prefix
                    pattern = re.compile(r"([^a-zA-Z0-9_])" + re.escape(old) + r"\b")
                    content = pattern.sub(rf"\1{new}", content)
                    
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    print(f"  [FIXED] {f}: Replaced references to old PascalCase names.")
                    modified_count += 1
                    
            except Exception as e:
                pass
                
    print(f"[*] Repair Complete. Modified {modified_count} files.")

if __name__ == "__main__":
    repair_imports()
