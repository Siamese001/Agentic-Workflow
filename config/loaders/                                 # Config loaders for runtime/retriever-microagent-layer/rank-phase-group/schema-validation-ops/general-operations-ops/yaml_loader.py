import os
import re
import yaml

# -------------------------------------------------------------
# CONFIG: update if your folder structure markdowns move
# -------------------------------------------------------------
MD_DIR = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic Folder Structure"
OUTPUT_DIR = os.path.join(MD_DIR, "yaml")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Utility: clean markdown tree lines
# -------------------------------------------------------------
def extract_tree_lines(md_text):
    """
    Extracts lines that represent folder trees from markdown.
    Looks for hierarchical tree content before the "### Directory Structure" heading.
    """
    # Split on the "### Directory Structure" heading and take content before it
    parts = md_text.split("### Directory Structure")
    if parts:
        content_before_heading = parts[0]
    else:
        content_before_heading = md_text

    # Extract lines with tree characters from the content before the heading
    lines = []
    for line in content_before_heading.splitlines():
        if any(x in line for x in ["â”œ", "â”‚", "â””"]) and line.strip():
            lines.append(line.rstrip())
    
    return lines
# -------------------------------------------------------------
# Convert ASCII tree â†’ nested dict structure
# -------------------------------------------------------------
def tree_to_dict(tree_lines):
    """
    Parses tree-like indentation into nested dicts:
      folder:
        subfolder:
          file: null
    """
    root = {}
    stack = [(0, root)]
    print(f"DEBUG: Processing {len(tree_lines)} tree lines")
    for i, raw_line in enumerate(tree_lines):
        print(f"DEBUG: Line {i}: '{raw_line}'")

        line = raw_line.strip()
        if not line:
            continue

        # Remove tree characters (â”œâ”€â”€, â””â”€â”€, â”‚) and get clean name
        cleaned = re.sub(r"[â”‚â”œâ””â”€]+", "", line).strip()
        print(f"DEBUG: Cleaned line: '{cleaned}'")

        if not cleaned:
            continue

        # Calculate indentation level by counting tree structure depth
        # Count occurrences of tree indicators to determine nesting level
        tree_prefix = raw_line[:len(raw_line) - len(line)]  # Get leading whitespace/tree chars
        # Count tree character groups (â”‚   â”œâ”€â”€ = level 1, â”‚   â”‚   â”œâ”€â”€ = level 2, etc.)
        indent_level = 0
        if "â”‚" in raw_line or "â”œ" in raw_line or "â””" in raw_line:
            # Each "â”‚   " or "    " group represents one level
            indent_level = (len(tree_prefix) // 4)

        print(f"DEBUG: Indent level: {indent_level}")

        # File or folder name
        name = cleaned

        # Descend stack to correct parent
        while stack and indent_level <= stack[-1][0]:
            stack.pop()

        print(f"DEBUG: Stack length after pop: {len(stack)}")

        # Ensure stack is never empty - keep root as fallback
        if not stack:
            stack = [(0, root)]
            print("DEBUG: Stack was empty, reset to root")

        parent = stack[-1][1]
        if "." in name:   # treat anything with a dot as a file
            parent[name] = None
            print(f"DEBUG: Added file: {name}")
        else:
            parent[name] = {}
            stack.append((indent_level, parent[name]))
            print(f"DEBUG: Added folder: {name}")

    return root


# -------------------------------------------------------------
# MAIN LOOP â€” process all 9 markdown files
# -------------------------------------------------------------
for md_file in os.listdir(MD_DIR):
    if not md_file.lower().endswith(".md"):
        continue

    md_path = os.path.join(MD_DIR, md_file)
    basename = os.path.splitext(md_file)[0]

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    print(f"Parsing: {md_file}")

    tree_lines = extract_tree_lines(md_text)
    print(f"DEBUG: Extracted {len(tree_lines)} tree lines for {md_file}:")
    for i, line in enumerate(tree_lines[:5]):  # Show first 5 lines
        print(f"  {i}: '{line}'")
    if len(tree_lines) > 5:
        print(f"  ... and {len(tree_lines) - 5} more lines")
    tree_dict = tree_to_dict(tree_lines)

    yaml_path = os.path.join(OUTPUT_DIR, f"{basename}.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(tree_dict, f, sort_keys=False, allow_unicode=True)

    print(f" â†’ YAML written to: {yaml_path}")

print("\nDONE: Converted all markdown file trees into YAML.")
