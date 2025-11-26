"""
Checks import validity to ensure resume generation system works properly.

Verifies all modules can be imported without errors to maintain
code quality and ensure smooth resume generation functionality.
"""

import pkgutil

print("=== IMPORT CHECK START ===")
for m in pkgutil.walk_packages([""]):
    name = (m.name or "").lstrip("")
    if not name:
        # Skip empty or invalid module names.
        continue
    try:
        __import__(name)
    except Exception as e:
        print("FAILED:", name, "->", type(e).__name__, str(e))
print("=== IMPORT CHECK END ===")


