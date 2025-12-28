import os
import re
import json
from pathlib import Path

# --- CONFIGURATION ---
MANIFEST_PATH = Path("sovereign_manifest.json")
ROOT_DIR = Path("C:/Git/Agentic-Workflow")
CORE_DIR = ROOT_DIR / "agentic_core"

class SynapseHardener:
    def __init__(self):
        self.manifest = self._load_manifest()
        self.fixes = 0

    def _load_manifest(self):
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)

    def harden_fortress(self):
        print("[*] SYNAPSE HARDENER: Rewriting Synapses...")
        
        for root, dirs, files in os.walk(CORE_DIR):
            for file in files:
                if file.endswith(".py"):
                    self._harden_file(Path(root) / file)
                    
        print(f"\n[OK] HARDENING COMPLETE. {self.fixes} modifications applied.")

    def _harden_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # --- PHASE 1: GRAVITY ENFORCEMENT ---
            # Comment out forbidden downstream imports
            for forbidden in self.manifest['gravity_laws']['forbidden_downstream_imports']:
                # Regex for "from forbidden import..." or "import forbidden"
                pattern = fr"^(from {forbidden}|import {forbidden})"
                if re.search(pattern, content, re.MULTILINE):
                    # We define a replacement function to comment it out
                    content = re.sub(pattern, r"# [GRAVITY BLOCKED] \1", content, flags=re.MULTILINE)

            # --- PHASE 2: ABSOLUTE PATH ENFORCEMENT ---
            # Convert "from . import X" to "from agentic_core.CURRENT_LAYER... import X"
            # This is hard to do perfectly with regex, so we do a brute force "from ." -> "from agentic_core."
            # and let the user/IDE polish the exact path, OR we force a generic fix.
            if "from ." in content:
                content = content.replace("from .", "from agentic_core.")
            if "from .." in content:
                content = content.replace("from ..", "from agentic_core.")

            # --- PHASE 3: TYPE STANDARDIZATION ---
            # Fix SQL-style types (INT -> int)
            for old_type, new_type in self.manifest['type_enforcement'].items():
                # Fix type hints like ": INT" or "-> INT"
                content = re.sub(fr":\s*{old_type}\b", f": {new_type}", content)
                content = re.sub(fr"->\s*{old_type}\b", f"-> {new_type}", content)

            # --- PHASE 4: MISSING IMPORTS INJECTION ---
            # If Dataclass is used but not imported
            if "@dataclass" in content and "from dataclasses import dataclass" not in content:
                content = "from dataclasses import dataclass\n" + content
            
            # If Enum is used but not imported
            if "(Enum)" in content and "from enum import Enum" not in content:
                 content = "from enum import Enum\n" + content

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes += 1
                print(f"  [✓] Hardened: {file_path.relative_to(ROOT_DIR)}")

        except Exception as e:
            print(f"  [X] Failed to harden {file_path.name}: {e}")

if __name__ == "__main__":
    hardener = SynapseHardener()
    hardener.harden_fortress()
