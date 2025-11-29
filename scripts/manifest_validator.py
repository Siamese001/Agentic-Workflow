# manifest_validator.py
# Validates repo structure against a canonical manifest.yaml specification.

import os
import sys
import yaml

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"

MANIFEST_PATH = os.path.join(REPO_ROOT, "manifest.yaml")

def load_manifest(path):
    if not os.path.exists(path):
        print(f"ERROR: manifest.yaml missing at: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def walk_repo(root):
    dirs = []
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        if rel == ".":
            rel = ""
        dirs.append(rel)
        for f in filenames:
            path = f"{rel}/{f}" if rel else f
            files.append(path)
    return dirs, files

def flatten_manifest(node, prefix=""):
    expected_dirs = set()
    expected_files = set()

    for entry in node:
        name = entry.get("name")
        path = f"{prefix}/{name}" if prefix else name

        if entry["type"] == "directory":
            expected_dirs.add(path)
            children = entry.get("children", [])
            d2, f2 = flatten_manifest(children, path)
            expected_dirs |= d2
            expected_files |= f2

        elif entry["type"] == "file":
            expected_files.add(path)

    return expected_dirs, expected_files

def main():
    manifest = load_manifest(MANIFEST_PATH)
    expected_dirs, expected_files = flatten_manifest(manifest["root"])

    actual_dirs, actual_files = walk_repo(REPO_ROOT)

    # normalize
    actual_dirs = set(d for d in actual_dirs if d != "")
    actual_files = set(actual_files)

    errors = []

    missing_dirs = expected_dirs - actual_dirs
    if missing_dirs:
        errors.append(f"Missing directories:\n  " + "\n  ".join(sorted(missing_dirs)))

    extra_dirs = actual_dirs - expected_dirs
    if extra_dirs:
        errors.append(f"Unexpected directories:\n  " + "\n  ".join(sorted(extra_dirs)))

    missing_files = expected_files - actual_files
    if missing_files:
        errors.append(f"Missing files:\n  " + "\n  ".join(sorted(missing_files)))

    extra_files = actual_files - expected_files
    if extra_files:
        errors.append(f"Unexpected extra files:\n  " + "\n  ".join(sorted(extra_files)))

    if errors:
        print("\n=== MANIFEST VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Manifest validation PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
