"""Apply Wave F: eliminate redundant sort in canonical_edge_text.

canonical_edge_text() calls sorted(self.edges) but self.edges is
already assigned via sorted(set(all_edges)) — the sort is redundant.
Removing it eliminates ~27s of CPU time (14,728 sorted() calls measured).
"""

import pathlib

TARGET = pathlib.Path(r"c:\Git\Agentic-Workflow\agentic_core\adg\extraction\static_scanner.py")
content = TARGET.read_text(encoding="utf-8")

# Fix: remove the inner sort — self.edges is already sorted at assignment time
old_canonical = (
    "        lines = []\n"
    "        for e in sorted(self.edges):  # S7: sort before digest\n"
    "            lines.append(\n"
    '                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"\n'
    '                f"|{e.source_file}|{e.line_no}|{e.symbol}"\n'
    "            )\n"
    '        return "\\n".join(lines)'
)
new_canonical = (
    "        lines = []\n"
    "        for e in self.edges:  # S7: edges already sorted at assignment (sorted(set(...)))\n"
    "            lines.append(\n"
    '                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"\n'
    '                f"|{e.source_file}|{e.line_no}|{e.symbol}"\n'
    "            )\n"
    '        return "\\n".join(lines)'
)

assert old_canonical in content, "canonical_edge_text sorted loop not found!"
content = content.replace(old_canonical, new_canonical, 1)
print("[OK] Wave F: removed redundant sorted() from canonical_edge_text")

TARGET.write_text(content, encoding="utf-8")
print(f"[DONE] {TARGET}")
