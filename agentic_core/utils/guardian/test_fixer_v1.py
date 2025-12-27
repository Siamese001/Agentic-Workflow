"""
Phase 1: Test Sovereignty Syntax Repair
Target: Bulk-repair indentation and markdown fences.
"""
import os
import pathlib

def repair_test_syntax(test_dir="tests"):
    files_fixed = 0
    for path in pathlib.Path(test_dir).rglob("*.py"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            new_lines = []
            changed = False

            # 1. Strip Markdown Fences
            if lines and lines[0].startswith("```"):
                lines = [l for l in lines if not l.startswith("```")]
                changed = True

            # 2. Repair Except Indentation
            i = 0
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)
                
                # If line is an except block and the next line isn't indented
                if line.strip().startswith("except ") and line.strip().endswith(":"):
                    if i + 1 < len(lines):
                        next_line = lines[i+1]
                        # Check if next line is 'pass' or code at wrong indentation
                        if next_line.strip() and not next_line.startswith((" ", "\t")):
                            # Calculate proper indentation (match except line + 4 spaces)
                            indent = len(line) - len(line.lstrip())
                            proper_indent = " " * (indent + 4)
                            
                            # Fix the next line and any following lines at wrong indent
                            j = i + 1
                            while j < len(lines):
                                following_line = lines[j]
                                if following_line.strip() and not following_line.startswith((" ", "\t")):
                                    # This line needs to be indented
                                    new_lines.append(proper_indent + following_line.lstrip())
                                    changed = True
                                    j += 1
                                else:
                                    # Properly indented or empty, stop fixing
                                    break
                            i = j - 1  # Skip the lines we just fixed
                
                i += 1

            if changed:
                path.write_text("\n".join(new_lines), encoding="utf-8")
                files_fixed += 1
                print(f"[FIXED] Syntax repair in {path}")
        except Exception as e:
            print(f"[ERROR] Failed to process {path}: {e}")
            
    return files_fixed

if __name__ == "__main__":
    count = repair_test_syntax()
    print(f"\nTotal files repaired: {count}")
