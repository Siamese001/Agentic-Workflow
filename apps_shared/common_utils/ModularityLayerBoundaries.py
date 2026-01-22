import ast

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _iter_core_files() -> None:
    core_root = PROJECT_ROOT / "core"
    if not core_root.exists():
        return
    for path in core_root.rglob("*.py"):
        if path.name.startswith("test_"):
            continue
        yield path


def _parse_calls(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                value = func.value
                if isinstance(value, ast.Name):
                    calls.append(f"{value.id}.{func.attr}")
            elif isinstance(func, ast.Name):
                calls.append(func.id)
    return calls


def _parse_import_from_runtime_utils(path: Path) -> list[str]:
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
        if isinstance(node, ast.ImportFrom) and node.module in (
            "runtime_utils",
            "runtime.runtime_utils",
        ):
            for alias in node.names:
                imports.append(alias.name)
    return imports


def test_core_does_not_call_runtime_utils_invoke_model() -> None:
    """core/* must not call runtime_utils.invoke_model directly."""
    forbidden = {"invoke_model", "runtime_utils.invoke_model"}
    for path in _iter_core_files():
        calls = set(_parse_calls(path))
        assert not (calls & forbidden), (
            f"{path} calls forbidden runtime_utils.invoke_model: {calls & forbidden}"
        )


def test_core_does_not_from_import_invoke_model() -> None:
    """core/* must not import invoke_model directly from runtime_utils."""
    for path in _iter_core_files():
        imported = set(_parse_import_from_runtime_utils(path))
        assert "invoke_model" not in imported, f"{path} imports invoke_model from runtime_utils"