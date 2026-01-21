import hashlib
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Groups to investigate based on naming patterns
GROUPS = {
    "Location": ["LocationAgent.py", "LocationValidatorAgent.py", "LocationHealerAgent.py"],
    "Hierarchy": ["HierarchyAgent.py", "HierarchyValidatorAgent.py"],
    "Import": ["ImportAgent.py", "ImportLockAgent.py"],
    "Strategic": ["StrategicRecommendationAgent.py", "StrategicPlannerAgent.py"]
}

def get_file_hash(path: Path):
    if not path.exists(): return None
    return hashlib.md5(path.read_bytes()).hexdigest()

def investigate():
    print("[*] Investigating Potential Overlaps...")
    print(f"[*] Project Root: {PROJECT_ROOT}")
    
    for group_name, filenames in GROUPS.items():
        print(f"\n--- Group: {group_name} ---")
        found_files = []
        for root, _, files in os.walk(PROJECT_ROOT / "agentic_core"):
            for f in files:
                if f in filenames:
                    found_files.append(Path(root) / f)

        if not found_files:
            print("  No files found.")
            continue

        for f_path in found_files:
            f_hash = get_file_hash(f_path)
            rel_path = f_path.relative_to(PROJECT_ROOT)
            print(f"  Found: {rel_path} (MD5: {f_hash[:8]}...)")
            
        # Logic Check: If MD5s match, they are duplicates. 
        # If names are similar but MD5s differ, they are likely intentional variants.
        hashes = [get_file_hash(p) for p in found_files]
        unique_hashes = set(hashes)
        
        if len(unique_hashes) < len(hashes):
            print("  [!] WARNING: Identical MD5 hashes detected in this group. Consolidation required.")
        else:
            print("  [✓] Implementation patterns differ. Likely intentional separation.")

if __name__ == "__main__":
    investigate()
