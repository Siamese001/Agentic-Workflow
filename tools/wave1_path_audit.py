#!/usr/bin/env python3
"""Path replace audit script - Wave 1 implementation"""

import json
import os
from pathlib import Path


def audit_path_replaces():
    results = []
    suspicious = []

    for root, _dirs, files in os.walk("agentic_core/L0_routing"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if ".replace(" in line:
                                content = line.strip()
                                # Check for suspicious patterns
                                is_suspicious = False
                                if "chr(92)" in content or r"'\\'" in content or r'"\\"' in content:
                                    is_suspicious = True

                                # Check if path-related
                                is_path_related = any(
                                    x in content.lower()
                                    for x in [
                                        "path",
                                        "file",
                                        "dir",
                                        "as_posix",
                                    ]
                                )

                                entry = {
                                    "file": path,
                                    "line": i,
                                    "content": content,
                                    "is_suspicious": is_suspicious,
                                    "is_path_related": is_path_related,
                                }

                                if is_suspicious:
                                    suspicious.append(entry)
                                else:
                                    results.append(entry)
                except OSError:
                    pass

    # Save audit report
    Path("artifacts").mkdir(exist_ok=True)
    with open("artifacts/path_replace_audit.json", "w") as f:
        json.dump(
            {
                "all": results + suspicious,
                "suspicious": suspicious,
                "path_related": [r for r in results if r.get("is_path_related")],
                "stats": {
                    "total": len(results) + len(suspicious),
                    "suspicious": len(suspicious),
                    "path_related": len([r for r in results if r.get("is_path_related")]),
                },
            },
            f,
            indent=2,
        )

    # Print summary
    print("Path Replace Audit Complete")
    print("=" * 50)
    print(f"Total .replace() calls: {len(results) + len(suspicious)}")
    print(f"Suspicious (backslash-related): {len(suspicious)}")
    print(f"Path-related: {len([r for r in results if r.get('is_path_related')])}")
    print()

    if suspicious:
        print("=== SUSPICIOUS PATTERNS (potential bug sources) ===")
        for s in suspicious:
            print(f"{s['file']}:{s['line']}")
            print(f"  {s['content'][:100]}")
            print()


if __name__ == "__main__":
    audit_path_replaces()
