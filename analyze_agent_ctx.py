"""Analyze all agents for ctx handling patterns."""
import re
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_agent_init(file_path: Path) -> Dict:
    """Analyze an agent file for ctx handling."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except:
        return {"error": "Could not read file"}
    
    result = {
        "file": str(file_path),
        "name": file_path.stem,
        "layer": "",
        "has_init": False,
        "ctx_pattern": "none",
        "ctx_optional": None,
        "inherits_from": "",
        "is_base_class": False,
        "is_testing_agent": False,
        "is_computation_agent": False,
        "recommendation": "",
        "needs_change": False
    }
    
    # Determine layer
    if "L0_maintenance" in str(file_path):
        result["layer"] = "L0"
    elif "L1_cognition" in str(file_path):
        result["layer"] = "L1"
    elif "L2_execution" in str(file_path):
        result["layer"] = "L2"
    elif "L3_orchestration" in str(file_path):
        result["layer"] = "L3"
    elif "L4_state" in str(file_path):
        result["layer"] = "L4"
    elif "L5_safety" in str(file_path):
        result["layer"] = "L5"
    elif "observability" in str(file_path):
        result["layer"] = "observability"
    elif "utils" in str(file_path):
        result["layer"] = "utils"
    elif "apps_" in str(file_path):
        result["layer"] = "apps"
    
    # Check if base class
    if "Base" in file_path.stem or "Canon" in file_path.stem:
        result["is_base_class"] = True
    
    # Check if testing agent
    if "Test" in file_path.stem or "test" in file_path.stem.lower():
        result["is_testing_agent"] = True
    
    # Check inheritance
    class_match = re.search(r'class\s+\w+\s*\(([^)]+)\)', content)
    if class_match:
        result["inherits_from"] = class_match.group(1).strip()
    
    # Find __init__ method
    init_match = re.search(r'def __init__\s*\(([^)]*)\)', content, re.MULTILINE)
    if init_match:
        result["has_init"] = True
        init_params = init_match.group(1)
        
        # Analyze ctx parameter
        if 'ctx' in init_params:
            if 'ctx=None' in init_params or 'ctx = None' in init_params:
                result["ctx_pattern"] = "optional"
                result["ctx_optional"] = True
            elif 'ctx:' in init_params and '= None' in init_params:
                result["ctx_pattern"] = "optional_typed"
                result["ctx_optional"] = True
            elif 'ctx' in init_params:
                result["ctx_pattern"] = "mandatory"
                result["ctx_optional"] = False
        else:
            result["ctx_pattern"] = "none"
    
    # Determine recommendation
    if result["is_base_class"]:
        result["recommendation"] = "BASE_CLASS - ctx mandatory in base"
        result["needs_change"] = result["ctx_optional"] == True
    elif result["is_testing_agent"]:
        result["recommendation"] = "TESTING - ctx optional OK"
        result["needs_change"] = False
    elif result["layer"] in ["L5", "L4", "L3", "L2"]:
        result["recommendation"] = "SOVEREIGN - ctx mandatory"
        result["needs_change"] = result["ctx_optional"] == True
    elif result["layer"] in ["L1", "L0"]:
        result["recommendation"] = "PRODUCTION - ctx mandatory"
        result["needs_change"] = result["ctx_optional"] == True
    elif result["layer"] in ["utils", "observability"]:
        result["recommendation"] = "UTILITY - ctx optional OK"
        result["needs_change"] = False
    else:
        result["recommendation"] = "REVIEW NEEDED"
        result["needs_change"] = False
    
    return result


def main():
    agents = []
    
    # Find all agent files
    for pattern in ["*Agent*.py", "*_agent*.py"]:
        for path in Path("agentic_core").rglob(pattern):
            agents.append(analyze_agent_init(path))
        for path in Path("apps_rg").rglob(pattern):
            agents.append(analyze_agent_init(path))
        for path in Path("apps_lic").rglob(pattern):
            agents.append(analyze_agent_init(path))
        for path in Path("apps_shared").rglob(pattern):
            agents.append(analyze_agent_init(path))
    
    # Remove duplicates
    seen = set()
    unique_agents = []
    for a in agents:
        if a["file"] not in seen:
            seen.add(a["file"])
            unique_agents.append(a)
    
    # Sort by layer
    layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "observability": 6, "utils": 7, "apps": 8, "": 9}
    unique_agents.sort(key=lambda x: (layer_order.get(x["layer"], 9), x["name"]))
    
    # Print summary
    print("=" * 100)
    print("AGENT CTX ANALYSIS REPORT")
    print("=" * 100)
    print()
    
    needs_change = [a for a in unique_agents if a["needs_change"]]
    no_change = [a for a in unique_agents if not a["needs_change"]]
    
    print(f"Total agents found: {len(unique_agents)}")
    print(f"Agents needing change (ctx should be mandatory): {len(needs_change)}")
    print(f"Agents OK (no change needed): {len(no_change)}")
    print()
    
    print("=" * 100)
    print("AGENTS NEEDING CHANGE (ctx should be mandatory)")
    print("=" * 100)
    for a in needs_change:
        print(f"  [{a['layer']}] {a['name']}")
        print(f"       Pattern: {a['ctx_pattern']} | Inherits: {a['inherits_from']}")
        print(f"       Recommendation: {a['recommendation']}")
        print()
    
    print("=" * 100)
    print("AGENTS OK (no change needed)")
    print("=" * 100)
    for a in no_change:
        print(f"  [{a['layer']}] {a['name']} - {a['recommendation']}")
    
    # Return data for further processing
    return unique_agents


if __name__ == "__main__":
    agents = main()
