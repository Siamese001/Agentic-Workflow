"""Apply Wave A optimizations to generate_full_adg.py:
A-2: orjson fast-path for report serialization
A-3: Wire _json_dumps into report writing loop
"""

TARGET = r"c:\Git\Agentic-Workflow\tools\generate_full_adg.py"

with open(TARGET, encoding="utf-8") as f:
    content = f.read()

# === Verify orjson not already present ===
if "orjson" in content:
    print("[SKIP] orjson already wired")
else:
    # Insert orjson fast-path after 'import json\nimport os\n'
    old_imports = "import json\nimport os\n"
    new_imports = (
        "import json\nimport os\n"
        "\ntry:\n"
        "    import orjson as _orjson\n"
        "    def _json_dumps(obj: object) -> str:\n"
        '        return _orjson.dumps(obj, option=_orjson.OPT_SORT_KEYS | _orjson.OPT_INDENT_2).decode("utf-8")\n'
        "except ImportError:\n"
        "    _orjson = None  # type: ignore[assignment]\n"
        "    def _json_dumps(obj: object) -> str:\n"
        "        return json.dumps(obj, indent=2, sort_keys=True)\n"
    )
    assert old_imports in content, "import json/os block not found!"
    content = content.replace(old_imports, new_imports, 1)
    print("[OK] A-2: orjson fast-path inserted")

# === Wire _json_dumps into report writing loop ===
old_report_write = (
    "    buffered_writer = BufferedFileWriter(buffer_size=65536)\n"
    "    for filename, report_data in reports:\n"
    "        report_path = reports_dir / filename\n"
    "        json_str = json.dumps(report_data, indent=2, sort_keys=True)\n"
    "        buffered_writer.write_buffered(\n"
    "            str(report_path),\n"
    "            iter([json_str]),\n"
    '            mode="w",\n'
    "        )\n"
    '        print(f"[ADG] Report generated: {filename}")'
)

new_report_write = (
    "    buffered_writer = BufferedFileWriter(buffer_size=65536)\n"
    "    for filename, report_data in reports:\n"
    "        report_path = reports_dir / filename\n"
    "        json_str = _json_dumps(report_data)\n"
    "        buffered_writer.write_buffered(\n"
    "            str(report_path),\n"
    "            iter([json_str]),\n"
    '            mode="w",\n'
    "        )\n"
    '        print(f"[ADG] Report generated: {filename}")'
)

assert old_report_write in content, "Report write loop not found!"
content = content.replace(old_report_write, new_report_write, 1)
print("[OK] A-3: _json_dumps wired into report writing loop")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(content)

print(f"[DONE] Wave A applied. File size: {len(content)} bytes")

# Verify
with open(TARGET, encoding="utf-8") as f:
    verify = f.read()
print(f"orjson in file: {'orjson' in verify}")
print(f"_json_dumps in file: {'_json_dumps' in verify}")
