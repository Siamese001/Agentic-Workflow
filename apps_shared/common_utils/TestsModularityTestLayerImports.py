
import ast
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


FORBIDDEN_TOP_LEVEL = {"l1", "l2", "cognitive_agents"}
PROVIDERS_PACKAGE = "providers"
FORBIDDEN_IMPORTERS_FOR_PROVIDERS = {"core", "meta", "prompts", "profiles"}


def _iter_project_py_files() -> list:
    for path in PROJECT_ROOT.glob("*.py"):
        if path.name in {"l1.py", "l2.py", "cognitive_agents.py", "import_check.py"}:
            continue
        yield path
    for path in PROJECT_ROOT.iterdir():
        if path.is_dir() and path.name not in {
            "tests",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".git",
        }:
            for sub in path.rglob("*.py"):
                yield sub


def _get_imported_modules(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])
    return modules


def _top_level_dir_for(path: pathlib.Path) -> str | None:
    """Return the top-level directory name for a given file, if any."""

    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) <= 1:
        return None
    return parts[0]


def test_no_direct_imports_of_top_level_l_layers() -> None:
    """Non-test modules must not import bare l1/l2/cognitive_agents.

    They should import via core.l1, core.l2, core.cognitive_agents
    instead. Tests are allowed to use the historical imports.
    """

    violations: list[tuple[str, list[str]]] = []
    for path in _iter_project_py_files():
        if "tests" in path.parts:
            continue
        imported = _get_imported_modules(path)
        bad = imported & FORBIDDEN_TOP_LEVEL
        if bad:
            violations.append((str(path), sorted(bad)))

    assert not violations, f"Forbidden direct imports found: {violations}"


def test_non_providers_do_not_import_providers() -> None:
    """Core/meta/prompts/profiles must not import the top-level providers package."""

    violations: list[tuple[str, list[str]]] = []
    for path in _iter_project_py_files():
        if "tests" in path.parts:
            continue

        top = _top_level_dir_for(path)
        if top not in FORBIDDEN_IMPORTERS_FOR_PROVIDERS:
            continue

        imported = _get_imported_modules(path)
        if PROVIDERS_PACKAGE in imported:
            violations.append((str(path), sorted(imported)))

    assert not violations, f"Non-provider modules importing providers: {violations}"


def test_meta_does_not_import_core_or_archived_l_layers() -> None:
    """meta/ modules must not import core or archived l1/l2/cognitive_agents."""

    violations: list[tuple[str, list[str]]] = []
    for path in _iter_project_py_files():
        if "tests" in path.parts:
            continue

        top = _top_level_dir_for(path)
        if top != "meta":
            continue

        imported = _get_imported_modules(path)
        bad = imported & (FORBIDDEN_TOP_LEVEL | {"core"})
        if bad:
            violations.append((str(path), sorted(bad)))

    assert not violations, f"meta modules importing forbidden core/L layers: {violations}"


def test_prompt_files_do_not_import_providers_or_core() -> None:
    """prompt_* files must not import providers or core/l1/l2/cognitive_agents."""

    violations: list[tuple[str, list[str]]] = []
    for path in _iter_project_py_files():
        if "tests" in path.parts:
            continue

        # Treat top-level prompt_* files as prompts layer for now.
        if path.name not in {"prompt_builder.py", "prompt_system_v10_10.py"}:
            continue

        imported = _get_imported_modules(path)
        bad = set()
        if PROVIDERS_PACKAGE in imported:
            bad.add(PROVIDERS_PACKAGE)
        if "core" in imported:
            bad.add("core")
        bad |= imported & FORBIDDEN_TOP_LEVEL

        if bad:
            violations.append((str(path), sorted(bad)))

    assert not violations, f"prompt_* files importing forbidden modules: {violations}"