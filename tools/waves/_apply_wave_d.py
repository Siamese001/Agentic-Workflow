"""Apply Wave D: lru_cache on module_path_to_layer in schema_util.py and schema.py.

The profiler shows _emit_layer_violation_edges takes 12.35s because
module_path_to_layer is called ~1.5M times with repeated string prefix scans.
lru_cache reduces this to O(1) after the first call per unique path.
"""

import pathlib

ROOT = pathlib.Path(r"c:\Git\Agentic-Workflow")


def patch_file(path: pathlib.Path) -> bool:
    content = path.read_text(encoding="utf-8")
    label = path.name

    # Already patched?
    if "lru_cache" in content and "module_path_to_layer" in content:
        # Check if lru_cache is already on module_path_to_layer
        idx = content.find("def module_path_to_layer(")
        if idx > 0:
            before = content[max(0, idx - 60) : idx]
            if "lru_cache" in before:
                print(f"[SKIP] {label}: already has lru_cache on module_path_to_layer")
                return False

    # 1. Add functools import if not present
    if "from functools import" in content:
        if "lru_cache" not in content.split("from functools import")[1].split("\n")[0]:
            old_import = content[content.find("from functools import") :].split("\n")[0]
            new_import = old_import.rstrip() + ", lru_cache"
            content = content.replace(old_import, new_import, 1)
            print(f"[OK] {label}: added lru_cache to existing functools import")
    elif "import functools" in content:
        # Already have functools, just use functools.lru_cache
        pass  # handled below by decorator form
    else:
        # Add fresh import after the docstring / first block of imports
        # Find a safe insertion point — after first stdlib import
        import_idx = content.find("\nimport ")
        if import_idx < 0:
            import_idx = content.find("\nfrom ")
        if import_idx >= 0:
            content = content[:import_idx] + "\nfrom functools import lru_cache" + content[import_idx:]
            print(f"[OK] {label}: added 'from functools import lru_cache'")

    # 2. Add @lru_cache(maxsize=8192) decorator before def module_path_to_layer
    old_def = "def module_path_to_layer(rel_path: str) -> str:"
    new_def = "@lru_cache(maxsize=8192)\ndef module_path_to_layer(rel_path: str) -> str:"

    if old_def not in content:
        print(f"[WARN] {label}: module_path_to_layer def not found, skipping")
        return False

    if "@lru_cache" in content and "module_path_to_layer" in content:
        idx = content.find("def module_path_to_layer(")
        before = content[max(0, idx - 60) : idx]
        if "@lru_cache" in before:
            print(f"[SKIP] {label}: lru_cache already on module_path_to_layer")
            return False

    content = content.replace(old_def, new_def, 1)
    print(f"[OK] {label}: @lru_cache(maxsize=8192) added to module_path_to_layer")

    path.write_text(content, encoding="utf-8")
    return True


# Patch both files
for rel in ["agentic_core/adg/schema_util.py", "agentic_core/adg/schema.py"]:
    p = ROOT / rel
    if p.exists():
        patch_file(p)
    else:
        print(f"[SKIP] {rel}: file not found")

print("\n[DONE] Wave D applied")

# Quick sanity check
for rel in ["agentic_core/adg/schema_util.py", "agentic_core/adg/schema.py"]:
    p = ROOT / rel
    if p.exists():
        content = p.read_text(encoding="utf-8")
        has_cache = "@lru_cache" in content
        print(f"  {rel}: lru_cache={has_cache}")
