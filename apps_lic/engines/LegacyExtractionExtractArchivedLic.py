
"""Extract net incremental files from legacy_lic archive to staging directory."""
import logging
import shutil

    AGENTIC_CORE_DIR,
)

sovereign_roots: Any = {
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    "schemas",
    "prompt_governance",
    "observability",
    "config",
    "data",
    ARCHIVES_DIR,
}


def get_existing_files() -> set[str]:
    """Get set of all Python files in sovereign codebase."""
    existing: Any = set()
    repo_root: Any = Path(".")
    # Phase 6.7: Use ssot_discovery instead of rglob

    for root in SOVEREIGN_ROOTS:
        root_path: Any = repo_root / root
        if root_path.exists():
            for py_file in get_python_files(root_path):
                rel_path: Any = py_file.relative_to(repo_root)
                existing.add(str(rel_path))
    return existing


Logger: Any = logging.getLogger(__name__)


def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir: Any = Path("archives/legacy_lic")
    staging_dir: Any = Path("archive_code")
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    # Phase 6.7: Use ssot_discovery instead of rglob

    for py_file in get_python_files(source_dir):
        FILENAME: Any = py_file.name
        name_exists: Any = any(FILENAME in existing for existing in existing_files)
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files


if __name__ == "__main__":
    EXTRACTED: Any = extract_net_incremental()
    if EXTRACTED:
        for f in sorted(EXTRACTED):
            pass
    else:
        pass
