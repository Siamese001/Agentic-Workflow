"""Apply Wave H: fast sort key for Edge sorted() calls.

Edge has order=True with 13 fields — Python generates __lt__ comparing
all fields one by one. With 728k edges, sorted() calls take 25s.

Fix: use key=lambda to build a single compact string from the 5 fields
that actually matter for determinism ordering, bypassing the 13-field
comparison. This eliminates the __lt__ overhead entirely.
"""

import pathlib

TARGET = pathlib.Path(r"c:\Git\Agentic-Workflow\agentic_core\adg\extraction\static_scanner.py")
content = TARGET.read_text(encoding="utf-8")

# Define the fast sort key as a module-level lambda (after Edge class)
# Insert after _EDGE_FIELD_NAMES definition
old_field_names = (
    "# Wave B: pre-compute field names once at module load time (not per call)\n"
    "_EDGE_FIELD_NAMES: frozenset[str] = frozenset(f.name for f in fields(Edge))\n"
)
new_field_names = (
    "# Wave B: pre-compute field names once at module load time (not per call)\n"
    "_EDGE_FIELD_NAMES: frozenset[str] = frozenset(f.name for f in fields(Edge))\n"
    "# Wave H: fast sort key — avoids 13-field dataclass __lt__ comparison on 728k edges\n"
    "_EDGE_SORT_KEY = lambda e: (e.from_name, e.relation_type, e.to_name, e.source_file, e.line_no)  # noqa: E731\n"
)
assert old_field_names in content, "_EDGE_FIELD_NAMES block not found!"
content = content.replace(old_field_names, new_field_names, 1)
print("[OK] 1. _EDGE_SORT_KEY lambda defined")

# Replace sorted(set(all_edges)) with sorted(..., key=_EDGE_SORT_KEY)
old_main_sort = "        result.edges = sorted(set(all_edges))  # S7: sorted for determinism"
new_main_sort = (
    "        result.edges = sorted(set(all_edges), key=_EDGE_SORT_KEY)  # S7: sorted for determinism"
)
assert old_main_sort in content, "main sorted(set(all_edges)) not found!"
content = content.replace(old_main_sort, new_main_sort, 1)
print("[OK] 2. main loop sort uses _EDGE_SORT_KEY")

# Replace interim sort (propagation eligibility temp sort)
old_temp_sort = "        result.edges = sorted(_post_scan_edge_set)  # temp sort for eligibility check"
new_temp_sort = "        result.edges = sorted(_post_scan_edge_set, key=_EDGE_SORT_KEY)  # temp sort for eligibility check"
assert old_temp_sort in content, "temp sort not found!"
content = content.replace(old_temp_sort, new_temp_sort, 1)
print("[OK] 3. eligibility temp sort uses _EDGE_SORT_KEY")

# Replace final post-scan sort
old_final_sort = "        result.edges = sorted(_post_scan_edge_set)"
new_final_sort = "        result.edges = sorted(_post_scan_edge_set, key=_EDGE_SORT_KEY)"
assert old_final_sort in content, "final post-scan sort not found!"
content = content.replace(old_final_sort, new_final_sort, 1)
print("[OK] 4. final post-scan sort uses _EDGE_SORT_KEY")

# Replace in the secondary scan path (line 7421 area)
old_secondary = "        result.edges = sorted(set(all_edges))  # S7"
new_secondary = "        result.edges = sorted(set(all_edges), key=_EDGE_SORT_KEY)  # S7"
if old_secondary in content:
    content = content.replace(old_secondary, new_secondary, 1)
    print("[OK] 5. secondary scan path sort uses _EDGE_SORT_KEY")
else:
    print("[SKIP] 5. secondary sort not found")

# Replace in canonical_edge_text if any sorted() remains
# (should already be fixed by Wave F but check)
remaining = content.count("sorted(self.edges)")
print(f"[INFO] remaining sorted(self.edges) calls: {remaining}")

TARGET.write_text(content, encoding="utf-8")
print(f"\n[DONE] Wave H applied to {TARGET}")

# Verify no plain sorted(set(all_edges)) without key remains
plain_sorts = [i for i in range(len(content)) if content[i:].startswith("sorted(set(all_edges))")]
print(f"Plain sorted(set(all_edges)) without key: {len(plain_sorts)}")
