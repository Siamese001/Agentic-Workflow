"""
file: tests/maintenance/fix_duplicate_detector_imports.py
description: Finds and updates all references to DuplicateCodeDetectorAgent
             from its old apps_lic path to its new apps_shared path.
"""

import os
import re
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
OLD_IMPORT = r"from apps_lic\.engines\.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent"
NEW_IMPORT = "from apps_shared.utils.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent"

# Alternative import patterns (e.g., if just importing the module)
OLD_MODULE = r"import apps_lic\.engines\.DuplicateCodeDetectorAgent"
NEW_MODULE = "import apps_shared.utils.DuplicateCodeDetectorAgent"

def fix_imports():
    print("--- Starting Global Import Repair for DuplicateCodeDetectorAgent ---")
    count = 0

    # We scan everything EXCEPT the archives and the agent itself
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip quarantined and irrelevant dirs
        if any(x in root for x in ["archives", ".git", "__pycache__", "venv"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file

                # Skip the agent itself at its new location
                if "apps_shared/utils/DuplicateCodeDetectorAgent.py" in str(file_path).replace("\\", "/"):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    if re.search(OLD_IMPORT, content) or re.search(OLD_MODULE, content):
                        new_content = re.sub(OLD_IMPORT, NEW_IMPORT, content)
                        new_content = re.sub(OLD_MODULE, NEW_MODULE, new_content)

                        file_path.write_text(new_content, encoding='utf-8')
                        print(f"✅ Repaired: {file_path}")
                        count += 1
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")

    print(f"--- Finished. Total files repaired: {count} ---")

if __name__ == "__main__":
    fix_imports()
