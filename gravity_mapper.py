import os
import re
from pathlib import Path

# The Law of the Land: Define the order of the layers (Lower index = higher authority/bedrock)
# Gravity only flows DOWN (e.g., L3 can import L2, L1, L0)
GRAVITY_LAYERS = [
    "L0_maintenance",
    "utils",
    "runtime",
    "schemas",
    "config",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "semantic_memory",
    "knowledge"
]

class GravityMapper:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.violations = []

    def get_layer_rank(self, path_str):
        for i, layer in enumerate(GRAVITY_LAYERS):
            if layer in path_str:
                return i
        return -1

    def scan_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Get rank of the current file
        current_rank = self.get_layer_rank(str(file_path))
        if current_rank == -1: return

        # Regex to find absolute imports within the agentic_core
        imports = re.findall(r'(?:from|import) agentic_core\.(\w+)', content)
        
        for imp in imports:
            import_rank = self.get_layer_rank(imp)
            
            # THE CORE RULE: If import_rank > current_rank, it's a Gravity Violation
            # (Higher index layers cannot be imported by lower index layers)
            if import_rank > current_rank:
                self.violations.append({
                    "file": file_path.relative_to(self.root),
                    "violator": GRAVITY_LAYERS[current_rank],
                    "target": GRAVITY_LAYERS[import_rank],
                    "line": imp
                })

    def run(self):
        print(f"--- STARTING GRAVITY SCAN: {self.root} ---")
        for py_file in self.root.rglob("*.py"):
            if "agentic_core" in str(py_file):
                self.scan_file(py_file)
        
        self.report()

    def report(self):
        if not self.violations:
            print("✅ 100% Strict Compliance: Gravity is stable.")
            return

        print(f"🚨 DETECTED {len(self.violations)} GRAVITY LEAKS\n")
        print(f"{'FILE':<50} | {'SOURCE':<15} -> {'ILLEGAL TARGET'}")
        print("-" * 90)
        for v in self.violations:
            print(f"{str(v['file']):<50} | {v['violator']:<15} -> {v['target']}")

# Run it
if __name__ == "__main__":
    # Point this to your local Git repo
    mapper = GravityMapper(r"C:/Git/Agentic-Workflow")
    mapper.run()
