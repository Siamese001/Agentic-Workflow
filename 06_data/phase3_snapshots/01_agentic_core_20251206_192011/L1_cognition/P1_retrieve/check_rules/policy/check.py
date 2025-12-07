# ==============================================================
# AUTO-HYDRATED BY PHASE 3H
# Donor: C:/Git/Agentic-Workflow/06_data/resume_engine_archive/Agentic-Workflow-10_11/tools/import_check.py
# Review and refactor as needed. Archive copy preserved.
# ==============================================================

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


