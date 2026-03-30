"""Apply Wave E: orjson fast-path in scan_cache.py for save() and load().

json.dumps of 728k-edge cache = 49.7s (measured).
orjson is 7.5x faster = expected ~6-7s after.
"""

import pathlib

TARGET = pathlib.Path(r"c:\Git\Agentic-Workflow\agentic_core\adg\extraction\scan_cache.py")
content = TARGET.read_text(encoding="utf-8")

# === 1. Add orjson import after 'import json' ===
old_import = "import json\nimport logging"
new_import = (
    "import json\nimport logging\n\n"
    "try:\n"
    "    import orjson as _orjson\n"
    "    _ORJSON_AVAILABLE = True\n"
    "except ImportError:\n"
    "    _orjson = None  # type: ignore[assignment]\n"
    "    _ORJSON_AVAILABLE = False"
)
assert old_import in content, "import json/logging block not found"
content = content.replace(old_import, new_import, 1)
print("[OK] 1. orjson import block added")

# === 2. Replace load() json.loads with orjson fast path ===
old_load = '        try:\n            raw = json.loads(cache_path.read_text(encoding="utf-8"))\n'
new_load = (
    "        try:\n"
    "            _raw_bytes = cache_path.read_bytes()\n"
    '            raw = _orjson.loads(_raw_bytes) if _ORJSON_AVAILABLE else json.loads(_raw_bytes.decode("utf-8"))\n'
)
assert old_load in content, "load() json.loads block not found"
content = content.replace(old_load, new_load, 1)
print("[OK] 2. load() uses orjson.loads")

# === 3. Replace save() json.dumps with orjson fast path ===
old_save = (
    "        try:\n"
    '            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n'
    "            tmp.replace(cache_path)\n"
)
new_save = (
    "        try:\n"
    "            if _ORJSON_AVAILABLE:\n"
    "                tmp.write_bytes(_orjson.dumps(payload, option=_orjson.OPT_INDENT_2))\n"
    "            else:\n"
    '                tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n'
    "            tmp.replace(cache_path)\n"
)
assert old_save in content, "save() json.dumps block not found"
content = content.replace(old_save, new_save, 1)
print("[OK] 3. save() uses orjson.dumps")

TARGET.write_text(content, encoding="utf-8")
print(f"\n[DONE] Wave E applied to {TARGET}")

# Verify
verify = TARGET.read_text(encoding="utf-8")
print(f"orjson in file: {'orjson' in verify}")
print(f"_ORJSON_AVAILABLE in file: {'_ORJSON_AVAILABLE' in verify}")
