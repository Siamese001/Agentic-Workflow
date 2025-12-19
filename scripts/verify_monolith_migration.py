import ast
import os

# CONFIGURATION
MONOLITH_PATH = "scripts/canon_validator_agentic.py"  # Correct path
CORE_DIR = "agentic_core"

# DNA MARKERS: Specific logic signatures that MUST exist in the new core
REQUIRED_SIGNATURES = {
    "classes": {
        "SwarmScheduler", "ValidationContext", "Historian", 
        "ArchitectureGovernor", "DependencySentinel", "SafetyInspector", 
        "ConcurrencyGuardian", "TestPilot", "ToolsmithAgent", 
        "StrategicPlanner", "ReflectionAgent", "GitAgent", 
        "BenchmarkingAgent", "MemoryLeakDetector", "DeadlockDetector",
        "RedSentinel", "TruthKeeper", "TheCartographer"
    },
    "methods": {
        "run_mission", "_calculate_mccabe", "_socratic_verify", 
        "broadcast_reasoning", "debate_failure", "_generate_git_metadata",
        "acquire_lock", "_internalize_trace", "search_memory",
        "_check_nesting_depth", "check_file_consistency"
    },
    "constants": {
        "MAX_COMPLEXITY", "ALLOWED_ROOT_FILES", "FEW_SHOT_STRATEGIC",
        "FEW_SHOT_SHERLOCK", "FEW_SHOT_CONCURRENCY"
    }
}

class DNAExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = set()
        self.methods = set()
        self.constants = set()

    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.methods.add(node.name)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.methods.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                self.constants.add(target.id)
        self.generic_visit(node)

def analyze_file(path: str) -> DNAExtractor:
    extractor = DNAExtractor()
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            extractor.visit(tree)
    except Exception as e:
        print(f"⚠️ Could not parse {path}: {e}")
    return extractor

def analyze_directory(directory: str) -> DNAExtractor:
    combined_extractor = DNAExtractor()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                file_extractor = analyze_file(path)
                combined_extractor.classes.update(file_extractor.classes)
                combined_extractor.methods.update(file_extractor.methods)
                combined_extractor.constants.update(file_extractor.constants)
    return combined_extractor

def main():
    print(f"🔍 STARTING FORENSIC AUDIT...")
    print(f"   Monolith: {MONOLITH_PATH} (optional)")
    print(f"   Target Core: {CORE_DIR}/")
    
    # Skip monolith check - just verify core has required signatures
    if not os.path.exists(MONOLITH_PATH):
        print(f"⚠️  Monolith file not found - proceeding with core verification only")

    # 1. Extract Core DNA
    print("\n🧬 Sequencing Agentic Core DNA...")
    core_dna = analyze_directory(CORE_DIR)
    print(f"   Found {len(core_dna.classes)} classes, {len(core_dna.methods)} methods.")

    # 2. Verify Markers
    print("\n🛡️  Verifying Critical Systems...")
    missing_items = {"classes": [], "methods": [], "constants": []}
    score = 0
    total_checks = 0

    # Check Classes
    for cls in REQUIRED_SIGNATURES["classes"]:
        total_checks += 1
        if cls in core_dna.classes:
            print(f"   ✅ Class: {cls}")
            score += 1
        else:
            print(f"   ❌ MISSING CLASS: {cls}")
            missing_items["classes"].append(cls)

    # Check Methods
    for method in REQUIRED_SIGNATURES["methods"]:
        total_checks += 1
        if method in core_dna.methods:
            print(f"   ✅ Method: {method}")
            score += 1
        else:
            print(f"   ❌ MISSING METHOD: {method}")
            missing_items["methods"].append(method)

    # Check Constants
    for const in REQUIRED_SIGNATURES["constants"]:
        total_checks += 1
        if const in core_dna.constants:
            print(f"   ✅ Constant: {const}")
            score += 1
        else:
            print(f"   ❌ MISSING CONSTANT: {const}")
            missing_items["constants"].append(const)

    # 3. Final Verdict
    completeness = (score / total_checks) * 100
    print(f"\n{'='*60}")
    print(f"FINAL MIGRATION STATUS: {completeness:.1f}% COMPLETE")
    print(f"{'='*60}")

    if completeness == 100:
        print("\n🎉 MIGRATION SUCCESSFUL. The Monolith is obsolete.")
        print("   Recommended Action: Move canon_validator_agentic.py to archives/")
    else:
        print("\n⚠️  MIGRATION INCOMPLETE. Do not delete the monolith.")
        print("   Missing Components:")
        for category, items in missing_items.items():
            if items:
                print(f"   - {category.upper()}: {', '.join(items)}")

if __name__ == "__main__":
    main()
