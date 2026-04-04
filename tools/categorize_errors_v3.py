#!/usr/bin/env python3
"""Categorize collection errors by trying to import each test module."""

import importlib
import re
from collections import Counter
from pathlib import Path

# Directly try importing each test file as a module to see what fails
tests_dir = Path("tests/unit/agentic_core")
categories = Counter()
cat_samples = {}
total = 0
errors = 0

for p in sorted(tests_dir.rglob("test_*.py")):
    total += 1
    fp = str(p).replace("\\", "/")

    try:
        content = p.read_text("utf-8")
    except Exception:
        categories["unreadable"] += 1
        continue

    # Check if it has top-level from...import that isn't in a try/except
    has_direct_import = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("from agentic_core") and "import" in stripped:
            has_direct_import = True
            break

    # Check if it uses our fixture pattern
    is_enhanced = "Behavioral contract tests for" in content and "@pytest.fixture" in content

    # Try to compile the test file itself
    try:
        compile(content, fp, "exec")
    except SyntaxError as e:
        categories["test_file_syntax_error"] += 1
        cat_samples.setdefault("test_file_syntax_error", []).append(fp)
        errors += 1
        continue
    except Exception:
        pass

    # If it has direct imports (not via fixture), try importing the module
    if has_direct_import and not is_enhanced:
        # Extract the module being imported
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("from agentic_core") and "import" in stripped:
                m = re.match(r"from\s+([\w.]+)\s+import", stripped)
                if m:
                    mod_name = m.group(1)
                    try:
                        importlib.import_module(mod_name)
                    except IndentationError:
                        categories["source_IndentationError"] += 1
                        cat_samples.setdefault("source_IndentationError", []).append((fp, mod_name))
                        errors += 1
                        break
                    except SyntaxError:
                        categories["source_SyntaxError"] += 1
                        cat_samples.setdefault("source_SyntaxError", []).append((fp, mod_name))
                        errors += 1
                        break
                    except FileNotFoundError as e:
                        categories["source_FileNotFoundError"] += 1
                        cat_samples.setdefault("source_FileNotFoundError", []).append((fp, mod_name, str(e)[:60]))
                        errors += 1
                        break
                    except ImportError as e:
                        emsg = str(e)
                        if "BATCH_SIZE" in emsg or "BUFFER_SIZE" in emsg:
                            categories["missing_constant_BATCH_SIZE"] += 1
                            cat_samples.setdefault("missing_constant_BATCH_SIZE", []).append((fp, mod_name))
                        elif "cannot import name" in emsg:
                            categories["missing_named_export"] += 1
                            cat_samples.setdefault("missing_named_export", []).append((fp, mod_name, emsg[:80]))
                        else:
                            categories["source_ImportError_other"] += 1
                            cat_samples.setdefault("source_ImportError_other", []).append((fp, mod_name, emsg[:80]))
                        errors += 1
                        break
                    except ModuleNotFoundError as e:
                        categories["source_ModuleNotFoundError"] += 1
                        cat_samples.setdefault("source_ModuleNotFoundError", []).append((fp, mod_name, str(e)[:60]))
                        errors += 1
                        break
                    except Exception as e:
                        categories["source_other_exception"] += 1
                        cat_samples.setdefault("source_other_exception", []).append((fp, mod_name, type(e).__name__, str(e)[:60]))
                        errors += 1
                        break

print(f"Total test files scanned: {total}")
print(f"Files with import-time errors: {errors}")
print()
print("ERROR CATEGORIES:")
for cat, count in categories.most_common():
    print(f"  {cat}: {count}")

for cat_name in sorted(cat_samples.keys()):
    samples = cat_samples[cat_name]
    print(f"\n--- {cat_name} ({len(samples)} total, first 5) ---")
    for s in samples[:5]:
        if isinstance(s, tuple):
            print(f"  {' | '.join(str(x) for x in s)}")
        else:
            print(f"  {s}")
