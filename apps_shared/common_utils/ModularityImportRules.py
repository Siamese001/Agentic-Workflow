import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _iter_py_files(root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*.py"):
        if path.name.startswith("test_"):
            continue
        yield path


def _parse_imports(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _has_forbidden_import(root: Path, forbidden_prefixes: list[str]) -> list[tuple[Path, str]]:
    violations: list[tuple[Path, str]] = []
    for path in _iter_py_files(root):
        for mod in _parse_imports(path):
            for prefix in forbidden_prefixes:
                if mod == prefix or mod.startswith(prefix + "."):
                    violations.append((path, mod))
    return violations


def test_core_does_not_import_providers() -> None:
    """core/* MUST NOT import providers/* (scoped to new core tree only)."""
    core_root = PROJECT_ROOT / "core"
    violations = _has_forbidden_import(core_root, ["providers"])
    assert not violations, f"core modules must not import providers: {violations}"


def test_core_does_not_import_meta_retrievers_directly() -> None:
    """core/* must not depend on low-level retrievers; use orchestrators instead."""
    core_root = PROJECT_ROOT / "core"
    violations = _has_forbidden_import(core_root, ["meta.retrieval.retrievers"])
    assert not violations, f"core modules must not import retrievers directly: {violations}"


def test_meta_does_not_import_core() -> None:
    """meta/* MUST NOT import core/* (except core.models.models for data types)."""
    meta_root = PROJECT_ROOT / "meta"
    all_violations = _has_forbidden_import(meta_root, ["core"])

    # Allow core.models.models imports for data types (established pattern)
    allowed_imports = {"core.models.models", "core.models"}
    violations = [(path, mod) for path, mod in all_violations if mod not in allowed_imports]

    assert not violations, f"meta modules must not import core (except core.models): {violations}"


def test_providers_do_not_import_core_or_meta() -> None:
    """providers/* MUST be infrastructure-only; no core/meta imports."""
    providers_root = PROJECT_ROOT / "providers"
    violations = _has_forbidden_import(providers_root, ["core", "meta"])
    assert not violations, f"providers must not import core/meta: {violations}"
