#!/usr/bin/env python3
"""Categorize collection errors by attempting to import each test file."""

import importlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

# Get list of error files from pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/unit/agentic_core/", "-q", "--tb=no", "--no-header"],
    capture_output=True, text=True,
)

# Parse ERROR lines
error_files = []
for line in (result.stdout + result.stderr).splitlines():
    m = re.match(r"ERROR\s+(.+\.py)", line.strip())
    if m:
        error_files.append(m.group(1).strip())

print(f"Total error files from pytest: {len(error_files)}")

# Categorize each
categories = Counter()
cat_samples = {}

for fp in error_files:
    p = Path(fp)
    if not p.exists():
        categories["file_not_found"] += 1
        continue

    content = p.read_text("utf-8")

    # Check if it's our enhanced file or pre-existing
    is_enhanced = "Behavioral contract tests for" in content and "@pytest.fixture" in content

    # Try to identify root cause from the file's imports
    if "from agentic_core" in content and "import" in content:
        # Extract the import line
        for line in content.splitlines():
            if line.strip().startswith("from agentic_core") and "import" in line:
                # Try to identify what fails
                m2 = re.search(r"from\s+([\w.]+)\s+import\s+(.+?)(?:\s*#|$)", line)
                if m2:
                    mod_path = m2.group(1)
                    imports = m2.group(2).strip().rstrip(")")
                    if "BATCH_SIZE" in imports:
                        categories["BATCH_SIZE_import"] += 1
                        cat_samples.setdefault("BATCH_SIZE_import", []).append(fp)
                        break
                    elif "BUFFER_SIZE" in imports or "MAX_RETRIES" in imports or "DEFAULT_SLEEP" in imports:
                        categories["config_constant_import"] += 1
                        cat_samples.setdefault("config_constant_import", []).append(fp)
                        break
        else:
            # Check if the module itself has syntax/indent errors
            # Try dynamic import to see
            try:
                # Extract MODULE_PATH if present
                mp_match = re.search(r'MODULE_PATH\s*=\s*["\']([^"\']+)["\']', content)
                if mp_match:
                    mod = mp_match.group(1)
                    try:
                        importlib.import_module(mod)
                        categories["module_imports_ok_but_test_fails"] += 1
                    except IndentationError:
                        categories["IndentationError_in_module"] += 1
                        cat_samples.setdefault("IndentationError_in_module", []).append(fp)
                    except SyntaxError:
                        categories["SyntaxError_in_module"] += 1
                        cat_samples.setdefault("SyntaxError_in_module", []).append(fp)
                    except ModuleNotFoundError:
                        categories["ModuleNotFoundError"] += 1
                        cat_samples.setdefault("ModuleNotFoundError", []).append(fp)
                    except FileNotFoundError:
                        categories["FileNotFoundError_at_import"] += 1
                        cat_samples.setdefault("FileNotFoundError_at_import", []).append(fp)
                    except ImportError as e:
                        categories["ImportError_other"] += 1
                        cat_samples.setdefault("ImportError_other", []).append((fp, str(e)[:80]))
                    except Exception as e:
                        categories["other_exception"] += 1
                        cat_samples.setdefault("other_exception", []).append((fp, type(e).__name__, str(e)[:60]))
                else:
                    categories["no_MODULE_PATH"] += 1
                    cat_samples.setdefault("no_MODULE_PATH", []).append(fp)
            except Exception:
                categories["analysis_failed"] += 1
    elif is_enhanced:
        categories["enhanced_unknown"] += 1
    else:
        categories["non_enhanced_unknown"] += 1
        cat_samples.setdefault("non_enhanced_unknown", []).append(fp)

print("\nERROR CATEGORIES:")
for cat, count in categories.most_common():
    print(f"  {cat}: {count}")

for cat in ["BATCH_SIZE_import", "IndentationError_in_module", "SyntaxError_in_module",
            "FileNotFoundError_at_import", "ModuleNotFoundError", "no_MODULE_PATH",
            "non_enhanced_unknown"]:
    samples = cat_samples.get(cat, [])
    if samples:
        print(f"\n--- {cat} (first 5) ---")
        for s in samples[:5]:
            if isinstance(s, tuple):
                print(f"  {s}")
            else:
                print(f"  {s}")
