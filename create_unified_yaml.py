import os
import yaml

# -------------------------------------------------------------
# CONFIG: paths for input YAML files and output unified file
# -------------------------------------------------------------
YAML_DIR = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic Folder Structure"
OUTPUT_FILE = os.path.join(YAML_DIR, "unified_structure.yaml")

# -------------------------------------------------------------
# Load all YAML files and merge into unified structure
# -------------------------------------------------------------
def create_unified_yaml():
    """
    Reads all individual YAML files and creates a unified structure
    """
    unified_structure = {}
    
    print("Creating unified YAML structure...")
    # Get all YAML files in the directory
    yaml_files = [f for f in os.listdir(YAML_DIR) if f.endswith('.yaml') and f != 'unified_structure.yaml']
    
    for yaml_file in sorted(yaml_files):
        yaml_path = os.path.join(YAML_DIR, yaml_file)

        print(f"Loading: {yaml_file}")

        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)

        # Use the filename (without .yaml) as the top-level key
        base_name = os.path.splitext(yaml_file)[0]
        unified_structure[base_name] = content

    # Write unified structure to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(unified_structure, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    print(f"\nUnified YAML written to: {OUTPUT_FILE}")
    print(f"Total sections: {len(unified_structure)}")
    
    return unified_structure

# -------------------------------------------------------------
# Run the unified YAML creation
# -------------------------------------------------------------
if __name__ == "__main__":
    unified = create_unified_yaml()
    
    # Print summary of what was included
    print("\nSections included:")
    for section in unified.keys():
        print(f"  - {section}")
