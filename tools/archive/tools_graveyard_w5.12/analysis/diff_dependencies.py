import subprocess
import sys

import tomllib


def main():
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    project = config.get("project", {})
    mandatory = {
        dep.split(">=")[0].split("==")[0].split("<=")[0].split("[")[0].strip().lower()
        for dep in project.get("dependencies", [])
    }

    optionals = project.get("optional-dependencies", {})
    optional_groups = {}
    for group, deps in optionals.items():
        optional_groups[group] = {
            dep.split(">=")[0].split("==")[0].split("<=")[0].split("[")[0].strip().lower() for dep in deps
        }

    all_listed = mandatory.copy()
    for group_deps in optional_groups.values():
        all_listed.update(group_deps)

    try:
        result = subprocess.run(
            [sys.executable, "tools/find_imports.py"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"Error running find_imports.py: {e}")
        return

    if len(lines) < 3:
        return

    found_imports = {}
    for line in lines[2:]:
        if " | " in line:
            parts = line.split(" | ")
            if len(parts) == 2:
                imp = parts[0].strip().lower()
                locs = {l.strip() for l in parts[1].split(",")}
                found_imports[imp] = locs

    # Mapping of import names to package names if different
    import_to_pkg = {
        "yaml": "pyyaml",
        "sklearn": "scikit-learn",
        "bs4": "beautifulsoup4",
        "google": "google-genai",
        "openai": "openai",
        "anthropic": "anthropic",
        "cv2": "opencv-python",
        "pypdf": "pypdf",
        "pypdf2": "pypdf2",
        "pdfplumber": "pdfplumber",
        "pdf2image": "pdf2image",
        "pytesseract": "pytesseract",
        "PIL": "pillow",
        "fitz": "pymupdf",
        "vllm": "vllm",
        "sentence_transformers": "sentence-transformers",
        "opentelemetry": "opentelemetry-api",
        "dotenv": "python-dotenv",
        "git": "gitpython",
        "faiss": "faiss-cpu",
        "tree_sitter": "tree-sitter",
        "tree_sitter_python": "tree-sitter-python",
        "pydantic_settings": "pydantic-settings",
        "pydantic_core": "pydantic",  # included in pydantic
        "rank_bm25": "rank-bm25",
    }

    missing_mandatory = []
    missing_optional = []
    misplaced = []  # in optional but used in core

    for imp, locs in found_imports.items():
        pkg_name = import_to_pkg.get(imp, imp)

        # Check if it's internal noise
        if imp in [
            "client",
            "data",
            "execute_ssot",
            "mcp0_git_add_or_commit",
            "mcp0_git_branch",
            "mcp0_git_log_or_diff",
            "mcp0_git_push",
            "mcp0_git_status",
            "mcp11_delete",
            "mcp11_get",
            "mcp11_set",
            "mcp4_fetch",
            "mcp6_get_file_info",
            "mcp6_list_directory",
            "mcp6_read_text_file",
            "mcp8_add_observations",
            "mcp8_create_entities",
            "mcp8_search_nodes",
            "mcp_time_client",
            "runtime",
            "services",
            "shared",
            "territory_ssot_definitions",
            "test_migration_guardian",
            "test_runtime_adg_integration",
            "test_shadow_router_classifier",
            "test_vllm_canonical_payload_lock",
            "test_vllm_replay_tamper_roundtrip",
            "wave6a_validation_enforcer",
            "wave_state_manager",
            "p0_microwave_wirer",
            "pre_execution_validator",
            "implement_unified_memory",
            "idempotent_wave_template",
            "guardian_sweep",
            "fast_file_analysis",
            "broken_module",
            "archives",
            "config",
            "titanium_rag_pipeline",
        ]:
            continue

        if pkg_name in mandatory:
            continue

        is_in_optional = False
        found_group = None
        for group, group_deps in optional_groups.items():
            if pkg_name in group_deps:
                is_in_optional = True
                found_group = group
                break

        if "core" in locs:
            if is_in_optional:
                misplaced.append((imp, pkg_name, found_group, locs))
            elif pkg_name not in mandatory:
                missing_mandatory.append((imp, pkg_name, locs))
        elif "apps" in locs:
            if not is_in_optional:
                missing_optional.append((imp, pkg_name, locs))

    print("--- Missing Mandatory (used in core, not in dependencies) ---")
    for imp, pkg, locs in sorted(missing_mandatory):
        print(f"  - {imp} (Package: {pkg}, Locations: {', '.join(locs)})")

    print("\n--- Misplaced (used in core, but listed in optional group) ---")
    for imp, pkg, group, locs in sorted(misplaced):
        print(f"  - {imp} (Package: {pkg}, Current Group: {group}, Locations: {', '.join(locs)})")

    print("\n--- Missing Optional (used in apps, but not listed anywhere) ---")
    for imp, pkg, locs in sorted(missing_optional):
        print(f"  - {imp} (Package: {pkg}, Locations: {', '.join(locs)})")


if __name__ == "__main__":
    main()
