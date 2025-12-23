import os
import ast
import json
import sys
from pathlib import Path
from collections import defaultdict

# --- CONFIGURATION ---
MANIFEST_PATH = Path("sovereign_manifest.json")
ROOT_DIR = Path("C:/Git/Agentic-Workflow")
CORE_DIR = ROOT_DIR / "agentic_core"

class SovereignViolation:
    def __init__(self, file_path, line_no, type_, message, severity="ERROR"):
        self.file_path = file_path
        self.line_no = line_no
        self.type = type_
        self.message = message
        self.severity = severity

    def __repr__(self):
        return f"[{self.severity}] {self.file_path.name}:{self.line_no} - {self.type}: {self.message}"

class StaticSentinel:
    def __init__(self):
        self.manifest = self._load_manifest()
        self.violations = []
        self.stats = {"scanned": 0, "violations": 0, "gravity_breaches": 0}

    def _load_manifest(self):
        if not MANIFEST_PATH.exists():
            print(f"[!] FATAL: Manifest not found at {MANIFEST_PATH}")
            sys.exit(1)
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)

    def scan_fortress(self):
        """Main execution loop."""
        print(f"[*] SENTINEL V3: Scanning Sovereign Domain ({self.manifest['sovereign_domain']})...")
        print("    Mode: STATIC AST ANALYSIS (No Execution)")
        
        # 1. Structural Scan (Depth & Naming)
        files_to_scan = []
        for root, dirs, files in os.walk(CORE_DIR):
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    self.stats["scanned"] += 1
                    
                    # Structural Check
                    if self._check_structure(full_path):
                        files_to_scan.append(full_path)

        # 2. Content Scan (AST Import Analysis)
        print(f"[*] AST PARSING {len(files_to_scan)} files for Gravity Violations...")
        for file_path in files_to_scan:
            self._analyze_ast(file_path)

        # 3. Report
        self._generate_report()

    def _check_structure(self, file_path):
        """Enforces Depth-4: agentic_core / Layer / Stage / File.py"""
        rel_path = file_path.relative_to(CORE_DIR)
        parts = rel_path.parts

        # Skip root files like __init__.py in agentic_core
        if len(parts) == 1: 
            return True

        # Check Depth (Should be exactly 3 parts: Layer/Stage/File)
        # agentic_core is root, so relative parts should be 3.
        if len(parts) != 3:
            self.violations.append(SovereignViolation(
                file_path, 0, "DEPTH_VIOLATION", 
                f"File depth is {len(parts)+1} (Required: {self.manifest['allowed_depth']}). Path: {rel_path}"
            ))
            return False # Don't AST scan structural failures

        layer, stage, filename = parts
        
        # Validate Layer
        if layer not in self.manifest['layers']:
            self.violations.append(SovereignViolation(
                file_path, 0, "ILLEGAL_LAYER", f"Layer '{layer}' is not in Manifest."
            ))

        # Validate Stage
        if stage not in self.manifest['stages']:
             self.violations.append(SovereignViolation(
                file_path, 0, "ILLEGAL_STAGE", f"Stage '{stage}' is not in Manifest."
            ))
            
        return True

    def _analyze_ast(self, file_path):
        """Parses Python AST to find forbidden imports without running code."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                # Check ImportNodes
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._check_import_node(node, file_path)
                    
        except SyntaxError as e:
            self.violations.append(SovereignViolation(
                file_path, e.lineno, "SYNTAX_ERROR", f"File failed to parse: {e.msg}"
            ))
        except Exception as e:
            self.violations.append(SovereignViolation(
                file_path, 0, "AST_FAILURE", str(e)
            ))

    def _check_import_node(self, node, file_path):
        """Validates a single import node against Gravity Laws."""
        laws = self.manifest['gravity_laws']
        
        # 1. Check for Relative Imports (from . import X)
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            if not laws['allow_relative_imports']:
                self.violations.append(SovereignViolation(
                    file_path, node.lineno, "GRAVITY_REL_IMPORT", 
                    "Relative imports are forbidden. Use absolute 'agentic_core...' path."
                ))

        # 2. Check for Downstream Imports (Gravity Leak)
        modules = []
        if isinstance(node, ast.Import):
            modules = [n.name for n in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module]

        for mod in modules:
            # Check prohibited prefixes
            for forbidden in laws['forbidden_downstream_imports']:
                if mod.startswith(forbidden):
                    self.violations.append(SovereignViolation(
                        file_path, node.lineno, "GRAVITY_LEAK", 
                        f"Core cannot import downstream domain: '{mod}'"
                    ))
                    self.stats["gravity_breaches"] += 1

            # Check Circular Self-Reference (agentic_core importing agentic_core)
            # Only flagged if the file is inside agentic_core (which it is)
            if mod.startswith(self.manifest['sovereign_domain']):
                 # We allow absolute imports, but we check if it's importing itself logically?
                 # Actually, absolute imports ARE allowed in V3. 
                 # We only ban downstream.
                 pass

    def _generate_report(self):
        print(f"\n[*] SCAN COMPLETE. Processed {self.stats['scanned']} files.")
        print(f"    Violations Found: {len(self.violations)}")
        print(f"    Gravity Breaches: {self.stats['gravity_breaches']}")
        
        if not self.violations:
            print("\n[SUCCESS] THE FORTRESS IS SECURE. 0 Violations.")
            sys.exit(0)
            
        print("\n[!] VIOLATION REPORT:")
        # Group by type for readability
        grouped = defaultdict(list)
        for v in self.violations:
            grouped[v.type].append(v)
            
        for v_type, v_list in grouped.items():
            print(f"\n--- {v_type} ({len(v_list)}) ---")
            for v in v_list[:5]: # Show top 5
                print(f"  {v.file_path.name}:{v.line_no} -> {v.message}")
            if len(v_list) > 5:
                print(f"  ... and {len(v_list) - 5} more.")

        print("\n[ACTION REQUIRED] Run 'synapse_hardener.py' to surgically fix these.")
        sys.exit(1)

if __name__ == "__main__":
    sentinel = StaticSentinel()
    sentinel.scan_fortress()
