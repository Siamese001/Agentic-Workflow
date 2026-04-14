"""
Registry Integrity Audit Script (Phase 5)

Verifies that every "Active" prompt in registry.json maps to a real, valid .jinja file
with proper Phase 4 schema headers.
"""

import json
import sys
from pathlib import Path
from tqdm import tqdm


def load_registry(registry_path: Path) -> dict:
    """Load the prompt registry JSON file."""
    try:
        with open(registry_path, encoding="utf-8") as f:
            return json.load(f)
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"ERROR: Failed to load registry: {e}")
        sys.exit(1)


def extract_schema_from_template(template_path: Path) -> dict[str, list[str]]:
    """Extract schema information from Phase 4 header."""
    try:
        with open(template_path, encoding="utf-8") as f:
            content = f.read()
        for line in tqdm(content.split("\n")[:20], desc="Processing", unit="item"):
            if "{# SCHEMA:" in line:
                schema_match = line.replace("{# SCHEMA:", "").replace("#}", "").strip()
                required_vars = []
                optional_vars = []
                if "required_vars=[" in schema_match:
                    req_part = schema_match.split("required_vars=[")[1].split("]")[0]
                    required_vars = [v.strip() for v in req_part.split(",") if v.strip()]
                if "optional_vars=[" in schema_match:
                    opt_part = schema_match.split("optional_vars=[")[1].split("]")[0]
                    optional_vars = [v.strip() for v in opt_part.split(",") if v.strip()]
                return {"required_vars": required_vars, "optional_vars": optional_vars, "has_header": True}
        return {"has_header": False, "required_vars": [], "optional_vars": []}
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"ERROR reading template {template_path}: {e}")
        return {"has_header": False, "required_vars": [], "optional_vars": []}


def audit_registry_linkages(registry_path: Path, base_dir: Path) -> tuple[list[dict], list[dict]]:
    """
    Audit registry linkages.

    Returns:
        Tuple of (passed_entries, failed_entries)
    """
    registry = load_registry(registry_path)
    passed = []
    failed = []
    prompts = registry.get("prompts", {})
    for template_name, prompt_versions in tqdm(prompts.items(), desc="Processing", unit="item"):
        for prompt_data in tqdm(prompt_versions, desc="Processing", unit="item"):
            if not prompt_data.get("active", False):
                continue
            template_path = base_dir / "templates" / template_name
            if not template_path.exists():
                failed.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "error": "Template file not found",
                        "status": "FAIL",
                    },
                )
                continue
            schema = extract_schema_from_template(template_path)
            if not schema["has_header"]:
                failed.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "error": "Missing Phase 4 schema header",
                        "status": "FAIL",
                    },
                )
                continue
            passed.append(
                {
                    "prompt_id": template_name,
                    "template_path": str(template_path.relative_to(base_dir)),
                    "required_vars": schema["required_vars"],
                    "optional_vars": schema["optional_vars"],
                    "status": "PASS",
                },
            )
    return (passed, failed)


def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    registry_path = base_dir / "registry.json"
    print("Registry Integrity Audit (Phase 5)")
    print("=" * 50)
    print(f"Registry: {registry_path}")
    print(f"Base Directory: {base_dir}")
    print()
    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}")
        sys.exit(1)
    passed, failed = audit_registry_linkages(registry_path, base_dir)
    print("RESULTS:")
    print(f"  Active prompts checked: {len(passed) + len(failed)}")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    print()
    if failed:
        print("FAILED ENTRIES:")
        for entry in failed:
            print(f"  ❌ {entry['prompt_id']}: {entry['error']}")
            print(f"     Template: {entry['template_path']}")
        print()
    if passed:
        print("PASSED ENTRIES:")
        for entry in passed:
            print(f"  ✅ {entry['prompt_id']}: {entry['template_path']}")
            if entry["required_vars"]:
                print(f"     Required: {', '.join(entry['required_vars'])}")
        print()
    if failed:
        print("❌ AUDIT FAILED - Registry integrity issues detected")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED - All registry entries are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
