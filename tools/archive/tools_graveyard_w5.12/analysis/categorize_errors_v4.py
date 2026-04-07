#!/usr/bin/env python3
"""
Categorize collection errors using subprocess isolation + timeout.

RCA fix: v3 hung because importlib.import_module() in-process triggers
import-time side effects (subprocess calls, file reads, network) that
block indefinitely. Fix: use subprocess with per-module timeout.

Complies with §9 timeout + progress requirements.
"""

import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

# §9 timeout: 10s per module import (fast query category)
PER_MODULE_TIMEOUT = 10
# Overall script timeout: 5 minutes
SCRIPT_TIMEOUT = 300

SCRIPT_START = time.monotonic()


def check_script_timeout():
    elapsed = time.monotonic() - SCRIPT_START
    if elapsed > SCRIPT_TIMEOUT:
        print(f"\n[TIMEOUT] Script exceeded {SCRIPT_TIMEOUT}s overall limit. Aborting.")
        sys.exit(1)


def try_import_module(module_path: str) -> dict:
    """Try importing a module in a subprocess with timeout."""
    code = f"""
import importlib, sys, json
try:
    mod = importlib.import_module("{module_path}")
    symbols = [n for n in dir(mod) if not n.startswith("_")]
    print(json.dumps({{"ok": True, "symbols": len(symbols)}}))
except IndentationError as e:
    print(json.dumps({{"ok": False, "error_type": "IndentationError", "msg": str(e)[:120]}}))
except SyntaxError as e:
    print(json.dumps({{"ok": False, "error_type": "SyntaxError", "msg": str(e)[:120]}}))
except FileNotFoundError as e:
    print(json.dumps({{"ok": False, "error_type": "FileNotFoundError", "msg": str(e)[:120]}}))
except ModuleNotFoundError as e:
    print(json.dumps({{"ok": False, "error_type": "ModuleNotFoundError", "msg": str(e)[:120]}}))
except ImportError as e:
    print(json.dumps({{"ok": False, "error_type": "ImportError", "msg": str(e)[:120]}}))
except Exception as e:
    print(json.dumps({{"ok": False, "error_type": type(e).__name__, "msg": str(e)[:120]}}))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True,
            timeout=PER_MODULE_TIMEOUT,
            encoding="utf-8", errors="replace",
        )
        stdout = result.stdout.strip()
        if stdout:
            return json.loads(stdout)
        stderr = result.stderr.strip()[:200]
        return {"ok": False, "error_type": "no_output", "msg": stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error_type": "TIMEOUT", "msg": f"Import hung for >{PER_MODULE_TIMEOUT}s"}
    except Exception as e:
        return {"ok": False, "error_type": "subprocess_error", "msg": str(e)[:120]}


def main():
    tests_dir = Path("tests/unit/agentic_core")
    categories = Counter()
    cat_samples: dict[str, list] = {}
    total = 0
    errors = 0
    ok_count = 0

    # Collect all test files
    all_files = sorted(tests_dir.rglob("test_*.py"))
    file_count = len(all_files)
    print(f"Scanning {file_count} test files with {PER_MODULE_TIMEOUT}s per-import timeout...")
    print(f"Overall script timeout: {SCRIPT_TIMEOUT}s")
    print()

    for i, p in enumerate(all_files):
        total += 1

        # §9 progress reporting
        if (i + 1) % 50 == 0 or i == 0:
            elapsed = time.monotonic() - SCRIPT_START
            pct = ((i + 1) / file_count) * 100
            print(f"  [{pct:5.1f}%] {i+1}/{file_count} files | {elapsed:.0f}s elapsed | errors={errors} ok={ok_count}")

        check_script_timeout()

        fp = str(p).replace("\\", "/")

        try:
            content = p.read_text("utf-8")
        except Exception:
            categories["unreadable"] += 1
            errors += 1
            continue

        # Check if it's our enhanced file with fixture pattern
        is_enhanced = "@pytest.fixture" in content and "FIRST-PARTY IMPORT FAILED" in content

        # Check if it has direct top-level from...import
        has_direct_import = False
        direct_import_modules = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("from agentic_core") and "import" in stripped:
                m = re.match(r"from\s+([\w.]+)\s+import", stripped)
                if m:
                    has_direct_import = True
                    direct_import_modules.append(m.group(1))

        # Compile check on the test file itself
        try:
            compile(content, fp, "exec")
        except SyntaxError:
            categories["test_file_syntax_error"] += 1
            cat_samples.setdefault("test_file_syntax_error", []).append(fp)
            errors += 1
            continue

        if is_enhanced:
            # Extract MODULE_PATH
            mp_match = re.search(r'MODULE_PATH\s*=\s*["\']([^"\']+)["\']', content)
            if mp_match:
                mod_path = mp_match.group(1)
                result = try_import_module(mod_path)
                if result["ok"]:
                    ok_count += 1
                else:
                    et = result["error_type"]
                    categories[f"enhanced_{et}"] += 1
                    cat_samples.setdefault(f"enhanced_{et}", []).append(
                        (fp, mod_path, result["msg"][:80]),
                    )
                    errors += 1
            else:
                ok_count += 1  # No MODULE_PATH = not a problem

        elif has_direct_import:
            # Non-enhanced file with direct imports — test each
            any_failed = False
            for mod_path in direct_import_modules:
                result = try_import_module(mod_path)
                if not result["ok"]:
                    et = result["error_type"]
                    msg = result["msg"]
                    if "BATCH_SIZE" in msg or "BUFFER_SIZE" in msg or "MAX_RETRIES" in msg:
                        categories["missing_constant"] += 1
                        cat_samples.setdefault("missing_constant", []).append(
                            (fp, mod_path, msg[:80]),
                        )
                    else:
                        categories[f"direct_{et}"] += 1
                        cat_samples.setdefault(f"direct_{et}", []).append(
                            (fp, mod_path, msg[:80]),
                        )
                    any_failed = True
                    errors += 1
                    break
            if not any_failed:
                ok_count += 1
        else:
            ok_count += 1

    elapsed = time.monotonic() - SCRIPT_START
    print()
    print("=" * 70)
    print(f"RESULTS ({elapsed:.0f}s)")
    print("=" * 70)
    print(f"Total files: {total}")
    print(f"OK (importable): {ok_count}")
    print(f"Errors: {errors}")
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

    # Write full report
    report_path = Path("artifacts/collection_error_categories.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "total": total, "ok": ok_count, "errors": errors,
        "elapsed_seconds": round(elapsed, 1),
        "categories": dict(categories.most_common()),
        "samples": {k: [str(s) for s in v[:10]] for k, v in cat_samples.items()},
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
