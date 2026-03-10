"""
Replace `assert True  # no-exception contract` with meaningful assertions.

Strategy: look at the line BEFORE the assert True to understand what was called,
then replace with an assertion on the return value if there is one,
or just remove the assert True (the not-raising itself is the contract,
and Python will naturally propagate any exception).
"""
import pathlib
import re

ROOT = pathlib.Path(".")

# Files with assert True to fix (from our scan, excluding archives)
TARGET_DIRS = [
    "tests/unit",
    "tests/unit_min_deps",
    "tests/governance",
    "tests/integration",
]

def fix_file(path: pathlib.Path) -> bool:
    content = path.read_text(encoding="utf-8")
    
    # Pattern 1: Simple "assert True  # no-exception contract" on its own line
    # Replace with nothing (the not-raising IS the contract - no need for a fake assert)
    # But we need to check context to see if there's a return value we should assert
    
    lines = content.splitlines(keepends=True)
    new_lines = []
    changed = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        
        # Check for assert True patterns
        if re.match(r"(\s*)assert True(?:\s*#.*)?$", stripped):
            indent = re.match(r"(\s*)", line).group(1)
            # Look at previous non-empty line for context
            prev_code = ""
            for j in range(i - 1, max(i - 5, -1), -1):
                prev_stripped = lines[j].strip()
                if prev_stripped and not prev_stripped.startswith("#"):
                    prev_code = lines[j]
                    break
            
            # Check if previous line has an assignment we can assert on
            assign_match = re.match(r"\s+(\w+)\s*=\s*\S", prev_code)
            call_match = re.match(r"\s+(\w+(?:\.\w+)*)\s*\(", prev_code)
            
            if assign_match:
                varname = assign_match.group(1)
                new_line = f"{indent}assert {varname} is not None  # returned value must be non-None\n"
                new_lines.append(new_line)
                changed = True
            else:
                # Just remove the assert True — the absence of exception is the contract
                # But keep a blank line to not collapse structure
                changed = True
                # Don't append this line (skip it)
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
        return True
    return False


# Process all test files
fixed = []
for tdir in TARGET_DIRS:
    for f in (ROOT / tdir).rglob("*.py"):
        content = f.read_text(encoding="utf-8", errors="replace")
        if "assert True  # no-exception contract" in content or \
           "assert True # no-exception contract" in content:
            if fix_file(f):
                fixed.append(str(f))

for f in fixed:
    print(f"Fixed: {f}")
print(f"Total fixed: {len(fixed)}")
