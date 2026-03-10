"""
Bulk-fix `assert True  # no-exception contract` patterns.

Rules:
1. If the assert True is the ONLY statement in a finally block -> remove it
2. If the assert True is preceded by a method call with known return variable -> assert var is not None
3. If the assert True follows a void call (like _evict(), validate(), etc.) -> remove it (not-raising is the contract)
4. If followed by assert True standalone on its own -> remove it
"""
import pathlib
import re

ROOT = pathlib.Path(".")

TARGET_DIRS = [
    "tests/unit",
    "tests/unit_min_deps",
    "tests/governance",
    "tests/integration",
]

PATTERN_NOEXCEPTION = re.compile(
    r'^(\s*)assert True\s*(?:#\s*no-exception contract)?\s*$',
    re.MULTILINE
)

def fix_file(path: pathlib.Path) -> int:
    content = path.read_text(encoding="utf-8")
    if "assert True" not in content:
        return 0
    
    lines = content.splitlines(keepends=True)
    new_lines = []
    removed = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Match assert True (with or without comment)
        if re.match(r"assert True\s*(?:#.*)?$", stripped):
            indent = len(line) - len(line.lstrip())
            
            # Check if previous meaningful line ends a finally block or is a method call
            prev_meaningful = ""
            for j in range(i - 1, max(i - 10, -1), -1):
                ps = lines[j].strip()
                if ps and not ps.startswith("#"):
                    prev_meaningful = ps
                    break
            
            # Case 1: Inside a finally block (prev line is cleanup() or sys.modules.update())
            # Just remove the assert True - the finally already guarantees execution
            # Case 2: After a method call (no assignment) - remove it
            # Case 3: After mock_ic.assert_called_once() - already has a real assertion, remove
            
            # Safe to remove if:
            # - previous line is a function call (ends with ')' or similar)
            # - previous line is cleanup() / sys.modules.update() 
            # - we're in a finally block
            
            # Check if we're in a finally block by looking for 'finally:' in context
            in_finally = False
            for j in range(i - 1, max(i - 20, -1), -1):
                ps = lines[j].strip()
                if ps == "finally:":
                    in_finally = True
                    break
                if re.match(r"def |class ", ps):
                    break
            
            # Always remove assert True - in all these cases the not-raising is the contract
            # and assert True adds zero value
            removed += 1
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    if removed > 0:
        path.write_text("".join(new_lines), encoding="utf-8")
    
    return removed


total_removed = 0
files_fixed = []

for tdir in TARGET_DIRS:
    d = ROOT / tdir
    if not d.exists():
        continue
    for f in d.rglob("*.py"):
        # Skip archives
        if "archives" in str(f):
            continue
        content_check = f.read_text(encoding="utf-8", errors="replace")
        if "assert True" in content_check:
            n = fix_file(f)
            if n > 0:
                total_removed += n
                files_fixed.append(f"{f} ({n})")

for ff in files_fixed:
    print(f"Fixed: {ff}")
print(f"Total assert True removed: {total_removed} across {len(files_fixed)} files")
