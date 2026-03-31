#!/usr/bin/env python3
"""
Script to fix cost-budget-ops nesting issues in unified_structure_subatomic.yaml
Moves cost-budget-ops from being nested under constraint-check-ops to be a direct child of safety-phase-group
"""

def fix_yaml_file():
    file_path = "unified_structure_subatomic.yaml"

    # Read the file
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a cost-budget-ops line that needs fixing
        if line.strip().startswith("cost-budget-ops:"):
            # Check indentation (10 spaces = nested under constraint-check-ops, 8 spaces = correct)
            if line.startswith("          "):  # 10 spaces - incorrectly nested
                # This cost-budget-ops needs to be moved up one level
                # Remove 2 spaces from indentation to make it sibling of constraint-check-ops
                fixed_line = "        " + line[10:]  # Change from 10 to 8 spaces
                fixed_lines.append(fixed_line)

                # Also fix all subsequent lines in this cost-budget-ops block
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() == "":
                        fixed_lines.append(next_line)  # Keep empty lines
                        i += 1
                        continue

                    # If we encounter another top-level key (8 spaces or less), we're done with this block
                    if next_line.startswith("        ") and not next_line.startswith("          "):
                        break

                    # Fix indentation for all lines in this block (remove 2 spaces)
                    if next_line.startswith("            "):  # 12 spaces -> 10 spaces
                        fixed_lines.append("          " + next_line[12:])
                    elif next_line.startswith("              "):  # 14 spaces -> 12 spaces
                        fixed_lines.append("            " + next_line[14:])
                    elif next_line.startswith("                "):  # 16 spaces -> 14 spaces
                        fixed_lines.append("              " + next_line[16:])
                    else:
                        fixed_lines.append(next_line)
                    i += 1
                continue  # Skip the i += 1 at the end since we already advanced

        fixed_lines.append(line)
        i += 1

    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print(f"Fixed YAML file: {file_path}")

if __name__ == "__main__":
    fix_yaml_file()
